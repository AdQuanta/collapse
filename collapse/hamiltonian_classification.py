"""Single-point Hamiltonian-to-root classification workflow.

The functional core in this module is shared by local validation and future
manifest/PBS runners.  It uses dense NumPy diagonalization and homogeneous QZ,
so it is intentionally limited to small/intermediate systems; a sector-aware
backend can be added without changing the diagnostic contract.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import time
from typing import Any

import numpy as np

from collapse.analysis import evolution_subblocks_from_eigenbasis
from collapse.born import diagnostics_from_radii
from collapse.detector_graphs import DetectorGraphSpec
from collapse.gleason_diagnostics import diagnose_labeled_bloch_histogram
from collapse.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from collapse.projective_roots import bloch_vectors_from_homogeneous
from collapse.relative_evolution_pencil import generalized_relative_evolution_spectrum


@dataclass(frozen=True)
class SinglePixelClassificationPoint:
    """One explicit single-pixel Hamiltonian and analysis point.

    Central-coupling values are source/collective coefficients.  With
    ``central_scale="sqrt_n"`` each is divided by ``sqrt(detector_n)`` before
    being assigned to every selected central--detector edge.
    """

    detector_n: int
    time: float
    J: float = 1.0
    Jpm: float = 0.0
    J2: float = 0.0
    Jpm2: float = 0.0
    Jxx: float = 0.0
    Jyy: float = 0.0
    Jx: float = 0.0
    Jy: float = 0.0
    Jz: float = 0.0
    Jzx: float = 0.0
    Jcpm: float = 0.0
    hx: float = 0.0
    hz: float = 0.0
    hx0: float = 0.0
    hz0: float = 0.0
    connectivity: str = "ring"
    central_coupling: str = "all"
    central_scale: str = "sqrt_n"
    seed: int = 20260815
    erdos_renyi_p: float = 0.3
    watts_strogatz_k: int = 4
    watts_strogatz_p: float = 0.3
    barabasi_albert_m: int = 2
    regular_degree: int = 4
    require_connected: bool = True
    graph_max_attempts: int = 10_000
    n_phi: int = 12
    n_mu: int = 6
    l_max: int = 5
    backend: str = "numpy_dense"

    def __post_init__(self) -> None:
        if self.detector_n < 2:
            raise ValueError("detector_n must be at least two")
        if not np.isfinite(self.time):
            raise ValueError("time must be finite")
        if self.central_scale not in {"sqrt_n", "none"}:
            raise ValueError("central_scale must be 'sqrt_n' or 'none'")
        if self.backend not in {"numpy_dense", "quspin_sectors", "haar_unitary"}:
            raise ValueError(
                "backend must be 'numpy_dense', 'quspin_sectors', or "
                "'haar_unitary'"
            )
        if self.n_phi < 2 or self.n_phi % 2:
            raise ValueError("n_phi must be an even integer")
        if self.n_mu < 1 or self.l_max < 1:
            raise ValueError("n_mu and l_max must be positive")
        if self.n_phi * self.n_mu < (self.l_max + 1) ** 2:
            raise ValueError("angular grid has fewer cells than retained harmonics")
        self.detector_graph_spec().validate(self.detector_n)

    @property
    def total_qubits(self) -> int:
        return self.detector_n + 1

    @property
    def dimension(self) -> int:
        return 2 ** self.total_qubits

    @property
    def root_count(self) -> int:
        return 2**self.detector_n

    @property
    def central_scale_factor(self) -> float:
        return 1.0 / math.sqrt(self.detector_n) if self.central_scale == "sqrt_n" else 1.0

    def effective_central_couplings(self) -> dict[str, float]:
        scale = self.central_scale_factor
        return {
            name: float(getattr(self, name) * scale)
            for name in ("Jx", "Jy", "Jz", "Jzx", "Jcpm")
        }

    def detector_graph_spec(self) -> DetectorGraphSpec:
        """Return the complete deterministic detector-graph specification."""

        return DetectorGraphSpec(
            kind=self.connectivity,
            seed=self.seed,
            erdos_renyi_p=self.erdos_renyi_p,
            watts_strogatz_k=self.watts_strogatz_k,
            watts_strogatz_p=self.watts_strogatz_p,
            barabasi_albert_m=self.barabasi_albert_m,
            regular_degree=self.regular_degree,
            require_connected=self.require_connected,
            max_attempts=self.graph_max_attempts,
        )


@dataclass(frozen=True)
class ClassificationPointResult:
    """Scalar result plus reusable root/source arrays for one point."""

    summary: dict[str, Any]
    alpha: np.ndarray
    beta: np.ndarray
    bloch_vectors_0: np.ndarray
    asymmetry: np.ndarray
    power_by_l: np.ndarray


def build_single_pixel_hamiltonian(point: SinglePixelClassificationPoint) -> np.ndarray:
    """Construct the exact dense Hamiltonian for one classification point."""

    coupling = point.effective_central_couplings()
    return SinglePixelHamiltonianNumpy(
        N_pixel=point.detector_n,
        J=point.J,
        Jpm=point.Jpm,
        J2=point.J2,
        Jpm2=point.Jpm2,
        Jxx=point.Jxx,
        Jyy=point.Jyy,
        Jx=coupling["Jx"],
        Jy=coupling["Jy"],
        Jz=coupling["Jz"],
        Jzx=coupling["Jzx"],
        Jcpm=coupling["Jcpm"],
        hx=point.hx,
        hz=point.hz,
        hx0=point.hx0,
        hz0=point.hz0,
        connectivity=point.connectivity,
        graph_spec=point.detector_graph_spec(),
        central_coupling=point.central_coupling,
        seed=point.seed,
    ).generate()


def _require_left_diagnostics(available: bool) -> None:
    """Refuse to classify a spectrum whose left diagnostics were skipped.

    ``qz_valid`` gates on ``maximum_left_homogeneous_residual < 1e-10``, and a
    NaN fails that comparison silently.  A spectrum built with
    ``compute_left_eigenvectors=False`` would therefore be reported invalid for
    a reason that never appears in the record, which is indistinguishable from a
    genuine solver failure.  Fail closed and say so instead.
    """

    if not available:
        raise ValueError(
            "this spectrum was computed with compute_left_eigenvectors=False, so "
            "the left backward residual is unavailable and qz_valid cannot be "
            "established; rerun the pencil with left eigenvectors enabled"
        )


def classify_single_pixel_point(
    point: SinglePixelClassificationPoint,
    *,
    verbose: bool = False,
) -> ClassificationPointResult:
    """Run dense eigendecomposition, homogeneous QZ, and sphere diagnostics."""

    started = time.perf_counter()
    if verbose:
        print(
            f"preparing {point.backend} dimension {point.dimension} "
            f"for N={point.detector_n}",
            flush=True,
        )
    diagonalization_started = time.perf_counter()
    if point.backend == "haar_unitary":
        rng = np.random.default_rng(point.seed)
        raw = rng.standard_normal((point.dimension, point.dimension)) + 1.0j * rng.standard_normal(
            (point.dimension, point.dimension)
        )
        unitary, triangular = np.linalg.qr(raw)
        diagonal = np.diag(triangular)
        phases = diagonal / np.abs(diagonal)
        unitary = unitary * phases[np.newaxis, :]
        diagonalization_seconds = time.perf_counter() - diagonalization_started
        half = point.root_count
        u00 = unitary[:half, :half]
        u10 = unitary[half:, :half]
        maximum_isometry_residual = float(
            np.linalg.norm(unitary.conj().T @ unitary - np.eye(point.dimension))
            / point.dimension
        )
        if verbose:
            print(f"solving homogeneous pencil with {point.root_count} roots", flush=True)
        pencil_started = time.perf_counter()
        spectrum = generalized_relative_evolution_spectrum(
            u00,
            u10,
            audit_root_indices=[0],
            assess_regularity=point.root_count <= 512,
            maximum_duplicate_roots=512,
        )
        pencil_seconds = time.perf_counter() - pencil_started
        alpha = spectrum.alpha
        beta = spectrum.beta
        radii = spectrum.radii
        finite = spectrum.finite
        infinite = spectrum.infinite
        indeterminate = spectrum.indeterminate
        maximum_residual = spectrum.maximum_homogeneous_residual
        _require_left_diagnostics(spectrum.left_diagnostics_available)
        maximum_left_residual = spectrum.maximum_left_homogeneous_residual
        condition_number = spectrum.condition_number_u00
        near_singular = spectrum.near_singular_u00_warning
        regularity = spectrum.regularity_audit
        regularity_status = regularity.status if regularity else "not_audited"
        representative_nullity = (
            spectrum.root_audits[0].nullity if spectrum.root_audits else None
        )
        duplicates_performed = spectrum.duplicate_diagnostics.performed
        largest_multiplicity = spectrum.duplicate_diagnostics.largest_multiplicity
        energy_min = energy_max = None
        sector_count = 1
        hermiticity_residual = None
    elif point.backend == "numpy_dense":
        hamiltonian = build_single_pixel_hamiltonian(point)
        hermiticity_residual: float | None = float(
            np.linalg.norm(hamiltonian - hamiltonian.conj().T)
            / max(np.linalg.norm(hamiltonian), 1.0)
        )
        energies, eigenvectors = np.linalg.eigh(hamiltonian)
        diagonalization_seconds = time.perf_counter() - diagonalization_started
        u00, u10 = evolution_subblocks_from_eigenbasis(
            energies,
            eigenvectors,
            point.time,
        )
        if verbose:
            print(f"solving homogeneous pencil with {point.root_count} roots", flush=True)
        pencil_started = time.perf_counter()
        spectrum = generalized_relative_evolution_spectrum(
            u00,
            u10,
            audit_root_indices=[0],
            assess_regularity=point.root_count <= 512,
            maximum_duplicate_roots=512,
        )
        pencil_seconds = time.perf_counter() - pencil_started
        alpha = spectrum.alpha
        beta = spectrum.beta
        radii = spectrum.radii
        finite = spectrum.finite
        infinite = spectrum.infinite
        indeterminate = spectrum.indeterminate
        maximum_residual = spectrum.maximum_homogeneous_residual
        _require_left_diagnostics(spectrum.left_diagnostics_available)
        maximum_left_residual = spectrum.maximum_left_homogeneous_residual
        condition_number = spectrum.condition_number_u00
        near_singular = spectrum.near_singular_u00_warning
        regularity = spectrum.regularity_audit
        regularity_status = (
            regularity.status if regularity is not None else "not_audited"
        )
        representative_nullity = (
            spectrum.root_audits[0].nullity if spectrum.root_audits else None
        )
        duplicates_performed = spectrum.duplicate_diagnostics.performed
        largest_multiplicity = spectrum.duplicate_diagnostics.largest_multiplicity
        energy_min, energy_max = float(energies[0]), float(energies[-1])
        sector_count = 1
        maximum_isometry_residual = None
    else:
        from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
        from collapse.relative_evolution_sector import generalized_relative_evolution_from_sectors

        coupling = point.effective_central_couplings()
        generator = SinglePixelHamiltonianQuSpin(
            N_pixel=point.detector_n,
            J=point.J,
            Jpm=point.Jpm,
            J2=point.J2,
            Jpm2=point.Jpm2,
            Jxx=point.Jxx,
            Jyy=point.Jyy,
            Jx=coupling["Jx"],
            Jy=coupling["Jy"],
            Jz=coupling["Jz"],
            Jzx=coupling["Jzx"],
            Jcpm=coupling["Jcpm"],
            hx=point.hx,
            hz=point.hz,
            hx0=point.hx0,
            hz0=point.hz0,
            connectivity=point.connectivity,
            graph_spec=point.detector_graph_spec(),
            central_coupling=point.central_coupling,
            seed=point.seed,
            use_symmetry=True,
        )
        sectors = generator.diagonalize_sectors()
        if not all(bool(sector.get("relative_evolution_local", False)) for sector in sectors):
            raise ValueError(
                "quspin_sectors backend currently requires sectors local to the "
                "relative-evolution pencil"
            )
        diagonalization_seconds = time.perf_counter() - diagonalization_started
        if verbose:
            print(
                f"solving {len(sectors)} symmetry-sector pencils with "
                f"{point.root_count} total roots",
                flush=True,
            )
        pencil_started = time.perf_counter()
        aggregate = generalized_relative_evolution_from_sectors(
            sectors,
            point.time,
            point.total_qubits,
            compare_direct=False,
        )
        pencil_seconds = time.perf_counter() - pencil_started
        alpha = np.concatenate([item.alpha for item in aggregate.spectra])
        beta = np.concatenate([item.beta for item in aggregate.spectra])
        radii = aggregate.radii
        finite = aggregate.finite
        infinite = aggregate.infinite
        indeterminate = aggregate.indeterminate
        maximum_residual = aggregate.maximum_homogeneous_residual
        _require_left_diagnostics(
            all(item.left_diagnostics_available for item in aggregate.spectra)
        )
        # np.max, not the builtin: max() over a generator containing NaN returns
        # a different answer depending on which element comes first.
        maximum_left_residual = float(
            np.max(
                [
                    item.maximum_left_homogeneous_residual
                    for item in aggregate.spectra
                ]
            )
        )
        condition_number = aggregate.maximum_condition_number_u00
        near_singular = any(item.near_singular_u00_warning for item in aggregate.spectra)
        regularity_status = "not_audited_sector_aggregate"
        representative_nullity = None
        duplicates_performed = False
        largest_multiplicity = 0
        all_energies = np.concatenate([np.asarray(sector["E"]) for sector in sectors])
        energy_min, energy_max = float(np.min(all_energies)), float(np.max(all_energies))
        sector_count = len(sectors)
        maximum_isometry_residual = aggregate.maximum_column_isometry_residual
        hermiticity_residual = None

    if alpha.size != point.root_count:
        raise RuntimeError("unexpected projective root count")
    determined = ~indeterminate
    bloch = bloch_vectors_from_homogeneous(
        alpha[determined],
        beta[determined],
    )
    histogram = diagnose_labeled_bloch_histogram(
        bloch,
        n_phi=point.n_phi,
        n_mu=point.n_mu,
        l_max=point.l_max,
        harmonic_estimator="weighted_least_squares",
        require_full_coverage=True,
    )
    sphere = histogram.diagnostics
    all_affine_finite = bool(np.all(finite))
    polar = diagnostics_from_radii(radii) if all_affine_finite else None
    qz_valid = bool(
        not np.any(indeterminate)
        and maximum_residual < 1.0e-10
        and maximum_left_residual < 1.0e-10
        and regularity_status
        not in {"numerically_singular_at_all_samples"}
    )
    summary: dict[str, Any] = {
        "schema_version": 2,
        "family": (
            "haar_unitary_null" if point.backend == "haar_unitary" else "single_pixel"
        ),
        "N": point.detector_n,
        "dimension": point.dimension,
        "time": point.time,
        "parameters": asdict(point),
        "effective_central_couplings_per_edge": point.effective_central_couplings(),
        "seed": point.seed,
        "backend": point.backend,
        "sector_count": sector_count,
        "root_count": int(alpha.size),
        "finite_roots": int(np.count_nonzero(finite)),
        "infinite_roots": int(np.count_nonzero(infinite)),
        "indeterminate_roots": int(np.count_nonzero(indeterminate)),
        "qz_valid": qz_valid,
        "maximum_qz_backward_residual": maximum_residual,
        "maximum_qz_left_backward_residual": maximum_left_residual,
        "maximum_column_isometry_residual": maximum_isometry_residual,
        "condition_number_u00": condition_number,
        "near_singular_u00_warning": near_singular,
        "regularity_status": regularity_status,
        "representative_root_nullity": representative_nullity,
        "duplicate_diagnostics_performed": duplicates_performed,
        "largest_root_multiplicity": largest_multiplicity,
        "coverage": histogram.coverage,
        "density_ratio_cross_residual": (
            histogram.born_density_ratio_cross_residual
        ),
        "epsilon_antipodal": sphere.epsilon_antipodal if sphere else None,
        "epsilon_B": sphere.born_rms_density_weighted if sphere else None,
        "higher_harmonic_leakage": (
            sphere.higher_odd_harmonic_leakage if sphere else None
        ),
        "dipole_vector": sphere.dipole_vector.tolist() if sphere else None,
        "dipole_sharpness": sphere.dipole_sharpness if sphere else None,
        "axis_fidelity": sphere.axis_fidelity if sphere else None,
        "P1_over_Podd": sphere.p1_over_podd if sphere else None,
        "polar_S_born": polar.born_similarity if polar else None,
        "hermiticity_residual": hermiticity_residual,
        "energy_min": energy_min,
        "energy_max": energy_max,
        "selection_measure_status": "not supplied",
        "timing_seconds": {
            "diagonalization": diagonalization_seconds,
            "pencil": pencil_seconds,
            "total": time.perf_counter() - started,
        },
    }
    return ClassificationPointResult(
        summary=summary,
        alpha=alpha,
        beta=beta,
        bloch_vectors_0=bloch,
        asymmetry=histogram.asymmetry,
        power_by_l=sphere.power_by_l if sphere else np.array([], dtype=float),
    )
