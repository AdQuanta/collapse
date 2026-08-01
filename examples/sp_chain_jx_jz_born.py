"""
Single-Pixel Chain – Jx × Jz Sweep  (Jpm=1, multiple hz, hz0∈{0,hz})
======================================================================

2-D sweep over ``Jx`` and ``Jz`` for several ``hz`` values, with
hx = 0, J = 1, Jpm = 1, open-chain connectivity.

Each ``hz`` value is run **twice**: once with ``hz0 = 0`` (no field on
the central qubit) and once with ``hz0 = hz`` (uniform field).

No translational symmetry is available for open-chain connectivity,
so the Hamiltonian is diagonalised in the full Hilbert space
(magnetisation sectors are still used when applicable).

Born-distribution similarity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the histogram ratio f(θ) = h₀/(h₀+h₁), define

    S = 1 − (1/π) ∫ dΩ |f(θ) − cos²(θ/2)|

S = 1 means perfect agreement with the Born rule.

Plots produced
~~~~~~~~~~~~~~~
1. **Histograms + Bloch** (per scenario):
   ``N={N}/histograms/hz={hz}_hz0={hz0}/Jx={Jx}_Jz={Jz}.png``

2. **Heatmaps** of *S* on the Jx–Jz plane (one per N, hz, hz0, time):
   ``N={N}/heatmaps/hz={hz}_hz0={hz0}/t={t}.png``

3. **Slices** of *S* vs Jx for each Jz (one per N, hz, hz0, time):
   ``N={N}/slices/hz={hz}_hz0={hz0}/t={t}.png``

Usage::

    python examples/sp_chain_jx_jz_born.py -N 9 --workers 4 --save figures/born_chain
    python examples/sp_chain_jx_jz_born.py -N 7 9 --save figures/born_chain
    python examples/sp_chain_jx_jz_born.py -N 9 --save figures/born_chain --hz-idx 3
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

from collapse.analysis import DisentanglementAnalyzer
from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

# ===================================================================
# Constants
# ===================================================================
TIMES = [1000.0, 10000.0, 100000.0, 1000000.0]
SEED = 44

JX_VALUES = np.round(np.logspace(np.log10(0.01), np.log10(10), 11), 4).tolist()
JZ_VALUES = np.round(np.logspace(np.log10(0.01), np.log10(10), 11), 4).tolist()
HZ_VALUES = np.round(np.logspace(np.log10(0.01), np.log10(10), 11), 4).tolist()

# Two modes for the central-qubit field
HZ0_MODES = ["hz0=0", "hz0=hz"]


# ===================================================================
# Born-similarity metric
# ===================================================================
def born_similarity(z0, z1, n_theta=100):
    r"""Compute Born-distribution similarity for the histogram ratio.

    Given Bloch-sphere z-components z0, z1 (for subsystems 0 and 1),
    build the angular histogram ratio f(θ) = h₀/(h₀+h₁) and return

        S = 1 − (1/π) ∫ dΩ |f(θ) − cos²(θ/2)|

    Since both f and cos²(θ/2) are independent of φ, the azimuthal
    integral contributes a factor of 2π:

        ∫ dΩ = 2π ∫₀^π |f(θ) − cos²(θ/2)| sin θ dθ

    so  S = 1 − 2 ∫₀^π |f(θ) − cos²(θ/2)| sin θ dθ.

    Calibration: S = 1 for perfect Born ratio, S = 0 for f = ½ everywhere.
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

    born = np.cos(theta_centers / 2) ** 2  # (1 + cos θ) / 2

    integrand = np.abs(ratio - born) * np.sin(theta_centers)
    integral = np.sum(integrand) * dtheta

    return 1.0 - 2.0 * integral


# ===================================================================
# Build all scenarios
# ===================================================================
def build_scenarios(N_list: list[int], hz_idx: int | None = None) -> list[dict]:
    """Enumerate N × Jx × Jz × hz × hz0_mode grid."""
    scenarios: list[dict] = []
    hz_list = [HZ_VALUES[hz_idx]] if hz_idx is not None else HZ_VALUES

    for N in N_list:
        N_pixel = N - 1
        for hz in hz_list:
            for hz0_mode in HZ0_MODES:
                hz0_val = 0.0 if hz0_mode == "hz0=0" else None  # None → same as hz
                for Jz in JZ_VALUES:
                    for Jx in JX_VALUES:
                        params = dict(
                            N_pixel=N_pixel,
                            J=0.0,
                            Jpm=1.0,
                            Jx=Jx,
                            Jz=Jz,
                            hx=0.0,
                            hz=hz,
                            hz0=hz0_val,
                            connectivity="chain",
                            seed=SEED,
                        )
                        hz0_disp = 0 if hz0_mode == "hz0=0" else hz
                        title_line = (
                            f"SP[chain,+-] N={N} | J=0  Jpm=1  "
                            f"Jx={Jx:g}  Jz={Jz:g}  "
                            f"hx=0  hz={hz:g}  hz0={hz0_disp:g}"
                        )
                        scenarios.append(
                            {
                                "title_line": title_line,
                                "model": "SP",
                                "cls": SinglePixelHamiltonianQuSpin,
                                "params": params,
                                "Jx": Jx,
                                "Jz": Jz,
                                "hz": hz,
                                "hz0_mode": hz0_mode,
                                "N": N,
                            }
                        )
    for i, s in enumerate(scenarios):
        s["idx"] = i
        s["total"] = len(scenarios)
    return scenarios


# ===================================================================
# Worker  (full diagonalisation — no ring symmetry for chain)
# ===================================================================
def _run_scenario(scenario: dict) -> dict:
    import os

    logger = logging.getLogger(__name__)
    title = scenario["title_line"]
    N_pixel = scenario["params"]["N_pixel"]
    N = N_pixel + 1
    prefix = (
        f"  [W{os.getpid()}] [{scenario['idx']+1:3d}/{scenario['total']:3d}] "
        f"{title:70s}"
    )
    try:
        t0 = time.time()
        ham = scenario["cls"](**scenario["params"])

        # Full diagonalisation (chain has no translational symmetry)
        t_diag = time.time()
        E, V = ham.diagonalize()
        logger.info(
            f"{prefix}  Diagonalized ({time.time()-t_diag:.1f}s)"
        )

        time_results = []
        for t_val in TIMES:
            analyzer = DisentanglementAnalyzer.from_eigenbasis(E, V, t_val)
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
            "Jx": scenario["Jx"],
            "Jz": scenario["Jz"],
            "hz": scenario["hz"],
            "hz0_mode": scenario["hz0_mode"],
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
            "Jx": scenario.get("Jx", 0),
            "Jz": scenario.get("Jz", 0),
            "hz": scenario.get("hz", 0),
            "hz0_mode": scenario.get("hz0_mode", ""),
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
# Plot type 1: Histograms + Bloch per scenario
# ===================================================================
def save_histograms(results, save_dir, logger):
    """Save per-scenario histogram + Bloch figures."""
    ntimes = len(TIMES)
    for res in results:
        if "error" in res:
            continue
        N, hz, Jx, Jz = res["N"], res["hz"], res["Jx"], res["Jz"]
        hz0_mode = res["hz0_mode"]
        tr = res["time_results"]

        out_dir = (
            save_dir / f"N={N}" / "histograms" / f"hz={hz:g}_{hz0_mode}"
        )
        out_dir.mkdir(parents=True, exist_ok=True)

        fig = plt.figure(
            figsize=(3.5 * ntimes, 7.0),
            dpi=120,
            constrained_layout=True,
        )
        for col, td in enumerate(tr):
            ax = fig.add_subplot(2, ntimes, col + 1)
            plot_histogram_on_ax(ax, td["z0"], td["z1"], title=f"t={td['t']:g}")
            ax3 = fig.add_subplot(2, ntimes, ntimes + col + 1, projection="3d")
            plot_bloch_on_ax(ax3, td, title=f"t={td['t']:g}")

        fig.suptitle(res["title_line"], fontsize=9, fontweight="bold", y=1.02)

        out = out_dir / f"Jx={Jx:g}_Jz={Jz:g}.png"
        fig.savefig(out, bbox_inches="tight", dpi=150)
        plt.close(fig)
        logger.info(f"Saved {out}")

# ===================================================================
# Plot type 2: Heatmaps of S on the Jx–Jz plane
# ===================================================================
def save_heatmaps(results, save_dir, logger):
    """One figure per (N, hz, hz0_mode, time) showing S on the Jx–Jz plane."""
    n_jx = len(JX_VALUES)
    n_jz = len(JZ_VALUES)
    jx_arr = np.array(JX_VALUES)
    jz_arr = np.array(JZ_VALUES)

    # Group: {(N, hz, hz0_mode): {(Jx, Jz): {t: S_ratio}}}
    groups: dict = {}
    for res in results:
        if "error" in res:
            continue
        key = (res["N"], res["hz"], res["hz0_mode"])
        if key not in groups:
            groups[key] = {}
        pt = (res["Jx"], res["Jz"])
        groups[key][pt] = {}
        for td in res["time_results"]:
            groups[key][pt][td["t"]] = td["S_ratio"]

    for (N, hz, hz0_mode), lookup in groups.items():
        out_dir = save_dir / f"N={N}" / "heatmaps" / f"hz={hz:g}_{hz0_mode}"
        out_dir.mkdir(parents=True, exist_ok=True)

        for t_val in TIMES:
            fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)

            grid = np.full((n_jz, n_jx), np.nan)
            for j, Jx in enumerate(JX_VALUES):
                for k, Jz in enumerate(JZ_VALUES):
                    pt = (Jx, Jz)
                    if pt in lookup and t_val in lookup[pt]:
                        grid[k, j] = lookup[pt][t_val]

            im = ax.pcolormesh(
                jx_arr,
                jz_arr,
                grid,
                cmap="RdYlGn",
                shading="nearest",
                vmin=0,
                vmax=1,
            )
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel(r"$J_x$", fontsize=10)
            ax.set_ylabel(r"$J_z$", fontsize=10)
            ax.set_title(
                rf"Born sim. $S$  |  SP[chain,$+-$]  $N={N}$,  "
                rf"$h_z={hz:g}$,  {hz0_mode},  $t={t_val:g}$",
                fontsize=10,
                fontweight="bold",
            )
            ax.tick_params(labelsize=8)
            plt.colorbar(im, ax=ax, pad=0.02, label="S")

            out = out_dir / f"t={t_val:g}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            plt.close(fig)
            logger.info(f"Saved {out}")


# ===================================================================
# Plot type 3: Slices of S vs Jx for each Jz
# ===================================================================
def save_slices(results, save_dir, logger):
    """One figure per (N, hz, hz0_mode, time), with S(Jx) curves coloured by Jz."""
    # Group: {(N, hz, hz0_mode): {Jz: {t: [(Jx, S), ...]}}}
    groups: dict = {}
    for res in results:
        if "error" in res:
            continue
        key = (res["N"], res["hz"], res["hz0_mode"])
        if key not in groups:
            groups[key] = {}
        Jz = res["Jz"]
        if Jz not in groups[key]:
            groups[key][Jz] = {t: [] for t in TIMES}
        for td in res["time_results"]:
            groups[key][Jz][td["t"]].append((res["Jx"], td["S_ratio"]))

    for (N, hz, hz0_mode), grouped in groups.items():
        for Jz in grouped:
            for t in TIMES:
                grouped[Jz][t].sort(key=lambda x: x[0])

        out_dir = save_dir / f"N={N}" / "slices" / f"hz={hz:g}_{hz0_mode}"
        out_dir.mkdir(parents=True, exist_ok=True)

        jz_sorted = sorted(grouped.keys())
        cmap = plt.cm.viridis
        colours = [
            cmap(i / max(1, len(jz_sorted) - 1)) for i in range(len(jz_sorted))
        ]

        for t_val in TIMES:
            fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
            for ci, Jz in enumerate(jz_sorted):
                entries = grouped[Jz][t_val]
                if not entries:
                    continue
                xs = [e[0] for e in entries]
                ys = [e[1] for e in entries]
                ax.plot(
                    xs,
                    ys,
                    "o-",
                    ms=3,
                    lw=1.2,
                    color=colours[ci],
                    label=f"Jz={Jz:g}",
                )
            ax.set_xscale("log")
            ax.set_xlabel(r"$J_x$", fontsize=10)
            ax.set_ylabel("S", fontsize=10)
            ax.set_ylim(-0.05, 1.05)
            ax.set_title(
                rf"Born sim. $S$ vs $J_x$  |  SP[chain,$+-$]  $N={N}$,  "
                rf"$h_z={hz:g}$,  {hz0_mode},  $t={t_val:g}$",
                fontsize=10,
                fontweight="bold",
            )
            ax.legend(fontsize=6, ncol=2, loc="lower left")
            ax.tick_params(labelsize=8)

            out = out_dir / f"t={t_val:g}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            plt.close(fig)
            logger.info(f"Saved {out}")


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description=(
            "SP chain – Jx × Jz sweep (multiple hz, hz0∈{0,hz}, Jpm=1). "
            "Supports multiple N values."
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
    parser.add_argument("--save", type=str, required=True)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument(
        "--hz-idx",
        type=int,
        default=None,
        help=(
            f"If given, run only the hz value at this index "
            f"(0..{len(HZ_VALUES)-1}).  Useful for splitting work across jobs."
        ),
    )
    args = parser.parse_args()

    if args.hz_idx is not None and not (0 <= args.hz_idx < len(HZ_VALUES)):
        parser.error(f"--hz-idx must be in 0..{len(HZ_VALUES)-1}")

    scenarios = build_scenarios(args.N_list, hz_idx=args.hz_idx)
    n_workers = args.workers or cpu_count()
    n = len(scenarios)

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_chain_jx_jz_born_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== SP Chain Jx × Jz Born-Similarity (Jpm=1, hz0∈{{0,hz}}): {n} scenarios "
        f"({len(JX_VALUES)}×{len(JZ_VALUES)}×{len(HZ_VALUES)} hz "
        f"× 2 hz0 modes × {len(args.N_list)} N), "
        f"N={args.N_list}, full diag, "
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

    # --- Histograms + Bloch ---
    logger.info("=== Saving histograms ===")
    save_histograms(results, save_dir, logger)

    # --- Heatmaps ---
    logger.info("=== Saving heatmaps ===")
    save_heatmaps(results, save_dir, logger)

    # --- Slices ---
    logger.info("=== Saving slices ===")
    save_slices(results, save_dir, logger)

    logger.info("All done.")


if __name__ == "__main__":
    main()
