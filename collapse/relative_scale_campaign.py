"""Single-pixel campaign organized by relative ``|hz|``, ``J``, and ``Jpm`` scales."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
from datetime import datetime
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import time
from typing import Any, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collapse.anisotropic_analysis import SpectrumMetricCalculator
from collapse.anisotropic_sweep import (
    AngularDiagnosticCalculator,
    AnisotropicCase,
    AnisotropicRepository,
    BlueRedDiagnosticPlotter,
    CaseBackend,
    DiagnosticPlotter,
    QuSpinAnisotropicBackend,
)
from collapse.degeneracy_heavy_tail_campaign import AtomicFileLock


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _atomic_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)
    return path


def _atomic_csv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)
    return path


@dataclass(frozen=True)
class RelativeScaleCase:
    """One explicit point representing a relative-scale regime."""

    case_id: str
    regime: str
    hz: float
    J: float
    Jpm: float
    description: str

    def __post_init__(self) -> None:
        if not self.case_id or any(character.isspace() for character in self.case_id):
            raise ValueError("case_id must be a nonempty token without whitespace")
        if not self.regime:
            raise ValueError("regime must be nonempty")
        if self.J < 0.0 or self.Jpm < 0.0:
            raise ValueError("J and Jpm must be non-negative")
        if not all(math.isfinite(value) for value in (self.hz, self.J, self.Jpm)):
            raise ValueError("Hamiltonian parameters must be finite")


@dataclass(frozen=True)
class RelativeScaleConfig:
    """Immutable configuration for the relative-scale campaign."""

    detector_sizes: tuple[int, ...]
    cases: tuple[RelativeScaleCase, ...]
    evolution_time: float = 1.0e6
    jx: float = 0.01
    hz0: float = 0.0
    bins: int = 48
    max_bloch_points: int = 6000
    seed: int = 44
    minimum_nonzero_scale_multiple: float = 10.0

    def __post_init__(self) -> None:
        if not self.detector_sizes or any(value < 3 for value in self.detector_sizes):
            raise ValueError("detector_sizes must contain values >=3")
        if len(set(self.detector_sizes)) != len(self.detector_sizes):
            raise ValueError("detector_sizes contains duplicates")
        if not self.cases or len({case.case_id for case in self.cases}) != len(self.cases):
            raise ValueError("cases must be nonempty with unique IDs")
        if self.evolution_time <= 0.0 or self.jx <= 0.0:
            raise ValueError("evolution_time and jx must be positive")
        if self.minimum_nonzero_scale_multiple < 1.0:
            raise ValueError("minimum_nonzero_scale_multiple must be >=1")
        threshold = self.minimum_nonzero_scale_multiple * self.jx
        for case in self.cases:
            for name, value in (("|hz|", abs(case.hz)), ("J", case.J), ("Jpm", case.Jpm)):
                if 0.0 < value < threshold - 1.0e-15:
                    raise ValueError(
                        f"{case.case_id}: nonzero {name}={value:g} is below {threshold:g}"
                    )

    @classmethod
    def from_json(cls, path: Path) -> "RelativeScaleConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            detector_sizes=tuple(int(value) for value in payload["detector_sizes"]),
            cases=tuple(RelativeScaleCase(**item) for item in payload["cases"]),
            evolution_time=float(payload.get("evolution_time", 1.0e6)),
            jx=float(payload.get("jx", 0.01)),
            hz0=float(payload.get("hz0", 0.0)),
            bins=int(payload.get("bins", 48)),
            max_bloch_points=int(payload.get("max_bloch_points", 6000)),
            seed=int(payload.get("seed", 44)),
            minimum_nonzero_scale_multiple=float(
                payload.get("minimum_nonzero_scale_multiple", 10.0)
            ),
        )

    @property
    def digest(self) -> str:
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()[:16]

    def simulation_case(self, detector_n: int, definition: RelativeScaleCase) -> AnisotropicCase:
        if detector_n not in self.detector_sizes:
            raise ValueError(f"N={detector_n} is not configured")
        return AnisotropicCase(
            detector_n=detector_n,
            hz=definition.hz,
            j=definition.J,
            jpm=definition.Jpm,
            evolution_time=self.evolution_time,
            jx=self.jx,
            hz0=self.hz0,
            seed=self.seed,
        )

    def ratios(self, case: RelativeScaleCase) -> dict[str, float]:
        values = {"abs_hz": abs(case.hz), "J": case.J, "Jpm": case.Jpm}
        nonzero = {name: value for name, value in values.items() if value > 0.0}
        ratios: dict[str, float] = {
            f"Jx_over_{name}": self.jx / value for name, value in nonzero.items()
        }
        ratios["maximum_Jx_ratio"] = max(ratios.values(), default=0.0)
        if nonzero:
            largest = max(nonzero.values())
            smallest = min(nonzero.values())
            ratios["largest_over_smallest_nonzero_scale"] = largest / smallest
        else:
            ratios["largest_over_smallest_nonzero_scale"] = 1.0
        return ratios


def smoke_config(config: RelativeScaleConfig) -> RelativeScaleConfig:
    """Select four qualitatively distinct cases for an N=4 smoke run."""

    wanted = (
        "p_h_gt_j_eq_p",
        "p_j_gt_h_eq_p",
        "p_p_gt_h_eq_j",
        "p_all_equal",
    )
    lookup = {case.case_id: case for case in config.cases}
    selected = tuple(lookup[name] for name in wanted if name in lookup)
    if len(selected) < 4:
        selected = config.cases[:4]
    return replace(
        config,
        detector_sizes=(4,),
        cases=selected,
        evolution_time=100.0,
        bins=24,
        max_bloch_points=256,
    )


class RelativeScaleRepository:
    """Named campaign outputs backed by the standard anisotropic repository."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.spectra = AnisotropicRepository(self.root)

    def metric_path(self, detector_n: int, case_id: str) -> Path:
        return self.root / "regime_metrics" / f"N{detector_n:02d}" / case_id / "metrics.json"

    def figure_path(self, detector_n: int, case_id: str) -> Path:
        return self.root / "figures" / f"N{detector_n:02d}" / case_id / "blue_red.png"

    def status_path(self, detector_n: int, name: str) -> Path:
        return self.root / "status" / f"N{detector_n:02d}" / name

    def aggregate_root(self, detector_n: int) -> Path:
        return self.root / "aggregates" / f"N{detector_n:02d}"

    def cross_n_lock(self) -> Path:
        return self.root / "status" / "aggregate_all.lock"


class RelativeScaleAggregator:
    """Build per-N comparisons and a concurrency-safe evolving cross-N atlas."""

    _fields = (
        "detector_n",
        "case_id",
        "regime",
        "hz",
        "J",
        "Jpm",
        "maximum_Jx_ratio",
        "scale_separation",
        "S_born",
        "born_rmse",
        "theta_power_law_alpha",
        "theta_power_law_js",
        "theta_power_law_log10_span",
        "angular_bin_coverage",
        "radius_atomic_fraction",
        "S_wrapped_heavy",
        "heavy_primary",
        "preferred_wrapped_model",
        "raw_path",
        "figure_path",
    )

    def __init__(self, repository: RelativeScaleRepository) -> None:
        self.repository = repository

    @staticmethod
    def _heavy(metrics: dict[str, Any]) -> bool:
        return bool(
            float(metrics["theta_power_law_alpha"]) <= 2.0
            and float(metrics["theta_power_law_js"]) <= 0.10
            and float(metrics["angular_bin_coverage"]) >= 0.50
            and float(metrics["theta_power_law_log10_span"]) >= 1.0
        )

    def _row(self, payload: dict[str, Any]) -> dict[str, Any]:
        definition = payload["definition"]
        metrics = payload["spectrum_metrics"]
        ratios = payload["perturbative_ratios"]
        return {
            "detector_n": int(metrics["detector_n"]),
            "case_id": definition["case_id"],
            "regime": definition["regime"],
            "hz": definition["hz"],
            "J": definition["J"],
            "Jpm": definition["Jpm"],
            "maximum_Jx_ratio": ratios["maximum_Jx_ratio"],
            "scale_separation": ratios["largest_over_smallest_nonzero_scale"],
            "S_born": metrics["S_born"],
            "born_rmse": metrics["born_rmse"],
            "theta_power_law_alpha": metrics["theta_power_law_alpha"],
            "theta_power_law_js": metrics["theta_power_law_js"],
            "theta_power_law_log10_span": metrics["theta_power_law_log10_span"],
            "angular_bin_coverage": metrics["angular_bin_coverage"],
            "radius_atomic_fraction": metrics["radius_atomic_fraction"],
            "S_wrapped_heavy": metrics["S_wrapped_heavy"],
            "heavy_primary": self._heavy(metrics),
            "preferred_wrapped_model": metrics["preferred_wrapped_model"],
            "raw_path": payload["raw_path"],
            "figure_path": payload["figure_path"],
        }

    def _load_rows(
        self,
        config: RelativeScaleConfig,
        detector_sizes: Sequence[int],
    ) -> tuple[list[dict[str, Any]], list[str]]:
        rows: list[dict[str, Any]] = []
        missing: list[str] = []
        for detector_n in detector_sizes:
            for definition in config.cases:
                path = self.repository.metric_path(detector_n, definition.case_id)
                if path.is_file():
                    rows.append(self._row(json.loads(path.read_text(encoding="utf-8"))))
                else:
                    missing.append(f"N{detector_n:02d}/{definition.case_id}")
        return rows, missing

    def aggregate_n(self, config: RelativeScaleConfig, detector_n: int) -> Path:
        rows, missing = self._load_rows(config, (detector_n,))
        if missing:
            raise RuntimeError(f"N={detector_n} missing {len(missing)} cases")
        order = {case.case_id: index for index, case in enumerate(config.cases)}
        rows.sort(key=lambda row: order[str(row["case_id"])])
        root = self.repository.aggregate_root(detector_n)
        csv_path = _atomic_csv(root / f"relative_scale_metrics_N{detector_n:02d}.csv", rows, self._fields)
        figure_path = root / f"relative_scale_comparison_N{detector_n:02d}.png"
        self._plot_n(rows, detector_n, figure_path)
        return _atomic_json(
            root / "summary.json",
            {
                "detector_n": detector_n,
                "case_count": len(rows),
                "metrics_csv": str(csv_path),
                "figure": str(figure_path),
                "heavy_primary_cases": [
                    row["case_id"] for row in rows if bool(row["heavy_primary"])
                ],
                "best_born_case": max(rows, key=lambda row: float(row["S_born"]))["case_id"],
            },
        )

    @staticmethod
    def _plot_n(rows: Sequence[dict[str, Any]], detector_n: int, path: Path) -> None:
        labels = [str(row["case_id"]) for row in rows]
        x = np.arange(len(rows))
        width = max(13.0, 0.48 * len(rows))
        figure, axes = plt.subplots(2, 1, figsize=(width, 8.8), dpi=180, constrained_layout=True)
        axes[0].plot(x, [float(row["S_born"]) for row in rows], "o-", color="#6b3f7c")
        axes[0].set(ylabel=r"$S_{\rm born}$", ylim=(-0.05, 1.05))
        axes[1].plot(
            x,
            [float(row["theta_power_law_alpha"]) for row in rows],
            "o-",
            color="#2b6f8e",
        )
        axes[1].axhline(2.0, color="black", linestyle="--", linewidth=1.0)
        axes[1].set(ylabel=r"wrapped power-law $\alpha$", xlabel="relative-scale regime")
        for axis in axes:
            axis.grid(alpha=0.18)
            axis.set_xticks(x, labels, rotation=35, ha="right", fontsize=8)
        figure.suptitle(rf"Relative-scale regime comparison, $N={detector_n}$, $t=10^6$")
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, bbox_inches="tight", pad_inches=0.08)
        plt.close(figure)

    def aggregate_all_locked(
        self,
        config: RelativeScaleConfig,
        *,
        allow_partial: bool,
    ) -> Path:
        with AtomicFileLock(self.repository.cross_n_lock()):
            rows, missing = self._load_rows(config, config.detector_sizes)
            if missing and not allow_partial:
                raise RuntimeError(f"missing {len(missing)} case metrics")
            root = self.repository.root / "aggregates" / "all_N"
            csv_path = _atomic_csv(root / "all_relative_scale_metrics.csv", rows, self._fields)
            figure_path = root / "relative_scale_across_N.png"
            self._plot_all(config, rows, figure_path)
            return _atomic_json(
                root / "summary.json",
                {
                    "config_digest": config.digest,
                    "expected_rows": len(config.detector_sizes) * len(config.cases),
                    "completed_rows": len(rows),
                    "complete": not missing,
                    "missing": missing,
                    "metrics_csv": str(csv_path),
                    "figure": str(figure_path),
                },
            )

    @staticmethod
    def _plot_all(
        config: RelativeScaleConfig,
        rows: Sequence[dict[str, Any]],
        path: Path,
    ) -> None:
        lookup = {(str(row["case_id"]), int(row["detector_n"])): row for row in rows}
        height = max(7.0, 0.32 * len(config.cases) + 1.5)
        figure, axes = plt.subplots(1, 3, figsize=(15.0, height), dpi=180, constrained_layout=True)
        specifications = (
            ("S_born", r"$S_{\rm born}$", "viridis", 0.0, 1.0),
            ("theta_power_law_alpha", r"power-law $\alpha$", "magma_r", 0.0, 4.0),
            ("heavy_primary", "wrapped-heavy gate", "RdYlGn", 0.0, 1.0),
        )
        for axis, (field, title, cmap, lower, upper) in zip(axes, specifications, strict=True):
            matrix = np.full((len(config.cases), len(config.detector_sizes)), np.nan)
            for y, case in enumerate(config.cases):
                for x, detector_n in enumerate(config.detector_sizes):
                    row = lookup.get((case.case_id, detector_n))
                    if row is not None:
                        matrix[y, x] = float(row[field])
            image = axis.imshow(
                matrix,
                aspect="auto",
                origin="upper",
                cmap=plt.get_cmap(cmap).with_extremes(bad="#d7d7d7"),
                vmin=lower,
                vmax=upper,
            )
            axis.set_xticks(range(len(config.detector_sizes)), config.detector_sizes)
            axis.set_yticks(range(len(config.cases)), [case.case_id for case in config.cases], fontsize=7)
            axis.set(xlabel="detector size N", title=title)
            figure.colorbar(image, ax=axis, fraction=0.046, pad=0.03)
        figure.suptitle("Relative-scale regimes across N (no cell annotations)")
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, bbox_inches="tight", pad_inches=0.08)
        plt.close(figure)


class RelativeScaleCampaignService:
    """Parallelize Hamiltonian regimes and checkpoint each completed case."""

    def __init__(
        self,
        repository: RelativeScaleRepository,
        backend: CaseBackend | None = None,
        plotter: DiagnosticPlotter | None = None,
    ) -> None:
        self.repository = repository
        self.backend = backend or QuSpinAnisotropicBackend()
        self.plotter = plotter or BlueRedDiagnosticPlotter()

    @staticmethod
    def recommended_workers(detector_n: int) -> int:
        if detector_n <= 13:
            return 4
        if detector_n <= 15:
            return 2
        return 1

    def run_n(
        self,
        config: RelativeScaleConfig,
        detector_n: int,
        *,
        workers: int = 0,
        force: bool = False,
    ) -> Path:
        if detector_n not in config.detector_sizes:
            raise ValueError(f"N={detector_n} is not configured")
        effective_workers = self.recommended_workers(detector_n) if workers <= 0 else workers
        calculator = AngularDiagnosticCalculator(config.bins)
        spectrum_calculator = SpectrumMetricCalculator(config.bins)
        running = self.repository.status_path(detector_n, "RUNNING.json")
        done = self.repository.status_path(detector_n, "DONE.json")
        failed = self.repository.status_path(detector_n, "FAILED.json")
        failed.unlink(missing_ok=True)
        completed: list[dict[str, Any]] = []
        started = time.time()

        def checkpoint() -> None:
            _atomic_json(
                running,
                {
                    "detector_n": detector_n,
                    "expected_cases": len(config.cases),
                    "completed_cases": len(completed),
                    "completed": completed,
                    "updated_at": _timestamp(),
                },
            )

        def persist(
            definition: RelativeScaleCase,
            case: AnisotropicCase,
            sample: Any,
            source: str,
        ) -> None:
            raw_path = self.repository.spectra.save_sample(case, sample)
            metadata_path = self.repository.spectra.save_metadata(case, sample, config.digest)
            diagnostic = calculator.calculate(sample)
            figure_path = self.repository.figure_path(detector_n, definition.case_id)
            if force or not figure_path.is_file():
                self.plotter.plot(case, sample, diagnostic, figure_path, config.max_bloch_points)
            metrics = spectrum_calculator.calculate(raw_path)
            metric_path = _atomic_json(
                self.repository.metric_path(detector_n, definition.case_id),
                {
                    "definition": asdict(definition),
                    "perturbative_ratios": config.ratios(definition),
                    "spectrum_metrics": asdict(metrics),
                    "raw_path": str(raw_path),
                    "metadata_path": str(metadata_path),
                    "figure_path": str(figure_path),
                    "source": source,
                    "worker_name": sample.worker_name,
                    "worker_pid": sample.worker_pid,
                    "saved_at": _timestamp(),
                    "diagnostic_figure_contents": (
                        "blue P(theta) and red P(pi-theta) histograms; connected "
                        "R(theta) versus Born; blue/red Bloch-sphere points"
                    ),
                },
            )
            completed.append(
                {
                    "case_id": definition.case_id,
                    "source": source,
                    "worker_name": sample.worker_name,
                    "worker_pid": sample.worker_pid,
                    "raw": str(raw_path),
                    "metadata": str(metadata_path),
                    "metrics": str(metric_path),
                    "figure": str(figure_path),
                }
            )
            print(
                f"[{_timestamp()}] parent_pid={os.getpid()} event=CHECKPOINT "
                f"worker={sample.worker_name} worker_pid={sample.worker_pid} "
                f"N={detector_n} case={definition.case_id} "
                f"completed={len(completed)}/{len(config.cases)}",
                flush=True,
            )
            checkpoint()

        checkpoint()
        pending: list[tuple[RelativeScaleCase, AnisotropicCase]] = []
        try:
            for definition in config.cases:
                case = config.simulation_case(detector_n, definition)
                if not force and self.repository.spectra.has_sample(case):
                    persist(
                        definition,
                        case,
                        self.repository.spectra.load_sample(case),
                        "checkpoint",
                    )
                else:
                    pending.append((definition, case))
            if effective_workers == 1 or len(pending) <= 1:
                for definition, case in pending:
                    persist(definition, case, self.backend.compute(case), "computed")
            else:
                pool_size = min(effective_workers, len(pending))
                print(
                    f"[{_timestamp()}] event=SUBMIT N={detector_n} cases={len(pending)} "
                    f"process_workers={pool_size} parallel_axis=Hamiltonian-regime",
                    flush=True,
                )
                with ProcessPoolExecutor(max_workers=pool_size) as pool:
                    futures = {
                        pool.submit(self.backend.compute, case): (definition, case)
                        for definition, case in pending
                    }
                    for future in as_completed(futures):
                        definition, case = futures[future]
                        persist(definition, case, future.result(), "computed")

            completed.sort(key=lambda item: str(item["case_id"]))
            aggregator = RelativeScaleAggregator(self.repository)
            per_n = aggregator.aggregate_n(config, detector_n)
            cross_n = aggregator.aggregate_all_locked(config, allow_partial=True)
            _atomic_json(
                done,
                {
                    "detector_n": detector_n,
                    "completed_cases": len(completed),
                    "completed": completed,
                    "per_n_aggregate": str(per_n),
                    "cross_n_aggregate": str(cross_n),
                    "elapsed_seconds": time.time() - started,
                    "finished_at": _timestamp(),
                    "checkpoint_contract": (
                        "every case is saved immediately; per-N and locked cross-N "
                        "plots/results are saved before DONE"
                    ),
                },
            )
        except Exception as exc:
            _atomic_json(
                failed,
                {
                    "detector_n": detector_n,
                    "completed": completed,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "failed_at": _timestamp(),
                },
            )
            raise
        running.unlink(missing_ok=True)
        return done


def describe_config(config: RelativeScaleConfig) -> dict[str, Any]:
    return {
        "config_digest": config.digest,
        "detector_sizes": list(config.detector_sizes),
        "case_count_per_N": len(config.cases),
        "total_simulations": len(config.detector_sizes) * len(config.cases),
        "evolution_time": config.evolution_time,
        "collective_Jx": config.jx,
        "edge_coupling_formula": "Jx/sqrt(N)",
        "minimum_nonzero_scale_multiple": config.minimum_nonzero_scale_multiple,
        "cases": [
            {**asdict(case), "perturbative_ratios": config.ratios(case)}
            for case in config.cases
        ],
    }


__all__ = [
    "RelativeScaleAggregator",
    "RelativeScaleCampaignService",
    "RelativeScaleCase",
    "RelativeScaleConfig",
    "RelativeScaleRepository",
    "describe_config",
    "smoke_config",
]
