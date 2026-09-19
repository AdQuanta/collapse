#!/usr/bin/env python3.11
"""Figures for the memory-versus-Born comparison.

The angular panels reuse the ring-catalog diagnostic style so these figures sit
beside the existing reports: `_plot_angular` and `_plot_ratio` are imported
rather than reimplemented, and the binning statement is carried in the footer.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work/_mplconfig"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

from scripts.build_network_wd_nonborn_size_spacing_figures import (  # noqa: E402
    _plot_angular,
)
from scripts.plot_hz0_0_ring_spacing_born_catalog import _plot_ratio  # noqa: E402

FOOTER = (
    "Exploratory mechanism study; no paper-readiness gate is claimed. "
    "S_Born uses 100 bins; plotted P/R use 64 bins. "
    "Empty bins stay undefined and the error is occupied-bin only."
)
CELL_MARKER = {
    ("ring", "all"): "o",
    ("chain", "first"): "s",
    ("ring", "first"): "^",
    ("chain", "all"): "D",
}
PHASE_COLOR = {0.5: "#2878b5", 1.0: "#6f3c8a", 1.5: "#d9534f"}


def load(root: Path):
    summary = json.loads((root / "summary.json").read_text())
    return summary["records"]


def case_arrays(root: Path, name: str):
    with np.load(root / name / "results.npz", allow_pickle=False) as handle:
        return {key: np.array(handle[key]) for key in handle.files}


def figure_diagnostics(root, records, output, *, size, scaling, hx0):
    """Per-configuration angular column, one row per geometry cell."""

    chosen = [
        r for r in records
        if r["N"] == size and r["scaling"] == scaling and r["hx0"] == hx0
    ]
    phases = sorted({r["hx_over_J"] for r in chosen})
    cells = list(CELL_MARKER)
    figure, axes = plt.subplots(
        2 * len(cells), len(phases), figsize=(4.1 * len(phases), 4.4 * len(cells)),
        squeeze=False,
    )
    for row, (connectivity, central) in enumerate(cells):
        for column, phase in enumerate(phases):
            match = [
                r for r in chosen
                if r["connectivity"] == connectivity
                and r["central_coupling"] == central
                and r["hx_over_J"] == phase
            ]
            top = axes[2 * row, column]
            bottom = axes[2 * row + 1, column]
            if not match:
                top.axis("off")
                bottom.axis("off")
                continue
            record = match[0]
            arrays = case_arrays(root, record["name"])
            metrics = json.loads(
                (root / record["name"] / "metrics.json").read_text()
            )["born"]
            _plot_angular(top, arrays)
            top.set_ylabel(r"$P(\theta)$ [rad$^{-1}$]")
            top.set_title(
                f"{connectivity}/{central}, $h_x/J$={phase}", fontsize=9
            )
            if row == 0 and column == 0:
                top.legend(frameon=False, ncol=2, fontsize=6.5)
            _plot_ratio(bottom, arrays, metrics, show_legend=(row == 0 and column == 0))
            bottom.set_xlabel(r"$\theta$")
            bottom.text(
                0.03, 0.80,
                rf"$N_{{\rm BLP}}={record['n_blp_mixed_early']:.3f}$",
                transform=bottom.transAxes, fontsize=7,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78},
            )
    figure.suptitle(
        f"Angular diagnostics, $N$={size}, {scaling} coupling, "
        rf"$h_{{x0}}$={hx0}, matched $\epsilon$={records[0]['epsilon']}",
        fontsize=12,
    )
    figure.text(0.5, 0.004, FOOTER, ha="center", fontsize=7.5)
    figure.tight_layout(rect=(0, 0.02, 1, 0.97))
    figure.savefig(output.with_suffix(".png"), dpi=160)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def figure_finite_size(root, records, output, *, scaling, hx0):
    """R(theta) against Born across N, one panel per cell and phase."""

    cells = list(CELL_MARKER)
    phases = sorted({r["hx_over_J"] for r in records})
    figure, axes = plt.subplots(
        len(cells), len(phases), figsize=(4.0 * len(phases), 2.9 * len(cells)),
        sharex=True, sharey=True, squeeze=False,
    )
    sizes = sorted({r["N"] for r in records})
    shades = plt.cm.viridis(np.linspace(0.15, 0.9, len(sizes)))
    for row, (connectivity, central) in enumerate(cells):
        for column, phase in enumerate(phases):
            axis = axes[row][column]
            for shade, size in zip(shades, sizes):
                match = [
                    r for r in records
                    if r["connectivity"] == connectivity
                    and r["central_coupling"] == central
                    and r["hx_over_J"] == phase and r["N"] == size
                    and r["scaling"] == scaling and r["hx0"] == hx0
                ]
                if not match:
                    continue
                arrays = case_arrays(root, match[0]["name"])
                occupied = np.asarray(arrays["R_occupied"], dtype=bool)
                axis.plot(
                    arrays["centers"][occupied], arrays["R"][occupied],
                    "-", color=shade, linewidth=0.9, label=f"N={size}",
                )
            centers = np.linspace(0.0, np.pi, 257)
            axis.plot(centers, np.cos(centers / 2) ** 2, "k--", linewidth=1.0)
            axis.set(xlim=(0, np.pi), ylim=(-0.04, 1.04))
            axis.set_xticks((0.0, np.pi / 2, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
            axis.grid(alpha=0.16)
            if row == 0:
                axis.set_title(rf"$h_x/J$={phase}", fontsize=9)
            if column == 0:
                axis.set_ylabel(f"{connectivity}/{central}\n" + r"$R(\theta)$",
                                fontsize=8)
            if row == len(cells) - 1:
                axis.set_xlabel(r"$\theta$")
    axes[0][0].legend(frameon=False, fontsize=6, ncol=2)
    figure.suptitle(
        f"Finite-size behaviour of $R(\\theta)$, {scaling} coupling, "
        rf"$h_{{x0}}$={hx0}; dashed $\cos^2(\theta/2)$",
        fontsize=12,
    )
    figure.text(0.5, 0.004, FOOTER, ha="center", fontsize=7.5)
    figure.tight_layout(rect=(0, 0.02, 1, 0.96))
    figure.savefig(output.with_suffix(".png"), dpi=160)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def figure_conjecture(records, output, *, hx0):
    """Memory against Born, and the N-scaling of memory: the conjecture test."""

    usable = [r for r in records if r["hx0"] == hx0]
    scalings = sorted({r["scaling"] for r in usable})
    figure, axes = plt.subplots(2, len(scalings), figsize=(5.6 * len(scalings), 8.4),
                                squeeze=False)
    for column, scaling in enumerate(scalings):
        subset = [r for r in usable if r["scaling"] == scaling]
        top = axes[0][column]
        for (connectivity, central), marker in CELL_MARKER.items():
            for phase, color in PHASE_COLOR.items():
                series = sorted(
                    [r for r in subset
                     if r["connectivity"] == connectivity
                     and r["central_coupling"] == central
                     and r["hx_over_J"] == phase],
                    key=lambda r: r["N"],
                )
                if not series:
                    continue
                top.plot(
                    [r["N"] for r in series],
                    [max(r["n_blp_mixed_early"], 1e-6) for r in series],
                    marker + "-", color=color, markersize=4, linewidth=0.9, alpha=0.85,
                )
        top.set(yscale="log", xlabel=r"$N$", ylabel=r"$N_{\rm BLP}$ (early window)")
        top.set_title(f"Memory versus size — {scaling} coupling", fontsize=10)
        top.grid(alpha=0.16)

        bottom = axes[1][column]
        xs, ys = [], []
        for (connectivity, central), marker in CELL_MARKER.items():
            for phase, color in PHASE_COLOR.items():
                series = [
                    r for r in subset
                    if r["connectivity"] == connectivity
                    and r["central_coupling"] == central
                    and r["hx_over_J"] == phase
                ]
                if not series:
                    continue
                x = [max(r["n_blp_mixed_early"], 1e-6) for r in series]
                y = [r["S_born"] for r in series]
                xs.extend(x)
                ys.extend(y)
                bottom.plot(x, y, marker, color=color, markersize=4.5, alpha=0.8,
                            linestyle="none")
        bottom.axhline(0.0, color="0.4", linewidth=0.9, linestyle=":")
        bottom.set(xscale="log", xlabel=r"$N_{\rm BLP}$ (early window)",
                   ylabel=r"$S_{\rm Born}$")
        if len(xs) > 2 and np.ptp(xs) > 0 and np.ptp(ys) > 0:
            rho, pvalue = spearmanr(xs, ys)
            bottom.text(
                0.03, 0.05,
                f"Spearman $\\rho$={rho:.3f}\n$p$={pvalue:.2g}  ($n$={len(xs)})",
                transform=bottom.transAxes, fontsize=8,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8},
            )
        bottom.set_title("Born similarity versus memory", fontsize=10)
        bottom.grid(alpha=0.16)

    handles = [
        plt.Line2D([], [], marker=marker, color="0.35", linestyle="none",
                   markersize=5, label=f"{c}/{t}")
        for (c, t), marker in CELL_MARKER.items()
    ] + [
        plt.Line2D([], [], marker="o", color=color, linestyle="none",
                   markersize=5, label=rf"$h_x/J$={phase}")
        for phase, color in PHASE_COLOR.items()
    ]
    axes[0][0].legend(handles=handles, frameon=False, fontsize=7, ncol=2,
                      loc="lower left")
    figure.suptitle(
        rf"Is one-way information flow necessary or sufficient for Born? ($h_{{x0}}$={hx0})",
        fontsize=12,
    )
    figure.text(
        0.5, 0.004,
        "Dotted line: the uninformative baseline S_Born=0. No memory threshold is "
        "drawn, because BLP=0 is the only principled cut and any other would be "
        "chosen after seeing these data.\n"
        "The quoted Spearman pools all N and is therefore confounded, since both "
        "axes vary systematically with size; the size-controlled within-N values "
        "are in analysis.txt.\n"
        "S_Born itself is not comparable across N: the thinning control in "
        "resolution_control.txt shows its apparent growth with N is bin-occupancy, "
        "not convergence toward Born.",
        ha="center", fontsize=7.5,
    )
    figure.tight_layout(rect=(0, 0.025, 1, 0.96))
    figure.savefig(output.with_suffix(".png"), dpi=160)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-root", type=Path, required=True)
    args = ap.parse_args()
    records = load(args.run_root)
    figures = args.run_root / "figures"
    figures.mkdir(exist_ok=True)

    largest = max(r["N"] for r in records)
    for scaling in sorted({r["scaling"] for r in records}):
        figure_diagnostics(
            args.run_root, records, figures / f"diagnostics_{scaling}_hx0_050",
            size=largest, scaling=scaling, hx0=0.5,
        )
        figure_finite_size(
            args.run_root, records, figures / f"finite_size_{scaling}_hx0_050",
            scaling=scaling, hx0=0.5,
        )
    figure_conjecture(records, figures / "conjecture_hx0_050", hx0=0.5)
    figure_conjecture(records, figures / "conjecture_hx0_000", hx0=0.0)
    print(f"wrote figures to {figures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
