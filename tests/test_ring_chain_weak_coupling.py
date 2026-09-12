"""Independent convention, resonance, and perturbative order checks."""
import numpy as np
import pytest
from scipy.linalg import expm

from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.ring_chain_family import RingChainSpec, build_ring_chain_parts
from core.weak_coupling_picture import interaction_picture_kernel, first_magnus_unitary


@pytest.mark.parametrize("topology,n", [("ring", 5), ("chain", 3)])
def test_positive_sign_family_matches_existing_native_subset(topology, n):
    spec = RingChainSpec(n, topology, (.03, 0., .11), (.2, 0., .4),
                         (.17, .17, .7), (0., 0., .13) if topology == "ring" else (0., 0., 0.),
                         (.05, -.02, .03))
    free, interaction = build_ring_chain_parts(spec)
    gx, gy, gz = spec.edge_couplings
    native = SinglePixelHamiltonianNumpy(
        N_pixel=n, J=-.7, Jpm=-.34, J2=-spec.second[2], Jx=-gx, Jy=-gy,
        Jz=-gz, hx=-.2, hz=-.4, hx0=-.03, hz0=-.11,
        connectivity=topology, central_coupling="all" if topology == "ring" else "first",
    ).generate()
    np.testing.assert_allclose(free + interaction, native, atol=2e-15)
    expected = sum(g*g for g in spec.coupling)
    if topology == "ring":
        expected = spec.coupling[0]**2 + spec.coupling[1]**2 + spec.coupling[2]**2 / n
    assert abs(np.linalg.norm(interaction, "fro")**2 / interaction.shape[0] - expected) < 1e-15
    fourth_norm = (np.linalg.norm(interaction @ interaction, "fro")**2
                   / interaction.shape[0])**.25
    bound = sum(abs(g) for g in spec.coupling)
    if topology == "ring":
        gx, gy, gz = spec.coupling
        bound = (3 - 2/n)**.25 * (abs(gx) + abs(gy) + abs(gz)/np.sqrt(n))
    assert fourth_norm <= bound + 1e-15


def test_all_y_fields_and_second_neighbors_have_correct_pauli_coefficients():
    spec = RingChainSpec(3, "chain", (.03, .07, .11), (.2, -.1, .4),
                         (.17, -.08, .7), (.09, .12, -.13), (.05, -.02, .03))
    h0, interaction = build_ring_chain_parts(spec)
    # Independent tensor-product construction, central qubit first.
    paulis = [np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.diag([1, -1])]
    expected = np.zeros_like(h0)
    for axis, p in enumerate(paulis):
        terms = [(spec.qubit_field[axis], [0])]
        terms += [(spec.detector_field[axis], [i]) for i in [1, 2, 3]]
        terms += [(spec.nearest[axis], list(pair)) for pair in [(1, 2), (2, 3)]]
        terms += [(spec.second[axis], [1, 3]), (spec.coupling[axis], [0, 1])]
        for coefficient, sites in terms:
            product = np.ones((1, 1))
            for i in range(4):
                product = np.kron(product, p if i in sites else np.eye(2))
            expected += coefficient * product
    np.testing.assert_allclose(h0 + interaction, expected, atol=2e-15)


def test_kernel_matches_time_quadrature_with_exact_degeneracy():
    h0 = np.diag([0., 0., .7, 1.3])
    rng = np.random.default_rng(912)
    v = rng.normal(size=(4, 4)) + 1j*rng.normal(size=(4, 4))
    v = (v + v.conj().T) / 2
    _, kernel = interaction_picture_kernel(h0, v, time=2.3)
    nodes, weights = np.polynomial.legendre.leggauss(64)
    reference = sum(w * (expm(1j * h0 * t) @ v @ expm(-1j * h0 * t))
                    for t, w in zip((nodes+1)*2.3/2, weights*2.3/2))
    np.testing.assert_allclose(kernel, reference, atol=3e-14)
    assert abs(kernel[0, 1] - 2.3*v[0, 1]) < 1e-14


def test_fixed_time_first_magnus_has_second_order_error():
    spec = RingChainSpec(3, "chain", (.03, .07, .11), (.2, -.1, .4),
                         (.17, -.08, .7), (.09, .12, -.13), (.7, .2, -.3))
    h0, v = build_ring_chain_parts(spec)
    errors = []
    for epsilon in [.02, .01, .005]:
        approximate = first_magnus_unitary(h0, epsilon*v, time=.8)
        exact = expm(-.8j*(h0+epsilon*v))
        np.testing.assert_allclose(approximate.conj().T@approximate, np.eye(16), atol=3e-14)
        errors.append(np.linalg.norm(exact-approximate, 2))
    assert all(3.8 < a/b < 4.2 for a, b in zip(errors[:-1], errors[1:]))


def test_commuting_resonant_resummation_is_exact_at_long_times():
    h0, v = np.zeros((2, 2)), np.array([[0., .01], [.01, 0.]])
    np.testing.assert_allclose(first_magnus_unitary(h0, v, time=1000.),
                               expm(-1000j*v), atol=2e-14)
