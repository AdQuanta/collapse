"""
Two-Pixel Connectivity & Coupling-Ratio Scan
================================================

Systematic survey of the two-pixel Hamiltonian across:

* **Connectivity modes**: chain, ring, all-to-all
* **Coupling-ratio regimes**: various (J, Jx, Jz) combinations

No disorder is applied and hx = hz = 0.

For each scenario the script constructs the Hamiltonian, evolves it in
time, extracts per-qubit initial states via
:class:`~core.analysis.DisentanglementAnalyzer`, and plots the
combined θ-histogram + ratio figure.

Usage::

    python scripts/two_pixel_connectivity_scan.py
    python scripts/two_pixel_connectivity_scan.py --no-theta
    python scripts/two_pixel_connectivity_scan.py --save tp_conn.png
    python scripts/two_pixel_connectivity_scan.py -N 9
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import time
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians.quspin_hamiltonians import TwoPixelHamiltonianQuSpin
from core.quantum_utils import generate_time_evolution_operator

# Default evolution time
T_DEFAULT = 10.0

# Connectivity modes to scan
CONNECTIVITIES = ["chain", "ring", "all_to_all"]

# Coupling-ratio regimes  (label, J, Jx, Jz)
# J  = intra-pixel ZZ,  Jx = central↔pixel XX,  Jz = central↔pixel ZZ
RATIO_REGIMES = [
    # --- Balanced ---
    (r"balanced" "\n" r"$J{=}1,\;J_x{=}1,\;J_z{=}1$", 1.0, 1.0, 1.0),
    # --- Intra-pixel dominated ---
    (r"intra-pixel dom." "\n" r"$J{=}1,\;J_x{=}0.1,\;J_z{=}0.1$", 1.0, 0.1, 0.1),
    # --- Central coupling dominated ---
    (r"central dom." "\n" r"$J{=}0.1,\;J_x{=}1,\;J_z{=}1$", 0.1, 1.0, 1.0),
    # --- XX-only central coupling ---
    (r"XX-only central" "\n" r"$J{=}1,\;J_x{=}1,\;J_z{=}0$", 1.0, 1.0, 0.0),
    # --- ZZ-only central coupling ---
    (r"ZZ-only central" "\n" r"$J{=}1,\;J_x{=}0,\;J_z{=}1$", 1.0, 0.0, 1.0),
    # --- No intra-pixel (pure star) ---
    (r"no intra-pixel" "\n" r"$J{=}0,\;J_x{=}1,\;J_z{=}1$", 0.0, 1.0, 1.0),
    # --- Weak central coupling ---
    (r"weak central" "\n" r"$J{=}1,\;J_x{=}0.3,\;J_z{=}0.3$", 1.0, 0.3, 0.3),
    # --- Strong central coupling ---
    (r"strong central" "\n" r"$J{=}0.3,\;J_x{=}1,\;J_z{=}1$", 0.3, 1.0, 1.0),
]

CONNECTIVITY_DISPLAY = {
    "chain": "Chain",
    "ring": "Ring",
    "all_to_all": "All-to-All",
}


# ===================================================================
# Scenario builder
# ===================================================================
def build_scenarios(N: int) -> list[dict]:
    """
    Build the full scenario list: connectivity × coupling-ratio.

    Parameters
    ----------
    N : int
        Total qubit count.  ``N_pixel = (N - 1) // 2``.
    """
    N_pixel = (N - 1) // 2
    scenarios: list[dict] = []

    for conn in CONNECTIVITIES:
        for ratio_label, J, Jx, Jz in RATIO_REGIMES:
            label = f"{CONNECTIVITY_DISPLAY[conn]} – {ratio_label}"
            scenarios.append(
                {
                    "label": label,
                    "connectivity": conn,
                    "cls": TwoPixelHamiltonianQuSpin,
                    "params": dict(
                        N_pixel=N_pixel,
                        J=J,
                        Jx=Jx,
                        Jz=Jz,
                        hx=0.0,
                        hz=0.0,
                        connectivity=conn,
                        seed=44,
                    ),
                    "t": T_DEFAULT,
                }
            )
    return scenarios


# ===================================================================
# Worker function
# ===================================================================
def _run_scenario(scenario: dict) -> dict:
    """Build H → U → disentangle → return z-components."""
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
            f"{label_short:35s}  ({elapsed:.1f}s)"
        )
        return {
            "idx": scenario["idx"],
            "label": scenario["label"],
            "connectivity": scenario["connectivity"],
            "z0": z0,
            "z1": z1,
        }
    except Exception as exc:
        print(
            f"  [{scenario['idx']+1:2d}/{scenario['total']:2d}] "
            f"{label_short:35s}  *** ERROR: {exc}"
        )
        return {
            "idx": scenario["idx"],
            "label": scenario["label"],
            "connectivity": scenario["connectivity"],
            "error": str(exc),
        }


# ===================================================================
# Plotting helper
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
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Two-pixel connectivity & coupling-ratio scan"
    )
    parser.add_argument(
        "-N",
        "--N",
        type=int,
        default=7,
        dest="N",
        help="Total number of qubits (default: 7). N_pixel = (N-1)//2.",
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
        help="Save figure(s) to file (e.g. tp_conn.png)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (default: cpu_count)",
    )
    args = parser.parse_args()

    scenarios = build_scenarios(args.N)
    n = len(scenarios)
    use_theta = not args.no_theta
    n_workers = args.workers or cpu_count()
    N_pixel = (args.N - 1) // 2

    print(
        f"=== Two-Pixel Connectivity Scan: {n} scenarios, "
        f"N={args.N}, N_pixel={N_pixel} (D={2**args.N}), "
        f"{n_workers} workers ===\n"
    )
    t0 = time.time()

    for i, s in enumerate(scenarios):
        s["idx"] = i
        s["total"] = n

    with Pool(n_workers) as pool:
        results_unordered = list(pool.imap_unordered(_run_scenario, scenarios))

    results_all = sorted(results_unordered, key=lambda r: r["idx"])
    results = [r for r in results_all if "error" not in r]
    n_failed = len(results_all) - len(results)

    elapsed = time.time() - t0
    print(f"\nComputation finished in {elapsed:.1f}s")
    if n_failed:
        print(f"  ⚠ {n_failed} scenario(s) skipped due to errors\n")

    # --- Layout: one figure per connectivity mode -----------------------
    # rows = ratio regimes, grouped by connectivity
    results_by_conn: dict[str, list[dict]] = {}
    for res in results:
        results_by_conn.setdefault(res["connectivity"], []).append(res)

    space = r"$\theta$" if use_theta else "$z$"
    save_stem = Path(args.save).stem if args.save else None
    save_suffix = Path(args.save).suffix if args.save else None

    for conn, conn_results in results_by_conn.items():
        n_res = len(conn_results)
        ncols = 4
        nrows = (n_res + ncols - 1) // ncols

        fig, axes = plt.subplots(
            nrows,
            ncols,
            figsize=(4.2 * ncols, 3.5 * nrows),
            dpi=120,
            constrained_layout=True,
        )
        axes_flat = np.asarray(axes).flatten() if n_res > 1 else [axes]

        for i, res in enumerate(conn_results):
            plot_combined_on_ax(
                axes_flat[i],
                res["z0"],
                res["z1"],
                title=res["label"],
                use_theta=use_theta,
            )

        for j in range(n_res, len(axes_flat)):
            axes_flat[j].set_visible(False)

        conn_name = CONNECTIVITY_DISPLAY[conn]
        fig.suptitle(
            f"Two Pixel ({conn_name}) — {space}-histograms & ratios",
            fontsize=13,
            fontweight="bold",
            y=1.01,
        )

        if args.save:
            out = f"{save_stem}_{conn}{save_suffix}"
            fig.savefig(out, bbox_inches="tight")
            print(f"Figure saved to {out}")

    if not args.save:
        plt.show()


if __name__ == "__main__":
    main()
