"""Build flat, per-N Born-ranked six-panel atlases for the Sobol coupling scans.

Each completed dynamics result is rendered as one horizontal figure:

1. detector energy-gap heatmap at ``N_D=8``;
2. the qubit-flip detector coupling ``V_ab`` in the detector energy basis;
3. detector-energy degeneracy multiplicities;
4. ``V_ab``, ``V_aa``, and ``V_bb`` for every multiplicity-two subspace;
5. ``P(theta)``, reflected ``P(pi-theta)``, WG/WC fits, and ``R`` vs Born;
6. the corresponding two Bloch-sphere branches.

Each ``(Jy family, N)`` combination is ranked independently by decreasing
``S_born`` and written to its own flat directory. Failed or incomplete
configurations are inventoried but cannot be plotted because they have no
validated result arrays.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(PROJECT_ROOT / ".mplconfig-sobol-flat-atlas"),
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collapse.anisotropic_sweep import BLUE, RED, RATIO  # noqa: E402
from collapse.detector_resonance import (  # noqa: E402
    DenseRingDetectorBuilder,
    DetectorSpec,
)


ROOT = PROJECT_ROOT
DEFAULT_SOURCE = ROOT / "work" / "zeus_sobol_coupling_scans_20260726_200003"
DEFAULT_OUTPUT = DEFAULT_SOURCE / "flat_ranked_1x6_by_n"
FAMILIES = ("jy_zero", "jy_nonzero")
DETECTOR_N = 8
GAP_FLOOR = 1.0e-12
VAB_POWER_FLOOR = 1.0e-12
VAB_AMPLITUDE_FLOOR = 1.0e-16
MODEL_BLUE = "#1f77b4"
MODEL_ORANGE = "#e68a00"


@dataclass(frozen=True)
class CaseRecord:
    family: str
    dynamics_n: int
    config_id: str
    s_born: float
    born_rmse: float
    hz: float
    j: float
    jpm: float
    jx: float
    jy: float
    source_dir: str
    rank: int = 0
    within_n_rank: int = 0
    output_path: str = ""

    @property
    def spectral_key(self) -> tuple[Any, ...]:
        return (
            self.family,
            self.config_id,
            self.hz,
            self.j,
            self.jpm,
            self.jx,
            self.jy,
        )


@dataclass(frozen=True)
class SpectralData:
    energies: np.ndarray
    normalized_gaps: np.ndarray
    vab_power: np.ndarray
    multiplicities: tuple[int, ...]
    multiplicity_two_pairs: np.ndarray
    multiplicity_two_couplings: np.ndarray
    degeneracy_tolerance: float
    validation: dict[str, float | bool]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _completed_case_dirs(n_dir: Path) -> Iterable[Path]:
    for path in sorted(n_dir.glob("config_*")):
        if path.is_dir() and (path / "COMPLETE.json").is_file():
            yield path


def inventory(source: Path) -> tuple[list[CaseRecord], list[dict[str, Any]]]:
    """Read all successfully completed records and inventory unavailable ones."""

    records: list[CaseRecord] = []
    unavailable: list[dict[str, Any]] = []
    for family in FAMILIES:
        family_dir = source / family
        if not family_dir.is_dir():
            unavailable.append({"family": family, "reason": "family directory missing"})
            continue
        n_dirs = sorted(
            (path for path in family_dir.glob("N*") if path.is_dir()),
            key=lambda path: int(path.name[1:]),
        )
        for n_dir in n_dirs:
            dynamics_n = int(n_dir.name[1:])
            all_dirs = sorted(path for path in n_dir.glob("config_*") if path.is_dir())
            for case_dir in all_dirs:
                required = (
                    case_dir / "metadata.json",
                    case_dir / "metrics.json",
                    case_dir / "results.npz",
                )
                if not all(path.is_file() for path in required):
                    unavailable.append(
                        {
                            "family": family,
                            "N": dynamics_n,
                            "config_id": case_dir.name,
                            "reason": "required result files missing",
                        }
                    )
                    continue
                metadata = _read_json(case_dir / "metadata.json")
                metrics = _read_json(case_dir / "metrics.json")
                config = metadata["configuration"]
                s_born = float(metrics["S_born"])
                if not math.isfinite(s_born):
                    unavailable.append(
                        {
                            "family": family,
                            "N": dynamics_n,
                            "config_id": case_dir.name,
                            "reason": "non-finite S_born",
                        }
                    )
                    continue
                records.append(
                    CaseRecord(
                        family=family,
                        dynamics_n=dynamics_n,
                        config_id=case_dir.name,
                        s_born=s_born,
                        born_rmse=float(metrics["born_RMSE_occupied"]),
                        hz=float(config["hz"]),
                        j=float(config["j"]),
                        jpm=float(config["jpm"]),
                        jx=float(config["jx"]),
                        jy=float(config["jy"]),
                        source_dir=str(case_dir.resolve()),
                    )
                )
    return records, unavailable


def _rank_records(records: Sequence[CaseRecord], output: Path) -> list[CaseRecord]:
    ranked: list[CaseRecord] = []
    for family in FAMILIES:
        sizes = sorted(
            {record.dynamics_n for record in records if record.family == family}
        )
        for dynamics_n in sizes:
            group_records = sorted(
                (
                    record
                    for record in records
                    if record.family == family and record.dynamics_n == dynamics_n
                ),
                key=lambda record: (-record.s_born, record.config_id),
            )
            for rank, record in enumerate(group_records, start=1):
                s_token = f"{record.s_born:.6f}".replace(".", "p")
                filename = (
                    f"rank_{rank:04d}__{record.config_id}__"
                    f"Sborn_{s_token}.png"
                )
                ranked.append(
                    CaseRecord(
                        **{
                            **asdict(record),
                            "rank": rank,
                            "within_n_rank": rank,
                            "output_path": str(
                                (
                                    output
                                    / family
                                    / f"N{dynamics_n:02d}"
                                    / filename
                                ).resolve()
                            ),
                        }
                    )
                )
    return ranked


def _collective_sy(n: int) -> np.ndarray:
    """Return ``sum_i sigma_i^y`` in the builder's computational basis."""

    dimension = 1 << n
    sy = np.zeros((dimension, dimension), dtype=np.complex128)
    for state in range(dimension):
        for site in range(n):
            bit = (state >> site) & 1
            target = state ^ (1 << site)
            sy[target, state] += 1j if bit == 0 else -1j
    if not np.allclose(sy, sy.conj().T, atol=1.0e-13):
        raise RuntimeError("constructed collective Sy is not Hermitian")
    return sy


def _degenerate_groups(energies: np.ndarray, tolerance: float) -> tuple[tuple[int, ...], ...]:
    groups: list[list[int]] = []
    for index, energy in enumerate(energies):
        if not groups or abs(float(energy - energies[groups[-1][0]])) > tolerance:
            groups.append([index])
        else:
            groups[-1].append(index)
    return tuple(tuple(group) for group in groups)


def compute_spectral(record: CaseRecord) -> SpectralData:
    """Build and fully diagonalize the ``N_D=8`` detector for one configuration."""

    operators = DenseRingDetectorBuilder().build(
        DetectorSpec(
            detector_n=DETECTOR_N,
            hz=record.hz,
            j=record.j,
            jpm=record.jpm,
        )
    )
    hamiltonian = np.asarray(operators.hamiltonian, dtype=np.complex128)
    sx = np.asarray(operators.coupling, dtype=np.complex128)
    sy = _collective_sy(DETECTOR_N)
    energies, vectors = np.linalg.eigh(hamiltonian)

    # In the central-qubit Z basis, <0|X|1>=1 and <0|Y|1>=-i.
    # Therefore the detector operator in the 0<-1 qubit-flip block is
    # V=(Jx*Sx-i*Jy*Sy)/sqrt(N_D).  The reverse block is V^\dagger.
    v_detector = (record.jx * sx - 1j * record.jy * sy) / math.sqrt(DETECTOR_N)
    vab = vectors.conj().T @ v_detector @ vectors

    energy_scale = max(float(np.ptp(energies)), 1.0)
    tolerance = max(1.0e-10, 1.0e-9 * energy_scale)
    groups = _degenerate_groups(energies, tolerance)
    multiplicities = tuple(len(group) for group in groups)

    gaps = np.abs(energies[:, None] - energies[None, :])
    normalized_gaps = gaps / energy_scale
    total_vab_power = max(float(np.sum(np.abs(vab) ** 2)), np.finfo(float).tiny)
    vab_power = np.abs(vab) ** 2 / total_vab_power
    vab_scale = math.sqrt(total_vab_power)
    multiplicity_two_pairs = np.asarray(
        [(group[0], group[1]) for group in groups if len(group) == 2],
        dtype=np.int64,
    ).reshape(-1, 2)
    multiplicity_two_couplings = np.asarray(
        [
            (
                abs(vab[a, b]) / vab_scale,
                abs(vab[a, a]) / vab_scale,
                abs(vab[b, b]) / vab_scale,
            )
            for a, b in multiplicity_two_pairs
        ],
        dtype=np.float64,
    ).reshape(-1, 3)

    identity = np.eye(energies.size)
    residual = hamiltonian @ vectors - vectors * energies[None, :]
    validation: dict[str, float | bool] = {
        "hamiltonian_hermiticity_max_abs": float(
            np.max(np.abs(hamiltonian - hamiltonian.conj().T))
        ),
        "eigenvector_orthonormality_max_abs": float(
            np.max(np.abs(vectors.conj().T @ vectors - identity))
        ),
        "eigenpair_residual_max_abs": float(np.max(np.abs(residual))),
        "eigenvalues_sorted": bool(np.all(np.diff(energies) >= -tolerance)),
        "vab_frobenius_consistency_rel": float(
            abs(np.sum(np.abs(vab) ** 2) - np.sum(np.abs(v_detector) ** 2))
            / max(np.sum(np.abs(v_detector) ** 2), np.finfo(float).tiny)
        ),
    }
    if (
        validation["hamiltonian_hermiticity_max_abs"] > 1.0e-11
        or validation["eigenvector_orthonormality_max_abs"] > 1.0e-10
        or validation["eigenpair_residual_max_abs"] > 1.0e-9
        or not validation["eigenvalues_sorted"]
        or validation["vab_frobenius_consistency_rel"] > 1.0e-10
    ):
        raise RuntimeError(f"spectral validation failed: {validation}")

    return SpectralData(
        energies=energies,
        normalized_gaps=normalized_gaps,
        vab_power=vab_power,
        multiplicities=multiplicities,
        multiplicity_two_pairs=multiplicity_two_pairs,
        multiplicity_two_couplings=multiplicity_two_couplings,
        degeneracy_tolerance=tolerance,
        validation=validation,
    )


def _wire_sphere(axis: Any) -> None:
    u = np.linspace(0.0, 2.0 * np.pi, 32)
    v = np.linspace(0.0, np.pi, 18)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    axis.plot_wireframe(
        x,
        y,
        z,
        color="0.74",
        linewidth=0.30,
        alpha=0.42,
        rstride=2,
        cstride=2,
    )


def _heatmap_panel(
    figure: plt.Figure,
    parent: Any,
    values: np.ndarray,
    *,
    title: str,
    cmap: str,
    vmin: float,
    vmax: float,
    colorbar_label: str,
) -> plt.Axes:
    subgrid = parent.subgridspec(1, 2, width_ratios=(1.0, 0.055), wspace=0.08)
    axis = figure.add_subplot(subgrid[0, 0])
    colorbar_axis = figure.add_subplot(subgrid[0, 1])
    image = axis.imshow(
        values,
        origin="lower",
        interpolation="nearest",
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        extent=(-0.5, values.shape[1] - 0.5, -0.5, values.shape[0] - 0.5),
        aspect="equal",
        rasterized=True,
    )
    axis.set_box_aspect(1)
    axis.set(
        title=title,
        xlabel="sorted eigenstate index $b$",
        ylabel="sorted eigenstate index $a$",
        xlim=(-0.5, values.shape[1] - 0.5),
        ylim=(-0.5, values.shape[0] - 0.5),
    )
    ticks = np.linspace(0, values.shape[0] - 1, 5, dtype=int)
    axis.set_xticks(ticks)
    axis.set_yticks(ticks)
    colorbar = figure.colorbar(image, cax=colorbar_axis)
    colorbar.set_label(colorbar_label, fontsize=7)
    colorbar_axis.tick_params(labelsize=6)
    return axis


def _multiplicity_panel(axis: plt.Axes, spectral: SpectralData) -> None:
    counts = Counter(spectral.multiplicities)
    multiplicities = np.asarray(sorted(counts), dtype=int)
    group_counts = np.asarray([counts[value] for value in multiplicities], dtype=int)
    axis.bar(
        multiplicities,
        group_counts,
        width=np.maximum(0.75, multiplicities * 0.0 + 0.75),
        color="#4c78a8",
        edgecolor="white",
        linewidth=0.45,
    )
    axis.set(
        title="Detector degeneracy multiplicities",
        xlabel="subspace multiplicity $m_g$",
        ylabel="number of energy subspaces",
    )
    axis.grid(axis="y", alpha=0.20)
    degenerate = [value for value in spectral.multiplicities if value > 1]
    degenerate_states = sum(degenerate)
    axis.text(
        0.97,
        0.96,
        "\n".join(
            (
                rf"$N_D={DETECTOR_N}$, $\dim={1 << DETECTOR_N}$",
                rf"$N_{{\rm groups}}={len(spectral.multiplicities)}$",
                rf"$N_{{m>1}}={len(degenerate)}$",
                rf"$m_{{\max}}={max(spectral.multiplicities)}$",
                rf"$f_{{\rm deg}}={degenerate_states / (1 << DETECTOR_N):.3f}$",
            )
        ),
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=7.1,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    if multiplicities.size > 8 or max(multiplicities) > 20:
        axis.set_xscale("log", base=2)
        axis.set_yscale("log")
    axis.set_box_aspect(1)


def _multiplicity_two_coupling_panel(
    axis: plt.Axes,
    spectral: SpectralData,
) -> None:
    """Plot solver-basis coupling magnitudes for all multiplicity-two blocks."""

    values = spectral.multiplicity_two_couplings
    pair_count = values.shape[0]
    axis.set(
        title=r"Couplings in $m_g=2$ subspaces",
        xlabel="multiplicity-two pair index",
        ylabel=r"$log_{10}(|V_{xy}|/|V|_F)$",
        ylim=(math.log10(VAB_AMPLITUDE_FLOOR), 0.0),
    )
    axis.grid(alpha=0.18)
    if pair_count == 0:
        axis.text(
            0.5,
            0.5,
            "No multiplicity-two\nenergy subspaces",
            transform=axis.transAxes,
            ha="center",
            va="center",
            fontsize=9,
        )
        axis.set_xlim(-0.5, 0.5)
        axis.set_box_aspect(1)
        return

    pair_index = np.arange(pair_count)
    display = np.log10(np.maximum(values, VAB_AMPLITUDE_FLOOR))
    axis.axhline(-12.0, color="0.45", linestyle=":", linewidth=0.8)
    series = (
        (0, r"$|V_{ab}|$", "o", "#2a6fbb", -0.18),
        (1, r"$|V_{aa}|$", "^", "#d1495b", 0.0),
        (2, r"$|V_{bb}|$", "s", "#2a9d8f", 0.18),
    )
    for column, label, marker_style, color, offset in series:
        axis.scatter(
            pair_index + offset,
            display[:, column],
            s=10,
            marker=marker_style,
            color=color,
            alpha=0.72,
            linewidths=0.0,
            label=label,
        )
    axis.set_xlim(-0.75, max(pair_count - 0.25, 0.75))
    axis.legend(frameon=False, fontsize=7.0, ncol=3, loc="lower center")
    axis.text(
        0.98,
        0.96,
        "\n".join(
            (
                rf"$N_{{m=2}}={pair_count}$",
                r"$a<b$ within each block",
                "solver eigenbasis",
                r"dotted: $10^{-12}$ guide",
            )
        ),
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=7.0,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    axis.set_box_aspect(1)


def _diagnostics_panel(
    figure: plt.Figure,
    parent: Any,
    arrays: dict[str, np.ndarray],
    record: CaseRecord,
) -> None:
    subgrid = parent.subgridspec(2, 1, height_ratios=(1.0, 0.90), hspace=0.28)
    axis_p = figure.add_subplot(subgrid[0, 0])
    axis_p.stairs(
        arrays["p_theta"],
        arrays["edges"],
        color=BLUE,
        linewidth=1.0,
        fill=True,
        alpha=0.19,
        label=r"$P(\theta)$",
    )
    axis_p.stairs(
        arrays["p_pi_minus_theta"],
        arrays["edges"],
        color=RED,
        linewidth=0.95,
        fill=True,
        alpha=0.14,
        label=r"$P(\pi-\theta)$",
    )
    axis_p.plot(
        arrays["fit_grid"],
        arrays["wg_density"],
        color=MODEL_BLUE,
        linewidth=0.95,
        label="WG",
    )
    axis_p.plot(
        arrays["fit_grid"],
        arrays["wc_density"],
        color=MODEL_ORANGE,
        linewidth=0.95,
        linestyle="--",
        label="WC",
    )
    axis_p.set(
        title="Dynamics diagnostics",
        ylabel="density",
        xlim=(0.0, np.pi),
    )
    axis_p.tick_params(labelbottom=False)
    axis_p.grid(alpha=0.16)
    axis_p.legend(ncol=2, frameon=False, fontsize=6.4, loc="upper center")

    axis_r = figure.add_subplot(subgrid[1, 0])
    occupied = arrays["R_occupied"].astype(bool)
    axis_r.plot(
        arrays["centers"][occupied],
        arrays["R"][occupied],
        "o-",
        color=RATIO,
        markersize=1.9,
        linewidth=0.75,
        label=r"$R(\theta)$",
    )
    axis_r.plot(
        arrays["centers"],
        arrays["R_born"],
        color="black",
        linestyle="--",
        linewidth=0.95,
        label=r"$\cos^2(\theta/2)$",
    )
    axis_r.set(
        xlabel=r"$\theta$",
        ylabel=r"$R(\theta)$",
        xlim=(0.0, np.pi),
        ylim=(-0.04, 1.04),
    )
    axis_r.grid(alpha=0.16)
    axis_r.legend(ncol=1, frameon=False, fontsize=6.4, loc="upper right")
    axis_r.text(
        0.04,
        0.08,
        rf"$S_{{\rm Born}}={record.s_born:.3f}$"
        + "\n"
        + rf"$\mathrm{{RMSE}}={record.born_rmse:.3f}$",
        transform=axis_r.transAxes,
        fontsize=7.0,
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1},
    )


def _bloch_panel(
    figure: plt.Figure,
    parent: Any,
    arrays: dict[str, np.ndarray],
    max_points: int,
) -> None:
    axis = figure.add_subplot(parent, projection="3d")
    _wire_sphere(axis)
    blue = arrays["bloch_blue"]
    red = arrays["bloch_red"]
    if blue.shape[0] > max_points:
        indices = np.linspace(0, blue.shape[0] - 1, max_points, dtype=int)
        blue = blue[indices]
        red = red[indices]
    axis.scatter(
        *blue.T,
        s=2.2,
        c=BLUE,
        alpha=0.34,
        depthshade=False,
        label=r"$v(\lambda)$",
    )
    axis.scatter(
        *red.T,
        s=2.2,
        c=RED,
        alpha=0.28,
        depthshade=False,
        label=r"$-v(\lambda)$",
    )
    axis.set(
        title="Bloch-sphere branches",
        xlim=(-1.04, 1.04),
        ylim=(-1.04, 1.04),
        zlim=(-1.04, 1.04),
    )
    axis.view_init(elev=22, azim=42)
    axis.set_box_aspect((1, 1, 1))
    axis.set_axis_off()
    axis.legend(frameon=False, fontsize=6.8, loc="upper left")


def _load_result_arrays(case_dir: Path) -> dict[str, np.ndarray]:
    required = (
        "edges",
        "centers",
        "p_theta",
        "p_pi_minus_theta",
        "R",
        "R_occupied",
        "R_born",
        "bloch_blue",
        "bloch_red",
        "fit_grid",
        "wg_density",
        "wc_density",
    )
    with np.load(case_dir / "results.npz") as archive:
        missing = [name for name in required if name not in archive.files]
        if missing:
            raise KeyError(f"{case_dir}: missing arrays {missing}")
        return {name: np.asarray(archive[name]) for name in required}


def _render_case(
    record: CaseRecord,
    spectral: SpectralData,
    *,
    force: bool,
    dpi: int,
    max_bloch_points: int,
) -> dict[str, Any]:
    output = Path(record.output_path)
    if output.is_file() and not force:
        return {
            **asdict(record),
            "status": "existing",
            "degeneracy_tolerance": spectral.degeneracy_tolerance,
            "multiplicity_two_pair_count": int(
                spectral.multiplicity_two_pairs.shape[0]
            ),
            "spectral_validation": spectral.validation,
        }

    arrays = _load_result_arrays(Path(record.source_dir))
    output.parent.mkdir(parents=True, exist_ok=True)

    figure = plt.figure(figsize=(30.0, 5.75), dpi=dpi, constrained_layout=False)
    grid = figure.add_gridspec(
        1,
        6,
        left=0.022,
        right=0.994,
        bottom=0.12,
        top=0.84,
        wspace=0.27,
        width_ratios=(1, 1, 1, 1, 1, 1),
    )

    gap_display = -np.log10(np.maximum(spectral.normalized_gaps, GAP_FLOOR))
    np.fill_diagonal(gap_display, np.nan)
    gap_cmap = plt.get_cmap("magma").copy()
    gap_cmap.set_bad("white")
    gap_axis = _heatmap_panel(
        figure,
        grid[0, 0],
        gap_display,
        title=rf"Energy proximity ($N_D={DETECTOR_N}$)",
        cmap=gap_cmap,
        vmin=0.0,
        vmax=-math.log10(GAP_FLOOR),
        colorbar_label=r"$-\log_{10}(|E_a-E_b|/\Delta E)$",
    )
    vab_axis = _heatmap_panel(
        figure,
        grid[0, 1],
        np.log10(np.maximum(spectral.vab_power, VAB_POWER_FLOOR)),
        title=rf"Interaction $V_{{ab}}$ ($N_D={DETECTOR_N}$)",
        cmap="viridis",
        vmin=math.log10(VAB_POWER_FLOOR),
        vmax=0.0,
        colorbar_label=r"$\log_{10}(|V_{ab}|^2/\mathrm{Tr}\,VV^\dagger)$",
    )
    # Explicit geometry assertion: the two requested heatmap data axes must
    # occupy the same physical box and use the same index limits/aspect.
    figure.canvas.draw()
    gap_box = gap_axis.get_position()
    vab_box = vab_axis.get_position()
    if not (
        abs(gap_box.width - vab_box.width) < 1.0e-8
        and abs(gap_box.height - vab_box.height) < 1.0e-8
        and np.allclose(gap_axis.get_xlim(), vab_axis.get_xlim())
        and np.allclose(gap_axis.get_ylim(), vab_axis.get_ylim())
        and gap_axis.get_aspect() == vab_axis.get_aspect()
    ):
        raise RuntimeError("heatmap geometry assertion failed")

    multiplicity_axis = figure.add_subplot(grid[0, 2])
    _multiplicity_panel(multiplicity_axis, spectral)
    coupling_axis = figure.add_subplot(grid[0, 3])
    _multiplicity_two_coupling_panel(coupling_axis, spectral)
    _diagnostics_panel(figure, grid[0, 4], arrays, record)
    _bloch_panel(figure, grid[0, 5], arrays, max_bloch_points)

    family_label = r"$J_y=0$" if record.family == "jy_zero" else r"$J_y>0$"
    figure.suptitle(
        (
            rf"Born rank {record.rank}: {family_label}, dynamics $N={record.dynamics_n}$, "
            rf"{record.config_id}, $S_{{\rm Born}}={record.s_born:.4f}$"
            + "\n"
            + rf"$h_z={record.hz:.3g}$, $J={record.j:.3g}$, "
            + rf"$J_\pm={record.jpm:.3g}$, $J_x={record.jx:.3g}$, "
            + rf"$J_y={record.jy:.3g}$, $t=10^6$"
        ),
        fontsize=12.5,
        fontweight="bold",
        y=0.975,
    )
    temp = output.with_name(output.stem + f".tmp.{os.getpid()}.png")
    figure.savefig(temp, dpi=dpi, facecolor="white")
    plt.close(figure)
    temp.replace(output)
    return {
        **asdict(record),
        "status": "rendered",
        "image_width_px": int(round(30.0 * dpi)),
        "image_height_px": int(round(5.75 * dpi)),
        "heatmap_box_width": gap_box.width,
        "heatmap_box_height": gap_box.height,
        "degeneracy_tolerance": spectral.degeneracy_tolerance,
        "multiplicity_two_pair_count": int(
            spectral.multiplicity_two_pairs.shape[0]
        ),
        "spectral_validation": spectral.validation,
    }


def _render_group(
    record_payloads: Sequence[dict[str, Any]],
    *,
    force: bool,
    dpi: int,
    max_bloch_points: int,
) -> list[dict[str, Any]]:
    records = [CaseRecord(**payload) for payload in record_payloads]
    reference = records[0]
    for record in records[1:]:
        if record.spectral_key != reference.spectral_key:
            raise ValueError("grouped records do not share detector/coupling parameters")
    spectral = compute_spectral(reference)
    return [
        _render_case(
            record,
            spectral,
            force=force,
            dpi=dpi,
            max_bloch_points=max_bloch_points,
        )
        for record in records
    ]


def _write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _write_outputs(
    output: Path,
    source: Path,
    records: Sequence[CaseRecord],
    unavailable: Sequence[dict[str, Any]],
    results: Sequence[dict[str, Any]],
) -> None:
    index_fields = (
        "family",
        "rank",
        "within_n_rank",
        "dynamics_n",
        "config_id",
        "s_born",
        "born_rmse",
        "hz",
        "j",
        "jpm",
        "jx",
        "jy",
        "source_dir",
        "output_path",
    )
    by_group: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_group[(record.family, record.dynamics_n)].append(asdict(record))
    for (family, dynamics_n), rows in sorted(by_group.items()):
        _write_csv(
            output / family / f"N{dynamics_n:02d}" / "ranked_index.csv",
            sorted(rows, key=lambda row: int(row["rank"])),
            index_fields,
        )

    _write_csv(
        output / "unavailable_cases.csv",
        list(unavailable),
        ("family", "N", "config_id", "reason"),
    )
    result_path = output / "render_manifest.json"
    result_path.write_text(
        json.dumps(
            {
                "source": str(source.resolve()),
                "output": str(output.resolve()),
                "detector_n": DETECTOR_N,
                "vab_definition": (
                    "V=(Jx*sum_i X_i - i*Jy*sum_i Y_i)/sqrt(N_D), "
                    "the <0|H_int|1> detector block; plotted as "
                    "log10(|V_ab|^2/Tr(V V^dagger)) in the sorted detector-energy basis"
                ),
                "energy_gap_definition": (
                    "-log10(max(|E_a-E_b|/(E_max-E_min),1e-12)); "
                    "the diagonal is displayed as missing/white"
                ),
                "degeneracy_definition": (
                    "adjacent sorted energies grouped when their difference is <= "
                    "max(1e-10,1e-9*max(E_max-E_min,1))"
                ),
                "rank_definition": (
                    "independent within each (Jy family, dynamics N) directory, "
                    "descending S_born"
                ),
                "multiplicity_two_coupling_definition": (
                    "for every detected multiplicity-two group (a,b), a<b, plot "
                    "log10(|V_ab|/||V||_F), log10(|V_aa|/||V||_F), and "
                    "log10(|V_bb|/||V||_F) in the solver-produced energy eigenbasis"
                ),
                "completed_records": len(records),
                "unavailable_transferred_records": len(unavailable),
                "family_counts": dict(Counter(record.family for record in records)),
                "n_counts": {
                    family: dict(
                        Counter(
                            str(record.dynamics_n)
                            for record in records
                            if record.family == family
                        )
                    )
                    for family in FAMILIES
                },
                "results": list(results),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    readme = [
        "# Flat per-N Born-ranked Sobol coupling atlas",
        "",
        f"Source: `{source.resolve()}`",
        "",
        "Every `(Jy family, N)` combination has its own flat directory. "
        "Within that directory, filenames begin with the rank obtained by "
        "sorting the usable results by decreasing `S_born`. This includes all "
        "usable partial `N=16` results found at generation time.",
        "",
        "Each 1x6 figure contains, from left to right:",
        "",
        "1. normalized minus-log detector energy gaps at `N_D=8`;",
        "2. the normalized energy-basis coupling power for "
        "`V=(Jx Sx-i Jy Sy)/sqrt(N_D)`;",
        "3. the multiplicity histogram of detector energy subspaces;",
        "4. normalized `|Vab|`, `|Vaa|`, and `|Vbb|` for every "
        "multiplicity-two detector subspace;",
        "5. `P(theta)`, `P(pi-theta)`, WG/WC fits, and `R(theta)` vs Born;",
        "6. the two Bloch-sphere point branches.",
        "",
        f"Rendered records: **{len(records)}**.",
        f"Unavailable/incomplete transferred case directories: **{len(unavailable)}**.",
        "",
        "See `ranked_index.csv` in each `family/N` directory and "
        "`render_manifest.json` for exact parameters, validation, and paths.",
        "",
    ]
    (output / "README.md").write_text("\n".join(readme), encoding="utf-8")


def build(
    *,
    source: Path,
    output: Path,
    workers: int,
    force: bool,
    dpi: int,
    max_bloch_points: int,
    limit: int | None,
) -> list[dict[str, Any]]:
    records, unavailable = inventory(source)
    ranked = _rank_records(records, output)
    if limit is not None:
        selected: list[CaseRecord] = []
        for family in FAMILIES:
            sizes = sorted(
                {
                    record.dynamics_n
                    for record in ranked
                    if record.family == family
                }
            )
            for dynamics_n in sizes:
                selected.extend(
                    sorted(
                        (
                            record
                            for record in ranked
                            if record.family == family
                            and record.dynamics_n == dynamics_n
                        ),
                        key=lambda record: record.rank,
                    )[:limit]
                )
        ranked = selected

    groups: dict[tuple[Any, ...], list[CaseRecord]] = defaultdict(list)
    for record in ranked:
        groups[record.spectral_key].append(record)
    for group in groups.values():
        group.sort(key=lambda record: (record.dynamics_n, record.rank))

    results: list[dict[str, Any]] = []
    if workers <= 1:
        for group in groups.values():
            results.extend(
                _render_group(
                    [asdict(record) for record in group],
                    force=force,
                    dpi=dpi,
                    max_bloch_points=max_bloch_points,
                )
            )
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    _render_group,
                    [asdict(record) for record in group],
                    force=force,
                    dpi=dpi,
                    max_bloch_points=max_bloch_points,
                ): group[0].spectral_key
                for group in groups.values()
            }
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results.extend(future.result())
                except Exception as error:
                    raise RuntimeError(f"rendering failed for spectral key {key}") from error

    results.sort(key=lambda row: (str(row["family"]), int(row["dynamics_n"]), int(row["rank"])))
    _write_outputs(output, source, ranked, unavailable, results)
    return results


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--workers",
        type=int,
        default=min(8, max(1, os.cpu_count() or 1)),
    )
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--max-bloch-points", type=int, default=6000)
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="For smoke tests, render this many highest-ranked records per family and N.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    results = build(
        source=args.source.resolve(),
        output=args.output.resolve(),
        workers=max(1, args.workers),
        force=args.force,
        dpi=max(80, args.dpi),
        max_bloch_points=max(100, args.max_bloch_points),
        limit=args.limit,
    )
    counts = Counter(str(row["family"]) for row in results)
    print(
        f"Rendered/indexed {len(results)} figures in {args.output.resolve()} "
        f"({dict(counts)})."
    )


if __name__ == "__main__":
    main()
