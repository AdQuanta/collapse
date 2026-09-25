"""Reproduce playground.py's ring-family anchors at a much larger detector size.

playground.py diagonalizes the full 2**(N+1)-dimensional unitary, which is only tractable
up to about N=9-10 in a few minutes. The ring model's coupling to the central qubit is
collective (every detector site couples equally), so it is invariant under cyclic
permutation of the detector sites; this script diagonalizes each momentum sector
separately (a few thousand-dimensional block instead of one 2**15-dimensional matrix) via
SinglePixelHamiltonianQuSpin and core.analysis's relative-evolution machinery, and reaches
N=14 in about three minutes on a laptop.

playground.ring_hamiltonian tilts the qubit's self-field by theta (hz0=h0*cos, hx0=h0*sin)
at a fixed coupling axis (X0), then reads out the roots after rotating the qubit basis so
the field sits at the pole (``rotate_qubit``). Conjugating the whole Hamiltonian by that
same rotation is equivalent and cheaper to build here: the field becomes pure Z, and the
coupling axis rotates into a mix of X0 and Z0,

    M^T X0 M = cos(theta) X0 + sin(theta) Z0,

i.e. Jx = g*cos(theta)/sqrt(N), Jzx = g*sin(theta)/sqrt(N). Only central-qubit operators
change, so the detector-site translation symmetry is untouched. Both this rewriting and
the antipodal shortcut below (r1 = -r0) are checked against playground's dense code at
small N by ``--verify``.

Usage:
    python onboarding/reproduce_large_N.py --verify
    python onboarding/reproduce_large_N.py --n-pixel 14 --fig onboarding/fig_three_anchors_large_N.png
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from quspin.basis import spin_basis_general  # noqa: E402
from quspin.operators import hamiltonian  # noqa: E402

from core.analysis import _relative_eigenvalues_from_local_sectors  # noqa: E402
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin  # noqa: E402
from playground import bloch, outcome_ratio, summarize, cloud as dense_cloud  # noqa: E402


def build_model(n_pixel: int, J: float = 1.0, hz: float = 1.0, h0: float = 1.0,
                 theta_deg: float = 0.0, g: float = 0.1) -> SinglePixelHamiltonianQuSpin:
    th = np.radians(theta_deg)
    return SinglePixelHamiltonianQuSpin(
        N_pixel=n_pixel, J=J, hz=hz, hz0=h0,
        Jx=g * np.cos(th) / np.sqrt(n_pixel), Jzx=g * np.sin(th) / np.sqrt(n_pixel),
        connectivity="ring", central_coupling="all",
    )


def sector_lambdas(model: SinglePixelHamiltonianQuSpin, kp: int, times: list[float]) -> np.ndarray:
    static, n_total = model._build_static()
    n = n_total - 1
    shift = np.arange(n_total)
    for k in range(n):
        shift[1 + k] = 1 + (k + 1) % n
    basis = spin_basis_general(n_total, kblock=(shift, kp))
    H_k = hamiltonian(static, [], basis=basis, dtype=np.complex128, check_symm=False, check_herm=False)
    E, V = np.linalg.eigh(H_k.toarray())
    sector = {"E": E, "V": V, "states": basis.states.copy(), "basis": basis,
              "central_top_bit": 1, "relative_evolution_local": True}
    lams = [_relative_eigenvalues_from_local_sectors([sector], float(t), n_total) for t in times]
    return np.concatenate(lams)


def _one_sector(args):
    n_pixel, theta_deg, h0, hz, J, g, kp, times = args
    model = build_model(n_pixel, J=J, hz=hz, h0=h0, theta_deg=theta_deg, g=g)
    lam = sector_lambdas(model, kp, times)
    reps = 1 if kp in (0, n_pixel / 2) else 2  # kp and n-kp give identical polar angles
    return np.concatenate([lam] * reps)


def ring_cloud_sectors(n_pixel: int, times: list[float], theta_deg: float = 0.0,
                        h0: float = 1.0, hz: float = 1.0, J: float = 1.0, g: float = 0.1,
                        pool: Pool | None = None):
    """Pooled (r0, r1) clouds for the ring model at N_pixel, via momentum sectors.

    r1 is the exact antipode of r0 (T1: outcome-1 is the antipodal image of outcome-0 for
    *any* unitary U), verified against playground's own independently-computed outcome-1
    pencil to < 1e-11 at small N -- this sidesteps the fixed-input/outcome-pencil
    conjugation bookkeeping entirely.
    """
    jobs = [(n_pixel, theta_deg, h0, hz, J, g, kp, times) for kp in range(n_pixel // 2 + 1)]
    lam_parts = pool.map(_one_sector, jobs) if pool is not None else [_one_sector(j) for j in jobs]
    r0 = bloch(np.concatenate(lam_parts))
    return r0, -r0


def verify_against_playground(n_pixel: int = 7) -> None:
    """Cross-check against playground's dense generalized-eig + ``rotate_qubit``."""
    from playground import ring_hamiltonian, time_unitary, disentangling_spectrum, rotate_qubit
    times = [7.3, 13.1, 22.7, 37.9, 63.5, 105.2, 178.0, 300.0]
    d = 2 ** n_pixel
    for theta_deg in (0.0, 45.0, 90.0):
        H = ring_hamiltonian(n_pixel, J=1.0, hz=1.0, h0=1.0, theta_deg=theta_deg, g=0.1)
        R0, R1 = [], []
        for t in times:
            U = rotate_qubit(time_unitary(H, t), theta_deg, d)
            r0, r1, _ = disentangling_spectrum(U, d)
            R0.append(r0); R1.append(r1)
        r0_dense, r1_dense = np.vstack(R0), np.vstack(R1)
        r0_sec, r1_sec = ring_cloud_sectors(n_pixel, times, theta_deg=theta_deg)

        z_err = np.max(np.abs(np.sort(r0_dense[:, 2]) - np.sort(r0_sec[:, 2])))
        s_dense = outcome_ratio(r0_dense, r1_dense)
        s_sec = outcome_ratio(r0_sec, r1_sec)
        print(f"theta_deg={theta_deg:5.1f}  max|z0_dense - z0_sector| = {z_err:.2e}  "
              f"MAE dense/sector = {s_dense['mae']:.6f}/{s_sec['mae']:.6f}  "
              f"k dense/sector = {s_dense['k']:.3f}/{s_sec['k']:.3f}")


def figure_capped(panels, path: str, max_scatter: int = 1500) -> None:
    """Like playground.figure(), but subsamples each cloud's scatter to max_scatter points
    (dense root counts at large N make the unsampled scatter unreadable). Statistics (MAE,
    k, axis) always come from outcome_ratio on the full, un-subsampled clouds."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]
    rng = np.random.default_rng(0)
    C0, C1, BORN = "#0072B2", "#D55E00", "#6E6E6E"
    fig, ax = plt.subplots(2, len(panels), figsize=(3.4 * len(panels), 6.2))
    for j, (title, r0, r1) in enumerate(panels):
        s = outcome_ratio(r0, r1); n = s["axis"]
        e1 = np.cross(n, [0, 1, 0])
        e1 = e1 / max(np.linalg.norm(e1), 1e-9) if np.linalg.norm(e1) > 1e-6 else np.array([1., 0, 0])
        for r, c, lab in ((r0, C0, "outcome 0"), (r1, C1, "outcome 1")):
            idx = rng.choice(len(r), size=min(max_scatter, len(r)), replace=False)
            rs = r[idx]
            ax[0, j].scatter(rs @ e1, rs @ n, s=4, c=c, alpha=0.35, lw=0, label=lab)
        ax[0, j].add_patch(plt.Circle((0, 0), 1, fill=False, color=BORN, lw=0.8)); ax[0, j].set_aspect("equal")
        ax[0, j].set_xlim(-1.1, 1.1); ax[0, j].set_ylim(-1.1, 1.1); ax[0, j].set_title(title, fontsize=9.5)
        ax[0, j].set_xticks([]); ax[0, j].set_yticks([]); [sp.set_visible(False) for sp in ax[0, j].spines.values()]
        ax[1, j].plot(s["mid"], s["born"], "--", color=BORN, lw=1.5, label="Born  cos²(θ/2)")
        ax[1, j].plot(s["mid"], s["R"], "o-", color=C0, lw=1.5, ms=4, label="R(θ) measured")
        ax[1, j].set_ylim(-0.03, 1.03); ax[1, j].set_xticks([0, np.pi / 2, np.pi]); ax[1, j].set_xticklabels(["0", "π/2", "π"])
        ax[1, j].set_xlabel("θ from outcome-0 pole (fitted axis)"); ax[1, j].grid(alpha=0.25)
        ax[1, j].text(0.03, 0.06, f"MAE {s['mae']:.3f}\nk = {s['k']:.2f}\n(n={len(r0) + len(r1)})",
                      transform=ax[1, j].transAxes, fontsize=9)
        for sp in ("top", "right"): ax[1, j].spines[sp].set_visible(False)
    ax[0, 0].legend(loc="lower left", fontsize=8, frameon=False, markerscale=3)
    ax[1, 0].set_ylabel("outcome ratio R(θ)")
    ax[1, 0].legend(loc="upper right", fontsize=8, frameon=False)
    fig.suptitle("Disentangling spectrum of a qubit + detector unitary: where the collapsible "
                 "inputs sit, and how they split", fontsize=11)
    fig.tight_layout(); fig.savefig(path, dpi=160); print("wrote", path)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n-pixel", type=int, default=14, help="detector ring size for the sector-based ring panels")
    p.add_argument("--taus", default="7,13,22,37,63,105,178,300", help="tau = g*t values pooled for statistics")
    p.add_argument("--g", type=float, default=0.1)
    p.add_argument("--fig", default=None, help="write the anchors figure to this path")
    p.add_argument("--verify", action="store_true", help="cross-check against playground's dense code and exit")
    p.add_argument("--workers", type=int, default=8)
    args = p.parse_args()

    if args.verify:
        verify_against_playground()
        return

    times = [float(tau) / args.g for tau in args.taus.split(",")]
    t0 = time.time()
    with Pool(processes=args.workers) as pool:
        ring_panels = []
        for title, theta_deg in [("matched ring  (hz = |h0|, g = 0.1)", 0.0),
                                  ("same ring, self-field rotated 45°", 45.0)]:
            r0, r1 = ring_cloud_sectors(args.n_pixel, times, theta_deg=theta_deg, g=args.g, pool=pool)
            ring_panels.append((f"{title}\n[N={args.n_pixel}, sectors]", r0, r1))
            summarize(title, r0, r1)
    print(f"ring panels (N={args.n_pixel}) done in {time.time() - t0:.1f}s")

    # Small-N dense anchors: T2 (Haar -> uniform) and T3 (secular no-go) are exact at any N,
    # so these are shown at the same N as the original figure rather than re-run at N_pixel.
    r0q, r1q = dense_cloud("qnd", N=8, K=8, seed=0)
    r0h, r1h = dense_cloud("haar", N=8, K=8, seed=0)
    summarize("QND (N=8, exact at any N)", r0q, r1q)
    summarize("Haar (N=8, exact at any N)", r0h, r1h)

    all_panels = [("QND:  h0 ∥ coupling  ([U, X0] = 0)\n[N=8]", r0q, r1q),
                  ("Haar-random unitary\n[N=8]", r0h, r1h)] + ring_panels
    if args.fig:
        figure_capped(all_panels, args.fig)
    print(f"total wall time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
