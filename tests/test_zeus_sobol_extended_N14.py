"""Scientific and scheduler contracts for the three new N=14 campaigns."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from core.sobol_coupling_scan import generate_sobol_points
from core.zeus_sobol_array import batch_bounds, build_scan_settings
from scripts.run_zeus_sobol_hz0_0_N14 import SPEC as HZ0_SPEC
from scripts.run_zeus_sobol_hz0_0p1_hz_0p0999_0p1001_N14 import (
    HZ_LOWER,
    HZ_UPPER,
    SPEC as NEAR_HZ_SPEC,
)
from scripts.run_zeus_sobol_second_neighbor_hz0_0_N14 import SPEC as SECOND_SPEC


ROOT = Path(__file__).resolve().parents[1]


def _args() -> Namespace:
    return Namespace(
        lower=1.0e-3,
        upper=10.0,
        kappa=0.1,
        evolution_time=1.0e6,
        bins=64,
        plot_grid=720,
        fit_harmonics=32,
        fit_tolerance=1.0e-10,
        max_bloch_points=6000,
    )


def test_all_campaigns_partition_exactly_400_N14_configurations() -> None:
    for spec in (HZ0_SPEC, NEAR_HZ_SPEC, SECOND_SPEC):
        assert spec.detector_n == 14
        assert spec.count == 400
        assert spec.batch_size == 100
        assert [batch_bounds(spec, index) for index in range(4)] == [
            (0, 100),
            (100, 200),
            (200, 300),
            (300, 400),
        ]


def test_fixed_hz0_and_very_near_hz_sampling_contracts() -> None:
    hz0_settings = build_scan_settings(HZ0_SPEC, _args())
    near_settings = build_scan_settings(NEAR_HZ_SPEC, _args())
    hz0_points, _ = generate_sobol_points(hz0_settings)
    near_points, _ = generate_sobol_points(near_settings)

    assert hz0_settings.hz0 == 0.0
    assert all(point.jy == 0.0 and point.j2 == point.jpm2 == 0.0 for point in hz0_points)
    assert all(
        point.jx <= 0.1 * min(point.j, point.jpm, point.hz) + 1.0e-12
        for point in hz0_points
    )
    assert near_settings.hz0 == 0.1
    assert (HZ_LOWER, HZ_UPPER) == (0.0999, 0.1001)
    assert all(HZ_LOWER <= point.hz <= HZ_UPPER for point in near_points)
    assert all(
        point.jx <= 0.1 * min(point.j, point.jpm, point.hz, 0.1) + 1.0e-12
        for point in near_points
    )


def test_second_neighbor_sampling_includes_all_detector_scales_in_constraint() -> None:
    settings = build_scan_settings(SECOND_SPEC, _args())
    points, coverage = generate_sobol_points(settings)

    assert settings.dimension == 6
    assert len(points) == 400
    assert len({(p.j, p.hz, p.jpm, p.jx, p.j2, p.jpm2) for p in points}) == 400
    assert all(
        settings.lower <= value <= settings.upper
        for point in points
        for value in (point.j, point.hz, point.jpm, point.jx, point.j2, point.jpm2)
    )
    assert all(
        point.jx
        <= settings.kappa * min(point.j, point.hz, point.jpm, point.j2, point.jpm2)
        + 1.0e-12
        for point in points
    )
    assert all(point.weak_ratio <= settings.kappa + 1.0e-12 for point in points)
    assert "J2,Jpm2" in coverage["constraint"]


def test_pbs_scripts_use_four_shards_and_established_N14_resources() -> None:
    stems = (
        "zeus_sobol_hz0_0_N14",
        "zeus_sobol_hz0_0p1_hz_0p0999_0p1001_N14",
        "zeus_sobol_second_neighbor_hz0_0_N14",
    )
    for stem in stems:
        pbs = (ROOT / "hpc" / f"{stem}_array.pbs").read_text(encoding="utf-8")
        submit = (ROOT / "hpc" / f"submit_{stem}.sh").read_text(encoding="utf-8")
        assert "#PBS -J 0-3" in pbs
        assert "#PBS -l select=1:ncpus=8:mem=128gb" in pbs
        assert "#PBS -l walltime=72:00:00" in pbs
        assert "--kappa 0.1" in pbs
        assert "--workers 2" in pbs
        assert "--resume" in pbs
        assert "total=400" in submit
        assert "shard_size=100" in submit
