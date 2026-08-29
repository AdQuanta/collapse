"""
Tests for postprocessed Born-rule gate evaluation.
"""

import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from evaluate_born_postprocess_gate import GateThresholds, evaluate_gate  # noqa: E402


FIELDS = [
    "family",
    "model",
    "N",
    "t",
    "connectivity",
    "hz0_mode",
    "J",
    "Jx_unscaled",
    "Jy_unscaled",
    "Jpm",
    "Jxx",
    "Jyy",
    "Jz",
    "Jzx",
    "Jcpm_unscaled",
    "hx",
    "hz",
    "mean_born_similarity",
    "min_born_similarity",
    "range_born_similarity",
    "median_tail_density_exponent",
    "median_reciprocity_error",
    "max_radius_q99_over_q50",
    "min_radius_atomic_fraction",
]


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _row(n_value: int, *, control: bool = False, recip: float = 0.7) -> dict[str, object]:
    return {
        "family": "detuning_control_ring_N12_N13" if control else f"primary_matched_ring_N{n_value}",
        "model": "single_pixel",
        "N": n_value,
        "t": 3162,
        "connectivity": "ring",
        "hz0_mode": "zero" if control else "matched",
        "J": 1.0,
        "Jx_unscaled": 0.04,
        "Jy_unscaled": 0.0,
        "Jpm": 0.0,
        "Jxx": 0.0,
        "Jyy": 0.0,
        "Jz": 0.0,
        "Jzx": 0.0,
        "Jcpm_unscaled": 0.0,
        "hx": 0.0,
        "hz": 0.08,
        "mean_born_similarity": 0.67,
        "min_born_similarity": 0.61,
        "range_born_similarity": 0.11,
        "median_tail_density_exponent": 2.4,
        "median_reciprocity_error": recip,
        "max_radius_q99_over_q50": 11.0,
        "min_radius_atomic_fraction": 0.02,
    }


def _write_diagnostics(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "index.md").write_text(
        "# diagnostics\n\n| figure |\n|:---|\n| [plot](plot.png) |\n",
        encoding="utf-8",
    )
    (path / "run.log").write_text("ok\n", encoding="utf-8")


def _write_common_outputs(root: Path, control_recip: float = 1.4) -> None:
    _write_csv(
        root / "metric_stability_primary_N13_N14" / "stability_summary.csv",
        [_row(13), _row(14)],
    )
    (root / "metric_stability_primary_N13_N14" / "run.log").write_text("ok\n", encoding="utf-8")
    _write_csv(
        root / "metric_stability_off_resonance_controls_N12_N13" / "stability_summary.csv",
        [_row(12, control=True, recip=control_recip)],
    )
    (root / "metric_stability_off_resonance_controls_N12_N13" / "run.log").write_text(
        "ok\n", encoding="utf-8"
    )
    _write_diagnostics(root / "diagnostics_primary_N13_N14")
    _write_diagnostics(root / "diagnostics_off_resonance_controls")


def _write_n15_n16_outputs(root: Path, control_recip: float = 1.4) -> None:
    _write_csv(
        root / "metric_stability_primary_N15_N16" / "stability_summary.csv",
        [_row(15), _row(16)],
    )
    (root / "metric_stability_primary_N15_N16" / "run.log").write_text("ok\n", encoding="utf-8")
    _write_csv(
        root / "metric_stability_controls_N15_N16" / "stability_summary.csv",
        [_row(15, control=True, recip=control_recip)],
    )
    (root / "metric_stability_controls_N15_N16" / "run.log").write_text("ok\n", encoding="utf-8")
    _write_diagnostics(root / "diagnostics_primary_N15_N16")
    _write_diagnostics(root / "diagnostics_controls_N15_N16")


def test_missing_outputs_are_pending():
    with tempfile.TemporaryDirectory() as tmp:
        result = evaluate_gate(Path(tmp), [], GateThresholds())
    assert result["status"] == "pending_outputs"
    assert result["missing"]
    assert result["workflow"]["name"] == "n13_n14"


def test_primary_pair_without_control_challenge_is_ready_for_visual_review():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_common_outputs(root, control_recip=1.4)
        result = evaluate_gate(root, [], GateThresholds())
    assert result["status"] == "ready_for_visual_review"
    assert result["workflow"]["name"] == "n13_n14"
    assert result["primary_paired_passes"]
    assert not result["control_challenges"]


def test_n15_n16_workflow_is_auto_detected():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_n15_n16_outputs(root, control_recip=1.4)
        result = evaluate_gate(root, [], GateThresholds())
    assert result["status"] == "ready_for_visual_review"
    assert result["workflow"]["name"] == "n15_n16"
    assert result["primary_paired_passes"][0]["n_values"] == [15, 16]


def test_off_resonance_control_can_challenge_mechanism():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_common_outputs(root, control_recip=0.7)
        result = evaluate_gate(root, [], GateThresholds())
    assert result["status"] == "off_resonance_falsifier_challenge"
    assert result["control_challenges"]


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
