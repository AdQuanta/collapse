"""Quantify parameter relations in the resolved nonzero-hz0 Sobol campaign.

The Sobol configurations are a deterministic space-filling design, not an
independent disorder ensemble. P-values and bootstrap intervals are therefore
reported only as descriptive sensitivity diagnostics, not sampling-theory
evidence for a population of Hamiltonians.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    ROOT / "work" / "hamiltonian_classification_20260815"
    / "sobol_ring_full_sphere" / "sobol_ring_classification_results.csv"
)
DEFAULT_OUTPUT = (
    ROOT / "work" / "hamiltonian_classification_20260815"
    / "sobol_ring_full_sphere" / "relations"
)
TARGET_FAMILY = "sobol_ring_hz0_0p1_matched_band"


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    """Return monotone Benjamini-Hochberg adjusted p-values."""

    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values)
    ranked = values[order]
    adjusted = ranked * values.size / np.arange(1, values.size + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    output = np.empty_like(adjusted)
    output[order] = np.clip(adjusted, 0.0, 1.0)
    return output.tolist()


def parameter_features(row: dict[str, str]) -> dict[str, float]:
    parameters = json.loads(row["parameters"])
    config = parameters["configuration"]
    j = float(config["j"])
    jpm = float(config["jpm"])
    jx = float(config["jx"])
    hz = float(config["hz"])
    hz0 = float(parameters["hz0"])
    return {
        "log10_J": float(np.log10(j)),
        "log10_Jpm": float(np.log10(jpm)),
        "log10_Jx_source": float(np.log10(jx)),
        "log10_J_over_Jx": float(np.log10(j / jx)),
        "log10_Jpm_over_J": float(np.log10(jpm / j)),
        "log10_Jpm_over_Jx": float(np.log10(jpm / jx)),
        "field_mismatch": hz0 - hz,
        "delta_source_signed": (hz0 - hz) / jx,
        "delta_source_absolute": abs(hz0 - hz) / jx,
        "weak_ratio": float(config["weak_ratio"]),
    }


def _bootstrap_spearman(
    x: np.ndarray,
    y: np.ndarray,
    *,
    seed: int,
    samples: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    estimates: list[float] = []
    for _ in range(samples):
        indices = rng.integers(0, x.size, size=x.size)
        estimate = float(spearmanr(x[indices], y[indices]).statistic)
        if np.isfinite(estimate):
            estimates.append(estimate)
    if not estimates:
        return np.nan, np.nan
    return tuple(np.quantile(estimates, [0.025, 0.975]).tolist())


def relation_rows(
    rows: list[dict[str, str]],
    *,
    bootstrap_samples: int = 1000,
    seed: int = 20260815,
) -> list[dict[str, object]]:
    records = [(row, parameter_features(row)) for row in rows]
    populations = {
        "all_400": records,
        "full_coverage_52": [
            item for item in records if float(item[0]["coverage"]) == 1.0
        ],
    }
    outcomes = {
        "all_400": {
            "coverage": lambda row: float(row["coverage"]),
            "full_coverage": lambda row: float(float(row["coverage"]) == 1.0),
            "polar_S_born": lambda row: float(row["polar_S_born"]),
        },
        "full_coverage_52": {
            "density_ratio_cross_residual": lambda row: float(
                row["density_ratio_cross_residual"]
            ),
            "higher_harmonic_leakage": lambda row: float(
                row["higher_harmonic_leakage"]
            ),
            "epsilon_B": lambda row: float(row["epsilon_B"]),
            "dipole_sharpness": lambda row: float(row["dipole_sharpness"]),
            "absolute_eta_minus_one": lambda row: abs(
                float(row["dipole_sharpness"]) - 1.0
            ),
            "P1_over_Podd": lambda row: float(row["P1_over_Podd"]),
            "polar_S_born": lambda row: float(row["polar_S_born"]),
        },
    }
    output: list[dict[str, object]] = []
    for population, items in populations.items():
        for outcome, getter in outcomes[population].items():
            group: list[dict[str, object]] = []
            y = np.array([getter(row) for row, _ in items], dtype=float)
            for feature in next(iter(items))[1]:
                x = np.array([features[feature] for _, features in items], dtype=float)
                test = spearmanr(x, y)
                lower, upper = _bootstrap_spearman(
                    x,
                    y,
                    seed=seed + len(output) + len(group),
                    samples=bootstrap_samples,
                )
                group.append(
                    {
                        "population": population,
                        "n": len(items),
                        "outcome": outcome,
                        "feature": feature,
                        "spearman_rho": float(test.statistic),
                        "p_value_descriptive": float(test.pvalue),
                        "bootstrap_95_lower_descriptive": lower,
                        "bootstrap_95_upper_descriptive": upper,
                        "design_note": (
                            "deterministic Sobol design; inferential quantities are "
                            "descriptive sensitivity diagnostics"
                        ),
                    }
                )
            q_values = benjamini_hochberg(
                [float(item["p_value_descriptive"]) for item in group]
            )
            for item, q_value in zip(group, q_values, strict=True):
                item["q_value_descriptive"] = q_value
            output.extend(group)
    return output


def _resolved_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    resolved = [row for row in rows if float(row["coverage"]) == 1.0]
    leakage_order = {
        row["source"]: rank
        for rank, row in enumerate(
            sorted(resolved, key=lambda item: float(item["higher_harmonic_leakage"])),
            start=1,
        )
    }
    born_order = {
        row["source"]: rank
        for rank, row in enumerate(
            sorted(resolved, key=lambda item: float(item["epsilon_B"])),
            start=1,
        )
    }
    ratio_order = {
        row["source"]: rank
        for rank, row in enumerate(
            sorted(
                resolved,
                key=lambda item: float(item["density_ratio_cross_residual"]),
            ),
            start=1,
        )
    }
    output: list[dict[str, object]] = []
    for row in resolved:
        features = parameter_features(row)
        output.append(
            {
                "source": row["source"],
                "rank_higher_harmonic_leakage": leakage_order[row["source"]],
                "rank_epsilon_B": born_order[row["source"]],
                "rank_density_ratio_cross_residual": ratio_order[row["source"]],
                "coverage": float(row["coverage"]),
                "density_ratio_cross_residual": float(
                    row["density_ratio_cross_residual"]
                ),
                "higher_harmonic_leakage": float(row["higher_harmonic_leakage"]),
                "P1_over_Podd": float(row["P1_over_Podd"]),
                "dipole_sharpness": float(row["dipole_sharpness"]),
                "axis_fidelity": float(row["axis_fidelity"]),
                "epsilon_B": float(row["epsilon_B"]),
                "polar_S_born": float(row["polar_S_born"]),
                **features,
            }
        )
    return sorted(output, key=lambda item: int(item["rank_higher_harmonic_leakage"]))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    args = parser.parse_args()
    if args.bootstrap_samples < 100:
        raise ValueError("bootstrap-samples must be at least 100")
    with args.input.resolve().open(newline="", encoding="utf-8") as handle:
        rows = [
            row for row in csv.DictReader(handle) if row["family"] == TARGET_FAMILY
        ]
    if len(rows) != 400:
        raise RuntimeError(f"expected 400 matched-band rows, found {len(rows)}")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    relations = relation_rows(rows, bootstrap_samples=args.bootstrap_samples)
    resolved = _resolved_rows(rows)
    _write_csv(output / "parameter_metric_relations.csv", relations)
    _write_csv(output / "resolved_configurations_ranked.csv", resolved)
    summary = {
        "family": TARGET_FAMILY,
        "configurations": len(rows),
        "full_coverage_configurations": len(resolved),
        "angular_grid": {"n_phi": 16, "n_mu": 8, "l_max": 7},
        "bootstrap_samples": args.bootstrap_samples,
        "selection_warning": (
            "resolved-subset relations are conditional on full angular coverage"
        ),
        "inference_warning": (
            "Sobol points are deterministic; p/q values and bootstrap intervals "
            "are descriptive, not disorder-ensemble uncertainty"
        ),
    }
    temporary = output / "summary.json.tmp"
    temporary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output / "summary.json")
    print(json.dumps({"output": str(output), **summary}, indent=2))


if __name__ == "__main__":
    main()
