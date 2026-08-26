from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from collapse.sobol_coupling_scan import generate_sobol_points
from examples.run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14 import (
    BATCH_SIZE,
    COUPLING_LOWER,
    DETECTOR_N,
    HZ0,
    HZ_LOWER,
    HZ_UPPER,
    KAPPA,
    TOTAL_CONFIGURATIONS,
    _batch_bounds,
    build_production_settings,
    parser,
)


ROOT = Path(__file__).resolve().parents[1]
PBS = (
    ROOT / "hpc"
    / "zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14_array.pbs"
)
SUBMIT = (
    ROOT / "hpc"
    / "submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14.sh"
)


def test_n14_campaign_is_strict_and_matches_n15_unscaled_points() -> None:
    settings_n14 = build_production_settings()
    settings_n15 = replace(settings_n14, sizes=(15,))
    points_n14, coverage = generate_sobol_points(settings_n14)
    points_n15, _ = generate_sobol_points(settings_n15)

    assert DETECTOR_N == 14
    assert len(points_n14) == TOTAL_CONFIGURATIONS == 100
    assert coverage["rejected_or_regenerated"] == 0
    assert coverage["coupling_lower"] == COUPLING_LOWER == 1.0e-5
    assert HZ_LOWER == 0.099 and HZ_UPPER == 0.101
    assert all(HZ_LOWER <= point.hz <= HZ_UPPER for point in points_n14)
    assert all(
        point.jx <= KAPPA * min(point.j, point.hz, HZ0) + 1.0e-15
        for point in points_n14
    )
    assert all(point.weak_ratio <= KAPPA + 1.0e-12 for point in points_n14)
    assert [
        (point.jx, point.jy, point.j, point.jpm, point.hz)
        for point in points_n14
    ] == [
        (point.jx, point.jy, point.j, point.jpm, point.hz)
        for point in points_n15
    ]


def test_n14_array_partition_resources_and_cli_are_exact() -> None:
    assert [_batch_bounds(index) for index in range(4)] == [
        (0, 25), (25, 50), (50, 75), (75, 100)
    ]
    assert BATCH_SIZE == 25
    options = parser()._option_string_actions
    assert "--batch-index" in options
    assert "--output-root" in options
    assert "--kappa" not in options
    assert "--coupling-lower" not in options

    pbs = PBS.read_text(encoding="utf-8")
    submit = SUBMIT.read_text(encoding="utf-8")
    assert "#PBS -J 0-3" in pbs
    assert "#PBS -l select=1:ncpus=8:mem=128gb" in pbs
    assert "two_order_N14.py" in pbs
    assert "--workers 2" in pbs
    assert "--resume" in pbs
    assert "activate" not in pbs.lower()
    assert "total=100" in submit
    assert "shard_size=25" in submit

