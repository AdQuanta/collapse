"""Regression checks for the fixed-Jx h_z-resonance workflow."""

from __future__ import annotations

import numpy as np

from core.analysis import evolution_subblocks_from_eigenbasis
from core.resonant_study import REQUIRED_JX, StudyConfig, _SinglePixelHamiltonian, folded_wrapped_gaussian, folded_wrapped_gaussian_bin_density, relative_data, run_case, wrapped_variance
from scipy.linalg import eigh
import json
from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy


def _hamiltonian(jx: float) -> np.ndarray:
    return _SinglePixelHamiltonian(
        N_pixel=3, J=1.0, Jx=jx / np.sqrt(3), hz=2.0, hz0=0.0,
        connectivity="ring", central_coupling="all",
    ).generate()


def test_fixed_jx_enters_single_pixel_hamiltonian():
    """This fails if the requested Jx=0.01 is accidentally ignored."""
    requested = _hamiltonian(REQUIRED_JX)
    decoupled = _hamiltonian(0.0)
    assert not np.allclose(requested, decoupled)
    assert np.allclose(requested, requested.conj().T)


def test_config_uses_detector_n_and_collective_edge_scale():
    config = StudyConfig(detector_n=8, hz=0.0, times=(1.0,))
    assert config.detector_dimension == 256
    assert config.full_dimension == 512
    assert np.isclose(config.edge_jx, REQUIRED_JX / np.sqrt(8))


def test_relative_data_reconstructs_eigenvalue_angles_with_solve():
    u00 = np.diag([2.0, 3.0])
    target = np.diag([0.0, 50.0j])
    data = relative_data(u00, u00 @ target)
    reconstructed = np.tan(data.theta / 2) * np.exp(1j * data.phi)
    finite = np.isfinite(data.phi)
    assert data.solver == "solve"
    assert data.solve_residual < 1e-13
    assert data.eigen_residual_max < 1e-12
    assert np.allclose(np.sort_complex(reconstructed[finite]), np.sort_complex(data.eigenvalues[finite]))
    assert np.isnan(data.phi[np.argmin(np.abs(data.eigenvalues))])


def test_eigenbasis_subblocks_reproduce_identity_at_zero_time():
    e = np.array([-1.0, -0.2, 0.5, 1.1])
    u00, u10 = evolution_subblocks_from_eigenbasis(e, np.eye(4), 0.0)
    assert np.allclose(u00, np.eye(2))
    assert np.allclose(u10, 0.0)


def test_wrapped_variance_has_all_three_expected_resonance_lines():
    t = 25.0
    resonance = [wrapped_variance(value, t) for value in (0.0, 2.0, -2.0)]
    off = wrapped_variance(1.0, t)
    assert min(resonance) > 10.0 * off


def test_quspin_and_numpy_single_pixel_hamiltonians_agree_small_n():
    parameters = dict(N_pixel=3, J=1.0, Jx=REQUIRED_JX / np.sqrt(3), hz=-2.0, hz0=0.0, connectivity="ring", central_coupling="all")
    reference = SinglePixelHamiltonianNumpy(**parameters).generate()
    tested = _SinglePixelHamiltonian(**parameters).generate()
    assert np.allclose(tested, reference)


def test_wrapped_gaussian_is_even_periodic_and_normalized():
    theta = np.linspace(0.0, np.pi, 20001)
    density = folded_wrapped_gaussian(theta, 0.7)
    assert np.isclose(np.trapezoid(density, theta), 1.0, atol=2e-4)
    assert np.isclose(density[0], folded_wrapped_gaussian(np.array([2*np.pi]), 0.7)[0], atol=1e-12)
    assert np.all(density >= 0.0)


def test_wrapped_gaussian_bin_density_resolves_narrow_endpoint_peak():
    edges = np.linspace(0.0, np.pi, 49)
    density = folded_wrapped_gaussian_bin_density(edges, 1e-4)
    assert np.isclose(np.sum(density * np.diff(edges)), 1.0, atol=1e-12)
    assert density[0] > 15.0
    assert np.all(density >= 0.0)


def test_physical_propagation_is_unitary_and_solve_matches_inverse():
    h = _hamiltonian(REQUIRED_JX)
    values, vectors = eigh(h)
    u = (vectors * np.exp(-1j * values * 0.7)) @ vectors.conj().T
    assert np.allclose(u.conj().T @ u, np.eye(u.shape[0]), atol=1e-12)
    half = u.shape[0] // 2
    via_solve = np.linalg.solve(u[:half,:half], u[half:,:half])
    via_inverse = np.linalg.inv(u[:half,:half]) @ u[half:,:half]
    assert np.allclose(via_solve, via_inverse, atol=1e-12)


def test_reduced_end_to_end_serializes_and_reloads(tmp_path):
    record = run_case(StudyConfig(3, 0.0, (1.0, 10.0)), tmp_path / 'case')
    saved = json.loads((tmp_path / 'case' / 'metadata.json').read_text(encoding='utf-8'))
    raw = np.load(tmp_path / 'case' / 'aggregate.npz')
    assert saved['config']['jx'] == REQUIRED_JX
    assert saved['summary']['eigenvalue_count'] == record['eigenvalue_count']
    assert raw['theta'].size == record['eigenvalue_count']
