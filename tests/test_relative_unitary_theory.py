from __future__ import annotations

import numpy as np

from core.relative_unitary_theory import (
    cayley_matrix,
    exact_relative_objects,
    finite_time_filter,
    finite_time_kernel,
    folded_angles_from_relative_unitary,
    leading_cayley_approximation,
)


def test_finite_time_filter_has_correct_zero_gap_limit() -> None:
    gaps = np.asarray([0.0, 1.0e-15, 0.7])
    values = finite_time_filter(gaps, 3.2)
    assert np.allclose(values[:2], 3.2)
    assert np.allclose(values[2], np.expm1(1j * 0.7 * 3.2) / (1j * 0.7))


def test_exact_relative_unitary_cayley_identity_and_angles() -> None:
    detector = np.diag([-0.7, 0.2, 1.1]).astype(complex)
    coupling = np.asarray([[0.2, 0.4, 0.0], [0.4, -0.1, 0.3], [0.0, 0.3, 0.5]], dtype=complex)
    _u00, _u10, relative, m_matrix = exact_relative_objects(detector, coupling, 0.07, 1.9)
    assert np.allclose(m_matrix, cayley_matrix(relative), atol=2.0e-13)
    phases = np.sort(np.abs(np.angle(np.linalg.eigvals(relative))))
    assert np.allclose(folded_angles_from_relative_unitary(relative), phases)


def test_leading_magnus_converges_as_coupling_decreases() -> None:
    detector = np.diag([-0.8, 0.1, 0.9]).astype(complex)
    coupling = np.asarray([[0.1, 0.3, 0.2], [0.3, -0.2, 0.4], [0.2, 0.4, 0.25]], dtype=complex)
    kernel = finite_time_kernel(detector, coupling, 1.3)
    assert np.allclose(kernel, kernel.conj().T)
    errors = []
    for strength in (0.08, 0.04, 0.02):
        *_unused, exact_m = exact_relative_objects(detector, coupling, strength, 1.3)
        _kernel, _relative, approximate_m = leading_cayley_approximation(detector, coupling, strength, 1.3)
        errors.append(np.linalg.norm(exact_m - approximate_m, ord=2))
    assert errors[2] < errors[1] < errors[0]
