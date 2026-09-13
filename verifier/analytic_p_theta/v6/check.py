"""Frozen scalar modulation/exception checks; not an a.e. convergence proof."""
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
sys.path.insert(0, str(HERE.parent/'v1'))
from reference import X, Z


def hashes() -> dict:
    return {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (HERE/'check.py', HERE.parent/'v1/reference.py')}


def zero(value, label: str) -> None:
    residual = sp.simplify(value)
    if residual != 0:
        raise AssertionError(f'{label}: {residual}')


def check(data: dict) -> list[str]:
    if data['schema'] != 'central-field-modulation-v1':
        raise AssertionError('schema')
    a, t, u, z = sp.symbols('a t u z', real=True)
    T, ell, n = sp.symbols('T ell n', positive=True)
    variables = dict(a=a, t=t, u=u, z=z, T=T, ell=ell, n=n, I=sp.I, pi=sp.pi)
    parse = lambda expression: sp.sympify(expression, locals=variables)
    up = sp.cos(u)*sp.eye(2)-sp.I*sp.sin(u)*(Z+X)/sp.sqrt(2)
    um = sp.cos(u)*sp.eye(2)-sp.I*sp.sin(u)*(Z-X)/sp.sqrt(2)
    w = um.H*up
    shifted = (sp.exp(sp.I*a*t)*um).H*(sp.exp(-sp.I*a*t)*up)
    candidate = sp.exp(-sp.I*parse(data['phase_factor'])*a*t)*w
    for entry in shifted-candidate:
        zero(entry, 'conditional sector modulation')
    window = parse(data['window'])
    zero(sp.diff(T*window, T)-sp.exp(-sp.I*z*T), 'Fourier window derivative')
    zero(sp.limit(T*window, T, 0), 'Fourier window lower endpoint')
    zero(sp.limit(window, z, 0)-1, 'zero-frequency window')
    zero(parse(data['field_plancherel_factor'])-2*sp.pi/(2*ell), 'field-frequency Jacobian')
    interpolation = parse(data['square_time_interpolation'])
    zero(interpolation-2*((n+1)**2-n**2)/n**2, 'square-time bound')
    zero(sp.limit(interpolation, n, sp.oo), 'all-time interpolation limit')
    zero(sp.summation(1/n**2, (n, 1, sp.oo))-sp.pi**2/6, 'summable-time sequence')
    # At a=sqrt(2)/2 and u=sqrt(2)t, the central phase is exp(-iu).
    for harmonic, target in enumerate(data['nonzero_resonant_means'], 1):
        integrand = sp.expand_trig(sp.re(sp.exp(-sp.I*harmonic*u)*sp.trace(w**harmonic)/2))
        actual = sp.integrate(integrand, (u, 0, 2*sp.pi))/(2*sp.pi)
        zero(actual-parse(target), f'nonzero resonance harmonic {harmonic}')
    for harmonic, target in enumerate(data['commuting_resonant_means'], 1):
        actual = sp.integrate((1+sp.cos(harmonic*u))/2, (u, 0, 2*sp.pi))/(2*sp.pi)
        zero(actual-parse(target), f'commuting resonance harmonic {harmonic}')
    return ['scalar sector modulation', 'Fourier window and zero frequency',
            'Plancherel Jacobian', 'summable times and interpolation',
            'nonzero resonance: b1=0,b2=1/2', 'commuting resonance: harmonics 1–4']


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    record = dict(verifier='analytic-p-theta-v6', timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                  python=platform.python_version(), sympy=sp.__version__, seed=None, source_hashes=hashes(),
                  commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  candidate=str(args.candidate))
    try:
        if json.loads((HERE/'manifest.json').read_text())['source_hashes'] != record['source_hashes']:
            raise AssertionError('frozen source hash mismatch')
        content = args.candidate.read_bytes()
        record['candidate_sha256'] = hashlib.sha256(content).hexdigest()
        record['checks'] = check(json.loads(content))
        record.update(status='PASS', decision='KEEP', evidence='PROVED')
    except Exception as error:
        record.update(status='FAIL', decision='REJECT', evidence='OPEN', error=f'{type(error).__name__}: {error}')
    record['elapsed_seconds'] = time.monotonic()-started
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open('a') as handle:
        handle.write(json.dumps(record,sort_keys=True)+'\n')
    print(json.dumps(record,indent=2))
    if record['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
