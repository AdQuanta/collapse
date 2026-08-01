"""Sweep detector plus-minus coupling at fixed J=1 and fixed fields.

The displayed Hamiltonian is

    H = hz sum_i Zi + J sum_i Zi Z(i+1)
        + Jpm sum_i (sigma+_i sigma-_(i+1) + h.c.)
        + (Jx/sqrt(N)) X0 sum_i Xi,

with ``hz=0.1``, ``hz0=0`` and collective ``Jx=0.01`` by default.  The
hybrid logarithmic/linear Jpm grid resolves weak exchange and includes
``Jpm=J`` plus values larger than J.  One 3xL atlas is produced per time.
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

from collapse.single_pixel_atlas import (
    AngularDiagnosticCalculator,
    DetectorSpectralVarianceProvider,
    NpzSpectrumRepository,
    QuSpinSectorBackend,
    RelativeSpectrumComputer,
    SinglePixelSpec,
    SweepRunner,
)
from examples.plot_single_pixel_hz0_diagnostic_atlas import (
    BLUE,
    RED,
    RATIO,
    bloch_branches,
    wire_sphere,
)


DEFAULT_JPM_VALUES = (0.0, 0.001, 0.01, 0.03, 0.1, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0)
DEFAULT_TIMES = (1.0e3, 1.0e4, 1.0e5, 1.0e6)


def value_tag(value: float) -> str:
    """Filesystem-safe stable tag for one nonnegative coupling value."""

    return f"{value:.6g}".replace(".", "p").replace("-", "m")


def case_root(raw_root: Path, jpm: float) -> Path:
    return Path(raw_root) / f"Jpm_{value_tag(jpm)}"


def raw_path(raw_root: Path, detector_n: int, jpm: float, hz: float, t: float) -> Path:
    return NpzSpectrumRepository(case_root(raw_root, jpm)).sample_path(detector_n, hz, t)


def validate_grid(jpm_values: tuple[float, ...], j: float) -> None:
    if any(value < 0.0 for value in jpm_values):
        raise ValueError("Jpm values must be nonnegative")
    if len(set(jpm_values)) != len(jpm_values):
        raise ValueError("Jpm grid contains duplicates")
    if not any(math.isclose(value, j, rel_tol=0.0, abs_tol=1.0e-12) for value in jpm_values):
        raise ValueError("Jpm grid must explicitly include Jpm=J")
    if not any(0.0 < value <= 0.01 * abs(j) for value in jpm_values):
        raise ValueError("Jpm grid must include a very small nonzero value")
    if not any(value > abs(j) for value in jpm_values):
        raise ValueError("Jpm grid must include values larger than J")


def compute_sweep(
    raw_root: Path,
    *,
    detector_n: int,
    jpm_values: tuple[float, ...],
    times: tuple[float, ...],
    hz0: float,
    hz: float,
    j: float,
    jx: float,
    force: bool,
) -> None:
    for jpm in jpm_values:
        spec = SinglePixelSpec(detector_n=detector_n, j=j, jpm=jpm, jx=jx, hz0=hz0)
        repository = NpzSpectrumRepository(case_root(raw_root, jpm))
        computer = RelativeSpectrumComputer(QuSpinSectorBackend(), DetectorSpectralVarianceProvider())
        SweepRunner(computer, repository).run(spec, (hz,), times, force=force)


def atlas_for_time(
    raw_root: Path,
    figure_root: Path,
    *,
    detector_n: int,
    jpm_values: tuple[float, ...],
    time_value: float,
    hz0: float,
    hz: float,
    j: float,
    jx: float,
    bins: int,
) -> tuple[Path, list[dict[str, float]]]:
    calculator = AngularDiagnosticCalculator(bins)
    width = max(18.0, 3.15 * len(jpm_values))
    figure = plt.figure(figsize=(width, 10.5), constrained_layout=True)
    grid = figure.add_gridspec(3, len(jpm_values), height_ratios=(1.0, 0.9, 1.35))
    records: list[dict[str, float]] = []

    for column, jpm in enumerate(jpm_values):
        repository = NpzSpectrumRepository(case_root(raw_root, jpm))
        sample = repository.load_sample(detector_n, hz, time_value)
        diagnostic = calculator.calculate(sample)

        ax_hist = figure.add_subplot(grid[0, column])
        ax_hist.stairs(
            diagnostic.p_theta, diagnostic.edges, color=BLUE, linewidth=1.45,
            fill=True, alpha=0.17, label=r"$P(\theta)$",
        )
        ax_hist.stairs(
            diagnostic.p_reflected, diagnostic.edges, color=RED, linewidth=1.35,
            fill=True, alpha=0.13, label=r"$P(\pi-\theta)$",
        )
        ax_hist.plot(
            diagnostic.centers, diagnostic.theory, color=BLUE, linestyle="--",
            linewidth=1.05, label="spectral WG",
        )
        ax_hist.plot(
            diagnostic.centers, diagnostic.theory_reflected, color=RED,
            linestyle="--", linewidth=1.0, label="reflected spectral WG",
        )
        equality = r"  ($J_{\pm}=J$)" if math.isclose(jpm, j, rel_tol=0.0, abs_tol=1.0e-12) else ""
        ax_hist.set_title(rf"$J_{{\pm}}={jpm:g}$" + equality, fontsize=11)
        ax_hist.set_xlim(0.0, np.pi)
        ax_hist.grid(alpha=0.16)
        ax_hist.tick_params(labelbottom=False, labelsize=8)
        if column == 0:
            ax_hist.set_ylabel("density", fontsize=11)
            ax_hist.legend(fontsize=7, loc="upper center", frameon=False)

        ax_ratio = figure.add_subplot(grid[1, column])
        ax_ratio.plot(
            diagnostic.centers[diagnostic.occupied], diagnostic.ratio[diagnostic.occupied],
            "o-", color=RATIO, linewidth=0.95, markersize=3.0,
            label=r"$R(\theta)$ (occupied bins)",
        )
        ax_ratio.plot(
            diagnostic.centers, diagnostic.born_curve, color="black", linestyle="--",
            linewidth=1.25, label=r"$\cos^2(\theta/2)$",
        )
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
        branch0, branch1 = bloch_branches(sample.eigenvalues)
        wire_sphere(ax_bloch)
        ax_bloch.scatter(
            branch0[:, 0], branch0[:, 1], branch0[:, 2], s=4.5,
            color=BLUE, alpha=0.34, depthshade=False,
        )
        ax_bloch.scatter(
            branch1[:, 0], branch1[:, 1], branch1[:, 2], s=4.5,
            color=RED, alpha=0.28, depthshade=False,
        )
        ax_bloch.set(xlim=(-1.04, 1.04), ylim=(-1.04, 1.04), zlim=(-1.04, 1.04))
        ax_bloch.set_box_aspect((1.0, 1.0, 1.0))
        ax_bloch.view_init(elev=22.0, azim=42.0)
        ax_bloch.set_axis_off()
        if column == 0:
            ax_bloch.text2D(
                0.02, 0.03, r"blue: $v(\lambda)$" + "\n" + r"red: $-v(\lambda)$",
                transform=ax_bloch.transAxes, fontsize=8,
            )

        records.append(
            {
                "detector_n": float(detector_n),
                "total_qubits": float(detector_n + 1),
                "hz0": hz0,
                "hz": hz,
                "J": j,
                "Jpm": jpm,
                "Jx": jx,
                "Jx_edge": jx / math.sqrt(detector_n),
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
    figure.suptitle(
        rf"Single-pixel $J_{{\pm}}$ sweep: detector $N={detector_n}$, $J={j:g}$, "
        rf"$h_z={hz:g}$, $h_{{z0}}={hz0:g}$, $J_x={jx:g}$ "
        rf"($J_x^{{edge}}={jx / math.sqrt(detector_n):.5f}$), $t=10^{{{power}}}$",
        fontsize=16, fontweight="bold",
    )
    path = figure_root / f"N{detector_n}_jpm_sweep_atlas_t1e{power}.png"
    figure.savefig(path, dpi=210, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path, records


def summary_plot(
    figure_root: Path,
    records: list[dict[str, float]],
    jpm_values: tuple[float, ...],
    times: tuple[float, ...],
    detector_n: int,
    j: float,
) -> Path:
    lookup = {(row["Jpm"], row["t"]): row for row in records}
    colors = plt.cm.viridis(np.linspace(0.08, 0.92, len(times)))
    metrics = (
        ("S_born", r"$S_{born}$", None),
        ("angular_bin_coverage", "occupied-bin fraction", (0.0, 1.03)),
        ("phi_harmonic_2", r"$|\langle e^{2i\phi}\rangle|$", (0.0, 1.03)),
        ("wrapped_gaussian_l1", "wrapped-Gaussian L1", None),
    )
    figure, axes = plt.subplots(2, 2, figsize=(12.5, 9.0), sharex=True, constrained_layout=True)
    for ax, (key, ylabel, ylim) in zip(axes.flat, metrics):
        for color, time_value in zip(colors, times):
            values = [lookup[(jpm, time_value)][key] for jpm in jpm_values]
            label = rf"$t=10^{{{int(round(math.log10(time_value)))}}}$"
            ax.plot(jpm_values, values, "o-", color=color, linewidth=1.35, markersize=4.0, label=label)
        ax.axvline(j, color="black", linestyle="--", linewidth=1.0, label=r"$J_{\pm}=J$")
        ax.set_xscale("symlog", linthresh=0.001, linscale=0.7)
        ax.set_ylabel(ylabel)
        ax.set_xlabel(r"$J_{\pm}$")
        ax.grid(alpha=0.2)
        if ylim is not None:
            ax.set_ylim(*ylim)
    axes[0, 0].legend(fontsize=8, frameon=False, ncol=2)
    figure.suptitle(
        rf"Single-pixel plus-minus sweep, detector $N={detector_n}$, $J={j:g}$, $h_z=0.1$, $h_{{z0}}=0$",
        fontsize=15, fontweight="bold",
    )
    path = figure_root / f"N{detector_n}_jpm_sweep_summary.png"
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-out", type=Path, default=Path("work/single_pixel_jpm_sweep_2026-07-14"))
    parser.add_argument("--fig-out", type=Path, default=Path("figures/single_pixel_jpm_sweep_atlas_2026-07-14"))
    parser.add_argument("--N", type=int, default=10, dest="detector_n")
    parser.add_argument("--Jpm", type=float, nargs="+", default=DEFAULT_JPM_VALUES, dest="jpm_values")
    parser.add_argument("--times", type=float, nargs="+", default=DEFAULT_TIMES)
    parser.add_argument("--hz0", type=float, default=0.0)
    parser.add_argument("--hz", type=float, default=0.1)
    parser.add_argument("--J", type=float, default=1.0, dest="j")
    parser.add_argument(
        "--Jx", type=float, default=0.01, dest="jx",
        help="collective coupling; each X0 Xi edge uses Jx/sqrt(N)",
    )
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    jpm_values = tuple(float(value) for value in args.jpm_values)
    times = tuple(float(value) for value in args.times)
    validate_grid(jpm_values, args.j)
    args.raw_out.mkdir(parents=True, exist_ok=True)
    args.fig_out.mkdir(parents=True, exist_ok=True)

    compute_sweep(
        args.raw_out,
        detector_n=args.detector_n,
        jpm_values=jpm_values,
        times=times,
        hz0=args.hz0,
        hz=args.hz,
        j=args.j,
        jx=args.jx,
        force=args.force,
    )

    records: list[dict[str, float]] = []
    atlas_paths: list[str] = []
    for time_value in times:
        path, time_records = atlas_for_time(
            args.raw_out,
            args.fig_out,
            detector_n=args.detector_n,
            jpm_values=jpm_values,
            time_value=time_value,
            hz0=args.hz0,
            hz=args.hz,
            j=args.j,
            jx=args.jx,
            bins=args.bins,
        )
        atlas_paths.append(str(path))
        records.extend(time_records)

    summary = summary_plot(args.fig_out, records, jpm_values, times, args.detector_n, args.j)
    metrics = args.fig_out / f"N{args.detector_n}_jpm_sweep_metrics.csv"
    with metrics.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    manifest = {
        "raw_root": str(args.raw_out.resolve()),
        "figure_root": str(args.fig_out.resolve()),
        "detector_n": args.detector_n,
        "total_qubits": args.detector_n + 1,
        "hamiltonian": "hz sum Zi + J sum Zi Z(i+1) + Jpm sum (sigma+_i sigma-_(i+1) + h.c.) + (Jx/sqrt(N)) X0 sum Xi",
        "overall_sign": "repository generators construct the negative of the displayed Hamiltonian; theta and R are invariant",
        "fixed_parameters": {
            "J": args.j,
            "Jx": args.jx,
            "Jx_edge": args.jx / math.sqrt(args.detector_n),
            "hz": args.hz,
            "hz0": args.hz0,
            "connectivity": "ring",
            "central_coupling": "all",
        },
        "Jpm_values": jpm_values,
        "Jpm_equals_J_included": any(math.isclose(value, args.j, rel_tol=0.0, abs_tol=1.0e-12) for value in jpm_values),
        "times": times,
        "bins": args.bins,
        "wrapped_gaussian_reference": "no-fit exact finite-N detector spectral variance from Eq. (6.4) of reports/four_model_finite_time_eigenvalue_derivation_2026-07-10.md",
        "empirical_distribution_rendering": "stairs histograms for P(theta) and P(pi-theta)",
        "ratio_rendering": "occupied-bin points connected by lines",
        "atlases": atlas_paths,
        "summary_plot": str(summary),
        "metrics_csv": str(metrics),
    }
    (args.fig_out / "jpm_sweep_atlas_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
