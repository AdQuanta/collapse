"""Independent quadrature, exact limits and information-loss bounds."""

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import expm, eigvals

from core.born_reciprocity import (
    born_moment_residuals, born_residual_bounds, cosine_moments,
    folded_gaussian_moment_residuals, histogram_cosine_moments,
    response_cosine_coefficients,
)
from core.born_structure_identities import shifted_symmetric_phase_angles


@pytest.mark.parametrize("envelope", [0.0, 0.7, -0.7])
def test_general_born_family_by_independent_quadrature(envelope):
    # Nonconstant symmetric envelopes demonstrate that the cardioid alone
    # is not the general solution of the Born ratio condition.
    def p(theta):
        return (1 + np.cos(theta)) * (1 + envelope * np.cos(2 * theta)) / np.pi
    moments = np.array([quad(lambda t: p(t) * np.cos(n * t), 0, np.pi,
                             epsabs=1e-12)[0] for n in range(17)])
    np.testing.assert_allclose(born_moment_residuals(moments), 0, atol=2e-14)
    assert moments[2] == pytest.approx(envelope / 2, abs=2e-14)


def test_uniform_and_atomic_negative_controls():
    uniform = np.r_[1., np.zeros(16)]
    assert born_moment_residuals(uniform)[0] == -1
    # An atom at theta=0 obeys reflection balance as a measure, but has no
    # broad angular coverage. Moment tests alone must not imply coverage.
    np.testing.assert_array_equal(born_moment_residuals(cosine_moments(np.zeros(8), 16)), 0)


def test_raw_moments_enclosed_by_histogram_bounds():
    rng = np.random.default_rng(20260910)
    theta = np.r_[rng.uniform(0, np.pi, 1000), 0., np.pi]
    edges = np.linspace(0, np.pi, 17)
    density = np.histogram(theta, edges)[0] / theta.size / np.diff(edges)
    estimated, lo, hi = histogram_cosine_moments(edges, density, 16)
    exact = cosine_moments(theta, 16)
    assert np.all(lo <= exact + 1e-14) and np.all(exact <= hi + 1e-14)
    assert np.all(lo <= estimated + 1e-14) and np.all(estimated <= hi + 1e-14)
    residual = born_moment_residuals(exact)
    lower, upper = born_residual_bounds(lo, hi)
    assert np.all(lower <= residual + 1e-14) and np.all(residual <= upper + 1e-14)


def test_cayley_reduction_against_full_propagator():
    rng = np.random.default_rng(17)
    matrices = [rng.normal(size=(6, 6)) + 1j * rng.normal(size=(6, 6)) for _ in range(2)]
    hd, v = [(a + a.conj().T) / 2 for a in matrices]
    t = 0.31
    full = expm(-1j * t * np.block([[hd, v], [v, hd]]))
    direct = np.linalg.solve(full[:6, :6], full[6:, :6])
    plus, minus = expm(-1j * t * (hd + v)), expm(-1j * t * (hd - v))
    w = plus.conj().T @ minus
    cayley = np.linalg.solve(np.eye(6) + w, np.eye(6) - w)
    np.testing.assert_allclose(direct, cayley, atol=2e-14)
    np.testing.assert_allclose(direct + direct.conj().T, 0, atol=3e-14)
    theta = np.sort(2 * np.arctan(np.abs(eigvals(direct))))
    folded_phase = np.sort(np.abs(np.angle(eigvals(w))))
    np.testing.assert_allclose(theta, folded_phase, atol=3e-14)


def test_folded_gaussian_moments_by_image_sum_quadrature():
    sigma = 1.1
    def p(t):
        return 2 * sum(np.exp(-(t + 2 * np.pi * k) ** 2 / (2 * sigma**2))
                       for k in range(-8, 9)) / (np.sqrt(2 * np.pi) * sigma)
    moments = np.array([quad(lambda t: p(t) * np.cos(n * t), 0, np.pi,
                             epsabs=1e-12)[0] for n in range(17)])
    np.testing.assert_allclose(folded_gaussian_moment_residuals(moments, sigma), 0, atol=1e-14)


@pytest.mark.parametrize("theta", [[], [np.nan], [-0.1], [np.pi + 0.1]])
def test_invalid_angles_are_rejected(theta):
    with pytest.raises(ValueError):
        cosine_moments(np.array(theta), 16)


def test_response_offset_and_even_harmonics_are_fixed_by_reflection():
    edges = np.linspace(0, np.pi, 65)
    centers = (edges[:-1] + edges[1:]) / 2
    p = np.exp(-centers) * (1 + .3 * np.cos(5 * centers))
    ratio = p / (p + p[::-1])
    arrays = dict(edges=edges, centers=centers, R=ratio, occupied=np.ones(64, dtype=bool))
    coefficients = response_cosine_coefficients(arrays, 9)
    assert coefficients[0] == pytest.approx(.5, abs=1e-14)
    np.testing.assert_allclose(coefficients[2::2], 0, atol=1e-14)
    arrays["occupied"][0] = False
    assert np.isnan(response_cosine_coefficients(arrays, 9)).all()


@pytest.mark.parametrize("jy", [1., -1.])
def test_one_direction_charge_transfer_is_nilpotent(jy):
    # Independent explicit Pauli construction, including a nonzero qubit
    # splitting and interacting magnetization-conserving detector.
    x = np.array([[0., 1.], [1., 0.]])
    y = np.array([[0., -1j], [1j, 0.]])
    z = np.diag([1., -1.])
    ident = np.eye(2)
    hd = .7 * np.kron(z, ident) + .9 * np.kron(ident, z) + .2 * np.kron(z, z)
    hd += .13 * (np.kron(x, x) + np.kron(y, y)).real
    vx = np.kron(x, ident) + np.kron(ident, x)
    vy = np.kron(y, ident) + np.kron(ident, y)
    h = np.kron(ident, hd) - .4 * np.kron(z, np.eye(4)) + .12 * (np.kron(x, vx) + jy * np.kron(y, vy))
    u = expm(-1j * .6 * h)
    m = np.linalg.solve(u[:4, :4], u[4:, :4])
    assert np.linalg.norm(m) > .1  # physical flip block is not zero
    np.testing.assert_allclose(np.linalg.matrix_power(m, 3), 0, atol=1e-14)
    np.testing.assert_allclose(eigvals(m), 0, atol=1e-14)


def test_parallel_qubit_field_translates_conditional_phases():
    rng = np.random.default_rng(19)
    a = rng.normal(size=(5, 5))
    b = rng.normal(size=(5, 5))
    hd, v = (a + a.T) / 2, (b + b.T) / 2
    t, hx0 = .71, .23
    w0 = expm(1j * t * (hd + v)) @ expm(-1j * t * (hd - v))
    wp = expm(1j * t * (hd + v - hx0 * np.eye(5))) @ expm(-1j * t * (hd - v + hx0 * np.eye(5)))
    np.testing.assert_allclose(wp, np.exp(-2j * hx0 * t) * w0, atol=2e-14)


def test_shifted_folded_measure_has_predicted_cosine_moments():
    theta = np.array([.1, .3, 1.7, 2.4])
    shift = .37
    result = shifted_symmetric_phase_angles(theta, shift)
    expected = cosine_moments(theta, 16) * np.cos(np.arange(17) * shift)
    np.testing.assert_allclose(cosine_moments(result, 16), expected, atol=2e-14)


@pytest.mark.parametrize("rho", [.2, .7, .95])
def test_poisson_kernel_gives_pure_cosine_response(rho):
    theta = np.linspace(0, np.pi, 1001)
    def p(t):
        return (1-rho**2)/(np.pi*(1+rho**2-2*rho*np.cos(t)))
    actual = p(theta) / (p(theta) + p(np.pi-theta))
    expected = .5 * (1 + 2*rho/(1+rho**2)*np.cos(theta))
    np.testing.assert_allclose(actual, expected, atol=2e-14)
    integral = quad(p, 0, np.pi, epsabs=1e-12)[0]
    assert integral == pytest.approx(1, abs=1e-12)


def test_quarter_circle_shift_gives_reflection_symmetric_measure():
    # Distribution identity applies to any even auxiliary phase law.
    theta = np.array([.01, .07, .13, .32, .65, .89, 1.12, 1.68, 2.1, 2.81])
    shifted = shifted_symmetric_phase_angles(theta, np.pi/2)
    np.testing.assert_allclose(np.sort(shifted), np.sort(np.pi-shifted), atol=2e-14)
