"""Analytic checks for full-sphere Gleason/Born diagnostics."""

import numpy as np
from scipy.special import sph_harm_y

from collapse.gleason_diagnostics import (
    _equal_area_geometry,
    _least_squares_harmonic_expansion,
    _power_by_degree,
    born_density_ratio_cross_residual,
    composition_consistency_error,
    diagnose_asymmetry_function,
    diagnose_labeled_bloch_histogram,
)


def _direction(theta, phi):
    return np.stack(
        np.broadcast_arrays(
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta) + np.zeros_like(phi),
        ),
        axis=-1,
    )


def test_exact_born_dipole_is_sharp_and_has_no_higher_odd_power() -> None:
    axis = np.array([0.3, -0.4, np.sqrt(0.75)])

    def field(theta, phi):
        return np.einsum("...i,i->...", _direction(theta, phi), axis)

    result = diagnose_asymmetry_function(
        field,
        target_axis=axis,
        l_max=7,
        n_theta=12,
        n_phi=24,
    )

    assert result.epsilon_antipodal < 1.0e-14
    assert result.epsilon_born < 1.0e-14
    assert result.higher_odd_harmonic_leakage < 1.0e-26
    assert result.even_fraction_of_total_power < 1.0e-27
    assert np.allclose(result.dipole_vector, axis, atol=1.0e-13)
    assert np.isclose(result.dipole_sharpness, 1.0, atol=1.0e-13)
    assert np.isclose(result.axis_fidelity, 1.0, atol=1.0e-13)


def test_unsharp_dipole_is_distinguished_from_higher_harmonics() -> None:
    result = diagnose_asymmetry_function(
        lambda theta, phi: 0.4 * np.cos(theta),
        target_axis=np.array([0.0, 0.0, 1.0]),
        l_max=7,
        n_theta=12,
        n_phi=24,
    )

    assert result.higher_odd_harmonic_leakage < 1.0e-26
    assert np.isclose(result.dipole_sharpness, 0.4, atol=1.0e-13)
    assert np.isclose(result.axis_fidelity, 1.0, atol=1.0e-13)
    assert np.isclose(result.epsilon_born, 0.6, atol=1.0e-13)


def test_degree_three_contamination_is_reported_as_higher_odd_leakage() -> None:
    def field(theta, phi):
        return np.cos(theta) + 0.2 * np.real(sph_harm_y(3, 0, theta, phi))

    result = diagnose_asymmetry_function(
        field,
        l_max=7,
        n_theta=12,
        n_phi=24,
    )

    assert result.epsilon_antipodal < 1.0e-14
    assert result.higher_odd_harmonic_leakage > 1.0e-4
    assert result.p1_over_podd < 1.0
    assert result.even_fraction_of_total_power < 1.0e-27


def test_even_contamination_triggers_antipodal_and_even_power_diagnostics() -> None:
    result = diagnose_asymmetry_function(
        lambda theta, phi: np.cos(theta) + 0.1 * np.real(sph_harm_y(2, 0, theta, phi)),
        l_max=6,
        n_theta=12,
        n_phi=24,
    )

    assert result.epsilon_antipodal > 0.01
    assert result.even_fraction_of_total_power > 1.0e-4


def test_zero_asymmetry_has_no_defined_axis() -> None:
    result = diagnose_asymmetry_function(
        lambda theta, phi: np.zeros(np.broadcast_shapes(theta.shape, phi.shape)),
        l_max=5,
        n_theta=8,
        n_phi=16,
    )

    assert result.dipole_sharpness == 0.0
    assert not result.axis_defined
    assert np.isnan(result.axis_fidelity)
    assert result.epsilon_antipodal == 0.0


def test_histogram_refuses_to_invent_field_in_empty_cells() -> None:
    north = np.tile([0.0, 0.0, 1.0], (16, 1))
    result = diagnose_labeled_bloch_histogram(north, n_mu=6, n_phi=12)

    assert result.coverage == 2.0 / (6 * 12)
    assert result.diagnostics is None


def test_coarse_grid_least_squares_does_not_alias_exact_dipole() -> None:
    _, _, directions, weights = _equal_area_geometry(8, 16)
    expansion = _least_squares_harmonic_expansion(
        directions[..., 2],
        directions,
        weights,
        l_max=7,
    )
    power = _power_by_degree(expansion)

    assert np.sum(power[3::2]) / np.sum(power[1::2]) < 1.0e-25
    assert np.sum(power[0::2]) / np.sum(power) < 1.0e-25


def test_exact_antipodal_histogram_has_zero_odd_parity_residual() -> None:
    rng = np.random.default_rng(20260815)
    points = rng.normal(size=(200_000, 3))
    points /= np.linalg.norm(points, axis=1)[:, None]
    result = diagnose_labeled_bloch_histogram(
        points,
        n_mu=8,
        n_phi=16,
        l_max=5,
    )

    assert result.coverage == 1.0
    assert result.diagnostics is not None
    assert result.diagnostics.epsilon_antipodal == 0.0


def test_direct_born_density_ratio_cross_residual_is_exact_and_division_free() -> None:
    _, _, directions, weights = _equal_area_geometry(8, 16)
    projection = directions[..., 2]
    density_0 = (1.0 + projection) / (4.0 * np.pi)

    exact = born_density_ratio_cross_residual(density_0, directions, weights)
    distorted = born_density_ratio_cross_residual(
        density_0 * (1.0 + 0.2 * projection),
        directions,
        weights,
    )

    assert exact < 1.0e-15
    assert distorted > 1.0e-3


def test_composition_error_is_normalized_and_detects_change() -> None:
    reference = np.array([[-1.0, -0.5], [0.5, 1.0]])

    assert composition_consistency_error(reference, reference) == 0.0
    assert np.isclose(
        composition_consistency_error(reference, 0.5 * reference),
        0.5,
    )
