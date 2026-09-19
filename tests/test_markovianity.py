"""Deterministic checks for the reduced-qubit non-Markovianity diagnostics.

The channel identity, the CPTP structure, two analytically solvable limits, and
the NumPy/QuSpin builder agreement are all exercised here.  One regression test
pins the estimator trap that silently reports zero information backflow for
every pure-dephasing model.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest
from scipy.linalg import expm

from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.markovianity import (
    bloch_series_from_spectrum,
    blp_backflow,
    channel_series,
    choi_from_bloch,
    fibonacci_directions,
    qubit_channel,
)
from core.projective_roots import split_qubit_first_blocks

try:
    from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

    HAS_QUSPIN = True
except ImportError:  # pragma: no cover - exercised only without QuSpin
    HAS_QUSPIN = False


def _random_unitary(dimension: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )
    unitary, _ = np.linalg.qr(raw)
    return unitary


def _explicit_reduced_map(unitary, detector_density, rho):
    """Reduced qubit output via an explicit partial trace, for cross-checking."""

    dimension = detector_density.shape[0]
    full = np.kron(rho, detector_density)
    evolved = unitary @ full @ unitary.conj().T
    return evolved.reshape(2, dimension, 2, dimension).trace(axis1=1, axis2=3)


def _channel_from_bloch(channel, rho):
    """Reconstruct the channel action from its Bloch-affine representation."""

    paulis = [
        np.array([[0, 1], [1, 0]], complex),
        np.array([[0, -1j], [1j, 0]]),
        np.array([[1, 0], [0, -1]], complex),
    ]
    vector = np.array([np.real(np.trace(p @ rho)) for p in paulis])
    trace = np.real(np.trace(rho))
    image = channel.bloch_matrix @ vector + trace * channel.bloch_translation
    return 0.5 * (
        trace * np.eye(2) + sum(image[a] * paulis[a] for a in range(3))
    )


@pytest.mark.parametrize("detector_qubits", [2, 3])
def test_gram_channel_matches_explicit_partial_trace(detector_qubits):
    dimension = 2**detector_qubits
    unitary = _random_unitary(2 * dimension, seed=20260920 + detector_qubits)
    probes = [
        np.array([[1, 0], [0, 0]], complex),
        np.array([[0.5, 0.5], [0.5, 0.5]], complex),
        np.array([[0.5, -0.5j], [0.5j, 0.5]]),
    ]

    mixed = qubit_channel(unitary, None)
    for rho in probes:
        expected = _explicit_reduced_map(unitary, np.eye(dimension) / dimension, rho)
        assert np.abs(_channel_from_bloch(mixed, rho) - expected).max() < 1.0e-14

    rng = np.random.default_rng(7)
    vector = rng.normal(size=dimension) + 1j * rng.normal(size=dimension)
    vector /= np.linalg.norm(vector)
    pure = qubit_channel(unitary, vector)
    density = np.outer(vector, vector.conj())
    for rho in probes:
        expected = _explicit_reduced_map(unitary, density, rho)
        assert np.abs(_channel_from_bloch(pure, rho) - expected).max() < 1.0e-14


def test_choi_is_positive_semidefinite_and_trace_preserving():
    for seed in (11, 12, 13):
        unitary = _random_unitary(8, seed=seed)
        channel = qubit_channel(unitary, None)
        eigenvalues = np.linalg.eigvalsh(channel.choi)
        assert eigenvalues.min() > -1.0e-14
        partial = channel.choi.reshape(2, 2, 2, 2).trace(axis1=1, axis2=3)
        assert np.abs(partial - np.eye(2)).max() < 1.0e-14


def test_choi_from_bloch_reproduces_the_channel_choi():
    unitary = _random_unitary(8, seed=404)
    channel = qubit_channel(unitary, None)
    rebuilt = choi_from_bloch(channel.bloch_matrix, channel.bloch_translation)
    assert np.abs(rebuilt - channel.choi).max() < 1.0e-13


def _hamiltonian(**overrides):
    parameters = dict(
        N_pixel=1, J=0.0, Jpm=0.0, Jxx=0.0, Jyy=0.0, Jx=0.0, Jy=0.0, Jz=0.0,
        Jzx=0.0, Jcpm=0.0, hx=0.0, hz=0.0, hx0=0.0, hz0=0.0,
        connectivity="chain", central_coupling="first",
    )
    parameters.update(overrides)
    return SinglePixelHamiltonianNumpy(**parameters).generate()


def test_uncoupled_qubit_gives_orthogonal_map_and_no_backflow():
    """With no qubit-detector coupling the qubit evolves unitarily."""

    hamiltonian = _hamiltonian(hx=0.7, hz=0.3, hx0=0.45, hz0=0.2, Jz=0.0)
    times = np.linspace(0.0, 25.0, 501)
    unitaries = np.array([expm(-1j * hamiltonian * t) for t in times])
    matrices, _ = channel_series(unitaries, None)

    for matrix in matrices:
        assert np.abs(matrix @ matrix.T - np.eye(3)).max() < 1.0e-12
    assert blp_backflow(matrices)["n_blp"] < 1.0e-10


def test_single_spin_dephasing_matches_the_closed_form():
    """Z_0 is conserved, so the coherence has an exact two-level expression."""

    jz, hz, hx = 0.35, 0.3, 0.6
    hamiltonian = _hamiltonian(Jz=jz, hz=hz, hx=hx)
    times = np.linspace(0.0, 12.0, 241)

    plus = np.array([-hx, 0.0, -(jz + hz)])
    minus = np.array([-hx, 0.0, jz - hz])
    omega_plus = np.linalg.norm(plus)
    omega_minus = np.linalg.norm(minus)
    overlap = float(plus @ minus / (omega_plus * omega_minus))

    for time in times:
        channel = qubit_channel(expm(-1j * hamiltonian * time), None)
        matrix = channel.bloch_matrix
        expected = np.cos(omega_plus * time) * np.cos(omega_minus * time) + (
            overlap * np.sin(omega_plus * time) * np.sin(omega_minus * time)
        )
        assert abs((matrix[0, 0] - 1j * matrix[1, 0]) - expected) < 1.0e-12
        assert abs(matrix[2, 2] - 1.0) < 1.0e-12
        assert max(abs(matrix[2, 0]), abs(matrix[2, 1]), abs(matrix[0, 2])) < 1.0e-12


def test_singular_value_estimator_misses_pure_dephasing_backflow():
    """Regression: the largest singular value tracks the conserved axis.

    A pure-dephasing model preserves the ``z`` axis exactly, so ``sigma_max(M)``
    is pinned at one and reports no backflow even while the coherence revives.
    Maximising over a direction grid is what recovers the real signal.
    """

    hamiltonian = _hamiltonian(N_pixel=4, Jz=0.15, hz=0.3, hx=0.5, J=1.0,
                               connectivity="ring", central_coupling="all")
    times = np.linspace(0.0, 40.0, 401)
    unitaries = np.array([expm(-1j * hamiltonian * t) for t in times])
    matrices, _ = channel_series(unitaries, None)

    singular = np.linalg.svd(matrices, compute_uv=False)[:, 0]
    naive = np.diff(singular)
    assert np.where(naive > 0, naive, 0).sum() < 1.0e-9

    assert blp_backflow(matrices)["n_blp"] > 0.1


@pytest.mark.skipif(not HAS_QUSPIN, reason="QuSpin is not installed")
@pytest.mark.parametrize(
    "connectivity,central_coupling", [("ring", "all"), ("chain", "first")]
)
def test_quspin_and_numpy_agree_on_hamiltonian_and_blocks(
    connectivity, central_coupling
):
    parameters = dict(
        N_pixel=4, J=1.0, Jpm=0.0, Jx=0.0, Jy=0.0, Jz=0.12, Jzx=0.0, Jcpm=0.0,
        hx=0.5, hz=0.3, hx0=0.4, hz0=0.0,
        connectivity=connectivity, central_coupling=central_coupling,
    )
    numpy_matrix = SinglePixelHamiltonianNumpy(**parameters).generate()
    quspin_matrix = np.asarray(
        SinglePixelHamiltonianQuSpin(**parameters).generate()
    )
    assert np.abs(numpy_matrix - quspin_matrix).max() < 1.0e-12

    numpy_blocks = split_qubit_first_blocks(expm(-1j * numpy_matrix * 3.7))
    quspin_blocks = split_qubit_first_blocks(expm(-1j * quspin_matrix * 3.7))
    for left, right in (
        (numpy_blocks.A, quspin_blocks.A),
        (numpy_blocks.B, quspin_blocks.B),
        (numpy_blocks.C, quspin_blocks.C),
        (numpy_blocks.D, quspin_blocks.D),
    ):
        assert np.abs(left - right).max() < 1.0e-12


def test_fibonacci_directions_are_unit_vectors():
    directions = fibonacci_directions(64)
    assert directions.shape == (64, 3)
    assert np.abs(np.linalg.norm(directions, axis=1) - 1.0).max() < 1.0e-12


@pytest.mark.parametrize("detector_state", ["mixed", "pure"])
def test_spectral_series_matches_explicit_propagators(detector_state):
    """The O(D^2) spectral path must agree with building every U(t)."""

    hamiltonian = _hamiltonian(N_pixel=4, J=1.0, Jz=0.2, hz=0.3, hx=0.5, hx0=0.4,
                               connectivity="ring", central_coupling="all")
    eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)
    times = np.linspace(0.0, 9.0, 37)
    state = None
    if detector_state == "pure":
        state = np.zeros(hamiltonian.shape[0] // 2)
        state[0] = 1.0

    fast_matrices, fast_translations = bloch_series_from_spectrum(
        eigenvalues, eigenvectors, times, state
    )

    unitaries = np.array([expm(-1j * hamiltonian * t) for t in times])
    slow_matrices, slow_translations = channel_series(unitaries, state)

    assert np.abs(fast_matrices - slow_matrices).max() < 1.0e-11
    assert np.abs(fast_translations - slow_translations).max() < 1.0e-11
