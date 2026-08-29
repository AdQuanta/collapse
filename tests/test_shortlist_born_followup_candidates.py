"""
Tests for Born follow-up shortlist ordering.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from shortlist_born_followup_candidates import (  # noqa: E402
    _negative_control_counts,
    _off_resonance_controls,
)


def _off_row(score: float, similarity: float, reciprocity: float, label: str) -> dict:
    return {
        "family": "detuning_control_ring_N12_N13",
        "model": "single_pixel",
        "connectivity": "ring",
        "hz0_mode": "zero",
        "N": 13,
        "J": 1.0,
        "Jx_unscaled": 0.05,
        "Jy_unscaled": 0.0,
        "Jcpm_unscaled": 0.0,
        "hx": 0.0,
        "hz": 0.1,
        "Jpm": 0.1,
        "Jxx": 0.0,
        "Jyy": 0.0,
        "Jz": 0.0,
        "Jzx": 0.0,
        "t": 3162.0,
        "perturbative_like": True,
        "target_like": True,
        "control_like": True,
        "local_resonance_label": "off",
        "local_resonance_distance": 0.1,
        "perturbative_balanced_score": score,
        "born_similarity": similarity,
        "tail_density_exponent": 2.5,
        "reciprocity_error": reciprocity,
        "radius_atomic_fraction": 0.02,
        "radius_q99_over_q50": 12.0,
        "label": label,
    }


def test_off_resonance_shortlist_prioritizes_scalar_gate_passes():
    high_score_bad_reciprocity = _off_row(0.70, 0.75, 1.4, "bad_recip")
    lower_score_gate_pass = _off_row(0.60, 0.68, 0.6, "gate_pass")

    selected = _off_resonance_controls([high_score_bad_reciprocity, lower_score_gate_pass])

    assert [row["label"] for row in selected] == ["gate_pass", "bad_recip"]


def test_negative_control_table_accepts_current_and_legacy_chain_names():
    rows = [
        {
            "family": "chain_transverse_perturbative_N13_N14",
            "N": 14,
            "target_like": True,
        },
        {
            "family": "chain_transverse_perturbative_N15",
            "N": 15,
            "target_like": False,
        },
    ]

    table = "\n".join(_negative_control_counts(rows))

    assert "chain_transverse_perturbative_N13_N14 | 14 | 1 | 1" in table
    assert "chain_transverse_perturbative_N15 | 15 | 0 | 1" in table


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
