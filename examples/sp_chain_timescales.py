"""
Single-Pixel Chain – multi-timescale simulation
=================================================

Simulates the chain Hamiltonian for a **single** choice of parameters
at many evolution times spanning several decades, capturing the
crossover from short-time coherent dynamics to long-time
thermalisation.

Default parameters::

    Jpm = 1,  J = 0,  Jx = 0.01,  Jz = 0,  hx = 0,  hz = 0.1,  N = 9

Times are log-spaced from 1 to 10^7 (21 points by default).

Plots produced (saved under ``--save`` directory)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. ``N={N}_timescales.png``  – theta-histogram grids at selected times
   (3 rows: theta-density + ratio, phi-density, Bloch sphere).
2. ``N={N}_born_vs_t.png``   – Born-similarity *S* vs *t* on a log-x
   axis showing convergence / drift across decades.
3. ``born_similarity.txt``   – table of S values for every time point.

Usage::

    python examples/sp_chain_timescales.py --save figures/chain_timescales
    python examples/sp_chain_timescales.py -N 7 --Jpm 1 --Jx 0.05 --hz 0.5 --save figures/chain_timescales
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

from collapse.analysis import DisentanglementAnalyzer
from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

# ===================================================================
# Constants
# ===================================================================
SEED = 44

# Representative subset of times shown in the histogram grid
GRID_INDICES = [0, 5, 10, 15, 20]  # indices into the full TIMES array


# ===================================================================
# Born-similarity metric
# ===================================================================
def born_similarity(z0, z1, n_theta=100):
    r"""S = 1 - 2 \int_0^\pi |f(\theta) - cos^2(\theta/2)| sin\theta d\theta.

    Calibration: S = 1 perfect Born, S = 0 for f = 1/2.
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
    return 1.0 - 2.0 * np.sum(np.abs(ratio - born) * np.sin(theta_centers)) * dtheta


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
    phi_az0 = np.arctan2(by0, bx0) % (2 * np.pi)
    phi_az1 = np.arctan2(by1, bx1) % (2 * np.pi)
    return z0, z1, bx0, by0, bx1, by1, phi_az0, phi_az1


# ===================================================================
# Plotting helpers
# ===================================================================
def _plot_theta_hist(ax, z0, z1, title, bins=30):
    """Theta density + ratio overlay with Born reference."""
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
    r"""Azimuthal phi density histogram."""
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
    """Bloch-sphere 3-D scatter."""
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
            "SP chain – multi-timescale simulation.  Diagonalises once "
            "and evaluates at many log-spaced times."
        )
    )
    parser.add_argument(
        "-N", "--N", type=int, default=9, help="Total qubit count (default: 9)"
    )
    parser.add_argument(
        "--Jpm", type=float, default=1.0, help="Intra-pixel +- coupling (default: 1.0)"
    )
    parser.add_argument(
        "--Jx", type=float, default=0.01, help="Central-pixel XX coupling (default: 0.01)"
    )
    parser.add_argument(
        "--Jz", type=float, default=0.0, help="Central-pixel ZZ coupling (default: 0.0)"
    )
    parser.add_argument(
        "--hx", type=float, default=0.0, help="Transverse field (default: 0.0)"
    )
    parser.add_argument(
        "--hz", type=float, default=0.1, help="Longitudinal field (default: 0.1)"
    )
    parser.add_argument(
        "--n-times",
        type=int,
        default=21,
        help="Number of log-spaced time points (default: 21)",
    )
    parser.add_argument(
        "--t-min", type=float, default=1.0, help="Minimum time (default: 1)"
    )
    parser.add_argument(
        "--t-max", type=float, default=1e7, help="Maximum time (default: 1e7)"
    )
    parser.add_argument("--save", type=str, required=True)
    args = parser.parse_args()

    N = args.N
    N_pixel = N - 1
    JPM = args.Jpm
    JX = args.Jx
    JZ = args.Jz
    HX = args.hx
    HZ = args.hz

    TIMES = np.logspace(
        np.log10(args.t_min), np.log10(args.t_max), args.n_times
    ).tolist()

    # Clamp grid indices to valid range
    grid_idx = [i for i in GRID_INDICES if i < len(TIMES)]
    if not grid_idx:
        grid_idx = list(range(min(5, len(TIMES))))

    save_dir = Path(args.save)
    save_dir.mkdir(parents=True, exist_ok=True)

    # --- Logging ----------------------------------------------------------
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_chain_timescales_{datetime.now():%Y%m%d_%H%M%S}.log"

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    param_str = (
        f"N={N}  Jpm={JPM}  J=0  Jx={JX}  Jz={JZ}  hx={HX}  hz={HZ}"
    )
    logger.info(f"=== SP Chain timescales: {param_str} ===")
    logger.info(
        f"  {len(TIMES)} times from {TIMES[0]:g} to {TIMES[-1]:g}  (log-spaced)"
    )
    logger.info(f"  Log file: {log_file}")

    # --- Diagonalise once -------------------------------------------------
    ham = SinglePixelHamiltonianQuSpin(
        N_pixel=N_pixel,
        J=0.0,
        Jpm=JPM,
        Jx=JX,
        Jz=JZ,
        hx=HX,
        hz=HZ,
        hz0=HZ,
        connectivity="chain",
        seed=SEED,
    )

    t0_wall = time.time()
    E, V = ham.diagonalize()
    logger.info(f"  Diagonalized  D={2**N}  ({time.time()-t0_wall:.1f}s)")

    # --- Evaluate at every time -------------------------------------------
    all_data: list[dict] = []
    sim_lines: list[str] = []
    header = f"{'N':>4s}  {'t':>12s}  {'S_born':>8s}"
    sim_lines.append(header)
    sim_lines.append("-" * len(header))
    logger.info(header)

    for t_val in TIMES:
        analyzer = DisentanglementAnalyzer.from_eigenbasis(E, V, t_val)
        analyzer.get_initial_qubit_states_from_eigenvalues()
        z0, z1, bx0, by0, bx1, by1, phi_az0, phi_az1 = _bloch_coords(analyzer)
        S = born_similarity(z0, z1)

        all_data.append(
            dict(
                t=t_val,
                z0=z0,
                z1=z1,
                bx0=bx0,
                by0=by0,
                bx1=bx1,
                by1=by1,
                phi_az0=phi_az0,
                phi_az1=phi_az1,
                S=S,
            )
        )
        line = f"{N:4d}  {t_val:12g}  {S:8.4f}"
        logger.info(line)
        sim_lines.append(line)

    # === Figure 1: S(t) curve =============================================
    fig_s, ax_s = plt.subplots(figsize=(10, 5), constrained_layout=True)
    ts = [d["t"] for d in all_data]
    ss = [d["S"] for d in all_data]

    ax_s.semilogx(ts, ss, "o-", color="teal", ms=5, lw=1.5)
    ax_s.axhline(1.0, color="gray", ls=":", lw=0.8, label="S = 1 (Born)")
    ax_s.axhline(0.0, color="gray", ls="--", lw=0.8, label="S = 0 (uniform)")
    ax_s.set_xlabel("t", fontsize=12)
    ax_s.set_ylabel("S  (Born similarity)", fontsize=12)
    ax_s.set_ylim(-0.1, 1.1)
    ax_s.set_title(
        f"Born similarity vs time  |  SP[chain]  {param_str}",
        fontsize=11,
        fontweight="bold",
    )
    ax_s.legend(fontsize=9, loc="lower right")
    ax_s.tick_params(labelsize=9)

    out_s = save_dir / f"N={N}_born_vs_t.png"
    fig_s.savefig(out_s, bbox_inches="tight", dpi=150)
    plt.close(fig_s)
    logger.info(f"Saved {out_s}")

    # === Figure 2: histogram grid at selected times =======================
    ncols = len(all_data)
    fig = plt.figure(
        figsize=(4.0 * ncols, 14.0),
        dpi=120,
    )
    fig.subplots_adjust(
        left=0.03, right=0.97, top=0.93, bottom=0.04,
        wspace=0.35, hspace=0.40,
    )

    for col_i, td in enumerate(all_data):

        # Row 1: theta histogram
        ax_th = fig.add_subplot(3, ncols, col_i + 1)
        _plot_theta_hist(
            ax_th,
            td["z0"],
            td["z1"],
            title=f"t={td['t']:g}   S={td['S']:.3f}",
        )

        # Row 2: phi histogram
        ax_ph = fig.add_subplot(3, ncols, ncols + col_i + 1)
        _plot_phi_hist(
            ax_ph,
            td["phi_az0"],
            td["phi_az1"],
            title=f"t={td['t']:g}",
        )

        # Row 3: Bloch sphere
        ax_bl = fig.add_subplot(
            3, ncols, 2 * ncols + col_i + 1, projection="3d"
        )
        _plot_bloch(
            ax_bl,
            td["bx0"],
            td["by0"],
            td["z0"],
            td["bx1"],
            td["by1"],
            td["z1"],
            title=f"t={td['t']:g}",
        )

    fig.suptitle(
        f"SP[chain,+-] {param_str}",
        fontsize=10,
        fontweight="bold",
        y=1.02,
    )
    out_hist = save_dir / f"N={N}_timescales.png"
    fig.savefig(out_hist, bbox_inches="tight", dpi=150)
    plt.close(fig)
    logger.info(f"Saved {out_hist}")

    # === Save similarity table ============================================
    txt_path = save_dir / "born_similarity.txt"
    txt_path.write_text("\n".join(sim_lines) + "\n", encoding="utf-8")
    logger.info(f"Saved {txt_path}")

    logger.info("All done.")


if __name__ == "__main__":
    main()
