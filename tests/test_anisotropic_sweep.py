from __future__ import annotations

import json
import math
import multiprocessing
from pathlib import Path
import time

import matplotlib.image as mpimg
import numpy as np

from core.anisotropic_sweep import (
    AngularDiagnosticCalculator,
    AnisotropicCase,
    AnisotropicRepository,
    AnisotropicSample,
    AnisotropicSweepConfig,
    AnisotropicSweepService,
    BlueRedDiagnosticPlotter,
    BornHeatmapAggregator,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.json"


class FakeBackend:
    def __init__(self) -> None:
        self.calls = 0

    def compute(self, case):
        self.calls += 1
        eigenvalues = np.array([0.0, 0.25 + 0.5j, -0.75 + 0.2j, 2.0 - 0.5j])
        return AnisotropicSample(
            eigenvalues=eigenvalues,
            theta=2.0 * np.arctan(np.abs(eigenvalues)),
            sector_count=case.detector_n,
            diagonalization_seconds=0.01,
            analysis_seconds=0.02,
        )


class FakePlotter:
    def __init__(self) -> None:
        self.calls = 0

    def plot(self, case, sample, diagnostic, path, max_bloch_points):
        self.calls += 1
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"figure")
        return path


class MultiprocessFakeBackend:
    def compute(self, case):
        started = time.time()
        time.sleep(0.08)
        eigenvalues = np.array([0.0, 0.25 + 0.5j, -0.75 + 0.2j, 2.0 - 0.5j])
        return AnisotropicSample(
            eigenvalues=eigenvalues,
            theta=2.0 * np.arctan(np.abs(eigenvalues)),
            sector_count=case.detector_n,
            diagonalization_seconds=time.time() - started,
            analysis_seconds=0.0,
            worker_name=multiprocessing.current_process().name,
            worker_pid=multiprocessing.current_process().pid or 0,
            calculation_started="2026-07-18T12:00:00+03:00",
            calculation_finished="2026-07-18T12:00:01+03:00",
        )


def tiny_config(*, j_values=(0.0,)) -> AnisotropicSweepConfig:
    return AnisotropicSweepConfig(
        detector_sizes=(4,),
        hz_values=(0.0,),
        j_values=tuple(j_values),
        jpm_values=(0.0, 0.5),
        evolution_time=100.0,
        jx=0.01,
        hz0=0.0,
        bins=16,
        max_bloch_points=64,
    )


def test_production_config_maps_all_704_array_tasks() -> None:
    config = AnisotropicSweepConfig.from_json(CONFIG_PATH)
    assert config.task_count == 704
    assert config.total_case_count == 7040
    assert config.task_for_index(1).detector_n == 11
    assert config.task_for_index(88).detector_n == 11
    assert config.task_for_index(89).detector_n == 12
    last = config.task_for_index(704)
    assert (last.detector_n, last.hz, last.j) == (18, 2.01, 2.0)
    assert math.isclose(config.jx / math.sqrt(18), 0.01 / math.sqrt(18))


def test_diagnostic_histograms_normalize_and_exclude_nonfinite_values() -> None:
    eigenvalues = np.array([0.0, 0.5 + 0.25j, 2.0j, np.nan + 0j])
    sample = AnisotropicSample(
        eigenvalues=eigenvalues,
        theta=2.0 * np.arctan(np.abs(eigenvalues)),
        sector_count=1,
        diagonalization_seconds=0.0,
        analysis_seconds=0.0,
    )
    diagnostic = AngularDiagnosticCalculator(20).calculate(sample)
    assert diagnostic.finite_eigenvalues == 3
    assert diagnostic.excluded_eigenvalues == 1
    assert diagnostic.p_theta_integral == 1.0
    assert diagnostic.p_reflected_integral == 1.0
    assert np.all((diagnostic.centers >= 0.0) & (diagnostic.centers <= np.pi))


def test_task_checkpoints_each_configuration_and_resumes(tmp_path: Path) -> None:
    config = tiny_config()
    repository = AnisotropicRepository(tmp_path)
    backend = FakeBackend()
    plotter = FakePlotter()
    service = AnisotropicSweepService(repository, backend, plotter)
    task = config.task_for_index(1)

    done_path = service.run_task(config, task)
    assert done_path.is_file()
    done = json.loads(done_path.read_text(encoding="utf-8"))
    assert len(done["completed"]) == 2
    assert backend.calls == 2
    assert plotter.calls == 2
    assert not repository.row_status_path(task, "RUNNING.json").exists()
    for item in done["completed"]:
        assert Path(item["raw"]).is_file()
        assert Path(item["metrics"]).is_file()
        assert Path(item["figure"]).is_file()

    service.run_task(config, task)
    assert backend.calls == 2
    assert plotter.calls == 2


def test_task_resume_repairs_metadata_without_recomputing(tmp_path: Path) -> None:
    config = tiny_config()
    repository = AnisotropicRepository(tmp_path)
    backend = FakeBackend()
    service = AnisotropicSweepService(repository, backend, FakePlotter())
    task = config.task_for_index(1)
    service.run_task(config, task)

    case = AnisotropicCase(
        detector_n=task.detector_n,
        hz=task.hz,
        j=task.j,
        jpm=config.jpm_values[0],
        evolution_time=config.evolution_time,
        jx=config.jx,
        hz0=config.hz0,
        seed=config.seed,
    )
    repository.metadata_path(case).unlink()
    assert not repository.metadata_path(case).exists()

    service.run_task(config, task)

    assert backend.calls == 2
    assert repository.metadata_path(case).is_file()


def test_real_blue_red_plot_and_complete_heatmap(tmp_path: Path) -> None:
    config = tiny_config(j_values=(0.0, 0.5))
    repository = AnisotropicRepository(tmp_path)
    backend = FakeBackend()
    service = AnisotropicSweepService(repository, backend, BlueRedDiagnosticPlotter())
    for index in range(1, config.task_count + 1):
        service.run_task(config, config.task_for_index(index))

    manifest_path = BornHeatmapAggregator(repository).aggregate_n(config, 4)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["complete"] is True
    assert manifest["completed_cases"] == 4
    assert len(manifest["heatmaps"]) == 1
    heatmap = Path(manifest["heatmaps"][0])
    assert heatmap.is_file()
    assert mpimg.imread(heatmap).shape[0] > 500
    first_figure = next((tmp_path / "figures").rglob("blue_red_*.png"))
    image = mpimg.imread(first_figure)
    assert image.shape[0] > image.shape[1]


def test_run_n_parallelizes_distinct_j_jpm_configurations(tmp_path: Path) -> None:
    config = tiny_config(j_values=(0.0, 0.5))
    repository = AnisotropicRepository(tmp_path)
    service = AnisotropicSweepService(repository, MultiprocessFakeBackend(), FakePlotter())
    done_path = service.run_n(config, 4, workers=2)
    done = json.loads(done_path.read_text(encoding="utf-8"))
    assert done["workers"] == 2
    assert done["completed_cases"] == 4
    assert {(item["J"], item["Jpm"]) for item in done["completed"]} == {
        (0.0, 0.0),
        (0.0, 0.5),
        (0.5, 0.0),
        (0.5, 0.5),
    }
    assert len({item["worker_pid"] for item in done["completed"]}) == 2
    assert all(item["calculation_started"] for item in done["completed"])
    assert all(item["calculation_finished"] for item in done["completed"])


def test_zeus_scripts_have_required_scheduler_contract() -> None:
    simulation = (ROOT / "hpc" / "zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.pbs").read_text(encoding="utf-8")
    aggregation = (ROOT / "hpc" / "zeus_single_pixel_anisotropic_j_jpm_hz_t1e6_aggregate.pbs").read_text(encoding="utf-8")
    for script in (simulation, aggregation):
        assert "#PBS -q zeus_new_q" in script
        assert "#PBS -l select=1:ncpus=8:mem=128gb" in script
        assert "#PBS -m abe" in script
        assert "#PBS -M matanhaller@campus.technion.ac.il" in script
        assert "python3.11" in script
        assert "quspin-extensions\":\"0.1.6" in script
        assert "LOG_ROOT" in script
    assert "#PBS -J 11-18" in simulation
    assert "simulate-N" in simulation
    assert "CONFIG_WORKERS" in simulation
    assert "#PBS -J 11-18" in aggregation
    assert "AGGREGATE_ARGS=(aggregate --N" in aggregation
