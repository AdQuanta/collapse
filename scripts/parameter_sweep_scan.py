"""
Parameter Sweep Scan (No Disorder)
====================================

Sweep Jx, Jz, hx, hz one-at-a-time for CentralSpin, SinglePixel
(chain/ring/all-to-all), and TwoPixel (chain/ring/all-to-all).
J = 1 throughout; no disorder.

Each scenario is evaluated at 10 time points and produces
z-histograms with Born-rule ratio overlays.

Usage::

    python scripts/parameter_sweep_scan.py
    python scripts/parameter_sweep_scan.py -N 5 --workers 1
    python scripts/parameter_sweep_scan.py --save figures/sweep
    python scripts/parameter_sweep_scan.py --no-theta
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
from core.hamiltonians.quspin_hamiltonians import (
    CentralSpinHamiltonianQuSpin,
    SinglePixelHamiltonianQuSpin,
    TwoPixelHamiltonianQuSpin,
)

# ===================================================================
# Constants
# ===================================================================
TIMES = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
SEED = 44

# Sweep values for each parameter
SWEEP_VALUES = [0.0, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]

# Connectivities for pixel models
SP_TP_CONNECTIVITIES = ["chain", "ring", "all_to_all"]

# Model baselines (parameter values when *not* being swept)
CS_BASELINE = dict(Jx=1.0, Jz=0.0, hx=0.0, hz=0.0)
SP_BASELINE = dict(Jx=0.5, Jz=0.5, hx=0.0, hz=0.0)
TP_BASELINE = dict(Jx=0.5, Jz=0.5, hx=0.0, hz=0.0)


# ===================================================================
# Scenario builders
# ===================================================================
def _make_cs_scenario(N_total, sweep_param, sweep_val, baseline):
    """Build a single CentralSpin scenario dict."""
    params = dict(N_star=N_total - 1, seed=SEED)
    for k, v in baseline.items():
        params[k] = v
    params[sweep_param] = sweep_val

    label = (
        f"CS – {sweep_param}={sweep_val:g}\n"
        rf"$J_x{{{params['Jx']:g}}},\;J_z{{{params['Jz']:g}}},\;"
        rf"h_x{{{params['hx']:g}}},\;h_z{{{params['hz']:g}}}$"
    )
    title_line = (
        f"CS | Jx={params['Jx']:g}  Jz={params['Jz']:g}  "
        f"hx={params['hx']:g}  hz={params['hz']:g}"
    )
    return {
        "label": label,
        "title_line": title_line,
        "model": "CS",
        "cls": CentralSpinHamiltonianQuSpin,
        "params": params,
    }


def _make_sp_scenario(N_total, sweep_param, sweep_val, baseline, connectivity):
    """Build a single SinglePixel scenario dict."""
    params = dict(N_pixel=N_total - 1, J=1.0, connectivity=connectivity, seed=SEED)
    for k, v in baseline.items():
        params[k] = v
    params[sweep_param] = sweep_val

    conn_tag = connectivity.replace("_", "-")
    label = (
        f"SP[{conn_tag}] – {sweep_param}={sweep_val:g}\n"
        rf"$J{{{params['J']:g}}},\;J_x{{{params['Jx']:g}}},\;J_z{{{params['Jz']:g}}},\;"
        rf"h_x{{{params['hx']:g}}},\;h_z{{{params['hz']:g}}}$"
    )
    title_line = (
        f"SP[{conn_tag}] | J={params['J']:g}  Jx={params['Jx']:g}  "
        f"Jz={params['Jz']:g}  hx={params['hx']:g}  hz={params['hz']:g}"
    )
    return {
        "label": label,
        "title_line": title_line,
        "model": "SP",
        "cls": SinglePixelHamiltonianQuSpin,
        "params": params,
    }


def _make_tp_scenario(N_total, sweep_param, sweep_val, baseline, connectivity):
    """Build a single TwoPixel scenario dict."""
    params = dict(
        N_pixel=(N_total - 1) // 2,
        J=1.0,
        connectivity=connectivity,
        seed=SEED,
    )
    for k, v in baseline.items():
        params[k] = v
    params[sweep_param] = sweep_val

    conn_tag = connectivity.replace("_", "-")
    label = (
        f"TP[{conn_tag}] – {sweep_param}={sweep_val:g}\n"
        rf"$J{{{params['J']:g}}},\;J_x{{{params['Jx']:g}}},\;J_z{{{params['Jz']:g}}},\;"
        rf"h_x{{{params['hx']:g}}},\;h_z{{{params['hz']:g}}}$"
    )
    title_line = (
        f"TP[{conn_tag}] | J={params['J']:g}  Jx={params['Jx']:g}  "
        f"Jz={params['Jz']:g}  hx={params['hx']:g}  hz={params['hz']:g}"
    )
    return {
        "label": label,
        "title_line": title_line,
        "model": "TP",
        "cls": TwoPixelHamiltonianQuSpin,
        "params": params,
    }


# ===================================================================
# Build all scenarios
# ===================================================================
def build_scenarios(N: int) -> list[dict]:
    """
    Enumerate all parameter-sweep scenarios.

    For each model (and connectivity variant), sweep Jx, Jz, hx, hz
    one at a time over ``SWEEP_VALUES`` while keeping the other
    parameters at baseline.

    Parameters
    ----------
    N : int
        Total number of qubits.

    Returns
    -------
    list[dict]
        Flat list of scenario dicts, globally numbered.
    """
    sweep_params = ["Jx", "Jz", "hx", "hz"]
    scenarios: list[dict] = []

    # ---- Central Spin ------------------------------------------------
    for param in sweep_params:
        for val in SWEEP_VALUES:
            scenarios.append(_make_cs_scenario(N, param, val, CS_BASELINE))

    # ---- Single Pixel ------------------------------------------------
    for conn in SP_TP_CONNECTIVITIES:
        for param in sweep_params:
            for val in SWEEP_VALUES:
                scenarios.append(_make_sp_scenario(N, param, val, SP_BASELINE, conn))

    # ---- Two Pixel ---------------------------------------------------
    for conn in SP_TP_CONNECTIVITIES:
        for param in sweep_params:
            for val in SWEEP_VALUES:
                scenarios.append(_make_tp_scenario(N, param, val, TP_BASELINE, conn))

    # Assign global indices
    for i, s in enumerate(scenarios):
        s["idx"] = i
        s["total"] = len(scenarios)

    return scenarios


# ===================================================================
# Worker
# ===================================================================
def _run_scenario(scenario: dict) -> dict:
    """
    Build H → diagonalize once → loop over times → extract z-data.

    Returns a dict with z0/z1 per time point.
    """
    import os

    logger = logging.getLogger(__name__)
    label_short = scenario["label"].split("\n")[0]
    prefix = (
        f"  [W{os.getpid()}] [{scenario['idx']+1:3d}/{scenario['total']:3d}] "
        f"{label_short:50s}"
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

            time_results.append({"t": t_val, "z0": z0, "z1": z1})

        elapsed = time.time() - t0
        logger.info(f"{prefix}  Done ({elapsed:.1f}s)")
        return {
            "idx": scenario["idx"],
            "label": scenario["label"],
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
            "label": scenario["label"],
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


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Parameter sweep scan – Jx/Jz/hx/hz (no disorder, J=1)"
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
        "--save",
        type=str,
        default=None,
        help="Save figures to directory (e.g. figures/sweep)",
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
    log_file = log_dir / f"parameter_sweep_scan_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== Parameter Sweep Scan: {n} scenarios, N={args.N} (D={2**args.N}), "
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

    # --- Plot: one figure per scenario (all times in one row) ----------
    space = r"$\theta$" if use_theta else "$z$"
    ntimes = len(TIMES)

    for res in results:
        title_line = res["title_line"]
        tr = res["time_results"]
        idx = res["idx"]

        fig, axes = plt.subplots(
            1,
            ntimes,
            figsize=(3.5 * ntimes, 3.5),
            dpi=120,
            constrained_layout=True,
        )
        if ntimes == 1:
            axes = [axes]

        for col, td in enumerate(tr):
            plot_histogram_on_ax(
                axes[col],
                td["z0"],
                td["z1"],
                title=f"t={td['t']:g}",
                use_theta=use_theta,
            )

        fig.suptitle(
            f"#{idx+1:03d}  {title_line} -- {space}-histograms",
            fontsize=10,
            fontweight="bold",
            y=1.02,
        )

        if save_dir:
            # Build a filesystem-safe name with the scenario number
            safe_name = (
                title_line.replace(" ", "_")
                .replace("/", "-")
                .replace("\\", "-")
                .replace("$", "")
                .replace(",", "")
                .replace(";", "")
                .replace("{", "")
                .replace("}", "")
                .replace("=", "")
                .replace("[", "")
                .replace("]", "")
                .replace("|", "_")
                .replace("\u2013", "-")
            )
            out = save_dir / f"{idx+1:03d}_{safe_name}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            logger.info(f"Saved {out}")
            plt.close(fig)

    if not args.save:
        plt.show()

    logger.info("All done.")


if __name__ == "__main__":
    main()
