"""Projective qubit-root conventions for block-unitary matrix pencils.

The central qubit is the first tensor factor.  For

``U = [[A, B], [C, D]]``

this module distinguishes two related calculations:

* the production fixed-input-pole pencil ``C v = z A v``;
* the same-unitary forward pole-preimage pencils
  ``(C + z D) eta = 0`` and ``(A + z B) eta = 0``.

The affine coordinate is always ``z = q_1 / q_0`` for a qubit ket
``q = (q_0, q_1)``.  Homogeneous generalized eigenvalues ``(alpha, beta)``
therefore represent the qubit ket ``(beta, alpha)``.  Keeping this convention
explicit avoids silently interchanging production roots, forward roots, time
reversal, complex conjugation, and antipodal labels.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import block_diag
from scipy.optimize import linear_sum_assignment

from core.relative_evolution_pencil import (
    RelativeEvolutionPencilSpectrum,
    generalized_relative_evolution_spectrum,
)


@dataclass(frozen=True)
class QubitFirstBlocks:
    """The four detector-space blocks of a qubit-first operator."""

    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray

    @property
    def detector_dimension(self) -> int:
        return int(self.A.shape[0])


def append_uncoupled_spectator(
    unitary: np.ndarray,
    spectator_unitary: np.ndarray,
) -> np.ndarray:
    r"""Return ``U_QD tensor U_A`` in the ordering ``Q tensor D tensor A``.

    Each qubit-first block is tensored by the same invertible spectator
    unitary.  Consequently, the projective root multiset is unchanged except
    that every algebraic root is repeated by ``dim(A)``.  This helper encodes
    only dynamically uncoupled composition; it does not cover arbitrary
    microscopic refinements of the detector interaction.
    """

    primary = np.asarray(unitary, dtype=np.complex128)
    spectator = np.asarray(spectator_unitary, dtype=np.complex128)
    split_qubit_first_blocks(primary)
    if spectator.ndim != 2 or spectator.shape[0] != spectator.shape[1]:
        raise ValueError("spectator_unitary must be square")
    if spectator.shape[0] == 0 or not np.all(np.isfinite(spectator)):
        raise ValueError("spectator_unitary must be nonempty and finite")
    return np.kron(primary, spectator)


def direct_sum_detector_contexts(
    unitaries: list[np.ndarray] | tuple[np.ndarray, ...],
) -> np.ndarray:
    r"""Combine qubit unitaries over a direct-sum detector refinement.

    If ``U_k=[[A_k,B_k],[C_k,D_k]]`` acts on ``Q tensor D_k``, the returned
    unitary acts on ``Q tensor (direct_sum_k D_k)`` with blocks
    ``direct_sum_k A_k`` and so on. Its production root multiset is the union
    of the component multisets. Repeating only one component therefore changes
    equal-root weights, unlike a uniform tensor-factor spectator.
    """

    if not unitaries:
        raise ValueError("unitaries must contain at least one operator")
    blocks = [split_qubit_first_blocks(unitary) for unitary in unitaries]
    combined = QubitFirstBlocks(
        A=block_diag(*(block.A for block in blocks)),
        B=block_diag(*(block.B for block in blocks)),
        C=block_diag(*(block.C for block in blocks)),
        D=block_diag(*(block.D for block in blocks)),
    )
    return np.block([[combined.A, combined.B], [combined.C, combined.D]])


def split_qubit_first_blocks(operator: np.ndarray) -> QubitFirstBlocks:
    """Split a square even-dimensional operator into qubit-first blocks."""

    matrix = np.asarray(operator, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("operator must be a square matrix")
    if matrix.shape[0] == 0 or matrix.shape[0] % 2:
        raise ValueError("operator dimension must be positive and even")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("operator must contain only finite values")
    half = matrix.shape[0] // 2
    return QubitFirstBlocks(
        A=matrix[:half, :half],
        B=matrix[:half, half:],
        C=matrix[half:, :half],
        D=matrix[half:, half:],
    )


def production_root_spectrum(
    unitary: np.ndarray,
    **solver_options: object,
) -> RelativeEvolutionPencilSpectrum:
    """Return fixed-input-pole roots from ``C v = z A v``.

    A finite root means

    ``U (|0> tensor v) = (|0> + z |1>) tensor (A v)``.
    """

    blocks = split_qubit_first_blocks(unitary)
    return generalized_relative_evolution_spectrum(
        blocks.A,
        blocks.C,
        **solver_options,
    )


def forward_pole_root_spectrum(
    unitary: np.ndarray,
    outcome: int,
    **solver_options: object,
) -> RelativeEvolutionPencilSpectrum:
    """Return same-unitary forward roots reaching qubit pole ``outcome``.

    For outcome 0 this solves ``-C eta = z D eta``, equivalent to
    ``(C + z D) eta = 0``.  For outcome 1 it solves
    ``-A eta = z B eta``, equivalent to ``(A + z B) eta = 0``.
    """

    blocks = split_qubit_first_blocks(unitary)
    if outcome == 0:
        denominator, numerator = blocks.D, -blocks.C
    elif outcome == 1:
        denominator, numerator = blocks.B, -blocks.A
    else:
        raise ValueError("outcome must be 0 or 1")
    return generalized_relative_evolution_spectrum(
        denominator,
        numerator,
        **solver_options,
    )


def bloch_vectors_from_homogeneous(
    alpha: np.ndarray,
    beta: np.ndarray,
    *,
    zero_tolerance: float = 0.0,
) -> np.ndarray:
    r"""Map projective roots ``z=alpha/beta`` to Bloch vectors.

    The associated normalized qubit ket is proportional to
    ``(beta, alpha)``.  The formula is homogeneous, so finite and infinite
    roots are treated without division.  A row is ``nan`` only when both
    homogeneous coordinates are numerically zero.
    """

    if zero_tolerance < 0.0:
        raise ValueError("zero_tolerance must be nonnegative")
    a, b = np.broadcast_arrays(
        np.asarray(alpha, dtype=np.complex128),
        np.asarray(beta, dtype=np.complex128),
    )
    a = a.ravel()
    b = b.ravel()
    norm_sq = np.abs(a) ** 2 + np.abs(b) ** 2
    valid = norm_sq > zero_tolerance**2
    vectors = np.full((a.size, 3), np.nan, dtype=float)
    overlap = np.conj(b[valid]) * a[valid]
    vectors[valid, 0] = 2.0 * np.real(overlap) / norm_sq[valid]
    vectors[valid, 1] = 2.0 * np.imag(overlap) / norm_sq[valid]
    vectors[valid, 2] = (
        np.abs(b[valid]) ** 2 - np.abs(a[valid]) ** 2
    ) / norm_sq[valid]
    return vectors


def antipodal_homogeneous_coordinates(
    alpha: np.ndarray,
    beta: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    r"""Return homogeneous coordinates of the orthogonal qubit ray.

    If ``(alpha, beta)`` represents the ket ``(beta, alpha)``, its antipode is
    represented by ``(conj(beta), -conj(alpha))``.  In the finite affine chart
    this is the familiar map ``z -> -1/conj(z)``.
    """

    a, b = np.broadcast_arrays(
        np.asarray(alpha, dtype=np.complex128),
        np.asarray(beta, dtype=np.complex128),
    )
    return np.conj(b), -np.conj(a)


def matched_bloch_distance(
    reference: np.ndarray,
    candidate: np.ndarray,
) -> tuple[float, float]:
    """Return optimal maximum and RMS Euclidean Bloch-vector distances."""

    first = np.asarray(reference, dtype=float)
    second = np.asarray(candidate, dtype=float)
    if first.ndim != 2 or first.shape[1] != 3 or second.shape != first.shape:
        raise ValueError("reference and candidate must both have shape (n, 3)")
    if not np.all(np.isfinite(first)) or not np.all(np.isfinite(second)):
        raise ValueError("Bloch vectors must be finite")
    cost = np.linalg.norm(first[:, None, :] - second[None, :, :], axis=2)
    rows, columns = linear_sum_assignment(cost)
    errors = cost[rows, columns]
    return float(np.max(errors)), float(np.sqrt(np.mean(errors**2)))
