"""
Spherical-Harmonic Projection of Bloch-Sphere Distributions
=============================================================

Demonstrates the spherical-harmonic projection machinery applied to
disentanglement analysis.  A single-pixel chain Hamiltonian is built
and diagonalised, the per-qubit initial states are extracted, and
their distribution on the Bloch sphere is projected onto Y_l^m.

Two functions are projected:

1. **Density** – a histogram-based estimate of the point-cloud density
   of the φ₀ qubit states on the sphere.
2. **Ratio**  – the bin-wise fraction  h₀/(h₀+h₁)  on the sphere,
   which should follow cos²(θ/2) = (1+cos θ)/2 under the Born rule.

The script produces a four-panel figure:

- θ-histogram with Born-rule ratio overlay
- Bloch sphere scatter
- SH power spectrum |a_{l,m}|² of the density
- SH power spectrum |a_{l,m}|² of the ratio

Usage::

    python scripts/spherical_harmonics_demo.py
    python scripts/spherical_harmonics_demo.py -N 9 -t 15 --l-max 8
    python scripts/spherical_harmonics_demo.py --save figures/sh_demo
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse

import matplotlib.pyplot as plt
import numpy as np

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.spherical_harmonics import SphericalHarmonicProjector

plt.rcParams["font.family"] = "Arial"


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _bloch_coordinates(phi_states: np.ndarray):
    """Return (bx, by, bz) Bloch-vector components for an (n, 2) state array."""
    bx = 2 * np.real(np.conj(phi_states[:, 0]) * phi_states[:, 1])
    by = 2 * np.imag(np.conj(phi_states[:, 0]) * phi_states[:, 1])
    bz = np.abs(phi_states[:, 0]) ** 2 - np.abs(phi_states[:, 1]) ** 2
    return bx, by, bz


def _bloch_to_spherical(bx, by, bz):
    """Convert Cartesian Bloch components to (theta, phi) on the unit sphere."""
    theta = np.arccos(np.clip(bz, -1, 1))
    phi = np.arctan2(by, bx) % (2 * np.pi)
    return theta, phi


def _histogram_on_grid(
    theta_pts: np.ndarray,
    phi_pts: np.ndarray,
    grid_theta: np.ndarray,
    grid_phi: np.ndarray,
) -> np.ndarray:
    """
    Bin a point cloud onto the (n_theta, n_phi) projector grid using
    nearest-neighbour assignment.  Returns counts normalised to integrate
    to len(theta_pts) over the sphere (i.e. a density-like quantity).
    """
    # Nearest grid index for each point
    theta_idx = np.argmin(np.abs(theta_pts[:, None] - grid_theta[None, :]), axis=1)
    phi_idx = np.argmin(np.abs(phi_pts[:, None] - grid_phi[None, :]), axis=1)

    counts = np.zeros((len(grid_theta), len(grid_phi)), dtype=np.float64)
    np.add.at(counts, (theta_idx, phi_idx), 1)
    return counts


def _coefficient_power_matrix(expansion) -> np.ma.MaskedArray:
    """Return |a_{l,m}|² as a masked (l_max+1, 2*l_max+1) array.

    Entries with |m| > l are masked so they appear blank in a heatmap.
    """
    coeffs = expansion.as_array(copy=False)
    l_max = expansion.l_max
    power = np.abs(coeffs) ** 2
    mask = np.ones_like(power, dtype=bool)
    for l in range(l_max + 1):
        for m in range(-l, l + 1):
            mask[l, m + l_max] = False
    return np.ma.array(power, mask=mask)


# -------------------------------------------------------------------
# Plotting helpers
# -------------------------------------------------------------------
def _plot_theta_histogram(ax, z0, z1, title, bins=30):
    """θ-histogram with Born-rule ratio overlay (twin-axis pattern)."""
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

    ax_r = ax.twinx()

    ax.bar(centers, h0d, width=bw, alpha=0.22, color="blue", label=r"$\rho_0(\theta)$")
    ax.bar(centers, h1d, width=bw, alpha=0.22, color="red", label=r"$\rho_1(\theta)$")

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
    ax.set_xlim(0, np.pi)
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("Density", color="gray")
    ax.tick_params(axis="y", labelcolor="gray")
    ax_r.set_ylabel("Fraction")
    ax.set_title(title, fontsize=10)


def _plot_bloch_sphere(ax, bx0, by0, bz0, bx1, by1, bz1):
    """Scatter both qubit-state sets on a wireframe Bloch sphere."""
    u = np.linspace(0, 2 * np.pi, 80)
    v = np.linspace(0, np.pi, 80)
    ax.plot_surface(
        np.outer(np.cos(u), np.sin(v)),
        np.outer(np.sin(u), np.sin(v)),
        np.outer(np.ones_like(u), np.cos(v)),
        color="gray",
        alpha=0.1,
    )

    ax.scatter(bx0, by0, bz0, c="blue", s=6, alpha=0.5, label=r"$\phi_0$")
    ax.scatter(bx1, by1, bz1, c="red", s=6, alpha=0.5, label=r"$\phi_1$")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Bloch sphere", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")


def _plot_power_heatmap(ax, power_matrix, l_max, title):
    """2-D heatmap of |a_{l,m}|² over (l, m)."""
    im = ax.pcolormesh(
        np.arange(-l_max, l_max + 2) - 0.5,
        np.arange(l_max + 2) - 0.5,
        power_matrix,
        cmap="viridis",
        shading="flat",
    )
    ax.set_xlabel(r"Order $m$")
    ax.set_ylabel(r"Degree $\ell$")
    ax.set_title(title, fontsize=10)
    ax.set_xticks(np.arange(-l_max, l_max + 1))
    ax.set_yticks(np.arange(l_max + 1))
    ax.invert_yaxis()
    plt.colorbar(im, ax=ax, label=r"$|a_{\ell m}|^2$", pad=0.02)


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="SH projection of Bloch-sphere distributions",
    )
    parser.add_argument("-N", type=int, default=8, help="Total qubits (default: 8)")
    parser.add_argument("-t", type=float, default=10.0, help="Evolution time")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--l-max", type=int, default=6, help="Max SH degree (default: 6)"
    )
    parser.add_argument(
        "--save", type=str, default=None, help="Directory to save figure"
    )
    args = parser.parse_args()

    N_pixel = args.N - 1
    l_max = args.l_max

    print(f"Single-pixel chain: N_pixel={N_pixel}, t={args.t}, l_max={l_max}")

    # --- Build Hamiltonian & diagonalise ----------------------------------
    ham = SinglePixelHamiltonianNumpy(
        N_pixel=N_pixel,
        Jpm=1.0,
        Jx=0.5,
        Jz=0.0,
        hx=0.0,
        hz=1.0,
        connectivity="chain",
        seed=args.seed,
    )
    H = ham.generate()
    E, V = np.linalg.eigh(H)

    # --- Disentangle from eigenbasis --------------------------------------
    analyzer = DisentanglementAnalyzer.from_eigenbasis(E, V, args.t)
    analyzer.get_initial_qubit_states_from_eigenvalues()

    phi0, phi1 = analyzer.phi0, analyzer.phi1

    bx0, by0, bz0 = _bloch_coordinates(phi0)
    bx1, by1, bz1 = _bloch_coordinates(phi1)

    theta0, azim0 = _bloch_to_spherical(bx0, by0, bz0)
    theta1, azim1 = _bloch_to_spherical(bx1, by1, bz1)

    # --- Build projector & histogram on its grid --------------------------
    n_theta = max(l_max + 1, 16)
    n_phi = max(2 * l_max + 1, 32)
    projector = SphericalHarmonicProjector(l_max=l_max, n_theta=n_theta, n_phi=n_phi)

    counts0 = _histogram_on_grid(theta0, azim0, projector.theta, projector.phi)
    counts1 = _histogram_on_grid(theta1, azim1, projector.theta, projector.phi)

    # Density of the φ₀ distribution
    density0 = counts0.astype(np.float64)
    density_expansion = projector.project_samples(density0, real_input=True)
    density_power = _coefficient_power_matrix(density_expansion)

    # Ratio  h₀ / (h₀ + h₁)
    total = counts0 + counts1
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(total > 0, counts0 / total, 0.0)
    ratio_expansion = projector.project_samples(ratio, real_input=True)
    ratio_power = _coefficient_power_matrix(ratio_expansion)

    # --- Figure -----------------------------------------------------------
    fig = plt.figure(figsize=(12, 7.5), dpi=100, constrained_layout=True)

    # Panel 1: θ-histogram + ratio overlay
    ax1 = fig.add_subplot(2, 2, 1)
    _plot_theta_histogram(
        ax1,
        bz0,
        bz1,
        rf"$\theta$-histogram  |  $N_\mathrm{{pixel}}={N_pixel},\; t={args.t}$",
    )

    # Panel 2: Bloch sphere
    ax2 = fig.add_subplot(2, 2, 2, projection="3d")
    _plot_bloch_sphere(ax2, bx0, by0, bz0, bx1, by1, bz1)

    # Panel 3: SH power heatmap of density
    ax3 = fig.add_subplot(2, 2, 3)
    _plot_power_heatmap(
        ax3,
        density_power,
        l_max,
        r"$|a_{\ell m}|^2$ of $\rho_0$ density",
    )

    # Panel 4: SH power heatmap of ratio h₀/(h₀+h₁)
    ax4 = fig.add_subplot(2, 2, 4)
    _plot_power_heatmap(
        ax4,
        ratio_power,
        l_max,
        r"$|a_{\ell m}|^2$ of $h_0/(h_0{+}h_1)$ ratio",
    )

    fig.suptitle(
        f"Spherical-Harmonic Projection  |  "
        rf"$N_\mathrm{{pixel}}={N_pixel},\; t={args.t},\; \ell_\max={l_max}$",
        fontsize=12,
        fontweight="bold",
    )

    if args.save:
        save_dir = Path(args.save)
        save_dir.mkdir(parents=True, exist_ok=True)
        out = save_dir / f"sh_demo_N{args.N}_t{args.t}_lmax{l_max}.png"
        fig.savefig(out, bbox_inches="tight", dpi=150)
        print(f"Saved {out}")
        plt.close(fig)
    else:
        plt.show()


if __name__ == "__main__":
    main()
