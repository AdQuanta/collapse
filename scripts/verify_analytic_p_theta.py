"""Reduced production-QZ crosschecks of frozen analytic formula data.

This secondary numerical diagnostic is separate from the frozen independent
SymPy verifier. It never changes production definitions or acceptance gates.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.projective_roots import production_root_spectrum
from core.ring_chain_family import RingChainSpec, build_ring_chain_parts


def expected_angles(spec: RingChainSpec, time_value: float, model: str) -> np.ndarray:
    """Closed-form candidate atoms, expanded by algebraic multiplicity."""
    n = spec.detector_n
    gx = spec.coupling[0]
    signs = np.array([sum(1 if (index >> i) & 1 else -1 for i in range(n))
                      for index in range(2**n)])
    if model == 'commuting':
        values = gx*signs/np.sqrt(n) if spec.topology == 'ring' else gx*np.tile([-1,1],2**(n-1))
        phase = time_value*(spec.qubit_field[0]+values)
    else:
        p, hy, hz = spec.detector_field
        q2 = hy*hy+hz*hz
        epsilon = gx/np.sqrt(n) if spec.topology == 'ring' else gx
        rp, rm = np.sqrt((p+epsilon)**2+q2), np.sqrt((p-epsilon)**2+q2)
        cosine = (np.cos(rp*time_value)*np.cos(rm*time_value)
                  +(p*p+q2-epsilon*epsilon)*time_value**2
                  *np.sinc(rp*time_value/np.pi)*np.sinc(rm*time_value/np.pi))
        phi = np.arccos(np.clip(cosine,-1,1))
        phase = phi*signs/2 if spec.topology == 'ring' else np.full(2**n,phi/2)
    return 2*np.arctan2(np.abs(np.sin(phase)),np.abs(np.cos(phase)))


def run(output: Path) -> dict:
    start=time.monotonic()
    rows=[]
    for family,sizes in [('chain',(1,2,3)),('ring',(5,6,7))]:
        for n in sizes:
            for model,hd,hq,j1,j2 in [
                ('commuting',(.3,0.,0.),(.17,0.,0.),(.2,0.,0.),(-.11,0.,0.)),
                ('independent',(0.,.3,.4),(0.,0.,0.),(0.,0.,0.),(0.,0.,0.)),
                ('independent',(.2,.3,.4),(0.,0.,0.),(0.,0.,0.),(0.,0.,0.)),
            ]:
                spec=RingChainSpec(n,family,hq,hd,j1,j2,(.8,0.,0.))
                h0,v=build_ring_chain_parts(spec)
                for t in (0.,.13,.71,1.33):
                    spectrum=production_root_spectrum(expm(-1j*t*(h0+v)))
                    target=expected_angles(spec,t,model)
                    error=float(np.max(np.abs(np.sort(target)-np.sort(spectrum.theta))))
                    residual=float(spectrum.maximum_homogeneous_residual)
                    valid=bool(not np.any(spectrum.indeterminate) and error<1e-7 and residual<1e-11)
                    rows.append(dict(spec=asdict(spec),time=t,model=model,angle_max_error=error,
                                     homogeneous_residual=residual,indeterminate=int(np.sum(spectrum.indeterminate)),
                                     status='PASS' if valid else 'FAIL'))
    exact_swap=np.array([[1,0,0,0],[0,0,-1j,0],[0,-1j,0,0],[0,0,0,1]],complex)
    singular=production_root_spectrum(exact_swap,assess_regularity=True)
    singular_count=int(np.sum(singular.indeterminate))
    sources=[Path(__file__),ROOT/'core/ring_chain_family.py',ROOT/'core/projective_roots.py',
             ROOT/'core/relative_evolution_pencil.py',ROOT/'core/pauli.py']
    result=dict(schema='analytic-p-theta-production-crosscheck-v1',
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,seed=None,
                source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                tolerances=dict(angle=1e-7,homogeneous_residual=1e-11),
                rows=rows,exact_swap_indeterminate_count=singular_count,
                status='PASS' if all(row['status']=='PASS' for row in rows) and singular_count>0 else 'FAIL',
                evidence='VERIFIED_NUMERICALLY',elapsed_seconds=time.monotonic()-start)
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():
        raise FileExistsError('Preserve existing evidence; choose a new output path')
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=run(args.output)
    print(json.dumps(dict(status=result['status'],conditions=len(result['rows']),
                          max_angle_error=max(r['angle_max_error'] for r in result['rows']),
                          max_residual=max(r['homogeneous_residual'] for r in result['rows']),
                          exact_swap_indeterminate_count=result['exact_swap_indeterminate_count']),indent=2))
    if result['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
