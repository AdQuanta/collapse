"""
Quantum Utility Functions
==========================

Standalone helpers used across the project: random unitary generation,
time evolution, Born-distribution sampling, and Bloch-sphere
eigenvalue conversions.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Random unitary matrix
# ---------------------------------------------------------------------------
def generate_random_unitary(D: int, seed: int | None = None) -> np.ndarray:
    """
    Generate a Haar-random unitary matrix of size ``D × D``.

    Parameters
    ----------
    D : int
        Dimension of the unitary.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        A ``(D, D)`` complex unitary matrix.
    """
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((D, D)) + 1j * rng.standard_normal((D, D))
    Q, R = np.linalg.qr(X)
    diag = np.diag(R.diagonal() / np.abs(R.diagonal()))
    return Q @ diag


# ---------------------------------------------------------------------------
# Time evolution
# ---------------------------------------------------------------------------
def generate_time_evolution_operator(H: np.ndarray, t: float) -> np.ndarray:
    """
    Compute the time-evolution operator  U = exp(−i H t).

    Uses exact diagonalisation of the Hermitian Hamiltonian *H* so that
    the eigenbasis computation dominates the cost; for multiple time
    points the caller can cache (*E*, *V*) and call
    :func:`time_evolution_from_eigenbasis` instead.

    Parameters
    ----------
    H : np.ndarray
        Hermitian Hamiltonian matrix.
    t : float
        Evolution time.

    Returns
    -------
    np.ndarray
        Unitary matrix of same shape as *H*.
    """
    E, V = np.linalg.eigh(H)
    return (V * np.exp(-1j * E * t)) @ V.conj().T


def time_evolution_from_eigenbasis(
    E: np.ndarray, V: np.ndarray, t: float
) -> np.ndarray:
    """
    Compute U = exp(−i H t) from a pre-computed eigenbasis.

    Parameters
    ----------
    E : np.ndarray
        Eigenvalues of *H* (1-D).
    V : np.ndarray
        Eigenvectors of *H* (columns).
    t : float
        Evolution time.

    Returns
    -------
    np.ndarray
        Unitary matrix.
    """
    return (V * np.exp(-1j * E * t)) @ V.conj().T


# ---------------------------------------------------------------------------
# Born-distribution sampling
# ---------------------------------------------------------------------------
def sample_from_born_distribution(
    num_samples: int, seed: int | None = None
) -> np.ndarray:
    """
    Sample *z* values according to the Born probability density
    ``f(z) = (1 + z) / 2`` for ``z ∈ [−1, 1]``.

    Parameters
    ----------
    num_samples : int
        Number of samples to draw.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        Array of shape ``(num_samples,)`` in ``[−1, 1]``.
    """
    rng = np.random.default_rng(seed)
    u = rng.uniform(0, 1, num_samples)
    return 2 * np.sqrt(u) - 1


# ---------------------------------------------------------------------------
# Bloch-sphere helpers
# ---------------------------------------------------------------------------
def get_eigvals_from_z_and_theta(z: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """
    Map Bloch-sphere coordinates ``(z, θ)`` to eigenvalues.

    Parameters
    ----------
    z : array-like
        z-component of the Bloch vector.
    theta : array-like
        Azimuthal angle.

    Returns
    -------
    np.ndarray
        Complex eigenvalues.
    """
    return np.sqrt((1 - z) / (1 + z)) * np.exp(1j * theta)


def generate_special_unitary_from_eigvals(lambdas: np.ndarray) -> np.ndarray:
    """
    Construct a block-diagonal special-unitary matrix from eigenvalues.

    Parameters
    ----------
    lambdas : np.ndarray
        1-D array of complex eigenvalues.

    Returns
    -------
    np.ndarray
        Unitary matrix of shape ``(2n, 2n)`` where ``n = len(lambdas)``.
    """
    a = 1.0 / np.sqrt(1 + np.abs(lambdas) ** 2)
    U00 = np.diag(a)
    U01 = np.diag(a * (-np.conj(lambdas)))
    U10 = np.diag(a * lambdas)
    U11 = np.diag(a)
    return np.block([[U00, U01], [U10, U11]])
