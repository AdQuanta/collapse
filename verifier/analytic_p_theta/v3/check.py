"""Frozen independent dense-Pauli verifier for local Liouvillian certificates.

Input is JSON formula data. Neither candidate implementation nor production
code is imported. Previous verifier versions remain immutable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / 'v1'))
from reference import hamiltonian, pauli


def hashes() -> dict[str, str]:
    paths = [HERE / 'check.py', HERE.parent / 'v1/reference.py']
    return {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}


def zero(value, label: str) -> None:
    if sp.simplify(value) != 0:
        raise AssertionError(label + ': ' + str(sp.simplify(value)))


def norm_squared(matrix: sp.MatrixBase) -> sp.Expr:
    return sum(sp.conjugate(v) * v for v in matrix.todok().values())


def check(data: dict) -> list[dict]:
    results = []
    h, j, g = sp.symbols('h J g', real=True)
    variables = dict(h=h, J=j, g=g)
    for case in data['cases']:
        n, family = case['n'], case['family']
        fields = {name: [sp.sympify(x, locals=variables) for x in case[name]]
                  for name in ('hd', 'j1', 'j2')}
        fields.update(hq=[0]*3, g=[0]*3)
        d = 2**n
        full = hamiltonian(n, family, fields)
        detector = sp.ImmutableSparseMatrix(full[:d, :d])
        targets = range(1, n+1) if case['observable'] == 'collective_x' else (1,)
        observable = sum((pauli(n, site, 0)[:d, :d] for site in targets), sp.zeros(d))
        observable = sp.ImmutableSparseMatrix(observable)
        normalization = n if case['observable'] == 'collective_x' else 1
        current = observable
        values = []
        for order, formula in enumerate(case['moments']):
            actual = sp.expand(norm_squared(current) / (d*normalization))
            proposed = sp.sympify(formula, locals=variables)
            zero(actual-proposed, f"{case['id']} spectral moment {2*order}")
            values.append(str(sp.factor(actual)))
            current = sp.ImmutableSparseMatrix(detector*current-current*detector)
        if 'commutator_slope_squared' in case:
            normalized = observable/sp.sqrt(normalization)
            derivative = sp.I*(detector*normalized-normalized*detector)
            commutator = normalized*derivative-derivative*normalized
            zero(sp.expand(norm_squared(commutator)/d)
                 - sp.sympify(case['commutator_slope_squared'], locals=variables),
                 case['id']+' fluctuation commutator derivative')
        if 'echo_taylor' in case:
            coupling = sp.sympify(case['coupling'], locals=variables)
            plus = detector+coupling*observable/sp.sqrt(normalization)
            minus = detector-coupling*observable/sp.sqrt(normalization)
            degree = len(case['echo_taylor'])-1
            plus_powers, minus_powers = [sp.eye(d)], [sp.eye(d)]
            for _ in range(degree):
                plus_powers.append(sp.ImmutableSparseMatrix(plus_powers[-1]*plus))
                minus_powers.append(sp.ImmutableSparseMatrix(minus_powers[-1]*minus))
            for order, formula in enumerate(case['echo_taylor']):
                actual = sum(sp.I**k*(-sp.I)**(order-k)
                             *sp.trace(minus_powers[k]*plus_powers[order-k])
                             /(sp.factorial(k)*sp.factorial(order-k)*d)
                             for k in range(order+1))
                zero(actual-sp.sympify(formula, locals=variables),
                     f"{case['id']} echo Taylor coefficient {order}")
        results.append(dict(id=case['id'],n=n,family=family,exact_even_moments=values))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    record = dict(verifier='analytic-p-theta-v3', timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                  python=platform.python_version(),sympy=sp.__version__,source_hashes=hashes(),seed=None,
                  commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  candidate=str(args.candidate))
    try:
        if json.loads((HERE/'manifest.json').read_text())['source_hashes'] != record['source_hashes']:
            raise AssertionError('frozen verifier hash mismatch')
        content = args.candidate.read_bytes()
        record['candidate_sha256'] = hashlib.sha256(content).hexdigest()
        record['checks'] = check(json.loads(content))
        record.update(status='PASS',decision='KEEP',evidence='PROVED')
    except Exception as error:
        record.update(status='FAIL',decision='REJECT',evidence='OPEN',error=f'{type(error).__name__}: {error}')
    record['elapsed_seconds'] = time.monotonic()-start
    args.log.parent.mkdir(parents=True,exist_ok=True)
    with args.log.open('a') as handle:
        handle.write(json.dumps(record,sort_keys=True)+'\n')
    print(json.dumps(record,indent=2))
    if record['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
