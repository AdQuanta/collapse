"""Reusable services for single-pixel diagnostic-atlas sweeps.

The module separates six responsibilities:

* :class:`SinglePixelSpec` owns immutable Hamiltonian configuration.
* :class:`QuSpinSectorBackend` provides the eigensystem implementation behind
  a small protocol.
* :class:`NpzSpectrumRepository` owns persistence and deterministic paths.
* :class:`SweepRunner` orchestrates fields and times through injected backend
  and repository abstractions.
* variance-provider strategies keep model-specific wrapped-Gaussian theory
  separate from propagation and diagnostics.
* :class:`AngularDiagnosticCalculator` converts one saved spectrum into plot
  data and scalar diagnostics.

This keeps plotting and CLI code independent of QuSpin construction and file
layout, and permits test doubles without modifying the orchestration logic.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import time
from typing import Protocol, Sequence

import numpy as np

from core.analysis import DisentanglementAnalyzer
from core.born import born_ratio_from_radii
from core.distribution_fit import fit_folded_circular_models
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.resonant_study import folded_wrapped_gaussian_bin_density


@dataclass(frozen=True)
class SinglePixelSpec:
    """Immutable clean-ring Hamiltonian parameters."""

    detector_n: int = 10
    j: float = 1.0
    jpm: float = 0.0
    jx: float = 0.01
    hz0: float = 0.0
    connectivity: str = "ring"
    central_coupling: str = "all"

    def __post_init__(self) -> None:
        if self.detector_n < 3:
            raise ValueError("detector_n must be at least 3 for the periodic ring")
        if self.connectivity != "ring":
            raise ValueError("this atlas service currently supports the periodic ring only")
        if self.central_coupling != "all":
            raise ValueError("this atlas service requires coupling to all detector spins")

    @property
    def total_qubits(self) -> int:
        return self.detector_n + 1

    @property
    def relative_dimension(self) -> int:
        return 2**self.detector_n

    @property
    def collective_jx(self) -> float:
        return self.jx

    @property
    def edge_jx(self) -> float:
        return self.jx / math.sqrt(self.detector_n)

    @property
    def reference_fields(self) -> tuple[float, ...]:
        """Natural field references for the configured detector model."""

        if self.jpm != 0.0 and self.j == 0.0:
            return (-2.0 * self.jpm, -self.jpm, 0.0, self.jpm, 2.0 * self.jpm)
        return (-2.0 * self.j, 0.0, 2.0 * self.j)


@dataclass(frozen=True)
class SpectrumSample:
    """One relative-evolution spectrum at a field and time."""

    hz: float
    t: float
    eigenvalues: np.ndarray
    theta: np.ndarray
    theory_variance: float


@dataclass(frozen=True)
class FieldRunMetadata:
    hz: float
    sector_count: int
    diagonalization_seconds: float


class SectorBackend(Protocol):
    """Abstraction for a Hamiltonian-sector implementation."""

    def diagonalize(self, spec: SinglePixelSpec, hz: float) -> list:
        ...


class SpectrumComputer(Protocol):
    """Computation abstraction consumed by :class:`SweepRunner`."""

    def compute_field(
        self,
        spec: SinglePixelSpec,
        hz: float,
        times: Sequence[float],
    ) -> tuple[list[SpectrumSample], FieldRunMetadata]:
        ...


class SpectrumRepository(Protocol):
    """Persistence abstraction consumed by :class:`SweepRunner`."""

    def has_sample(self, detector_n: int, hz: float, t: float) -> bool:
        ...

    def save_sample(self, spec: SinglePixelSpec, sample: SpectrumSample) -> Path:
        ...

    def load_sample(self, detector_n: int, hz: float, t: float) -> SpectrumSample:
        ...

    def save_field_metadata(self, spec: SinglePixelSpec, metadata: FieldRunMetadata, times: Sequence[float]) -> Path:
        ...


class TheoryVarianceProvider(Protocol):
    """Model-specific no-fit wrapped-Gaussian variance strategy."""

    def variances(
        self,
        spec: SinglePixelSpec,
        hz: float,
        times: Sequence[float],
    ) -> tuple[float, ...]:
        ...


class QuSpinSectorBackend:
    """QuSpin implementation of the sector-backend protocol."""

    def diagonalize(self, spec: SinglePixelSpec, hz: float) -> list:
        hamiltonian = SinglePixelHamiltonianQuSpin(
            N_pixel=spec.detector_n,
            J=spec.j,
            Jpm=spec.jpm,
            Jx=spec.edge_jx,
            Jy=0.0,
            Jz=0.0,
            Jzx=0.0,
            hx=0.0,
            hz=hz,
            hx0=0.0,
            hz0=spec.hz0,
            connectivity=spec.connectivity,
            central_coupling=spec.central_coupling,
            use_symmetry=True,
        )
        return hamiltonian.diagonalize_sectors()


class RelativeSpectrumComputer:
    """Compute relative spectra using an injected sector backend."""

    def __init__(
        self,
        backend: SectorBackend,
        variance_provider: TheoryVarianceProvider | None = None,
    ):
        self._backend = backend
        self._variance_provider = variance_provider or IsingLocalVarianceProvider()

    def compute_field(
        self,
        spec: SinglePixelSpec,
        hz: float,
        times: Sequence[float],
    ) -> tuple[list[SpectrumSample], FieldRunMetadata]:
        started = time.perf_counter()
        sectors = self._backend.diagonalize(spec, hz)
        diagonalization_seconds = time.perf_counter() - started
        variances = self._variance_provider.variances(spec, hz, times)
        if len(variances) != len(times):
            raise ValueError("variance provider returned the wrong number of values")
        samples: list[SpectrumSample] = []
        for t, variance in zip(times, variances):
            analyzer = DisentanglementAnalyzer.from_sectors(sectors, float(t), spec.total_qubits)
            eigenvalues = np.asarray(analyzer.D0, dtype=np.complex128)
            theta = 2.0 * np.arctan(np.abs(eigenvalues))
            samples.append(
                SpectrumSample(
                    hz=float(hz),
                    t=float(t),
                    eigenvalues=eigenvalues,
                    theta=theta,
                    theory_variance=variance,
                )
            )
        return samples, FieldRunMetadata(
            hz=float(hz),
            sector_count=len(sectors),
            diagonalization_seconds=diagonalization_seconds,
        )


class NpzSpectrumRepository:
    """Deterministic NPZ/JSON implementation of the repository protocol."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def case_dir(self, detector_n: int, hz: float) -> Path:
        return self.root / f"N{detector_n:02d}" / f"hz_{hz:+.4f}"

    def sample_path(self, detector_n: int, hz: float, t: float) -> Path:
        return self.case_dir(detector_n, hz) / f"raw_t{t:.12g}.npz"

    def has_sample(self, detector_n: int, hz: float, t: float) -> bool:
        return self.sample_path(detector_n, hz, t).is_file()

    def save_sample(self, spec: SinglePixelSpec, sample: SpectrumSample) -> Path:
        path = self.sample_path(spec.detector_n, sample.hz, sample.t)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            eigenvalues=sample.eigenvalues,
            theta=sample.theta,
            theory_variance=sample.theory_variance,
            hz0=spec.hz0,
            hz=sample.hz,
            J=spec.j,
            Jpm=spec.jpm,
            Jx=spec.jx,
            Jx_edge=spec.edge_jx,
            detector_n=spec.detector_n,
            total_qubits=spec.total_qubits,
        )
        return path

    def load_sample(self, detector_n: int, hz: float, t: float) -> SpectrumSample:
        with np.load(self.sample_path(detector_n, hz, t)) as raw:
            return SpectrumSample(
                hz=float(raw["hz"]),
                t=float(t),
                eigenvalues=np.asarray(raw["eigenvalues"], dtype=np.complex128),
                theta=np.asarray(raw["theta"], dtype=float),
                theory_variance=float(raw["theory_variance"]),
            )

    def save_field_metadata(
        self,
        spec: SinglePixelSpec,
        metadata: FieldRunMetadata,
        times: Sequence[float],
    ) -> Path:
        path = self.case_dir(spec.detector_n, metadata.hz) / "metadata.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        nearest = min(spec.reference_fields, key=lambda center: abs(metadata.hz - center))
        payload = {
            "detector_n": spec.detector_n,
            "total_qubits": spec.total_qubits,
            "hz0": spec.hz0,
            "hz": metadata.hz,
            "J": spec.j,
            "Jpm": spec.jpm,
            "Jx": spec.jx,
            "Jx_edge": spec.edge_jx,
            "times": [float(value) for value in times],
            "sector_count": metadata.sector_count,
            "diagonalization_seconds": metadata.diagonalization_seconds,
            "nearest_resonance": nearest,
            "detuning": abs(metadata.hz - nearest),
            "overall_sign": "repository convention is minus the displayed Hamiltonian; theta and R are invariant",
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path


class SweepRunner:
    """Orchestrate a sweep without depending on concrete backend or storage."""

    def __init__(self, computer: SpectrumComputer, repository: SpectrumRepository):
        self._computer = computer
        self._repository = repository

    def run(
        self,
        spec: SinglePixelSpec,
        hz_values: Sequence[float],
        times: Sequence[float],
        *,
        force: bool = False,
    ) -> None:
        for hz in hz_values:
            if not force and all(self._repository.has_sample(spec.detector_n, float(hz), float(t)) for t in times):
                print(f"Reusing N={spec.detector_n}, hz={float(hz):+.4f}", flush=True)
                continue
            print(
                f"Diagonalizing sectors: N={spec.detector_n}, hz0={spec.hz0:g}, "
                f"hz={float(hz):+.4f}, J={spec.j:g}, Jpm={spec.jpm:g}, "
                f"Jx={spec.jx:g}, Jx(edge)={spec.edge_jx:.7g}",
                flush=True,
            )
            samples, metadata = self._computer.compute_field(spec, float(hz), times)
            for sample in samples:
                self._repository.save_sample(spec, sample)
            self._repository.save_field_metadata(spec, metadata, times)


@dataclass(frozen=True)
class AngularDiagnostics:
    edges: np.ndarray
    centers: np.ndarray
    p_theta: np.ndarray
    p_reflected: np.ndarray
    ratio: np.ndarray
    occupied: np.ndarray
    born_curve: np.ndarray
    theory: np.ndarray
    theory_reflected: np.ndarray
    born_score: float
    born_rmse: float
    coverage: float
    phi_harmonic_2: float
    wrapped_gaussian_l1: float
    best_fit_wrapped_gaussian_sigma: float
    best_fit_wrapped_gaussian_l1: float
    best_fit_wrapped_gaussian_js: float
    best_fit_wrapped_cauchy_gamma: float
    best_fit_wrapped_cauchy_l1: float
    best_fit_wrapped_cauchy_js: float
    cauchy_log_likelihood_advantage_per_sample: float
    preferred_wrapped_model: str
    finite_eigenvalues: int


class AngularDiagnosticCalculator:
    """Convert one spectrum sample into plot-ready angular diagnostics."""

    def __init__(self, bins: int = 48):
        if bins < 4:
            raise ValueError("bins must be at least 4")
        self._edges = np.linspace(0.0, np.pi, bins + 1)

    def calculate(self, sample: SpectrumSample) -> AngularDiagnostics:
        edges = self._edges
        centers = 0.5 * (edges[:-1] + edges[1:])
        p_theta = histogram_density(sample.theta, edges)
        p_reflected = histogram_density(np.pi - sample.theta, edges)
        denominator = p_theta + p_reflected
        ratio = np.divide(p_theta, denominator, out=np.full_like(p_theta, np.nan), where=denominator > 0.0)
        occupied = np.isfinite(ratio)
        born_curve = np.cos(centers / 2.0) ** 2
        theory = folded_wrapped_gaussian_bin_density(edges, sample.theory_variance)
        finite = np.isfinite(sample.eigenvalues.real) & np.isfinite(sample.eigenvalues.imag)
        born_score = float(born_ratio_from_radii(np.abs(sample.eigenvalues[finite]), n_theta=100).similarity)
        born_rmse = float(np.sqrt(np.mean((ratio[occupied] - born_curve[occupied]) ** 2)))
        harmonic = second_phi_harmonic(sample.eigenvalues)
        fitted = fit_folded_circular_models(sample.theta, edges)
        return AngularDiagnostics(
            edges=edges,
            centers=centers,
            p_theta=p_theta,
            p_reflected=p_reflected,
            ratio=ratio,
            occupied=occupied,
            born_curve=born_curve,
            theory=theory,
            theory_reflected=theory[::-1],
            born_score=born_score,
            born_rmse=born_rmse,
            coverage=float(np.mean(occupied)),
            phi_harmonic_2=harmonic,
            wrapped_gaussian_l1=float(np.sum(np.abs(p_theta - theory) * np.diff(edges))),
            best_fit_wrapped_gaussian_sigma=fitted.wrapped_gaussian_sigma,
            best_fit_wrapped_gaussian_l1=fitted.wrapped_gaussian_l1,
            best_fit_wrapped_gaussian_js=fitted.wrapped_gaussian_js,
            best_fit_wrapped_cauchy_gamma=fitted.wrapped_cauchy_gamma,
            best_fit_wrapped_cauchy_l1=fitted.wrapped_cauchy_l1,
            best_fit_wrapped_cauchy_js=fitted.wrapped_cauchy_js,
            cauchy_log_likelihood_advantage_per_sample=fitted.cauchy_log_likelihood_advantage_per_sample,
            preferred_wrapped_model=fitted.preferred_model,
            finite_eigenvalues=int(np.count_nonzero(finite)),
        )


def central_field_wrapped_variance(spec: SinglePixelSpec, hz: float, t: float) -> float:
    """Finite-time local-channel variance for the configured clean ring."""

    def kernel(omega: float) -> float:
        if abs(omega) < 1.0e-14:
            return t * t
        return 2.0 * (1.0 - math.cos(omega * t)) / omega**2

    weighted = 0.0
    for spin in (-1.0, 1.0):
        for neighbours, probability in ((-2.0, 0.25), (0.0, 0.50), (2.0, 0.25)):
            delta = spec.hz0 + spin * (hz + spec.j * neighbours)
            weighted += 0.5 * probability * kernel(2.0 * delta)
    return float(4.0 * spec.collective_jx**2 * weighted)


class IsingLocalVarianceProvider:
    """Closed-form local-channel variance for the clean ZZ ring."""

    def variances(
        self,
        spec: SinglePixelSpec,
        hz: float,
        times: Sequence[float],
    ) -> tuple[float, ...]:
        return tuple(central_field_wrapped_variance(spec, hz, float(t)) for t in times)


class DetectorSpectralVarianceProvider:
    """Exact finite-N spectral variance for a clean ZZ/plus-minus detector.

    This evaluates Eq. (6.4) of
    ``reports/four_model_finite_time_eigenvalue_derivation_2026-07-10.md``:
    the normalized detector trace of the integrated interaction-picture
    collective-X operator.  It supplies a no-fit wrapped-Gaussian reference;
    agreement still requires the cumulant assumptions documented there.
    """

    def variances(
        self,
        spec: SinglePixelSpec,
        hz: float,
        times: Sequence[float],
    ) -> tuple[float, ...]:
        from quspin.basis import spin_basis_1d
        from quspin.operators import hamiltonian

        n = spec.detector_n
        basis = spin_basis_1d(L=n)
        zz_bonds = [[-spec.j, i, (i + 1) % n] for i in range(n)]
        pm_bonds = [[-spec.jpm / 4.0, i, (i + 1) % n] for i in range(n)]
        fields = [[-float(hz), i] for i in range(n)]
        static = [["zz", zz_bonds], ["z", fields]]
        if spec.jpm != 0.0:
            static.extend([["+-", pm_bonds], ["-+", pm_bonds]])
        detector = hamiltonian(
            static,
            [],
            basis=basis,
            dtype=np.float64,
            check_symm=False,
            check_herm=False,
            check_pcon=False,
        ).toarray()
        collective_x = hamiltonian(
            [["x", [[1.0, i] for i in range(n)]]],
            [],
            basis=basis,
            dtype=np.float64,
            check_symm=False,
            check_herm=False,
            check_pcon=False,
        ).toarray()
        energies, vectors = np.linalg.eigh(detector)
        interaction = vectors.conj().T @ collective_x @ vectors
        weights = np.abs(interaction) ** 2
        gaps = energies[:, None] - energies[None, :]
        normalization = float(n * 2**n)
        output: list[float] = []
        for time_value in times:
            t = float(time_value)
            kernel = np.empty_like(gaps)
            zero = np.abs(gaps) < 1.0e-12
            kernel[zero] = t * t
            nonzero = ~zero
            kernel[nonzero] = 4.0 * np.sin(0.5 * gaps[nonzero] * t) ** 2 / gaps[nonzero] ** 2
            v_n = float(np.sum(weights * kernel) / normalization)
            output.append(4.0 * spec.collective_jx**2 * v_n)
        return tuple(output)


class PlusMinusSpectralVarianceProvider(DetectorSpectralVarianceProvider):
    """Backward-compatible name for the exact detector spectral strategy."""


def histogram_density(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    counts, _ = np.histogram(values, bins=edges)
    return counts / max(values.size, 1) / np.diff(edges)


def second_phi_harmonic(eigenvalues: np.ndarray) -> float:
    values = np.asarray(eigenvalues, dtype=np.complex128)
    mask = np.isfinite(values.real) & np.isfinite(values.imag) & (np.abs(values) > 1.0e-12)
    if not np.any(mask):
        return float("nan")
    return float(abs(np.mean(np.exp(2j * np.angle(values[mask])))))
