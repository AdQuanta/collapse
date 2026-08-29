from __future__ import annotations

from core.sobol_coupling_scan import ScanSettings, generate_sobol_points
from scripts.run_zeus_sobol_hz0_0p1_N15 import (
    BATCH_SIZE,
    DETECTOR_N,
    HZ0,
    TOTAL_CONFIGURATIONS,
    _batch_bounds,
    parser,
)


def test_fixed_hz0_sampling_is_strict_and_perturbative() -> None:
    for name, nonzero in (("jy_zero", False), ("jy_nonzero", True)):
        settings = ScanSettings(
            name=name,
            jy_nonzero=nonzero,
            count=TOTAL_CONFIGURATIONS,
            sizes=(DETECTOR_N,),
            upper=10.0,
            hz0=HZ0,
        )
        points, coverage = generate_sobol_points(settings)
        assert len(points) == 400
        assert all(
            max(point.jx, point.jy)
            <= settings.kappa * min(point.j, point.jpm, point.hz, HZ0) + 1e-12
            for point in points
        )
        assert all(point.weak_ratio <= settings.kappa + 1e-12 for point in points)
        assert "abs(hz0)" in coverage["constraint"]


def test_hz0_array_batches_partition_all_configurations() -> None:
    bounds = [_batch_bounds(index) for index in range(4)]
    assert bounds == [(0, 100), (100, 200), (200, 300), (300, 400)]
    assert sum(stop - start for start, stop in bounds) == TOTAL_CONFIGURATIONS
    assert BATCH_SIZE == 100
    assert HZ0 == 0.1
    assert "--hz0" not in parser()._option_string_actions

