"""Regenerate figures and a combined machine-readable analysis from saved runs."""
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

from collapse.born import born_ratio_from_radii
from collapse.resonant_study import folded_wrapped_gaussian, wrapped_variance
from collapse.level_spacing import poisson_spacing_distribution, wigner_spacing_distribution, compute_unfolded_spacings


def records_from(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def numeric(row: dict, name: str) -> float:
    return float(row[name])


def raw_files(case_dir: Path) -> list[Path]:
    return sorted(case_dir.glob("raw_*.npz"), key=lambda item: float(item.stem.split("_t")[-1]))


def density(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    counts, _ = np.histogram(values, bins=edges)
    return counts / max(values.size, 1) / np.diff(edges)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--broad", required=True, type=Path)
    parser.add_argument("--focused", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--principal-n", type=int, default=9)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    broad = records_from(args.broad / "summary.csv")
    focused = records_from(args.focused / "summary.csv")

    # Broad finite-size comparison: use theory variance (physics prediction),
    # Born discrepancy, and azimuthal resultant (zero is uniform).
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.5), constrained_layout=True)
    for n in (4, 6, 8):
        rows = sorted((r for r in broad if int(r["N"]) == n), key=lambda r: numeric(r, "hz"))
        hz = [numeric(r, "hz") for r in rows]
        axes[0].plot(hz, [numeric(r, "theory_variance_median") for r in rows], "o-", label=f"N={n}")
        axes[1].plot(hz, [numeric(r, "born_rmse") for r in rows], "o-", label=f"N={n}")
        axes[2].plot(hz, [numeric(r, "phi_resultant") for r in rows], "o-", label=f"N={n}")
    for ax, title, ylabel in zip(axes, ("Wrapped-Gaussian prediction", "Born-profile discrepancy", "Azimuth concentration"), (r"median $\sigma^2_{ZZ}(t)$", "pooled RMSE", r"$|\langle e^{i\phi}\rangle|$")):
        for resonance in (-2, 0, 2): ax.axvline(resonance, color="0.75", ls="--", lw=1)
        ax.set(title=title, xlabel=r"$h_z$", ylabel=ylabel)
        ax.legend(fontsize=8)
    fig.savefig(args.out / "broad_scan_summary.png", dpi=220)
    plt.close(fig)

    principal = args.principal_n
    principal_dir = args.focused / f"N{principal:02d}"
    # Principal comparison at the final saved time, without pooling times.
    final_time = 100.0
    hz_values = (-2.0, 0.0, 2.0)
    theta_edges = np.linspace(0, np.pi, 41)
    centers = (theta_edges[1:] + theta_edges[:-1]) / 2
    fig, axes = plt.subplots(3, 3, figsize=(12, 9), constrained_layout=True)
    derived_rows = []
    for col, hz in enumerate(hz_values):
        case = principal_dir / f"hz_{hz:+.3f}"
        selected = min(raw_files(case), key=lambda p: abs(float(p.stem.split("_t")[-1]) - final_time))
        raw = np.load(selected)
        theta, phi, eig = raw["theta"], raw["phi"], raw["eigenvalues"]
        p_theta = density(theta, theta_edges)
        p_ref = density(np.pi - theta, theta_edges)
        theory = folded_wrapped_gaussian(centers, float(raw["theory_variance"]))
        ratio = p_theta / np.maximum(p_theta + p_ref, 1e-300)
        born = np.cos(centers / 2) ** 2
        width = np.diff(theta_edges)
        axes[0, col].bar(centers-width*.24, p_theta, width=width*.48, alpha=.65, label=r"hist. $P(\theta)$")
        axes[0, col].bar(centers+width*.24, p_ref, width=width*.48, alpha=.65, label=r"hist. $P(\pi-\theta)$")
        axes[0, col].plot(centers, theory, "k--", label="fixed theory")
        axes[0, col].set(title=rf"$h_z={hz:g}$, $t={final_time:g}$", xlabel=r"$\theta$", ylabel="density / dθ")
        axes[0, col].legend(fontsize=7)
        axes[1, col].plot(centers, ratio, label="empirical R")
        axes[1, col].plot(centers, born, "k--", label="Born")
        axes[1, col].set(xlabel=r"$\theta$", ylabel=r"$R(\theta)$", ylim=(-.05, 1.05))
        axes[1, col].legend(fontsize=7)
        finite_phi = phi[np.isfinite(phi)]
        axes[2, col].hist(finite_phi, bins=24, density=True, alpha=.7)
        axes[2, col].axhline(1/(2*np.pi), color="k", ls="--")
        axes[2, col].set(xlabel=r"$\phi$", ylabel="density / dφ", xlim=(-np.pi, np.pi))
        norm = np.abs(eig)
        s_born = born_ratio_from_radii(norm[np.isfinite(norm)], n_theta=100).similarity
        derived_rows.append({"N": principal, "hz": hz, "t": final_time, "S_born": float(s_born), "theory_variance": float(raw["theory_variance"]), "fitted_variance": float(raw["fitted_variance"]), "fixed_theory_l1": float(np.sum(np.abs(p_theta-theory)*np.diff(theta_edges))), "born_rmse_time": float(np.sqrt(np.mean((ratio-born)**2))), "condition_number": float(raw["condition_number"]), "solve_residual": float(raw["solve_residual"]), "eigen_residual_max": float(raw["eigen_residual_max"]), "radius_max": float(np.nanmax(norm))})
    fig.savefig(args.out / f"N{principal}_principal_angular_born_phi.png", dpi=220)
    plt.close(fig)

    # Density-aware Bloch maps and full/detector spectra for the same cases.
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    for col, hz in enumerate(hz_values):
        case = principal_dir / f"hz_{hz:+.3f}"
        raw = np.load(min(raw_files(case), key=lambda p: abs(float(p.stem.split("_t")[-1]) - final_time)))
        theta, phi = raw["theta"], raw["phi"]
        finite = np.isfinite(phi)
        axes[0, col].hexbin(phi[finite], np.cos(theta[finite]), gridsize=28, mincnt=1, cmap="viridis")
        axes[0, col].set(title=rf"$h_z={hz:g}$", xlabel=r"Bloch azimuth $\phi$", ylabel=r"Bloch $z=\cos\theta$", xlim=(-np.pi,np.pi), ylim=(-1,1))
        aggregate = np.load(case / "aggregate.npz")
        detector, full = aggregate["detector_spectrum"], aggregate["full_spectrum"]
        axes[1, col].plot(np.sort(detector), np.arange(detector.size), label="detector", lw=1)
        axes[1, col].plot(np.sort(full), np.arange(full.size), label="full", lw=1)
        axes[1, col].set(xlabel="energy", ylabel="index")
        axes[1, col].legend(fontsize=7)
    fig.savefig(args.out / f"N{principal}_bloch_maps_and_spectra.png", dpi=220)
    plt.close(fig)

    # True 3-D Bloch-sphere distributions for every focused resonant and
    # nonresonant h_z value.  The fixed camera makes comparisons meaningful.
    controls = tuple(sorted(float(path.name.split('_')[-1]) for path in principal_dir.glob('hz_*')))
    fig = plt.figure(figsize=(14, 7), constrained_layout=True)
    for index, hz in enumerate(controls, start=1):
        ax = fig.add_subplot(2, 4, index, projection="3d")
        raw = np.load(min(raw_files(principal_dir / f"hz_{hz:+.3f}"), key=lambda p: abs(float(p.stem.split("_t")[-1]) - final_time)))
        finite = np.isfinite(raw["phi"])
        theta, phi = raw["theta"][finite], raw["phi"][finite]
        x, y, z = np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)
        ax.scatter(x, y, z, s=5, alpha=.55, c=z, cmap="coolwarm")
        u=np.linspace(0,2*np.pi,24); v=np.linspace(0,np.pi,12)
        ax.plot_wireframe(np.outer(np.cos(u),np.sin(v)),np.outer(np.sin(u),np.sin(v)),np.outer(np.ones_like(u),np.cos(v)),color="0.8",linewidth=.25)
        ax.set(title=rf"$h_z={hz:g}$",xlim=(-1,1),ylim=(-1,1),zlim=(-1,1)); ax.view_init(elev=22, azim=38); ax.set_axis_off()
    fig.savefig(args.out / f"N{principal}_3D_bloch_spheres_resonant_and_controls.png", dpi=220)
    plt.close(fig)

    # Requested long-time histogram evolution for all focused resonance and
    # nonresonance fields. Each panel is an actual P(theta) histogram.
    time_values = (100.0, 10_000.0, 100_000.0, 1_000_000.0)
    fig, axes = plt.subplots(len(time_values), len(controls), figsize=(17, 9), sharex=True, sharey=True, constrained_layout=True)
    for row, t_value in enumerate(time_values):
        for col, hz in enumerate(controls):
            files = raw_files(principal_dir / f"hz_{hz:+.3f}")
            raw = np.load(min(files, key=lambda p: abs(float(p.stem.split("_t")[-1])-t_value)))
            h = density(raw["theta"], theta_edges)
            axes[row,col].bar(centers, h, width=np.diff(theta_edges), color="#4c78a8", alpha=.8)
            if row == 0: axes[row,col].set_title(rf"$h_z={hz:g}$", fontsize=9)
            if col == 0: axes[row,col].set_ylabel(rf"$t={t_value:.0e}$\n$P(\theta)$", fontsize=8)
            axes[row,col].set_ylim(bottom=0)
    fig.savefig(args.out / f"N{principal}_long_time_Ptheta_histograms_resonant_and_controls.png", dpi=220)
    plt.close(fig)

    # Detector level-spacing plots: informative but deliberately labelled inconclusive.
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.3), constrained_layout=True)
    for ax, hz in zip(axes, hz_values):
        aggregate = np.load(principal_dir / f"hz_{hz:+.3f}" / "aggregate.npz")
        spacings = compute_unfolded_spacings(aggregate["detector_spectrum"], tol=1e-9, degree=3, trim_fraction=.1)
        spread = np.ptp(spacings) if spacings.size else 0.0
        scale = max(float(np.max(np.abs(spacings))) if spacings.size else 1.0, 1.0)
        if spacings.size and np.all(np.isfinite(spacings)) and spread > 1e-10 * scale:
            ax.hist(spacings, bins=20, density=True, alpha=.6, label="resolved levels")
            x = np.linspace(0, max(3, np.quantile(spacings,.99)), 300)
            ax.plot(x, poisson_spacing_distribution(x), "k--", label="Poisson")
            ax.plot(x, wigner_spacing_distribution(x, 1), label="GOE")
            ax.plot(x, wigner_spacing_distribution(x, 2), label="GUE")
        ax.set(title=rf"$h_z={hz:g}$ (sector-mixed)", xlabel="unfolded spacing", ylabel="density")
        if ax.get_legend_handles_labels()[0]: ax.legend(fontsize=7)
    fig.savefig(args.out / f"N{principal}_detector_level_spacings_inconclusive.png", dpi=220)
    plt.close(fig)

    with (args.out / "principal_time_analysis.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(derived_rows[0]))
        writer.writeheader(); writer.writerows(derived_rows)
    (args.out / "analysis_notes.json").write_text(json.dumps({"measure": "P(theta) is a density with respect to dtheta; all N=9 principal comparisons use one t=100 slice", "level_statistics": "Sector-mixed detector levels; shown only as an inconclusive diagnostic.", "theory_source": "reports/four_model_finite_time_eigenvalue_derivation_2026-07-10.md, Eq. 7.8"}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
