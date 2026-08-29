"""Analytical-numerical utilities for the relative-evolution matrix study.

All Hamiltonians in this module use the repository convention

    H = -hz0 Z0 - hz sum_i Zi - J sum_i Zi Z(i+1)
        - Jpm sum_i (sigma_i^+ sigma_(i+1)^- + h.c.)
        - (Jx/sqrt(N)) X0 sum_i Xi,

with a periodic detector ring and ``sigma^+ = (X+iY)/2``.  ``Jx`` is the
collective, unscaled coupling recorded in configurations.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import time
from typing import Iterable

import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import wasserstein_distance

from core.detector_resonance import (
    DenseRingDetectorBuilder,
    DetectorOperators,
    DetectorSpec,
    SpectralProjectorAnalyzer,
)
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.relative_evolution_pencil import matched_projective_angle_error
from core.relative_evolution_sector import (
    SectorPencilAggregate,
    generalized_relative_evolution_from_sectors,
)


@dataclass(frozen=True)
class RelativeEvolutionCase:
    """One clean periodic central-qubit/detector Hamiltonian."""

    key: str
    model: str
    description: str
    hz: float
    j: float
    jpm: float
    hz0: float
    collective_jx: float = 0.01

    def __post_init__(self) -> None:
        values = (self.hz, self.j, self.jpm, self.hz0, self.collective_jx)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("case parameters must be finite")
        if self.collective_jx < 0.0:
            raise ValueError("collective_jx must be nonnegative")


@dataclass(frozen=True)
class AngularHistogram:
    """Finite-bin visualization of an exact empirical angular measure."""

    edges: np.ndarray
    centers: np.ndarray
    counts: np.ndarray
    reflected_counts: np.ndarray
    density: np.ndarray
    reflected_density: np.ndarray
    ratio: np.ndarray
    occupied: np.ndarray
    born: np.ndarray
    born_similarity: float
    occupied_rmse: float
    occupied_mean_absolute_error: float
    coverage: float
    entropy_normalized: float
    support_fraction: float
    sample_count: int


@dataclass(frozen=True)
class SnapshotResult:
    """One exact finite-N projective spectrum and derived diagnostics."""

    case: RelativeEvolutionCase
    detector_n: int
    time: float
    spectrum: SectorPencilAggregate
    histogram: AngularHistogram
    elapsed_seconds: float


@dataclass(frozen=True)
class DetectorResonanceResult:
    """Basis-invariant detector spectral weights relevant at first order."""

    dimension: int
    distinct_energies: int
    maximum_multiplicity: int
    zero_gap_weight_fraction: float
    resonant_weight_fraction: float
    nearest_active_detuning: float
    target_signed_gap: float


def default_cases() -> tuple[RelativeEvolutionCase, ...]:
    """Return representative regimes already used in earlier project studies."""

    return (
        RelativeEvolutionCase(
            "m1_j0", "Model 1", "independent detector spins (J=0)",
            hz=1.0, j=0.0, jpm=0.0, hz0=0.0,
        ),
        RelativeEvolutionCase(
            "m1_ising_generic", "Model 1", "interacting Ising, generic field",
            hz=0.7, j=1.0, jpm=0.0, hz0=0.0,
        ),
        RelativeEvolutionCase(
            "m1_ising_degenerate", "Model 1", "interacting Ising, zero-gap line hz=0",
            hz=0.0, j=1.0, jpm=0.0, hz0=0.0,
        ),
        RelativeEvolutionCase(
            "m2_matched", "Model 2", "central-field resonance hz0=hz",
            hz=0.1, j=1.0, jpm=0.0, hz0=0.1,
        ),
        RelativeEvolutionCase(
            "m2_detuned", "Model 2", "30 percent central-field detuning",
            hz=0.1, j=1.0, jpm=0.0, hz0=0.13,
        ),
        RelativeEvolutionCase(
            "m3_flipflop", "Model 3", "integrable detector XY limit",
            hz=0.1, j=0.0, jpm=1.0, hz0=0.0,
        ),
        RelativeEvolutionCase(
            "m4_xxz", "Model 4", "XXZ detector with generic transverse conditional field",
            hz=0.1, j=1.0, jpm=0.3, hz0=0.0,
        ),
        RelativeEvolutionCase(
            "m4_su2", "Model 4", "isotropic detector line Jpm=2J",
            hz=0.1, j=1.0, jpm=2.0, hz0=0.0,
        ),
    )


def build_sector_eigenbases(
    case: RelativeEvolutionCase,
    detector_n: int,
) -> tuple[list[dict], float]:
    """Diagonalize the full Hamiltonian in detector-translation sectors."""

    if detector_n < 2:
        raise ValueError("detector_n must be at least two")
    started = time.perf_counter()
    hamiltonian = SinglePixelHamiltonianQuSpin(
        N_pixel=detector_n,
        J=case.j,
        Jpm=case.jpm,
        Jx=case.collective_jx / math.sqrt(detector_n),
        Jy=0.0,
        Jz=0.0,
        Jzx=0.0,
        hx=0.0,
        hz=case.hz,
        hx0=0.0,
        hz0=case.hz0,
        connectivity="ring",
        central_coupling="all",
        seed=44,
        use_symmetry=True,
    )
    sectors = hamiltonian.diagonalize_sectors()
    if not all(item.get("symmetry_label") == "pixel_shift" for item in sectors):
        raise RuntimeError("clean ring calculation did not use detector translation sectors")
    return sectors, time.perf_counter() - started


def angular_histogram(theta: np.ndarray, bins: int = 48) -> AngularHistogram:
    """Histogram an empirical projective-angle measure without smoothing.

    Empty reflection-ratio bins are represented by NaN and excluded from the
    occupied-bin RMSE.  The legacy project score retains its documented 1/2
    convention in empty bins so it remains comparable to prior reports.
    """

    if bins < 4:
        raise ValueError("bins must be at least four")
    values = np.asarray(theta, dtype=float).ravel()
    values = values[np.isfinite(values)]
    values = values[(values >= 0.0) & (values <= np.pi)]
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    counts, _ = np.histogram(values, bins=edges)
    reflected_counts, _ = np.histogram(np.pi - values, bins=edges)
    normalizer = max(values.size, 1)
    density = counts / (normalizer * widths)
    reflected_density = reflected_counts / (normalizer * widths)
    denominator = counts + reflected_counts
    ratio = np.divide(
        counts,
        denominator,
        out=np.full(counts.shape, np.nan, dtype=float),
        where=denominator > 0,
    )
    occupied = denominator > 0
    born = np.cos(centers / 2.0) ** 2
    differences = ratio[occupied] - born[occupied]
    rmse = float(np.sqrt(np.mean(differences**2))) if differences.size else np.nan
    mae = float(np.mean(np.abs(differences))) if differences.size else np.nan

    legacy_ratio = np.where(occupied, ratio, 0.5)
    legacy_error = np.abs(legacy_ratio - born)
    born_similarity = 1.0 - 2.0 * float(
        np.sum(legacy_error * np.sin(centers)) * widths[0]
    )
    probabilities = counts.astype(float) / max(int(np.sum(counts)), 1)
    nonzero = probabilities > 0.0
    entropy = -float(np.sum(probabilities[nonzero] * np.log(probabilities[nonzero])))
    normalized_entropy = entropy / math.log(bins) if bins > 1 else np.nan
    return AngularHistogram(
        edges=edges,
        centers=centers,
        counts=counts,
        reflected_counts=reflected_counts,
        density=density,
        reflected_density=reflected_density,
        ratio=ratio,
        occupied=occupied,
        born=born,
        born_similarity=born_similarity,
        occupied_rmse=rmse,
        occupied_mean_absolute_error=mae,
        coverage=float(np.mean(occupied)),
        entropy_normalized=normalized_entropy,
        support_fraction=float(np.mean(counts > 0)),
        sample_count=int(values.size),
    )


def evaluate_snapshot(
    case: RelativeEvolutionCase,
    detector_n: int,
    time_value: float,
    sectors: list[dict],
    *,
    bins: int = 48,
    compare_direct: bool = False,
) -> SnapshotResult:
    """Evaluate an exact finite-N spectrum at one finite time."""

    started = time.perf_counter()
    spectrum = generalized_relative_evolution_from_sectors(
        sectors,
        float(time_value),
        detector_n + 1,
        compare_direct=compare_direct,
    )
    histogram = angular_histogram(spectrum.theta, bins=bins)
    return SnapshotResult(
        case=case,
        detector_n=detector_n,
        time=float(time_value),
        spectrum=spectrum,
        histogram=histogram,
        elapsed_seconds=time.perf_counter() - started,
    )


def midpoint_time_grid(final_time: float, samples: int) -> np.ndarray:
    """Midpoint-rule grid on ``[0, final_time]``."""

    if final_time <= 0.0 or samples <= 0:
        raise ValueError("final_time and samples must be positive")
    step = final_time / samples
    return (np.arange(samples, dtype=float) + 0.5) * step


def evaluate_time_average(
    case: RelativeEvolutionCase,
    detector_n: int,
    sectors: list[dict],
    times: Iterable[float],
    *,
    bins: int = 48,
) -> tuple[AngularHistogram, list[SnapshotResult]]:
    """Approximate the time-averaged empirical measure by equal quadrature."""

    snapshots = [
        evaluate_snapshot(case, detector_n, float(value), sectors, bins=bins)
        for value in times
    ]
    if not snapshots:
        raise ValueError("times must contain at least one value")
    pooled = np.concatenate([item.spectrum.theta for item in snapshots])
    return angular_histogram(pooled, bins=bins), snapshots


def histogram_distances(
    first: AngularHistogram,
    second: AngularHistogram,
) -> dict[str, float]:
    """Compare equal-bin angular measures by L1 and Jensen-Shannon distance."""

    if not np.allclose(first.edges, second.edges):
        raise ValueError("histograms must use identical edges")
    widths = np.diff(first.edges)
    l1 = float(np.sum(np.abs(first.density - second.density) * widths))
    p = first.counts / max(int(np.sum(first.counts)), 1)
    q = second.counts / max(int(np.sum(second.counts)), 1)
    js = float(jensenshannon(p, q, base=2.0) ** 2)
    return {"histogram_l1": l1, "jensen_shannon": js}


def theta_wasserstein(first: np.ndarray, second: np.ndarray) -> float:
    """Return the Wasserstein-1 distance between finite angle samples."""

    a = np.asarray(first, dtype=float)
    b = np.asarray(second, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if not a.size or not b.size:
        return np.nan
    return float(wasserstein_distance(a, b))


def weak_first_order_matrix(
    case: RelativeEvolutionCase,
    detector_n: int,
    time_value: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r"""Return the first-order ``M`` matrix in the detector energy basis.

    With ``g=Jx/sqrt(N)`` and repository signs,

    ``M1_ab = i g exp(-2 i hz0 t) B_ab F_t(Ea-Eb+2 hz0)``,

    where ``F_t(delta)=(exp(i delta t)-1)/(i delta)`` and ``F_t(0)=t``.
    The approximation is first order in ``g`` and is not uniform when
    ``g t`` is order one in a resonant block.
    """

    displayed = DenseRingDetectorBuilder().build(
        DetectorSpec(detector_n, case.hz, case.j, case.jpm)
    )
    detector_hamiltonian = -np.asarray(displayed.hamiltonian, dtype=float)
    energies, vectors = np.linalg.eigh(detector_hamiltonian)
    coupling = vectors.conj().T @ displayed.coupling @ vectors
    delta = energies[:, None] - energies[None, :] + 2.0 * case.hz0
    kernel = np.empty_like(delta, dtype=np.complex128)
    small = np.abs(delta) <= 1.0e-12
    kernel[small] = float(time_value)
    kernel[~small] = np.expm1(1j * delta[~small] * time_value) / (1j * delta[~small])
    edge = case.collective_jx / math.sqrt(detector_n)
    matrix = 1j * edge * np.exp(-2j * case.hz0 * time_value) * coupling * kernel
    return matrix, energies, coupling


def compare_first_order_to_exact(snapshot: SnapshotResult) -> dict[str, float]:
    """Compare first-order and exact finite-N angle distributions."""

    matrix, _, _ = weak_first_order_matrix(
        snapshot.case, snapshot.detector_n, snapshot.time
    )
    approximate_theta = 2.0 * np.arctan(np.abs(np.linalg.eigvals(matrix)))
    exact_theta = snapshot.spectrum.theta[np.isfinite(snapshot.spectrum.theta)]
    maximum, rms = matched_projective_angle_error(exact_theta, approximate_theta)
    return {
        "maximum_matched_angle_error": maximum,
        "rms_matched_angle_error": rms,
        "wasserstein_angle_error": theta_wasserstein(exact_theta, approximate_theta),
    }


def detector_resonance_summary(
    case: RelativeEvolutionCase,
    detector_n: int,
    *,
    tolerance: float = 1.0e-9,
) -> DetectorResonanceResult:
    """Compute basis-invariant coupling weight at the first-order resonance."""

    displayed = DenseRingDetectorBuilder().build(
        DetectorSpec(detector_n, case.hz, case.j, case.jpm)
    )
    operators = DetectorOperators(
        hamiltonian=-np.asarray(displayed.hamiltonian, dtype=float),
        coupling=np.asarray(displayed.coupling, dtype=float),
    )
    analyzer = SpectralProjectorAnalyzer(
        degeneracy_tolerance=tolerance,
        weight_tolerance=1.0e-12,
    )
    subspaces = analyzer.energy_subspaces(operators.hamiltonian)
    transitions = analyzer.active_transitions(subspaces, operators.coupling)
    total = float(sum(item.weight for item in transitions))
    target = -2.0 * case.hz0
    resonant = float(
        sum(item.weight for item in transitions if abs(item.gap - target) <= tolerance)
    )
    zero = float(
        sum(item.weight for item in transitions if abs(item.gap) <= tolerance)
    )
    nearest = min(
        (abs(item.gap - target) for item in transitions),
        default=float("inf"),
    )
    multiplicities = [item.multiplicity for item in subspaces]
    return DetectorResonanceResult(
        dimension=2**detector_n,
        distinct_energies=len(subspaces),
        maximum_multiplicity=max(multiplicities, default=0),
        zero_gap_weight_fraction=zero / total if total else 0.0,
        resonant_weight_fraction=resonant / total if total else 0.0,
        nearest_active_detuning=float(nearest),
        target_signed_gap=target,
    )


def exact_zero_field_j0_angles(
    detector_n: int,
    collective_jx: float,
    time_value: float,
) -> np.ndarray:
    r"""Exact angles for ``J=Jpm=hz=hz0=0`` with binomial multiplicity.

    Here ``M=i tan[g t sum_i X_i]`` away from its poles and the projective
    formula remains valid at the poles.
    """

    edge = collective_jx / math.sqrt(detector_n)
    angles: list[float] = []
    for flipped in range(detector_n + 1):
        b = detector_n - 2 * flipped
        alpha = abs(math.sin(edge * b * time_value))
        beta = abs(math.cos(edge * b * time_value))
        theta = 2.0 * math.atan2(alpha, beta)
        angles.extend([theta] * math.comb(detector_n, flipped))
    return np.asarray(angles, dtype=float)
