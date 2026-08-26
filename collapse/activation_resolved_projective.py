r"""Activation-resolved projective diagnostics for clean ring detectors.

The central interaction is

.. math::

   V=-J_x^{\rm eff}X_0\sum_jX_j,

so detector momentum is conserved while detector magnetisation changes by one.
This module resolves the isolated detector in ``(k, N_up)`` blocks, constructs
a basis-invariant finite-time activation operator inside every degenerate
energy subspace, and uses its eigenchannels to partition the right
eigenvectors of the relative-evolution matrix into weak, intermediate, and
strongly activated components.

The activation partition is not an additional conserved symmetry.  It is an
orthogonal decomposition of each projective root's initial detector vector.
Consequently its weighted histograms reconstruct the unconditioned histogram,
but the components do not evolve independently under the original Hamiltonian.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Callable, Sequence

import numpy as np
from scipy import sparse
from scipy.optimize import minimize

from collapse.hamiltonians.numpy_hamiltonians import (
    _pixel_bonds,
    _pixel_ring_second_neighbor_bonds,
)


ProgressCallback = Callable[[str], None]


@dataclass(frozen=True)
class RingActivationParameters:
    """Physical parameters for one clean single-pixel ring.

    ``jx_unscaled`` is the source parameter.  The full Hamiltonian and the
    activation operator both use ``jx_unscaled/sqrt(detector_n)`` exactly once.
    """

    hz: float
    hz0: float
    j: float
    jpm: float
    jx_unscaled: float
    evolution_time: float
    j2: float = 0.0
    jpm2: float = 0.0

    def effective_jx(self, detector_n: int) -> float:
        if detector_n < 3:
            raise ValueError("detector_n must be at least three")
        return float(self.jx_unscaled) / math.sqrt(detector_n)


@dataclass
class DetectorMagnetizationSector:
    """One isolated-detector ``(k, N_up)`` eigensystem."""

    n_up: int
    momentum: int
    basis: Any
    projector: sparse.csc_matrix
    energies: np.ndarray
    eigenvectors: np.ndarray
    activation_scores: np.ndarray

    @property
    def dimension(self) -> int:
        return int(self.energies.size)


@dataclass(frozen=True)
class DetectorMomentumActivation:
    """Canonical activation eigenchannels for one detector momentum."""

    momentum: int
    sectors: tuple[DetectorMagnetizationSector, ...]
    degeneracy_tolerance: float
    minimum_activation_eigenvalue: float
    maximum_activation_hermiticity_residual: float

    @property
    def scores(self) -> np.ndarray:
        if not self.sectors:
            return np.empty(0, dtype=float)
        return np.concatenate([sector.activation_scores for sector in self.sectors])

    @property
    def energies(self) -> np.ndarray:
        if not self.sectors:
            return np.empty(0, dtype=float)
        return np.concatenate([sector.energies for sector in self.sectors])


@dataclass(frozen=True)
class ActivationPartition:
    """Global score thresholds defining an orthogonal channel partition."""

    labels: tuple[str, ...]
    lower_quantile: float
    upper_quantile: float
    lower_threshold: float
    upper_threshold: float
    channel_counts: tuple[int, ...]

    def class_indices(self, scores: np.ndarray) -> np.ndarray:
        values = np.asarray(scores, dtype=float)
        # Keeping threshold ties in one class makes the classification
        # invariant under permutations of equally bright eigenchannels.
        return np.where(
            values <= self.lower_threshold,
            0,
            np.where(values <= self.upper_threshold, 1, 2),
        ).astype(np.int8)


@dataclass(frozen=True)
class MomentumProjectiveComponents:
    """Relative roots and their activation-class weights for one momentum."""

    momentum: int
    eigenvalues: np.ndarray
    theta: np.ndarray
    class_weights: np.ndarray
    pencil_condition_number: float
    eigenvector_condition_number: float
    maximum_eigenpair_residual: float
    maximum_weight_sum_error: float
    detector_basis_completeness_error: float


@dataclass(frozen=True)
class WeightedProjectiveDiagnostics:
    """Weighted ``P(theta)`` and complementary-angle ratio diagnostics."""

    label: str
    edges: np.ndarray
    centers: np.ndarray
    p_theta: np.ndarray
    p_pi_minus_theta: np.ndarray
    ratio: np.ndarray
    occupied: np.ndarray
    born: np.ndarray
    residual: np.ndarray
    total_weight: float
    effective_root_count: float
    similarity: float
    rmse_occupied: float
    l1_occupied: float
    occupied_fraction: float


@dataclass(frozen=True)
class WeightedAngularFits:
    """Reflection-augmented weighted WG/WC harmonic fits."""

    grid: np.ndarray
    wrapped_gaussian_density: np.ndarray
    wrapped_cauchy_density: np.ndarray
    wrapped_gaussian: dict[str, Any]
    wrapped_cauchy: dict[str, Any]


def detector_translation(detector_n: int) -> np.ndarray:
    """Return the one-site cyclic permutation on detector sites."""

    if detector_n < 2:
        raise ValueError("detector_n must be at least two")
    return np.asarray([(site + 1) % detector_n for site in range(detector_n)])


def full_pixel_translation(detector_n: int) -> np.ndarray:
    """Return the detector shift with central site zero held fixed."""

    permutation = np.arange(detector_n + 1)
    for site in range(detector_n):
        permutation[1 + site] = 1 + (site + 1) % detector_n
    return permutation


def detector_static_terms(
    detector_n: int,
    parameters: RingActivationParameters,
) -> list[list[Any]]:
    """Construct the isolated detector with the simulation sign convention."""

    nearest = _pixel_bonds(0, detector_n, "ring")
    second = _pixel_ring_second_neighbor_bonds(0, detector_n)
    static: list[list[Any]] = []
    if parameters.j:
        static.append(["zz", [[-parameters.j, left, right] for left, right in nearest]])
    if parameters.jpm:
        exchange = [[-parameters.jpm / 4.0, left, right] for left, right in nearest]
        static.extend((["+-", exchange], ["-+", exchange]))
    if parameters.j2:
        static.append(["zz", [[-parameters.j2, left, right] for left, right in second]])
    if parameters.jpm2:
        exchange2 = [[-parameters.jpm2 / 4.0, left, right] for left, right in second]
        static.extend((["+-", exchange2], ["-+", exchange2]))
    if parameters.hz:
        static.append(["z", [[-parameters.hz, site] for site in range(detector_n)]])
    return static


def finite_time_transition_kernel(detuning: np.ndarray, time: float) -> np.ndarray:
    r"""Return ``4 sin^2(delta t/2)/delta^2`` with its exact zero limit."""

    if not np.isfinite(time) or time < 0.0:
        raise ValueError("time must be finite and nonnegative")
    delta = np.asarray(detuning, dtype=float)
    argument = 0.5 * delta * float(time)
    result = np.empty_like(delta)
    small = np.abs(argument) <= 1.0e-6
    # sinc(x)=sin(pi*x)/(pi*x), so this expression is stable at zero.
    result[small] = float(time) ** 2 * np.sinc(argument[small] / np.pi) ** 2
    result[~small] = 4.0 * np.sin(argument[~small]) ** 2 / delta[~small] ** 2
    return result


def central_flip_activation_kernel(
    detector_gap: np.ndarray,
    hz0: float,
    time: float,
) -> np.ndarray:
    """Average the two central-qubit flip directions at gaps ``+/-2 hz0``."""

    gap = np.asarray(detector_gap, dtype=float)
    omega = 2.0 * float(hz0)
    return 0.5 * (
        finite_time_transition_kernel(gap - omega, time)
        + finite_time_transition_kernel(gap + omega, time)
    )


def _energy_groups(energies: np.ndarray, tolerance: float) -> tuple[np.ndarray, ...]:
    values = np.asarray(energies, dtype=float)
    output: list[np.ndarray] = []
    start = 0
    while start < values.size:
        stop = start + 1
        while stop < values.size and abs(float(values[stop] - values[start])) <= tolerance:
            stop += 1
        output.append(np.arange(start, stop, dtype=np.int64))
        start = stop
    return tuple(output)


def _collect_detector_sectors(
    detector_n: int,
    momentum: int,
    parameters: RingActivationParameters,
) -> list[DetectorMagnetizationSector]:
    from quspin.basis import spin_basis_general
    from quspin.operators import hamiltonian

    translation = detector_translation(detector_n)
    static = detector_static_terms(detector_n, parameters)
    output: list[DetectorMagnetizationSector] = []
    for n_up in range(detector_n + 1):
        basis = spin_basis_general(
            detector_n,
            Nup=n_up,
            kblock=(translation, momentum),
        )
        if basis.Ns == 0:
            continue
        operator = hamiltonian(
            static,
            [],
            basis=basis,
            dtype=np.complex128,
            check_symm=False,
            check_herm=False,
            check_pcon=False,
        )
        energies, eigenvectors = np.linalg.eigh(operator.toarray())
        output.append(
            DetectorMagnetizationSector(
                n_up=n_up,
                momentum=momentum,
                basis=basis,
                projector=basis.get_proj(np.complex128),
                energies=np.asarray(energies, dtype=float),
                eigenvectors=np.asarray(eigenvectors, dtype=np.complex128),
                activation_scores=np.zeros(energies.size, dtype=float),
            )
        )
    return output


def _collective_x_operator(detector_n: int) -> sparse.csr_matrix:
    from quspin.basis import spin_basis_general
    from quspin.operators import hamiltonian

    basis = spin_basis_general(detector_n)
    operator = hamiltonian(
        [["x", [[1.0, site] for site in range(detector_n)]]],
        [],
        basis=basis,
        dtype=np.float64,
        check_symm=False,
        check_herm=False,
        check_pcon=False,
    )
    return operator.tocsr()


def detector_momentum_activation(
    detector_n: int,
    momentum: int,
    parameters: RingActivationParameters,
    collective_x: sparse.csr_matrix | None = None,
) -> DetectorMomentumActivation:
    """Diagonalize the canonical finite-time activation operator at one ``k``.

    Within an exactly degenerate detector energy subspace, individual
    eigensolver vectors are arbitrary.  We therefore accumulate the positive
    activation matrix in that subspace and diagonalize it.  Its eigenvalues
    and eigenchannels are invariant under a prior unitary rotation of the
    degenerate energy basis.
    """

    if momentum < 0 or momentum >= detector_n:
        raise ValueError("momentum is outside the cyclic range")
    sectors = _collect_detector_sectors(detector_n, momentum, parameters)
    coupling = collective_x if collective_x is not None else _collective_x_operator(detector_n)
    scale = max(
        (float(np.ptp(sector.energies)) for sector in sectors if sector.dimension),
        default=1.0,
    )
    degeneracy_tolerance = 1.0e-10 * max(scale, 1.0)
    activation_blocks = [
        np.zeros((sector.dimension, sector.dimension), dtype=np.complex128)
        for sector in sectors
    ]
    jx_squared = parameters.effective_jx(detector_n) ** 2

    for left_index, (source, target) in enumerate(zip(sectors[:-1], sectors[1:])):
        if target.n_up != source.n_up + 1:
            raise RuntimeError("detector magnetization sectors are not adjacent")
        reduced = target.projector.conj().T @ (coupling @ source.projector)
        energy_block = target.eigenvectors.conj().T @ (
            reduced @ source.eigenvectors
        )

        for group in _energy_groups(source.energies, degeneracy_tolerance):
            energy = float(np.mean(source.energies[group]))
            amplitudes = energy_block[:, group]
            kernel = central_flip_activation_kernel(
                target.energies - energy,
                parameters.hz0,
                parameters.evolution_time,
            )
            activation_blocks[left_index][np.ix_(group, group)] += (
                jx_squared * amplitudes.conj().T @ (kernel[:, None] * amplitudes)
            )

        for group in _energy_groups(target.energies, degeneracy_tolerance):
            energy = float(np.mean(target.energies[group]))
            amplitudes = energy_block[group, :]
            kernel = central_flip_activation_kernel(
                energy - source.energies,
                parameters.hz0,
                parameters.evolution_time,
            )
            activation_blocks[left_index + 1][np.ix_(group, group)] += (
                jx_squared * (amplitudes * kernel[None, :]) @ amplitudes.conj().T
            )

    minimum_eigenvalue = 0.0
    maximum_hermiticity = 0.0
    for sector, activation in zip(sectors, activation_blocks, strict=True):
        hermiticity = float(
            np.linalg.norm(activation - activation.conj().T)
            / max(np.linalg.norm(activation), 1.0)
        )
        maximum_hermiticity = max(maximum_hermiticity, hermiticity)
        rotated = np.array(sector.eigenvectors, copy=True)
        scores = np.empty(sector.dimension, dtype=float)
        for group in _energy_groups(sector.energies, degeneracy_tolerance):
            block = 0.5 * (
                activation[np.ix_(group, group)]
                + activation[np.ix_(group, group)].conj().T
            )
            values, vectors = np.linalg.eigh(block)
            minimum_eigenvalue = min(minimum_eigenvalue, float(np.min(values)))
            tolerance = 1.0e-11 * max(float(np.max(np.abs(values))), 1.0)
            if float(np.min(values)) < -tolerance:
                raise RuntimeError("activation operator is not positive semidefinite")
            scores[group] = np.maximum(values, 0.0)
            rotated[:, group] = sector.eigenvectors[:, group] @ vectors
        sector.eigenvectors = rotated
        sector.activation_scores = scores

    return DetectorMomentumActivation(
        momentum=momentum,
        sectors=tuple(sectors),
        degeneracy_tolerance=degeneracy_tolerance,
        minimum_activation_eigenvalue=minimum_eigenvalue,
        maximum_activation_hermiticity_residual=maximum_hermiticity,
    )


def all_detector_activation_channels(
    detector_n: int,
    parameters: RingActivationParameters,
    *,
    progress: ProgressCallback | None = None,
) -> tuple[DetectorMomentumActivation, ...]:
    """Return activation eigenchannels for every detector momentum."""

    coupling = _collective_x_operator(detector_n)
    output: list[DetectorMomentumActivation] = []
    for momentum in range(detector_n):
        if progress is not None:
            progress(f"detector activation k={momentum}/{detector_n - 1}")
        output.append(
            detector_momentum_activation(
                detector_n,
                momentum,
                parameters,
                collective_x=coupling,
            )
        )
    actual = sum(item.scores.size for item in output)
    expected = 2**detector_n
    if actual != expected:
        raise RuntimeError(f"activation channels have dimension {actual}, expected {expected}")
    return tuple(output)


def activation_quantile_partition(
    momenta: Sequence[DetectorMomentumActivation],
    lower_quantile: float = 0.2,
    upper_quantile: float = 0.8,
) -> ActivationPartition:
    """Partition canonical activation channels by global score quantiles."""

    if not 0.0 < lower_quantile < upper_quantile < 1.0:
        raise ValueError("activation quantiles must satisfy 0 < lower < upper < 1")
    scores = np.concatenate([item.scores for item in momenta])
    if scores.size == 0 or not np.all(np.isfinite(scores)):
        raise ValueError("activation scores must be nonempty and finite")
    lower, upper = np.quantile(scores, [lower_quantile, upper_quantile])
    temporary = ActivationPartition(
        labels=("weak", "intermediate", "strong"),
        lower_quantile=float(lower_quantile),
        upper_quantile=float(upper_quantile),
        lower_threshold=float(lower),
        upper_threshold=float(upper),
        channel_counts=(0, 0, 0),
    )
    classes = temporary.class_indices(scores)
    counts = tuple(int(np.count_nonzero(classes == index)) for index in range(3))
    if any(count == 0 for count in counts):
        raise RuntimeError(
            "activation quantiles produced an empty class; choose different quantiles"
        )
    return ActivationPartition(
        labels=temporary.labels,
        lower_quantile=temporary.lower_quantile,
        upper_quantile=temporary.upper_quantile,
        lower_threshold=temporary.lower_threshold,
        upper_threshold=temporary.upper_threshold,
        channel_counts=counts,
    )


def _full_hamiltonian_momentum_sector(
    detector_n: int,
    momentum: int,
    parameters: RingActivationParameters,
) -> tuple[Any, np.ndarray, np.ndarray]:
    from quspin.basis import spin_basis_general
    from quspin.operators import hamiltonian
    from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

    model = SinglePixelHamiltonianQuSpin(
        N_pixel=detector_n,
        J=parameters.j,
        Jpm=parameters.jpm,
        J2=parameters.j2,
        Jpm2=parameters.jpm2,
        Jx=parameters.effective_jx(detector_n),
        Jy=0.0,
        Jz=0.0,
        Jzx=0.0,
        hx=0.0,
        hz=parameters.hz,
        hx0=0.0,
        hz0=parameters.hz0,
        connectivity="ring",
        central_coupling="all",
        seed=44,
        use_symmetry=True,
    )
    static, total_qubits = model._build_static()
    if total_qubits != detector_n + 1:
        raise RuntimeError("full Hamiltonian dimension is inconsistent")
    basis = spin_basis_general(
        total_qubits,
        kblock=(full_pixel_translation(detector_n), momentum),
    )
    operator = hamiltonian(
        static,
        [],
        basis=basis,
        dtype=np.complex128,
        check_symm=False,
        check_herm=False,
        check_pcon=False,
    )
    energies, eigenvectors = np.linalg.eigh(operator.toarray())
    return basis, np.asarray(energies, dtype=float), np.asarray(eigenvectors, dtype=np.complex128)


def momentum_projective_components(
    detector_n: int,
    momentum_data: DetectorMomentumActivation,
    partition: ActivationPartition,
    parameters: RingActivationParameters,
) -> MomentumProjectiveComponents:
    """Compute relative roots and activation-class weights at one momentum."""

    momentum = momentum_data.momentum
    basis, energies, eigenvectors = _full_hamiltonian_momentum_sector(
        detector_n,
        momentum,
        parameters,
    )
    states = np.asarray(basis.states, dtype=np.int64)
    central_bits = (states >> detector_n) & 1
    top = np.where(central_bits == 1)[0]
    bottom = np.where(central_bits == 0)[0]
    if top.size != bottom.size or top.size == 0:
        raise RuntimeError("full momentum sector does not split into equal central slices")
    phases = np.exp(-1j * energies * parameters.evolution_time)
    top_vectors = eigenvectors[top, :]
    evolved_columns = (eigenvectors * phases) @ top_vectors.conj().T
    u00 = evolved_columns[top, :]
    u10 = evolved_columns[bottom, :]
    relative = np.linalg.solve(u00, u10)
    values, right_vectors = np.linalg.eig(relative)
    norms = np.linalg.norm(right_vectors, axis=0)
    if np.any(norms == 0.0):
        raise RuntimeError("relative eigenproblem returned a zero eigenvector")
    right_vectors /= norms[None, :]

    full_projector = basis.get_proj(np.complex128)
    detector_dimension = 2**detector_n
    top_map = full_projector[:detector_dimension, :][:, top]
    completeness = np.zeros((top.size, top.size), dtype=np.complex128)
    class_weights = np.zeros((len(partition.labels), values.size), dtype=float)
    for sector in momentum_data.sectors:
        coordinate_map = sector.projector.conj().T @ top_map
        completeness += (coordinate_map.conj().T @ coordinate_map).toarray()
        coefficients = sector.eigenvectors.conj().T @ (
            coordinate_map @ right_vectors
        )
        probabilities = np.abs(coefficients) ** 2
        classes = partition.class_indices(sector.activation_scores)
        for class_index in range(len(partition.labels)):
            class_weights[class_index] += np.sum(
                probabilities[classes == class_index, :], axis=0
            )
    identity = np.eye(top.size, dtype=np.complex128)
    completeness_error = float(
        np.linalg.norm(completeness - identity) / max(np.linalg.norm(identity), 1.0)
    )
    weight_error = float(np.max(np.abs(np.sum(class_weights, axis=0) - 1.0)))
    residuals = np.linalg.norm(
        relative @ right_vectors - right_vectors * values[None, :], axis=0
    ) / np.maximum(
        np.linalg.norm(relative) + np.abs(values),
        np.finfo(float).eps,
    )
    return MomentumProjectiveComponents(
        momentum=momentum,
        eigenvalues=np.asarray(values, dtype=np.complex128),
        theta=2.0 * np.arctan(np.abs(values)),
        class_weights=class_weights,
        pencil_condition_number=float(np.linalg.cond(u00)),
        eigenvector_condition_number=float(np.linalg.cond(right_vectors)),
        maximum_eigenpair_residual=float(np.max(residuals)),
        maximum_weight_sum_error=weight_error,
        detector_basis_completeness_error=completeness_error,
    )


def weighted_projective_diagnostics(
    theta: np.ndarray,
    weights: np.ndarray,
    *,
    label: str,
    bins: int = 64,
    similarity_bins: int = 100,
) -> WeightedProjectiveDiagnostics:
    """Compute normalized weighted ``P`` and ``R`` on a common angular grid."""

    angles = np.asarray(theta, dtype=float)
    sample_weights = np.asarray(weights, dtype=float)
    if angles.ndim != 1 or sample_weights.shape != angles.shape:
        raise ValueError("theta and weights must be equal-length vectors")
    if bins < 1 or similarity_bins < 1:
        raise ValueError("histogram bin counts must be positive")
    if np.any(sample_weights < -1.0e-12) or not np.all(np.isfinite(sample_weights)):
        raise ValueError("weights must be finite and nonnegative")
    sample_weights = np.maximum(sample_weights, 0.0)
    total_weight = float(np.sum(sample_weights))
    if total_weight <= 0.0:
        raise ValueError("weights have zero total")
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    blue, _ = np.histogram(angles, bins=edges, weights=sample_weights)
    red, _ = np.histogram(np.pi - angles, bins=edges, weights=sample_weights)
    p_blue = blue / total_weight / widths
    p_red = red / total_weight / widths
    denominator = blue + red
    occupied = denominator > 0.0
    ratio = np.divide(
        blue,
        denominator,
        out=np.full(bins, np.nan),
        where=occupied,
    )
    born = np.cos(centers / 2.0) ** 2
    residual = ratio - born

    score_edges = np.linspace(0.0, np.pi, similarity_bins + 1)
    score_centers = 0.5 * (score_edges[:-1] + score_edges[1:])
    score_width = float(score_edges[1] - score_edges[0])
    score_blue, _ = np.histogram(angles, bins=score_edges, weights=sample_weights)
    score_red, _ = np.histogram(
        np.pi - angles,
        bins=score_edges,
        weights=sample_weights,
    )
    score_total = score_blue + score_red
    score_ratio = np.divide(
        score_blue,
        score_total,
        out=np.full(similarity_bins, 0.5),
        where=score_total > 0.0,
    )
    score_born = np.cos(score_centers / 2.0) ** 2
    similarity = 1.0 - 2.0 * float(
        np.sum(np.abs(score_ratio - score_born) * np.sin(score_centers))
        * score_width
    )
    squared_weight = float(np.sum(sample_weights**2))
    effective_count = total_weight**2 / squared_weight if squared_weight else 0.0
    return WeightedProjectiveDiagnostics(
        label=label,
        edges=edges,
        centers=centers,
        p_theta=p_blue,
        p_pi_minus_theta=p_red,
        ratio=ratio,
        occupied=occupied,
        born=born,
        residual=residual,
        total_weight=total_weight,
        effective_root_count=effective_count,
        similarity=float(similarity),
        rmse_occupied=(
            float(np.sqrt(np.mean(residual[occupied] ** 2)))
            if np.any(occupied)
            else float("nan")
        ),
        l1_occupied=(
            float(np.sum(np.abs(residual[occupied]) * widths[occupied]))
            if np.any(occupied)
            else float("nan")
        ),
        occupied_fraction=float(np.mean(occupied)),
    )


def pooled_component_diagnostics(
    components: Sequence[MomentumProjectiveComponents],
    partition: ActivationPartition,
    *,
    bins: int = 64,
) -> tuple[WeightedProjectiveDiagnostics, ...]:
    """Pool momenta and return global plus activation-class diagnostics."""

    if not components:
        raise ValueError("components must not be empty")
    theta = np.concatenate([item.theta for item in components])
    class_weights = np.concatenate([item.class_weights for item in components], axis=1)
    output = [
        weighted_projective_diagnostics(
            theta,
            np.ones(theta.size),
            label="global",
            bins=bins,
        )
    ]
    for index, label in enumerate(partition.labels):
        output.append(
            weighted_projective_diagnostics(
                theta,
                class_weights[index],
                label=label,
                bins=bins,
            )
        )
    return tuple(output)


def validate_component_reconstruction(
    diagnostics: Sequence[WeightedProjectiveDiagnostics],
) -> dict[str, float]:
    """Check that normalized class histograms reconstruct the global one."""

    if len(diagnostics) < 2 or diagnostics[0].label != "global":
        raise ValueError("diagnostics must start with global and include components")
    global_result = diagnostics[0]
    components = diagnostics[1:]
    total = sum(item.total_weight for item in components)
    p_theta = sum(
        item.total_weight * item.p_theta for item in components
    ) / total
    p_reflected = sum(
        item.total_weight * item.p_pi_minus_theta for item in components
    ) / total
    return {
        "p_theta_max_abs_error": float(
            np.max(np.abs(p_theta - global_result.p_theta))
        ),
        "p_reflected_max_abs_error": float(
            np.max(np.abs(p_reflected - global_result.p_pi_minus_theta))
        ),
        "component_weight_sum_error": float(
            abs(total - global_result.total_weight)
        ),
    }


def _angular_model_moments(
    model: str,
    mu: float,
    shape: float,
    nmax: int,
) -> np.ndarray:
    harmonics = np.arange(1, nmax + 1, dtype=float)
    amplitude = (
        np.exp(-0.5 * harmonics**2 * shape**2)
        if model == "wrapped_gaussian"
        else shape**harmonics
    )
    return amplitude * np.exp(1j * harmonics * mu)


def _fit_weighted_angular_model(
    angles: np.ndarray,
    weights: np.ndarray,
    model: str,
    nmax: int,
    tolerance: float,
) -> dict[str, Any]:
    harmonics = np.arange(1, nmax + 1, dtype=float)
    empirical = np.sum(
        weights[:, None] * np.exp(1j * np.outer(angles, harmonics)),
        axis=0,
    ) / np.sum(weights)
    harmonic_weights = 1.0 / harmonics**2
    first = empirical[0]
    mu0 = float(np.angle(first) % (2.0 * np.pi))
    if model == "wrapped_gaussian":
        shape0 = float(
            np.clip(
                math.sqrt(max(0.0, -2.0 * math.log(max(abs(first), 1.0e-14)))),
                1.0e-4,
                np.pi,
            )
        )
        bounds = [(0.0, 2.0 * np.pi), (1.0e-5, 8.0)]
        starts = [(mu0, shape0), (0.0, 0.5), (np.pi, 1.5), (mu0, 3.0)]
    elif model == "wrapped_cauchy":
        shape0 = float(np.clip(abs(first), 1.0e-6, 0.999999))
        bounds = [(0.0, 2.0 * np.pi), (0.0, 0.999999)]
        starts = [(mu0, shape0), (0.0, 0.2), (np.pi, 0.7), (mu0, 0.95)]
    else:
        raise ValueError("unknown angular model")

    def objective(point: np.ndarray) -> float:
        residual = empirical - _angular_model_moments(
            model,
            float(point[0]),
            float(point[1]),
            nmax,
        )
        return float(np.sum(harmonic_weights * np.abs(residual) ** 2))

    results = [
        minimize(
            objective,
            start,
            method="L-BFGS-B",
            bounds=bounds,
            options={"ftol": tolerance, "maxiter": 2000},
        )
        for start in starts
    ]
    best = min(results, key=lambda item: float(item.fun))
    return {
        "model": model,
        "mu": float(best.x[0] % (2.0 * np.pi)),
        "shape": float(best.x[1]),
        "shape_name": "sigma" if model == "wrapped_gaussian" else "rho",
        "objective": float(best.fun),
        "converged": bool(best.success),
        "iterations": int(getattr(best, "nit", -1)),
        "message": str(best.message),
        "initializations": len(starts),
        "n_harmonics": int(nmax),
        "weight_sum": float(np.sum(weights)),
    }


def _circular_density(grid: np.ndarray, fit: dict[str, Any]) -> np.ndarray:
    mu = float(fit["mu"])
    shape = float(fit["shape"])
    if fit["model"] == "wrapped_cauchy":
        return (1.0 - shape**2) / (
            2.0
            * np.pi
            * (1.0 + shape**2 - 2.0 * shape * np.cos(grid - mu))
        )
    delta = (
        grid[:, None]
        - mu
        + 2.0 * np.pi * np.arange(-13, 14, dtype=float)[None, :]
    )
    return np.sum(np.exp(-0.5 * (delta / shape) ** 2), axis=1) / (
        math.sqrt(2.0 * np.pi) * shape
    )


def _folded_density(grid: np.ndarray, fit: dict[str, Any]) -> np.ndarray:
    return _circular_density(grid, fit) + _circular_density(
        (-grid) % (2.0 * np.pi), fit
    )


def fit_weighted_angular_distributions(
    theta: np.ndarray,
    weights: np.ndarray,
    *,
    plot_grid: int = 720,
    nmax: int = 32,
    tolerance: float = 1.0e-10,
) -> WeightedAngularFits:
    """Fit weighted reflection-augmented WG/WC models.

    This is the weighted counterpart of the established Sobol diagnostic fit:
    it duplicates each angle at ``-theta mod 2pi``, duplicates its weight, and
    minimizes the same inverse-square-weighted harmonic-moment residual.
    """

    angles = np.asarray(theta, dtype=float)
    sample_weights = np.asarray(weights, dtype=float)
    if angles.ndim != 1 or sample_weights.shape != angles.shape:
        raise ValueError("theta and weights must be equal-length vectors")
    if np.any(sample_weights < 0.0) or not np.all(np.isfinite(sample_weights)):
        raise ValueError("fit weights must be finite and nonnegative")
    keep = sample_weights > 0.0
    if not np.any(keep):
        raise ValueError("fit weights have zero total")
    augmented_angles = np.concatenate(
        (angles[keep], (-angles[keep]) % (2.0 * np.pi))
    )
    augmented_weights = np.concatenate((sample_weights[keep], sample_weights[keep]))
    gaussian = _fit_weighted_angular_model(
        augmented_angles,
        augmented_weights,
        "wrapped_gaussian",
        nmax,
        tolerance,
    )
    cauchy = _fit_weighted_angular_model(
        augmented_angles,
        augmented_weights,
        "wrapped_cauchy",
        nmax,
        tolerance,
    )
    grid = np.linspace(0.0, np.pi, plot_grid)
    gaussian_density = _folded_density(grid, gaussian)
    cauchy_density = _folded_density(grid, cauchy)
    gaussian["folded_integral_trapezoid"] = float(np.trapezoid(gaussian_density, grid))
    cauchy["folded_integral_trapezoid"] = float(np.trapezoid(cauchy_density, grid))
    return WeightedAngularFits(
        grid=grid,
        wrapped_gaussian_density=gaussian_density,
        wrapped_cauchy_density=cauchy_density,
        wrapped_gaussian=gaussian,
        wrapped_cauchy=cauchy,
    )
