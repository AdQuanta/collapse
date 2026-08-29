"""
Single-Pixel Ring – Analytical P(θ) vs Exact Numerics  (hz0 = hz, Jx ≪ J)
=============================================================================

Derives a **semi-analytical** expression for the disentanglement-angle
distribution P(θ) using first-order time-dependent perturbation theory
in Jx / J and compares it with exact numerical diagonalisation.

Theory
------
When Jx = 0 the Hamiltonian is block-diagonal in the qubit-0 basis:

    H₀ = |0⟩⟨0| ⊗ (−hz + H_pixel) + |1⟩⟨1| ⊗ (+hz + H_pixel)

with identical pixel Hamiltonians in both sectors (since Jz = 0 and
hz0 = hz).  The perturbation V = −Jx Σᵢ X₀ Xᵢ couples the two sectors
only via its off-diagonal block V_off = −Jx Σᵢ Xᵢ.

First-order Dyson series gives the (1,0) block of U(t):

    U₁₀⁽¹⁾ = −i ∫₀ᵗ e^{−ihz(t−t')} Uₚ(t−t') V_off e^{ihz t'} Uₚ(t') dt'

from which W₀ = U₀₀⁻¹ U₁₀ is obtained analytically in the pixel
eigenbasis.  Its matrix elements are:

    (W₀)ₘₙ = −Jx Σᵢ ⟨m|Xᵢ|n⟩ · [e^{iωₘₙ t} − e^{−2ihz t}] / (ωₘₙ + 2hz)

where ωₘₙ = εₘ − εₙ are pixel-Hamiltonian energy differences.

The eigenvalues λₖ of this W₀ give θₖ = arccos((1−|λₖ|²)/(1+|λₖ|²)).

Plots produced
~~~~~~~~~~~~~~
1. ``ptheta_comparison.png``  – P(θ) exact vs perturbative (multi-N × multi-t)
2. ``born_ratio_comparison.png`` – Born ratio exact vs perturbative
3. ``jx_convergence.png``  – σ_θ vs Jx showing linear scaling
4. ``ptheta_log_comparison.png`` – same as (1) but log-y scale

Usage::

    python scripts/sp_ring_analytical_ptheta.py --save figures/analytical
    python scripts/sp_ring_analytical_ptheta.py -N 5 7 --save figures/analytical
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import time as timer

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Arial"

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.pauli import build_pauli_operators

# ===================================================================
# Constants
# ===================================================================
SEED = 44
TIMES = [100.0, 1_000.0, 10_000.0, 1_000_000.0]
JX_UNSCALED_DEFAULT = 0.01
HZ_DEFAULT = 0.1

# Jx values for the convergence study (unscaled)
JX_CONVERGENCE = [0.001, 0.003, 0.01, 0.03, 0.1]

N_BINS = 50  # histogram bins on [0, π]


# ===================================================================
# Build the pixel-only ring Hamiltonian  (qubits 1…N_pixel)
# ===================================================================
def build_pixel_ring_hamiltonian(N_pixel: int, J: float, hz: float) -> np.ndarray:
    """
    H_pixel = −J Σ_{ring} Z_i Z_j − hz Σ_i Z_i

    for N_pixel qubits in a ring.  Returns a (2^N_pixel × 2^N_pixel) matrix.
    """
    D = 2**N_pixel
    Xs, Zs = build_pauli_operators(N_pixel)
    H = np.zeros((D, D), dtype=np.float64)

    # Ring ZZ bonds: (0,1), (1,2), …, (N_pixel-2, N_pixel-1), (N_pixel-1, 0)
    for k in range(N_pixel):
        j = (k + 1) % N_pixel
        H -= J * (Zs[k] @ Zs[j])

    # Longitudinal field
    for k in range(N_pixel):
        H -= hz * Zs[k]

    return H


# ===================================================================
# Pixel X-sum operator:  Σᵢ Xᵢ  in the pixel eigenbasis
# ===================================================================
def pixel_xsum_matrix_elements(V_pixel: np.ndarray, N_pixel: int) -> np.ndarray:
    """
    Compute ⟨m| Σᵢ Xᵢ |n⟩ in the pixel eigenbasis.

    Parameters
    ----------
    V_pixel : (D_p, D_p) eigenvectors of H_pixel (columns)
    N_pixel : number of pixel qubits

    Returns
    -------
    X_sum_eig : (D_p, D_p) matrix of ⟨m|Σ Xᵢ|n⟩
    """
    Xs, _ = build_pauli_operators(N_pixel)
    D_p = 2**N_pixel
    X_sum = np.zeros((D_p, D_p), dtype=np.float64)
    for k in range(N_pixel):
        X_sum += Xs[k]

    # Transform to eigenbasis: V† X_sum V
    return V_pixel.conj().T @ X_sum @ V_pixel


# ===================================================================
# Perturbative W₀ matrix  (first order in Jx)
# ===================================================================
def perturbative_W0(
    E_pixel: np.ndarray,
    V_pixel: np.ndarray,
    N_pixel: int,
    Jx: float,
    hz: float,
    t: float,
) -> np.ndarray:
    r"""
    Compute the W₀ = U₀₀⁻¹ U₁₀ matrix to first order in Jx.

    (W₀)ₘₙ = −Jx · ⟨m|Σ Xᵢ|n⟩ · [e^{iωₘₙ t} − e^{−2ihz t}] / (ωₘₙ + 2hz)

    where ωₘₙ = εₘ − εₙ.
    """
    D_p = len(E_pixel)
    X_mn = pixel_xsum_matrix_elements(V_pixel, N_pixel)

    # Energy differences ωₘₙ = εₘ − εₙ
    omega = E_pixel[:, None] - E_pixel[None, :]  # (D_p, D_p)

    # Denominator: ωₘₙ + 2hz
    denom = omega + 2.0 * hz

    # Numerator: e^{iωₘₙ t} − e^{−2ihz t}
    phase_omega = np.exp(1j * omega * t)
    phase_hz = np.exp(-2j * hz * t)
    numer = phase_omega - phase_hz

    # Handle near-zero denominator (resonance ωₘₙ ≈ −2hz)
    # In that case, use L'Hôpital: limit → i·t·e^{iωₘₙ t}
    mask = np.abs(denom) < 1e-12
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(mask, 1j * t * phase_omega, numer / denom)

    W0 = -Jx * X_mn * ratio
    return W0


# ===================================================================
# Extract θ from eigenvalues of W₀
# ===================================================================
def eigenvalues_to_theta(lambdas: np.ndarray) -> np.ndarray:
    """Map W₀ eigenvalues to Bloch polar angles θ ∈ [0, π]."""
    abs_lam_sq = np.abs(lambdas) ** 2
    z = (1.0 - abs_lam_sq) / (1.0 + abs_lam_sq)
    return np.arccos(np.clip(z, -1.0, 1.0))


# ===================================================================
# Exact computation via full Hamiltonian
# ===================================================================
def exact_theta(
    N_pixel: int,
    J: float,
    Jx: float,
    hz: float,
    t: float,
    seed: int = SEED,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute exact θ₀, θ₁ arrays from full diagonalisation.

    Returns (theta0, theta1) arrays of length D/2 = 2^N_total / 2.
    """
    ham = SinglePixelHamiltonianNumpy(
        N_pixel=N_pixel,
        J=J,
        Jx=Jx,
        Jz=0.0,
        hx=0.0,
        hz=hz,
        hz0=None,  # hz0 = hz
        connectivity="ring",
        seed=seed,
    )
    H = ham.generate()
    N_total = N_pixel + 1
    E, V = np.linalg.eigh(H)

    analyzer = DisentanglementAnalyzer.from_eigenbasis(E, V, t)
    analyzer.get_initial_qubit_states_from_eigenvalues()

    z0 = np.abs(analyzer.phi0[:, 0]) ** 2 - np.abs(analyzer.phi0[:, 1]) ** 2
    z1 = np.abs(analyzer.phi1[:, 0]) ** 2 - np.abs(analyzer.phi1[:, 1]) ** 2
    theta0 = np.arccos(np.clip(z0, -1.0, 1.0))
    theta1 = np.arccos(np.clip(z1, -1.0, 1.0))
    return theta0, theta1


# ===================================================================
# Perturbative computation
# ===================================================================
def perturbative_theta(
    N_pixel: int,
    J: float,
    Jx: float,
    hz: float,
    t: float,
) -> np.ndarray:
    """
    Compute θ from the perturbative W₀ eigenvalues.

    Returns theta array of length 2^N_pixel.
    """
    H_pix = build_pixel_ring_hamiltonian(N_pixel, J, hz)
    E_pix, V_pix = np.linalg.eigh(H_pix)
    W0 = perturbative_W0(E_pix, V_pix, N_pixel, Jx, hz, t)
    lambdas = np.linalg.eigvals(W0)
    return eigenvalues_to_theta(lambdas)


# ===================================================================
# Born ratio computation from θ₀, θ₁ arrays
# ===================================================================
def born_ratio(theta0, theta1, n_bins=N_BINS):
    """Compute histogram-based Born ratio f(θ) = h₀/(h₀+h₁)."""
    edges = np.linspace(0, np.pi, n_bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    h0, _ = np.histogram(theta0, bins=edges)
    h1, _ = np.histogram(theta1, bins=edges)
    total = h0 + h1
    mask = (h0 > 0) & (h1 > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(mask, h0 / total, np.nan)
    return centers, ratio, mask


def born_similarity(z0, z1, n_theta=100):
    r"""S = 1 − 2 ∫₀^π |f(θ) − cos²(θ/2)| sin θ dθ."""
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
# Plotting helpers
# ===================================================================
def plot_ptheta_comparison(
    all_data: dict,
    save_dir: Path,
    hz_val: float,
    jx_val: float,
    log_scale: bool = False,
):
    """
    Figure: P(θ) exact vs perturbative.

    all_data : {N: {t: {"exact_theta0": ..., "exact_theta1": ...,
                         "pert_theta": ...}}}
    """
    N_list = sorted(all_data.keys())
    n_rows = len(N_list)
    n_cols = len(TIMES)

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(4.0 * n_cols, 3.2 * n_rows),
        constrained_layout=True,
        squeeze=False,
    )

    edges = np.linspace(0, np.pi, N_BINS + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    bw = edges[1] - edges[0]

    for ri, N in enumerate(N_list):
        for ci, t_val in enumerate(TIMES):
            ax = axes[ri, ci]
            d = all_data[N][t_val]

            # Exact: density of theta0
            h_ex, _ = np.histogram(d["exact_theta0"], bins=edges, density=True)
            ax.bar(
                centers, h_ex, width=bw, alpha=0.35, color="steelblue",
                label="Exact",
            )

            # Perturbative
            h_pt, _ = np.histogram(d["pert_theta"], bins=edges, density=True)
            ax.step(
                edges[:-1], h_pt, where="post", color="crimson", lw=1.6,
                label="Perturbative",
            )

            if log_scale:
                ax.set_yscale("log")
                all_h = np.concatenate([h_ex[h_ex > 0], h_pt[h_pt > 0]])
                if len(all_h):
                    ax.set_ylim(bottom=all_h.min() * 0.3)

            ax.set_xlim(0, np.pi)
            ax.set_xlabel(r"$\theta$", fontsize=8)
            if ci == 0:
                ax.set_ylabel(f"N={N}\nDensity", fontsize=8)
            ax.set_title(f"t = {t_val:g}", fontsize=8, fontweight="bold")
            ax.tick_params(labelsize=6)
            if ri == 0 and ci == n_cols - 1:
                ax.legend(fontsize=6, loc="upper right")

    suffix = "_log" if log_scale else ""
    scale_str = " (log scale)" if log_scale else ""
    fig.suptitle(
        rf"$P(\theta)$ — Exact vs 1st-order Perturbation Theory{scale_str}"
        f"\n"
        rf"SP[ring], $h_z = h_{{z0}} = {hz_val}$, "
        rf"$J_x = {jx_val}/\sqrt{{N_p}}$, $J = 1$",
        fontsize=11, fontweight="bold",
    )
    out = save_dir / f"ptheta_comparison{suffix}.png"
    fig.savefig(out, bbox_inches="tight", dpi=180)
    plt.close(fig)
    print(f"  Saved {out}")


def plot_born_ratio_comparison(all_data: dict, save_dir: Path, hz_val: float, jx_val: float):
    """
    Figure: Born ratio f(θ) = P(θ)/(P(θ)+P(π−θ)) exact vs perturbative.
    """
    N_list = sorted(all_data.keys())
    n_rows = len(N_list)
    n_cols = len(TIMES)

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(4.0 * n_cols, 3.0 * n_rows),
        constrained_layout=True,
        squeeze=False,
    )

    x_born = np.linspace(0, np.pi, 500)
    y_born = np.cos(x_born / 2) ** 2

    for ri, N in enumerate(N_list):
        for ci, t_val in enumerate(TIMES):
            ax = axes[ri, ci]
            d = all_data[N][t_val]

            # Exact Born ratio
            centers_ex, ratio_ex, mask_ex = born_ratio(
                d["exact_theta0"], d["exact_theta1"]
            )
            ax.plot(
                centers_ex[mask_ex], ratio_ex[mask_ex],
                "o", ms=3, color="steelblue", alpha=0.7, label="Exact",
            )

            # Perturbative Born ratio
            # For the perturbative result, θ₁ = π − θ₀ by construction
            pert_theta0 = d["pert_theta"]
            pert_theta1 = np.pi - pert_theta0
            centers_pt, ratio_pt, mask_pt = born_ratio(pert_theta0, pert_theta1)
            ax.plot(
                centers_pt[mask_pt], ratio_pt[mask_pt],
                "s", ms=2.5, color="crimson", alpha=0.7, label="Perturbative",
            )

            # Born reference
            ax.plot(x_born, y_born, "k--", lw=0.8, label=r"$\cos^2(\theta/2)$")
            ax.plot(x_born, 1 - y_born, "k--", lw=0.8)

            ax.set_ylim(-0.02, 1.02)
            ax.set_xlim(0, np.pi)
            ax.set_xlabel(r"$\theta$", fontsize=8)
            if ci == 0:
                ax.set_ylabel(f"N={N}\nRatio", fontsize=8)
            ax.set_title(f"t = {t_val:g}", fontsize=8, fontweight="bold")
            ax.tick_params(labelsize=6)
            if ri == 0 and ci == n_cols - 1:
                ax.legend(fontsize=5.5, loc="center right")

    fig.suptitle(
        r"Born Ratio $P(\theta)/[P(\theta)+P(\pi-\theta)]$ — Exact vs Perturbative"
        f"\n"
        rf"SP[ring], $h_z = h_{{z0}} = {hz_val}$, "
        rf"$J_x = {jx_val}/\sqrt{{N_p}}$",
        fontsize=11, fontweight="bold",
    )
    out = save_dir / "born_ratio_comparison.png"
    fig.savefig(out, bbox_inches="tight", dpi=180)
    plt.close(fig)
    print(f"  Saved {out}")


def plot_jx_convergence(conv_data: dict, save_dir: Path, hz_val: float):
    """
    Figure: σ_θ vs Jx for multiple N and t values, showing linear scaling.

    conv_data : {N: {t: {Jx_unscaled: {"exact_std": ..., "pert_std": ...}}}}
    """
    N_list = sorted(conv_data.keys())
    n_cols = len(TIMES)
    n_rows = len(N_list)

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(4.0 * n_cols, 3.2 * n_rows),
        constrained_layout=True,
        squeeze=False,
    )

    for ri, N in enumerate(N_list):
        for ci, t_val in enumerate(TIMES):
            ax = axes[ri, ci]
            jx_vals = sorted(conv_data[N][t_val].keys())
            ex_stds = [conv_data[N][t_val][jx]["exact_std"] for jx in jx_vals]
            pt_stds = [conv_data[N][t_val][jx]["pert_std"] for jx in jx_vals]

            ax.loglog(
                jx_vals, ex_stds, "o-", color="steelblue", ms=5, lw=1.3,
                label="Exact σ_θ",
            )
            ax.loglog(
                jx_vals, pt_stds, "s--", color="crimson", ms=4, lw=1.3,
                label="Pert. σ_θ",
            )

            # Linear reference: σ ∝ Jx
            jx_arr = np.array(jx_vals)
            if len(ex_stds) > 1 and ex_stds[0] > 0:
                ref = ex_stds[0] * (jx_arr / jx_arr[0])
                ax.loglog(jx_arr, ref, ":", color="gray", lw=0.8, label=r"$\propto J_x$")

            ax.set_xlabel(r"$J_x$ (unscaled)", fontsize=8)
            if ci == 0:
                ax.set_ylabel(f"N={N}\n" + r"$\sigma_\theta$", fontsize=8)
            ax.set_title(f"t = {t_val:g}", fontsize=8, fontweight="bold")
            ax.tick_params(labelsize=6)
            if ri == 0 and ci == n_cols - 1:
                ax.legend(fontsize=5.5, loc="lower right")

    fig.suptitle(
        r"Convergence: $\sigma_\theta$ vs $J_x$  (should be linear for $J_x \ll J$)"
        f"\nSP[ring], hz = hz0 = {hz_val}, J = 1",
        fontsize=11, fontweight="bold",
    )
    out = save_dir / "jx_convergence.png"
    fig.savefig(out, bbox_inches="tight", dpi=180)
    plt.close(fig)
    print(f"  Saved {out}")


def plot_eigenvalue_comparison(all_data: dict, save_dir: Path, jx_val: float):
    """
    Figure: scatter of exact |λ| vs perturbative |λ| (sorted) for one N, one t.
    """
    N_list = sorted(all_data.keys())
    n_cols = len(TIMES)

    fig, axes = plt.subplots(
        1, n_cols,
        figsize=(4.0 * n_cols, 3.5),
        constrained_layout=True,
        squeeze=False,
    )

    N = N_list[-1]  # use largest N
    for ci, t_val in enumerate(TIMES):
        ax = axes[0, ci]
        d = all_data[N][t_val]

        exact_lam = np.sort(np.abs(d["exact_lambdas"]))
        pert_lam = np.sort(np.abs(d["pert_lambdas"]))

        # They may differ in length (exact has D/2, pert has D_pixel)
        # Use the shorter length
        n_common = min(len(exact_lam), len(pert_lam))
        ax.scatter(
            exact_lam[:n_common], pert_lam[:n_common],
            s=6, alpha=0.4, color="darkorchid", edgecolors="none",
        )

        # Perfect agreement line
        lim = max(exact_lam[:n_common].max(), pert_lam[:n_common].max()) * 1.1
        ax.plot([0, lim], [0, lim], "k--", lw=0.7, alpha=0.5)
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_xlabel(r"$|\lambda|$ exact", fontsize=8)
        ax.set_ylabel(r"$|\lambda|$ perturbative", fontsize=8)
        ax.set_title(f"t = {t_val:g}", fontsize=8, fontweight="bold")
        ax.tick_params(labelsize=6)
        ax.set_aspect("equal")

    fig.suptitle(
        rf"Eigenvalue comparison $|\lambda_k|$  |  N={N}, "
        rf"$J_x = {jx_val}/\sqrt{{{N-1}}}$",
        fontsize=11, fontweight="bold",
    )
    out = save_dir / "eigenvalue_comparison.png"
    fig.savefig(out, bbox_inches="tight", dpi=180)
    plt.close(fig)
    print(f"  Saved {out}")


# ===================================================================
# Main
# ===================================================================
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Analytical P(θ) vs exact numerics for SP[ring] with hz0=hz, Jx≪J."
        )
    )
    parser.add_argument(
        "-N", "--N", type=int, nargs="+", default=[5, 7, 9], dest="N_list",
        help="Total qubit counts (default: 5 7 9)",
    )
    parser.add_argument(
        "--hz", type=float, default=HZ_DEFAULT,
        help=f"Longitudinal field (default: {HZ_DEFAULT})",
    )
    parser.add_argument(
        "--Jx", type=float, default=JX_UNSCALED_DEFAULT,
        help=f"Unscaled central XX coupling (default: {JX_UNSCALED_DEFAULT})",
    )
    parser.add_argument("--save", type=str, required=True)
    args = parser.parse_args()

    save_dir = Path(args.save)
    save_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"=== Analytical P(θ) comparison ===\n"
        f"  N = {args.N_list},  Jx = {args.Jx},  hz = {args.hz}\n"
        f"  Times = {TIMES}\n"
        f"  Output: {save_dir}\n"
    )

    # ==============================================================
    # Part 1: P(θ) comparison (exact vs perturbative)
    # ==============================================================
    print("--- Part 1: P(θ) exact vs perturbative ---")
    all_data: dict = {}

    for N in args.N_list:
        N_pixel = N - 1
        Jx_scaled = args.Jx / np.sqrt(N_pixel)
        print(f"\n  N = {N}  (N_pixel = {N_pixel}, D = {2**N})")
        print(f"  Jx_scaled = {args.Jx}/√{N_pixel} = {Jx_scaled:.6f}")

        all_data[N] = {}

        # Pre-compute pixel eigenbasis (used for all times)
        t0 = timer.time()
        H_pix = build_pixel_ring_hamiltonian(N_pixel, J=1.0, hz=args.hz)
        E_pix, V_pix = np.linalg.eigh(H_pix)
        print(f"  Pixel diag: {timer.time()-t0:.2f}s")

        # Pre-compute exact eigenbasis (used for all times)
        t0 = timer.time()
        ham = SinglePixelHamiltonianNumpy(
            N_pixel=N_pixel, J=1.0, Jx=Jx_scaled, Jz=0.0,
            hx=0.0, hz=args.hz, hz0=None,
            connectivity="ring", seed=SEED,
        )
        H_full = ham.generate()
        E_full, V_full = np.linalg.eigh(H_full)
        print(f"  Full diag:  {timer.time()-t0:.2f}s")

        for t_val in TIMES:
            t0 = timer.time()

            # --- Exact ---
            analyzer = DisentanglementAnalyzer.from_eigenbasis(E_full, V_full, t_val)
            analyzer.get_initial_qubit_states_from_eigenvalues()
            z0 = np.abs(analyzer.phi0[:, 0]) ** 2 - np.abs(analyzer.phi0[:, 1]) ** 2
            z1 = np.abs(analyzer.phi1[:, 0]) ** 2 - np.abs(analyzer.phi1[:, 1]) ** 2
            theta0_ex = np.arccos(np.clip(z0, -1.0, 1.0))
            theta1_ex = np.arccos(np.clip(z1, -1.0, 1.0))

            # Also grab the exact eigenvalues of W0 from the analyzer
            exact_lambdas = analyzer.D0.copy()

            # --- Perturbative ---
            W0 = perturbative_W0(E_pix, V_pix, N_pixel, Jx_scaled, args.hz, t_val)
            pert_lambdas = np.linalg.eigvals(W0)
            theta_pt = eigenvalues_to_theta(pert_lambdas)

            # Born similarity for exact
            S_ex = born_similarity(z0, z1)

            elapsed = timer.time() - t0
            print(
                f"    t = {t_val:>10g}  "
                f"σ_θ(exact) = {np.std(theta0_ex):.4f}  "
                f"σ_θ(pert) = {np.std(theta_pt):.4f}  "
                f"S_born(exact) = {S_ex:.4f}  "
                f"({elapsed:.2f}s)"
            )

            all_data[N][t_val] = {
                "exact_theta0": theta0_ex,
                "exact_theta1": theta1_ex,
                "pert_theta": theta_pt,
                "exact_lambdas": exact_lambdas,
                "pert_lambdas": pert_lambdas,
                "S_born": S_ex,
            }

    # --- Generate P(θ) comparison plots ---
    print("\n--- Generating P(θ) comparison plots ---")
    plot_ptheta_comparison(all_data, save_dir, args.hz, args.Jx, log_scale=False)
    plot_ptheta_comparison(all_data, save_dir, args.hz, args.Jx, log_scale=True)

    # --- Born ratio comparison ---
    print("--- Generating Born ratio comparison ---")
    plot_born_ratio_comparison(all_data, save_dir, args.hz, args.Jx)

    # --- Eigenvalue scatter ---
    print("--- Generating eigenvalue comparison ---")
    plot_eigenvalue_comparison(all_data, save_dir, args.Jx)

    # ==============================================================
    # Part 2: Jx convergence study
    # ==============================================================
    print("\n--- Part 2: Jx convergence study ---")
    conv_data: dict = {}

    for N in args.N_list:
        N_pixel = N - 1
        print(f"\n  N = {N}  (N_pixel = {N_pixel})")
        conv_data[N] = {}

        # Pre-compute pixel eigenbasis
        H_pix = build_pixel_ring_hamiltonian(N_pixel, J=1.0, hz=args.hz)
        E_pix, V_pix = np.linalg.eigh(H_pix)

        for t_val in TIMES:
            conv_data[N][t_val] = {}

            for Jx_unscaled in JX_CONVERGENCE:
                Jx_s = Jx_unscaled / np.sqrt(N_pixel)

                # Exact
                theta0_ex, theta1_ex = exact_theta(
                    N_pixel, J=1.0, Jx=Jx_s, hz=args.hz, t=t_val,
                )

                # Perturbative
                W0 = perturbative_W0(E_pix, V_pix, N_pixel, Jx_s, args.hz, t_val)
                pert_lam = np.linalg.eigvals(W0)
                theta_pt = eigenvalues_to_theta(pert_lam)

                conv_data[N][t_val][Jx_unscaled] = {
                    "exact_std": np.std(theta0_ex),
                    "pert_std": np.std(theta_pt),
                }

            # Print summary for this (N, t)
            for Jx_u in JX_CONVERGENCE:
                d = conv_data[N][t_val][Jx_u]
                print(
                    f"    t={t_val:>10g}  Jx={Jx_u:>6.3f}  "
                    f"σ_exact={d['exact_std']:.5f}  "
                    f"σ_pert={d['pert_std']:.5f}  "
                    f"ratio={d['pert_std']/max(d['exact_std'],1e-15):.4f}"
                )

    print("\n--- Generating Jx convergence plot ---")
    plot_jx_convergence(conv_data, save_dir)

    # ==============================================================
    # Part 3: Summary table
    # ==============================================================
    print("\n--- Writing summary table ---")
    lines = []
    header = (
        f"{'N':>4s}  {'t':>12s}  {'Jx_unsc':>8s}  "
        f"{'σ_exact':>10s}  {'σ_pert':>10s}  {'ratio':>8s}  {'S_born':>8s}"
    )
    lines.append(header)
    lines.append("-" * len(header))

    for N in sorted(all_data.keys()):
        for t_val in TIMES:
            d = all_data[N][t_val]
            lines.append(
                f"{N:4d}  {t_val:12g}  {args.Jx:8.4f}  "
                f"{np.std(d['exact_theta0']):10.6f}  "
                f"{np.std(d['pert_theta']):10.6f}  "
                f"{np.std(d['pert_theta'])/max(np.std(d['exact_theta0']),1e-15):8.4f}  "
                f"{d['S_born']:8.4f}"
            )

    lines.append("")
    lines.append("# Jx convergence")
    lines.append(
        f"{'N':>4s}  {'t':>12s}  {'Jx_unsc':>8s}  "
        f"{'σ_exact':>10s}  {'σ_pert':>10s}  {'ratio':>8s}"
    )
    lines.append("-" * 70)
    for N in sorted(conv_data.keys()):
        for t_val in TIMES:
            for Jx_u in JX_CONVERGENCE:
                d = conv_data[N][t_val][Jx_u]
                lines.append(
                    f"{N:4d}  {t_val:12g}  {Jx_u:8.4f}  "
                    f"{d['exact_std']:10.6f}  "
                    f"{d['pert_std']:10.6f}  "
                    f"{d['pert_std']/max(d['exact_std'],1e-15):8.4f}"
                )

    txt_path = save_dir / "summary.txt"
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Saved {txt_path}")

    print("\nAll done.")


if __name__ == "__main__":
    main()
