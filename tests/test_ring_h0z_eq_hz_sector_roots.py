"""The sector worker's polar angles equal the dense SPEC outcome-0 pencil's (real H)."""

import importlib.util
from pathlib import Path

import numpy as np

from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.projective_roots import forward_pole_root_spectrum

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ring_sector_worker", ROOT / "scripts" / "ring_h0z_eq_hz_sector_roots.py")
worker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(worker)


def test_sector_thetas_match_dense_outcome_pencil():
    n, h, j, g, t = 5, 1.0, 0.37, 0.1, 23.0
    model = worker.build_model(n, h, j, g)
    thetas = []
    for kp in range(n // 2 + 1):
        weight = 1 if kp in (0, n / 2) else 2
        thetas.append(np.repeat(worker.sector_thetas(model, kp, np.array([t]))[0], weight))
    thetas = np.sort(np.concatenate(thetas))

    ham = SinglePixelHamiltonianNumpy(N_pixel=n, J=-j, Jx=-g / np.sqrt(n), hz=-h, hz0=-h,
                                      connectivity="ring", central_coupling="all").generate()
    w, v = np.linalg.eigh(ham)
    u = (v * np.exp(-1j * w * t)) @ v.conj().T
    dense = np.sort(np.asarray(forward_pole_root_spectrum(u, 0).theta))
    assert thetas.shape == dense.shape == (2**n,)
    assert np.max(np.abs(thetas - dense)) < 1e-9
