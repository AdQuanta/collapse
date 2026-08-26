from __future__ import annotations

from pathlib import Path

from collapse.sobol_coupling_scan import ScanSettings, generate_sobol_points
from examples.run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_N15 import (
    BATCH_SIZE,
    FIXED_JPM,
    FIXED_JY,
    HZ0,
    HZ_LOWER,
    HZ_UPPER,
    TOTAL_CONFIGURATIONS,
    _batch_bounds,
    parser,
)


ROOT = Path(__file__).resolve().parents[1]


def test_very_near_two_order_sampling_contract() -> None:
    settings = ScanSettings(
        name="jy_zero",
        jy_nonzero=False,
        seed=20260806,
        count=TOTAL_CONFIGURATIONS,
        sizes=(15,),
        lower=1.0e-3,
        upper=10.0,
        kappa=0.01,
        coupling_lower=1.0e-5,
        hz0=HZ0,
        fixed_jpm=FIXED_JPM,
        hz_lower=HZ_LOWER,
        hz_upper=HZ_UPPER,
    )
    points, coverage = generate_sobol_points(settings)

    assert HZ_LOWER == 0.0999 and HZ_UPPER == 0.1001
    assert len(points) == 100
    assert coverage["coupling_lower"] == 1.0e-5
    assert all(HZ_LOWER <= point.hz <= HZ_UPPER for point in points)
    assert all(point.jpm == 0.0 and point.jy == FIXED_JY for point in points)
    assert all(point.jx >= 1.0e-5 for point in points)
    assert all(
        point.jx <= 0.01 * min(point.j, point.hz, HZ0) + 1.0e-15
        for point in points
    )
    assert all(point.weak_ratio <= 0.01 + 1.0e-12 for point in points)


def test_very_near_two_order_array_files_and_resources() -> None:
    assert [_batch_bounds(index) for index in range(4)] == [
        (0, 25), (25, 50), (50, 75), (75, 100)
    ]
    assert BATCH_SIZE == 25
    assert "--coupling-lower" in parser()._option_string_actions

    for n in (14, 15):
        stem = (
            "zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_"
            f"two_order_N{n}"
        )
        pbs = (ROOT / "hpc" / f"{stem}_array.pbs").read_text(encoding="utf-8")
        submit = (ROOT / "hpc" / f"submit_{stem}.sh").read_text(encoding="utf-8")
        assert "#PBS -J 0-3" in pbs
        assert "#PBS -l select=1:ncpus=8:mem=128gb" in pbs
        assert "hz_range=[0.0999,0.1001]" in pbs
        assert "--kappa 0.01" in pbs
        assert "--coupling-lower 1e-5" in pbs
        assert "--workers 2" in pbs
        assert "--resume" in pbs
        assert "activate" not in pbs.lower()
        assert "total=100" in submit
        assert "shard_size=25" in submit
