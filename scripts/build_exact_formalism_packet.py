"""Build fresh state-level evidence and illustrative theta plots; never certify a gate."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import block_diag

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.projective_roots import (
    append_uncoupled_spectator, direct_sum_detector_contexts,
    forward_pole_root_spectrum, reconstruct_collapse_state,
)

BINS = 18  # Predeclared visualization choice, not an acceptance gate.


def qr_unitary(dimension, seed):
    rng = np.random.default_rng(seed)
    q, r = np.linalg.qr(rng.normal(size=(dimension, dimension)) +
                        1j*rng.normal(size=(dimension, dimension)))
    return q * (np.diag(r)/np.abs(np.diag(r)))


def inverse_sqrt(matrix):
    values, vectors = np.linalg.eigh(matrix)
    return (vectors/np.sqrt(values)) @ vectors.conj().T


def fixtures():
    cases, plots = {}, {}
    def add(name, states, kind, coordinates=None):
        cases[name] = states
        # coordinates: [(outcome, alpha, beta, kernel weight)]. Only analytically
        # known fixture measures receive kernel weights; samples get unit weights.
        plots[name] = dict(kind=kind, coordinates=(coordinates if coordinates is not None else
                           [(b, a, c, 1) for U, b, a, c, d in states]))

    identity = np.eye(6, dtype=complex)
    qnd = block_diag(np.diag(np.exp(1j*np.array([.2, -.7, 1.1]))),
                     np.diag(np.exp(1j*np.array([-.1, .8, 1.7]))))
    for name, U in [('identity', identity), ('qnd', qnd)]:
        ds = list(np.eye(3)) + [np.array([1, 2j, -3])]
        add(name, [(U, b, b, 1-b, d) for b in (0, 1) for d in ds],
            'Analytic pole measure (kernel weights)', [(0, 0, 1, 3), (1, 1, 0, 3)])

    U = qr_unitary(8, 20260919)
    generic = []
    for b in (0, 1):
        spectrum = forward_pole_root_spectrum(U, b)
        if np.any(spectrum.indeterminate):
            raise ValueError('generic fixture unexpectedly has indeterminate coordinates')
        for i, (alpha, beta) in enumerate(zip(spectrum.alpha, spectrum.beta)):
            generic.append((U, b, alpha, beta, spectrum.right_eigenvectors[:, i]))
    add('generic', generic, 'Regular simple-root fixture; both pencils solved')

    angles = [.2, .2, 1.0]
    rotations = [np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]) for t in angles]
    U = direct_sum_detector_contexts(rotations)
    semisimple, coordinates = [], []
    for b in (0, 1):
        for i, t in enumerate(angles):
            a, c = (-np.sin(t), np.cos(t)) if b == 0 else (np.cos(t), np.sin(t))
            semisimple.append((U, b, a, c, np.eye(3)[i]))
        t = angles[0]
        a, c = (-np.sin(t), np.cos(t)) if b == 0 else (np.cos(t), np.sin(t))
        semisimple.append((U, b, a, c, np.array([1, 1j, 0])))
        for t, weight in [(.2, 2), (1.0, 1)]:
            a, c = (-np.sin(t), np.cos(t)) if b == 0 else (np.cos(t), np.sin(t))
            coordinates.append((b, a, c, weight))
    add('semisimple', semisimple, 'Analytic semisimple measure (kernel weights)', coordinates)
    add('kernel_superposition', [semisimple[3], semisimple[7]],
        'Selected kernel superpositions; incomplete ray sample')

    M = np.array([[1., 1.], [0., 1.]])
    D, E = inverse_sqrt(np.eye(2)+M@M.T), inverse_sqrt(np.eye(2)+M.T@M)
    U = np.block([[E, E@M.T], [-D@M, D]])
    defective = [(U, 0, 1, 1, np.array([1, 0])), (U, 1, -1, 1, np.array([0, 1]))]
    add('defective', defective, 'Analytic defective measure; kernel weight one')

    swap = np.eye(4)[[0, 2, 1, 3]]
    rays = [(0, 1), (1, 0), (1, 1), (-1, 1), (1j, 1), (-1j, 1)]
    add('swap', [(swap, b, a, c, np.eye(2)[b]) for b in (0, 1) for a, c in rays],
        'Illustrative rays only; continuum measure UNDEFINED')

    add('homogeneous_rescaling', [(U, b, (2-3j)*a, (2-3j)*c, d) for U,b,a,c,d in generic],
        'Same generic roots after homogeneous rescaling')
    permutation = np.eye(4)[[2, 0, 3, 1]]
    change = np.kron(np.eye(2), permutation)
    add('detector_basis_change', [(change@U@change.T, b, a, c, permutation@d)
                                 for U,b,a,c,d in generic],
        'Same generic roots after detector basis permutation')
    spectator = qr_unitary(3, 20260819)
    add('spectator', [(append_uncoupled_spectator(U, spectator), b, a, c, np.kron(d, e))
                      for U,b,a,c,d in generic for e in np.eye(3)],
        'Generic roots with threefold spectator kernel weights')

    add('wrong_outcome', [(U, 1-b, a, c, d) for U,b,a,c,d in generic],
        'REJECTED inputs; not collapsible outcome sets')
    add('wrong_coordinate_order', [(U, b, c, a, d) for U,b,a,c,d in generic],
        'REJECTED inputs; not collapsible outcome sets')
    add('perturbed_detector', [(U, b, a, c, d+.1*np.eye(4)[0]) for U,b,a,c,d in generic],
        'REJECTED detector states; input-ray sample only')
    add('nonunitary', [(1.001*U, b, a, c, d) for U,b,a,c,d in generic],
        'REJECTED nonunitary operator; input-ray sample only')
    add('near_collapse', [(np.eye(4), 0, 1e-6, 1, np.array([1, 0])),
                          (np.eye(4), 1, 1, 1e-6, np.array([1, 0]))],
        'REJECTED near-collapse inputs; high fidelity is insufficient')
    return cases, plots


def theta_histograms(coordinates):
    edges = np.linspace(0, np.pi, BINS+1)
    densities = []
    for outcome in (0, 1):
        selected = [(a, b, weight) for o, a, b, weight in coordinates if o == outcome]
        theta = [2*np.arctan2(abs(a), abs(b)) for a,b,w in selected]
        counts = np.histogram(theta, bins=edges, weights=[w for a,b,w in selected])[0]
        densities.append(counts/(np.sum(counts)*np.diff(edges)))
    total = densities[0]+densities[1]
    ratio = np.divide(densities[0], total, out=np.full_like(total, np.nan), where=total>0)
    return edges, densities, ratio


def render_plot(path, name, plot):
    edges, densities, ratio = theta_histograms(plot['coordinates'])
    centers = (edges[:-1]+edges[1:])/2
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 3.8), layout='constrained')
    colors = ['#2864a5', '#d97428']
    for b in (0, 1):
        axes[0].stairs(densities[b], edges, color=colors[b], linewidth=2,
                       label=f'Outcome {b}', fill=True, alpha=.35)
    axes[0].set_ylabel('Normalized polar histogram')
    axes[0].legend(frameon=False)
    line = np.linspace(0, np.pi, 501)
    axes[1].plot(line, np.cos(line/2)**2, 'k--', linewidth=1.5,
                 label=r'Born $\cos^2(\theta/2)$')
    support = np.isfinite(ratio)
    axes[1].plot(centers[support], ratio[support], 'o', color='#4b8645', markersize=5,
                 label='Supported-bin ratio')
    axes[1].plot(centers[~support], np.full(np.sum(~support), -.07), '|', color='.65',
                 label='Empty bins (undefined)')
    axes[1].set(ylim=(-.12, 1.07), ylabel=r'$\rho_0^{(\theta)}/(\rho_0^{(\theta)}+\rho_1^{(\theta)})$')
    axes[1].legend(frameon=False, fontsize=8, loc='upper right')
    for ax in axes:
        ax.set(xlim=(0, np.pi), xlabel=r'$\theta$', xticks=[0, np.pi/2, np.pi],
               xticklabels=['0', r'$\pi/2$', r'$\pi$'])
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle(name.replace('_', ' ').title()+'\n'+plot['kind'], fontsize=11)
    fig.savefig(path.with_suffix('.png'), dpi=160)
    fig.savefig(path.with_suffix('.pdf'))
    plt.close(fig)
    return dict(edges=edges.tolist(), density_0=densities[0].tolist(),
                density_1=densities[1].tolist(),
                ratio=[float(x) if np.isfinite(x) else None for x in ratio],
                kind=plot['kind'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Every invocation gets a new directory; previous evidence is never overwritten.
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'plots').mkdir()
    cases, plots = fixtures()
    arrays, rows, summaries = {}, [], []
    for case, states in cases.items():
        for i, (U, outcome, alpha, beta, detector) in enumerate(states):
            key = f'{case}__{i}'
            reconstruction = reconstruct_collapse_state(U, outcome, alpha, beta, detector)
            fields = dict(U=U, outcome=outcome, alpha=alpha, beta=beta, detector=detector,
                          **asdict(reconstruction))
            arrays.update({f'{key}__{name}': value for name, value in fields.items()})
            rows.append(dict(id=key))
            summaries.append(dict(id=key, forbidden_branch_norm=reconstruction.forbidden_branch_norm,
                                  retained_norm_error=reconstruction.retained_norm_error,
                                  factorization_residual=reconstruction.factorization_residual))
    np.savez_compressed(args.output/'states.npz', **arrays)
    (args.output/'cases.json').write_text(json.dumps(dict(states=rows), indent=2)+'\n')
    (args.output/'reconstruction.json').write_text(json.dumps(summaries, indent=2)+'\n')
    plot_data = {name: render_plot(args.output/'plots'/name, name, plot)
                 for name, plot in plots.items()}
    (args.output/'plot_data.json').write_text(json.dumps(plot_data, indent=2)+'\n')
    # Keep a complete recoverable source snapshot, including untracked source files.
    source_paths = ['core/projective_roots.py', 'scripts/build_exact_formalism_packet.py',
                    'verifier/exact_formalism/v1/check.py', 'verifier/exact_formalism/v1/METHOD.md',
                    'tests/test_collapse_state_reconstruction.py', 'tests/test_exact_formalism_verifier.py',
                    'SPEC.md', 'requirements.txt', 'requirements-dev.txt']
    source_hashes = {}
    for name in source_paths:
        source = ROOT/name
        # Evidence copies must not be imported or collected as duplicate tests.
        target = args.output/'source'/(name+'.snapshot')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        source_hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    (args.output/'working-tree.patch').write_bytes(subprocess.check_output(
        ['git', 'diff', '--binary', 'HEAD'], cwd=ROOT))
    provenance = dict(timestamp=datetime.now(timezone.utc).isoformat(),
                      command=sys.argv, python=platform.python_version(),
                      commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                      git_status=subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
                      versions={name: importlib.metadata.version(name) for name in
                                ['numpy', 'scipy', 'sympy', 'matplotlib', 'pytest']},
                      source_hashes=source_hashes, plot_bins=BINS, certification=False,
                      purpose='State-level formalism; no Hamiltonian campaign or physical time',
                      seeds=dict(generic=20260919, spectator=20260819))
    (args.output/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps(dict(packet=str(args.output), states=len(rows), plots=len(plots))))


if __name__ == '__main__':
    main()
