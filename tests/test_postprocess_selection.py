"""
Tests for queued post-processing candidate selection.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "examples"))

from born_candidate_stability import select_rows  # noqa: E402


def _row(family: str, n_value: int, hz: float, score: float) -> dict:
    return {
        "family": family,
        "model": "single_pixel",
        "connectivity": "ring",
        "hz0_mode": "matched",
        "J": 1.0,
        "Jx_unscaled": 0.04,
        "Jy_unscaled": 0.0,
        "Jcpm_unscaled": 0.0,
        "hx": 0.0,
        "hz": hz,
        "Jpm": 0.0,
        "Jxx": 0.0,
        "Jyy": 0.0,
        "Jz": 0.0,
        "Jzx": 0.0,
        "t": 3162.0,
        "N": n_value,
        "born_similarity": 0.7,
        "radius_atomic_fraction": 0.01,
        "control_like": False,
        "target_like": True,
        "shortlist_group_score": score,
    }


def test_queue_selection_keeps_primary_families_and_requested_ns():
    rows = [
        _row("primary_matched_ring_N13", 13, 0.08, 0.9),
        _row("primary_matched_ring_N14", 14, 0.08, 0.9),
        _row("detuning_control_ring_N12_N13", 13, 0.08, 1.0),
        _row("primary_matched_ring_N13", 13, 0.12, 0.8),
        _row("primary_matched_ring_N14", 14, 0.12, 0.8),
    ]

    args = argparse.Namespace(
        queue_csv=[Path(__file__).with_name("postprocess_queue_fixture.csv")],
        top_groups=1,
        min_n=13,
        max_n=14,
        family=["primary_matched_ring_N13", "primary_matched_ring_N14"],
        mode="primary",
        max_jx_unscaled=0.05,
        max_jy_unscaled=0.05,
        max_jcpm_unscaled=0.05,
        max_hx=0.05,
        min_born_similarity=0.35,
        max_atomic_fraction=0.25,
        top_rows=8,
    )

    selected = select_rows(rows, args)

    assert [row["N"] for row in selected] == [13, 14]
    assert {row["family"] for row in selected} == {
        "primary_matched_ring_N13",
        "primary_matched_ring_N14",
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
