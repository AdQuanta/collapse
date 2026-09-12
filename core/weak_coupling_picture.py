"""Resonance-finite interaction-picture kernels retaining complex phases.

First Magnus exponentiation preserves unitarity and resums the first term;
it is not an unconditional long-time or thermodynamic approximation.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import eigh, expm


def interaction_picture_kernel(
    h0: np.ndarray, interaction: np.ndarray, *, time: float,
    hermitian_tolerance: float = 1e-12,
) -> tuple[np.ndarray, np.ndarray]:
    """Return U0(t) and integral exp(iH0s) V exp(-iH0s) ds.

    F_t(delta)=t exp(i delta t/2) sinc(delta t/(2pi)) is entire at delta=0.
    Exact and near degeneracies require no eigenvalue-denominator division.
    """
    a, v = np.asarray(h0, dtype=complex), np.asarray(interaction, dtype=complex)
    if (a.ndim != 2 or a.shape[0] == 0 or a.shape[0] != a.shape[1]
            or v.shape != a.shape):
        raise ValueError("H0 and V must be matching nonempty square matrices")
    if not np.isfinite(time) or not np.all(np.isfinite([a, v])):
        raise ValueError("matrices and time must be finite")
    if not np.isfinite(hermitian_tolerance) or hermitian_tolerance <= 0:
        raise ValueError("hermitian_tolerance must be positive and finite")
    for matrix in (a, v):
        scale = max(1., np.linalg.norm(matrix))
        if np.linalg.norm(matrix - matrix.conj().T) > hermitian_tolerance * scale:
            raise ValueError("H0 and V must be Hermitian")
    energies, vectors = eigh(a)
    delta = energies[:, None] - energies[None, :]
    phase = delta * time / 2
    filt = time * np.exp(1j * phase) * np.sinc(phase / np.pi)
    kernel = vectors @ ((vectors.conj().T @ v @ vectors) * filt) @ vectors.conj().T
    kernel = (kernel + kernel.conj().T) / 2
    free = (vectors * np.exp(-1j * time * energies)) @ vectors.conj().T
    return free, kernel


def first_magnus_unitary(
    h0: np.ndarray, interaction: np.ndarray, *, time: float,
) -> np.ndarray:
    """U0 exp(-iK1); caller must verify time/coupling accuracy against U."""
    free, kernel = interaction_picture_kernel(h0, interaction, time=time)
    return free @ expm(-1j * kernel)
