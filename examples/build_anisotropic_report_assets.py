"""Build report-ready anisotropic summaries from the analyzed spectrum table."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.anisotropic_sweep import (  # noqa: E402
    AnisotropicCase,
    AnisotropicRepository,
    AnisotropicSweepConfig,
)


NUMERIC_FIELDS = {
    "detector_n", "hz", "J", "Jpm", "S_born", "born_rmse",
    "angular_bin_coverage", "S_wrapped_heavy", "tail_density_exponent",
    "radius_q99_over_q50", "radius_atomic_fraction", "reciprocity_error",
    "phi_harmonic_2", "wrapped_gaussian_js", "wrapped_cauchy_js",
    "theta_power_law_alpha", "theta_power_law_js",
    "theta_power_law_log_likelihood_per_sample", "theta_power_law_log10_span",
}


@dataclass(frozen=True)
class Gates:
    born_score: float = 0.75
    born_rmse: float = 0.15
    coverage: float = 0.50
    power_law_js: float = 0.10
    power_law_span: float = 1.00

    def born(self, row: dict[str, Any]) -> bool:
        return row["S_born"] >= self.born_score and row["born_rmse"] <= self.born_rmse and row["angular_bin_coverage"] >= self.coverage

    def resolved_power_law(self, row: dict[str, Any]) -> bool:
        return (
            math.isfinite(row["theta_power_law_alpha"])
            and row["theta_power_law_js"] <= self.power_law_js
            and row["angular_bin_coverage"] >= self.coverage
            and row["theta_power_law_log10_span"] >= self.power_law_span
        )


def _read(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for field in NUMERIC_FIELDS:
            row[field] = int(row[field]) if field == "detector_n" else float(row[field])
    return rows


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _groups(rows: Iterable[dict[str, Any]], fields: tuple[str, ...]) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    output: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        output.setdefault(tuple(row[field] for field in fields), []).append(row)
    return output


def _plot_alpha_heatmaps(
    rows: list[dict[str, Any]],
    config: AnisotropicSweepConfig,
    root: Path,
) -> list[str]:
    output: list[str] = []
    for (detector_n, hz), group in sorted(_groups(rows, ("detector_n", "hz")).items()):
        matrix = np.full((len(config.jpm_values), len(config.j_values)), np.nan)
        for row in group:
            matrix[config.jpm_values.index(row["Jpm"]), config.j_values.index(row["J"])] = row["theta_power_law_alpha"]
        fig, axis = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
        image = axis.imshow(matrix, origin="lower", aspect="auto", cmap="RdYlGn_r", vmin=0.0, vmax=4.0)
        axis.set_xticks(range(len(config.j_values)), [f"{value:g}" for value in config.j_values], rotation=45, ha="right")
        axis.set_yticks(range(len(config.jpm_values)), [f"{value:g}" for value in config.jpm_values])
        axis.set(xlabel=r"$J$", ylabel=r"$J_{\pm}$", title=rf"Periodic power-law exponent, $N={detector_n}$, $h_z={hz:g}$")
        fig.colorbar(image, ax=axis, pad=0.02, extend="max", label=r"$\alpha$ in $P(\theta)\propto d_{2\pi}(\theta,0)^{-\alpha}$")
        path = root / f"theta_power_law_alpha_N{detector_n:02d}_hz_{hz:+g}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=190)
        plt.close(fig)
        output.append(str(path))
    return output


def _plot_clean_born_heatmaps(
    rows: list[dict[str, Any]],
    config: AnisotropicSweepConfig,
    root: Path,
) -> list[str]:
    """Re-render source Born scores without cell text or diagonal markers."""

    output: list[str] = []
    for (detector_n, hz), group in sorted(_groups(rows, ("detector_n", "hz")).items()):
        matrix = np.full((len(config.jpm_values), len(config.j_values)), np.nan)
        for row in group:
            matrix[config.jpm_values.index(row["Jpm"]), config.j_values.index(row["J"])] = row["S_born"]
        fig, axis = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
        image = axis.imshow(matrix, origin="lower", aspect="auto", cmap="RdYlGn", vmin=0.0, vmax=1.0)
        axis.set_xticks(range(len(config.j_values)), [f"{value:g}" for value in config.j_values], rotation=45, ha="right")
        axis.set_yticks(range(len(config.jpm_values)), [f"{value:g}" for value in config.jpm_values])
        axis.set(xlabel=r"$J$", ylabel=r"$J_{\pm}$", title=rf"Born similarity, $N={detector_n}$, $h_z={hz:g}$")
        fig.colorbar(image, ax=axis, pad=0.02, label=r"$S_{\rm Born}$ (0: red, 1: green)")
        path = root / f"S_born_clean_N{detector_n:02d}_hz_{hz:+g}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=190)
        plt.close(fig)
        output.append(str(path))
    return output


def _finite_size(rows: list[dict[str, Any]], gates: Gates) -> list[dict[str, Any]]:
    complete = [row for row in rows if row["detector_n"] <= 14]
    output: list[dict[str, Any]] = []
    for (hz, j, jpm), group in sorted(_groups(complete, ("hz", "J", "Jpm")).items()):
        if len(group) != 4:
            continue
        output.append(
            {
                "hz": hz,
                "J": j,
                "Jpm": jpm,
                "born_sizes": sum(gates.born(row) for row in group),
                "resolved_power_law_sizes": sum(gates.resolved_power_law(row) for row in group),
                "mean_S_born": float(np.mean([row["S_born"] for row in group])),
                "min_S_born": float(np.min([row["S_born"] for row in group])),
                "mean_theta_power_law_alpha": float(np.mean([row["theta_power_law_alpha"] for row in group])),
                "median_theta_power_law_js": float(np.median([row["theta_power_law_js"] for row in group])),
            }
        )
    return output


def _summary(rows: list[dict[str, Any]], gates: Gates, finite: list[dict[str, Any]]) -> dict[str, Any]:
    by_n = []
    for (detector_n,), group in sorted(_groups(rows, ("detector_n",)).items()):
        born = [row for row in group if gates.born(row)]
        resolved = [row for row in group if gates.resolved_power_law(row)]
        by_n.append(
            {
                "detector_n": detector_n,
                "available": len(group),
                "born_like": len(born),
                "resolved_power_law": len(resolved),
                "born_and_resolved_power_law": sum(gates.resolved_power_law(row) for row in born),
                "median_S_born": float(np.median([row["S_born"] for row in group])),
                "median_alpha_all": float(np.median([row["theta_power_law_alpha"] for row in group])),
                "median_alpha_resolved": float(np.median([row["theta_power_law_alpha"] for row in resolved])) if resolved else math.nan,
            }
        )
    complete = [row for row in rows if row["detector_n"] <= 14]
    correlations = []
    for field in ("theta_power_law_alpha", "theta_power_law_js", "theta_power_law_log10_span", "radius_q99_over_q50", "reciprocity_error", "phi_harmonic_2", "angular_bin_coverage"):
        x = np.asarray([row["S_born"] for row in complete])
        y = np.asarray([row[field] for row in complete])
        mask = np.isfinite(x) & np.isfinite(y)
        result = spearmanr(x[mask], y[mask])
        correlations.append({"metric": field, "n": int(mask.sum()), "rho": float(result.statistic), "p": float(result.pvalue)})
    return {
        "gates": gates.__dict__,
        "available_spectra": len(rows),
        "complete_grid_spectra_N11_N14": len(complete),
        "by_n": by_n,
        "correlations_complete_N11_N14": correlations,
        "stable_across_N11_N14": {
            "born_all_four": sum(row["born_sizes"] == 4 for row in finite),
            "born_at_least_three": sum(row["born_sizes"] >= 3 for row in finite),
            "resolved_power_law_all_four": sum(row["resolved_power_law_sizes"] == 4 for row in finite),
            "born_and_resolved_all_four": sum(row["born_sizes"] == 4 and row["resolved_power_law_sizes"] == 4 for row in finite),
        },
    }


def _plot_summary(rows: list[dict[str, Any]], summary: dict[str, Any], path: Path) -> str:
    by_n = summary["by_n"]
    complete_n = [row for row in by_n if row["detector_n"] <= 14]
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.0), constrained_layout=True)
    n_values = [row["detector_n"] for row in by_n]
    axes[0, 0].bar(n_values, [row["available"] for row in by_n], color="#94a3b8")
    axes[0, 0].axhline(880, color="#334155", linestyle="--", linewidth=1)
    axes[0, 0].set(title="Downloaded coverage", xlabel="detector N", ylabel="available configurations")
    axes[0, 1].plot([row["detector_n"] for row in complete_n], [row["born_like"] for row in complete_n], "o-", label="Born-like", color="#2563eb")
    axes[0, 1].plot([row["detector_n"] for row in complete_n], [row["resolved_power_law"] for row in complete_n], "o-", label="resolved power-law fits", color="#c2410c")
    axes[0, 1].plot([row["detector_n"] for row in complete_n], [row["born_and_resolved_power_law"] for row in complete_n], "o-", label="Born + resolved fit", color="#7c3aed")
    axes[0, 1].set(title="Born and fit-quality counts", xlabel="detector N", ylabel="configurations")
    axes[0, 1].legend(frameon=False)

    trajectories = [
        (-0.01, 0.5, 0.05, "Born / Gaussian"),
        (-0.01, 0.5, 0.25, "Born + power law"),
        (-2.0, 1.0, 0.05, "resonant stripe"),
    ]
    for hz, j, jpm, label in trajectories:
        group = sorted(
            [row for row in rows if row["detector_n"] <= 14 and row["hz"] == hz and row["J"] == j and row["Jpm"] == jpm],
            key=lambda row: row["detector_n"],
        )
        axes[1, 0].plot([row["detector_n"] for row in group], [row["S_born"] for row in group], "o-", label=label)
    axes[1, 0].axhline(0.75, color="#334155", linestyle="--", linewidth=1)
    axes[1, 0].set(title="Representative finite-size Born trajectories", xlabel="detector N", ylabel=r"$S_{\rm Born}$", ylim=(0, 1))
    axes[1, 0].legend(frameon=False, fontsize=8)

    correlations = summary["correlations_complete_N11_N14"]
    label_map = {
        "theta_power_law_alpha": r"power-law $\alpha$",
        "theta_power_law_js": "power-law JS",
        "theta_power_law_log10_span": "power-law log-span",
        "radius_q99_over_q50": r"$q_{99}/q_{50}$",
        "reciprocity_error": "reciprocity error",
        "phi_harmonic_2": r"$|\langle e^{2i\phi}\rangle|$",
        "angular_bin_coverage": "angular coverage",
    }
    labels = [label_map[item["metric"]] for item in correlations]
    values = [item["rho"] for item in correlations]
    axes[1, 1].barh(labels, values, color=["#2563eb" if value >= 0 else "#dc2626" for value in values])
    axes[1, 1].axvline(0, color="#334155", linewidth=0.8)
    axes[1, 1].set(title=r"Spearman correlation with $S_{\rm Born}$", xlabel=r"$\rho$", xlim=(-0.5, 0.8))
    for axis in axes.flat:
        axis.grid(alpha=0.18)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190)
    plt.close(fig)
    return str(path)


def _plot_diagnostic_montage(
    rows: list[dict[str, Any]],
    repository: AnisotropicRepository,
    config: AnisotropicSweepConfig,
    path: Path,
) -> tuple[str, list[dict[str, Any]]]:
    requests = [
        (14, 0.0, 1.0, 1.5, "Born-like, resolved power law"),
        (14, -0.01, 0.5, 0.1, "strongest Born-like example"),
        (14, -0.01, 0.0, 0.25, "Born-like near-zero-field example"),
        (14, -2.01, 0.5, 0.05, "steep but angularly unresolved control"),
    ]
    selected: list[dict[str, Any]] = []
    fig, axes = plt.subplots(2, 2, figsize=(14.0, 15.0), constrained_layout=True)
    for axis, (detector_n, hz, j, jpm, label) in zip(axes.flat, requests, strict=True):
        row = next(row for row in rows if row["detector_n"] == detector_n and row["hz"] == hz and row["J"] == j and row["Jpm"] == jpm)
        case = AnisotropicCase(detector_n, hz, j, jpm, config.evolution_time, config.jx, config.hz0, config.seed)
        figure = repository.figure_path(case)
        axis.imshow(mpimg.imread(figure))
        axis.set_title(f"{label}: hz={hz:g}, J={j:g}, Jpm={jpm:g}\nS_B={row['S_born']:.3f}, alpha={row['theta_power_law_alpha']:.3f}, JS_PL={row['theta_power_law_js']:.3f}", fontsize=11)
        axis.axis("off")
        selected.append({"label": label, "figure": str(figure), "metrics": {key: row[key] for key in ("detector_n", "hz", "J", "Jpm", "S_born", "born_rmse", "angular_bin_coverage", "theta_power_law_alpha", "theta_power_law_js", "theta_power_law_log10_span", "radius_q99_over_q50", "phi_harmonic_2")}})
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return str(path), selected


def _plot_heatmap_montage(
    born_root: Path,
    alpha_root: Path,
    path: Path,
) -> str:
    choices = [-2.0, -0.01, 0.0]
    fig, axes = plt.subplots(2, 3, figsize=(15.0, 9.0), constrained_layout=True)
    for column, hz in enumerate(choices):
        born_path = born_root / f"S_born_clean_N14_hz_{hz:+g}.png"
        alpha_path = alpha_root / f"theta_power_law_alpha_N14_hz_{hz:+g}.png"
        axes[0, column].imshow(mpimg.imread(born_path))
        axes[1, column].imshow(mpimg.imread(alpha_path))
        axes[0, column].set_title(rf"$S_{{Born}}$, $h_z={hz:g}$")
        axes[1, column].set_title(rf"$\alpha$, $h_z={hz:g}$")
        axes[0, column].axis("off")
        axes[1, column].axis("off")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.json"))
    parser.add_argument("--run-root", type=Path, default=Path("work/zeus_single_pixel_anisotropic_20260718_130606"))
    parser.add_argument("--analysis-root", type=Path, default=Path("reports/anisotropic_parameter_study_2026-07-21"))
    args = parser.parse_args()
    config = AnisotropicSweepConfig.from_json(args.config)
    rows = _read(args.analysis_root / "data" / "spectrum_metrics.csv")
    gates = Gates()
    _write(args.analysis_root / "data" / "spectrum_metrics_power_law.csv", rows)
    alpha_heatmaps = _plot_alpha_heatmaps(rows, config, args.analysis_root / "figures" / "theta_power_law_alpha_heatmaps")
    born_heatmaps = _plot_clean_born_heatmaps(rows, config, args.analysis_root / "figures" / "clean_born_heatmaps")
    finite = _finite_size(rows, gates)
    _write(args.analysis_root / "data" / "finite_size_regimes_N11_N14.csv", finite)
    summary = _summary(rows, gates, finite)
    summary_figure = _plot_summary(rows, summary, args.analysis_root / "figures" / "campaign_summary.png")
    montage, selected = _plot_diagnostic_montage(rows, AnisotropicRepository(args.run_root), config, args.analysis_root / "figures" / "representative_diagnostics.png")
    heatmap_montage = _plot_heatmap_montage(
        args.analysis_root / "figures" / "clean_born_heatmaps",
        args.analysis_root / "figures" / "theta_power_law_alpha_heatmaps",
        args.analysis_root / "figures" / "N14_born_alpha_heatmap_montage.png",
    )
    payload = summary | {
        "theta_power_law_definition": (
            "P_b(alpha) is proportional to bin_width * max(d_2pi(theta_b,0), Delta/2)^(-alpha); "
            "alpha is the multinomial maximum-likelihood estimate. Resolved-fit screen: JS <= 0.10, "
            "angular coverage >= 0.50, log10 distance span >= 1.0."
        ),
        "theta_power_law_alpha_heatmaps": alpha_heatmaps,
        "clean_born_heatmaps": born_heatmaps,
        "summary_figure": summary_figure,
        "representative_diagnostics": montage,
        "selected_diagnostics": selected,
        "heatmap_montage": heatmap_montage,
    }
    (args.analysis_root / "data" / "report_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
