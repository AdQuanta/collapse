"""Exact projective angles when [Hd, V]=0 and H=Hd-hz0*Z0+X0*V.

Pauli eigenvalues are +/-1, hbar=1. Detector eigenvalues retain algebraic
multiplicity. This solvable limit is not assumed for interacting ring scans.
"""

from __future__ import annotations

import numpy as np


def commuting_detector_angles(
    coupling_eigenvalues: np.ndarray, *, hz0: float, time: float,
) -> np.ndarray:
    """Fold the exact two-level solution, including zero and infinite roots.

    A simultaneous Hd eigenvalue contributes only a cancelling scalar phase.
    Evaluate homogeneous magnitudes instead of dividing by U00. At hz0=0,
    zero U00 with nonzero U10 is a well-defined infinite projective root.
    """
    values = np.asarray(coupling_eigenvalues, dtype=float)
    if values.ndim != 1 or not values.size or not np.all(np.isfinite(values)):
        raise ValueError("coupling eigenvalues must be a finite nonempty vector")
    if not np.isfinite(hz0) or not np.isfinite(time):
        raise ValueError("field and time must be finite")
    frequency = np.hypot(values, hz0)
    integrated_sine = time * np.sinc(frequency * time / np.pi)
    numerator = np.abs(values * integrated_sine)
    denominator = np.hypot(np.cos(frequency * time), hz0 * integrated_sine)
    return 2 * np.arctan2(numerator, denominator)
