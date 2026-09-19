"""Independent verifier checks, fixture coverage, and deliberate packet corruption."""
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from core.projective_roots import reconstruct_collapse_state

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = load('formalism_check', 'verifier/exact_formalism/v1/check.py')
BUILD = load('formalism_build', 'scripts/build_exact_formalism_packet.py')


def packet(path):
    cases, _ = BUILD.fixtures()
    arrays, rows = {}, []
    for case, states in cases.items():
        for i, (U, b, a, c, d) in enumerate(states):
            key = f'{case}__{i}'
            record = dict(U=U, outcome=b, alpha=a, beta=c, detector=d,
                          **asdict(reconstruct_collapse_state(U, b, a, c, d)))
            arrays.update({f'{key}__{k}': v for k, v in record.items()})
            rows.append(dict(id=key))
    (path/'cases.json').write_text(json.dumps(dict(states=rows)))
    np.savez(path/'states.npz', **arrays)
    return arrays


def test_complete_packet_and_expected_rejections(tmp_path):
    packet(tmp_path)
    result = CHECK.verify_packet(tmp_path)
    assert result['status'] == 'PASS'
    assert result['certification'] is True
    assert len(result['states']) == sum(CHECK.CASE_COUNTS.values())
    assert all(not r['accepted_as_collapse'] for r in result['states'] if r['expected_rejection'])


def test_corrupt_saved_state_is_rejected(tmp_path):
    arrays = packet(tmp_path)
    arrays['identity__0__evolved_joint_state'] = np.ones(6)
    np.savez(tmp_path/'states.npz', **arrays)
    assert CHECK.verify_packet(tmp_path)['status'] == 'FAIL'


def test_negative_control_cannot_silently_become_positive(tmp_path):
    arrays = packet(tmp_path)
    key = 'near_collapse__0'
    result = reconstruct_collapse_state(np.eye(4), 0, 0, 1, [1, 0])
    arrays[f'{key}__alpha'] = 0
    arrays.update({f'{key}__{k}': v for k, v in asdict(result).items()})
    np.savez(tmp_path/'states.npz', **arrays)
    assert CHECK.verify_packet(tmp_path)['status'] == 'FAIL'


def test_omitted_fixture_is_rejected(tmp_path):
    packet(tmp_path)
    rows = json.loads((tmp_path/'cases.json').read_text())['states']
    (tmp_path/'cases.json').write_text(json.dumps(dict(states=rows[:-1])))
    with pytest.raises(ValueError, match='missing'):
        CHECK.verify_packet(tmp_path)


def test_invariance_of_joint_states_and_histograms():
    cases, plots = BUILD.fixtures()
    permutation = np.eye(4)[[2, 0, 3, 1]]
    spectator = BUILD.qr_unitary(3, 20260819)
    for i, state in enumerate(cases['generic']):
        base = reconstruct_collapse_state(*state)
        changed = reconstruct_collapse_state(*cases['detector_basis_change'][i])
        np.testing.assert_allclose(changed.evolved_joint_state,
                                   np.kron(np.eye(2), permutation)@base.evolved_joint_state,
                                   rtol=0, atol=1e-12)
        for j in range(3):
            composed = reconstruct_collapse_state(*cases['spectator'][3*i+j])
            np.testing.assert_allclose(composed.evolved_joint_state,
                                       np.kron(base.evolved_joint_state, spectator[:, j]),
                                       rtol=0, atol=1e-12)
    base_hist = BUILD.theta_histograms(plots['generic']['coordinates'])
    for name in ('homogeneous_rescaling', 'detector_basis_change', 'spectator'):
        hist = BUILD.theta_histograms(plots[name]['coordinates'])
        for expected, actual in zip(base_hist, hist):
            np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)


def test_antipodal_roots_from_independent_forward_solves():
    cases, _ = BUILD.fixtures()
    roots = [complex(a/c) for U,b,a,c,d in cases['generic']]
    expected = [-1/np.conj(z) for z in roots[:4]]
    for z in expected:
        assert min(abs(z-w) for w in roots[4:]) < 1e-12


def test_empty_bins_are_undefined_and_marginals_normalize_separately():
    _, plots = BUILD.fixtures()
    for data in plots.values():
        edges, densities, ratio = BUILD.theta_histograms(data['coordinates'])
        for density in densities:
            np.testing.assert_allclose(np.sum(density*np.diff(edges)), 1, rtol=0, atol=1e-14)
        empty = densities[0]+densities[1] == 0
        assert np.all(np.isnan(ratio[empty]))
    assert 'UNDEFINED' in plots['swap']['kind']


def test_symbolic_identities():
    assert len(CHECK.symbolic_checks()) == 6
