"""
Single-Pixel Ring – hz0 offset sweep
======================================

Sweep ``hz0`` across a range of offsets from ``hz`` and plot the
Born-similarity metric *S* as a function of ``hz − hz0`` for multiple
evolution times.

Fixed parameters (defaults, all overridable via CLI):

    J = 1,  Jx = 0.01 / sqrt(N_pixel),  Jz = 0,  hx = 0,  hz = 0.1

Ring connectivity, symmetry sectors used.

Plots produced
~~~~~~~~~~~~~~~
1. ``N={N}/S_vs_offset.png`` — S(hz − hz0) curves coloured by *t*.
2. ``N={N}/histograms/hz0={hz0}.png`` — theta-histogram + Bloch per hz0.
3. ``born_similarity.txt`` — table of S values.

Usage::

    python scripts/sp_ring_hz0_sweep.py -N 9 --save figures/hz0_sweep
    python scripts/sp_ring_hz0_sweep.py -N 7 9 11 --workers 4 --save figures/hz0_sweep
    python scripts/sp_ring_hz0_sweep.py -N 9 --hz 1.0 --Jx 0.1 --save figures/hz0_sweep
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import logging
import time
from datetime import datetime
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Arial"

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

# ===================================================================
# Constants
# ===================================================================
TIMES = [1000.0, 10_000.0, 100_000.0, 1_000_000.0]
SEED = 44

# Offsets:  hz0 = hz + offset, so hz − hz0 = −offset
HZ0_OFFSETS = np.round(
    np.concatenate(
        [
            np.linspace(-0.1, -0.01, 10),
            np.linspace(-0.009, 0.009, 19),
            np.linspace(0.01, 0.1, 10),
        ]
    ),
    4,
).tolist()


# ===================================================================
# Born-similarity metric
# ===================================================================
def born_similarity(z0, z1, n_theta=100):
    r"""S = 1 − 2 ∫₀^π |f(θ) − cos²(θ/2)| sin θ dθ.

    Calibration: S = 1 perfect Born, S = 0 for f = ½.
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
# Build scenarios
# ===================================================================
def build_scenarios(
    N_list: list[int],
    hz: float,
    Jx_unscaled: float,
    Jz: float,
) -> list[dict]:
    """Enumerate N × hz0_offset grid."""
    scenarios: list[dict] = []

    for N in N_list:
        N_pixel = N - 1
        Jx_s = Jx_unscaled / np.sqrt(N_pixel)
        for offset in HZ0_OFFSETS:
            hz0_val = hz + offset
            params = dict(
                N_pixel=N_pixel,
                J=1.0,
                Jx=Jx_s,
                Jz=Jz,
                hx=0.0,
                hz=hz,
                hz0=hz0_val,
                connectivity="ring",
                seed=SEED,
                use_symmetry=True,
            )
            title_line = (
                f"SP[ring] N={N} | J=1  Jx={Jx_unscaled:g}/√{N_pixel}  "
                f"Jz={Jz:g}  hz={hz:g}  hz0={hz0_val:g}"
            )
            scenarios.append(
                {
                    "title_line": title_line,
                    "model": "SP",
                    "cls": SinglePixelHamiltonianQuSpin,
                    "params": params,
                    "hz0": hz0_val,
                    "offset": offset,
                    "N": N,
                }
            )

    for i, s in enumerate(scenarios):
        s["idx"] = i
        s["total"] = len(scenarios)
    return scenarios


# ===================================================================
# Worker  (uses symmetry sectors)
# ===================================================================
def _run_scenario(scenario: dict) -> dict:
    import os

    logger = logging.getLogger(__name__)
    title = scenario["title_line"]
    N_pixel = scenario["params"]["N_pixel"]
    N = N_pixel + 1
    prefix = (
        f"  [W{os.getpid()}] [{scenario['idx']+1:3d}/{scenario['total']:3d}] "
        f"{title:65s}"
    )
    try:
        t0 = time.time()
        ham = scenario["cls"](**scenario["params"])

        t_sec = time.time()
        sectors = ham.diagonalize_sectors()
        logger.info(
            f"{prefix}  Sectors ({len(sectors)}) built ({time.time()-t_sec:.1f}s)"
        )

        time_results = []
        for t_val in TIMES:
            analyzer = DisentanglementAnalyzer.from_sectors(sectors, t_val, N)
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

            S_ratio = born_similarity(z0, z1)

            time_results.append(
                {
                    "t": t_val,
                    "S_ratio": S_ratio,
                    "z0": z0,
                    "z1": z1,
                    "bx0": bx0,
                    "by0": by0,
                    "bx1": bx1,
                    "by1": by1,
                }
            )

        elapsed = time.time() - t0
        logger.info(f"{prefix}  Done ({elapsed:.1f}s)")
        return {
            "idx": scenario["idx"],
            "title_line": scenario["title_line"],
            "model": scenario["model"],
            "hz0": scenario["hz0"],
            "offset": scenario["offset"],
            "N": scenario["N"],
            "time_results": time_results,
        }
    except Exception as exc:
        logger.error(f"{prefix}  *** ERROR: {exc}")
        import traceback

        traceback.print_exc()
        return {
            "idx": scenario["idx"],
            "title_line": scenario["title_line"],
            "model": scenario["model"],
            "hz0": scenario.get("hz0", 0),
            "offset": scenario.get("offset", 0),
            "N": scenario.get("N", 0),
            "error": str(exc),
        }


# ===================================================================
# Plotting helpers
# ===================================================================
def plot_histogram_on_ax(ax, z0, z1, title, bins=30):
    """Draw density histogram + ratio overlay on *ax*."""
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
    ax.set_title(title, fontsize=6, pad=3)


def plot_bloch_on_ax(ax, td, title):
    """Draw Bloch-sphere scatter on a 3-D *ax*."""
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 40)
    ax.plot_surface(
        np.outer(np.cos(u), np.sin(v)),
        np.outer(np.sin(u), np.sin(v)),
        np.outer(np.ones_like(u), np.cos(v)),
        color="gray",
        alpha=0.10,
    )
    ax.scatter(td["bx0"], td["by0"], td["z0"], color="blue", alpha=0.4, s=4)
    ax.scatter(td["bx1"], td["by1"], td["z1"], color="red", alpha=0.4, s=4)
    ax.set_xlabel("X", fontsize=5, labelpad=-4)
    ax.set_ylabel("Y", fontsize=5, labelpad=-4)
    ax.set_zlabel("Z", fontsize=5, labelpad=-4)
    ax.tick_params(axis="both", labelsize=4, pad=-2)
    ax.set_title(title, fontsize=6, pad=1)


# ===================================================================
# Plot: histograms + Bloch per hz0 value
# ===================================================================
def save_histograms(results, save_dir, logger):
    """Save per-scenario histogram + Bloch figures."""
    ntimes = len(TIMES)
    for res in results:
        if "error" in res:
            continue
        N, hz0 = res["N"], res["hz0"]
        tr = res["time_results"]

        out_dir = save_dir / f"N={N}" / "histograms"
        out_dir.mkdir(parents=True, exist_ok=True)

        fig = plt.figure(
            figsize=(3.5 * ntimes, 7.0),
            dpi=120,
            constrained_layout=True,
        )
        for col, td in enumerate(tr):
            ax = fig.add_subplot(2, ntimes, col + 1)
            plot_histogram_on_ax(
                ax,
                td["z0"],
                td["z1"],
                title=f"t={td['t']:g}  S={td['S_ratio']:.3f}",
            )
            ax3 = fig.add_subplot(2, ntimes, ntimes + col + 1, projection="3d")
            plot_bloch_on_ax(ax3, td, title=f"t={td['t']:g}")

        fig.suptitle(res["title_line"], fontsize=9, fontweight="bold", y=1.02)

        out = out_dir / f"hz0={hz0:g}.png"
        fig.savefig(out, bbox_inches="tight", dpi=150)
        plt.close(fig)
        logger.info(f"Saved {out}")


# ===================================================================
# Plot: S vs (hz − hz0) curves, one per time
# ===================================================================
def save_s_vs_offset(results, hz, save_dir, logger):
    """One figure per N showing S(hz − hz0) for each evolution time."""
    # Group by N: {N: {offset: {t: S}}}
    by_N: dict[int, dict[float, dict[float, float]]] = {}
    for res in results:
        if "error" in res:
            continue
        N = res["N"]
        if N not in by_N:
            by_N[N] = {}
        off = res["offset"]
        by_N[N][off] = {}
        for td in res["time_results"]:
            by_N[N][off][td["t"]] = td["S_ratio"]

    cmap = plt.cm.viridis
    colours = [cmap(i / max(1, len(TIMES) - 1)) for i in range(len(TIMES))]

    for N, lookup in by_N.items():
        out_dir = save_dir / f"N={N}"
        out_dir.mkdir(parents=True, exist_ok=True)

        offsets_sorted = sorted(lookup.keys())
        x_vals = [hz - (hz + off) for off in offsets_sorted]  # hz − hz0 = −offset

        fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
        for ci, t_val in enumerate(TIMES):
            ys = [lookup[off].get(t_val, np.nan) for off in offsets_sorted]
            ax.plot(
                x_vals,
                ys,
                "o-",
                ms=4,
                lw=1.4,
                color=colours[ci],
                label=f"t={t_val:g}",
            )

        ax.axvline(0, color="gray", ls=":", lw=0.8)
        ax.set_xlabel(r"$h_z - h_{z0}$", fontsize=12)
        ax.set_ylabel("S  (Born similarity)", fontsize=12)
        ax.set_ylim(-0.05, 1.05)
        ax.set_title(
            rf"Born sim. $S$ vs $h_z - h_{{z0}}$  |  SP[ring]  $N={N}$,  $h_z={hz:g}$",
            fontsize=12,
            fontweight="bold",
        )
        ax.legend(fontsize=8, loc="lower right")
        ax.tick_params(labelsize=9)

        out = out_dir / "S_vs_offset.png"
        fig.savefig(out, bbox_inches="tight", dpi=150)
        plt.close(fig)
        logger.info(f"Saved {out}")


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description=(
            "SP ring – hz0 offset sweep.  Plots Born-similarity S vs "
            "(hz − hz0) for multiple evolution times."
        )
    )
    parser.add_argument(
        "-N",
        "--N",
        type=int,
        nargs="+",
        default=[9],
        dest="N_list",
        help="One or more total-qubit counts (default: 9)",
    )
    parser.add_argument(
        "--Jx",
        type=float,
        default=0.01,
        help="Central-pixel XX coupling (unscaled; divided by √N_pixel) (default: 0.01)",
    )
    parser.add_argument(
        "--Jz",
        type=float,
        default=0.0,
        help="Central-pixel ZZ coupling (default: 0.0)",
    )
    parser.add_argument(
        "--hz",
        type=float,
        default=0.1,
        help="Field on the ring spins (default: 0.1)",
    )
    parser.add_argument("--save", type=str, required=True)
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()

    scenarios = build_scenarios(
        args.N_list,
        hz=args.hz,
        Jx_unscaled=args.Jx,
        Jz=args.Jz,
    )
    n_workers = args.workers or cpu_count()
    n = len(scenarios)

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_ring_hz0_sweep_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== SP Ring hz0 offset sweep: {n} scenarios, "
        f"N={args.N_list}, Jx={args.Jx}, Jz={args.Jz}, hz={args.hz}, "
        f"{n_workers} workers, {len(TIMES)} time points ==="
    )
    logger.info(f"Log file: {log_file}")
    t_start = time.time()

    if n_workers == 1:
        results_unordered = [_run_scenario(s) for s in scenarios]
    else:
        with Pool(n_workers) as pool:
            results_unordered = list(pool.imap_unordered(_run_scenario, scenarios))

    results = sorted(
        [r for r in results_unordered if "error" not in r],
        key=lambda r: r["idx"],
    )
    n_failed = len(results_unordered) - len(results)
    elapsed = time.time() - t_start
    logger.info(f"Computation finished in {elapsed:.1f}s")
    if n_failed:
        logger.warning(f"{n_failed} scenario(s) skipped due to errors")

    save_dir = Path(args.save)
    save_dir.mkdir(parents=True, exist_ok=True)

    # --- S vs offset plot ---
    logger.info("=== Saving S vs offset plots ===")
    save_s_vs_offset(results, args.hz, save_dir, logger)

    # --- Histograms + Bloch ---
    logger.info("=== Saving histograms ===")
    save_histograms(results, save_dir, logger)

    # --- Similarity table ---
    sim_lines = []
    header = f"{'N':>4s}  {'hz0':>8s}  {'offset':>8s}  {'t':>12s}  {'S':>8s}"
    sim_lines.append(header)
    sim_lines.append("-" * len(header))
    for res in results:
        if "error" in res:
            continue
        for td in res["time_results"]:
            sim_lines.append(
                f"{res['N']:4d}  {res['hz0']:8.4f}  {res['offset']:8.4f}  "
                f"{td['t']:12g}  {td['S_ratio']:8.4f}"
            )
    txt_path = save_dir / "born_similarity.txt"
    txt_path.write_text("\n".join(sim_lines) + "\n", encoding="utf-8")
    logger.info(f"Saved {txt_path}")

    logger.info("All done.")


if __name__ == "__main__":
    main()
