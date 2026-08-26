"""Scientific and scheduler contracts for graph-connectivity campaigns."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from collapse.detector_graphs import detector_graph_metadata
from collapse.sobol_coupling_scan import generate_sobol_points
from collapse.zeus_sobol_array import build_scan_settings, resolve_array_spec
from examples.run_zeus_sobol_barabasi_albert_hz0_0 import SPEC as BA_SPEC
from examples.run_zeus_sobol_erdos_renyi_hz0_0 import SPEC as ER_SPEC
from examples.run_zeus_sobol_expander_hz0_0 import SPEC as EXPANDER_SPEC
from examples.run_zeus_sobol_watts_strogatz_hz0_0 import SPEC as WS_SPEC


ROOT = Path(__file__).resolve().parents[1]
SPECS = (ER_SPEC, WS_SPEC, BA_SPEC, EXPANDER_SPEC)


def _args(**overrides) -> Namespace:
    values = {
        "lower": 1.0e-3,
        "upper": 10.0,
        "kappa": 0.1,
        "evolution_time": 1.0e6,
        "bins": 64,
        "plot_grid": 720,
        "fit_harmonics": 32,
        "fit_tolerance": 1.0e-10,
        "max_bloch_points": 6000,
    }
    values.update(overrides)
    return Namespace(**values)


def test_network_campaign_defaults_are_400_N12_and_full_sector() -> None:
    assert {spec.connectivity for spec in SPECS} == {
        "erdos_renyi",
        "watts_strogatz",
        "barabasi_albert",
        "random_regular",
    }
    for spec in SPECS:
        assert spec.detector_n == 12
        assert spec.count == 400
        assert spec.batch_size == 100
        assert spec.batch_count == 4
        assert spec.graph_per_configuration
        assert spec.graph_require_connected


def test_runtime_size_and_shard_overrides_are_validated() -> None:
    resolved = resolve_array_spec(
        ER_SPEC,
        _args(detector_n=9, count=24, batch_size=6),
    )
    assert (resolved.detector_n, resolved.count, resolved.batch_size) == (9, 24, 6)
    assert resolved.batch_count == 4


def test_each_configuration_gets_a_reproducible_graph_realization() -> None:
    settings = build_scan_settings(WS_SPEC, _args())
    points, _ = generate_sobol_points(settings)
    first = settings.detector_graph_spec(points[0].sobol_index)
    second = settings.detector_graph_spec(points[1].sobol_index)

    assert first.seed != second.seed
    assert first == settings.detector_graph_spec(points[0].sobol_index)
    assert detector_graph_metadata(12, first)["connected"] is True
    assert all(
        point.jx <= settings.kappa * min(point.j, point.jpm, point.hz) + 1e-12
        for point in points
    )


def test_network_pbs_and_submit_wrappers_are_runtime_tweakable() -> None:
    stems = (
        "zeus_sobol_erdos_renyi_hz0_0",
        "zeus_sobol_watts_strogatz_hz0_0",
        "zeus_sobol_barabasi_albert_hz0_0",
        "zeus_sobol_expander_hz0_0",
    )
    common = (ROOT / "hpc" / "zeus_sobol_network_array_common.sh").read_text(
        encoding="utf-8"
    )
    assert '--detector-n "$DETECTOR_N"' in common
    assert '--count "$COUNT"' in common
    assert '--batch-size "$BATCH_SIZE"' in common
    assert "--graph-per-configuration" in common
    for stem in stems:
        pbs = (ROOT / "hpc" / f"{stem}_array.pbs").read_text(encoding="utf-8")
        submit = (ROOT / "hpc" / f"submit_{stem}.sh").read_text(encoding="utf-8")
        assert "#PBS -J 0-3" in pbs
        assert "mem=128gb" in pbs
        assert "walltime=72:00:00" in pbs
        assert 'DETECTOR_N="${DETECTOR_N:-12}"' in submit
        assert 'COUNT="${COUNT:-400}"' in submit
        assert 'qsub -J "0-$LAST"' in submit
