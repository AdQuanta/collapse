"""Saved-data P(theta) and reflected-ratio diagnostic panels."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_polar_diagnostic_grid(
    output_stem: Path, rows: list[dict], *, title: str,
) -> None:
    """Plot precomputed densities and ratios; NaNs leave empty bins undefined.

    Each row contains a title and profiles with label, edges, centers,
    density, reflected_density, ratio, coverage, and moment_max. Ratios
    use bin centers, with all algebraic roots and no smoothing.
    """
    if not rows:
        raise ValueError("at least one diagnostic row is required")
    fig, axes = plt.subplots(len(rows), 2, figsize=(11, 3.15*len(rows)),
                             squeeze=False, constrained_layout=True)
    colors = ("#4477AA", "#CC6677", "#228833", "#AA3377")
    markers = ("o", "s", "^", "D")
    curve = np.linspace(0, np.pi, 400)
    for index, row in enumerate(rows):
        density_ax, ratio_ax = axes[index]
        for j, profile in enumerate(row["profiles"]):
            color, marker = colors[j % len(colors)], markers[j % len(markers)]
            label = profile["label"]
            density_ax.stairs(profile["density"], profile["edges"], color=color,
                              linewidth=1.2, label=label)
            density_ax.stairs(profile["reflected_density"], profile["edges"],
                              color=color, linestyle="--", linewidth=.8, alpha=.7)
            ratio_ax.plot(profile["centers"], profile["ratio"], color=color,
                          marker=marker, markersize=2.5, linewidth=.8,
                          label=f"{label}; cov={profile['coverage']:.3f}, m={profile['moment_max']:.3g}")
        ratio_ax.plot(curve, np.cos(curve/2)**2, "k--", linewidth=1.4,
                      label=r"Born $\cos^2(\theta/2)$")
        density_ax.set_title(row["title"])
        ratio_ax.set_title(row["title"])
        density_ax.set_ylabel(r"$P(\theta)$ [rad$^{-1}$]")
        ratio_ax.set_ylabel(r"$R(\theta)$")
        ratio_ax.set_ylim(-.035, 1.035)
        for ax in (density_ax, ratio_ax):
            ax.set_xlabel(r"$\theta$ [rad]")
            ax.set_xlim(0, np.pi)
            ax.tick_params(direction="out")
            ax.legend(fontsize=7.5, loc="best")
    fig.suptitle(title+"\nDashed densities are reflected; gaps in R are unoccupied bins.\n"
                 "cov: reflected coverage; m: maximum of eight Born moment residuals", fontsize=11)
    for suffix in ("png", "pdf"):
        fig.savefig(output_stem.with_suffix("."+suffix), dpi=180)
    plt.close(fig)
