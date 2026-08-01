r"""Checkpointed anisotropic single-pixel sweeps and blue/red diagnostics.

The production Hamiltonian is the clean periodic single-pixel model

.. math::

   H = h_z \sum_i Z_i + J \sum_i Z_i Z_{i+1}
       + J_{\pm}\sum_i(\sigma_i^+\sigma_{i+1}^- + \mathrm{h.c.})
       + \frac{J_x}{\sqrt N}X_0\sum_i X_i,

with ``hz0=0`` and collective ``Jx=0.01`` in the supplied Zeus campaign.
The module keeps configuration, simulation, persistence, diagnostics, plotting,
and aggregation behind separate interfaces so the orchestration can be tested
without invoking QuSpin.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
from datetime import datetime
import csv
import gc
import hashlib
import importlib.metadata
import json
import math
import multiprocessing
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any, Protocol, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collapse.analysis import DisentanglementAnalyzer
from collapse.born import born_ratio_from_radii
from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin


BLUE = "#1677b8"
RED = "#df2b2f"
RATIO = "#6a3d7a"


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def _value_tag(value: float) -> str:
    text = f"{float(value):+.8g}"
    return text.replace("+", "p").replace("-", "m").replace(".", "p")


def _time_tag(value: float) -> str:
    return f"{float(value):.8g}".replace("+", "p").replace("-", "m").replace(".", "p")


def _package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("quspin", "quspin-extensions", "numpy", "scipy", "matplotlib"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


def _timestamp() -> str:
    """Return a timezone-aware local timestamp suitable for Zeus logs."""

    return datetime.now().astimezone().isoformat(timespec="seconds")


def recommended_worker_count(detector_n: int) -> int:
    """Memory-aware process count for independent configurations."""

    if detector_n <= 13:
        return 4
    if detector_n <= 15:
        return 2
    return 1


@dataclass(frozen=True)
class AnisotropicSweepConfig:
    """Immutable production-grid configuration."""

    detector_sizes: tuple[int, ...]
    hz_values: tuple[float, ...]
    j_values: tuple[float, ...]
    jpm_values: tuple[float, ...]
    evolution_time: float = 1.0e6
    jx: float = 0.01
    hz0: float = 0.0
    bins: int = 48
    max_bloch_points: int = 6000
    seed: int = 44
    connectivity: str = "ring"
    central_coupling: str = "all"

    def __post_init__(self) -> None:
        if not self.detector_sizes or any(value < 3 for value in self.detector_sizes):
            raise ValueError("detector_sizes must contain values >= 3")
        if len(set(self.detector_sizes)) != len(self.detector_sizes):
            raise ValueError("detector_sizes contains duplicates")
        for name, values in (
            ("hz_values", self.hz_values),
            ("j_values", self.j_values),
            ("jpm_values", self.jpm_values),
        ):
            if not values or not all(math.isfinite(value) for value in values):
                raise ValueError(f"{name} must contain finite values")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} contains duplicates")
        if self.evolution_time <= 0.0 or not math.isfinite(self.evolution_time):
            raise ValueError("evolution_time must be finite and positive")
        if self.jx <= 0.0 or not math.isfinite(self.jx):
            raise ValueError("jx must be finite and positive")
        if self.bins < 4:
            raise ValueError("bins must be at least 4")
        if self.connectivity != "ring" or self.central_coupling != "all":
            raise ValueError("the production sector path requires ring/all geometry")

    @classmethod
    def from_json(cls, path: Path) -> "AnisotropicSweepConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            detector_sizes=tuple(int(value) for value in payload["detector_sizes"]),
            hz_values=tuple(float(value) for value in payload["hz_values"]),
            j_values=tuple(float(value) for value in payload["j_values"]),
            jpm_values=tuple(float(value) for value in payload["jpm_values"]),
            evolution_time=float(payload.get("evolution_time", 1.0e6)),
            jx=float(payload.get("jx", 0.01)),
            hz0=float(payload.get("hz0", 0.0)),
            bins=int(payload.get("bins", 48)),
            max_bloch_points=int(payload.get("max_bloch_points", 6000)),
            seed=int(payload.get("seed", 44)),
            connectivity=str(payload.get("connectivity", "ring")),
            central_coupling=str(payload.get("central_coupling", "all")),
        )

    @property
    def task_count(self) -> int:
        return len(self.detector_sizes) * len(self.hz_values) * len(self.j_values)

    @property
    def cases_per_task(self) -> int:
        return len(self.jpm_values)

    @property
    def total_case_count(self) -> int:
        return self.task_count * self.cases_per_task

    @property
    def digest(self) -> str:
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]

    def task_for_index(self, one_based_index: int) -> "SweepRowTask":
        if one_based_index < 1 or one_based_index > self.task_count:
            raise ValueError(f"task index must be in 1..{self.task_count}")
        zero = one_based_index - 1
        per_size = len(self.hz_values) * len(self.j_values)
        size_index, remainder = divmod(zero, per_size)
        hz_index, j_index = divmod(remainder, len(self.j_values))
        return SweepRowTask(
            task_index=one_based_index,
            detector_n=self.detector_sizes[size_index],
            hz=self.hz_values[hz_index],
            j=self.j_values[j_index],
        )


def smoke_config(config: AnisotropicSweepConfig) -> AnisotropicSweepConfig:
    """Return a deliberately tiny, clearly separate end-to-end smoke grid."""

    return replace(
        config,
        detector_sizes=(4,),
        hz_values=(0.0,),
        j_values=(0.0, 0.5),
        jpm_values=(0.0, 0.5),
        evolution_time=100.0,
        bins=24,
        max_bloch_points=256,
    )


@dataclass(frozen=True)
class SweepRowTask:
    """One PBS-array unit: fixed ``N``, ``hz``, and ``J``; sweep ``Jpm``."""

    task_index: int
    detector_n: int
    hz: float
    j: float


@dataclass(frozen=True)
class AnisotropicCase:
    detector_n: int
    hz: float
    j: float
    jpm: float
    evolution_time: float
    jx: float
    hz0: float
    seed: int = 44

    @property
    def edge_jx(self) -> float:
        return self.jx / math.sqrt(self.detector_n)


@dataclass(frozen=True)
class AnisotropicSample:
    eigenvalues: np.ndarray
    theta: np.ndarray
    sector_count: int
    diagonalization_seconds: float
    analysis_seconds: float
    worker_name: str = "unknown"
    worker_pid: int = 0
    calculation_started: str = ""
    calculation_finished: str = ""


@dataclass(frozen=True)
class AngularDiagnostics:
    edges: np.ndarray
    centers: np.ndarray
    p_theta: np.ndarray
    p_reflected: np.ndarray
    ratio: np.ndarray
    occupied: np.ndarray
    born_curve: np.ndarray
    born_score: float
    born_rmse: float
    coverage: float
    phi_harmonic_2: float
    finite_eigenvalues: int
    excluded_eigenvalues: int
    p_theta_integral: float
    p_reflected_integral: float


class CaseBackend(Protocol):
    def compute(self, case: AnisotropicCase) -> AnisotropicSample:
        ...


class DiagnosticPlotter(Protocol):
    def plot(
        self,
        case: AnisotropicCase,
        sample: AnisotropicSample,
        diagnostic: AngularDiagnostics,
        path: Path,
        max_bloch_points: int,
    ) -> Path:
        ...


class QuSpinAnisotropicBackend:
    """QuSpin implementation using the clean-ring pixel-shift sectors."""

    def compute(self, case: AnisotropicCase) -> AnisotropicSample:
        process = multiprocessing.current_process()
        worker_name = process.name
        worker_pid = os.getpid()
        calculation_started = _timestamp()
        print(
            f"[{calculation_started}] worker={worker_name} pid={worker_pid} event=START "
            f"N={case.detector_n} hz={case.hz:+g} J={case.j:g} Jpm={case.jpm:g} "
            f"Jx_edge={case.edge_jx:.8g} t={case.evolution_time:.0e}",
            flush=True,
        )
        hamiltonian = SinglePixelHamiltonianQuSpin(
            N_pixel=case.detector_n,
            J=case.j,
            Jpm=case.jpm,
            Jx=case.edge_jx,
            Jy=0.0,
            Jz=0.0,
            Jzx=0.0,
            hx=0.0,
            hz=case.hz,
            hx0=0.0,
            hz0=case.hz0,
            connectivity="ring",
            central_coupling="all",
            seed=case.seed,
            use_symmetry=True,
        )
        started = time.perf_counter()
        sectors = hamiltonian.diagonalize_sectors()
        diagonalization_seconds = time.perf_counter() - started
        started = time.perf_counter()
        analyzer = DisentanglementAnalyzer.from_sectors(
            sectors,
            case.evolution_time,
            case.detector_n + 1,
        )
        eigenvalues = np.asarray(analyzer.D0, dtype=np.complex128)
        analysis_seconds = time.perf_counter() - started
        theta = 2.0 * np.arctan(np.abs(eigenvalues))
        calculation_finished = _timestamp()
        sample = AnisotropicSample(
            eigenvalues=eigenvalues,
            theta=theta,
            sector_count=len(sectors),
            diagonalization_seconds=diagonalization_seconds,
            analysis_seconds=analysis_seconds,
            worker_name=worker_name,
            worker_pid=worker_pid,
            calculation_started=calculation_started,
            calculation_finished=calculation_finished,
        )
        print(
            f"[{calculation_finished}] worker={worker_name} pid={worker_pid} event=FINISH "
            f"N={case.detector_n} hz={case.hz:+g} J={case.j:g} Jpm={case.jpm:g} "
            f"diag_s={diagonalization_seconds:.6f} analysis_s={analysis_seconds:.6f}",
            flush=True,
        )
        del analyzer, sectors, hamiltonian
        gc.collect()
        return sample


class AnisotropicRepository:
    """Deterministic, atomic filesystem persistence for independent tasks."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def case_relative_dir(self, case: AnisotropicCase) -> Path:
        return (
            Path(f"N{case.detector_n:02d}")
            / f"hz_{_value_tag(case.hz)}"
            / f"J_{_value_tag(case.j)}"
            / f"Jpm_{_value_tag(case.jpm)}"
        )

    def raw_path(self, case: AnisotropicCase) -> Path:
        return self.root / "raw" / self.case_relative_dir(case) / f"spectrum_t{_time_tag(case.evolution_time)}.npz"

    def metadata_path(self, case: AnisotropicCase) -> Path:
        return self.root / "raw" / self.case_relative_dir(case) / "metadata.json"

    def metrics_path(self, case: AnisotropicCase) -> Path:
        return self.root / "metrics" / self.case_relative_dir(case) / "diagnostics.json"

    def figure_path(self, case: AnisotropicCase) -> Path:
        return self.root / "figures" / self.case_relative_dir(case) / f"blue_red_t{_time_tag(case.evolution_time)}.png"

    def row_status_path(self, task: SweepRowTask, name: str) -> Path:
        return (
            self.root
            / "status"
            / f"N{task.detector_n:02d}"
            / f"hz_{_value_tag(task.hz)}"
            / f"J_{_value_tag(task.j)}"
            / name
        )

    def n_status_path(self, detector_n: int, name: str) -> Path:
        return self.root / "status" / f"N{detector_n:02d}" / name

    def has_sample(self, case: AnisotropicCase) -> bool:
        return self.raw_path(case).is_file()

    def save_sample(self, case: AnisotropicCase, sample: AnisotropicSample) -> Path:
        path = self.raw_path(case)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.stem + ".tmp.npz")
        np.savez_compressed(
            temporary,
            eigenvalues=sample.eigenvalues,
            theta=sample.theta,
            detector_n=case.detector_n,
            total_qubits=case.detector_n + 1,
            hz=case.hz,
            hz0=case.hz0,
            J=case.j,
            Jpm=case.jpm,
            Jx=case.jx,
            Jx_edge=case.edge_jx,
            t=case.evolution_time,
            sector_count=sample.sector_count,
            diagonalization_seconds=sample.diagonalization_seconds,
            analysis_seconds=sample.analysis_seconds,
            worker_name=sample.worker_name,
            worker_pid=sample.worker_pid,
            calculation_started=sample.calculation_started,
            calculation_finished=sample.calculation_finished,
        )
        temporary.replace(path)
        return path

    def load_sample(self, case: AnisotropicCase) -> AnisotropicSample:
        with np.load(self.raw_path(case)) as raw:
            files = set(raw.files)
            return AnisotropicSample(
                eigenvalues=np.asarray(raw["eigenvalues"], dtype=np.complex128),
                theta=np.asarray(raw["theta"], dtype=float),
                sector_count=int(raw["sector_count"]),
                diagonalization_seconds=float(raw["diagonalization_seconds"]),
                analysis_seconds=float(raw["analysis_seconds"]),
                worker_name=str(raw["worker_name"]) if "worker_name" in files else "legacy",
                worker_pid=int(raw["worker_pid"]) if "worker_pid" in files else 0,
                calculation_started=str(raw["calculation_started"]) if "calculation_started" in files else "",
                calculation_finished=str(raw["calculation_finished"]) if "calculation_finished" in files else "",
            )

    def save_metadata(self, case: AnisotropicCase, sample: AnisotropicSample, config_digest: str) -> Path:
        path = self.metadata_path(case)
        payload = {
            "case": asdict(case),
            "collective_coupling": case.jx,
            "edge_coupling": case.edge_jx,
            "edge_coupling_formula": "Jx/sqrt(N)",
            "hamiltonian_sign_convention": "repository overall-minus convention; theta and R are invariant",
            "symmetry": "cyclic pixel-shift sectors",
            "sector_count": sample.sector_count,
            "diagonalization_seconds": sample.diagonalization_seconds,
            "analysis_seconds": sample.analysis_seconds,
            "worker_name": sample.worker_name,
            "worker_pid": sample.worker_pid,
            "calculation_started": sample.calculation_started,
            "calculation_finished": sample.calculation_finished,
            "config_digest": config_digest,
            "runtime": {
                "python": sys.version,
                "platform": platform.platform(),
                "packages": _package_versions(),
            },
            "completed_unix_time": time.time(),
        }
        _atomic_json(path, payload)
        return path

    def save_metrics(self, case: AnisotropicCase, diagnostic: AngularDiagnostics) -> Path:
        path = self.metrics_path(case)
        payload = {
            "case": asdict(case),
            "Jx_edge": case.edge_jx,
            "S_born": diagnostic.born_score,
            "born_rmse": diagnostic.born_rmse,
            "angular_bin_coverage": diagnostic.coverage,
            "phi_harmonic_2": diagnostic.phi_harmonic_2,
            "finite_eigenvalues": diagnostic.finite_eigenvalues,
            "excluded_eigenvalues": diagnostic.excluded_eigenvalues,
            "p_theta_integral": diagnostic.p_theta_integral,
            "p_reflected_integral": diagnostic.p_reflected_integral,
        }
        _atomic_json(path, payload)
        return path

    def load_metrics(self, case: AnisotropicCase) -> dict[str, Any]:
        return json.loads(self.metrics_path(case).read_text(encoding="utf-8"))


class AngularDiagnosticCalculator:
    """Calculate the canonical reflected Born diagnostic from one spectrum."""

    def __init__(self, bins: int):
        if bins < 4:
            raise ValueError("bins must be at least 4")
        self.edges = np.linspace(0.0, np.pi, bins + 1)

    def calculate(self, sample: AnisotropicSample) -> AngularDiagnostics:
        eigenvalues = np.asarray(sample.eigenvalues, dtype=np.complex128)
        finite = np.isfinite(eigenvalues.real) & np.isfinite(eigenvalues.imag)
        values = eigenvalues[finite]
        theta = 2.0 * np.arctan(np.abs(values))
        centers = 0.5 * (self.edges[:-1] + self.edges[1:])
        counts_theta, _ = np.histogram(theta, bins=self.edges)
        counts_reflected, _ = np.histogram(np.pi - theta, bins=self.edges)
        widths = np.diff(self.edges)
        norm = max(theta.size, 1)
        p_theta = counts_theta / norm / widths
        p_reflected = counts_reflected / norm / widths
        denominator = counts_theta + counts_reflected
        ratio = np.divide(
            counts_theta,
            denominator,
            out=np.full(counts_theta.shape, np.nan, dtype=float),
            where=denominator > 0,
        )
        occupied = np.isfinite(ratio)
        born_curve = np.cos(centers / 2.0) ** 2
        radii = np.abs(values)
        born_score = float(born_ratio_from_radii(radii, n_theta=100).similarity) if radii.size else float("nan")
        born_rmse = (
            float(np.sqrt(np.mean((ratio[occupied] - born_curve[occupied]) ** 2)))
            if np.any(occupied)
            else float("nan")
        )
        nonzero = np.abs(values) > 1.0e-12
        phi_harmonic_2 = (
            float(abs(np.mean(np.exp(2j * np.angle(values[nonzero])))))
            if np.any(nonzero)
            else float("nan")
        )
        return AngularDiagnostics(
            edges=self.edges,
            centers=centers,
            p_theta=p_theta,
            p_reflected=p_reflected,
            ratio=ratio,
            occupied=occupied,
            born_curve=born_curve,
            born_score=born_score,
            born_rmse=born_rmse,
            coverage=float(np.mean(occupied)),
            phi_harmonic_2=phi_harmonic_2,
            finite_eigenvalues=int(values.size),
            excluded_eigenvalues=int(eigenvalues.size - values.size),
            p_theta_integral=float(np.sum(p_theta * widths)),
            p_reflected_integral=float(np.sum(p_reflected * widths)),
        )


def _bloch_branches(eigenvalues: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(eigenvalues, dtype=np.complex128)
    finite = np.isfinite(values.real) & np.isfinite(values.imag)
    values = values[finite]
    radius_squared = np.abs(values) ** 2
    denominator = 1.0 + radius_squared
    branch = np.column_stack(
        [
            2.0 * values.real / denominator,
            2.0 * values.imag / denominator,
            (1.0 - radius_squared) / denominator,
        ]
    )
    return branch, -branch


def _wire_sphere(axis: Any) -> None:
    azimuth = np.linspace(0.0, 2.0 * np.pi, 44)
    polar = np.linspace(0.0, np.pi, 22)
    x = np.outer(np.cos(azimuth), np.sin(polar))
    y = np.outer(np.sin(azimuth), np.sin(polar))
    z = np.outer(np.ones_like(azimuth), np.cos(polar))
    axis.plot_wireframe(x, y, z, color="#8b8b8b", linewidth=0.32, alpha=0.24)


class BlueRedDiagnosticPlotter:
    """Render the requested three-row blue/red diagnostic figure."""

    def plot(
        self,
        case: AnisotropicCase,
        sample: AnisotropicSample,
        diagnostic: AngularDiagnostics,
        path: Path,
        max_bloch_points: int,
    ) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        figure = plt.figure(figsize=(7.2, 11.2), dpi=180, constrained_layout=True)
        grid = figure.add_gridspec(3, 1, height_ratios=(1.0, 0.9, 1.35))

        histogram = figure.add_subplot(grid[0, 0])
        histogram.stairs(
            diagnostic.p_theta,
            diagnostic.edges,
            color=BLUE,
            linewidth=1.55,
            fill=True,
            alpha=0.17,
            label=r"$P(\theta)$",
        )
        histogram.stairs(
            diagnostic.p_reflected,
            diagnostic.edges,
            color=RED,
            linewidth=1.45,
            fill=True,
            alpha=0.13,
            label=r"$P(\pi-\theta)$",
        )
        histogram.set(xlim=(0.0, np.pi), ylabel="density")
        histogram.grid(alpha=0.16)
        histogram.legend(frameon=False, loc="upper center", ncol=2)

        ratio_axis = figure.add_subplot(grid[1, 0])
        ratio_axis.plot(
            diagnostic.centers[diagnostic.occupied],
            diagnostic.ratio[diagnostic.occupied],
            "o-",
            color=RATIO,
            linewidth=1.05,
            markersize=3.2,
            label=r"$R(\theta)$ (occupied bins)",
        )
        ratio_axis.plot(
            diagnostic.centers,
            diagnostic.born_curve,
            color="black",
            linestyle="--",
            linewidth=1.35,
            label=r"$\cos^2(\theta/2)$",
        )
        ratio_axis.set(xlim=(0.0, np.pi), ylim=(-0.04, 1.04), xlabel=r"$\theta$", ylabel=r"$R(\theta)$")
        ratio_axis.grid(alpha=0.16)
        ratio_axis.legend(frameon=False, loc="upper center", ncol=2)
        ratio_axis.text(
            0.03,
            0.07,
            rf"$S_{{\mathrm{{born}}}}={diagnostic.born_score:.3f}$" + "\n" + rf"RMSE$={diagnostic.born_rmse:.3f}$",
            transform=ratio_axis.transAxes,
            fontsize=9,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
        )

        bloch = figure.add_subplot(grid[2, 0], projection="3d")
        branch_blue, branch_red = _bloch_branches(sample.eigenvalues)
        _wire_sphere(bloch)
        if max_bloch_points > 0 and branch_blue.shape[0] > max_bloch_points:
            indices = np.linspace(0, branch_blue.shape[0] - 1, max_bloch_points, dtype=int)
            branch_blue = branch_blue[indices]
            branch_red = branch_red[indices]
        bloch.scatter(
            branch_blue[:, 0], branch_blue[:, 1], branch_blue[:, 2],
            s=4.5, color=BLUE, alpha=0.34, depthshade=False, label=r"$v(\lambda)$",
        )
        bloch.scatter(
            branch_red[:, 0], branch_red[:, 1], branch_red[:, 2],
            s=4.5, color=RED, alpha=0.28, depthshade=False, label=r"$-v(\lambda)$",
        )
        bloch.set(xlim=(-1.04, 1.04), ylim=(-1.04, 1.04), zlim=(-1.04, 1.04))
        bloch.set_box_aspect((1.0, 1.0, 1.0))
        bloch.view_init(elev=22.0, azim=42.0)
        bloch.set_axis_off()
        bloch.legend(frameon=False, loc="upper left")

        figure.suptitle(
            rf"Single pixel: $N={case.detector_n}$, $h_z={case.hz:g}$, $J={case.j:g}$, "
            rf"$J_{{\pm}}={case.jpm:g}$, $h_{{z0}}={case.hz0:g}$, "
            rf"$J_x={case.jx:g}$, $t={case.evolution_time:.0e}$",
            fontsize=13,
            fontweight="bold",
        )
        figure.savefig(path, bbox_inches="tight", pad_inches=0.10)
        plt.close(figure)
        return path


class AnisotropicSweepService:
    """Orchestrate one independent PBS row through injected services."""

    def __init__(
        self,
        repository: AnisotropicRepository,
        backend: CaseBackend,
        plotter: DiagnosticPlotter,
    ):
        self.repository = repository
        self.backend = backend
        self.plotter = plotter

    def run_task(
        self,
        config: AnisotropicSweepConfig,
        task: SweepRowTask,
        *,
        force: bool = False,
    ) -> Path:
        calculator = AngularDiagnosticCalculator(config.bins)
        completed: list[dict[str, Any]] = []
        started = time.time()
        running_path = self.repository.row_status_path(task, "RUNNING.json")
        done_path = self.repository.row_status_path(task, "DONE.json")
        failed_path = self.repository.row_status_path(task, "FAILED.json")
        failed_path.unlink(missing_ok=True)
        _atomic_json(
            running_path,
            {
                "task": asdict(task),
                "config_digest": config.digest,
                "expected_jpm_values": list(config.jpm_values),
                "started_unix_time": started,
            },
        )
        try:
            for jpm in config.jpm_values:
                case = AnisotropicCase(
                    detector_n=task.detector_n,
                    hz=task.hz,
                    j=task.j,
                    jpm=float(jpm),
                    evolution_time=config.evolution_time,
                    jx=config.jx,
                    hz0=config.hz0,
                    seed=config.seed,
                )
                if force or not self.repository.has_sample(case):
                    print(
                        f"Simulating N={case.detector_n} hz={case.hz:+g} J={case.j:g} "
                        f"Jpm={case.jpm:g} Jx_edge={case.edge_jx:.8g} t={case.evolution_time:.0e}",
                        flush=True,
                    )
                    sample = self.backend.compute(case)
                    self.repository.save_sample(case, sample)
                    self.repository.save_metadata(case, sample, config.digest)
                else:
                    print(
                        f"Reusing N={case.detector_n} hz={case.hz:+g} J={case.j:g} Jpm={case.jpm:g}",
                        flush=True,
                    )
                    sample = self.repository.load_sample(case)
                diagnostic = calculator.calculate(sample)
                metrics_path = self.repository.save_metrics(case, diagnostic)
                figure_path = self.repository.figure_path(case)
                if force or not figure_path.is_file():
                    self.plotter.plot(case, sample, diagnostic, figure_path, config.max_bloch_points)
                completed.append(
                    {
                        "Jpm": case.jpm,
                        "raw": str(self.repository.raw_path(case)),
                        "metrics": str(metrics_path),
                        "figure": str(figure_path),
                        "S_born": diagnostic.born_score,
                    }
                )
                _atomic_json(
                    running_path,
                    {
                        "task": asdict(task),
                        "config_digest": config.digest,
                        "expected_jpm_values": list(config.jpm_values),
                        "completed": completed,
                        "updated_unix_time": time.time(),
                    },
                )
                del sample, diagnostic
                gc.collect()
        except Exception as exc:
            _atomic_json(
                failed_path,
                {
                    "task": asdict(task),
                    "config_digest": config.digest,
                    "completed": completed,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "failed_unix_time": time.time(),
                },
            )
            raise
        _atomic_json(
            done_path,
            {
                "task": asdict(task),
                "config_digest": config.digest,
                "completed": completed,
                "elapsed_seconds": time.time() - started,
                "finished_unix_time": time.time(),
            },
        )
        running_path.unlink(missing_ok=True)
        return done_path

    def run_n(
        self,
        config: AnisotropicSweepConfig,
        detector_n: int,
        *,
        workers: int = 0,
        force: bool = False,
    ) -> Path:
        """Run all ``(hz, J, Jpm)`` configurations for one detector size.

        Independent Hamiltonians are submitted to a process pool. The parent
        alone persists spectra, metrics, figures, and status, so completion
        order cannot cause concurrent writes to shared files.
        """

        if detector_n not in config.detector_sizes:
            raise ValueError(f"N={detector_n} is not present in the configuration")
        effective_workers = recommended_worker_count(detector_n) if workers <= 0 else int(workers)
        if effective_workers < 1:
            raise ValueError("workers must be positive or zero for the memory-aware default")
        # Diagonal traversal ensures the first simultaneously active workers
        # receive different values of both J and Jpm, not merely adjacent Jpm
        # values at one fixed J. Every Cartesian-product pair appears once.
        j_jpm_pairs = [
            (config.j_values[j_index], config.jpm_values[(offset + j_index) % len(config.jpm_values)])
            for offset in range(len(config.jpm_values))
            for j_index in range(len(config.j_values))
        ]
        cases = [
            AnisotropicCase(
                detector_n=detector_n,
                hz=hz,
                j=j,
                jpm=jpm,
                evolution_time=config.evolution_time,
                jx=config.jx,
                hz0=config.hz0,
                seed=config.seed,
            )
            for hz in config.hz_values
            for j, jpm in j_jpm_pairs
        ]
        calculator = AngularDiagnosticCalculator(config.bins)
        completed: list[dict[str, Any]] = []
        started = time.time()
        running_path = self.repository.n_status_path(detector_n, "RUNNING.json")
        done_path = self.repository.n_status_path(detector_n, "DONE.json")
        failed_path = self.repository.n_status_path(detector_n, "FAILED.json")
        failed_path.unlink(missing_ok=True)

        def checkpoint() -> None:
            _atomic_json(
                running_path,
                {
                    "detector_n": detector_n,
                    "config_digest": config.digest,
                    "workers": effective_workers,
                    "expected_cases": len(cases),
                    "completed_cases": len(completed),
                    "completed": completed,
                    "updated_at": _timestamp(),
                    "updated_unix_time": time.time(),
                },
            )

        def persist(case: AnisotropicCase, sample: AnisotropicSample, source: str) -> None:
            self.repository.save_sample(case, sample)
            self.repository.save_metadata(case, sample, config.digest)
            diagnostic = calculator.calculate(sample)
            metrics_path = self.repository.save_metrics(case, diagnostic)
            figure_path = self.repository.figure_path(case)
            if force or not figure_path.is_file():
                self.plotter.plot(case, sample, diagnostic, figure_path, config.max_bloch_points)
            completed.append(
                {
                    "hz": case.hz,
                    "J": case.j,
                    "Jpm": case.jpm,
                    "source": source,
                    "worker_name": sample.worker_name,
                    "worker_pid": sample.worker_pid,
                    "calculation_started": sample.calculation_started,
                    "calculation_finished": sample.calculation_finished,
                    "raw": str(self.repository.raw_path(case)),
                    "metrics": str(metrics_path),
                    "figure": str(figure_path),
                    "S_born": diagnostic.born_score,
                }
            )
            print(
                f"[{_timestamp()}] parent_pid={os.getpid()} event=CHECKPOINT "
                f"worker={sample.worker_name} worker_pid={sample.worker_pid} "
                f"N={case.detector_n} hz={case.hz:+g} J={case.j:g} Jpm={case.jpm:g} "
                f"completed={len(completed)}/{len(cases)}",
                flush=True,
            )
            checkpoint()
            del diagnostic
            gc.collect()

        _atomic_json(
            running_path,
            {
                "detector_n": detector_n,
                "config_digest": config.digest,
                "workers": effective_workers,
                "expected_cases": len(cases),
                "completed_cases": 0,
                "completed": [],
                "started_at": _timestamp(),
                "started_unix_time": started,
            },
        )
        print(
            f"[{_timestamp()}] N={detector_n} configurations={len(cases)} "
            f"process_workers={effective_workers}",
            flush=True,
        )
        try:
            pending: list[AnisotropicCase] = []
            for case in cases:
                if not force and self.repository.has_sample(case):
                    sample = self.repository.load_sample(case)
                    print(
                        f"[{_timestamp()}] worker=parent pid={os.getpid()} event=REUSE "
                        f"N={case.detector_n} hz={case.hz:+g} J={case.j:g} Jpm={case.jpm:g}",
                        flush=True,
                    )
                    persist(case, sample, "checkpoint")
                    del sample
                else:
                    pending.append(case)

            if effective_workers == 1 or len(pending) <= 1:
                for case in pending:
                    persist(case, self.backend.compute(case), "computed")
            else:
                pool_size = min(effective_workers, len(pending))
                print(
                    f"[{_timestamp()}] submitting={len(pending)} process_workers={pool_size} "
                    "parallel_axes=J,Jpm,hz scheduling=diagonal-J-Jpm",
                    flush=True,
                )
                with ProcessPoolExecutor(max_workers=pool_size) as pool:
                    futures = {pool.submit(self.backend.compute, case): case for case in pending}
                    for future in as_completed(futures):
                        case = futures[future]
                        persist(case, future.result(), "computed")
        except Exception as exc:
            _atomic_json(
                failed_path,
                {
                    "detector_n": detector_n,
                    "config_digest": config.digest,
                    "workers": effective_workers,
                    "completed_cases": len(completed),
                    "completed": completed,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "failed_at": _timestamp(),
                    "failed_unix_time": time.time(),
                },
            )
            raise

        completed.sort(key=lambda item: (float(item["hz"]), float(item["J"]), float(item["Jpm"])))
        _atomic_json(
            done_path,
            {
                "detector_n": detector_n,
                "config_digest": config.digest,
                "workers": effective_workers,
                "completed_cases": len(completed),
                "completed": completed,
                "elapsed_seconds": time.time() - started,
                "finished_at": _timestamp(),
                "finished_unix_time": time.time(),
            },
        )
        running_path.unlink(missing_ok=True)
        return done_path


class BornHeatmapAggregator:
    """Aggregate completed cases into per-``N``, per-``hz`` J--Jpm maps."""

    def __init__(self, repository: AnisotropicRepository):
        self.repository = repository

    def _cases_for_n_hz(
        self,
        config: AnisotropicSweepConfig,
        detector_n: int,
        hz: float,
    ) -> list[AnisotropicCase]:
        return [
            AnisotropicCase(
                detector_n=detector_n,
                hz=hz,
                j=j,
                jpm=jpm,
                evolution_time=config.evolution_time,
                jx=config.jx,
                hz0=config.hz0,
                seed=config.seed,
            )
            for j in config.j_values
            for jpm in config.jpm_values
        ]

    def aggregate_n(
        self,
        config: AnisotropicSweepConfig,
        detector_n: int,
        *,
        allow_partial: bool = False,
    ) -> Path:
        if detector_n not in config.detector_sizes:
            raise ValueError(f"N={detector_n} is not present in the configuration")
        n_root = self.repository.root / "aggregates" / f"N{detector_n:02d}"
        n_root.mkdir(parents=True, exist_ok=True)
        all_rows: list[dict[str, Any]] = []
        missing: list[str] = []
        heatmaps: list[str] = []
        for hz in config.hz_values:
            matrix = np.full((len(config.jpm_values), len(config.j_values)), np.nan, dtype=float)
            for j_index, j in enumerate(config.j_values):
                for jpm_index, jpm in enumerate(config.jpm_values):
                    case = AnisotropicCase(
                        detector_n=detector_n,
                        hz=hz,
                        j=j,
                        jpm=jpm,
                        evolution_time=config.evolution_time,
                        jx=config.jx,
                        hz0=config.hz0,
                        seed=config.seed,
                    )
                    metrics_path = self.repository.metrics_path(case)
                    figure_path = self.repository.figure_path(case)
                    raw_path = self.repository.raw_path(case)
                    if not (metrics_path.is_file() and figure_path.is_file() and raw_path.is_file()):
                        missing.append(str(self.repository.case_relative_dir(case)))
                        continue
                    row = self.repository.load_metrics(case)
                    row["raw_path"] = str(raw_path)
                    row["figure_path"] = str(figure_path)
                    all_rows.append(row)
                    matrix[jpm_index, j_index] = float(row["S_born"])
            if np.isfinite(matrix).any():
                heatmap_path = n_root / f"S_born_hz_{_value_tag(hz)}_J_vs_Jpm.png"
                self._plot_heatmap(config, detector_n, hz, matrix, heatmap_path)
                heatmaps.append(str(heatmap_path))

        if missing and not allow_partial:
            preview = ", ".join(missing[:5])
            raise RuntimeError(f"N={detector_n} is missing {len(missing)} cases; first: {preview}")

        csv_path = n_root / f"anisotropic_metrics_N{detector_n:02d}.csv"
        self._write_metrics_csv(csv_path, all_rows)
        manifest_path = n_root / "manifest.json"
        _atomic_json(
            manifest_path,
            {
                "detector_n": detector_n,
                "total_qubits": detector_n + 1,
                "config_digest": config.digest,
                "expected_cases": len(config.hz_values) * len(config.j_values) * len(config.jpm_values),
                "completed_cases": len(all_rows),
                "missing_cases": missing,
                "complete": not missing,
                "evolution_time": config.evolution_time,
                "collective_Jx": config.jx,
                "edge_Jx": config.jx / math.sqrt(detector_n),
                "heatmaps": heatmaps,
                "metrics_csv": str(csv_path),
                "completed_unix_time": time.time(),
            },
        )
        return manifest_path

    @staticmethod
    def _write_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "detector_n", "hz", "J", "Jpm", "evolution_time", "jx", "hz0", "Jx_edge",
            "S_born", "born_rmse", "angular_bin_coverage", "phi_harmonic_2",
            "finite_eigenvalues", "excluded_eigenvalues", "p_theta_integral",
            "p_reflected_integral", "raw_path", "figure_path",
        ]
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for payload in rows:
                case = payload["case"]
                row = {
                    "detector_n": case["detector_n"],
                    "hz": case["hz"],
                    "J": case["j"],
                    "Jpm": case["jpm"],
                    "evolution_time": case["evolution_time"],
                    "jx": case["jx"],
                    "hz0": case["hz0"],
                    **{key: payload.get(key, "") for key in fields if key not in {
                        "detector_n", "hz", "J", "Jpm", "evolution_time", "jx", "hz0"
                    }},
                }
                writer.writerow(row)
        temporary.replace(path)

    @staticmethod
    def _plot_heatmap(
        config: AnisotropicSweepConfig,
        detector_n: int,
        hz: float,
        matrix: np.ndarray,
        path: Path,
    ) -> None:
        figure, axis = plt.subplots(figsize=(9.2, 7.1), dpi=190, constrained_layout=True)
        colormap = plt.get_cmap("RdYlGn").with_extremes(bad="#d7d7d7")
        image = axis.imshow(matrix, origin="lower", aspect="auto", cmap=colormap, vmin=0.0, vmax=1.0)
        axis.set_xlabel(r"Ising coupling $J$")
        axis.set_ylabel(r"exchange coupling $J_{\pm}$")
        axis.set_xticks(range(len(config.j_values)))
        axis.set_xticklabels([f"{value:g}" for value in config.j_values], rotation=35, ha="right")
        axis.set_yticks(range(len(config.jpm_values)))
        axis.set_yticklabels([f"{value:g}" for value in config.jpm_values])
        for jpm_index, jpm in enumerate(config.jpm_values):
            for j_index, j in enumerate(config.j_values):
                if math.isclose(jpm, j, rel_tol=0.0, abs_tol=1.0e-12):
                    axis.scatter(j_index, jpm_index, s=54, facecolors="none", edgecolors="black", linewidths=0.8)
        colorbar = figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
        colorbar.set_label(r"$S_{\mathrm{born}}$ (values $\leq 0$ are red)")
        axis.set_title(
            rf"Single pixel, $N={detector_n}$, $h_z={hz:g}$, $h_{{z0}}={config.hz0:g}$, "
            rf"$J_x={config.jx:g}$, $t={config.evolution_time:.0e}$"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, bbox_inches="tight", pad_inches=0.10)
        plt.close(figure)


def describe_config(config: AnisotropicSweepConfig) -> dict[str, Any]:
    per_n = len(config.hz_values) * len(config.j_values)
    ranges = []
    for index, detector_n in enumerate(config.detector_sizes):
        start = index * per_n + 1
        ranges.append({"N": detector_n, "task_start": start, "task_end": start + per_n - 1})
    return {
        "config_digest": config.digest,
        "pbs_array_indices": list(config.detector_sizes),
        "pbs_task_count": len(config.detector_sizes),
        "cases_per_N": len(config.hz_values) * len(config.j_values) * len(config.jpm_values),
        "internal_row_task_count": config.task_count,
        "cases_per_internal_row": config.cases_per_task,
        "total_case_count": config.total_case_count,
        "internal_rows_by_N": ranges,
        "recommended_process_workers": {
            str(detector_n): recommended_worker_count(detector_n)
            for detector_n in config.detector_sizes
        },
        "collective_Jx": config.jx,
        "edge_coupling_formula": "Jx/sqrt(N)",
        "evolution_time": config.evolution_time,
    }


__all__ = [
    "AngularDiagnosticCalculator",
    "AngularDiagnostics",
    "AnisotropicCase",
    "AnisotropicRepository",
    "AnisotropicSample",
    "AnisotropicSweepConfig",
    "AnisotropicSweepService",
    "BlueRedDiagnosticPlotter",
    "BornHeatmapAggregator",
    "CaseBackend",
    "DiagnosticPlotter",
    "QuSpinAnisotropicBackend",
    "SweepRowTask",
    "describe_config",
    "recommended_worker_count",
    "smoke_config",
]
