"""Frozen v1 diagnostics for instantaneous, equal-multiplicity Born roots.

Wraps the production histogram, cosine moments, and homogeneous QZ. A pass
is a finite-resolution diagnostic, never a phase or convergence certificate.
Archived angles without homogeneous residuals cannot pass the numerical gate.
"""
from __future__ import annotations

import numpy as np

from core.born import born_ratio_from_theta
from core.born_reciprocity import born_moment_residuals, cosine_moments
from core.relative_evolution_pencil import RelativeEvolutionPencilSpectrum

SCHEMA_VERSION = "born-phase-verifier-v1"
THETA_BINS = 64
MOMENT_PAIRS = 8
RATIO_TOLERANCE = 0.05
MOMENT_TOLERANCE = 0.05
QZ_RESIDUAL_TOLERANCE = 1e-10


def evaluate_angles(theta: np.ndarray, *, expected_count: int) -> dict:
    """Audit all angles; refuse invalid/missing roots instead of filtering.

    The direct balance residual is ||nu-S_*nu|| on the fixed bin partition,
    nu=sin²(theta/2) mu. Both absolute L1 and L1/(2 nu(total)) are reported.
    Weight each root before binning; this avoids a bin-center tilt error.
    A zero tilted mass has undefined relative residual and fails coverage.
    Endpoint fractions here mean exact stored angles, not QZ classification.
    """
    values = np.asarray(theta, dtype=float)
    if not isinstance(expected_count, int) or expected_count < 1:
        raise ValueError("expected_count must be a positive integer")
    if values.shape != (expected_count,):
        raise ValueError("root count/shape mismatch")
    moments = cosine_moments(values, 2 * MOMENT_PAIRS)
    residuals = born_moment_residuals(moments)
    profile = born_ratio_from_theta(values, np.pi-values, n_theta=THETA_BINS)
    occupied = profile.counts_0 + profile.counts_1 > 0
    errors = profile.ratio[occupied] - profile.born[occupied]
    coverage = float(np.mean(occupied))
    rmse = float(np.sqrt(np.mean(errors**2)))
    moment_max = float(np.max(np.abs(residuals)))
    edges = np.linspace(0, np.pi, THETA_BINS + 1)
    weights = np.sin(values/2)**2 / expected_count
    tilted = np.histogram(values, bins=edges, weights=weights)[0]
    reflected_tilt = np.histogram(np.pi-values, bins=edges, weights=weights)[0]
    balance_l1 = float(np.sum(np.abs(tilted-reflected_tilt)))
    mass = float(np.sum(weights))
    return {
        "schema_version": SCHEMA_VERSION,
        "root_count": expected_count,
        "angle_validity": True,
        "stored_zero_angle_fraction": float(np.mean(values == 0)),
        "stored_pi_angle_fraction": float(np.mean(values == np.pi)),
        "coverage": coverage,
        "individual_polar_support": float(np.mean(profile.counts_0 > 0)),
        "occupied_ratio_rmse": rmse,
        "global_ratio_rmse": rmse if np.all(occupied) else None,
        "global_ratio_linf": float(np.max(np.abs(errors))) if np.all(occupied) else None,
        "moments": moments.tolist(),
        "moment_residuals": residuals.tolist(),
        "moment_max": moment_max,
        "tilted_mass": mass,
        "balance_binned_l1": balance_l1,
        "balance_binned_relative": balance_l1/(2*mass) if mass > 0 else None,
        "structural_gate": bool(coverage == 1 and rmse <= RATIO_TOLERANCE
                                and moment_max <= MOMENT_TOLERANCE),
        "qz_validity": None,
        "numerical_and_structural_gate": None,
        "qz_scope": "Unavailable: angles alone do not certify homogeneous roots",
        "profile": {
            "centers": profile.theta_centers.tolist(),
            "density": (profile.counts_0/expected_count*THETA_BINS/np.pi).tolist(),
            "reflected_density": (profile.counts_1/expected_count*THETA_BINS/np.pi).tolist(),
            "ratio": [float(r) if ok else None for r, ok in zip(profile.ratio, occupied)],
            "born": profile.born.tolist(),
        },
    }


def evaluate_spectrum(spectrum: RelativeEvolutionPencilSpectrum, *, expected_count: int) -> dict:
    """Attach production QZ validity, poles, residuals and conditioning.

    Small backward residuals are not a forward-error guarantee. All left
    residuals are required by this v1 gate. Missing diagnostics stay missing.
    """
    s = spectrum
    count_ok = len(s.alpha) == expected_count
    determined = not np.any(s.indeterminate)
    residuals_ok = bool(
        np.all(np.isfinite(s.homogeneous_residuals))
        and np.all(s.homogeneous_residuals <= QZ_RESIDUAL_TOLERANCE)
    )
    left_ok = (bool(np.all(np.isfinite(s.left_homogeneous_residuals))
                    and np.all(s.left_homogeneous_residuals <= QZ_RESIDUAL_TOLERANCE))
               if s.left_diagnostics_available else None)
    valid = False if not (count_ok and determined and residuals_ok) else left_ok
    result = (evaluate_angles(s.theta, expected_count=expected_count)
              if count_ok and determined else {"schema_version": SCHEMA_VERSION,
                  "root_count": len(s.alpha), "angle_validity": False,
                  "structural_gate": False, "profile": None})
    scales = np.maximum(np.abs(s.alpha), np.abs(s.beta))
    zeros = (~s.indeterminate) & (np.abs(s.alpha) <= s.projective_tolerance*scales)
    def number(value: float) -> float | None:
        return float(value) if np.isfinite(value) else None
    result.update(
        qz_validity=valid,
        qz_scope="Production homogeneous QZ with recorded diagnostic availability",
        qz_zero_fraction=float(np.mean(zeros)),
        qz_infinite_fraction=float(np.mean(s.infinite)),
        qz_indeterminate_fraction=float(np.mean(s.indeterminate)),
        qz_max_right_residual=number(s.maximum_homogeneous_residual),
        qz_max_left_residual=number(s.maximum_left_homogeneous_residual),
        qz_left_available=s.left_diagnostics_available,
        qz_max_local_coordinate_condition=number(np.max(s.local_coordinate_condition_numbers)),
        qz_nonfinite_local_condition_count=int(np.sum(~np.isfinite(s.local_coordinate_condition_numbers))),
        qz_denominator_condition=number(s.condition_number_u00),
        qz_denominator_near_singular=s.near_singular_u00_warning,
        qz_projective_tolerance=s.projective_tolerance,
        qz_residual_tolerance=QZ_RESIDUAL_TOLERANCE,
        numerical_and_structural_gate=(bool(valid and result["structural_gate"])
                                      if valid is not None else None),
    )
    return result


def summarize_conditions(records: list[dict]) -> dict:
    """Retain failures and expose condition coverage without extrapolation.

    Records have candidate, N, time, perturbation, split and diagnostics.
    Discovery and held-out results are never pooled. Lists and per-condition
    records, not a trend fit, are the size/time/perturbation diagnostics.
    """
    if not records:
        raise ValueError("at least one condition is required")
    groups = {}
    seen = set()
    for record in records:
        key = (record["candidate"], record["split"])
        identity = (*key, record["N"], record["time"], record["perturbation"])
        if identity in seen:
            raise ValueError("duplicate condition")
        seen.add(identity)
        groups.setdefault(key, []).append(record)
    summaries = []
    for (candidate, split), rows in sorted(groups.items()):
        diagnostics = [r["diagnostics"] for r in rows]
        complete = all(d is not None and d.get("angle_validity") for d in diagnostics)
        available = [d for d in diagnostics if d is not None and d.get("angle_validity")]
        def worst(metric: str) -> float | None:
            values = [d.get(metric) for d in available]
            return max(values) if complete and all(v is not None for v in values) else None
        summaries.append({
            "candidate": candidate, "split": split,
            "conditions": len(rows), "failed_conditions": len(rows)-len(available),
            "sizes": sorted({r["N"] for r in rows}),
            "times": sorted({r["time"] for r in rows}),
            "perturbations": sorted({r["perturbation"] for r in rows}),
            "worst_global_ratio_rmse": worst("global_ratio_rmse"),
            "worst_moment_max": worst("moment_max"),
            "worst_balance_binned_relative": worst("balance_binned_relative"),
            "minimum_coverage": min(d["coverage"] for d in available) if complete else None,
            "all_qz_verified": all(d is not None and d.get("qz_validity") is True for d in diagnostics),
            "all_structural_gate": complete and all(d["structural_gate"] for d in available),
            "phase_status": "OPEN: finite conditions cannot establish the required limits or basin",
        })
    return {"schema_version": SCHEMA_VERSION, "groups": summaries}
