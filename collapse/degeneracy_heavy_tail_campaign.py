"""Decisive finite-size tests of the degenerate-coupling heavy-tail conjecture.

The campaign uses Hamiltonian families for which activation can be certified
without a dense detector diagonalization:

* clean Ising detectors (``Jpm=0``), where a coupling matrix element flips
  one spin and has one of three analytically known energy gaps;
* the non-pure-Ising SU(2) line (``Jpm=2J``), where the exchange Hamiltonian
  commutes with ``V=sum_i X_i`` and a nonzero longitudinal field gives every
  nonzero ``V`` transition the exact gap ``2|hz|``.

Only the dynamical wrapped-heavy-tail outcome requires the expensive
many-body simulation.  Every case also satisfies a pre-registered
perturbative-scale check for the collective coupling ``Jx``.
"""

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
from typing import Any, Protocol, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collapse.anisotropic_analysis import SpectrumMetricCalculator, SpectrumMetrics
from collapse.anisotropic_sweep import (
    AngularDiagnosticCalculator,
    AnisotropicCase,
    AnisotropicRepository,
    AnisotropicSample,
    BlueRedDiagnosticPlotter,
    CaseBackend,
    DiagnosticPlotter,
    QuSpinAnisotropicBackend,
)


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


class AtomicFileLock:
    """Small cross-platform lock for the shared cross-N aggregation files."""

    def __init__(
        self,
        path: Path,
        *,
        timeout_seconds: float = 600.0,
        stale_seconds: float = 3600.0,
    ) -> None:
        self.path = Path(path)
        self.timeout_seconds = float(timeout_seconds)
        self.stale_seconds = float(stale_seconds)
        self._owned = False

    def __enter__(self) -> "AtomicFileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout_seconds
        payload = json.dumps(
            {
                "pid": os.getpid(),
                "created_at": _timestamp(),
            },
            sort_keys=True,
        ).encode("utf-8")
        while True:
            try:
                descriptor = os.open(
                    self.path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                )
            except FileExistsError:
                try:
                    age = time.time() - self.path.stat().st_mtime
                except FileNotFoundError:
                    continue
                if age >= self.stale_seconds:
                    stale = self.path.with_name(
                        f"{self.path.name}.stale.{int(time.time())}.{os.getpid()}"
                    )
                    try:
                        self.path.replace(stale)
                    except FileNotFoundError:
                        continue
                    stale.unlink(missing_ok=True)
                    continue
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out waiting for aggregation lock {self.path}")
                time.sleep(0.25)
                continue
            try:
                os.write(descriptor, payload)
            finally:
                os.close(descriptor)
            self._owned = True
            return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self._owned:
            self.path.unlink(missing_ok=True)
            self._owned = False


@dataclass(frozen=True)
class CampaignCaseDefinition:
    """One Hamiltonian chosen to populate a logical truth-table quadrant."""

    case_id: str
    hz: float
    J: float
    Jpm: float
    role: str
    rationale: str
    activation_model: str = "ising_local_flip"

    def __post_init__(self) -> None:
        if not self.case_id or any(character.isspace() for character in self.case_id):
            raise ValueError("case_id must be a nonempty token without whitespace")
        if not all(math.isfinite(value) for value in (self.hz, self.J, self.Jpm)):
            raise ValueError("Hamiltonian parameters must be finite")
        if self.activation_model == "ising_local_flip":
            if not math.isclose(self.Jpm, 0.0, rel_tol=0.0, abs_tol=1.0e-15):
                raise ValueError("ising_local_flip requires Jpm=0")
        elif self.activation_model == "su2_total_spin":
            if self.J <= 0.0 or not math.isclose(
                self.Jpm, 2.0 * self.J, rel_tol=0.0, abs_tol=1.0e-12
            ):
                raise ValueError("su2_total_spin requires J>0 and Jpm=2J")
        else:
            raise ValueError(f"unsupported activation_model {self.activation_model!r}")


@dataclass(frozen=True)
class HeavyTailGates:
    """Pre-registered primary and robustness gates."""

    power_law_alpha_max: float = 2.0
    power_law_js_max: float = 0.10
    angular_coverage_min: float = 0.50
    power_law_log10_span_min: float = 1.0
    robust_alpha_min: float = 0.10
    robust_power_law_js_max: float = 0.05
    robust_angular_coverage_min: float = 0.75
    robust_power_law_log10_span_min: float = 1.50
    robust_atomic_fraction_max: float = 0.05

    def primary(self, metrics: SpectrumMetrics | dict[str, Any]) -> bool:
        row = asdict(metrics) if isinstance(metrics, SpectrumMetrics) else metrics
        return bool(
            float(row["theta_power_law_alpha"]) <= self.power_law_alpha_max
            and float(row["theta_power_law_js"]) <= self.power_law_js_max
            and float(row["angular_bin_coverage"]) >= self.angular_coverage_min
            and float(row["theta_power_law_log10_span"]) >= self.power_law_log10_span_min
        )

    def robust(self, metrics: SpectrumMetrics | dict[str, Any]) -> bool:
        row = asdict(metrics) if isinstance(metrics, SpectrumMetrics) else metrics
        return bool(
            self.primary(row)
            and float(row["theta_power_law_alpha"]) >= self.robust_alpha_min
            and float(row["theta_power_law_js"]) <= self.robust_power_law_js_max
            and float(row["angular_bin_coverage"]) >= self.robust_angular_coverage_min
            and float(row["theta_power_law_log10_span"])
            >= self.robust_power_law_log10_span_min
            and float(row["radius_atomic_fraction"]) <= self.robust_atomic_fraction_max
        )


@dataclass(frozen=True)
class CampaignConfig:
    """Immutable simulation and classification configuration."""

    detector_sizes: tuple[int, ...]
    cases: tuple[CampaignCaseDefinition, ...]
    evolution_time: float = 1.0e6
    jx: float = 0.01
    hz0: float = 0.0
    bins: int = 48
    max_bloch_points: int = 6000
    seed: int = 44
    degeneracy_tolerance: float = 1.0e-12
    perturbative_ratio_max: float = 0.10
    gates: HeavyTailGates = HeavyTailGates()

    def __post_init__(self) -> None:
        if not self.detector_sizes or any(value < 3 for value in self.detector_sizes):
            raise ValueError("detector_sizes must contain values >= 3")
        if len(set(self.detector_sizes)) != len(self.detector_sizes):
            raise ValueError("detector_sizes contains duplicates")
        if not self.cases or len({case.case_id for case in self.cases}) != len(self.cases):
            raise ValueError("cases must be nonempty and have unique case_id values")
        if self.evolution_time <= 0.0 or self.jx <= 0.0:
            raise ValueError("evolution_time and jx must be positive")
        if self.bins < 4 or self.max_bloch_points < 0:
            raise ValueError("invalid plotting resolution")
        if self.degeneracy_tolerance <= 0.0:
            raise ValueError("degeneracy_tolerance must be positive")
        if not 0.0 < self.perturbative_ratio_max < 1.0:
            raise ValueError("perturbative_ratio_max must lie strictly between zero and one")
        for definition in self.cases:
            scales = [abs(definition.hz), abs(definition.J)]
            if definition.Jpm != 0.0:
                scales.append(abs(definition.Jpm))
            nonzero_scales = [scale for scale in scales if scale > 0.0]
            largest_ratio = max(
                (self.jx / scale for scale in nonzero_scales),
                default=0.0,
            )
            if largest_ratio > self.perturbative_ratio_max:
                raise ValueError(
                    f"{definition.case_id}: max collective-coupling ratio {largest_ratio:g} "
                    f"exceeds {self.perturbative_ratio_max:g}"
                )

    @classmethod
    def from_json(cls, path: Path) -> "CampaignConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            detector_sizes=tuple(int(value) for value in payload["detector_sizes"]),
            cases=tuple(CampaignCaseDefinition(**item) for item in payload["cases"]),
            evolution_time=float(payload.get("evolution_time", 1.0e6)),
            jx=float(payload.get("jx", 0.01)),
            hz0=float(payload.get("hz0", 0.0)),
            bins=int(payload.get("bins", 48)),
            max_bloch_points=int(payload.get("max_bloch_points", 6000)),
            seed=int(payload.get("seed", 44)),
            degeneracy_tolerance=float(payload.get("degeneracy_tolerance", 1.0e-12)),
            perturbative_ratio_max=float(payload.get("perturbative_ratio_max", 0.10)),
            gates=HeavyTailGates(**payload.get("gates", {})),
        )

    def perturbative_ratios(self, definition: CampaignCaseDefinition) -> dict[str, float]:
        ratios: dict[str, float] = {}
        if definition.hz != 0.0:
            ratios["Jx_over_abs_hz"] = self.jx / abs(definition.hz)
        if definition.J != 0.0:
            ratios["Jx_over_abs_J"] = self.jx / abs(definition.J)
        if definition.Jpm != 0.0:
            ratios["Jx_over_abs_Jpm"] = self.jx / abs(definition.Jpm)
        ratios["maximum_ratio"] = max(ratios.values(), default=0.0)
        return ratios

    @property
    def digest(self) -> str:
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]

    def simulation_case(self, detector_n: int, definition: CampaignCaseDefinition) -> AnisotropicCase:
        if detector_n not in self.detector_sizes:
            raise ValueError(f"N={detector_n} is not in this campaign")
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


def smoke_config(config: CampaignConfig) -> CampaignConfig:
    """Small, separately rooted end-to-end configuration."""

    nonising = next((case for case in config.cases if case.Jpm != 0.0), None)
    selected = list(config.cases[:3])
    if nonising is not None and nonising not in selected:
        selected.append(nonising)
    else:
        selected = list(config.cases[:4])
    return replace(
        config,
        detector_sizes=(4,),
        cases=tuple(selected),
        evolution_time=100.0,
        bins=24,
        max_bloch_points=256,
    )


@dataclass(frozen=True)
class ActivationCertificate:
    """Exact coupling-gap statement for one analytically certified family."""

    certificate_type: str
    proof_scope: str
    exact_active: bool
    exact_active_weight_fraction: float
    minimum_coupled_gap: float
    coupled_gap_values: tuple[float, ...]
    coupled_gap_weight_fractions: tuple[float, ...]
    finite_time_kernel_power_fraction: float
    criterion: str


class IsingActivationCertifier:
    """Prove the activation label without diagonalizing the detector."""

    _weights = np.asarray((0.25, 0.50, 0.25), dtype=float)

    def certify(
        self,
        definition: CampaignCaseDefinition,
        *,
        evolution_time: float,
        tolerance: float,
    ) -> ActivationCertificate:
        if definition.Jpm != 0.0:
            raise ValueError("analytic Ising certificate is valid only for Jpm=0")
        local_fields = np.asarray(
            (
                definition.hz - 2.0 * definition.J,
                definition.hz,
                definition.hz + 2.0 * definition.J,
            ),
            dtype=float,
        )
        gaps = 2.0 * np.abs(local_fields)
        resonant = gaps <= tolerance
        exact_fraction = float(np.sum(self._weights[resonant]))
        # np.sinc(x) = sin(pi*x)/(pi*x), so this is
        # |F_t(delta)|^2/t^2 = sinc^2(delta*t/(2*pi)).
        kernel = float(
            np.sum(self._weights * np.sinc(gaps * evolution_time / (2.0 * np.pi)) ** 2)
        )
        return ActivationCertificate(
            certificate_type="ising_local_flip",
            proof_scope="all detector sizes N>=3",
            exact_active=bool(np.any(resonant)),
            exact_active_weight_fraction=exact_fraction,
            minimum_coupled_gap=float(np.min(gaps)),
            coupled_gap_values=tuple(float(value) for value in gaps),
            coupled_gap_weight_fractions=tuple(float(value) for value in self._weights),
            finite_time_kernel_power_fraction=kernel,
            criterion="For N>=3 and Jpm=0: exact activation iff hz is one of {-2J, 0, +2J}.",
        )


class SU2ActivationCertifier:
    """Certify activation on the isotropic ``Jpm=2J`` exchange line."""

    def certify(
        self,
        definition: CampaignCaseDefinition,
        *,
        evolution_time: float,
        tolerance: float,
    ) -> ActivationCertificate:
        if definition.J <= 0.0 or not math.isclose(
            definition.Jpm, 2.0 * definition.J, rel_tol=0.0, abs_tol=1.0e-12
        ):
            raise ValueError("analytic SU(2) certificate requires J>0 and Jpm=2J")
        gap = 2.0 * abs(definition.hz)
        active = gap <= tolerance
        kernel = float(np.sinc(gap * evolution_time / (2.0 * np.pi)) ** 2)
        return ActivationCertificate(
            certificate_type="su2_total_spin",
            proof_scope="all detector sizes N>=2",
            exact_active=active,
            exact_active_weight_fraction=1.0 if active else 0.0,
            minimum_coupled_gap=gap,
            coupled_gap_values=(gap,),
            coupled_gap_weight_fractions=(1.0,),
            finite_time_kernel_power_fraction=kernel,
            criterion=(
                "For Jpm=2J, H_exchange is SU(2)-invariant and commutes with "
                "V=sum_i X_i; V changes total magnetization by one, so its "
                "nonzero matrix elements have gap 2|hz| and are exactly "
                "degenerate iff hz=0."
            ),
        )


class ActivationCertifier:
    """Dispatch exact analytic activation proofs by Hamiltonian family."""

    def __init__(self) -> None:
        self._certifiers = {
            "ising_local_flip": IsingActivationCertifier(),
            "su2_total_spin": SU2ActivationCertifier(),
        }

    def certify(
        self,
        definition: CampaignCaseDefinition,
        *,
        evolution_time: float,
        tolerance: float,
    ) -> ActivationCertificate:
        return self._certifiers[definition.activation_model].certify(
            definition,
            evolution_time=evolution_time,
            tolerance=tolerance,
        )


class CampaignRepository:
    """Atomic persistence for named cases and per-size checkpoints."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.spectra = AnisotropicRepository(self.root)

    def metrics_path(self, detector_n: int, case_id: str) -> Path:
        return self.root / "campaign_metrics" / f"N{detector_n:02d}" / case_id / "metrics.json"

    def figure_path(self, detector_n: int, case_id: str) -> Path:
        return self.root / "figures" / f"N{detector_n:02d}" / case_id / "blue_red.png"

    def status_path(self, detector_n: int, name: str) -> Path:
        return self.root / "status" / f"N{detector_n:02d}" / name

    def aggregate_root(self, detector_n: int) -> Path:
        return self.root / "aggregates" / f"N{detector_n:02d}"

    def cross_n_aggregation_lock(self) -> Path:
        return self.root / "status" / "aggregate_all.lock"

    def save_metrics(self, detector_n: int, case_id: str, payload: dict[str, Any]) -> Path:
        return _atomic_json(self.metrics_path(detector_n, case_id), payload)

    def load_metrics(self, detector_n: int, case_id: str) -> dict[str, Any]:
        return json.loads(self.metrics_path(detector_n, case_id).read_text(encoding="utf-8"))


class CampaignAggregator:
    """Create the logical truth table after each N and across all N."""

    _csv_fields = (
        "detector_n",
        "case_id",
        "role",
        "hz",
        "J",
        "Jpm",
        "activation_model",
        "certificate_type",
        "proof_scope",
        "Jx_over_abs_hz",
        "Jx_over_abs_J",
        "Jx_over_abs_Jpm",
        "maximum_perturbative_ratio",
        "exact_active",
        "exact_active_weight_fraction",
        "minimum_coupled_gap",
        "finite_time_kernel_power_fraction",
        "theta_power_law_alpha",
        "theta_power_law_js",
        "theta_power_law_log10_span",
        "angular_bin_coverage",
        "radius_atomic_fraction",
        "S_wrapped_heavy",
        "preferred_wrapped_model",
        "heavy_primary",
        "heavy_robust",
        "logical_quadrant_primary",
        "logical_quadrant_robust",
        "raw_path",
        "figure_path",
    )

    def __init__(self, repository: CampaignRepository) -> None:
        self.repository = repository

    @staticmethod
    def _quadrant(active: bool, heavy: bool) -> str:
        return f"activation_{'yes' if active else 'no'}__heavy_{'yes' if heavy else 'no'}"

    def _flat_row(self, payload: dict[str, Any]) -> dict[str, Any]:
        definition = payload["definition"]
        certificate = payload["activation_certificate"]
        metrics = payload["spectrum_metrics"]
        active = bool(certificate["exact_active"])
        primary = bool(payload["heavy_primary"])
        robust = bool(payload["heavy_robust"])
        return {
            "detector_n": int(metrics["detector_n"]),
            "case_id": definition["case_id"],
            "role": definition["role"],
            "hz": definition["hz"],
            "J": definition["J"],
            "Jpm": definition["Jpm"],
            "activation_model": definition["activation_model"],
            "certificate_type": certificate["certificate_type"],
            "proof_scope": certificate["proof_scope"],
            "Jx_over_abs_hz": payload["perturbative_ratios"].get("Jx_over_abs_hz", ""),
            "Jx_over_abs_J": payload["perturbative_ratios"].get("Jx_over_abs_J", ""),
            "Jx_over_abs_Jpm": payload["perturbative_ratios"].get(
                "Jx_over_abs_Jpm", ""
            ),
            "maximum_perturbative_ratio": payload["perturbative_ratios"][
                "maximum_ratio"
            ],
            "exact_active": active,
            "exact_active_weight_fraction": certificate["exact_active_weight_fraction"],
            "minimum_coupled_gap": certificate["minimum_coupled_gap"],
            "finite_time_kernel_power_fraction": certificate[
                "finite_time_kernel_power_fraction"
            ],
            "theta_power_law_alpha": metrics["theta_power_law_alpha"],
            "theta_power_law_js": metrics["theta_power_law_js"],
            "theta_power_law_log10_span": metrics["theta_power_law_log10_span"],
            "angular_bin_coverage": metrics["angular_bin_coverage"],
            "radius_atomic_fraction": metrics["radius_atomic_fraction"],
            "S_wrapped_heavy": metrics["S_wrapped_heavy"],
            "preferred_wrapped_model": metrics["preferred_wrapped_model"],
            "heavy_primary": primary,
            "heavy_robust": robust,
            "logical_quadrant_primary": self._quadrant(active, primary),
            "logical_quadrant_robust": self._quadrant(active, robust),
            "raw_path": payload["raw_path"],
            "figure_path": payload["figure_path"],
        }

    def aggregate_n(self, config: CampaignConfig, detector_n: int) -> Path:
        rows = [
            self._flat_row(self.repository.load_metrics(detector_n, definition.case_id))
            for definition in config.cases
        ]
        rows.sort(key=lambda row: str(row["case_id"]))
        root = self.repository.aggregate_root(detector_n)
        csv_path = _atomic_csv(root / f"case_metrics_N{detector_n:02d}.csv", rows, self._csv_fields)
        truth: dict[str, Any] = {
            "detector_n": detector_n,
            "config_digest": config.digest,
            "case_count": len(rows),
            "primary_counts": self._truth_counts(rows, "heavy_primary"),
            "robust_counts": self._truth_counts(rows, "heavy_robust"),
            "sufficiency_counterexamples_primary": [
                row["case_id"] for row in rows if row["exact_active"] and not row["heavy_primary"]
            ],
            "necessity_counterexamples_primary": [
                row["case_id"] for row in rows if not row["exact_active"] and row["heavy_primary"]
            ],
            "sufficiency_counterexamples_robust": [
                row["case_id"] for row in rows if row["exact_active"] and not row["heavy_robust"]
            ],
            "necessity_counterexamples_robust": [
                row["case_id"] for row in rows if not row["exact_active"] and row["heavy_robust"]
            ],
            "metrics_csv": str(csv_path),
        }
        figure_path = root / f"activation_vs_heavy_N{detector_n:02d}.png"
        self._plot_truth_tables(rows, detector_n, figure_path)
        truth["figure"] = str(figure_path)
        return _atomic_json(root / "truth_table.json", truth)

    @staticmethod
    def _truth_counts(rows: Sequence[dict[str, Any]], field: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            key = CampaignAggregator._quadrant(bool(row["exact_active"]), bool(row[field]))
            counts[key] = counts.get(key, 0) + 1
        return counts

    @staticmethod
    def _plot_truth_tables(rows: Sequence[dict[str, Any]], detector_n: int, path: Path) -> None:
        figure, axes = plt.subplots(1, 2, figsize=(9.4, 4.1), dpi=180, constrained_layout=True)
        for axis, field, title in zip(
            axes,
            ("heavy_primary", "heavy_robust"),
            ("project heavy-tail gate", "robust heavy-tail gate"),
            strict=True,
        ):
            matrix = np.zeros((2, 2), dtype=int)
            for row in rows:
                matrix[int(bool(row["exact_active"])), int(bool(row[field]))] += 1
            image = axis.imshow(matrix, origin="lower", cmap="Blues", vmin=0, vmax=max(1, int(np.max(matrix))))
            axis.set_xticks((0, 1), ("no", "yes"))
            axis.set_yticks((0, 1), ("no", "yes"))
            axis.set_xlabel("wrapped heavy-tailed")
            axis.set_ylabel(r"exact $V_{ab}$ activation")
            axis.set_title(title)
            for y in range(2):
                for x in range(2):
                    axis.text(x, y, str(matrix[y, x]), ha="center", va="center", fontweight="bold")
            figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04, label="case count")
        figure.suptitle(rf"Necessity and sufficiency truth tables, $N={detector_n}$")
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, bbox_inches="tight", pad_inches=0.08)
        plt.close(figure)

    def aggregate_all(self, config: CampaignConfig, *, allow_partial: bool = False) -> Path:
        rows: list[dict[str, Any]] = []
        missing: list[str] = []
        for detector_n in config.detector_sizes:
            for definition in config.cases:
                path = self.repository.metrics_path(detector_n, definition.case_id)
                if not path.is_file():
                    missing.append(f"N{detector_n:02d}/{definition.case_id}")
                    continue
                rows.append(self._flat_row(self.repository.load_metrics(detector_n, definition.case_id)))
        if missing and not allow_partial:
            raise RuntimeError(f"missing {len(missing)} case metrics; first: {', '.join(missing[:5])}")
        root = self.repository.root / "aggregates" / "all_N"
        all_csv = _atomic_csv(root / "all_case_metrics.csv", rows, self._csv_fields)
        persistence_rows: list[dict[str, Any]] = []
        for definition in config.cases:
            selected = sorted(
                (row for row in rows if row["case_id"] == definition.case_id),
                key=lambda row: int(row["detector_n"]),
            )
            active = bool(selected[0]["exact_active"]) if selected else False
            persistence_rows.append(
                {
                    "case_id": definition.case_id,
                    "role": definition.role,
                    "exact_active": active,
                    "sizes_completed": len(selected),
                    "heavy_primary_sizes": sum(bool(row["heavy_primary"]) for row in selected),
                    "heavy_robust_sizes": sum(bool(row["heavy_robust"]) for row in selected),
                    "primary_sufficiency_counterexample_sizes": sum(
                        active and not bool(row["heavy_primary"]) for row in selected
                    ),
                    "primary_necessity_counterexample_sizes": sum(
                        (not active) and bool(row["heavy_primary"]) for row in selected
                    ),
                    "robust_sufficiency_counterexample_sizes": sum(
                        active and not bool(row["heavy_robust"]) for row in selected
                    ),
                    "robust_necessity_counterexample_sizes": sum(
                        (not active) and bool(row["heavy_robust"]) for row in selected
                    ),
                }
            )
        persistence_fields = tuple(persistence_rows[0]) if persistence_rows else (
            "case_id",
            "role",
            "exact_active",
            "sizes_completed",
            "heavy_primary_sizes",
            "heavy_robust_sizes",
            "primary_sufficiency_counterexample_sizes",
            "primary_necessity_counterexample_sizes",
            "robust_sufficiency_counterexample_sizes",
            "robust_necessity_counterexample_sizes",
        )
        persistence_csv = _atomic_csv(
            root / "case_persistence.csv", persistence_rows, persistence_fields
        )
        figure_path = root / "heavy_tail_persistence.png"
        self._plot_persistence(config, rows, figure_path)
        summary = {
            "config_digest": config.digest,
            "expected_rows": len(config.detector_sizes) * len(config.cases),
            "completed_rows": len(rows),
            "missing": missing,
            "complete": not missing,
            "all_case_metrics_csv": str(all_csv),
            "case_persistence_csv": str(persistence_csv),
            "figure": str(figure_path),
            "universal_iff_status": (
                "falsified_both_directions"
                if any(row["primary_sufficiency_counterexample_sizes"] for row in persistence_rows)
                and any(row["primary_necessity_counterexample_sizes"] for row in persistence_rows)
                else "not_yet_falsified_both_directions_by_primary_gate"
            ),
        }
        return _atomic_json(root / "summary.json", summary)

    def aggregate_all_locked(
        self,
        config: CampaignConfig,
        *,
        allow_partial: bool = False,
    ) -> Path:
        """Serialize the shared synthesis when PBS array elements finish together."""

        with AtomicFileLock(self.repository.cross_n_aggregation_lock()):
            return self.aggregate_all(config, allow_partial=allow_partial)

    @staticmethod
    def _plot_persistence(
        config: CampaignConfig,
        rows: Sequence[dict[str, Any]],
        path: Path,
    ) -> None:
        lookup = {
            (str(row["case_id"]), int(row["detector_n"])): row
            for row in rows
        }
        figure, axes = plt.subplots(1, 2, figsize=(11.5, 5.4), dpi=180, constrained_layout=True)
        for axis, field, title in zip(
            axes,
            ("heavy_primary", "heavy_robust"),
            ("project gate", "robust gate"),
            strict=True,
        ):
            matrix = np.full((len(config.cases), len(config.detector_sizes)), np.nan)
            for y, definition in enumerate(config.cases):
                for x, detector_n in enumerate(config.detector_sizes):
                    row = lookup.get((definition.case_id, detector_n))
                    if row is not None:
                        matrix[y, x] = float(bool(row[field]))
            axis.imshow(
                matrix,
                origin="upper",
                aspect="auto",
                cmap=plt.get_cmap("RdYlGn").with_extremes(bad="#d7d7d7"),
                vmin=0.0,
                vmax=1.0,
            )
            axis.set_xticks(range(len(config.detector_sizes)), config.detector_sizes)
            axis.set_yticks(
                range(len(config.cases)),
                [
                    f"{definition.case_id}  [A={int(ActivationCertifier().certify(definition, evolution_time=config.evolution_time, tolerance=config.degeneracy_tolerance).exact_active)}]"
                    for definition in config.cases
                ],
                fontsize=8,
            )
            axis.set_xlabel("detector size N")
            axis.set_title(title)
        figure.suptitle("Heavy-tail classification across N (red=no, green=yes; A=exact activation)")
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, bbox_inches="tight", pad_inches=0.08)
        plt.close(figure)


class DegeneracyHeavyTailCampaignService:
    """Orchestrate independent cases with one parent writer."""

    def __init__(
        self,
        repository: CampaignRepository,
        backend: CaseBackend | None = None,
        plotter: DiagnosticPlotter | None = None,
        certifier: ActivationCertifier | None = None,
    ) -> None:
        self.repository = repository
        self.backend = backend or QuSpinAnisotropicBackend()
        self.plotter = plotter or BlueRedDiagnosticPlotter()
        self.certifier = certifier or ActivationCertifier()

    @staticmethod
    def recommended_workers(detector_n: int) -> int:
        if detector_n <= 13:
            return 4
        if detector_n <= 15:
            return 2
        return 1

    def run_n(
        self,
        config: CampaignConfig,
        detector_n: int,
        *,
        workers: int = 0,
        force: bool = False,
    ) -> Path:
        if detector_n not in config.detector_sizes:
            raise ValueError(f"N={detector_n} is not present in the configuration")
        effective_workers = self.recommended_workers(detector_n) if workers <= 0 else int(workers)
        if effective_workers < 1:
            raise ValueError("workers must be positive or zero")
        calculator = AngularDiagnosticCalculator(config.bins)
        spectrum_calculator = SpectrumMetricCalculator(config.bins)
        running_path = self.repository.status_path(detector_n, "RUNNING.json")
        done_path = self.repository.status_path(detector_n, "DONE.json")
        failed_path = self.repository.status_path(detector_n, "FAILED.json")
        failed_path.unlink(missing_ok=True)
        completed: list[dict[str, Any]] = []
        started = time.time()

        def checkpoint() -> None:
            _atomic_json(
                running_path,
                {
                    "detector_n": detector_n,
                    "config_digest": config.digest,
                    "workers": effective_workers,
                    "expected_cases": len(config.cases),
                    "completed_cases": len(completed),
                    "completed": completed,
                    "updated_at": _timestamp(),
                },
            )

        def persist(
            definition: CampaignCaseDefinition,
            case: AnisotropicCase,
            sample: AnisotropicSample,
            source: str,
        ) -> None:
            raw_path = self.repository.spectra.save_sample(case, sample)
            self.repository.spectra.save_metadata(case, sample, config.digest)
            angular = calculator.calculate(sample)
            figure_path = self.repository.figure_path(detector_n, definition.case_id)
            if force or not figure_path.is_file():
                self.plotter.plot(case, sample, angular, figure_path, config.max_bloch_points)
            spectrum_metrics = spectrum_calculator.calculate(raw_path)
            certificate = self.certifier.certify(
                definition,
                evolution_time=config.evolution_time,
                tolerance=config.degeneracy_tolerance,
            )
            payload = {
                "definition": asdict(definition),
                "activation_certificate": asdict(certificate),
                "spectrum_metrics": asdict(spectrum_metrics),
                "heavy_primary": config.gates.primary(spectrum_metrics),
                "heavy_robust": config.gates.robust(spectrum_metrics),
                "heavy_tail_gates": asdict(config.gates),
                "perturbative_ratios": config.perturbative_ratios(definition),
                "perturbative_ratio_max": config.perturbative_ratio_max,
                "diagnostic_figure_contents": (
                    "row 1: blue P(theta) and red P(pi-theta) histograms; "
                    "row 2: connected R(theta) and Born cos^2(theta/2); "
                    "row 3: corresponding blue/red Bloch-sphere point distributions"
                ),
                "raw_path": str(raw_path),
                "figure_path": str(figure_path),
                "source": source,
                "worker_name": sample.worker_name,
                "worker_pid": sample.worker_pid,
                "calculation_started": sample.calculation_started,
                "calculation_finished": sample.calculation_finished,
                "saved_at": _timestamp(),
                "config_digest": config.digest,
            }
            metrics_path = self.repository.save_metrics(detector_n, definition.case_id, payload)
            completed.append(
                {
                    "case_id": definition.case_id,
                    "source": source,
                    "worker_name": sample.worker_name,
                    "worker_pid": sample.worker_pid,
                    "metrics": str(metrics_path),
                    "raw": str(raw_path),
                    "figure": str(figure_path),
                    "exact_active": certificate.exact_active,
                    "heavy_primary": payload["heavy_primary"],
                    "heavy_robust": payload["heavy_robust"],
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
        pending: list[tuple[CampaignCaseDefinition, AnisotropicCase]] = []
        try:
            for definition in config.cases:
                case = config.simulation_case(detector_n, definition)
                if not force and self.repository.spectra.has_sample(case):
                    sample = self.repository.spectra.load_sample(case)
                    print(
                        f"[{_timestamp()}] worker=parent pid={os.getpid()} event=REUSE "
                        f"N={detector_n} case={definition.case_id}",
                        flush=True,
                    )
                    persist(definition, case, sample, "checkpoint")
                else:
                    pending.append((definition, case))

            if effective_workers == 1 or len(pending) <= 1:
                for definition, case in pending:
                    persist(definition, case, self.backend.compute(case), "computed")
            else:
                pool_size = min(effective_workers, len(pending))
                print(
                    f"[{_timestamp()}] event=SUBMIT N={detector_n} cases={len(pending)} "
                    f"process_workers={pool_size} parallel_axis=Hamiltonian-case",
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
        except Exception as exc:
            _atomic_json(
                failed_path,
                {
                    "detector_n": detector_n,
                    "config_digest": config.digest,
                    "completed": completed,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "failed_at": _timestamp(),
                },
            )
            raise

        completed.sort(key=lambda item: str(item["case_id"]))
        try:
            aggregator = CampaignAggregator(self.repository)
            aggregate = aggregator.aggregate_n(config, detector_n)
            cross_n_aggregate = aggregator.aggregate_all_locked(
                config,
                allow_partial=True,
            )
            _atomic_json(
                done_path,
                {
                    "detector_n": detector_n,
                    "config_digest": config.digest,
                    "workers": effective_workers,
                    "completed_cases": len(completed),
                    "completed": completed,
                    "per_n_aggregate": str(aggregate),
                    "cross_n_aggregate": str(cross_n_aggregate),
                    "checkpoint_contract": (
                        "raw spectrum, metadata, metrics, and blue-red diagnostic are "
                        "saved after every case; per-N and cross-N aggregates are saved "
                        "before this DONE manifest"
                    ),
                    "elapsed_seconds": time.time() - started,
                    "finished_at": _timestamp(),
                },
            )
        except Exception as exc:
            _atomic_json(
                failed_path,
                {
                    "detector_n": detector_n,
                    "config_digest": config.digest,
                    "completed": completed,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "stage": "per-N/cross-N aggregation",
                    "failed_at": _timestamp(),
                },
            )
            raise
        running_path.unlink(missing_ok=True)
        return done_path


def describe_config(config: CampaignConfig) -> dict[str, Any]:
    certifier = ActivationCertifier()
    return {
        "config_digest": config.digest,
        "detector_sizes": list(config.detector_sizes),
        "case_count_per_N": len(config.cases),
        "total_simulations": len(config.detector_sizes) * len(config.cases),
        "evolution_time": config.evolution_time,
        "collective_Jx": config.jx,
        "edge_coupling_formula": "Jx/sqrt(N)",
        "perturbative_ratio_max": config.perturbative_ratio_max,
        "diagnostic_figure_contents": (
            "P(theta)/P(pi-theta) blue-red histograms, connected R(theta) versus Born, "
            "and blue-red Bloch-sphere points"
        ),
        "cases": [
            {
                **asdict(definition),
                "perturbative_ratios": config.perturbative_ratios(definition),
                "activation_certificate": asdict(
                    certifier.certify(
                        definition,
                        evolution_time=config.evolution_time,
                        tolerance=config.degeneracy_tolerance,
                    )
                ),
            }
            for definition in config.cases
        ],
        "recommended_workers": {
            str(detector_n): DegeneracyHeavyTailCampaignService.recommended_workers(detector_n)
            for detector_n in config.detector_sizes
        },
    }


__all__ = [
    "ActivationCertificate",
    "ActivationCertifier",
    "CampaignAggregator",
    "CampaignCaseDefinition",
    "CampaignConfig",
    "CampaignRepository",
    "DegeneracyHeavyTailCampaignService",
    "HeavyTailGates",
    "IsingActivationCertifier",
    "SU2ActivationCertifier",
    "describe_config",
    "smoke_config",
]
