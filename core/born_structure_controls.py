"""Reduced, controlled perturbations of the existing ring Hamiltonian.

The full solver and operator conventions are inherited from the production
SinglePixelHamiltonianQuSpin implementation. No surrogate dynamics is used.
"""

from __future__ import annotations

import numpy as np

from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.relative_evolution_sector import generalized_relative_evolution_from_sectors
from core.relative_evolution_study import angular_histogram
from core.born_reciprocity import (
    cosine_moments, born_moment_residuals, reflection_diagnostics,
    response_cosine_coefficients,
)
from core.born import born_ratio_from_theta


def control_sectors(parameters: dict[str, float], detector_n: int) -> list[dict]:
    """Build translation sectors with collective couplings scaled once."""
    if detector_n < 5 or detector_n > 10:
        raise ValueError("this reduced-control workflow is limited to 5 <= N <= 10")
    model = SinglePixelHamiltonianQuSpin(
        N_pixel=detector_n, J=parameters["j"], Jpm=parameters["jpm"],
        J2=parameters["j2"], Jpm2=parameters["jpm2"],
        Jx=parameters["jx"] / np.sqrt(detector_n),
        Jy=parameters.get("jy", 0.) / np.sqrt(detector_n),
        Jz=0., Jzx=0., hx=parameters.get("hx", 0.), hx0=parameters.get("hx0", 0.),
        hz=parameters["hz"], hz0=parameters["hz0"],
        connectivity="ring", central_coupling="all", seed=44, use_symmetry=True,
    )
    sectors = model.diagonalize_sectors()
    if any(s.get("symmetry_label") != "pixel_shift" for s in sectors):
        raise ValueError("control did not use detector translation sectors")
    return sectors


def control_snapshot(sectors: list[dict], detector_n: int, time: float, bins: int) -> dict:
    """Solve the homogeneous pencil and retain numerical reliability evidence."""
    result = generalized_relative_evolution_from_sectors(sectors, time, detector_n + 1, compare_direct=True)
    if result.theta.size != 2**detector_n or np.any(result.indeterminate):
        raise ValueError("incomplete or indeterminate projective spectrum")
    if result.maximum_homogeneous_residual > 1e-9 or result.maximum_column_isometry_residual > 1e-10:
        raise ValueError("control failed residual/isometry gate")
    hist = angular_histogram(result.theta, bins)
    arrays = dict(edges=hist.edges, centers=hist.centers, P=hist.density,
                  P_reflected=hist.reflected_density, R=hist.ratio,
                  occupied=hist.occupied, Born=hist.born)
    moments = cosine_moments(result.theta, 16)
    coeff = response_cosine_coefficients(arrays, 9)
    return dict(
        arrays=arrays, theta=result.theta, moments=moments,
        born_moment_residuals=born_moment_residuals(moments),
        response_coefficients=coeff,
        S_born=born_ratio_from_theta(result.theta, np.pi - result.theta, n_theta=100).similarity,
        visibility=2 * coeff[1], higher_odd_norm=float(np.linalg.norm(2 * coeff[3::2])),
        born_moment_max=float(np.max(np.abs(born_moment_residuals(moments)))),
        homogeneous_residual=result.maximum_homogeneous_residual,
        isometry_residual=result.maximum_column_isometry_residual,
        condition_u00=result.maximum_condition_number_u00,
        local_root_condition_max=float(max(np.max(s.local_coordinate_condition_numbers) for s in result.spectra)),
        direct_angle_error=result.maximum_direct_angle_error,
        direct_compared=result.direct_comparison_sectors,
        direct_skipped=result.direct_skipped_sectors,
        **reflection_diagnostics(arrays),
    )
