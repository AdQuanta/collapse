"""Test collective isotropic cancellation against the native Hamiltonian."""

import numpy as np
import pytest
from scipy.stats import wasserstein_distance

from core.born_structure_controls import control_sectors
from core.isotropic_detector_identity import isotropic_root_measure
from core.relative_evolution_sector import generalized_relative_evolution_from_sectors


@pytest.mark.parametrize("n,hz", [(5, 0.), (5, .31), (6, -.31)])
def test_binomial_measure_with_both_isotropic_neighbor_ranges(n, hz):
    parameters = dict(j=.27, jpm=.54, j2=.13, jpm2=.26, jx=.21, hz=hz, hz0=0.)
    sectors = control_sectors(parameters, n)
    for time in (.9, 7.1, 1e6):
        actual = generalized_relative_evolution_from_sectors(sectors, time, n + 1)
        theta, weights = isotropic_root_measure(n, collective_jx=.21, hz=hz, time=time)
        assert wasserstein_distance(actual.theta, theta, v_weights=weights) < 2e-8
        assert actual.maximum_homogeneous_residual < 1e-10
        assert len(np.unique(np.round(theta, 10))) <= n // 2 + 1


def test_exchange_cancellation_also_holds_for_nonzero_qubit_fields():
    common = dict(jx=.21, jy=.07, hz=.31, hz0=.19, hx0=.11)
    bare = control_sectors(dict(j=0., jpm=0., j2=0., jpm2=0., **common), 5)
    coupled = control_sectors(dict(j=.27, jpm=.54, j2=.13, jpm2=.26, **common), 5)
    for time in (.9, 7.1):
        a = generalized_relative_evolution_from_sectors(bare, time, 6)
        b = generalized_relative_evolution_from_sectors(coupled, time, 6)
        assert wasserstein_distance(a.theta, b.theta) < 1e-11


def test_zero_coupling_and_zero_time():
    for coupling, time in [(0., 8.), (.3, 0.)]:
        theta, weights = isotropic_root_measure(7, collective_jx=coupling, hz=.1, time=time)
        np.testing.assert_allclose(theta, 0.)
        assert weights.sum() == pytest.approx(1.)


def test_edge_commutator_exposes_nonuniform_coupling():
    x = np.array([[0., 1.], [1., 0.]])
    y = np.array([[0., -1j], [1j, 0.]])
    z = np.diag([1., -1.])
    identity = np.eye(2)
    strength = .37
    exchange = -strength * sum(np.kron(a, a) for a in (x, y, z))
    for left, right in [(.2, .2), (.2, -.1)]:
        coupling = -left * np.kron(x, identity) - right * np.kron(identity, x)
        predicted = 2j * strength * (left - right) * (np.kron(y, z) - np.kron(z, y))
        np.testing.assert_allclose(exchange @ coupling - coupling @ exchange, predicted, atol=1e-15, rtol=0)


@pytest.mark.parametrize("n,jx", [(0, .1), (2.5, .1), (3, np.nan)])
def test_invalid_inputs(n, jx):
    with pytest.raises(ValueError):
        isotropic_root_measure(n, collective_jx=jx, hz=.1, time=1.)
