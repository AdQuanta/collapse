"""Exact count certification and independent native propagator checks."""

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import eigvals, expm

from core.born_commuting_family import (
    certify_commuting_seed,
    conditional_qubit_angles,
    polar_gate_metrics,
    rational_phase_inventory,
)


CONFIG = json.loads((Path(__file__).parents[1] /
                     "configs/born_commuting_family_2026-09-11.json").read_text())


def test_exact_rational_certificate_proves_a_nonempty_open_family():
    certificate = certify_commuting_seed(CONFIG)
    assert certificate["gate_certified"]
    assert certificate["roots"] == 8192
    assert certificate["center_rms_upper"] < .018
    assert certificate["entire_ball_moment_residual_upper"] < .045
    assert certificate["minimum_edge_distance_rad_lower"] > .0001


def test_integer_count_inventory_matches_independent_native_angle_map():
    divisors = CONFIG["phase_divisors"]
    phases = 99*np.pi/(200*np.array(divisors))
    exact = rational_phase_inventory(divisors)
    measured = polar_gate_metrics(conditional_qubit_angles(phases))
    np.testing.assert_array_equal(exact["counts"], measured["counts"])
    assert measured["accepted"]


@pytest.mark.parametrize("graph", ["chain", "ring", "all_to_all"])
@pytest.mark.parametrize("hz0", [0., .073])
def test_reduced_native_quspin_exponential_matches_conditional_blocks(graph, hz0):
    from quspin.basis import spin_basis_1d
    from quspin.operators import hamiltonian
    from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

    couplings = np.array([.17, -.31, .083, .22, -.037])
    hx0, time = .019, 1.3
    model = SinglePixelHamiltonianQuSpin(
        N_pixel=5, J=0., Jpm=0., Jxx=.29, Jx=1., hx=.137,
        hx0=hx0, hz=0., hz0=hz0, connectivity=graph,
        central_coupling="all", use_symmetry=False,
    )
    static, size = model._build_static()
    # Supply one explicit realization of the backend's disordered Jx bonds.
    for operator, bonds in static:
        if operator == "xx":
            for bond in bonds:
                if bond[1] == 0:
                    bond[0] = -couplings[bond[2]-1]
    matrix = hamiltonian(
        static, [], basis=spin_basis_1d(size), dtype=np.float64,
        check_symm=False, check_herm=False, check_pcon=False,
    ).toarray()
    unitary = expm(-1j*time*matrix)
    a, c = unitary[:32, :32], unitary[32:, :32]
    homogeneous = eigvals(c, a, homogeneous_eigvals=True)
    theta = 2*np.arctan2(abs(homogeneous[0]), abs(homogeneous[1]))
    reference = conditional_qubit_angles(
        2*time*couplings, transverse_phase=2*time*hx0,
        longitudinal_phase=2*time*hz0,
    )
    np.testing.assert_allclose(np.sort(theta), np.sort(reference), atol=2e-12, rtol=0)
    np.testing.assert_allclose(unitary.conj().T @ unitary, np.eye(64), atol=2e-14)


def test_random_certified_perturbations_keep_exact_counts_and_gate():
    rng = np.random.default_rng(20260911)
    phases = 99*np.pi/(200*np.array(CONFIG["phase_divisors"]))
    reference = polar_gate_metrics(conditional_qubit_angles(phases))
    for _ in range(24):
        delta = rng.normal(size=15)
        delta *= CONFIG["phase_l1_radius"]*rng.uniform() / np.abs(delta).sum()
        result = polar_gate_metrics(conditional_qubit_angles(
            phases + delta[:13], transverse_phase=delta[13],
            longitudinal_phase=delta[14],
        ))
        np.testing.assert_array_equal(result["counts"], reference["counts"])
        assert result["accepted"]


def test_spectators_and_independent_coupling_signs_preserve_measure():
    phases = np.array([.2, .3, .7])
    baseline = conditional_qubit_angles(phases)
    transformed = conditional_qubit_angles(np.r_[-phases[::-1], 0., 0.])
    np.testing.assert_allclose(np.sort(transformed), np.repeat(np.sort(baseline), 4))


def test_integer_aliases_preserve_seed_and_the_detuned_neighborhood():
    phases = 99*np.pi/(200*np.array(CONFIG["phase_divisors"]))
    alias = phases + 2*np.pi*np.arange(-6, 7)
    reference = polar_gate_metrics(conditional_qubit_angles(phases))
    result = polar_gate_metrics(conditional_qubit_angles(
        alias, longitudinal_phase=CONFIG["phase_l1_radius"],
    ))
    np.testing.assert_array_equal(result["counts"], reference["counts"])
    assert result["accepted"]


def test_explicit_degenerate_and_nondegenerate_full_hamiltonians():
    from core.born_commuting_family import signed_sums

    divisors = CONFIG["phase_divisors"]
    common = 240240
    weights = np.array([99*common//q for q in divisors], dtype=np.int64)
    v = signed_sums(weights)
    assert np.all(v != 0)
    assert np.unique(np.r_[v, -v]).size < 2*v.size
    multiplier = 2*sum(abs(weights)) + 1
    detector = signed_sums(multiplier * 2**np.arange(13, dtype=np.int64))
    # Same sign-configuration ordering in both exact integer inventories.
    energies = np.r_[detector+v, detector-v]
    assert np.unique(energies).size == 16384


def test_outside_family_can_pass_and_violating_examples_fail():
    phases = 99*np.pi/(200*np.array(CONFIG["phase_divisors"]))
    # The explicit certified ball is a sufficient subset, not the full preimage.
    assert polar_gate_metrics(conditional_qubit_angles(phases * (100/99))) ["accepted"] is False
    assert polar_gate_metrics(conditional_qubit_angles(phases * (199/198)))["accepted"]
    assert not polar_gate_metrics(conditional_qubit_angles(phases*0))["accepted"]
    assert not polar_gate_metrics(conditional_qubit_angles(phases, longitudinal_phase=20))["accepted"]


def test_certificate_rejects_an_excessive_claimed_radius():
    with pytest.raises(ArithmeticError):
        certify_commuting_seed(dict(CONFIG, phase_l1_radius=.1))


def test_effective_iff_against_independent_bloch_chebyshev_native_ensemble():
    from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

    rng = np.random.default_rng(7312026)
    for index in range(16):
        j, jpm, jx, jy, hx, hx0, hz, hz0 = rng.uniform(-.7, .7, 8)
        model = SinglePixelHamiltonianQuSpin(
            N_pixel=5, J=j, Jpm=jpm, Jx=jx, Jy=jy, hx=hx, hx0=hx0,
            hz=hz, hz0=hz0, connectivity=["chain", "ring"][index % 2],
            central_coupling="all", use_symmetry=False,
        )
        unitary = expm(-1j*model.generate())
        roots = eigvals(unitary[32:, :32], unitary[:32, :32],
                        homogeneous_eigvals=True)
        alpha2, beta2 = abs(roots[0])**2, abs(roots[1])**2
        z = (beta2-alpha2)/(beta2+alpha2)
        theta = 2*np.arctan2(abs(roots[0]), abs(roots[1]))
        measured = polar_gate_metrics(theta)
        # Independent cosine moments use polynomial recurrence in Bloch z.
        previous, current = np.ones_like(z), z
        moments = [1., float(z.mean())]
        for _ in range(2, 17):
            previous, current = current, 2*z*current-previous
            moments.append(float(current.mean()))
        moments = np.array(moments)
        residuals = 2*moments[1::2]-moments[:-2:2]-moments[2::2]
        np.testing.assert_allclose(residuals, measured["residuals"], atol=8e-14)
        edges_z = np.cos(np.linspace(0, np.pi, 65))[::-1]
        blue = np.histogram(z, edges_z)[0][::-1]
        red = np.histogram(-z, edges_z)[0][::-1]
        total = blue+red
        if np.all(total > 0):
            born = (1+np.cos((np.arange(64)+.5)*np.pi/64))/2
            independent_gate = (np.sum((blue/total-born)**2) <= 64/400
                                and max(abs(residuals)) <= 1/20)
        else:
            independent_gate = False
        assert measured["accepted"] == independent_gate
