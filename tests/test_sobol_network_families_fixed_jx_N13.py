"""Scientific and scheduler contracts for the fixed-Jx network scan."""

from __future__ import annotations

from argparse import Namespace
import logging
from pathlib import Path

import pytest

from core.sobol_coupling_scan import ScanSettings, generate_sobol_points
from core import zeus_sobol_array
from core.zeus_sobol_array import build_scan_settings
from scripts.run_zeus_sobol_network_families_fixed_jx_N13 import (
    BATCH_SIZE,
    CONFIGURATIONS_PER_FAMILY,
    DETECTOR_LOWER,
    DETECTOR_N,
    DETECTOR_UPPER,
    EVOLUTION_TIME,
    FIXED_JX_UNSCALED,
    MAX_WEAK_RATIO,
    SPECS,
)


ROOT = Path(__file__).resolve().parents[1]


def _args() -> Namespace:
    return Namespace(
        lower=DETECTOR_LOWER,
        upper=DETECTOR_UPPER,
        kappa=MAX_WEAK_RATIO,
        fixed_jx=FIXED_JX_UNSCALED,
        evolution_time=EVOLUTION_TIME,
        bins=64,
        plot_grid=720,
        fit_harmonics=32,
        fit_tolerance=1.0e-10,
        max_bloch_points=6000,
    )


def test_fixed_jx_scan_has_matched_three_dimensional_sobol_points() -> None:
    generated = []
    for spec in SPECS:
        settings = build_scan_settings(spec, _args())
        points, coverage = generate_sobol_points(settings)
        generated.append(points)

        assert settings.dimension == 3
        assert len(points) == CONFIGURATIONS_PER_FAMILY == 100
        assert all(len(point.unit) == 3 for point in points)
        assert all(point.jx == FIXED_JX_UNSCALED for point in points)
        assert all(point.jy == 0.0 for point in points)
        assert all(
            DETECTOR_LOWER <= scale <= DETECTOR_UPPER
            for point in points
            for scale in (point.j, point.jpm, point.hz)
        )
        assert all(
            point.jx
            <= MAX_WEAK_RATIO * min(point.j, point.jpm, point.hz) + 1.0e-12
            for point in points
        )
        assert all(point.weak_ratio <= MAX_WEAK_RATIO + 1.0e-12 for point in points)
        assert coverage["fixed_jx_unscaled"] == FIXED_JX_UNSCALED
        assert coverage["rejected_or_regenerated"] == 0
        assert [point.sobol_index for point in points] == list(range(100))

    reference = [
        (point.sobol_index, point.j, point.jpm, point.hz)
        for point in generated[0]
    ]
    for points in generated[1:]:
        assert [
            (point.sobol_index, point.j, point.jpm, point.hz)
            for point in points
        ] == reference


def test_fixed_jx_scan_family_and_array_contracts() -> None:
    assert DETECTOR_N == 13
    assert BATCH_SIZE == 25
    assert EVOLUTION_TIME == 1.0e6
    assert {spec.connectivity for spec in SPECS} == {
        "erdos_renyi",
        "watts_strogatz",
        "barabasi_albert",
        "random_regular",
    }
    assert all(spec.batch_count == 4 for spec in SPECS)
    assert all(spec.graph_per_configuration for spec in SPECS)
    assert len({spec.graph_seed for spec in SPECS}) == 4

    pbs = (
        ROOT / "hpc" / "zeus_sobol_network_families_fixed_jx_N13_array.pbs"
    ).read_text(encoding="utf-8")
    submit = (
        ROOT / "hpc" / "submit_zeus_sobol_network_families_fixed_jx_N13.sh"
    ).read_text(encoding="utf-8")
    assert "#PBS -J 0-15" in pbs
    assert "#PBS -q zeus_new_q" in pbs
    assert "mem=128gb" in pbs
    assert "walltime=72:00:00" in pbs
    assert "--fixed-jx 0.01" in pbs
    assert "--lower 1" in pbs
    assert "--upper 100" in pbs
    assert "--kappa 1e-2" in pbs
    assert "--evolution-time 1e6" in pbs
    assert 'WORKERS="${WORKERS:-1}"' in pbs
    assert "THREADS_PER_WORKER=$((8 / WORKERS))" in pbs
    assert 'qsub -J "0-$ARRAY_LAST"' in submit
    assert 'WORKERS="${WORKERS:-1}"' in submit
    assert logging.getLogger("matplotlib.font_manager").level == logging.ERROR


def test_single_worker_execution_does_not_require_a_process_pool(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payloads = [
        ({}, {"config_id": f"config_{index:03d}"}, 13, str(tmp_path / str(index)))
        for index in range(2)
    ]

    def fake_worker(payload):
        return {
            "config_id": payload[1]["config_id"],
            "N": 13,
            "status": "success",
            "runtime_seconds": 0.0,
        }

    monkeypatch.setattr(zeus_sobol_array, "_case_worker", fake_worker)
    results = list(zeus_sobol_array._run_inline(payloads, SPECS[0]))

    assert [result["config_id"] for result in results] == [
        "config_000",
        "config_001",
    ]
    output = capsys.readouterr().out
    assert "dispatch=1/2 config=config_000" in output
    assert "dispatch=2/2 config=config_001" in output


def test_impossible_fixed_jx_constraint_fails_before_sampling() -> None:
    settings = ScanSettings(
        name="jy_zero",
        jy_nonzero=False,
        count=1,
        sizes=(13,),
        lower=1.0,
        upper=10.0,
        kappa=0.01,
        fixed_jx=1.0,
    )
    with pytest.raises(ValueError, match="fixed_jx cannot satisfy"):
        settings.validate()
