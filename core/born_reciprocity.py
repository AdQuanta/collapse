"""Distribution-level Born tests for projective-root polar angles.

Angles are in radians on [0, pi]; roots retain algebraic multiplicity.
For a probability measure P define a_n = integral cos(n theta) dP.
The Born reflection identity is equivalent to
2 a_(2m+1) - a_(2m) - a_(2m+2) = 0 for every m >= 0.
A finite prefix is a necessary test, never a sufficiency certificate.
No independence or sampling-error interpretation is assigned to roots.
"""

from __future__ import annotations

import numpy as np


def cosine_moments(theta: np.ndarray, maximum_order: int) -> np.ndarray:
    """Compute empirical cosine moments without binning or dropping roots."""
    values = np.asarray(theta, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("theta must be a nonempty one-dimensional array")
    if not np.all(np.isfinite(values)) or np.any((values < 0) | (values > np.pi)):
        raise ValueError("theta must be finite and in [0, pi]")
    if not isinstance(maximum_order, int) or maximum_order < 0:
        raise ValueError("maximum_order must be a nonnegative integer")
    return np.array([np.mean(np.cos(n * values)) for n in range(maximum_order + 1)])


def born_moment_residuals(moments: np.ndarray) -> np.ndarray:
    """Return the necessary Born residuals for a_0 through a_(2k)."""
    values = np.asarray(moments, dtype=float)
    if values.ndim != 1 or values.size < 3 or values.size % 2 != 1:
        raise ValueError("moments must contain orders 0 through a positive even order")
    if not np.all(np.isfinite(values)) or not np.isclose(values[0], 1, atol=1e-12, rtol=0):
        raise ValueError("moments must be finite and normalized")
    return 2 * values[1::2] - values[:-2:2] - values[2::2]


def folded_gaussian_moment_residuals(moments: np.ndarray, sigma: float) -> np.ndarray:
    """Compare with a centered folded wrapped normal; sigma is in radians."""
    values = np.asarray(moments, dtype=float)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("moments must be a finite one-dimensional array")
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be positive and finite")
    n = np.arange(values.size)
    return values - np.exp(-0.5 * (sigma * n) ** 2)


def histogram_cosine_moments(
    edges: np.ndarray, density: np.ndarray, maximum_order: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return uniform-within-bin estimates and rigorous within-bin bounds.

    Bounds allow any placement of the recorded mass inside each bin. They
    quantify loss of raw angles, not numerical solver or statistical error.
    """
    edges = np.asarray(edges, dtype=float)
    density = np.asarray(density, dtype=float)
    if (edges.ndim != 1 or density.shape != (edges.size - 1,)
            or not np.all(np.isfinite(edges)) or not np.all(np.isfinite(density))
            or np.any(np.diff(edges) <= 0) or np.any(density < 0)):
        raise ValueError("invalid histogram")
    mass = density * np.diff(edges)
    if not np.allclose(edges[[0, -1]], [0, np.pi], atol=1e-12, rtol=0):
        raise ValueError("edges must span [0, pi]")
    if not np.isclose(mass.sum(), 1, atol=1e-11, rtol=0):
        raise ValueError("histogram must be normalized")
    if not isinstance(maximum_order, int) or maximum_order < 0:
        raise ValueError("maximum_order must be a nonnegative integer")
    estimates, lower, upper = [1.0], [1.0], [1.0]
    for n in range(1, maximum_order + 1):
        estimates.append(float(density @ (np.diff(np.sin(n * edges)) / n)))
        endpoints = np.cos(n * edges)
        minima = np.minimum(endpoints[:-1], endpoints[1:])
        maxima = np.maximum(endpoints[:-1], endpoints[1:])
        for k in range(n + 1):
            point = k * np.pi / n
            inside = (edges[:-1] <= point) & (point <= edges[1:])
            if k % 2:
                minima[inside] = -1
            else:
                maxima[inside] = 1
        lower.append(float(mass @ minima))
        upper.append(float(mass @ maxima))
    return np.array(estimates), np.array(lower), np.array(upper)


def born_residual_bounds(lower: np.ndarray, upper: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Propagate moment intervals conservatively to Born residual intervals."""
    lo, hi = np.asarray(lower), np.asarray(upper)
    born_moment_residuals(lo)
    born_moment_residuals(hi)
    if lo.shape != hi.shape or np.any(lo > hi + 1e-14):
        raise ValueError("invalid moment intervals")
    return (2 * lo[1::2] - hi[:-2:2] - hi[2::2],
            2 * hi[1::2] - lo[:-2:2] - lo[2::2])


def reflection_diagnostics(arrays: dict[str, np.ndarray]) -> dict[str, float]:
    """Separate occupied support, density entropy, and Born reflection error.

    The reflection L1 residual integrates |P - Born*(P+P_reflected)|.
    It weights by mass and cannot certify agreement on unoccupied regions.
    The canonical S_born remains the stored metric, outside this function.
    """
    p, reflected = arrays["P"], arrays["P_reflected"]
    widths = np.diff(arrays["edges"])
    total = p + reflected
    occupied = total > 0
    mass = p * widths
    positive = mass > 0
    residual = p - arrays["Born"] * total
    ratio = np.divide(p, total, out=np.zeros_like(p), where=occupied)
    return {
        "coverage": float(np.mean(occupied)),
        "P_support": float(np.mean(p > 0)),
        "entropy_normalized": float(-np.sum(mass[positive] * np.log(mass[positive])) / np.log(p.size)),
        "reflection_L1": float(np.sum(np.abs(residual) * widths)),
        "occupied_RMSE": float(np.sqrt(np.mean((ratio[occupied] - arrays["Born"][occupied]) ** 2))),
    }


def response_cosine_coefficients(arrays: dict[str, np.ndarray], order: int) -> np.ndarray:
    """Midpoint cosine coefficients of R = c_0 + sum c_n cos(n theta).

    Refuse to extrapolate missing angular support: all coefficients are NaN
    unless every reflection-pair bin is occupied. This is a finite-bin
    quadrature, distinct from raw-angle moments of P.
    """
    if not isinstance(order, int) or order < 1:
        raise ValueError("order must be a positive integer")
    widths = np.diff(arrays["edges"])
    if not np.allclose(widths, widths[0], atol=1e-12, rtol=0):
        raise ValueError("response coefficients require uniform bins")
    if order >= widths.size:
        raise ValueError("order must be smaller than the number of bins")
    if not np.all(arrays["occupied"]):
        return np.full(order + 1, np.nan)
    values = arrays["R"]
    coeff = np.array([2 * np.mean(values * np.cos(n * arrays["centers"]))
                      for n in range(order + 1)])
    coeff[0] /= 2
    return coeff
