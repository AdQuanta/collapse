"""Repeat every heavy-tail/Born conjecture sweep for one versus two pixels.

The exact four grids from the completed Zeus analysis are reproduced at equal
total detector size.  Each pair compares one eight-spin ring with two
independent four-spin rings, preserves the two-pixel opposite coupling signs,
and uses collective ``Jx=0.01`` with edge coefficient ``Jx/sqrt(8)``.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import csv
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.conjecture_two_pixel_comparison import (
    ConjectureFamily,
    all_specs,
    conjecture_families,
    family_specs,
    paired_distance_records,
)
from collapse.two_pixel_study import (
    AngularDiagnosticService,
    ComparisonSimulator,
    ComparisonSpec,
    load_raw,
)
from examples.compare_two_pixel_single_pixel import bloch_branches, wire_sphere


BLUE = "#1677b8"
RED = "#df2b2f"
RATIO_SINGLE = "#6a3d7a"
RATIO_TWO = "#d97706"
DEFAULT_TIMES = (1.0e3, 1.0e4, 1.0e5, 1.0e6)
DETAIL_TIMES = (1.0e3, 1.0e6)


def _run_spec(payload: tuple[str, ComparisonSpec, tuple[float, ...], bool]) -> str:
    raw_root, spec, times, force = payload
    ComparisonSimulator(Path(raw_root)).run(spec, times, force=force)
    return spec.key


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _model_lookup(
    specs: tuple[ComparisonSpec, ...],
) -> dict[tuple[str, float, str], ComparisonSpec]:
    return {(spec.family, spec.parameter_value, spec.kind): spec for spec in specs}


def plot_family_atlas_page(
    raw_root: Path,
    figure_root: Path,
    family: ConjectureFamily,
    specs: tuple[ComparisonSpec, ...],
    diagnostics: AngularDiagnosticService,
    time_value: float,
    values: tuple[float, ...],
    page_index: int,
) -> Path:
    lookup = _model_lookup(specs)
    simulator = ComparisonSimulator(raw_root)
    figure = plt.figure(figsize=(3.65 * len(values), 10.6), constrained_layout=True)
    grid = figure.add_gridspec(3, len(values), height_ratios=(1.0, 0.9, 1.35))
    for column, value in enumerate(values):
        single = lookup[(family.name, value, "single")]
        two = lookup[(family.name, value, "two")]
        raw_single = load_raw(simulator.raw_path(single, time_value))
        raw_two = load_raw(simulator.raw_path(two, time_value))
        ds = diagnostics.distributions(raw_single)
        dt = diagnostics.distributions(raw_two)
        rs = diagnostics.calculate(single, time_value, raw_single)
        rt = diagnostics.calculate(two, time_value, raw_two)

        ax_hist = figure.add_subplot(grid[0, column])
        ax_hist.stairs(ds["p_theta"], diagnostics.edges, color=BLUE, linewidth=1.35, fill=True, alpha=0.13, label=r"single $P(\theta)$")
        ax_hist.stairs(ds["p_reflected"], diagnostics.edges, color=RED, linewidth=1.3, fill=True, alpha=0.10, label=r"single $P(\pi-\theta)$")
        ax_hist.stairs(dt["p_theta"], diagnostics.edges, color=BLUE, linewidth=1.35, linestyle="--", label=r"two $P(\theta)$")
        ax_hist.stairs(dt["p_reflected"], diagnostics.edges, color=RED, linewidth=1.3, linestyle="--", label=r"two $P(\pi-\theta)$")
        ax_hist.plot(diagnostics.centers, ds["theory"], color=BLUE, linestyle="-.", linewidth=0.85, alpha=0.8, label="single WG")
        ax_hist.plot(diagnostics.centers, dt["theory"], color=BLUE, linestyle=":", linewidth=1.0, alpha=0.9, label="two WG")
        ax_hist.set_xlim(0.0, np.pi)
        ax_hist.grid(alpha=0.16)
        ax_hist.set_title(rf"{family.parameter_symbol}=${value:g}$", fontsize=11)
        ax_hist.tick_params(labelbottom=False, labelsize=8)
        if column == 0:
            ax_hist.set_ylabel("density")
            ax_hist.legend(fontsize=6.6, frameon=False, ncol=2, loc="upper center")

        ax_ratio = figure.add_subplot(grid[1, column])
        occupied_single = np.isfinite(ds["ratio"])
        occupied_two = np.isfinite(dt["ratio"])
        ax_ratio.plot(diagnostics.centers[occupied_single], ds["ratio"][occupied_single], "o-", color=RATIO_SINGLE, linewidth=0.9, markersize=2.8, label="single")
        ax_ratio.plot(diagnostics.centers[occupied_two], dt["ratio"][occupied_two], "s--", color=RATIO_TWO, linewidth=0.9, markersize=2.6, label="two")
        ax_ratio.plot(diagnostics.centers, ds["born"], color="black", linestyle="--", linewidth=1.15, label=r"$\cos^2(\theta/2)$")
        ax_ratio.set(xlim=(0.0, np.pi), ylim=(-0.04, 1.04), xlabel=r"$\theta$")
        ax_ratio.grid(alpha=0.16)
        ax_ratio.tick_params(labelsize=8)
        ax_ratio.text(
            0.03, 0.06,
            rf"single: $S={rs.born_similarity:.2f}$, $\alpha={rs.tail_density_exponent:.2f}$" + "\n" + rf"two: $S={rt.born_similarity:.2f}$, $\alpha={rt.tail_density_exponent:.2f}$",
            transform=ax_ratio.transAxes, fontsize=7.2,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.4},
        )
        if column == 0:
            ax_ratio.set_ylabel(r"$R(\theta)$")
            ax_ratio.legend(fontsize=7, frameon=False, loc="upper center")

        ax_bloch = figure.add_subplot(grid[2, column], projection="3d")
        single0, single1 = bloch_branches(raw_single["eigenvalues"])
        two0, two1 = bloch_branches(raw_two["eigenvalues"])
        wire_sphere(ax_bloch)
        ax_bloch.scatter(*single0.T, s=5.0, marker="o", color=BLUE, alpha=0.28, depthshade=False)
        ax_bloch.scatter(*single1.T, s=5.0, marker="o", color=RED, alpha=0.24, depthshade=False)
        ax_bloch.scatter(*two0.T, s=7.0, marker="^", color=BLUE, alpha=0.38, depthshade=False)
        ax_bloch.scatter(*two1.T, s=7.0, marker="^", color=RED, alpha=0.34, depthshade=False)
        ax_bloch.set(xlim=(-1.04, 1.04), ylim=(-1.04, 1.04), zlim=(-1.04, 1.04))
        ax_bloch.set_box_aspect((1.0, 1.0, 1.0))
        ax_bloch.view_init(elev=22.0, azim=42.0)
        ax_bloch.set_axis_off()
        if column == 0:
            ax_bloch.text2D(0.01, 0.02, "circles: single\ntriangles: two", transform=ax_bloch.transAxes, fontsize=7.2)

    power = int(round(math.log10(time_value)))
    figure.suptitle(
        rf"Single/two-pixel {family.title}: $N_D=8$, collective $J_x=0.01$, $t=10^{{{power}}}$",
        fontsize=15, fontweight="bold",
    )
    path = figure_root / "atlases" / f"{family.name}_t1e{power}_page{page_index:02d}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=210, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path


def _heatmap(
    ax,
    matrix: np.ndarray,
    title: str,
    values: tuple[float, ...],
    times: tuple[float, ...],
    *,
    diverging: bool,
) -> None:
    finite = matrix[np.isfinite(matrix)]
    if diverging:
        absolute = np.abs(finite)
        limit = max(float(np.quantile(absolute, 0.95)) if finite.size else 1.0, 1.0e-9)
        clipped = np.clip(matrix, -limit, limit)
        image = ax.imshow(
            clipped,
            aspect="auto",
            cmap="coolwarm",
            norm=TwoSlopeNorm(vmin=-limit, vcenter=0.0, vmax=limit),
        )
        if finite.size and np.max(absolute) > limit:
            title += " (95% scale)"
    else:
        image = ax.imshow(matrix, aspect="auto", cmap="viridis")
    ax.set_title(title, fontsize=10)
    ax.set_yticks(range(len(times)), [rf"$10^{{{int(round(math.log10(value)))}}}$" for value in times])
    step = max(1, math.ceil(len(values) / 9))
    indices = list(range(0, len(values), step))
    ax.set_xticks(indices, [f"{values[index]:g}" for index in indices], rotation=45, ha="right")
    ax.tick_params(labelsize=8)
    plt.colorbar(image, ax=ax, fraction=0.046, pad=0.03)


def plot_family_heatmaps(
    figure_root: Path,
    family: ConjectureFamily,
    records: list[dict[str, object]],
    paired: list[dict[str, object]],
    times: tuple[float, ...],
) -> Path:
    model = {(row["parameter_value"], row["time"], row["kind"]): row for row in records if row["family"] == family.name}
    distances = {(row["parameter_value"], row["time"]): row for row in paired if row["family"] == family.name}
    metric_specs = (
        ("born_similarity", r"$\Delta S_{Born}$", True),
        ("occupied_bin_fraction", r"$\Delta$ polar coverage", True),
        ("phi_harmonic_2", r"$\Delta |\langle e^{2i\phi}\rangle|$", True),
        ("cauchy_log_likelihood_advantage_per_sample", r"$\Delta$ Cauchy advantage", True),
        ("tail_density_exponent", r"$\Delta$ tail exponent", True),
    )
    figure, axes = plt.subplots(2, 3, figsize=(16.0, 8.5), constrained_layout=True)
    for ax, (metric, title, diverging) in zip(axes.flat[:5], metric_specs):
        matrix = np.array([
            [float(model[(value, time_value, "two")][metric]) - float(model[(value, time_value, "single")][metric]) for value in family.values]
            for time_value in times
        ])
        _heatmap(ax, matrix, title, family.values, times, diverging=diverging)
    wasserstein = np.array([
        [float(distances[(value, time_value)]["theta_wasserstein"]) for value in family.values]
        for time_value in times
    ])
    _heatmap(axes.flat[5], wasserstein, r"single--two $W_1(\theta)$", family.values, times, diverging=False)
    for ax in axes[-1, :]:
        ax.set_xlabel(family.parameter_symbol)
    axes[0, 0].set_ylabel("time")
    axes[1, 0].set_ylabel("time")
    figure.suptitle(f"Topology response: {family.title}", fontsize=15, fontweight="bold")
    path = figure_root / f"{family.name}_topology_heatmaps.png"
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path


def aggregate_rows(
    families: tuple[ConjectureFamily, ...],
    records: list[dict[str, object]],
    paired: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for family in families:
        family_records = [row for row in records if row["family"] == family.name]
        family_pairs = [row for row in paired if row["family"] == family.name]
        for kind in ("single", "two"):
            selected = [row for row in family_records if row["kind"] == kind]
            rows.append(
                {
                    "family": family.name,
                    "kind": kind,
                    "spectra": len(selected),
                    "median_S_born": float(np.nanmedian([row["born_similarity"] for row in selected])),
                    "median_coverage": float(np.nanmedian([row["occupied_bin_fraction"] for row in selected])),
                    "median_phi_harmonic_2": float(np.nanmedian([row["phi_harmonic_2"] for row in selected])),
                    "median_cauchy_advantage": float(np.nanmedian([row["cauchy_log_likelihood_advantage_per_sample"] for row in selected])),
                    "cauchy_preferred_fraction": float(np.mean([row["preferred_model"] == "wrapped_cauchy" for row in selected])),
                    "median_tail_density_exponent": float(np.nanmedian([row["tail_density_exponent"] for row in selected])),
                    "median_q99_over_q50": float(np.nanmedian([row["radius_q99_over_q50"] for row in selected])),
                    "median_reciprocity_error": float(np.nanmedian([row["reciprocity_error"] for row in selected])),
                    "median_theta_wasserstein": float(np.nanmedian([row["theta_wasserstein"] for row in family_pairs])),
                }
            )
    return rows


def plot_synthesis(figure_root: Path, aggregates: list[dict[str, object]]) -> Path:
    families = [family.name for family in conjecture_families()]
    lookup = {(row["family"], row["kind"]): row for row in aggregates}
    metrics = (
        ("median_S_born", r"median $S_{Born}$"),
        ("median_coverage", "median polar coverage"),
        ("median_phi_harmonic_2", r"median $|\langle e^{2i\phi}\rangle|$"),
        ("median_cauchy_advantage", "median Cauchy advantage"),
        ("median_tail_density_exponent", "median tail exponent"),
    )
    figure, axes = plt.subplots(2, 3, figsize=(15.5, 8.5), constrained_layout=True)
    x = np.arange(len(families))
    width = 0.36
    for ax, (metric, title) in zip(axes.flat[:5], metrics):
        ax.bar(x - width / 2, [lookup[(family, "single")][metric] for family in families], width, color=BLUE, label="single")
        ax.bar(x + width / 2, [lookup[(family, "two")][metric] for family in families], width, color=RED, label="two")
        ax.set_title(title)
        ax.set_xticks(x, families, rotation=25, ha="right")
        ax.grid(axis="y", alpha=0.2)
    axes.flat[0].legend(frameon=False)
    axes.flat[5].bar(x, [lookup[(family, "single")]["median_theta_wasserstein"] for family in families], color="#6a3d7a")
    axes.flat[5].set_title(r"median single--two $W_1(\theta)$")
    axes.flat[5].set_xticks(x, families, rotation=25, ha="right")
    axes.flat[5].grid(axis="y", alpha=0.2)
    figure.suptitle("Heavy-tail/Born family comparison under detector splitting", fontsize=15, fontweight="bold")
    path = figure_root / "conjecture_family_synthesis.png"
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path


def runtime_versions() -> dict[str, str]:
    output = {"python": sys.version, "platform": platform.platform(), "logical_cpus": str(os.cpu_count())}
    for package in ("quspin", "quspin-extensions", "numpy", "scipy", "matplotlib"):
        try:
            output[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            output[package] = "not installed"
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-out", type=Path, default=Path("work/conjecture_two_pixel_comparison_2026-07-16"))
    parser.add_argument("--fig-out", type=Path, default=Path("figures/conjecture_two_pixel_comparison_2026-07-16"))
    parser.add_argument("--detector-spins", type=int, default=8)
    parser.add_argument("--times", type=float, nargs="+", default=DEFAULT_TIMES)
    parser.add_argument("--detail-times", type=float, nargs="+", default=DETAIL_TIMES)
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--columns-per-page", type=int, default=5)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.detector_spins % 2:
        parser.error("--detector-spins must be even")
    if args.workers < 1:
        parser.error("--workers must be positive")
    times = tuple(float(value) for value in args.times)
    detail_times = tuple(float(value) for value in args.detail_times)
    if not set(detail_times).issubset(times):
        parser.error("--detail-times must be a subset of --times")
    args.raw_out.mkdir(parents=True, exist_ok=True)
    args.fig_out.mkdir(parents=True, exist_ok=True)
    specs = all_specs(args.detector_spins)
    payloads = [(str(args.raw_out), spec, times, args.force) for spec in specs]
    if args.workers == 1:
        for payload in payloads:
            print(f"Completed {_run_spec(payload)}", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(payloads))) as pool:
            futures = {pool.submit(_run_spec, payload): payload[1].key for payload in payloads}
            for future in as_completed(futures):
                print(f"Completed {future.result()}", flush=True)

    diagnostics = AngularDiagnosticService(args.bins)
    simulator = ComparisonSimulator(args.raw_out)
    records: list[dict[str, object]] = []
    for spec in specs:
        for time_value in times:
            raw = load_raw(simulator.raw_path(spec, time_value))
            records.append(asdict(diagnostics.calculate(spec, time_value, raw)))
    paired = paired_distance_records(args.raw_out, specs, times, diagnostics)
    families = conjecture_families()
    atlases: list[str] = []
    heatmaps: list[str] = []
    for family in families:
        family_model_specs = family_specs(family, detector_spins=args.detector_spins)
        for time_value in detail_times:
            for page_index, start in enumerate(range(0, len(family.values), args.columns_per_page), start=1):
                values = family.values[start : start + args.columns_per_page]
                atlases.append(str(plot_family_atlas_page(args.raw_out, args.fig_out, family, family_model_specs, diagnostics, time_value, values, page_index)))
        heatmaps.append(str(plot_family_heatmaps(args.fig_out, family, records, paired, times)))
    aggregates = aggregate_rows(families, records, paired)
    synthesis = plot_synthesis(args.fig_out, aggregates)
    metrics_path = args.fig_out / "conjecture_model_metrics.csv"
    paired_path = args.fig_out / "conjecture_paired_distances.csv"
    aggregate_path = args.fig_out / "conjecture_family_aggregates.csv"
    write_csv(metrics_path, records)
    write_csv(paired_path, paired)
    write_csv(aggregate_path, aggregates)
    manifest = {
        "scope": "exact four study grids analyzed in reports/zeus_single_pixel_analysis_2026-07-16/conclusions.tex",
        "detector_spins": args.detector_spins,
        "total_qubits": args.detector_spins + 1,
        "single_detector_partition": [args.detector_spins],
        "two_detector_partition": [args.detector_spins // 2, args.detector_spins // 2],
        "collective_Jx": 0.01,
        "edge_Jx": 0.01 / math.sqrt(args.detector_spins),
        "two_pixel_signs": "detector 1 negative; detector 2 positive",
        "times": times,
        "detail_times": detail_times,
        "bins": args.bins,
        "families": [asdict(family) for family in families],
        "pair_count": len(specs) // 2,
        "model_count": len(specs),
        "expected_raw_spectra": len(specs) * len(times),
        "raw_root": str(args.raw_out.resolve()),
        "figure_root": str(args.fig_out.resolve()),
        "atlases": atlases,
        "heatmaps": heatmaps,
        "synthesis": str(synthesis),
        "metrics": str(metrics_path),
        "paired_distances": str(paired_path),
        "family_aggregates": str(aggregate_path),
        "runtime": runtime_versions(),
    }
    (args.fig_out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
