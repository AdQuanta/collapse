"""Completeness checks for Zeus classification collection."""

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "collect_hamiltonian_classification_results.py"
SPEC = importlib.util.spec_from_file_location("classification_collect", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_collect_separates_complete_and_missing(tmp_path) -> None:
    rows = [
        {
            "point_id": str(index),
            "campaign": "matched",
            "scan_parameter": "fixed",
            "scan_value": "0",
            "detector_n": "2",
            "time": "1",
            "parameters_json": "{}",
        }
        for index in range(2)
    ]
    manifest = tmp_path / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    case = MODULE.expected_case_dir(tmp_path, rows[0])
    case.mkdir(parents=True)
    (case / "COMPLETE.json").write_text(json.dumps({"root_count": 4}))
    (case / "result.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "N": 2,
                "dimension": 8,
                "time": 1,
                "parameters": {},
                "seed": 0,
                "root_count": 4,
                "qz_valid": True,
                "maximum_qz_backward_residual": 0,
                "maximum_qz_left_backward_residual": 0,
                "coverage": 1,
                "density_ratio_cross_residual": 0,
                "epsilon_antipodal": 0,
                "epsilon_B": 0,
                "higher_harmonic_leakage": 0,
                "dipole_sharpness": 1,
                "axis_fidelity": 1,
                "P1_over_Podd": 1,
                "polar_S_born": 1,
            }
        )
    )

    complete, missing, corrupt = MODULE.collect(manifest, tmp_path)

    assert len(complete) == 1
    assert len(missing) == 1
    assert not corrupt


def test_scan_value_parser_preserves_network_categories() -> None:
    assert MODULE._parse_scan_value("0.3") == 0.3
    assert MODULE._parse_scan_value("erdos_renyi") == "erdos_renyi"
