"""Compact symmetry-resolved detector level-spacing summaries."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from core.graph_spectral_sectors import (  # noqa: E402
    largest_detector_symmetry_sectors,
)
from core.level_spacing import (  # noqa: E402
    compute_level_spacing_ratios,
    compute_level_spacings,
    compute_unfolded_spacings,
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)
from core.sobol_coupling_scan import (  # noqa: E402
    _atomic_json,
    _atomic_npz,
    _sha256,
    timestamp,
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return payload


def _complete_valid(case_dir: Path) -> bool:
    marker_path = case_dir / "detector_spacing_COMPLETE.json"
    if not marker_path.is_file():
        return False
    try:
        marker = _read_json(marker_path)
        return marker.get("status") == "complete" and all(
            (case_dir / name).is_file()
            and _sha256(case_dir / name) == expected
            for name, expected in marker["files"].items()
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def save_detector_spacing_summary(
    case_dir: Path,
    *,
    n_nodes: int,
    edges: Iterable[tuple[int, int]],
    hz: float,
    j: float,
    jpm: float,
    sector_count: int = 4,
    histogram_bins: int = 32,
    resume: bool = True,
) -> dict[str, Any]:
    """Resolve detector symmetries and save histogram-level spectral evidence.

    The full sector spectra and unfolded-spacing samples exist only in memory.
    Persisted arrays contain histogram counts, plotting densities, and ensemble
    references; JSON records the exact sector construction and scalar metrics.
    """

    case_dir = Path(case_dir)
    if sector_count < 1:
        raise ValueError("sector_count must be positive")
    if histogram_bins < 8:
        raise ValueError("histogram_bins must be at least eight")
    if resume and _complete_valid(case_dir):
        return {
            "status": "resumed",
            "marker": str(case_dir / "detector_spacing_COMPLETE.json"),
        }

    canonical_edges = tuple(
        sorted(tuple(sorted((int(left), int(right)))) for left, right in edges)
    )
    sectors, symmetry = largest_detector_symmetry_sectors(
        n_nodes,
        canonical_edges,
        hz=hz,
        j=j,
        jpm=jpm,
        count=sector_count,
    )
    archive: dict[str, np.ndarray] = {}
    records: list[dict[str, Any]] = []
    for index, sector in enumerate(sectors):
        scale = max(float(np.ptp(sector.energies)), 1.0)
        tolerance = max(1.0e-10, 1.0e-9 * scale)
        unfolded = compute_unfolded_spacings(
            sector.energies,
            tol=tolerance,
            degree=3,
            trim_fraction=0.10,
        )
        raw_spacings = compute_level_spacings(sector.energies, tol=tolerance)
        ratios = compute_level_spacing_ratios(raw_spacings)
        if unfolded.size == 0 or ratios.size == 0:
            raise RuntimeError(
                f"sector {index} is too small for spacing diagnostics"
            )
        histogram_max = max(4.0, float(np.percentile(unfolded, 99.5)))
        bin_edges = np.linspace(0.0, histogram_max, histogram_bins + 1)
        counts, _ = np.histogram(unfolded, bins=bin_edges)
        in_range = int(np.sum(counts))
        if in_range == 0:
            raise RuntimeError(f"sector {index} has no in-range spacings")
        widths = np.diff(bin_edges)
        density = counts / (in_range * widths)
        centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        poisson = poisson_spacing_distribution(centers)
        goe = wigner_spacing_distribution(centers, beta=1)
        prefix = f"sector_{index:02d}"
        archive.update(
            {
                f"{prefix}__edges": bin_edges,
                f"{prefix}__counts": counts.astype(np.int64),
                f"{prefix}__density": density,
                f"{prefix}__poisson": poisson,
                f"{prefix}__goe": goe,
            }
        )
        records.append(
            {
                "key": prefix,
                "hamming_weight": sector.hamming_weight,
                "sector_index": sector.sector_index,
                "dimension": sector.dimension,
                "symmetry_label": sector.symmetry_label,
                "equivalent_copy_count": sector.equivalent_copy_count,
                "group_algebra_eigenvalue": sector.group_algebra_eigenvalue,
                "spectral_tolerance": tolerance,
                "raw_spacing_count": int(raw_spacings.size),
                "ratio_count": int(ratios.size),
                "unfolded_spacing_count": int(unfolded.size),
                "histogram_in_range_count": in_range,
                "histogram_overflow_count": int(unfolded.size - in_range),
                "mean_adjacent_gap_ratio": float(np.mean(ratios)),
                "histogram_l1_poisson": float(
                    np.sum(np.abs(density - poisson) * widths)
                ),
                "histogram_l1_goe": float(
                    np.sum(np.abs(density - goe) * widths)
                ),
            }
        )

    case_dir.mkdir(parents=True, exist_ok=True)
    archive_path = case_dir / "detector_spacing_summary.npz"
    metadata_path = case_dir / "detector_spacing_metadata.json"
    figure_path = case_dir / "detector_spacing_histograms.png"
    _atomic_npz(archive_path, **archive)
    _atomic_json(
        metadata_path,
        {
            "schema_version": 1,
            "created": timestamp(),
            "observable": "symmetry-resolved detector-only level spacings",
            "hamiltonian": (
                "H_D=-hz sum_i Z_i-J sum_(ij) Z_i Z_j-"
                "Jpm sum_(ij)(sigma_i^+ sigma_j^-+h.c.)"
            ),
            "parameters": {
                "N": n_nodes,
                "hz": hz,
                "J": j,
                "Jpm": jpm,
                "edges_zero_based": [list(edge) for edge in canonical_edges],
            },
            "symmetry_resolution": symmetry,
            "sector_selection": (
                f"{sector_count} largest nonredundant exact sectors after fixed "
                "Hamming weight, complete graph automorphisms, and half-filling "
                "spin reversal where applicable"
            ),
            "unfolding": {
                "method": "cubic staircase with local-spacing fallback",
                "degree": 3,
                "trim_fraction": 0.10,
                "tolerance_rule": "max(1e-10, 1e-9 * max(energy range, 1))",
            },
            "histogram": {
                "bin_count": histogram_bins,
                "upper_edge_rule": "max(4, 99.5th percentile per sector)",
                "density_rule": "counts / (in-range count * bin width)",
            },
            "storage": {
                "saved": (
                    "per-sector histogram edges, exact counts, densities, "
                    "Poisson/GOE reference samples, symmetry metadata, and metrics"
                ),
                "omitted": [
                    "detector sector eigenvalues",
                    "raw level spacings",
                    "unfolded level spacings",
                    "adjacent-gap-ratio samples",
                ],
                "reproduction_note": (
                    "The exact Hamiltonian parameters, graph edge list, symmetry "
                    "construction, tolerances, unfolding rule, and histogram rule "
                    "are retained. Individual spectra require rerunning the "
                    "defining committed code."
                ),
            },
            "sectors": records,
        },
    )

    figure, axes = plt.subplots(2, 2, figsize=(10.5, 7.6), squeeze=False)
    for axis, record in zip(axes.flat, records, strict=True):
        prefix = str(record["key"])
        edges_array = archive[f"{prefix}__edges"]
        centers = 0.5 * (edges_array[:-1] + edges_array[1:])
        axis.bar(
            centers,
            archive[f"{prefix}__density"],
            width=0.92 * np.diff(edges_array),
            color="#8ecae6",
            edgecolor="white",
            linewidth=0.35,
            label="data",
        )
        axis.plot(centers, archive[f"{prefix}__poisson"], "--", label="Poisson")
        axis.plot(centers, archive[f"{prefix}__goe"], "-", label="GOE")
        axis.set_title(
            f"{record['symmetry_label']}; dim={record['dimension']}\n"
            + rf"$\langle r\rangle={record['mean_adjacent_gap_ratio']:.3f}$, "
            + rf"$L_1^{{GOE}}={record['histogram_l1_goe']:.3f}$"
        )
        axis.set_xlabel("unfolded spacing s")
        axis.set_ylabel("density")
        axis.set_xlim(0.0, float(edges_array[-1]))
        axis.legend(fontsize=8)
    figure.suptitle(f"Detector-only symmetry-resolved spacings, N={n_nodes}")
    figure.tight_layout()
    temporary = figure_path.with_name(figure_path.stem + f".tmp.{os.getpid()}.png")
    figure.savefig(temporary, dpi=170, facecolor="white")
    plt.close(figure)
    temporary.replace(figure_path)

    files = (archive_path.name, metadata_path.name, figure_path.name)
    marker_path = case_dir / "detector_spacing_COMPLETE.json"
    _atomic_json(
        marker_path,
        {
            "status": "complete",
            "completed": timestamp(),
            "files": {name: _sha256(case_dir / name) for name in files},
        },
    )
    return {
        "status": "success",
        "marker": str(marker_path),
        "files": {name: _sha256(case_dir / name) for name in files},
    }
