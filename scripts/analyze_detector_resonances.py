"""Analyze detector eigenspaces, active resonances, and matched central fields.

The detector-only part is diagonalized at N=8.  Active transition weights are
computed as Frobenius norms of spectral-projector blocks, making every result
independent of the basis chosen inside a degenerate eigenspace.  A targeted
exact-M(t) comparison then tests zero, matched, and detuned central fields for
the Ising-field and plus-minus-field families.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict
from pathlib import Path
import sys
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.detector_resonance import (
    DenseRingDetectorBuilder,
    DetectorSpec,
    SpectralProjectorAnalyzer,
    relative_weight_map_error,
    rotate_subspaces,
    transition_weight_map,
)
from core.single_pixel_atlas import (
    AngularDiagnosticCalculator,
    QuSpinSectorBackend,
    RelativeSpectrumComputer,
    SinglePixelSpec,
    SpectrumSample,
)
from scripts.plot_single_pixel_hz0_diagnostic_atlas import (
    BLUE,
    RED,
    RATIO,
    bloch_branches,
    wire_sphere,
)


CASE2_FIELDS = (-2.0, -0.01, 0.0, 0.01, 2.0)
CASE4_FIELDS = (-2.0, -1.0, 0.0, 1.0, 2.0)
TIMES = (1.0e3, 1.0e4, 1.0e5, 1.0e6)
JPM_VALUES = (0.0, 0.001, 0.01, 0.03, 0.1, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0)


class ZeroVarianceProvider:
    """Avoid unrelated detector-variance work in the exact-M comparison."""

    def variances(self, spec: SinglePixelSpec, hz: float, times: Sequence[float]):
        return tuple(0.0 for _ in times)


def central_mode_value(mode: str, hz: float) -> float:
    if mode == "zero":
        return 0.0
    if mode == "matched":
        return float(hz)
    if mode == "detuned":
        return float(hz + 0.05)
    raise ValueError(mode)


def close_field_grid(centers: Sequence[float]) -> tuple[float, ...]:
    values = {round(center + offset, 12) for center in centers for offset in (-0.05, -0.01, 0.0, 0.01, 0.05)}
    return tuple(sorted(values))


def detector_rows(detector_n: int):
    builder = DenseRingDetectorBuilder()
    analyzer = SpectralProjectorAnalyzer()
    rows: list[dict[str, object]] = []
    cache = {}

    def evaluate(family: str, parameter_name: str, parameter: float, spec: DetectorSpec, mode: str, hz0: float):
        key = (spec.hz, spec.j, spec.jpm)
        if key not in cache:
            operators = builder.build(spec)
            subspaces, transitions, _ = analyzer.analyze(operators, 0.0)
            cache[key] = (operators, subspaces, transitions)
        operators, subspaces, transitions = cache[key]
        summary = analyzer.summarize(subspaces, transitions, hz0)
        row = {
            "family": family,
            "detector_n": detector_n,
            "parameter_name": parameter_name,
            "parameter_value": parameter,
            "mode": mode,
            "hz0": hz0,
            "hz": spec.hz,
            "J": spec.j,
            "Jpm": spec.jpm,
            **asdict(summary),
        }
        rows.append(row)
        return operators, subspaces, transitions

    for hz0 in (-0.2, -0.1, -0.05, 0.0, 0.05, 0.1, 0.2):
        evaluate("case1_hz0", "hz0", hz0, DetectorSpec(detector_n, 0.1, 1.0, 0.0), "sweep", hz0)

    for hz in close_field_grid((-2.0, 0.0, 2.0)):
        for mode in ("zero", "matched", "detuned"):
            evaluate("case2_hz", "hz", hz, DetectorSpec(detector_n, hz, 1.0, 0.0), mode, central_mode_value(mode, hz))

    for jpm in JPM_VALUES:
        evaluate("case3_jpm", "Jpm", jpm, DetectorSpec(detector_n, 0.1, 1.0, jpm), "zero", 0.0)

    for hz in close_field_grid((-2.0, -1.0, 0.0, 1.0, 2.0)):
        for mode in ("zero", "matched", "detuned"):
            evaluate("case4_jpm_hz", "hz", hz, DetectorSpec(detector_n, hz, 0.0, 1.0), mode, central_mode_value(mode, hz))

    invariance_specs = {
        "case1_hz0": DetectorSpec(detector_n, 0.1, 1.0, 0.0),
        "case2_hz_resonant": DetectorSpec(detector_n, 2.0, 1.0, 0.0),
        "case3_jpm_equal_J": DetectorSpec(detector_n, 0.1, 1.0, 1.0),
        "case4_jpm_hz_zero": DetectorSpec(detector_n, 0.0, 0.0, 1.0),
    }
    invariance: list[dict[str, object]] = []
    for family, spec in invariance_specs.items():
        operators = builder.build(spec)
        subspaces = analyzer.energy_subspaces(operators.hamiltonian)
        reference = transition_weight_map(analyzer.active_transitions(subspaces, operators.coupling))
        errors = []
        for seed in range(8):
            candidate = transition_weight_map(
                analyzer.active_transitions(rotate_subspaces(subspaces, seed), operators.coupling)
            )
            errors.append(relative_weight_map_error(reference, candidate))
        invariance.append({"family": family, "maximum_relative_error": max(errors), "rotations": len(errors)})
    return rows, invariance


def dynamics_rows(detector_n: int):
    computer = RelativeSpectrumComputer(QuSpinSectorBackend(), ZeroVarianceProvider())
    calculator = AngularDiagnosticCalculator(48)
    rows: list[dict[str, object]] = []
    samples: dict[tuple[str, str, float, float], SpectrumSample] = {}
    configurations = (
        ("case2_hz", 1.0, 0.0, CASE2_FIELDS),
        ("case4_jpm_hz", 0.0, 1.0, CASE4_FIELDS),
    )
    for family, j, jpm, fields in configurations:
        for hz in fields:
            for mode in ("zero", "matched", "detuned"):
                hz0 = central_mode_value(mode, hz)
                spec = SinglePixelSpec(detector_n=detector_n, j=j, jpm=jpm, jx=0.01, hz0=hz0)
                field_samples, metadata = computer.compute_field(spec, hz, TIMES)
                for sample in field_samples:
                    diagnostic = calculator.calculate(sample)
                    strong = (
                        diagnostic.born_score >= 0.75
                        and diagnostic.coverage >= 0.50
                        and diagnostic.phi_harmonic_2 <= 0.25
                    )
                    row = {
                        "family": family,
                        "detector_n": detector_n,
                        "mode": mode,
                        "hz0": hz0,
                        "hz": hz,
                        "J": j,
                        "Jpm": jpm,
                        "Jx": 0.01,
                        "Jx_edge": 0.01 / math.sqrt(detector_n),
                        "t": sample.t,
                        "S_born": diagnostic.born_score,
                        "born_rmse": diagnostic.born_rmse,
                        "coverage": diagnostic.coverage,
                        "phi_harmonic_2": diagnostic.phi_harmonic_2,
                        "strong_born_candidate": strong,
                        "sector_count": metadata.sector_count,
                    }
                    rows.append(row)
                    samples[(family, mode, hz, sample.t)] = sample
    return rows, samples


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_resonance_maps(rows, path: Path) -> None:
    labels = {
        "case1_hz0": (r"Case 1: $h_{z0}$ sweep", r"$h_{z0}$"),
        "case2_hz": (r"Case 2: Ising $h_z$ sweep", r"$h_z$"),
        "case3_jpm": (r"Case 3: $J_{\pm}$ sweep", r"$J_{\pm}$"),
        "case4_jpm_hz": (r"Case 4: exchange $h_z$ sweep", r"$h_z$"),
    }
    colors = {"zero": "#3366cc", "matched": "#009e73", "detuned": "#d55e00", "sweep": "#7b3294"}
    figure, axes = plt.subplots(2, 2, figsize=(13.0, 8.5), constrained_layout=True)
    for ax, family in zip(axes.flat, labels):
        subset = [row for row in rows if row["family"] == family]
        for mode in dict.fromkeys(str(row["mode"]) for row in subset):
            mode_rows = [row for row in subset if row["mode"] == mode]
            x = [float(row["parameter_value"]) for row in mode_rows]
            y = [float(row["exact_resonant_weight_fraction"]) for row in mode_rows]
            ax.plot(x, y, "o-", color=colors[mode], markersize=3.2, linewidth=1.1, label=mode)
        unique = {}
        for row in subset:
            unique[float(row["parameter_value"])] = float(row["detector_degenerate_weight_fraction"])
        ax.plot(sorted(unique), [unique[x] for x in sorted(unique)], "k--", linewidth=1.15, label=r"$P_EVP_E$ weight")
        ax.set_title(labels[family][0])
        ax.set_xlabel(labels[family][1])
        ax.set_ylabel("active weight fraction")
        ax.set_ylim(-0.01, 1.01)
        ax.grid(alpha=0.22)
        ax.legend(fontsize=8, frameon=False)
    figure.suptitle(r"Basis-invariant active resonance weights, detector $N=8$", fontsize=15)
    figure.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def plot_case3(rows, path: Path) -> None:
    subset = [row for row in rows if row["family"] == "case3_jpm"]
    x = np.array([float(row["parameter_value"]) for row in subset])
    degenerate = np.array([float(row["detector_degenerate_weight_fraction"]) for row in subset])
    detuning = np.array([float(row["nearest_active_detuning"]) for row in subset])
    figure, axes = plt.subplots(1, 2, figsize=(12.0, 4.3), constrained_layout=True)
    axes[0].plot(x, degenerate, "o-", color="#7b3294")
    axes[0].axvline(1.0, color="black", linestyle="--", linewidth=1.0, label=r"$J_{\pm}=J$")
    axes[0].set(xlabel=r"$J_{\pm}$", ylabel=r"$\sum_E\|P_EVP_E\|_F^2/\mathrm{Tr}V^2$", ylim=(-0.01, 1.01))
    axes[0].legend(frameon=False)
    axes[1].semilogy(x, np.maximum(detuning, 1.0e-14), "s-", color="#d55e00")
    axes[1].axvline(1.0, color="black", linestyle="--", linewidth=1.0)
    axes[1].set(xlabel=r"$J_{\pm}$", ylabel="nearest active detuning to zero")
    for ax in axes:
        ax.grid(alpha=0.22)
    figure.suptitle(r"Case 3: exact degeneracy requires a nonzero collective-$X$ form factor", fontsize=14)
    figure.savefig(path, dpi=230, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def plot_invariance(invariance, path: Path) -> None:
    names = [str(row["family"]).replace("_", "\n") for row in invariance]
    errors = [max(float(row["maximum_relative_error"]), 1.0e-18) for row in invariance]
    figure, ax = plt.subplots(figsize=(9.0, 4.2), constrained_layout=True)
    ax.bar(names, errors, color="#3366cc", alpha=0.82)
    ax.axhline(1.0e-12, color="#d55e00", linestyle="--", label=r"$10^{-12}$ tolerance")
    ax.set_yscale("log")
    ax.set_ylabel("maximum relative projector-weight error")
    ax.set_title("Eight random basis rotations inside every degenerate eigenspace")
    ax.grid(axis="y", alpha=0.22)
    ax.legend(frameon=False)
    figure.savefig(path, dpi=230, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def plot_dynamics(rows, path: Path) -> None:
    colors = {"zero": "#3366cc", "matched": "#009e73", "detuned": "#d55e00"}
    families = ("case2_hz", "case4_jpm_hz")
    metrics = (("S_born", r"max $S_{Born}$"), ("coverage", "coverage at max score"), ("phi_harmonic_2", "harmonic at max score"))
    figure, axes = plt.subplots(2, 3, figsize=(14.0, 7.2), constrained_layout=True, sharex="row")
    for row_index, family in enumerate(families):
        subset = [row for row in rows if row["family"] == family]
        fields = sorted({float(row["hz"]) for row in subset})
        best = {}
        for mode in colors:
            for hz in fields:
                candidates = [row for row in subset if row["mode"] == mode and float(row["hz"]) == hz]
                best[(mode, hz)] = max(candidates, key=lambda item: float(item["S_born"]))
        for column, (metric, ylabel) in enumerate(metrics):
            ax = axes[row_index, column]
            for mode, color in colors.items():
                values = [float(best[(mode, hz)][metric]) for hz in fields]
                ax.plot(fields, values, "o-", color=color, label=mode, markersize=4)
            ax.set_xlabel(r"$h_z$")
            ax.set_ylabel(ylabel)
            ax.grid(alpha=0.22)
            if metric != "S_born":
                ax.set_ylim(-0.03, 1.03)
            if row_index == 0 and column == 0:
                ax.legend(frameon=False)
        axes[row_index, 0].text(0.02, 0.94, "Case 2" if row_index == 0 else "Case 4", transform=axes[row_index, 0].transAxes, va="top", fontweight="bold")
    figure.suptitle(r"Matched $h_{z0}=h_z$ does not by itself satisfy radial and azimuthal Born gates ($N=8$)", fontsize=14)
    figure.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def select_examples(rows):
    output = []
    for family in ("case2_hz", "case4_jpm_hz"):
        for mode in ("zero", "matched"):
            candidates = [row for row in rows if row["family"] == family and row["mode"] == mode]
            chosen = max(
                candidates,
                key=lambda row: float(row["S_born"]) + float(row["coverage"]) - float(row["phi_harmonic_2"]),
            )
            output.append(chosen)
    return output


def plot_atlas(rows, samples, path: Path) -> None:
    chosen = select_examples(rows)
    calculator = AngularDiagnosticCalculator(48)
    figure = plt.figure(figsize=(14.5, 9.0), constrained_layout=True)
    grid = figure.add_gridspec(3, 4, height_ratios=(1.0, 0.9, 1.25))
    for column, row in enumerate(chosen):
        key = (str(row["family"]), str(row["mode"]), float(row["hz"]), float(row["t"]))
        sample = samples[key]
        diagnostic = calculator.calculate(sample)
        ax = figure.add_subplot(grid[0, column])
        ax.stairs(diagnostic.p_theta, diagnostic.edges, color=BLUE, fill=True, alpha=0.18, label=r"$P(\theta)$")
        ax.stairs(diagnostic.p_reflected, diagnostic.edges, color=RED, fill=True, alpha=0.14, label=r"$P(\pi-\theta)$")
        ax.set_xlim(0.0, np.pi)
        ax.grid(alpha=0.18)
        title = ("Case 2" if row["family"] == "case2_hz" else "Case 4") + f", {row['mode']}\n" + rf"$h_z={float(row['hz']):g},\ h_{{z0}}={float(row['hz0']):g},\ t={float(row['t']):.0e}$"
        ax.set_title(title, fontsize=10)
        if column == 0:
            ax.set_ylabel("density")
            ax.legend(fontsize=7, frameon=False)
        ax = figure.add_subplot(grid[1, column])
        ax.plot(diagnostic.centers[diagnostic.occupied], diagnostic.ratio[diagnostic.occupied], "o-", color=RATIO, markersize=2.8, linewidth=0.9)
        ax.plot(diagnostic.centers, diagnostic.born_curve, "k--", linewidth=1.1)
        ax.set(xlim=(0.0, np.pi), ylim=(-0.04, 1.04), xlabel=r"$\theta$")
        ax.grid(alpha=0.18)
        ax.text(0.04, 0.08, rf"$S_B={diagnostic.born_score:.3f}$" + "\n" + rf"$A_2={diagnostic.phi_harmonic_2:.3f}$", transform=ax.transAxes, fontsize=8)
        if column == 0:
            ax.set_ylabel(r"$R(\theta)$")
        ax = figure.add_subplot(grid[2, column], projection="3d")
        branch0, branch1 = bloch_branches(sample.eigenvalues)
        wire_sphere(ax)
        ax.scatter(branch0[:, 0], branch0[:, 1], branch0[:, 2], s=5, color=BLUE, alpha=0.4, depthshade=False)
        ax.scatter(branch1[:, 0], branch1[:, 1], branch1[:, 2], s=5, color=RED, alpha=0.3, depthshade=False)
        ax.set(xlim=(-1.04, 1.04), ylim=(-1.04, 1.04), zlim=(-1.04, 1.04))
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=22, azim=42)
        ax.set_axis_off()
    figure.suptitle(r"Best finite-$N$ zero/matched examples: radial agreement must be checked against Bloch mixing", fontsize=15)
    figure.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def summarize(detector_rows_data, invariance, dynamics):
    family_summary = {}
    for family in ("case1_hz0", "case2_hz", "case3_jpm", "case4_jpm_hz"):
        subset = [row for row in detector_rows_data if row["family"] == family]
        family_summary[family] = {
            "maximum_detector_degenerate_weight_fraction": max(float(row["detector_degenerate_weight_fraction"]) for row in subset),
            "parameters_with_active_detector_degeneracy": sorted({float(row["parameter_value"]) for row in subset if float(row["detector_degenerate_weight_fraction"]) > 1.0e-12}),
        }
    dynamics_summary = {}
    for family in ("case2_hz", "case4_jpm_hz"):
        dynamics_summary[family] = {}
        for mode in ("zero", "matched", "detuned"):
            subset = [row for row in dynamics if row["family"] == family and row["mode"] == mode]
            best = max(subset, key=lambda row: float(row["S_born"]))
            dynamics_summary[family][mode] = {
                "best": best,
                "strong_born_candidate_count": sum(bool(row["strong_born_candidate"]) for row in subset),
            }
    return {
        "detector_n": int(detector_rows_data[0]["detector_n"]),
        "detector_families": family_summary,
        "basis_invariance": invariance,
        "dynamics": dynamics_summary,
        "strong_born_definition": "S_born >= 0.75, coverage >= 0.50, phi_harmonic_2 <= 0.25",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("reports/detector_resonance_analysis_2026-07-17"))
    parser.add_argument("--N", type=int, default=8, dest="detector_n")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    figure_dir = args.out / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    detector_data, invariance = detector_rows(args.detector_n)
    write_csv(args.out / "detector_resonance_metrics.csv", detector_data)
    write_csv(args.out / "basis_invariance.csv", invariance)
    plot_resonance_maps(detector_data, figure_dir / "active_resonance_maps.png")
    plot_case3(detector_data, figure_dir / "case3_degenerate_coupling.png")
    plot_invariance(invariance, figure_dir / "basis_invariance.png")

    dynamics, samples = dynamics_rows(args.detector_n)
    write_csv(args.out / "matched_unmatched_dynamics.csv", dynamics)
    plot_dynamics(dynamics, figure_dir / "matched_unmatched_born.png")
    plot_atlas(dynamics, samples, figure_dir / "matched_unmatched_atlas.png")
    result = summarize(detector_data, invariance, dynamics)
    (args.out / "summary.json").write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
