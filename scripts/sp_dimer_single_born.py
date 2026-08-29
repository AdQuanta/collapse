"""
Dimerized Pixel – Single-parameter Born-distribution diagnostic
================================================================

Simulates a **single** parameter choice using the dimerized intra-pixel
ZZ coupling  J∑_{i=1}^{N_pixel/2} σ^z_{2i-1} σ^z_{2i}:

    J = 1,  Jx = 0.01 / √N_pixel,  Jz = 0,  hz = hz0 = 0.1,  hx = 0

at times t = 100, 1000, 10 000, 1 000 000, using symmetry sectors.

Produces for each N:

1. **θ-histograms** with density (blue/red bars) and ratio overlaid
   with the Born curve cos²(θ/2).  One column per time.
2. **φ-histograms** (azimuthal Bloch angle) for subsystems 0 and 1
   shown as density only (no ratio / Born reference).
3. **Bloch-sphere** scatter (3-D) for each time.

A table of the Born similarity metric *S* is printed to stdout
and saved as ``born_similarity.txt``.

Usage::

    python scripts/sp_dimer_single_born.py -N 9 11 --save figures/dimer_born
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import logging
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Arial"

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians.quspin_hamiltonians import DimerizedPixelHamiltonianQuSpin

# ===================================================================
# Constants
# ===================================================================
TIMES = [100.0, 1000.0, 10_000.0, 1_000_000.0]
SEED = 44
JX_UNSCALED = 0.01
HZ = 0.1


# ===================================================================
# Born-similarity metric  (copied from sp_ring_jx_hz_born.py)
# ===================================================================
def born_similarity(z0, z1, n_theta=100):
    r"""Born-distribution similarity for the histogram ratio.

        S = 1 − 2 ∫₀^π |f(θ) − cos²(θ/2)| sin θ dθ

    Calibration: S = 1 for perfect Born ratio, S = 0 for f = ½.
    """
    theta0 = np.arccos(np.clip(z0, -1, 1))
    theta1 = np.arccos(np.clip(z1, -1, 1))

    theta_edges = np.linspace(0, np.pi, n_theta + 1)
    theta_centers = (theta_edges[:-1] + theta_edges[1:]) / 2
    dtheta = theta_edges[1] - theta_edges[0]

    h0, _ = np.histogram(theta0, bins=theta_edges)
    h1, _ = np.histogram(theta1, bins=theta_edges)
    total = h0 + h1
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(total > 0, h0 / total, 0.5)

    born = np.cos(theta_centers / 2) ** 2
    integrand = np.abs(ratio - born) * np.sin(theta_centers)
    return 1.0 - 2.0 * np.sum(integrand) * dtheta


# ===================================================================
# Bloch-coordinate extraction
# ===================================================================
def _bloch_coords(analyzer):
    """Return (z0, z1, bx0, by0, bx1, by1, phi_az0, phi_az1)."""
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
    # Azimuthal angle on the Bloch sphere
    phi_az0 = np.arctan2(by0, bx0) % (2 * np.pi)
    phi_az1 = np.arctan2(by1, bx1) % (2 * np.pi)
    return z0, z1, bx0, by0, bx1, by1, phi_az0, phi_az1


# ===================================================================
# Plotting helpers
# ===================================================================
def _plot_theta_hist(ax, z0, z1, title, bins=30):
    """Draw θ density histogram + ratio overlay with Born reference."""
    data0 = np.arccos(np.clip(z0, -1, 1))
    data1 = np.arccos(np.clip(z1, -1, 1))
    bin_edges = np.linspace(0, np.pi, bins + 1)
    x_th = np.linspace(0, np.pi, 1000)
    born = (1 + np.cos(x_th)) / 2
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
    ax.set_xlabel(r"$\theta$", fontsize=7)
    ax.set_ylabel("Density", fontsize=6, color="gray")
    ax.tick_params(axis="y", labelcolor="gray", labelsize=5)
    ax_r.set_ylabel("Fraction", fontsize=6)
    ax_r.tick_params(axis="y", labelsize=5)
    ax.tick_params(axis="x", labelsize=5)
    ax.set_title(title, fontsize=7, pad=3)


def _plot_phi_hist(ax, phi_az0, phi_az1, title, bins=30):
    r"""Draw azimuthal (φ) density histogram for subsystems 0 and 1."""
    bin_edges = np.linspace(0, 2 * np.pi, bins + 1)
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bw = bin_edges[1] - bin_edges[0]
    h0, _ = np.histogram(phi_az0, bins=bin_edges, density=True)
    h1, _ = np.histogram(phi_az1, bins=bin_edges, density=True)
    ax.bar(centers, h0, width=bw, alpha=0.35, color="blue", label=r"$\phi_0$")
    ax.bar(centers, h1, width=bw, alpha=0.35, color="red", label=r"$\phi_1$")
    ax.set_xlim(0, 2 * np.pi)
    ax.set_xlabel(r"$\varphi$", fontsize=7)
    ax.set_ylabel("Density", fontsize=6)
    ax.tick_params(labelsize=5)
    ax.set_title(title, fontsize=7, pad=3)
    ax.legend(fontsize=5, loc="upper right")


def _plot_bloch(ax, bx0, by0, z0, bx1, by1, z1, title):
    """Draw Bloch-sphere scatter on a 3-D axis."""
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 40)
    ax.plot_surface(
        np.outer(np.cos(u), np.sin(v)),
        np.outer(np.sin(u), np.sin(v)),
        np.outer(np.ones_like(u), np.cos(v)),
        color="gray",
        alpha=0.10,
    )
    ax.scatter(bx0, by0, z0, color="blue", alpha=0.4, s=4)
    ax.scatter(bx1, by1, z1, color="red", alpha=0.4, s=4)
    ax.set_xlabel("X", fontsize=5, labelpad=-4)
    ax.set_ylabel("Y", fontsize=5, labelpad=-4)
    ax.set_zlabel("Z", fontsize=5, labelpad=-4)
    ax.tick_params(axis="both", labelsize=4, pad=-2)
    ax.set_title(title, fontsize=7, pad=1)


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Dimerized Pixel – single parameter set, Born diagnostic.  "
            "J=1, Jx=0.01/√N_pixel, Jz=0, hz=hz0=0.1."
        )
    )
    parser.add_argument(
        "-N", "--N", type=int, nargs="+", default=[9], dest="N_list",
        help="One or more total-qubit counts (N_pixel = N-1 must be even, "
             "so N must be odd; default: 9)",
    )
    parser.add_argument("--save", type=str, required=True)
    args = parser.parse_args()

    # Validate that every N yields an even N_pixel
    for N in args.N_list:
        N_pixel = N - 1
        if N_pixel % 2 != 0:
            parser.error(
                f"N={N} gives N_pixel={N_pixel} which is odd; "
                f"dimerized model requires even N_pixel."
            )

    save_dir = Path(args.save)
    save_dir.mkdir(parents=True, exist_ok=True)

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_dimer_single_born_{datetime.now():%Y%m%d_%H%M%S}.log"

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.info(
        f"=== Dimerized Pixel single-param Born diagnostic: "
        f"N={args.N_list}, Jx={JX_UNSCALED}, hz={HZ}, "
        f"{len(TIMES)} time points ==="
    )
    logger.info(f"Log file: {log_file}")

    similarity_lines: list[str] = []
    header = f"{'N':>4s}  {'t':>12s}  {'S_born':>8s}"
    similarity_lines.append(header)
    similarity_lines.append("-" * len(header))
    logger.info(header)

    for N in args.N_list:
        N_pixel = N - 1
        Jx_scaled = JX_UNSCALED / np.sqrt(N_pixel)

        logger.info(
            f"=== N={N}  (N_pixel={N_pixel}, D={2**N})  "
            f"Jx={JX_UNSCALED}/sqrt({N_pixel})={Jx_scaled:.6f} ==="
        )

        ham = DimerizedPixelHamiltonianQuSpin(
            N_pixel=N_pixel,
            J=1.0,
            Jx=Jx_scaled,
            Jz=0.0,
            hx=0.0,
            hz=HZ,
            hz0=None,  # same as hz
            seed=SEED,
            use_symmetry=True,
        )

        t0 = time.time()
        sectors = ham.diagonalize_sectors()
        logger.info(f"    {len(sectors)} sectors built ({time.time()-t0:.1f}s)")

        ntimes = len(TIMES)
        time_data: list[dict] = []

        for t_val in TIMES:
            analyzer = DisentanglementAnalyzer.from_sectors(sectors, t_val, N)
            analyzer.get_initial_qubit_states_from_eigenvalues()
            z0, z1, bx0, by0, bx1, by1, phi_az0, phi_az1 = _bloch_coords(
                analyzer
            )
            S = born_similarity(z0, z1)
            time_data.append(
                dict(
                    t=t_val,
                    z0=z0, z1=z1,
                    bx0=bx0, by0=by0, bx1=bx1, by1=by1,
                    phi_az0=phi_az0, phi_az1=phi_az1,
                    S=S,
                )
            )
            line = f"{N:4d}  {t_val:12g}  {S:8.4f}"
            logger.info(line)
            similarity_lines.append(line)

        # ---- Figure: 3 rows × ntimes cols ----
        fig = plt.figure(
            figsize=(4.0 * ntimes, 10.0),
            dpi=120,
            constrained_layout=True,
        )

        for col, td in enumerate(time_data):
            # Row 1: θ-histogram
            ax_th = fig.add_subplot(3, ntimes, col + 1)
            _plot_theta_hist(
                ax_th, td["z0"], td["z1"],
                title=f"t={td['t']:g}   S={td['S']:.3f}",
            )

            # Row 2: φ-histogram
            ax_ph = fig.add_subplot(3, ntimes, ntimes + col + 1)
            _plot_phi_hist(
                ax_ph, td["phi_az0"], td["phi_az1"],
                title=f"t={td['t']:g}",
            )

            # Row 3: Bloch sphere
            ax_bl = fig.add_subplot(3, ntimes, 2 * ntimes + col + 1, projection="3d")
            _plot_bloch(
                ax_bl,
                td["bx0"], td["by0"], td["z0"],
                td["bx1"], td["by1"], td["z1"],
                title=f"t={td['t']:g}",
            )

        fig.suptitle(
            f"Dimerized Pixel  N={N}  |  J=1  Jx={JX_UNSCALED}/√{N_pixel}  "
            f"Jz=0  hz=hz0={HZ}",
            fontsize=11,
            fontweight="bold",
            y=1.02,
        )

        out = save_dir / f"N={N}.png"
        fig.savefig(out, bbox_inches="tight", dpi=150)
        plt.close(fig)
        logger.info(f"Saved {out}")

        # ---- Save similarity table (incrementally) ----
        txt_path = save_dir / "born_similarity.txt"
        txt_path.write_text("\n".join(similarity_lines) + "\n", encoding="utf-8")
        logger.info(f"Similarity table updated: {txt_path}")

    logger.info("All done.")


if __name__ == "__main__":
    main()
