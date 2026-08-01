"""
Single-Pixel Ring – Jx × Jz Grid  (SH Heatmaps)
==================================================

2-D sweep over ``Jx`` (30 log-spaced, 0.01–10) and ``Jz`` (30 log-spaced,
0.01–10) with fixed J=1, hx=0, hz=0.5, ring connectivity.

Three ``hz``-placement modes are tested for each grid point:

* **central only** – ``hz0=0.5, hz=0``
* **detector only** – ``hz0=0, hz=0.5``
* **all qubits** – ``hz0=None, hz=0.5``

For every grid point the spherical-harmonic projections of both the
φ₀ **density** and the **ratio** h₀/(h₀+h₁) are computed.  The
results are visualised as heatmaps on the (Jx, Jz) plane:

* ``|a_{0,0}|²``
* ``|a_{1,0}|²``
* ``Σ|a_{1,±1}|²``
* ``Σ_{ℓ≥2} |a_{ℓm}|²``

One figure per (time value × hz mode), with 2 rows (density / ratio)
× 4 columns (SH components).

Usage::

    python examples/sp_ring_jx_jz_grid.py
    python examples/sp_ring_jx_jz_grid.py -N 7 --workers 4
    python examples/sp_ring_jx_jz_grid.py --save figures/jx_jz_grid
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
L_MAX = 6

# 30 log-spaced values from 0.01 to 10
JX_VALUES = np.round(np.logspace(np.log10(0.01), np.log10(100), 40), 4).tolist()
JZ_VALUES = np.round(np.logspace(np.log10(0.01), np.log10(100), 40), 4).tolist()

# hz placement modes: (label, hz, hz0)
HZ_MODES = [
    ("hz0_only", 0.0, 0.5),  # central qubit only
    ("hz_only", 0.5, 0.0),  # detector qubits only
    ("hz_all", 0.5, None),  # uniform on all qubits
]

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
def build_scenarios(N: int) -> list[dict]:
    scenarios: list[dict] = []
    for Jx in JX_VALUES:
        for Jz in JZ_VALUES:
            for hz_label, hz_val, hz0_val in HZ_MODES:
                params = dict(
                    N_pixel=N - 1,
                    J=1.0,
                    Jx=Jx,
                    Jz=Jz,
                    hx=0.0,
                    hz=hz_val,
                    hz0=hz0_val,
                    connectivity="ring",
                    seed=SEED,
                )
                hz0_str = f"{hz0_val:g}" if hz0_val is not None else "—"
                title_line = (
                    f"SP[ring] | J=1  Jx={Jx:g}  Jz={Jz:g}  hx=0  "
                    f"hz={hz_val:g}  hz0={hz0_str}  ({hz_label})"
                )
                scenarios.append(
                    {
                        "title_line": title_line,
                        "model": "SP",
                        "cls": SinglePixelHamiltonianQuSpin,
                        "params": params,
                        "Jx": Jx,
                        "Jz": Jz,
                        "hz_label": hz_label,
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
        f"{title:55s}"
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
            "hz_label": scenario["hz_label"],
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
            "hz_label": scenario.get("hz_label", ""),
            "error": str(exc),
        }


# ===================================================================
# Heatmap plots
# ===================================================================
def plot_heatmaps(results, save_dir, logger):
    """Produce heatmap figures: one per (time value × hz mode).

    Each figure has 2 rows (density, ratio) × 4 columns (SH components).
    """
    projector = SphericalHarmonicProjector(
        l_max=L_MAX, n_theta=max(L_MAX + 1, 16), n_phi=max(2 * L_MAX + 1, 32)
    )

    n_jx = len(JX_VALUES)
    n_jz = len(JZ_VALUES)
    jx_arr = np.array(JX_VALUES)
    jz_arr = np.array(JZ_VALUES)
    mode_labels = [m[0] for m in HZ_MODES]

    # Pre-compute SH projections grouped by hz mode:
    # {hz_label: {(Jx, Jz): {t: (density_decomp, ratio_decomp)}}}
    sh_data: dict[str, dict[tuple[float, float], dict[float, tuple]]] = {
        ml: {} for ml in mode_labels
    }
    for res in results:
        if "error" in res:
            continue
        ml = res["hz_label"]
        key = (res["Jx"], res["Jz"])
        sh_data[ml][key] = {}
        for td in res["time_results"]:
            sh_data[ml][key][td["t"]] = compute_sh_projections(td, projector)

    kind_names = ["density", "ratio"]

    for ml in mode_labels:
        for t_val in TIMES:
            fig, axes = plt.subplots(
                2,
                4,
                figsize=(20, 8),
                constrained_layout=True,
            )

            for kind_idx, kind_name in enumerate(kind_names):
                # Build 2-D arrays: shape (n_jz, n_jx)
                grids = [np.full((n_jz, n_jx), np.nan) for _ in range(4)]

                for j, Jx in enumerate(JX_VALUES):
                    for k, Jz in enumerate(JZ_VALUES):
                        key = (Jx, Jz)
                        if key not in sh_data[ml] or t_val not in sh_data[ml][key]:
                            continue
                        decomp = sh_data[ml][key][t_val][kind_idx]
                        for c in range(4):
                            grids[c][k, j] = decomp[c]

                for c in range(4):
                    ax = axes[kind_idx, c]
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
                    ax.set_title(
                        f"{kind_name}: {SH_LABELS[c]}",
                        fontsize=8,
                        fontweight="bold",
                    )
                    ax.tick_params(labelsize=7)
                    plt.colorbar(im, ax=ax, pad=0.02)

            fig.suptitle(
                rf"SH projections on $J_x$–$J_z$ plane  |  {ml}  |  $t={t_val:g}$",
                fontsize=13,
                fontweight="bold",
            )

            if save_dir:
                out = save_dir / f"sh_heatmap_jx_jz_{ml}_t{t_val:g}.png"
                fig.savefig(out, bbox_inches="tight", dpi=150)
                logger.info(f"Saved {out}")
                plt.close(fig)


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description="SP ring – Jx × Jz grid with SH heatmaps"
    )
    parser.add_argument("-N", "--N", type=int, default=7, dest="N")
    parser.add_argument("--save", type=str, default=None)
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()

    scenarios = build_scenarios(args.N)
    n_workers = args.workers or cpu_count()
    n = len(scenarios)

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_ring_jx_jz_grid_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== SP Ring Jx × Jz Grid: {n} scenarios ({len(JX_VALUES)}×{len(JZ_VALUES)}), "
        f"N={args.N} (D={2**args.N}), {n_workers} workers, "
        f"{len(TIMES)} time points ==="
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

    save_dir = None
    if args.save:
        save_dir = Path(args.save)
        save_dir.mkdir(parents=True, exist_ok=True)

    # --- Heatmap plots ---
    plot_heatmaps(results, save_dir, logger)

    if not args.save:
        plt.show()
    logger.info("All done.")


if __name__ == "__main__":
    main()
