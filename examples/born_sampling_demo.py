"""
Born-Distribution Sampling Demo
================================

Samples eigenvalues according to the Born probability distribution,
reconstructs the two qubit states (φ₀, φ₁) from each eigenvalue, and
plots:

1. θ-coordinate histograms for both qubit sets with Born-rule ratio
   overlay (cos²(θ/2) and sin²(θ/2))
2. Both sets of points on the Bloch sphere

For each sampled eigenvalue λ the two qubit states are:

    φ₀ = (a,  a λ)        →  z₀ = (1 − |λ|²) / (1 + |λ|²)
    φ₁ = (−a λ*,  a)      →  z₁ = −z₀

where  a = 1/√(1 + |λ|²).

Usage::

    python examples/born_sampling_demo.py
    python examples/born_sampling_demo.py -n 5000 --seed 123
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse

import matplotlib.pyplot as plt
import numpy as np

from collapse.quantum_utils import (
    get_eigvals_from_z_and_theta,
    sample_from_born_distribution,
)

plt.rcParams["font.family"] = "Arial"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sample eigenvalues from the Born distribution "
        "and visualise the two qubit sets on the Bloch sphere."
    )
    parser.add_argument(
        "-n", type=int, default=10_000, help="Number of eigenvalues (default: 10 000)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)

    # --- Sample eigenvalues ------------------------------------------------
    z = sample_from_born_distribution(args.n, seed=1024)
    phi = rng.uniform(0, 2 * np.pi, args.n)
    eigvals = get_eigvals_from_z_and_theta(z, phi)

    # --- Reconstruct qubit states from eigenvalues -------------------------
    lam = eigvals
    a = 1.0 / np.sqrt(1 + np.abs(lam) ** 2)

    # φ₀ = (a,  a·λ)   normalised
    phi0 = np.column_stack([a, a * lam])
    # φ₁ = (−a·λ*,  a)  normalised
    phi1 = np.column_stack([-a * np.conj(lam), a])

    # z-components
    z0 = np.abs(phi0[:, 0]) ** 2 - np.abs(phi0[:, 1]) ** 2
    z1 = np.abs(phi1[:, 0]) ** 2 - np.abs(phi1[:, 1]) ** 2

    # Bloch-sphere Cartesian coordinates
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
    born = np.cos(x_th / 2) ** 2

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
    ax_r.plot(x_th, born, "k--", lw=1, label=r"$\cos^2(\theta/2)$")
    ax_r.plot(x_th, 1 - born, "k--", lw=1)

    ax_r.set_ylim(0, 1.05)
    ax1.set_xlim(0, np.pi)
    ax1.set_xlabel(r"$\theta$")
    ax1.set_ylabel("Density", color="gray")
    ax1.tick_params(axis="y", labelcolor="gray")
    ax_r.set_ylabel("Fraction")
    ax1.set_title(
        rf"Born sampling  |  $\theta$-histogram  ($n = {args.n:,}$)",
        fontsize=10,
    )

    # -- Panel 2: Bloch sphere ---------------------------------------------
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
