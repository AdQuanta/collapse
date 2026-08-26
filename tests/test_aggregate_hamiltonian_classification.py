"""Schema checks for the common Hamiltonian-classification table."""

import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "aggregate_hamiltonian_classification.py"
)
SPEC = importlib.util.spec_from_file_location("classification_aggregate", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_required_columns_are_present() -> None:
    required = {
        "family",
        "N",
        "dimension",
        "time",
        "parameters",
        "seed",
        "root_count",
        "qz_valid",
        "coverage",
        "density_ratio_cross_residual",
        "epsilon_antipodal",
        "epsilon_B",
        "higher_harmonic_leakage",
        "dipole_sharpness",
        "axis_fidelity",
        "P1_over_Podd",
        "composition_error",
        "status",
    }

    assert required <= set(MODULE.FIELDS)


def test_additional_rows_are_normalized_to_common_schema(tmp_path: Path) -> None:
    path = tmp_path / "additional.csv"
    path.write_text("family,N\nnetwork_test,6\n", encoding="utf-8")

    rows = MODULE._additional_rows([path])

    assert rows[0]["family"] == "network_test"
    assert rows[0]["N"] == "6"
    assert set(rows[0]) == set(MODULE.FIELDS)


def test_zeus_rows_preserve_qz_status(tmp_path: Path) -> None:
    path = tmp_path / "zeus.csv"
    fields = {
        "campaign": "haar_unitary_null",
        "N": "3",
        "dimension": "16",
        "time": "0",
        "parameters": "{}",
        "seed": "7",
        "root_count": "8",
        "qz_valid": "True",
        "coverage": "1",
        "epsilon_antipodal": "0",
        "epsilon_B": "0.6",
        "higher_harmonic_leakage": "0.9",
        "dipole_sharpness": "0.1",
        "axis_fidelity": "0.2",
        "P1_over_Podd": "0.1",
        "polar_S_born": "0",
        "case_dir": "raw/haar/point",
    }
    import csv

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerow(fields)

    rows = MODULE._zeus_rows([path])

    assert rows[0]["family"] == "haar_unitary_null"
    assert rows[0]["qz_valid"] is True
    assert set(rows[0]) == set(MODULE.FIELDS)
