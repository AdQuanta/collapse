"""Study basis-invariant V_ab activation at exact and near detector degeneracies."""

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
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import fisher_exact, rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collapse.anisotropic_sweep import AnisotropicSweepConfig  # noqa: E402
from collapse.degenerate_activation import (  # noqa: E402
    ActivationConfig,
    DegenerateActivationAnalyzer,
)
from collapse.detector_resonance import DetectorSpec  # noqa: E402


OUTCOME_FIELDS = (
    "S_born",
    "born_rmse",
    "angular_bin_coverage",
    "theta_power_law_alpha",
    "theta_power_law_js",
    "theta_power_law_log10_span",
    "reciprocity_error",
    "max_radius",
)

PREDICTORS = (
    ("exact_active_weight_fraction", r"exact weight $D_{\rm act}$"),
    ("active_degenerate_subspace_fraction", "active degenerate-subspace coverage"),
    ("active_degenerate_state_fraction", "active degenerate-state coverage"),
    ("exact_activation_rank_fraction", "intrablock rank fraction"),
    ("exact_spectral_participation_fraction", "intrablock spectral participation"),
    ("exact_block_breadth", "exact block breadth"),
    ("finite_time_kernel_power_fraction", "finite-time kernel power"),
    ("finite_time_transition_participation_fraction", "finite-time transition participation"),
    ("finite_time_transition_breadth", "finite-time transition breadth"),
    ("weight_fraction_gap_le_1em4", r"weight with $|\Delta E|\le10^{-4}$"),
    ("degenerate_state_fraction", "raw degenerate-state fraction"),
)

WINDOW_COLUMNS = (
    (1.0e-9, "exact_active_weight_fraction"),
    (1.0e-6, "weight_fraction_gap_le_1em6"),
    (1.0e-5, "weight_fraction_gap_le_1em5"),
    (1.0e-4, "weight_fraction_gap_le_1em4"),
    (1.0e-3, "weight_fraction_gap_le_1em3"),
    (1.0e-2, "weight_fraction_gap_le_1em2"),
    (1.0e-1, "weight_fraction_gap_le_1em1"),
)

REPRESENTATIVES = (
    ("active_born", "active and Born-like", 0.0, 0.0, 0.1),
    ("near_born", "Born-like without exact activation", 0.01, 0.75, 0.5),
    ("saturated_nonborn", "saturated exact activation, non-Born", 0.0, 0.5, 1.0),
    ("narrow_control", "narrow non-heavy control", 1.0, 0.25, 0.0),
)


def _calculate(task: tuple[int, float, float, float, float]) -> dict[str, float | int]:
    detector_n, hz, j, jpm, evolution_time = task
    analyzer = DegenerateActivationAnalyzer(ActivationConfig(evolution_time=evolution_time))
    return analyzer.analyze(DetectorSpec(detector_n, hz, j, jpm)).to_row()


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _read_dynamics(path: Path, detector_n: int) -> dict[tuple[float, float, float], dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            (float(row["hz"]), float(row["J"]), float(row["Jpm"])): row
            for row in csv.DictReader(handle)
            if int(row["detector_n"]) == detector_n
        }


def _join_outcomes(
    activation: Iterable[dict[str, Any]],
    dynamics: dict[tuple[float, float, float], dict[str, str]],
) -> list[dict[str, Any]]:
    joined: list[dict[str, Any]] = []
    for activation_row in activation:
        key = (
            float(activation_row["hz"]),
            float(activation_row["J"]),
            float(activation_row["Jpm"]),
        )
        if key not in dynamics:
            continue
        outcome = dynamics[key]
        row = {name: float(value) for name, value in activation_row.items()}
        row.update({name: float(outcome[name]) for name in OUTCOME_FIELDS})
        row["resolved_power_law"] = (
            row["theta_power_law_js"] <= 0.10
            and row["angular_bin_coverage"] >= 0.50
            and row["theta_power_law_log10_span"] >= 1.0
        )
        row["heavy_tailed"] = row["resolved_power_law"] and row["theta_power_law_alpha"] <= 2.0
        row["born_like"] = (
            row["S_born"] >= 0.75
            and row["born_rmse"] <= 0.15
            and row["angular_bin_coverage"] >= 0.50
        )
        row["exact_block_breadth"] = (
            1.0 - row["exact_largest_block_share"]
            if row["exact_active_weight_fraction"] > 1.0e-12
            else 0.0
        )
        row["finite_time_transition_breadth"] = 1.0 - row["finite_time_largest_transition_share"]
        joined.append(row)
    return joined


def _finite_arrays(rows: list[dict[str, Any]], x_name: str, y_name: str) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray([float(row[x_name]) for row in rows], dtype=float)
    y = np.asarray([float(row[y_name]) for row in rows], dtype=float)
    finite = np.isfinite(x) & np.isfinite(y)
    return x[finite], y[finite]


def _spearman(rows: list[dict[str, Any]], predictor: str, outcome: str) -> dict[str, Any]:
    x, y = _finite_arrays(rows, predictor, outcome)
    if x.size < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        rho, p_value = float("nan"), float("nan")
    else:
        result = spearmanr(x, y)
        rho, p_value = float(result.statistic), float(result.pvalue)
    return {
        "predictor": predictor,
        "outcome": outcome,
        "sample_count": int(x.size),
        "spearman_rho": rho,
        "two_sided_p_value": p_value,
    }


def _auc(score: np.ndarray, label: np.ndarray) -> float:
    positive = np.asarray(label, dtype=bool)
    values = np.asarray(score, dtype=float)
    n_positive = int(np.count_nonzero(positive))
    n_negative = int(values.size - n_positive)
    if not n_positive or not n_negative:
        return float("nan")
    ranks = rankdata(values, method="average")
    return float(
        (np.sum(ranks[positive]) - n_positive * (n_positive + 1) / 2.0)
        / (n_positive * n_negative)
    )


def _auc_with_interval(
    rows: list[dict[str, Any]],
    predictor: str,
    outcome: str,
    rng: np.random.Generator,
    repetitions: int = 400,
) -> dict[str, Any]:
    score = np.asarray([float(row[predictor]) for row in rows], dtype=float)
    label = np.asarray([bool(row[outcome]) for row in rows], dtype=bool)
    finite = np.isfinite(score)
    score, label = score[finite], label[finite]
    positive_score = score[label]
    negative_score = score[~label]
    bootstrap: list[float] = []
    for _ in range(repetitions):
        sampled = np.concatenate(
            [
                rng.choice(positive_score, size=positive_score.size, replace=True),
                rng.choice(negative_score, size=negative_score.size, replace=True),
            ]
        )
        sampled_label = np.concatenate(
            [
                np.ones(positive_score.size, dtype=bool),
                np.zeros(negative_score.size, dtype=bool),
            ]
        )
        bootstrap.append(_auc(sampled, sampled_label))
    lower, upper = np.quantile(bootstrap, [0.025, 0.975])
    return {
        "predictor": predictor,
        "outcome": outcome,
        "sample_count": int(score.size),
        "positive_count": int(np.count_nonzero(label)),
        "auc": _auc(score, label),
        "bootstrap_95_lower": float(lower),
        "bootstrap_95_upper": float(upper),
    }


def _contingency(rows: list[dict[str, Any]], outcome: str) -> dict[str, Any]:
    active = np.asarray([float(row["exact_active_weight_fraction"]) > 1.0e-12 for row in rows])
    positive = np.asarray([bool(row[outcome]) for row in rows])
    table = np.asarray(
        [
            [np.count_nonzero(active & positive), np.count_nonzero(active & ~positive)],
            [np.count_nonzero(~active & positive), np.count_nonzero(~active & ~positive)],
        ],
        dtype=int,
    )
    result = fisher_exact(table)
    return {
        "outcome": outcome,
        "table_active_positive_active_negative_inactive_positive_inactive_negative": table.ravel().tolist(),
        "odds_ratio": float(result.statistic),
        "two_sided_p_value": float(result.pvalue),
    }


def _activation_bands(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active_values = np.asarray(
        [float(row["exact_active_weight_fraction"]) for row in rows if float(row["exact_active_weight_fraction"]) > 1.0e-12]
    )
    q1, q2 = np.quantile(active_values, [1.0 / 3.0, 2.0 / 3.0])
    groups = (
        ("zero", lambda value: value <= 1.0e-12),
        ("low", lambda value: 1.0e-12 < value <= q1),
        ("middle", lambda value: q1 < value <= q2),
        ("high", lambda value: value > q2),
    )
    output: list[dict[str, Any]] = []
    for label, condition in groups:
        selected = [row for row in rows if condition(float(row["exact_active_weight_fraction"]))]
        resolved = [row for row in selected if bool(row["resolved_power_law"])]
        output.append(
            {
                "activation_band": label,
                "count": len(selected),
                "minimum_exact_weight": min(float(row["exact_active_weight_fraction"]) for row in selected),
                "maximum_exact_weight": max(float(row["exact_active_weight_fraction"]) for row in selected),
                "heavy_tailed_rate": float(np.mean([bool(row["heavy_tailed"]) for row in selected])),
                "born_like_rate": float(np.mean([bool(row["born_like"]) for row in selected])),
                "median_S_born": float(np.median([float(row["S_born"]) for row in selected])),
                "median_resolved_alpha": (
                    float(np.median([float(row["theta_power_law_alpha"]) for row in resolved]))
                    if resolved
                    else float("nan")
                ),
            }
        )
    return output


def _family(row: dict[str, Any]) -> str:
    j = float(row["J"])
    jpm = float(row["Jpm"])
    if j == 0.0 and jpm == 0.0:
        return "uncoupled detector"
    if jpm == 0.0:
        return "pure ZZ"
    if j == 0.0:
        return "pure exchange"
    return "mixed ZZ+exchange"


def _family_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for family in ("uncoupled detector", "pure ZZ", "pure exchange", "mixed ZZ+exchange"):
        selected = [row for row in rows if _family(row) == family]
        output.append(
            {
                "family": family,
                "count": len(selected),
                "exact_active_count": sum(float(row["exact_active_weight_fraction"]) > 1.0e-12 for row in selected),
                "heavy_tailed_count": sum(bool(row["heavy_tailed"]) for row in selected),
                "born_like_count": sum(bool(row["born_like"]) for row in selected),
                "median_exact_weight": float(np.median([float(row["exact_active_weight_fraction"]) for row in selected])),
            }
        )
    return output


def _finite_size_stability(rows_by_n: dict[int, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    metric_names = (
        "exact_active_weight_fraction",
        "active_degenerate_state_fraction",
        "exact_activation_rank_fraction",
        "finite_time_kernel_power_fraction",
    )
    indexed = {
        detector_n: {
            (float(row["hz"]), float(row["J"]), float(row["Jpm"])): row
            for row in rows
        }
        for detector_n, rows in rows_by_n.items()
    }
    sizes = sorted(rows_by_n)
    for left, right in zip(sizes[:-1], sizes[1:], strict=True):
        keys = sorted(set(indexed[left]) & set(indexed[right]))
        for metric in metric_names:
            x = np.asarray([float(indexed[left][key][metric]) for key in keys])
            y = np.asarray([float(indexed[right][key][metric]) for key in keys])
            result = spearmanr(x, y)
            output.append(
                {
                    "left_detector_n": left,
                    "right_detector_n": right,
                    "metric": metric,
                    "sample_count": len(keys),
                    "spearman_rho": float(result.statistic),
                    "two_sided_p_value": float(result.pvalue),
                }
            )
    return output


def _category_masks(rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    heavy = np.asarray([bool(row["heavy_tailed"]) for row in rows])
    born = np.asarray([bool(row["born_like"]) for row in rows])
    return ~heavy, heavy & ~born, born


def _plot_relationships(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    other, heavy_nonborn, born = _category_masks(rows)
    colors = ("#9ca3af", "#dc2626", "#2563eb")
    labels = ("not resolved-heavy", "heavy, not Born-like", "Born-like")
    masks = (other, heavy_nonborn, born)
    x_specs = (
        ("exact_active_weight_fraction", r"$\log_{10}(D_{\rm act}+10^{-14})$", True),
        ("active_degenerate_state_fraction", "active degenerate-state fraction", False),
        ("exact_activation_rank_fraction", "intrablock rank fraction", False),
    )
    y_specs = (
        ("theta_power_law_alpha", r"periodic exponent $\alpha$", True),
        ("S_born", r"$S_{\rm Born}$", False),
    )
    figure, axes = plt.subplots(2, 3, figsize=(14.2, 8.3), constrained_layout=True)
    for row_index, (y_name, y_label, resolved_only) in enumerate(y_specs):
        for column_index, (x_name, x_label, log_x) in enumerate(x_specs):
            axis = axes[row_index, column_index]
            for mask, color, label in zip(masks, colors, labels, strict=True):
                selection = mask.copy()
                if resolved_only:
                    selection &= np.asarray([bool(item["resolved_power_law"]) for item in rows])
                x = np.asarray([float(item[x_name]) for item in rows])[selection]
                y = np.asarray([float(item[y_name]) for item in rows])[selection]
                if log_x:
                    x = np.log10(x + 1.0e-14)
                axis.scatter(x, y, s=17, alpha=0.50, color=color, edgecolors="none", label=label)
            axis.set(xlabel=x_label, ylabel=y_label)
            axis.grid(alpha=0.18)
            if row_index == 0:
                axis.set_title(("Weight", "Coverage", "Rank")[column_index])
    axes[0, 0].legend(frameon=False, fontsize=9, loc="upper right")
    figure.suptitle("How degenerate V blocks relate to heavy tails and the Born ratio", fontsize=15)
    figure.savefig(path, dpi=220)
    plt.close(figure)


def _plot_scale_scan(
    rows: list[dict[str, Any]],
    auc_rows: list[dict[str, Any]],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    scales = np.asarray([item[0] for item in WINDOW_COLUMNS])
    born_corr = [_spearman(rows, column, "S_born")["spearman_rho"] for _, column in WINDOW_COLUMNS]
    resolved = [row for row in rows if bool(row["resolved_power_law"])]
    alpha_corr = [_spearman(resolved, column, "theta_power_law_alpha")["spearman_rho"] for _, column in WINDOW_COLUMNS]
    auc_index = {(row["predictor"], row["outcome"]): row for row in auc_rows}
    heavy_auc = [auc_index[(column, "heavy_tailed")]["auc"] for _, column in WINDOW_COLUMNS]
    born_auc = [auc_index[(column, "born_like")]["auc"] for _, column in WINDOW_COLUMNS]
    figure, axes = plt.subplots(1, 2, figsize=(11.6, 4.5), constrained_layout=True)
    axes[0].plot(scales, born_corr, "o-", color="#2563eb", label=r"$\rho(A_\epsilon,S_{\rm Born})$")
    axes[0].plot(scales, alpha_corr, "s-", color="#dc2626", label=r"$\rho(A_\epsilon,\alpha)$ (resolved)")
    axes[0].axhline(0.0, color="#6b7280", linewidth=0.8)
    axes[0].set(xscale="log", xlabel=r"gap window $\epsilon$", ylabel="Spearman correlation", title="Association versus gap scale")
    axes[0].legend(frameon=False)
    axes[1].plot(scales, heavy_auc, "o-", color="#dc2626", label="heavy-tail AUC")
    axes[1].plot(scales, born_auc, "s-", color="#2563eb", label="Born-like AUC")
    axes[1].axhline(0.5, color="#6b7280", linewidth=0.8)
    axes[1].set(xscale="log", xlabel=r"gap window $\epsilon$", ylabel="ROC AUC", title="Single-metric discrimination")
    axes[1].legend(frameon=False)
    for axis in axes:
        axis.grid(alpha=0.18)
        axis.axvline(1.0e-6, color="#111827", linewidth=0.9, linestyle="--")
        axis.text(1.0e-6, 0.98, r"$1/t$", transform=axis.get_xaxis_transform(), ha="right", va="top", fontsize=9)
    figure.suptitle(r"Activation $A_\epsilon=\sum_{|E_a-E_b|\leq\epsilon}\|P_aVP_b\|_F^2/\mathrm{Tr}(V^2)$")
    figure.savefig(path, dpi=220)
    plt.close(figure)


def _plot_activation_bands(bands: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    labels = [str(row["activation_band"]) for row in bands]
    positions = np.arange(len(labels))
    heavy = np.asarray([float(row["heavy_tailed_rate"]) for row in bands])
    born = np.asarray([float(row["born_like_rate"]) for row in bands])
    medians = np.asarray([float(row["median_resolved_alpha"]) for row in bands])
    counts = [int(row["count"]) for row in bands]
    figure, axes = plt.subplots(1, 2, figsize=(10.8, 4.5), constrained_layout=True)
    width = 0.36
    axes[0].bar(positions - width / 2, heavy, width, color="#dc2626", label="resolved heavy")
    axes[0].bar(positions + width / 2, born, width, color="#2563eb", label="Born-like")
    for index, count in enumerate(counts):
        axes[0].text(index, min(max(heavy[index], born[index]) + 0.035, 1.075), f"n={count}", ha="center", fontsize=9)
    axes[0].set(xticks=positions, xticklabels=labels, ylabel="fraction of configurations", title="Outcome rates")
    axes[0].set_ylim(0.0, 1.12)
    axes[0].legend(frameon=False)
    axes[1].plot(positions, medians, "o-", color="#7c3aed", linewidth=2.0)
    axes[1].set(xticks=positions, xticklabels=labels, ylabel=r"median resolved $\alpha$", title="Tail exponent within each band")
    axes[1].grid(alpha=0.18)
    figure.suptitle(r"Exact activation bands of $D_{\rm act}$ (positive values split into tertiles)")
    figure.savefig(path, dpi=220)
    plt.close(figure)


def _representative_details(
    detector_n: int,
    evolution_time: float,
    dynamics: dict[tuple[float, float, float], dict[str, str]],
    data_root: Path,
) -> list[tuple[str, str, Any, dict[str, str]]]:
    analyzer = DegenerateActivationAnalyzer(ActivationConfig(evolution_time=evolution_time))
    output: list[tuple[str, str, Any, dict[str, str]]] = []
    for key, label, hz, j, jpm in REPRESENTATIVES:
        detail = analyzer.analyze_detail(DetectorSpec(detector_n, hz, j, jpm))
        outcome = dynamics[(hz, j, jpm)]
        np.savez_compressed(
            data_root / f"{key}_activation_detail_N{detector_n:02d}.npz",
            subspace_energies=detail.subspace_energies,
            subspace_multiplicities=detail.subspace_multiplicities,
            block_gaps=detail.block_gaps,
            block_weights=detail.block_weights,
            exact_block_weights=detail.exact_block_weights,
            exact_singular_weight=detail.exact_singular_weight,
        )
        output.append((key, label, detail, outcome))
    return output


def _plot_representatives(details: list[tuple[str, str, Any, dict[str, str]]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(3, len(details), figsize=(15.0, 9.2), constrained_layout=True)
    for column, (_, label, detail, outcome) in enumerate(details):
        gaps = np.abs(detail.block_gaps).ravel()
        weights = detail.block_weights.ravel()
        total = float(np.sum(weights))
        positive_gaps = gaps[gaps > 1.0e-12]
        maximum = max(float(np.max(positive_gaps)), 1.0e-1)
        windows = np.logspace(-9, math.log10(maximum), 180)
        cumulative = np.asarray([np.sum(weights[gaps <= window]) / total for window in windows])
        axes[0, column].plot(windows, cumulative, color="#2563eb", linewidth=1.8)
        axes[0, column].axvline(1.0e-6, color="#111827", linestyle="--", linewidth=0.9)
        axes[0, column].set(xscale="log", ylim=(-0.02, 1.02), title=label)

        exact = np.sort(detail.exact_block_weights[detail.exact_block_weights > 1.0e-12 * total])[::-1]
        if exact.size:
            axes[1, column].plot(np.arange(1, exact.size + 1), exact / np.sum(exact), "o-", color="#dc2626", markersize=3)
            if exact.size > 1:
                axes[1, column].set(yscale="log")
            else:
                axes[1, column].set(xlim=(0.5, 1.5), ylim=(0.0, 1.08))
        else:
            axes[1, column].text(0.5, 0.5, "no exact active block", ha="center", va="center", transform=axes[1, column].transAxes)

        time = 1.0e6
        filter_magnitude = time * np.abs(np.sinc(detail.block_gaps * time / (2.0 * np.pi)))
        power = (detail.block_weights * filter_magnitude**2).ravel()
        power = np.sort(power[power > 1.0e-12 * max(float(np.sum(power)), 1.0)])[::-1]
        if power.size:
            axes[2, column].plot(np.arange(1, power.size + 1), power / np.sum(power), color="#7c3aed", linewidth=1.5)
            axes[2, column].set(xscale="log", yscale="log")
        axes[0, column].text(
            0.03,
            0.08,
            rf"$S_B={float(outcome['S_born']):.3f}$, $\alpha={float(outcome['theta_power_law_alpha']):.3f}$",
            transform=axes[0, column].transAxes,
            fontsize=9,
        )
        axes[0, column].grid(alpha=0.18)
        axes[1, column].grid(alpha=0.18)
        axes[2, column].grid(alpha=0.18)
        axes[1, column].set_xlabel("ranked exact block")
        axes[2, column].set_xlabel("ranked finite-time transition")
    axes[0, 0].set_ylabel(r"cumulative $V$ weight $A_\epsilon$")
    axes[1, 0].set_ylabel("share of exact weight")
    axes[2, 0].set_ylabel("share of finite-time power")
    for column in range(len(details)):
        axes[0, column].set_xlabel(r"gap window $\epsilon$")
    figure.suptitle("Representative activation structure: amount, exact-block spread, and finite-time spread", fontsize=15)
    figure.savefig(path, dpi=220)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.json"))
    parser.add_argument("--spectrum-metrics", type=Path, default=Path("reports/anisotropic_parameter_study_2026-07-21/data/spectrum_metrics.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/vab_degenerate_activation_study_2026-07-22"))
    parser.add_argument("--detector-ns", type=int, nargs="+", default=[6, 7, 8])
    parser.add_argument("--join-n", type=int, default=14)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--reuse-existing", action="store_true")
    args = parser.parse_args()

    sweep = AnisotropicSweepConfig.from_json(args.config)
    data_root = args.output / "data"
    figure_root = args.output / "figures"
    data_root.mkdir(parents=True, exist_ok=True)
    rows_by_n: dict[int, list[dict[str, Any]]] = {}
    for detector_n in args.detector_ns:
        csv_path = data_root / f"vab_activation_N{detector_n:02d}.csv"
        if args.reuse_existing and csv_path.exists():
            with csv_path.open(newline="", encoding="utf-8") as handle:
                rows_by_n[detector_n] = list(csv.DictReader(handle))
            continue
        tasks = [
            (detector_n, hz, j, jpm, sweep.evolution_time)
            for hz in sweep.hz_values
            for j in sweep.j_values
            for jpm in sweep.jpm_values
        ]
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(_calculate, tasks, chunksize=8))
        rows.sort(key=lambda row: (float(row["hz"]), float(row["J"]), float(row["Jpm"])))
        rows_by_n[detector_n] = rows
        _write_csv(csv_path, rows)

    join_detector_n = max(args.detector_ns)
    dynamics = _read_dynamics(args.spectrum_metrics, args.join_n)
    joined = _join_outcomes(rows_by_n[join_detector_n], dynamics)
    _write_csv(data_root / f"vab_activation_N{join_detector_n:02d}_to_dynamics_N{args.join_n:02d}.csv", joined)

    rng = np.random.default_rng(20260722)
    spearman_rows: list[dict[str, Any]] = []
    resolved = [row for row in joined if bool(row["resolved_power_law"])]
    heavy = [row for row in joined if bool(row["heavy_tailed"])]
    for predictor, _ in PREDICTORS:
        spearman_rows.extend(
            [
                _spearman(joined, predictor, "S_born"),
                _spearman(joined, predictor, "reciprocity_error"),
                _spearman(resolved, predictor, "theta_power_law_alpha"),
                _spearman(heavy, predictor, "S_born"),
            ]
        )
    _write_csv(data_root / "activation_spearman_correlations.csv", spearman_rows)

    auc_predictors = list(PREDICTORS) + [
        (column, f"activation window {window:g}") for window, column in WINDOW_COLUMNS
        if column not in {name for name, _ in PREDICTORS}
    ]
    auc_rows = [
        _auc_with_interval(joined, predictor, outcome, rng)
        for predictor, _ in auc_predictors
        for outcome in ("heavy_tailed", "born_like")
    ]
    _write_csv(data_root / "activation_auc.csv", auc_rows)

    bands = _activation_bands(joined)
    _write_csv(data_root / "activation_bands.csv", bands)
    families = _family_summary(joined)
    _write_csv(data_root / "activation_by_family.csv", families)
    stability = _finite_size_stability(rows_by_n)
    _write_csv(data_root / "activation_finite_size_stability.csv", stability)

    details = _representative_details(join_detector_n, sweep.evolution_time, dynamics, data_root)
    relationship_path = figure_root / "vab_activation_outcomes.png"
    scale_path = figure_root / "vab_activation_scale_scan.png"
    band_path = figure_root / "vab_activation_bands.png"
    representative_path = figure_root / "vab_activation_representatives.png"
    _plot_relationships(joined, relationship_path)
    _plot_scale_scan(joined, auc_rows, scale_path)
    _plot_activation_bands(bands, band_path)
    _plot_representatives(details, representative_path)

    exact_active = [row for row in joined if float(row["exact_active_weight_fraction"]) > 1.0e-12]
    born_rows = [row for row in joined if bool(row["born_like"])]
    heavy_rows = [row for row in joined if bool(row["heavy_tailed"])]
    summary = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "detector_probe_sizes": args.detector_ns,
        "dynamics_join_n": args.join_n,
        "parameter_points": len(joined),
        "exact_active_points": len(exact_active),
        "resolved_heavy_points": len(heavy_rows),
        "born_like_points": len(born_rows),
        "heavy_with_exact_activation": sum(float(row["exact_active_weight_fraction"]) > 1.0e-12 for row in heavy_rows),
        "born_with_exact_activation": sum(float(row["exact_active_weight_fraction"]) > 1.0e-12 for row in born_rows),
        "contingency": [_contingency(joined, "heavy_tailed"), _contingency(joined, "born_like")],
        "activation_bands": bands,
        "family_summary": families,
        "finite_size_stability": stability,
        "spearman_correlations": spearman_rows,
        "auc": auc_rows,
        "representatives": [
            {
                "key": key,
                "label": label,
                "hz": detail.metrics.hz,
                "J": detail.metrics.J,
                "Jpm": detail.metrics.Jpm,
                "metrics": asdict(detail.metrics),
                "S_born": float(outcome["S_born"]),
                "born_rmse": float(outcome["born_rmse"]),
                "alpha": float(outcome["theta_power_law_alpha"]),
            }
            for key, label, detail, outcome in details
        ],
        "figures": [str(path) for path in (relationship_path, scale_path, band_path, representative_path)],
        "interpretive_guardrail": (
            "Exact V activation is a basis-invariant resonant-weight diagnostic. "
            "It is neither necessary nor sufficient for a heavy tail or Born similarity; "
            "block rank, participation, and finite-time gap broadening must be inspected separately."
        ),
    }
    (data_root / "vab_activation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in (
        "parameter_points", "exact_active_points", "resolved_heavy_points", "born_like_points",
        "heavy_with_exact_activation", "born_with_exact_activation", "contingency",
    )}, indent=2))


if __name__ == "__main__":
    main()
