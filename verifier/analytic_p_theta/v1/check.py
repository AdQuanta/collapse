"""Frozen v1 checks. Candidate input is formula data, never imported code.

Run from the repository root with --candidate PATH --log PATH.
Every completed invocation appends its outcome, including identity failures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time

import sympy as sp

from reference import X, hamiltonian, pauli, spins, x_basis

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def require_zero(value, name: str) -> None:
    entries = list(value) if isinstance(value, sp.MatrixBase) else [value]
    if any(sp.simplify(v) != 0 for v in entries):
        raise AssertionError(name)


def verify(data: dict) -> list[str]:
    passed = []
    K, V, t = sp.symbols('K V t', real=True)
    loc = {'K': K, 'V': V, 't': t, 'I': sp.I}
    a, c = [sp.sympify(data[key], locals=loc) for key in ('A', 'C')]
    direct = K * sp.eye(2) + V * X
    for order in range(7):
        proposed = sp.Matrix([sp.diff(a, t, order).subs(t, 0),
                              sp.diff(c, t, order).subs(t, 0)])
        require_zero(proposed - (-sp.I * direct) ** order * sp.Matrix([1, 0]),
                     f'Taylor order {order}')
    passed.append('exact propagator Taylor orders 0..6')
    require_zero(a * sp.conjugate(a) + c * sp.conjugate(c) - 1, 'column normalization')
    require_zero(c.subs(V, 0), 'zero coupling C')
    require_zero(a.subs(V, 0) - sp.exp(-sp.I * K * t), 'zero coupling A')
    require_zero(c.subs(V, -V) + c, 'C sign reflection')
    require_zero(a.subs(V, -V) - a, 'A sign reflection')
    passed.append('exact normalization, sign reflection, zero coupling')
    # The gate is fixed across all commuting coefficient rungs, including NNN
    # and a commuting central field extension. No dense eigensolver is used.
    for family, n in [('chain', 1), ('chain', 2), ('chain', 3), ('ring', 5)]:
        for rung in range(5):
            hx = sp.Rational(2, 7) if rung >= 1 else sp.S.Zero
            jx = sp.Rational(-1, 3) if rung >= 2 else sp.S.Zero
            j2x = sp.Rational(3, 11) if rung >= 3 else sp.S.Zero
            hqx = sp.Rational(1, 5) if rung >= 4 else sp.S.Zero
            gx = sp.Rational(4, 9)
            fields = dict(hq=[hqx, 0, 0], hd=[hx, 0, 0], j1=[jx, 0, 0],
                          j2=[j2x, 0, 0], g=[gx, 0, 0])
            h = hamiltonian(n, family, fields)
            q = sp.kronecker_product(sp.eye(2), x_basis(n))
            transformed = q.T * h * q
            expected = sp.zeros(2 ** (n + 1))
            for index, s in enumerate(spins(n)):
                def bond(distance):
                    return (sum(s[i] * s[(i + distance) % n] for i in range(n))
                            if family == 'ring' else
                            sum(s[i] * s[i + distance] for i in range(n - distance)))
                variables = dict(hx=hx, jx=jx, j2x=j2x, hqx=hqx, gx=gx,
                                 M=sum(s), B1=bond(1), B2=bond(2),
                                 L=sum(s) / sp.sqrt(n) if family == 'ring' else s[0])
                k = sp.sympify(data['K'], locals=variables)
                v = sp.sympify(data['V'], locals=variables)
                d = 2**n
                expected[index, index] = expected[index+d, index+d] = k
                expected[index, index+d] = expected[index+d, index] = v
            require_zero(transformed - expected, f'{family} N={n} rung={rung} reduction')
            passed.append(f'{family} N={n} rung={rung}: all exact X sectors')
    z = sp.symbols('z', nonzero=True)
    for n in range(1, 10):
        candidate = sp.sympify(data['magnetization_laurent'], locals={'z': z, 'N': n})
        reference = sum(sp.binomial(n, k) * z**(n-2*k) for k in range(n+1)) / 2**n
        require_zero(sp.expand(candidate-reference), f'binomial characteristic N={n}')
        require_zero(candidate.subs(z, 1)-1, f'binomial normalization N={n}')
    passed.append('exact binomial characteristic and normalization N=1..9')
    return passed


def exchange_checks() -> list[str]:
    """Independent charge and two-state identities at the singular exchange time."""
    passed = []
    for family, n in [('chain', 1), ('chain', 3), ('ring', 5)]:
        h = hamiltonian(n, family, dict(hq=[0]*3, hd=[0]*3, j1=[0]*3,
                                       j2=[0]*3, g=[1, 1, 0]))
        charge = sum((pauli(n, s, 2) for s in range(n+1)), sp.zeros(h.rows))
        require_zero(h * charge - charge * h, 'exchange charge')
        # Central |0>, all detector spins |1>. H psi=2 phi, H phi=2 psi.
        psi = sp.zeros(h.rows, 1)
        psi[2**n-1] = 1
        phi = h * psi / 2
        require_zero(phi.conjugate().T * phi - sp.eye(1), 'bright norm')
        require_zero(h * phi - 2 * psi, 'bright exchange frequency')
        require_zero(phi[:2**n, :], 'bright central flip')
        passed.append(f'{family} N={n}: exact conserved charge and bright swap frequency 2')
    h = hamiltonian(1, 'chain', dict(hq=[0]*3, hd=[0]*3, j1=[0]*3,
                                    j2=[0]*3, g=[1, 1, 0]))
    u = (-sp.I * sp.pi * h / 4).exp()
    alpha, beta = sp.symbols('alpha beta')
    require_zero((beta*u[2:, :2] - alpha*u[:2, :2]).det(), 'identically singular pencil')
    passed.append('chain N=1: exact exponential at pi/4, identically zero homogeneous determinant')
    return passed


def hashes() -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.glob('*.py'))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    record = dict(verifier='analytic-p-theta-v1', timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  source_hashes=hashes(), candidate=str(args.candidate),
                  python=platform.python_version(), sympy=sp.__version__, seed=None,
                  commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    try:
        manifest = json.loads((HERE/'manifest.json').read_text())
        if record['source_hashes'] != manifest['source_hashes']:
            raise AssertionError('frozen verifier hash mismatch')
        content = args.candidate.read_bytes()
        record['candidate_sha256'] = hashlib.sha256(content).hexdigest()
        record['checks'] = verify(json.loads(content)) + exchange_checks()
        record.update(status='PASS', evidence='PROVED', decision='KEEP')
    except Exception as error:
        record.update(status='FAIL', evidence='OPEN', decision='REJECT',
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
