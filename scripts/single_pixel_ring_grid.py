"""
Single-Pixel Ring – Full 3-Parameter Grid Scan
================================================

Sweep **all** combinations of (Jx, Jz, hz) over
{0, 0.1, 0.2, 0.5, 1, 2, 5, 10} with hx=0, J=1, ring connectivity.

8³ = 512 scenarios, each evaluated at 9 time points.

Usage::

    python scripts/single_pixel_ring_grid.py
    python scripts/single_pixel_ring_grid.py -N 7 --workers 4
    python scripts/single_pixel_ring_grid.py --save figures/sp_ring
    python scripts/single_pixel_ring_grid.py --save figures/sp_ring --bloch
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

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

# ===================================================================
# Constants
# ===================================================================
TIMES = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0]
SEED = 44

# Grid values for each swept parameter
GRID_VALUES = [0.0, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]


# ===================================================================
# Build all scenarios
# ===================================================================
def build_scenarios(N: int) -> list[dict]:
    """
    Enumerate all (Jx, Jz, hz) combinations on an 8³ grid.

    Parameters
    ----------
    N : int
        Total number of qubits.

    Returns
    -------
    list[dict]
        Flat list of scenario dicts, globally numbered.
    """
    scenarios: list[dict] = []

    for Jx in GRID_VALUES:
        for Jz in GRID_VALUES:
            for hz in GRID_VALUES:
                params = dict(
                    N_pixel=N - 1,
                    J=1.0,
                    Jx=Jx,
                    Jz=Jz,
                    hx=0.0,
                    hz=hz,
                    connectivity="ring",
                    seed=SEED,
                )
                title_line = f"SP[ring] | J=1  Jx={Jx:g}  Jz={Jz:g}  hx=0  hz={hz:g}"
                scenarios.append(
                    {
                        "title_line": title_line,
                        "model": "SP",
                        "cls": SinglePixelHamiltonianQuSpin,
                        "params": params,
                    }
                )

    for i, s in enumerate(scenarios):
        s["idx"] = i
        s["total"] = len(scenarios)

    return scenarios


# ===================================================================
# Worker
# ===================================================================
def _run_scenario(scenario: dict) -> dict:
    """
    Build H → diagonalize once → loop over times → extract z-data
    and (optionally) Bloch-sphere coordinates.
    """
    import os

    logger = logging.getLogger(__name__)
    title = scenario["title_line"]
    prefix = (
        f"  [W{os.getpid()}] [{scenario['idx']+1:3d}/{scenario['total']:3d}] "
        f"{title:55s}"
    )
    try:
        t0 = time.time()

        # 1. Generate Hamiltonian
        ham = scenario["cls"](**scenario["params"])
        H = ham.generate()
        logger.info(f"{prefix}  H generated ({time.time()-t0:.1f}s)")

        # 2. Diagonalize once
        t1 = time.time()
        E, V = np.linalg.eigh(H)
        logger.info(f"{prefix}  Diagonalized ({time.time()-t1:.1f}s)")

        # 3. Loop over times
        time_results = []
        for t_val in TIMES:
            analyzer = DisentanglementAnalyzer.from_eigenbasis(E, V, t_val)
            analyzer.get_initial_qubit_states_from_eigenvalues()

            z0 = np.abs(analyzer.phi0[:, 0]) ** 2 - np.abs(analyzer.phi0[:, 1]) ** 2
            z1 = np.abs(analyzer.phi1[:, 0]) ** 2 - np.abs(analyzer.phi1[:, 1]) ** 2

            # Bloch-sphere coordinates
            half = analyzer.N // 2
            bx0 = np.empty(half)
            by0 = np.empty(half)
            bx1 = np.empty(half)
            by1 = np.empty(half)
            for i in range(half):
                phi = analyzer.phi0[i, :]
                bx0[i] = 2 * np.real(np.conj(phi[0]) * phi[1])
                by0[i] = 2 * np.imag(np.conj(phi[0]) * phi[1])
                phi = analyzer.phi1[i, :]
                bx1[i] = 2 * np.real(np.conj(phi[0]) * phi[1])
                by1[i] = 2 * np.imag(np.conj(phi[0]) * phi[1])

            time_results.append(
                {
                    "t": t_val,
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
            "error": str(exc),
        }


# ===================================================================
# Plotting helpers
# ===================================================================
def plot_histogram_on_ax(ax, z0, z1, title, bins=30, use_theta=True):
    """Draw combined density-histogram + ratio on *ax*."""
    if use_theta:
        data0 = np.arccos(np.clip(z0, -1, 1))
        data1 = np.arccos(np.clip(z1, -1, 1))
        bin_edges = np.linspace(0, np.pi, bins + 1)
        x_th = np.linspace(0, np.pi, 1000)
        born = (1 + np.cos(x_th)) / 2
        d_label = (r"$\rho_0(\theta)$", r"$\rho_1(\theta)$")
        xlabel = r"$\theta$"
    else:
        data0, data1 = z0, z1
        bin_edges = np.linspace(-1, 1, bins + 1)
        x_th = np.linspace(-1, 1, 1000)
        born = (1 + x_th) / 2
        d_label = (r"$\rho_0(z)$", r"$\rho_1(z)$")
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
    ax.bar(centers, h0d, width=bw, alpha=0.22, color="blue", label=d_label[0])
    ax.bar(centers, h1d, width=bw, alpha=0.22, color="red", label=d_label[1])
    ax_r.plot(
        centers[mask],
        r0[mask],
        "o-",
        color="blue",
        ms=2,
        lw=1,
        label=r"$h_0/(h_0{+}h_1)$",
    )
    ax_r.plot(
        centers[mask],
        r1[mask],
        "o-",
        color="red",
        ms=2,
        lw=1,
        label=r"$h_1/(h_0{+}h_1)$",
    )
    ax_r.plot(x_th, born, "k--", lw=0.8, label="Born rule")
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


def plot_bloch_on_ax(ax, td, title):
    """Draw Bloch-sphere scatter on a 3-D *ax*."""
    # Wire-frame sphere
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 40)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(xs, ys, zs, color="gray", alpha=0.10)

    ax.scatter(td["bx0"], td["by0"], td["z0"], color="blue", alpha=0.4, s=4)
    ax.scatter(td["bx1"], td["by1"], td["z1"], color="red", alpha=0.4, s=4)

    ax.set_xlabel("X", fontsize=5, labelpad=-4)
    ax.set_ylabel("Y", fontsize=5, labelpad=-4)
    ax.set_zlabel("Z", fontsize=5, labelpad=-4)
    ax.tick_params(axis="both", labelsize=4, pad=-2)
    ax.set_title(title, fontsize=6, pad=1)


def _safe_filename(title_line: str) -> str:
    """Convert a title line to a safe filename component."""
    return (
        title_line.replace(" ", "_")
        .replace("|", "_")
        .replace("[", "")
        .replace("]", "")
        .replace("=", "")
        .replace(",", "")
        .replace("/", "-")
        .replace("\\", "-")
        .replace("\u2013", "-")
    )


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Single-Pixel ring grid scan – all (Jx, Jz, hz) combos, "
            "hx=0, J=1, no disorder"
        )
    )
    parser.add_argument(
        "-N",
        "--N",
        type=int,
        default=7,
        dest="N",
        help="Total number of qubits (default: 7).",
    )
    parser.add_argument(
        "--no-theta",
        action="store_true",
        help="Plot in z-space instead of θ = arccos(z)",
    )
    parser.add_argument(
        "--bloch",
        action="store_true",
        help="Also save Bloch-sphere scatter plots for each scenario",
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Save figures to directory (e.g. figures/sp_ring)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (default: cpu_count)",
    )
    args = parser.parse_args()

    scenarios = build_scenarios(args.N)
    use_theta = not args.no_theta
    n_workers = args.workers or cpu_count()
    n = len(scenarios)

    # --- Logging setup ------------------------------------------------
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"single_pixel_ring_grid_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== SP Ring Grid Scan: {n} scenarios, N={args.N} (D={2**args.N}), "
        f"{n_workers} workers, {len(TIMES)} time points ==="
    )
    logger.info(f"Log file: {log_file}")
    t_start = time.time()

    # --- Parallel computation -----------------------------------------
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

    # --- Save directory -----------------------------------------------
    save_dir = None
    if args.save:
        save_dir = Path(args.save)
        save_dir.mkdir(parents=True, exist_ok=True)

    # --- Plot: one figure per scenario --------------------------------
    space = r"$\theta$" if use_theta else "$z$"
    ntimes = len(TIMES)
    nrows = 2 if args.bloch else 1

    for res in results:
        title_line = res["title_line"]
        tr = res["time_results"]
        idx = res["idx"]
        safe_name = _safe_filename(title_line)

        fig = plt.figure(
            figsize=(3.5 * ntimes, 3.5 * nrows),
            dpi=120,
            constrained_layout=True,
        )

        # Row 1: histograms (always)
        for col, td in enumerate(tr):
            ax = fig.add_subplot(nrows, ntimes, col + 1)
            plot_histogram_on_ax(
                ax,
                td["z0"],
                td["z1"],
                title=f"t={td['t']:g}",
                use_theta=use_theta,
            )

        # Row 2: Bloch spheres (when --bloch is active)
        if args.bloch:
            for col, td in enumerate(tr):
                ax3 = fig.add_subplot(
                    nrows,
                    ntimes,
                    ntimes + col + 1,
                    projection="3d",
                )
                plot_bloch_on_ax(ax3, td, title=f"t={td['t']:g}")

        fig.suptitle(
            f"#{idx+1:03d}  {title_line}",
            fontsize=10,
            fontweight="bold",
            y=1.02,
        )

        if save_dir:
            out = save_dir / f"{idx+1:03d}_{safe_name}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            logger.info(f"Saved {out}")
            plt.close(fig)

    if not args.save:
        plt.show()

    logger.info("All done.")


if __name__ == "__main__":
    main()
