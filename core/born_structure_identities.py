"""Independent checks of charge grading and conditional phase translation."""

from __future__ import annotations

import numpy as np


def shifted_symmetric_phase_angles(theta: np.ndarray, shift: float) -> np.ndarray:
    """Fold a shifted conjugation-symmetric auxiliary phase ensemble.

    Requires an auxiliary unitary with conjugate-paired phases and theta
    equal to their absolute principal values. This is NOT valid for a
    generic nonzero-hz0 relative pencil. Duplication preserves normalized
    multiplicity, not an assumption of independent samples.
    """
    values = np.asarray(theta, dtype=float)
    if values.ndim != 1 or not values.size or not np.all(np.isfinite(values)):
        raise ValueError("theta must be a finite nonempty vector")
    if np.any((values < 0) | (values > np.pi)) or not np.isfinite(shift):
        raise ValueError("invalid angle or shift")
    phases = np.r_[values, -values] + shift
    return np.abs(np.arctan2(np.sin(phases), np.cos(phases)))


def charge_grading_check(sectors: list[dict], detector_n: int, time: float, shift: int) -> dict[str, float]:
    """Check the one-way charge ladder without trusting defective eigenvalues.

    In the production QuSpin convention bit 1 has Z=+1. A central flip
    transfers +2 detector charge for exchange and -2 for pair creation.
    Relative grading errors and normalized M^(N+1) test nilpotence directly.
    """
    if shift not in (-2, 2):
        raise ValueError("charge shift must be +/-2")
    checks = []
    for sector in sectors:
        states = np.asarray(sector["states"], dtype=np.int64)
        top_bit = int(sector.get("central_top_bit", 1 if states[0] > states[-1] else 0))
        if top_bit != 1:
            raise ValueError("this identity check requires QuSpin's top-bit convention")
        top = np.where(((states >> detector_n) & 1) == 1)[0]
        bottom = np.where(((states >> detector_n) & 1) == 0)[0]
        charges = np.array([2 * (int(s) & ((1 << detector_n) - 1)).bit_count() - detector_n for s in states])
        np.testing.assert_array_equal(charges[top], charges[bottom])
        vectors, energies = sector["V"], sector["E"]
        columns = (vectors * np.exp(-1j * time * energies)) @ vectors[top, :].conj().T
        a, c = columns[top, :], columns[bottom, :]
        q = charges[top]
        differences = q[:, None] - q[None, :]
        m = np.linalg.solve(a, c)
        norm = np.linalg.norm(m)
        checks.append(dict(
            U00_charge_error=float(np.linalg.norm(differences * a) / max(np.linalg.norm(a), 1e-300)),
            U10_charge_error=float(np.linalg.norm((differences - shift) * c) / max(np.linalg.norm(c), 1e-300)),
            M_charge_error=float(np.linalg.norm((differences - shift) * m) / max(norm, 1e-300)),
            normalized_nilpotence_error=float(np.linalg.norm(np.linalg.matrix_power(m / max(norm, 1e-300), detector_n + 1))),
            U10_norm=float(np.linalg.norm(c)),
        ))
    return {key: max(c[key] for c in checks) for key in checks[0]}
