"""Exact root columns and phase-mixed caps for commuting detector fields.

H=K-X_q V-Z_q W, with K,V,W commuting and Pauli eigenvalues +/-1.
These formulas cannot replace a noncommuting detector by its trace CLT.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import quad


def vector_field_column(
    transverse: np.ndarray, longitudinal: np.ndarray, *, time: float
) -> tuple[np.ndarray, np.ndarray]:
    """Return diagonal A,C entries after cancelling the common K phase."""
    v, w = np.broadcast_arrays(
        np.asarray(transverse, dtype=float),
        np.asarray(longitudinal, dtype=float),
    )
    if not np.all(np.isfinite(v)) or not np.all(np.isfinite(w)):
        raise ValueError("field eigenvalues must be finite")
    if not np.isfinite(time):
        raise ValueError("time must be finite")
    omega = np.hypot(v, w)
    sine_over_omega = time * np.sinc(time * omega / np.pi)
    return (
        np.cos(time * omega) + 1j * w * sine_over_omega,
        1j * v * sine_over_omega,
    )


def mixed_south_probability(k: np.ndarray, *, epsilon: float) -> np.ndarray:
    """Pr[k sin²(phi)>1-epsilon] for phi uniform on [0,pi]."""
    values = np.asarray(k, dtype=float)
    if not np.all(np.isfinite(values)) or np.any((values < 0) | (values > 1)):
        raise ValueError("k must lie in [0,1]")
    if not 0 < epsilon < 1:
        raise ValueError("epsilon must lie in (0,1)")
    answer = np.zeros_like(values)
    active = values > 1 - epsilon
    argument = (values[active] - (1 - epsilon)) / values[active]
    answer[active] = 2 / np.pi * np.arcsin(np.sqrt(argument))
    return answer


def gaussian_resonant_cap(
    *, transverse_slope: float, transverse_offset: float,
    longitudinal_slope: float, detuning: float, epsilon: float,
) -> tuple[float, float]:
    """Phase-mixed south cap for V=h+gG, W=b+cG, G standard Gaussian.

    Uses the exact resonance interval. Requires c!=0 and a sufficiently
    small cap so the interval is bounded; returns a quadrature estimate.
    """
    g, h, c, b = (
        transverse_slope, transverse_offset, longitudinal_slope, detuning,
    )
    if not np.all(np.isfinite([g, h, c, b])) or c == 0:
        raise ValueError("finite fields and nonzero longitudinal slope required")
    if not 0 < epsilon < 1:
        raise ValueError("epsilon must lie in (0,1)")
    q = np.sqrt(epsilon / (1 - epsilon))
    if c * c <= q * q * g * g:
        raise ValueError("cap too large for the bounded resonance interval")
    resonance = -b / c
    v0 = h + g * resonance
    if v0 == 0:
        return 0., 0.
    # s=resonance+v0*u avoids subtracting nearly coincident field zeros.
    left, right = sorted([q / (c - q * g), -q / (c + q * g)])

    def integrand(u: float) -> float:
        v, w = 1 + g * u, c * u
        k = v * v / (v * v + w * w)
        probability = float(mixed_south_probability(k, epsilon=epsilon))
        s = resonance + v0 * u
        return probability * np.exp(-s * s / 2) / np.sqrt(2 * np.pi)

    value, error = quad(integrand, left, right, epsabs=1e-13, epsrel=1e-10)
    value, error = abs(v0) * value, abs(v0) * error
    mass_bound = min(1., abs(v0) * (right - left) / np.sqrt(2 * np.pi))
    upper = mass_bound * 2 / np.pi * np.arcsin(np.sqrt(epsilon))
    if value < -error or value > upper + 1e-12:
        raise ArithmeticError("resonant cap exceeded its probability bound")
    return float(value), float(error)


def gaussian_resonance_coefficient(
    *, transverse_slope: float, transverse_offset: float,
    longitudinal_slope: float, detuning: float,
) -> float:
    """Exact lim cap(epsilon)/epsilon; zero for coincident field zeros."""
    g, h, c, b = (
        transverse_slope, transverse_offset, longitudinal_slope, detuning,
    )
    if not np.all(np.isfinite([g, h, c, b])) or c == 0:
        raise ValueError("finite fields and nonzero longitudinal slope required")
    resonance = -b / c
    return float(abs(h + g * resonance) / abs(c)
                 * np.exp(-resonance**2 / 2) / np.sqrt(2 * np.pi))
