"""Reduced verification figures for the transverse gauge and return dynamics."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_return_comparison(output: Path, records: list[dict]) -> None:
    """Show changes in the bounded root potential, without fitting a limit."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for column, topology in enumerate(("ring", "chain")):
        selected = [r for r in records if r["topology"] == topology and r["eta"] != 0]
        for n in sorted({r["N"] for r in selected}):
            rows = sorted((r for r in selected if r["N"] == n), key=lambda r: r["time"])
            times = [r["time"] for r in rows]
            axes[0, column].plot(times, [r["exact_gauge_potential_difference"] for r in rows],
                                 "o-", label=f"N={n}, full U")
            axes[1, column].plot(times, [r["leading_to_exact_potential_difference"] for r in rows],
                                 "o-", label=f"N={n}")
        axes[0, column].set_title(topology)
        axes[0, column].set_ylabel(r"$\max_x|J_{\eta=0.5}-J_{\eta=0}|$")
        axes[1, column].set_ylabel(r"$\max_x|J_{\rm full}-J_{\rm leading}|$")
        for ax in axes[:, column]:
            ax.set_xscale("log")
            ax.set_xlabel("Time [inverse energy]")
            ax.legend(fontsize=8)
    fig.suptitle("Reduced verification: equal leading spectra, distinct return dynamics")
    for suffix in ("png", "pdf"):
        fig.savefig(output / f"return_comparison.{suffix}", dpi=180)
    plt.close(fig)
