"""Small strict-QND validation smoke tests."""

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_qnd_no_go_validation.py"
SPEC = importlib.util.spec_from_file_location("qnd_no_go", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_small_qnd_case_is_block_diagonal_and_pole_only() -> None:
    row = MODULE.evaluate_size(detector_n=2, time=0.7)

    assert row["commutator_relative_frobenius"] == 0.0
    assert row["off_diagonal_block_relative_frobenius"] == 0.0
    assert row["maximum_production_theta"] == 0.0
    assert row["production_north_pole_max_distance"] == 0.0
    assert row["forward_outcome_1_south_pole_max_distance"] == 0.0
    assert row["representative_root_nullity"] == 4
    assert row["equal_area_coverage"] < 1.0
    assert row["full_sphere_harmonics_available"] is False

