"""Fit folded circular distributions to the projective angle ``P(theta)``.

The relative-evolution phase lives on ``(-pi, pi]`` while the projective
polar angle is its fold ``theta = abs(phi)`` in ``[0, pi]``.  Consequently a
centered circular density ``rho`` predicts ``P(theta) = rho(theta) +
rho(-theta)``.  This module compares two one-parameter families on the same
histogram bins:

* a folded wrapped Gaussian with unwrapped standard deviation ``sigma``;
* a folded wrapped Cauchy with circular scale ``gamma`` (``r = exp(-gamma)``).

Fits use the multinomial likelihood of the bin counts.  L1 and
Jensen--Shannon distances quantify absolute agreement, while the
log-likelihood ratio per sample is positive when the wrapped Cauchy is
preferred over the wrapped Gaussian.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import ndtr


_MIN_SCALE = 1.0e-4
_MAX_SCALE = 20.0
_PROBABILITY_FLOOR = 1.0e-300


@dataclass(frozen=True)
class FoldedDistributionFit:
    """Best-fit diagnostics for the two folded circular model families."""

    wrapped_gaussian_sigma: float
    wrapped_gaussian_l1: float
    wrapped_gaussian_js: float
    wrapped_gaussian_nll: float
    wrapped_cauchy_gamma: float
    wrapped_cauchy_l1: float
    wrapped_cauchy_js: float
    wrapped_cauchy_nll: float
    cauchy_log_likelihood_advantage_per_sample: float
    preferred_model: str
    sample_count: int
    empirical_probabilities: np.ndarray
    wrapped_gaussian_probabilities: np.ndarray
    wrapped_cauchy_probabilities: np.ndarray


def _validate_edges(edges: np.ndarray) -> np.ndarray:
    values = np.asarray(edges, dtype=float)
    if values.ndim != 1 or values.size < 3:
        raise ValueError("edges must be a one-dimensional array with at least two bins")
    if not np.all(np.isfinite(values)) or not np.all(np.diff(values) > 0.0):
        raise ValueError("edges must be finite and strictly increasing")
    if not math.isclose(float(values[0]), 0.0, abs_tol=1.0e-12):
        raise ValueError("folded-distribution edges must start at zero")
    if not math.isclose(float(values[-1]), math.pi, abs_tol=1.0e-12):
        raise ValueError("folded-distribution edges must end at pi")
    return values


def folded_wrapped_gaussian_bin_probabilities(edges: np.ndarray, sigma: float) -> np.ndarray:
    """Exact bin masses for ``abs(wrap(N(0, sigma**2)))``."""

    bins = _validate_edges(edges)
    scale = float(sigma)
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("sigma must be finite and positive")
    lower = bins[:-1]
    upper = bins[1:]
    wrap_count = int(math.ceil(8.0 * scale / (2.0 * math.pi))) + 2
    probabilities = np.zeros(lower.size, dtype=float)
    for k in range(-wrap_count, wrap_count + 1):
        shift = 2.0 * math.pi * k
        probabilities += ndtr((upper + shift) / scale) - ndtr((lower + shift) / scale)
        probabilities += ndtr((-lower + shift) / scale) - ndtr((-upper + shift) / scale)
    return _normalize_probabilities(probabilities)


def folded_wrapped_cauchy_bin_probabilities(edges: np.ndarray, gamma: float) -> np.ndarray:
    """Exact bin masses for a centered folded wrapped Cauchy law."""

    bins = _validate_edges(edges)
    scale = float(gamma)
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("gamma must be finite and positive")
    # (1+r)/(1-r) = coth(gamma/2); this form remains stable for large gamma.
    concentration = 1.0 / math.tanh(0.5 * scale)
    transformed = np.arctan(concentration * np.tan(0.5 * bins))
    transformed[0] = 0.0
    transformed[-1] = 0.5 * math.pi
    probabilities = (2.0 / math.pi) * np.diff(transformed)
    return _normalize_probabilities(probabilities)


def fit_folded_circular_models(
    theta: np.ndarray,
    edges: np.ndarray,
    *,
    min_scale: float = _MIN_SCALE,
    max_scale: float = _MAX_SCALE,
) -> FoldedDistributionFit:
    """Fit folded wrapped-Gaussian and wrapped-Cauchy models to ``theta``."""

    bins = _validate_edges(edges)
    values = np.asarray(theta, dtype=float).ravel()
    values = values[np.isfinite(values)]
    values = values[(values >= bins[0]) & (values <= bins[-1])]
    if values.size == 0:
        raise ValueError("theta contains no finite samples in [0, pi]")
    if not (0.0 < min_scale < max_scale):
        raise ValueError("scale bounds must satisfy 0 < min_scale < max_scale")

    counts, _ = np.histogram(values, bins=bins)
    empirical = counts.astype(float) / float(counts.sum())
    gaussian_sigma, gaussian_probabilities, gaussian_nll = _fit_scale(
        counts,
        bins,
        folded_wrapped_gaussian_bin_probabilities,
        min_scale,
        max_scale,
    )
    cauchy_gamma, cauchy_probabilities, cauchy_nll = _fit_scale(
        counts,
        bins,
        folded_wrapped_cauchy_bin_probabilities,
        min_scale,
        max_scale,
    )
    advantage = (gaussian_nll - cauchy_nll) / float(counts.sum())
    tolerance = 1.0e-12
    if advantage > tolerance:
        preferred = "wrapped_cauchy"
    elif advantage < -tolerance:
        preferred = "wrapped_gaussian"
    else:
        preferred = "indistinguishable"
    return FoldedDistributionFit(
        wrapped_gaussian_sigma=gaussian_sigma,
        wrapped_gaussian_l1=float(np.sum(np.abs(empirical - gaussian_probabilities))),
        wrapped_gaussian_js=_jensen_shannon(empirical, gaussian_probabilities),
        wrapped_gaussian_nll=gaussian_nll,
        wrapped_cauchy_gamma=cauchy_gamma,
        wrapped_cauchy_l1=float(np.sum(np.abs(empirical - cauchy_probabilities))),
        wrapped_cauchy_js=_jensen_shannon(empirical, cauchy_probabilities),
        wrapped_cauchy_nll=cauchy_nll,
        cauchy_log_likelihood_advantage_per_sample=float(advantage),
        preferred_model=preferred,
        sample_count=int(counts.sum()),
        empirical_probabilities=empirical,
        wrapped_gaussian_probabilities=gaussian_probabilities,
        wrapped_cauchy_probabilities=cauchy_probabilities,
    )


def _fit_scale(
    counts: np.ndarray,
    edges: np.ndarray,
    probability_function: Callable[[np.ndarray, float], np.ndarray],
    min_scale: float,
    max_scale: float,
) -> tuple[float, np.ndarray, float]:
    log_min = math.log(min_scale)
    log_max = math.log(max_scale)

    def objective(log_scale: float) -> float:
        probabilities = probability_function(edges, math.exp(float(log_scale)))
        return float(-np.dot(counts, np.log(np.clip(probabilities, _PROBABILITY_FLOOR, 1.0))))

    grid = np.linspace(log_min, log_max, 121)
    values = np.asarray([objective(point) for point in grid])
    best = int(np.argmin(values))
    left = grid[max(0, best - 1)]
    right = grid[min(grid.size - 1, best + 1)]
    if left == right:
        optimum_log_scale = float(grid[best])
    else:
        result = minimize_scalar(objective, bounds=(float(left), float(right)), method="bounded")
        optimum_log_scale = float(result.x) if result.success else float(grid[best])
    scale = math.exp(optimum_log_scale)
    probabilities = probability_function(edges, scale)
    return scale, probabilities, objective(optimum_log_scale)


def _normalize_probabilities(probabilities: np.ndarray) -> np.ndarray:
    values = np.asarray(probabilities, dtype=float)
    values = np.clip(values, 0.0, None)
    total = float(np.sum(values))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("model bin probabilities could not be normalized")
    return values / total


def _jensen_shannon(first: np.ndarray, second: np.ndarray) -> float:
    p = _normalize_probabilities(first)
    q = _normalize_probabilities(second)
    mixture = 0.5 * (p + q)

    def kl(left: np.ndarray, right: np.ndarray) -> float:
        mask = left > 0.0
        return float(np.sum(left[mask] * np.log(left[mask] / right[mask])))

    return 0.5 * kl(p, mixture) + 0.5 * kl(q, mixture)
