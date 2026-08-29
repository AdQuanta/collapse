from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from core.anisotropic_sweep import AnisotropicSample
from core.relative_scale_campaign import (
    RelativeScaleCampaignService,
    RelativeScaleConfig,
    RelativeScaleRepository,
    smoke_config,
)


ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "configs" / "zeus_relative_scale_regimes_N13_N18.json"


class FakeBackend:
    def compute(self, case):
        theta = np.linspace(0.02, np.pi - 0.02, 256)
        radii = np.tan(theta / 2.0)
        phases = np.linspace(-np.pi, np.pi, theta.size, endpoint=False)
        return AnisotropicSample(
            eigenvalues=radii * np.exp(1j * phases),
            theta=theta,
            sector_count=1,
            diagonalization_seconds=0.01,
            analysis_seconds=0.02,
            worker_name="fake-regime-worker-2",
            worker_pid=456,
            calculation_started="2026-07-24T14:00:00+03:00",
            calculation_finished="2026-07-24T14:00:01+03:00",
        )


class FakePlotter:
    def plot(self, case, sample, diagnostic, path, max_bloch_points):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fake-png")
        return path


def test_config_covers_relative_regimes_and_requested_sizes() -> None:
    config = RelativeScaleConfig.from_json(CONFIG)
    assert config.detector_sizes == (13, 14, 15, 16, 17, 18)
    assert len(config.cases) == 30
    identifiers = {case.case_id for case in config.cases}
    assert {
        "p_h_gt_j_gt_p",
        "p_h_gt_p_gt_j",
        "p_j_gt_h_gt_p",
        "p_j_gt_p_gt_h",
        "p_p_gt_h_gt_j",
        "p_p_gt_j_gt_h",
        "p_h_eq_j_gt_p",
        "p_h_eq_p_gt_j",
        "p_j_eq_p_gt_h",
        "p_h_gt_j_eq_p",
        "p_j_gt_h_eq_p",
        "p_p_gt_h_eq_j",
        "p_all_equal",
        "only_h",
        "only_j",
        "only_p",
        "all_zero",
    } <= identifiers
    for case in config.cases:
        assert config.ratios(case)["maximum_Jx_ratio"] <= 0.1 + 1.0e-12
    positive = config.cases[:13]
    assert all(all(value > 0.0 for value in (abs(case.hz), case.J, case.Jpm)) for case in positive)

    def weak_order_signature(case):
        values = (abs(case.hz), case.J, case.Jpm)
        return tuple(
            tuple(index for index, value in enumerate(values) if value == level)
            for level in sorted(set(values), reverse=True)
        )

    assert len({weak_order_signature(case) for case in positive}) == 13
    for case in positive:
        levels = sorted({abs(case.hz), case.J, case.Jpm}, reverse=True)
        assert all(upper / lower >= 10.0 - 1.0e-12 for upper, lower in zip(levels, levels[1:]))
    one_zero = config.cases[13:22]
    assert len(one_zero) == 9
    assert all(sum(value == 0.0 for value in (abs(case.hz), case.J, case.Jpm)) == 1 for case in one_zero)
    for case in one_zero:
        levels = sorted(
            {value for value in (abs(case.hz), case.J, case.Jpm) if value > 0.0},
            reverse=True,
        )
        if len(levels) == 2:
            assert levels[0] / levels[1] >= 10.0 - 1.0e-12
    single_nonzero = config.cases[22:25]
    assert all(sum(value > 0.0 for value in (abs(case.hz), case.J, case.Jpm)) == 1 for case in single_nonzero)
    assert all(value == 0.0 for value in (abs(config.cases[25].hz), config.cases[25].J, config.cases[25].Jpm))


def test_service_saves_cases_and_both_aggregation_levels(tmp_path: Path) -> None:
    config = smoke_config(RelativeScaleConfig.from_json(CONFIG))
    repository = RelativeScaleRepository(tmp_path / "run")
    service = RelativeScaleCampaignService(
        repository,
        backend=FakeBackend(),
        plotter=FakePlotter(),
    )
    done_path = service.run_n(config, 4, workers=1)
    done = json.loads(done_path.read_text(encoding="utf-8"))
    assert done["completed_cases"] == 4
    assert "saved immediately" in done["checkpoint_contract"]
    assert Path(done["per_n_aggregate"]).is_file()
    assert Path(done["cross_n_aggregate"]).is_file()
    assert len(list((repository.root / "regime_metrics" / "N04").rglob("metrics.json"))) == 4
    assert len(list((repository.root / "figures" / "N04").rglob("blue_red.png"))) == 4
    assert (repository.root / "aggregates" / "N04" / "summary.json").is_file()
    assert (repository.root / "aggregates" / "all_N" / "summary.json").is_file()
    assert not repository.cross_n_lock().exists()
    assert not repository.status_path(4, "RUNNING.json").exists()


def test_pbs_and_runbook_match_zeus_requirements() -> None:
    pbs = (ROOT / "hpc" / "zeus_relative_scale_regimes_N13_N18.pbs").read_text(
        encoding="utf-8"
    )
    runbook = (ROOT / "hpc" / "zeus_relative_scale_regimes_N13_N18.md").read_text(
        encoding="utf-8"
    )
    for required in (
        "#PBS -q zeus_new_q",
        "#PBS -l select=1:ncpus=8:mem=128gb",
        "#PBS -J 13-18",
        "#PBS -m abe",
        "#PBS -M matanhaller@campus.technion.ac.il",
        "python3.11",
        "PARALLEL_AXIS=relative-scale-Hamiltonian-regime",
    ):
        assert required in pbs
    assert "VIRTUAL_ENV" not in pbs
    assert "/bin/activate" not in pbs
    assert "qsub" in runbook
    assert "No separate aggregation job is required" in runbook
    assert "heatmaps contain no cell numbers" in runbook
