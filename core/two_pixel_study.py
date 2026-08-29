"""Reusable services for controlled single- versus two-pixel comparisons.

The user-facing collective coupling ``Jx`` is converted to an edge coefficient
``Jx/sqrt(N_detector)`` in one place.  This keeps simulation policy separate
from the Hamiltonian generators, whose parameters are always literal matrix
coefficients.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from pathlib import Path
from typing import Literal

import numpy as np

from core.analysis import DisentanglementAnalyzer
from core.born import born_ratio_from_radii
from core.born import diagnostics_from_radii
from core.distribution_fit import fit_folded_circular_models
from core.hamiltonians.quspin_hamiltonians import (
    SinglePixelHamiltonianQuSpin,
    TwoPixelHamiltonianQuSpin,
)
from core.resonant_study import folded_wrapped_gaussian_bin_density
from core.single_pixel_atlas import (
    DetectorSpectralVarianceProvider,
    SinglePixelSpec,
)


ModelKind = Literal["single", "two"]


@dataclass(frozen=True)
class ComparisonSpec:
    """One Hamiltonian in an equal-total-detector comparison."""

    key: str
    label: str
    kind: ModelKind
    detector_spins: int
    hz0: float
    family: str = "baseline"
    parameter_name: str = "hz0"
    parameter_value: float = 0.0
    hz: float = 0.1
    j: float = 1.0
    jpm: float = 0.0
    collective_jx: float = 0.01
    connectivity: str = "ring"
    central_coupling: str = "all"

    @property
    def edge_jx(self) -> float:
        return self.collective_jx / math.sqrt(self.detector_spins)

    @property
    def n_pixel(self) -> int:
        if self.kind == "two":
            if self.detector_spins % 2:
                raise ValueError("Two-pixel comparisons require an even detector count")
            return self.detector_spins // 2
        return self.detector_spins

    @property
    def total_qubits(self) -> int:
        return self.detector_spins + 1


@dataclass(frozen=True)
class AngularRecord:
    key: str
    family: str
    parameter_name: str
    parameter_value: float
    kind: str
    hz0: float
    hz: float
    j: float
    jpm: float
    time: float
    detector_spins: int
    edge_jx: float
    finite_eigenvalues: int
    born_similarity: float
    born_rmse: float
    occupied_bin_fraction: float
    wrapped_gaussian_l1: float
    fitted_gaussian_l1: float
    fitted_cauchy_l1: float
    cauchy_log_likelihood_advantage_per_sample: float
    preferred_model: str
    tail_density_exponent: float
    reciprocity_error: float
    radius_q99_over_q50: float
    radius_atomic_fraction: float
    phi_harmonic_2: float
    theta_median: float
    theta_q95: float


def default_specs(detector_spins: int = 8) -> tuple[ComparisonSpec, ...]:
    """Return matched comparisons at zero and resonant central field."""

    specs: list[ComparisonSpec] = []
    for hz0, suffix in ((0.0, "zero"), (0.1, "matched")):
        specs.extend(
            [
                ComparisonSpec(
                    key=f"single_{suffix}",
                    label=rf"single pixel, $h_{{z0}}={hz0:g}$",
                    kind="single",
                    detector_spins=detector_spins,
                    hz0=hz0,
                ),
                ComparisonSpec(
                    key=f"two_{suffix}",
                    label=rf"two pixels (opposite), $h_{{z0}}={hz0:g}$",
                    kind="two",
                    detector_spins=detector_spins,
                    hz0=hz0,
                ),
            ]
        )
    return tuple(specs)


def reference_variance(spec: ComparisonSpec, time_value: float) -> float:
    """Local-channel perturbative variance used as a common null reference.

    Detector-2 signs disappear after squaring, so the equal-total-spin,
    ``Jx/sqrt(N_detector)`` normalization gives the same second-order reference
    for the single- and two-pixel cases.
    """

    def kernel(omega: float) -> float:
        if abs(omega) < 1.0e-14:
            return time_value**2
        return 2.0 * (1.0 - math.cos(omega * time_value)) / omega**2

    weighted = 0.0
    for spin in (-1.0, 1.0):
        for neighbours, probability in ((-2.0, 0.25), (0.0, 0.5), (2.0, 0.25)):
            delta = spec.hz0 + spin * (spec.hz + spec.j * neighbours)
            weighted += 0.5 * probability * kernel(2.0 * delta)
    return float(4.0 * spec.collective_jx**2 * weighted)


def reference_variances(
    spec: ComparisonSpec,
    times: tuple[float, ...],
) -> tuple[float, ...]:
    """Return the no-fit theory reference appropriate to one detector model.

    Pure-ZZ cases use the established local-channel formula.  Plus-minus
    cases use the exact finite-detector spectral trace.  For two pixels the
    trace is evaluated on one independent pixel while retaining the total
    collective ``Jx`` normalization; cross-pixel trace terms vanish.
    """

    if spec.jpm == 0.0:
        return tuple(reference_variance(spec, value) for value in times)
    theory_n = spec.detector_spins if spec.kind == "single" else spec.n_pixel
    theory_spec = SinglePixelSpec(
        detector_n=theory_n,
        j=spec.j,
        jpm=spec.jpm,
        jx=spec.collective_jx,
        hz0=spec.hz0,
        connectivity=spec.connectivity,
        central_coupling=spec.central_coupling,
    )
    return DetectorSpectralVarianceProvider().variances(
        theory_spec,
        spec.hz,
        times,
    )


class HamiltonianFactory:
    """Construct canonical QuSpin generators from immutable study specs."""

    @staticmethod
    def build(spec: ComparisonSpec):
        common = dict(
            N_pixel=spec.n_pixel,
            J=spec.j,
            Jpm=spec.jpm,
            Jxx=0.0,
            Jyy=0.0,
            Jx=spec.edge_jx,
            Jy=0.0,
            Jz=0.0,
            Jzx=0.0,
            Jcpm=0.0,
            hx=0.0,
            hz=spec.hz,
            hx0=0.0,
            hz0=spec.hz0,
            connectivity=spec.connectivity,
            central_coupling=spec.central_coupling,
            use_symmetry=True,
        )
        if spec.kind == "single":
            return SinglePixelHamiltonianQuSpin(**common)
        return TwoPixelHamiltonianQuSpin(**common)


class ComparisonSimulator:
    """Run spectra and checkpoint every model/time result independently."""

    def __init__(self, output_root: Path, factory: HamiltonianFactory | None = None):
        self.output_root = Path(output_root)
        self.factory = factory or HamiltonianFactory()

    def raw_path(self, spec: ComparisonSpec, time_value: float) -> Path:
        return self.output_root / spec.key / f"raw_t{time_value:.12g}.npz"

    def run(self, spec: ComparisonSpec, times: tuple[float, ...], *, force: bool = False) -> None:
        paths = [self.raw_path(spec, value) for value in times]
        if not force and all(path.is_file() for path in paths):
            return
        case_dir = self.output_root / spec.key
        case_dir.mkdir(parents=True, exist_ok=True)
        sectors = self.factory.build(spec).diagonalize_sectors()
        variances = reference_variances(spec, times)
        for time_value, path, variance in zip(times, paths, variances):
            if path.is_file() and not force:
                continue
            analyzer = DisentanglementAnalyzer.from_sectors(
                sectors, time_value, spec.total_qubits
            )
            eigenvalues = np.asarray(analyzer.D0, dtype=np.complex128)
            theta = 2.0 * np.arctan(np.abs(eigenvalues))
            np.savez_compressed(
                path,
                eigenvalues=eigenvalues,
                theta=theta,
                theory_variance=variance,
                **asdict(spec),
                edge_jx=spec.edge_jx,
                n_pixel=spec.n_pixel,
                total_qubits=spec.total_qubits,
                time=time_value,
            )


class AngularDiagnosticService:
    """Calculate distribution diagnostics without plotting or I/O policy."""

    def __init__(self, bins: int = 48):
        self.edges = np.linspace(0.0, np.pi, bins + 1)
        self.centers = 0.5 * (self.edges[:-1] + self.edges[1:])

    def density(self, values: np.ndarray) -> np.ndarray:
        counts, _ = np.histogram(values, bins=self.edges)
        return counts / max(values.size, 1) / np.diff(self.edges)

    def distributions(self, raw: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        theta = np.asarray(raw["theta"], dtype=float)
        p_theta = self.density(theta)
        p_reflected = self.density(np.pi - theta)
        denominator = p_theta + p_reflected
        ratio = np.divide(
            p_theta,
            denominator,
            out=np.full_like(p_theta, np.nan),
            where=denominator > 0.0,
        )
        variance = float(raw["theory_variance"])
        return {
            "p_theta": p_theta,
            "p_reflected": p_reflected,
            "ratio": ratio,
            "born": np.cos(self.centers / 2.0) ** 2,
            "theory": folded_wrapped_gaussian_bin_density(self.edges, variance),
        }

    def calculate(self, spec: ComparisonSpec, time_value: float, raw: dict[str, np.ndarray]) -> AngularRecord:
        theta = np.asarray(raw["theta"], dtype=float)
        eigenvalues = np.asarray(raw["eigenvalues"], dtype=np.complex128)
        finite = np.isfinite(eigenvalues.real) & np.isfinite(eigenvalues.imag)
        dist = self.distributions(raw)
        occupied = np.isfinite(dist["ratio"])
        fitted = fit_folded_circular_models(theta, self.edges)
        born_score = born_ratio_from_radii(np.abs(eigenvalues[finite]), n_theta=100)
        radii = np.abs(eigenvalues[finite])
        born_diagnostics = diagnostics_from_radii(radii, n_theta=100)
        positive = radii[np.isfinite(radii) & (radii > 0.0)]
        if positive.size:
            radius_q50, radius_q99 = np.quantile(positive, (0.50, 0.99))
            spread = float(radius_q99 / radius_q50) if radius_q50 > 0.0 else float("inf")
            rounded = np.round(positive, decimals=12)
            _, atom_counts = np.unique(rounded, return_counts=True)
            atom_fraction = float(np.max(atom_counts) / rounded.size)
        else:
            spread = float("nan")
            atom_fraction = float("nan")
        phase_mask = finite & (np.abs(eigenvalues) > 1.0e-12)
        harmonic = (
            float(abs(np.mean(np.exp(2j * np.angle(eigenvalues[phase_mask])))))
            if np.any(phase_mask)
            else float("nan")
        )
        widths = np.diff(self.edges)
        return AngularRecord(
            key=spec.key,
            family=spec.family,
            parameter_name=spec.parameter_name,
            parameter_value=spec.parameter_value,
            kind=spec.kind,
            hz0=spec.hz0,
            hz=spec.hz,
            j=spec.j,
            jpm=spec.jpm,
            time=time_value,
            detector_spins=spec.detector_spins,
            edge_jx=spec.edge_jx,
            finite_eigenvalues=int(np.count_nonzero(finite)),
            born_similarity=float(born_score.similarity),
            born_rmse=float(np.sqrt(np.mean((dist["ratio"][occupied] - dist["born"][occupied]) ** 2))),
            occupied_bin_fraction=float(np.mean(occupied)),
            wrapped_gaussian_l1=float(np.sum(np.abs(dist["p_theta"] - dist["theory"]) * widths)),
            fitted_gaussian_l1=float(fitted.wrapped_gaussian_l1),
            fitted_cauchy_l1=float(fitted.wrapped_cauchy_l1),
            cauchy_log_likelihood_advantage_per_sample=float(
                fitted.cauchy_log_likelihood_advantage_per_sample
            ),
            preferred_model=fitted.preferred_model,
            tail_density_exponent=float(born_diagnostics.tail_density_exponent),
            reciprocity_error=float(born_diagnostics.reciprocity_error),
            radius_q99_over_q50=spread,
            radius_atomic_fraction=atom_fraction,
            phi_harmonic_2=harmonic,
            theta_median=float(np.median(theta)),
            theta_q95=float(np.quantile(theta, 0.95)),
        )


def load_raw(path: Path) -> dict[str, np.ndarray]:
    """Load an NPZ into an ordinary mapping with no open file handle."""
    with np.load(path) as payload:
        return {name: payload[name] for name in payload.files}
