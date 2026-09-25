r"""Outcome-resolved Bloch measures and the binning-free preferred-axis estimator.

This module implements the observable of ``goal_preferred_basis.md`` section 2:
the strong Born criterion, ``rho_0(-Omega) = tan^2(theta'/2) rho_0(Omega)`` with
``theta'`` measured from a preferred axis ``n_hat``, is equivalent to the
reweighted measure ``nu = sin^2(theta'/2) rho_0`` being inversion-symmetric,
i.e. every odd-``l`` spherical-harmonic moment of ``nu`` vanishing. Taking the
``l=1`` block of that statement gives a closed-form ``3x3`` linear solve on the
Bloch root cloud,

    S n_hat_raw = m,    S = sum_j k_j u_j u_j^T,    m = sum_j k_j u_j,
    n_hat = n_hat_raw / B1,    B1 = ||n_hat_raw||,

with Born forcing ``B1 = 1`` exactly. This is a sample moment of the labelled
root cloud, not a histogram, so it carries no bin-occupancy artifact.

Both ``SPEC.md`` section 3 outcome pencils (``forward_pole_root_spectrum`` for
outcome 0 giving ``rho_0``, and for outcome 1 giving ``rho_1``) feed this
estimator through :func:`outcome_bloch_cloud`. ``core.gleason_diagnostics``
supplies the ``SPEC.md`` section 6 diagnostic quartet (``E_2``, ``E_inf``,
``E_harm``, ``E_marg``) as a histogram-based cross-check, evaluated at the
axis this module fits.

Cost note (goal section 4, WP1): exact kernel-dimension weights need one SVD
per distinct root (``core.pencil_characterization.characterize_pencil_roots``),
which is ``O(n^4)`` and infeasible at ``n=4096``. This module therefore uses
``k_j=1`` per raw projective root returned by ``forward_pole_root_spectrum``,
and records that spectrum's own QZ duplicate-cluster diagnostics as a guard
rather than performing the SVD kernel-dimension computation. Callers that need
certified kernel dimensions should run ``characterize_pencil_roots`` directly,
at ``N <= 6`` only, to certify genericity (goal section 4, WP1).

Mandatory fail-closed branch (goal section 2.4): ``S`` is singular exactly
when the roots collapse onto a great circle or a point -- the degenerate case
``RESEARCH_STATE.md`` section 3 warns satisfies moment relations vacuously,
and it is reachable in the approved families (central-X great-circle
confinement, nilpotent collapsed laws; ``RESEARCH_STATE.md`` section 5).
:func:`preferred_axis_from_cloud` gates on ``cond(S)`` and refuses to report an
axis when it is ill-conditioned, rather than returning a numerically arbitrary
answer.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import sph_harm_y

from core.gleason_diagnostics import (
    FullSphereBornDiagnostics,
    _equal_area_geometry,
    _power_by_degree,
    diagnose_labeled_bloch_histogram,
)
from core.projective_roots import (
    bloch_vectors_from_homogeneous,
    forward_pole_root_spectrum,
)
from core.spherical_harmonics import SphericalHarmonicExpansion

#: Condition-number gate for the 3x3 preferred-axis system, matching the house
#: ill-conditioning convention used for the (much larger) relative-evolution
#: pencil in ``scripts/eval_chain_born.py`` (``ILL_CONDITIONED_THRESHOLD``).
PREFERRED_AXIS_COND_MAX = 1.0e6

#: Default equal-area histogram resolution for the SPEC.md section 6 quartet,
#: matching ``core.gleason_diagnostics.diagnose_labeled_bloch_histogram``'s own
#: default. If it fails to cover the whole sphere the resolution is reduced
#: along this ladder and the resolution actually used is always reported.
#: Every rung has at least ``(l_max + 1)**2 = 64`` cells for the default
#: ``l_max = 7``, so the harmonic least-squares fit is never rank deficient
#: purely from too few cells.
QUARTET_RESOLUTION_LADDER: tuple[tuple[int, int], ...] = (
    (18, 36),
    (12, 24),
    (9, 18),
    (8, 16),
)


@dataclass(frozen=True)
class BlochCloud:
    """One outcome pencil's projective root cloud, mapped to the Bloch sphere."""

    points: np.ndarray
    weights: np.ndarray
    n_raw_roots: int
    n_indeterminate: int
    largest_cluster_multiplicity: int
    distinct_root_count: int


def outcome_bloch_cloud(
    unitary: np.ndarray,
    outcome: int,
    **solver_options: object,
) -> BlochCloud:
    """Return the ``SPEC.md`` section 3 outcome-``outcome`` Bloch root cloud.

    Every non-indeterminate projective root is kept with weight ``k_j = 1``
    (see the module docstring's cost note). The pencil's own QZ
    duplicate-cluster diagnostics are recorded as the duplicate-detection
    guard the campaign uses in place of exact kernel dimensions.
    """

    spectrum = forward_pole_root_spectrum(unitary, outcome, **solver_options)
    vectors = bloch_vectors_from_homogeneous(spectrum.alpha, spectrum.beta)
    valid = np.all(np.isfinite(vectors), axis=1)
    duplicate = spectrum.duplicate_diagnostics
    return BlochCloud(
        points=vectors[valid],
        weights=np.ones(int(np.count_nonzero(valid)), dtype=float),
        n_raw_roots=int(vectors.shape[0]),
        n_indeterminate=int(np.count_nonzero(~valid)),
        largest_cluster_multiplicity=int(duplicate.largest_multiplicity),
        distinct_root_count=int(duplicate.distinct_root_count),
    )


def antipodal_bloch_cloud(cloud: BlochCloud) -> BlochCloud:
    """Return outcome 1's Bloch cloud as the antipodal pushforward of outcome 0's.

    Unitarity alone forces ``rho_1 = A_* rho_0`` for the antipodal map
    ``A: r -> -r``, weights included, for *every* unitary -- this is unrelated
    to (and unconditional on) the ``h_0y = 0`` restriction that limits the
    separate fixed-input/outcome-0 shortcut
    (``wiki/concepts/fixed-input-outcome-equivalence.md``). It is proved in
    ``wiki/concepts/outcome-antipodality.md`` and certified numerically,
    including on the exact approved endpoint-chain family, by
    ``tests/test_outcome_antipodality.py::test_approved_families_have_antipodal_outcome_sets``.

    Using it in place of a second ``forward_pole_root_spectrum`` solve is
    therefore exact, not an approximation, and it halves the pencil-solving
    cost of every measurement in this module. ``outcome_bloch_cloud(unitary,
    outcome=1, ...)`` remains available to verify this identity directly
    against an independent QZ solve.
    """

    return BlochCloud(
        points=-cloud.points,
        weights=cloud.weights.copy(),
        n_raw_roots=cloud.n_raw_roots,
        n_indeterminate=cloud.n_indeterminate,
        largest_cluster_multiplicity=cloud.largest_cluster_multiplicity,
        distinct_root_count=cloud.distinct_root_count,
    )


@dataclass(frozen=True)
class PreferredAxisResult:
    """The closed-form preferred axis and dipole magnitude, or a refusal."""

    status: str
    n_hat: np.ndarray | None
    B1: float | None
    S: np.ndarray
    m: np.ndarray
    condition_number: float
    n_points: int
    total_weight: float
    refusal_reason: str | None


def preferred_axis_from_cloud(
    points: np.ndarray,
    weights: np.ndarray,
    *,
    cond_max: float = PREFERRED_AXIS_COND_MAX,
) -> PreferredAxisResult:
    """Solve ``S n_hat_raw = m`` for the preferred axis and ``B1``.

    ``points`` need not come from a root cloud: the acceptance tests in
    ``goal_preferred_basis.md`` section 2.5 feed it a density-weighted
    quadrature grid instead, and the same closed form applies unchanged since
    it is a moment of whatever measure ``(points, weights)`` represents.

    Refuses (``status="singular_refused"``) rather than reporting an axis when
    ``S`` is ill-conditioned or the dipole moment vanishes -- the mandatory
    fail-closed branch of goal section 2.4.
    """

    u = np.asarray(points, dtype=float)
    k = np.asarray(weights, dtype=float)
    if u.ndim != 2 or u.shape[1] != 3 or u.shape[0] == 0:
        raise ValueError("points must have shape (n, 3) with n > 0")
    if k.shape != (u.shape[0],):
        raise ValueError("weights must have one entry per point")
    if not np.all(np.isfinite(u)) or not np.all(np.isfinite(k)):
        raise ValueError("points and weights must be finite")
    if np.any(k < 0.0):
        raise ValueError("weights must be nonnegative")

    S = np.einsum("j,ja,jb->ab", k, u, u)
    m = np.einsum("j,ja->a", k, u)
    total_weight = float(np.sum(k))
    condition_number = float(np.linalg.cond(S))

    if not np.isfinite(condition_number) or condition_number > cond_max:
        return PreferredAxisResult(
            status="singular_refused",
            n_hat=None,
            B1=None,
            S=S,
            m=m,
            condition_number=condition_number,
            n_points=int(u.shape[0]),
            total_weight=total_weight,
            refusal_reason=(
                f"cond(S)={condition_number:.3e} exceeds {cond_max:.3e}: roots "
                "are confined to a great circle or a point (RESEARCH_STATE.md "
                "section 5); the preferred axis is not numerically defined"
            ),
        )

    n_raw = np.linalg.solve(S, m)
    B1 = float(np.linalg.norm(n_raw))
    if B1 == 0.0:
        return PreferredAxisResult(
            status="singular_refused",
            n_hat=None,
            B1=0.0,
            S=S,
            m=m,
            condition_number=condition_number,
            n_points=int(u.shape[0]),
            total_weight=total_weight,
            refusal_reason="dipole moment vanishes exactly: B1 = 0",
        )
    n_hat = n_raw / B1
    return PreferredAxisResult(
        status="ok",
        n_hat=n_hat,
        B1=B1,
        S=S,
        m=m,
        condition_number=condition_number,
        n_points=int(u.shape[0]),
        total_weight=total_weight,
        refusal_reason=None,
    )


def odd_harmonic_power(
    points: np.ndarray,
    weights: np.ndarray,
    axis: np.ndarray,
    *,
    l_max: int = 7,
) -> dict[str, object]:
    """Return the degree-``l`` power spectrum of the reweighted measure ``nu``.

    ``nu = sin^2(theta'/2) * (point measure)``, with ``theta'`` measured from
    ``axis``; this is the same reweighting used in the ``S n_hat = m`` solve
    (goal section 2.1-2.2). Its coefficients are exact moments of the discrete
    weighted point cloud, ``sum_j nu_j conj(Y_lm(u_j))`` -- no histogram or
    quadrature grid is involved, so there is no bin-occupancy artifact.
    Degree-``l`` power (summed over order ``m``) is rotation invariant, so it
    does not matter that ``(theta, phi)`` below are lab-frame coordinates
    rather than coordinates aligned with ``axis``.
    """

    u = np.asarray(points, dtype=float)
    k = np.asarray(weights, dtype=float)
    n_hat = np.asarray(axis, dtype=float)
    n_hat = n_hat / np.linalg.norm(n_hat)

    cos_theta_prime = np.clip(u @ n_hat, -1.0, 1.0)
    nu_weight = k * (1.0 - cos_theta_prime) / 2.0
    theta = np.arccos(np.clip(u[:, 2], -1.0, 1.0))
    phi = np.arctan2(u[:, 1], u[:, 0])

    coefficients = np.zeros((l_max + 1, 2 * l_max + 1), dtype=np.complex128)
    for degree in range(l_max + 1):
        for order in range(-degree, degree + 1):
            harmonic = sph_harm_y(degree, order, theta, phi)
            coefficients[degree, order + l_max] = np.sum(nu_weight * np.conj(harmonic))
    expansion = SphericalHarmonicExpansion(l_max=l_max, coefficients=coefficients)
    power = _power_by_degree(expansion)
    odd_power = float(np.sum(power[1::2]))
    even_power = float(np.sum(power[0::2]))
    higher_odd = float(np.sum(power[3::2]))
    total_power = float(np.sum(power))

    # The l=1 moment of nu is driven to ~0 by construction: n_hat is exactly
    # the axis that zeros it (S n_hat = m). Normalizing l>=3 power by "odd
    # power" (l=1+3+5+...) is therefore ill-conditioned at genuine Born
    # agreement, where l=1 and l=3,5,7 all vanish together -- the ratio would
    # divide noise by noise. Total power (all l, dominated by the non-trivial
    # even sectors) stays well away from zero, so it is the well-defined
    # denominator for "how much genuine residual odd(l>=3) content survives
    # the l=1 fit."
    higher_odd_leakage = higher_odd / total_power if total_power > 0.0 else float("nan")

    return {
        "power_by_l": power,
        "odd_power": odd_power,
        "even_power": even_power,
        "total_power": total_power,
        "l1_power_fraction": (power[1] / total_power) if total_power > 0.0 else float("nan"),
        "higher_odd_l3_l5_l7_leakage": higher_odd_leakage,
        "total_reweighted_mass": float(np.sum(nu_weight)),
        "n_points": int(u.shape[0]),
    }


def weak_marginal_error(
    points_0: np.ndarray,
    weights_0: np.ndarray,
    points_1: np.ndarray,
    weights_1: np.ndarray,
    axis: np.ndarray,
    *,
    n_bins: int = 100,
) -> dict[str, object]:
    """Return the ``SPEC.md`` section 6.4 weak-marginal error, ``E_marg``.

    Both outcome pencils' genuine polar marginals (relative to ``axis``, not
    to a lab-frame pole) are compared against their Born targets
    ``cos^2(theta'/2)`` and ``sin^2(theta'/2)`` with a ``sin(theta')`` weight,
    over bins where either marginal has support -- unlike the weak-criterion
    machinery in ``scripts/eval_chain_born.py``, which read one pencil's
    reflection as a synthetic stand-in for the second label. That shortcut is
    invalid at ``screen_00`` because ``h_0y != 0`` (goal section 4, WP1;
    ``wiki/concepts/fixed-input-outcome-equivalence.md``), so this module
    always uses the genuine second outcome pencil.
    """

    n_hat = np.asarray(axis, dtype=float)
    n_hat = n_hat / np.linalg.norm(n_hat)
    theta_0 = np.arccos(np.clip(np.asarray(points_0, dtype=float) @ n_hat, -1.0, 1.0))
    theta_1 = np.arccos(np.clip(np.asarray(points_1, dtype=float) @ n_hat, -1.0, 1.0))

    edges = np.linspace(0.0, np.pi, n_bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    width = edges[1] - edges[0]
    counts_0, _ = np.histogram(theta_0, bins=edges, weights=np.asarray(weights_0, dtype=float))
    counts_1, _ = np.histogram(theta_1, bins=edges, weights=np.asarray(weights_1, dtype=float))
    total_0 = float(np.sum(counts_0))
    total_1 = float(np.sum(counts_1))
    density_0 = counts_0 / (total_0 * width) if total_0 > 0.0 else np.zeros_like(counts_0)
    density_1 = counts_1 / (total_1 * width) if total_1 > 0.0 else np.zeros_like(counts_1)
    occupied = (counts_0 + counts_1) > 0.0

    target_0 = np.cos(centers / 2.0) ** 2
    target_1 = np.sin(centers / 2.0) ** 2
    sin_weight = np.sin(centers)

    def weighted_rms(density: np.ndarray, target: np.ndarray) -> float:
        if not np.any(occupied):
            return float("nan")
        w = sin_weight[occupied]
        total = float(np.sum(w))
        if total <= 0.0:
            return float("nan")
        squared = (density[occupied] - target[occupied]) ** 2
        return float(np.sqrt(np.sum(squared * w) / total))

    e_marg_0 = weighted_rms(density_0, target_0)
    e_marg_1 = weighted_rms(density_1, target_1)
    finite = [value for value in (e_marg_0, e_marg_1) if np.isfinite(value)]
    e_marg = float(np.sqrt(np.mean(np.square(finite)))) if finite else float("nan")

    return {
        "E_marg": e_marg,
        "E_marg_0": e_marg_0,
        "E_marg_1": e_marg_1,
        "coverage_bins": int(np.count_nonzero(occupied)),
        "n_bins": n_bins,
    }


def spec_quartet(
    points_0: np.ndarray,
    weights_0: np.ndarray,
    points_1: np.ndarray,
    weights_1: np.ndarray,
    axis: np.ndarray,
    *,
    l_max: int = 7,
    resolution_ladder: tuple[tuple[int, int], ...] = QUARTET_RESOLUTION_LADDER,
    marginal_bins: int = 100,
) -> dict[str, object]:
    """Return the ``SPEC.md`` section 6 quartet ``E_2, E_inf, E_harm, E_marg``.

    ``E_2`` and ``E_harm`` are read off ``core.gleason_diagnostics``'s
    labelled-histogram diagnostics at the fitted axis: ``E_2`` is half the
    reported area-RMS deviation of the asymmetry field from its target (since
    ``p_0 - cos^2(theta'/2) = (a - n_hat.r) / 2``), and ``E_harm`` is that same
    module's normalized odd-``l>=3`` leakage fraction, which is exactly the
    quantity goal section 2.2 asks this campaign to report and is rotation
    invariant so it does not depend on the histogram's coordinate frame.
    ``E_inf`` is computed directly from the same histogram's occupied cells.
    ``E_marg`` is :func:`weak_marginal_error`, using the genuine second
    outcome pencil rather than an antipodal-reflection stand-in.

    This is one specific, documented operational reading of the SPEC.md
    quartet's prose definitions; it is disclosed explicitly here rather than
    asserted as the unique correct one, per the estimator-robustness
    requirement (SPEC.md section 6.5).
    """

    n_hat = np.asarray(axis, dtype=float)
    n_hat = n_hat / np.linalg.norm(n_hat)

    resolution_used = None
    histogram = None
    last_error: str | None = None
    for n_mu, n_phi in resolution_ladder:
        try:
            candidate = diagnose_labeled_bloch_histogram(
                roots_0=points_0,
                roots_1=points_1,
                weights_0=weights_0,
                weights_1=weights_1,
                n_mu=n_mu,
                n_phi=n_phi,
                target_axis=n_hat,
                l_max=l_max,
                require_full_coverage=True,
            )
        except ValueError as error:
            # Too few occupied cells to resolve l_max harmonics by weighted
            # least squares at this resolution; try a coarser rung.
            last_error = str(error)
            continue
        histogram = candidate
        resolution_used = (n_mu, n_phi)
        if candidate.diagnostics is not None:
            break

    marginal = weak_marginal_error(
        points_0, weights_0, points_1, weights_1, n_hat, n_bins=marginal_bins
    )

    if histogram is None or histogram.diagnostics is None:
        return {
            "E_2": float("nan"),
            "E_inf": float("nan"),
            "E_harm": float("nan"),
            "even_fraction_of_total_power": float("nan"),
            "E_marg": marginal["E_marg"],
            "E_marg_0": marginal["E_marg_0"],
            "E_marg_1": marginal["E_marg_1"],
            "quartet_coverage": histogram.coverage if histogram is not None else 0.0,
            "quartet_resolution": resolution_used,
            "marginal_coverage_bins": marginal["coverage_bins"],
            "marginal_n_bins": marginal["n_bins"],
            "quartet_status": (
                "refused: incomplete equal-area coverage at every resolution on "
                f"the ladder ({last_error})" if last_error else
                "refused: incomplete equal-area coverage at every resolution on the ladder"
            ),
        }

    diagnostics: FullSphereBornDiagnostics = histogram.diagnostics
    n_mu, n_phi = resolution_used
    _, _, directions, _ = _equal_area_geometry(n_mu, n_phi)
    target = np.einsum("...i,i->...", directions, n_hat)
    asymmetry = histogram.asymmetry
    occupied = histogram.occupied
    e_inf = float(np.max(np.abs(asymmetry[occupied] - target[occupied])) / 2.0) if np.any(occupied) else float("nan")

    return {
        "E_2": diagnostics.born_rms_area / 2.0,
        "E_inf": e_inf,
        "E_harm": diagnostics.higher_odd_harmonic_leakage,
        "even_fraction_of_total_power": diagnostics.even_fraction_of_total_power,
        "E_marg": marginal["E_marg"],
        "E_marg_0": marginal["E_marg_0"],
        "E_marg_1": marginal["E_marg_1"],
        "quartet_coverage": histogram.coverage,
        "quartet_resolution": resolution_used,
        "marginal_coverage_bins": marginal["coverage_bins"],
        "marginal_n_bins": marginal["n_bins"],
        "quartet_status": "ok",
    }


def outcome_measures_report(
    unitary: np.ndarray,
    *,
    l_max: int = 7,
    cond_max: float = PREFERRED_AXIS_COND_MAX,
    resolution_ladder: tuple[tuple[int, int], ...] = QUARTET_RESOLUTION_LADDER,
    marginal_bins: int = 100,
    **solver_options: object,
) -> dict[str, object]:
    """Return the full preferred-basis measurement for one unitary snapshot.

    Solves the outcome-0 pencil, fits the preferred axis from its root cloud,
    and reports ``B1``, the axis, the odd-``l`` leakage at that axis, and the
    ``SPEC.md`` section 6 quartet. Outcome 1's cloud is the exact antipodal
    pushforward of outcome 0's (:func:`antipodal_bloch_cloud`), not a second
    QZ solve. Refuses cleanly (goal section 2.4) when the outcome-0 cloud does
    not determine an axis.
    """

    cloud_0 = outcome_bloch_cloud(unitary, outcome=0, **solver_options)
    cloud_1 = antipodal_bloch_cloud(cloud_0)

    axis_result = preferred_axis_from_cloud(cloud_0.points, cloud_0.weights, cond_max=cond_max)

    report: dict[str, object] = {
        "cloud_0": cloud_0,
        "cloud_1": cloud_1,
        "axis_result": axis_result,
    }

    if axis_result.status != "ok":
        report["status"] = "refused"
        report["refusal_reason"] = axis_result.refusal_reason
        return report

    n_hat = axis_result.n_hat
    report["status"] = "ok"
    report["n_hat"] = n_hat
    report["B1"] = axis_result.B1
    report["condition_number"] = axis_result.condition_number
    report["odd_harmonic"] = odd_harmonic_power(
        cloud_0.points, cloud_0.weights, n_hat, l_max=l_max
    )
    report["quartet"] = spec_quartet(
        cloud_0.points,
        cloud_0.weights,
        cloud_1.points,
        cloud_1.weights,
        n_hat,
        l_max=l_max,
        resolution_ladder=resolution_ladder,
        marginal_bins=marginal_bins,
    )
    return report
