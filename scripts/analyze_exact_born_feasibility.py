"""Validate finite-output no-go bounds and diagnose azimuthal false positives."""

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

from core.born_profile_export import write_table
from core.born_structure_plotting import save_figure
from core.exact_born_limits import (
    circular_count_harmonics, histogram_born_errors,
    minimum_uniform_histogram_tv, uniform_bin_born_limits,
)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/exact_born_feasibility_2026-09-11.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    audit = ROOT / config["audit"]
    manifest = json.loads((audit / "manifest.json").read_text())
    cases = {c["id"]: c for c in manifest["cases"]}
    args.output.mkdir(parents=True, exist_ok=False)
    import matplotlib.pyplot as plt

    sizes = config["bin_counts"]
    bounds = [uniform_bin_born_limits(b) for b in sizes]
    write_table(args.output / "step_function_bounds.dat", ["bins", "minimum_supremum", "minimum_rms"],
                np.column_stack([sizes, [b["supremum"] for b in bounds], [b["rms"] for b in bounds]]))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for field in ("supremum", "rms"):
        axes[0].loglog(sizes, [b[field] for b in bounds], "o-", label=field)
    axes[0].set(xlabel="number of theta bins", ylabel="best attainable whole-interval error", title="No finite-bin step function is exactly Born")
    axes[0].legend()
    axes[0].grid(alpha=.2)

    phase_fig, phase_axes = plt.subplots(2, len(config["case_ids"]), figsize=(14, 7), squeeze=False)
    results, source_hashes = [], {}
    for col, ident in enumerate(config["case_ids"]):
        case = cases[ident]
        source = ROOT / case["source"]
        checks = case["source_checks"]
        if digest(source / "COMPLETE.json") != checks["marker_sha256"]:
            raise ValueError("source marker changed")
        for name, expected in checks["files"].items():
            if digest(source / name) != expected:
                raise ValueError("source file hash mismatch")
        archive = source / ("activation_resolved_results.npz" if (source / "activation_resolved_results.npz").exists() else "results.npz")
        with np.load(archive, allow_pickle=False) as data:
            theta, roots = data["theta"], data["eigenvalues"]
        profile_path = audit / ident / "profile.dat"
        if digest(profile_path) != manifest["outputs"][f"{ident}/profile.dat"]:
            raise ValueError("profile changed")
        profile = np.genfromtxt(profile_path, names=True)
        edges = np.r_[profile["bin_left_rad"], profile["bin_right_rad"][-1]]
        ratio = np.where(profile["occupied"], profile["R"], np.nan)
        errors = histogram_born_errors(edges, ratio)
        mask = np.sin(theta) > config["minimum_polar_sine"]
        phi = np.mod(np.angle(roots[mask]), 2*np.pi)
        if not phi.size:
            raise ValueError("no nonpolar azimuths")
        pooled = np.r_[phi, np.mod(phi + np.pi, 2*np.pi)]
        harmonics = circular_count_harmonics(pooled, config["phi_harmonic_order"])
        phi_edges = np.linspace(0, 2*np.pi, config["phi_bins"] + 1)
        counts, _ = np.histogram(pooled, phi_edges)
        probabilities = counts / counts.sum()
        phase_axes[0, col].stairs(probabilities / np.diff(phi_edges), phi_edges / np.pi)
        phase_axes[0, col].axhline(1/(2*np.pi), color="black", ls="--")
        phase_axes[0, col].set(title=config["case_labels"][ident], xlabel=r"$\phi/\pi$", ylabel="azimuth density / rad")
        phase_axes[1, col].stem(np.arange(1, 17), abs(harmonics[1:17]), basefmt=" ")
        phase_axes[1, col].set(xlabel="azimuth harmonic m", ylabel=r"$|\langle e^{im\phi}\rangle|$", ylim=(-.03, 1.03))
        write_table(args.output / f"{ident}_phi_harmonics.dat", ["m", "real", "imag", "absolute"],
                    np.column_stack([np.arange(len(harmonics)), harmonics.real, harmonics.imag, abs(harmonics)]))
        write_table(args.output / f"{ident}_phi_histogram.dat", ["phi_left", "phi_right", "probability"],
                    np.column_stack([phi_edges[:-1], phi_edges[1:], probabilities]))
        results.append(dict(id=ident, roots=len(roots), phi_retained_roots=len(phi),
                            phi_removed_polar_fraction=float(1-np.mean(mask)),
                            whole_bin_errors=errors,
                            center_supremum=float(np.nanmax(abs(ratio-profile["Born"]))),
                            center_rms=float(np.sqrt(np.nanmean((ratio-profile["Born"])**2))),
                            phi_histogram_TV=float(.5*np.sum(abs(probabilities-1/config["phi_bins"]))),
                            first_phi_harmonic=float(abs(harmonics[1])), second_phi_harmonic=float(abs(harmonics[2])),
                            exact_atomic_circle_TV_to_Haar=1,
                            exact_strong_error_max_weak_sup_and_circle_TV=1,
                            circle_TV_status="analytical: finite support has Haar measure zero",
                            count_TV_lower_bound=minimum_uniform_histogram_tv(len(pooled), config["phi_bins"])))
        source_hashes[str(archive.relative_to(ROOT))] = digest(archive)
        source_hashes[str(profile_path.relative_to(ROOT))] = digest(profile_path)
        if ident == "case_082":
            axes[1].stairs(ratio, edges / np.pi, label="saved 64-bin R")
            dense = np.linspace(0, np.pi, 2001)
            axes[1].plot(dense / np.pi, np.cos(dense/2)**2, "--", label="Born")
            axes[1].set(xlabel=r"$\theta/\pi$", ylabel="R", title=f"Best reviewed ring: whole-bin sup error {errors['supremum']:.4f}")
            axes[1].legend()
            joint, theta_edges, azimuth_edges = np.histogram2d(
                np.r_[theta[mask], np.pi-theta[mask]], pooled,
                bins=[np.linspace(0, np.pi, 33), phi_edges])
            conditional = np.divide(joint, joint.sum(axis=1, keepdims=True), out=np.full_like(joint, np.nan), where=joint.sum(axis=1, keepdims=True)>0)
            joint_fig, ax = plt.subplots(figsize=(8, 5))
            mesh = ax.pcolormesh(theta_edges/np.pi, azimuth_edges/np.pi, conditional.T / np.diff(phi_edges)[:, None], shading="flat")
            ax.set(xlabel=r"$\theta/\pi$", ylabel=r"$\phi/\pi$", title="N=17 high-Born ring: pooled conditional azimuth density\nFinite-bin visualization; nonpolar roots only")
            joint_fig.colorbar(mesh, ax=ax, label="conditional density / rad")
            joint_fig.tight_layout()
            save_figure(joint_fig, args.output / "conditional_phi")
    fig.tight_layout()
    save_figure(fig, args.output / "finite_theta_limits")
    phase_fig.suptitle("Native root azimuths: antipodal pooling can hide anisotropy from the first harmonic\nDeclared polar cut applied; exact continuous TV remains 1 for every finite cloud")
    phase_fig.tight_layout(rect=(0, 0, 1, .9))
    save_figure(phase_fig, args.output / "native_phi_diagnostics")

    count = config["adversarial_phase_count"]
    phases = 2*np.pi*(np.arange(count)+.5)/count
    moments = circular_count_harmonics(phases, 2*count)
    hist, e = np.histogram(phases, np.linspace(0, 2*np.pi, count+1))
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].stairs(hist / count / np.diff(e), e/np.pi)
    ax[0].set(xlabel=r"$\phi/\pi$", ylabel="binned density / rad", title="Exactly flat 32-bin histogram")
    ax[1].stem(range(1, len(moments)), abs(moments[1:]), basefmt=" ")
    ax[1].set(xlabel="harmonic m", ylabel="amplitude", title="First 31 modes vanish, but mode 32 equals 1")
    fig.suptitle("Adversarial finite phase array: not continuous uniformity or a native Hamiltonian claim")
    fig.tight_layout(rect=(0, 0, 1, .9))
    save_figure(fig, args.output / "false_uniformity_certificate")
    write_table(args.output / "adversarial_phi_harmonics.dat", ["m", "absolute"], np.column_stack([np.arange(len(moments)), abs(moments)]))
    summary = dict(cases=results, limits=[dict(bins=b, **v) for b, v in zip(sizes, bounds)],
                   finite_circle_TV_theorem=1,
                   scope="Finite model preserved. No continuum or ensemble averaging introduced.")
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    sources = [Path(__file__), args.config, ROOT / "core/exact_born_limits.py", ROOT / "core/born_profile_export.py", ROOT / "core/born_structure_plotting.py"]
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), config=config,
                   python=platform.python_version(), numpy=np.__version__,
                   audit_manifest_sha256=digest(audit / "manifest.json"), input_hashes=source_hashes,
                   defining_hashes={str(p.relative_to(ROOT)): digest(p) for p in sources},
                   outputs={str(p.relative_to(args.output)): digest(p) for p in sorted(args.output.rglob("*")) if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
