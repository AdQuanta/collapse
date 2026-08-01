"""Simulate and compare canonical single- and two-pixel Hamiltonians.

Four equal-total-detector cases are shown: single/two-pixel at ``hz0=0`` and
at the matched field ``hz0=hz=0.1``.  The collective coupling is ``Jx=0.01``;
every central edge uses ``Jx/sqrt(N_detector)``.  The two-pixel class retains
its historical opposite signs for the two independent detectors.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import csv
import json
import math
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import wasserstein_distance

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.two_pixel_study import (
    AngularDiagnosticService,
    ComparisonSimulator,
    ComparisonSpec,
    default_specs,
    load_raw,
)


BLUE = "#1677b8"
RED = "#df2b2f"
RATIO = "#6a3d7a"
DEFAULT_TIMES = (1.0e3, 1.0e4, 1.0e5, 1.0e6)


def bloch_branches(eigenvalues: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lam = np.asarray(eigenvalues, dtype=np.complex128)
    finite = np.isfinite(lam.real) & np.isfinite(lam.imag)
    lam = lam[finite]
    radius2 = np.abs(lam) ** 2
    denominator = 1.0 + radius2
    branch = np.column_stack(
        (2.0 * lam.real / denominator, 2.0 * lam.imag / denominator, (1.0 - radius2) / denominator)
    )
    return branch, -branch


def wire_sphere(ax) -> None:
    azimuth = np.linspace(0.0, 2.0 * np.pi, 34)
    polar = np.linspace(0.0, np.pi, 17)
    ax.plot_wireframe(
        np.outer(np.cos(azimuth), np.sin(polar)),
        np.outer(np.sin(azimuth), np.sin(polar)),
        np.outer(np.ones_like(azimuth), np.cos(polar)),
        color="#9aa0a6",
        linewidth=0.28,
        alpha=0.25,
    )


def plot_atlas(
    raw_root: Path,
    figure_root: Path,
    specs: tuple[ComparisonSpec, ...],
    time_value: float,
    diagnostics: AngularDiagnosticService,
) -> Path:
    figure = plt.figure(figsize=(22.0, 10.5), constrained_layout=True)
    grid = figure.add_gridspec(3, len(specs), height_ratios=(1.0, 0.9, 1.35))
    for column, spec in enumerate(specs):
        raw = load_raw(ComparisonSimulator(raw_root).raw_path(spec, time_value))
        dist = diagnostics.distributions(raw)
        eigenvalues = np.asarray(raw["eigenvalues"], dtype=np.complex128)
        record = diagnostics.calculate(spec, time_value, raw)

        ax_hist = figure.add_subplot(grid[0, column])
        ax_hist.stairs(
            dist["p_theta"], diagnostics.edges, color=BLUE, linewidth=1.4,
            fill=True, alpha=0.17, label=r"$P(\theta)$",
        )
        ax_hist.stairs(
            dist["p_reflected"], diagnostics.edges, color=RED, linewidth=1.35,
            fill=True, alpha=0.13, label=r"$P(\pi-\theta)$",
        )
        ax_hist.plot(
            diagnostics.centers, dist["theory"], color=BLUE,
            linestyle="--", linewidth=1.0, label="perturbative wrapped Gaussian",
        )
        ax_hist.plot(
            diagnostics.centers, dist["theory"][::-1], color=RED,
            linestyle="--", linewidth=1.0, label="reflected reference",
        )
        ax_hist.set_xlim(0.0, np.pi)
        ax_hist.grid(alpha=0.16)
        ax_hist.set_title(spec.label, fontsize=11)
        ax_hist.tick_params(labelbottom=False, labelsize=8)
        if column == 0:
            ax_hist.set_ylabel("density")
            ax_hist.legend(fontsize=7, frameon=False, loc="upper center")

        ax_ratio = figure.add_subplot(grid[1, column])
        occupied = np.isfinite(dist["ratio"])
        ax_ratio.plot(
            diagnostics.centers[occupied], dist["ratio"][occupied], "o-",
            color=RATIO, linewidth=0.95, markersize=3.0,
            label=r"$R(\theta)$ (occupied bins)",
        )
        ax_ratio.plot(
            diagnostics.centers, dist["born"], color="black", linestyle="--",
            linewidth=1.25, label=r"$\cos^2(\theta/2)$",
        )
        ax_ratio.set(xlim=(0.0, np.pi), ylim=(-0.04, 1.04), xlabel=r"$\theta$")
        ax_ratio.grid(alpha=0.16)
        ax_ratio.tick_params(labelsize=8)
        ax_ratio.text(
            0.04, 0.08,
            rf"$S_{{Born}}={record.born_similarity:.3f}$" + "\n" + rf"RMSE$={record.born_rmse:.3f}$",
            transform=ax_ratio.transAxes, fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
        )
        if column == 0:
            ax_ratio.set_ylabel(r"$R(\theta)$")
            ax_ratio.legend(fontsize=7, frameon=False, loc="upper center")

        ax_bloch = figure.add_subplot(grid[2, column], projection="3d")
        branch0, branch1 = bloch_branches(eigenvalues)
        wire_sphere(ax_bloch)
        ax_bloch.scatter(*branch0.T, s=5.0, color=BLUE, alpha=0.34, depthshade=False)
        ax_bloch.scatter(*branch1.T, s=5.0, color=RED, alpha=0.28, depthshade=False)
        ax_bloch.set(xlim=(-1.04, 1.04), ylim=(-1.04, 1.04), zlim=(-1.04, 1.04))
        ax_bloch.set_box_aspect((1.0, 1.0, 1.0))
        ax_bloch.view_init(elev=22.0, azim=42.0)
        ax_bloch.set_axis_off()
        if column == 0:
            ax_bloch.text2D(
                0.02, 0.03, r"blue: $v(\lambda)$" + "\n" + r"red: $-v(\lambda)$",
                transform=ax_bloch.transAxes, fontsize=8,
            )

    power = int(round(math.log10(time_value)))
    figure.suptitle(
        rf"Equal-detector single/two-pixel comparison: $N_D={specs[0].detector_spins}$, "
        rf"$J=1$, $h_z=0.1$, collective $J_x=0.01$, $t=10^{{{power}}}$",
        fontsize=15, fontweight="bold",
    )
    path = figure_root / f"two_pixel_comparison_t1e{power}.png"
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path


def paired_metrics(
    raw_root: Path,
    specs: tuple[ComparisonSpec, ...],
    times: tuple[float, ...],
    diagnostics: AngularDiagnosticService,
) -> list[dict[str, float]]:
    by_key = {spec.key: spec for spec in specs}
    rows: list[dict[str, float]] = []
    simulator = ComparisonSimulator(raw_root)
    for suffix, hz0 in (("zero", 0.0), ("matched", 0.1)):
        single = by_key[f"single_{suffix}"]
        two = by_key[f"two_{suffix}"]
        for time_value in times:
            a = load_raw(simulator.raw_path(single, time_value))
            b = load_raw(simulator.raw_path(two, time_value))
            da, db = diagnostics.distributions(a), diagnostics.distributions(b)
            pa = da["p_theta"] * np.diff(diagnostics.edges)
            pb = db["p_theta"] * np.diff(diagnostics.edges)
            joint = np.isfinite(da["ratio"]) & np.isfinite(db["ratio"])
            rows.append(
                {
                    "hz0": hz0,
                    "time": time_value,
                    "theta_wasserstein": float(wasserstein_distance(a["theta"], b["theta"])),
                    "theta_js_divergence": float(jensenshannon(pa, pb, base=2.0) ** 2),
                    "R_rmse_between_models": float(np.sqrt(np.mean((da["ratio"][joint] - db["ratio"][joint]) ** 2))),
                    "common_R_bin_fraction": float(np.mean(joint)),
                }
            )
    return rows


def plot_summary(
    figure_root: Path,
    records: list[dict[str, object]],
    pairs: list[dict[str, float]],
) -> Path:
    figure, axes = plt.subplots(2, 3, figsize=(15.5, 8.3), constrained_layout=True)
    colors = {"single": BLUE, "two": RED}
    markers = {0.0: "o", 0.1: "s"}
    for kind in ("single", "two"):
        for hz0 in (0.0, 0.1):
            selected = sorted(
                (row for row in records if row["kind"] == kind and row["hz0"] == hz0),
                key=lambda row: row["time"],
            )
            times = [row["time"] for row in selected]
            label = f"{kind}, hz0={hz0:g}"
            axes[0, 0].semilogx(times, [row["born_similarity"] for row in selected], marker=markers[hz0], color=colors[kind], linestyle="-" if hz0 == 0 else "--", label=label)
            axes[0, 1].semilogx(times, [row["born_rmse"] for row in selected], marker=markers[hz0], color=colors[kind], linestyle="-" if hz0 == 0 else "--")
            axes[0, 2].semilogx(times, [row["wrapped_gaussian_l1"] for row in selected], marker=markers[hz0], color=colors[kind], linestyle="-" if hz0 == 0 else "--")
            axes[1, 0].semilogx(times, [row["phi_harmonic_2"] for row in selected], marker=markers[hz0], color=colors[kind], linestyle="-" if hz0 == 0 else "--")
    for hz0, style in ((0.0, "-"), (0.1, "--")):
        selected = sorted((row for row in pairs if row["hz0"] == hz0), key=lambda row: row["time"])
        axes[1, 1].semilogx([row["time"] for row in selected], [row["theta_wasserstein"] for row in selected], "o" + style, label=f"hz0={hz0:g}")
        axes[1, 2].semilogx([row["time"] for row in selected], [row["theta_js_divergence"] for row in selected], "o" + style)
    titles = (
        "Born similarity", "Born-ratio RMSE", "analytic Gaussian L1",
        r"azimuthal $|\langle e^{2i\phi}\rangle|$", r"single--two $W_1(\theta)$", "single--two JS divergence",
    )
    for ax, title in zip(axes.flat, titles):
        ax.set_title(title)
        ax.set_xlabel("time")
        ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8, frameon=False)
    axes[1, 1].legend(fontsize=8, frameon=False)
    figure.suptitle("Single- versus two-pixel diagnostic summary", fontsize=15, fontweight="bold")
    path = figure_root / "two_pixel_comparison_summary.png"
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-out", type=Path, default=Path("work/two_pixel_comparison_2026-07-16"))
    parser.add_argument("--fig-out", type=Path, default=Path("figures/two_pixel_comparison_2026-07-16"))
    parser.add_argument("--detector-spins", type=int, default=8)
    parser.add_argument("--times", type=float, nargs="+", default=DEFAULT_TIMES)
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.detector_spins % 2:
        parser.error("--detector-spins must be even")
    args.raw_out.mkdir(parents=True, exist_ok=True)
    args.fig_out.mkdir(parents=True, exist_ok=True)
    times = tuple(float(value) for value in args.times)
    specs = default_specs(args.detector_spins)
    simulator = ComparisonSimulator(args.raw_out)
    diagnostics = AngularDiagnosticService(args.bins)

    for spec in specs:
        print(f"Simulating {spec.key}: edge Jx={spec.edge_jx:.8g}", flush=True)
        simulator.run(spec, times, force=args.force)

    records = []
    for spec in specs:
        for time_value in times:
            raw = load_raw(simulator.raw_path(spec, time_value))
            records.append(asdict(diagnostics.calculate(spec, time_value, raw)))
    pairs = paired_metrics(args.raw_out, specs, times, diagnostics)
    atlases = [str(plot_atlas(args.raw_out, args.fig_out, specs, t, diagnostics)) for t in times]
    summary = plot_summary(args.fig_out, records, pairs)
    metrics_path = args.fig_out / "two_pixel_comparison_metrics.csv"
    pairs_path = args.fig_out / "two_pixel_paired_distances.csv"
    write_csv(metrics_path, records)
    write_csv(pairs_path, pairs)
    manifest = {
        "specs": [asdict(spec) | {"edge_jx": spec.edge_jx, "n_pixel": spec.n_pixel} for spec in specs],
        "times": times,
        "bins": args.bins,
        "normalization": "collective Jx=0.01; edge Jx=0.01/sqrt(total detector spins)",
        "two_pixel_signs": "detector 1 negative, detector 2 positive",
        "raw_root": str(args.raw_out.resolve()),
        "atlases": atlases,
        "summary": str(summary),
        "metrics": str(metrics_path),
        "paired_distances": str(pairs_path),
    }
    (args.fig_out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
