"""Reduced production-QZ check of the interacting endpoint conditional unitary."""
from __future__ import annotations

from dataclasses import asdict
import argparse
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

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.projective_roots import production_root_spectrum
from core.ring_chain_family import RingChainSpec,build_ring_chain_parts


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Preserve existing evidence; choose a new output')
    started=time.monotonic()
    rows=[]
    for n in (2,3,4):
        spec=RingChainSpec(n,'chain',(.17,0.,0.),(.2,.3,.4),(.3,-.1,.2),(.1,.08,-.06),(.8,0.,0.))
        h0,v=build_ring_chain_parts(spec)
        d=2**n
        detector=h0[:d,:d]
        local=v[:d,d:]
        for t in (.13,.71,1.33):
            s=production_root_spectrum(expm(-1j*t*(h0+v)))
            w=np.exp(-2j*.17*t)*expm(1j*t*(detector-local))@expm(-1j*t*(detector+local))
            eigenvalues=np.linalg.eigvals(w)
            angles=2*np.arctan2(np.abs(eigenvalues-1),np.abs(eigenvalues+1))
            error=float(np.max(np.abs(np.sort(angles)-np.sort(s.theta))))
            residual=float(s.maximum_homogeneous_residual)
            passed=bool(not np.any(s.indeterminate) and error<1e-8 and residual<1e-11)
            rows.append(dict(spec=asdict(spec),time=t,angle_max_error=error,homogeneous_residual=residual,
                             status='PASS' if passed else 'FAIL',indeterminate=int(np.sum(s.indeterminate)),
                             cosine_moments=[float(np.mean(np.cos(ell*s.theta))) for ell in range(1,7)]))
    paths=[Path(__file__),ROOT/'core/ring_chain_family.py',ROOT/'core/projective_roots.py',
           ROOT/'core/relative_evolution_pencil.py',ROOT/'core/pauli.py']
    result=dict(schema='analytic-chain-norm-limit-crosscheck-v1',
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
                source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,seed=None,
                tolerances=dict(angle=1e-8,homogeneous_residual=1e-11),rows=rows,
                evidence='VERIFIED_NUMERICALLY',status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',
                elapsed_seconds=time.monotonic()-started)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],conditions=len(rows),max_angle_error=max(r['angle_max_error'] for r in rows)),indent=2))
    if result['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
