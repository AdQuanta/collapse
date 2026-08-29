"""Post-process the completed anisotropic ``J``--``Jpm`` Zeus campaign.

The simulation layer deliberately saves raw spectra and only a compact Born
diagnostic.  This module adds a second, independent analysis layer.  It
reconstructs ``theta = 2 arctan(|lambda|)`` from every saved spectrum, fits a
resolution-regularized periodic power law directly to ``P(theta)``, and
creates parameter-plane heatmaps without mutating the simulation results.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import spearmanr

from core.anisotropic_sweep import (
    AngularDiagnosticCalculator,
    AnisotropicCase,
    AnisotropicRepository,
    AnisotropicSample,
    AnisotropicSweepConfig,
)
from core.born import diagnostics_from_radii
from core.distribution_fit import FoldedDistributionFit, fit_folded_circular_models
from core.detector_resonance import DenseRingDetectorBuilder, DetectorSpec


@dataclass(frozen=True)
class CampaignCompleteness:
    """File-level completeness evidence for one detector size."""

    detector_n: int
    expected_cases: int
    raw_spectra: int
    metadata_files: int
    metrics_files: int
    diagnostic_figures: int
    done_marker: bool
    aggregate_manifest: bool
    aggregate_complete: bool

    @property
    def complete(self) -> bool:
        expected = self.expected_cases
        return (
            self.raw_spectra == expected
            and self.metadata_files == expected
            and self.metrics_files == expected
            and self.diagnostic_figures == expected
            and self.done_marker
            and self.aggregate_manifest
            and self.aggregate_complete
        )


@dataclass(frozen=True)
class SpectrumMetrics:
    """Scalar diagnostics derived from one raw spectrum."""

    detector_n: int
    total_qubits: int
    hz: float
    J: float
    Jpm: float
    evolution_time: float
    Jx: float
    hz0: float
    sample_count: int
    theta_reconstruction_max_error: float
    S_born: float
    born_rmse: float
    angular_bin_coverage: float
    phi_harmonic_2: float
    wrapped_gaussian_sigma: float
    wrapped_gaussian_l1: float
    wrapped_gaussian_js: float
    wrapped_cauchy_gamma: float
    wrapped_cauchy_l1: float
    wrapped_cauchy_js: float
    cauchy_log_likelihood_advantage_per_sample: float
    cauchy_log_likelihood_advantage_total: float
    preferred_wrapped_model: str
    S_wrapped_heavy: float
    theta_power_law_alpha: float
    theta_power_law_js: float
    theta_power_law_log_likelihood_per_sample: float
    theta_power_law_log10_span: float
    radius_q50: float
    radius_q95: float
    radius_q99: float
    radius_q99_over_q50: float
    radius_atomic_fraction: float
    tail_density_exponent: float
    tail_survival_exponent: float
    reciprocity_error: float
    max_radius: float
    source_npz: str


@dataclass(frozen=True)
class DetectorDegeneracyMetrics:
    """Basis-invariant detector degeneracy diagnostics at one grid point."""

    detector_n: int
    hz: float
    J: float
    Jpm: float
    distinct_energies: int
    degenerate_subspaces: int
    maximum_multiplicity: int
    detector_degenerate_state_fraction: float
    active_zero_gap_weight_fraction: float
    nearest_active_gap: float
    total_active_weight: float


@dataclass(frozen=True)
class PeriodicPowerLawFit:
    r"""Maximum-likelihood fit of ``P(theta) ~ d(theta, 0)^(-alpha)``.

    ``d`` is the shortest distance modulo ``2*pi``.  The distance is floored
    at half a histogram bin, which is the finest scale resolved by the data
    and keeps the discretized model normalizable for every fitted exponent.
    """

    alpha: float
    jensen_shannon_divergence: float
    log_likelihood_per_sample: float
    occupied_bin_fraction: float
    log10_distance_span: float


def fit_periodic_power_law(
    theta: np.ndarray,
    edges: np.ndarray,
    *,
    alpha_bounds: tuple[float, float] = (0.0, 8.0),
) -> PeriodicPowerLawFit:
    r"""Fit ``P(theta) proportional to d_Delta(theta)^(-alpha)``.

    The likelihood is multinomial over the supplied bins.  For bin center
    ``theta_b``, ``d_Delta=max(min_k|theta_b-2*pi*k|, Delta/2)`` and the model
    probability is proportional to ``d_Delta**(-alpha) * bin_width``.  This
    makes the modulo-``2*pi`` convention and the finite angular resolution
    explicit instead of hiding them in a wrapped-Cauchy proxy.
    """

    values = np.asarray(theta, dtype=float)
    values = values[np.isfinite(values)]
    bin_edges = np.asarray(edges, dtype=float)
    if values.size == 0:
        raise ValueError("theta must contain at least one finite value")
    if bin_edges.ndim != 1 or bin_edges.size < 5 or np.any(np.diff(bin_edges) <= 0.0):
        raise ValueError("edges must be a strictly increasing one-dimensional array")
    lower, upper = map(float, alpha_bounds)
    if lower < 0.0 or upper <= lower:
        raise ValueError("alpha_bounds must satisfy 0 <= lower < upper")

    counts, _ = np.histogram(values, bins=bin_edges)
    widths = np.diff(bin_edges)
    centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    phase = np.mod(centers, 2.0 * np.pi)
    circular_distance = np.minimum(phase, 2.0 * np.pi - phase)
    resolved_distance = np.maximum(circular_distance, 0.5 * float(np.min(widths)))
    log_distance = np.log(resolved_distance)
    log_width = np.log(widths)

    def probabilities(alpha: float) -> np.ndarray:
        log_weight = log_width - float(alpha) * log_distance
        log_weight -= float(np.max(log_weight))
        weights = np.exp(log_weight)
        return weights / float(np.sum(weights))

    def negative_log_likelihood(alpha: float) -> float:
        model = probabilities(alpha)
        return float(-np.dot(counts, np.log(np.maximum(model, np.finfo(float).tiny))))

    result = minimize_scalar(
        negative_log_likelihood,
        bounds=(lower, upper),
        method="bounded",
        options={"xatol": 1.0e-8},
    )
    alpha = float(result.x)
    model = probabilities(alpha)
    empirical = counts.astype(float) / float(np.sum(counts))
    midpoint = 0.5 * (empirical + model)
    positive_empirical = empirical > 0.0
    js = 0.5 * float(np.sum(empirical[positive_empirical] * np.log(empirical[positive_empirical] / midpoint[positive_empirical])))
    js += 0.5 * float(np.sum(model * np.log(model / midpoint)))
    occupied = counts > 0
    if np.count_nonzero(occupied) >= 2:
        occupied_distances = resolved_distance[occupied]
        span = float(np.log10(np.max(occupied_distances) / np.min(occupied_distances)))
    else:
        span = 0.0
    return PeriodicPowerLawFit(
        alpha=alpha,
        jensen_shannon_divergence=js,
        log_likelihood_per_sample=float(-result.fun / np.sum(counts)),
        occupied_bin_fraction=float(np.mean(occupied)),
        log10_distance_span=span,
    )


class DetectorDegeneracyCalculator:
    """Calculate projector-invariant zero-gap coupling weight efficiently."""

    def __init__(
        self,
        degeneracy_tolerance: float = 1.0e-9,
        relative_weight_tolerance: float = 1.0e-12,
    ):
        self.degeneracy_tolerance = float(degeneracy_tolerance)
        self.relative_weight_tolerance = float(relative_weight_tolerance)
        self.builder = DenseRingDetectorBuilder()

    def calculate(self, spec: DetectorSpec) -> DetectorDegeneracyMetrics:
        operators = self.builder.build(spec)
        energies, vectors = np.linalg.eigh(operators.hamiltonian)
        transformed = vectors.conj().T @ operators.coupling @ vectors
        weights = np.abs(transformed) ** 2
        total_weight = float(np.sum(weights))
        gaps = energies[:, None] - energies[None, :]
        zero_gap = np.abs(gaps) <= self.degeneracy_tolerance
        active_fraction = float(np.sum(weights[zero_gap]) / total_weight) if total_weight else 0.0
        threshold = self.relative_weight_tolerance * max(total_weight, 1.0)
        active = weights > threshold
        nearest = float(np.min(np.abs(gaps[active]))) if np.any(active) else math.inf

        multiplicities: list[int] = []
        start = 0
        while start < energies.size:
            stop = start + 1
            while stop < energies.size and abs(float(energies[stop] - energies[start])) <= self.degeneracy_tolerance:
                stop += 1
            multiplicities.append(stop - start)
            start = stop
        degenerate_states = sum(value for value in multiplicities if value > 1)
        return DetectorDegeneracyMetrics(
            detector_n=spec.detector_n,
            hz=spec.hz,
            J=spec.j,
            Jpm=spec.jpm,
            distinct_energies=len(multiplicities),
            degenerate_subspaces=sum(value > 1 for value in multiplicities),
            maximum_multiplicity=max(multiplicities),
            detector_degenerate_state_fraction=float(degenerate_states / energies.size),
            active_zero_gap_weight_fraction=active_fraction,
            nearest_active_gap=nearest,
            total_active_weight=total_weight,
        )


def wrapped_heavy_score(fit: FoldedDistributionFit) -> float:
    r"""Return a bounded wrapped-heavy-tail score in ``[0, 1]``.

    The absolute-fit factor is normalized Jensen--Shannon closeness to a
    folded wrapped Cauchy, ``1 - JS/log(2)``.  It is multiplied by the signed
    likelihood evidence for Cauchy over Gaussian, mapped to ``[0,1]`` as

    ``max(0, tanh((log L_C - log L_G)/2))``.

    Thus a broad nearly uniform distribution, for which both fitted families
    are indistinguishable, is not automatically labeled heavy-tailed.
    """

    closeness = float(np.clip(1.0 - fit.wrapped_cauchy_js / math.log(2.0), 0.0, 1.0))
    total_advantage = fit.cauchy_log_likelihood_advantage_per_sample * fit.sample_count
    evidence = math.tanh(max(0.0, float(total_advantage)) / 2.0)
    return float(closeness * evidence)


class CampaignInspector:
    """Inspect campaign outputs without loading the spectra."""

    def __init__(self, repository: AnisotropicRepository, config: AnisotropicSweepConfig):
        self.repository = repository
        self.config = config

    def inspect_n(self, detector_n: int) -> CampaignCompleteness:
        expected = len(self.config.hz_values) * len(self.config.j_values) * len(self.config.jpm_values)
        root = self.repository.root
        raw_root = root / "raw" / f"N{detector_n:02d}"
        metrics_root = root / "metrics" / f"N{detector_n:02d}"
        figures_root = root / "figures" / f"N{detector_n:02d}"
        manifest_path = root / "aggregates" / f"N{detector_n:02d}" / "manifest.json"
        aggregate_complete = False
        if manifest_path.is_file():
            try:
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                aggregate_complete = bool(payload.get("complete")) and int(payload.get("completed_cases", -1)) == expected
            except (OSError, ValueError, TypeError):
                aggregate_complete = False
        return CampaignCompleteness(
            detector_n=detector_n,
            expected_cases=expected,
            raw_spectra=sum(1 for _ in raw_root.rglob("spectrum_t*.npz")) if raw_root.is_dir() else 0,
            metadata_files=sum(1 for _ in raw_root.rglob("metadata.json")) if raw_root.is_dir() else 0,
            metrics_files=sum(1 for _ in metrics_root.rglob("diagnostics.json")) if metrics_root.is_dir() else 0,
            diagnostic_figures=sum(1 for _ in figures_root.rglob("blue_red_t*.png")) if figures_root.is_dir() else 0,
            done_marker=(root / "status" / f"N{detector_n:02d}" / "DONE.json").is_file(),
            aggregate_manifest=manifest_path.is_file(),
            aggregate_complete=aggregate_complete,
        )

    def inspect_all(self) -> list[CampaignCompleteness]:
        return [self.inspect_n(detector_n) for detector_n in self.config.detector_sizes]


class SpectrumMetricCalculator:
    """Compute Born, circular-fit, and radial diagnostics from one NPZ file."""

    def __init__(self, bins: int = 48):
        if bins < 4:
            raise ValueError("bins must be at least 4")
        self.bins = bins
        self.edges = np.linspace(0.0, np.pi, bins + 1)
        self.angular = AngularDiagnosticCalculator(bins)

    def calculate(self, path: Path) -> SpectrumMetrics:
        with np.load(path) as raw:
            eigenvalues = np.asarray(raw["eigenvalues"], dtype=np.complex128)
            saved_theta = np.asarray(raw["theta"], dtype=float)
            detector_n = int(raw["detector_n"])
            hz = float(raw["hz"])
            j = float(raw["J"])
            jpm = float(raw["Jpm"])
            evolution_time = float(raw["t"])
            jx = float(raw["Jx"])
            hz0 = float(raw["hz0"])

        finite = np.isfinite(eigenvalues.real) & np.isfinite(eigenvalues.imag)
        values = eigenvalues[finite]
        theta = 2.0 * np.arctan(np.abs(values))
        saved_finite = saved_theta[np.isfinite(saved_theta)]
        reconstruction_error = (
            float(np.max(np.abs(theta - saved_finite)))
            if theta.size == saved_finite.size and theta.size
            else math.inf
        )
        sample = AnisotropicSample(
            eigenvalues=values,
            theta=theta,
            sector_count=0,
            diagonalization_seconds=math.nan,
            analysis_seconds=math.nan,
        )
        angular = self.angular.calculate(sample)
        fit = fit_folded_circular_models(theta, self.edges)
        power_law = fit_periodic_power_law(theta, self.edges)
        radii = np.abs(values)
        born = diagnostics_from_radii(radii)
        q50, q95, q99 = np.quantile(radii, (0.50, 0.95, 0.99))
        rounded = np.round(radii, decimals=12)
        _, multiplicities = np.unique(rounded, return_counts=True)
        per_sample_advantage = fit.cauchy_log_likelihood_advantage_per_sample
        return SpectrumMetrics(
            detector_n=detector_n,
            total_qubits=detector_n + 1,
            hz=hz,
            J=j,
            Jpm=jpm,
            evolution_time=evolution_time,
            Jx=jx,
            hz0=hz0,
            sample_count=int(radii.size),
            theta_reconstruction_max_error=reconstruction_error,
            S_born=angular.born_score,
            born_rmse=angular.born_rmse,
            angular_bin_coverage=angular.coverage,
            phi_harmonic_2=angular.phi_harmonic_2,
            wrapped_gaussian_sigma=fit.wrapped_gaussian_sigma,
            wrapped_gaussian_l1=fit.wrapped_gaussian_l1,
            wrapped_gaussian_js=fit.wrapped_gaussian_js,
            wrapped_cauchy_gamma=fit.wrapped_cauchy_gamma,
            wrapped_cauchy_l1=fit.wrapped_cauchy_l1,
            wrapped_cauchy_js=fit.wrapped_cauchy_js,
            cauchy_log_likelihood_advantage_per_sample=per_sample_advantage,
            cauchy_log_likelihood_advantage_total=per_sample_advantage * fit.sample_count,
            preferred_wrapped_model=fit.preferred_model,
            S_wrapped_heavy=wrapped_heavy_score(fit),
            theta_power_law_alpha=power_law.alpha,
            theta_power_law_js=power_law.jensen_shannon_divergence,
            theta_power_law_log_likelihood_per_sample=power_law.log_likelihood_per_sample,
            theta_power_law_log10_span=power_law.log10_distance_span,
            radius_q50=float(q50),
            radius_q95=float(q95),
            radius_q99=float(q99),
            radius_q99_over_q50=float(q99 / q50) if q50 > 0.0 else math.inf,
            radius_atomic_fraction=float(np.max(multiplicities) / radii.size),
            tail_density_exponent=float(born.tail_density_exponent),
            tail_survival_exponent=float(born.tail_survival_exponent),
            reciprocity_error=float(born.reciprocity_error),
            max_radius=float(born.max_radius),
            source_npz=str(path),
        )


class MetricTableRepository:
    """Persist scalar analysis rows and reload them deterministically."""

    @staticmethod
    def write(path: Path, rows: Sequence[SpectrumMetrics]) -> Path:
        if not rows:
            raise ValueError("cannot write an empty metrics table")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        fields = list(asdict(rows[0]))
        with temporary.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow(asdict(row))
        temporary.replace(path)
        return path

    @staticmethod
    def read(path: Path) -> list[dict[str, str]]:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def write_dicts(path: Path, rows: Sequence[dict[str, Any]]) -> Path:
        if not rows:
            raise ValueError("cannot write an empty table")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
        return path


class WrappedHeavyHeatmapPlotter:
    """Render clean red-to-green J--Jpm maps with no cell text or markers."""

    def plot(
        self,
        rows: Sequence[SpectrumMetrics],
        j_values: Sequence[float],
        jpm_values: Sequence[float],
        detector_n: int,
        hz: float,
        path: Path,
    ) -> Path:
        selected = [row for row in rows if row.detector_n == detector_n and math.isclose(row.hz, hz, abs_tol=1e-12)]
        matrix = np.full((len(jpm_values), len(j_values)), np.nan, dtype=float)
        j_index = {float(value): index for index, value in enumerate(j_values)}
        jpm_index = {float(value): index for index, value in enumerate(jpm_values)}
        for row in selected:
            matrix[jpm_index[row.Jpm], j_index[row.J]] = row.S_wrapped_heavy
        if not np.isfinite(matrix).any():
            raise ValueError(f"no finite rows for N={detector_n}, hz={hz}")

        fig, axis = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
        image = axis.imshow(matrix, origin="lower", aspect="auto", vmin=0.0, vmax=1.0, cmap="RdYlGn")
        axis.set_xticks(np.arange(len(j_values)), [f"{value:g}" for value in j_values], rotation=45, ha="right")
        axis.set_yticks(np.arange(len(jpm_values)), [f"{value:g}" for value in jpm_values])
        axis.set_xlabel(r"$J$")
        axis.set_ylabel(r"$J_{\pm}$")
        axis.set_title(rf"Wrapped-heavy score, $N={detector_n}$, $h_z={hz:g}$")
        colorbar = fig.colorbar(image, ax=axis, pad=0.02)
        colorbar.set_label(r"$S_{\rm WH}$ (0: red, 1: green)")
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=190)
        plt.close(fig)
        return path


class ThetaPowerLawHeatmapPlotter:
    r"""Render clean heatmaps of the fitted periodic power-law exponent."""

    def __init__(self, alpha_limits: tuple[float, float] = (0.0, 4.0)):
        self.alpha_limits = tuple(map(float, alpha_limits))
        if self.alpha_limits[0] < 0.0 or self.alpha_limits[1] <= self.alpha_limits[0]:
            raise ValueError("alpha_limits must satisfy 0 <= lower < upper")

    def plot(
        self,
        rows: Sequence[SpectrumMetrics],
        j_values: Sequence[float],
        jpm_values: Sequence[float],
        detector_n: int,
        hz: float,
        path: Path,
    ) -> Path:
        selected = [row for row in rows if row.detector_n == detector_n and math.isclose(row.hz, hz, abs_tol=1e-12)]
        matrix = np.full((len(jpm_values), len(j_values)), np.nan, dtype=float)
        j_index = {float(value): index for index, value in enumerate(j_values)}
        jpm_index = {float(value): index for index, value in enumerate(jpm_values)}
        for row in selected:
            matrix[jpm_index[row.Jpm], j_index[row.J]] = row.theta_power_law_alpha
        if not np.isfinite(matrix).any():
            raise ValueError(f"no finite rows for N={detector_n}, hz={hz}")

        figure, axis = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
        colormap = plt.get_cmap("RdYlGn_r").copy()
        colormap.set_bad("#d1d5db")
        image = axis.imshow(
            matrix,
            origin="lower",
            aspect="auto",
            vmin=self.alpha_limits[0],
            vmax=self.alpha_limits[1],
            cmap=colormap,
        )
        axis.set_xticks(np.arange(len(j_values)), [f"{value:g}" for value in j_values], rotation=45, ha="right")
        axis.set_yticks(np.arange(len(jpm_values)), [f"{value:g}" for value in jpm_values])
        axis.set_xlabel(r"$J$")
        axis.set_ylabel(r"$J_{\pm}$")
        axis.set_title(rf"Periodic power-law exponent, $N={detector_n}$, $h_z={hz:g}$")
        colorbar = figure.colorbar(image, ax=axis, pad=0.02, extend="max")
        colorbar.set_label(r"$\alpha$ in $P(\theta)\propto d_{2\pi}(\theta,0)^{-\alpha}$")
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, dpi=190)
        plt.close(figure)
        return path


class ParameterRegimeSummarizer:
    """Select robust regimes and quantify cross-diagnostic relationships."""

    def __init__(
        self,
        *,
        born_score_min: float = 0.75,
        born_rmse_max: float = 0.15,
        coverage_min: float = 0.50,
        wrapped_heavy_min: float = 0.75,
    ):
        self.born_score_min = born_score_min
        self.born_rmse_max = born_rmse_max
        self.coverage_min = coverage_min
        self.wrapped_heavy_min = wrapped_heavy_min

    def is_born_like(self, row: SpectrumMetrics) -> bool:
        return (
            row.S_born >= self.born_score_min
            and row.born_rmse <= self.born_rmse_max
            and row.angular_bin_coverage >= self.coverage_min
        )

    def is_wrapped_heavy(self, row: SpectrumMetrics) -> bool:
        return row.S_wrapped_heavy >= self.wrapped_heavy_min

    @staticmethod
    def _compact(row: SpectrumMetrics) -> dict[str, Any]:
        return {
            "detector_n": row.detector_n,
            "hz": row.hz,
            "J": row.J,
            "Jpm": row.Jpm,
            "S_born": row.S_born,
            "born_rmse": row.born_rmse,
            "angular_bin_coverage": row.angular_bin_coverage,
            "S_wrapped_heavy": row.S_wrapped_heavy,
            "theta_power_law_alpha": row.theta_power_law_alpha,
            "theta_power_law_js": row.theta_power_law_js,
            "theta_power_law_log10_span": row.theta_power_law_log10_span,
            "cauchy_advantage_per_sample": row.cauchy_log_likelihood_advantage_per_sample,
            "wrapped_cauchy_js": row.wrapped_cauchy_js,
            "tail_density_exponent": row.tail_density_exponent,
            "radius_q99_over_q50": row.radius_q99_over_q50,
            "reciprocity_error": row.reciprocity_error,
            "phi_harmonic_2": row.phi_harmonic_2,
            "source_npz": row.source_npz,
        }

    def summarize(self, rows: Sequence[SpectrumMetrics]) -> dict[str, Any]:
        if not rows:
            raise ValueError("cannot summarize an empty campaign")
        born_like = sorted((row for row in rows if self.is_born_like(row)), key=lambda row: row.S_born, reverse=True)
        wrapped_heavy = sorted(
            (row for row in rows if self.is_wrapped_heavy(row)),
            key=lambda row: row.S_wrapped_heavy,
            reverse=True,
        )
        joint = [row for row in born_like if self.is_wrapped_heavy(row)]
        best_by_n_hz: list[dict[str, Any]] = []
        for detector_n, hz in sorted({(row.detector_n, row.hz) for row in rows}):
            group = [row for row in rows if row.detector_n == detector_n and row.hz == hz]
            best_born = max(group, key=lambda row: row.S_born)
            best_heavy = max(group, key=lambda row: row.S_wrapped_heavy)
            best_by_n_hz.append(
                {
                    "detector_n": detector_n,
                    "hz": hz,
                    "configurations": len(group),
                    "born_like_count": sum(self.is_born_like(row) for row in group),
                    "wrapped_heavy_count": sum(self.is_wrapped_heavy(row) for row in group),
                    "joint_count": sum(self.is_born_like(row) and self.is_wrapped_heavy(row) for row in group),
                    "best_born_J": best_born.J,
                    "best_born_Jpm": best_born.Jpm,
                    "max_S_born": best_born.S_born,
                    "best_heavy_J": best_heavy.J,
                    "best_heavy_Jpm": best_heavy.Jpm,
                    "max_S_wrapped_heavy": best_heavy.S_wrapped_heavy,
                }
            )
        return {
            "thresholds": {
                "born_score_min": self.born_score_min,
                "born_rmse_max": self.born_rmse_max,
                "coverage_min": self.coverage_min,
                "wrapped_heavy_min": self.wrapped_heavy_min,
            },
            "configuration_count": len(rows),
            "born_like_count": len(born_like),
            "wrapped_heavy_count": len(wrapped_heavy),
            "joint_count": len(joint),
            "top_born": [self._compact(row) for row in born_like[:100]],
            "top_wrapped_heavy": [self._compact(row) for row in wrapped_heavy[:100]],
            "joint_candidates": [self._compact(row) for row in joint],
            "best_by_n_hz": best_by_n_hz,
            "spearman_correlations": self._correlations(rows),
        }

    @staticmethod
    def _correlations(rows: Sequence[SpectrumMetrics]) -> list[dict[str, Any]]:
        born = np.asarray([row.S_born for row in rows], dtype=float)
        variables = {
            "theta_power_law_alpha": np.asarray([row.theta_power_law_alpha for row in rows], dtype=float),
            "theta_power_law_js": np.asarray([row.theta_power_law_js for row in rows], dtype=float),
            "S_wrapped_heavy": np.asarray([row.S_wrapped_heavy for row in rows], dtype=float),
            "tail_density_exponent": np.asarray([row.tail_density_exponent for row in rows], dtype=float),
            "radius_q99_over_q50": np.asarray([row.radius_q99_over_q50 for row in rows], dtype=float),
            "reciprocity_error": np.asarray([row.reciprocity_error for row in rows], dtype=float),
            "phi_harmonic_2": np.asarray([row.phi_harmonic_2 for row in rows], dtype=float),
            "angular_bin_coverage": np.asarray([row.angular_bin_coverage for row in rows], dtype=float),
        }
        output: list[dict[str, Any]] = []
        for name, values in variables.items():
            finite = np.isfinite(born) & np.isfinite(values)
            if np.count_nonzero(finite) < 3:
                coefficient = p_value = math.nan
            else:
                result = spearmanr(born[finite], values[finite])
                coefficient = float(result.statistic)
                p_value = float(result.pvalue)
            output.append(
                {
                    "born_metric": "S_born",
                    "spectrum_metric": name,
                    "sample_count": int(np.count_nonzero(finite)),
                    "spearman_rho": coefficient,
                    "two_sided_p_value": p_value,
                }
            )
        return output


class RelationshipPlotter:
    """Plot the separation or overlap of Born and wrapped-heavy evidence."""

    def plot(self, rows: Sequence[SpectrumMetrics], path: Path) -> Path:
        fig, axis = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
        detector_sizes = sorted({row.detector_n for row in rows})
        palette = plt.get_cmap("viridis", len(detector_sizes))
        for index, detector_n in enumerate(detector_sizes):
            group = [row for row in rows if row.detector_n == detector_n]
            axis.scatter(
                [row.S_wrapped_heavy for row in group],
                [row.S_born for row in group],
                s=15,
                alpha=0.55,
                color=palette(index),
                edgecolors="none",
                label=f"N={detector_n}",
            )
        axis.axvline(0.75, color="#b45309", linestyle="--", linewidth=1.2)
        axis.axhline(0.75, color="#2563eb", linestyle="--", linewidth=1.2)
        axis.set(
            xlim=(-0.02, 1.02),
            ylim=(-1.02, 1.02),
            xlabel=r"wrapped-heavy score $S_{\rm WH}$",
            ylabel=r"Born similarity $S_{\rm Born}$",
            title="Wrapped-heavy and Born evidence across the anisotropic sweep",
        )
        axis.grid(alpha=0.2)
        axis.legend(ncol=2, fontsize=8, frameon=False)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=190)
        plt.close(fig)
        return path


class PowerLawRelationshipPlotter:
    """Plot fitted ``alpha`` against Born similarity, colored by fit quality."""

    def plot(self, rows: Sequence[SpectrumMetrics], path: Path) -> Path:
        figure, axis = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
        alpha = np.asarray([row.theta_power_law_alpha for row in rows], dtype=float)
        born = np.asarray([row.S_born for row in rows], dtype=float)
        js = np.asarray([row.theta_power_law_js for row in rows], dtype=float)
        coverage = np.asarray([row.angular_bin_coverage for row in rows], dtype=float)
        reliable = np.isfinite(alpha) & np.isfinite(born) & (js <= 0.10) & (coverage >= 0.50)
        unreliable = np.isfinite(alpha) & np.isfinite(born) & ~reliable
        axis.scatter(
            alpha[unreliable],
            born[unreliable],
            s=11,
            alpha=0.16,
            color="#9ca3af",
            edgecolors="none",
            label="unresolved / poor fit",
        )
        points = axis.scatter(
            alpha[reliable],
            born[reliable],
            c=js[reliable],
            s=16,
            alpha=0.58,
            cmap="viridis_r",
            vmin=0.0,
            vmax=0.10,
            edgecolors="none",
            label="resolved fit",
        )
        axis.axhline(0.75, color="#2563eb", linestyle="--", linewidth=1.2)
        axis.set(
            xlim=(-0.1, 8.1),
            ylim=(-1.02, 1.02),
            xlabel=r"periodic power-law exponent $\alpha$",
            ylabel=r"Born similarity $S_{\rm Born}$",
            title=r"Power-law exponent and Born similarity",
        )
        axis.grid(alpha=0.2)
        axis.legend(frameon=False, fontsize=8)
        colorbar = figure.colorbar(points, ax=axis, pad=0.02)
        colorbar.set_label(r"power-law fit JS divergence")
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, dpi=190)
        plt.close(figure)
        return path


def iter_expected_cases(config: AnisotropicSweepConfig) -> Iterable[AnisotropicCase]:
    """Yield the full configured Cartesian grid in stable order."""

    for detector_n in config.detector_sizes:
        for hz in config.hz_values:
            for j in config.j_values:
                for jpm in config.jpm_values:
                    yield AnisotropicCase(
                        detector_n=detector_n,
                        hz=hz,
                        j=j,
                        jpm=jpm,
                        evolution_time=config.evolution_time,
                        jx=config.jx,
                        hz0=config.hz0,
                        seed=config.seed,
                    )


def completeness_payload(rows: Sequence[CampaignCompleteness]) -> dict[str, Any]:
    return {
        "complete": all(row.complete for row in rows),
        "detector_sizes": [asdict(row) | {"complete": row.complete} for row in rows],
        "total_expected_cases": sum(row.expected_cases for row in rows),
        "total_raw_spectra": sum(row.raw_spectra for row in rows),
        "total_metrics_files": sum(row.metrics_files for row in rows),
        "total_diagnostic_figures": sum(row.diagnostic_figures for row in rows),
    }
