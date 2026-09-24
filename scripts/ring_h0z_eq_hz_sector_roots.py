"""Polar root law of the resonant Ising ring, h0z = hz, via pixel-translation sectors.

Model (SPEC positive convention, Pauli matrices, qubit first, periodic ring):

    H = h s0^z + h sum_i s_i^z + J sum_i s_i^z s_{i+1}^z + (g / sqrt(N)) s0^x sum_i s_i^x

built with ``SinglePixelHamiltonianQuSpin`` in its minus-sign convention
(code parameter = -SPEC coefficient; the central coupling is per edge, so the
1/sqrt(N) factor is applied here). Each detector-momentum sector is built and
diagonalised on its own and passed through the local relative-evolution path of
``DisentanglementAnalyzer.from_sectors`` (``_relative_eigenvalues_from_local_sectors``),
so only one sector is held in memory at a time. H is real, so the fixed-input
roots are complex conjugates of the SPEC outcome-0 roots and the polar angles are
identical; sectors k and N-k have identical polar angles, so only k = 0..N/2 are
computed and the others are carried by an integer weight of 2.

Output: one ``.npz`` per sector with ``theta`` (shape (n_times, sector_half)),
``times``, ``weight``, ``kp`` and the parameters, plus a JSON completion marker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from quspin.basis import spin_basis_general  # noqa: E402
from quspin.operators import hamiltonian  # noqa: E402

from core.analysis import _relative_eigenvalues_from_local_sectors  # noqa: E402
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin  # noqa: E402


def build_model(n: int, h: float, j: float, g: float, h0: float | None = None) -> SinglePixelHamiltonianQuSpin:
    return SinglePixelHamiltonianQuSpin(
        N_pixel=n, J=-j, Jx=-g / np.sqrt(n), hz=-h, hz0=-(h if h0 is None else h0),
        connectivity="ring", central_coupling="all",
    )


def sector_thetas(model: SinglePixelHamiltonianQuSpin, kp: int, times: np.ndarray) -> np.ndarray:
    static, n_total = model._build_static()
    n = n_total - 1
    shift = np.arange(n_total)
    for k in range(n):
        shift[1 + k] = 1 + (k + 1) % n
    basis = spin_basis_general(n_total, kblock=(shift, kp))
    h_k = hamiltonian(static, [], basis=basis, dtype=np.complex128, check_symm=False, check_herm=False)
    energies, vectors = np.linalg.eigh(h_k.toarray())
    sector = {"E": energies, "V": vectors, "states": basis.states.copy(), "basis": basis,
              "central_top_bit": 1, "relative_evolution_local": True}
    rows = []
    for t in times:
        z = _relative_eigenvalues_from_local_sectors([sector], float(t), n_total)
        rows.append(2.0 * np.arctan(np.abs(z)))
    return np.array(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--h", type=float, default=1.0)
    parser.add_argument("--h0", type=float, default=None, help="qubit field h0z (default: equal to --h)")
    parser.add_argument("--j", type=float, required=True)
    parser.add_argument("--g", type=float, required=True)
    parser.add_argument("--taus", type=str, default="10,30,100", help="tau = g T values")
    parser.add_argument("--kp", type=str, default="all", help="'all' or comma list of sector indices 0..N/2")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    n = args.n
    times = np.array([float(x) / args.g for x in args.taus.split(",")])
    kps = range(n // 2 + 1) if args.kp == "all" else [int(x) for x in args.kp.split(",")]
    args.out.mkdir(parents=True, exist_ok=True)
    model = build_model(n, args.h, args.j, args.g, args.h0)
    for kp in kps:
        if not 0 <= kp <= n // 2:
            raise ValueError(f"kp must lie in 0..{n // 2}; got {kp}")
        start = time.time()
        theta = sector_thetas(model, kp, times)
        weight = 1 if kp in (0, n / 2) else 2
        tag = f"N{n}_J{args.j}_g{args.g}" + ("" if args.h0 is None else f"_h0{args.h0}")
        path = args.out / f"{tag}_kp{kp}.npz"
        np.savez(path, theta=theta, times=times, weight=weight, kp=kp, n=n, h=args.h, h0=args.h if args.h0 is None else args.h0, j=args.j, g=args.g)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        marker = {"status": "complete", "n": n, "kp": kp, "weight": weight, "file": str(path), "sha256": digest,
                  "n_roots": int(theta.shape[1]), "seconds": round(time.time() - start, 1)}
        (args.out / f"{tag}_kp{kp}_complete.json").write_text(json.dumps(marker))
        print(json.dumps(marker), flush=True)


if __name__ == "__main__":
    main()
