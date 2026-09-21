"""Tests for the projective relative-evolution matrix pencil."""

import numpy as np

from core.relative_evolution_pencil import (
    audit_linear_pencil_regularity,
    compare_direct_and_generalized,
    diagnose_projective_duplicates,
    generalized_relative_evolution_spectrum,
    matched_projective_angle_error,
)


def test_finite_pencil_matches_direct_solve() -> None:
    u00 = np.array([[2.0, 0.4], [0.0, 1.5]], dtype=np.complex128)
    target = np.diag([0.25, 3.0j])
    u10 = u00 @ target

    spectrum = generalized_relative_evolution_spectrum(u00, u10)
    comparison = compare_direct_and_generalized(u00, u10)

    assert np.all(spectrum.finite)
    assert not np.any(spectrum.infinite)
    assert not np.any(spectrum.indeterminate)
    assert np.allclose(np.sort(spectrum.radii), np.array([0.25, 3.0]))
    assert comparison["eligible"] is True
    assert comparison["maximum_angle_error"] < 1.0e-12
    assert spectrum.maximum_homogeneous_residual < 1.0e-12
    assert spectrum.maximum_left_homogeneous_residual < 1.0e-12
    assert np.all(np.isfinite(spectrum.local_coordinate_condition_numbers))
    assert np.all(spectrum.local_condition_coordinate == "lambda")


def test_singular_u00_produces_infinite_root_and_theta_pi() -> None:
    u00 = np.diag([1.0, 0.0])
    u10 = np.diag([0.5, 1.0])

    spectrum = generalized_relative_evolution_spectrum(u00, u10)

    assert np.count_nonzero(spectrum.infinite) == 1
    assert np.isinf(spectrum.radii[spectrum.infinite][0])
    assert spectrum.theta[spectrum.infinite][0] == np.pi
    assert spectrum.numerical_rank_u00 == 1
    assert np.isinf(spectrum.condition_number_u00)


def test_common_nullspace_is_indeterminate_not_a_pseudoinverse_root() -> None:
    u00 = np.diag([1.0, 0.0])
    u10 = np.diag([0.5, 0.0])

    spectrum = generalized_relative_evolution_spectrum(u00, u10)

    assert np.count_nonzero(spectrum.indeterminate) == 1
    assert np.isnan(spectrum.theta[spectrum.indeterminate][0])
    assert not spectrum.finite[spectrum.indeterminate][0]
    assert not spectrum.infinite[spectrum.indeterminate][0]


def test_exact_tangent_pole_is_represented_projectively() -> None:
    # One detector basis state and H = -g X_c give U00=cos(gt),
    # U10=i sin(gt).  At gt=pi/2 the ordinary M diverges.
    u00 = np.array([[0.0]], dtype=np.complex128)
    u10 = np.array([[1.0j]], dtype=np.complex128)

    spectrum = generalized_relative_evolution_spectrum(u00, u10)

    assert spectrum.infinite[0]
    assert spectrum.theta[0] == np.pi
    assert spectrum.maximum_homogeneous_residual == 0.0


def test_projective_angles_are_invariant_under_common_block_scaling() -> None:
    rng = np.random.default_rng(20260801)
    u00 = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
    u10 = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))

    first = generalized_relative_evolution_spectrum(u00, u10)
    second = generalized_relative_evolution_spectrum((2.0 - 3.0j) * u00, (2.0 - 3.0j) * u10)
    maximum, rms = matched_projective_angle_error(first.theta, second.theta)

    assert maximum < 1.0e-12
    assert rms < 1.0e-12
    assert first.maximum_homogeneous_residual < 1.0e-12
    assert second.maximum_homogeneous_residual < 1.0e-12


def test_repeated_root_and_representative_nullity_are_audited() -> None:
    u00 = np.eye(3)
    u10 = np.diag([1.0, 1.0, 2.0])

    spectrum = generalized_relative_evolution_spectrum(
        u00,
        u10,
        audit_root_indices=[0, 1, 2],
        assess_regularity=True,
        duplicate_tolerance=1.0e-12,
    )

    assert spectrum.regularity_audit is not None
    assert spectrum.regularity_audit.status == "numerically_regular_at_sample"
    assert spectrum.duplicate_diagnostics.performed
    assert spectrum.duplicate_diagnostics.largest_multiplicity == 2
    assert spectrum.duplicate_diagnostics.distinct_root_count == 2
    assert sorted(audit.nullity for audit in spectrum.root_audits) == [1, 2, 2]


def test_all_sampled_ranks_warn_for_zero_singular_pencil() -> None:
    zeros = np.zeros((2, 2))

    audit = audit_linear_pencil_regularity(zeros, zeros)
    spectrum = generalized_relative_evolution_spectrum(
        zeros,
        zeros,
        assess_regularity=True,
    )

    assert audit.status == "numerically_singular_at_all_samples"
    assert audit.maximum_numerical_rank == 0
    assert spectrum.regularity_audit is not None
    assert spectrum.regularity_audit.status == audit.status
    assert np.all(spectrum.indeterminate)


def test_duplicate_diagnostics_skip_quadratic_work_above_limit() -> None:
    alpha = np.arange(1.0, 7.0)
    beta = np.ones(6)

    result = diagnose_projective_duplicates(
        alpha,
        beta,
        tolerance=1.0e-12,
        maximum_roots=5,
    )

    assert not result.performed
    assert result.distinct_root_count == -1


def test_left_eigenvector_opt_out_preserves_the_projective_spectrum() -> None:
    """Disabling left eigenvectors is a diagnostic reduction, not a new spectrum.

    The opt-out exists so that production-size runs can trade the left-vector
    diagnostics for one fewer ``d x d`` complex array.  It must not perturb the
    roots, angles, or right-hand backward residuals by even one ulp.
    """

    rng = np.random.default_rng(20260827)
    dimension = 24
    unitary, _ = np.linalg.qr(
        rng.normal(size=(2 * dimension, 2 * dimension))
        + 1j * rng.normal(size=(2 * dimension, 2 * dimension))
    )
    u00 = unitary[:dimension, :dimension].copy()
    u10 = unitary[dimension:, :dimension].copy()

    full = generalized_relative_evolution_spectrum(u00, u10)
    lean = generalized_relative_evolution_spectrum(
        u00, u10, compute_left_eigenvectors=False
    )

    for field in ("alpha", "beta", "eigenvalues", "radii", "theta"):
        np.testing.assert_array_equal(
            np.asarray(getattr(full, field)), np.asarray(getattr(lean, field))
        )
    np.testing.assert_array_equal(full.finite, lean.finite)
    np.testing.assert_array_equal(full.infinite, lean.infinite)
    np.testing.assert_array_equal(full.indeterminate, lean.indeterminate)
    np.testing.assert_array_equal(
        full.homogeneous_residuals, lean.homogeneous_residuals
    )
    assert full.maximum_homogeneous_residual == lean.maximum_homogeneous_residual
    assert full.condition_number_u00 == lean.condition_number_u00
    assert full.numerical_rank_u00 == lean.numerical_rank_u00


def test_left_eigenvector_opt_out_reports_nan_instead_of_guessing() -> None:
    """Left-defined diagnostics must be NaN, never approximated from the right."""

    u00 = np.array([[2.0, 0.4], [0.0, 1.5]], dtype=np.complex128)
    u10 = u00 @ np.diag([0.25, 3.0j])

    lean = generalized_relative_evolution_spectrum(
        u00, u10, compute_left_eigenvectors=False
    )

    assert lean.left_eigenvectors.shape == (2, 0)
    assert np.all(np.isnan(lean.left_homogeneous_residuals))
    assert np.isnan(lean.maximum_left_homogeneous_residual)
    assert np.all(np.isnan(lean.local_coordinate_condition_numbers))
    # The coordinate label describes the root, not the left eigenvector, so it
    # must still be recorded rather than left at the indeterminate default.
    assert np.all(lean.local_condition_coordinate == "lambda")


def test_local_coordinate_labels_survive_the_opt_out_for_infinite_roots() -> None:
    u00 = np.diag([1.0, 0.0]).astype(np.complex128)
    u10 = np.diag([0.5, 1.0]).astype(np.complex128)

    full = generalized_relative_evolution_spectrum(u00, u10)
    lean = generalized_relative_evolution_spectrum(
        u00, u10, compute_left_eigenvectors=False
    )

    np.testing.assert_array_equal(
        full.local_condition_coordinate, lean.local_condition_coordinate
    )
    assert "mu=1/lambda" in set(lean.local_condition_coordinate)


def test_spectrum_records_whether_left_diagnostics_were_computed() -> None:
    """NaN from "not computed" must be distinguishable from NaN from "singular".

    ``qz_valid`` gates on the left backward residual, and ``NaN < 1e-10`` is
    False.  Without an explicit flag a reduced-diagnostic run and a genuinely
    failed one are indistinguishable in the record.
    """

    import pytest

    from core.hamiltonian_classification import _require_left_diagnostics

    u00 = np.array([[2.0, 0.4], [0.0, 1.5]], dtype=np.complex128)
    u10 = u00 @ np.diag([0.25, 3.0j])

    full = generalized_relative_evolution_spectrum(u00, u10)
    lean = generalized_relative_evolution_spectrum(
        u00, u10, compute_left_eigenvectors=False
    )

    assert full.left_diagnostics_available is True
    assert lean.left_diagnostics_available is False

    _require_left_diagnostics(full.left_diagnostics_available)
    with pytest.raises(ValueError, match="compute_left_eigenvectors=False"):
        _require_left_diagnostics(lean.left_diagnostics_available)


def test_singular_pencil_keeps_left_diagnostics_flag_true() -> None:
    """An all-indeterminate pencil yields a NaN residual for a real reason.

    That case must keep flowing through the classification gate as it always
    has, rather than being mistaken for a reduced-diagnostic run.
    """

    from core.hamiltonian_classification import _require_left_diagnostics

    zero = np.zeros((3, 3), dtype=np.complex128)

    spectrum = generalized_relative_evolution_spectrum(zero, zero)

    assert np.all(spectrum.indeterminate)
    assert np.isnan(spectrum.maximum_left_homogeneous_residual)
    assert spectrum.left_diagnostics_available is True
    _require_left_diagnostics(spectrum.left_diagnostics_available)


def _structured_ring_blocks(detector_n: int) -> tuple[np.ndarray, np.ndarray]:
    """Return the ``(U00, U10)`` blocks of a symmetric matched ring at ``t=37``."""

    from scipy.linalg import expm

    from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy

    hamiltonian = SinglePixelHamiltonianNumpy(
        N_pixel=detector_n,
        J=1.0,
        Jpm=0.0,
        Jx=0.01 / np.sqrt(detector_n),
        Jy=0.0,
        Jz=0.0,
        Jzx=0.0,
        Jcpm=0.0,
        hx=0.0,
        hz=0.1,
        hx0=0.0,
        hz0=0.1,
        connectivity="ring",
        central_coupling="all",
    ).generate()
    unitary = expm(-1.0j * hamiltonian * 37.0)
    half = unitary.shape[0] // 2
    return unitary[:half, :half].copy(), unitary[half:, :half].copy()


def _worst_backward_error(
    u00: np.ndarray,
    u10: np.ndarray,
    alpha: np.ndarray,
    beta: np.ndarray,
) -> float:
    """Return the largest ``sigma_min(beta U10 - alpha U00)`` over unit root pairs."""

    worst = 0.0
    for a, b in zip(alpha, beta, strict=True):
        scale = float(np.hypot(abs(a), abs(b)))
        if scale == 0.0:
            continue
        smallest = np.linalg.svd(
            (b / scale) * u10 - (a / scale) * u00, compute_uv=False
        )[-1]
        worst = max(worst, float(smallest))
    return worst


def test_preconditioning_restores_precision_on_structured_blocks() -> None:
    """LAPACK ``zggev`` loses digits on exactly structured symmetric blocks.

    Every root of this pencil is semisimple and every eigenvalue condition
    number is order one, so the loss is a property of the exact zeros in the
    blocks rather than of the problem.  The unitary DFT right factor mixes that
    structure away without changing the projective spectrum, and both the roots
    and the eigenvectors return to machine precision.
    """

    u00, u10 = _structured_ring_blocks(4)

    plain = generalized_relative_evolution_spectrum(u00, u10, precondition=False)
    preconditioned = generalized_relative_evolution_spectrum(u00, u10)

    assert plain.preconditioner == "none"
    assert preconditioned.preconditioner == "dft"

    plain_backward = _worst_backward_error(u00, u10, plain.alpha, plain.beta)
    fixed_backward = _worst_backward_error(
        u00, u10, preconditioned.alpha, preconditioned.beta
    )
    assert plain_backward > 1.0e-10
    assert fixed_backward < 1.0e-14

    # The eigenvectors are the collapsible detector states, so their residual
    # matters as much as the root location.
    assert plain.maximum_homogeneous_residual > 1.0e-10
    assert preconditioned.maximum_homogeneous_residual < 1.0e-14


def test_preconditioning_leaves_generic_pencils_unharmed() -> None:
    """A generic pencil is already accurate, and the DFT factor must not cost it."""

    rng = np.random.default_rng(20260920)
    dimension = 24
    unitary, _ = np.linalg.qr(
        rng.normal(size=(2 * dimension, 2 * dimension))
        + 1j * rng.normal(size=(2 * dimension, 2 * dimension))
    )
    u00 = unitary[:dimension, :dimension].copy()
    u10 = unitary[dimension:, :dimension].copy()

    plain = generalized_relative_evolution_spectrum(u00, u10, precondition=False)
    preconditioned = generalized_relative_evolution_spectrum(u00, u10)

    maximum, _ = matched_projective_angle_error(plain.theta, preconditioned.theta)
    assert maximum < 1.0e-12
    assert preconditioned.maximum_homogeneous_residual < 1.0e-14


def test_preconditioning_applies_without_left_eigenvectors() -> None:
    """The correction is a change of basis, so the lean path gets it too."""

    u00, u10 = _structured_ring_blocks(4)

    lean = generalized_relative_evolution_spectrum(
        u00, u10, compute_left_eigenvectors=False
    )

    assert lean.preconditioner == "dft"
    assert lean.left_diagnostics_available is False
    assert _worst_backward_error(u00, u10, lean.alpha, lean.beta) < 1.0e-14
    assert lean.maximum_homogeneous_residual < 1.0e-14
