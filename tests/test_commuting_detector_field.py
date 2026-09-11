"""Independent full-unitary and exact-limit checks of field regularization."""

import numpy as np
import pytest
from scipy.linalg import eigvals, expm

from core.commuting_detector_field import commuting_detector_angles


@pytest.mark.parametrize("hz0", [0., .15, -.15, 1.3])
def test_against_full_nontrivial_commuting_hamiltonian(hz0):
    x = np.array([[0., 1.], [1., 0.]])
    z = np.diag([1., -1.])
    ident = np.eye(2)
    v = .3 * np.kron(x, ident) + .17 * np.kron(ident, x)
    hd = .27 * v + .13 * v @ v
    h = np.kron(ident, hd) - hz0 * np.kron(z, np.eye(4)) + np.kron(x, v)
    for time in (.2, 1.7, 8.1):
        u = expm(-1j * time * h)
        roots = eigvals(u[4:, :4], u[:4, :4])
        actual = 2 * np.arctan(np.abs(roots))
        predicted = commuting_detector_angles(np.linalg.eigvalsh(v), hz0=hz0, time=time)
        np.testing.assert_allclose(np.sort(actual), np.sort(predicted), atol=2e-13, rtol=0)


def test_native_ring_zero_detector_limit():
    from core.born_structure_controls import control_sectors
    from core.relative_evolution_sector import generalized_relative_evolution_from_sectors

    n, collective = 5, .31
    parameters = dict(j=0., jpm=0., j2=0., jpm2=0., hz=0., hz0=.23, jx=collective)
    sectors = control_sectors(parameters, n)
    values = -collective / np.sqrt(n) * np.array([n - 2 * k.bit_count() for k in range(2**n)])
    for time in (.7, 3.1):
        result = generalized_relative_evolution_from_sectors(sectors, time, n + 1, compare_direct=True)
        prediction = commuting_detector_angles(values, hz0=parameters["hz0"], time=time)
        np.testing.assert_allclose(np.sort(result.theta), np.sort(prediction), atol=1e-11, rtol=0)
        assert result.maximum_homogeneous_residual < 1e-11


def test_zero_field_poles_zero_modes_and_field_bound():
    values = np.array([0., .01, .4, 1.])
    np.testing.assert_allclose(commuting_detector_angles(values, hz0=0., time=0.), 0.)
    assert commuting_detector_angles(np.array([1.]), hz0=0., time=np.pi / 2)[0] == pytest.approx(np.pi)
    for field in (.01, .5, 2.):
        bound = 2 * np.arctan(np.abs(values) / field)
        for time in (.1, 1., 10., 100.):
            assert np.all(commuting_detector_angles(values, hz0=field, time=time) <= bound + 1e-13)


@pytest.mark.parametrize("values,hz0,time", [([], 0., 1.), ([np.nan], 0., 1.), ([1.], np.inf, 1.)])
def test_invalid_inputs(values, hz0, time):
    with pytest.raises(ValueError):
        commuting_detector_angles(np.asarray(values), hz0=hz0, time=time)
