"""
Single-Pixel Ring – Jx × Jz × hz Sweep  (no central field, hz0=0)
===================================================================

3-D parameter sweep over ``Jx``, ``Jz``, and ``hz`` with **hz0 = 0**
(no field on the central qubit), hx = 0, J = 1, ring connectivity.

The intra-pixel couplings ``Jx``, ``Jz`` and the detector field ``hz``
are scaled by ``1 / N_pixel`` to keep the energy per spin O(1).

Sweep ranges
~~~~~~~~~~~~
* ``Jx``: 15 log-spaced values from 0.01 to 10
* ``Jz``: 10 log-spaced values from 0.01 to 10
* ``hz``: [0.1, 0.5, 1.0, 5.0]

Total scenarios = 15 × 10 × 4 = 600.

Three types of plots are produced (all saved progressively):

1. **Histograms + Bloch** (per scenario):
   ``histograms/hz={hz}/Jz={Jz}/Jx={Jx}.png``

2. **SH curves vs Jx** (per hz, Jz):
   ``sh_curves/hz={hz}/Jz={Jz}_{density|ratio}.png``

3. **SH heatmaps on Jx–Jz plane** (per hz, time):
   ``sh_heatmaps/hz={hz}/t={t}_{density|ratio}.png``

Usage::

    python examples/sp_ring_jx_jz_hz_sweep.py -N 7 --workers 4 --save figures/sweep3d
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
from collapse.spherical_harmonics import SphericalHarmonicProjector

# ===================================================================
# Constants
# ===================================================================
TIMES = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0]
SEED = 44
L_MAX = 10

JX_VALUES = np.round(np.logspace(np.log10(0.1), np.log10(10), 11), 4).tolist()
JZ_VALUES = np.round(np.logspace(np.log10(0.1), np.log10(10), 11), 4).tolist()
HZ_VALUES = np.round(np.logspace(np.log10(0.1), np.log10(10), 11), 4).tolist()

SH_LABELS = [
    r"$|a_{0,0}|^2$",
    r"$|a_{1,0}|^2$",
    r"$\sum|a_{1,\pm1}|^2$",
    r"$\sum_{\ell\geq2}|a_{\ell m}|^2$",
]


# ===================================================================
# Spherical-harmonic helpers
# ===================================================================
def _bloch_to_spherical(bx, by, bz):
    theta = np.arccos(np.clip(bz, -1, 1))
    phi = np.arctan2(by, bx) % (2 * np.pi)
    return theta, phi


def _histogram_on_grid(theta_pts, phi_pts, grid_theta, grid_phi):
    theta_idx = np.argmin(np.abs(theta_pts[:, None] - grid_theta[None, :]), axis=1)
    phi_idx = np.argmin(np.abs(phi_pts[:, None] - grid_phi[None, :]), axis=1)
    counts = np.zeros((len(grid_theta), len(grid_phi)), dtype=np.float64)
    np.add.at(counts, (theta_idx, phi_idx), 1)
    return counts


def _sh_decomposition(expansion):
    c = expansion.as_array(copy=False)
    l_max = expansion.l_max
    p00 = float(np.abs(c[0, l_max]) ** 2)
    p10 = float(np.abs(c[1, l_max]) ** 2) if l_max >= 1 else 0.0
    p1m1 = (
        float(np.abs(c[1, l_max - 1]) ** 2 + np.abs(c[1, l_max + 1]) ** 2)
        if l_max >= 1
        else 0.0
    )
    p_higher = 0.0
    for l in range(2, l_max + 1):
        for m in range(-l, l + 1):
            p_higher += float(np.abs(c[l, m + l_max]) ** 2)
    return p00, p10, p1m1, p_higher


def compute_sh_projections(td, projector):
    """Return ``(density_decomp, ratio_decomp)``."""
    bx0, by0 = td["bx0"], td["by0"]
    bx1, by1 = td["bx1"], td["by1"]
    z0, z1 = td["z0"], td["z1"]

    theta0, azim0 = _bloch_to_spherical(bx0, by0, z0)
    theta1, azim1 = _bloch_to_spherical(bx1, by1, z1)

    counts0 = _histogram_on_grid(theta0, azim0, projector.theta, projector.phi)
    counts1 = _histogram_on_grid(theta1, azim1, projector.theta, projector.phi)

    density_exp = projector.project_samples(counts0.astype(np.float64), real_input=True)
    density_decomp = _sh_decomposition(density_exp)

    total = counts0 + counts1
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(total > 0, counts0 / total, 0.0)
    ratio_exp = projector.project_samples(ratio, real_input=True)
    ratio_decomp = _sh_decomposition(ratio_exp)

    return density_decomp, ratio_decomp


# ===================================================================
# Build all scenarios
# ===================================================================
def build_scenarios(N: int, hz_idx: int | None = None) -> list[dict]:
    """Enumerate Jx × Jz × hz scenarios with Jx/Jz/hz scaled by 1/N_pixel, hz0=0.

    If *hz_idx* is given, only the hz value at that index is used.
    """
    N_pixel = N - 1
    scenarios: list[dict] = []
    hz_list = [HZ_VALUES[hz_idx]] if hz_idx is not None else HZ_VALUES

    for hz in hz_list:
        for Jz in JZ_VALUES:
            for Jx in JX_VALUES:
                Jx_s = Jx / N_pixel
                Jz_s = Jz / N_pixel
                hz_s = hz / N_pixel
                params = dict(
                    N_pixel=N_pixel,
                    J=1.0,
                    Jx=Jx_s,
                    Jz=Jz_s,
                    hx=0.0,
                    hz=hz_s,
                    hz0=0.0,
                    connectivity="ring",
                    seed=SEED,
                )
                title_line = (
                    f"SP[ring] | J=1  Jx={Jx:g}/{N_pixel}  Jz={Jz:g}/{N_pixel}  "
                    f"hx=0  hz={hz:g}/{N_pixel}  hz0=0"
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
    import os

    logger = logging.getLogger(__name__)
    title = scenario["title_line"]
    prefix = (
        f"  [W{os.getpid()}] [{scenario['idx']+1:3d}/{scenario['total']:3d}] "
        f"{title:65s}"
    )
    try:
        t0 = time.time()
        ham = scenario["cls"](**scenario["params"])
        H = ham.generate()
        logger.info(f"{prefix}  H generated ({time.time()-t0:.1f}s)")

        t1 = time.time()
        E, V = np.linalg.eigh(H)
        logger.info(f"{prefix}  Diagonalized ({time.time()-t1:.1f}s)")

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
            "Jx": scenario["Jx"],
            "Jz": scenario["Jz"],
            "hz": scenario["hz"],
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
            "error": str(exc),
        }


# ===================================================================
# Plotting helpers
# ===================================================================
def plot_histogram_on_ax(ax, z0, z1, title, bins=30):
    data0 = np.arccos(np.clip(z0, -1, 1))
    data1 = np.arccos(np.clip(z1, -1, 1))
    bin_edges = np.linspace(0, np.pi, bins + 1)
    x_th = np.linspace(0, np.pi, 1000)
    born = (1 + np.cos(x_th)) / 2
    xlabel = r"$\theta$"
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
    ax.set_xlabel(xlabel, fontsize=7)
    ax.set_ylabel("Density", fontsize=6, color="gray")
    ax.tick_params(axis="y", labelcolor="gray", labelsize=5)
    ax_r.set_ylabel("Fraction", fontsize=6)
    ax_r.tick_params(axis="y", labelsize=5)
    ax.tick_params(axis="x", labelsize=5)
    ax.set_title(title, fontsize=6, pad=3)


def plot_bloch_on_ax(ax, td, title):
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
    """Save per-scenario histogram + Bloch figures, organised in folders."""
    ntimes = len(TIMES)
    for res in results:
        if "error" in res:
            continue
        hz, Jz, Jx = res["hz"], res["Jz"], res["Jx"]
        tr = res["time_results"]

        out_dir = save_dir / "histograms" / f"hz={hz:g}" / f"Jz={Jz:g}"
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
# Plot type 2: SH curves vs Jx (per hz, Jz)
# ===================================================================
def save_sh_curves(results, save_dir, logger):
    """Save SH projection curves vs Jx for each (hz, Jz) combination."""
    projector = SphericalHarmonicProjector(
        l_max=L_MAX, n_theta=max(L_MAX + 1, 16), n_phi=max(2 * L_MAX + 1, 32)
    )

    # Group: {(hz, Jz): {t: [(Jx, (density, ratio)), ...]}}
    grouped: dict[tuple[float, float], dict[float, list]] = {}
    for res in results:
        if "error" in res:
            continue
        key = (res["hz"], res["Jz"])
        if key not in grouped:
            grouped[key] = {t: [] for t in TIMES}
        for td in res["time_results"]:
            decomps = compute_sh_projections(td, projector)
            grouped[key][td["t"]].append((res["Jx"], decomps))

    # Sort by Jx
    for key in grouped:
        for t in TIMES:
            grouped[key][t].sort(key=lambda x: x[0])

    n_times = len(TIMES)
    kind_info = [
        ("density", r"SH density projections vs $J_x$"),
        ("ratio", r"SH ratio $h_0/(h_0{+}h_1)$ projections vs $J_x$"),
    ]

    for (hz, Jz), time_data in grouped.items():
        out_dir = save_dir / "sh_curves" / f"hz={hz:g}"
        out_dir.mkdir(parents=True, exist_ok=True)

        for kind_idx, (kind_name, suptitle_base) in enumerate(kind_info):
            fig, axes = plt.subplots(
                n_times,
                1,
                figsize=(6, 2.5 * n_times),
                constrained_layout=True,
                sharex=True,
            )
            if n_times == 1:
                axes = [axes]

            for row, t_val in enumerate(TIMES):
                ax = axes[row]
                entries = time_data[t_val]
                if not entries:
                    continue
                xs = [e[0] for e in entries]
                decomps = [e[1][kind_idx] for e in entries]
                p00s = [d[0] for d in decomps]
                p10s = [d[1] for d in decomps]
                p1pms = [d[2] for d in decomps]
                p_highs = [d[3] for d in decomps]

                ax.plot(xs, p00s, "o-", ms=3, lw=1.2, label=SH_LABELS[0])
                ax.plot(xs, p10s, "s-", ms=3, lw=1.2, label=SH_LABELS[1])
                ax.plot(xs, p1pms, "^-", ms=3, lw=1.2, label=SH_LABELS[2])
                ax.plot(xs, p_highs, "D-", ms=3, lw=1.2, label=SH_LABELS[3])

                ax.set_xscale("log")
                ax.set_ylabel(f"t={t_val:g}", fontsize=7)
                ax.tick_params(labelsize=6)
                if row == 0:
                    ax.legend(fontsize=6, loc="upper right")
                if row == n_times - 1:
                    ax.set_xlabel(r"$J_x$", fontsize=8)

            fig.suptitle(
                f"{suptitle_base}  |  hz={hz:g}  Jz={Jz:g}",
                fontsize=11,
                fontweight="bold",
            )

            out = out_dir / f"Jz={Jz:g}_{kind_name}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            plt.close(fig)
            logger.info(f"Saved {out}")


# ===================================================================
# Plot type 3: SH heatmaps on Jx-Jz plane (per hz, time)
# ===================================================================
def save_sh_heatmaps(results, save_dir, logger):
    """Save SH heatmaps on the Jx-Jz plane for each (hz, time) pair."""
    projector = SphericalHarmonicProjector(
        l_max=L_MAX, n_theta=max(L_MAX + 1, 16), n_phi=max(2 * L_MAX + 1, 32)
    )

    n_jx = len(JX_VALUES)
    n_jz = len(JZ_VALUES)
    jx_arr = np.array(JX_VALUES)
    jz_arr = np.array(JZ_VALUES)

    # Group: {hz: {(Jx, Jz): {t: (density, ratio)}}}
    grouped: dict[float, dict[tuple[float, float], dict[float, tuple]]] = {}
    for res in results:
        if "error" in res:
            continue
        hz = res["hz"]
        if hz not in grouped:
            grouped[hz] = {}
        key = (res["Jx"], res["Jz"])
        grouped[hz][key] = {}
        for td in res["time_results"]:
            grouped[hz][key][td["t"]] = compute_sh_projections(td, projector)

    kind_info = [
        ("density", r"SH density on $J_x$–$J_z$ plane"),
        ("ratio", r"SH ratio $h_0/(h_0{+}h_1)$ on $J_x$–$J_z$ plane"),
    ]

    for hz, grid_data in grouped.items():
        out_dir = save_dir / "sh_heatmaps" / f"hz={hz:g}"
        out_dir.mkdir(parents=True, exist_ok=True)

        for t_val in TIMES:
            for kind_idx, (kind_name, suptitle_base) in enumerate(kind_info):
                fig, axes = plt.subplots(
                    1,
                    4,
                    figsize=(20, 4),
                    constrained_layout=True,
                )

                grids = [np.full((n_jz, n_jx), np.nan) for _ in range(4)]
                for j, Jx in enumerate(JX_VALUES):
                    for k, Jz in enumerate(JZ_VALUES):
                        key = (Jx, Jz)
                        if key not in grid_data or t_val not in grid_data[key]:
                            continue
                        decomp = grid_data[key][t_val][kind_idx]
                        for c in range(4):
                            grids[c][k, j] = decomp[c]

                for c in range(4):
                    ax = axes[c]
                    im = ax.pcolormesh(
                        jx_arr,
                        jz_arr,
                        grids[c],
                        cmap="viridis",
                        shading="nearest",
                    )
                    ax.set_xscale("log")
                    ax.set_yscale("log")
                    ax.set_xlabel(r"$J_x$", fontsize=9)
                    ax.set_ylabel(r"$J_z$", fontsize=9)
                    ax.set_title(SH_LABELS[c], fontsize=8, fontweight="bold")
                    ax.tick_params(labelsize=7)
                    plt.colorbar(im, ax=ax, pad=0.02)

                fig.suptitle(
                    f"{suptitle_base}  |  hz={hz:g}  t={t_val:g}",
                    fontsize=12,
                    fontweight="bold",
                )

                out = out_dir / f"t={t_val:g}_{kind_name}.png"
                fig.savefig(out, bbox_inches="tight", dpi=150)
                plt.close(fig)
                logger.info(f"Saved {out}")


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description="SP ring – Jx × Jz × hz sweep (hz0=0, Jx/Jz/hz scaled by 1/N_pixel)"
    )
    parser.add_argument("-N", "--N", type=int, default=7, dest="N")
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

    scenarios = build_scenarios(args.N, hz_idx=args.hz_idx)
    n_workers = args.workers or cpu_count()
    n = len(scenarios)
    N_pixel = args.N - 1

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_ring_jx_jz_hz_sweep_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== SP Ring Jx × Jz × hz Sweep (hz0=0): {n} scenarios "
        f"({len(JX_VALUES)}×{len(JZ_VALUES)}×{len(HZ_VALUES)}), "
        f"N={args.N} (N_pixel={N_pixel}, D={2**args.N}), "
        f"J=1, Jx/Jz/hz scaled by 1/{N_pixel}, "
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

    # --- Plot type 1: per-scenario histograms + Bloch ---
    logger.info("=== Saving histograms ===")
    save_histograms(results, save_dir, logger)

    # --- Plot type 2: SH curves vs Jx ---
    logger.info("=== Saving SH curves ===")
    save_sh_curves(results, save_dir, logger)

    # --- Plot type 3: SH heatmaps ---
    logger.info("=== Saving SH heatmaps ===")
    save_sh_heatmaps(results, save_dir, logger)

    logger.info("All done.")


if __name__ == "__main__":
    main()
