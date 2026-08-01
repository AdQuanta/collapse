from __future__ import annotations

from collapse.sobol_coupling_scan import ScanSettings, generate_sobol_points
from examples.run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p05_0p5_N15 import (
    BATCH_SIZE,
    DETECTOR_N,
    FIXED_JPM,
    FIXED_JY,
    HZ0,
    HZ_LOWER,
    HZ_UPPER,
    TOTAL_CONFIGURATIONS,
    _batch_bounds,
    parser,
)


def test_fixed_jpm_zero_hz_band_sampling_is_strict_and_perturbative() -> None:
    settings = ScanSettings(
        name="jy_zero",
        jy_nonzero=False,
        count=TOTAL_CONFIGURATIONS,
        sizes=(DETECTOR_N,),
        upper=10.0,
        hz0=HZ0,
        fixed_jpm=FIXED_JPM,
        hz_lower=HZ_LOWER,
        hz_upper=HZ_UPPER,
    )
    points, _ = generate_sobol_points(settings)
    assert settings.dimension == 3
    assert len(points) == 100
    assert all(point.jpm == 0.0 and point.jy == FIXED_JY for point in points)
    assert all(len(point.unit) == 3 for point in points)
    assert all(HZ_LOWER <= point.hz <= HZ_UPPER for point in points)
    assert min(point.hz for point in points) < 0.06
    assert max(point.hz for point in points) > 0.4
    assert all(
        point.jx <= settings.kappa * min(point.j, point.hz, HZ0) + 1e-12
        for point in points
    )
    assert all(point.weak_ratio <= settings.kappa + 1e-12 for point in points)


def test_fixed_jpm_zero_hz_band_array_batches_partition_all_configurations() -> None:
    assert [_batch_bounds(index) for index in range(4)] == [
        (0, 25), (25, 50), (50, 75), (75, 100)
    ]
    assert BATCH_SIZE == 25
    assert TOTAL_CONFIGURATIONS == 100
    assert HZ0 == 0.1
    assert HZ_LOWER == 0.05
    assert HZ_UPPER == 0.5
    assert FIXED_JPM == 0.0
    assert FIXED_JY == 0.0
    options = parser()._option_string_actions
    assert "--hz0" not in options
    assert "--jpm" not in options
    assert "--jy" not in options
    assert "--hz-lower" not in options
    assert "--hz-upper" not in options

