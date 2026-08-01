"""
Single-Pixel Ring – Jx × Jzx Sweep  (Jz=0, hz=1, born similarity)
====================================================================

2-D sweep over ``Jx`` and ``Jzx`` with **Jz = 0**, **hx = 0**, J = 1,
hz = hz0 = 1, ring connectivity.

Both ``Jx`` and ``Jzx`` are normalised by ``1/sqrt(N_pixel)``.

The ZX interaction adds a  σ^z_0 σ^x_i  coupling between the central
qubit and the pixel qubits.  Both XX and ZX terms break total-Sz
conservation, but the **cyclic pixel-shift symmetry** is preserved
(the sums Σ_i X_0 X_i and Σ_i Z_0 X_i are invariant under cyclic
permutation of the pixel sites).  Computation exploits this translational
symmetry via ``ham.diagonalize_sectors()`` and
``DisentanglementAnalyzer.from_sectors()``, giving a large speed-up.

Born-distribution similarity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the histogram ratio f(θ,φ) = h₀/(h₀+h₁), define

    S = 1 − (1/π) ∫ dΩ |f(θ,φ) − cos²(θ/2)|

where dΩ = sin θ dθ dφ and the Born distribution is cos²(θ/2).
S = 1 means perfect agreement.

Plots produced
~~~~~~~~~~~~~~~
1. **Histograms + Bloch** (per scenario):
   ``N={N}/histograms/Jzx={Jzx}/Jx={Jx}.png``

2. **Heatmaps** of *S* on the Jx–Jzx plane (one per N and time value):
   ``N={N}/heatmaps/t={t}.png``

3. **Slices** of *S* vs Jx for each Jzx (one per N and time value):
   ``N={N}/slices/t={t}.png``

Usage::

    python examples/sp_ring_jx_jzx_born.py -N 9 --workers 4 --save figures/born_jx_jzx
    python examples/sp_ring_jx_jzx_born.py -N 7 9 11 --save figures/born_jx_jzx
    python examples/sp_ring_jx_jzx_born.py -N 9 --save figures/born_jx_jzx --jzx-idx 3
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
TIMES = [1000.0]
SEED = 44

JX_VALUES = np.round(np.logspace(np.log10(0.01), np.log10(10), 11), 4).tolist()
JZX_VALUES = np.round(np.logspace(np.log10(0.01), np.log10(10), 11), 4).tolist()

HZ_DEFAULT = 1.0  # fixed longitudinal field


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

    # S = 1 − (1/π) · 2π · ∫₀^π |f − born| sin θ dθ
    #   = 1 − 2 · Σᵢ |fᵢ − bornᵢ| sin(θᵢ) Δθ
    integrand = np.abs(ratio - born) * np.sin(theta_centers)
    integral = np.sum(integrand) * dtheta  # ≈ ∫₀^π |f − born| sin θ dθ

    return 1.0 - 2.0 * integral


# ===================================================================
# Build all scenarios
# ===================================================================
def build_scenarios(
    N_list: list[int],
    hz: float,
    jzx_idx: int | None = None,
) -> list[dict]:
    """Enumerate N × Jx × Jzx grid.  Both Jx and Jzx scaled by 1/√N_pixel."""
    scenarios: list[dict] = []
    jzx_list = [JZX_VALUES[jzx_idx]] if jzx_idx is not None else JZX_VALUES

    for N in N_list:
        N_pixel = N - 1
        for Jzx in jzx_list:
            Jzx_s = Jzx / np.sqrt(N_pixel)
            for Jx in JX_VALUES:
                Jx_s = Jx / np.sqrt(N_pixel)
                params = dict(
                    N_pixel=N_pixel,
                    J=1.0,
                    Jx=Jx_s,
                    Jz=0.0,
                    Jzx=Jzx_s,
                    hx=0.0,
                    hz=hz,
                    hz0=None,  # central qubit uses same hz
                    connectivity="ring",
                    seed=SEED,
                    use_symmetry=True,
                )
                title_line = (
                    f"SP[ring] N={N} | J=1  Jx={Jx:g}/√{N_pixel}  "
                    f"Jzx={Jzx:g}/√{N_pixel}  Jz=0  "
                    f"hx=0  hz=hz0={hz:g}"
                )
                scenarios.append(
                    {
                        "title_line": title_line,
                        "model": "SP",
                        "cls": SinglePixelHamiltonianQuSpin,
                        "params": params,
                        "Jx": Jx,
                        "Jzx": Jzx,
                        "N": N,
                    }
                )
    for i, s in enumerate(scenarios):
        s["idx"] = i
        s["total"] = len(scenarios)
    return scenarios


# ===================================================================
# Worker  (uses translational symmetry sectors)
# ===================================================================
def _run_scenario(scenario: dict) -> dict:
    import os

    logger = logging.getLogger(__name__)
    title = scenario["title_line"]
    N_pixel = scenario["params"]["N_pixel"]
    N = N_pixel + 1
    prefix = (
        f"  [W{os.getpid()}] [{scenario['idx']+1:3d}/{scenario['total']:3d}] "
        f"{title:60s}"
    )
    try:
        t0 = time.time()
        ham = scenario["cls"](**scenario["params"])

        # Use symmetry sectors (cyclic pixel shift is conserved)
        t_sec = time.time()
        sectors = ham.diagonalize_sectors()
        logger.info(
            f"{prefix}  Sectors ({len(sectors)}) built "
            f"({time.time()-t_sec:.1f}s)"
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

            # Born-similarity for the ratio
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
            "Jzx": scenario["Jzx"],
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
            "Jzx": scenario.get("Jzx", 0),
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
    """Save per-scenario histogram + Bloch figures, organised in N=/Jzx= folders."""
    ntimes = len(TIMES)
    for res in results:
        if "error" in res:
            continue
        N, Jzx, Jx = res["N"], res["Jzx"], res["Jx"]
        tr = res["time_results"]

        out_dir = save_dir / f"N={N}" / "histograms" / f"Jzx={Jzx:g}"
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

        out = out_dir / f"Jx={Jx:g}.png"
        fig.savefig(out, bbox_inches="tight", dpi=150)
        plt.close(fig)
        logger.info(f"Saved {out}")

# ===================================================================
# Plot type 2: Heatmaps of S on the Jx–Jzx plane
# ===================================================================
def save_heatmaps(results, save_dir, logger):
    """One figure per (N, time) showing S on the Jx–Jzx plane."""
    n_jx = len(JX_VALUES)
    n_jzx = len(JZX_VALUES)
    jx_arr = np.array(JX_VALUES)
    jzx_arr = np.array(JZX_VALUES)

    # Group by N: {N: {(Jx, Jzx): {t: S_ratio}}}
    by_N: dict[int, dict[tuple[float, float], dict[float, float]]] = {}
    for res in results:
        if "error" in res:
            continue
        N = res["N"]
        if N not in by_N:
            by_N[N] = {}
        key = (res["Jx"], res["Jzx"])
        by_N[N][key] = {}
        for td in res["time_results"]:
            by_N[N][key][td["t"]] = td["S_ratio"]

    for N, lookup in by_N.items():
        out_dir = save_dir / f"N={N}" / "heatmaps"
        out_dir.mkdir(parents=True, exist_ok=True)

        for t_val in TIMES:
            fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)

            grid = np.full((n_jzx, n_jx), np.nan)
            for j, Jx in enumerate(JX_VALUES):
                for k, Jzx in enumerate(JZX_VALUES):
                    key = (Jx, Jzx)
                    if key in lookup and t_val in lookup[key]:
                        grid[k, j] = lookup[key][t_val]

            im = ax.pcolormesh(
                jx_arr,
                jzx_arr,
                grid,
                cmap="RdYlGn",
                shading="nearest",
                vmin=0,
                vmax=1,
            )
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel(r"$J_x$  (unscaled)", fontsize=10)
            ax.set_ylabel(r"$J_{zx}$  (unscaled)", fontsize=10)
            ax.set_title(
                rf"Born sim. $S$  |  $N={N}$,  $t={t_val:g}$",
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
# Plot type 3: Slices of S vs Jx for each Jzx
# ===================================================================
def save_slices(results, save_dir, logger):
    """One figure per (N, time), with S(Jx) curves coloured by Jzx."""
    # Group by N: {N: {Jzx: {t: [(Jx, S_ratio), ...]}}}
    by_N: dict[int, dict[float, dict[float, list]]] = {}
    for res in results:
        if "error" in res:
            continue
        N = res["N"]
        if N not in by_N:
            by_N[N] = {}
        Jzx = res["Jzx"]
        if Jzx not in by_N[N]:
            by_N[N][Jzx] = {t: [] for t in TIMES}
        for td in res["time_results"]:
            by_N[N][Jzx][td["t"]].append((res["Jx"], td["S_ratio"]))

    for N, grouped in by_N.items():
        for Jzx in grouped:
            for t in TIMES:
                grouped[Jzx][t].sort(key=lambda x: x[0])

        out_dir = save_dir / f"N={N}" / "slices"
        out_dir.mkdir(parents=True, exist_ok=True)

        jzx_sorted = sorted(grouped.keys())
        cmap = plt.cm.viridis
        colours = [cmap(i / max(1, len(jzx_sorted) - 1)) for i in range(len(jzx_sorted))]

        for t_val in TIMES:
            fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
            for ci, Jzx in enumerate(jzx_sorted):
                entries = grouped[Jzx][t_val]
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
                    label=rf"$J_{{zx}}$={Jzx:g}",
                )
            ax.set_xscale("log")
            ax.set_xlabel(r"$J_x$  (unscaled)", fontsize=10)
            ax.set_ylabel("S", fontsize=10)
            ax.set_ylim(-0.05, 1.05)
            ax.set_title(
                rf"Born sim. $S$ vs $J_x$  |  $N={N}$,  $t={t_val:g}$",
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
            "SP ring – Jx × Jzx sweep (Jz=0, hz=hz0=const). "
            "Jx, Jzx scaled by 1/√N_pixel.  Supports multiple N values."
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
        "--hz",
        type=float,
        default=HZ_DEFAULT,
        help=f"Longitudinal field hz=hz0 (default: {HZ_DEFAULT})",
    )
    parser.add_argument(
        "--jzx-idx",
        type=int,
        default=None,
        help=(
            f"If given, run only the Jzx value at this index "
            f"(0..{len(JZX_VALUES)-1}).  Useful for splitting work across jobs."
        ),
    )
    args = parser.parse_args()

    if args.jzx_idx is not None and not (0 <= args.jzx_idx < len(JZX_VALUES)):
        parser.error(f"--jzx-idx must be in 0..{len(JZX_VALUES)-1}")

    scenarios = build_scenarios(args.N_list, hz=args.hz, jzx_idx=args.jzx_idx)
    n_workers = args.workers or cpu_count()
    n = len(scenarios)

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_ring_jx_jzx_born_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== SP Ring Jx × Jzx Born-Similarity (Jz=0, hz=hz0={args.hz}): {n} scenarios "
        f"({len(JX_VALUES)}×{len(JZX_VALUES)}×{len(args.N_list)} N values), "
        f"N={args.N_list}, sectors, "
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
