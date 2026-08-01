"""
Comprehensive Parameter Scan
==============================

Runs a systematic survey of all four Hamiltonian models across
physically interesting parameter regimes. Each scenario generates
a Hamiltonian, evolves it in time, extracts per-qubit initial
states, and plots the combined z-histogram + ratio figure.

Heavy computation (Hamiltonian → U → disentanglement) is
parallelised with ``multiprocessing.Pool``.

Usage::

    python examples/parameter_scan.py                # θ-space (default)
    python examples/parameter_scan.py --no-theta      # z-space
    python examples/parameter_scan.py --save scan.png # save figure
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import time
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

from collapse.analysis import DisentanglementAnalyzer
from collapse.hamiltonians.quspin_hamiltonians import (
    CentralSpinHamiltonianQuSpin,
    MixedFieldIsingHamiltonianQuSpin,
    SinglePixelHamiltonianQuSpin,
    TwoPixelHamiltonianQuSpin,
)
from collapse.quantum_utils import generate_time_evolution_operator

# Default evolution time for all scenarios
T_DEFAULT = 10.0

# Base disorder amplitudes per model (actual σ = A/√N for uniform/gaussian, A/N for lorentzian)
# Each entry: (coupling_amplitude, field_amplitude)
BASE_AMPS = {
    "CS": (2.0, 2.0),  # Central Spin
    "MFI": (2.0, 8.0),  # Mixed-field Ising (field needs larger A for MBL regime)
    "SP": (0.8, 0.8),  # Single Pixel
    "TP": (0.8, 0.5),  # Two Pixel
}

# Strength multipliers applied to base amplitudes
STRENGTH_MULTS = [("weak", 0.3), ("medium", 1.0), ("strong", 3.0)]

# Disorder distributions to scan
DISTRIBUTIONS = ["uniform", "gaussian", "lorentzian"]


# ===================================================================
# Scenario builder helpers
# ===================================================================
def _cs(N_total, label_suffix, extra_params, t=T_DEFAULT):
    """Central Spin scenario.  N_star = N_total - 1."""
    base = dict(N_star=N_total - 1, Jx=0.0, Jz=1.0, seed=44)
    base.update(extra_params)
    return {
        "label": f"CS – {label_suffix}",
        "model": "CS",
        "cls": CentralSpinHamiltonianQuSpin,
        "params": base,
        "t": t,
    }


def _mfi(N_total, label_suffix, extra_params, t=T_DEFAULT):
    """Mixed-field Ising scenario.  N = N_total."""
    base = dict(N=N_total, J=1.0, hx=1.0, hz=0.0, seed=44)
    base.update(extra_params)
    return {
        "label": f"MFI – {label_suffix}",
        "model": "MFI",
        "cls": MixedFieldIsingHamiltonianQuSpin,
        "params": base,
        "t": t,
    }


def _sp(N_total, label_suffix, extra_params, t=T_DEFAULT):
    """Single Pixel scenario.  N_pixel = N_total - 1."""
    base = dict(N_pixel=N_total - 1, J=1.0, Jx=0.5, Jz=0.5, seed=44)
    base.update(extra_params)
    return {
        "label": f"SP – {label_suffix}",
        "model": "SP",
        "cls": SinglePixelHamiltonianQuSpin,
        "params": base,
        "t": t,
    }


def _tp(N_total, label_suffix, extra_params, t=T_DEFAULT):
    """Two Pixel scenario.  N_pixel = (N_total - 1) // 2."""
    base = dict(N_pixel=(N_total - 1) // 2, J=1.0, Jx=0.5, Jz=0.5, seed=44)
    base.update(extra_params)
    return {
        "label": f"TP – {label_suffix}",
        "model": "TP",
        "cls": TwoPixelHamiltonianQuSpin,
        "params": base,
        "t": t,
    }


# ===================================================================
# Disorder scenario generator
# ===================================================================
def _scaled_sigma(A: float, dist: str, N: int) -> float:
    """Compute the N-scaled disorder strength for a given base amplitude."""
    from math import sqrt

    return A / N if dist == "lorentzian" else A / sqrt(N)


def _disorder_scenarios(builder, N, model_key, component, param_key, extra_base=None):
    """
    Generate weak/medium/strong × uniform/gaussian/lorentzian scenarios
    for a single component (coupling or field) of a given model.

    Returns 9 scenario dicts (3 strengths × 3 distributions).
    """
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
# Scenario list builder
# ===================================================================
def build_scenarios(N: int) -> dict[str, list[dict]]:
    """
    Return scenarios grouped by Hamiltonian model for a given total system
    size *N*.

    Disorder strength scaling:
      - Uniform / Gaussian : σ = A / √N
      - Lorentzian         : σ = A / N

    Each disorder component is scanned at three regimes (weak / medium / strong)
    and three distributions (uniform / gaussian / lorentzian).

    The mapping from *N* to each Hamiltonian's size parameter:
      - CentralSpin     : N_star  = N - 1
      - MixedFieldIsing : N       = N
      - SinglePixel     : N_pixel = N - 1
      - TwoPixel        : N_pixel = (N - 1) // 2

    Returns
    -------
    dict[str, list[dict]]
        Keys are model short names ("CS", "MFI", "SP", "TP"), values are
        the corresponding scenario lists.
    """
    groups: dict[str, list[dict]] = {}

    # ---- Central Spin ------------------------------------------------
    cs = [
        _cs(N, "clean Ising\n" r"$J_z{=}1$", {}),
        _cs(N, "Heisenberg\n" r"$J_x{=}1,\;J_z{=}1$", dict(Jx=1.0)),
    ]
    cs += _disorder_scenarios(_cs, N, "CS", "coupling", "Jx")
    cs += _disorder_scenarios(_cs, N, "CS", "field", "hz", extra_base=dict(hz=0.5))
    groups["CS"] = cs

    # ---- Mixed-field Ising -------------------------------------------
    mfi = [
        _mfi(N, "integrable\n" r"$h_x{=}1,\;h_z{=}0$", {}),
        _mfi(N, "chaotic\n" r"$h_x{=}0.9045,\;h_z{=}0.809$", dict(hx=0.9045, hz=0.809)),
    ]
    mfi += _disorder_scenarios(_mfi, N, "MFI", "coupling", "J")
    mfi += _disorder_scenarios(_mfi, N, "MFI", "field", "hz", extra_base=dict(hx=0.5))
    groups["MFI"] = mfi

    # ---- Single Pixel ------------------------------------------------
    sp = [
        _sp(
            N,
            "ring dominated\n" r"$J{=}1,\;J_x{=}0.1,\;J_z{=}0.1$",
            dict(Jx=0.1, Jz=0.1),
        ),
        _sp(
            N,
            "central dominated\n" r"$J{=}0.1,\;J_x{=}1,\;J_z{=}1$",
            dict(J=0.1, Jx=1.0, Jz=1.0),
        ),
    ]
    sp += _disorder_scenarios(_sp, N, "SP", "coupling", "Jx")
    sp += _disorder_scenarios(_sp, N, "SP", "field", "hz", extra_base=dict(hz=0.3))
    groups["SP"] = sp

    # ---- Two Pixel ---------------------------------------------------
    tp = [
        _tp(N, "clean symmetric\n" r"$J_x{=}0.5,\;J_z{=}0.5$", {}),
        _tp(N, "XX only\n" r"$J_x{=}1,\;J_z{=}0$", dict(Jx=1.0, Jz=0.0)),
    ]
    tp += _disorder_scenarios(_tp, N, "TP", "coupling", "J")
    tp += _disorder_scenarios(_tp, N, "TP", "field", "hx", extra_base=dict(hx=0.3))
    groups["TP"] = tp

    return groups


# ===================================================================
# Worker function  (one per process)
# ===================================================================
def _run_scenario(scenario: dict) -> dict:
    """
    Build H → compute U = exp(-iHt) → disentangle → return z-components.

    If the scenario raises an exception the error is recorded and the
    result is marked so plotting can skip it gracefully.
    """
    label_short = scenario["label"].split("\n")[0]
    try:
        t0 = time.time()
        ham = scenario["cls"](**scenario["params"])
        H = ham.generate()
        U = generate_time_evolution_operator(H, scenario["t"])

        analyzer = DisentanglementAnalyzer(U)
        analyzer.diagonalize_subblocks_product()
        analyzer.get_initial_qubit_states_from_eigenvalues()

        z0 = np.abs(analyzer.phi0[:, 0]) ** 2 - np.abs(analyzer.phi0[:, 1]) ** 2
        z1 = np.abs(analyzer.phi1[:, 0]) ** 2 - np.abs(analyzer.phi1[:, 1]) ** 2
        elapsed = time.time() - t0
        print(
            f"  [{scenario['idx']+1:2d}/{scenario['total']:2d}] "
            f"{label_short:30s}  ({elapsed:.1f}s)"
        )
        return {
            "idx": scenario["idx"],
            "label": scenario["label"],
            "model": scenario["model"],
            "z0": z0,
            "z1": z1,
        }
    except Exception as exc:
        print(
            f"  [{scenario['idx']+1:2d}/{scenario['total']:2d}] "
            f"{label_short:30s}  *** ERROR: {exc}"
        )
        return {
            "idx": scenario["idx"],
            "label": scenario["label"],
            "model": scenario["model"],
            "error": str(exc),
        }


# ===================================================================
# Plotting helper  (axes-based, no plt.show())
# ===================================================================
def plot_combined_on_ax(
    ax_hist,
    z0: np.ndarray,
    z1: np.ndarray,
    title: str,
    bins: int = 30,
    use_theta: bool = True,
) -> None:
    """Draw the combined density-histogram + ratio plot on *ax_hist*."""
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

    # background: density
    ax_hist.bar(centers, h0d, width=bw, alpha=0.22, color="blue", label=d_label[0])
    ax_hist.bar(centers, h1d, width=bw, alpha=0.22, color="red", label=d_label[1])

    # foreground: ratio curves
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
# Full model names for figure titles
MODEL_NAMES = {
    "CS": "Central Spin",
    "MFI": "Mixed-Field Ising",
    "SP": "Single Pixel",
    "TP": "Two Pixel",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Comprehensive parameter scan")
    parser.add_argument(
        "-N",
        "--N",
        type=int,
        default=7,
        dest="N",
        help="Total number of qubits (default: 7). Each Hamiltonian adapts "
        "its size parameter accordingly.",
    )
    parser.add_argument(
        "--no-theta",
        action="store_true",
        help="Plot in z-space instead of θ = arccos(z)",
    )
    parser.add_argument(
        "--save", type=str, default=None, help="Save figure to file (e.g. scan.png)"
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

    # Flatten all scenarios for parallel computation
    all_scenarios = []
    for model_scenarios in scenario_groups.values():
        all_scenarios.extend(model_scenarios)
    n = len(all_scenarios)

    print(
        f"=== Parameter Scan: {n} scenarios, N={args.N} (D={2**args.N}), "
        f"{n_workers} workers ===\n"
    )
    t0 = time.time()

    # --- Parallel computation -------------------------------------------
    # Tag each scenario with its index for progress reporting & reordering
    for i, s in enumerate(all_scenarios):
        s["idx"] = i
        s["total"] = n

    with Pool(n_workers) as pool:
        results_unordered = list(pool.imap_unordered(_run_scenario, all_scenarios))

    # Restore original order and filter out failed scenarios
    results_all = sorted(results_unordered, key=lambda r: r["idx"])
    results = [r for r in results_all if "error" not in r]
    n_failed = len(results_all) - len(results)

    elapsed = time.time() - t0
    print(f"Computation finished in {elapsed:.1f}s")
    if n_failed:
        print(f"  ⚠ {n_failed} scenario(s) skipped due to errors\n")
    else:
        print()

    # --- Group results by model -----------------------------------------
    results_by_model: dict[str, list[dict]] = {}
    for res in results:
        results_by_model.setdefault(res["model"], []).append(res)

    # --- One figure per Hamiltonian model --------------------------------
    space = r"$\theta$" if use_theta else "$z$"
    save_stem = Path(args.save).stem if args.save else None
    save_suffix = Path(args.save).suffix if args.save else None

    for model_key, model_results in results_by_model.items():
        n_model = len(model_results)
        ncols = 4
        nrows = (n_model + ncols - 1) // ncols

        fig, axes = plt.subplots(
            nrows,
            ncols,
            figsize=(4.2 * ncols, 3.5 * nrows),
            dpi=120,
            constrained_layout=True,
        )
        axes_flat = np.asarray(axes).flatten() if n_model > 1 else [axes]

        for i, res in enumerate(model_results):
            plot_combined_on_ax(
                axes_flat[i],
                res["z0"],
                res["z1"],
                title=res["label"],
                use_theta=use_theta,
            )

        # Hide unused axes
        for j in range(n_model, len(axes_flat)):
            axes_flat[j].set_visible(False)

        full_name = MODEL_NAMES.get(model_key, model_key)
        fig.suptitle(
            f"{full_name} — {space}-histograms & ratios",
            fontsize=13,
            fontweight="bold",
            y=1.01,
        )

        if args.save:
            out = f"{save_stem}_{model_key}{save_suffix}"
            fig.savefig(out, bbox_inches="tight")
            print(f"Figure saved to {out}")

    if not args.save:
        plt.show()


if __name__ == "__main__":
    main()
