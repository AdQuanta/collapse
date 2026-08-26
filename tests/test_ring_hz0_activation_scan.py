"""Contracts for the N=17 Born-like-ring central-field scan."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from collapse.activation_resolved_projective import RingActivationParameters
from examples.run_three_ring_activation_resolved import _apply_parameter_overrides
from examples.summarize_ring_hz0_activation_scan import collect_scan_rows


ROOT = Path(__file__).resolve().parents[1]


def test_scan_grid_is_ordered_exact_and_resolves_hz_resonance() -> None:
    config = json.loads(
        (ROOT / "configs/ring_born_like_hz0_scan_N17.json").read_text()
    )
    assert config["detector_n"] == 17
    assert len(config["cases"]) == 20
    hz = float(config["source_hz"])
    ratios = [float(case["hz0_over_hz"]) for case in config["cases"]]
    assert ratios == sorted(ratios)
    assert ratios[0] == 0.0
    assert ratios[-1] == 2.0
    assert {0.99999, 1.0, 1.00001}.issubset(ratios)
    for case, ratio in zip(config["cases"], ratios, strict=True):
        hz0 = float(case["parameter_overrides"]["hz0"])
        assert math.isclose(hz0, ratio * hz, rel_tol=2.0e-16, abs_tol=1.0e-18)


def test_second_neighbor_wd_scan_uses_same_exact_relative_grid() -> None:
    original = json.loads(
        (ROOT / "configs/ring_born_like_hz0_scan_N17.json").read_text()
    )
    config = json.loads(
        (ROOT / "configs/ring_second_neighbor_wd_hz0_scan_N17.json").read_text()
    )
    assert config["detector_n"] == 17
    assert len(config["cases"]) == 20
    ratios = [float(case["hz0_over_hz"]) for case in config["cases"]]
    assert ratios == [float(case["hz0_over_hz"]) for case in original["cases"]]
    hz = float(config["source_hz"])
    for case, ratio in zip(config["cases"], ratios, strict=True):
        assert "source_03/rank_001/N17" in case["source_result"]
        hz0 = float(case["parameter_overrides"]["hz0"])
        assert math.isclose(hz0, ratio * hz, rel_tol=2.0e-16, abs_tol=1.0e-18)


def test_parameter_overrides_are_explicit_and_reject_unknown_names() -> None:
    source = RingActivationParameters(
        hz=0.2,
        hz0=0.0,
        j=0.3,
        jpm=0.1,
        jx_unscaled=0.01,
        evolution_time=1.0e6,
    )
    result, overrides = _apply_parameter_overrides(
        source, {"parameter_overrides": {"hz0": 0.19}}
    )
    assert result.hz0 == 0.19
    assert result.hz == source.hz
    assert overrides == {"hz0": 0.19}
    with pytest.raises(ValueError, match="unknown parameter"):
        _apply_parameter_overrides(
            source, {"parameter_overrides": {"hz_0": 0.19}}
        )


def test_summary_collector_validates_and_orders_completed_cases(tmp_path: Path) -> None:
    labels = ("global", "weak", "intermediate", "strong")
    cases = [
        {
            "case_id": "high",
            "hz0_over_hz": 1.0,
            "parameter_overrides": {"hz0": 0.2},
        },
        {
            "case_id": "low",
            "hz0_over_hz": 0.0,
            "parameter_overrides": {"hz0": 0.0},
        },
    ]
    config = {"detector_n": 4, "source_hz": 0.2, "cases": cases}
    for case in cases:
        case_dir = tmp_path / case["case_id"]
        case_dir.mkdir()
        (case_dir / "COMPLETE.json").write_text(
            json.dumps({"status": "complete"}), encoding="utf-8"
        )
        diagnostics = [
            {
                "label": label,
                "S_born": 0.1 + index,
                "born_RMSE_occupied": 0.2 + index,
                "effective_root_count": 16.0 - index,
            }
            for index, label in enumerate(labels)
        ]
        (case_dir / "activation_resolved_metrics.json").write_text(
            json.dumps(
                {
                    "detector_n": 4,
                    "parameters": {
                        "hz": 0.2,
                        "hz0": case["parameter_overrides"]["hz0"],
                    },
                    "diagnostics": diagnostics,
                }
            ),
            encoding="utf-8",
        )
    rows, missing = collect_scan_rows(config, tmp_path, allow_partial=False)
    assert missing == []
    assert [row["case_id"] for row in rows] == ["low", "high"]
    assert rows[1]["strong_S_born"] == 3.1


def test_zeus_scan_array_shape_resources_and_race_free_status_files() -> None:
    pbs = (
        ROOT / "hpc/zeus_ring_born_like_hz0_scan_N17_array.pbs"
    ).read_text()
    submit = (
        ROOT / "hpc/submit_zeus_ring_born_like_hz0_scan_N17.sh"
    ).read_text()
    runner = (
        ROOT / "examples/run_three_ring_activation_resolved.py"
    ).read_text()
    assert "#PBS -J 0-19" in pbs
    assert "#PBS -q zeus_new_q" in pbs
    assert "mem=256gb" in pbs
    assert "walltime=120:00:00" in pbs
    assert "--case-index \"$ARRAY_INDEX\"" in pbs
    assert "effective_scan_config.json" in submit
    assert 'ARRAY_RANGE="${ARRAY_RANGE:-0-19}"' in submit
    assert 'qsub -J "$ARRAY_RANGE"' in submit
    assert 'record_suffix = "" if args.all else' in runner


def test_second_neighbor_wd_zeus_scan_resources() -> None:
    pbs = (
        ROOT / "hpc/zeus_ring_second_neighbor_wd_hz0_scan_N17_array.pbs"
    ).read_text()
    submit = (
        ROOT / "hpc/submit_zeus_ring_second_neighbor_wd_hz0_scan_N17.sh"
    ).read_text()
    assert "#PBS -J 0-19" in pbs
    assert "#PBS -q zeus_new_q" in pbs
    assert "mem=256gb" in pbs
    assert "walltime=120:00:00" in pbs
    assert "second_neighbor=true" in pbs
    assert 'ARRAY_RANGE="${ARRAY_RANGE:-0-19}"' in submit
    assert 'qsub -J "$ARRAY_RANGE"' in submit
    assert "effective_scan_config.json" in submit
