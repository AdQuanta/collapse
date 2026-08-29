"""Relate graph-detector physics to Born similarity in four N=12 campaigns.

The dynamics and ``S_born`` values are read from the completed Zeus results.
Graph features and symmetry-resolved level statistics are read from the ranked
2x3 atlas metadata.  No detector spectrum or dynamics is recomputed here.

The half-filled level-spacing panel is deliberately excluded from quantitative
level-statistics summaries: at ``N_up=N/2`` global spin reversal is an extra
Z2 symmetry, while the saved panel was split only by graph automorphisms.
Mixing its two spin-reversal sectors would bias the distribution toward
Poisson statistics.  The three largest saved non-half-filled sectors are exact
symmetry sectors and form the primary level-statistics summary.
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
    "MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig-network-born-relations")
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.stats import norm, rankdata, spearmanr  # noqa: E402


DYNAMICS_N = 12
SPECTRAL_PROXY_N = 10
ATLAS_ROOT = (
    PROJECT_ROOT / "reports" / "network_sobol_graph_ranked_2x3_2026-08-12"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "reports" / "network_sobol_born_relations_final_2026-08-14"
)

FAMILIES = {
    "erdos_renyi": "Erdos-Renyi",
    "watts_strogatz": "Watts-Strogatz",
    "barabasi_albert": "Barabasi-Albert",
    "expander": "random 4-regular",
}
EXPECTED_COUNTS = {
    "erdos_renyi": 346,
    "watts_strogatz": 334,
    "barabasi_albert": 347,
    "expander": 339,
}

# key -> (label, category).  All logarithms are base ten.
FEATURES: dict[str, tuple[str, str]] = {
    "log_hz": ("log10 hz", "Hamiltonian"),
    "log_J": ("log10 J", "Hamiltonian"),
    "log_Jpm": ("log10 Jpm", "Hamiltonian"),
    "log_Jx": ("log10 Jx", "Hamiltonian"),
    "weak_ratio": ("Jx / weak-limit", "Hamiltonian"),
    "log_hz_over_J": ("log10(hz/J)", "Hamiltonian"),
    "log_Jpm_over_J": ("log10(Jpm/J)", "Hamiltonian"),
    "edge_density": ("edge density", "Graph"),
    "degree_cv": ("degree coefficient of variation", "Graph"),
    "degree_max_over_mean": ("maximum degree / mean degree", "Graph"),
    "mean_clustering": ("mean local clustering", "Graph"),
    "mean_path_length": ("mean shortest-path length", "Graph"),
    "diameter": ("graph diameter", "Graph"),
    "laplacian_gap": ("Laplacian algebraic connectivity", "Graph"),
    "normalized_laplacian_gap": ("normalized-Laplacian gap", "Graph"),
    "adjacency_spectral_radius": ("adjacency spectral radius", "Graph"),
    "adjacency_gap_ratio": ("adjacency absolute-gap ratio", "Graph"),
    "log_automorphism_order": ("log10 graph automorphism order", "Graph"),
    "largest_sector_fraction": ("largest selected sector / 2^N", "Graph"),
    "level_r_mean": ("non-half-filled mean gap ratio", "Exact N=12 spectrum"),
    "level_r_std": ("sector-to-sector std of mean gap ratio", "Exact N=12 spectrum"),
    "level_r_goe_abs_error": ("abs(mean gap ratio - GOE)", "Exact N=12 spectrum"),
    "level_l1_goe": ("level-spacing L1 distance to GOE", "Exact N=12 spectrum"),
    "level_l1_poisson": ("level-spacing L1 distance to Poisson", "Exact N=12 spectrum"),
    "level_goe_advantage": ("L1(Poisson) - L1(GOE)", "Exact N=12 spectrum"),
    "largest_nonhalf_r": ("largest non-half-filled sector mean gap ratio", "Exact N=12 spectrum"),
    "log_proxy_mean_spacing": ("log10 N=10 same-seed mean spacing", "N=10 proxy"),
    "log_Jx_eff_over_proxy_spacing": (
        "log10[(Jx/sqrt(12))/N=10 proxy spacing]",
        "N=10 proxy",
    ),
    "occupied_fraction": ("occupied theta-bin fraction", "Outcome diagnostic"),
}

PARAMETER_CONTROLS = ["log_hz", "log_J", "log_Jpm", "log_Jx"]
GRAPH_FEATURES = [key for key, (_, category) in FEATURES.items() if category == "Graph"]
LEVEL_FEATURES = [
    key for key, (_, category) in FEATURES.items() if category == "Exact N=12 spectrum"
]
PROXY_FEATURES = [
    key for key, (_, category) in FEATURES.items() if category == "N=10 proxy"
]
HAMILTONIAN_FEATURES = [
    key for key, (_, category) in FEATURES.items() if category == "Hamiltonian"
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_log10(value: float) -> float:
    return math.log10(value) if value > 0.0 and math.isfinite(value) else math.nan


def graph_features(metadata: dict[str, Any]) -> dict[str, float]:
    """Return deterministic structural and adjacency-spectrum graph features."""

    n_nodes = int(metadata["nodes"])
    edges = [tuple(map(int, edge)) for edge in metadata["edges_zero_based"]]
    adjacency = np.zeros((n_nodes, n_nodes), dtype=float)
    for left, right in edges:
        if left == right or not (0 <= left < n_nodes and 0 <= right < n_nodes):
            raise ValueError(f"invalid detector edge {(left, right)}")
        adjacency[left, right] = 1.0
        adjacency[right, left] = 1.0
    degrees = np.sum(adjacency, axis=1)
    if np.any(degrees <= 0.0):
        raise ValueError("connected detector graph cannot contain an isolated node")
    mean_degree = float(np.mean(degrees))

    local_clustering = np.zeros(n_nodes, dtype=float)
    for node in range(n_nodes):
        neighbors = np.flatnonzero(adjacency[node])
        if neighbors.size >= 2:
            neighbor_edges = float(np.sum(adjacency[np.ix_(neighbors, neighbors)]) / 2.0)
            local_clustering[node] = 2.0 * neighbor_edges / (
                neighbors.size * (neighbors.size - 1)
            )

    distances: list[int] = []
    diameter = 0
    for source in range(n_nodes):
        distance = np.full(n_nodes, -1, dtype=int)
        distance[source] = 0
        queue = [source]
        for node in queue:
            for neighbor in np.flatnonzero(adjacency[node]):
                if distance[neighbor] < 0:
                    distance[neighbor] = distance[node] + 1
                    queue.append(int(neighbor))
        if np.any(distance < 0):
            raise ValueError("detector graph is disconnected")
        for target in range(source + 1, n_nodes):
            distances.append(int(distance[target]))
        diameter = max(diameter, int(np.max(distance)))

    laplacian = np.diag(degrees) - adjacency
    laplacian_eigenvalues = np.linalg.eigvalsh(laplacian)
    inverse_sqrt_degree = np.diag(1.0 / np.sqrt(degrees))
    normalized_laplacian = inverse_sqrt_degree @ laplacian @ inverse_sqrt_degree
    normalized_eigenvalues = np.linalg.eigvalsh(normalized_laplacian)
    adjacency_eigenvalues = np.linalg.eigvalsh(adjacency)
    absolute_order = np.sort(np.abs(adjacency_eigenvalues))[::-1]
    spectral_radius = float(absolute_order[0])
    adjacency_gap_ratio = (
        (spectral_radius - float(absolute_order[1])) / spectral_radius
        if spectral_radius > 0.0
        else math.nan
    )
    stored_gap = float(metadata["laplacian_algebraic_connectivity"])
    computed_gap = float(laplacian_eigenvalues[1])
    if not math.isclose(stored_gap, computed_gap, rel_tol=1.0e-9, abs_tol=1.0e-10):
        raise ValueError(
            f"stored/computed Laplacian gaps disagree: {stored_gap} versus {computed_gap}"
        )
    return {
        "edge_density": 2.0 * len(edges) / (n_nodes * (n_nodes - 1)),
        "degree_cv": float(np.std(degrees) / mean_degree),
        "degree_max_over_mean": float(np.max(degrees) / mean_degree),
        "mean_clustering": float(np.mean(local_clustering)),
        "mean_path_length": float(np.mean(distances)),
        "diameter": float(diameter),
        "laplacian_gap": computed_gap,
        "normalized_laplacian_gap": float(normalized_eigenvalues[1]),
        "adjacency_spectral_radius": spectral_radius,
        "adjacency_gap_ratio": adjacency_gap_ratio,
    }


def level_features(
    sector_data: dict[str, Any], *, n_nodes: int
) -> dict[str, float]:
    """Aggregate saved exact sectors, excluding unresolved half-filling Z2."""

    sectors = [
        value
        for key, value in sector_data.items()
        if key.startswith("sector_")
        and int(value["hamming_weight"]) != n_nodes // 2
    ]
    if not sectors:
        raise ValueError("no non-half-filled detector sectors were saved")
    weights = np.asarray([int(item["spacing_count"]) for item in sectors], dtype=float)
    weights /= np.sum(weights)
    ratios = np.asarray([float(item["mean_ratio"]) for item in sectors])
    l1_goe = np.asarray([float(item["l1_distances"]["GOE"]) for item in sectors])
    l1_poisson = np.asarray(
        [float(item["l1_distances"]["Poisson"]) for item in sectors]
    )
    mean_ratio = float(np.sum(weights * ratios))
    largest = max(sectors, key=lambda item: int(item["dimension"]))
    return {
        "level_r_mean": mean_ratio,
        "level_r_std": float(np.sqrt(np.sum(weights * (ratios - mean_ratio) ** 2))),
        "level_r_goe_abs_error": abs(mean_ratio - 0.5307),
        "level_l1_goe": float(np.sum(weights * l1_goe)),
        "level_l1_poisson": float(np.sum(weights * l1_poisson)),
        "level_goe_advantage": float(np.sum(weights * (l1_poisson - l1_goe))),
        "largest_nonhalf_r": float(largest["mean_ratio"]),
    }


def load_rows(atlas_root: Path = ATLAS_ROOT) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family, label in FAMILIES.items():
        metadata_dir = atlas_root / family / "metadata"
        if not metadata_dir.is_dir():
            raise FileNotFoundError(f"missing atlas metadata: {metadata_dir}")
        for path in sorted(metadata_dir.glob("*.json")):
            atlas = _read_json(path)
            if "s_born" not in atlas or "graph_metadata" not in atlas:
                continue
            source = Path(atlas["source_dir"])
            run_metadata = _read_json(source / "metadata.json")
            metrics = _read_json(source / "metrics.json")
            graph = atlas["graph_metadata"]
            n_nodes = int(graph["nodes"])
            if n_nodes != DYNAMICS_N:
                raise ValueError(f"unexpected dynamics N={n_nodes} in {path}")
            hz = float(atlas["hz"])
            j = float(atlas["j"])
            jpm = float(atlas["jpm"])
            jx = float(atlas["jx"])
            proxy_spacing = float(atlas["mean_spacing"])
            automorphism_order = int(atlas["source_graph_automorphism_group_order"])
            selected_dimensions = [int(value) for value in atlas["selected_sector_dimensions"]]
            configuration = run_metadata["configuration"]
            row: dict[str, Any] = {
                "family": family,
                "family_label": label,
                "config_id": atlas["config_id"],
                "rank": int(atlas["rank"]),
                "S_born": float(metrics["S_born"]),
                "born_RMSE": float(metrics["born_RMSE_occupied"]),
                "born_L1": float(metrics["born_L1_occupied"]),
                "occupied_fraction": float(metrics["occupied_fraction"]),
                "theta_entropy": float(metrics["theta_entropy"]),
                "hz": hz,
                "J": j,
                "Jpm": jpm,
                "Jx": jx,
                "weak_ratio": float(
                    run_metadata.get(
                        "weak_ratio", configuration.get("weak_ratio", math.nan)
                    )
                ),
                "graph_seed": int(graph["spec"]["seed"]),
                "automorphism_order": automorphism_order,
                "log_hz": _safe_log10(hz),
                "log_J": _safe_log10(j),
                "log_Jpm": _safe_log10(jpm),
                "log_Jx": _safe_log10(jx),
                "log_hz_over_J": _safe_log10(hz / j),
                "log_Jpm_over_J": _safe_log10(jpm / j),
                "log_automorphism_order": _safe_log10(float(automorphism_order)),
                "largest_sector_fraction": max(selected_dimensions) / (1 << n_nodes),
                "proxy_mean_spacing": proxy_spacing,
                "log_proxy_mean_spacing": _safe_log10(proxy_spacing),
                "log_Jx_eff_over_proxy_spacing": _safe_log10(
                    (jx / math.sqrt(n_nodes)) / proxy_spacing
                ),
                "source_dir": str(source.resolve()),
                "atlas_metadata": str(path.resolve()),
            }
            row.update(graph_features(graph))
            row.update(
                level_features(
                    atlas["symmetry_resolved_level_spacings"], n_nodes=n_nodes
                )
            )
            rows.append(row)
    return rows


def _finite_varying_features(rows: list[dict[str, Any]]) -> list[str]:
    output = []
    for key in FEATURES:
        values = np.asarray([float(row.get(key, math.nan)) for row in rows])
        if np.all(np.isfinite(values)) and float(np.ptp(values)) > 1.0e-12:
            output.append(key)
    return output


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


def _rank_residual(values: np.ndarray, controls: np.ndarray) -> np.ndarray:
    design = np.column_stack((np.ones(values.size), controls))
    ranked = rankdata(values)
    return ranked - design @ np.linalg.lstsq(design, ranked, rcond=None)[0]


def correlation_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    rng = np.random.default_rng(20260814)
    for family in FAMILIES:
        subset = [row for row in rows if row["family"] == family]
        y = np.asarray([row["S_born"] for row in subset])
        negative_rmse = -np.asarray([row["born_RMSE"] for row in subset])
        coverage = np.asarray([row["occupied_fraction"] for row in subset])
        coverage_controls = rankdata(coverage)[:, None]
        y_coverage_residual = _rank_residual(y, coverage_controls)
        parameter_controls = np.column_stack(
            [rankdata([row[key] for row in subset]) for key in PARAMETER_CONTROLS]
        )
        y_parameter_residual = _rank_residual(y, parameter_controls)
        available_graph = [
            key for key in GRAPH_FEATURES if key in _finite_varying_features(subset)
        ]
        graph_controls = np.column_stack(
            [parameter_controls]
            + [rankdata([row[key] for row in subset]) for key in available_graph]
        )
        y_full_residual = _rank_residual(y, graph_controls)
        family_rows: list[dict[str, Any]] = []
        for key in _finite_varying_features(subset):
            x = np.asarray([row[key] for row in subset])
            result = spearmanr(x, y)
            category = FEATURES[key][1]
            partial_parameter = math.nan
            partial_parameter_graph = math.nan
            if category not in {"Hamiltonian", "Outcome diagnostic"}:
                x_residual = _rank_residual(x, parameter_controls)
                partial_parameter = float(
                    np.corrcoef(x_residual, y_parameter_residual)[0, 1]
                )
            if category in {"Exact N=12 spectrum", "N=10 proxy"}:
                x_residual = _rank_residual(x, graph_controls)
                partial_parameter_graph = float(
                    np.corrcoef(x_residual, y_full_residual)[0, 1]
                )
            family_rows.append(
                {
                    "family": family,
                    "feature": key,
                    "label": FEATURES[key][0],
                    "category": category,
                    "n": len(subset),
                    "spearman_rho": float(result.statistic),
                    "p_value": float(result.pvalue),
                    "partial_rho_controlling_parameters": partial_parameter,
                    "partial_rho_controlling_parameters_and_graph": partial_parameter_graph,
                    "partial_rho_controlling_coverage": float(
                        np.corrcoef(
                            _rank_residual(x, coverage_controls),
                            y_coverage_residual,
                        )[0, 1]
                    ),
                    "rho_to_coverage": float(spearmanr(x, coverage).statistic),
                    "rho_to_negative_RMSE": float(
                        spearmanr(x, negative_rmse).statistic
                    ),
                    "rho_ci_low": math.nan,
                    "rho_ci_high": math.nan,
                }
            )
        q_values = _benjamini_hochberg(item["p_value"] for item in family_rows)
        for item, q_value in zip(family_rows, q_values, strict=True):
            item["q_value"] = float(q_value)
        for item in sorted(
            family_rows, key=lambda value: -abs(value["spearman_rho"])
        )[:10]:
            x = np.asarray([row[item["feature"]] for row in subset])
            bootstrap = np.empty(500, dtype=float)
            for draw in range(bootstrap.size):
                indices = rng.integers(0, len(subset), len(subset))
                bootstrap[draw] = (
                    float(spearmanr(x[indices], y[indices]).statistic)
                    if np.ptp(x[indices]) > 1.0e-12
                    else math.nan
                )
            item["rho_ci_low"], item["rho_ci_high"] = np.quantile(
                bootstrap[np.isfinite(bootstrap)], [0.025, 0.975]
            )
        output.extend(family_rows)
    return output


def meta_correlation_table(
    correlations: list[dict[str, Any]], *, rho_field: str = "spearman_rho"
) -> list[dict[str, Any]]:
    """Fixed-effect Fisher-z summary of within-family Spearman correlations."""

    output = []
    for feature in FEATURES:
        items = [
            row
            for row in correlations
            if row["feature"] == feature and math.isfinite(row[rho_field])
        ]
        if len(items) < 2:
            continue
        rhos = np.clip([row[rho_field] for row in items], -0.999999, 0.999999)
        weights = np.asarray([row["n"] - 3 for row in items], dtype=float)
        z_values = np.arctanh(rhos)
        z_mean = float(np.sum(weights * z_values) / np.sum(weights))
        standard_error = 1.0 / math.sqrt(float(np.sum(weights)))
        z_score = z_mean / standard_error
        q_statistic = float(np.sum(weights * (z_values - z_mean) ** 2))
        degrees = len(items) - 1
        i_squared = max(0.0, (q_statistic - degrees) / q_statistic) if q_statistic > 0 else 0.0
        output.append(
            {
                "feature": feature,
                "rho_field": rho_field,
                "label": FEATURES[feature][0],
                "category": FEATURES[feature][1],
                "families": len(items),
                "meta_rho": math.tanh(z_mean),
                "ci_low": math.tanh(z_mean - 1.96 * standard_error),
                "ci_high": math.tanh(z_mean + 1.96 * standard_error),
                "p_value": 2.0 * float(norm.sf(abs(z_score))),
                "direction_agreement": max(
                    sum(row[rho_field] > 0 for row in items),
                    sum(row[rho_field] < 0 for row in items),
                )
                / len(items),
                "i_squared": i_squared,
            }
        )
    q_values = _benjamini_hochberg(item["p_value"] for item in output)
    for item, q_value in zip(output, q_values, strict=True):
        item["q_value"] = float(q_value)
    return output


def _fold_for(family: str, config_id: str, salt: str, folds: int) -> int:
    digest = hashlib.sha256(f"{family}|{config_id}|{salt}".encode()).digest()
    return int.from_bytes(digest[:8], "little") % folds


def _fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[np.ndarray, float]:
    intercept = float(np.mean(y))
    coefficients = np.linalg.solve(
        x.T @ x + alpha * np.eye(x.shape[1]), x.T @ (y - intercept)
    )
    return coefficients, intercept


def _standardize_fit(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale[scale < 1.0e-12] = 1.0
    return mean, scale


def cross_validated_ridge(
    rows: list[dict[str, Any]], columns: list[str]
) -> dict[str, float]:
    columns = [
        key
        for key in columns
        if all(math.isfinite(float(row.get(key, math.nan))) for row in rows)
        and np.ptp([row[key] for row in rows]) > 1.0e-12
    ]
    if not columns:
        return {
            "n": len(rows),
            "feature_count": 0,
            "rmse": math.nan,
            "r2": math.nan,
            "median_selected_alpha": math.nan,
        }
    x = np.asarray([[row[key] for key in columns] for row in rows], dtype=float)
    y = np.asarray([row["S_born"] for row in rows], dtype=float)
    outer = np.asarray(
        [_fold_for(row["family"], row["config_id"], "outer", 10) for row in rows]
    )
    prediction = np.full(y.shape, np.nan)
    selected_alphas = []
    alpha_grid = (0.01, 0.1, 1.0, 10.0, 100.0)
    for fold in range(10):
        test = outer == fold
        train = ~test
        inner = np.asarray(
            [
                _fold_for(row["family"], row["config_id"], f"inner-{fold}", 5)
                for row in rows
            ]
        )
        errors = []
        for alpha in alpha_grid:
            squared_errors: list[float] = []
            for inner_fold in range(5):
                validation = train & (inner == inner_fold)
                fitting = train & (inner != inner_fold)
                mean, scale = _standardize_fit(x[fitting])
                coefficients, intercept = _fit_ridge(
                    (x[fitting] - mean) / scale, y[fitting], alpha
                )
                estimate = (x[validation] - mean) / scale @ coefficients + intercept
                squared_errors.extend((estimate - y[validation]) ** 2)
            errors.append(float(np.mean(squared_errors)))
        alpha = alpha_grid[int(np.argmin(errors))]
        selected_alphas.append(alpha)
        mean, scale = _standardize_fit(x[train])
        coefficients, intercept = _fit_ridge((x[train] - mean) / scale, y[train], alpha)
        prediction[test] = (x[test] - mean) / scale @ coefficients + intercept
    residual_sum = float(np.sum((prediction - y) ** 2))
    total_sum = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "n": len(rows),
        "feature_count": len(columns),
        "rmse": math.sqrt(residual_sum / len(rows)),
        "r2": 1.0 - residual_sum / total_sum,
        "median_selected_alpha": float(np.median(selected_alphas)),
    }


def model_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups = {
        "Hamiltonian": HAMILTONIAN_FEATURES,
        "Graph": GRAPH_FEATURES,
        "Exact spectrum": LEVEL_FEATURES,
        "Hamiltonian + graph": HAMILTONIAN_FEATURES + GRAPH_FEATURES,
        "Hamiltonian + exact spectrum": HAMILTONIAN_FEATURES + LEVEL_FEATURES,
        "All exact": HAMILTONIAN_FEATURES + GRAPH_FEATURES + LEVEL_FEATURES,
        "All exact + N=10 proxy": HAMILTONIAN_FEATURES
        + GRAPH_FEATURES
        + LEVEL_FEATURES
        + PROXY_FEATURES,
        "Outcome coverage only": ["occupied_fraction"],
    }
    output = []
    for family in FAMILIES:
        subset = [row for row in rows if row["family"] == family]
        baseline = float(np.std([row["S_born"] for row in subset]))
        output.append(
            {
                "family": family,
                "model": "Mean baseline",
                "n": len(subset),
                "feature_count": 0,
                "rmse": baseline,
                "r2": 0.0,
                "median_selected_alpha": math.nan,
            }
        )
        for name, columns in groups.items():
            output.append(
                {"family": family, "model": name, **cross_validated_ridge(subset, columns)}
            )
    return output


def outcome_diagnostics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for family in FAMILIES:
        subset = [row for row in rows if row["family"] == family]
        score = np.asarray([row["S_born"] for row in subset])
        coverage = np.asarray([row["occupied_fraction"] for row in subset])
        negative_rmse = -np.asarray([row["born_RMSE"] for row in subset])
        output.append(
            {
                "family": family,
                "n": len(subset),
                "S_born_min": float(np.min(score)),
                "S_born_median": float(np.median(score)),
                "S_born_max": float(np.max(score)),
                "occupied_fraction_median": float(np.median(coverage)),
                "rho_S_born_coverage": float(spearmanr(score, coverage).statistic),
                "rho_S_born_negative_RMSE": float(
                    spearmanr(score, negative_rmse).statistic
                ),
            }
        )
    return output


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted(set().union(*(row.keys() for row in rows)))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _plot_correlations(
    correlations: list[dict[str, Any]], meta: list[dict[str, Any]], output: Path
) -> None:
    selected = {
        row["feature"]
        for family in FAMILIES
        for row in sorted(
            [item for item in correlations if item["family"] == family],
            key=lambda item: -abs(item["spearman_rho"]),
        )[:5]
    }
    selected.update(
        row["feature"]
        for row in sorted(meta, key=lambda item: -abs(item["meta_rho"]))[:8]
    )
    ordered = sorted(
        selected,
        key=lambda feature: -max(
            abs(row["spearman_rho"])
            for row in correlations
            if row["feature"] == feature
        ),
    )
    lookup = {(row["feature"], row["family"]): row for row in correlations}
    matrix = np.full((len(ordered), len(FAMILIES)), np.nan)
    for row_index, feature in enumerate(ordered):
        for column_index, family in enumerate(FAMILIES):
            if (feature, family) in lookup:
                matrix[row_index, column_index] = lookup[(feature, family)]["spearman_rho"]
    figure, axis = plt.subplots(
        figsize=(10.5, max(7.0, 0.36 * len(ordered) + 2.0)), constrained_layout=True
    )
    image = axis.imshow(matrix, vmin=-0.65, vmax=0.65, cmap="coolwarm", aspect="auto")
    axis.set_xticks(range(len(FAMILIES)), [FAMILIES[key] for key in FAMILIES])
    axis.set_yticks(range(len(ordered)), [FEATURES[key][0] for key in ordered])
    axis.tick_params(axis="x", labelrotation=15)
    for row_index, feature in enumerate(ordered):
        for column_index, family in enumerate(FAMILIES):
            if (feature, family) in lookup:
                item = lookup[(feature, family)]
                marker = "*" if item["q_value"] < 0.05 else ""
                axis.text(
                    column_index,
                    row_index,
                    f"{item['spearman_rho']:+.2f}{marker}",
                    ha="center",
                    va="center",
                    fontsize=8,
                )
    axis.set_title(r"Within-family association with $S_{\rm Born}$")
    colorbar = figure.colorbar(image, ax=axis, shrink=0.8)
    colorbar.set_label(r"Spearman $\rho$; * within-family BH-FDR $q<0.05$")
    figure.savefig(output / "correlation_heatmap.png", dpi=220)
    figure.savefig(output / "correlation_heatmap.pdf")
    plt.close(figure)


def _plot_models(models: list[dict[str, Any]], output: Path) -> None:
    names = [
        "Hamiltonian",
        "Graph",
        "Exact spectrum",
        "Hamiltonian + graph",
        "Hamiltonian + exact spectrum",
        "All exact",
        "All exact + N=10 proxy",
    ]
    figure, axes = plt.subplots(2, 2, figsize=(12.0, 8.2), sharex=True, constrained_layout=True)
    for axis, family in zip(axes.flat, FAMILIES, strict=True):
        lookup = {row["model"]: row for row in models if row["family"] == family}
        values = [lookup[name]["r2"] for name in names]
        bars = axis.barh(range(len(names)), values, color="#567da5")
        axis.axvline(0.0, color="0.25", linewidth=0.8)
        axis.set_yticks(range(len(names)), names)
        axis.invert_yaxis()
        axis.set_xlabel(r"nested 10-fold CV $R^2$")
        axis.set_title(FAMILIES[family])
        axis.grid(axis="x", alpha=0.2)
        for bar, value in zip(bars, values, strict=True):
            if math.isfinite(value):
                axis.text(
                    value + (0.012 if value >= 0 else -0.012),
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:+.2f}",
                    ha="left" if value >= 0 else "right",
                    va="center",
                    fontsize=8,
                )
    figure.suptitle(r"Held-out additive prediction of $S_{\rm Born}$")
    figure.savefig(output / "model_cross_validation.png", dpi=220)
    figure.savefig(output / "model_cross_validation.pdf")
    plt.close(figure)


def _plot_level_relations(
    rows: list[dict[str, Any]], correlations: list[dict[str, Any]], output: Path
) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(11.0, 8.4), constrained_layout=True)
    lookup = {(row["family"], row["feature"]): row for row in correlations}
    for axis, family in zip(axes.flat, FAMILIES, strict=True):
        subset = [row for row in rows if row["family"] == family]
        x = np.asarray([row["level_goe_advantage"] for row in subset])
        y = np.asarray([row["S_born"] for row in subset])
        color = np.asarray([row["log_Jpm_over_J"] for row in subset])
        points = axis.scatter(x, y, c=color, cmap="viridis", s=13, alpha=0.55, edgecolors="none")
        order = np.argsort(x)
        chunks = np.array_split(order, 8)
        centers = [float(np.median(x[chunk])) for chunk in chunks]
        medians = [float(np.median(y[chunk])) for chunk in chunks]
        axis.plot(centers, medians, "o-", color="#b33b32", linewidth=1.5, markersize=4)
        item = lookup[(family, "level_goe_advantage")]
        axis.set_title(f"{FAMILIES[family]}: rho={item['spearman_rho']:+.2f}")
        axis.set_xlabel("L1(Poisson) - L1(GOE), non-half-filled sectors")
        axis.set_ylabel(r"$S_{\rm Born}$")
        axis.grid(alpha=0.2)
    colorbar = figure.colorbar(points, ax=axes, shrink=0.8)
    colorbar.set_label("log10(Jpm/J)")
    figure.savefig(output / "goe_preference_relations.png", dpi=220)
    figure.savefig(output / "goe_preference_relations.pdf")
    plt.close(figure)


def _format_ci(item: dict[str, Any]) -> str:
    if math.isfinite(item["rho_ci_low"]):
        return f"[{item['rho_ci_low']:+.3f}, {item['rho_ci_high']:+.3f}]"
    return "--"


def markdown_report(
    rows: list[dict[str, Any]],
    correlations: list[dict[str, Any]],
    meta: list[dict[str, Any]],
    meta_accuracy: list[dict[str, Any]],
    meta_coverage: list[dict[str, Any]],
    models: list[dict[str, Any]],
    diagnostics: list[dict[str, Any]],
) -> str:
    lines = [
        "# Network-detector relations to Born similarity",
        "",
        "This is an observational finite-size analysis of the completed N=12 Zeus runs.",
        "Associations are computed within each graph family; they do not establish causation.",
        "",
        "## Essential spectral convention",
        "",
        "The quantitative level-statistics summaries exclude the saved half-filled sector",
        "(`N_up=6`). At half filling, global spin reversal is an additional exact Z2 symmetry.",
        "The saved plot split graph automorphisms but not this Z2, so its displayed spacing",
        "distribution mixes two independent spectra. The retained `N_up=5,4,3` panels are",
        "exact symmetry sectors (including graph automorphisms) and are aggregated with",
        "their spacing counts as weights.",
        "",
        "## Outcome diagnostic",
        "",
        "| family | n | median S_born | range | median coverage | rho(score, coverage) | rho(score, -RMSE) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in diagnostics:
        lines.append(
            f"| {FAMILIES[item['family']]} | {item['n']} | {item['S_born_median']:.3f} "
            f"| [{item['S_born_min']:.3f}, {item['S_born_max']:.3f}] "
            f"| {item['occupied_fraction_median']:.3f} "
            f"| {item['rho_S_born_coverage']:+.3f} "
            f"| {item['rho_S_born_negative_RMSE']:+.3f} |"
        )
    lines.extend(
        [
            "",
            "## Cross-family consistency",
            "",
            "Fixed-effect Fisher-z summaries combine the four within-family Spearman",
            "correlations. Large I2 means the effect is family-dependent, so the pooled",
            "number should not be read as universal.",
            "",
            "| feature | category | meta rho | 95% CI | direction agreement | I2 | BH q |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for item in sorted(meta, key=lambda value: -abs(value["meta_rho"]))[:12]:
        lines.append(
            f"| {item['label']} | {item['category']} | {item['meta_rho']:+.3f} "
            f"| [{item['ci_low']:+.3f}, {item['ci_high']:+.3f}] "
            f"| {item['direction_agreement']:.2f} | {item['i_squared']:.2f} "
            f"| {item['q_value']:.3g} |"
        )
    lines.extend(
        [
            "",
            "### What drives the score: coverage versus occupied-bin accuracy",
            "",
            "| feature | meta rho with coverage | meta rho with -RMSE |",
            "|---|---:|---:|",
        ]
    )
    coverage_lookup = {item["feature"]: item for item in meta_coverage}
    accuracy_lookup = {item["feature"]: item for item in meta_accuracy}
    diagnostic_features = sorted(
        set(coverage_lookup) & set(accuracy_lookup),
        key=lambda feature: -max(
            abs(coverage_lookup[feature]["meta_rho"]),
            abs(accuracy_lookup[feature]["meta_rho"]),
        ),
    )[:12]
    for feature in diagnostic_features:
        lines.append(
            f"| {FEATURES[feature][0]} "
            f"| {coverage_lookup[feature]['meta_rho']:+.3f} "
            f"| {accuracy_lookup[feature]['meta_rho']:+.3f} |"
        )
    lines.extend(["", "## Family-specific strongest relations", ""])
    for family in FAMILIES:
        subset = [row for row in correlations if row["family"] == family]
        top = sorted(subset, key=lambda value: -abs(value["spearman_rho"]))[:10]
        lines.extend(
            [
                f"### {FAMILIES[family]}",
                "",
                "| feature | category | rho | 95% bootstrap CI | BH q | partial: coverage | partial: parameters | partial: parameters+graph | rho(-RMSE) |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for item in top:
            parameter_partial = item["partial_rho_controlling_parameters"]
            full_partial = item["partial_rho_controlling_parameters_and_graph"]
            parameter_text = (
                f"{parameter_partial:+.3f}"
                if math.isfinite(parameter_partial)
                else "--"
            )
            full_text = f"{full_partial:+.3f}" if math.isfinite(full_partial) else "--"
            lines.append(
                f"| {item['label']} | {item['category']} | {item['spearman_rho']:+.3f} "
                f"| {_format_ci(item)} | {item['q_value']:.3g} "
                f"| {item['partial_rho_controlling_coverage']:+.3f} "
                f"| {parameter_text} | {full_text} "
                f"| {item['rho_to_negative_RMSE']:+.3f} |"
            )
        model_lookup = {
            item["model"]: item for item in models if item["family"] == family
        }
        lines.extend(
            [
                "",
                "Nested cross-validated additive prediction:",
                "",
                "| model | features | CV R2 | CV RMSE |",
                "|---|---:|---:|---:|",
            ]
        )
        for model_name in (
            "Hamiltonian",
            "Graph",
            "Exact spectrum",
            "Hamiltonian + graph",
            "Hamiltonian + exact spectrum",
            "All exact",
            "All exact + N=10 proxy",
        ):
            item = model_lookup[model_name]
            lines.append(
                f"| {model_name} | {item['feature_count']} | {item['r2']:+.3f} | {item['rmse']:.4f} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation limits",
            "",
            "- `Jx` in the source configuration is unscaled; the physical collective coupling",
            "  used in dynamics is `Jx/sqrt(12)`. The weak-ratio feature records the conditional",
            "  Sobol constraint, so raw Jx trends are not independent of detector scales.",
            "- The exact N=12 level ratios and L1 distances are scale-free. They diagnose",
            "  level repulsion after the saved spatial-symmetry resolution, apart from the",
            "  excluded half-filled Z2 issue described above.",
            "- The N=10 mean spacing is only a same-seed regenerated-graph proxy. These graph",
            "  families do not possess a canonical N=12 to N=10 reduction, so proxy results",
            "  are reported as sensitivity checks and are not used for the main conclusion.",
            "- Graph-family generator parameters are fixed (ER p=0.3, WS k=4/p=0.3, BA m=2,",
            "  random-regular d=4); graph realization and seed vary by configuration. Within-family",
            "  graph correlations therefore concern realization-to-realization variation.",
            "- Multiple-testing q values are Benjamini-Hochberg adjusted within each family.",
            "  The ten strongest correlations use 500 fixed-seed bootstrap resamples.",
            "- Ridge CV tests additive held-out predictability, not causality. Negative CV R2",
            "  means the feature set performs worse than predicting the family mean.",
            "",
            "## Reproducibility",
            "",
            f"- Dynamics size: N={DYNAMICS_N}; cases analyzed: {len(rows)}.",
            f"- Same-seed spectral proxy size: N={SPECTRAL_PROXY_N}.",
            "- Source atlas: `reports/network_sobol_graph_ranked_2x3_2026-08-12`.",
            "- Random resampling seed: 20260814.",
            "- Prediction: deterministic nested 10-fold outer / 5-fold inner ridge CV.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas-root", type=Path, default=ATLAS_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    rows = load_rows(args.atlas_root.resolve())
    counts = {
        family: sum(row["family"] == family for row in rows) for family in FAMILIES
    }
    if counts != EXPECTED_COUNTS:
        raise RuntimeError(f"unexpected case counts {counts}; expected {EXPECTED_COUNTS}")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)

    correlations = correlation_table(rows)
    meta = meta_correlation_table(correlations)
    meta_accuracy = meta_correlation_table(
        correlations, rho_field="rho_to_negative_RMSE"
    )
    meta_coverage = meta_correlation_table(correlations, rho_field="rho_to_coverage")
    models = model_table(rows)
    diagnostics = outcome_diagnostics(rows)
    _write_csv(output / "feature_table.csv", rows)
    _write_csv(output / "within_family_correlations.csv", correlations)
    _write_csv(output / "cross_family_meta_correlations.csv", meta)
    _write_csv(
        output / "cross_family_meta_correlations_negative_rmse.csv", meta_accuracy
    )
    _write_csv(output / "cross_family_meta_correlations_coverage.csv", meta_coverage)
    _write_csv(output / "cross_validated_models.csv", models)
    _write_csv(output / "outcome_diagnostics.csv", diagnostics)
    _plot_correlations(correlations, meta, output)
    _plot_models(models, output)
    _plot_level_relations(rows, correlations, output)
    (output / "summary.md").write_text(
        markdown_report(
            rows,
            correlations,
            meta,
            meta_accuracy,
            meta_coverage,
            models,
            diagnostics,
        ),
        encoding="utf-8",
    )
    manifest = {
        "analysis": "network Sobol graph-detector relations to Born similarity",
        "dynamics_N": DYNAMICS_N,
        "spectral_proxy_N": SPECTRAL_PROXY_N,
        "counts": counts,
        "total": len(rows),
        "atlas_root": str(args.atlas_root.resolve()),
        "half_filled_sector_excluded": True,
        "reason": "saved N_up=N/2 panel does not split global spin-reversal Z2",
        "outputs": sorted(path.name for path in output.iterdir()),
    }
    (output / "analysis_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
