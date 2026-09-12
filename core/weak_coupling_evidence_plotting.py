"""Plots of saved ring evidence, without fitting or smoothing."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_ring_evidence(output: Path, records: list[dict], scans: dict) -> None:
    """Render densities, reflected ratios, size trends, and field sensitivity."""
    names = list(dict.fromkeys(row["candidate"] for row in records))
    fig, axes = plt.subplots(3, 2, figsize=(10, 9), constrained_layout=True)
    for column, name in enumerate(names):
        row = max((r for r in records if r["candidate"] == name), key=lambda r: r["N"])
        x = np.array(row["centers"])
        density = np.array(row["density"])
        axes[0, column].plot(x, density, label=r"$P_N(\theta)$")
        axes[0, column].plot(x, row["reflected_density"], label=r"$P_N(\pi-\theta)$")
        axes[0, column].set_title(f"{name.replace('_', ' ')}; N={row['N']}")
        axes[0, column].set_ylabel(r"Density [rad$^{-1}$]")
        axes[0, column].legend()
        target = np.cos(x / 2)**2
        axes[1, column].plot(x, row["ratio"], label="Saved roots")
        axes[1, column].plot(x, target, "k--", label=r"$\cos^2(\theta/2)$")
        axes[1, column].set_ylabel(r"$R_N(\theta)$")
        axes[1, column].legend()
        axes[2, column].plot(x, np.array(row["ratio"]) - target)
        axes[2, column].axhline(0, color="k", linewidth=.7)
        axes[2, column].set_ylabel("Ratio residual")
    for ax in axes.flat:
        ax.set_xlabel(r"$\theta$ [rad]")
        ax.set_xlim(0, np.pi)
    fig.suptitle(r"Existing ring snapshots: $t=10^6$, $g_x/\sqrt{N}$, $g_y=g_z=0$")
    for suffix in ("png", "pdf"):
        fig.savefig(output / f"ring_profiles.{suffix}", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), constrained_layout=True)
    for name in names:
        rows = sorted((r for r in records if r["candidate"] == name), key=lambda r: r["N"])
        label = name.replace("_", " ")
        axes[0].plot([r["N"] for r in rows], [r["global_rmse"] for r in rows], "o-", label=label)
        axes[1].plot([r["N"] for r in rows], [r["moment_max"] for r in rows], "o-", label=label)
        scan = sorted(scans[name], key=lambda r: r["hz0_over_hz"])
        axes[2].plot([r["hz0_over_hz"] for r in scan], [r["global_RMSE"] for r in scan], "o", label=label)
    axes[0].set_ylabel("64-bin ratio RMSE")
    axes[1].set_ylabel("Maximum of 8 moment residuals")
    for ax in axes[:2]:
        ax.set_xlabel("Detector N")
        ax.set_xticks(sorted({r["N"] for r in records}))
    axes[2].set_xscale("symlog", linthresh=1e-4)
    axes[2].set_xlabel(r"Central field $h_{0z}/h_z$ (N=17)")
    axes[2].set_ylabel("Saved global ratio RMSE")
    axes[0].legend(fontsize=8)
    fig.suptitle(r"Finite-size and field sensitivity at one time, $t=10^6$")
    for suffix in ("png", "pdf"):
        fig.savefig(output / f"ring_sensitivity.{suffix}", dpi=180)
    plt.close(fig)
