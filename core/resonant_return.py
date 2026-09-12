"""Exact qubit-block resolvents and leading transverse response.

These are detector-matrix objects, not probabilities or Born classifiers.
The Schur complement resums return processes without a nondegenerate
energy-denominator expansion. The time-domain leading response is only
a fixed-time perturbative coefficient.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import eigh, solve


def _square(value: np.ndarray, *, hermitian: bool) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if (matrix.ndim != 2 or matrix.shape[0] == 0
            or matrix.shape[0] != matrix.shape[1]
            or not np.all(np.isfinite(matrix))):
        raise ValueError("matrices must be finite nonempty square arrays")
    if hermitian and not np.allclose(matrix, matrix.conj().T, rtol=0, atol=1e-12):
        raise ValueError("diagonal Hamiltonian blocks must be Hermitian")
    return matrix


@dataclass(frozen=True)
class ProjectedResolvent:
    """First block column of (z-H)^-1 and exact return self-energy."""

    upper: np.ndarray
    lower: np.ndarray
    self_energy: np.ndarray
    column_residual: float


def projected_resolvent(
    h_plus: np.ndarray, h_minus: np.ndarray, flip: np.ndarray,
    *, spectral_parameter: complex,
) -> ProjectedResolvent:
    """Solve the Schur complement of H=[[H+, Q†], [Q, H-]].

    Require Im(z)!=0, so a Hermitian H has no resolvent pole. No real-axis
    gap, level separation, or small-coupling assumption is used. Residual
    is ||(z-H)G_column-[I;0]||_F/sqrt(d), not a condition-number estimate.
    """
    hp, hm = _square(h_plus, hermitian=True), _square(h_minus, hermitian=True)
    q = _square(flip, hermitian=False)
    z = complex(spectral_parameter)
    if hp.shape != hm.shape or q.shape != hp.shape:
        raise ValueError("all blocks must have the same shape")
    if not np.isfinite(z) or z.imag == 0:
        raise ValueError("spectral_parameter must be finite and off the real axis")
    identity = np.eye(len(hp), dtype=complex)
    returned = solve(z*identity-hm, q)
    sigma = q.conj().T @ returned
    upper = solve(z*identity-hp-sigma, identity)
    lower = returned @ upper
    r0 = (z*identity-hp) @ upper - q.conj().T @ lower - identity
    r1 = (z*identity-hm) @ lower - q @ upper
    residual = np.hypot(np.linalg.norm(r0), np.linalg.norm(r1)) / np.sqrt(len(hp))
    return ProjectedResolvent(upper, lower, sigma, float(residual))


def leading_transverse_matrix(
    detector_h: np.ndarray, flip: np.ndarray, *, central_z: float, time: float,
) -> np.ndarray:
    """Coefficient M1 of A^-1 C for H=HD+bZ0+epsilon [[0,Q†],[Q,0]].

    M1=-i exp(2ibt) integral exp(-2ibs) exp(iHDs) Q exp(-iHDs) ds.
    The entire sinc filter retains exact and near resonances. M1 is not
    the spectrum of the exact propagator at finite epsilon or late time.
    """
    hd, q = _square(detector_h, hermitian=True), _square(flip, hermitian=False)
    if hd.shape != q.shape or not np.all(np.isfinite([central_z, time])):
        raise ValueError("matching blocks and finite field/time are required")
    energies, vectors = eigh(hd)
    delta = energies[:, None] - energies[None, :] - 2*central_z
    phase = delta*time/2
    filt = time*np.exp(1j*phase)*np.sinc(phase/np.pi)
    response = vectors @ ((vectors.conj().T @ q @ vectors)*filt) @ vectors.conj().T
    return -1j*np.exp(2j*central_z*time)*response


def transverse_gauge(
    magnetizations: np.ndarray, *, gx: float, gy: float,
) -> tuple[np.ndarray, complex]:
    """Return diagonal D and s with D M(gx,gy) D^-1=s M(1,0).

    This identity requires [HD,Mz]=0 and [Mz,L+/-]=+/-2 L+/-; callers
    must verify them. D uses principal complex logarithm; s²=gx²-gy².
    Degenerate gx=+/-gy is deliberately outside this invertible mapping.
    Numerical conditioning worsens with N and coupling anisotropy.
    """
    m = np.asarray(magnetizations, dtype=float)
    if m.ndim != 1 or m.size == 0 or not np.all(np.isfinite(m)):
        raise ValueError("magnetizations must be a finite nonempty vector")
    if not np.all(np.isfinite([gx, gy])) or gx == gy or gx == -gy:
        raise ValueError("finite gx,gy with gx != +/-gy are required")
    u, v = gx+gy, gx-gy
    exponent = np.log(complex(v/u))/4
    diagonal = np.exp(exponent*m)
    if not np.all(np.isfinite(diagonal)) or np.any(diagonal == 0):
        raise FloatingPointError("gauge is outside floating-point dynamic range")
    return diagonal, complex(u*np.exp(2*exponent))
