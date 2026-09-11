"""Exact root measure for uniform coupling to an isotropic spin detector.

Hd = -sum_edges J_ij (Xi Xj + Yi Yj + Zi Zj) - hz sum_i Zi,
Hqd = -(Jx/sqrt(N)) X0 sum_i Xi, Hq=0, with hbar=1 and Pauli +/-1.
The isotropic interaction commutes with all collective spin components and
cancels from the relative pencil. Graph weights do not enter this measure.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import binom


def isotropic_root_measure(
    detector_n: int, *, collective_jx: float, hz: float, time: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return N+1 folded angles and their binomial multiplicity weights.

    Coincident folded angles remain separate entries with additive weights.
    Their number of distinct values is at most floor(N/2)+1. This is the
    exact full-space counting measure, not a symmetric-spin-sector measure.
    It requires uniform detector field and coupling, hz0=hx0=Jy=0, and
    isotropic interactions on every edge (native Jpm=2J and Jpm2=2J2).
    """
    if not isinstance(detector_n, int) or detector_n < 1:
        raise ValueError("detector_n must be a positive integer")
    if not np.all(np.isfinite([collective_jx, hz, time])):
        raise ValueError("coupling, field and time must be finite")
    g = collective_jx / np.sqrt(detector_n)
    omega = np.hypot(hz, g)
    sine = g * time * np.sinc(omega * time / np.pi)
    phase = 2 * np.arcsin(np.clip(abs(sine), 0., 1.))
    m = np.arange(detector_n + 1)
    total_phase = (detector_n - 2 * m) * phase
    theta = np.abs(np.arctan2(np.sin(total_phase), np.cos(total_phase)))
    weights = binom.pmf(m, detector_n, .5)
    return theta, weights / weights.sum()
