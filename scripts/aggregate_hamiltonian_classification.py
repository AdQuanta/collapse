"""Build the common Hamiltonian-classification table from validated outputs.

The aggregator is intentionally conservative: unavailable quantities remain
empty/NaN and QZ validation is never inferred from an affine-root file.
Additional family adapters can be added as their modern analyses complete.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATCHED = (
    ROOT
    / "work"
    / "hamiltonian_classification_20260815"
    / "matched_ring_reproduction"
    / "scaling"
    / "matched_ring_full_sphere_scaling.csv"
)
DEFAULT_QND = (
    ROOT
    / "work"
    / "hamiltonian_classification_20260815"
    / "qnd_no_go_validation"
    / "qnd_size_validation.csv"
)
DEFAULT_OUTPUT = ROOT / "hamiltonian_classification_results.csv"


FIELDS = [
    "family",
    "N",
    "dimension",
    "time",
    "parameters",
    "seed",
    "root_count",
    "qz_valid",
    "qz_status",
    "coverage",
    "density_ratio_cross_residual",
    "epsilon_antipodal",
    "epsilon_B",
    "epsilon_B_definition",
    "higher_harmonic_leakage",
    "dipole_sharpness",
    "axis_fidelity",
    "P1_over_Podd",
    "composition_error",
    "composition_status",
    "harmonic_estimator",
    "polar_S_born",
    "source",
    "status",
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _matched_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in _read_csv(path):
        rows.append({key: source.get(key, "") for key in FIELDS})
        rows[-1]["source"] = source["source_npz"]
        rows[-1]["composition_error"] = 0.0
        rows[-1]["composition_status"] = (
            "PROVED ANALYTICALLY and VERIFIED NUMERICALLY for uncoupled "
            "tensor-factor spectators; other context refinements untested"
        )
    return rows


def _qnd_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in _read_csv(path):
        rows.append(
            {
                "family": source["family"],
                "N": source["detector_n"],
                "dimension": source["dimension"],
                "time": source["time"],
                "parameters": source["parameters"],
                "seed": 20260815,
                "root_count": source["root_count"],
                "qz_valid": True,
                "qz_status": (
                    "homogeneous_QZ_left_and_right_residuals; regularity and "
                    "representative_nullity audited"
                ),
                "coverage": source["equal_area_coverage"],
                "density_ratio_cross_residual": np.nan,
                "epsilon_antipodal": 0.0,
                "epsilon_B": np.nan,
                "epsilon_B_definition": "unavailable: pole-only support",
                "higher_harmonic_leakage": np.nan,
                "dipole_sharpness": np.nan,
                "axis_fidelity": np.nan,
                "P1_over_Podd": np.nan,
                "composition_error": 0.0,
                "composition_status": (
                    "PROVED ANALYTICALLY for uncoupled tensor-factor spectators; "
                    "not separately post-processed for this QND row"
                ),
                "harmonic_estimator": "unavailable: incomplete sphere",
                "polar_S_born": np.nan,
                "source": str(path.relative_to(ROOT)),
                "status": (
                    "PROVED ANALYTICALLY; VERIFIED NUMERICALLY; strict-QND "
                    "pole-degenerate no-go"
                ),
            }
        )
    return rows


def _additional_rows(paths: list[Path]) -> list[dict[str, object]]:
    """Load already-normalized adapters without inventing missing fields."""

    rows: list[dict[str, object]] = []
    for path in paths:
        for source in _read_csv(path):
            unknown = set(source) - set(FIELDS)
            if unknown:
                raise ValueError(f"unexpected columns in {path}: {sorted(unknown)}")
            rows.append({key: source.get(key, "") for key in FIELDS})
    return rows


def _zeus_rows(paths: list[Path]) -> list[dict[str, object]]:
    """Normalize outputs from the manifest collector to the common schema."""

    rows: list[dict[str, object]] = []
    for path in paths:
        for source in _read_csv(path):
            qz_valid = source["qz_valid"].strip().lower() == "true"
            rows.append(
                {
                    "family": source["campaign"],
                    "N": source["N"],
                    "dimension": source["dimension"],
                    "time": source["time"],
                    "parameters": source["parameters"],
                    "seed": source["seed"],
                    "root_count": source["root_count"],
                    "qz_valid": qz_valid,
                    "qz_status": (
                        "homogeneous QZ with saved left/right backward residuals"
                        if qz_valid
                        else "homogeneous QZ validation failed"
                    ),
                    "coverage": source["coverage"],
                    "density_ratio_cross_residual": source.get(
                        "density_ratio_cross_residual", np.nan
                    ),
                    "epsilon_antipodal": source["epsilon_antipodal"],
                    "epsilon_B": source["epsilon_B"],
                    "epsilon_B_definition": (
                        "total-root-density-weighted RMS of a-n.r"
                    ),
                    "higher_harmonic_leakage": source[
                        "higher_harmonic_leakage"
                    ],
                    "dipole_sharpness": source["dipole_sharpness"],
                    "axis_fidelity": source["axis_fidelity"],
                    "P1_over_Podd": source["P1_over_Podd"],
                    "composition_error": np.nan,
                    "composition_status": "not tested for this point",
                    "harmonic_estimator": "weighted_least_squares",
                    "polar_S_born": source["polar_S_born"],
                    "source": source["case_dir"],
                    "status": (
                        "VERIFIED NUMERICALLY; homogeneous-QZ audited"
                        if qz_valid
                        else "QZ VALIDATION FAILED"
                    ),
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matched", type=Path, default=DEFAULT_MATCHED)
    parser.add_argument("--qnd", type=Path, default=DEFAULT_QND)
    parser.add_argument(
        "--additional",
        type=Path,
        action="append",
        default=[],
        help="additional CSV already normalized to the common schema",
    )
    parser.add_argument(
        "--zeus-results",
        type=Path,
        action="append",
        default=[],
        help="classification_results.csv emitted by the manifest collector",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    matched = args.matched.resolve()
    qnd = args.qnd.resolve()
    if not matched.is_file() or not qnd.is_file():
        raise FileNotFoundError("run matched-ring and QND reproduction scripts first")
    additional = [path.resolve() for path in args.additional]
    missing_additional = [path for path in additional if not path.is_file()]
    if missing_additional:
        raise FileNotFoundError(f"missing additional tables: {missing_additional}")
    zeus_results = [path.resolve() for path in args.zeus_results]
    missing_zeus = [path for path in zeus_results if not path.is_file()]
    if missing_zeus:
        raise FileNotFoundError(f"missing Zeus result tables: {missing_zeus}")
    rows = (
        _matched_rows(matched)
        + _qnd_rows(qnd)
        + _additional_rows(additional)
        + _zeus_rows(zeus_results)
    )
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    print(
        json.dumps(
            {
                "output": str(output),
                "rows": len(rows),
                "families": sorted({str(row["family"]) for row in rows}),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
