"""Run and plot a central-field sweep for the clean single-pixel ring.

The requested Hamiltonian is represented with the repository's overall-minus
sign convention, which leaves theta distributions and Born-ratio diagnostics
unchanged. ``Jx`` is the collective coupling and every ``X_0 X_i`` edge has
coefficient ``Jx/sqrt(N)``.

The script is resumable.  It saves one sector eigensystem per ``hz0`` and one
raw relative-evolution spectrum per requested time, then creates matched 3xL
atlases.  ``P(theta)`` and ``P(pi-theta)`` are always rendered as histograms;
the occupied-bin ``R(theta)`` values are connected with lines as requested.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.analysis import DisentanglementAnalyzer
from collapse.born import born_ratio_from_radii
from collapse.distribution_fit import fit_folded_circular_models
from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from collapse.resonant_study import folded_wrapped_gaussian_bin_density


BLUE = "#1677b8"
RED = "#df2b2f"
RATIO = "#6a3d7a"
DEFAULT_HZ0 = (0.0, 0.05, 0.09, 0.10, 0.11, 0.15, 0.20)
DEFAULT_TIMES = (1.0e3, 1.0e4, 1.0e5, 1.0e6)


def local_resonance_distance(hz0: float, hz: float, j: float) -> float:
    """Return min |hz0 + s(hz + J r)| for s=+/-1 and r=-2,0,2."""
    return float(
        min(abs(hz0 + spin * (hz + j * neighbours)) for spin in (-1.0, 1.0) for neighbours in (-2.0, 0.0, 2.0))
    )


def central_field_wrapped_variance(
    hz0: float,
    hz: float,
    t: float,
    *,
    j: float,
    jx: float,
) -> float:
    """Finite-time local-channel variance for an infinite-temperature ring.

    The local denominators are ``delta = hz0 + s(hz + J r)`` with
    ``P(r=-2,0,2)=(1/4,1/2,1/4)``. ``jx`` is the collective coupling before
    division by ``sqrt(N)``.
    """

    def kernel(omega: float) -> float:
        if abs(omega) < 1.0e-14:
            return t * t
        return 2.0 * (1.0 - math.cos(omega * t)) / omega**2

    weighted = 0.0
    for spin in (-1.0, 1.0):
        for neighbours, probability in ((-2.0, 0.25), (0.0, 0.50), (2.0, 0.25)):
            delta = hz0 + spin * (hz + j * neighbours)
            weighted += 0.5 * probability * kernel(2.0 * delta)
    return float(4.0 * jx**2 * weighted)


def density(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    counts, _ = np.histogram(values, bins=edges)
    return counts / max(values.size, 1) / np.diff(edges)


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


def phi_harmonic_2(eigenvalues: np.ndarray) -> float:
    lam = np.asarray(eigenvalues, dtype=np.complex128)
    mask = np.isfinite(lam.real) & np.isfinite(lam.imag) & (np.abs(lam) > 1.0e-12)
    if not np.any(mask):
        return float("nan")
    return float(abs(np.mean(np.exp(2j * np.angle(lam[mask])))))


def wire_sphere(ax) -> None:
    azimuth = np.linspace(0.0, 2.0 * np.pi, 34)
    polar = np.linspace(0.0, np.pi, 17)
    x = np.outer(np.cos(azimuth), np.sin(polar))
    y = np.outer(np.sin(azimuth), np.sin(polar))
    z = np.outer(np.ones_like(azimuth), np.cos(polar))
    ax.plot_wireframe(x, y, z, color="#9aa0a6", linewidth=0.28, alpha=0.25)


def raw_path(raw_root: Path, detector_n: int, hz0: float, t: float) -> Path:
    return raw_root / f"N{detector_n:02d}" / f"hz0_{hz0:+.4f}" / f"raw_t{t:.12g}.npz"


def compute_sweep(
    raw_root: Path,
    *,
    detector_n: int,
    hz0_values: tuple[float, ...],
    times: tuple[float, ...],
    hz: float,
    j: float,
    jx: float,
    force: bool,
) -> None:
    total_qubits = detector_n + 1
    edge_jx = jx / math.sqrt(detector_n)
    for hz0 in hz0_values:
        case_dir = raw_root / f"N{detector_n:02d}" / f"hz0_{hz0:+.4f}"
        case_dir.mkdir(parents=True, exist_ok=True)
        requested = [raw_path(raw_root, detector_n, hz0, t) for t in times]
        if not force and all(path.is_file() for path in requested):
            print(f"Reusing N={detector_n}, hz0={hz0:+.4f}", flush=True)
            continue

        print(f"Diagonalizing sectors: N={detector_n}, hz={hz:g}, hz0={hz0:+.4f}, Jx={jx:g}, Jx(edge)={edge_jx:.7g}", flush=True)
        started = time.perf_counter()
        hamiltonian = SinglePixelHamiltonianQuSpin(
            N_pixel=detector_n,
            J=j,
            Jpm=0.0,
            Jx=edge_jx,
            Jy=0.0,
            Jz=0.0,
            Jzx=0.0,
            hx=0.0,
            hz=hz,
            hx0=0.0,
            hz0=hz0,
            connectivity="ring",
            central_coupling="all",
            use_symmetry=True,
        )
        sectors = hamiltonian.diagonalize_sectors()
        diagonalization_seconds = time.perf_counter() - started
        for t in times:
            analyzer = DisentanglementAnalyzer.from_sectors(sectors, t, total_qubits)
            eigenvalues = np.asarray(analyzer.D0, dtype=np.complex128)
            theta = 2.0 * np.arctan(np.abs(eigenvalues))
            variance = central_field_wrapped_variance(
                hz0, hz, t, j=j, jx=jx
            )
            np.savez_compressed(
                raw_path(raw_root, detector_n, hz0, t),
                eigenvalues=eigenvalues,
                theta=theta,
                theory_variance=variance,
                hz0=hz0,
                hz=hz,
                J=j,
                Jx_edge=edge_jx,
                Jx=jx,
                detector_n=detector_n,
                total_qubits=total_qubits,
            )
        metadata = {
            "detector_n": detector_n,
            "total_qubits": total_qubits,
            "hz": hz,
            "hz0": hz0,
            "J": j,
            "Jx": jx,
            "Jx_edge": edge_jx,
            "times": times,
            "sector_count": len(sectors),
            "diagonalization_seconds": diagonalization_seconds,
            "local_resonance_distance": local_resonance_distance(hz0, hz, j),
            "overall_sign": "repository convention is minus the displayed Hamiltonian; theta and R are invariant",
        }
        (case_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def atlas_for_time(
    raw_root: Path,
    figure_root: Path,
    *,
    detector_n: int,
    hz0_values: tuple[float, ...],
    time_value: float,
    hz: float,
    j: float,
    jx: float,
    bins: int,
) -> tuple[Path, list[dict[str, float]]]:
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    born = np.cos(centers / 2.0) ** 2
    figure = plt.figure(figsize=(24.0, 10.5), constrained_layout=True)
    grid = figure.add_gridspec(3, len(hz0_values), height_ratios=(1.0, 0.9, 1.35))
    records: list[dict[str, float]] = []

    for column, hz0 in enumerate(hz0_values):
        raw = np.load(raw_path(raw_root, detector_n, hz0, time_value))
        theta = np.asarray(raw["theta"], dtype=float)
        eigenvalues = np.asarray(raw["eigenvalues"], dtype=np.complex128)
        p_theta = density(theta, edges)
        p_reflected = density(np.pi - theta, edges)
        denominator = p_theta + p_reflected
        ratio = np.divide(p_theta, denominator, out=np.full_like(p_theta, np.nan), where=denominator > 0.0)
        occupied = np.isfinite(ratio)
        variance = float(raw["theory_variance"])
        theory = folded_wrapped_gaussian_bin_density(edges, variance)
        theory_reflected = theory[::-1]
        wrapped_l1 = float(np.sum(np.abs(p_theta - theory) * np.diff(edges)))
        born_rmse = float(np.sqrt(np.mean((ratio[occupied] - born[occupied]) ** 2)))
        finite = np.isfinite(eigenvalues.real) & np.isfinite(eigenvalues.imag)
        born_score = float(born_ratio_from_radii(np.abs(eigenvalues[finite]), n_theta=100).similarity)
        fitted = fit_folded_circular_models(theta, edges)

        ax_hist = figure.add_subplot(grid[0, column])
        # Both empirical distributions are histograms.  Only the analytic
        # wrapped-Gaussian references are drawn as dashed curves.
        ax_hist.stairs(p_theta, edges, color=BLUE, linewidth=1.45, fill=True, alpha=0.17, label=r"$P(\theta)$")
        ax_hist.stairs(p_reflected, edges, color=RED, linewidth=1.35, fill=True, alpha=0.13, label=r"$P(\pi-\theta)$")
        ax_hist.plot(centers, theory, color=BLUE, linestyle="--", linewidth=1.05, label="wrapped Gaussian")
        ax_hist.plot(centers, theory_reflected, color=RED, linestyle="--", linewidth=1.00, label="reflected Gaussian")
        ax_hist.set_xlim(0.0, np.pi)
        ax_hist.grid(alpha=0.16)
        matched = abs(hz0 - hz) < 1.0e-12
        ax_hist.set_title(rf"$h_{{z0}}={hz0:g}$" + ("  matched" if matched else ""), fontsize=12)
        ax_hist.tick_params(labelbottom=False, labelsize=8)
        if column == 0:
            ax_hist.set_ylabel("density", fontsize=11)
            ax_hist.legend(fontsize=7, loc="upper center", frameon=False)

        ax_ratio = figure.add_subplot(grid[1, column])
        # Connect all occupied-bin points, including across empty-bin gaps, as
        # explicitly requested by the user.
        ax_ratio.plot(
            centers[occupied],
            ratio[occupied],
            "o-",
            color=RATIO,
            linewidth=0.95,
            markersize=3.0,
            label=r"$R(\theta)$ (occupied bins)",
        )
        ax_ratio.plot(centers, born, color="black", linestyle="--", linewidth=1.25, label=r"$\cos^2(\theta/2)$")
        ax_ratio.set(xlim=(0.0, np.pi), ylim=(-0.04, 1.04))
        ax_ratio.grid(alpha=0.16)
        ax_ratio.tick_params(labelsize=8)
        ax_ratio.text(
            0.04,
            0.08,
            rf"$S_{{born}}={born_score:.3f}$" + "\n" + rf"RMSE$={born_rmse:.3f}$",
            transform=ax_ratio.transAxes,
            fontsize=8,
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
                "hz": hz,
                "hz0": hz0,
                "hz0_minus_hz": hz0 - hz,
                "t": time_value,
                "S_born": born_score,
                "born_rmse": born_rmse,
                "angular_bin_coverage": float(np.mean(occupied)),
                "phi_harmonic_2": phi_harmonic_2(eigenvalues),
                "theory_variance": variance,
                "wrapped_gaussian_l1": wrapped_l1,
                "best_fit_wrapped_gaussian_sigma": fitted.wrapped_gaussian_sigma,
                "best_fit_wrapped_gaussian_l1": fitted.wrapped_gaussian_l1,
                "best_fit_wrapped_gaussian_js": fitted.wrapped_gaussian_js,
                "best_fit_wrapped_cauchy_gamma": fitted.wrapped_cauchy_gamma,
                "best_fit_wrapped_cauchy_l1": fitted.wrapped_cauchy_l1,
                "best_fit_wrapped_cauchy_js": fitted.wrapped_cauchy_js,
                "cauchy_log_likelihood_advantage_per_sample": fitted.cauchy_log_likelihood_advantage_per_sample,
                "preferred_wrapped_model": fitted.preferred_model,
                "finite_eigenvalues": float(np.count_nonzero(finite)),
                "local_resonance_distance": local_resonance_distance(hz0, hz, j),
            }
        )

    power = int(round(math.log10(time_value)))
    edge_jx = jx / math.sqrt(detector_n)
    figure.suptitle(
        rf"Single-pixel central-field atlas: detector $N={detector_n}$, $J=1$, $h_z={hz:g}$, "
        rf"$J_x={jx:g}$ ($J_x^{{edge}}={edge_jx:.5f}$), $t=10^{{{power}}}$",
        fontsize=16,
        fontweight="bold",
    )
    path = figure_root / f"N{detector_n}_hz0_diagnostic_atlas_t1e{power}.png"
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path, records


def summary_plot(figure_root: Path, records: list[dict[str, float]], hz0_values: tuple[float, ...], times: tuple[float, ...], detector_n: int) -> Path:
    lookup = {(row["t"], row["hz0"]): row for row in records}
    colors = plt.cm.viridis(np.linspace(0.08, 0.92, len(times)))
    figure, axes = plt.subplots(1, 3, figsize=(16.0, 4.7), constrained_layout=True)
    for color, time_value in zip(colors, times):
        label = rf"$t=10^{{{int(round(math.log10(time_value)))}}}$"
        axes[0].plot(hz0_values, [lookup[(time_value, value)]["S_born"] for value in hz0_values], "o-", color=color, label=label)
        axes[1].plot(hz0_values, [lookup[(time_value, value)]["angular_bin_coverage"] for value in hz0_values], "o-", color=color)
        axes[2].plot(hz0_values, [lookup[(time_value, value)]["phi_harmonic_2"] for value in hz0_values], "o-", color=color)
    for ax in axes:
        ax.axvline(0.1, color="black", linestyle="--", linewidth=1.0, label=r"$h_{z0}=h_z$")
        ax.set_xlabel(r"$h_{z0}$")
        ax.grid(alpha=0.2)
    axes[0].set_ylabel(r"$S_{born}$")
    axes[0].set_title("Born similarity")
    axes[0].legend(fontsize=8, frameon=False)
    axes[1].set_ylabel("occupied-bin fraction")
    axes[1].set_ylim(-0.03, 1.03)
    axes[1].set_title(r"polar support")
    axes[2].set_ylabel(r"$|\langle e^{2i\phi}\rangle|$")
    axes[2].set_ylim(-0.03, 1.03)
    axes[2].set_title("azimuthal localization")
    figure.suptitle(rf"Central-field sweep summary, detector $N={detector_n}$, $h_z=0.1$", fontsize=15, fontweight="bold")
    path = figure_root / f"N{detector_n}_hz0_sweep_summary.png"
    figure.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-out", type=Path, default=Path("work/single_pixel_hz0_sweep_2026-07-14"))
    parser.add_argument("--fig-out", type=Path, default=Path("figures/single_pixel_hz0_diagnostic_atlas_2026-07-14"))
    parser.add_argument("--N", type=int, default=10, dest="detector_n", help="detector spins; total qubits are N+1")
    parser.add_argument("--hz", type=float, default=0.1)
    parser.add_argument("--hz0", type=float, nargs="+", default=DEFAULT_HZ0)
    parser.add_argument("--times", type=float, nargs="+", default=DEFAULT_TIMES)
    parser.add_argument("--J", type=float, default=1.0, dest="j")
    parser.add_argument("--Jx", type=float, default=0.01, dest="jx", help="collective coupling; each X0 Xi edge uses Jx/sqrt(N)")
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    hz0_values = tuple(float(value) for value in args.hz0)
    times = tuple(float(value) for value in args.times)
    args.raw_out.mkdir(parents=True, exist_ok=True)
    args.fig_out.mkdir(parents=True, exist_ok=True)

    compute_sweep(
        args.raw_out,
        detector_n=args.detector_n,
        hz0_values=hz0_values,
        times=times,
        hz=args.hz,
        j=args.j,
        jx=args.jx,
        force=args.force,
    )

    records: list[dict[str, float]] = []
    atlases: list[str] = []
    for time_value in times:
        path, time_records = atlas_for_time(
            args.raw_out,
            args.fig_out,
            detector_n=args.detector_n,
            hz0_values=hz0_values,
            time_value=time_value,
            hz=args.hz,
            j=args.j,
            jx=args.jx,
            bins=args.bins,
        )
        records.extend(time_records)
        atlases.append(str(path))

    summary = summary_plot(args.fig_out, records, hz0_values, times, args.detector_n)
    metrics = args.fig_out / f"N{args.detector_n}_hz0_diagnostic_metrics.csv"
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
            "hz": args.hz,
            "connectivity": "ring",
            "central_coupling": "all",
        },
        "hz0": hz0_values,
        "times": times,
        "bins": args.bins,
        "empirical_distribution_rendering": "stairs histograms for P(theta) and P(pi-theta)",
        "ratio_rendering": "occupied-bin points connected by lines",
        "atlases": atlases,
        "summary_plot": str(summary),
        "metrics_csv": str(metrics),
    }
    (args.fig_out / "hz0_diagnostic_atlas_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
