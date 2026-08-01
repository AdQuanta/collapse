"""
Tests for level-spacing diagnostics.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from scipy.integrate import quad

from collapse import (
    MEAN_R_POISSON,
    compute_level_spacing_ratios,
    compute_level_spacings,
    compute_unfolded_spacings,
    mean_level_spacing_ratio,
    poisson_spacing_distribution,
    poisson_surmise,
    unfold_spectrum,
    wigner_spacing_distribution,
    wigner_surmise,
)


TOL = 1e-8


def test_uniform_spacings_ratio_is_one():
    """Uniform spacings give ratios equal to 1."""
    eigenvalues = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    spacings = compute_level_spacings(eigenvalues)
    ratios = compute_level_spacing_ratios(spacings)
    assert np.allclose(ratios, 1.0, atol=TOL)
    assert np.isclose(np.mean(ratios), 1.0, atol=TOL)


def test_degeneracies_removed():
    """Exact degeneracies should collapse to a single resolved level."""
    eigenvalues = np.array([0.0, 0.0, 1.0, 2.0])
    spacings = compute_level_spacings(eigenvalues)
    assert len(spacings) == 2
    assert np.allclose(spacings, [1.0, 1.0])


def test_all_degenerate_returns_nan():
    """All-identical eigenvalues give no spacings and NaN mean ratio."""
    eigenvalues = np.array([5.0, 5.0, 5.0, 5.0])
    spacings = compute_level_spacings(eigenvalues)
    assert len(spacings) == 0
    ratios = compute_level_spacing_ratios(spacings)
    assert len(ratios) == 0
    assert np.isnan(mean_level_spacing_ratio(eigenvalues))


def test_unfold_spectrum_rejects_invalid_degree():
    """Unfolding requires a positive polynomial degree."""
    eigenvalues = np.array([0.0, 1.0, 2.0, 3.0])
    try:
        unfold_spectrum(eigenvalues, degree=0)
    except ValueError:
        return
    raise AssertionError("Expected unfold_spectrum to reject degree=0")


def test_quadratic_staircase_unfolds_to_uniform_spacings():
    """A spectrum with quadratic staircase should unfold to uniform spacings."""
    levels = np.sqrt(np.arange(1.0, 41.0))
    unfolded = compute_unfolded_spacings(levels, degree=2, trim_fraction=0.0)
    assert np.allclose(unfolded, 1.0, atol=1e-6)


def test_poisson_surmise_normalisation():
    """Integral of P_Poisson(r) over [0, 1] should be 1."""
    integral, _ = quad(poisson_surmise, 0.0, 1.0)
    assert np.isclose(integral, 1.0, atol=TOL)


def test_wigner_normalisation_goe():
    """Integral of P_GOE(r) over [0, 1] should be 1."""
    integral, _ = quad(lambda r: wigner_surmise(r, beta=1), 0.0, 1.0)
    assert np.isclose(integral, 1.0, atol=TOL)


def test_wigner_normalisation_gue():
    """Integral of P_GUE(r) over [0, 1] should be 1."""
    integral, _ = quad(lambda r: wigner_surmise(r, beta=2), 0.0, 1.0)
    assert np.isclose(integral, 1.0, atol=TOL)


def test_poisson_spacing_distribution_normalisation():
    """Integral of P_Poisson(s) over [0, inf) should be 1."""
    integral, _ = quad(poisson_spacing_distribution, 0.0, np.inf)
    assert np.isclose(integral, 1.0, atol=TOL)


def test_wigner_spacing_distribution_normalisation_goe():
    """Integral of P_GOE(s) over [0, inf) should be 1."""
    integral, _ = quad(lambda s: wigner_spacing_distribution(s, beta=1), 0.0, np.inf)
    assert np.isclose(integral, 1.0, atol=TOL)


def test_wigner_spacing_distribution_normalisation_gue():
    """Integral of P_GUE(s) over [0, inf) should be 1."""
    integral, _ = quad(lambda s: wigner_spacing_distribution(s, beta=2), 0.0, np.inf)
    assert np.isclose(integral, 1.0, atol=TOL)


def test_mean_ratio_goe_random_matrix():
    """A large GOE matrix should give <r> near 0.5307."""
    rng = np.random.default_rng(42)
    size = 800
    matrix = rng.standard_normal((size, size))
    hamiltonian = (matrix + matrix.T) / 2.0
    eigenvalues = np.linalg.eigvalsh(hamiltonian)
    mean_r = mean_level_spacing_ratio(eigenvalues)
    assert abs(mean_r - 0.5307) < 0.03, f"GOE mean r = {mean_r:.4f}"


def test_mean_ratio_poisson():
    """Uncorrelated eigenvalues should give <r> near the Poisson value."""
    rng = np.random.default_rng(123)
    spacings = rng.exponential(1.0, size=5000)
    eigenvalues = np.cumsum(spacings)
    mean_r = mean_level_spacing_ratio(eigenvalues)
    assert abs(mean_r - MEAN_R_POISSON) < 0.02, f"Poisson mean r = {mean_r:.4f}"


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
