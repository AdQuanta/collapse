"""Root/determinant duality and a native nonnormal thermodynamic counterexample."""

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import eigvalsh, expm

from core.collective_exchange import (
    exchange_log_cutoff_audit, exchange_sector_blocks, gaussian_exchange_flip_probability,
    gaussian_exchange_root_potential,
)
from core.projective_potential import (
    determinant_radial_potential, homogeneous_radial_potential,
)
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum


def test_projective_endpoints_multiplicity_and_scale_invariance():
    alpha = np.array([0., 1., 2., 2j])
    beta = np.array([1., 0., 1., 1.])
    x = np.array([-3., -1., 0., 1., 3.])
    expected = (x+2*(np.maximum(np.log(2), x)-np.log(2)))/4
    np.testing.assert_allclose(homogeneous_radial_potential(alpha, beta, x), expected)
    scales = np.array([1e-80, 1e80j, -13., .0003j])
    np.testing.assert_allclose(homogeneous_radial_potential(alpha*scales, beta*scales, x),
                               expected, atol=2e-14)
    with pytest.raises(ValueError):
        homogeneous_radial_potential(np.zeros(1), np.zeros(1), x)


def test_potential_derivative_recovers_cdf_and_is_convex_lipschitz():
    logs = np.array([-2., -.6, .2, 1.3])
    x = np.linspace(-3, 3, 121)
    potential = homogeneous_radial_potential(np.exp(logs), np.ones(4), x)
    slopes = np.diff(potential)/np.diff(x)
    assert np.min(slopes) > -1e-13
    assert np.max(slopes) < 1+1e-13
    assert np.min(np.diff(slopes)) > -1e-12
    query, delta = np.array([-2.4, -1.3, -.1, .7, 2.]), 1e-5
    derivative = (homogeneous_radial_potential(np.exp(logs), np.ones(4), query+delta)
                  - homogeneous_radial_potential(np.exp(logs), np.ones(4), query-delta))/(2*delta)
    np.testing.assert_allclose(derivative, np.mean(logs < query[:, None], axis=1), atol=2e-11)


@pytest.mark.parametrize("seed", [19, 37, 91])
def test_native_nonnormal_pencil_jensen_identity(seed):
    from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
    rng = np.random.default_rng(seed)
    params = dict(zip(["J", "Jpm", "Jx", "Jy", "Jz", "Jzx", "hx", "hz", "hx0", "hz0"],
                      rng.uniform(-.5, .5, 10)))
    h = SinglePixelHamiltonianNumpy(N_pixel=3, **params).generate()
    u = expm(-.3j*h)
    a, c = u[:8, :8], u[8:, :8]
    roots = generalized_relative_evolution_spectrum(a, c)
    assert not np.any(roots.indeterminate | roots.infinite)
    assert roots.maximum_homogeneous_residual < 1e-13
    # Stay away from root circles to test angular quadrature independently.
    logs = np.log(abs(roots.eigenvalues))
    x = np.r_[logs.min()-1, 0., logs.max()+1]
    exact = homogeneous_radial_potential(roots.alpha, roots.beta, x)
    for nodes in [64, 128, 256]:
        measured = determinant_radial_potential(a, c, x, phase_nodes=nodes)
        np.testing.assert_allclose(measured, exact, atol=2e-10, rtol=0)


@pytest.mark.parametrize("size", [2, 3, 4, 5])
def test_native_exchange_sector_trace_and_zero_roots(size):
    from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
    g, time = .7, .61
    h = SinglePixelHamiltonianQuSpin(
        N_pixel=size, J=0., Jx=g/np.sqrt(size), Jy=g/np.sqrt(size),
        hx=0., hz=0., hx0=0., hz0=0., central_coupling="all", use_symmetry=False,
    ).generate()
    u = expm(-1j*time*h)
    d = 2**size
    a, c = u[:d, :d], u[d:, :d]
    root = generalized_relative_evolution_spectrum(a, c)
    assert not np.any(root.indeterminate | root.infinite)
    np.testing.assert_allclose(root.theta, 0, atol=1e-12)
    weight_sum, flip, loga = 0, 0., 0.
    for sector in exchange_sector_blocks(size, coupling=g, time=time):
        dim = sector.two_j+1
        weight = sector.multiplicity/d
        weight_sum += sector.multiplicity*dim
        np.testing.assert_allclose(sector.a.conj().T@sector.a+sector.c.conj().T@sector.c,
                                   np.eye(dim), atol=3e-15)
        flip += weight*np.linalg.norm(sector.c, "fro")**2
        loga += weight*np.sum(np.log(abs(sector.a.diagonal())))
        qz = generalized_relative_evolution_spectrum(sector.a, sector.c)
        np.testing.assert_allclose(qz.theta, 0, atol=1e-14)
    assert weight_sum == d
    assert abs(flip-np.linalg.norm(c, "fro")**2/d) < 2e-14
    np.testing.assert_allclose(a, a.conj().T, atol=2e-14)
    assert abs(loga-np.sum(np.log(abs(eigvalsh(a))))/d) < 2e-14


def test_gaussian_trace_limit_and_incorrect_root_limit_separate():
    g, time = .7, .61
    predicted = gaussian_exchange_flip_probability(coupling=g, time=time)
    independent = quad(lambda r: r*np.exp(-r*r/2)*np.sin(g*time*r)**2,
                       0, np.inf, epsabs=1e-12)[0]
    assert abs(predicted-independent) < 2e-13
    errors = []
    for size in [16, 32, 64, 128]:
        flip = sum(s.multiplicity/2**size*np.linalg.norm(s.c, "fro")**2
                   for s in exchange_sector_blocks(size, coupling=g, time=time))
        errors.append(abs(flip-predicted))
    assert all(a > b for a, b in zip(errors[:-1], errors[1:]))
    assert errors[-1] < .002
    # Native roots have a1=1 at every size; scalar-limit roots have a1=1-2*flip.
    assert 2*predicted > .2
    scalar, quadrature_error = gaussian_exchange_root_potential(
        np.array([-1., 0., 1.]), coupling=g, time=time
    )
    assert max(quadrature_error) < 1e-10
    assert scalar[0] > -.8  # native potential is exactly x, hence -1 here
    assert scalar[1] == 0
    assert scalar[2] < 1


def test_lost_log_mass_survives_when_root_law_is_exactly_known():
    kwargs = dict(coupling=.7, time=.61, log_radii=np.array([-1., 0., 1.]),
                  singular_cutoffs=np.array([1e-4, 1e-8]))
    small = exchange_log_cutoff_audit(4, **kwargs)
    large = exchange_log_cutoff_audit(32, **kwargs)
    np.testing.assert_allclose(small["clipped_potential"][:, -1], [-1, 0, 1], atol=1e-12)
    assert large["lost_log_integral"][0, -1] > .03
    assert large["clipped_potential"][0, -1] > -.98
    assert np.min(large["lost_log_integral"]) > -2e-12


@pytest.mark.parametrize("size", [2, 3, 5])
def test_asymptotic_commutativity_does_not_control_the_roots(size):
    from core.pauli import build_pauli_x, build_pauli_y
    sx = sum(build_pauli_x(i, size) for i in range(size))/np.sqrt(size)
    sy = sum(build_pauli_y(i, size) for i in range(size))/np.sqrt(size)
    commutator = sx@sy-sy@sx
    assert abs(np.linalg.norm(commutator, "fro")**2/2**size-4/size) < 2e-14
    assert abs(np.trace(sx@sy@sx@sy)/2**size-(1-2/size)) < 2e-14
