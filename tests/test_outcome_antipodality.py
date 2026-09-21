"""Antipodality of the two `SPEC.md` §3 outcome root sets.

Unitarity alone forces the outcome-1 collapsible rays to be the antipodes of
the outcome-0 rays, with identical kernel dimensions.  The statements below are
exact consequences of that theorem, so these are correctness tests rather than
regression snapshots: no tolerance here absorbs a physical approximation, only
floating-point error.
"""

import numpy as np
import pytest
from scipy.linalg import expm, fractional_matrix_power

from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.projective_roots import forward_pole_root_spectrum, split_qubit_first_blocks
from core.quantum_utils import generate_random_unitary

EXACT = 1e-12


def branch(unitary: np.ndarray, outcome: int, alpha: complex, beta: complex) -> np.ndarray:
    """Return the forbidden branch of *outcome* at the homogeneous ray ``[alpha:beta]``."""

    blocks = split_qubit_first_blocks(unitary)
    if outcome == 0:
        return beta * blocks.C + alpha * blocks.D
    return beta * blocks.A + alpha * blocks.B


def antipode(alpha: complex, beta: complex) -> tuple[complex, complex]:
    """Return the ray orthogonal to ``[alpha:beta]``, i.e. its Bloch antipode."""

    return np.conjugate(beta), -np.conjugate(alpha)


def kernel_dimension(matrix: np.ndarray, scale: float) -> int:
    return int(np.count_nonzero(np.linalg.svd(matrix, compute_uv=False) <= 1e-8 * scale))


def rays(spectrum) -> list[tuple[complex, complex]]:
    return list(zip(np.asarray(spectrum.alpha), np.asarray(spectrum.beta)))


def approved_unitary(connectivity: str, central_coupling: str, n_pixel: int, time: float):
    hamiltonian = SinglePixelHamiltonianNumpy(
        N_pixel=n_pixel, J=1.0, Jpm=0.2, Jx=0.005, hz=0.3, hx0=0.0, hz0=0.1,
        connectivity=connectivity, central_coupling=central_coupling,
    )
    return expm(-1j * hamiltonian.generate() * time)


def defective_unitary() -> np.ndarray:
    """A unitary whose outcome-0 pencil is ``D (lambda I - M)`` for a Jordan block ``M``.

    Algebraic multiplicity two, kernel dimension one: the case where counting QZ
    entries and counting kernel dimensions disagree.
    """

    m = np.array([[1.0, 1.0], [0.0, 1.0]], dtype=np.complex128)
    d = fractional_matrix_power(np.eye(2) + m @ m.conj().T, -0.5)
    lower = np.hstack([-d @ m, d])
    _, _, right_h = np.linalg.svd(lower)
    return np.vstack([right_h[2:], lower])


@pytest.mark.parametrize("dimension", [2, 4, 8])
def test_branch_gram_identity(dimension: int) -> None:
    """The two branches of any two rays satisfy ``M0(c)* M0(c') + M1(c)* M1(c') = <c,c'> I``.

    This is the whole content of unitarity for the pair of outcome pencils, and
    every other statement in this file follows from it.
    """

    rng = np.random.default_rng(20260921)
    unitary = generate_random_unitary(2 * dimension, seed=11)
    identity = np.eye(dimension)
    for _ in range(5):
        c = rng.normal(size=4).view(np.complex128)
        c_prime = rng.normal(size=4).view(np.complex128)
        gram = sum(
            branch(unitary, b, c[1], c[0]).conj().T @ branch(unitary, b, c_prime[1], c_prime[0])
            for b in (0, 1)
        )
        overlap = np.vdot(c, c_prime)
        assert np.allclose(gram, overlap * identity, atol=EXACT, rtol=0.0)


@pytest.mark.parametrize("dimension", [2, 4, 8])
def test_orthogonal_ray_has_equal_kernel_dimension(dimension: int) -> None:
    """Every outcome-0 root is matched by an outcome-1 root at its antipode."""

    unitary = generate_random_unitary(2 * dimension, seed=7)
    for alpha, beta in rays(forward_pole_root_spectrum(unitary, outcome=0)):
        scale = float(np.hypot(abs(alpha), abs(beta)))
        assert kernel_dimension(branch(unitary, 0, alpha, beta), scale) == 1
        assert kernel_dimension(branch(unitary, 1, *antipode(alpha, beta)), scale) == 1


@pytest.mark.parametrize(
    "connectivity,central_coupling,n_pixel,time",
    [("ring", "all", 3, 3.7), ("ring", "all", 4, 211.0),
     ("chain", "first", 3, 3.7), ("chain", "first", 4, 211.0)],
)
def test_approved_families_have_antipodal_outcome_sets(
    connectivity: str, central_coupling: str, n_pixel: int, time: float
) -> None:
    """On the approved ring and endpoint chain, outcome 1 is the antipodal image of outcome 0."""

    unitary = approved_unitary(connectivity, central_coupling, n_pixel, time)
    bloch_zero = _bloch(forward_pole_root_spectrum(unitary, outcome=0))
    bloch_one = _bloch(forward_pole_root_spectrum(unitary, outcome=1))
    assert bloch_zero.shape == bloch_one.shape
    distance = np.linalg.norm(bloch_one[:, None, :] + bloch_zero[None, :, :], axis=2)
    assert float(distance.min(axis=1).max()) < 1e-10


def _bloch(spectrum) -> np.ndarray:
    alpha = np.asarray(spectrum.alpha, dtype=np.complex128)
    beta = np.asarray(spectrum.beta, dtype=np.complex128)
    theta = 2.0 * np.arctan2(np.abs(alpha), np.abs(beta))
    phi = np.angle(alpha * np.conjugate(beta))
    return np.stack(
        [np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)], axis=1
    )


def test_degenerate_kernel_dimension_is_preserved() -> None:
    """``I_2 (x) I_n`` collapses at the poles with kernel dimension ``n`` on both outcomes."""

    dimension = 3
    unitary = np.eye(2 * dimension, dtype=np.complex128)
    assert kernel_dimension(branch(unitary, 0, 0.0, 1.0), 1.0) == dimension
    assert kernel_dimension(branch(unitary, 1, *antipode(0.0, 1.0)), 1.0) == dimension


def test_defective_root_keeps_kernel_dimension_under_antipodal_map() -> None:
    """Algebraic multiplicity two, kernel dimension one, on both sides of the map."""

    unitary = defective_unitary()
    assert kernel_dimension(branch(unitary, 0, 1.0, 1.0), 1.0) == 1
    assert kernel_dimension(branch(unitary, 1, *antipode(1.0, 1.0)), 1.0) == 1


def test_same_ray_singular_values_are_complementary() -> None:
    """``sigma^2(M0(c)) + sigma^2(M1(c)) = |c|^2`` pairwise, the ray-local form of unitarity."""

    unitary = generate_random_unitary(8, seed=3)
    alpha, beta = 0.4 + 0.9j, -1.3 + 0.2j
    scale = abs(alpha) ** 2 + abs(beta) ** 2
    zero = np.linalg.svd(branch(unitary, 0, alpha, beta), compute_uv=False)
    one = np.linalg.svd(branch(unitary, 1, alpha, beta), compute_uv=False)
    assert np.allclose(zero**2 + one[::-1] ** 2, scale, atol=EXACT, rtol=0.0)
