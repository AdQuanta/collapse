"""
Single-Pixel Ring – hx Sweep
==============================

Sweep hx over [0.1, 0.2, ..., 1.0] with Jx=0.1, Jz=0, J=1, hz=0.5.

Usage::

    python examples/sp_ring_hx_sweep.py
    python examples/sp_ring_hx_sweep.py -N 7 --workers 4
    python examples/sp_ring_hx_sweep.py --save figures/hx_sweep --bloch
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse, logging, time
from datetime import datetime
from multiprocessing import Pool, cpu_count
import matplotlib.pyplot as plt
import numpy as np
from collapse.analysis import DisentanglementAnalyzer
from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

TIMES = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0]
SEED = 44
HX_VALUES = [round(0.1 * k, 1) for k in range(1, 11)]


def build_scenarios(N):
    scenarios = []
    for hx in HX_VALUES:
        params = dict(
            N_pixel=N - 1,
            J=1.0,
            Jx=0.1,
            Jz=0.0,
            hx=hx,
            hz=0.5,
            connectivity="ring",
            seed=SEED,
        )
        title_line = f"SP[ring] | J=1  Jx=0.1  Jz=0  hx={hx:g}  hz=0.5"
        scenarios.append(
            {
                "title_line": title_line,
                "model": "SP",
                "cls": SinglePixelHamiltonianQuSpin,
                "params": params,
            }
        )
    for i, s in enumerate(scenarios):
        s["idx"] = i
        s["total"] = len(scenarios)
    return scenarios


def _run_scenario(scenario):
    import os

    logger = logging.getLogger(__name__)
    title = scenario["title_line"]
    prefix = f"  [W{os.getpid()}] [{scenario['idx']+1:3d}/{scenario['total']:3d}] {title:55s}"
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
        logger.info(f"{prefix}  Done ({time.time()-t0:.1f}s)")
        return {
            "idx": scenario["idx"],
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
            "title_line": scenario["title_line"],
            "model": scenario["model"],
            "error": str(exc),
        }


def plot_histogram_on_ax(ax, z0, z1, title, bins=30, use_theta=True):
    if use_theta:
        data0, data1 = np.arccos(np.clip(z0, -1, 1)), np.arccos(np.clip(z1, -1, 1))
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


def main():
    ap = argparse.ArgumentParser(description="SP ring hx sweep")
    ap.add_argument("-N", "--N", type=int, default=7, dest="N")
    ap.add_argument("--no-theta", action="store_true")
    ap.add_argument("--bloch", action="store_true")
    ap.add_argument("--save", type=str, default=None)
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()

    scenarios = build_scenarios(args.N)
    use_theta = not args.no_theta
    nw = args.workers or cpu_count()
    n = len(scenarios)

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_ring_hx_sweep_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.info(f"=== SP Ring hx Sweep: {n} scenarios, N={args.N}, {nw} workers ===")
    t_start = time.time()

    if nw == 1:
        res_un = [_run_scenario(s) for s in scenarios]
    else:
        with Pool(nw) as pool:
            res_un = list(pool.imap_unordered(_run_scenario, scenarios))
    results = sorted([r for r in res_un if "error" not in r], key=lambda r: r["idx"])
    logger.info(f"Computation finished in {time.time()-t_start:.1f}s")

    save_dir = Path(args.save) if args.save else None
    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
    ntimes = len(TIMES)
    nrows = 2 if args.bloch else 1

    for res in results:
        tl, tr, idx = res["title_line"], res["time_results"], res["idx"]
        fig = plt.figure(
            figsize=(3.5 * ntimes, 3.5 * nrows), dpi=120, constrained_layout=True
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
        fig.suptitle(f"#{idx+1:03d}  {tl}", fontsize=10, fontweight="bold", y=1.02)
        if save_dir:
            out = save_dir / f"{idx+1:03d}_{_safe_filename(tl)}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            logger.info(f"Saved {out}")
            plt.close(fig)
    if not args.save:
        plt.show()
    logger.info("All done.")


if __name__ == "__main__":
    main()
