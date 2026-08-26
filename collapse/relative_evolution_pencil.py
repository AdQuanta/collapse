"""Stable projective spectra for the relative-evolution matrix pencil.

The physical object is the detector-space pencil

    U10 v = lambda U00 v.

At well-conditioned times this is equivalent to diagonalizing
``solve(U00, U10)``.  At singular times a projective eigenvalue
``(alpha, beta)`` remains meaningful even when ``lambda = alpha / beta`` is
infinite.  A simultaneous numerical zero of ``alpha`` and ``beta`` signals an
indeterminate root of a singular pencil and is never converted to an ordinary
finite eigenvalue.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.linalg import eig
from scipy.optimize import linear_sum_assignment


@dataclass(frozen=True)
class RelativeEvolutionPencilSpectrum:
    """Generalized spectrum and numerical diagnostics for ``(U10, U00)``.

    ``alpha`` and ``beta`` obey ``beta U10 v = alpha U00 v``.  The polar
    angle is evaluated projectively as ``2 atan2(|alpha|, |beta|)`` and is
    therefore well defined for an infinite generalized eigenvalue.
    """

    alpha: np.ndarray
    beta: np.ndarray
    eigenvalues: np.ndarray
    radii: np.ndarray
    theta: np.ndarray
    right_eigenvectors: np.ndarray
    left_eigenvectors: np.ndarray
    finite: np.ndarray
    infinite: np.ndarray
    indeterminate: np.ndarray
    homogeneous_residuals: np.ndarray
    homogeneous_residual_norms: np.ndarray
    left_homogeneous_residuals: np.ndarray
    maximum_homogeneous_residual: float
    maximum_left_homogeneous_residual: float
    local_coordinate_condition_numbers: np.ndarray
    local_condition_coordinate: np.ndarray
    condition_number_u00: float
    smallest_singular_value_u00: float
    numerical_rank_u00: int
    rank_tolerance: float
    projective_tolerance: float
    near_singular_u00_warning: bool
    regularity_audit: "LinearPencilRegularityAudit | None"
    root_audits: tuple["ProjectiveRootAudit", ...]
    duplicate_diagnostics: "ProjectiveDuplicateDiagnostics"
    solver: str = "scipy.linalg.eig-homogeneous"


@dataclass(frozen=True)
class LinearPencilRegularityAudit:
    """Numerical rank sampling for ``beta U10 - alpha U00``.

    A full-rank value certifies regularity up to the declared numerical rank
    tolerance.  Failure to find one is a warning, not an exact proof that the
    determinant polynomial vanishes identically.
    """

    status: str
    dimension: int
    maximum_numerical_rank: int
    sample_alpha: np.ndarray
    sample_beta: np.ndarray
    sample_ranks: np.ndarray
    rank_tolerance: float


@dataclass(frozen=True)
class ProjectiveRootAudit:
    """SVD rank/nullity diagnostic at one normalized projective root."""

    index: int
    alpha: complex
    beta: complex
    numerical_rank: int
    nullity: int
    smallest_singular_value: float
    second_smallest_singular_value: float
    rank_tolerance: float


@dataclass(frozen=True)
class ProjectiveDuplicateDiagnostics:
    """Clusters of projectively coincident roots at a declared tolerance."""

    performed: bool
    tolerance: float
    clusters: tuple[tuple[int, ...], ...]
    largest_multiplicity: int
    distinct_root_count: int


def _validate_blocks(u00: np.ndarray, u10: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(u00, dtype=np.complex128)
    c = np.asarray(u10, dtype=np.complex128)
    if a.ndim != 2 or c.ndim != 2:
        raise ValueError("U00 and U10 must be two-dimensional")
    if a.shape[0] != a.shape[1]:
        raise ValueError("U00 must be square")
    if c.shape != a.shape:
        raise ValueError("U10 must have the same shape as U00")
    if a.shape[0] == 0:
        raise ValueError("the detector block dimension must be positive")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(c)):
        raise ValueError("U00 and U10 must contain only finite values")
    return a, c


def projective_chordal_distance(
    alpha_1: complex,
    beta_1: complex,
    alpha_2: complex,
    beta_2: complex,
) -> float:
    """Return the scale-invariant chordal distance between two ``CP1`` roots."""

    norm_1 = float(np.hypot(abs(alpha_1), abs(beta_1)))
    norm_2 = float(np.hypot(abs(alpha_2), abs(beta_2)))
    if norm_1 == 0.0 or norm_2 == 0.0:
        return np.nan
    return float(abs(alpha_1 * beta_2 - alpha_2 * beta_1) / (norm_1 * norm_2))


def diagnose_projective_duplicates(
    alpha: np.ndarray,
    beta: np.ndarray,
    *,
    tolerance: float,
    maximum_roots: int = 512,
) -> ProjectiveDuplicateDiagnostics:
    """Cluster finite or infinite projective roots by chordal distance.

    The pairwise calculation is deliberately skipped above ``maximum_roots``
    to avoid quadratic work and memory in production-scale spectra.
    """

    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if maximum_roots < 1:
        raise ValueError("maximum_roots must be positive")
    a, b = np.broadcast_arrays(
        np.asarray(alpha, dtype=np.complex128),
        np.asarray(beta, dtype=np.complex128),
    )
    a, b = a.ravel(), b.ravel()
    count = int(a.size)
    determined = np.hypot(np.abs(a), np.abs(b)) > 0.0
    if count > maximum_roots:
        return ProjectiveDuplicateDiagnostics(
            performed=False,
            tolerance=float(tolerance),
            clusters=(),
            largest_multiplicity=0,
            distinct_root_count=-1,
        )

    parent = np.arange(count)

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = int(parent[index])
        return index

    def union(left: int, right: int) -> None:
        root_left, root_right = find(left), find(right)
        if root_left != root_right:
            parent[root_right] = root_left

    valid_indices = np.flatnonzero(determined)
    for offset, left in enumerate(valid_indices):
        for right in valid_indices[offset + 1 :]:
            if projective_chordal_distance(a[left], b[left], a[right], b[right]) <= tolerance:
                union(int(left), int(right))

    grouped: dict[int, list[int]] = {}
    for index in valid_indices:
        grouped.setdefault(find(int(index)), []).append(int(index))
    clusters = tuple(
        tuple(group)
        for group in sorted(grouped.values(), key=lambda item: (item[0], len(item)))
        if len(group) > 1
    )
    largest = max((len(group) for group in grouped.values()), default=0)
    return ProjectiveDuplicateDiagnostics(
        performed=True,
        tolerance=float(tolerance),
        clusters=clusters,
        largest_multiplicity=int(largest),
        distinct_root_count=int(len(grouped)),
    )


def audit_linear_pencil_regularity(
    u00: np.ndarray,
    u10: np.ndarray,
    *,
    rank_tolerance: float | None = None,
) -> LinearPencilRegularityAudit:
    """Sample projective coordinates to audit numerical pencil regularity."""

    a, c = _validate_blocks(u00, u10)
    n = a.shape[0]
    eps = np.finfo(float).eps
    scale = max(float(np.linalg.norm(a, ord=2)), float(np.linalg.norm(c, ord=2)), 1.0)
    if rank_tolerance is None:
        rank_tolerance = n * eps * scale
    if rank_tolerance < 0.0:
        raise ValueError("rank_tolerance must be nonnegative")
    sample_alpha = np.array([0.0, 1.0, 1.0, -1.0, 1.0j], dtype=np.complex128)
    sample_beta = np.array([1.0, 0.0, 1.0, 1.0, 1.0], dtype=np.complex128)
    ranks = np.array(
        [
            np.linalg.matrix_rank(beta * c - alpha * a, tol=rank_tolerance)
            for alpha, beta in zip(sample_alpha, sample_beta, strict=True)
        ],
        dtype=int,
    )
    maximum = int(np.max(ranks))
    status = (
        "numerically_regular_at_sample"
        if maximum == n
        else "numerically_singular_at_all_samples"
    )
    return LinearPencilRegularityAudit(
        status=status,
        dimension=n,
        maximum_numerical_rank=maximum,
        sample_alpha=sample_alpha,
        sample_beta=sample_beta,
        sample_ranks=ranks,
        rank_tolerance=float(rank_tolerance),
    )


def _audit_root(
    index: int,
    alpha: complex,
    beta: complex,
    a: np.ndarray,
    c: np.ndarray,
    rank_tolerance: float | None,
) -> ProjectiveRootAudit:
    pair_norm = float(np.hypot(abs(alpha), abs(beta)))
    if pair_norm == 0.0:
        raise ValueError("cannot audit an indeterminate (0,0) root")
    normalized_alpha = alpha / pair_norm
    normalized_beta = beta / pair_norm
    matrix = normalized_beta * c - normalized_alpha * a
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    eps = np.finfo(float).eps
    tolerance = rank_tolerance
    if tolerance is None:
        tolerance = matrix.shape[0] * eps * max(float(singular_values[0]), 1.0)
    rank = int(np.count_nonzero(singular_values > tolerance))
    second_smallest = (
        float(singular_values[-2]) if singular_values.size >= 2 else np.nan
    )
    return ProjectiveRootAudit(
        index=int(index),
        alpha=complex(normalized_alpha),
        beta=complex(normalized_beta),
        numerical_rank=rank,
        nullity=int(matrix.shape[0] - rank),
        smallest_singular_value=float(singular_values[-1]),
        second_smallest_singular_value=second_smallest,
        rank_tolerance=float(tolerance),
    )


def generalized_relative_evolution_spectrum(
    u00: np.ndarray,
    u10: np.ndarray,
    *,
    projective_tolerance: float | None = None,
    rank_tolerance: float | None = None,
    condition_warning_threshold: float = 1.0e12,
    audit_root_indices: Sequence[int] | None = None,
    audit_root_rank_tolerance: float | None = None,
    assess_regularity: bool = False,
    duplicate_tolerance: float | None = None,
    maximum_duplicate_roots: int = 512,
) -> RelativeEvolutionPencilSpectrum:
    """Solve ``U10 v = lambda U00 v`` without forming ``U00**(-1)``.

    Parameters
    ----------
    u00, u10:
        Square detector-space propagator blocks in the same basis.
    projective_tolerance:
        Relative threshold used only to classify ``beta=0`` and ``0/0``
        homogeneous pairs.  The default is ``64 * eps`` for float64.
    rank_tolerance:
        Absolute singular-value threshold for the numerical rank of ``U00``.
        The default is ``n * eps * sigma_max``.
    condition_warning_threshold:
        Threshold for flagging the denominator block as near singular.
    audit_root_indices:
        Optional root indices at which to compute an SVD rank/nullity audit.
        This is intentionally opt-in because an SVD per root is expensive.
    assess_regularity:
        If true, sample five projective coordinates for a numerical
        regular/singular-pencil audit.
    duplicate_tolerance:
        Chordal distance used to cluster repeated projective roots. Defaults
        to ``sqrt(eps)``. Pairwise work is skipped when the spectrum exceeds
        ``maximum_duplicate_roots``.

    Returns
    -------
    RelativeEvolutionPencilSpectrum
        Projective eigenvalues, angles, right eigenvectors, conditioning, and
        backward residuals.  No pseudoinverse continuation is used.
    """

    a, c = _validate_blocks(u00, u10)
    n = a.shape[0]
    eps = np.finfo(float).eps
    if projective_tolerance is None:
        projective_tolerance = 64.0 * eps
    if projective_tolerance <= 0.0:
        raise ValueError("projective_tolerance must be positive")

    if condition_warning_threshold <= 1.0:
        raise ValueError("condition_warning_threshold must exceed one")
    if duplicate_tolerance is None:
        duplicate_tolerance = float(np.sqrt(eps))
    homogeneous, left_vectors, right_vectors = eig(
        c,
        a,
        right=True,
        left=True,
        homogeneous_eigvals=True,
        check_finite=True,
    )
    alpha = np.asarray(homogeneous[0], dtype=np.complex128)
    beta = np.asarray(homogeneous[1], dtype=np.complex128)
    left_vectors = np.asarray(left_vectors, dtype=np.complex128)
    right_vectors = np.asarray(right_vectors, dtype=np.complex128)

    pair_scale = np.maximum(np.abs(alpha), np.abs(beta))
    absolute_floor = projective_tolerance * max(
        float(np.linalg.norm(a, ord=2)),
        float(np.linalg.norm(c, ord=2)),
        1.0,
    )
    indeterminate = pair_scale <= absolute_floor
    infinite = (~indeterminate) & (np.abs(beta) <= projective_tolerance * pair_scale)
    finite = ~(indeterminate | infinite)

    eigenvalues = np.full(n, np.nan + 1j * np.nan, dtype=np.complex128)
    eigenvalues[finite] = alpha[finite] / beta[finite]
    eigenvalues[infinite] = np.inf + 0j
    radii = np.full(n, np.nan, dtype=float)
    radii[finite] = np.abs(eigenvalues[finite])
    radii[infinite] = np.inf
    theta = np.full(n, np.nan, dtype=float)
    determined = ~indeterminate
    theta[determined] = 2.0 * np.arctan2(
        np.abs(alpha[determined]),
        np.abs(beta[determined]),
    )

    singular_values = np.linalg.svd(a, compute_uv=False)
    sigma_max = float(singular_values[0])
    sigma_min = float(singular_values[-1])
    if rank_tolerance is None:
        rank_tolerance = n * eps * sigma_max
    if rank_tolerance < 0.0:
        raise ValueError("rank_tolerance must be nonnegative")
    numerical_rank = int(np.count_nonzero(singular_values > rank_tolerance))
    condition_number = np.inf if sigma_min == 0.0 else sigma_max / sigma_min

    norm_a = float(np.linalg.norm(a, ord=2))
    norm_c = float(np.linalg.norm(c, ord=2))
    residual_norms = np.full(n, np.nan, dtype=float)
    residuals = np.full(n, np.nan, dtype=float)
    left_residuals = np.full(n, np.nan, dtype=float)
    local_conditions = np.full(n, np.nan, dtype=float)
    local_coordinates = np.full(n, "indeterminate", dtype="<U16")
    for index in range(n):
        if indeterminate[index]:
            continue
        vector = right_vectors[:, index]
        left_vector = left_vectors[:, index]
        numerator = np.linalg.norm(
            beta[index] * (c @ vector) - alpha[index] * (a @ vector)
        )
        residual_norms[index] = float(numerator)
        denominator = (
            abs(beta[index]) * norm_c + abs(alpha[index]) * norm_a
        ) * np.linalg.norm(vector)
        residuals[index] = float(numerator / denominator) if denominator else float(numerator)
        left_numerator = np.linalg.norm(
            np.conj(beta[index]) * (c.conj().T @ left_vector)
            - np.conj(alpha[index]) * (a.conj().T @ left_vector)
        )
        left_denominator = (
            abs(beta[index]) * norm_c + abs(alpha[index]) * norm_a
        ) * np.linalg.norm(left_vector)
        left_residuals[index] = (
            float(left_numerator / left_denominator)
            if left_denominator
            else float(left_numerator)
        )
        vector_norm_product = np.linalg.norm(vector) * np.linalg.norm(left_vector)
        if finite[index]:
            value = eigenvalues[index]
            overlap = abs(np.vdot(left_vector, a @ vector))
            numerator_condition = (norm_c + abs(value) * norm_a) * vector_norm_product
            local_conditions[index] = (
                float(numerator_condition / overlap) if overlap > 0.0 else np.inf
            )
            local_coordinates[index] = "lambda"
        elif infinite[index]:
            inverse_value = beta[index] / alpha[index]
            overlap = abs(np.vdot(left_vector, c @ vector))
            numerator_condition = (
                norm_a + abs(inverse_value) * norm_c
            ) * vector_norm_product
            local_conditions[index] = (
                float(numerator_condition / overlap) if overlap > 0.0 else np.inf
            )
            local_coordinates[index] = "mu=1/lambda"
    finite_residuals = residuals[np.isfinite(residuals)]
    maximum_residual = (
        float(np.max(finite_residuals)) if finite_residuals.size else np.nan
    )
    finite_left_residuals = left_residuals[np.isfinite(left_residuals)]
    maximum_left_residual = (
        float(np.max(finite_left_residuals))
        if finite_left_residuals.size
        else np.nan
    )

    requested_indices = tuple(int(index) for index in (audit_root_indices or ()))
    root_audits: list[ProjectiveRootAudit] = []
    for index in requested_indices:
        if index < 0 or index >= n:
            raise IndexError(f"audit root index {index} outside [0, {n})")
        if indeterminate[index]:
            continue
        root_audits.append(
            _audit_root(
                index,
                alpha[index],
                beta[index],
                a,
                c,
                audit_root_rank_tolerance,
            )
        )
    regularity = (
        audit_linear_pencil_regularity(a, c, rank_tolerance=rank_tolerance)
        if assess_regularity
        else None
    )
    duplicates = diagnose_projective_duplicates(
        alpha,
        beta,
        tolerance=duplicate_tolerance,
        maximum_roots=maximum_duplicate_roots,
    )

    return RelativeEvolutionPencilSpectrum(
        alpha=alpha,
        beta=beta,
        eigenvalues=eigenvalues,
        radii=radii,
        theta=theta,
        right_eigenvectors=right_vectors,
        left_eigenvectors=left_vectors,
        finite=finite,
        infinite=infinite,
        indeterminate=indeterminate,
        homogeneous_residuals=residuals,
        homogeneous_residual_norms=residual_norms,
        left_homogeneous_residuals=left_residuals,
        maximum_homogeneous_residual=maximum_residual,
        maximum_left_homogeneous_residual=maximum_left_residual,
        local_coordinate_condition_numbers=local_conditions,
        local_condition_coordinate=local_coordinates,
        condition_number_u00=float(condition_number),
        smallest_singular_value_u00=sigma_min,
        numerical_rank_u00=numerical_rank,
        rank_tolerance=float(rank_tolerance),
        projective_tolerance=float(projective_tolerance),
        near_singular_u00_warning=bool(
            numerical_rank < n or condition_number > condition_warning_threshold
        ),
        regularity_audit=regularity,
        root_audits=tuple(root_audits),
        duplicate_diagnostics=duplicates,
    )


def matched_projective_angle_error(
    reference_theta: np.ndarray,
    candidate_theta: np.ndarray,
) -> tuple[float, float]:
    """Return optimal maximum and RMS errors between two angle multisets.

    A Hungarian assignment is used because generalized eigenvalue ordering is
    not stable across algorithms.  Indeterminate (NaN) angles are rejected.
    """

    reference = np.asarray(reference_theta, dtype=float).ravel()
    candidate = np.asarray(candidate_theta, dtype=float).ravel()
    if reference.size != candidate.size:
        raise ValueError("angle arrays must have the same size")
    if not np.all(np.isfinite(reference)) or not np.all(np.isfinite(candidate)):
        raise ValueError("angle arrays must be finite")
    cost = np.abs(reference[:, None] - candidate[None, :])
    rows, columns = linear_sum_assignment(cost)
    errors = cost[rows, columns]
    return float(np.max(errors)), float(np.sqrt(np.mean(errors**2)))


def compare_direct_and_generalized(
    u00: np.ndarray,
    u10: np.ndarray,
    *,
    maximum_condition_number: float = 1.0e10,
) -> dict[str, float | int | bool]:
    """Compare inversion and projective spectra at a well-conditioned time."""

    if maximum_condition_number <= 1.0:
        raise ValueError("maximum_condition_number must exceed one")
    a, c = _validate_blocks(u00, u10)
    pencil = generalized_relative_evolution_spectrum(a, c)
    eligible = bool(
        pencil.condition_number_u00 <= maximum_condition_number
        and not np.any(pencil.infinite)
        and not np.any(pencil.indeterminate)
    )
    result: dict[str, float | int | bool] = {
        "eligible": eligible,
        "dimension": int(a.shape[0]),
        "condition_number_u00": pencil.condition_number_u00,
        "maximum_pencil_residual": pencil.maximum_homogeneous_residual,
        "infinite_eigenvalues": int(np.count_nonzero(pencil.infinite)),
        "indeterminate_eigenvalues": int(np.count_nonzero(pencil.indeterminate)),
    }
    if not eligible:
        result["maximum_angle_error"] = np.nan
        result["rms_angle_error"] = np.nan
        return result
    direct_theta = 2.0 * np.arctan(np.abs(np.linalg.eigvals(np.linalg.solve(a, c))))
    maximum, rms = matched_projective_angle_error(direct_theta, pencil.theta)
    result["maximum_angle_error"] = maximum
    result["rms_angle_error"] = rms
    return result
