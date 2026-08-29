"""
Tests for the CSV-only perturbative resonance audit.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from audit_born_followup_resonance import _json_safe, classify_row, csv_gate_pass, resonance_check  # noqa: E402
from summarize_born_search_results import local_resonance_distance, local_resonance_label  # noqa: E402


def _row(hz0_mode: str, hz: float = 0.1, **overrides):
    row = {
        "family": "detuning_control_ring_N12_N13",
        "model": "single_pixel",
        "connectivity": "ring",
        "hz0_mode": hz0_mode,
        "hz": hz,
        "J": 1.0,
        "Jx_unscaled": 0.05,
        "Jcpm_unscaled": 0.0,
        "hx": 0.0,
        "perturbative_like": True,
        "control_like": True,
        "target_like": True,
        "born_similarity": 0.7,
        "tail_density_exponent": 2.4,
        "reciprocity_error": 0.7,
        "radius_atomic_fraction": 0.02,
        "radius_q99_over_q50": 12.0,
    }
    row.update(overrides)
    row["local_resonance_distance"] = local_resonance_distance(row)
    row["local_resonance_label"] = local_resonance_label(row)
    return row


def test_resonance_distance_distinguishes_matched_minus_and_zero():
    matched = _row("matched")
    minus = _row("minus")
    zero = _row("zero")

    assert math.isclose(matched["local_resonance_distance"], 0.0)
    assert math.isclose(minus["local_resonance_distance"], 0.0)
    assert math.isclose(zero["local_resonance_distance"], 0.1)
    assert matched["local_resonance_label"] == "exact"
    assert minus["local_resonance_label"] == "exact"
    assert zero["local_resonance_label"] == "off"


def test_audit_buckets_true_zero_falsifier_separately_from_resonance_adjacent():
    zero = _row("zero")
    minus = _row("minus")
    primary = _row("matched", family="primary_matched_ring_N13", control_like=False)

    assert classify_row(zero) == "off_resonance_zero_falsifier"
    assert classify_row(minus) == "resonance_adjacent_control"
    assert classify_row(primary) == "primary_matched_ring_evidence"
    assert csv_gate_pass(zero)


def test_resonance_check_reports_recorded_distance_mismatch():
    row = _row("matched")
    row["local_resonance_distance"] = 0.2
    row["local_resonance_label"] = "off"
    check = resonance_check([row], tolerance=1.0e-9)

    assert check["checked_ring_rows"] == 1
    assert check["mismatch_count"] == 1
    assert check["mismatches"][0]["expected_label"] == "exact"


def test_json_safe_replaces_nonfinite_numbers():
    assert _json_safe({"x": float("nan"), "items": [1.0, float("inf")]}) == {
        "x": None,
        "items": [1.0, None],
    }


if __name__ == "__main__":
    tests = [value for key, value in sorted(globals().items()) if key.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        name = test.__name__
        try:
            test()
            print(f"  PASS  {name}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {name}: {exc}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
