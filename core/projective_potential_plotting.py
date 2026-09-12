"""Scientific plots of the native nonnormal thermodynamic counterexample."""

from pathlib import Path

import numpy as np

from core.born_structure_plotting import plt, save_figure


def plot_nonnormal_limit(
    output: Path, sizes: np.ndarray, cutoffs: np.ndarray,
    clipped: np.ndarray, lost: np.ndarray, flips: np.ndarray,
    x: np.ndarray, gaussian_j: np.ndarray, gaussian_flip: float,
    *, coupling: float, time: float,
) -> None:
    """Plot saved exact-form and quadrature data; no root or solver calls."""
    fig, axes = plt.subplots(1, 3, figsize=(11.7, 3.5))
    axes[0].semilogx(sizes, flips, "o-", label="native normalized trace")
    axes[0].axhline(gaussian_flip, color="#bb5939", ls="--", label="proved Gaussian trace limit")
    axes[0].set(xlabel="detector spins N", ylabel=r"$\tau(C^\dagger C)$")
    axes[1].semilogx(sizes, np.ones_like(sizes), "o-", label="native projective roots")
    axes[1].axhline(1-2*gaussian_flip, color="#bb5939", ls="--", label="roots of Gaussian blocks")
    axes[1].set(xlabel="detector spins N", ylabel=r"first root moment $a_1$")
    axes[2].plot(x, x, color="#225e91", label="native, every regular N")
    axes[2].plot(x, gaussian_j, "--", color="#bb5939", label="roots of Gaussian blocks")
    axes[2].set(xlabel=r"log radius $x$", ylabel=r"normalized potential $J(x)$")
    for ax in axes:
        ax.grid(alpha=.2)
        ax.legend(fontsize=7)
    fig.suptitle(f"Native exchange: trace convergence does not imply root convergence (g={coupling:g}, t={time:g})")
    fig.tight_layout()
    save_figure(fig, output/"native_gaussian_mismatch")

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9))
    for col, cutoff in enumerate(cutoffs):
        axes[0].semilogx(sizes, clipped[:, 0, col], "o-", label=rf"cutoff $\eta={cutoff:g}$")
        axes[1].semilogx(sizes, lost[:, 0, col], "o-", label=rf"$\eta={cutoff:g}$")
    target = np.interp(-1., x, gaussian_j)
    axes[0].axhline(-1., color="#225e91", lw=1, label="exact native J(-1)")
    axes[0].axhline(target, color="#bb5939", ls="--", label="Gaussian root J(-1)")
    axes[0].set(xlabel="detector spins N", ylabel=r"potential from $\log\max(s,\eta)$")
    axes[1].set(xlabel="detector spins N", ylabel=r"lost log integral at radius $e^{-1}$")
    for ax in axes:
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle("Small singular values retain information lost by a fixed cutoff")
    fig.tight_layout()
    save_figure(fig, output/"singular_log_cutoff")
