"""
Single-Pixel Chain – Born diagnostic + wrapped-distribution fits
=================================================================

Simulates **one** parameter set for **two** central-qubit field cases:

* **hz0 = 0** : no field on the central qubit
* **hz0 = hz**: uniform field on all qubits (including central)

Default parameters:

    J = 0,  Jpm = 1,  Jx = 0.01,  Jz = 0,  hz = 0.1,  hx = 0

All of Jx, Jz, hz can be overridden via command-line arguments.

Open-chain connectivity.  No translational symmetry is available, so
the Hamiltonian is diagonalised in the full Hilbert space
(magnetisation sectors are still used when applicable).

Times: t = 100, 1 000, 10 000, 1 000 000.

Plots produced (per N)
~~~~~~~~~~~~~~~~~~~~~~
1. ``N={N}_{scenario}.png`` -- theta-histograms with Born ratio,
   phi-histograms, and Bloch-sphere scatter (3 rows x ntimes cols).
2. ``N={N}_fits.png`` -- theta-density histograms on both linear and
   log y-scale, overlaid with wrapped-Gaussian and wrapped-Cauchy
   (Lorentzian) fits centred at mu=0.  4 rows: (hz0=0 linear, hz0=0 log,
   hz0=hz linear, hz0=hz log) x ntimes cols.
3. ``N={N}_comparison.png`` -- both scenarios overlaid on the same axes
   (2 rows: linear, log) x ntimes cols.
4. ``born_similarity.txt`` -- table of S values (updated after each N).

Usage::

    python examples/sp_chain_single_born_fits.py -N 7 9 --save figures/fits_chain
    python examples/sp_chain_single_born_fits.py -N 9 --Jx 0.1 --Jz 0.5 --hz 1.0 --save figures/fits_chain
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import logging
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

plt.rcParams["font.family"] = "Arial"

from collapse.analysis import DisentanglementAnalyzer
from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

# ===================================================================
# Constants
# ===================================================================
TIMES = [1000.0, 10_000.0, 100_000.0, 1_000_000.0]
SEED = 44


def get_scenarios(hz_val: float):
    return [
        {"label": "hz0=0", "hz0": 0.0},
        {"label": "hz0=hz", "hz0": None},  # None -> central qubit uses hz
    ]


# ===================================================================
# Born-similarity metric
# ===================================================================
def born_similarity(z0, z1, n_theta=100):
    r"""S = 1 - 2 int_0^pi |f(theta) - cos^2(theta/2)| sin theta dtheta.

    Calibration: S = 1 perfect Born, S = 0 for f = 1/2.
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
    born = np.cos(theta_centers / 2) ** 2
    return 1.0 - 2.0 * np.sum(np.abs(ratio - born) * np.sin(theta_centers)) * dtheta


# ===================================================================
# Wrapped distributions  (on [0, 2pi), evaluated at any theta)
# ===================================================================
def wrapped_gaussian_pdf(theta, mu, sigma, n_terms=20):
    r"""Wrapped normal density on [0, 2pi).

    f(theta; mu, sigma) = (1/2pi)[1 + 2 sum_{p=1}^{P} e^{-p^2 sigma^2/2} cos(p(theta-mu))]
    """
    result = np.ones_like(theta, dtype=float) / (2 * np.pi)
    for p in range(1, n_terms + 1):
        result += (
            (1.0 / np.pi) * np.exp(-0.5 * p**2 * sigma**2) * np.cos(p * (theta - mu))
        )
    return np.maximum(result, 0.0)


def wrapped_cauchy_pdf(theta, mu, rho):
    r"""Wrapped Cauchy (Lorentzian) density on [0, 2pi).

    f(theta; mu, rho) = (1/2pi) (1 - rho^2) / (1 + rho^2 - 2 rho cos(theta - mu))

    0 < rho < 1;  rho -> 0 is uniform, rho -> 1 is delta.
    """
    return (
        (1.0 / (2 * np.pi)) * (1 - rho**2) / (1 + rho**2 - 2 * rho * np.cos(theta - mu))
    )


def fit_wrapped_distributions(theta_vals, n_bins=50):
    """Fit wrapped Gaussian and wrapped Cauchy to a theta-density histogram.

    Both distributions are centred at mu = 0 (fixed).

    Returns (centers, density, gauss_popt, cauchy_popt).
    gauss_popt = (A, sigma) or None.
    cauchy_popt = (A, rho) or None.
    """
    bin_edges = np.linspace(0, np.pi, n_bins + 1)
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    density, _ = np.histogram(theta_vals, bins=bin_edges, density=True)

    sigma0 = np.std(theta_vals)
    A0 = np.max(density) * (2 * np.pi)  # rough amplitude

    # Wrapped Gaussian: f(theta) = A * WG(theta, mu=0, sigma)
    def _gauss_model(theta, A, sigma):
        return A * wrapped_gaussian_pdf(theta, 0.0, sigma)

    try:
        gauss_popt, _ = curve_fit(
            _gauss_model,
            centers,
            density,
            p0=[A0, sigma0],
            bounds=([0, 1e-6], [np.inf, 20.0]),
            maxfev=5000,
        )
    except Exception:
        gauss_popt = None

    # Wrapped Cauchy: f(theta) = A * WC(theta, mu=0, rho)
    def _cauchy_model(theta, A, rho):
        return A * wrapped_cauchy_pdf(theta, 0.0, rho)

    try:
        cauchy_popt, _ = curve_fit(
            _cauchy_model,
            centers,
            density,
            p0=[A0, 0.5],
            bounds=([0, 1e-6], [np.inf, 1 - 1e-6]),
            maxfev=5000,
        )
    except Exception:
        cauchy_popt = None

    return centers, density, gauss_popt, cauchy_popt


# ===================================================================
# Bloch-coordinate extraction
# ===================================================================
def _bloch_coords(analyzer):
    """Return (z0, z1, bx0, by0, bx1, by1, phi_az0, phi_az1)."""
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
    phi_az0 = np.arctan2(by0, bx0) % (2 * np.pi)
    phi_az1 = np.arctan2(by1, bx1) % (2 * np.pi)
    return z0, z1, bx0, by0, bx1, by1, phi_az0, phi_az1


# ===================================================================
# Plotting helpers
# ===================================================================
def _plot_theta_hist(ax, z0, z1, title, bins=30):
    """Theta density + ratio overlay with Born reference."""
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
    ax.set_title(title, fontsize=7, pad=3)


def _plot_phi_hist(ax, phi_az0, phi_az1, title, bins=30):
    r"""Azimuthal phi density histogram."""
    bin_edges = np.linspace(0, 2 * np.pi, bins + 1)
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bw = bin_edges[1] - bin_edges[0]
    h0, _ = np.histogram(phi_az0, bins=bin_edges, density=True)
    h1, _ = np.histogram(phi_az1, bins=bin_edges, density=True)
    ax.bar(centers, h0, width=bw, alpha=0.35, color="blue", label=r"$\phi_0$")
    ax.bar(centers, h1, width=bw, alpha=0.35, color="red", label=r"$\phi_1$")
    ax.set_xlim(0, 2 * np.pi)
    ax.set_xlabel(r"$\varphi$", fontsize=7)
    ax.set_ylabel("Density", fontsize=6)
    ax.tick_params(labelsize=5)
    ax.set_title(title, fontsize=7, pad=3)
    ax.legend(fontsize=5, loc="upper right")


def _plot_bloch(ax, bx0, by0, z0, bx1, by1, z1, title):
    """Bloch-sphere 3-D scatter."""
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 40)
    ax.plot_surface(
        np.outer(np.cos(u), np.sin(v)),
        np.outer(np.sin(u), np.sin(v)),
        np.outer(np.ones_like(u), np.cos(v)),
        color="gray",
        alpha=0.10,
    )
    ax.scatter(bx0, by0, z0, color="blue", alpha=0.4, s=4)
    ax.scatter(bx1, by1, z1, color="red", alpha=0.4, s=4)
    ax.set_xlabel("X", fontsize=5, labelpad=-4)
    ax.set_ylabel("Y", fontsize=5, labelpad=-4)
    ax.set_zlabel("Z", fontsize=5, labelpad=-4)
    ax.tick_params(axis="both", labelsize=4, pad=-2)
    ax.set_title(title, fontsize=7, pad=1)


def _plot_density_with_fits(
    ax, centers, density, gauss_popt, cauchy_popt, title, log_scale=False
):
    """Draw density histogram bars + Gaussian/Cauchy fit curves (mu=0 fixed)."""
    bw = centers[1] - centers[0]
    ax.bar(centers, density, width=bw, alpha=0.3, color="steelblue", label="data")

    theta_fine = np.linspace(0, np.pi, 500)

    if gauss_popt is not None:
        A, sigma = gauss_popt
        y_gauss = A * wrapped_gaussian_pdf(theta_fine, 0.0, sigma)
        ax.plot(
            theta_fine,
            y_gauss,
            "-",
            color="darkorange",
            lw=1.5,
            label=rf"W-Gauss $\sigma$={sigma:.2f}",
        )

    if cauchy_popt is not None:
        A, rho = cauchy_popt
        y_cauchy = A * wrapped_cauchy_pdf(theta_fine, 0.0, rho)
        ax.plot(
            theta_fine,
            y_cauchy,
            "-",
            color="green",
            lw=1.5,
            label=rf"W-Cauchy $\rho$={rho:.3f}",
        )

    if log_scale:
        ax.set_yscale("log")
        ax.set_ylim(
            bottom=(
                max(density[density > 0].min() * 0.3, 1e-6)
                if np.any(density > 0)
                else 1e-6
            )
        )

    ax.set_xlim(0, np.pi)
    ax.set_xlabel(r"$\theta$", fontsize=7)
    ax.set_ylabel("Density" + (" (log)" if log_scale else ""), fontsize=6)
    ax.tick_params(labelsize=5)
    ax.set_title(title, fontsize=6, pad=3)
    ax.legend(fontsize=4.5, loc="upper right")


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description=(
            "SP chain -- single param set, Born diagnostic + wrapped fits.  "
            "Compares hz0=0 vs hz0=hz."
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
    parser.add_argument(
        "--Jx",
        type=float,
        default=0.01,
        help="Central-pixel XX coupling (default: 0.01)",
    )
    parser.add_argument(
        "--Jz",
        type=float,
        default=0.0,
        help="Central-pixel ZZ coupling (default: 0.0)",
    )
    parser.add_argument(
        "--hz",
        type=float,
        default=0.1,
        help="Field value on the chain spins (default: 0.1)",
    )
    parser.add_argument("--save", type=str, required=True)
    args = parser.parse_args()
    JX = args.Jx
    JZ = args.Jz
    HZ = args.hz

    save_dir = Path(args.save)
    save_dir.mkdir(parents=True, exist_ok=True)

    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"sp_chain_single_born_fits_{datetime.now():%Y%m%d_%H%M%S}.log"

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
        f"=== SP Chain Born + fits: N={args.N_list}, "
        f"Jx={JX}, Jz={JZ}, hz={HZ}, {len(TIMES)} times ==="
    )
    logger.info(f"Log file: {log_file}")

    sim_lines: list[str] = []
    header = f"{'N':>4s}  {'scenario':>10s}  {'t':>12s}  {'S_born':>8s}"
    sim_lines.append(header)
    sim_lines.append("-" * len(header))
    logger.info(header)

    ntimes = len(TIMES)

    for N in args.N_list:
        N_pixel = N - 1
        logger.info(
            f"=== N={N}  (N_pixel={N_pixel}, D={2**N})  "
            f"Jx={JX}  Jz={JZ}  hz={HZ} ==="
        )

        # {scenario_label: [time_data_dict, ...]}
        all_scenario_data: dict[str, list[dict]] = {}
        SCENARIOS = get_scenarios(HZ)

        for scen in SCENARIOS:
            label = scen["label"]
            hz0_val = scen["hz0"]
            logger.info(f"  Scenario: {label}")

            ham = SinglePixelHamiltonianQuSpin(
                N_pixel=N_pixel,
                J=0.0,
                Jpm=1.0,
                Jx=JX,
                Jz=JZ,
                hx=0.0,
                hz=HZ,
                hz0=hz0_val,
                connectivity="chain",
                seed=SEED,
            )

            t0_wall = time.time()
            E, V = ham.diagonalize()
            logger.info(f"    Diagonalized ({time.time()-t0_wall:.1f}s)")

            time_data: list[dict] = []
            for t_val in TIMES:
                analyzer = DisentanglementAnalyzer.from_eigenbasis(E, V, t_val)
                analyzer.get_initial_qubit_states_from_eigenvalues()
                z0, z1, bx0, by0, bx1, by1, phi_az0, phi_az1 = _bloch_coords(analyzer)
                S = born_similarity(z0, z1)
                theta0 = np.arccos(np.clip(z0, -1, 1))

                # Fit wrapped distributions to phi0 theta density
                centers, density, gauss_popt, cauchy_popt = fit_wrapped_distributions(
                    theta0
                )

                time_data.append(
                    dict(
                        t=t_val,
                        z0=z0,
                        z1=z1,
                        bx0=bx0,
                        by0=by0,
                        bx1=bx1,
                        by1=by1,
                        phi_az0=phi_az0,
                        phi_az1=phi_az1,
                        S=S,
                        fit_centers=centers,
                        fit_density=density,
                        gauss_popt=gauss_popt,
                        cauchy_popt=cauchy_popt,
                    )
                )
                line = f"{N:4d}  {label:>10s}  {t_val:12g}  {S:8.4f}"
                logger.info(line)
                sim_lines.append(line)

            all_scenario_data[label] = time_data

            # ---- Figure 1: histogram + Bloch (per scenario) ----
            fig = plt.figure(
                figsize=(4.0 * ntimes, 10.0),
                dpi=120,
                constrained_layout=True,
            )
            for col, td in enumerate(time_data):
                ax_th = fig.add_subplot(3, ntimes, col + 1)
                _plot_theta_hist(
                    ax_th,
                    td["z0"],
                    td["z1"],
                    title=f"t={td['t']:g}   S={td['S']:.3f}",
                )
                ax_ph = fig.add_subplot(3, ntimes, ntimes + col + 1)
                _plot_phi_hist(
                    ax_ph,
                    td["phi_az0"],
                    td["phi_az1"],
                    title=f"t={td['t']:g}",
                )
                ax_bl = fig.add_subplot(
                    3,
                    ntimes,
                    2 * ntimes + col + 1,
                    projection="3d",
                )
                _plot_bloch(
                    ax_bl,
                    td["bx0"],
                    td["by0"],
                    td["z0"],
                    td["bx1"],
                    td["by1"],
                    td["z1"],
                    title=f"t={td['t']:g}",
                )

            safe_label = label.replace("=", "")
            fig.suptitle(
                f"SP[chain,+-] N={N} | J=0 Jpm=1 Jx={JX} " f"Jz={JZ} hz={HZ} {label}",
                fontsize=10,
                fontweight="bold",
                y=1.02,
            )
            out = save_dir / f"N={N}_{safe_label}.png"
            fig.savefig(out, bbox_inches="tight", dpi=150)
            plt.close(fig)
            logger.info(f"  Saved {out}")

        # ---- Figure 2: fit comparison (both scenarios, linear + log) ----
        n_scen = len(SCENARIOS)
        fig2, axes = plt.subplots(
            2 * n_scen,
            ntimes,
            figsize=(4.0 * ntimes, 3.5 * 2 * n_scen),
            constrained_layout=True,
        )

        for si, scen in enumerate(SCENARIOS):
            label = scen["label"]
            td_list = all_scenario_data[label]
            for col, td in enumerate(td_list):
                for scale_idx, log_scale in enumerate([False, True]):
                    row = 2 * si + scale_idx
                    ax = axes[row, col]
                    scale_str = "log" if log_scale else "linear"
                    _plot_density_with_fits(
                        ax,
                        td["fit_centers"],
                        td["fit_density"],
                        td["gauss_popt"],
                        td["cauchy_popt"],
                        title=f"{label}  t={td['t']:g}  ({scale_str})",
                        log_scale=log_scale,
                    )

        fig2.suptitle(
            f"Wrapped-distribution fits  |  N={N}  Jx={JX}  Jz={JZ}  hz={HZ}",
            fontsize=11,
            fontweight="bold",
        )
        out2 = save_dir / f"N={N}_fits.png"
        fig2.savefig(out2, bbox_inches="tight", dpi=150)
        plt.close(fig2)
        logger.info(f"Saved {out2}")

        # ---- Figure 3: comparison (both scenarios overlaid) ----
        fig3, axes3 = plt.subplots(
            2,
            ntimes,
            figsize=(4.0 * ntimes, 7.0),
            constrained_layout=True,
        )
        scen_colors = {"hz0=0": "steelblue", "hz0=hz": "indianred"}
        for col in range(ntimes):
            for row, log_scale in enumerate([False, True]):
                ax = axes3[row, col]
                for scen in SCENARIOS:
                    label = scen["label"]
                    td = all_scenario_data[label][col]
                    bw = td["fit_centers"][1] - td["fit_centers"][0]
                    ax.bar(
                        td["fit_centers"],
                        td["fit_density"],
                        width=bw,
                        alpha=0.3,
                        color=scen_colors[label],
                        label=label,
                    )
                if log_scale:
                    ax.set_yscale("log")
                    # Set lower bound from all visible data
                    all_dens = np.concatenate(
                        [
                            all_scenario_data[s["label"]][col]["fit_density"]
                            for s in SCENARIOS
                        ]
                    )
                    pos = all_dens[all_dens > 0]
                    if len(pos):
                        ax.set_ylim(bottom=pos.min() * 0.3)
                ax.set_xlim(0, np.pi)
                scale_str = "log" if log_scale else "linear"
                t_val = TIMES[col]
                ax.set_xlabel(r"$\theta$", fontsize=7)
                ax.set_ylabel("Density" + (" (log)" if log_scale else ""), fontsize=6)
                ax.tick_params(labelsize=5)
                ax.set_title(f"t={t_val:g}  ({scale_str})", fontsize=7, pad=3)
                ax.legend(fontsize=5, loc="upper right")

        fig3.suptitle(
            f"Scenario comparison  |  N={N}  Jx={JX}  Jz={JZ}  hz={HZ}",
            fontsize=11,
            fontweight="bold",
        )
        out3 = save_dir / f"N={N}_comparison.png"
        fig3.savefig(out3, bbox_inches="tight", dpi=150)
        plt.close(fig3)
        logger.info(f"Saved {out3}")

        # ---- Save similarity table (incrementally) ----
        txt_path = save_dir / "born_similarity.txt"
        txt_path.write_text("\n".join(sim_lines) + "\n", encoding="utf-8")
        logger.info(f"Similarity table updated: {txt_path}")

    logger.info("All done.")


if __name__ == "__main__":
    main()
