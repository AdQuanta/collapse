"""Build the reproducible numerical evidence for the M(t) study.

The production convention is documented in ``collapse.relative_evolution_study``.
No kernel smoothing is used: displayed angular distributions are raw uniform-bin
histograms and empty reflection-ratio bins are masked.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
import platform
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy

from collapse.relative_evolution_study import (
    AngularHistogram,
    RelativeEvolutionCase,
    angular_histogram,
    build_sector_eigenbases,
    compare_first_order_to_exact,
    default_cases,
    detector_resonance_summary,
    evaluate_snapshot,
    evaluate_time_average,
    exact_zero_field_j0_angles,
    histogram_distances,
    midpoint_time_grid,
    theta_wasserstein,
)


BLUE = "#1f77b4"
RED = "#d62728"
PURPLE = "#6f3c8a"
BLACK = "#111111"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/pdf/relative_evolution_matrix_study_2026-08-01"),
    )
    parser.add_argument("--max-n", type=int, default=12)
    parser.add_argument("--time-average-n", type=int, default=8)
    parser.add_argument("--time-samples", type=int, default=96)
    parser.add_argument("--final-time", type=float, default=1000.0)
    parser.add_argument("--snapshot-time", type=float, default=31.7)
    return parser.parse_args()


def save_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty table {path}")
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_histogram(ax_p, ax_r, histogram: AngularHistogram, title: str) -> None:
    ax_p.stairs(
        histogram.density,
        histogram.edges,
        fill=True,
        alpha=0.20,
        color=BLUE,
        label=r"$P(\theta)$",
    )
    ax_p.stairs(
        histogram.reflected_density,
        histogram.edges,
        fill=True,
        alpha=0.16,
        color=RED,
        label=r"$P(\pi-\theta)$",
    )
    ax_p.set(xlim=(0, np.pi), ylabel="density", title=title)
    ax_p.legend(frameon=False, ncol=2, fontsize=8)
    ax_p.grid(alpha=0.18)

    ax_r.plot(
        histogram.centers[histogram.occupied],
        histogram.ratio[histogram.occupied],
        "o-",
        color=PURPLE,
        markersize=2.5,
        linewidth=1.0,
        label=r"$R(\theta)$ (occupied bins)",
    )
    ax_r.plot(
        histogram.centers,
        histogram.born,
        "--",
        color=BLACK,
        linewidth=1.2,
        label=r"$\cos^2(\theta/2)$",
    )
    ax_r.text(
        0.03,
        0.08,
        rf"$S_{{\rm Born}}={histogram.born_similarity:.3f}$" + "\n"
        + rf"$\mathrm{{RMSE}}={histogram.occupied_rmse:.3f}$",
        transform=ax_r.transAxes,
        fontsize=8,
    )
    ax_r.set(xlim=(0, np.pi), ylim=(-0.03, 1.03), xlabel=r"$\theta$", ylabel=r"$R(\theta)$")
    ax_r.legend(frameon=False, fontsize=8)
    ax_r.grid(alpha=0.18)


def diagnostic_atlas(
    path: Path,
    cases: tuple[RelativeEvolutionCase, ...],
    histograms: dict[str, AngularHistogram],
    heading: str,
) -> None:
    fig, axes = plt.subplots(len(cases), 2, figsize=(10.5, 2.6 * len(cases)), constrained_layout=True)
    for row, case in enumerate(cases):
        plot_histogram(axes[row, 0], axes[row, 1], histograms[case.key], case.key.replace("_", " "))
    fig.suptitle(heading, fontsize=14, fontweight="bold")
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = parse_args()
    if args.max_n < 4 or args.time_average_n < 4:
        raise ValueError("system sizes must be at least four")
    output = args.output.resolve()
    figures = output / "figures"
    data = output / "data"
    figures.mkdir(parents=True, exist_ok=False)
    data.mkdir(parents=True)

    cases = default_cases()
    sizes = tuple(value for value in (4, 6, 8, 10, 12) if value <= args.max_n)
    if args.time_average_n not in sizes:
        raise ValueError("time-average N must be one of the evaluated sizes")
    configuration = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "repository_hamiltonian_sign": "minus",
        "boundary_condition": "periodic detector ring",
        "sigma_plus": "(sigma_x + i sigma_y)/2",
        "central_basis": "sigma_z eigenbasis; logical |0> has sigma_z=+1",
        "histogram_bins": 48,
        "empty_ratio_visualization": "masked",
        "legacy_born_score_empty_bin_value": 0.5,
        "sizes": sizes,
        "time_average_n": args.time_average_n,
        "time_samples": args.time_samples,
        "final_time": args.final_time,
        "snapshot_time": args.snapshot_time,
        "cases": [asdict(case) for case in cases],
    }
    save_json(output / "effective_configuration.json", configuration)
    save_json(
        output / "environment.json",
        {
            "platform": platform.platform(),
            "python": sys.version,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
        },
    )

    snapshot_rows: list[dict] = []
    resonance_rows: list[dict] = []
    time_rows: list[dict] = []
    snapshot_histograms: dict[str, AngularHistogram] = {}
    average_histograms: dict[str, AngularHistogram] = {}
    snapshots_by_case_n = {}
    cached_time_sectors = {}

    total_started = time.perf_counter()
    for case_index, case in enumerate(cases, start=1):
        print(f"[{case_index}/{len(cases)}] {case.key}", flush=True)
        for detector_n in sizes:
            sectors, diagonalization_seconds = build_sector_eigenbases(case, detector_n)
            if detector_n == args.time_average_n:
                cached_time_sectors[case.key] = sectors
            snapshot = evaluate_snapshot(
                case,
                detector_n,
                args.snapshot_time,
                sectors,
                compare_direct=detector_n <= 10,
            )
            snapshots_by_case_n[(case.key, detector_n)] = snapshot
            np.savez_compressed(
                data / f"snapshot_{case.key}_N{detector_n}.npz",
                theta=snapshot.spectrum.theta,
                radii=snapshot.spectrum.radii,
                finite=snapshot.spectrum.finite,
                infinite=snapshot.spectrum.infinite,
                indeterminate=snapshot.spectrum.indeterminate,
            )
            h = snapshot.histogram
            snapshot_rows.append(
                {
                    "case": case.key,
                    "model": case.model,
                    "N": detector_n,
                    "detector_dimension": 2**detector_n,
                    "time": args.snapshot_time,
                    "diagonalization_seconds": diagonalization_seconds,
                    "pencil_seconds": snapshot.elapsed_seconds,
                    "max_sector_dimension": max(snapshot.spectrum.sector_dimensions),
                    "max_pencil_dimension": max(snapshot.spectrum.detector_block_dimensions),
                    "max_homogeneous_residual": snapshot.spectrum.maximum_homogeneous_residual,
                    "max_isometry_residual": snapshot.spectrum.maximum_column_isometry_residual,
                    "max_condition_u00": snapshot.spectrum.maximum_condition_number_u00,
                    "min_singular_u00": snapshot.spectrum.minimum_singular_value_u00,
                    "infinite_roots": int(np.sum(snapshot.spectrum.infinite)),
                    "indeterminate_roots": int(np.sum(snapshot.spectrum.indeterminate)),
                    "direct_comparison_sectors": snapshot.spectrum.direct_comparison_sectors,
                    "direct_skipped_sectors": snapshot.spectrum.direct_skipped_sectors,
                    "max_direct_angle_error": snapshot.spectrum.maximum_direct_angle_error,
                    "born_similarity": h.born_similarity,
                    "occupied_rmse": h.occupied_rmse,
                    "entropy_normalized": h.entropy_normalized,
                    "support_fraction": h.support_fraction,
                }
            )
            print(
                f"  N={detector_n}: diag={diagonalization_seconds:.2f}s "
                f"pencil={snapshot.elapsed_seconds:.2f}s residual="
                f"{snapshot.spectrum.maximum_homogeneous_residual:.2e}",
                flush=True,
            )

        snapshot_histograms[case.key] = snapshots_by_case_n[(case.key, sizes[-1])].histogram
        resonance = detector_resonance_summary(case, detector_n=args.time_average_n)
        resonance_rows.append({"case": case.key, **asdict(resonance)})

        times = midpoint_time_grid(args.final_time, args.time_samples)
        average, time_snapshots = evaluate_time_average(
            case,
            args.time_average_n,
            cached_time_sectors[case.key],
            times,
            bins=48,
        )
        average_histograms[case.key] = average
        pooled = np.concatenate([item.spectrum.theta for item in time_snapshots])
        np.savez_compressed(
            data / f"time_average_{case.key}_N{args.time_average_n}.npz",
            times=times,
            theta=pooled,
            histogram_edges=average.edges,
            histogram_counts=average.counts,
        )
        time_rows.append(
            {
                "case": case.key,
                "N": args.time_average_n,
                "final_time": args.final_time,
                "samples": args.time_samples,
                "born_similarity": average.born_similarity,
                "occupied_rmse": average.occupied_rmse,
                "entropy_normalized": average.entropy_normalized,
                "support_fraction": average.support_fraction,
            }
        )

    write_csv(data / "snapshot_metrics.csv", snapshot_rows)
    write_csv(data / "resonance_metrics.csv", resonance_rows)
    write_csv(data / "time_average_metrics.csv", time_rows)

    diagnostic_atlas(
        figures / "snapshot_diagnostics.png",
        cases,
        snapshot_histograms,
        rf"Exact finite-$N$ projective spectra at $t={args.snapshot_time:g}$, $N={sizes[-1]}$",
    )
    diagnostic_atlas(
        figures / "time_average_diagnostics.png",
        cases,
        average_histograms,
        rf"Midpoint time averages: $N={args.time_average_n}$, $T={args.final_time:g}$, {args.time_samples} samples",
    )

    # Finite-size convergence relative to the largest calculated N.
    convergence_rows: list[dict] = []
    fig, ax = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
    for case in cases:
        reference = snapshots_by_case_n[(case.key, sizes[-1])].spectrum.theta
        values = []
        for detector_n in sizes:
            candidate = snapshots_by_case_n[(case.key, detector_n)].spectrum.theta
            distance = theta_wasserstein(candidate, reference)
            values.append(distance)
            convergence_rows.append(
                {"case": case.key, "N": detector_n, "reference_N": sizes[-1], "wasserstein_theta": distance}
            )
        ax.plot(sizes, values, "o-", markersize=4, label=case.key.replace("_", " "))
    ax.set(xlabel=r"detector size $N$", ylabel=r"$W_1(P_t^{(N)},P_t^{(N_{\max})})$", yscale="symlog", title="Finite-size comparison of raw angle measures")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=7, ncol=2)
    fig.savefig(figures / "finite_size_convergence.png", dpi=240, bbox_inches="tight")
    plt.close(fig)
    write_csv(data / "finite_size_convergence.csv", convergence_rows)

    # Exact collective-spin validation in the zero-field independent-spin limit.
    exact_case = RelativeEvolutionCase("m1_exact_zero", "Model 1", "exact zero-field limit", 0.0, 0.0, 0.0, 0.0, 0.2)
    exact_sectors, _ = build_sector_eigenbases(exact_case, 8)
    exact_rows = []
    fig, ax = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
    exact_times = np.linspace(0.0, 40.0, 81)
    maximum_errors = []
    for value in exact_times:
        numerical = evaluate_snapshot(exact_case, 8, float(value), exact_sectors)
        analytical = exact_zero_field_j0_angles(8, exact_case.collective_jx, float(value))
        distance = theta_wasserstein(numerical.spectrum.theta, analytical)
        maximum_errors.append(distance)
        exact_rows.append({"time": value, "wasserstein_theta": distance})
    ax.semilogy(exact_times, np.maximum(maximum_errors, np.finfo(float).tiny), color=BLUE)
    ax.set(xlabel=r"$t$", ylabel=r"$W_1$ angle error", title=r"Exact check: $M=i\tan[(J_x/\sqrt{N})t\sum_i X_i]$ ($N=8$)")
    ax.grid(alpha=0.25)
    fig.savefig(figures / "exact_collective_spin_validation.png", dpi=240, bbox_inches="tight")
    plt.close(fig)
    write_csv(data / "exact_collective_spin_validation.csv", exact_rows)

    # First-order error scaling away from and at resonance.
    perturbation_rows: list[dict] = []
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2), constrained_layout=True)
    base_cases = [next(case for case in cases if case.key == key) for key in ("m2_matched", "m2_detuned")]
    couplings = (0.0025, 0.005, 0.01, 0.02)
    perturbation_times = (0.1, 1.0, 10.0)
    for axis, base in zip(axes, base_cases):
        for time_value in perturbation_times:
            errors = []
            for coupling_value in couplings:
                case = replace(base, collective_jx=coupling_value)
                sectors, _ = build_sector_eigenbases(case, 6)
                snapshot = evaluate_snapshot(case, 6, time_value, sectors)
                metrics = compare_first_order_to_exact(snapshot)
                errors.append(metrics["wasserstein_angle_error"])
                perturbation_rows.append(
                    {"case": base.key, "Jx": coupling_value, "N": 6, "time": time_value, **metrics}
                )
            axis.loglog(couplings, errors, "o-", label=rf"$t={time_value:g}$")
        axis.set(xlabel=r"collective $J_x$", ylabel=r"$W_1$ angle error", title=base.key.replace("_", " "))
        axis.grid(alpha=0.25, which="both")
        axis.legend(frameon=False)
    fig.suptitle("First-order Dyson approximation: controlled only before secular growth")
    fig.savefig(figures / "first_order_error_scaling.png", dpi=240, bbox_inches="tight")
    plt.close(fig)
    write_csv(data / "first_order_error_scaling.csv", perturbation_rows)

    # Correlate basis-invariant resonant weight with time-averaged diagnostics.
    resonance_by_case = {row["case"]: row for row in resonance_rows}
    average_by_case = {row["case"]: row for row in time_rows}
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2), constrained_layout=True)
    for case in cases:
        weight = resonance_by_case[case.key]["resonant_weight_fraction"]
        axes[0].scatter(weight, average_by_case[case.key]["entropy_normalized"], s=45)
        axes[1].scatter(weight, average_by_case[case.key]["born_similarity"], s=45)
        for axis in axes:
            axis.annotate(case.key, (weight, axis.collections[-1].get_offsets()[-1, 1]), fontsize=6, xytext=(3, 3), textcoords="offset points")
    axes[0].set(xlabel="resonant Frobenius-weight fraction", ylabel="normalized histogram entropy")
    axes[1].set(xlabel="resonant Frobenius-weight fraction", ylabel=r"$S_{\rm Born}$")
    for axis in axes:
        axis.grid(alpha=0.25)
    fig.suptitle(r"First-order resonance is a mechanism, not by itself a theorem for $P$ or $R$")
    fig.savefig(figures / "resonance_weight_correlations.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    # Numerical conditioning and validation at the representative snapshot.
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.0), constrained_layout=True)
    for case in cases:
        rows = [row for row in snapshot_rows if row["case"] == case.key]
        n_values = [row["N"] for row in rows]
        axes[0].semilogy(n_values, [max(row["max_homogeneous_residual"], 1e-18) for row in rows], "o-", label=case.key)
        axes[1].semilogy(n_values, [max(row["max_isometry_residual"], 1e-18) for row in rows], "o-")
        direct_x = [row["N"] for row in rows if np.isfinite(row["max_direct_angle_error"])]
        direct_y = [max(row["max_direct_angle_error"], 1e-18) for row in rows if np.isfinite(row["max_direct_angle_error"])]
        axes[2].semilogy(direct_x, direct_y, "o-")
    axes[0].set(ylabel="maximum residual", title="homogeneous pencil residual")
    axes[1].set(title="propagator-column isometry residual")
    axes[2].set(title="direct solve vs projective pencil")
    for axis in axes:
        axis.set(xlabel=r"$N$")
        axis.grid(alpha=0.25)
    axes[0].legend(frameon=False, fontsize=6, ncol=2)
    fig.savefig(figures / "numerical_validation.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    # Quadrature-window and sample-count sensitivity for matched/detuned cases.
    averaging_rows: list[dict] = []
    for key in ("m2_matched", "m2_detuned"):
        case = next(item for item in cases if item.key == key)
        reference = average_histograms[key]
        sectors = cached_time_sectors[key]
        for final_time, sample_count in ((300.0, 48), (1000.0, 48), (1000.0, 192)):
            candidate, _ = evaluate_time_average(
                case,
                args.time_average_n,
                sectors,
                midpoint_time_grid(final_time, sample_count),
                bins=48,
            )
            averaging_rows.append(
                {
                    "case": key,
                    "N": args.time_average_n,
                    "final_time": final_time,
                    "samples": sample_count,
                    **histogram_distances(candidate, reference),
                    "born_similarity": candidate.born_similarity,
                }
            )
    write_csv(data / "time_average_convergence.csv", averaging_rows)

    principal = []
    for case in cases:
        snapshot = next(row for row in snapshot_rows if row["case"] == case.key and row["N"] == sizes[-1])
        principal.append(
            {
                "case": case.key,
                "model": case.model,
                "hz": case.hz,
                "J": case.j,
                "Jpm": case.jpm,
                "hz0": case.hz0,
                "Jx_collective": case.collective_jx,
                "snapshot_N": sizes[-1],
                "snapshot_entropy": snapshot["entropy_normalized"],
                "snapshot_S_born": snapshot["born_similarity"],
                "time_average_N": args.time_average_n,
                "time_average_entropy": average_by_case[case.key]["entropy_normalized"],
                "time_average_S_born": average_by_case[case.key]["born_similarity"],
                "resonant_weight_fraction": resonance_by_case[case.key]["resonant_weight_fraction"],
                "nearest_active_detuning": resonance_by_case[case.key]["nearest_active_detuning"],
            }
        )
    write_csv(output / "principal_comparisons.csv", principal)

    readme = f"""# Relative-evolution matrix study outputs

Generated by `examples/build_relative_evolution_matrix_study.py` using the exact
finite-size generalized pencil `U10 v = lambda U00 v` in detector-translation
sectors. The repository Hamiltonian has the documented overall minus sign.

## Reproduce

```powershell
.venv\\Scripts\\python.exe examples\\build_relative_evolution_matrix_study.py --output {args.output.as_posix()}
```

The configured sizes are `{sizes}`; the largest snapshot size is `N={sizes[-1]}`.
Time averages use `N={args.time_average_n}`, `T={args.final_time:g}`, and
`{args.time_samples}` midpoint samples. Histograms use 48 uniform bins on
`[0, pi]` with no smoothing. Empty `R` bins are masked; only the legacy
`S_Born` metric assigns them `1/2`.
Dependencies are Python 3.11-compatible NumPy, SciPy, Matplotlib, QuSpin, and
pytest. Render the readable report panels and compile the report with:

```powershell
.venv\\Scripts\\python.exe examples\\render_relative_evolution_study_panels.py {args.output.as_posix()}
Set-Location {args.output.as_posix()}
pdflatex -interaction=nonstopmode -halt-on-error relative_evolution_matrix_study.tex
pdflatex -interaction=nonstopmode -halt-on-error relative_evolution_matrix_study.tex
```

`principal_comparisons.csv` is the compact machine-readable result table.
`data/` contains full metrics and compressed raw projective-angle samples.
`figures/` contains the publication-quality plots. The LaTeX report and PDF are
compiled separately in this same directory.
"""
    (output / "README.md").write_text(readme, encoding="utf-8")
    save_json(
        output / "run_summary.json",
        {
            "elapsed_seconds": time.perf_counter() - total_started,
            "largest_N": sizes[-1],
            "status": "complete",
        },
    )
    print(f"Completed in {time.perf_counter() - total_started:.1f}s: {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
