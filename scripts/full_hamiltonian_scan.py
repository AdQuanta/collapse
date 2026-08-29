"""
Full Hamiltonian Scenario Scan (No Symmetries)
=================================================

Comprehensive scan of all four Hamiltonian models across physically
interesting parameter regimes, **without** exploiting symmetries.

Each scenario is evaluated at 10 time points and produces
z-histograms with Born-rule ratio overlays.

Usage::

    python scripts/full_hamiltonian_scan.py
    python scripts/full_hamiltonian_scan.py -N 5 --workers 1
    python scripts/full_hamiltonian_scan.py --save figures/scan
    python scripts/full_hamiltonian_scan.py --no-theta
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import logging
import time
from datetime import datetime
from math import sqrt
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians.quspin_hamiltonians import (
    CentralSpinHamiltonianQuSpin,
    MixedFieldIsingHamiltonianQuSpin,
    SinglePixelHamiltonianQuSpin,
    TwoPixelHamiltonianQuSpin,
)

# ===================================================================
# Constants
# ===================================================================
TIMES = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
SEED = 44

# Disorder scanning parameters
DISTRIBUTIONS = ["uniform", "gaussian", "lorentzian"]
STRENGTH_MULTS = [("weak", 0.3), ("medium", 1.0), ("strong", 3.0)]
# Base disorder amplitudes (coupling_amp, field_amp)
BASE_AMPS = {
    "CS": (2.0, 2.0),
    "MFI": (2.0, 8.0),
    "SP": (0.8, 0.8),
    "TP": (0.8, 0.5),
}

MODEL_NAMES = {
    "CS": "Central Spin",
    "MFI": "Mixed-Field Ising",
    "SP": "Single Pixel",
    "TP": "Two Pixel",
}


# ===================================================================
# Disorder helpers
# ===================================================================
def _scaled_sigma(A: float, dist: str, N: int) -> float:
    """N-scaled disorder strength."""
    return A / N if dist == "lorentzian" else A / sqrt(N)


def _disorder_scenarios(builder, N, model_key, component, param_key, extra_base=None):
    """Generate weak/medium/strong × uniform/gaussian/lorentzian scenarios."""
    A_coupling, A_field = BASE_AMPS[model_key]
    A_base = A_coupling if component == "coupling" else A_field
    scenarios = []
    for strength_name, mult in STRENGTH_MULTS:
        for dist in DISTRIBUTIONS:
            A = A_base * mult
            sigma = _scaled_sigma(A, dist, N)
            params = {"disorder": dist, f"disorder_strength_{param_key}": sigma}
            if extra_base:
                params.update(extra_base)
            label = (
                f"{component} {dist} {strength_name}\n"
                rf"$\sigma_{{{param_key}}}{{=}}{sigma:.3f}$"
            )
            scenarios.append(builder(N, label, params))
    return scenarios


# ===================================================================
# Scenario builder helpers
# ===================================================================
def _cs(N_total, label_suffix, extra_params):
    """Central Spin scenario."""
    base = dict(N_star=N_total - 1, Jx=0.0, Jz=1.0, seed=SEED)
    base.update(extra_params)
    return {
        "label": f"CS – {label_suffix}",
        "model": "CS",
        "cls": CentralSpinHamiltonianNumpy,
        "params": base,
    }


def _mfi(N_total, label_suffix, extra_params):
    """Mixed-field Ising scenario."""
    base = dict(N=N_total, J=1.0, hx=1.0, hz=0.0, seed=SEED)
    base.update(extra_params)
    return {
        "label": f"MFI – {label_suffix}",
        "model": "MFI",
        "cls": MixedFieldIsingHamiltonianNumpy,
        "params": base,
    }


def _sp(N_total, label_suffix, extra_params, connectivity="ring"):
    """Single Pixel scenario."""
    base = dict(
        N_pixel=N_total - 1,
        J=1.0,
        Jx=0.5,
        Jz=0.5,
        connectivity=connectivity,
        seed=SEED,
    )
    base.update(extra_params)
    conn_tag = connectivity.replace("_", "-")
    return {
        "label": f"SP[{conn_tag}] – {label_suffix}",
        "model": "SP",
        "cls": SinglePixelHamiltonianNumpy,
        "params": base,
    }


def _tp(N_total, label_suffix, extra_params, connectivity="ring"):
    """Two Pixel scenario."""
    base = dict(
        N_pixel=(N_total - 1) // 2,
        J=1.0,
        Jx=0.5,
        Jz=0.5,
        connectivity=connectivity,
        seed=SEED,
    )
    base.update(extra_params)
    conn_tag = connectivity.replace("_", "-")
    return {
        "label": f"TP[{conn_tag}] – {label_suffix}",
        "model": "TP",
        "cls": TwoPixelHamiltonianNumpy,
        "params": base,
    }


# ===================================================================
# Build all scenarios
# ===================================================================
def build_scenarios(N: int) -> dict[str, list[dict]]:
    """
    Return scenarios grouped by Hamiltonian model.

    Parameters
    ----------
    N : int
        Total number of qubits.
    """
    groups: dict[str, list[dict]] = {}

    # ---- Central Spin ------------------------------------------------
    # Coupling regimes
    cs = [
        _cs(N, r"clean Ising  $J_z{=}1$", {}),
        _cs(N, r"Heisenberg  $J_x{=}1,\;J_z{=}1$", dict(Jx=1.0)),
        _cs(N, r"XX-only  $J_x{=}1$", dict(Jx=1.0, Jz=0.0)),
        _cs(N, r"weak coupling  $J_x{=}0.1,\;J_z{=}0.1$", dict(Jx=0.1, Jz=0.1)),
        _cs(N, r"strong coupling  $J_x{=}3,\;J_z{=}3$", dict(Jx=3.0, Jz=3.0)),
        _cs(N, r"extremely weak  $J_x{=}0.01,\;J_z{=}0.01$", dict(Jx=0.01, Jz=0.01)),
        _cs(N, r"extremely strong  $J_x{=}10,\;J_z{=}10$", dict(Jx=10.0, Jz=10.0)),
        _cs(N, r"asymmetric  $J_x{=}0.3,\;J_z{=}0.8$", dict(Jx=0.3, Jz=0.8)),
    ]
    # Field regimes
    cs += [
        _cs(N, r"transverse field  $J_z{=}1,\;h_x{=}1$", dict(hx=1.0)),
        _cs(N, r"longitudinal field  $J_z{=}1,\;h_z{=}1$", dict(hz=1.0)),
        _cs(N, r"weak fields  $J_z{=}1,\;h{=}0.1$", dict(hx=0.1, hz=0.1)),
        _cs(N, r"strong fields  $J_z{=}1,\;h{=}3$", dict(hx=3.0, hz=3.0)),
        _cs(
            N,
            r"mixed fields  $J_x{=}1,\;J_z{=}1,\;h{=}0.5$",
            dict(Jx=1.0, hx=0.5, hz=0.5),
        ),
    ]
    # Disorder: coupling on Jx, coupling on Jz, field on hz
    cs += _disorder_scenarios(_cs, N, "CS", "coupling", "Jx", extra_base=dict(Jx=1.0))
    cs += _disorder_scenarios(_cs, N, "CS", "coupling", "Jz")
    cs += _disorder_scenarios(_cs, N, "CS", "field", "hz", extra_base=dict(hz=0.5))
    groups["CS"] = cs

    # ---- Mixed-field Ising -------------------------------------------
    # Field regimes (J=1 fixed)
    mfi = [
        _mfi(N, r"integrable  $h_x{=}1,\;h_z{=}0$", {}),
        _mfi(N, r"chaotic  $h_x{=}0.9045,\;h_z{=}0.809$", dict(hx=0.9045, hz=0.809)),
        _mfi(N, r"deep paramagnetic  $h_x{=}5$", dict(hx=5.0)),
        _mfi(N, r"longitudinal only  $h_x{=}0,\;h_z{=}1$", dict(hx=0.0, hz=1.0)),
        _mfi(N, r"weak fields  $h_x{=}0.1,\;h_z{=}0.1$", dict(hx=0.1, hz=0.1)),
        _mfi(N, r"strong transverse  $h_x{=}3$", dict(hx=3.0)),
        _mfi(N, r"mixed fields  $h_x{=}0.5,\;h_z{=}0.5$", dict(hx=0.5, hz=0.5)),
        _mfi(N, r"extremely weak fields  $h_x{=}0.01$", dict(hx=0.01)),
        _mfi(N, r"extremely strong fields  $h_x{=}10$", dict(hx=10.0)),
        _mfi(N, r"strong longitudinal  $h_z{=}3$", dict(hx=0.0, hz=3.0)),
    ]
    # Disorder: coupling on J, field on hz, field on hx
    mfi += _disorder_scenarios(_mfi, N, "MFI", "coupling", "J")
    mfi += _disorder_scenarios(_mfi, N, "MFI", "field", "hz", extra_base=dict(hx=0.5))
    mfi += _disorder_scenarios(_mfi, N, "MFI", "field", "hx")
    groups["MFI"] = mfi

    # ---- Single Pixel ------------------------------------------------
    sp: list[dict] = []
    connectivities = ["chain", "ring", "all_to_all"]
    # Coupling regimes
    sp_coupling_regimes = [
        (r"balanced  $J_x{=}0.5,\;J_z{=}0.5$", dict(Jx=0.5, Jz=0.5)),
        (r"weak central  $J_x{=}0.1,\;J_z{=}0.1$", dict(Jx=0.1, Jz=0.1)),
        (r"strong central  $J_x{=}1,\;J_z{=}1$", dict(Jx=1.0, Jz=1.0)),
        (r"XX-dominant  $J_x{=}1,\;J_z{=}0$", dict(Jx=1.0, Jz=0.0)),
        (r"ZZ-dominant  $J_x{=}0,\;J_z{=}1$", dict(Jx=0.0, Jz=1.0)),
        (r"asymmetric  $J_x{=}0.3,\;J_z{=}0.8$", dict(Jx=0.3, Jz=0.8)),
        (r"extremely weak  $J_x{=}0.01,\;J_z{=}0.01$", dict(Jx=0.01, Jz=0.01)),
        (r"extremely strong  $J_x{=}10,\;J_z{=}10$", dict(Jx=10.0, Jz=10.0)),
    ]
    # Field regimes
    sp_field_regimes = [
        (r"transverse field  $h_x{=}1$", dict(Jx=0.5, Jz=0.5, hx=1.0)),
        (r"longitudinal field  $h_z{=}1$", dict(Jx=0.5, Jz=0.5, hz=1.0)),
        (r"weak fields  $h{=}0.1$", dict(Jx=0.5, Jz=0.5, hx=0.1, hz=0.1)),
        (r"strong fields  $h{=}3$", dict(Jx=0.5, Jz=0.5, hx=3.0, hz=3.0)),
        (r"mixed fields  $h{=}0.5$", dict(Jx=0.5, Jz=0.5, hx=0.5, hz=0.5)),
    ]
    sp_clean_regimes = sp_coupling_regimes + sp_field_regimes
    for conn in connectivities:
        for label, params in sp_clean_regimes:
            sp.append(_sp(N, label, params, connectivity=conn))
    # Disorder (ring only): coupling on Jx, coupling on Jz, coupling on J,
    # field on hz, field on hx
    _sp_ring = lambda n, l, p: _sp(n, l, p, connectivity="ring")
    sp += _disorder_scenarios(_sp_ring, N, "SP", "coupling", "Jx")
    sp += _disorder_scenarios(_sp_ring, N, "SP", "coupling", "Jz")
    sp += _disorder_scenarios(_sp_ring, N, "SP", "coupling", "J")
    sp += _disorder_scenarios(_sp_ring, N, "SP", "field", "hz", extra_base=dict(hz=0.3))
    sp += _disorder_scenarios(_sp_ring, N, "SP", "field", "hx", extra_base=dict(hx=0.3))
    groups["SP"] = sp

    # ---- Two Pixel ---------------------------------------------------
    tp: list[dict] = []
    # Coupling regimes
    tp_coupling_regimes = [
        (r"symmetric  $J_x{=}0.5,\;J_z{=}0.5$", dict(Jx=0.5, Jz=0.5)),
        (r"XX-only  $J_x{=}1,\;J_z{=}0$", dict(Jx=1.0, Jz=0.0)),
        (r"ZZ-only  $J_x{=}0,\;J_z{=}1$", dict(Jx=0.0, Jz=1.0)),
        (r"weak central  $J_x{=}0.1,\;J_z{=}0.1$", dict(Jx=0.1, Jz=0.1)),
        (r"strong central  $J_x{=}1,\;J_z{=}1$", dict(Jx=1.0, Jz=1.0)),
        (r"asymmetric  $J_x{=}0.3,\;J_z{=}0.8$", dict(Jx=0.3, Jz=0.8)),
        (r"extremely weak  $J_x{=}0.01,\;J_z{=}0.01$", dict(Jx=0.01, Jz=0.01)),
        (r"extremely strong  $J_x{=}10,\;J_z{=}10$", dict(Jx=10.0, Jz=10.0)),
    ]
    # Field regimes
    tp_field_regimes = [
        (r"transverse field  $h_x{=}1$", dict(Jx=0.5, Jz=0.5, hx=1.0)),
        (r"longitudinal field  $h_z{=}1$", dict(Jx=0.5, Jz=0.5, hz=1.0)),
        (r"weak fields  $h{=}0.1$", dict(Jx=0.5, Jz=0.5, hx=0.1, hz=0.1)),
        (r"strong fields  $h{=}3$", dict(Jx=0.5, Jz=0.5, hx=3.0, hz=3.0)),
        (r"mixed fields  $h{=}0.5$", dict(Jx=0.5, Jz=0.5, hx=0.5, hz=0.5)),
    ]
    tp_clean_regimes = tp_coupling_regimes + tp_field_regimes
    for conn in connectivities:
        for label, params in tp_clean_regimes:
            tp.append(_tp(N, label, params, connectivity=conn))
    # Disorder (ring only): coupling on J, coupling on Jx, coupling on Jz,
    # field on hx, field on hz
    _tp_ring = lambda n, l, p: _tp(n, l, p, connectivity="ring")
    tp += _disorder_scenarios(_tp_ring, N, "TP", "coupling", "J")
    tp += _disorder_scenarios(_tp_ring, N, "TP", "coupling", "Jx")
    tp += _disorder_scenarios(_tp_ring, N, "TP", "coupling", "Jz")
    tp += _disorder_scenarios(_tp_ring, N, "TP", "field", "hx", extra_base=dict(hx=0.3))
    tp += _disorder_scenarios(_tp_ring, N, "TP", "field", "hz", extra_base=dict(hz=0.3))
    groups["TP"] = tp

    return groups


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
        f"  [W{os.getpid()}] [{scenario['idx']+1:2d}/{scenario['total']:2d}] "
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
            t2 = time.time()
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
            "model": scenario["model"],
            "error": str(exc),
        }


# ===================================================================
# Plotting helpers
# ===================================================================
def plot_histogram_on_ax(ax, z0, z1, title, bins=30, use_theta=True):
    """Draw combined density-histogram + ratio on *ax*."""
    if use_theta:
        data0, data1 = np.arccos(np.clip(z0, -1, 1)), np.arccos(np.clip(z1, -1, 1))
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
        description="Full Hamiltonian scenario scan (no symmetries)"
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
        help="Save figures to directory (e.g. figures/scan)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (default: cpu_count)",
    )
    args = parser.parse_args()

    scenario_groups = build_scenarios(args.N)
    use_theta = not args.no_theta
    n_workers = args.workers or cpu_count()

    # Flatten
    all_scenarios: list[dict] = []
    for model_scenarios in scenario_groups.values():
        all_scenarios.extend(model_scenarios)
    n = len(all_scenarios)

    # --- Logging setup ------------------------------------------------
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"full_hamiltonian_scan_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== Full Hamiltonian Scan: {n} scenarios, N={args.N} (D={2**args.N}), "
        f"{n_workers} workers, {len(TIMES)} time points ==="
    )
    logger.info(f"Log file: {log_file}")
    t_start = time.time()

    for i, s in enumerate(all_scenarios):
        s["idx"] = i
        s["total"] = n

    # --- Parallel computation -----------------------------------------
    if n_workers == 1:
        results_unordered = [_run_scenario(s) for s in all_scenarios]
    else:
        with Pool(n_workers) as pool:
            results_unordered = list(pool.imap_unordered(_run_scenario, all_scenarios))

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
        label = res["label"]
        label_short = label.split("\n")[0]
        tr = res["time_results"]

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
            f"{label_short} -- {space}-histograms",
            fontsize=10,
            fontweight="bold",
            y=1.02,
        )

        if save_dir:
            safe_name = (
                label_short.replace(" ", "_")
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
                .replace("\u2013", "-")
            )
            out = save_dir / f"{safe_name}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            logger.info(f"Saved {out}")
            plt.close(fig)

    if not args.save:
        plt.show()

    logger.info("All done.")


if __name__ == "__main__":
    main()
