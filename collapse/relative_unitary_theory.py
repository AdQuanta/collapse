"""Exact relative-unitary bridge and finite-time weak-coupling kernel."""

from __future__ import annotations

import numpy as np
from scipy.linalg import expm


def finite_time_filter(delta: np.ndarray, time: float, tolerance: float = 1.0e-12) -> np.ndarray:
    r"""Return ``(exp(i*delta*t)-1)/(i*delta)`` with the ``delta=0`` limit."""

    gaps = np.asarray(delta, dtype=float)
    output = np.empty(gaps.shape, dtype=np.complex128)
    small = np.abs(gaps) <= tolerance
    output[small] = float(time)
    output[~small] = np.expm1(1j * gaps[~small] * float(time)) / (1j * gaps[~small])
    return output


def finite_time_kernel(detector_hamiltonian: np.ndarray, coupling: np.ndarray, time: float) -> np.ndarray:
    r"""Calculate ``integral_0^t exp(i H_D s) V exp(-i H_D s) ds``."""

    hamiltonian = np.asarray(detector_hamiltonian, dtype=np.complex128)
    operator = np.asarray(coupling, dtype=np.complex128)
    if hamiltonian.shape != operator.shape or hamiltonian.ndim != 2 or hamiltonian.shape[0] != hamiltonian.shape[1]:
        raise ValueError("detector_hamiltonian and coupling must be equally sized square matrices")
    energies, vectors = np.linalg.eigh(hamiltonian)
    transformed = vectors.conj().T @ operator @ vectors
    gaps = energies[:, None] - energies[None, :]
    kernel_energy_basis = transformed * finite_time_filter(gaps, time)
    kernel = vectors @ kernel_energy_basis @ vectors.conj().T
    return 0.5 * (kernel + kernel.conj().T)


def relative_unitary(u_plus: np.ndarray, u_minus: np.ndarray) -> np.ndarray:
    """Return ``A=U_-^{-1}U_+`` using a linear solve."""

    return np.linalg.solve(np.asarray(u_minus, dtype=np.complex128), np.asarray(u_plus, dtype=np.complex128))


def cayley_matrix(relative: np.ndarray) -> np.ndarray:
    r"""Return ``(I+A)^{-1}(A-I)`` using a linear solve."""

    matrix = np.asarray(relative, dtype=np.complex128)
    identity = np.eye(matrix.shape[0], dtype=np.complex128)
    return np.linalg.solve(identity + matrix, matrix - identity)


def exact_relative_objects(
    detector_hamiltonian: np.ndarray,
    coupling: np.ndarray,
    strength: float,
    time: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return exact ``U00``, ``U10``, ``A``, and ``M`` for ``X0 tensor V``."""

    detector = np.asarray(detector_hamiltonian, dtype=np.complex128)
    operator = np.asarray(coupling, dtype=np.complex128)
    u_plus = expm(-1j * float(time) * (detector + float(strength) * operator))
    u_minus = expm(-1j * float(time) * (detector - float(strength) * operator))
    u00 = 0.5 * (u_plus + u_minus)
    u10 = 0.5 * (u_plus - u_minus)
    relative = relative_unitary(u_plus, u_minus)
    m_matrix = np.linalg.solve(u00, u10)
    return u00, u10, relative, m_matrix


def leading_cayley_approximation(
    detector_hamiltonian: np.ndarray,
    coupling: np.ndarray,
    strength: float,
    time: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r"""Exponentiate the first Magnus term and retain the exact Cayley map."""

    kernel = finite_time_kernel(detector_hamiltonian, coupling, time)
    relative = expm(-2j * float(strength) * kernel)
    return kernel, relative, cayley_matrix(relative)


def folded_angles_from_relative_unitary(relative: np.ndarray) -> np.ndarray:
    r"""Return exact polar angles ``theta=|phase(A)|`` in ``[0,pi]``."""

    phases = np.angle(np.linalg.eigvals(np.asarray(relative, dtype=np.complex128)))
    return np.sort(np.abs(phases))

