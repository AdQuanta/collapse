"""Build one approval sample for the network-connectivity Sobol atlases.

The established 18-by-10-inch six-panel block is retained without resizing any
of its cells.  The exact N=12 detector graph used in the dynamics is appended
in a separate column to the right.  As in the approved recent Sobol atlases,
spectral calculations use N_D=10, the Vab histogram has a logarithmic
mean-spacing-normalized x axis, and the lower-right panel shows unfolded level
spacings.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-network-sobol-graph-sample")
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
import numpy as np  # noqa: E402
from scipy.optimize import minimize  # noqa: E402

from core.level_spacing import (  # noqa: E402
    MEAN_R_GOE,
    MEAN_R_POISSON,
    compute_level_spacing_ratios,
    compute_level_spacings,
    compute_unfolded_spacings,
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)
from core.graph_spectral_sectors import (  # noqa: E402
    DetectorSymmetrySector,
    largest_detector_symmetry_sectors,
)
from core.detector_graphs import (  # noqa: E402
    DetectorGraphSpec,
    detector_graph_edges,
)
from scripts.build_second_neighbor_mean_spacing_sample_2x3 import (  # noqa: E402
    plot_mean_spacing_gap_weight,
)
from scripts.build_sobol_flat_ranked_1x6_by_n import (  # noqa: E402
    CaseRecord,
    GAP_FLOOR,
    SpectralData,
    VAB_POWER_FLOOR,
    _diagnostics_panel,
    _heatmap_panel,
    _load_result_arrays,
    inventory,
)
from scripts.ranked_atlas_2x3 import (  # noqa: E402
    bandwidth_normalized_gaps,
    degenerate_groups,
    multiplicity_panel_all_ticks,
)


SOURCES = (
    ROOT / "work/zeus_sobol_erdos_renyi_hz0_0_N12_20260809_150226",
    ROOT / "work/zeus_sobol_watts_strogatz_hz0_0_N12_20260809_150226",
    ROOT / "work/zeus_sobol_barabasi_albert_hz0_0_N12_20260809_150226",
    ROOT / "work/zeus_sobol_expander_hz0_0_N12_20260809_150228",
)
OUTPUT = ROOT / "reports/network_sobol_graph_sample_2x3_2026-08-12"
SPECTRAL_N = 10


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _build_detector_matrices(
    record: CaseRecord,
    detector_n: int,
    graph_spec: DetectorGraphSpec,
) -> tuple[np.ndarray, np.ndarray, tuple[tuple[int, int], ...]]:
    """Return detector H and V in the computational basis.

    H_D = -hz sum_i Zi - J sum_(ij) Zi Zj
          - Jpm sum_(ij) (sigma_i^+ sigma_j^- + h.c.),
    V = (Jx/sqrt(N_D)) sum_i Xi.  Jy is zero in these four campaigns.
    """

    if record.jy != 0.0:
        raise ValueError("network campaigns are expected to have Jy=0")
    edges = detector_graph_edges(detector_n, graph_spec)
    dimension = 1 << detector_n
    hamiltonian = np.zeros((dimension, dimension), dtype=np.float64)
    coupling = np.zeros((dimension, dimension), dtype=np.float64)
    edge_jx = record.jx / math.sqrt(detector_n)
    for state in range(dimension):
        z = np.asarray(
            [1.0 if ((state >> site) & 1) == 0 else -1.0 for site in range(detector_n)]
        )
        hamiltonian[state, state] = (
            -record.hz * float(np.sum(z))
            -record.j * sum(float(z[left] * z[right]) for left, right in edges)
        )
        for left, right in edges:
            if ((state >> left) & 1) != ((state >> right) & 1):
                target = state ^ (1 << left) ^ (1 << right)
                hamiltonian[target, state] -= record.jpm
        for site in range(detector_n):
            coupling[state ^ (1 << site), state] += edge_jx
    if not np.allclose(hamiltonian, hamiltonian.T, atol=1.0e-13):
        raise RuntimeError("network detector Hamiltonian is not Hermitian")
    if not np.allclose(coupling, coupling.T, atol=1.0e-13):
        raise RuntimeError("network detector coupling is not Hermitian")
    return hamiltonian, coupling, edges


def compute_network_spectral(
    record: CaseRecord,
    graph_spec: DetectorGraphSpec,
    *,
    detector_n: int = SPECTRAL_N,
) -> SpectralData:
    """Diagonalize the network detector in exact total-magnetization sectors."""

    hamiltonian, coupling, _ = _build_detector_matrices(
        record, detector_n, graph_spec
    )
    sectors = tuple(
        np.asarray(
            [state for state in range(1 << detector_n) if state.bit_count() == nup],
            dtype=np.int64,
        )
        for nup in range(detector_n + 1)
    )
    block_energies: list[np.ndarray] = []
    block_vectors: list[np.ndarray] = []
    orthonormality_error = 0.0
    residual_error = 0.0
    for indices in sectors:
        block = hamiltonian[np.ix_(indices, indices)]
        energies, vectors = np.linalg.eigh(block)
        block_energies.append(energies)
        block_vectors.append(vectors)
        orthonormality_error = max(
            orthonormality_error,
            float(np.max(np.abs(vectors.T @ vectors - np.eye(indices.size)))),
        )
        residual_error = max(
            residual_error,
            float(np.max(np.abs(block @ vectors - vectors * energies[None, :]))),
        )
    offsets = np.cumsum([0, *[values.size for values in block_energies]])
    sector_energies = np.concatenate(block_energies)
    sector_vab = np.zeros(
        (sector_energies.size, sector_energies.size), dtype=np.float64
    )
    for row_sector, row_indices in enumerate(sectors):
        row_slice = slice(offsets[row_sector], offsets[row_sector + 1])
        for column_sector in (row_sector - 1, row_sector + 1):
            if column_sector < 0 or column_sector > detector_n:
                continue
            column_indices = sectors[column_sector]
            column_slice = slice(offsets[column_sector], offsets[column_sector + 1])
            sector_vab[row_slice, column_slice] = (
                block_vectors[row_sector].T
                @ coupling[np.ix_(row_indices, column_indices)]
                @ block_vectors[column_sector]
            )
    order = np.argsort(sector_energies, kind="stable")
    energies = sector_energies[order]
    vab = sector_vab[np.ix_(order, order)]
    scale = max(float(np.ptp(energies)), 1.0)
    tolerance = max(1.0e-10, 1.0e-9 * scale)
    groups = degenerate_groups(energies, tolerance)
    gaps = np.abs(energies[:, None] - energies[None, :])
    power_total = float(np.sum(np.abs(vab) ** 2))
    if not np.isfinite(power_total) or power_total <= 0.0:
        raise RuntimeError("network Vab Frobenius norm is not positive")
    vab_power = np.abs(vab) ** 2 / power_total
    full_coupling_power = float(np.sum(coupling**2))
    validation: dict[str, float | bool] = {
        "hamiltonian_hermiticity_max_abs": float(
            np.max(np.abs(hamiltonian - hamiltonian.T))
        ),
        "coupling_hermiticity_max_abs": float(np.max(np.abs(coupling - coupling.T))),
        "eigenvector_orthonormality_max_abs": orthonormality_error,
        "eigenpair_residual_max_abs": residual_error,
        "eigenvalues_sorted": bool(np.all(np.diff(energies) >= -tolerance)),
        "magnetization_sectors_exploited": True,
        "vab_frobenius_consistency_rel": abs(power_total - full_coupling_power)
        / max(full_coupling_power, np.finfo(float).tiny),
    }
    if (
        validation["hamiltonian_hermiticity_max_abs"] > 1.0e-12
        or validation["coupling_hermiticity_max_abs"] > 1.0e-12
        or validation["eigenvector_orthonormality_max_abs"] > 1.0e-10
        or validation["eigenpair_residual_max_abs"] > 1.0e-9
        or not validation["eigenvalues_sorted"]
        or validation["vab_frobenius_consistency_rel"] > 1.0e-10
    ):
        raise RuntimeError(f"network spectral validation failed: {validation}")
    pairs = np.asarray(
        [(group[0], group[1]) for group in groups if len(group) == 2],
        dtype=np.int64,
    ).reshape(-1, 2)
    amplitudes = np.asarray(
        [
            (
                abs(vab[left, right]) / math.sqrt(power_total),
                abs(vab[left, left]) / math.sqrt(power_total),
                abs(vab[right, right]) / math.sqrt(power_total),
            )
            for left, right in pairs
        ],
        dtype=float,
    ).reshape(-1, 3)
    return SpectralData(
        energies=energies,
        normalized_gaps=gaps / scale,
        vab_power=vab_power,
        multiplicities=tuple(len(group) for group in groups),
        multiplicity_two_pairs=pairs,
        multiplicity_two_couplings=amplitudes,
        degeneracy_tolerance=tolerance,
        validation=validation,
    )


def _transposition_automorphism(metadata: dict[str, Any]) -> tuple[int, int]:
    """Return the unique nonidentity node transposition of this sample graph."""

    nodes = int(metadata["nodes"])
    edges = {
        tuple(sorted((int(left), int(right))))
        for left, right in metadata["edges_zero_based"]
    }
    transpositions = []
    for left in range(nodes):
        for right in range(left + 1, nodes):
            permutation = list(range(nodes))
            permutation[left], permutation[right] = right, left
            transformed = {
                tuple(sorted((permutation[a], permutation[b]))) for a, b in edges
            }
            if transformed == edges:
                transpositions.append((left, right))
    if len(transpositions) != 1:
        raise ValueError(
            "sample requires exactly one nonidentity transposition automorphism; "
            f"found {transpositions}"
        )
    return transpositions[0]


def _fixed_nup_hamiltonian(
    record: CaseRecord,
    nodes: int,
    edges: tuple[tuple[int, int], ...],
    n_up: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return the detector Hamiltonian in one exact magnetization sector."""

    states = np.asarray(
        [state for state in range(1 << nodes) if state.bit_count() == n_up],
        dtype=np.int64,
    )
    state_to_index = {int(state): index for index, state in enumerate(states)}
    block = np.zeros((states.size, states.size), dtype=np.float64)
    for column, raw_state in enumerate(states):
        state = int(raw_state)
        z = np.asarray(
            [1.0 if ((state >> site) & 1) == 0 else -1.0 for site in range(nodes)]
        )
        block[column, column] = (
            -record.hz * float(np.sum(z))
            -record.j * sum(float(z[a] * z[b]) for a, b in edges)
        )
        for left, right in edges:
            if ((state >> left) & 1) != ((state >> right) & 1):
                target = state ^ (1 << left) ^ (1 << right)
                block[state_to_index[target], column] -= record.jpm
    if not np.allclose(block, block.T, atol=1.0e-13):
        raise RuntimeError("fixed-magnetization Hamiltonian block is not symmetric")
    return states, block


def _swap_state(state: int, left: int, right: int) -> int:
    if ((state >> left) & 1) == ((state >> right) & 1):
        return state
    return state ^ (1 << left) ^ (1 << right)


def _parity_bases(
    states: np.ndarray,
    swap: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """Construct orthonormal even/odd bases of a node-swap involution."""

    index = {int(state): position for position, state in enumerate(states)}
    visited: set[int] = set()
    plus_columns: list[np.ndarray] = []
    minus_columns: list[np.ndarray] = []
    for raw_state in states:
        state = int(raw_state)
        if state in visited:
            continue
        partner = _swap_state(state, *swap)
        visited.add(state)
        visited.add(partner)
        if partner == state:
            column = np.zeros(states.size, dtype=np.float64)
            column[index[state]] = 1.0
            plus_columns.append(column)
            continue
        plus = np.zeros(states.size, dtype=np.float64)
        minus = np.zeros(states.size, dtype=np.float64)
        plus[index[state]] = plus[index[partner]] = 1.0 / math.sqrt(2.0)
        minus[index[state]] = 1.0 / math.sqrt(2.0)
        minus[index[partner]] = -1.0 / math.sqrt(2.0)
        plus_columns.append(plus)
        minus_columns.append(minus)
    plus_basis = np.column_stack(plus_columns)
    minus_basis = np.column_stack(minus_columns)
    return plus_basis, minus_basis


def symmetry_resolved_spectra(
    record: CaseRecord,
    graph_metadata: dict[str, Any],
) -> tuple[dict[tuple[int, int], np.ndarray], dict[str, Any]]:
    """Compute the four largest nonredundant ``(Nup, swap parity)`` spectra."""

    nodes = int(graph_metadata["nodes"])
    edges = tuple(
        tuple(int(value) for value in edge)
        for edge in graph_metadata["edges_zero_based"]
    )
    swap = _transposition_automorphism(graph_metadata)
    spectra: dict[tuple[int, int], np.ndarray] = {}
    validation: dict[str, Any] = {
        "nodes": nodes,
        "swap_zero_based": list(swap),
        "swap_one_based": [swap[0] + 1, swap[1] + 1],
        "blocks": {},
    }
    for n_up in (nodes // 2 - 1, nodes // 2):
        states, block = _fixed_nup_hamiltonian(record, nodes, edges, n_up)
        plus_basis, minus_basis = _parity_bases(states, swap)
        projectors = {1: plus_basis, -1: minus_basis}
        union = []
        for parity, basis in projectors.items():
            parity_block = basis.T @ block @ basis
            residual = float(
                np.max(np.abs(block @ basis - basis @ parity_block))
            )
            energies = np.linalg.eigvalsh(parity_block)
            spectra[(n_up, parity)] = energies
            union.append(energies)
            validation["blocks"][f"Nup_{n_up}_p_{parity:+d}"] = {
                "dimension": int(energies.size),
                "invariant_subspace_residual_max_abs": residual,
            }
        full_energies = np.linalg.eigvalsh(block)
        union_energies = np.sort(np.concatenate(union))
        union_error = float(np.max(np.abs(full_energies - union_energies)))
        validation["blocks"][f"Nup_{n_up}_union"] = {
            "dimension": int(full_energies.size),
            "spectrum_union_max_abs": union_error,
        }
        if union_error > 1.0e-9:
            raise RuntimeError("parity-sector spectra do not reconstruct Nup block")
    return spectra, validation


def _sector_spacing_data(energies: np.ndarray) -> dict[str, Any]:
    scale = max(float(np.ptp(energies)), 1.0)
    tolerance = max(1.0e-10, 1.0e-9 * scale)
    unfolded = compute_unfolded_spacings(
        energies, tol=tolerance, degree=3, trim_fraction=0.10
    )
    raw = compute_level_spacings(energies, tol=tolerance)
    ratios = compute_level_spacing_ratios(raw)
    upper = max(4.0, float(np.percentile(unfolded, 99.5)))
    edges = np.linspace(0.0, upper, 21)
    histogram, _ = np.histogram(unfolded, bins=edges, density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    references = {
        "Poisson": poisson_spacing_distribution(centers),
        "GOE": wigner_spacing_distribution(centers, beta=1),
    }
    distances = {
        label: float(np.sum(np.abs(histogram - reference) * widths))
        for label, reference in references.items()
    }
    return {
        "unfolded": unfolded,
        "edges": edges,
        "histogram": histogram,
        "mean_ratio": float(np.mean(ratios)),
        "distances": distances,
        "tolerance": tolerance,
    }


def plot_symmetry_resolved_spacings(
    figure: plt.Figure,
    parent: Any,
    sectors: Sequence[DetectorSymmetrySector],
) -> dict[str, Any]:
    """Render four independently unfolded irreducible-sector distributions."""

    pane_grid = parent.subgridspec(
        2,
        2,
        wspace=0.32,
        hspace=0.48,
    )
    parent_bounds = parent.get_position(figure)
    figure.text(
        parent_bounds.x0 + 0.5 * parent_bounds.width,
        parent_bounds.y1 + 0.038,
        r"Symmetry-resolved detector level spacings ($N_D=12$)",
        fontsize=12.5,
        ha="center",
        va="center",
    )
    results: dict[str, Any] = {}
    if len(sectors) != 4:
        raise ValueError(f"expected four selected sectors, received {len(sectors)}")
    for panel_index, sector in enumerate(sectors):
        axis = figure.add_subplot(
            pane_grid[panel_index // 2, panel_index % 2]
        )
        energies = sector.energies
        data = _sector_spacing_data(energies)
        edges = data["edges"]
        centers = 0.5 * (edges[:-1] + edges[1:])
        axis.bar(
            centers,
            data["histogram"],
            width=0.92 * np.diff(edges),
            color="#9ecae1",
            edgecolor="white",
            linewidth=0.25,
        )
        grid = np.linspace(0.0, float(edges[-1]), 400)
        axis.plot(
            grid,
            poisson_spacing_distribution(grid),
            color="#222222",
            linestyle="--",
            linewidth=0.9,
            label="Poisson",
        )
        axis.plot(
            grid,
            wigner_spacing_distribution(grid, beta=1),
            color="#e45756",
            linewidth=0.9,
            label="GOE",
        )
        axis.set_title(
            sector.symmetry_label + rf"; dim={energies.size}",
            fontsize=9.0,
            pad=3,
        )
        axis.set(xlim=(0.0, float(edges[-1])), ylim=(0.0, None))
        axis.tick_params(labelsize=8.0, pad=1.5)
        axis.grid(axis="y", alpha=0.18)
        if panel_index // 2 == 1:
            axis.set_xlabel(r"$s$", fontsize=8.8, labelpad=1.5)
        if panel_index % 2 == 0:
            axis.set_ylabel(r"$p(s)$", fontsize=8.8, labelpad=1.5)
        axis.text(
            0.97,
            0.92,
            rf"$\langle\tilde r\rangle={data['mean_ratio']:.3f}$"
            + "\n"
            + rf"$D_1(P/G)={data['distances']['Poisson']:.2f}/"
            + rf"{data['distances']['GOE']:.2f}$",
            transform=axis.transAxes,
            ha="right",
            va="top",
            fontsize=7.0,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 0.7},
        )
        if panel_index == 0:
            axis.legend(frameon=False, fontsize=7.0, loc="upper left")
        results[f"sector_{panel_index + 1}"] = {
            "hamming_weight": sector.hamming_weight,
            "sector_index": sector.sector_index,
            "dimension": int(energies.size),
            "symmetry_label": sector.symmetry_label,
            "equivalent_copy_count": sector.equivalent_copy_count,
            "spacing_count": int(data["unfolded"].size),
            "mean_ratio": data["mean_ratio"],
            "l1_distances": data["distances"],
        }
    results["reference_mean_ratio"] = {
        "Poisson": MEAN_R_POISSON,
        "GOE": MEAN_R_GOE,
    }
    return results


def _shortest_path_distances(
    nodes: int, edges: tuple[tuple[int, int], ...]
) -> np.ndarray:
    distances = np.full((nodes, nodes), np.inf)
    np.fill_diagonal(distances, 0.0)
    for left, right in edges:
        distances[left, right] = distances[right, left] = 1.0
    for middle in range(nodes):
        distances = np.minimum(
            distances, distances[:, middle, None] + distances[None, middle, :]
        )
    if not np.all(np.isfinite(distances)):
        raise ValueError("publication graph layout requires a connected graph")
    return distances


def _kamada_kawai_layout(
    nodes: int, edges: tuple[tuple[int, int], ...]
) -> np.ndarray:
    """Return a deterministic stress-minimized graph layout."""

    distances = _shortest_path_distances(nodes, edges)
    angles = np.linspace(0.0, 2.0 * np.pi, nodes, endpoint=False) + np.pi / 2.0
    initial = np.column_stack((np.cos(angles), np.sin(angles)))
    rows, columns = np.triu_indices(nodes, k=1)
    targets = distances[rows, columns]
    weights = 1.0 / np.maximum(targets, 1.0) ** 2

    def objective(flat: np.ndarray) -> tuple[float, np.ndarray]:
        positions = flat.reshape(nodes, 2)
        delta = positions[rows] - positions[columns]
        lengths = np.maximum(np.linalg.norm(delta, axis=1), 1.0e-12)
        residual = lengths - targets
        value = 0.5 * float(np.sum(weights * residual**2))
        pair_gradient = (weights * residual / lengths)[:, None] * delta
        gradient = np.zeros_like(positions)
        np.add.at(gradient, rows, pair_gradient)
        np.add.at(gradient, columns, -pair_gradient)
        # Remove translational and weak rotational flat directions.
        center = np.mean(positions, axis=0)
        value += 0.5 * 1.0e-3 * float(np.sum(center**2))
        gradient += (1.0e-3 / nodes) * center
        return value, gradient.ravel()

    result = minimize(
        objective,
        initial.ravel(),
        jac=True,
        method="L-BFGS-B",
        options={"maxiter": 3000, "ftol": 1.0e-13, "gtol": 1.0e-9},
    )
    if not result.success and float(np.linalg.norm(result.jac, ord=np.inf)) > 1.0e-5:
        raise RuntimeError(f"graph layout did not converge: {result.message}")
    positions = result.x.reshape(nodes, 2)
    positions -= np.mean(positions, axis=0)
    span = float(np.max(np.ptp(positions, axis=0)))
    if span <= 0.0:
        raise RuntimeError("graph layout collapsed")
    return 1.78 * positions / span


def plot_detector_graph(axis: plt.Axes, metadata: dict[str, Any]) -> None:
    """Draw the exact dynamics graph with degree-encoded node area."""

    nodes = int(metadata["nodes"])
    edges = tuple(tuple(int(value) for value in edge) for edge in metadata["edges_zero_based"])
    degrees = np.asarray(metadata["degree_sequence"], dtype=float)
    positions = _kamada_kawai_layout(nodes, edges)
    segments = [[positions[left], positions[right]] for left, right in edges]
    axis.add_collection(
        LineCollection(
            segments,
            colors="#667085",
            linewidths=1.05,
            alpha=0.72,
            zorder=1,
        )
    )
    sizes = 95.0 + 34.0 * degrees
    axis.scatter(
        positions[:, 0],
        positions[:, 1],
        s=sizes,
        c=degrees,
        cmap="viridis",
        edgecolors="white",
        linewidths=1.0,
        zorder=2,
    )
    for node, (x_value, y_value) in enumerate(positions):
        axis.text(
            x_value,
            y_value,
            str(node + 1),
            ha="center",
            va="center",
            color="white" if degrees[node] >= np.median(degrees) else "black",
            fontsize=7.0,
            fontweight="bold",
            zorder=3,
        )
    kind_names = {
        "erdos_renyi": "Erdős–Rényi",
        "watts_strogatz": "Watts–Strogatz",
        "barabasi_albert": "Barabási–Albert",
        "random_regular": "random regular",
    }
    kind = str(metadata["canonical_kind"])
    axis.set_title(
        "Detector interaction graph\n"
        + f"{kind_names.get(kind, kind)} "
        + rf"($N={nodes}$, $|E|={len(edges)}$)",
        fontsize=8.5,
        pad=3,
    )
    axis.text(
        0.02,
        0.02,
        rf"node area $\propto$ degree; $\lambda_2(L)={float(metadata['laplacian_algebraic_connectivity']):.3f}$",
        transform=axis.transAxes,
        ha="left",
        va="bottom",
        fontsize=6.7,
        color="0.25",
    )
    x_min, y_min = np.min(positions, axis=0)
    x_max, y_max = np.max(positions, axis=0)
    x_pad = 0.16
    lower_pad = 0.30
    upper_pad = 0.16
    axis.set(
        xlim=(float(x_min - x_pad), float(x_max + x_pad)),
        ylim=(float(y_min - lower_pad), float(y_max + upper_pad)),
    )
    axis.set_aspect("equal")
    axis.axis("off")


def render_sample(
    record: CaseRecord,
    spectral: SpectralData,
    arrays: dict[str, np.ndarray],
    graph_metadata: dict[str, Any],
    sector_spectra: Sequence[DetectorSymmetrySector],
    sector_validation: dict[str, Any],
    output: Path,
    *,
    dpi: int = 220,
    approval_sample: bool = True,
) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    # The left 18 inches reproduce the established figure exactly.  Only the
    # canvas is extended, by 5 inches, for the separate network diagram.
    figure_width = 23.0
    legacy_width = 18.0
    figure = plt.figure(
        figsize=(figure_width, 10.0), dpi=dpi, constrained_layout=False
    )
    grid = figure.add_gridspec(
        2,
        3,
        left=0.045 * legacy_width / figure_width,
        right=0.985 * legacy_width / figure_width,
        bottom=0.07,
        top=0.86,
        wspace=0.24,
        hspace=0.30,
    )
    bandwidth_gaps, _, _ = bandwidth_normalized_gaps(spectral)
    gap_display = -np.log10(np.maximum(bandwidth_gaps, GAP_FLOOR))
    np.fill_diagonal(gap_display, np.nan)
    gap_cmap = plt.get_cmap("magma").copy()
    gap_cmap.set_bad("white")
    gap_axis = _heatmap_panel(
        figure,
        grid[0, 0],
        gap_display,
        title=rf"Energy proximity ($N_D={SPECTRAL_N}$)",
        cmap=gap_cmap,
        vmin=0.0,
        vmax=-math.log10(GAP_FLOOR),
        colorbar_label=r"$-\log_{10}(|E_a-E_b|/(E_{\max}-E_{\min}))$",
    )
    multiplicity_panel_all_ticks(figure.add_subplot(grid[0, 1]), spectral)
    _diagnostics_panel(figure, grid[0, 2], arrays, record)
    vab_axis = _heatmap_panel(
        figure,
        grid[1, 0],
        np.log10(np.maximum(spectral.vab_power, VAB_POWER_FLOOR)),
        title=rf"Interaction $V_{{ab}}$ ($N_D={SPECTRAL_N}$)",
        cmap="viridis",
        vmin=math.log10(VAB_POWER_FLOOR),
        vmax=0.0,
        colorbar_label=r"$\log_{10}(|V_{ab}|^2/\operatorname{Tr}(VV^\dagger))$",
    )
    histogram = plot_mean_spacing_gap_weight(
        figure.add_subplot(grid[1, 1]), spectral
    )
    sector_spacing = plot_symmetry_resolved_spacings(
        figure, grid[1, 2], sector_spectra
    )
    graph_axis = figure.add_axes(
        (18.25 / figure_width, 0.17, 4.45 / figure_width, 0.66)
    )
    plot_detector_graph(graph_axis, graph_metadata)
    divider_x = 18.08 / figure_width
    figure.add_artist(
        plt.Line2D(
            [divider_x, divider_x],
            [0.07, 0.90],
            transform=figure.transFigure,
            color="0.82",
            linewidth=0.8,
        )
    )
    figure.canvas.draw()
    gap_box = gap_axis.get_position()
    vab_box = vab_axis.get_position()
    if not (
        abs(gap_box.width - vab_box.width) < 1.0e-8
        and abs(gap_box.height - vab_box.height) < 1.0e-8
        and np.allclose(gap_axis.get_xlim(), vab_axis.get_xlim())
        and np.allclose(gap_axis.get_ylim(), vab_axis.get_ylim())
    ):
        raise RuntimeError("heatmap geometry assertion failed")
    kind_names = {
        "erdos_renyi": "Erdős–Rényi",
        "watts_strogatz": "Watts–Strogatz",
        "barabasi_albert": "Barabási–Albert",
        "random_regular": "Expander candidate (random regular)",
    }
    kind = str(graph_metadata["canonical_kind"])
    title = (
        ("Approval sample with interaction graph: " if approval_sample else "Interaction graph: ")
        + kind_names.get(kind, kind)
        + rf", Born rank {record.rank}, dynamics $N={record.dynamics_n}$, "
        + rf"{record.config_id}, $S_{{\rm Born}}={record.s_born:.4f}$"
        + "\n"
        + rf"$h_z={record.hz:.3g}$, $J={record.j:.3g}$, "
        + rf"$J_\pm={record.jpm:.3g}$, $J_x={record.jx:.3g}$, "
        + r"$J_y=0$, $h_{z0}=0$, $t=10^6$"
    )
    figure.text(
        0.5 * legacy_width / figure_width,
        0.975,
        title,
        fontsize=12.5,
        fontweight="bold",
        ha="center",
        va="top",
    )
    temporary = output.with_name(output.stem + f".tmp.{os.getpid()}.png")
    figure.savefig(temporary, dpi=dpi, facecolor="white")
    plt.close(figure)
    temporary.replace(output)
    return {
        "output": str(output.resolve()),
        "record": asdict(record),
        "graph_metadata": graph_metadata,
        "spectral_N": SPECTRAL_N,
        "spectral_graph_spec": asdict(
            DetectorGraphSpec(**graph_metadata["spec"])
        ),
        "spectral_validation": spectral.validation,
        "histogram_weight_sum": float(histogram["sum"]),
        "mean_spacing": float(histogram["mean_spacing"]),
        "symmetry_resolved_level_spacings": sector_spacing,
        "symmetry_sector_validation": sector_validation,
        "legacy_2x3_size_inches": [legacy_width, 10.0],
        "appended_graph_width_inches": figure_width - legacy_width,
    }


def select_sample() -> tuple[CaseRecord, dict[str, Any], Path]:
    candidates: list[tuple[CaseRecord, Path]] = []
    for source in SOURCES:
        records, _ = inventory(source)
        for record in records:
            if record.family == "jy_zero" and record.dynamics_n == 12:
                candidates.append((record, source))
    if not candidates:
        raise RuntimeError("no validated network-connectivity cases found")
    selected, source = max(
        candidates,
        key=lambda item: (item[0].s_born, item[0].config_id),
    )
    source_records = sorted(
        (record for record, root in candidates if root == source),
        key=lambda record: (-record.s_born, record.config_id),
    )
    rank = next(
        index for index, record in enumerate(source_records, start=1)
        if record.config_id == selected.config_id
    )
    selected = CaseRecord(**{**asdict(selected), "rank": rank, "within_n_rank": rank})
    metadata = _read_json(Path(selected.source_dir) / "metadata.json")
    graph = metadata.get("detector_graph")
    if not isinstance(graph, dict):
        raise ValueError("selected case lacks detector_graph metadata")
    return selected, graph, source


def main() -> None:
    record, graph_metadata, source = select_sample()
    graph_spec = DetectorGraphSpec(**graph_metadata["spec"])
    spectral = compute_network_spectral(record, graph_spec)
    sector_spectra, sector_validation = largest_detector_symmetry_sectors(
        int(graph_metadata["nodes"]),
        [tuple(edge) for edge in graph_metadata["edges_zero_based"]],
        hz=record.hz,
        j=record.j,
        jpm=record.jpm,
        count=4,
    )
    arrays = _load_result_arrays(Path(record.source_dir))
    output = OUTPUT / "sample_rank_0001_with_detector_graph.png"
    result = render_sample(
        record,
        spectral,
        arrays,
        graph_metadata,
        sector_spectra,
        sector_validation,
        output,
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "sample_manifest.json").write_text(
        json.dumps({**result, "source_campaign": str(source.resolve())}, indent=2),
        encoding="utf-8",
    )
    print(output.resolve())


if __name__ == "__main__":
    main()
