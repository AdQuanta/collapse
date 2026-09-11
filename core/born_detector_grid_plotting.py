"""Controlled detector-parameter figures with explicit support diagnostics."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from core.born_structure_plotting import save_figure


def detector_plane(records: list[dict], config: dict, path: Path) -> None:
    """Show every J/Jpm cell at one prespecified field, for all four sizes."""
    fields = ["occupied_RMSE", "coverage", "born_moment_max"]
    labels = ["Occupied R RMSE", "Reflection coverage", "Born moment residual"]
    fig, axes = plt.subplots(3, len(config["detector_sizes"]), figsize=(14, 10))
    js, jpms = config["j_values"], config["jpm_values"]
    selected = [r for r in records if r["hz"] == config["selected_hz"]]
    for row, (field, label) in enumerate(zip(fields, labels)):
        vmax = 1. if field == "coverage" else max(r[field] for r in selected)
        for col, n in enumerate(config["detector_sizes"]):
            values = np.full((len(js), len(jpms)), np.nan)
            for record in selected:
                if record["N"] == n:
                    values[js.index(record["J"]), jpms.index(record["Jpm"])] = record[field]
            im = axes[row, col].imshow(values, origin="lower", aspect="auto", vmin=0, vmax=vmax)
            for i, j in enumerate(js):
                if 2 * j in jpms:
                    axes[row, col].plot(jpms.index(2 * j), i, "s", fillstyle="none", color="white", ms=10)
            axes[row, col].set_xticks(range(len(jpms)), [f"{x:g}" for x in jpms], rotation=70)
            axes[row, col].set_yticks(range(len(js)), [f"{x:g}" for x in js])
            axes[row, col].set(xlabel=r"$J_\pm$", ylabel="J", title=f"N={n}: {label}")
        fig.colorbar(im, ax=list(axes[row, :]), fraction=.012, pad=.015)
    fig.suptitle(f"Controlled detector grid at hz={config['selected_hz']:g}, Jx=0.01, hz0=0, t=1e6\nCategorical parameter positions; white squares: isotropic Jpm=2J. Legacy source solves lack matrix residuals.")
    fig.subplots_adjust(top=.87, bottom=.1, hspace=.65, wspace=.35, right=.86)
    save_figure(fig, path)


def exchange_slices(records: list[dict], config: dict, path: Path) -> None:
    """Compare matched exchange changes without conflating coverage and fit."""
    fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
    fields = ["occupied_RMSE", "coverage", "born_moment_max", "visibility"]
    labels = ["Occupied R RMSE", "Reflection coverage", "Born moment residual", "Fundamental visibility"]
    for n in config["detector_sizes"]:
        selected = sorted([r for r in records if r["N"] == n and r["J"] == config["selected_j"] and r["hz"] == config["selected_hz"]], key=lambda r: r["Jpm"])
        for ax, field in zip(axes, fields):
            ax.plot(range(len(selected)), [r[field] for r in selected], "o-", ms=4, label=f"N={n}")
    iso = config["jpm_values"].index(2 * config["selected_j"])
    for ax, label in zip(axes, labels):
        ax.axvline(iso, color="black", ls="--", lw=1)
        ax.set_ylabel(label)
        ax.grid(alpha=.2)
    axes[1].set_ylim(-.03, 1.03)
    axes[0].legend(ncol=4)
    axes[-1].set_xticks(range(len(config["jpm_values"])), [f"{x:g}" for x in config["jpm_values"]])
    axes[-1].set_xlabel(r"$J_\pm$ (categorical positions)")
    fig.suptitle(f"Fixed J={config['selected_j']:g}, hz={config['selected_hz']:g}, Jx=0.01, hz0=0, t=1e6\nDashed line: isotropic exchange. Visibility omitted when angular support is incomplete.")
    fig.tight_layout(rect=(0, 0, 1, .93))
    save_figure(fig, path)
