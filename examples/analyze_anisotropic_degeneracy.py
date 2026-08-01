"""Relate detector and total-Hamiltonian degeneracy to anisotropic outcomes."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.anisotropic_analysis import DetectorDegeneracyCalculator  # noqa: E402
from collapse.anisotropic_sweep import AnisotropicSweepConfig  # noqa: E402
from collapse.detector_resonance import DenseRingDetectorBuilder, DetectorSpec  # noqa: E402


def _calculate(values: tuple[int, float, float, float]) -> dict[str, Any]:
    detector_n, hz, j, jpm = values
    metric = DetectorDegeneracyCalculator().calculate(DetectorSpec(detector_n, hz, j, jpm))
    return asdict(metric)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _read_spectrum_rows(path: Path, detector_n: int) -> dict[tuple[float, float, float], dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {
        (float(row["hz"]), float(row["J"]), float(row["Jpm"])): row
        for row in rows
        if int(row["detector_n"]) == detector_n
    }


def _correlation(rows: list[dict[str, Any]], left: str, right: str) -> dict[str, Any]:
    x = np.asarray([float(row[left]) for row in rows], dtype=float)
    y = np.asarray([float(row[right]) for row in rows], dtype=float)
    finite = np.isfinite(x) & np.isfinite(y)
    result = spearmanr(x[finite], y[finite])
    return {
        "left": left,
        "right": right,
        "sample_count": int(np.count_nonzero(finite)),
        "spearman_rho": float(result.statistic),
        "two_sided_p_value": float(result.pvalue),
    }


def _validate_total_doublets(specs: list[DetectorSpec], collective_jx: float) -> list[dict[str, Any]]:
    builder = DenseRingDetectorBuilder()
    rows: list[dict[str, Any]] = []
    for spec in specs:
        operators = builder.build(spec)
        edge = collective_jx / math.sqrt(spec.detector_n)
        plus = np.linalg.eigvalsh(operators.hamiltonian + edge * operators.coupling)
        minus = np.linalg.eigvalsh(operators.hamiltonian - edge * operators.coupling)
        rows.append(
            {
                "detector_n": spec.detector_n,
                "hz": spec.hz,
                "J": spec.j,
                "Jpm": spec.jpm,
                "maximum_paired_spectrum_error": float(np.max(np.abs(plus - minus))),
                "interpretation": "H_+ and H_- are unitarily related by detector Z parity; total-H eigenvalues are exact doublets",
            }
        )
    return rows


def _plot_heatmaps(rows: list[dict[str, Any]], config: AnisotropicSweepConfig, root: Path) -> list[str]:
    output: list[str] = []
    for hz in config.hz_values:
        matrix = np.full((len(config.jpm_values), len(config.j_values)), np.nan)
        for row in rows:
            if math.isclose(float(row["hz"]), hz, abs_tol=1e-12):
                y = config.jpm_values.index(float(row["Jpm"]))
                x = config.j_values.index(float(row["J"]))
                matrix[y, x] = float(row["active_zero_gap_weight_fraction"])
        fig, axis = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
        image = axis.imshow(matrix, origin="lower", aspect="auto", cmap="magma", vmin=0.0, vmax=max(0.05, float(np.nanmax(matrix))))
        axis.set_xticks(range(len(config.j_values)), [f"{value:g}" for value in config.j_values], rotation=45, ha="right")
        axis.set_yticks(range(len(config.jpm_values)), [f"{value:g}" for value in config.jpm_values])
        axis.set(xlabel=r"$J$", ylabel=r"$J_{\pm}$", title=rf"Active detector degeneracy, $N=8$, $h_z={hz:g}$")
        fig.colorbar(image, ax=axis, pad=0.02, label=r"$\sum_E\|P_E V P_E\|_F^2 / \mathrm{Tr}(V^2)$")
        path = root / f"active_detector_degeneracy_hz_{hz:+g}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=190)
        plt.close(fig)
        output.append(str(path))
    return output


def _plot_relationship(joined: list[dict[str, Any]], path: Path) -> str:
    active = np.asarray([float(row["active_zero_gap_weight_fraction"]) for row in joined])
    born = np.asarray([float(row["S_born"]) for row in joined])
    alpha = np.asarray([float(row["theta_power_law_alpha"]) for row in joined])
    resolved = np.asarray([
        float(row["theta_power_law_js"]) <= 0.10
        and float(row["angular_bin_coverage"]) >= 0.50
        and float(row["theta_power_law_log10_span"]) >= 1.0
        for row in joined
    ])
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), constrained_layout=True)
    axes[0].scatter(active, born, s=18, alpha=0.55, color="#2563eb", edgecolors="none")
    axes[1].scatter(active[~resolved], alpha[~resolved], s=12, alpha=0.18, color="#9ca3af", edgecolors="none")
    axes[1].scatter(active[resolved], alpha[resolved], s=18, alpha=0.55, color="#c2410c", edgecolors="none")
    axes[0].set(ylabel=r"$S_{\rm Born}$", title="Born similarity")
    axes[1].set(ylabel=r"periodic power-law exponent $\alpha$", title="Power-law exponent")
    for axis in axes:
        axis.set(xlabel="active zero-gap detector weight")
        axis.grid(alpha=0.2)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190)
    plt.close(fig)
    return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.json"))
    parser.add_argument("--spectrum-metrics", type=Path, default=Path("reports/anisotropic_parameter_study_2026-07-21/data/spectrum_metrics.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/anisotropic_parameter_study_2026-07-21"))
    parser.add_argument("--detector-n", type=int, default=8)
    parser.add_argument("--join-n", type=int, default=14)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    config = AnisotropicSweepConfig.from_json(args.config)
    work = [(args.detector_n, hz, j, jpm) for hz in config.hz_values for j in config.j_values for jpm in config.jpm_values]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        degeneracy = list(pool.map(_calculate, work, chunksize=8))
    degeneracy.sort(key=lambda row: (row["hz"], row["J"], row["Jpm"]))
    dynamics = _read_spectrum_rows(args.spectrum_metrics, args.join_n)
    joined: list[dict[str, Any]] = []
    for row in degeneracy:
        key = (float(row["hz"]), float(row["J"]), float(row["Jpm"]))
        if key in dynamics:
            joined.append(row | {name: dynamics[key][name] for name in (
                "S_born", "born_rmse", "angular_bin_coverage", "theta_power_law_alpha",
                "theta_power_law_js", "theta_power_law_log10_span",
                "tail_density_exponent", "radius_q99_over_q50", "reciprocity_error", "phi_harmonic_2",
            )})

    data_root = args.output / "data"
    _write_csv(data_root / "detector_degeneracy_N08.csv", degeneracy)
    _write_csv(data_root / "degeneracy_join_N08_to_dynamics_N14.csv", joined)
    representative = [
        DetectorSpec(args.detector_n, -0.01, 0.75, 0.5),
        DetectorSpec(args.detector_n, -0.01, 0.5, 0.1),
        DetectorSpec(args.detector_n, -2.0, 1.0, 0.05),
        DetectorSpec(args.detector_n, -2.01, 0.5, 0.05),
        DetectorSpec(args.detector_n, 0.0, 0.0, 0.1),
    ]
    total_doublets = _validate_total_doublets(representative, config.jx)
    _write_csv(data_root / "total_hamiltonian_doublet_validation.csv", total_doublets)
    correlations = [
        _correlation(joined, "active_zero_gap_weight_fraction", "S_born"),
        _correlation(joined, "active_zero_gap_weight_fraction", "theta_power_law_alpha"),
        _correlation(joined, "detector_degenerate_state_fraction", "S_born"),
        _correlation(joined, "detector_degenerate_state_fraction", "theta_power_law_alpha"),
    ]
    active = [row for row in joined if float(row["active_zero_gap_weight_fraction"]) > 1e-12]
    born_like = [row for row in joined if float(row["S_born"]) >= 0.75 and float(row["born_rmse"]) <= 0.15 and float(row["angular_bin_coverage"]) >= 0.50]
    resolved = [
        row for row in joined
        if float(row["theta_power_law_js"]) <= 0.10
        and float(row["angular_bin_coverage"]) >= 0.50
        and float(row["theta_power_law_log10_span"]) >= 1.0
    ]
    heatmaps = _plot_heatmaps(degeneracy, config, args.output / "figures" / "degeneracy_heatmaps")
    relationship = _plot_relationship(joined, args.output / "figures" / "degeneracy_relationship.png")
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "detector_grid_n": args.detector_n,
        "dynamics_join_n": args.join_n,
        "grid_points": len(joined),
        "active_detector_degeneracy_points": len(active),
        "born_like_points": len(born_like),
        "resolved_power_law_points": len(resolved),
        "born_like_with_active_detector_degeneracy": sum(float(row["active_zero_gap_weight_fraction"]) > 1e-12 for row in born_like),
        "resolved_power_law_with_active_detector_degeneracy": sum(float(row["active_zero_gap_weight_fraction"]) > 1e-12 for row in resolved),
        "correlations": correlations,
        "total_hamiltonian_doublet_validation": total_doublets,
        "analytic_total_degeneracy": (
            "At hz0=0, total H splits in the X0 basis into H_D +/- (Jx/sqrt(N))V. "
            "Detector Z parity commutes with H_D and anticommutes with V, so the two blocks are unitarily equivalent. "
            "Every total-H eigenvalue is therefore at least doubly degenerate for every J,Jpm,hz in this campaign."
        ),
        "heatmaps": heatmaps,
        "relationship_figure": relationship,
    }
    (data_root / "degeneracy_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
