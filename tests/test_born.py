"""
Tests for Born-rule angle diagnostics.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from collapse import (
    born_ratio_from_radii,
    born_ratio_from_theta,
    born_ratio_from_z,
    diagonalize_relative_evolution,
    diagonalize_relative_evolution_from_unitary,
    diagnostics_from_radii,
    hill_tail_exponent,
    phase_angles_from_eigenvalues,
    phase_uniformity_from_eigenvalues,
    relative_evolution_matrix,
    reciprocity_error_from_radii,
    theta_pair_from_eigenvalues,
    theta_pair_from_radii,
)


def test_theta_pair_from_radii_reflects_about_pi_over_two():
    radii = np.array([0.0, 1.0, 3.0])
    theta0, theta1 = theta_pair_from_radii(radii)
    assert np.allclose(theta0 + theta1, np.pi)
    assert np.isclose(theta0[1], np.pi / 2)


def test_theta_pair_from_eigenvalues_uses_relative_evolution_radii():
    eigenvalues = np.array([0.0, 1.0j, -3.0])
    theta0, theta1 = theta_pair_from_eigenvalues(eigenvalues)
    expected, reflected = theta_pair_from_radii(np.array([0.0, 1.0, 3.0]))
    assert np.allclose(theta0, expected)
    assert np.allclose(theta1, reflected)


def test_relative_evolution_matrix_solves_u00_inverse_u10():
    U00 = np.array([[2.0, 0.5], [0.0, 1.5]])
    target = np.diag([0.25, 3.0j])
    U10 = U00 @ target

    matrix = relative_evolution_matrix(U00, U10)
    spectrum = diagonalize_relative_evolution(U00, U10)

    assert np.allclose(matrix, target)
    assert np.allclose(np.sort(spectrum.radii), np.array([0.25, 3.0]))
    assert np.allclose(spectrum.theta + spectrum.theta_reflected, np.pi)
    assert spectrum.solver == "solve"
    assert spectrum.condition_number >= 1.0


def test_relative_evolution_from_unitary_partitions_upper_left_blocks():
    U00 = np.eye(2)
    target = np.diag([0.5, 2.0])
    U = np.zeros((4, 4), dtype=float)
    U[:2, :2] = U00
    U[2:, :2] = target

    spectrum = diagonalize_relative_evolution_from_unitary(U)
    assert np.allclose(np.sort(spectrum.radii), np.array([0.5, 2.0]))


def test_born_ratio_from_z_scores_synthetic_born_data_near_one():
    n_theta = 24
    edges = np.linspace(0.0, np.pi, n_theta + 1)
    centers = (edges[:-1] + edges[1:]) / 2.0
    born = np.cos(centers / 2.0) ** 2

    scale = 400
    counts0 = np.rint(scale * born).astype(int)
    counts1 = scale - counts0
    z0 = np.repeat(np.cos(centers), counts0)
    z1 = np.repeat(np.cos(centers), counts1)

    result = born_ratio_from_z(z0, z1, n_theta=n_theta)
    assert result.similarity > 0.98
    assert result.mean_abs_error < 0.01


def test_balanced_reflected_radii_scores_like_uninformative_ratio():
    u = np.linspace(-3.0, 3.0, 600)
    radii = np.exp(u)

    result = born_ratio_from_radii(radii, n_theta=60)
    assert abs(result.similarity) < 0.05
    assert abs(result.mean_abs_error - 0.25) < 0.03


def test_born_ratio_pseudocount_smooths_sparse_bins():
    theta0 = np.array([0.1])
    theta1 = np.array([])

    raw = born_ratio_from_theta(theta0, theta1, n_theta=4)
    smooth = born_ratio_from_theta(theta0, theta1, n_theta=4, pseudocount=0.5)

    occupied = np.argmax(raw.counts_0)
    assert raw.ratio[occupied] == 1.0
    assert np.isclose(smooth.ratio[occupied], 0.75)
    assert np.allclose(smooth.ratio[smooth.counts_0 + smooth.counts_1 == 0], 0.5)


def test_hill_tail_exponent_recovers_pareto_density_exponent():
    density_exponent = 2.0
    n = 5000
    u = (np.arange(1, n + 1) - 0.5) / n
    radii = (1.0 - u) ** (-1.0 / (density_exponent - 1.0))

    estimate = hill_tail_exponent(radii, tail_fraction=0.2)
    assert abs(estimate.density_exponent - density_exponent) < 0.08
    assert estimate.n_tail == 1000


def test_reciprocity_error_is_small_for_constant_envelope_core():
    centers = np.linspace(-4.0, 4.0, 81)
    x = np.exp(centers)
    p_u = x / (1.0 + x**2) ** 2
    counts = np.maximum(1, np.rint(5000 * p_u / p_u.max()).astype(int))
    radii = np.repeat(x, counts)

    error = reciprocity_error_from_radii(radii, n_log_bins=40, min_count=3)
    assert error < 0.15


def test_phase_uniformity_scores_uniform_azimuths_near_one():
    bin_width = 2.0 * np.pi / 12
    phases = np.repeat((np.arange(12) + 0.5) * bin_width, 2)
    eigenvalues = np.exp(1j * phases)

    result = phase_uniformity_from_eigenvalues(
        eigenvalues,
        n_phi=12,
        include_antipodes=False,
    )

    assert result.n_samples == 24
    assert result.uniformity_score > 0.99
    assert result.entropy_score > 0.99
    assert result.max_bin_fraction < 0.10


def test_phase_uniformity_penalizes_concentrated_azimuths():
    eigenvalues = np.ones(24, dtype=np.complex128)

    result = phase_uniformity_from_eigenvalues(
        eigenvalues,
        n_phi=12,
        include_antipodes=False,
    )

    assert result.uniformity_score < 0.05
    assert result.entropy_score < 0.05
    assert result.max_bin_fraction == 1.0


def test_phase_angles_include_antipodal_bloch_branch():
    phases = phase_angles_from_eigenvalues(np.array([1.0 + 0.0j]), include_antipodes=True)

    assert np.allclose(np.sort(phases), np.array([0.0, np.pi]))


def test_diagnostics_from_radii_combines_scalar_metrics():
    radii = np.exp(np.linspace(-2.0, 2.0, 200))

    diagnostics = diagnostics_from_radii(radii, n_theta=40, n_log_bins=20)
    assert diagnostics.n_samples == 200
    assert np.isfinite(diagnostics.born_similarity)
    assert diagnostics.max_radius > diagnostics.p99_radius > diagnostics.p95_radius


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        name = test.__name__
        try:
            test()
            print(f"  PASS  {name}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {name}: {exc}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
