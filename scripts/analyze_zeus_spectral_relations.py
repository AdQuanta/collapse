"""Relate exact detector-sector spectra to root geometry after Zeus completes.

Identically parameterized ring/random-network controls and explicit physical
architecture controls are included.
Detector level statistics are computed separately inside the largest exact
irreducible sectors returned by the complete graph-automorphism, Hamming-weight,
and half-filling spin-reversal resolver. Mixed-sector spacings are never used.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
import math

import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

from plot_zeus_hamiltonian_classification import load_complete_results  # noqa: E402
from core.detector_graphs import detector_graph_edges, detector_graph_metadata  # noqa: E402
from core.graph_spectral_sectors import (  # noqa: E402
    detector_hamiltonian_block,
    fixed_weight_states,
    largest_detector_symmetry_sectors,
)
from core.hamiltonian_classification import SinglePixelClassificationPoint  # noqa: E402
from core.level_spacing import (  # noqa: E402
    compute_level_spacing_ratios,
    compute_level_spacings,
)


SPECTRAL_CAMPAIGNS = {
    "cross_network_matched",
    "cross_architecture_ring_control",
    "cross_physical_architectures",
}
RANDOM_GRAPH_ARCHITECTURES = {
    "erdos_renyi",
    "watts_strogatz",
    "barabasi_albert",
    "expander",
}
SPECTRAL_FEATURES = (
    "detector_mean_adjacent_gap_ratio",
    "distance_to_goe_ratio",
    "distance_to_poisson_ratio",
    "detector_bandwidth",
    "median_resolved_sector_spacing",
    "edge_Jx_over_bandwidth",
    "edge_Jx_over_median_spacing",
    "graph_algebraic_connectivity",
    "graph_degree_variance",
    "graph_automorphism_group_order",
)
ROOT_OUTCOMES = (
    "coverage",
    "density_ratio_cross_residual",
    "higher_harmonic_leakage",
    "dipole_sharpness",
    "axis_fidelity",
    "epsilon_B",
    "polar_S_born",
)


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values)
    ranked = values[order]
    adjusted = ranked * values.size / np.arange(1, values.size + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    output = np.empty_like(adjusted)
    output[order] = np.clip(adjusted, 0.0, 1.0)
    return output.tolist()


def detector_spectral_features(row: dict[str, str]) -> dict[str, object]:
    point = SinglePixelClassificationPoint(**json.loads(row["parameters"]))
    edges = detector_graph_edges(point.detector_n, point.detector_graph_spec())
    active_edges = edges if point.J != 0.0 or point.Jpm != 0.0 else ()
    if active_edges:
        sectors, validation = largest_detector_symmetry_sectors(
            point.detector_n,
            active_edges,
            hz=point.hz,
            j=point.J,
            jpm=point.Jpm,
            count=4,
        )
    else:
        sectors = []
        validation = {
            "automorphism_group_order": math.factorial(point.detector_n),
            "selection_rule": (
                "noninteracting detector: fixed-Hamming-weight blocks are "
                "exactly degenerate, so adjacent-gap statistics are undefined"
            ),
        }
    ratios: list[np.ndarray] = []
    spacings: list[np.ndarray] = []
    sector_ratios: list[float] = []
    for sector in sectors:
        tolerance = 1.0e-10 * max(float(np.ptp(sector.energies)), 1.0)
        sector_spacings = compute_level_spacings(sector.energies, tol=tolerance)
        sector_gap_ratios = compute_level_spacing_ratios(sector_spacings)
        spacings.append(sector_spacings)
        ratios.append(sector_gap_ratios)
        sector_ratios.append(
            float(np.mean(sector_gap_ratios)) if sector_gap_ratios.size else np.nan
        )
    nonempty_ratios = [item for item in ratios if item.size]
    nonempty_spacings = [item for item in spacings if item.size]
    pooled_ratios = (
        np.concatenate(nonempty_ratios) if nonempty_ratios else np.array([])
    )
    pooled_spacings = (
        np.concatenate(nonempty_spacings) if nonempty_spacings else np.array([])
    )

    minimum = np.inf
    maximum = -np.inf
    for weight in range(point.detector_n + 1):
        states = fixed_weight_states(point.detector_n, weight)
        block = detector_hamiltonian_block(
            point.detector_n,
            active_edges,
            states,
            hz=point.hz,
            j=point.J,
            jpm=point.Jpm,
        )
        energies = np.linalg.eigvalsh(block)
        minimum = min(minimum, float(energies[0]))
        maximum = max(maximum, float(energies[-1]))
    bandwidth = maximum - minimum
    median_spacing = (
        float(np.median(pooled_spacings)) if pooled_spacings.size else np.nan
    )
    mean_ratio = float(np.mean(pooled_ratios)) if pooled_ratios.size else np.nan
    if active_edges:
        graph = detector_graph_metadata(point.detector_n, point.detector_graph_spec())
    else:
        graph = {
            "edge_count": 0,
            "laplacian_algebraic_connectivity": 0.0,
            "degree_variance": 0.0,
        }
    edge_jx = point.effective_central_couplings()["Jx"]
    if row["campaign"] == "cross_network_matched":
        architecture = point.connectivity
    elif row["campaign"] == "cross_physical_architectures":
        architecture = row["scan_value"]
    else:
        architecture = "ring"
    return {
        "point_id": int(row["point_id"]),
        "campaign": row["campaign"],
        "architecture": architecture,
        "N": point.detector_n,
        "seed": point.seed,
        "time": point.time,
        "detector_mean_adjacent_gap_ratio": mean_ratio,
        "distance_to_goe_ratio": abs(mean_ratio - 0.5307),
        "distance_to_poisson_ratio": abs(mean_ratio - 0.3863),
        "detector_bandwidth": bandwidth,
        "median_resolved_sector_spacing": median_spacing,
        "edge_Jx": edge_jx,
        "edge_Jx_over_bandwidth": edge_jx / bandwidth,
        "edge_Jx_over_median_spacing": (
            edge_jx / median_spacing if np.isfinite(median_spacing) else np.nan
        ),
        "graph_edge_count": graph["edge_count"],
        "graph_algebraic_connectivity": graph[
            "laplacian_algebraic_connectivity"
        ],
        "graph_degree_variance": graph["degree_variance"],
        "graph_automorphism_group_order": validation["automorphism_group_order"],
        "sector_dimensions": json.dumps([sector.dimension for sector in sectors]),
        "sector_labels": json.dumps([sector.symmetry_label for sector in sectors]),
        "sector_mean_gap_ratios": json.dumps(sector_ratios),
        "sector_equivalent_copy_counts": json.dumps(
            [sector.equivalent_copy_count for sector in sectors]
        ),
        "sector_resolution": validation["selection_rule"],
        "coverage": row["coverage"],
        "density_ratio_cross_residual": row["density_ratio_cross_residual"],
        "higher_harmonic_leakage": row["higher_harmonic_leakage"],
        "dipole_sharpness": row["dipole_sharpness"],
        "axis_fidelity": row["axis_fidelity"],
        "epsilon_B": row["epsilon_B"],
        "polar_S_born": row["polar_S_born"],
        "case_dir": row["case_dir"],
    }


def _finite(row: dict[str, object], key: str) -> float | None:
    value = row.get(key)
    if value in {None, "", "None", "nan", "NaN"}:
        return None
    number = float(value)
    return number if np.isfinite(number) else None


def spectral_relation_rows(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    populations = {
        "all_network_sizes": rows,
        **{
            f"N{detector_n}": [row for row in rows if int(row["N"]) == detector_n]
            for detector_n in sorted({int(row["N"]) for row in rows})
        },
    }
    for population, subset in populations.items():
        for outcome in ROOT_OUTCOMES:
            group: list[dict[str, object]] = []
            for feature in SPECTRAL_FEATURES:
                pairs = [
                    (x, y)
                    for row in subset
                    if (x := _finite(row, feature)) is not None
                    and (y := _finite(row, outcome)) is not None
                ]
                if len(pairs) < 5:
                    continue
                x, y = (np.asarray(values) for values in zip(*pairs, strict=True))
                test = spearmanr(x, y)
                group.append(
                    {
                        "population": population,
                        "n": len(pairs),
                        "outcome": outcome,
                        "feature": feature,
                        "spearman_rho": float(test.statistic),
                        "p_value_descriptive": float(test.pvalue),
                        "dependence_warning": (
                            "pooled architecture/size correlations are descriptive; "
                            "only graph seeds within one architecture are independent"
                        ),
                    }
                )
            if group:
                adjusted = benjamini_hochberg(
                    [float(row["p_value_descriptive"]) for row in group]
                )
                for row, q_value in zip(group, adjusted, strict=True):
                    row["q_value_descriptive"] = q_value
                output.extend(group)
    return output


def disorder_statistics(
    rows: list[dict[str, object]],
    *,
    bootstrap_samples: int = 5000,
) -> list[dict[str, object]]:
    rng = np.random.default_rng(20260815)
    output: list[dict[str, object]] = []
    random_rows = [
        row
        for row in rows
        if row["architecture"] in RANDOM_GRAPH_ARCHITECTURES
    ]
    for architecture in sorted({str(row["architecture"]) for row in random_rows}):
        for detector_n in sorted({int(row["N"]) for row in random_rows}):
            group = [
                row
                for row in random_rows
                if row["architecture"] == architecture and int(row["N"]) == detector_n
            ]
            for metric in (*SPECTRAL_FEATURES, *ROOT_OUTCOMES):
                values = np.asarray(
                    [value for row in group if (value := _finite(row, metric)) is not None]
                )
                if values.size == 0:
                    continue
                boot = np.mean(
                    rng.choice(values, size=(bootstrap_samples, values.size), replace=True),
                    axis=1,
                )
                output.append(
                    {
                        "architecture": architecture,
                        "N": detector_n,
                        "metric": metric,
                        "independent_graph_realizations": len(group),
                        "finite_metric_values": values.size,
                        "mean": float(np.mean(values)),
                        "median": float(np.median(values)),
                        "standard_deviation": (
                            float(np.std(values, ddof=1)) if values.size > 1 else np.nan
                        ),
                        "q25": float(np.quantile(values, 0.25)),
                        "q75": float(np.quantile(values, 0.75)),
                        "bootstrap_mean_95_lower": float(np.quantile(boot, 0.025)),
                        "bootstrap_mean_95_upper": float(np.quantile(boot, 0.975)),
                        "uncertainty_status": (
                            "five-seed exploratory ensemble"
                            if len(group) == 5
                            else "incomplete seed ensemble"
                        ),
                    }
                )
    return output


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"no rows generated for {path.name}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    output = (
        args.output.resolve()
        if args.output is not None
        else run_root / "aggregated" / "spectral_relations"
    )
    output.mkdir(parents=True, exist_ok=True)
    collected = load_complete_results(run_root)
    selected = [row for row in collected if row["campaign"] in SPECTRAL_CAMPAIGNS]
    point_rows = [detector_spectral_features(row) for row in selected]
    relations = spectral_relation_rows(point_rows)
    uncertainty = disorder_statistics(point_rows)
    _write_csv(output / "detector_spectral_point_table.csv", point_rows)
    _write_csv(output / "detector_spectral_relations.csv", relations)
    _write_csv(output / "network_disorder_statistics.csv", uncertainty)
    summary = {
        "points": len(point_rows),
        "random_graph_points": sum(
            row["architecture"] in RANDOM_GRAPH_ARCHITECTURES for row in point_rows
        ),
        "ring_controls": sum(row["architecture"] == "ring" for row in point_rows),
        "sector_rule": (
            "largest four nonredundant exact graph-automorphism/Hamming-weight/"
            "half-filling-spin-reversal sectors per detector"
        ),
        "claim_status": "descriptive mechanism analysis; causality not inferred",
    }
    temporary = output / "summary.json.tmp"
    temporary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output / "summary.json")
    print(json.dumps({"output": str(output), **summary}, indent=2))


if __name__ == "__main__":
    main()
