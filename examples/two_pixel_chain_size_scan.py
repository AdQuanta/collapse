"""
Two-Pixel Size & Connectivity & Time Scan
=============================================

Analyses the two-pixel Hamiltonian with fixed couplings
(J=1, Jx=Jz=0.3, hx=hz=0) across:

* **Connectivities**: chain, ring, all-to-all
* **System sizes**: N = 7, 9, 11, 13
* **Evolution times**: t = 1, 5, 10, 20

One figure is produced per connectivity mode, with rows = system sizes
and columns = time points (4×4 grid).

Usage::

    python examples/two_pixel_chain_size_scan.py
    python examples/two_pixel_chain_size_scan.py --no-theta
    python examples/two_pixel_chain_size_scan.py --save tp_scan.png
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import logging
import time
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

from collapse.analysis import DisentanglementAnalyzer
from collapse.hamiltonians.quspin_hamiltonians import TwoPixelHamiltonianQuSpin

SYSTEM_SIZES = [7, 9, 11, 13]
TIMES = [1.0, 10.0, 100.0]
# CONNECTIVITIES = ["chain", "ring", "all_to_all"]
CONNECTIVITIES = ["ring"]

CONNECTIVITY_DISPLAY = {
    "chain": "Chain",
    "ring": "Ring",
    "all_to_all": "All-to-All",
}


# ===================================================================
# Scenario builder
# ===================================================================
def build_scenarios() -> list[dict]:
    scenarios: list[dict] = []
    for conn in CONNECTIVITIES:
        for N in SYSTEM_SIZES:
            N_pixel = (N - 1) // 2
            for t in TIMES:
                label = f"N={N}, t={t:g}\n" rf"$N_{{px}}={N_pixel},\;D={2**N}$"
                scenarios.append(
                    {
                        "label": label,
                        "N": N,
                        "t": t,
                        "connectivity": conn,
                        "cls": TwoPixelHamiltonianQuSpin,
                        "params": dict(
                            N_pixel=N_pixel,
                            J=1.0,
                            Jx=0.3,
                            Jz=0.3,
                            hx=0.0,
                            hz=0.0,
                            connectivity=conn,
                            seed=44,
                        ),
                    }
                )
    return scenarios


# ===================================================================
# Worker
# ===================================================================
def _run_scenario(scenario: dict) -> dict:
    import os

    logger = logging.getLogger(__name__)
    label_short = scenario["label"].split("\n")[0]
    conn = scenario["connectivity"]
    prefix = (
        f"  [W{os.getpid()}] [{scenario['idx']+1:2d}/{scenario['total']:2d}] "
        f"{conn:10s} {label_short:18s}"
    )
    try:
        t0 = time.time()

        ham = scenario["cls"](**scenario["params"])

        t1 = time.time()
        N_total = 2 * scenario["params"]["N_pixel"] + 1
        sectors = ham.diagonalize_sectors()
        logger.info(f"{prefix}  Hamiltonian diagonalized ({time.time()-t1:.1f}s)")

        t2 = time.time()
        analyzer = DisentanglementAnalyzer.from_sectors(sectors, scenario["t"], N_total)
        logger.info(f"{prefix}  Sub-block product diagonalized ({time.time()-t2:.1f}s)")

        analyzer.get_initial_qubit_states_from_eigenvalues()

        z0 = np.abs(analyzer.phi0[:, 0]) ** 2 - np.abs(analyzer.phi0[:, 1]) ** 2
        z1 = np.abs(analyzer.phi1[:, 0]) ** 2 - np.abs(analyzer.phi1[:, 1]) ** 2
        elapsed = time.time() - t0
        logger.info(f"{prefix}  Done ({elapsed:.1f}s)")
        return {
            "idx": scenario["idx"],
            "label": scenario["label"],
            "connectivity": conn,
            "N": scenario["N"],
            "t": scenario["t"],
            "z0": z0,
            "z1": z1,
        }
    except Exception as exc:
        logger.error(f"{prefix}  *** ERROR: {exc}")
        return {
            "idx": scenario["idx"],
            "label": scenario["label"],
            "connectivity": conn,
            "N": scenario["N"],
            "t": scenario["t"],
            "error": str(exc),
        }


# ===================================================================
# Plotting helper
# ===================================================================
def plot_combined_on_ax(
    ax_hist,
    z0,
    z1,
    title,
    bins=30,
    use_theta=True,
):
    if use_theta:
        data0, data1 = np.arccos(z0), np.arccos(z1)
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

    ax_r = ax_hist.twinx()
    ax_hist.bar(centers, h0d, width=bw, alpha=0.22, color="blue", label=d_label[0])
    ax_hist.bar(centers, h1d, width=bw, alpha=0.22, color="red", label=d_label[1])
    ax_r.plot(
        centers[mask],
        r0[mask],
        "o-",
        color="blue",
        ms=3,
        lw=1.2,
        label=r"$h_0/(h_0{+}h_1)$",
    )
    ax_r.plot(
        centers[mask],
        r1[mask],
        "o-",
        color="red",
        ms=3,
        lw=1.2,
        label=r"$h_1/(h_0{+}h_1)$",
    )
    ax_r.plot(x_th, born, "k--", lw=1, label="Born rule")
    ax_r.plot(x_th, 1 - born, "k--", lw=1)

    ax_r.set_ylim(0, 1.05)
    ax_hist.set_xlim(bin_edges[0], bin_edges[-1])
    ax_hist.set_xlabel(xlabel, fontsize=8)
    ax_hist.set_ylabel("Density", fontsize=7, color="gray")
    ax_hist.tick_params(axis="y", labelcolor="gray", labelsize=6)
    ax_r.set_ylabel("Fraction", fontsize=7)
    ax_r.tick_params(axis="y", labelsize=6)
    ax_hist.tick_params(axis="x", labelsize=6)
    ax_hist.set_title(title, fontsize=7, pad=4)


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Two-pixel size, connectivity & time scan"
    )
    parser.add_argument(
        "--no-theta",
        action="store_true",
        help="Plot in z-space instead of θ = arccos(z)",
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Save figures to file (e.g. tp_scan.png → tp_scan_chain.png, …)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (default: cpu_count)",
    )
    args = parser.parse_args()

    scenarios = build_scenarios()
    n = len(scenarios)
    use_theta = not args.no_theta
    n_workers = args.workers or cpu_count()

    # --- Set up logging (console + file) ---------------------------------
    from datetime import datetime

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"two_pixel_chain_size_scan_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== Two-Pixel Scan: {n} scenarios "
        f"({len(CONNECTIVITIES)} conn × {len(SYSTEM_SIZES)} sizes "
        f"× {len(TIMES)} times), {n_workers} workers ==="
    )
    logger.info(f"Log file: {log_file}")
    t0 = time.time()

    for i, s in enumerate(scenarios):
        s["idx"] = i
        s["total"] = n

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
    elapsed = time.time() - t0
    logger.info(f"Computation finished in {elapsed:.1f}s")
    if n_failed:
        logger.warning(f"{n_failed} scenario(s) skipped due to errors")

    # --- Group results by connectivity ----------------------------------
    results_by_conn: dict[str, list[dict]] = {}
    for res in results:
        results_by_conn.setdefault(res["connectivity"], []).append(res)

    space = r"$\theta$" if use_theta else "$z$"
    save_stem = Path(args.save).stem if args.save else None
    save_suffix = Path(args.save).suffix if args.save else None

    nrows = len(SYSTEM_SIZES)
    ncols = len(TIMES)

    for conn in CONNECTIVITIES:
        conn_results = results_by_conn.get(conn, [])
        if not conn_results:
            continue

        # Build a lookup: (N, t) → result
        lookup = {(r["N"], r["t"]): r for r in conn_results}

        fig, axes = plt.subplots(
            nrows,
            ncols,
            figsize=(4.2 * ncols, 3.5 * nrows),
            dpi=120,
            constrained_layout=True,
        )

        for row, N in enumerate(SYSTEM_SIZES):
            for col, t in enumerate(TIMES):
                ax = axes[row, col]
                res = lookup.get((N, t))
                if res is not None:
                    plot_combined_on_ax(
                        ax,
                        res["z0"],
                        res["z1"],
                        title=res["label"],
                        use_theta=use_theta,
                    )
                else:
                    ax.set_visible(False)

        conn_name = CONNECTIVITY_DISPLAY[conn]
        fig.suptitle(
            f"Two Pixel ({conn_name}, J=1, Jx=Jz=0.3) — "
            f"{space}-histograms & ratios",
            fontsize=13,
            fontweight="bold",
            y=1.01,
        )

        if args.save:
            out = f"{save_stem}_{conn}{save_suffix}"
            fig.savefig(out, bbox_inches="tight")
            logging.getLogger(__name__).info(f"Figure saved to {out}")

    if not args.save:
        plt.show()


if __name__ == "__main__":
    main()
