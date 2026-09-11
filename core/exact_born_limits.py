"""Exact finite-resolution limits of the root-count Born diagnostics.

These functions quantify an impossibility result; they do not replace the
empirical root measure with a continuous probability distribution.
"""

from __future__ import annotations

import numpy as np


def histogram_born_errors(edges: np.ndarray, ratio: np.ndarray) -> dict[str, float]:
    """Compare a fully supported step function with Born over entire bins.

    Return supremum and RMS with respect to uniform dtheta/pi, not merely
    values at bin centers. A missing bin leaves the global error undefined.
    """
    e, r = np.asarray(edges, dtype=float), np.asarray(ratio, dtype=float)
    if e.ndim != 1 or r.shape != (e.size - 1,) or e.size < 2:
        raise ValueError("incompatible edges and ratio")
    if not np.all(np.isfinite(e)) or np.any(np.diff(e) <= 0):
        raise ValueError("edges must be finite and increasing")
    if not np.allclose(e[[0, -1]], [0., np.pi], atol=1e-14, rtol=0):
        raise ValueError("edges must span [0, pi]")
    if not np.all(np.isfinite(r)):
        return dict(supremum=np.nan, rms=np.nan)
    born_at_edges = np.cos(e / 2)**2
    maximum = np.maximum(abs(r - born_at_edges[:-1]), abs(r - born_at_edges[1:]))
    width = np.diff(e)
    integral_born = width / 2 + np.diff(np.sin(e)) / 2
    integral_square = 3 * width / 8 + np.diff(np.sin(e)) / 2 + np.diff(np.sin(2 * e)) / 16
    mean_square = np.sum(r*r*width - 2*r*integral_born + integral_square) / np.pi
    return dict(supremum=float(maximum.max()), rms=float(np.sqrt(max(0., mean_square))))


def uniform_bin_born_limits(bins: int) -> dict[str, float]:
    """Best possible errors over arbitrary constants in each uniform bin.

    Supremum and RMS optima use different bin constants. These bounds even
    allow arbitrary real weights, so root-count arithmetic cannot evade them.
    """
    if not isinstance(bins, int) or bins < 1:
        raise ValueError("bins must be a positive integer")
    if bins == 1:
        return dict(supremum=.5, rms=float(np.sqrt(1 / 8)))
    half_width = np.pi / (2 * bins)
    factor = np.cos(half_width) if bins % 2 == 0 else 1.
    return dict(supremum=float(.5 * factor * np.sin(half_width)),
                rms=float(np.sqrt((1 - np.sinc(half_width / np.pi)**2) / 8)))


def minimum_uniform_histogram_tv(sample_count: int, bins: int) -> float:
    """Exact count-arithmetic lower bound on TV to a flat bin distribution."""
    if any(not isinstance(x, int) or x < 1 for x in (sample_count, bins)):
        raise ValueError("sample_count and bins must be positive integers")
    remainder = sample_count % bins
    return remainder * (bins - remainder) / (bins * sample_count)


def circular_count_harmonics(phases: np.ndarray, order: int) -> np.ndarray:
    """Empirical Fourier moments; finitely many zero modes do not imply Haar."""
    values = np.asarray(phases, dtype=float)
    if values.ndim != 1 or not values.size or not np.all(np.isfinite(values)):
        raise ValueError("phases must be a finite nonempty vector")
    if not isinstance(order, int) or order < 0:
        raise ValueError("order must be a nonnegative integer")
    return np.array([np.mean(np.exp(1j * m * values)) for m in range(order + 1)])
