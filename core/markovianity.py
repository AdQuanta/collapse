"""Non-Markovianity diagnostics for the qubit channel of a closed qubit+detector unitary.

Write the qubit-first propagator in blocks,

    U = |0><0| (x) A + |0><1| (x) B + |1><0| (x) C + |1><1| (x) D,

and let ``rho_D`` be the initial detector state.  The induced qubit channel has
Kraus operators ``K_mu = <mu|_D U |D_0>_D`` and channel tensor

    T[i, j, k, l] = sum_mu (K_mu)_{ij} conj((K_mu)_{kl}) = Tr(U_kl^dag U_ij rho_D),

so that ``Lambda(rho)_{ik} = sum_{jl} T[i, j, k, l] rho_{jl}``.  For a pure
detector state this is the Gram matrix of the four block images
``A|D_0>, B|D_0>, C|D_0>, D|D_0>``; for the maximally mixed state it is the
Hilbert-Schmidt Gram ``Tr(X^dag Y)/d``.  Neither form builds a ``2^(N+1)``
density matrix or takes a partial trace.

Every quantity is computed exactly from ``U(t)``.  No Lindblad or Born-Markov
approximation is fitted anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.projective_roots import split_qubit_first_blocks

# Pauli basis with the identity first, matching the Bloch conventions below.
_PAULI = (
    np.eye(2, dtype=np.complex128),
    np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
    np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128),
    np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
)


@dataclass(frozen=True)
class QubitChannel:
    """Reduced qubit channel at one time, in Choi and Bloch-affine form.

    ``bloch_matrix`` and ``bloch_translation`` act as ``r -> M r + c`` on the
    Bloch vector.  ``choi`` uses the convention
    ``J[(j, i), (l, k)] = T[i, j, k, l]``, so complete positivity is
    ``choi >= 0`` and trace preservation is ``Tr_2(choi) = I``.
    """

    choi: np.ndarray
    bloch_matrix: np.ndarray
    bloch_translation: np.ndarray


def _detector_gram(blocks, detector_state: np.ndarray | None) -> np.ndarray:
    """Return ``T[i, j, k, l] = Tr(U_kl^dag U_ij rho_D)`` for the four blocks."""

    grid = ((blocks.A, blocks.B), (blocks.C, blocks.D))
    dimension = blocks.A.shape[0]
    tensor = np.zeros((2, 2, 2, 2), dtype=np.complex128)

    if detector_state is None:
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    for l in range(2):
                        tensor[i, j, k, l] = (
                            np.vdot(grid[k][l], grid[i][j]) / dimension
                        )
        return tensor

    state = np.asarray(detector_state, dtype=np.complex128)
    if state.ndim == 1:
        norm = float(np.linalg.norm(state))
        if norm == 0.0:
            raise ValueError("the detector state vector must be nonzero")
        state = state / norm
        images = [[grid[i][j] @ state for j in range(2)] for i in range(2)]
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    for l in range(2):
                        tensor[i, j, k, l] = np.vdot(images[k][l], images[i][j])
        return tensor

    if state.ndim != 2 or state.shape != (dimension, dimension):
        raise ValueError(
            "the detector state must be a vector or a square density matrix "
            "matching the detector dimension"
        )
    for i in range(2):
        for j in range(2):
            for k in range(2):
                for l in range(2):
                    tensor[i, j, k, l] = np.trace(
                        grid[k][l].conj().T @ grid[i][j] @ state
                    )
    return tensor


def _apply(tensor: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """Apply the channel tensor to a 2x2 qubit operator."""

    return np.einsum("ijkl,jl->ik", tensor, rho)


def qubit_channel(
    unitary: np.ndarray, detector_state: np.ndarray | None = None
) -> QubitChannel:
    """Return the reduced qubit channel induced by ``unitary``.

    ``detector_state`` is the maximally mixed state when ``None``, a pure state
    when a vector, and an explicit density matrix when a square matrix.
    """

    blocks = split_qubit_first_blocks(unitary)
    tensor = _detector_gram(blocks, detector_state)

    choi = np.zeros((4, 4), dtype=np.complex128)
    for i in range(2):
        for j in range(2):
            for k in range(2):
                for l in range(2):
                    choi[2 * j + i, 2 * l + k] = tensor[i, j, k, l]

    matrix = np.zeros((3, 3), dtype=np.float64)
    for axis in range(3):
        image = _apply(tensor, _PAULI[axis + 1])
        for row in range(3):
            matrix[row, axis] = np.real(0.5 * np.trace(_PAULI[row + 1] @ image))
    identity_image = _apply(tensor, _PAULI[0])
    translation = np.array(
        [
            float(np.real(0.5 * np.trace(_PAULI[row + 1] @ identity_image)))
            for row in range(3)
        ]
    )
    return QubitChannel(choi=choi, bloch_matrix=matrix, bloch_translation=translation)


def choi_from_bloch(matrix: np.ndarray, translation: np.ndarray) -> np.ndarray:
    """Return the Choi matrix of the affine qubit map ``r -> M r + c``."""

    matrix = np.asarray(matrix, dtype=np.float64)
    translation = np.asarray(translation, dtype=np.float64)
    images = [_PAULI[0] + sum(translation[a] * _PAULI[a + 1] for a in range(3))]
    for axis in range(3):
        images.append(sum(matrix[a, axis] * _PAULI[a + 1] for a in range(3)))

    choi = np.zeros((4, 4), dtype=np.complex128)
    for j in range(2):
        for l in range(2):
            image = sum(
                _PAULI[mu][l, j] * images[mu] for mu in range(4)
            ) / 2.0
            for i in range(2):
                for k in range(2):
                    choi[2 * j + i, 2 * l + k] = image[i, k]
    return choi


def fibonacci_directions(count: int = 512) -> np.ndarray:
    """Return ``count`` near-uniform unit vectors on the sphere.

    A Fibonacci lattice is used rather than a latitude/longitude grid, which
    over-samples the poles and so biases a maximisation over directions.
    """

    if count < 1:
        raise ValueError("count must be positive")
    index = np.arange(count, dtype=np.float64) + 0.5
    z = 1.0 - 2.0 * index / count
    radius = np.sqrt(np.clip(1.0 - z * z, 0.0, None))
    phi = np.pi * (1.0 + 5.0**0.5) * index
    return np.column_stack((radius * np.cos(phi), radius * np.sin(phi), z))


def trace_distance_curves(
    matrices: np.ndarray, directions: np.ndarray
) -> np.ndarray:
    """Return ``D_n(t) = |M(t) n|`` with shape ``(times, directions)``.

    For a qubit the Breuer-Laine-Piilo optimal pair is antipodal, and the
    translation cancels in the difference, so the trace distance between the
    images of the pair with Bloch vectors ``+/- n`` is exactly ``|M(t) n|``.
    """

    return np.linalg.norm(np.einsum("tab,nb->tna", matrices, directions), axis=2)


def blp_backflow(matrices: np.ndarray, directions: np.ndarray | None = None) -> dict:
    """Return the BLP information backflow accumulated over the sampled window.

    The returned value is a **lower bound** on the true measure: the supremum
    over state pairs is estimated on a finite direction grid, and the time
    integral is replaced by a sum of increments on the supplied time samples.
    """

    if directions is None:
        directions = fibonacci_directions()
    curves = trace_distance_curves(matrices, directions)
    increments = np.diff(curves, axis=0)
    accumulated = np.where(increments > 0.0, increments, 0.0).sum(axis=0)
    best = int(np.argmax(accumulated))
    return {
        "n_blp": float(accumulated[best]),
        "direction": directions[best].tolist(),
        "direction_count": int(directions.shape[0]),
        "max_contraction": float(curves.min()),
    }


def volume_measure(matrices: np.ndarray) -> dict:
    """Return the accumulated increase of ``|det M(t)|``.

    A completely positive divisible evolution contracts the accessible Bloch
    volume monotonically, so any positive accumulation certifies a violation.
    """

    volumes = np.abs(np.linalg.det(matrices))
    increments = np.diff(volumes)
    return {
        "volume_backflow": float(np.where(increments > 0.0, increments, 0.0).sum()),
        "minimum_volume": float(volumes.min()),
    }


def rhp_divisibility(
    matrices: np.ndarray,
    translations: np.ndarray,
    *,
    determinant_floor: float = 1.0e-9,
) -> dict:
    """Return the accumulated CP-divisibility violation of the intermediate maps.

    The intermediate map ``Lambda(t + dt, t) = Lambda_{t + dt} . Lambda_t^{-1}``
    requires inverting ``M(t)``.  Steps whose determinant falls below
    ``determinant_floor`` are skipped and counted, because the inverse is not
    numerically meaningful there; the count is reported rather than hidden.
    """

    violation = 0.0
    minimum_eigenvalue = 0.0
    skipped = 0
    for index in range(matrices.shape[0] - 1):
        current = matrices[index]
        if abs(np.linalg.det(current)) < determinant_floor:
            skipped += 1
            continue
        inverse = np.linalg.inv(current)
        step_matrix = matrices[index + 1] @ inverse
        step_translation = (
            translations[index + 1] - step_matrix @ translations[index]
        )
        eigenvalues = np.linalg.eigvalsh(
            choi_from_bloch(step_matrix, step_translation)
        )
        smallest = float(eigenvalues.min())
        minimum_eigenvalue = min(minimum_eigenvalue, smallest)
        if smallest < 0.0:
            violation += -smallest
    return {
        "rhp_violation": float(violation),
        "minimum_choi_eigenvalue": float(minimum_eigenvalue),
        "skipped_steps": int(skipped),
        "total_steps": int(matrices.shape[0] - 1),
    }


def channel_series(
    unitaries: np.ndarray, detector_state: np.ndarray | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Return stacked Bloch matrices and translations for a series of unitaries."""

    channels = [qubit_channel(u, detector_state) for u in unitaries]
    matrices = np.array([c.bloch_matrix for c in channels])
    translations = np.array([c.bloch_translation for c in channels])
    return matrices, translations


def _bloch_from_tensor(tensor: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return stacked Bloch matrices and translations from channel tensors."""

    count = tensor.shape[0]
    matrices = np.empty((count, 3, 3), dtype=np.float64)
    translations = np.empty((count, 3), dtype=np.float64)
    for column, source in enumerate(_PAULI):
        image = np.einsum("tijkl,jl->tik", tensor, source)
        for row in range(3):
            value = 0.5 * np.real(np.einsum("ik,tki->t", _PAULI[row + 1], image))
            if column == 0:
                translations[:, row] = value
            else:
                matrices[:, row, column - 1] = value
    return matrices, translations


def bloch_series_from_spectrum(
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    times: np.ndarray,
    detector_state: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Bloch-affine series for ``exp(-i H t)`` without ever forming ``U(t)``.

    With ``H = V diag(w) V^dag`` and ``c^(i)`` the qubit-``i`` row block of
    ``V``, the blocks are ``U_ij = sum_m exp(-i w_m t) c^(i)_m c^(j)_m{}^dag``.
    Substituting into ``T[i, j, k, l] = Tr(U_kl^dag U_ij rho_D)`` leaves a
    quadratic form in the eigenphases, which costs ``O(D^2)`` per time instead
    of the ``O(D^3)`` of building the propagator.
    """

    eigenvalues = np.asarray(eigenvalues, dtype=np.float64)
    dimension = eigenvalues.size
    detector_dimension = dimension // 2
    blocks = (eigenvectors[:detector_dimension, :], eigenvectors[detector_dimension:, :])
    phases = np.exp(-1j * np.outer(np.asarray(times, dtype=np.float64), eigenvalues))
    tensor = np.empty((phases.shape[0], 2, 2, 2, 2), dtype=np.complex128)

    if detector_state is None:
        gram = [[blocks[p].conj().T @ blocks[q] for q in range(2)] for p in range(2)]
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    for l in range(2):
                        kernel = gram[k][i] * gram[j][l].T
                        tensor[:, i, j, k, l] = (
                            np.einsum("tm,mt->t", phases.conj(), kernel @ phases.T)
                            / detector_dimension
                        )
    else:
        state = np.asarray(detector_state, dtype=np.complex128).ravel()
        norm = float(np.linalg.norm(state))
        if norm == 0.0:
            raise ValueError("the detector state vector must be nonzero")
        state = state / norm
        overlaps = [blocks[q].conj().T @ state for q in range(2)]
        images = [
            [blocks[i] @ (phases * overlaps[j]).T for j in range(2)] for i in range(2)
        ]
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    for l in range(2):
                        tensor[:, i, j, k, l] = np.einsum(
                            "dt,dt->t", images[k][l].conj(), images[i][j]
                        )

    return _bloch_from_tensor(tensor)
