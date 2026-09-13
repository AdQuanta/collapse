"""Reduced diagnostic of general-chain second-echo-moment frequency weights.

This does not approximate an infinite-time or thermodynamic probability law.
It probes a proposed sufficient bound, retaining all permutation resonances.
Frequency coalescing tolerances are reported separately, never fitted.
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
sys.path.insert(0, str(ROOT))
from core.projective_roots import production_root_spectrum
from core.ring_chain_family import RingChainSpec, build_ring_chain_parts


def weights(plus: np.ndarray, minus: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Aggregate exact index permutations before any frequency clustering."""
    ep, vp = eigh(plus)
    em, vm = eigh(minus)
    overlap = vm.conj().T @ vp
    d = len(ep)
    j, l = np.triu_indices(d)
    mult = np.where(j == l, 1, 2)
    frequencies, coefficients = [], []
    for i in range(d):
        for k in range(i, d):
            quartet = (overlap[i, j]*overlap[k, j].conj()
                       *overlap[k, l]*overlap[i, l].conj())
            coefficients.append((1 if i == k else 2)*mult*quartet.real/d)
            # K convention: transform exp(-it omega).
            frequencies.append(ep[j]+ep[l]-em[i]-em[k])
    residual = max(np.linalg.norm(plus@vp-vp*ep, ord=2),
                   np.linalg.norm(minus@vm-vm*em, ord=2))
    return np.concatenate(frequencies), np.concatenate(coefficients), float(residual)


def coalesced_variation(omega: np.ndarray, coefficient: np.ndarray, tolerance: float) -> dict:
    order = np.argsort(omega)
    freq, coeff = omega[order], coefficient[order]
    starts = np.r_[0, np.flatnonzero(np.diff(freq) > tolerance)+1]
    sums = np.add.reduceat(coeff, starts)
    ends = np.r_[starts[1:]-1, len(freq)-1]
    return dict(tolerance=tolerance, total_variation=float(np.sum(np.abs(sums))),
                groups=len(starts), maximum_cluster_span=float(np.max(freq[ends]-freq[starts])))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Preserve existing evidence; choose a new output path')
    started = time.monotonic()
    rows = []
    models = dict(general=((1/2, 2/5, 3/7), (2/7, -1/3, 1/5), (-2/5, 1/7, 2/9)),
                  commuting=((1/2, 0., 0.), (2/7, 0., 0.), (-2/5, 0., 0.)))
    for label, (hd, j1, j2) in models.items():
        for n in (2, 3, 4, 5):
            a, g = 1/7, 2/3
            spec = RingChainSpec(n, 'chain', (a, 0., 0.), hd, j1, j2, (g, 0., 0.))
            h0, v = build_ring_chain_parts(spec)
            d = 2**n
            detector, coupling = h0[:d, :d], v[:d, d:]
            plus = detector+coupling+a*np.eye(d)
            minus = detector-coupling-a*np.eye(d)
            omega, coefficient, residual = weights(plus, minus)
            checks = []
            for t in (.13, .71, 1.33):
                spectrum = production_root_spectrum(expm(-1j*t*(h0+v)))
                predicted = float(np.real(np.sum(coefficient*np.exp(-1j*t*omega))))
                observed = float(np.mean(np.cos(2*spectrum.theta)))
                error = abs(predicted-observed)
                valid = not np.any(spectrum.indeterminate)
                checks.append(dict(time=t, spectral_moment=predicted, qz_moment=observed,
                                   error=error, homogeneous_residual=float(spectrum.maximum_homogeneous_residual),
                                   indeterminate=int(np.sum(spectrum.indeterminate)),
                                   status='PASS' if valid and error<1e-8 and
                                   spectrum.maximum_homogeneous_residual<1e-11 else 'FAIL'))
            grouped = [coalesced_variation(omega, coefficient, tol) for tol in (1e-12, 1e-10, 1e-8)]
            mass_error = float(abs(np.sum(coefficient)-1))
            row = dict(model=label, spec=asdict(spec), dimension=d, spectral_terms=len(coefficient),
                       eigensolver_residual=residual, total_mass_error=mass_error,
                       permutation_grouped_variation=float(np.sum(np.abs(coefficient))),
                       coalesced=grouped, checks=checks,
                       status='PASS' if mass_error<1e-10 and all(c['status']=='PASS' for c in checks) else 'FAIL')
            if label == 'commuting':
                row['control_variation_error'] = abs(grouped[1]['total_variation']-1)
                if row['control_variation_error'] >= 1e-10:
                    row['status'] = 'FAIL'
            rows.append(row)
    paths = [Path(__file__), ROOT/'core/ring_chain_family.py', ROOT/'core/projective_roots.py',
             ROOT/'core/relative_evolution_pencil.py', ROOT/'core/pauli.py']
    result = dict(schema='endpoint-replica-weights-v1',
                  timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  source_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, seed=None,
                  evidence='PRELIMINARY_NUMERIC',
                  limitation='Finite-size frequency diagnostic; no infinite-volume total-variation or Cesaro claim',
                  tolerances=dict(moment=1e-8, homogeneous_residual=1e-11, mass=1e-10,
                                  frequency_coalescing=[1e-12, 1e-10, 1e-8]),
                  rows=rows, elapsed_seconds=time.monotonic()-started,
                  status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], rows=[dict(model=r['model'], n=r['spec']['detector_n'],
          variation=r['coalesced'][1]['total_variation']) for r in rows]), indent=2))
    if result['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
