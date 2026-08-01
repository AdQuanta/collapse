"""Create the completion figures/tables from saved mandatory and long-time runs."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collapse.level_spacing import compute_unfolded_spacings, poisson_spacing_distribution, wigner_spacing_distribution
from collapse.resonant_study import folded_wrapped_gaussian_bin_density


def _raw(case: Path, time_value: float) -> Path:
    paths = list(case.glob("raw_*.npz"))
    return min(paths, key=lambda path: abs(float(path.stem.split("_t")[-1]) - time_value))


def _density(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    counts, _ = np.histogram(values, bins=edges)
    return counts / max(values.size, 1) / np.diff(edges)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mandatory", type=Path, required=True)
    parser.add_argument("--long-average", type=Path, required=True)
    parser.add_argument("--near-resonance", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    hz_values = (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)
    required_times = (100.0, 1_000.0, 10_000.0, 100_000.0, 1_000_000.0)
    edges = np.linspace(0.0, np.pi, 49)
    centers = (edges[:-1] + edges[1:]) / 2.0
    born = np.cos(centers / 2.0) ** 2
    colors = plt.cm.viridis(np.linspace(0.05, 0.95, len(required_times)))

    time_rows: list[dict] = []
    theory_rows: list[dict] = []
    for hz in hz_values:
        case = args.mandatory / "N10" / f"hz_{hz:+.3f}"
        for row in _read_csv(case / "time_metrics.csv"):
            row.update({"N": 10, "hz": hz})
            time_rows.append(row)
        for time_value in required_times:
            raw = np.load(_raw(case, time_value))
            empirical = _density(raw["theta"], edges)
            predicted = folded_wrapped_gaussian_bin_density(edges, float(raw["theory_variance"]))
            theory_rows.append({
                "N": 10, "hz": hz, "t": time_value,
                "predicted_variance": float(raw["theory_variance"]),
                "fitted_variance": float(raw["fitted_variance"]),
                "predicted_density_l1": float(np.sum(np.abs(empirical - predicted) * np.diff(edges))),
            })
    _write_csv(args.out / "N10_per_time_metrics.csv", time_rows)
    _write_csv(args.out / "N10_wrapped_gaussian_comparison.csv", theory_rows)

    near_rows: list[dict] = []
    for case in sorted((args.near_resonance / "N08").glob("hz_*")):
        hz = float(case.name.split("_")[-1])
        center = min((-2.0, 0.0, 2.0), key=lambda value: abs(hz - value))
        for row in _read_csv(case / "time_metrics.csv"):
            row.update({"N": 8, "hz": hz, "resonance_center": center, "detuning": hz - center})
            near_rows.append(row)
    _write_csv(args.out / "N8_near_resonance_metrics.csv", near_rows)

    fig, axes = plt.subplots(3, 3, figsize=(14, 10), sharex="col", constrained_layout=True)
    for col, center in enumerate((-2.0, 0.0, 2.0)):
        for time_value, color in zip(required_times, colors):
            selected = sorted((row for row in near_rows if np.isclose(float(row["resonance_center"]), center) and np.isclose(float(row["t"]), time_value)), key=lambda row: float(row["detuning"]))
            delta = [float(row["detuning"]) for row in selected]
            axes[0, col].plot(delta, [float(row["S_born"]) for row in selected], "o-", color=color, label=f"{time_value:.0e}")
            axes[1, col].semilogy(delta, [max(float(row["theory_variance"]), 1e-14) for row in selected], "o-", color=color)
            axes[2, col].semilogy(delta, [float(row["condition_number"]) for row in selected], "o-", color=color)
        for row_index in range(3):
            axes[row_index, col].axvline(0.0, color="0.55", ls="--", lw=0.8)
        axes[0, col].set_title(rf"around $h_z={center:g}$")
        axes[2, col].set_xlabel(r"detuning $\delta h_z$")
    axes[0, 0].set_ylabel(r"project $S_{born}$")
    axes[1, 0].set_ylabel(r"predicted $\sigma^2$")
    axes[2, 0].set_ylabel(r"cond$(U_{00})$")
    axes[0, 0].legend(title="time", fontsize=7)
    fig.savefig(args.out / "N8_near_resonance_resolution.png", dpi=240)
    plt.close(fig)

    finite_size_rows = list(time_rows)
    for hz in hz_values:
        case = args.long_average / "N08" / f"hz_{hz:+.3f}"
        for row in _read_csv(case / "time_metrics.csv"):
            if any(np.isclose(float(row["t"]), value) for value in required_times):
                row.update({"N": 8, "hz": hz})
                finite_size_rows.append(row)
    _write_csv(args.out / "N8_N10_required_time_metrics.csv", finite_size_rows)

    # Exact required-time metric table and conditioning evolution.
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8), constrained_layout=True)
    for time_value, color in zip(required_times, colors):
        selected = sorted((row for row in time_rows if np.isclose(float(row["t"]), time_value)), key=lambda row: float(row["hz"]))
        x = [float(row["hz"]) for row in selected]
        axes[0].plot(x, [float(row["S_born"]) for row in selected], "o-", color=color, label=f"{time_value:.0e}")
        axes[1].plot(x, [float(row["born_rmse"]) for row in selected], "o-", color=color)
        axes[2].semilogy(x, [float(row["condition_number"]) for row in selected], "o-", color=color)
    for ax in axes:
        for resonance in (-2, 0, 2):
            ax.axvline(resonance, color="0.75", ls="--", lw=0.8)
        ax.set_xlabel(r"$h_z$")
    axes[0].set(ylabel=r"project $S_{born}$", title="Canonical Born similarity")
    axes[1].set(ylabel="Born-ratio RMSE", title="Ratio residual")
    axes[2].set(ylabel=r"cond$(U_{00})$", title="Numerical conditioning")
    axes[0].legend(title="time", fontsize=8)
    fig.savefig(args.out / "N10_required_times_metrics_and_conditioning.png", dpi=240)
    plt.close(fig)

    fig, axes = plt.subplots(1, len(required_times), figsize=(18, 3.2), sharey=True, constrained_layout=True)
    for ax, time_value in zip(axes, required_times):
        for n, style in ((8, "o-"), (10, "s--")):
            selected = sorted((row for row in finite_size_rows if int(row["N"]) == n and np.isclose(float(row["t"]), time_value)), key=lambda row: float(row["hz"]))
            ax.plot([float(row["hz"]) for row in selected], [float(row["S_born"]) for row in selected], style, label=f"N={n}")
        for resonance in (-2, 0, 2):
            ax.axvline(resonance, color="0.8", ls=":", lw=0.8)
        ax.set(title=rf"$t={time_value:.0e}$", xlabel=r"$h_z$")
    axes[0].set_ylabel(r"project $S_{born}$")
    axes[0].legend(fontsize=8)
    fig.savefig(args.out / "N8_N10_finite_size_Sborn.png", dpi=240)
    plt.close(fig)

    # Every mandatory (h_z,t) distribution, reflected density, and fixed theory.
    fig, axes = plt.subplots(len(required_times), len(hz_values), figsize=(18, 11), sharex=True, sharey=True, constrained_layout=True)
    for row_index, time_value in enumerate(required_times):
        for col_index, hz in enumerate(hz_values):
            raw = np.load(_raw(args.mandatory / "N10" / f"hz_{hz:+.3f}", time_value))
            p = _density(raw["theta"], edges)
            reflected = _density(np.pi - raw["theta"], edges)
            theory = folded_wrapped_gaussian_bin_density(edges, float(raw["theory_variance"]))
            ax = axes[row_index, col_index]
            ax.plot(centers, p, color="#1f77b4", lw=1.2)
            ax.plot(centers, reflected, color="#e45756", lw=1.0, alpha=0.85)
            ax.plot(centers, theory, color="black", ls="--", lw=0.9)
            if row_index == 0:
                ax.set_title(rf"$h_z={hz:g}$", fontsize=10)
            if col_index == 0:
                ax.set_ylabel(rf"$t={time_value:.0e}$" + "\ndensity", fontsize=9)
    axes[-1, 0].set_xlabel(r"$\theta$")
    axes[0, 0].legend((r"$P(\theta)$", r"$P(\pi-\theta)$", "fixed theory"), fontsize=7)
    fig.savefig(args.out / "N10_all_required_Ptheta_reflection_theory.png", dpi=240)
    plt.close(fig)

    # Compact fixed-theory comparison for presentation use.
    fig, axes = plt.subplots(2, 3, figsize=(12, 6), sharex=True, sharey=True, constrained_layout=True)
    for row_index, time_value in enumerate((100.0, 1_000.0)):
        for col_index, hz in enumerate((-2.0, 0.0, 2.0)):
            raw = np.load(_raw(args.mandatory / "N10" / f"hz_{hz:+.3f}", time_value))
            empirical = _density(raw["theta"], edges)
            predicted = folded_wrapped_gaussian_bin_density(edges, float(raw["theory_variance"]))
            axes[row_index, col_index].step(centers, empirical, where="mid", color="#1f77b4", label="QuSpin")
            axes[row_index, col_index].plot(centers, predicted, "k--", label="fixed theory")
            axes[row_index, col_index].set_title(rf"$h_z={hz:g},\ t={time_value:.0e}$")
            if col_index == 0:
                axes[row_index, col_index].set_ylabel(r"density / $d\theta$")
    axes[0, 0].legend(fontsize=8)
    for ax in axes[1]:
        ax.set_xlabel(r"$\theta$")
    fig.savefig(args.out / "N10_wrapped_gaussian_early_late.png", dpi=240)
    plt.close(fig)

    # Fresh 3-D Bloch-sphere point clouds at the final mandatory time.
    fig = plt.figure(figsize=(12, 4), constrained_layout=True)
    for index, hz in enumerate((-2.0, 0.0, 2.0), start=1):
        ax = fig.add_subplot(1, 3, index, projection="3d")
        raw = np.load(_raw(args.mandatory / "N10" / f"hz_{hz:+.3f}", 1_000_000.0))
        finite = np.isfinite(raw["phi"])
        theta, phi = raw["theta"][finite], raw["phi"][finite]
        x, y, z = np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)
        ax.scatter(x, y, z, s=5, alpha=0.5, c=z, cmap="coolwarm")
        u = np.linspace(0, 2 * np.pi, 28)
        v = np.linspace(0, np.pi, 14)
        ax.plot_wireframe(np.outer(np.cos(u), np.sin(v)), np.outer(np.sin(u), np.sin(v)), np.outer(np.ones_like(u), np.cos(v)), color="0.82", linewidth=0.25)
        ax.set(title=rf"$h_z={hz:g}$", xlim=(-1, 1), ylim=(-1, 1), zlim=(-1, 1))
        ax.view_init(elev=22, azim=38)
        ax.set_axis_off()
    fig.suptitle(r"Fresh N=10 Bloch distributions at $t=10^6$", fontsize=14)
    fig.savefig(args.out / "N10_3D_bloch_t1e6.png", dpi=240)
    plt.close(fig)

    # R(theta)-Born residual for every mandatory point.
    fig, axes = plt.subplots(len(required_times), len(hz_values), figsize=(18, 10), sharex=True, sharey=True, constrained_layout=True)
    for row_index, time_value in enumerate(required_times):
        for col_index, hz in enumerate(hz_values):
            raw = np.load(_raw(args.mandatory / "N10" / f"hz_{hz:+.3f}", time_value))
            p = _density(raw["theta"], edges)
            reflected = _density(np.pi - raw["theta"], edges)
            ratio = np.divide(p, p + reflected, out=np.full_like(p, np.nan), where=(p + reflected) > 0)
            ax = axes[row_index, col_index]
            ax.axhline(0, color="0.6", lw=0.7)
            ax.plot(centers, ratio - born, color="#6f4e7c", lw=1.1)
            if row_index == 0:
                ax.set_title(rf"$h_z={hz:g}$", fontsize=10)
            if col_index == 0:
                ax.set_ylabel(rf"$t={time_value:.0e}$" + "\nR-Born", fontsize=9)
    axes[-1, 0].set_xlabel(r"$\theta$")
    fig.savefig(args.out / "N10_all_required_R_minus_Born.png", dpi=240)
    plt.close(fig)

    # Genuine long-time averages and time-block uncertainty.
    long_rows: list[dict] = []
    fig, axes = plt.subplots(2, 4, figsize=(15, 7), sharex=True, sharey=True, constrained_layout=True)
    for ax, hz in zip(axes.flat, hz_values):
        case = args.long_average / "N08" / f"hz_{hz:+.3f}"
        average = np.load(case / "long_time_average.npz")
        summary = json.loads((case / "long_time_summary.json").read_text(encoding="utf-8"))
        x = (average["theta_edges"][:-1] + average["theta_edges"][1:]) / 2.0
        ax.plot(x, average["p_theta"], color="#1f77b4", label=r"$\bar P(\theta)$")
        ax.fill_between(x, average["p_theta"] - average["p_theta_time_se"], average["p_theta"] + average["p_theta_time_se"], color="#1f77b4", alpha=0.2)
        ax.plot(x, average["p_reflected"], color="#e45756", label=r"$\bar P(\pi-\theta)$")
        ax.set_title(rf"$h_z={hz:g}$")
        long_rows.append({"N": 8, "hz": hz, **{key: value for key, value in summary.items() if not isinstance(value, (list, dict))}, **{f"born_rmse_bins_{key}": value for key, value in summary["binning_born_rmse"].items()}})
    axes.flat[-1].axis("off")
    axes[0, 0].legend(fontsize=8)
    for ax in axes[-1, :3]:
        ax.set_xlabel(r"$\theta$")
    fig.suptitle(r"Equal-weight long-time average, 66 saved times with $t>10^3$", fontsize=14)
    fig.savefig(args.out / "N8_long_time_average_with_block_uncertainty.png", dpi=240)
    plt.close(fig)
    _write_csv(args.out / "N8_long_time_summary.csv", long_rows)

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.5), constrained_layout=True)
    x = [row["hz"] for row in long_rows]
    axes[0].bar(x, [row["alternate_grid_l1"] for row in long_rows])
    axes[1].bar(x, [row["lower_edge_sensitivity_l1"] for row in long_rows])
    for key, style in zip(("32", "48", "64"), ("o-", "s-", "^-") ):
        axes[2].plot(x, [row[f"born_rmse_bins_{key}"] for row in long_rows], style, label=f"{key} bins")
    axes[0].set(title="Interleaved-grid sensitivity", ylabel="density L1", xlabel=r"$h_z$")
    axes[1].set(title=r"Lower edge: $10^3$ vs $10^4$", ylabel="density L1", xlabel=r"$h_z$")
    axes[2].set(title="Binning sensitivity", ylabel="Born RMSE", xlabel=r"$h_z$")
    axes[2].legend(fontsize=8)
    fig.savefig(args.out / "N8_long_time_stability.png", dpi=240)
    plt.close(fig)

    # Raw/mean-shifted spectra and resolved-sector level statistics.
    fig, axes = plt.subplots(2, 4, figsize=(15, 7), constrained_layout=True)
    spacing_rows = []
    for ax, hz in zip(axes.flat, hz_values):
        aggregate = np.load(args.mandatory / "N10" / f"hz_{hz:+.3f}" / "aggregate.npz")
        levels = aggregate["detector_sector_spectrum"]
        spacings = compute_unfolded_spacings(levels, tol=1e-9, degree=3, trim_fraction=0.1)
        spread = float(np.ptp(spacings)) if spacings.size else 0.0
        scale = max(float(np.max(np.abs(spacings))) if spacings.size else 1.0, 1.0)
        if spacings.size and np.all(np.isfinite(spacings)) and spread > 1e-10 * scale:
            ax.hist(spacings, bins=12, density=True, alpha=0.55, label=f"sector n={spacings.size}")
            grid = np.linspace(0, max(3.5, float(np.quantile(spacings, 0.99))), 300)
            ax.plot(grid, poisson_spacing_distribution(grid), "k--", lw=1, label="Poisson")
            ax.plot(grid, wigner_spacing_distribution(grid, 1), lw=1, label="GOE")
            ax.plot(grid, wigner_spacing_distribution(grid, 2), lw=1, label="GUE")
        elif spacings.size:
            ax.text(0.5, 0.5, "Collapsed/degenerate\nspacing sample", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(rf"$h_z={hz:g}$")
        meta = json.loads((args.mandatory / "N10" / f"hz_{hz:+.3f}" / "metadata.json").read_text(encoding="utf-8"))
        spacing_rows.append({"N": 10, "hz": hz, **meta["summary"]["detector_spacing_sector"], **{key: meta["summary"][key] for key in ("spacing_count", "mean_r", "spacing_l1_poisson", "spacing_l1_goe", "spacing_l1_gue")}})
    axes.flat[-1].axis("off")
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(r"Detector spacings in one resolved $k=0,p=+1$ sector ($z=+1$ at $h_z=0$)", fontsize=13)
    fig.savefig(args.out / "N10_detector_sector_level_statistics.png", dpi=240)
    plt.close(fig)
    _write_csv(args.out / "N10_detector_sector_level_statistics.csv", spacing_rows)

    fig, axes = plt.subplots(2, 4, figsize=(15, 7), constrained_layout=True)
    for ax, hz in zip(axes.flat, hz_values):
        aggregate = np.load(args.mandatory / "N10" / f"hz_{hz:+.3f}" / "aggregate.npz")
        detector = np.sort(aggregate["detector_spectrum"])
        full = np.sort(aggregate["full_spectrum"])
        ax.plot(detector - detector.mean(), np.linspace(0, 1, detector.size), label="detector", lw=1)
        ax.plot(full - full.mean(), np.linspace(0, 1, full.size), label="full", lw=1)
        ax.set_title(rf"$h_z={hz:g}$")
        ax.set_xlabel("mean-shifted energy")
        ax.set_ylabel("spectral CDF")
    axes.flat[-1].axis("off")
    axes[0, 0].legend(fontsize=8)
    fig.savefig(args.out / "N10_full_and_detector_spectra_shifted.png", dpi=240)
    plt.close(fig)

    catalog = {
        "mandatory": {"N": 10, "hz": hz_values, "times": required_times, "case_count": 7, "raw_time_points": 35},
        "long_time": {"N": 8, "hz": hz_values, "strict_lower_bound": 1000.0, "log_grid_count": 64, "actual_distinct_time_count": 66, "weighting": "equal per sampled time"},
        "near_resonance": {"N": 8, "centers": (-2.0, 0.0, 2.0), "offsets": (-0.25, -0.10, -0.05, -0.01, 0.0, 0.01, 0.05, 0.10, 0.25), "times": required_times, "raw_time_points": 135},
        "level_statistics": "single resolved translation/reflection sector; z inversion additionally resolved at h_z=0",
        "energy_plot": "mean-shifted energies, sectors not combined for spacing statistics",
    }
    (args.out / "dataset_catalog.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
