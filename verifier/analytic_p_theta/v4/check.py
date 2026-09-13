"""Frozen independent Clifford/Pauli checks for the endpoint benchmark.

Candidate formulas are data; no candidate implementation is imported.
The Hamiltonian cases and Taylor orders below are fixed independently.
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

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'v1'))
from reference import hamiltonian,pauli


def hashes():
    paths=[HERE/'check.py',HERE.parent/'v1/reference.py']
    return {str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def zero(value,label):
    entries=list(value) if isinstance(value,sp.MatrixBase) else [value]
    if any(sp.simplify(v)!=0 for v in entries):
        raise AssertionError(label)


def verify(candidate):
    factor=sp.sympify(candidate['upper_generator_factor'])
    passed=[]
    for n in (1,2,3):
        for g,h,j in [(sp.Rational(2,3),sp.Rational(3,5),sp.Rational(4,7)),
                      (0,1,sp.Rational(1,2)),(1,0,sp.Rational(1,2)),(1,1,0)]:
            hamilton=hamiltonian(n,'chain',dict(hq=[0]*3,hd=[0,0,h],j1=[j,0,0],j2=[0]*3,g=[g,0,0]))
            dimension=hamilton.rows
            gammas=[]
            prefix=sp.eye(dimension)
            for site in range(n+1):
                gammas.extend([prefix*pauli(n,site,0),prefix*pauli(n,site,1)])
                prefix=prefix*pauli(n,site,2)
            generator=sp.zeros(2*n+2)
            links=[g]+[h if i%2==0 else j for i in range(2*n-1)]
            for index,coupling in enumerate(links,1):
                generator[index,index+1]=factor*coupling
                generator[index+1,index]=-factor*coupling
            for index,gamma in enumerate(gammas):
                expected=sum((generator[index,k]*gammas[k] for k in range(len(gammas))),sp.zeros(dimension))
                zero(sp.I*(hamilton*gamma-gamma*hamilton)-expected,'Majorana generator')
            z=pauli(n,0,2)
            derivative=z
            for order in range(7):
                expected=2*(generator**order)[1,1]*sp.eye(dimension)
                zero(z*derivative+derivative*z-expected,'root anticommutator Taylor identity')
                derivative=sp.I*(hamilton*derivative-derivative*hamilton)
            passed.append(f'N={n},g={g},h={h},J={j}: generator and root identity orders 0..6')
    # Exact falsifier of average(W^2)=average(W)^2 at N=1, h=g=1.
    x=sp.Matrix([[0,1],[1,0]])
    z=sp.diag(1,-1)
    u=sp.symbols('u',real=True)
    plus=sp.cos(u)*sp.eye(2)-sp.I*sp.sin(u)*(z+x)/sp.sqrt(2)
    minus=sp.cos(u)*sp.eye(2)-sp.I*sp.sin(u)*(z-x)/sp.sqrt(2)
    w=minus.conjugate().T*plus
    averaged=w.applyfunc(lambda v:sp.integrate(sp.expand_trig(v),(u,0,sp.pi))/sp.pi)
    b1=sp.integrate(sp.expand_trig(sp.trace(w)/2),(u,0,sp.pi))/sp.pi
    b2=sp.integrate(sp.expand_trig(sp.trace(w*w)/2),(u,0,sp.pi))/sp.pi
    zero(b1-sp.sympify(candidate['single_pixel_b1']),'single-pixel first Cesaro moment')
    zero(b2-sp.sympify(candidate['single_pixel_b2']),'single-pixel second Cesaro moment')
    zero(sp.trace(averaged*averaged)/2,'incorrect averaged-operator prediction is zero')
    passed.append('N=1 exact Cesaro counterexample: b1=1/2, b2=-1/4, trace(mean W)^2/2=0')
    A,B,C,z,f=sp.symbols('A B C z f',nonzero=True)
    quadratic=z*C*f*f-(z*z+C-B)*f+z
    E2=sp.sympify(candidate['bound_energy_squared'],locals=dict(A=A,B=B,C=C))
    weight=sp.sympify(candidate['bound_weight_each'],locals=dict(A=A,B=B,C=C))
    zero((quadratic.subs(f,z/A)/z).subs(z*z,E2),'bound pole equation')
    fprime=-sp.diff(quadratic,z)/sp.diff(quadratic,f)
    residue=(1/(1-A*fprime)).subs(f,z/A)
    zero(sp.factor(residue.subs(z*z,E2)-weight),'bound pole residue')
    passed.append('exact nonzero pole equation and derivative residue identity')
    return passed


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--log',type=Path,required=True)
    args=parser.parse_args()
    started=time.monotonic()
    record=dict(verifier='analytic-p-theta-v4',timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                source_hashes=hashes(),python=platform.python_version(),sympy=sp.__version__,seed=None,
                candidate=str(args.candidate))
    try:
        if record['source_hashes']!=json.loads((HERE/'manifest.json').read_text())['source_hashes']:
            raise AssertionError('frozen verifier hash mismatch')
        content=args.candidate.read_bytes()
        record['candidate_sha256']=hashlib.sha256(content).hexdigest()
        record['checks']=verify(json.loads(content))
        record.update(status='PASS',evidence='PROVED',decision='KEEP')
    except Exception as error:
        record.update(status='FAIL',evidence='OPEN',decision='REJECT',error=f'{type(error).__name__}: {error}')
    record['elapsed_seconds']=time.monotonic()-started
    args.log.parent.mkdir(parents=True,exist_ok=True)
    with args.log.open('a') as handle:handle.write(json.dumps(record,sort_keys=True)+'\n')
    print(json.dumps(record,indent=2))
    if record['status']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()
