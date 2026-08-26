"""Validate, aggregate, and list missing Zeus classification points."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


RESULT_SCHEMA_VERSION = 2


def expected_case_dir(output_root: Path, row: dict[str, str]) -> Path:
    return (
        output_root
        / "raw"
        / row["campaign"]
        / f"point_{int(row['point_id']):04d}_N{int(row['detector_n'])}_t{float(row['time']):.12g}"
    )


def _parse_scan_value(value: str) -> float | str:
    """Preserve categorical scan values while normalizing numeric values."""

    try:
        return float(value)
    except ValueError:
        return value


def collect(manifest: Path, output_root: Path):
    with manifest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    complete_rows: list[dict[str, object]] = []
    missing_rows: list[dict[str, str]] = []
    corrupt_rows: list[dict[str, str]] = []
    for row in rows:
        case_dir = expected_case_dir(output_root, row)
        complete_path = case_dir / "COMPLETE.json"
        result_path = case_dir / "result.json"
        if not complete_path.is_file() or not result_path.is_file():
            missing_rows.append(row)
            continue
        try:
            completion = json.loads(complete_path.read_text(encoding="utf-8"))
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if int(completion["root_count"]) != 2 ** int(row["detector_n"]):
                raise ValueError("root-count mismatch")
            if int(result["schema_version"]) != RESULT_SCHEMA_VERSION:
                raise ValueError("result-schema mismatch")
            if int(result["N"]) != int(row["detector_n"]):
                raise ValueError("N mismatch")
        except (KeyError, ValueError, json.JSONDecodeError):
            corrupt_rows.append(row)
            continue
        complete_rows.append(
            {
                "point_id": int(row["point_id"]),
                "campaign": row["campaign"],
                "scan_parameter": row["scan_parameter"],
                "scan_value": _parse_scan_value(row["scan_value"]),
                "N": int(result["N"]),
                "dimension": int(result["dimension"]),
                "time": float(result["time"]),
                "parameters": json.dumps(result["parameters"], sort_keys=True),
                "seed": result["seed"],
                "root_count": result["root_count"],
                "qz_valid": result["qz_valid"],
                "maximum_qz_backward_residual": result["maximum_qz_backward_residual"],
                "maximum_qz_left_backward_residual": result["maximum_qz_left_backward_residual"],
                "coverage": result["coverage"],
                "density_ratio_cross_residual": result[
                    "density_ratio_cross_residual"
                ],
                "epsilon_antipodal": result["epsilon_antipodal"],
                "epsilon_B": result["epsilon_B"],
                "higher_harmonic_leakage": result["higher_harmonic_leakage"],
                "dipole_sharpness": result["dipole_sharpness"],
                "axis_fidelity": result["axis_fidelity"],
                "P1_over_Podd": result["P1_over_Podd"],
                "polar_S_born": result["polar_S_born"],
                "case_dir": str(case_dir),
                "status": "COMPLETE",
            }
        )
    return complete_rows, missing_rows, corrupt_rows


def _write_rows(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    aggregate_dir = output_root / "aggregated"
    aggregate_dir.mkdir(parents=True, exist_ok=True)
    complete, missing, corrupt = collect(args.manifest.resolve(), output_root)
    if complete:
        _write_rows(
            aggregate_dir / "classification_results.csv",
            complete,
            list(complete[0]),
        )
    manifest_fields = [
        "point_id",
        "campaign",
        "scan_parameter",
        "scan_value",
        "detector_n",
        "time",
        "parameters_json",
    ]
    _write_rows(aggregate_dir / "missing_manifest.csv", missing, manifest_fields)
    _write_rows(aggregate_dir / "corrupt_manifest.csv", corrupt, manifest_fields)
    summary = {
        "expected": len(complete) + len(missing) + len(corrupt),
        "complete": len(complete),
        "missing": len(missing),
        "corrupt": len(corrupt),
        "resubmit_required": bool(missing or corrupt),
    }
    (aggregate_dir / "collection_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
