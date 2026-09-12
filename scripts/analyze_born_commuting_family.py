"""Certify and plot a broad finite Born-like family in the native X/XX model."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born_commuting_family import (
    certify_commuting_seed, conditional_qubit_angles, polar_gate_metrics,
)
from core.born_profile_export import write_table
from core.born_structure_plotting import save_figure
from core.detector_graphs import DetectorGraphSpec, detector_graph_edges


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def scalar_metrics(result: dict) -> dict:
    keys = ["coverage", "center_rms", "moment_max", "accepted", "whole_bin", "S_born_100"]
    return {key: result[key] for key in keys}


def save_diagnostic(path: Path, result: dict) -> None:
    counts, edges = result["counts"], result["edges"]
    widths = np.diff(edges)
    write_table(path, ["theta_rad", "bin_left", "bin_right", "P", "P_reflected",
                       "R", "Born", "residual", "occupied"], np.column_stack([
        result["centers"], edges[:-1], edges[1:], counts/counts.sum()/widths,
        result["reflected_counts"]/counts.sum()/widths,
        result["ratio"], result["target"], result["ratio"]-result["target"],
        counts+result["reflected_counts"] > 0,
    ]))


def plot_diagnostics(results: list[tuple[str, dict]], output: Path) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, len(results), figsize=(15, 6), squeeze=False)
    dense = np.linspace(0, np.pi, 2001)
    for col, (label, result) in enumerate(results):
        edges, counts = result["edges"], result["counts"]
        axes[0, col].stairs(counts/counts.sum()/np.diff(edges), edges/np.pi)
        axes[0, col].set(xlabel=r"$\theta/\pi$", ylabel=r"$P(\theta)$ / rad",
                         title=f"{label}\n100-bin S_born={result['S_born_100']:.4f}")
        axes[1, col].plot(dense/np.pi, np.cos(dense/2)**2, "k--", label="Born")
        axes[1, col].stairs(result["ratio"], edges/np.pi, label="64-bin R", baseline=None)
        axes[1, col].set(xlabel=r"$\theta/\pi$", ylabel="R", ylim=(-.03, 1.03),
                         title=f"coverage={result['coverage']:.3f}; gate={result['accepted']}")
        axes[1, col].legend(fontsize=8)
    fig.tight_layout()
    save_figure(fig, output / "diagnostics")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/born_commuting_family_2026-09-11.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    certificate = certify_commuting_seed(config)
    args.output.mkdir(parents=True, exist_ok=False)
    import matplotlib.pyplot as plt

    phases = config["phase_numerator"]*np.pi / (
        config["phase_denominator_factor"]*np.array(config["phase_divisors"]))
    radius = config["phase_l1_radius"]
    baseline_theta = conditional_qubit_angles(phases)
    baseline = polar_gate_metrics(baseline_theta)
    np.testing.assert_array_equal(baseline["counts"], certificate["exact_counts"])
    variants = [
        ("Certified family seed", baseline),
        ("Outside ball, still accepted", polar_gate_metrics(
            conditional_qubit_angles(phases*(199/198)))),
        ("Uncontracted phases", polar_gate_metrics(
            conditional_qubit_angles(phases*(100/99)))),
        ("Qubit detuning 2t hz0=5", polar_gate_metrics(
            conditional_qubit_angles(phases, longitudinal_phase=5))),
    ]
    plot_diagnostics(variants, args.output)
    for index, (_, result) in enumerate(variants):
        save_diagnostic(args.output / f"case_{index}_diagnostic.dat", result)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    axes[0].stairs(baseline["ratio"]-baseline["target"], baseline["edges"]/np.pi,
                   baseline=None)
    axes[0].set(xlabel=r"$\theta/\pi$", ylabel="R minus Born at bin center",
                title="Certified seed residual")
    n = np.arange(17)
    coefficients = np.array([2*np.mean(baseline["ratio"]*np.cos(m*baseline["centers"]))
                             for m in n])
    coefficients[0] /= 2
    axes[1].stem(n, coefficients, basefmt=" ")
    axes[1].set(xlabel="cosine order n", ylabel="R cosine coefficient",
                title="Midpoint cosine coefficients")
    axes[2].stem(np.arange(8), baseline["residuals"], basefmt=" ")
    for limit in [-.05, .05]:
        axes[2].axhline(limit, color="black", ls="--")
    axes[2].set(xlabel="moment relation m", ylabel=r"$2a_{2m+1}-a_{2m}-a_{2m+2}$",
                title="Raw-angle moment gate")
    fig.tight_layout()
    save_figure(fig, args.output / "residuals_and_harmonics")
    write_table(args.output / "harmonics.dat", ["n", "P_cosine_moment", "R_cosine_coefficient"],
                np.column_stack([n, baseline["moments"], coefficients]))

    rng = np.random.default_rng(config["seed"])
    samples = []
    for group in ["inside", "outside"]:
        for index in range(config[group+"_samples"]):
            direction = rng.normal(size=15)
            amplitude = (radius*rng.uniform() if group == "inside"
                         else 10**rng.uniform(-4, 1))
            delta = direction * amplitude / np.abs(direction).sum()
            theta = conditional_qubit_angles(
                phases+delta[:13], transverse_phase=delta[13],
                longitudinal_phase=delta[14],
            )
            result = polar_gate_metrics(theta)
            if group == "inside":
                np.testing.assert_array_equal(result["counts"], baseline["counts"])
                if not result["accepted"]:
                    raise ArithmeticError("a certified member failed the gate")
            # These native detector coefficients cancel analytically. Store
            # actual draws so this is a reproducible Hamiltonian ensemble.
            detector = dict(
                graph=["chain", "ring", "all_to_all"][index % 3],
                Jxx=float(rng.uniform(-2, 2)),
                X_fields=rng.uniform(-1, 1, size=13).tolist(),
            )
            samples.append(dict(group=group, index=index, l1=amplitude,
                                delta=delta.tolist(), detector=detector,
                                **scalar_metrics(result)))
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    all_rms = np.array([r["center_rms"] for r in samples])
    rms_bins = np.linspace(0, np.nanmax(all_rms)*1.05, 25)
    all_scores = np.array([r["S_born_100"] for r in samples])
    score_bins = np.linspace(all_scores.min()-.02, all_scores.max()+.02, 25)
    for group in ["inside", "outside"]:
        rows = [r for r in samples if r["group"] == group]
        rms = np.array([r["center_rms"] for r in rows])
        moment = np.array([r["moment_max"] for r in rows])
        axes[0].hist(rms[np.isfinite(rms)], bins=rms_bins, alpha=.65, label=group)
        axes[1].scatter(rms, moment, s=12, alpha=.6, label=group)
        axes[2].hist([r["S_born_100"] for r in rows], bins=score_bins, alpha=.65, label=group)
    axes[0].set(xlabel="64-bin R RMSE (full coverage only)", ylabel="number of draws")
    axes[1].set(xlabel="64-bin R RMSE", ylabel="maximum moment residual")
    axes[1].axvline(.05, color="black", ls="--")
    axes[1].axhline(.05, color="black", ls="--")
    axes[2].set(xlabel="canonical 100-bin S_born", ylabel="number of draws")
    for ax in axes:
        ax.legend()
    fig.suptitle("256 draws per ensemble; outside the certified ball need not fail the gate")
    fig.tight_layout()
    save_figure(fig, args.output / "ensemble_errors")

    perturbations = []
    scan = np.r_[0., np.geomspace(1e-6, 2., 48)]
    for kind in ["coupling", "timing", "longitudinal", "transverse", "output_axis"]:
        for value in scan:
            if kind == "coupling":
                changed = phases.copy()
                changed[0] += value
                theta = conditional_qubit_angles(changed)
            elif kind == "timing":
                theta = conditional_qubit_angles(phases*(1+value))
            elif kind == "output_axis":
                theta = np.arccos(np.clip(np.cos(value)*np.cos(baseline_theta), -1, 1))
            else:
                key = "longitudinal_phase" if kind == "longitudinal" else "transverse_phase"
                theta = conditional_qubit_angles(phases, **{key: value})
            perturbations.append(dict(kind=kind, value=float(value),
                                      **scalar_metrics(polar_gate_metrics(theta))))
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for kind in ["coupling", "timing", "longitudinal", "transverse", "output_axis"]:
        rows = [r for r in perturbations if r["kind"] == kind]
        x = [r["value"] for r in rows]
        for ax, field in zip(axes, ["center_rms", "moment_max", "S_born_100"]):
            ax.plot(x, [r[field] for r in rows], label=kind)
            ax.set_xscale("symlog", linthresh=1e-6)
            ax.set(xlabel="declared perturbation parameter", ylabel=field)
    for ax in axes[:2]:
        ax.axhline(.05, color="black", ls="--")
    axes[2].legend(fontsize=8)
    fig.suptitle("Coupling/qubit field: phase increment; timing: relative change; output axis: radians\nMissing-coverage RMS is undefined; detector X/XX changes cancel exactly")
    fig.tight_layout()
    save_figure(fig, args.output / "perturbations")

    family_members = []
    fig, axes = plt.subplots(3, 4, figsize=(14, 10))
    graph_specs = [(13, "chain", .17, .03), (13, "ring", .3, .11),
                   (13, "erdos_renyi", -.7, -.23), (15, "all_to_all", .12, .31)]
    for col, (size, kind, jxx, hx) in enumerate(graph_specs):
        spec = DetectorGraphSpec(kind=kind, seed=config["seed"]+col)
        edges = detector_graph_edges(size, spec)
        angle = 2*np.pi*np.arange(size)/size
        xy = np.column_stack([np.cos(angle), np.sin(angle)])
        for left, right in edges:
            axes[0, col].plot(xy[[left, right], 0], xy[[left, right], 1], color=".7", lw=.6)
        axes[0, col].scatter(*xy.T, s=16)
        axes[0, col].set(title=f"N={size}, {kind}\nJxx={jxx}, hx={hx}", aspect="equal")
        axes[0, col].axis("off")
        signs = 1-2*((np.arange(2**size)[:, None] >> np.arange(size)) & 1)
        detector_energies = -hx*signs.sum(axis=1).astype(float)
        for left, right in edges:
            detector_energies -= jxx*signs[:, left]*signs[:, right]
        axes[1, col].hist(detector_energies, bins=40, density=True)
        axes[1, col].set(xlabel="detector energy (hbar=1, t=1)",
                         ylabel="density", title="Exact commuting detector spectrum")
        steps = np.r_[phases, np.zeros(size-13)]
        result = polar_gate_metrics(conditional_qubit_angles(steps))
        np.testing.assert_allclose(result["ratio"], baseline["ratio"], rtol=0, atol=0)
        axes[2, col].stairs(result["ratio"], result["edges"]/np.pi, baseline=None)
        axes[2, col].plot(np.linspace(0, 1, 2001), np.cos(np.linspace(0, np.pi, 2001)/2)**2, "k--")
        axes[2, col].set(xlabel=r"$\theta/\pi$", ylabel="R",
                         title=f"S_born={result['S_born_100']:.4f}")
        family_members.append(dict(N=size, graph=kind, Jxx=jxx, hx=hx,
                                   graph_seed=spec.seed, edges=[list(e) for e in edges],
                                   phase_steps=steps.tolist(), **scalar_metrics(result)))
        write_table(args.output / f"graph_{col}_nodes.dat", ["id", "x", "y"],
                    np.column_stack([np.arange(size), xy]))
        write_table(args.output / f"graph_{col}_edges.dat", ["source", "target"], np.array(edges))
        write_table(args.output / f"graph_{col}_detector_energies.dat", ["energy"],
                    detector_energies[:, None])
    fig.suptitle("Native X/XX detector graphs: exact commuting cancellation, different detector dynamics\n13 active couplings; extra X spins duplicate the normalized root measure")
    fig.tight_layout()
    save_figure(fig, args.output / "distinct_detector_families")

    summary = dict(
        certificate=certificate, seed_metrics=scalar_metrics(baseline),
        representative_cases=[dict(label=label, **scalar_metrics(r)) for label, r in variants],
        family_members=family_members,
        ensembles={g: dict(count=sum(r["group"] == g for r in samples),
                           passed=sum(r["accepted"] for r in samples if r["group"] == g),
                           missing_coverage=sum(r["coverage"] < 1 for r in samples if r["group"] == g))
                   for g in ["inside", "outside"]},
        scope="Native commuting conditional blocks, exact count certificate; no continuum or production matrix run",
    )
    for name, payload in [("summary", summary), ("ensemble_samples", samples),
                          ("perturbation_samples", perturbations)]:
        (args.output / f"{name}.json").write_text(json.dumps(payload, indent=2)+"\n")
    sources = [Path(__file__), args.config, ROOT/"core/born_commuting_family.py",
               ROOT/"core/born.py", ROOT/"core/born_reciprocity.py",
               ROOT/"core/exact_born_limits.py", ROOT/"core/born_profile_export.py",
               ROOT/"core/detector_graphs.py", ROOT/"core/born_structure_plotting.py"]
    manifest = dict(
        created_utc=datetime.now(timezone.utc).isoformat(), config=config,
        python=platform.python_version(), numpy=np.__version__,
        defining_hashes={str(p.relative_to(ROOT)): digest(p) for p in sources},
        outputs={str(p.relative_to(args.output)): digest(p)
                 for p in sorted(args.output.iterdir()) if p.is_file()},
    )
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"certificate": certificate, "ensembles": summary["ensembles"],
                      "seed_metrics": summary["seed_metrics"]}, indent=2))


if __name__ == "__main__":
    main()
