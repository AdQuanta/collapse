"""Fresh h_z resonance sweep for the clean single-pixel Hamiltonian.

The central field is fixed to ``hz0=0`` and the collective coupling is
``Jx=0.01``.  Every ``X_0 X_i`` edge therefore has coefficient
``Jx/sqrt(N)``. Five fields are sampled around each analytic resonance
``hz=-2J,0,+2J``. The script saves raw spectra and produces one 3x5 diagnostic
atlas per resonance and requested time.

Empirical ``P(theta)`` and ``P(pi-theta)`` are histogram stairs.  Occupied-bin
``R(theta)`` points are connected by lines, following the user's latest plot
convention.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.single_pixel_atlas import (
    AngularDiagnosticCalculator,
    NpzSpectrumRepository,
    QuSpinSectorBackend,
    RelativeSpectrumComputer,
    SinglePixelSpec,
    SweepRunner,
    central_field_wrapped_variance,
)
from scripts.plot_single_pixel_hz0_diagnostic_atlas import (
    BLUE,
    RED,
    RATIO,
    bloch_branches,
    wire_sphere,
)


DEFAULT_CENTERS = (-2.0, 0.0, 2.0)
DEFAULT_OFFSETS = (-0.05, -0.01, 0.0, 0.01, 0.05)
DEFAULT_TIMES = (1.0e3, 1.0e4, 1.0e5, 1.0e6)


def field_grid(centers: tuple[float, ...], offsets: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(round(center + offset, 10) for center in centers for offset in offsets)


def raw_path(raw_root: Path, detector_n: int, hz: float, t: float) -> Path:
    return NpzSpectrumRepository(raw_root).sample_path(detector_n, hz, t)


def compute_sweep(
    raw_root: Path,
    *,
    detector_n: int,
    hz_values: tuple[float, ...],
    times: tuple[float, ...],
    hz0: float,
    j: float,
    jx: float,
    force: bool,
    jpm: float = 0.0,
) -> None:
    spec = SinglePixelSpec(detector_n=detector_n, j=j, jpm=jpm, jx=jx, hz0=hz0)
    repository = NpzSpectrumRepository(raw_root)
    computer = RelativeSpectrumComputer(QuSpinSectorBackend())
    SweepRunner(computer, repository).run(spec, hz_values, times, force=force)


def atlas_for_resonance(
    raw_root: Path,
    figure_root: Path,
    *,
    detector_n: int,
    center: float,
    offsets: tuple[float, ...],
    time_value: float,
    hz0: float,
    j: float,
    jx: float,
    bins: int,
    jpm: float = 0.0,
    exact_label: str = "resonant",
    filename_prefix: str = "hz_atlas",
) -> tuple[Path, list[dict[str, float]]]:
    hz_values = tuple(round(center + offset, 10) for offset in offsets)
    repository = NpzSpectrumRepository(raw_root)
    calculator = AngularDiagnosticCalculator(bins)
    figure = plt.figure(figsize=(18.0, 10.5), constrained_layout=True)
    grid = figure.add_gridspec(3, len(hz_values), height_ratios=(1.0, 0.9, 1.35))
    records: list[dict[str, float]] = []

    for column, (hz, offset) in enumerate(zip(hz_values, offsets)):
        sample = repository.load_sample(detector_n, hz, time_value)
        diagnostic = calculator.calculate(sample)
        eigenvalues = sample.eigenvalues

        ax_hist = figure.add_subplot(grid[0, column])
        ax_hist.stairs(diagnostic.p_theta, diagnostic.edges, color=BLUE, linewidth=1.45, fill=True, alpha=0.17, label=r"$P(\theta)$")
        ax_hist.stairs(diagnostic.p_reflected, diagnostic.edges, color=RED, linewidth=1.35, fill=True, alpha=0.13, label=r"$P(\pi-\theta)$")
        theory_label = "spectral WG" if jpm != 0.0 else "wrapped Gaussian"
        ax_hist.plot(diagnostic.centers, diagnostic.theory, color=BLUE, linestyle="--", linewidth=1.05, label=theory_label)
        ax_hist.plot(diagnostic.centers, diagnostic.theory_reflected, color=RED, linestyle="--", linewidth=1.00, label="reflected " + theory_label)
        ax_hist.set_xlim(0.0, np.pi)
        ax_hist.grid(alpha=0.16)
        resonant = abs(offset) < 1.0e-12
        ax_hist.set_title(rf"$h_z={hz:g}$" + (f"  {exact_label}" if resonant else rf"  ($\delta={offset:+.2f}$)"), fontsize=12)
        ax_hist.tick_params(labelbottom=False, labelsize=8)
        if column == 0:
            ax_hist.set_ylabel("density", fontsize=11)
            ax_hist.legend(fontsize=7, loc="upper center", frameon=False)

        ax_ratio = figure.add_subplot(grid[1, column])
        ax_ratio.plot(
            diagnostic.centers[diagnostic.occupied], diagnostic.ratio[diagnostic.occupied], "o-", color=RATIO,
            linewidth=0.95, markersize=3.0, label=r"$R(\theta)$ (occupied bins)",
        )
        ax_ratio.plot(diagnostic.centers, diagnostic.born_curve, color="black", linestyle="--", linewidth=1.25, label=r"$\cos^2(\theta/2)$")
        ax_ratio.set(xlim=(0.0, np.pi), ylim=(-0.04, 1.04))
        ax_ratio.grid(alpha=0.16)
        ax_ratio.tick_params(labelsize=8)
        ax_ratio.text(
            0.04, 0.08,
            rf"$S_{{born}}={diagnostic.born_score:.3f}$" + "\n" + rf"RMSE$={diagnostic.born_rmse:.3f}$",
            transform=ax_ratio.transAxes, fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
        )
        if column == 0:
            ax_ratio.set_ylabel(r"$R(\theta)$", fontsize=11)
            ax_ratio.legend(fontsize=7, loc="upper center", frameon=False)
        ax_ratio.set_xlabel(r"$\theta$", fontsize=10)

        ax_bloch = figure.add_subplot(grid[2, column], projection="3d")
        branch0, branch1 = bloch_branches(eigenvalues)
        wire_sphere(ax_bloch)
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
                "detector_n": float(detector_n),
                "total_qubits": float(detector_n + 1),
                "hz0": hz0,
                "J": j,
                "Jpm": jpm,
                "resonance_center": center,
                "hz": hz,
                "detuning": offset,
                "t": time_value,
                "S_born": diagnostic.born_score,
                "born_rmse": diagnostic.born_rmse,
                "angular_bin_coverage": diagnostic.coverage,
                "phi_harmonic_2": diagnostic.phi_harmonic_2,
                "theory_variance": sample.theory_variance,
                "wrapped_gaussian_l1": diagnostic.wrapped_gaussian_l1,
                "best_fit_wrapped_gaussian_sigma": diagnostic.best_fit_wrapped_gaussian_sigma,
                "best_fit_wrapped_gaussian_l1": diagnostic.best_fit_wrapped_gaussian_l1,
                "best_fit_wrapped_gaussian_js": diagnostic.best_fit_wrapped_gaussian_js,
                "best_fit_wrapped_cauchy_gamma": diagnostic.best_fit_wrapped_cauchy_gamma,
                "best_fit_wrapped_cauchy_l1": diagnostic.best_fit_wrapped_cauchy_l1,
                "best_fit_wrapped_cauchy_js": diagnostic.best_fit_wrapped_cauchy_js,
                "cauchy_log_likelihood_advantage_per_sample": diagnostic.cauchy_log_likelihood_advantage_per_sample,
                "preferred_wrapped_model": diagnostic.preferred_wrapped_model,
                "finite_eigenvalues": float(diagnostic.finite_eigenvalues),
            }
        )

    power = int(round(math.log10(time_value)))
    if center == 0.0:
        center_tag = "0"
    else:
        magnitude = f"{abs(center):g}".replace(".", "p")
        center_tag = ("m" if center < 0 else "p") + magnitude
    edge_jx = jx / math.sqrt(detector_n)
    detector_label = rf"$J={j:g}$" if jpm == 0.0 else rf"$J={j:g}, J_{{\pm}}={jpm:g}$"
    figure.suptitle(
        rf"Single-pixel $h_z$ atlas near $h_z={center:g}$: detector $N={detector_n}$, $h_{{z0}}={hz0:g}$, "
        + detector_label
        + rf", $J_x={jx:g}$ ($J_x^{{edge}}={edge_jx:.5f}$), $t=10^{{{power}}}$",
        fontsize=16, fontweight="bold",
    )
    path = figure_root / f"N{detector_n}_{filename_prefix}_center_{center_tag}_t1e{power}.png"
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path, records


def summary_plot(
    figure_root: Path,
    records: list[dict[str, float]],
    centers: tuple[float, ...],
    offsets: tuple[float, ...],
    times: tuple[float, ...],
    detector_n: int,
    *,
    title: str | None = None,
    filename: str | None = None,
) -> Path:
    lookup = {(row["resonance_center"], row["detuning"], row["t"]): row for row in records}
    colors = plt.cm.viridis(np.linspace(0.08, 0.92, len(times)))
    metrics = (
        ("S_born", r"$S_{born}$", None),
        ("angular_bin_coverage", "occupied-bin fraction", (0.0, 1.03)),
        ("phi_harmonic_2", r"$|\langle e^{2i\phi}\rangle|$", (0.0, 1.03)),
    )
    figure, axes = plt.subplots(3, len(centers), figsize=(15.0, 11.0), sharex=True, constrained_layout=True)
    for column, center in enumerate(centers):
        for row_index, (key, ylabel, ylim) in enumerate(metrics):
            ax = axes[row_index, column]
            for color, time_value in zip(colors, times):
                label = rf"$t=10^{{{int(round(math.log10(time_value)))}}}$"
                values = [lookup[(center, offset, time_value)][key] for offset in offsets]
                ax.plot(offsets, values, "o-", color=color, linewidth=1.35, markersize=4.0, label=label)
            ax.axvline(0.0, color="black", linestyle="--", linewidth=1.0)
            ax.grid(alpha=0.2)
            if ylim is not None:
                ax.set_ylim(*ylim)
            if column == 0:
                ax.set_ylabel(ylabel)
            if row_index == 0:
                ax.set_title(rf"near $h_z={center:g}$")
            if row_index == 2:
                ax.set_xlabel(r"detuning $\delta h_z$")
    axes[0, 0].legend(fontsize=8, frameon=False)
    figure.suptitle(title or rf"Single-pixel resonance neighborhoods, detector $N={detector_n}$, $h_{{z0}}=0$", fontsize=16, fontweight="bold")
    path = figure_root / (filename or f"N{detector_n}_hz_resonance_summary.png")
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-out", type=Path, default=Path("work/single_pixel_hz_resonance_sweep_2026-07-14"))
    parser.add_argument("--fig-out", type=Path, default=Path("figures/single_pixel_hz_resonance_atlas_2026-07-14"))
    parser.add_argument("--N", type=int, default=10, dest="detector_n")
    parser.add_argument("--centers", type=float, nargs="+", default=DEFAULT_CENTERS)
    parser.add_argument("--offsets", type=float, nargs="+", default=DEFAULT_OFFSETS)
    parser.add_argument("--times", type=float, nargs="+", default=DEFAULT_TIMES)
    parser.add_argument("--hz0", type=float, default=0.0)
    parser.add_argument("--J", type=float, default=1.0, dest="j")
    parser.add_argument("--Jx", type=float, default=0.01, dest="jx", help="collective coupling; each X0 Xi edge uses Jx/sqrt(N)")
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    centers = tuple(float(value) for value in args.centers)
    offsets = tuple(float(value) for value in args.offsets)
    times = tuple(float(value) for value in args.times)
    hz_values = field_grid(centers, offsets)
    if len(set(hz_values)) != len(hz_values):
        raise ValueError("center/offset grid contains duplicate h_z values")
    args.raw_out.mkdir(parents=True, exist_ok=True)
    args.fig_out.mkdir(parents=True, exist_ok=True)

    compute_sweep(
        args.raw_out,
        detector_n=args.detector_n,
        hz_values=hz_values,
        times=times,
        hz0=args.hz0,
        j=args.j,
        jx=args.jx,
        force=args.force,
    )

    records: list[dict[str, float]] = []
    atlas_paths: list[str] = []
    for time_value in times:
        for center in centers:
            path, atlas_records = atlas_for_resonance(
                args.raw_out, args.fig_out,
                detector_n=args.detector_n, center=center, offsets=offsets,
                time_value=time_value, hz0=args.hz0, j=args.j,
                jx=args.jx, bins=args.bins,
            )
            atlas_paths.append(str(path))
            records.extend(atlas_records)

    summary = summary_plot(args.fig_out, records, centers, offsets, times, args.detector_n)
    metrics = args.fig_out / f"N{args.detector_n}_hz_resonance_metrics.csv"
    with metrics.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    manifest = {
        "raw_root": str(args.raw_out.resolve()),
        "figure_root": str(args.fig_out.resolve()),
        "detector_n": args.detector_n,
        "total_qubits": args.detector_n + 1,
        "fixed_parameters": {
            "J": args.j,
            "Jx": args.jx,
            "Jx_edge": args.jx / math.sqrt(args.detector_n),
            "hz0": args.hz0,
            "connectivity": "ring",
            "central_coupling": "all",
        },
        "resonance_centers": centers,
        "offsets": offsets,
        "hz": hz_values,
        "times": times,
        "bins": args.bins,
        "empirical_distribution_rendering": "stairs histograms for P(theta) and P(pi-theta)",
        "ratio_rendering": "occupied-bin points connected by lines",
        "atlases": atlas_paths,
        "summary_plot": str(summary),
        "metrics_csv": str(metrics),
    }
    (args.fig_out / "hz_resonance_atlas_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
