"""
Single-Pixel Ring – hx Sweep × Field Placement
=================================================

Sweep hx over [0.1, 0.2, …, 1.0] with fixed Jx=0.1, Jz=0, J=1, ring
connectivity.

For every ``hx`` value, **all 9 combinations** of hz-placement and
hx-placement are tested:

hz-placement (3 modes):
    * ``hz0_only``  – ``hz0=0.5, hz=0``
    * ``hz_only``   – ``hz0=0,   hz=0.5``
    * ``hz_all``    – ``hz0=None, hz=0.5``

hx-placement (3 modes):
    * ``hx0_only``  – ``hx0=<value>, hx=0``
    * ``hx_only``   – ``hx0=0,       hx=<value>``
    * ``hx_all``    – ``hx0=None,     hx=<value>``

Total scenarios = 10 × 3 × 3 = 90.

In addition to per-scenario histograms, a summary figure shows the
spherical-harmonic projections of the ratio h₀/(h₀+h₁) as a function
of ``hx`` for each field-placement combination.

Usage::

    python scripts/sp_ring_hx_sweep_field_placement.py
    python scripts/sp_ring_hx_sweep_field_placement.py -N 7 --workers 4
    python scripts/sp_ring_hx_sweep_field_placement.py --save figures/hx_field --bloch
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

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.spherical_harmonics import SphericalHarmonicProjector

# ===================================================================
# Constants
# ===================================================================
TIMES = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0]
SEED = 44
L_MAX = 4
HX_VALUES = [round(0.1 * k, 1) for k in range(1, 11)]

# Field placement modes: (label, field_value_for_remaining, field_value_for_central)
HZ_MODES = [
    ("hz0_only",  0.0, 0.5),   # central qubit only
    ("hz_only",   0.5, 0.0),   # detector qubits only
    ("hz_all",    0.5, None),   # uniform on all qubits
]

HX_MODES = [
    ("hx0_only",  0.0, lambda hx: hx),    # central qubit only
    ("hx_only",   1.0, lambda hx: 0.0),   # detector qubits only
    ("hx_all",    1.0, lambda hx: None),   # uniform on all qubits
]


# ===================================================================
# Spherical-harmonic helpers
# ===================================================================
def _bloch_to_spherical(bx, by, bz):
    """Convert Cartesian Bloch components to (theta, phi) on the unit sphere."""
    theta = np.arccos(np.clip(bz, -1, 1))
    phi = np.arctan2(by, bx) % (2 * np.pi)
    return theta, phi


def _histogram_on_grid(theta_pts, phi_pts, grid_theta, grid_phi):
    """Bin a point cloud onto the projector grid."""
    theta_idx = np.argmin(np.abs(theta_pts[:, None] - grid_theta[None, :]), axis=1)
    phi_idx = np.argmin(np.abs(phi_pts[:, None] - grid_phi[None, :]), axis=1)
    counts = np.zeros((len(grid_theta), len(grid_phi)), dtype=np.float64)
    np.add.at(counts, (theta_idx, phi_idx), 1)
    return counts


def _sh_decomposition(expansion):
    """Extract the four summary quantities from a SphericalHarmonicExpansion.

    Returns (p00, p10, p1pm, p_higher) – all real non-negative.
    """
    c = expansion.as_array(copy=False)
    l_max = expansion.l_max

    p00 = float(np.abs(c[0, l_max]) ** 2)
    p10 = float(np.abs(c[1, l_max]) ** 2)                          if l_max >= 1 else 0.0
    p1m1 = float(np.abs(c[1, l_max - 1]) ** 2 + np.abs(c[1, l_max + 1]) ** 2) if l_max >= 1 else 0.0

    p_higher = 0.0
    for l in range(2, l_max + 1):
        for m in range(-l, l + 1):
            p_higher += float(np.abs(c[l, m + l_max]) ** 2)

    return p00, p10, p1m1, p_higher


def compute_sh_projections(td, projector):
    """Compute SH projections of density and ratio for one time-point.

    Returns ``(density_decomp, ratio_decomp)`` where each is a
    ``(p00, p10, p1pm, p_higher)`` tuple.
    """
    bx0, by0 = td["bx0"], td["by0"]
    bx1, by1 = td["bx1"], td["by1"]
    z0, z1 = td["z0"], td["z1"]

    theta0, azim0 = _bloch_to_spherical(bx0, by0, z0)
    theta1, azim1 = _bloch_to_spherical(bx1, by1, z1)

    counts0 = _histogram_on_grid(theta0, azim0, projector.theta, projector.phi)
    counts1 = _histogram_on_grid(theta1, azim1, projector.theta, projector.phi)

    # Density of the phi_0 distribution
    density0 = counts0.astype(np.float64)
    density_exp = projector.project_samples(density0, real_input=True)
    density_decomp = _sh_decomposition(density_exp)

    # Ratio h0 / (h0 + h1)
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
    """Enumerate hx × hz-placement × hx-placement scenarios."""
    scenarios: list[dict] = []
    for hx_sweep in HX_VALUES:
        for hz_label, hz_val, hz0_val in HZ_MODES:
            for hx_label, hx_mult, hx0_fn in HX_MODES:
                hx_param = round(hx_sweep * hx_mult, 4)
                hx0_param = hx0_fn(hx_sweep)

                params = dict(
                    N_pixel=N - 1,
                    J=1.0,
                    Jx=0.1,
                    Jz=0.0,
                    hx=hx_param,
                    hz=hz_val,
                    hx0=hx0_param,
                    hz0=hz0_val,
                    connectivity="ring",
                    seed=SEED,
                )
                hx0_str = f"{hx0_param:g}" if hx0_param is not None else "—"
                hz0_str = f"{hz0_val:g}" if hz0_val is not None else "—"
                combo_label = f"{hx_label}+{hz_label}"
                title_line = (
                    f"SP[ring] | J=1  Jx=0.1  Jz=0  "
                    f"hx={hx_param:g}  hx0={hx0_str}  "
                    f"hz={hz_val:g}  hz0={hz0_str}  "
                    f"({combo_label})"
                )
                scenarios.append(
                    {
                        "title_line": title_line,
                        "model": "SP",
                        "cls": SinglePixelHamiltonianQuSpin,
                        "params": params,
                        "combo_label": combo_label,
                        "sweep_val": hx_sweep,
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
        f"{title:90s}"
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
            "combo_label": scenario["combo_label"],
            "sweep_val": scenario["sweep_val"],
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
            "combo_label": scenario.get("combo_label", ""),
            "sweep_val": scenario.get("sweep_val", 0),
            "error": str(exc),
        }


# ===================================================================
# Plotting helpers
# ===================================================================
def plot_histogram_on_ax(ax, z0, z1, title, bins=30, use_theta=True):
    if use_theta:
        data0 = np.arccos(np.clip(z0, -1, 1))
        data1 = np.arccos(np.clip(z1, -1, 1))
        bin_edges = np.linspace(0, np.pi, bins + 1)
        x_th = np.linspace(0, np.pi, 1000)
        born = (1 + np.cos(x_th)) / 2
        xlabel = r"$\theta$"
    else:
        data0, data1 = z0, z1
        bin_edges = np.linspace(-1, 1, bins + 1)
        x_th = np.linspace(-1, 1, 1000)
        born = (1 + x_th) / 2
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


def _safe_filename(s):
    for ch in " |[]=,/\\–":
        s = s.replace(ch, "_" if ch in " |" else "")
    return s


# ===================================================================
# Spherical-harmonic summary plot
# ===================================================================
def plot_sh_summary(results, save_dir, logger):
    """Produce two summary figures (density + ratio): SH projections vs hx
    for each combo mode.  One row per time value, one column per combo.
    """
    projector = SphericalHarmonicProjector(l_max=L_MAX, n_theta=max(L_MAX + 1, 16), n_phi=max(2 * L_MAX + 1, 32))

    # Build ordered list of combo labels
    combo_labels = []
    for _, hz_label, _, _ in [(None, m[0], m[1], m[2]) for m in HZ_MODES]:
        for _, hx_label, _, _ in [(None, m[0], m[1], m[2]) for m in HX_MODES]:
            combo_labels.append(f"{hx_label}+{hz_label}")

    # {combo_label: {t_val: [(sweep_val, (density_decomp, ratio_decomp)), ...]}}
    data = {cl: {t: [] for t in TIMES} for cl in combo_labels}

    for res in results:
        if "error" in res:
            continue
        combo_label = res["combo_label"]
        sweep_val = res["sweep_val"]
        for td in res["time_results"]:
            decomps = compute_sh_projections(td, projector)
            data[combo_label][td["t"]].append((sweep_val, decomps))

    for cl in combo_labels:
        for t in TIMES:
            data[cl][t].sort(key=lambda x: x[0])

    n_times = len(TIMES)
    n_combos = len(combo_labels)

    # Generate one figure for density and one for ratio
    for kind_idx, (kind_name, file_suffix, suptitle) in enumerate([
        ("density", "density", r"SH projections of $\rho_0$ density vs $h_x$"),
        ("ratio",   "ratio",  r"SH projections of $h_0/(h_0{+}h_1)$ ratio vs $h_x$"),
    ]):
        fig, axes = plt.subplots(
            n_times, n_combos,
            figsize=(4 * n_combos, 2.5 * n_times),
            constrained_layout=True,
            sharex=True,
        )

        for col, cl in enumerate(combo_labels):
            for row, t_val in enumerate(TIMES):
                ax = axes[row, col]
                entries = data[cl][t_val]
                if not entries:
                    continue
                xs = [e[0] for e in entries]
                decomps = [e[1][kind_idx] for e in entries]
                p00s    = [d[0] for d in decomps]
                p10s    = [d[1] for d in decomps]
                p1pms   = [d[2] for d in decomps]
                p_highs = [d[3] for d in decomps]

                ax.plot(xs, p00s,   "o-", ms=3, lw=1.2, label=r"$|a_{0,0}|^2$")
                ax.plot(xs, p10s,   "s-", ms=3, lw=1.2, label=r"$|a_{1,0}|^2$")
                ax.plot(xs, p1pms,  "^-", ms=3, lw=1.2, label=r"$\sum|a_{1,\pm1}|^2$")
                ax.plot(xs, p_highs,"D-", ms=3, lw=1.2, label=r"$\sum_{\ell\geq2}|a_{\ell m}|^2$")

                ax.tick_params(labelsize=5)
                if row == 0:
                    ax.set_title(cl, fontsize=7, fontweight="bold")
                if col == 0:
                    ax.set_ylabel(f"t={t_val:g}", fontsize=6)
                if row == n_times - 1:
                    ax.set_xlabel(r"$h_x$", fontsize=7)
                if row == 0 and col == n_combos - 1:
                    ax.legend(fontsize=5, loc="upper right")

        fig.suptitle(suptitle, fontsize=12, fontweight="bold")

        if save_dir:
            out = save_dir / f"sh_summary_hx_field_{file_suffix}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            logger.info(f"Saved {out}")
            plt.close(fig)


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description="SP ring – hx sweep × hx/hz field placement"
    )
    parser.add_argument("-N", "--N", type=int, default=7, dest="N")
    parser.add_argument("--no-theta", action="store_true")
    parser.add_argument("--bloch", action="store_true")
    parser.add_argument("--save", type=str, default=None)
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()

    scenarios = build_scenarios(args.N)
    use_theta = not args.no_theta
    n_workers = args.workers or cpu_count()
    n = len(scenarios)

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_ring_hx_sweep_field_placement_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== SP Ring hx Sweep × Field Placement: {n} scenarios, N={args.N} "
        f"(D={2**args.N}), {n_workers} workers, {len(TIMES)} time points ==="
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
        for col, td in enumerate(tr):
            ax = fig.add_subplot(nrows, ntimes, col + 1)
            plot_histogram_on_ax(
                ax, td["z0"], td["z1"], title=f"t={td['t']:g}", use_theta=use_theta
            )
        if args.bloch:
            for col, td in enumerate(tr):
                ax3 = fig.add_subplot(nrows, ntimes, ntimes + col + 1, projection="3d")
                plot_bloch_on_ax(ax3, td, title=f"t={td['t']:g}")

        fig.suptitle(
            f"#{idx+1:03d}  {title_line}", fontsize=9, fontweight="bold", y=1.02
        )

        if save_dir:
            out = save_dir / f"{idx+1:03d}_{safe_name}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            logger.info(f"Saved {out}")
            plt.close(fig)

    # --- Spherical-harmonic summary plot ---
    plot_sh_summary(results, save_dir, logger)

    if not args.save:
        plt.show()
    logger.info("All done.")


if __name__ == "__main__":
    main()
