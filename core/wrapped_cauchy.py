"""
Wrapped Cauchy Distribution — Computation Module
==================================================

Pure-math and pure-computation routines for studying sums of i.i.d.
Cauchy random variables wrapped onto the circle.

Separation from plotting is intentional: these functions can be
imported in headless scripts and tests without pulling in Matplotlib.

Theory
------
* Each  x_i ~ Cauchy(0, γ).
* For any fixed sign vector  (s_1, …, s_N)  the sum  S = Σ s_i x_i
  is distributed as  Cauchy(0, Nγ)  (scale is additive for independent
  Cauchy sums).
* The wrapped Cauchy PDF on  (-π, π]  with scale  g  is:

      f(θ; g) = sinh(g) / [2π (cosh(g) − cos θ)]
"""

from __future__ import annotations

import numpy as np


def wrapped_cauchy_pdf(theta: np.ndarray, gamma: float) -> np.ndarray:
    """
    PDF of the wrapped Cauchy distribution on  (-π, π].

    Parameters
    ----------
    theta : array-like
        Angles in  (-π, π].
    gamma : float
        Scale parameter of the underlying Cauchy distribution.

    Returns
    -------
    np.ndarray
        PDF values at the given angles.
    """
    return (1.0 / (2.0 * np.pi)) * np.sinh(gamma) / (np.cosh(gamma) - np.cos(theta))


def compute_wrapped_sums(
    N: int,
    gamma: float,
    M: int = 1,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Sample M realisations of N i.i.d. Cauchy(0, γ) RVs and compute all
    2^N signed sums, wrapped mod 2π into (-π, π].

    Parameters
    ----------
    N : int
        Number of Cauchy RVs.  Keep  N ≤ ~20  to avoid excessive memory.
    gamma : float
        Scale parameter.
    M : int
        Number of independent realisations.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    wrapped_sums : np.ndarray
        Shape ``(M, 2^N)`` or ``(2^N,)`` when ``M == 1``.
    x : np.ndarray
        The sampled Cauchy RVs, shape ``(M, N)`` or ``(N,)`` when ``M == 1``.
    """
    if seed is not None:
        np.random.seed(seed)

    x = gamma * np.random.standard_cauchy((M, N))

    # Build all 2^N sign vectors via bit manipulation
    num_combos = 1 << N
    indices = np.arange(num_combos, dtype=np.int64)
    signs = 1 - 2 * ((indices[:, None] >> np.arange(N)[None, :]) & 1)

    # Matrix multiply to get all signed sums
    sums = x @ signs.astype(np.float64).T  # (M, 2^N)

    # Wrap mod 2π → (-π, π]
    wrapped = np.mod(sums + np.pi, 2.0 * np.pi) - np.pi

    if M == 1:
        return wrapped[0], x[0]
    return wrapped, x
