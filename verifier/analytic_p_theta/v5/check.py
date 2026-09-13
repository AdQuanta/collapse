"""Frozen exact checker for general endpoint echo/replica formula data."""
from __future__ import annotations

import argparse
import hashlib
from itertools import product
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
    paths = (HERE / 'check.py', HERE.parent / 'v1/reference.py')
    return {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}


def zero(value, label: str) -> None:
    residual = sp.simplify(value)
    if residual != 0:
        raise AssertionError(f'{label}: {residual}')


def matrix_zero(value, label: str) -> None:
    for item in value:
        zero(item, label)


def cycle(d: int, ell: int) -> sp.ImmutableSparseMatrix:
    entries = {}
    for indices in product(range(d), repeat=ell):
        shifted = indices[1:] + indices[:1]
        col = sum(v*d**(ell-1-j) for j, v in enumerate(indices))
        row = sum(v*d**(ell-1-j) for j, v in enumerate(shifted))
        entries[row, col] = 1
    return sp.ImmutableSparseMatrix(d**ell, d**ell, entries)


def series_product(left: list, right: list, degree: int) -> list:
    d = left[0].rows
    return [sp.ImmutableSparseMatrix(sum(
        (left[k]*right[q-k] for k in range(q+1)), sp.zeros(d)))
        for q in range(degree+1)]


def check(data: dict) -> list[dict]:
    if data['schema'] != 'endpoint-replica-v1':
        raise AssertionError('candidate schema')
    results = []
    a, g = sp.Rational(1, 7), sp.Rational(2, 3)
    fields = dict(hq=[0, 0, 0], g=[0, 0, 0],
                  hd=[sp.Rational(1, 2), sp.Rational(2, 5), sp.Rational(3, 7)],
                  j1=[sp.Rational(2, 7), sp.Rational(-1, 3), sp.Rational(1, 5)],
                  j2=[sp.Rational(-2, 5), sp.Rational(1, 7), sp.Rational(2, 9)])
    degree = 4
    for n in (1, 2, 3):
        d = 2**n
        detector = sp.ImmutableSparseMatrix(hamiltonian(n, 'chain', fields)[:d, :d])
        x = sp.ImmutableSparseMatrix(pauli(n, 1, 0)[:d, :d])
        plus = detector + g*x + a*sp.eye(d)
        minus = detector - g*x - a*sp.eye(d)
        pp, mm = [sp.eye(d)], [sp.eye(d)]
        for k in range(1, degree+1):
            pp.append(sp.ImmutableSparseMatrix(pp[-1]*plus))
            mm.append(sp.ImmutableSparseMatrix(mm[-1]*minus))
        direct = series_product(
            [(-sp.I)**k*pp[k]/sp.factorial(k) for k in range(degree+1)],
            [sp.I**k*mm[k]/sp.factorial(k) for k in range(degree+1)], degree)
        current = sp.eye(d)
        proposed = []
        moments = []
        for k in range(degree+1):
            proposed.append(sp.ImmutableSparseMatrix((-sp.I)**k*current/sp.factorial(k)))
            matrix_zero(proposed[-1]-direct[k], f'N={n} generator order {k}')
            moments.append(sp.simplify(sp.trace(current)/d))
            current = sp.ImmutableSparseMatrix(
                data['left_sign']*plus*current + data['right_sign']*current*minus)
        mu2 = sp.trace((detector*x-x*detector).H*(detector*x-x*detector))/d
        symbols = dict(a=a, g=g, mu2=mu2)
        for k, formula in enumerate(data['first_spectral_moments']):
            zero(moments[k]-sp.sympify(formula, locals=symbols), f'N={n} spectral moment {k}')
        # Direct matrix powers and tensor Taylor contractions are independent
        # constructions. The tensor is never imported from candidate code.
        power_series = [sp.eye(d)] + [sp.zeros(d) for _ in range(degree)]
        for ell in (1, 2, 3):
            power_series = series_product(power_series, direct, degree)
            p = cycle(d, ell)
            factor = sp.sympify(data['replica_factor'], locals=dict(d=sp.Integer(d), ell=ell))
            for q in range(degree+1):
                contraction = sp.S.Zero
                for orders in product(range(q+1), repeat=ell):
                    if sum(orders) == q:
                        for indices in product(range(d), repeat=ell):
                            contraction += sp.prod(proposed[orders[j]][indices[j], indices[(j+1)%ell]]
                                                   for j in range(ell))
                actual = factor*contraction/d**ell
                zero(actual-sp.trace(power_series[q])/d,
                     f'N={n} ell={ell} replica derivative {q}')
            zero(sp.trace(p.H*p)/d**ell-1, f'N={n} ell={ell} cycle norm')
            predicted_norm2 = sp.sympify(data['functional_norm_squared'],
                                        locals=dict(d=sp.Integer(d), ell=ell))
            zero(factor**2-predicted_norm2, f'N={n} ell={ell} functional norm')
        results.append(dict(n=n, derivative_order=degree, root_moments=[1, 2, 3],
                            first_spectral_moments=[str(v) for v in moments]))
    # Exact lower-coefficient limits, without changing the main case list.
    z = sp.diag(1, -1)
    x = sp.Matrix([[0, 1], [1, 0]])
    for coupling, detector in ((0, z), (g, sp.Rational(3, 5)*x)):
        current = sp.eye(2)
        plus, minus = detector+coupling*x, detector-coupling*x
        for k in range(5):
            matrix_zero(current-(2*coupling*x)**k, 'commuting/zero limit')
            current = data['left_sign']*plus*current + data['right_sign']*current*minus
    # The allowed N=1 g=h_z=1 control has r(t)=cos(sqrt(2)t)^2.
    u = sp.symbols('u', real=True)
    c, s = sp.cos(u), sp.sin(u)
    plus = c*sp.eye(2)-sp.I*s*(z+x)/sp.sqrt(2)
    minus = c*sp.eye(2)-sp.I*s*(z-x)/sp.sqrt(2)
    w = minus.H*plus
    for ell, target in enumerate(data['control_time_means'], 1):
        mean = sp.integrate(sp.expand_trig(sp.trace(w**ell)/2), (u, 0, sp.pi))/sp.pi
        zero(mean-sp.sympify(target), f'single pixel mean ell={ell}')
    results.append(dict(controls='zero coupling, commuting detector, signed higher moment',
                        means=data['control_time_means']))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    record = dict(verifier='analytic-p-theta-v5',
                  timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  python=platform.python_version(), sympy=sp.__version__, source_hashes=hashes(),
                  seed=None, commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                  cwd=ROOT, text=True).strip(), candidate=str(args.candidate))
    try:
        if json.loads((HERE/'manifest.json').read_text())['source_hashes'] != record['source_hashes']:
            raise AssertionError('frozen verifier hash mismatch')
        content = args.candidate.read_bytes()
        record['candidate_sha256'] = hashlib.sha256(content).hexdigest()
        record['checks'] = check(json.loads(content))
        record.update(status='PASS', decision='KEEP', evidence='PROVED')
    except Exception as error:
        record.update(status='FAIL', decision='REJECT', evidence='OPEN',
                      error=f'{type(error).__name__}: {error}')
    record['elapsed_seconds'] = time.monotonic()-start
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open('a') as handle:
        handle.write(json.dumps(record, sort_keys=True)+'\n')
    print(json.dumps(record, indent=2))
    if record['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
