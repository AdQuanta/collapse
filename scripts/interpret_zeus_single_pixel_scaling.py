"""Interpret the completed Zeus scaling aggregate and render finite-size evidence.

The aggregation stage intentionally excludes interrupted cases.  This script
operates only on its validated CSV outputs and keeps data access, statistical
analysis, artifact writing, and plotting in separate services.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
from typing import Iterable, Protocol, Sequence

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".mplconfig"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


@dataclass(frozen=True)
class AnalysisConfig:
    source: Path
    output: Path
    born_coverage_gate: float = 0.50
    born_phi_gate: float = 0.25
    heavy_tail_exponent_low: float = 1.5
    heavy_tail_exponent_high: float = 2.7
    top_count: int = 20


class RowRepository(Protocol):
    def load(self) -> list[dict[str, object]]: ...


class CsvRowRepository:
    """Read the typed subset of aggregate columns used by this analysis."""

    NUMERIC_COLUMNS = {
        "detector_n",
        "total_qubits",
        "t",
        "parameter_value",
        "reference_value",
        "detuning",
        "hz",
        "hz0",
        "J",
        "Jpm",
        "Jx",
        "sample_count",
        "S_born",
        "born_rmse",
        "angular_bin_coverage",
        "phi_harmonic_2",
        "best_fit_wrapped_gaussian_js",
        "best_fit_wrapped_cauchy_js",
        "cauchy_log_likelihood_advantage_per_sample",
        "tail_density_exponent",
        "radius_q99_over_q50",
        "radius_atomic_fraction",
        "theta_mass_gt_0p5",
    }

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> list[dict[str, object]]:
        with self._path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            for key in self.NUMERIC_COLUMNS:
                raw = row.get(key, "nan")
                try:
                    row[key] = float(raw)
                except (TypeError, ValueError):
                    row[key] = math.nan
        return rows


def _finite(values: Iterable[float]) -> np.ndarray:
    array = np.asarray(list(values), dtype=float)
    return array[np.isfinite(array)]


def _median(rows: Sequence[dict[str, object]], key: str) -> float:
    values = _finite(float(row[key]) for row in rows)
    return float(np.median(values)) if values.size else math.nan


def _rank_correlation(rows: Sequence[dict[str, object]], left: str, right: str) -> tuple[float, float, int]:
    pairs = np.asarray(
        [(float(row[left]), float(row[right])) for row in rows], dtype=float
    )
    pairs = pairs[np.all(np.isfinite(pairs), axis=1)]
    if pairs.shape[0] < 3:
        return math.nan, math.nan, int(pairs.shape[0])
    result = spearmanr(pairs[:, 0], pairs[:, 1])
    return float(result.statistic), float(result.pvalue), int(pairs.shape[0])


class ScalingAnalyzer:
    def __init__(self, config: AnalysisConfig) -> None:
        self._config = config

    def parameter_summary(self, rows: Sequence[dict[str, object]]) -> list[dict[str, object]]:
        groups: dict[tuple[str, int, float], list[dict[str, object]]] = {}
        for row in rows:
            key = (str(row["study"]), int(float(row["detector_n"])), float(row["parameter_value"]))
            groups.setdefault(key, []).append(row)
        output: list[dict[str, object]] = []
        for (study, detector_n, parameter), group in sorted(groups.items()):
            output.append(
                {
                    "study": study,
                    "detector_n": detector_n,
                    "parameter_name": group[0]["parameter_name"],
                    "parameter_value": parameter,
                    "spectra": len(group),
                    "median_S_born": _median(group, "S_born"),
                    "max_S_born": max(float(row["S_born"]) for row in group),
                    "median_coverage": _median(group, "angular_bin_coverage"),
                    "median_phi_harmonic_2": _median(group, "phi_harmonic_2"),
                    "median_cauchy_advantage": _median(group, "cauchy_log_likelihood_advantage_per_sample"),
                    "cauchy_preferred_fraction": float(
                        np.mean([row["preferred_wrapped_model"] == "wrapped_cauchy" for row in group])
                    ),
                    "median_tail_density_exponent": _median(group, "tail_density_exponent"),
                    "median_q99_over_q50": _median(group, "radius_q99_over_q50"),
                }
            )
        return output

    def correlations(self, rows: Sequence[dict[str, object]]) -> list[dict[str, object]]:
        comparisons = (
            ("cauchy_log_likelihood_advantage_per_sample", "radius_q99_over_q50"),
            ("cauchy_log_likelihood_advantage_per_sample", "tail_density_exponent"),
            ("cauchy_log_likelihood_advantage_per_sample", "S_born"),
            ("S_born", "angular_bin_coverage"),
            ("S_born", "phi_harmonic_2"),
        )
        output: list[dict[str, object]] = []
        scopes = [("all", list(rows))]
        scopes.extend(
            (study, [row for row in rows if row["study"] == study])
            for study in sorted({str(row["study"]) for row in rows})
        )
        for scope, group in scopes:
            for left, right in comparisons:
                rho, pvalue, count = _rank_correlation(group, left, right)
                output.append(
                    {"scope": scope, "left": left, "right": right, "spearman_rho": rho, "pvalue": pvalue, "count": count}
                )
        return output

    def top_born(self, rows: Sequence[dict[str, object]]) -> list[dict[str, object]]:
        gated = [
            row for row in rows
            if float(row["angular_bin_coverage"]) >= self._config.born_coverage_gate
        ]
        return sorted(gated, key=lambda row: float(row["S_born"]), reverse=True)[: self._config.top_count]

    def jointly_gated_born(self, rows: Sequence[dict[str, object]]) -> list[dict[str, object]]:
        return sorted(
            [
                row for row in rows
                if float(row["angular_bin_coverage"]) >= self._config.born_coverage_gate
                and float(row["phi_harmonic_2"]) <= self._config.born_phi_gate
            ],
            key=lambda row: float(row["S_born"]),
            reverse=True,
        )

    def top_heavy(self, rows: Sequence[dict[str, object]]) -> list[dict[str, object]]:
        low = self._config.heavy_tail_exponent_low
        high = self._config.heavy_tail_exponent_high
        gated = [
            row for row in rows
            if float(row["cauchy_log_likelihood_advantage_per_sample"]) > 0.0
            and low <= float(row["tail_density_exponent"]) <= high
        ]
        return sorted(
            gated,
            key=lambda row: (
                float(row["cauchy_log_likelihood_advantage_per_sample"]),
                float(row["radius_q99_over_q50"]),
            ),
            reverse=True,
        )[: self._config.top_count]

    def summary(self, rows: Sequence[dict[str, object]], jointly_gated: Sequence[dict[str, object]]) -> dict[str, object]:
        by_study: dict[str, object] = {}
        for study in sorted({str(row["study"]) for row in rows}):
            group = [row for row in rows if row["study"] == study]
            by_study[study] = {
                "spectra": len(group),
                "detector_n_min": min(int(float(row["detector_n"])) for row in group),
                "detector_n_max": max(int(float(row["detector_n"])) for row in group),
                "cauchy_preferred_fraction": float(np.mean([row["preferred_wrapped_model"] == "wrapped_cauchy" for row in group])),
                "median_cauchy_advantage": _median(group, "cauchy_log_likelihood_advantage_per_sample"),
                "median_tail_density_exponent": _median(group, "tail_density_exponent"),
                "median_q99_over_q50": _median(group, "radius_q99_over_q50"),
                "median_S_born": _median(group, "S_born"),
                "max_S_born": max(float(row["S_born"]) for row in group),
                "median_phi_harmonic_2": _median(group, "phi_harmonic_2"),
            }
        return {
            "spectra": len(rows),
            "criteria": {
                "born_coverage_gate": self._config.born_coverage_gate,
                "born_phi_gate": self._config.born_phi_gate,
                "heavy_tail_exponent_window": [self._config.heavy_tail_exponent_low, self._config.heavy_tail_exponent_high],
            },
            "jointly_gated_born_count": len(jointly_gated),
            "studies": by_study,
        }


class ArtifactWriter:
    CANDIDATE_COLUMNS = (
        "study", "detector_n", "t", "parameter_name", "parameter_value", "hz", "hz0", "J", "Jpm", "Jx",
        "S_born", "angular_bin_coverage", "phi_harmonic_2", "cauchy_log_likelihood_advantage_per_sample",
        "preferred_wrapped_model", "tail_density_exponent", "radius_q99_over_q50", "best_fit_wrapped_gaussian_js",
        "best_fit_wrapped_cauchy_js", "source_npz",
    )

    def __init__(self, output: Path) -> None:
        self._output = output

    def write_csv(self, name: str, rows: Sequence[dict[str, object]], columns: Sequence[str] | None = None) -> None:
        if not rows:
            (self._output / name).write_text("", encoding="utf-8")
            return
        fieldnames = list(columns or rows[0].keys())
        with (self._output / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def write_json(self, name: str, payload: object) -> None:
        (self._output / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class FigureRenderer:
    COLORS = {"hz0": "#3b82f6", "hz_resonance": "#8b5cf6", "jpm_coupling": "#ef4444", "jpm_hz": "#f59e0b"}

    def __init__(self, output: Path) -> None:
        self._output = output

    def finite_size(self, rows: Sequence[dict[str, object]]) -> None:
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        metrics = (
            ("S_born", "Median Born score"),
            ("cauchy_log_likelihood_advantage_per_sample", "Median Cauchy log-likelihood advantage"),
            ("radius_q99_over_q50", "Median radius q99/q50"),
            ("phi_harmonic_2", "Median azimuthal second harmonic"),
        )
        studies = sorted({str(row["study"]) for row in rows})
        for ax, (metric, label) in zip(axes.flat, metrics):
            for study in studies:
                group = [row for row in rows if row["study"] == study]
                sizes = sorted({int(float(row["detector_n"])) for row in group})
                medians = [_median([row for row in group if int(float(row["detector_n"])) == size], metric) for size in sizes]
                ax.plot(sizes, medians, marker="o", linewidth=2, label=study, color=self.COLORS[study])
            ax.set_xlabel("Detector N")
            ax.set_ylabel(label)
            ax.grid(alpha=0.25)
        axes[0, 1].axhline(0.0, color="black", linewidth=1, linestyle="--")
        axes[1, 1].axhline(0.25, color="black", linewidth=1, linestyle="--", label="uniformity gate")
        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.subplots_adjust(top=0.84, hspace=0.32, wspace=0.26)
        fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.92), ncol=4, frameon=False)
        fig.suptitle("Zeus completed-case finite-size diagnostics", fontsize=15, y=0.98)
        fig.savefig(self._output / "finite_size_diagnostics.png", dpi=180)
        plt.close(fig)

    def tradeoff(self, rows: Sequence[dict[str, object]]) -> None:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for study in sorted({str(row["study"]) for row in rows}):
            group = [row for row in rows if row["study"] == study]
            color = self.COLORS[study]
            axes[0].scatter(
                [float(row["tail_density_exponent"]) for row in group],
                [float(row["cauchy_log_likelihood_advantage_per_sample"]) for row in group],
                s=12, alpha=0.45, label=study, color=color,
            )
            axes[1].scatter(
                [float(row["angular_bin_coverage"]) for row in group],
                [float(row["S_born"]) for row in group],
                s=12, alpha=0.45, label=study, color=color,
            )
        axes[0].axhline(0.0, color="black", linewidth=1, linestyle="--")
        axes[0].axvline(2.0, color="black", linewidth=1, linestyle=":")
        axes[0].set(xlabel="Fitted radius density-tail exponent", ylabel="Cauchy LL advantage per sample")
        axes[1].axvline(0.50, color="black", linewidth=1, linestyle="--")
        axes[1].set(xlabel="Polar-bin coverage", ylabel="Born score")
        for ax in axes:
            ax.grid(alpha=0.25)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.subplots_adjust(top=0.76, wspace=0.24)
        fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.90), ncol=4, frameon=False)
        fig.suptitle("Heavy-tail and Born-score evidence are distinct gates", fontsize=15, y=0.98)
        fig.savefig(self._output / "regime_tradeoffs.png", dpi=180)
        plt.close(fig)


def parse_args() -> AnalysisConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("reports/zeus_single_pixel_analysis_2026-07-16/spectrum_metrics.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/zeus_single_pixel_analysis_2026-07-16"))
    args = parser.parse_args()
    return AnalysisConfig(source=args.source, output=args.output)


def main() -> None:
    config = parse_args()
    config.output.mkdir(parents=True, exist_ok=True)
    rows = CsvRowRepository(config.source).load()
    analyzer = ScalingAnalyzer(config)
    parameter_summary = analyzer.parameter_summary(rows)
    correlations = analyzer.correlations(rows)
    top_born = analyzer.top_born(rows)
    jointly_gated = analyzer.jointly_gated_born(rows)
    top_heavy = analyzer.top_heavy(rows)
    summary = analyzer.summary(rows, jointly_gated)

    writer = ArtifactWriter(config.output)
    writer.write_csv("parameter_summary.csv", parameter_summary)
    writer.write_csv("correlations.csv", correlations)
    writer.write_csv("top_born_candidates.csv", top_born, ArtifactWriter.CANDIDATE_COLUMNS)
    writer.write_csv("jointly_gated_born_candidates.csv", jointly_gated, ArtifactWriter.CANDIDATE_COLUMNS)
    writer.write_csv("top_heavy_tail_candidates.csv", top_heavy, ArtifactWriter.CANDIDATE_COLUMNS)
    writer.write_json("interpretation_summary.json", summary)

    renderer = FigureRenderer(config.output)
    renderer.finite_size(rows)
    renderer.tradeoff(rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
