"""Independent finite propagator checks of the asymptotic reductions."""

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import expm

from core.born_asymptotic import (
    collective_cosine_moments,
    conditional_phase_traces,
    field_interval_first_residual,
    gaussian_limit_density,
    recurrence_angle_bound,
    shifted_cosine_moments,
)
from core.born_reciprocity import born_moment_residuals, cosine_moments
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum


def _qz_angles(h, time):
    u = expm(-1j * time * h)
    d = h.shape[0] // 2
    roots = generalized_relative_evolution_spectrum(u[:d, :d], u[d:, :d])
    assert not np.any(roots.indeterminate)
    assert roots.maximum_homogeneous_residual < 2e-13
    return roots.theta


@pytest.mark.parametrize("seed", [51, 72, 93])
def test_noncommuting_detector_trace_shift_matches_production_qz(seed):
    rng = np.random.default_rng(seed)
    matrices = rng.normal(size=(2, 4, 4)) + 1j * rng.normal(size=(2, 4, 4))
    k, v = (matrices + matrices.conj().transpose(0, 2, 1)) / 2
    x = np.array([[0, 1], [1, 0]])
    time = .731
    traces = conditional_phase_traces(k, v, time, 16)
    for field in [-.27, 0., .041]:
        h = np.kron(np.eye(2), k) - np.kron(x, v + field * np.eye(4))
        observed = cosine_moments(_qz_angles(h, time), 16)
        expected = shifted_cosine_moments(traces, field=field, time=time)
        np.testing.assert_allclose(observed, expected, atol=3e-13, rtol=0)


def test_recurrence_bound_for_nonnormal_native_pencils():
    from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
    h = SinglePixelHamiltonianNumpy(
        N_pixel=3, J=.43, Jpm=.27, Jx=.18, Jy=.11,
        hz=.3, hx=.13, hz0=.17, hx0=.08,
    ).generate()
    for time in [.0001, .003, .01]:
        epsilon = np.linalg.norm(expm(-1j * time * h) - np.eye(16), ord=2)
        assert np.max(_qz_angles(h, time)) <= recurrence_angle_bound(epsilon)
    with pytest.raises(ValueError):
        recurrence_angle_bound(1.)


@pytest.mark.parametrize("size", [3, 4, 5])
def test_collective_formula_and_recurrence_against_native_qz(size):
    from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
    g = .37
    h = SinglePixelHamiltonianQuSpin(
        N_pixel=size, J=0., Jxx=.17, Jx=g / np.sqrt(size), hx=.09,
        hz=0., hx0=0., hz0=0., central_coupling="all", use_symmetry=False,
    ).generate()
    for time in [.23, 1.2, 7.1, np.pi * np.sqrt(size) / g]:
        observed = cosine_moments(_qz_angles(h, time), 16)
        exact = collective_cosine_moments(size, coupling=g, time=time, maximum_order=16)
        np.testing.assert_allclose(observed, exact, atol=3e-12, rtol=0)


def test_field_integral_and_dimension_independent_bound():
    # Deliberately asymmetric phase spectrum, so imaginary traces matter.
    phases = np.array([.19, .73, 2.18])
    traces = np.mean(np.exp(1j * np.arange(3)[:, None] * phases), axis=1)
    width, center = .37, -.11
    for time in [.2, 3., 30., 100.]:
        numerical = quad(lambda h: born_moment_residuals(
            shifted_cosine_moments(traces, field=h, time=time)
        )[0], center-width/2, center+width/2, epsabs=2e-12)[0] / width
        exact = field_interval_first_residual(
            traces, time=time, center=center, width=width
        )
        assert abs(numerical - exact) < 2e-12
        assert abs(exact + 1) <= 2.5 / (width * time)


def test_gaussian_limit_by_independent_wrapped_normal_and_quadrature():
    theta = np.linspace(0, np.pi, 221)
    g, time = .7, .8
    density, tail = gaussian_limit_density(theta, coupling=g, time=time, modes=16)
    sigma = 2 * g * time
    images = theta[:, None] + 2*np.pi*np.arange(-8, 9)
    independent = 2 * np.sum(np.exp(-images**2/(2*sigma**2)), axis=1) / (
        np.sqrt(2*np.pi) * sigma
    )
    np.testing.assert_allclose(density, independent, atol=2e-15, rtol=0)
    assert 0 < tail < 1e-30
    assert gaussian_limit_density(theta, coupling=g, time=100.)[1] > 0
    for n in range(5):
        moment = quad(lambda angle: float(gaussian_limit_density(
            np.array(angle), coupling=g, time=time
        )[0]) * np.cos(n*angle), 0, np.pi, epsabs=1e-12)[0]
        assert abs(moment - np.exp(-2*n*n*g*g*time*time)) < 2e-13


def test_derived_finite_size_correction_has_second_order_remainder():
    g, time, n = .43, .72, 2
    remainder = []
    for size in [64, 128, 256]:
        moment = collective_cosine_moments(size, coupling=g, time=time, maximum_order=n)[n]
        corrected = np.log(moment) + 2*n*n*g*g*time*time + 4*n**4*g**4*time**4/(3*size)
        remainder.append(abs(corrected))
    assert 3.9 < remainder[0] / remainder[1] < 4.1
    assert 3.9 < remainder[1] / remainder[2] < 4.1


def test_radial_log_and_planar_jacobians_for_nonconstant_envelope():
    # Born envelope E=(1+.2 cos(2theta))/pi, verified independently in theta.
    def p(theta):
        return (1+np.cos(theta))*(1+.2*np.cos(2*theta))/np.pi
    def q(r):
        return p(2*np.arctan(r))*2/(1+r*r)
    r = np.geomspace(.03, 30, 97)
    np.testing.assert_allclose(q(1/r), r**4*q(r), atol=1e-12, rtol=1e-11)
    log_plus, log_minus = r*q(r), q(1/r)/r
    np.testing.assert_allclose(log_minus, r*r*log_plus, atol=1e-13)
    # Isotropic planar lift only; angular covariance is stronger in general.
    f, f_inverse = q(r)/(2*np.pi*r), q(1/r)*r/(2*np.pi)
    np.testing.assert_allclose(f_inverse, r**6*f, atol=2e-12, rtol=1e-11)


@pytest.mark.parametrize("detuning", [.03, .4, 1.1])
def test_detuned_commuting_population_formula_against_native_qz(detuning):
    from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
    from scipy.special import comb
    size, g, shift = 4, .37, -.13
    h = SinglePixelHamiltonianQuSpin(
        N_pixel=size, J=0., Jxx=.17, Jx=g/np.sqrt(size), hx=.09,
        hz=0., hx0=shift, hz0=detuning, central_coupling="all", use_symmetry=False,
    ).generate()
    u = g/np.sqrt(size)*(size-2*np.arange(size+1)) + shift
    frequency = np.hypot(u, detuning)
    weights = comb(size, np.arange(size+1), exact=False)/2**size
    for time in [.3, 4., 70.]:
        x = (u/frequency*np.sin(time*frequency))**2
        moments = np.polynomial.chebyshev.chebvander(1-2*x, 16).T @ weights
        np.testing.assert_allclose(cosine_moments(_qz_angles(h, time), 16),
                                   moments, atol=3e-12, rtol=0)


def test_detuned_gaussian_limit_and_cap_obstruction_without_time_averaging():
    from scipy.special import erfc
    from scipy.stats import norm
    b, sigma = .4, .7
    limiting_a1 = np.sqrt(np.pi/2)*b/sigma*np.exp(b*b/(2*sigma*sigma))*erfc(
        b/(np.sqrt(2)*sigma)
    )
    # Frequency-space Fourier integral for the instantaneous a1(t) correction.
    def amplitude(omega):
        u = np.sqrt(max(omega*omega-b*b, 0.))
        return 2*u/omega*norm.pdf(u, scale=sigma)
    errors = []
    for time in [10., 30., 100.]:
        oscillatory, error = quad(amplitude, b, np.inf, weight="cos", wvar=2*time,
                                  epsabs=2e-10, limlst=200)
        assert error < 2e-9
        errors.append(abs(oscillatory))
        assert 0 < limiting_a1 + oscillatory < 1
    assert max(errors[1:]) < .01
    assert errors[-1] < .001
    # k>=1/2 has known positive Gaussian mass; no fitted tail exponent.
    m0 = 2*norm.sf(b/sigma)
    epsilon = .005
    born_required = 2*m0/(3*np.pi)*(1-2**(-1.5))*epsilon**1.5
    actual_upper = 2*norm.sf(b*np.sqrt((1-epsilon)/epsilon)/sigma)
    assert actual_upper < born_required * 1e-8


def test_heavy_tail_counterexample_is_born_but_is_not_native_linear_x():
    # Prescribing k uniform is an explicit non-native spectral construction.
    # Independent arcsine-mixture quadrature checks the claimed density.
    for x in [.07, .21, .49, .78, .93]:
        mixture = quad(lambda k: 1/(np.pi*np.sqrt(x*(k-x))), x, 1,
                       epsabs=1e-11)[0]
        expected = 2/np.pi*np.sqrt((1-x)/x)
        assert abs(mixture-expected) < 2e-11
        reflected = 2/np.pi*np.sqrt(x/(1-x))
        assert abs(mixture/(mixture+reflected)-(1-x)) < 2e-12
