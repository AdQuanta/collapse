"""Full-sphere diagnostics for Born-compatible labelled root geometry.

This module analyzes the angular asymmetry

``a(Omega) = (rho0(Omega) - rho1(Omega)) / (rho0(Omega) + rho1(Omega))``.

Unitarity pairs the two labelled root measures by antipodes, which makes the
exact asymmetry inversion-odd.  A trace-rule qubit measurement is more
restrictive: ``a(r) = n dot r`` is a pure degree-one spherical harmonic.  The
diagnostics below deliberately keep those statements separate from any
physical probability or root-selection measure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from collapse.spherical_harmonics import (
    SphericalHarmonicExpansion,
    SphericalHarmonicProjector,
)


@dataclass(frozen=True)
class FullSphereBornDiagnostics:
    """Harmonic and geometric diagnostics of a resolved asymmetry field."""

    l_max: int
    power_by_l: np.ndarray
    odd_power: float
    even_power: float
    higher_odd_harmonic_leakage: float
    p1_over_podd: float
    even_fraction_of_total_power: float
    dipole_vector: np.ndarray
    dipole_sharpness: float
    axis_fidelity: float
    axis_defined: bool
    born_rms_area: float
    born_rms_density_weighted: float
    epsilon_born: float
    epsilon_born_density_weighted: float
    epsilon_antipodal: float
    asymmetry_l2_power: float
    expansion: SphericalHarmonicExpansion
    quadrature: str


@dataclass(frozen=True)
class EqualAreaLabeledHistogram:
    """Labelled densities and asymmetry on a uniform ``(mu, phi)`` grid."""

    mu_edges: np.ndarray
    phi_edges: np.ndarray
    counts_0: np.ndarray
    counts_1: np.ndarray
    density_0: np.ndarray
    density_1: np.ndarray
    total_density: np.ndarray
    asymmetry: np.ndarray
    occupied: np.ndarray
    coverage: float
    root_weight_0: float
    root_weight_1: float
    pseudocount: float
    born_density_ratio_cross_residual: float | None
    diagnostics: FullSphereBornDiagnostics | None


def _unit_vector(vector: np.ndarray, name: str) -> np.ndarray:
    values = np.asarray(vector, dtype=float)
    if values.shape != (3,) or not np.all(np.isfinite(values)):
        raise ValueError(f"{name} must be a finite vector of shape (3,)")
    norm = float(np.linalg.norm(values))
    if norm == 0.0:
        raise ValueError(f"{name} must be nonzero")
    return values / norm


def _power_by_degree(expansion: SphericalHarmonicExpansion) -> np.ndarray:
    coefficients = expansion.as_array(copy=False)
    powers = np.empty(expansion.l_max + 1, dtype=float)
    for degree in range(expansion.l_max + 1):
        orders = slice(expansion.l_max - degree, expansion.l_max + degree + 1)
        powers[degree] = float(np.sum(np.abs(coefficients[degree, orders]) ** 2))
    return powers


def _finish_diagnostics(
    *,
    asymmetry: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray,
    antipodal_asymmetry: np.ndarray,
    target_axis: np.ndarray,
    expansion: SphericalHarmonicExpansion,
    density_weight: np.ndarray | None,
    axis_tolerance: float,
    quadrature: str,
) -> FullSphereBornDiagnostics:
    values = np.asarray(asymmetry, dtype=float)
    vectors = np.asarray(directions, dtype=float)
    area_weights = np.broadcast_to(np.asarray(weights, dtype=float), values.shape)
    antipodes = np.asarray(antipodal_asymmetry, dtype=float)
    if vectors.shape != values.shape + (3,):
        raise ValueError("directions must have shape asymmetry.shape + (3,)")
    if antipodes.shape != values.shape:
        raise ValueError("antipodal_asymmetry must match asymmetry")
    if not (
        np.all(np.isfinite(values))
        and np.all(np.isfinite(vectors))
        and np.all(np.isfinite(area_weights))
        and np.all(area_weights > 0.0)
    ):
        raise ValueError("asymmetry, directions, and weights must be finite")

    target = np.einsum("...i,i->...", vectors, target_axis)
    asymmetry_power = float(np.sum(area_weights * values**2))
    anti_numerator = float(np.sum(area_weights * (values + antipodes) ** 2))
    epsilon_antipodal = (
        float(np.sqrt(anti_numerator / asymmetry_power))
        if asymmetry_power > 0.0
        else 0.0
    )

    target_power = float(np.sum(area_weights * target**2))
    born_numerator = float(np.sum(area_weights * (values - target) ** 2))
    total_area = float(np.sum(area_weights))
    born_rms_area = float(np.sqrt(born_numerator / total_area))
    epsilon_born = (
        float(np.sqrt(born_numerator / target_power))
        if target_power > 0.0
        else np.nan
    )

    if density_weight is None:
        epsilon_born_weighted = epsilon_born
        born_rms_weighted = born_rms_area
    else:
        density = np.broadcast_to(np.asarray(density_weight, dtype=float), values.shape)
        if not np.all(np.isfinite(density)) or np.any(density < 0.0):
            raise ValueError("density_weight must be finite and nonnegative")
        weighted_target_power = float(np.sum(area_weights * density * target**2))
        weighted_numerator = float(
            np.sum(area_weights * density * (values - target) ** 2)
        )
        total_density_weight = float(np.sum(area_weights * density))
        born_rms_weighted = (
            float(np.sqrt(weighted_numerator / total_density_weight))
            if total_density_weight > 0.0
            else np.nan
        )
        epsilon_born_weighted = (
            float(np.sqrt(weighted_numerator / weighted_target_power))
            if weighted_target_power > 0.0
            else np.nan
        )

    dipole = (3.0 / (4.0 * np.pi)) * np.sum(
        (area_weights * values)[..., None] * vectors,
        axis=tuple(range(values.ndim)),
    )
    sharpness = float(np.linalg.norm(dipole))
    axis_defined = bool(sharpness > axis_tolerance)
    axis_fidelity = (
        float(np.dot(dipole / sharpness, target_axis)) if axis_defined else np.nan
    )

    power = _power_by_degree(expansion)
    odd_power = float(np.sum(power[1::2]))
    even_power = float(np.sum(power[0::2]))
    p1 = float(power[1]) if expansion.l_max >= 1 else 0.0
    higher_odd = float(np.sum(power[3::2]))
    total_power = odd_power + even_power
    leakage = higher_odd / odd_power if odd_power > 0.0 else np.nan
    p1_over_podd = p1 / odd_power if odd_power > 0.0 else np.nan
    even_fraction = even_power / total_power if total_power > 0.0 else 0.0

    return FullSphereBornDiagnostics(
        l_max=expansion.l_max,
        power_by_l=power,
        odd_power=odd_power,
        even_power=even_power,
        higher_odd_harmonic_leakage=float(leakage),
        p1_over_podd=float(p1_over_podd),
        even_fraction_of_total_power=float(even_fraction),
        dipole_vector=np.asarray(dipole, dtype=float),
        dipole_sharpness=sharpness,
        axis_fidelity=axis_fidelity,
        axis_defined=axis_defined,
        born_rms_area=born_rms_area,
        born_rms_density_weighted=born_rms_weighted,
        epsilon_born=epsilon_born,
        epsilon_born_density_weighted=epsilon_born_weighted,
        epsilon_antipodal=epsilon_antipodal,
        asymmetry_l2_power=asymmetry_power,
        expansion=expansion,
        quadrature=quadrature,
    )


def diagnose_asymmetry_function(
    function: Callable[[np.ndarray, np.ndarray], np.ndarray],
    *,
    target_axis: np.ndarray | None = None,
    l_max: int = 7,
    n_theta: int | None = None,
    n_phi: int | None = None,
    density_weight: Callable[[np.ndarray, np.ndarray], np.ndarray] | None = None,
    axis_tolerance: float = 1.0e-12,
) -> FullSphereBornDiagnostics:
    """Diagnose a callable field using Gauss--Legendre/azimuthal quadrature."""

    if l_max < 1:
        raise ValueError("l_max must be at least one")
    if axis_tolerance < 0.0:
        raise ValueError("axis_tolerance must be nonnegative")
    axis = _unit_vector(
        np.array([0.0, 0.0, 1.0]) if target_axis is None else target_axis,
        "target_axis",
    )
    projector = SphericalHarmonicProjector(
        l_max=l_max,
        n_theta=n_theta,
        n_phi=n_phi,
    )
    theta = projector.theta[:, None]
    phi = projector.phi[None, :]
    samples = np.asarray(function(theta, phi), dtype=float)
    samples = np.broadcast_to(samples, projector.grid_shape)
    anti_samples = np.asarray(
        function(np.pi - theta, np.mod(phi + np.pi, 2.0 * np.pi)),
        dtype=float,
    )
    anti_samples = np.broadcast_to(anti_samples, projector.grid_shape)
    sin_theta = np.sin(theta)
    directions = np.stack(
        np.broadcast_arrays(
            sin_theta * np.cos(phi),
            sin_theta * np.sin(phi),
            np.cos(theta) + np.zeros_like(phi),
        ),
        axis=-1,
    )
    weights = projector.theta_weights[:, None] * (2.0 * np.pi / projector.n_phi)
    expansion = projector.project_samples(samples, real_input=True)
    sampled_density = None
    if density_weight is not None:
        sampled_density = np.broadcast_to(
            np.asarray(density_weight(theta, phi), dtype=float),
            projector.grid_shape,
        )
    return _finish_diagnostics(
        asymmetry=samples,
        directions=directions,
        weights=weights,
        antipodal_asymmetry=anti_samples,
        target_axis=axis,
        expansion=expansion,
        density_weight=sampled_density,
        axis_tolerance=axis_tolerance,
        quadrature="Gauss-Legendre in cos(theta), uniform Fourier grid in phi",
    )


def antipodal_equal_area_field(field: np.ndarray) -> np.ndarray:
    """Evaluate a uniform ``(mu,phi)`` grid field at antipodal cell centers."""

    values = np.asarray(field)
    if values.ndim != 2 or values.shape[1] % 2:
        raise ValueError("field must be 2-D with an even number of phi bins")
    return np.roll(np.flip(values, axis=0), values.shape[1] // 2, axis=1)


def born_density_ratio_cross_residual(
    density_0: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray | float,
    *,
    target_axis: np.ndarray | None = None,
) -> float:
    r"""Test ``rho0(-Omega)/rho0(Omega)=|lambda_n|^2`` without division.

    For stereographic coordinates relative to ``target_axis=n``, the ideal
    ratio is ``(1-n.r)/(1+n.r)``. The returned normalized residual compares
    ``rho0(-r)(1+n.r)`` with ``rho0(r)(1-n.r)``. This cross-multiplied form is
    finite at poles and in cells where one density vanishes.
    """

    density = np.asarray(density_0, dtype=float)
    vectors = np.asarray(directions, dtype=float)
    if density.ndim != 2 or vectors.shape != density.shape + (3,):
        raise ValueError("density_0 and directions must have shapes (m,p) and (m,p,3)")
    if not np.all(np.isfinite(density)) or np.any(density < 0.0):
        raise ValueError("density_0 must be finite and nonnegative")
    quadrature = np.broadcast_to(np.asarray(weights, dtype=float), density.shape)
    if not np.all(np.isfinite(quadrature)) or np.any(quadrature <= 0.0):
        raise ValueError("weights must be finite and positive")
    axis = _unit_vector(
        np.array([0.0, 0.0, 1.0]) if target_axis is None else target_axis,
        "target_axis",
    )
    projection = np.einsum("...i,i->...", vectors, axis)
    antipodal_density = antipodal_equal_area_field(density)
    left = antipodal_density * (1.0 + projection)
    right = density * (1.0 - projection)
    denominator = float(np.sum(quadrature * (left + right) ** 2))
    numerator = float(np.sum(quadrature * (left - right) ** 2))
    if denominator == 0.0:
        return 0.0 if numerator == 0.0 else np.inf
    return float(np.sqrt(numerator / denominator))


def _equal_area_geometry(
    n_mu: int,
    n_phi: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if n_mu < 1:
        raise ValueError("n_mu must be positive")
    if n_phi < 2 or n_phi % 2:
        raise ValueError("n_phi must be a positive even integer")
    mu_edges = np.linspace(-1.0, 1.0, n_mu + 1)
    phi_edges = np.linspace(-np.pi, np.pi, n_phi + 1)
    mu = 0.5 * (mu_edges[:-1] + mu_edges[1:])
    phi = 0.5 * (phi_edges[:-1] + phi_edges[1:])
    transverse = np.sqrt(np.maximum(0.0, 1.0 - mu[:, None] ** 2))
    directions = np.stack(
        np.broadcast_arrays(
            transverse * np.cos(phi[None, :]),
            transverse * np.sin(phi[None, :]),
            mu[:, None] + np.zeros((1, n_phi)),
        ),
        axis=-1,
    )
    solid_angle = np.full(
        (n_mu, n_phi),
        (mu_edges[1] - mu_edges[0]) * (phi_edges[1] - phi_edges[0]),
    )
    return mu_edges, phi_edges, directions, solid_angle


def _midpoint_harmonic_expansion(
    asymmetry: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray,
    l_max: int,
) -> SphericalHarmonicExpansion:
    from scipy.special import sph_harm_y

    theta = np.arccos(np.clip(directions[..., 2], -1.0, 1.0))
    phi = np.arctan2(directions[..., 1], directions[..., 0])
    coefficients = np.zeros((l_max + 1, 2 * l_max + 1), dtype=np.complex128)
    for degree in range(l_max + 1):
        for order in range(-degree, degree + 1):
            harmonic = sph_harm_y(degree, order, theta, phi)
            coefficients[degree, order + l_max] = np.sum(
                weights * asymmetry * np.conj(harmonic)
            )
    return SphericalHarmonicExpansion(l_max=l_max, coefficients=coefficients)


def _least_squares_harmonic_expansion(
    asymmetry: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray,
    l_max: int,
) -> SphericalHarmonicExpansion:
    """Fit a band-limited harmonic field to equal-area cell-center values.

    Unlike a midpoint quadrature, this estimator exactly recovers any field in
    the retained harmonic span when the sampled design has full column rank.
    This matters on coarse grids, where midpoint quadrature can alias an exact
    dipole into high odd degrees.
    """

    from scipy.special import sph_harm_y

    theta = np.arccos(np.clip(directions[..., 2], -1.0, 1.0)).ravel()
    phi = np.arctan2(directions[..., 1], directions[..., 0]).ravel()
    columns: list[np.ndarray] = []
    indices: list[tuple[int, int]] = []
    for degree in range(l_max + 1):
        for order in range(-degree, degree + 1):
            columns.append(sph_harm_y(degree, order, theta, phi))
            indices.append((degree, order))
    design = np.column_stack(columns)
    square_root_weights = np.sqrt(np.asarray(weights, dtype=float).ravel())
    weighted_design = square_root_weights[:, None] * design
    weighted_values = square_root_weights * np.asarray(asymmetry, dtype=float).ravel()
    fitted, _, rank, _ = np.linalg.lstsq(weighted_design, weighted_values, rcond=None)
    if rank != design.shape[1]:
        raise ValueError(
            "equal-area grid does not resolve all requested spherical harmonics; "
            "increase n_mu/n_phi or reduce l_max"
        )
    coefficients = np.zeros((l_max + 1, 2 * l_max + 1), dtype=np.complex128)
    for coefficient, (degree, order) in zip(fitted, indices, strict=True):
        coefficients[degree, order + l_max] = coefficient
    return SphericalHarmonicExpansion(l_max=l_max, coefficients=coefficients)


def _coerce_bloch_points(points: np.ndarray, name: str) -> np.ndarray:
    vectors = np.asarray(points, dtype=float)
    if vectors.ndim != 2 or vectors.shape[1] != 3 or vectors.shape[0] == 0:
        raise ValueError(f"{name} must have shape (n, 3) with n > 0")
    if not np.all(np.isfinite(vectors)):
        raise ValueError(f"{name} must contain only finite values")
    norms = np.linalg.norm(vectors, axis=1)
    if np.any(norms == 0.0):
        raise ValueError(f"{name} contains a zero vector")
    if not np.allclose(norms, 1.0, atol=1.0e-10, rtol=1.0e-10):
        raise ValueError(f"{name} must contain unit Bloch vectors")
    return vectors / norms[:, None]


def _point_histogram(
    points: np.ndarray,
    mu_edges: np.ndarray,
    phi_edges: np.ndarray,
    weights: np.ndarray | None,
) -> np.ndarray:
    mu = np.clip(points[:, 2], -1.0, 1.0)
    phi = np.arctan2(points[:, 1], points[:, 0])
    # Azimuth is undefined at either pole. Canonicalize it so signed floating
    # zeros do not create fictitious angular coverage.
    transverse_sq = points[:, 0] ** 2 + points[:, 1] ** 2
    phi = np.where(transverse_sq <= 1.0e-28, 0.0, phi)
    return np.histogram2d(
        mu,
        phi,
        bins=[mu_edges, phi_edges],
        weights=weights,
    )[0]


def diagnose_labeled_bloch_histogram(
    roots_0: np.ndarray,
    roots_1: np.ndarray | None = None,
    *,
    weights_0: np.ndarray | None = None,
    weights_1: np.ndarray | None = None,
    n_mu: int = 18,
    n_phi: int = 36,
    pseudocount: float = 0.0,
    target_axis: np.ndarray | None = None,
    l_max: int = 7,
    harmonic_estimator: str = "weighted_least_squares",
    require_full_coverage: bool = True,
    axis_tolerance: float = 1.0e-12,
) -> EqualAreaLabeledHistogram:
    """Histogram labelled Bloch roots and, when resolved, diagnose ``a``.

    If ``roots_1`` is omitted, its count histogram is constructed by the exact
    antipodal transform of the label-0 histogram.  Passing both arrays instead
    provides an independent convention/numerical check.  A positive
    ``pseudocount`` is allowed but is recorded and must be reported as a
    regularized estimator.

    With the default ``require_full_coverage=True``, harmonic quantities are
    returned only when every cell has nonzero total weight.  This prevents an
    uncovered sphere (for example a strict-QND pole cloud) from being silently
    interpreted as a zero asymmetry away from observed roots.

    ``harmonic_estimator="weighted_least_squares"`` is the modern default and
    exactly recovers retained band-limited fields on a full-rank grid.
    ``"midpoint"`` reproduces the older manuscript post-processing but can
    alias a pure dipole into higher odd degrees on coarse grids.
    """

    if pseudocount < 0.0:
        raise ValueError("pseudocount must be nonnegative")
    if l_max < 1:
        raise ValueError("l_max must be at least one")
    if harmonic_estimator not in {"weighted_least_squares", "midpoint"}:
        raise ValueError(
            "harmonic_estimator must be 'weighted_least_squares' or 'midpoint'"
        )
    points_0 = _coerce_bloch_points(roots_0, "roots_0")
    axis = _unit_vector(
        np.array([0.0, 0.0, 1.0]) if target_axis is None else target_axis,
        "target_axis",
    )
    if weights_0 is not None:
        weights_0 = np.asarray(weights_0, dtype=float)
        if weights_0.shape != (points_0.shape[0],):
            raise ValueError("weights_0 must have one entry per root")
    mu_edges, phi_edges, directions, area_weights = _equal_area_geometry(n_mu, n_phi)
    counts_0 = _point_histogram(points_0, mu_edges, phi_edges, weights_0)

    if roots_1 is None:
        if weights_1 is not None:
            raise ValueError("weights_1 cannot be supplied when roots_1 is omitted")
        counts_1 = antipodal_equal_area_field(counts_0)
    else:
        points_1 = _coerce_bloch_points(roots_1, "roots_1")
        if weights_1 is not None:
            weights_1 = np.asarray(weights_1, dtype=float)
            if weights_1.shape != (points_1.shape[0],):
                raise ValueError("weights_1 must have one entry per root")
        counts_1 = _point_histogram(points_1, mu_edges, phi_edges, weights_1)

    count_0_regularized = counts_0 + pseudocount
    count_1_regularized = counts_1 + pseudocount
    total_0 = float(np.sum(count_0_regularized))
    total_1 = float(np.sum(count_1_regularized))
    if total_0 <= 0.0 or total_1 <= 0.0:
        raise ValueError("each label must have positive total weight")
    cell_area = float(area_weights[0, 0])
    density_0 = count_0_regularized / (total_0 * cell_area)
    density_1 = count_1_regularized / (total_1 * cell_area)
    total_density = density_0 + density_1
    occupied = (counts_0 + counts_1) > 0.0
    coverage = float(np.mean(occupied))
    asymmetry = np.divide(
        density_0 - density_1,
        total_density,
        out=np.full_like(total_density, np.nan),
        where=total_density > 0.0,
    )

    can_diagnose = bool(np.all(np.isfinite(asymmetry)))
    if require_full_coverage and pseudocount == 0.0 and coverage < 1.0:
        can_diagnose = False
    diagnostics = None
    ratio_residual = None
    if can_diagnose:
        ratio_residual = born_density_ratio_cross_residual(
            density_0,
            directions,
            area_weights,
            target_axis=axis,
        )
        if harmonic_estimator == "weighted_least_squares":
            expansion = _least_squares_harmonic_expansion(
                asymmetry,
                directions,
                area_weights,
                l_max,
            )
            quadrature = "equal-area cell-center weighted harmonic least squares"
        else:
            expansion = _midpoint_harmonic_expansion(
                asymmetry,
                directions,
                area_weights,
                l_max,
            )
            quadrature = "equal-area (cos(theta), phi) histogram midpoint rule"
        diagnostics = _finish_diagnostics(
            asymmetry=asymmetry,
            directions=directions,
            weights=area_weights,
            antipodal_asymmetry=antipodal_equal_area_field(asymmetry),
            target_axis=axis,
            expansion=expansion,
            density_weight=total_density,
            axis_tolerance=axis_tolerance,
            quadrature=quadrature,
        )

    return EqualAreaLabeledHistogram(
        mu_edges=mu_edges,
        phi_edges=phi_edges,
        counts_0=counts_0,
        counts_1=counts_1,
        density_0=density_0,
        density_1=density_1,
        total_density=total_density,
        asymmetry=asymmetry,
        occupied=occupied,
        coverage=coverage,
        root_weight_0=float(np.sum(counts_0)),
        root_weight_1=float(np.sum(counts_1)),
        pseudocount=float(pseudocount),
        born_density_ratio_cross_residual=ratio_residual,
        diagnostics=diagnostics,
    )


def composition_consistency_error(
    reference_asymmetry: np.ndarray,
    candidate_asymmetry: np.ndarray,
    weights: np.ndarray | float = 1.0,
) -> float:
    r"""Return the normalized ``L2`` composition/context discrepancy.

    This is a geometric comparison only.  It does not establish that either
    field is an operational probability assignment.
    """

    reference, candidate = np.broadcast_arrays(
        np.asarray(reference_asymmetry, dtype=float),
        np.asarray(candidate_asymmetry, dtype=float),
    )
    quadrature = np.broadcast_to(np.asarray(weights, dtype=float), reference.shape)
    if not (
        np.all(np.isfinite(reference))
        and np.all(np.isfinite(candidate))
        and np.all(np.isfinite(quadrature))
        and np.all(quadrature > 0.0)
    ):
        raise ValueError("fields and weights must be finite; weights must be positive")
    denominator = float(np.sum(quadrature * reference**2))
    numerator = float(np.sum(quadrature * (reference - candidate) ** 2))
    if denominator == 0.0:
        return 0.0 if numerator == 0.0 else np.inf
    return float(np.sqrt(numerator / denominator))
