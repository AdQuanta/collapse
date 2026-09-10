"""Static scientific figures for the Born structural audit."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def save_figure(fig: plt.Figure, path: Path) -> None:
    """Save both paper-vector and preview versions, then close the figure."""
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=160, bbox_inches="tight")
    plt.close(fig)


def profile_grid(records: list[dict], path: Path, title: str) -> None:
    """Display density, response, residual and response harmonics per case."""
    fig, axes = plt.subplots(4, len(records), figsize=(3.1 * len(records), 9), squeeze=False)
    for col, record in enumerate(records):
        arrays = record["arrays"]
        x = arrays["centers"] / np.pi
        occupied = arrays["occupied"].astype(bool)
        ratio = np.where(occupied, arrays["R"], np.nan)
        axes[0, col].stairs(arrays["P"], arrays["edges"] / np.pi, color="#256b97", label="P")
        axes[0, col].plot(x, (1 + np.cos(np.pi * x)) / np.pi, "--", color="0.55", label="one Born P")
        axes[0, col].set_title(record["label"], fontsize=9)
        axes[1, col].plot(x, ratio, ".-", color="#256b97", markersize=2, linewidth=.7)
        axes[1, col].plot(x, arrays["Born"], "--", color="#c14d35", linewidth=1.3)
        axes[1, col].set_ylim(-.03, 1.03)
        axes[1, col].text(.04, .05, f"S={record['S_born']:.3f}; C={record['coverage']:.2f}",
                          transform=axes[1, col].transAxes, fontsize=8)
        axes[2, col].axhline(0, color="0.6", linewidth=.7)
        axes[2, col].plot(x, ratio - arrays["Born"], ".-", color="#834a92", markersize=2, linewidth=.7)
        residual_extent = max(.55, float(np.nanmax(np.abs(ratio - arrays["Born"]))) + .05)
        axes[2, col].set_ylim(-residual_extent, residual_extent)
        coeff = record["response_coefficients"]
        if np.all(np.isfinite(coeff)):
            n = np.arange(1, len(coeff))
            axes[3, col].bar(n, 2 * coeff[1:], color="#256b97", width=.6)
            axes[3, col].plot(n, (n == 1).astype(float), "o", color="#c14d35", markersize=3)
        else:
            axes[3, col].text(.5, .5, "Incomplete support:\nno Fourier extrapolation", ha="center",
                              va="center", transform=axes[3, col].transAxes, fontsize=8)
        minimum = min(-.5, float(np.min(2 * coeff[1:])) - .1) if np.all(np.isfinite(coeff)) else -.5
        axes[3, col].set_ylim(minimum, 1.6)
        axes[3, col].set_xticks([1, 3, 5, 7, 9])
        axes[3, col].set_xlabel("cosine order n")
        for row in range(3):
            axes[row, col].set_xlim(0, 1)
            axes[row, col].set_xticks([0, .5, 1])
            axes[row, col].set_xlabel(r"$\theta/\pi$")
    for ax, label in zip(axes[:, 0], [r"$P$ [rad$^{-1}$]", r"$R$", r"$R-\cos^2(\theta/2)$", r"$2c_n$ of $R$"]):
        ax.set_ylabel(label)
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(title + "\nBlue: numerical; red: Born. Missing ratio bins are omitted.", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, .94))
    save_figure(fig, path)


def scan_figure(groups: dict[str, list[dict]], path: Path) -> None:
    """Compare all 20 field values without obscuring closely spaced resonances."""
    fig, axes = plt.subplots(5, 1, figsize=(13, 13), sharex=True)
    fields = ["S_born", "occupied_RMSE", "coverage", "born_moment_max", "gaussian_moment_max"]
    labels = [r"$S_{\rm Born}$ (stored)", "Occupied R RMSE", "Reflection coverage", r"$\max_{m<8}|d_m|$ (P)", "WG moment discrepancy (P)"]
    for group, records in groups.items():
        records = sorted(records, key=lambda r: r["hz0_ratio"])
        for ax, field in zip(axes, fields):
            line, = ax.plot(range(len(records)), [r[field] for r in records], "-", label=group, linewidth=1)
            for i, r in enumerate(records):
                ax.plot(i, r[field], "o", color=line.get_color(), markersize=4,
                        markerfacecolor="white" if r.get("conditioning_caution", False) else line.get_color())
    for ax, label in zip(axes, labels):
        ax.set_ylabel(label)
        ax.grid(alpha=.2)
    axes[0].legend(ncol=3, fontsize=9)
    axes[-1].set_xticks(range(20), [f"{r['hz0_ratio']:g}" for r in records], rotation=65)
    axes[-1].set_xlabel(r"$h_{z0}/h_z$ (categorical positions; actual values labeled)")
    fig.suptitle("Fixed-detector field scans, N=17, t=10^6\nOpen circles: conditioning caution. Small moment errors alone do not imply broad support.")
    fig.tight_layout(rect=(0, 0, 1, .95))
    save_figure(fig, path)


def moment_figure(records: list[dict], path: Path) -> None:
    """Compare the general Born hierarchy with the overrestrictive cardioid."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for record in records:
        axes[0].plot(np.arange(1, 17), record["moments"][1:], ".-", label=record["label"])
        axes[1].plot(np.arange(8), record["born_moment_residuals"], ".-", label=record["label"])
    axes[0].plot(np.arange(1, 17), np.r_[.5, np.zeros(15)], "k--", label="cardioid sufficient example")
    axes[1].axhline(0, color="black", linestyle="--")
    axes[0].set(xlabel="n", ylabel=r"$a_n=\langle\cos(n\theta)\rangle$")
    axes[1].set(xlabel="m", ylabel=r"$d_m=2a_{2m+1}-a_{2m}-a_{2m+2}$")
    axes[0].legend(fontsize=7)
    fig.suptitle("Born R permits a family of P densities; the general moment test is on the right")
    fig.tight_layout()
    save_figure(fig, path)


def control_parameter_figure(rows: list[dict], sizes: list[int], path: Path) -> None:
    """Plot parameter sensitivity with mandatory coverage beside error metrics."""
    properties = ["Jx_scale", "hz0_over_hz", "Jy_over_Jx"]
    labels = [r"$J_x/J_{x,\mathrm{ref}}$", r"$h_{z0}/h_z$", r"$J_y/J_x$"]
    fig, axes = plt.subplots(3, 3, figsize=(13, 10))
    for col, prop in enumerate(properties):
        for size in sizes:
            subset = [r for r in rows if r["property"] == prop and r["N"] == size]
            baseline = [r for r in rows if r["case"] == "baseline" and r["N"] == size]
            points = [(r["value"], r) for r in subset]
            points.extend([(1 if prop == "Jx_scale" else 0, r) for r in baseline])
            values = sorted({x for x, _ in points})
            for ax, metric in zip(axes[:, col], ["occupied_RMSE", "born_moment_max", "coverage"]):
                ys = [[r[metric] for x, r in points if x == value] for value in values]
                mean = np.array([np.mean(y) for y in ys])
                lo, hi = np.array([min(y) for y in ys]), np.array([max(y) for y in ys])
                ax.errorbar(range(len(values)), mean, yerr=[mean-lo, hi-mean], fmt="o-", capsize=3, label=f"N={size}")
                ax.set_xticks(range(len(values)), [f"{v:g}" for v in values], rotation=45)
                ax.set_xlabel(labels[col])
                ax.grid(alpha=.2)
        for ax, label in zip(axes[:, col], ["Occupied R RMSE", "max Born moment residual", "Reflection coverage"]):
            ax.set_ylabel(label)
        axes[2, col].set_ylim(0, 1.05)
    axes[0, 0].legend()
    fig.suptitle("One-parameter perturbations of config 353\nMean and full range over three times; low error without coverage is not a Born profile")
    fig.tight_layout(rect=(0, 0, 1, .94))
    save_figure(fig, path)
