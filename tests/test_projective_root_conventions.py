"""Exact convention checks for production and forward matrix pencils."""

import numpy as np
from scipy.linalg import expm

from collapse.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from collapse.projective_roots import (
    append_uncoupled_spectator,
    antipodal_homogeneous_coordinates,
    bloch_vectors_from_homogeneous,
    direct_sum_detector_contexts,
    forward_pole_root_spectrum,
    matched_bloch_distance,
    production_root_spectrum,
    split_qubit_first_blocks,
)
from collapse.quantum_utils import generate_random_unitary


def _bloch(spectrum):
    assert not np.any(spectrum.indeterminate)
    return bloch_vectors_from_homogeneous(spectrum.alpha, spectrum.beta)


def test_homogeneous_bloch_map_includes_zero_and_infinity() -> None:
    vectors = bloch_vectors_from_homogeneous(
        np.array([0.0, 1.0, 1.0j]),
        np.array([1.0, 0.0, 1.0]),
    )

    assert np.allclose(vectors[0], [0.0, 0.0, 1.0])
    assert np.allclose(vectors[1], [0.0, 0.0, -1.0])
    assert np.allclose(vectors[2], [0.0, 1.0, 0.0])
    assert np.allclose(np.linalg.norm(vectors, axis=1), 1.0)


def test_production_of_adjoint_equals_forward_outcome_zero() -> None:
    unitary = generate_random_unitary(8, seed=20260815)
    forward = forward_pole_root_spectrum(unitary, outcome=0)
    production_adjoint = production_root_spectrum(unitary.conj().T)

    maximum, rms = matched_bloch_distance(_bloch(forward), _bloch(production_adjoint))

    assert maximum < 2.0e-12
    assert rms < 1.0e-12
    assert forward.maximum_homogeneous_residual < 1.0e-12
    assert production_adjoint.maximum_homogeneous_residual < 1.0e-12


def test_forward_outcome_roots_are_exact_antipodal_multisets() -> None:
    unitary = generate_random_unitary(8, seed=20260816)
    outcome_zero = forward_pole_root_spectrum(unitary, outcome=0)
    outcome_one = forward_pole_root_spectrum(unitary, outcome=1)
    anti_alpha, anti_beta = antipodal_homogeneous_coordinates(
        outcome_zero.alpha,
        outcome_zero.beta,
    )
    antipodes = bloch_vectors_from_homogeneous(anti_alpha, anti_beta)

    maximum, rms = matched_bloch_distance(antipodes, _bloch(outcome_one))

    assert maximum < 2.0e-12
    assert rms < 1.0e-12


def test_real_hamiltonian_forward_roots_are_azimuth_reflected_production_roots() -> None:
    rng = np.random.default_rng(20260817)
    raw = rng.normal(size=(8, 8))
    hamiltonian = 0.5 * (raw + raw.T)
    energies, vectors = np.linalg.eigh(hamiltonian)
    unitary = (vectors * np.exp(-1.0j * energies * 1.7)) @ vectors.T

    production = _bloch(production_root_spectrum(unitary))
    forward = _bloch(forward_pole_root_spectrum(unitary, outcome=0))
    reflected = production.copy()
    reflected[:, 1] *= -1.0
    maximum, rms = matched_bloch_distance(reflected, forward)

    assert maximum < 2.0e-12
    assert rms < 1.0e-12


def test_strict_qnd_unitary_has_only_pole_roots() -> None:
    detector_dimension = 3
    phases_zero = np.exp(1.0j * np.array([0.2, -0.7, 1.1]))
    phases_one = np.exp(1.0j * np.array([-0.1, 0.8, 1.7]))
    unitary = np.block(
        [
            [np.diag(phases_zero), np.zeros((3, 3))],
            [np.zeros((3, 3)), np.diag(phases_one)],
        ]
    )

    production = production_root_spectrum(unitary)
    outcome_zero = forward_pole_root_spectrum(unitary, outcome=0)
    outcome_one = forward_pole_root_spectrum(unitary, outcome=1)

    north = np.tile([0.0, 0.0, 1.0], (detector_dimension, 1))
    south = -north
    assert np.allclose(_bloch(production), north)
    assert np.allclose(_bloch(outcome_zero), north)
    assert np.allclose(_bloch(outcome_one), south)
    assert np.count_nonzero(outcome_one.infinite) == detector_dimension


def test_conserved_central_x_confines_production_roots_to_yz_great_circle() -> None:
    rng = np.random.default_rng(20260820)
    detector_dimension = 5
    raw_d = rng.normal(size=(detector_dimension, detector_dimension))
    raw_v = rng.normal(size=(detector_dimension, detector_dimension))
    h_detector = 0.5 * (raw_d + raw_d.T)
    interaction = 0.5 * (raw_v + raw_v.T)
    identity = np.eye(detector_dimension)
    central_x = np.array([[0.0, 1.0], [1.0, 0.0]])
    hamiltonian = np.kron(np.eye(2), h_detector) + np.kron(
        central_x, interaction
    )
    x_operator = np.kron(central_x, identity)
    assert np.allclose(hamiltonian @ x_operator, x_operator @ hamiltonian)

    unitary = expm(-1.0j * hamiltonian * 1.3)
    blocks = split_qubit_first_blocks(unitary)
    assert np.allclose(blocks.A, blocks.D)
    assert np.allclose(blocks.B, blocks.C)
    assert np.allclose(
        blocks.A.conj().T @ blocks.C + blocks.C.conj().T @ blocks.A,
        0.0,
        atol=2.0e-12,
    )
    roots = production_root_spectrum(unitary)
    bloch = _bloch(roots)

    assert np.max(np.abs(bloch[:, 0])) < 2.0e-12


def test_small_matched_ring_obeys_real_hamiltonian_forward_bridge() -> None:
    detector_n = 4
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
    assert np.allclose(hamiltonian, hamiltonian.T)
    unitary = expm(-1.0j * hamiltonian * 37.0)
    production = production_root_spectrum(
        unitary,
        assess_regularity=True,
        audit_root_indices=[0],
    )
    forward = forward_pole_root_spectrum(unitary, outcome=0)
    production_vectors = _bloch(production)
    production_vectors[:, 1] *= -1.0
    maximum, rms = matched_bloch_distance(production_vectors, _bloch(forward))

    assert maximum < 2.0e-11
    assert rms < 1.0e-11
    assert production.regularity_audit is not None
    assert production.regularity_audit.status == "numerically_regular_at_sample"
    assert production.maximum_homogeneous_residual < 1.0e-12
    assert production.maximum_left_homogeneous_residual < 1.0e-12
    assert production.root_audits[0].nullity >= 1


def test_uncoupled_spectator_repeats_roots_without_changing_normalized_density() -> None:
    unitary = generate_random_unitary(8, seed=20260818)
    spectator = generate_random_unitary(3, seed=20260819)
    base = production_root_spectrum(unitary)
    composed = production_root_spectrum(append_uncoupled_spectator(unitary, spectator))
    base_vectors = _bloch(base)
    composed_vectors = _bloch(composed)
    repeated = np.repeat(base_vectors, spectator.shape[0], axis=0)
    maximum, rms = matched_bloch_distance(repeated, composed_vectors)

    assert composed.theta.size == spectator.shape[0] * base.theta.size
    assert maximum < 3.0e-12
    assert rms < 1.0e-12

    from collapse.gleason_diagnostics import diagnose_labeled_bloch_histogram

    base_histogram = diagnose_labeled_bloch_histogram(
        base_vectors,
        n_mu=4,
        n_phi=8,
        require_full_coverage=False,
    )
    composed_histogram = diagnose_labeled_bloch_histogram(
        composed_vectors,
        n_mu=4,
        n_phi=8,
        require_full_coverage=False,
    )
    assert np.allclose(composed_histogram.counts_0, 3.0 * base_histogram.counts_0)
    assert np.allclose(composed_histogram.density_0, base_histogram.density_0)
    assert np.allclose(composed_histogram.density_1, base_histogram.density_1)


def test_detector_basis_permutation_leaves_root_multiset_invariant() -> None:
    unitary = generate_random_unitary(8, seed=20260821)
    permutation = np.eye(4)[[2, 0, 3, 1]]
    detector_change = np.kron(np.eye(2), permutation)
    transformed = detector_change @ unitary @ detector_change.T

    maximum, rms = matched_bloch_distance(
        _bloch(production_root_spectrum(unitary)),
        _bloch(production_root_spectrum(transformed)),
    )

    assert maximum < 3.0e-12
    assert rms < 1.0e-12


def test_nonuniform_direct_sum_refinement_changes_equal_root_measure() -> None:
    def rotation(angle: float) -> np.ndarray:
        return np.array(
            [
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)],
            ]
        )

    first = rotation(0.2)
    second = rotation(1.0)
    base = direct_sum_detector_contexts([first, second])
    refined = direct_sum_detector_contexts([first, first, second])
    base_roots = _bloch(production_root_spectrum(base))
    refined_roots = _bloch(production_root_spectrum(refined))
    first_root = _bloch(production_root_spectrum(first))[0]
    second_root = _bloch(production_root_spectrum(second))[0]

    assert np.allclose(np.mean(base_roots, axis=0), 0.5 * (first_root + second_root))
    assert np.allclose(
        np.mean(refined_roots, axis=0),
        (2.0 * first_root + second_root) / 3.0,
    )
    assert not np.allclose(
        np.mean(base_roots, axis=0),
        np.mean(refined_roots, axis=0),
    )
