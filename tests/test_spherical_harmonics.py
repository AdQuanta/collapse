"""
Tests for spherical-harmonic projection support.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from scipy.special import sph_harm_y

from collapse import (
    SphericalHarmonicProjector,
    evaluate_spherical_harmonic,
    project_onto_spherical_harmonics,
)


TOL = 1e-10


def test_evaluate_spherical_harmonic_matches_scipy():
    theta = np.linspace(0.2, 2.7, 5)[:, None]
    phi = np.linspace(0.1, 5.8, 7)[None, :]

    actual = evaluate_spherical_harmonic(4, -2, theta, phi)
    expected = sph_harm_y(4, -2, theta, phi)

    assert np.allclose(actual, expected, atol=TOL)


def test_constant_function_projects_to_y00_only():
    expansion = project_onto_spherical_harmonics(lambda theta, phi: 1.0, l_max=4)

    assert np.allclose(expansion.coefficient(0, 0), np.sqrt(4.0 * np.pi), atol=TOL)

    coefficients = expansion.as_array()
    coefficients[0, 4] = 0.0
    assert np.max(np.abs(coefficients)) < TOL


def test_projector_recovers_known_harmonic():
    projector = SphericalHarmonicProjector(l_max=5, n_theta=8, n_phi=16)
    expansion = projector.project_function(
        lambda theta, phi: sph_harm_y(3, 2, theta, phi)
    )

    assert np.allclose(expansion.coefficient(3, 2), 1.0, atol=TOL)

    coefficients = expansion.as_array()
    coefficients[3, 5 + 2] = 0.0
    assert np.max(np.abs(coefficients)) < TOL


def test_real_input_matches_full_complex_projection():
    projector = SphericalHarmonicProjector(l_max=4, n_theta=8, n_phi=16)

    def function(theta, phi):
        harmonic = sph_harm_y(3, 2, theta, phi)
        return harmonic + np.conj(harmonic)

    fast = projector.project_function(function, real_input=True)
    full = projector.project_function(function, real_input=False)

    assert np.allclose(fast.as_array(), full.as_array(), atol=TOL)
    assert np.allclose(fast.coefficient(3, -2), 1.0, atol=TOL)
    assert np.allclose(fast.coefficient(3, 2), 1.0, atol=TOL)


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
