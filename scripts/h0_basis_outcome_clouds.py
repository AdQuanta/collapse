"""Redefine the outcome-0/outcome-1 split against a given qubit-0 axis.

Shared by the ad hoc h0-rotation summary figures
(``plot_h0_rotation_summary_figure.py``, ``plot_h0_rotation_summary_figure_
ring.py``) only -- not part of the frozen ``goal_preferred_basis.md``
campaign machinery (``core/outcome_measures.py``, ``scripts/eval_preferred_
basis.py``), which is left untouched.

``core/projective_roots.py``'s dual outcome pencils classify an initial
qubit-0 ray by which lab-frame Z pole (``|0>`` or ``|1>``) the *final* state
collapses to. Redefining "collapse" against a different qubit-0 axis
``n_hat`` asks the same question about the ``n_hat``-eigenbasis pole instead:
if ``R`` is the single-qubit rotation with ``R|0> = |+n_hat>``,
``R|1> = |-n_hat>``, then a ray's final state collapses to ``|+n_hat>``
exactly when ``R^dagger`` applied to the final state collapses to ``|0>``.
Left-multiplying the qubit-0 (most significant, per the house tensor-ordering
convention) block of the propagator by ``R^dagger`` therefore redefines the
outcome-0/outcome-1 split without touching the initial-state parameterization
at all: the returned Bloch points are still directions in the *original* lab
frame, so panels stay directly comparable to the Z-basis figures they are
compared against.

``R^dagger tensor I`` composed with a unitary ``U`` is itself unitary, with
the same qubit-first block structure, so ``wiki/concepts/outcome-
antipodality.md``'s antipodal-pairing theorem -- proved for *every* unitary
on the qubit-first split, with no restriction on how it was built -- applies
to the rotated propagator exactly as it does to the original; the antipodal
shortcut (outcome 1 = ``-`` outcome 0's points) stays exact.
"""

from __future__ import annotations

import numpy as np


def qubit0_pole_rotation(direction: np.ndarray) -> np.ndarray:
    """Return the 2x2 unitary ``R`` with ``R|0> = |+n_hat>``, ``R|1> = |-n_hat>``."""

    n = np.asarray(direction, dtype=float)
    n = n / np.linalg.norm(n)
    polar = np.arccos(np.clip(n[2], -1.0, 1.0))
    azimuth = np.arctan2(n[1], n[0])
    c, s = np.cos(polar / 2.0), np.sin(polar / 2.0)
    return np.array([
        [c, -s * np.exp(-1j * azimuth)],
        [s * np.exp(1j * azimuth), c],
    ], dtype=np.complex128)


def rotate_qubit0_output_basis(unitary: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Return ``(R^dagger tensor I) @ unitary`` for qubit 0 as the MSB factor."""

    rotation_dagger = qubit0_pole_rotation(direction).conj().T
    half = unitary.shape[0] // 2
    top, bottom = unitary[:half], unitary[half:]
    r00, r01 = rotation_dagger[0, 0], rotation_dagger[0, 1]
    r10, r11 = rotation_dagger[1, 0], rotation_dagger[1, 1]
    rotated = np.empty_like(unitary)
    rotated[:half] = r00 * top + r01 * bottom
    rotated[half:] = r10 * top + r11 * bottom
    return rotated
