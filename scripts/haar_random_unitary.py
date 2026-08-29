"""
Haar Random Unitary – Disentanglement Analysis
================================================

Generate a single Haar-random unitary and run the disentanglement
analysis.  There is no Hamiltonian or time evolution — the unitary
itself is the object of study.

Usage::

    python scripts/haar_random_unitary.py
    python scripts/haar_random_unitary.py -N 7 --bloch
    python scripts/haar_random_unitary.py -N 7 --save figures/haar
    python scripts/haar_random_unitary.py -N 7 --seed 42
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse, logging, time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from core.analysis import DisentanglementAnalyzer
from core.quantum_utils import generate_random_unitary

SEED = 44


def _analyse_unitary(U):
    """Run disentanglement analysis on a unitary and return Bloch data."""
    analyzer = DisentanglementAnalyzer(U)
    analyzer.diagonalize_subblocks_product()
    analyzer.get_initial_qubit_states_from_eigenvalues()

    z0 = np.abs(analyzer.phi0[:, 0]) ** 2 - np.abs(analyzer.phi0[:, 1]) ** 2
    z1 = np.abs(analyzer.phi1[:, 0]) ** 2 - np.abs(analyzer.phi1[:, 1]) ** 2
    half = analyzer.N // 2
    bx0, by0, bx1, by1 = (np.empty(half) for _ in range(4))
    for i in range(half):
        phi = analyzer.phi0[i, :]
        bx0[i] = 2 * np.real(np.conj(phi[0]) * phi[1])
        by0[i] = 2 * np.imag(np.conj(phi[0]) * phi[1])
        phi = analyzer.phi1[i, :]
        bx1[i] = 2 * np.real(np.conj(phi[0]) * phi[1])
        by1[i] = 2 * np.imag(np.conj(phi[0]) * phi[1])
    return {"z0": z0, "z1": z1, "bx0": bx0, "by0": by0, "bx1": bx1, "by1": by1}


def plot_histogram_on_ax(ax, z0, z1, title, bins=30, use_theta=True):
    if use_theta:
        data0, data1 = np.arccos(np.clip(z0, -1, 1)), np.arccos(np.clip(z1, -1, 1))
        bin_edges = np.linspace(0, np.pi, bins + 1)
        x_th = np.linspace(0, np.pi, 1000)
        born = (1 + np.cos(x_th)) / 2
        xlabel = r"$\theta$"
    else:
        data0, data1 = z0, z1
        bin_edges = np.linspace(-1, 1, bins + 1)
        x_th = np.linspace(-1, 1, 1000)
        born = (1 + x_th) / 2
        xlabel = r"$z$"
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bw = bin_edges[1] - bin_edges[0]
    h0d, _ = np.histogram(data0, bins=bin_edges, density=True)
    h1d, _ = np.histogram(data1, bins=bin_edges, density=True)
    h0c, _ = np.histogram(data0, bins=bin_edges)
    h1c, _ = np.histogram(data1, bins=bin_edges)
    hs = h0c + h1c
    mask = (h0c > 0) & (h1c > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        r0 = np.where(mask, h0c / hs, np.nan)
        r1 = np.where(mask, h1c / hs, np.nan)
    ax_r = ax.twinx()
    ax.bar(centers, h0d, width=bw, alpha=0.22, color="blue")
    ax.bar(centers, h1d, width=bw, alpha=0.22, color="red")
    ax_r.plot(centers[mask], r0[mask], "o-", color="blue", ms=2, lw=1)
    ax_r.plot(centers[mask], r1[mask], "o-", color="red", ms=2, lw=1)
    ax_r.plot(x_th, born, "k--", lw=0.8)
    ax_r.plot(x_th, 1 - born, "k--", lw=0.8)
    ax_r.set_ylim(0, 1.05)
    ax.set_xlim(bin_edges[0], bin_edges[-1])
    ax.set_xlabel(xlabel, fontsize=7)
    ax.set_ylabel("Density", fontsize=6, color="gray")
    ax.tick_params(axis="y", labelcolor="gray", labelsize=5)
    ax_r.set_ylabel("Fraction", fontsize=6)
    ax_r.tick_params(axis="y", labelsize=5)
    ax.tick_params(axis="x", labelsize=5)
    ax.set_title(title, fontsize=6, pad=3)


def plot_bloch_on_ax(ax, data, title):
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 40)
    ax.plot_surface(
        np.outer(np.cos(u), np.sin(v)),
        np.outer(np.sin(u), np.sin(v)),
        np.outer(np.ones_like(u), np.cos(v)),
        color="gray",
        alpha=0.10,
    )
    ax.scatter(data["bx0"], data["by0"], data["z0"], color="blue", alpha=0.4, s=4)
    ax.scatter(data["bx1"], data["by1"], data["z1"], color="red", alpha=0.4, s=4)
    ax.set_xlabel("X", fontsize=5, labelpad=-4)
    ax.set_ylabel("Y", fontsize=5, labelpad=-4)
    ax.set_zlabel("Z", fontsize=5, labelpad=-4)
    ax.tick_params(axis="both", labelsize=4, pad=-2)
    ax.set_title(title, fontsize=6, pad=1)


def main():
    ap = argparse.ArgumentParser(description="Haar random unitary analysis")
    ap.add_argument(
        "-N", "--N", type=int, default=7, dest="N", help="Number of qubits (D = 2^N)"
    )
    ap.add_argument(
        "--seed", type=int, default=SEED, help="Random seed for the Haar unitary"
    )
    ap.add_argument("--no-theta", action="store_true")
    ap.add_argument("--bloch", action="store_true")
    ap.add_argument("--save", type=str, default=None)
    args = ap.parse_args()

    D = 2**args.N
    use_theta = not args.no_theta

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"haar_random_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.info(f"=== Haar Random Unitary: N={args.N}, D={D}, seed={args.seed} ===")

    t0 = time.time()
    U = generate_random_unitary(D, seed=args.seed)
    logger.info(f"Haar unitary generated ({time.time()-t0:.2f}s)")

    t1 = time.time()
    data = _analyse_unitary(U)
    logger.info(f"Disentanglement analysis done ({time.time()-t1:.2f}s)")

    title_line = f"Haar random U | N={args.N}  D={D}  seed={args.seed}"

    # Single figure: histogram (+ Bloch sphere if --bloch)
    ncols = 2 if args.bloch else 1
    fig = plt.figure(figsize=(6 * ncols, 5), dpi=120, constrained_layout=True)

    ax_hist = fig.add_subplot(1, ncols, 1)
    plot_histogram_on_ax(
        ax_hist, data["z0"], data["z1"], title="Histogram", use_theta=use_theta
    )

    if args.bloch:
        ax3 = fig.add_subplot(1, ncols, 2, projection="3d")
        plot_bloch_on_ax(ax3, data, title="Bloch sphere")

    fig.suptitle(title_line, fontsize=10, fontweight="bold", y=1.02)

    if args.save:
        save_dir = Path(args.save)
        save_dir.mkdir(parents=True, exist_ok=True)
        out = save_dir / f"haar_N{args.N}_seed{args.seed}.png"
        fig.savefig(out, bbox_inches="tight", dpi=150)
        logger.info(f"Saved {out}")
        plt.close(fig)
    else:
        plt.show()

    logger.info("All done.")


if __name__ == "__main__":
    main()
