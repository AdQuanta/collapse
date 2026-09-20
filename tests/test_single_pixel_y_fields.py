"""
Verification tests for the ``hy`` / ``hy0`` single-site Y self-fields.

The Y self-fields complete the qubit and detector one-body field triples
(``h0x, h0y, h0z`` and ``hx, hy, hz``) for the single-pixel family.  They are a
governed extension of the approved Hamiltonian family; see
``wiki/governance/`` for the approval record.

A single-site Y term is purely imaginary in the computational basis, which makes
it structurally different from every other term in this builder: it forces a
complex accumulator and it breaks both total-``Sz`` conservation and ``Z``-parity.
Both consequences are asserted here, along with exact NumPy/QuSpin twin
agreement and unchanged behaviour when the Y fields are off.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest

from core.pauli import build_pauli_y
from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy

try:
    from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

    HAS_QUSPIN = True
except ImportError:  # pragma: no cover - exercised only without QuSpin
    HAS_QUSPIN = False


BASE = dict(
    N_pixel=3,
    connectivity="chain",
    central_coupling="first",
    J=1.0,
    Jxx=0.3,
    Jyy=0.2,
    Jx=0.05,
    Jy=0.04,
    Jz=0.03,
    hx=0.7,
    hz=0.5,
    hx0=0.2,
    hz0=0.3,
)


def test_y_fields_add_exactly_the_expected_terms():
    """``hy``/``hy0`` must subtract exactly ``hy0 Y_0 + hy sum_i Y_i``."""

    without = SinglePixelHamiltonianNumpy(**BASE).generate()
    with_y = SinglePixelHamiltonianNumpy(**BASE, hy=0.6, hy0=0.4).generate()

    n_qubits = BASE["N_pixel"] + 1
    ys = [build_pauli_y(i, n_qubits) for i in range(n_qubits)]
    expected = (
        without.astype(np.complex128)
        - 0.4 * ys[0]
        - 0.6 * sum(ys[i] for i in range(1, n_qubits))
    )
    assert np.array_equal(with_y, expected)


def test_y_field_hamiltonian_is_hermitian():
    hamiltonian = SinglePixelHamiltonianNumpy(**BASE, hy=0.6, hy0=-0.4).generate()
    assert np.allclose(hamiltonian, hamiltonian.conj().T, atol=0.0)


def test_hy0_falls_back_to_hy():
    """An unset ``hy0`` inherits ``hy``, matching the ``hx0``/``hz0`` convention."""

    inherited = SinglePixelHamiltonianNumpy(**BASE, hy=0.6).generate()
    explicit = SinglePixelHamiltonianNumpy(**BASE, hy=0.6, hy0=0.6).generate()
    assert np.array_equal(inherited, explicit)


def test_dtype_is_unchanged_when_y_fields_are_off():
    """Existing callers must be bit-identical, including the real dtype."""

    assert SinglePixelHamiltonianNumpy(**BASE).generate().dtype == np.float64
    assert (
        SinglePixelHamiltonianNumpy(**BASE, hy=0.0, hy0=0.0).generate().dtype
        == np.float64
    )
    assert (
        SinglePixelHamiltonianNumpy(**BASE, hy=0.6).generate().dtype == np.complex128
    )


@pytest.mark.skipif(not HAS_QUSPIN, reason="QuSpin is not installed")
@pytest.mark.parametrize(
    "connectivity,central_coupling",
    [("chain", "first"), ("chain", "all"), ("ring", "all")],
)
def test_numpy_and_quspin_twins_agree_with_y_fields(connectivity, central_coupling):
    """The twins must remain exactly equal once Y self-fields are active."""

    config = dict(
        BASE,
        connectivity=connectivity,
        central_coupling=central_coupling,
        hy=0.6,
        hy0=-0.4,
    )
    numpy_matrix = SinglePixelHamiltonianNumpy(**config).generate()
    quspin_matrix = SinglePixelHamiltonianQuSpin(**config).generate()
    assert np.allclose(numpy_matrix, quspin_matrix, rtol=0.0, atol=1e-12)


@pytest.mark.skipif(not HAS_QUSPIN, reason="QuSpin is not installed")
def test_symmetry_path_stays_exact_with_a_y_field():
    """``use_symmetry=True`` must not apply a sector the Y field has broken.

    With only longitudinal terms the builder would reach for the magnetization
    and ``Z``-parity sectors.  A ``Y`` field breaks both, so the sector path has
    to be declined; a stale predicate would silently return a wrong spectrum
    rather than raise.
    """

    config = dict(
        N_pixel=4,
        connectivity="chain",
        central_coupling="first",
        J=1.0,
        hz=0.5,
        hz0=0.3,
        hy=0.6,
        hy0=0.4,
        Jz=0.05,
    )
    energies, vectors = SinglePixelHamiltonianQuSpin(
        **config, use_symmetry=True
    ).diagonalize()
    reference = np.linalg.eigvalsh(
        SinglePixelHamiltonianQuSpin(**config, use_symmetry=False).generate()
    )
    assert np.allclose(np.sort(energies), np.sort(reference), atol=1e-10)
    identity = np.eye(vectors.shape[0])
    assert np.allclose(vectors.conj().T @ vectors, identity, atol=1e-10)


@pytest.mark.skipif(not HAS_QUSPIN, reason="QuSpin is not installed")
def test_y_field_breaks_sz_conservation():
    """A Y self-field must not leave total ``Sz`` conserved."""

    config = dict(
        N_pixel=3,
        connectivity="chain",
        central_coupling="first",
        J=1.0,
        hz=0.5,
        hz0=0.3,
        Jz=0.05,
    )
    n_qubits = config["N_pixel"] + 1
    total_z = sum(
        np.diag(np.kron(np.kron(np.eye(2**i), np.diag([1.0, -1.0])), np.eye(2 ** (n_qubits - i - 1))))
        for i in range(n_qubits)
    )
    sz = np.diag(total_z)

    without = SinglePixelHamiltonianQuSpin(**config).generate()
    with_y = SinglePixelHamiltonianQuSpin(**config, hy=0.6).generate()
    assert np.allclose(without @ sz - sz @ without, 0.0, atol=1e-12)
    assert not np.allclose(with_y @ sz - sz @ with_y, 0.0, atol=1e-12)
