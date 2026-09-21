"""Equivalence of the fixed-input pencil and the `SPEC.md` §3 outcome pencils.

The production Born pipeline solves the block-column pencil ``U10 v = z U00 v``
while the specification defines collapsibility through the block-row pencils.
Two exact statements relate them, and this file certifies both:

1. **Time-reversal duality, unconditional.** The fixed-input characterization of
   ``U`` is the outcome-0 characterization of ``U^dagger``.
2. **Equality under time-reversal symmetry.** If ``U^T = U``, equivalently if
   ``H`` is real in the computational basis, the fixed-input roots are the
   complex conjugates of the outcome-0 roots.

Both are exact, so the tolerances below absorb floating-point error only. The
second statement fails exactly when a single-site ``Y`` operator is present,
which is the ``h_y`` / ``h_0y`` corner of the approved families; that failure is
asserted too, so the test cannot pass vacuously.

See `wiki/concepts/fixed-input-outcome-equivalence.md`.
"""

import numpy as np
import pytest
from scipy.linalg import expm

from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.pencil_characterization import STATUS_REGULAR, characterize_pencil_roots
from core.projective_roots import split_qubit_first_blocks
from core.quantum_utils import generate_random_unitary
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum

EXACT = 1.0e-12


def sorted_roots(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """Return the sorted affine roots of the pencil solved by ``(first, second)``."""

    spectrum = generalized_relative_evolution_spectrum(
        first, second, compute_left_eigenvectors=False
    )
    return np.sort_complex(np.asarray(spectrum.alpha) / np.asarray(spectrum.beta))


def fixed_input_roots(unitary: np.ndarray) -> np.ndarray:
    """Roots of ``U10 v = z U00 v``: the pencil the production pipeline solves."""

    blocks = split_qubit_first_blocks(unitary)
    return sorted_roots(blocks.A, blocks.C)


def outcome_roots(unitary: np.ndarray, outcome: int) -> np.ndarray:
    """Roots of the `SPEC.md` §3 pencil for *outcome*."""

    blocks = split_qubit_first_blocks(unitary)
    if outcome == 0:
        return sorted_roots(blocks.D, -blocks.C)
    return sorted_roots(blocks.B, -blocks.A)


def separation(first: np.ndarray, second: np.ndarray) -> float:
    return float(np.max(np.abs(np.sort_complex(first) - np.sort_complex(second))))


def approved_unitary(
    connectivity: str,
    central_coupling: str,
    n_pixel: int,
    time: float,
    *,
    y_fields: bool,
) -> np.ndarray:
    """A propagator from the approved families, with the ``Y`` self-fields on or off.

    Every other term of these families is real in the computational basis, so
    ``y_fields`` alone decides whether ``U`` is symmetric.
    """

    hamiltonian = SinglePixelHamiltonianNumpy(
        N_pixel=n_pixel,
        J=1.10, Jxx=1.32, Jyy=2.53,
        Jx=0.10, Jy=0.05, Jz=0.06,
        hx=-1.34, hy=0.7 if y_fields else 0.0, hz=1.00,
        hx0=-1.35, hy0=-1.69 if y_fields else 0.0, hz0=2.01,
        connectivity=connectivity, central_coupling=central_coupling,
    )
    return expm(-1j * hamiltonian.generate() * time)


@pytest.mark.parametrize("seed", [7, 11, 23])
def test_fixed_input_pencil_is_the_outcome_pencil_of_the_adjoint(seed: int) -> None:
    """Statement 1, which assumes nothing about the unitary.

    A Haar unitary is not symmetric, so the two characterizations of the *same*
    propagator genuinely differ; only passing to the adjoint identifies them.
    """

    unitary = generate_random_unitary(8, seed=seed)

    assert separation(fixed_input_roots(unitary), outcome_roots(unitary.conj().T, 0)) < EXACT
    assert separation(fixed_input_roots(unitary), outcome_roots(unitary, 0)) > 1.0


@pytest.mark.parametrize("connectivity", ["ring", "chain"])
@pytest.mark.parametrize("central_coupling", ["all", "first"])
@pytest.mark.parametrize("time", [1.0, 211.0])
def test_real_hamiltonian_conjugates_the_outcome_roots(
    connectivity: str, central_coupling: str, time: float
) -> None:
    """Statement 2 across the approved families: radii agree, azimuths mirror."""

    unitary = approved_unitary(connectivity, central_coupling, 4, time, y_fields=False)

    assert np.max(np.abs(unitary - unitary.T)) < EXACT

    fixed = fixed_input_roots(unitary)
    outcome = outcome_roots(unitary, 0)
    assert separation(fixed, np.conj(outcome)) < EXACT
    assert float(np.max(np.abs(np.sort(np.abs(fixed)) - np.sort(np.abs(outcome))))) < EXACT

    # The intermediate step of the proof, checked on its own: transposing the
    # outcome-1 pencil maps it to the fixed-input pencil under z = -1/lambda.
    assert separation(fixed, -1.0 / outcome_roots(unitary, 1)) < 1.0e-8


def test_conjugation_map_is_not_vacuous() -> None:
    """Replacing the conjugation by the identity must break the agreement.

    Without this the preceding test would also pass for a real root set, where
    conjugation does nothing.
    """

    unitary = approved_unitary("chain", "first", 4, 211.0, y_fields=False)
    outcome = outcome_roots(unitary, 0)

    assert separation(fixed_input_roots(unitary), outcome) > 1.0e-3


def test_y_self_field_breaks_the_symmetry_and_the_equality() -> None:
    """The one corner of the approved families where statement 2 does not hold.

    The ``Y`` self-fields are the only imaginary terms these families admit, so
    they alone destroy ``U^T = U``; the duality of statement 1 survives.
    """

    unitary = approved_unitary("chain", "first", 4, 211.0, y_fields=True)

    assert np.max(np.abs(unitary - unitary.T)) > 1.0e-3

    fixed = fixed_input_roots(unitary)
    outcome = outcome_roots(unitary, 0)
    assert separation(fixed, np.conj(outcome)) > 1.0e-3
    assert float(np.max(np.abs(np.sort(np.abs(fixed)) - np.sort(np.abs(outcome))))) > 1.0e-6

    assert separation(fixed, outcome_roots(unitary.conj().T, 0)) < EXACT


def test_the_two_pencils_carry_the_same_weights() -> None:
    """The duality pairs kernel dimensions, not just root locations."""

    unitary = approved_unitary("chain", "first", 4, 211.0, y_fields=False)
    blocks = split_qubit_first_blocks(unitary)

    fixed = characterize_pencil_roots(blocks.A, blocks.C)
    outcome = characterize_pencil_roots(blocks.D, -blocks.C)

    assert fixed.status == STATUS_REGULAR
    assert outcome.status == STATUS_REGULAR
    assert fixed.distinct_root_count == outcome.distinct_root_count
    assert fixed.total_kernel_dimension == outcome.total_kernel_dimension
    assert sorted(root.kernel_dimension for root in fixed.roots) == sorted(
        root.kernel_dimension for root in outcome.roots
    )
