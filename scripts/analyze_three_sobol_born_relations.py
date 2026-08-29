"""Relate Hamiltonian and N_D=10 spectral features to Born similarity.

This study reads the three approved, per-configuration 2x3 atlases.  It does
not rerun the N=14 dynamics.  Detector quantities come from the already
validated N_D=10 spectral metadata; interaction-shape summaries are computed
from the saved logarithmic V_ab-weight histograms.  Associations are evaluated
within each Sobol campaign so that campaign-dependent parameter ranges are not
mistaken for physical trends.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig-sobol-relation-study")
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.stats import rankdata, spearmanr  # noqa: E402


DETECTOR_N = 10
DYNAMICS_N = 14
DETECTOR_DIMENSION = 1 << DETECTOR_N
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "reports" / "three_sobol_born_relations_final_v2_2026-08-09"
)

CAMPAIGNS = {
    "second_neighbor_hz0_0": {
        "label": r"$h_{z0}=0$, second neighbor",
        "atlas": PROJECT_ROOT
        / "reports"
        / "second_neighbor_mean_spacing_log_ranked_2x3_N14_2026-08-06",
        "hz0": 0.0,
    },
    "nearest_hz0_0": {
        "label": r"$h_{z0}=0$, nearest neighbor",
        "atlas": PROJECT_ROOT
        / "reports"
        / "sobol_hz0_0_mean_spacing_log_ranked_2x3_N14_2026-08-06",
        "hz0": 0.0,
    },
    "nearest_hz0_0p1": {
        "label": r"$h_{z0}=0.1$, nearest neighbor",
        "atlas": PROJECT_ROOT
        / "reports"
        / "sobol_hz0_0p1_hz_0p0999_0p1001_mean_spacing_log_ranked_2x3_N14_2026-08-06",
        "hz0": 0.1,
    },
}


# Feature key -> (plain-text label, category).  Logarithms are base ten.
FEATURES: dict[str, tuple[str, str]] = {
    "log_hz": ("log10 hz", "Hamiltonian"),
    "log_J": ("log10 J", "Hamiltonian"),
    "log_Jpm": ("log10 Jpm", "Hamiltonian"),
    "log_J2": ("log10 J2", "Hamiltonian"),
    "log_Jpm2": ("log10 Jpm2", "Hamiltonian"),
    "log_Jx": ("log10 Jx", "Hamiltonian"),
    "weak_ratio": ("Jx / weak-limit", "Hamiltonian"),
    "log_hz_over_J": ("log10(hz/J)", "Hamiltonian"),
    "log_Jpm_over_J": ("log10(Jpm/J)", "Hamiltonian"),
    "log_J2_over_J": ("log10(J2/J)", "Hamiltonian"),
    "log_Jpm2_over_J2": ("log10(Jpm2/J2)", "Hamiltonian"),
    "log_mean_spacing": ("log10 mean spacing", "Detector spectrum"),
    "resolved_fraction": ("resolved-level fraction", "Detector spectrum"),
    "degeneracy_fraction": ("unresolved/excess fraction", "Detector spectrum"),
    "log_bandwidth": ("log10 detector bandwidth", "Detector spectrum"),
    "vab_special_weight": ("exact degenerate/resonant Vab weight", "Vab shape"),
    "vab_hist_entropy": ("Vab gap-bin entropy", "Vab shape"),
    "vab_hist_participation": ("Vab gap-bin participation", "Vab shape"),
    "vab_log_detuning_mean": ("Vab-weighted mean log10 detuning", "Vab shape"),
    "vab_log_detuning_std": ("Vab-weighted std(log10 detuning)", "Vab shape"),
    "vab_log_detuning_median": ("Vab-weighted median log10 detuning", "Vab shape"),
    "vab_weight_delta_lt_0p1": ("Vab weight: detuning/spacing < 0.1", "Vab shape"),
    "vab_weight_delta_lt_1": ("Vab weight: detuning/spacing < 1", "Vab shape"),
    "vab_weight_delta_lt_10": ("Vab weight: detuning/spacing < 10", "Vab shape"),
    "log_Jx_eff_over_spacing": ("log10[(Jx/sqrt(14))/spacing]", "Interaction scale"),
    "log_Jx_eff_over_bandwidth": ("log10[(Jx/sqrt(14))/bandwidth]", "Interaction scale"),
    "log_golden_rule_proxy": ("log10[(Jx/sqrt(14))^2/spacing]", "Interaction scale"),
    "target_over_spacing": ("2|hz0| / mean spacing", "Interaction scale"),
}

MODEL_GROUPS = {
    "Hamiltonian": [key for key, value in FEATURES.items() if value[1] == "Hamiltonian"],
    "Detector spectrum": [
        key for key, value in FEATURES.items() if value[1] == "Detector spectrum"
    ],
    "Vab shape": [key for key, value in FEATURES.items() if value[1] == "Vab shape"],
    "Interaction scale": [
        key for key, value in FEATURES.items() if value[1] == "Interaction scale"
    ],
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_log10(value: float) -> float:
    return math.log10(value) if value > 0.0 and math.isfinite(value) else math.nan


def _histogram_cdf_at(edges: np.ndarray, weights: np.ndarray, threshold: float) -> float:
    """Estimate cumulative weight assuming uniform density in log(x) per bin."""

    if threshold <= 0.0:
        return 0.0
    total = 0.0
    log_threshold = math.log(threshold)
    for left, right, weight in zip(edges[:-1], edges[1:], weights, strict=True):
        if threshold >= right:
            total += float(weight)
        elif threshold > left:
            fraction = (log_threshold - math.log(left)) / (math.log(right) - math.log(left))
            total += float(weight) * float(np.clip(fraction, 0.0, 1.0))
            break
        else:
            break
    return total


def _weighted_histogram_features(
    edges: np.ndarray, weights: np.ndarray, special_weight: float
) -> dict[str, float]:
    if edges.ndim != 1 or weights.ndim != 1 or edges.size != weights.size + 1:
        raise ValueError("histogram edges and weights have incompatible shapes")
    if np.any(edges <= 0.0) or np.any(np.diff(edges) <= 0.0):
        raise ValueError("Vab histogram edges must be positive and increasing")
    regular = float(np.sum(weights))
    total = regular + special_weight
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=2.0e-8):
        raise ValueError(f"Vab weights sum to {total}, expected one")
    probabilities = weights / regular if regular > 0.0 else np.zeros_like(weights)
    positive = probabilities > 0.0
    entropy = -float(np.sum(probabilities[positive] * np.log(probabilities[positive])))
    entropy_normalized = entropy / math.log(weights.size) if weights.size > 1 else 0.0
    centers_log10 = 0.5 * (np.log10(edges[:-1]) + np.log10(edges[1:]))
    mean = float(np.sum(probabilities * centers_log10)) if regular > 0.0 else math.nan
    variance = (
        float(np.sum(probabilities * (centers_log10 - mean) ** 2))
        if regular > 0.0
        else math.nan
    )
    cumulative = np.cumsum(probabilities)
    median_index = int(np.searchsorted(cumulative, 0.5, side="left"))
    median_index = min(median_index, centers_log10.size - 1)
    return {
        "vab_hist_entropy": entropy_normalized,
        "vab_hist_participation": math.exp(entropy) / weights.size,
        "vab_log_detuning_mean": mean,
        "vab_log_detuning_std": math.sqrt(max(variance, 0.0)),
        "vab_log_detuning_median": float(centers_log10[median_index]),
        "vab_weight_delta_lt_0p1": special_weight
        + _histogram_cdf_at(edges, weights, 0.1),
        "vab_weight_delta_lt_1": special_weight
        + _histogram_cdf_at(edges, weights, 1.0),
        "vab_weight_delta_lt_10": special_weight
        + _histogram_cdf_at(edges, weights, 10.0),
    }


def _load_campaign(campaign: str, specification: dict[str, Any]) -> list[dict[str, Any]]:
    atlas = Path(specification["atlas"])
    metadata_dir = atlas / "metadata"
    if not metadata_dir.is_dir():
        raise FileNotFoundError(f"atlas metadata directory is missing: {metadata_dir}")
    rows: list[dict[str, Any]] = []
    for path in sorted(metadata_dir.glob("*.json")):
        atlas_data = _read_json(path)
        if atlas_data.get("status") != "rendered":
            continue
        source = Path(atlas_data["source_dir"])
        metrics = _read_json(source / "metrics.json")
        run_metadata = _read_json(source / "metadata.json")
        configuration = run_metadata["configuration"]

        mean_spacing = float(atlas_data["mean_spacing"])
        resolved = int(atlas_data["resolved_level_count"])
        bandwidth = mean_spacing * max(resolved - 1, 0)
        jx = float(atlas_data["jx"])
        jx_effective = float(run_metadata.get("Jx_effective", jx / math.sqrt(DYNAMICS_N)))
        special_weight = float(
            atlas_data.get(
                "special_weight",
                atlas_data.get("resonant_weight", atlas_data.get("degenerate_weight", 0.0)),
            )
        )
        edges = np.asarray(atlas_data["histogram_edges"], dtype=float)
        weights = np.asarray(atlas_data["histogram_weights"], dtype=float)
        histogram_features = _weighted_histogram_features(edges, weights, special_weight)

        hz = float(atlas_data["hz"])
        j = float(atlas_data["j"])
        jpm = float(atlas_data["jpm"])
        j2 = float(atlas_data.get("j2", 0.0))
        jpm2 = float(atlas_data.get("jpm2", 0.0))
        target = 2.0 * abs(float(specification["hz0"]))
        row: dict[str, Any] = {
            "campaign": campaign,
            "campaign_label": specification["label"],
            "config_id": atlas_data["config_id"],
            "rank": int(atlas_data["rank"]),
            "S_born": float(metrics["S_born"]),
            "born_RMSE": float(metrics["born_RMSE_occupied"]),
            "born_L1": float(metrics["born_L1_occupied"]),
            "theta_entropy": float(metrics["theta_entropy"]),
            "phi_harmonic_2": float(metrics["phi_harmonic_2"]),
            "occupied_fraction": float(metrics["occupied_fraction"]),
            "hz": hz,
            "J": j,
            "Jpm": jpm,
            "J2": j2,
            "Jpm2": jpm2,
            "Jx": jx,
            "Jx_effective": jx_effective,
            "weak_ratio": float(
                run_metadata.get("weak_ratio", configuration.get("weak_ratio", math.nan))
            ),
            "mean_spacing": mean_spacing,
            "resolved_level_count": resolved,
            "resolved_fraction": resolved / DETECTOR_DIMENSION,
            "degeneracy_fraction": 1.0 - resolved / DETECTOR_DIMENSION,
            "bandwidth": bandwidth,
            "vab_special_weight": special_weight,
            "target_gap": target,
            "target_over_spacing": target / mean_spacing if target > 0.0 else math.nan,
            "log_hz": _safe_log10(hz),
            "log_J": _safe_log10(j),
            "log_Jpm": _safe_log10(jpm),
            "log_J2": _safe_log10(j2),
            "log_Jpm2": _safe_log10(jpm2),
            "log_Jx": _safe_log10(jx),
            "log_hz_over_J": _safe_log10(hz / j),
            "log_Jpm_over_J": _safe_log10(jpm / j),
            "log_J2_over_J": _safe_log10(j2 / j) if j2 > 0.0 else math.nan,
            "log_Jpm2_over_J2": _safe_log10(jpm2 / j2) if jpm2 > 0.0 else math.nan,
            "log_mean_spacing": _safe_log10(mean_spacing),
            "log_bandwidth": _safe_log10(bandwidth),
            "log_Jx_eff_over_spacing": _safe_log10(jx_effective / mean_spacing),
            "log_Jx_eff_over_bandwidth": _safe_log10(jx_effective / bandwidth),
            "log_golden_rule_proxy": _safe_log10(jx_effective**2 / mean_spacing),
            "spectral_validation_ok": bool(
                atlas_data.get("spectral_validation", {}).get(
                    "magnetization_sectors_exploited", False
                )
            ),
        }
        row.update(histogram_features)
        rows.append(row)
    if not rows:
        raise RuntimeError(f"no rendered cases found for {campaign}")
    return sorted(rows, key=lambda item: int(item["rank"]))


def load_all_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for campaign, specification in CAMPAIGNS.items():
        rows.extend(_load_campaign(campaign, specification))
    return rows


def _finite_feature_keys(rows: list[dict[str, Any]]) -> list[str]:
    keys = []
    for key in FEATURES:
        values = np.asarray([float(row.get(key, math.nan)) for row in rows])
        finite = values[np.isfinite(values)]
        if finite.size == len(rows) and float(np.ptp(finite)) > 1.0e-13:
            keys.append(key)
    return keys


def _benjamini_hochberg(p_values: Iterable[float]) -> np.ndarray:
    values = np.asarray(list(p_values), dtype=float)
    order = np.argsort(values)
    adjusted = np.empty_like(values)
    running = 1.0
    count = values.size
    for reverse_rank, index in enumerate(order[::-1], start=1):
        rank = count - reverse_rank + 1
        running = min(running, values[index] * count / rank)
        adjusted[index] = running
    return np.clip(adjusted, 0.0, 1.0)


def correlation_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    rng = np.random.default_rng(20260809)
    for campaign in CAMPAIGNS:
        subset = [row for row in rows if row["campaign"] == campaign]
        y = np.asarray([row["S_born"] for row in subset], dtype=float)
        y_rmse = -np.asarray([row["born_RMSE"] for row in subset], dtype=float)
        coverage = np.asarray([row["occupied_fraction"] for row in subset], dtype=float)
        coverage_design = np.column_stack((np.ones(len(subset)), rankdata(coverage)))
        y_rank = rankdata(y)
        y_rank_residual = y_rank - coverage_design @ np.linalg.lstsq(
            coverage_design, y_rank, rcond=None
        )[0]
        campaign_rows: list[dict[str, Any]] = []
        for key in _finite_feature_keys(subset):
            x = np.asarray([row[key] for row in subset], dtype=float)
            result = spearmanr(x, y)
            x_rank = rankdata(x)
            x_rank_residual = x_rank - coverage_design @ np.linalg.lstsq(
                coverage_design, x_rank, rcond=None
            )[0]
            partial = float(np.corrcoef(x_rank_residual, y_rank_residual)[0, 1])
            campaign_rows.append(
                {
                    "campaign": campaign,
                    "feature": key,
                    "label": FEATURES[key][0],
                    "category": FEATURES[key][1],
                    "n": len(subset),
                    "spearman_rho": float(result.statistic),
                    "partial_rho_controlling_coverage": partial,
                    "spearman_rho_to_negative_rmse": float(
                        spearmanr(x, y_rmse).statistic
                    ),
                    "p_value": float(result.pvalue),
                    "rho_ci_low": math.nan,
                    "rho_ci_high": math.nan,
                }
            )
        q_values = _benjamini_hochberg(item["p_value"] for item in campaign_rows)
        for item, q_value in zip(campaign_rows, q_values, strict=True):
            item["q_value"] = float(q_value)
        top = sorted(campaign_rows, key=lambda item: -abs(item["spearman_rho"]))[:8]
        for item in top:
            x = np.asarray([row[item["feature"]] for row in subset], dtype=float)
            bootstrap = np.empty(500, dtype=float)
            for draw in range(bootstrap.size):
                indices = rng.integers(0, len(subset), size=len(subset))
                bootstrap[draw] = float(spearmanr(x[indices], y[indices]).statistic)
            item["rho_ci_low"], item["rho_ci_high"] = np.quantile(
                bootstrap, [0.025, 0.975]
            )
        output.extend(campaign_rows)
    return output


def outcome_diagnostics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Describe how the ranked score relates to support and occupied-bin error."""

    output = []
    for campaign in CAMPAIGNS:
        subset = [row for row in rows if row["campaign"] == campaign]
        s_born = np.asarray([row["S_born"] for row in subset], dtype=float)
        coverage = np.asarray([row["occupied_fraction"] for row in subset], dtype=float)
        negative_rmse = -np.asarray([row["born_RMSE"] for row in subset], dtype=float)
        entropy = np.asarray([row["theta_entropy"] for row in subset], dtype=float)
        output.append(
            {
                "campaign": campaign,
                "n": len(subset),
                "S_born_min": float(np.min(s_born)),
                "S_born_median": float(np.median(s_born)),
                "S_born_max": float(np.max(s_born)),
                "occupied_fraction_median": float(np.median(coverage)),
                "rho_S_born_occupied_fraction": float(
                    spearmanr(s_born, coverage).statistic
                ),
                "rho_S_born_negative_RMSE": float(
                    spearmanr(s_born, negative_rmse).statistic
                ),
                "rho_S_born_theta_entropy": float(
                    spearmanr(s_born, entropy).statistic
                ),
            }
        )
    return output


def _fold_for(campaign: str, config_id: str, salt: str, folds: int) -> int:
    digest = hashlib.sha256(f"{campaign}|{config_id}|{salt}".encode()).digest()
    return int.from_bytes(digest[:8], "little") % folds


def _fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[np.ndarray, float]:
    mean_y = float(np.mean(y))
    gram = x.T @ x + alpha * np.eye(x.shape[1])
    coefficients = np.linalg.solve(gram, x.T @ (y - mean_y))
    return coefficients, mean_y


def _standardize_fit(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale[scale < 1.0e-12] = 1.0
    return mean, scale


def cross_validated_ridge(
    rows: list[dict[str, Any]], columns: list[str]
) -> tuple[dict[str, float], np.ndarray]:
    columns = [
        key
        for key in columns
        if all(math.isfinite(float(row.get(key, math.nan))) for row in rows)
        and np.ptp([float(row[key]) for row in rows]) > 1.0e-13
    ]
    if not columns:
        raise ValueError("ridge model has no finite nonconstant features")
    x = np.asarray([[row[key] for key in columns] for row in rows], dtype=float)
    y = np.asarray([row["S_born"] for row in rows], dtype=float)
    outer = np.asarray(
        [_fold_for(row["campaign"], row["config_id"], "outer", 10) for row in rows]
    )
    predictions = np.full(y.shape, np.nan)
    selected_alphas: list[float] = []
    alpha_grid = (0.01, 0.1, 1.0, 10.0, 100.0)
    for fold in range(10):
        test = outer == fold
        train = ~test
        if not np.any(test):
            continue
        inner = np.asarray(
            [
                _fold_for(row["campaign"], row["config_id"], f"inner-{fold}", 5)
                for row in rows
            ]
        )
        alpha_errors: list[float] = []
        for alpha in alpha_grid:
            errors: list[float] = []
            for inner_fold in range(5):
                validation = train & (inner == inner_fold)
                fitting = train & (inner != inner_fold)
                if not np.any(validation) or not np.any(fitting):
                    continue
                mean, scale = _standardize_fit(x[fitting])
                x_fit = (x[fitting] - mean) / scale
                coefficients, intercept = _fit_ridge(x_fit, y[fitting], alpha)
                predicted = (x[validation] - mean) / scale @ coefficients + intercept
                errors.extend((predicted - y[validation]) ** 2)
            alpha_errors.append(float(np.mean(errors)))
        alpha = alpha_grid[int(np.argmin(alpha_errors))]
        selected_alphas.append(alpha)
        mean, scale = _standardize_fit(x[train])
        coefficients, intercept = _fit_ridge((x[train] - mean) / scale, y[train], alpha)
        predictions[test] = (x[test] - mean) / scale @ coefficients + intercept
    if not np.all(np.isfinite(predictions)):
        raise RuntimeError("cross-validation left non-finite predictions")
    residual_sum = float(np.sum((predictions - y) ** 2))
    total_sum = float(np.sum((y - np.mean(y)) ** 2))
    return (
        {
            "n": len(rows),
            "feature_count": len(columns),
            "rmse": math.sqrt(residual_sum / len(rows)),
            "r2": 1.0 - residual_sum / total_sum,
            "median_selected_alpha": float(np.median(selected_alphas)),
        },
        predictions,
    )


def model_table(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    output: list[dict[str, Any]] = []
    predictions: dict[str, np.ndarray] = {}
    for campaign in CAMPAIGNS:
        subset = [row for row in rows if row["campaign"] == campaign]
        available = set(_finite_feature_keys(subset))
        groups = {
            name: [key for key in keys if key in available]
            for name, keys in MODEL_GROUPS.items()
        }
        groups["All physical"] = sorted(set().union(*map(set, groups.values())))
        groups["Coverage diagnostic"] = ["occupied_fraction"]
        groups["All physical + coverage"] = groups["All physical"] + [
            "occupied_fraction"
        ]
        y = np.asarray([row["S_born"] for row in subset], dtype=float)
        baseline_rmse = math.sqrt(float(np.mean((y - np.mean(y)) ** 2)))
        output.append(
            {
                "campaign": campaign,
                "model": "Mean baseline",
                "n": len(subset),
                "feature_count": 0,
                "rmse": baseline_rmse,
                "r2": 0.0,
                "median_selected_alpha": math.nan,
            }
        )
        for name, columns in groups.items():
            metrics, predicted = cross_validated_ridge(subset, columns)
            output.append({"campaign": campaign, "model": name, **metrics})
            if name == "All physical + coverage":
                predictions[campaign] = predicted
    return output, predictions


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = sorted(set().union(*(row.keys() for row in rows)))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _plot_correlations(correlations: list[dict[str, Any]], output: Path) -> None:
    selected = set()
    for campaign in CAMPAIGNS:
        subset = [row for row in correlations if row["campaign"] == campaign]
        selected.update(
            row["feature"]
            for row in sorted(subset, key=lambda item: -abs(item["spearman_rho"]))[:6]
        )
    ordered = sorted(
        selected,
        key=lambda feature: -max(
            abs(row["spearman_rho"])
            for row in correlations
            if row["feature"] == feature
        ),
    )
    matrix = np.full((len(ordered), len(CAMPAIGNS)), np.nan)
    campaign_names = list(CAMPAIGNS)
    lookup = {(row["feature"], row["campaign"]): row for row in correlations}
    for i, feature in enumerate(ordered):
        for j, campaign in enumerate(campaign_names):
            if (feature, campaign) in lookup:
                matrix[i, j] = lookup[(feature, campaign)]["spearman_rho"]
    height = max(6.0, 0.38 * len(ordered) + 1.8)
    figure, axis = plt.subplots(figsize=(9.2, height), constrained_layout=True)
    image = axis.imshow(matrix, vmin=-0.7, vmax=0.7, cmap="coolwarm", aspect="auto")
    axis.set_xticks(range(len(campaign_names)), [CAMPAIGNS[key]["label"] for key in campaign_names])
    axis.set_yticks(range(len(ordered)), [FEATURES[key][0] for key in ordered])
    axis.tick_params(axis="x", labelrotation=12)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if np.isfinite(matrix[i, j]):
                row = lookup[(ordered[i], campaign_names[j])]
                marker = "*" if row["q_value"] < 0.05 else ""
                axis.text(j, i, f"{matrix[i, j]:+.2f}{marker}", ha="center", va="center", fontsize=8)
    axis.set_title(r"Within-campaign Spearman association with $S_{\rm Born}$")
    colorbar = figure.colorbar(image, ax=axis, shrink=0.82)
    colorbar.set_label(r"Spearman $\rho$; * BH-FDR $q<0.05$")
    figure.savefig(output / "correlation_heatmap.png", dpi=220)
    figure.savefig(output / "correlation_heatmap.pdf")
    plt.close(figure)


def _plot_top_relations(
    rows: list[dict[str, Any]], correlations: list[dict[str, Any]], output: Path
) -> None:
    figure, axes = plt.subplots(3, 2, figsize=(11.2, 12.2), constrained_layout=True)
    for row_index, campaign in enumerate(CAMPAIGNS):
        subset = [row for row in rows if row["campaign"] == campaign]
        candidates = [row for row in correlations if row["campaign"] == campaign]
        top = sorted(candidates, key=lambda item: -abs(item["spearman_rho"]))[:2]
        for column_index, correlation in enumerate(top):
            axis = axes[row_index, column_index]
            key = correlation["feature"]
            x = np.asarray([row[key] for row in subset], dtype=float)
            y = np.asarray([row["S_born"] for row in subset], dtype=float)
            axis.scatter(x, y, s=11, alpha=0.28, color="#496f9b", edgecolors="none")
            order = np.argsort(x)
            chunks = np.array_split(order, 8)
            centers = np.asarray([np.median(x[chunk]) for chunk in chunks])
            medians = np.asarray([np.median(y[chunk]) for chunk in chunks])
            low = np.asarray([np.quantile(y[chunk], 0.16) for chunk in chunks])
            high = np.asarray([np.quantile(y[chunk], 0.84) for chunk in chunks])
            axis.plot(centers, medians, "o-", color="#c23b32", linewidth=1.5, markersize=4)
            axis.fill_between(centers, low, high, color="#c23b32", alpha=0.14)
            axis.set_xlabel(FEATURES[key][0])
            axis.set_ylabel(r"$S_{\rm Born}$")
            axis.grid(alpha=0.2)
            ci = ""
            if math.isfinite(correlation["rho_ci_low"]):
                ci = (
                    f"\n95% bootstrap CI "
                    f"[{correlation['rho_ci_low']:+.2f}, {correlation['rho_ci_high']:+.2f}]"
                )
            axis.set_title(
                f"{CAMPAIGNS[campaign]['label']}\n"
                f"rho={correlation['spearman_rho']:+.2f}, q={correlation['q_value']:.2g}{ci}",
                fontsize=10,
            )
    figure.suptitle("Strongest monotonic relations (points and equal-count-bin summaries)")
    figure.savefig(output / "top_relations.png", dpi=220)
    figure.savefig(output / "top_relations.pdf")
    plt.close(figure)


def _plot_models(models: list[dict[str, Any]], output: Path) -> None:
    names = [
        "Hamiltonian",
        "Detector spectrum",
        "Vab shape",
        "Interaction scale",
        "All physical",
        "Coverage diagnostic",
        "All physical + coverage",
    ]
    figure, axes = plt.subplots(1, 3, figsize=(12.5, 4.3), sharey=True, constrained_layout=True)
    for axis, campaign in zip(axes, CAMPAIGNS, strict=True):
        lookup = {
            row["model"]: row
            for row in models
            if row["campaign"] == campaign
        }
        values = [lookup[name]["r2"] for name in names]
        bars = axis.barh(range(len(names)), values, color="#597fa8")
        axis.axvline(0.0, color="0.25", linewidth=0.8)
        axis.set_yticks(range(len(names)), names)
        axis.invert_yaxis()
        axis.set_xlabel(r"nested 10-fold CV $R^2$")
        axis.set_title(CAMPAIGNS[campaign]["label"], fontsize=10)
        axis.grid(axis="x", alpha=0.2)
        for bar, value in zip(bars, values, strict=True):
            axis.text(
                value + (0.015 if value >= 0 else -0.015),
                bar.get_y() + bar.get_height() / 2,
                f"{value:+.2f}",
                ha="left" if value >= 0 else "right",
                va="center",
                fontsize=8,
            )
    figure.suptitle(r"Held-out prediction of $S_{\rm Born}$ with ridge models")
    figure.savefig(output / "model_cross_validation.png", dpi=220)
    figure.savefig(output / "model_cross_validation.pdf")
    plt.close(figure)


def _markdown_report(
    rows: list[dict[str, Any]],
    correlations: list[dict[str, Any]],
    models: list[dict[str, Any]],
    diagnostics: list[dict[str, Any]],
) -> str:
    lines = [
        "# Hamiltonian, detector-spectrum, and interaction relations to Born similarity",
        "",
        "This is an observational analysis of the completed Sobol configurations, not a causal test.",
        "All correlations are computed **within each campaign**. Detector spectral summaries use",
        "the approved N_D=10 diagonalizations, which exploited total-magnetization sectors.",
        "The dynamics and S_born values are the original N=14 results.",
        "",
        "## Outcome diagnostic",
        "",
        "S_born evaluates the full theta interval and assigns R=1/2 to empty bins; it therefore",
        "mixes angular support with agreement on occupied bins. The table quantifies that split.",
        "",
        "| campaign | median occupied fraction | rho(S_born, coverage) | rho(S_born, -RMSE) | rho(S_born, theta entropy) |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in diagnostics:
        lines.append(
            f"| {item['campaign']} | {item['occupied_fraction_median']:.3f} "
            f"| {item['rho_S_born_occupied_fraction']:+.3f} "
            f"| {item['rho_S_born_negative_RMSE']:+.3f} "
            f"| {item['rho_S_born_theta_entropy']:+.3f} |"
        )
    correlation_lookup = {
        (item["campaign"], item["feature"]): item for item in correlations
    }
    model_lookup_all = {
        (item["campaign"], item["model"]): item for item in models
    }
    second_scale = correlation_lookup[
        ("second_neighbor_hz0_0", "log_Jx_eff_over_spacing")
    ]
    nearest_scale = correlation_lookup[("nearest_hz0_0", "log_Jx_eff_over_spacing")]
    second_near = correlation_lookup[
        ("second_neighbor_hz0_0", "vab_weight_delta_lt_1")
    ]
    nearest_near = correlation_lookup[("nearest_hz0_0", "vab_weight_delta_lt_1")]
    resonant_near = correlation_lookup[
        ("nearest_hz0_0p1", "vab_weight_delta_lt_1")
    ]
    resonant_median = correlation_lookup[
        ("nearest_hz0_0p1", "vab_log_detuning_median")
    ]
    resonant_ratio = correlation_lookup[("nearest_hz0_0p1", "log_Jpm_over_J")]
    lines.extend(
        [
            "",
            "## Main synthesis",
            "",
            "- The most reproducible common hz0=0 relation is a larger effective interaction",
            "  relative to detector mean spacing: rho="
            f"{second_scale['spearman_rho']:+.3f} (second neighbor) and "
            f"{nearest_scale['spearman_rho']:+.3f} (nearest neighbor). The signs survive both "
            "coverage control and the -RMSE check, although the partial effects are small "
            f"({second_scale['partial_rho_controlling_coverage']:+.3f}, "
            f"{nearest_scale['partial_rho_controlling_coverage']:+.3f}).",
            "- More Vab power within one detector spacing of zero detuning also raises raw",
            f"  S_born (rho={second_near['spearman_rho']:+.3f} and "
            f"{nearest_near['spearman_rho']:+.3f}). In the nearest-neighbor campaign it has "
            f"the opposite relation to occupied-bin accuracy (rho(-RMSE)="
            f"{nearest_near['spearman_rho_to_negative_rmse']:+.3f}), so much of this trend is "
            "support broadening rather than pointwise Born agreement.",
            "- At hz0=0.1 the resonance condition around 2|hz0| dominates raw S_born:",
            f"  weight within one spacing has rho={resonant_near['spearman_rho']:+.3f}, and the "
            f"weighted median detuning has rho={resonant_median['spearman_rho']:+.3f}. Both "
            "reverse sign for -RMSE "
            f"({resonant_near['spearman_rho_to_negative_rmse']:+.3f}, "
            f"{resonant_median['spearman_rho_to_negative_rmse']:+.3f}). Thus resonance fills "
            "theta support but does not improve the conditional occupied-bin ratio.",
            f"- In that nonzero-hz0 campaign, smaller Jpm/J raises raw S_born "
            f"(rho={resonant_ratio['spearman_rho']:+.3f}), while larger Jpm/J improves "
            f"occupied-bin accuracy (rho(-RMSE)={resonant_ratio['spearman_rho_to_negative_rmse']:+.3f}).",
            "- J2 and Jpm2 show no direct monotonic association with raw S_born in the",
            "  second-neighbor campaign (all corresponding |rho| <= 0.057). Their benefit, if",
            "  any, is mediated through spectral density/eigenstate structure or interactions",
            "  with the other couplings rather than a simple one-parameter trend.",
            "- All physical features predict held-out S_born with CV R2="
            f"{model_lookup_all[('second_neighbor_hz0_0', 'All physical')]['r2']:.3f}, "
            f"{model_lookup_all[('nearest_hz0_0', 'All physical')]['r2']:.3f}, and "
            f"{model_lookup_all[('nearest_hz0_0p1', 'All physical')]['r2']:.3f}. Adding the "
            "coverage diagnostic materially helps only the nonzero-hz0 campaign, reaching "
            f"{model_lookup_all[('nearest_hz0_0p1', 'All physical + coverage')]['r2']:.3f}.",
            "",
        "## Campaign-level results",
        "",
        ]
    )
    for campaign in CAMPAIGNS:
        subset = [row for row in rows if row["campaign"] == campaign]
        corr = [row for row in correlations if row["campaign"] == campaign]
        top = sorted(corr, key=lambda item: -abs(item["spearman_rho"]))[:8]
        model_lookup = {
            row["model"]: row for row in models if row["campaign"] == campaign
        }
        lines.extend(
            [
                f"### {campaign} (n={len(subset)})",
                "",
                "| feature | category | rho(S_born) | partial rho controlling coverage | rho(-RMSE) | 95% bootstrap CI | BH q |",
                "|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for item in top:
            ci = (
                f"[{item['rho_ci_low']:+.3f}, {item['rho_ci_high']:+.3f}]"
                if math.isfinite(item["rho_ci_low"])
                else "not bootstrapped"
            )
            lines.append(
                f"| {item['label']} | {item['category']} | {item['spearman_rho']:+.3f} "
                f"| {item['partial_rho_controlling_coverage']:+.3f} "
                f"| {item['spearman_rho_to_negative_rmse']:+.3f} "
                f"| {ci} | {item['q_value']:.3g} |"
            )
        lines.extend(
            [
                "",
                "Held-out nested-CV ridge performance:",
                "",
                "| model | features | CV R2 | CV RMSE |",
                "|---|---:|---:|---:|",
            ]
        )
        for name in (
            "Hamiltonian",
            "Detector spectrum",
            "Vab shape",
            "Interaction scale",
            "All physical",
            "Coverage diagnostic",
            "All physical + coverage",
        ):
            item = model_lookup[name]
            lines.append(
                f"| {name} | {item['feature_count']} | {item['r2']:+.3f} | {item['rmse']:.4f} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation and limitations",
            "",
            "- S_born is a similarity score, so a positive rho means that increasing the listed",
            "  feature is associated with a more Born-like R(theta) within that campaign.",
            "  The partial rho removes the linear rank effect of the 64-bin occupied fraction,",
            "  and rho(-RMSE) checks the direction against the occupied-bin error diagnostic.",
            "- The Vab histogram uses |Ea-Eb|/<s> for hz0=0 and",
            "  ||Ea-Eb|-2|hz0||/<s> for hz0=0.1. Threshold weights and log moments are",
            "  reconstructed from the saved logarithmic bins, assuming uniform density in log",
            "  detuning inside a partially crossed bin.",
            "- Jx is sampled under a conditional weak-coupling constraint. Consequently its raw",
            "  correlation mixes coupling strength with the scale that imposed the constraint.",
            "  The dimensionless Jx/sqrt(14)-to-spacing and -to-bandwidth ratios are more physical.",
            "- With Jy=0, normalizing |Vab|^2 to unit total weight removes the overall Jx factor.",
            "  Vab-shape features therefore probe detector eigenstates and selection rules, while",
            "  the interaction-scale features retain the absolute coupling strength.",
            "- Resolved-level fraction and mean spacing use the full detector spectrum after",
            "  magnetization-block diagonalization. Other unresolved symmetries can still create",
            "  degeneracies; no claim of GOE/GUE/Poisson universality is made here.",
            "- Ridge CV measures additive out-of-sample predictability, not causation. Negative CV",
            "  R2 means the feature family does worse than predicting the campaign mean.",
            "",
            "## Reproducibility",
            "",
            f"- Dynamics size: N={DYNAMICS_N}; detector spectral size: N_D={DETECTOR_N}.",
            f"- Total completed configurations: {len(rows)}.",
            "- Spearman p-values are adjusted within campaign by Benjamini-Hochberg FDR.",
            "- The eight largest absolute correlations per campaign use 500 fixed-seed bootstrap",
            "  resamples for their confidence intervals.",
            "- Predictive scores use deterministic nested 10-fold outer / 5-fold inner ridge CV.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()

    rows = load_all_rows()
    expected = {
        "second_neighbor_hz0_0": 343,
        "nearest_hz0_0": 329,
        "nearest_hz0_0p1": 400,
    }
    counts = {campaign: sum(row["campaign"] == campaign for row in rows) for campaign in CAMPAIGNS}
    if counts != expected:
        raise RuntimeError(f"unexpected campaign counts: {counts}; expected {expected}")
    if not all(row["spectral_validation_ok"] for row in rows):
        raise RuntimeError("at least one N_D=10 spectral calculation did not exploit magnetization")
    output.mkdir(parents=True, exist_ok=False)

    correlations = correlation_table(rows)
    diagnostics = outcome_diagnostics(rows)
    models, predictions = model_table(rows)
    for campaign, predicted in predictions.items():
        subset = [row for row in rows if row["campaign"] == campaign]
        for row, value in zip(subset, predicted, strict=True):
            row["cv_prediction_all_physical_plus_coverage"] = float(value)

    _write_csv(output / "configuration_features.csv", rows)
    _write_csv(output / "within_campaign_correlations.csv", correlations)
    _write_csv(output / "outcome_diagnostics.csv", diagnostics)
    _write_csv(output / "nested_cv_models.csv", models)
    _plot_correlations(correlations, output)
    _plot_top_relations(rows, correlations, output)
    _plot_models(models, output)
    (output / "report.md").write_text(
        _markdown_report(rows, correlations, models, diagnostics), encoding="utf-8"
    )
    provenance = {
        "schema_version": 1,
        "dynamics_n": DYNAMICS_N,
        "detector_n": DETECTOR_N,
        "campaign_counts": counts,
        "campaigns": {
            key: {
                **value,
                "atlas": Path(value["atlas"])
                .resolve()
                .relative_to(PROJECT_ROOT.resolve())
                .as_posix(),
            }
            for key, value in CAMPAIGNS.items()
        },
        "notes": [
            "No N=14 dynamics were rerun.",
            "N_D=10 spectral metadata came from magnetization-sector diagonalization.",
            "Vab histogram partial-bin CDFs assume uniform density in log detuning.",
        ],
    }
    (output / "provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )
    print(json.dumps({"output": str(output), "counts": counts}, indent=2))


if __name__ == "__main__":
    main()
