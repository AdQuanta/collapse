"""Independent v2 extension for the noninteracting detector-field rung.

v1 remains frozen and is not redefined. This new series checks supplied
formula data against direct Pauli products and exact differentiation.
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
from reference import X, Z, hamiltonian, x_basis
from check import require_zero


def source_hashes() -> dict:
    paths = [HERE/'check.py', HERE.parent/'v1'/'reference.py', HERE.parent/'v1'/'check.py']
    return {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def verify(data: dict) -> list[str]:
    passed = []
    p, q, e, t = sp.symbols('p q e t', real=True)
    # q>0 avoids absolute-value branches in derivatives at e=0. The resulting
    # identity is continuous in q, with the h=0 case treated separately.
    q = sp.symbols('q', positive=True)
    rp, rm = sp.sqrt((p+e)**2+q*q), sp.sqrt((p-e)**2+q*q)
    loc = dict(p=p, q=q, e=e, t=t, rp=rp, rm=rm)
    proposed = sp.sympify(data['cos_phi'], locals=loc)
    up = sp.cos(rp*t)*sp.eye(2)-sp.I*sp.sin(rp*t)/rp*((p+e)*X+q*Z)
    um_dagger = sp.cos(rm*t)*sp.eye(2)+sp.I*sp.sin(rm*t)/rm*((p-e)*X+q*Z)
    require_zero(sp.trace(um_dagger*up)/2-proposed, 'local relative SU2 trace')
    passed.append('exact relative-unitary trace with parallel and transverse field')
    require_zero(proposed.subs(e,0)-1, 'zero-coupling relative unitary')
    require_zero(proposed.subs(e,-e)-proposed, 'coupling sign symmetry')
    b2 = sp.sympify(data['B_squared'], locals=loc)
    require_zero(sp.diff(proposed,e,2).subs(e,0)+4*b2, 'fixed-time second derivative')
    passed.append('exact epsilon^2 coefficient controlling thermodynamic limit')
    k = sp.symbols('k', positive=True)
    theta = sp.symbols('theta', real=True)
    dens = sp.sympify(data['chain_density'], locals=dict(k=k,theta=theta))
    z = sp.sin(theta/2)**2
    # Within 0<theta<2 asin(sqrt(k)), the Jacobian is positive.
    jacobian = sp.sin(theta/2)*sp.cos(theta/2)
    expected = jacobian/(sp.pi*sp.sin(theta/2)*sp.sqrt(k-z))
    require_zero(dens-expected, 'arcsine pushforward Jacobian')
    passed.append('exact chain time-average density Jacobian')
    for family,n in [('chain',1),('chain',3),('ring',5)]:
        for hd in ([0,0,sp.Rational(3,5)], [sp.Rational(1,3),0,sp.Rational(3,5)]):
            fields=dict(hq=[0]*3,hd=hd,j1=[0]*3,j2=[0]*3,g=[sp.Rational(4,7),0,0])
            h=hamiltonian(n,family,fields)
            change=sp.kronecker_product(x_basis(1),sp.eye(2**n))
            transformed=change.T*h*change
            require_zero(transformed[:2**n,2**n:], 'conserved central X sectors')
            plus,minus=transformed[:2**n,:2**n],transformed[2**n:,2**n:]
            # Detector terms act on distinct tensor factors; construct the
            # proposed product-generator independently of the full builder.
            for sign,block in [(1,plus),(-1,minus)]:
                expected=sp.zeros(2**n)
                for site in range(n):
                    coupling=sp.Rational(4,7)/(sp.sqrt(n) if family=='ring' else 1)
                    if family=='chain' and site!=0:
                        coupling=0
                    one=(hd[0]+sign*coupling)*X+hd[2]*Z
                    factors=[sp.eye(2)]*n
                    factors[site]=one
                    from functools import reduce
                    expected+=reduce(sp.kronecker_product,factors)
                require_zero(block-expected, 'conditional product-generator identity')
            passed.append(f'{family} N={n}, h={hd}: exact conditional product generators')
    for ep,hz in [(sp.Rational(2,3),sp.Rational(3,5)), (0,sp.Rational(3,5)), (sp.Rational(2,3),0)]:
        if hz==0:
            # evaluate positive e before substitution to avoid artificial 0/0
            expr=proposed.subs({p:0,q:0,e:ep})
        else:
            expr=proposed.subs({p:0,q:hz,e:ep})
        omega=sp.sqrt(ep*ep+hz*hz)
        target=1-2*ep*ep/omega**2*sp.sin(omega*t)**2
        require_zero(sp.trigsimp(expr-target), 'transverse and zero-coefficient reductions')
    passed.append('exact transverse trace, zero-coupling and zero-field limits')
    return passed


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--log',type=Path,required=True)
    args=parser.parse_args()
    start=time.monotonic()
    record=dict(verifier='analytic-p-theta-v2',timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                source_hashes=source_hashes(),python=platform.python_version(),sympy=sp.__version__,seed=None,
                candidate=str(args.candidate),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    try:
        if json.loads((HERE/'manifest.json').read_text())['source_hashes']!=record['source_hashes']:
            raise AssertionError('frozen verifier hash mismatch')
        content=args.candidate.read_bytes()
        record['candidate_sha256']=hashlib.sha256(content).hexdigest()
        record['checks']=verify(json.loads(content))
        record.update(status='PASS',evidence='PROVED',decision='KEEP')
    except Exception as error:
        record.update(status='FAIL',evidence='OPEN',decision='REJECT',error=f'{type(error).__name__}: {error}')
    record['elapsed_seconds']=time.monotonic()-start
    args.log.parent.mkdir(parents=True,exist_ok=True)
    with args.log.open('a') as handle:
        handle.write(json.dumps(record,sort_keys=True)+'\n')
    print(json.dumps(record,indent=2))
    if record['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
