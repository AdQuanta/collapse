"""Exact reductions used in the asymptotic Born-obstruction proofs.

These functions do not replace the production homogeneous-QZ root solver or
the finite Born gate. Units use hbar=1, Pauli eigenvalues +/-1 and radians.
See BORN_ASYMPTOTIC_OBSTRUCTIONS.md for hypotheses and scope.
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import expm


def recurrence_angle_bound(unitary_distance: float) -> float:
    """Bound every root angle when ||U-I||_2 <= distance < 1.

    A is then invertible and ||A^-1 C|| <= distance/(1-distance), even for
    nonnormal pencils. The result bounds a recurrence; it does not find one.
    """
    if not np.isfinite(unitary_distance) or not 0 <= unitary_distance < 1:
        raise ValueError("unitary_distance must be finite and in [0, 1)")
    return float(2 * np.arctan(unitary_distance / (1 - unitary_distance)))


def conditional_phase_traces(
    detector: np.ndarray,
    coupling: np.ndarray,
    time: float,
    maximum_order: int,
) -> np.ndarray:
    """Return normalized traces of W^n for H=I*K-X*V, n=0,...,order.

    K and V are finite Hermitian matrices in the same detector basis.
    W=exp(+it(K-V)) exp(-it(K+V)); no commutation is assumed.
    """
    k = np.asarray(detector, dtype=complex)
    v = np.asarray(coupling, dtype=complex)
    if k.ndim != 2 or k.shape[0] == 0 or k.shape[0] != k.shape[1]:
        raise ValueError("detector must be a nonempty square matrix")
    if v.shape != k.shape or not np.all(np.isfinite([k, v])):
        raise ValueError("coupling must match detector; entries must be finite")
    for matrix in (k, v):
        if not np.allclose(matrix, matrix.conj().T, atol=1e-12, rtol=1e-12):
            raise ValueError("detector and coupling must be Hermitian")
    if not np.isfinite(time):
        raise ValueError("time must be finite")
    if not isinstance(maximum_order, int) or maximum_order < 0:
        raise ValueError("maximum_order must be a nonnegative integer")
    w = expm(1j * time * (k - v)) @ expm(-1j * time * (k + v))
    power = np.eye(k.shape[0], dtype=complex)
    result = np.empty(maximum_order + 1, dtype=complex)
    for n in range(maximum_order + 1):
        result[n] = np.trace(power) / k.shape[0]
        power = power @ w
    return result


def shifted_cosine_moments(
    traces: np.ndarray, *, field: float, time: float
) -> np.ndarray:
    """Root cosine moments after adding -field*X to an X-conserving H."""
    values = np.asarray(traces, dtype=complex)
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        raise ValueError("traces must be a finite nonempty vector")
    if not np.isfinite(field) or not np.isfinite(time):
        raise ValueError("field and time must be finite")
    n = np.arange(values.size)
    return np.real(values * np.exp(-2j * n * field * time))


def field_interval_first_residual(
    traces: np.ndarray, *, time: float, center: float, width: float
) -> float:
    """Exact field-interval mean of d0=2a1-1-a2; not a time average.

    The interval has full width ``width``. Its departure from -1 is bounded
    by 5/(2*width*abs(time)) for nonzero time, independently of dimension.
    """
    if not np.isfinite(width) or width <= 0:
        raise ValueError("width must be finite and positive")
    values = shifted_cosine_moments(traces, field=center, time=time)
    if values.size < 3:
        raise ValueError("traces must include orders zero through two")
    return float(2 * values[1] * np.sinc(time * width / np.pi) - 1
                 - values[2] * np.sinc(2 * time * width / np.pi))


def collective_cosine_moments(
    detector_size: int, *, coupling: float, time: float, maximum_order: int
) -> np.ndarray:
    """Exact a_n=cos(2*n*g*t/sqrt(N))^N for collective commuting X coupling.

    Algebraic multiplicities of all 2^N roots are included analytically.
    This is not sampling or a floating-point certificate of exact equality.
    """
    if not isinstance(detector_size, int) or detector_size < 1:
        raise ValueError("detector_size must be a positive integer")
    if not isinstance(maximum_order, int) or maximum_order < 0:
        raise ValueError("maximum_order must be a nonnegative integer")
    if not np.isfinite(coupling) or not np.isfinite(time):
        raise ValueError("coupling and time must be finite")
    n = np.arange(maximum_order + 1)
    return np.cos(2 * n * coupling * time / np.sqrt(detector_size)) ** detector_size


def gaussian_limit_density(
    theta: np.ndarray, *, coupling: float, time: float, modes: int = 128
) -> tuple[np.ndarray, float]:
    """N-first collective limit density and a uniform Fourier-tail bound.

    P_t=(1+2 sum exp(-2*n^2*g^2*t^2) cos(n*theta))/pi. The returned
    truncation bound is 2/pi*q^((modes+1)^2)/(1-q^(2*modes+3)). Its floating
    estimate is floored at the smallest positive float if it underflows;
    this is not an interval-arithmetic certificate or a roundoff bound.
    This Fourier representation is for nonzero g*t; t=0 is a delta mass.
    """
    angles = np.asarray(theta, dtype=float)
    if not np.all(np.isfinite(angles)) or np.any((angles < 0) | (angles > np.pi)):
        raise ValueError("theta must be finite and in [0, pi]")
    if not np.isfinite(coupling) or not np.isfinite(time) or coupling * time == 0:
        raise ValueError("coupling*time must be finite and nonzero")
    if not isinstance(modes, int) or modes < 1:
        raise ValueError("modes must be a positive integer")
    decay = 2 * (coupling * time) ** 2
    n = np.arange(1, modes + 1)
    result = (1 + 2 * np.sum(
        np.exp(-decay * n**2) * np.cos(angles[..., None] * n), axis=-1
    )) / np.pi
    tail = 2 / np.pi * np.exp(-decay * (modes + 1)**2) / (
        -np.expm1(-decay * (2 * modes + 3))
    )
    return result, float(max(tail, np.nextafter(0., 1.)))
