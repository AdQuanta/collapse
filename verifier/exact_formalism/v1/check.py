"""Frozen exact-collapse-formalism verifier approved on 2026-09-19."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TOLERANCE = 1e-12
CASE_COUNTS = {
    'identity': 8, 'qnd': 8, 'generic': 8, 'semisimple': 8,
    'defective': 2, 'swap': 12, 'homogeneous_rescaling': 8,
    'detector_basis_change': 8, 'spectator': 24, 'kernel_superposition': 2,
    'wrong_outcome': 8, 'wrong_coordinate_order': 8, 'perturbed_detector': 8,
    'nonunitary': 8, 'near_collapse': 2,
}
NEGATIVE = {'wrong_outcome', 'wrong_coordinate_order', 'perturbed_detector',
            'nonunitary', 'near_collapse'}


def symbolic_checks():
    """Exact component identities; the arbitrary-dimension argument is in METHOD."""
    a, b = sp.symbols('alpha beta', complex=True)
    x, y = sp.symbols('x y', complex=True)
    entries = sp.symbols('u:16', complex=True)
    U = sp.Matrix(4, 4, entries)
    d = sp.Matrix([x, y])
    q = sp.Matrix([b, a])
    actual = U * sp.kronecker_product(q, d)
    expected = (b*U[:2, :2]*d + a*U[:2, 2:]*d).col_join(
        b*U[2:, :2]*d + a*U[2:, 2:]*d)
    assert sp.simplify(actual-expected) == sp.zeros(4, 1)
    swap = sp.eye(4).permute_rows([0, 2, 1, 3])
    for outcome in (0, 1):
        pole = sp.eye(2)[:, outcome]
        assert swap*sp.kronecker_product(q, pole) == sp.kronecker_product(pole, q)
        forbidden = swap[2*(1-outcome):2*(2-outcome), :]
        pencil = b*forbidden[:, :2] + a*forbidden[:, 2:]
        assert sp.expand(pencil.det()) == 0
    # Orthogonality of the two output branches gives the exact norm identity.
    r, s, t, w = sp.symbols('r s t w', complex=True)
    retained, forbidden = sp.Matrix([r, s]), sp.Matrix([t, w])
    joint = retained.col_join(forbidden)
    assert sp.expand((joint.adjoint()*joint)[0] -
                     (retained.adjoint()*retained)[0] -
                     (forbidden.adjoint()*forbidden)[0]) == 0
    # A degenerate kernel permits every linear combination, not just a basis.
    m = sp.Matrix([[0, 0, 0], [0, 0, 0], [0, 0, 1]])
    assert m*sp.Matrix([x, y, 0]) == sp.zeros(3, 1)
    jordan = sp.Matrix([[1, 1], [0, 1]])
    assert (sp.eye(2)-jordan)*sp.Matrix([1, 0]) == sp.zeros(2, 1)
    return ['block identity', 'branch norm identity', 'SWAP arbitrary-ray identity',
            'SWAP singular determinants', 'kernel superposition', 'defective kernel']


def normalized(v):
    v = np.asarray(v, dtype=complex)
    scale = max(np.max(abs(v.real)), np.max(abs(v.imag)))
    if not np.isfinite(scale) or scale == 0:
        raise ValueError('invalid vector')
    return (v/scale) / np.linalg.norm(v/scale)


def inspect_state(U, outcome, alpha, beta, detector):
    """Independent direct propagation: no production helper or block splitter."""
    U = np.asarray(U, dtype=complex)
    if U.ndim != 2 or U.shape[0] != U.shape[1] or U.shape[0] % 2 or not U.size:
        raise ValueError('invalid operator dimensions')
    if not np.all(np.isfinite(U)) or outcome not in (0, 1):
        raise ValueError('invalid operator or outcome')
    dimension = U.shape[0]//2
    if np.shape(detector) != (dimension,):
        raise ValueError('invalid detector dimension')
    q, d = normalized([beta, alpha]), normalized(detector)
    evolved = U @ np.kron(q, d)
    retained = evolved[outcome*dimension:(outcome+1)*dimension]
    forbidden = evolved[(1-outcome)*dimension:(2-outcome)*dimension]
    target = np.zeros_like(evolved)
    target[outcome*dimension:(outcome+1)*dimension] = retained
    # No normalization of the retained branch is allowed.
    errors = {
        'unitarity': float(np.linalg.norm(U.conj().T@U-np.eye(U.shape[0]), ord=2)),
        'qubit_normalization': float(abs(np.linalg.norm(q)-1)),
        'detector_normalization': float(abs(np.linalg.norm(d)-1)),
        'evolved_normalization': float(abs(np.linalg.norm(evolved)-1)),
        'forbidden_branch_norm': float(np.linalg.norm(forbidden)),
        'retained_norm_error': float(abs(np.linalg.norm(retained)-1)),
        'factorization_residual': float(np.linalg.norm(evolved-target)),
    }
    arrays = dict(qubit_input=q, detector_input=d, evolved_joint_state=evolved,
                  retained_detector_branch=retained)
    return errors, arrays


def verify_packet(packet):
    metadata = json.loads((packet/'cases.json').read_text())
    rows = metadata['states']
    expected = {f'{name}__{i}' for name, count in CASE_COUNTS.items() for i in range(count)}
    if len(rows) != len(expected) or {r['id'] for r in rows} != expected:
        raise ValueError('missing, duplicated, or unexpected fixture states')
    results = []
    with np.load(packet/'states.npz', allow_pickle=False) as saved:
        for row in rows:
            key = row['id']
            case = key.split('__')[0]
            get = lambda field: saved[f'{key}__{field}']
            errors, arrays = inspect_state(get('U'), int(get('outcome')), complex(get('alpha')),
                                            complex(get('beta')), get('detector'))
            for field, value in arrays.items():
                errors[f'saved_{field}'] = float(np.linalg.norm(get(field)-value))
            for field in ('forbidden_branch_norm', 'retained_norm_error', 'factorization_residual'):
                errors[f'saved_{field}'] = float(abs(float(get(field))-errors[field]))
            agreement = all(np.isfinite(v) and v <= TOLERANCE for k, v in errors.items()
                            if k.startswith('saved_'))
            physical = all(np.isfinite(v) and v <= TOLERANCE for k, v in errors.items()
                           if not k.startswith('saved_'))
            # A negative control must fail its intended check, not an unrelated one.
            failure_key = 'unitarity' if case == 'nonunitary' else 'forbidden_branch_norm'
            expected_rejection = case in NEGATIVE
            passed = agreement and ((not physical and errors[failure_key] > TOLERANCE)
                                    if expected_rejection else physical)
            serializable_errors = {k: v if np.isfinite(v) else None for k, v in errors.items()}
            results.append(dict(id=key, checks=serializable_errors, expected_rejection=expected_rejection,
                                accepted_as_collapse=physical, passed=bool(passed)))
    return dict(status='PASS' if all(r['passed'] for r in results) else 'FAIL',
                certification=True, tolerance=TOLERANCE, symbolic_checks=symbolic_checks(),
                states=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    record = dict(timestamp=datetime.now(timezone.utc).isoformat(), certification=True,
                  packet=str(args.packet.resolve()))
    try:
        manifest = json.loads((HERE/'manifest.json').read_text())
        if manifest['status'] != 'activated' or manifest['certification'] is not True:
            raise ValueError('verifier manifest is not activated for certification')
        if hashlib.sha256((ROOT/'SPEC.md').read_bytes()).hexdigest() != manifest['spec_sha256']:
            raise ValueError('review specification hash mismatch')
        for path, digest in manifest['source_hashes'].items():
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != digest:
                raise ValueError(f'review manifest mismatch: {path}')
        provenance = json.loads((args.packet/'provenance.json').read_text())
        record['commit'] = provenance['commit']
        record['spec_sha256'] = manifest['spec_sha256']
        if provenance['source_hashes']['SPEC.md'] != manifest['spec_sha256']:
            raise ValueError('packet specification hash mismatch')
        for path, digest in provenance['source_hashes'].items():
            snapshot = args.packet/'source'/(path+'.snapshot')
            if hashlib.sha256(snapshot.read_bytes()).hexdigest() != digest:
                raise ValueError(f'packet source snapshot hash mismatch: {path}')
        record.update(verify_packet(args.packet))
        record['source_hashes'] = manifest['source_hashes']
        record['packet_hashes'] = {name: hashlib.sha256((args.packet/name).read_bytes()).hexdigest()
                                   for name in ('states.npz', 'cases.json', 'provenance.json')}
    except Exception as error:
        record.update(status='FAIL', error=f'{type(error).__name__}: {error}')
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open('a') as stream:
        stream.write(json.dumps(record, allow_nan=False, sort_keys=True)+'\n')
    print(json.dumps({k: v for k, v in record.items() if k != 'states'}, indent=2))
    if record['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
