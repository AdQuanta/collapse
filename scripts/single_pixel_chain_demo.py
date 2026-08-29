"""
Single-Pixel Chain Demo
========================

Simulates the single-pixel model with chain connectivity, extracts
per-qubit initial states via disentanglement analysis, and plots:

1. θ-component histogram with Born-rule ratio overlay
2. Points on the Bloch sphere

The computation follows the eigenbasis approach used in
``full_hamiltonian_scan.py``: diagonalise H once, then build the
analyser from the eigenbasis for the chosen time.

Usage::

    python scripts/single_pixel_chain_demo.py
    python scripts/single_pixel_chain_demo.py -N 9 -t 15
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse

import matplotlib.pyplot as plt
import numpy as np

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-pixel chain demo")
    parser.add_argument("-N", type=int, default=8, help="Total qubits (default: 8)")
    parser.add_argument("-t", type=float, default=10.0, help="Evolution time")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    N_pixel = args.N - 1

    print(f"Single-pixel chain: N_pixel={N_pixel}, t={args.t}")

    # --- Build Hamiltonian & diagonalise once -----------------------------
    ham = SinglePixelHamiltonianNumpy(
        N_pixel=N_pixel,
        J=1.0,
        Jx=10.0,
        Jz=10.0,
        hx=1.0,
        hz=1.0,
        connectivity="chain",
        seed=args.seed,
    )
    H = ham.generate()
    E, V = np.linalg.eigh(H)

    # --- Disentangle from eigenbasis -------------------------------------
    analyzer = DisentanglementAnalyzer.from_eigenbasis(E, V, args.t)
    analyzer.get_initial_qubit_states_from_eigenvalues()

    phi0, phi1 = analyzer.phi0, analyzer.phi1

    # z-components
    z0 = np.abs(phi0[:, 0]) ** 2 - np.abs(phi0[:, 1]) ** 2
    z1 = np.abs(phi1[:, 0]) ** 2 - np.abs(phi1[:, 1]) ** 2

    # Bloch coordinates
    bx0 = 2 * np.real(np.conj(phi0[:, 0]) * phi0[:, 1])
    by0 = 2 * np.imag(np.conj(phi0[:, 0]) * phi0[:, 1])
    bz0 = z0

    bx1 = 2 * np.real(np.conj(phi1[:, 0]) * phi1[:, 1])
    by1 = 2 * np.imag(np.conj(phi1[:, 0]) * phi1[:, 1])
    bz1 = z1

    # --- Figure -----------------------------------------------------------
    fig = plt.figure(figsize=(13, 5), dpi=120, constrained_layout=True)

    # -- Panel 1: θ-histogram + ratio overlay ------------------------------
    ax1 = fig.add_subplot(1, 2, 1)
    bins = 30

    theta0 = np.arccos(np.clip(z0, -1, 1))
    theta1 = np.arccos(np.clip(z1, -1, 1))
    bin_edges = np.linspace(0, np.pi, bins + 1)
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bw = bin_edges[1] - bin_edges[0]

    h0d, _ = np.histogram(theta0, bins=bin_edges, density=True)
    h1d, _ = np.histogram(theta1, bins=bin_edges, density=True)
    h0c, _ = np.histogram(theta0, bins=bin_edges)
    h1c, _ = np.histogram(theta1, bins=bin_edges)
    hs = h0c + h1c
    mask = (h0c > 0) & (h1c > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        r0 = np.where(mask, h0c / hs, np.nan)
        r1 = np.where(mask, h1c / hs, np.nan)

    x_th = np.linspace(0, np.pi, 1000)
    born = (1 + np.cos(x_th)) / 2

    ax_r = ax1.twinx()

    # background: density histograms
    ax1.bar(centers, h0d, width=bw, alpha=0.22, color="blue", label=r"$\rho_0(\theta)$")
    ax1.bar(centers, h1d, width=bw, alpha=0.22, color="red", label=r"$\rho_1(\theta)$")

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
    ax1.set_xlim(0, np.pi)
    ax1.set_xlabel(r"$\theta$")
    ax1.set_ylabel("Density", color="gray")
    ax1.tick_params(axis="y", labelcolor="gray")
    ax_r.set_ylabel("Fraction")
    ax1.set_title(
        f"Single-pixel chain  |  "
        r"$\theta$"
        f"-histogram\n"
        rf"$N_\mathrm{{pixel}}={N_pixel},\; t={args.t}$",
        fontsize=10,
    )

    # -- Panel 2: Bloch sphere --------------------------------------------
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")

    u = np.linspace(0, 2 * np.pi, 80)
    v = np.linspace(0, np.pi, 80)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    ax2.plot_surface(xs, ys, zs, color="gray", alpha=0.1)

    ax2.scatter(bx0, by0, bz0, c="blue", s=6, alpha=0.5, label=r"$\phi_0$")
    ax2.scatter(bx1, by1, bz1, c="red", s=6, alpha=0.5, label=r"$\phi_1$")

    ax2.set_xlabel("X")
    ax2.set_ylabel("Y")
    ax2.set_zlabel("Z")
    ax2.set_title("Bloch sphere", fontsize=10)
    ax2.legend(fontsize=8, loc="upper left")

    plt.show()


if __name__ == "__main__":
    main()
