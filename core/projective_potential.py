"""Bounded radial log potentials for regular homogeneous root pencils.

The potential is normalized to zero at log radius zero. It retains zero
and infinite roots and is equivalent to the complete polar root measure.
Numerical determinant quadrature is a check, not a replacement for QZ.
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import lu_factor


def homogeneous_radial_potential(
    alpha: np.ndarray, beta: np.ndarray, log_radii: np.ndarray
) -> np.ndarray:
    """Return mean[max(log|alpha|, x+log|beta|)-max(log|alpha|,log|beta|)].

    Homogeneous pairs have equal algebraic weight. The kernel is bounded
    by |x|; it is x for zero roots and zero for infinite roots. No logarithmic
    root-moment assumption or affine division is required.
    """
    a, b = np.asarray(alpha, dtype=complex), np.asarray(beta, dtype=complex)
    x = np.asarray(log_radii, dtype=float)
    if a.ndim != 1 or a.size == 0 or b.shape != a.shape:
        raise ValueError("alpha and beta must be matching nonempty vectors")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("homogeneous entries must be finite")
    if np.any((a == 0) & (b == 0)):
        raise ValueError("indeterminate homogeneous roots are not a measure")
    if not np.all(np.isfinite(x)):
        raise ValueError("log_radii must be finite")
    with np.errstate(divide="ignore"):
        la, lb = np.log(np.abs(a)), np.log(np.abs(b))
    reference = np.maximum(la, lb)
    return np.mean(np.maximum(la, x[..., None] + lb) - reference, axis=-1)


def determinant_radial_potential(
    a: np.ndarray, c: np.ndarray, log_radii: np.ndarray, *, phase_nodes: int
) -> np.ndarray:
    """Approximate circle-averaged log determinants by midpoint quadrature.

    Return [mean_phi log|det(C-exp(x+i phi) A)| - value_at_x=0]/d.
    Caller must check angular refinement, especially near a root circle.
    A singular sampled pencil raises rather than supplying a regularizer.
    """
    a, c = np.asarray(a, dtype=complex), np.asarray(c, dtype=complex)
    x = np.asarray(log_radii, dtype=float)
    if a.ndim != 2 or a.shape[0] == 0 or a.shape[0] != a.shape[1] or c.shape != a.shape:
        raise ValueError("A,C must be nonempty matching square matrices")
    if not np.all(np.isfinite([a, c])) or not np.all(np.isfinite(x)):
        raise ValueError("pencil and radii must be finite")
    if np.any(np.abs(x) > 300):
        raise ValueError("determinant quadrature requires |log radius| <= 300")
    if not isinstance(phase_nodes, int) or phase_nodes < 4:
        raise ValueError("phase_nodes must be an integer >= 4")
    phases = np.exp(2j*np.pi*(np.arange(phase_nodes)+.5)/phase_nodes)

    def circle_mean(value: float) -> float:
        logs = []
        for phase in phases:
            factor, _ = lu_factor(c-np.exp(value)*phase*a)
            diagonal = np.abs(np.diag(factor))
            if np.any(diagonal == 0):
                raise ArithmeticError("singular quadrature node; no log cutoff was applied")
            logs.append(np.sum(np.log(diagonal)))
        if not np.all(np.isfinite(logs)):
            raise ArithmeticError("singular quadrature node; no log cutoff was applied")
        return float(np.mean(logs)/a.shape[0])

    reference = circle_mean(0.)
    return np.array([circle_mean(float(value))-reference for value in x.ravel()]).reshape(x.shape)
