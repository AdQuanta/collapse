"""Independent resolvent, weak-response, and charge-gauge verification."""
import numpy as np
import pytest
from scipy.linalg import expm, solve

from core.pauli import build_pauli_operators, build_pauli_y
from core.resonant_return import (
    leading_transverse_matrix, projected_resolvent, transverse_gauge,
)
from core.ring_chain_family import RingChainSpec, build_ring_chain_parts


@pytest.mark.parametrize("z", [.13+.2j, .13+.02j, .13-.02j])
def test_schur_resolvent_matches_full_solve_at_exact_degeneracy(z):
    rng = np.random.default_rng(923)
    hp = np.diag([0., 0., .3, .7])
    hm = np.diag([0., 0., .3, .7])
    q = .02*(rng.normal(size=(4, 4))+1j*rng.normal(size=(4, 4)))
    blocks = projected_resolvent(hp, hm, q, spectral_parameter=z)
    h = np.block([[hp, q.conj().T], [q, hm]])
    reference = solve(z*np.eye(8)-h, np.eye(8)[:, :4])
    np.testing.assert_allclose(np.vstack([blocks.upper, blocks.lower]), reference,
                               rtol=2e-13, atol=2e-13)
    assert blocks.column_residual < 3e-14
    # Hermitian resolvents have a negative-semidefinite imaginary part above
    # the real axis; the self-energy retains this causality property.
    imaginary_sigma = (blocks.self_energy-blocks.self_energy.conj().T)/(2j)
    assert np.max(np.linalg.eigvalsh(np.sign(z.imag)*imaginary_sigma)) < 1e-13


@pytest.mark.parametrize("topology,n", [("ring", 5), ("chain", 3)])
@pytest.mark.parametrize("gx,gy", [(1., .35), (-1., .35), (.35, 1.)])
def test_anisotropic_gauge_for_interacting_magnetization_conserving_detector(topology, n, gx, gy):
    spec = RingChainSpec(n, topology, (0., 0., 0.), (0., 0., .23),
                         (.17, .17, .43), (.07, .07, -.13), (0., 0., 0.))
    free, _ = build_ring_chain_parts(spec)
    hd = free[:2**n, :2**n]
    xs, zs = build_pauli_operators(n)
    ys = [build_pauli_y(i, n) for i in range(n)]
    lx = sum(xs)/np.sqrt(n) if topology == "ring" else xs[0]
    ly = sum(ys)/np.sqrt(n) if topology == "ring" else ys[0]
    mz = sum(zs)
    np.testing.assert_allclose(mz@hd, hd@mz, atol=1e-14)
    lp = (lx+1j*ly)/2
    np.testing.assert_allclose(mz@lp-lp@mz, 2*lp, atol=1e-14)
    diagonal, scale = transverse_gauge(np.diag(mz), gx=gx, gy=gy)
    response = leading_transverse_matrix(hd, gx*lx+1j*gy*ly, central_z=.09, time=3.7)
    reference = leading_transverse_matrix(hd, lx, central_z=.09, time=3.7)
    np.testing.assert_allclose(diagonal[:, None]*response/diagonal[None, :],
                               scale*reference, atol=3e-13)
    assert abs(scale**2-(gx**2-gy**2)) < 1e-14


def test_leading_matrix_is_derivative_of_exact_relative_evolution():
    hd = np.array([[.1, .17j], [-.17j, -.3]])
    q = np.array([[.2, .7j], [.3+.2j, -.1]])
    b, time = .13, 1.7
    expected = leading_transverse_matrix(hd, q, central_z=b, time=time)
    errors = []
    for epsilon in [.04, .02, .01]:
        h = np.block([[hd+b*np.eye(2), epsilon*q.conj().T],
                      [epsilon*q, hd-b*np.eye(2)]])
        unitary = expm(-1j*time*h)
        relative = solve(unitary[:2, :2], unitary[2:, :2])
        errors.append(np.linalg.norm(relative/epsilon-expected))
    assert all(3.9 < a/b < 4.1 for a, b in zip(errors[:-1], errors[1:]))


def test_gauge_boundary_is_not_treated_as_invertible():
    with pytest.raises(ValueError, match="gx !="):
        transverse_gauge(np.array([-1., 1.]), gx=1., gy=1.)
