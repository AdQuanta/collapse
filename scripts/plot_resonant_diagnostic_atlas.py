"""Build Born-search-style diagnostic atlases from saved fresh QuSpin runs.

Each requested time receives one 3 x L figure. Columns are detector fields and
the rows are (1) P(theta), P(pi-theta), and their fixed wrapped-Gaussian
predictions, (2) the reflected Born ratio, and (3) the two antipodal Bloch
branches. The script reads completed raw files and never recomputes dynamics.
"""
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

from core.resonant_study import folded_wrapped_gaussian_bin_density


BLUE = "#1f77b4"
RED = "#d62728"
RATIO = "#6f4e7c"
DEFAULT_HZ = (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)
DEFAULT_TIMES = (1_000.0, 10_000.0, 100_000.0, 1_000_000.0)


def _raw_path(case: Path, time_value: float) -> Path:
    paths = list(case.glob("raw_*.npz"))
    if not paths:
        raise FileNotFoundError(f"No raw files in {case}")
    selected = min(paths, key=lambda path: abs(float(path.stem.split("_t")[-1]) - time_value))
    saved_time = float(selected.stem.split("_t")[-1])
    if not np.isclose(saved_time, time_value, rtol=0.0, atol=max(1e-10, abs(time_value) * 1e-12)):
        raise FileNotFoundError(f"Requested t={time_value:g}; nearest saved file is t={saved_time:g}")
    return selected


def _density(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    counts, _ = np.histogram(values, bins=edges)
    return counts / max(values.size, 1) / np.diff(edges)


def _time_metrics(case: Path, time_value: float) -> dict[str, float]:
    with (case / "time_metrics.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    selected = min(rows, key=lambda row: abs(float(row["t"]) - time_value))
    if not np.isclose(float(selected["t"]), time_value):
        raise ValueError(f"No metrics row for t={time_value:g} in {case}")
    return {key: float(value) for key, value in selected.items() if key != "solver" and value != ""}


def _bloch_branches(eigenvalues: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Match scripts/born_hamiltonian_search.py exactly: v(lambda), -v(lambda)."""
    lam = np.asarray(eigenvalues, dtype=np.complex128)
    finite = np.isfinite(lam.real) & np.isfinite(lam.imag)
    lam = lam[finite]
    radius2 = np.abs(lam) ** 2
    denominator = 1.0 + radius2
    branch0 = np.column_stack(
        [2.0 * lam.real / denominator, 2.0 * lam.imag / denominator, (1.0 - radius2) / denominator]
    )
    return branch0, -branch0


def _downsample(values: np.ndarray, maximum: int) -> np.ndarray:
    if maximum <= 0 or values.shape[0] <= maximum:
        return values
    return values[np.linspace(0, values.shape[0] - 1, maximum, dtype=int)]


def _wire_sphere(ax) -> None:
    azimuth = np.linspace(0.0, 2.0 * np.pi, 34)
    polar = np.linspace(0.0, np.pi, 17)
    x = np.outer(np.cos(azimuth), np.sin(polar))
    y = np.outer(np.sin(azimuth), np.sin(polar))
    z = np.outer(np.ones_like(azimuth), np.cos(polar))
    ax.plot_wireframe(x, y, z, color="#9aa0a6", linewidth=0.28, alpha=0.25)


def _atlas(
    mandatory: Path,
    out: Path,
    *,
    n_detector: int,
    hz_values: tuple[float, ...],
    time_value: float,
    bins: int,
    max_bloch_points: int,
) -> tuple[Path, list[dict[str, float]]]:
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    born = np.cos(centers / 2.0) ** 2
    figure = plt.figure(figsize=(24.0, 10.5), constrained_layout=True)
    grid = figure.add_gridspec(3, len(hz_values), height_ratios=(1.0, 0.9, 1.35))
    records: list[dict[str, float]] = []

    for column, hz in enumerate(hz_values):
        case = mandatory / f"N{n_detector:02d}" / f"hz_{hz:+.3f}"
        raw_path = _raw_path(case, time_value)
        raw = np.load(raw_path)
        metrics = _time_metrics(case, time_value)
        theta = np.asarray(raw["theta"], dtype=float)
        p_theta = _density(theta, edges)
        p_reflected = _density(np.pi - theta, edges)
        denominator = p_theta + p_reflected
        ratio = np.divide(
            p_theta,
            denominator,
            out=np.full_like(p_theta, np.nan),
            where=denominator > 0.0,
        )
        theory = folded_wrapped_gaussian_bin_density(edges, float(raw["theory_variance"]))
        theory_reflected = theory[::-1]
        theory_l1 = float(np.sum(np.abs(p_theta - theory) * np.diff(edges)))

        ax_hist = figure.add_subplot(grid[0, column])
        ax_hist.stairs(p_theta, edges, color=BLUE, linewidth=1.45, fill=True, alpha=0.14, label=r"$P(\theta)$")
        ax_hist.stairs(p_reflected, edges, color=RED, linewidth=1.35, fill=True, alpha=0.11, label=r"$P(\pi-\theta)$")
        ax_hist.plot(centers, theory, color=BLUE, linestyle="--", linewidth=1.15, label="wrapped Gaussian")
        ax_hist.plot(centers, theory_reflected, color=RED, linestyle="--", linewidth=1.10, label="reflected Gaussian")
        ax_hist.set_xlim(0.0, np.pi)
        ax_hist.grid(alpha=0.16)
        ax_hist.set_title(rf"$h_z={hz:g}$" + ("  resonant" if hz in (-2.0, 0.0, 2.0) else ""), fontsize=12)
        ax_hist.tick_params(labelbottom=False, labelsize=8)
        if column == 0:
            ax_hist.set_ylabel("density", fontsize=11)
            ax_hist.legend(fontsize=7, loc="upper center", frameon=False)

        ax_ratio = figure.add_subplot(grid[1, column])
        mask = np.isfinite(ratio)
        # Do not connect empty-bin gaps: a line would imply unsupported angular coverage.
        ax_ratio.plot(centers[mask], ratio[mask], "o", color=RATIO, markersize=3.0, label=r"$R(\theta)$ (occupied bins)")
        ax_ratio.plot(centers, born, color="black", linestyle="--", linewidth=1.25, label=r"$\cos^2(\theta/2)$")
        ax_ratio.set(xlim=(0.0, np.pi), ylim=(-0.04, 1.04))
        ax_ratio.grid(alpha=0.16)
        ax_ratio.tick_params(labelsize=8)
        ax_ratio.text(
            0.04,
            0.08,
            rf"$S_{{born}}={metrics['S_born']:.3f}$" + "\n" + rf"RMSE$={metrics['born_rmse']:.3f}$",
            transform=ax_ratio.transAxes,
            fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
        )
        if column == 0:
            ax_ratio.set_ylabel(r"$R(\theta)$", fontsize=11)
            ax_ratio.legend(fontsize=7, loc="upper center", frameon=False)
        ax_ratio.set_xlabel(r"$\theta$", fontsize=10)

        ax_bloch = figure.add_subplot(grid[2, column], projection="3d")
        branch0, branch1 = _bloch_branches(raw["eigenvalues"])
        finite_eigenvalue_count = branch0.shape[0]
        branch0 = _downsample(branch0, max_bloch_points)
        branch1 = _downsample(branch1, max_bloch_points)
        _wire_sphere(ax_bloch)
        ax_bloch.scatter(branch0[:, 0], branch0[:, 1], branch0[:, 2], s=4.5, color=BLUE, alpha=0.34, depthshade=False)
        ax_bloch.scatter(branch1[:, 0], branch1[:, 1], branch1[:, 2], s=4.5, color=RED, alpha=0.28, depthshade=False)
        ax_bloch.set(xlim=(-1.04, 1.04), ylim=(-1.04, 1.04), zlim=(-1.04, 1.04))
        ax_bloch.set_box_aspect((1.0, 1.0, 1.0))
        ax_bloch.view_init(elev=22.0, azim=42.0)
        ax_bloch.set_axis_off()
        if column == 0:
            ax_bloch.text2D(0.02, 0.03, r"blue: $v(\lambda)$" + "\n" + r"red: $-v(\lambda)$", transform=ax_bloch.transAxes, fontsize=8)

        records.append(
            {
                "N": float(n_detector),
                "hz": hz,
                "t": time_value,
                "S_born": metrics["S_born"],
                "born_rmse": metrics["born_rmse"],
                "condition_number": metrics["condition_number"],
                "phi_harmonic_2": metrics["phi_harmonic_2"],
                "theory_variance": float(raw["theory_variance"]),
                "fitted_variance": float(raw["fitted_variance"]),
                "wrapped_gaussian_l1": theory_l1,
                "angular_bin_coverage": float(np.mean(mask)),
                "finite_eigenvalues": float(finite_eigenvalue_count),
            }
        )

    time_power = int(round(np.log10(time_value)))
    figure.suptitle(
        rf"Born-search diagnostic atlas: $N={n_detector}$, $J=1$, $J_x=0.01$, $h_{{z0}}=0$, $t=10^{{{time_power}}}$",
        fontsize=17,
        fontweight="bold",
    )
    filename = out / f"N{n_detector}_diagnostic_atlas_t1e{time_power}.png"
    figure.savefig(filename, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return filename, records


def _summary_heatmap(out: Path, records: list[dict[str, float]], hz_values: tuple[float, ...], times: tuple[float, ...], n_detector: int) -> Path:
    metrics = (
        ("S_born", r"canonical $S_{born}$", "coolwarm", None),
        ("born_rmse", "Born-ratio RMSE", "magma", (0.0, None)),
        ("condition_number", r"$\log_{10}\,\mathrm{cond}(U_{00})$", "viridis", None),
        ("phi_harmonic_2", r"azimuthal $|\langle e^{2i\phi}\rangle|$", "cividis", (0.0, 1.0)),
        ("angular_bin_coverage", r"occupied $\theta$-bin fraction", "Blues", (0.0, 1.0)),
        ("wrapped_gaussian_l1", "wrapped-Gaussian L1", "plasma", (0.0, None)),
    )
    lookup = {(row["t"], row["hz"]): row for row in records}
    figure, axes = plt.subplots(1, len(metrics), figsize=(22.0, 4.4), constrained_layout=True)
    for ax, (key, title, cmap, limits) in zip(axes, metrics):
        values = np.array([[lookup[(time, hz)][key] for hz in hz_values] for time in times], dtype=float)
        if key == "condition_number":
            values = np.log10(values)
        vmin = None if limits is None else limits[0]
        vmax = None if limits is None else limits[1]
        image = ax.imshow(values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
        for row in range(values.shape[0]):
            for column in range(values.shape[1]):
                rgba = image.cmap(image.norm(values[row, column]))
                luminance = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
                ax.text(column, row, f"{values[row, column]:.2f}", ha="center", va="center", fontsize=8, color="black" if luminance > 0.55 else "white")
        ax.set_title(title, fontsize=11)
        ax.set_xticks(range(len(hz_values)), [f"{hz:g}" for hz in hz_values])
        ax.set_yticks(range(len(times)), [f"$10^{{{int(np.log10(time))}}}$" for time in times])
        ax.set_xlabel(r"$h_z$")
        figure.colorbar(image, ax=ax, shrink=0.76)
    axes[0].set_ylabel("time")
    figure.suptitle(rf"N={n_detector}: coupled dynamical, angular, and numerical diagnostics", fontsize=16, fontweight="bold")
    path = out / f"N{n_detector}_diagnostic_metric_heatmaps_t1e3_to_t1e6.png"
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mandatory", type=Path, default=Path("work/single_pixel_quspin_fresh_2026-07-12/mandatory_N10"))
    parser.add_argument("--out", type=Path, default=Path("figures/single_pixel_quspin_diagnostic_atlas_2026-07-13"))
    parser.add_argument("--N", type=int, default=10, dest="n_detector")
    parser.add_argument("--hz", type=float, nargs="+", default=DEFAULT_HZ)
    parser.add_argument("--times", type=float, nargs="+", default=DEFAULT_TIMES)
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument("--max-bloch-points", type=int, default=1024)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    hz_values = tuple(float(value) for value in args.hz)
    times = tuple(float(value) for value in args.times)
    all_records: list[dict[str, float]] = []
    atlas_paths: list[str] = []
    for time_value in times:
        path, records = _atlas(
            args.mandatory,
            args.out,
            n_detector=args.n_detector,
            hz_values=hz_values,
            time_value=time_value,
            bins=args.bins,
            max_bloch_points=args.max_bloch_points,
        )
        atlas_paths.append(str(path))
        all_records.extend(records)

    heatmap = _summary_heatmap(args.out, all_records, hz_values, times, args.n_detector)
    csv_path = args.out / f"N{args.n_detector}_diagnostic_atlas_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_records[0]))
        writer.writeheader()
        writer.writerows(all_records)
    manifest = {
        "source": str(args.mandatory.resolve()),
        "N": args.n_detector,
        "hz": hz_values,
        "times": times,
        "bins": args.bins,
        "blue_branch": "P(theta) and v(lambda)",
        "red_branch": "P(pi-theta) and -v(lambda)",
        "wrapped_gaussian": "repository fixed no-fit prediction and its reflected density",
        "atlases": atlas_paths,
        "summary_heatmap": str(heatmap),
        "metrics_csv": str(csv_path),
    }
    (args.out / "diagnostic_atlas_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
