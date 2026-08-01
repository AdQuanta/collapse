from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from collapse.anisotropic_sweep import AnisotropicSample
from collapse.degeneracy_heavy_tail_campaign import (
    ActivationCertifier,
    CampaignConfig,
    CampaignRepository,
    DegeneracyHeavyTailCampaignService,
    IsingActivationCertifier,
    smoke_config,
)


ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "configs" / "zeus_degeneracy_heavy_tail_iff_N13_N18.json"


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
            worker_name="fake-worker-1",
            worker_pid=123,
            calculation_started="2026-07-24T09:00:00+03:00",
            calculation_finished="2026-07-24T09:00:01+03:00",
        )


class FakePlotter:
    def plot(self, case, sample, diagnostic, path, max_bloch_points):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fake-png")
        return path


def test_config_covers_requested_sizes_and_decisive_roles() -> None:
    config = CampaignConfig.from_json(CONFIG)
    assert config.detector_sizes == (13, 14, 15, 16, 17, 18)
    assert len(config.cases) == 11
    roles = {case.role for case in config.cases}
    assert "sufficiency_falsifier" in roles
    assert "necessity_falsifier" in roles
    assert any(case.Jpm == 0.0 for case in config.cases)
    assert any(case.Jpm != 0.0 for case in config.cases)
    for case in config.cases:
        assert config.perturbative_ratios(case)["maximum_ratio"] <= 0.1


def test_ising_activation_certificate_is_exact() -> None:
    config = CampaignConfig.from_json(CONFIG)
    cases = {case.case_id: case for case in config.cases}
    certifier = IsingActivationCertifier()

    flat = certifier.certify(
        cases["active_flat_atomic"],
        evolution_time=config.evolution_time,
        tolerance=config.degeneracy_tolerance,
    )
    assert flat.exact_active
    assert math.isclose(flat.exact_active_weight_fraction, 1.0)
    assert flat.minimum_coupled_gap == 0.0

    hz0 = certifier.certify(
        cases["active_hz0_resonance"],
        evolution_time=config.evolution_time,
        tolerance=config.degeneracy_tolerance,
    )
    assert hz0.exact_active
    assert math.isclose(hz0.exact_active_weight_fraction, 0.5)

    plus = certifier.certify(
        cases["active_plus_2J"],
        evolution_time=config.evolution_time,
        tolerance=config.degeneracy_tolerance,
    )
    assert plus.exact_active
    assert math.isclose(plus.exact_active_weight_fraction, 0.25)

    detuned = certifier.certify(
        cases["inactive_near_plus_2J"],
        evolution_time=config.evolution_time,
        tolerance=config.degeneracy_tolerance,
    )
    assert not detuned.exact_active
    assert detuned.exact_active_weight_fraction == 0.0
    assert math.isclose(detuned.minimum_coupled_gap, 0.02, abs_tol=1e-12)


def test_nonising_su2_activation_certificate_is_exact() -> None:
    config = CampaignConfig.from_json(CONFIG)
    cases = {case.case_id: case for case in config.cases}
    certifier = ActivationCertifier()
    active = certifier.certify(
        cases["nonising_su2_active_hz0"],
        evolution_time=config.evolution_time,
        tolerance=config.degeneracy_tolerance,
    )
    assert active.certificate_type == "su2_total_spin"
    assert active.exact_active
    assert active.exact_active_weight_fraction == 1.0
    inactive = certifier.certify(
        cases["nonising_su2_medium"],
        evolution_time=config.evolution_time,
        tolerance=config.degeneracy_tolerance,
    )
    assert not inactive.exact_active
    assert inactive.minimum_coupled_gap == 2.0


def test_service_checkpoints_every_case_and_aggregates_one_n(tmp_path: Path) -> None:
    config = smoke_config(CampaignConfig.from_json(CONFIG))
    repository = CampaignRepository(tmp_path / "run")
    service = DegeneracyHeavyTailCampaignService(
        repository,
        backend=FakeBackend(),
        plotter=FakePlotter(),
    )
    done = service.run_n(config, 4, workers=1)
    payload = json.loads(done.read_text(encoding="utf-8"))
    assert payload["completed_cases"] == 4
    assert "saved after every case" in payload["checkpoint_contract"]
    assert Path(payload["per_n_aggregate"]).is_file()
    assert Path(payload["cross_n_aggregate"]).is_file()
    assert len(list((repository.root / "campaign_metrics" / "N04").rglob("metrics.json"))) == 4
    assert len(list((repository.root / "figures" / "N04").rglob("blue_red.png"))) == 4
    assert (repository.root / "aggregates" / "N04" / "truth_table.json").is_file()
    assert (repository.root / "aggregates" / "all_N" / "summary.json").is_file()
    assert not repository.cross_n_aggregation_lock().exists()
    assert not repository.status_path(4, "RUNNING.json").exists()


def test_zeus_scripts_pin_requested_resources_and_array() -> None:
    simulation = (ROOT / "hpc" / "zeus_degeneracy_heavy_tail_iff_N13_N18.pbs").read_text(
        encoding="utf-8"
    )
    aggregate = (ROOT / "hpc" / "zeus_degeneracy_heavy_tail_iff_aggregate.pbs").read_text(
        encoding="utf-8"
    )
    runbook = (ROOT / "hpc" / "zeus_degeneracy_heavy_tail_iff_N13_N18.md").read_text(
        encoding="utf-8"
    )
    for text in (simulation, aggregate):
        assert "#PBS -q zeus_new_q" in text
        assert "#PBS -l select=1:ncpus=8:mem=128gb" in text
        assert "#PBS -m abe" in text
        assert "#PBS -M matanhaller@campus.technion.ac.il" in text
        assert "python3.11" in text
        assert "VIRTUAL_ENV" not in text
        assert "/bin/activate" not in text
    assert "#PBS -J 13-18" in simulation
    assert "CHECKPOINT_POLICY=save_each_case_then_per_N_plots_then_locked_cross_N_summary" in simulation
    assert "worker_name" not in simulation  # worker identity is emitted by Python
    assert "qsub" in runbook
    assert "No second `qsub` is required" in runbook
    assert "VIRTUAL_ENV" not in runbook
    assert "venv-zeus" not in runbook
    assert "hpc/zeus_degeneracy_heavy_tail_iff_N13_N18.pbs" in runbook
