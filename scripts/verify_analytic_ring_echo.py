"""Reduced QZ and finite-size diagnostics for the interacting central-X echo.

Exact unitary reduction is checked against production QZ. Finite-size errors
against the limiting Gaussian are reported without a fitted acceptance gate.
No verifier or candidate Pauli-recurrence implementation is imported.
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
from scipy.linalg import eigh, expm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.projective_roots import production_root_spectrum
from core.ring_chain_family import RingChainSpec, build_ring_chain_parts


def normalized_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix,'fro')/np.sqrt(matrix.shape[0]))


def run(output: Path) -> dict:
    if output.exists():
        raise FileExistsError('Choose a new output path; previous evidence is immutable')
    start=time.monotonic()
    rows=[]
    for n in (5,6,7):
        for name,field,j1,j2 in [
            ('transverse_ising',(0.,0.,.6),(.4,0.,0.),(0.,0.,0.)),
            ('full_nn',(.2,.3,.4),(.3,-.1,.2),(0.,0.,0.)),
            ('full_nnn',(.2,.3,.4),(.3,-.1,.2),(.1,.08,-.06)),
        ]:
            a,g=.17,.8
            spec=RingChainSpec(n,'ring',(a,0.,0.),field,j1,j2,(g,0.,0.))
            h0,v=build_ring_chain_parts(spec)
            d=2**n
            detector=h0[:d,:d]
            fluctuation=v[:d,d:]/g
            energies,basis=eigh(detector)
            transformed=basis.conj().T@fluctuation@basis
            delta=energies[:,None]-energies[None,:]
            for t in (.13,.71,1.33):
                spectrum=production_root_spectrum(expm(-1j*t*(h0+v)))
                plus=expm(-1j*t*(detector+g*fluctuation))
                minus=expm(-1j*t*(detector-g*fluctuation))
                echo=np.exp(-2j*a*t)*(minus.conj().T@plus)
                values=np.linalg.eigvals(echo)
                angles=2*np.arctan2(np.abs(values-1),np.abs(values+1))
                angle_error=float(np.max(np.abs(np.sort(angles)-np.sort(spectrum.theta))))
                kernel=t*np.exp(.5j*t*delta)*np.sinc(t*delta/(2*np.pi))
                integrated=basis@(transformed*kernel)@basis.conj().T
                integrated=(integrated+integrated.conj().T)/2
                evolved=basis@(transformed*np.exp(1j*t*delta))@basis.conj().T
                variance=normalized_norm(integrated)**2
                gaussian_unitary=np.exp(-2j*a*t)*expm(-2j*g*integrated)
                echo_error=normalized_norm(echo-gaussian_unitary)
                commutator=normalized_norm(fluctuation@evolved-evolved@fluctuation)
                exact_moments=[float(np.mean(np.cos(ell*spectrum.theta))) for ell in range(1,7)]
                moment_target=[float(np.cos(2*ell*a*t)*np.exp(-2*ell**2*g*g*variance)) for ell in range(1,7)]
                residual=float(spectrum.maximum_homogeneous_residual)
                valid=bool(not np.any(spectrum.indeterminate) and angle_error<1e-8 and residual<1e-11)
                rows.append(dict(spec=asdict(spec),model=name,time=t,status='PASS' if valid else 'FAIL',
                                 qz_angle_max_error=angle_error,qz_homogeneous_residual=residual,
                                 indeterminate=int(np.sum(spectrum.indeterminate)),
                                 integrated_variance=variance,echo_integrated_field_error=echo_error,
                                 scaled_echo_error=np.sqrt(n)*echo_error,
                                 fluctuation_commutator_norm=commutator,
                                 scaled_commutator_norm=np.sqrt(n)*commutator,
                                 exact_root_cosine_moments=exact_moments,
                                 gaussian_finite_variance_moments=moment_target,
                                 gaussian_moment_max_error=max(abs(x-y) for x,y in zip(exact_moments,moment_target))))
    files=[Path(__file__),ROOT/'core/ring_chain_family.py',ROOT/'core/projective_roots.py',
           ROOT/'core/relative_evolution_pencil.py',ROOT/'core/pauli.py']
    result=dict(schema='analytic-ring-echo-crosscheck-v1',
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,seed=None,
                source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                exact_reduction_tolerances=dict(angle=1e-8,homogeneous_residual=1e-11),
                approximation_gate=None,rows=rows,status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',
                evidence='VERIFIED_NUMERICALLY',elapsed_seconds=time.monotonic()-start)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=run(args.output)
    print(json.dumps(dict(status=result['status'],conditions=len(result['rows']),
                          max_qz_angle_error=max(r['qz_angle_max_error'] for r in result['rows']),
                          max_qz_residual=max(r['qz_homogeneous_residual'] for r in result['rows'])),indent=2))
    if result['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
