"""Audit Gaussianization in the three completed fixed-detector field scans.

Reuse saved fits and bin-free moments; do not refit or rerun production.
Compare with the exact commuting-detector limit, explicitly labelled as such.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born_profile_export import write_table
from core.born_structure_plotting import save_figure
from core.commuting_detector_field import commuting_detector_angles
from core.distribution_fit import folded_wrapped_gaussian_bin_probabilities


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/finite_field_gaussian_audit_2026-09-11.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    audit = ROOT / config["audit"]
    manifest = json.loads((audit / "manifest.json").read_text())
    for name, expected in manifest["outputs"].items():
        if digest(audit / name) != expected:
            raise ValueError(f"audit output hash mismatch: {name}")
    with (audit / "case_metrics.csv").open() as stream:
        rows = [r for r in csv.DictReader(stream) if r["group"] in config["groups"]]
    ids = {r["id"] for r in rows}
    for case in manifest["cases"]:
        if case["id"] not in ids:
            continue
        source = ROOT / case["source"]
        checks = case["source_checks"]
        if digest(source / "COMPLETE.json") != checks["marker_sha256"]:
            raise ValueError("source marker changed")
        for name, expected in checks["files"].items():
            if digest(source / name) != expected:
                raise ValueError(f"source changed: {source / name}")
    args.output.mkdir(parents=True, exist_ok=False)
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(4, 3, figsize=(13, 11), sharex="col")
    fields = ["gaussian_sigma", "gaussian_moment_max", "occupied_RMSE", "coverage"]
    labels = [r"WG width $\sigma$ (rad)", r"max $|a_n-e^{-n^2\sigma^2/2}|$", "occupied R RMSE", "reflection coverage"]
    for col, group in enumerate(config["groups"]):
        cases = sorted([r for r in rows if r["group"] == group], key=lambda r: float(r["hz0_ratio"]))
        if len(cases) != config["expected_cases_per_group"]:
            raise ValueError("incomplete field scan")
        x = np.array([float(r["hz0_ratio"]) for r in cases])
        caution = np.array([r["conditioning_caution"] == "True" for r in cases])
        for ax, key, label in zip(axes[:, col], fields, labels):
            y = np.array([float(r[key]) for r in cases])
            ax.plot(x, y, "o-", ms=3, lw=1)
            ax.plot(x[caution], y[caution], "x", color="crimson", ms=7, label="conditioning caution")
            ax.set(ylabel=label, xscale="symlog")
            ax.set_xscale("symlog", linthresh=1e-4)
            ax.grid(alpha=.2)
        axes[0, col].set_title(group.replace("_scan", "").replace("_", " "))
        axes[3, col].set(xlabel=r"$h_{z0}/h_z$", ylim=(-.03, 1.04))
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Fixed-detector N=17 scans: Gaussian fit agreement versus Born agreement\nSaved fits; raw cosine moments n=1,...,16; red crosses flag source eigenvector condition > 1e8")
    fig.tight_layout(rect=(0, 0, 1, .94))
    save_figure(fig, args.output / "field_gaussian_audit")

    fig, axes = plt.subplots(3, len(config["representative_ratios"]), figsize=(12, 9))
    for col, ratio in enumerate(config["representative_ratios"]):
        row = next(r for r in rows if r["group"] == "nearest_scan" and np.isclose(float(r["hz0_ratio"]), ratio, atol=1e-12))
        profile = np.genfromtxt(audit / row["id"] / "profile.dat", names=True)
        moments = np.genfromtxt(audit / row["id"] / "P_moments.dat", names=True)
        edges = np.r_[profile["bin_left_rad"], profile["bin_right_rad"][-1]]
        sigma = float(row["gaussian_sigma"])
        gaussian = folded_wrapped_gaussian_bin_probabilities(edges, sigma) / np.diff(edges)
        axes[0, col].stairs(profile["P"], edges / np.pi, label="saved P")
        axes[0, col].plot(profile["theta_over_pi"], gaussian, "--", label="saved WG fit")
        axes[0, col].set(yscale="log", ylim=(1e-5, 10), ylabel=r"$P(\theta)$ / rad", title=rf"$h_{{z0}}/h_z={ratio:g}$")
        axes[1, col].plot(profile["theta_over_pi"], np.where(profile["occupied"], profile["R"], np.nan), "o-", ms=2, label="saved R")
        axes[1, col].plot(profile["theta_over_pi"], profile["Born"], "--", color="black", label="Born")
        axes[1, col].set(xlabel=r"$\theta/\pi$", ylabel="R", ylim=(-.03, 1.03))
        n = moments["n"]
        predicted = np.exp(-.5 * (n * sigma)**2)
        axes[2, col].plot(n, moments["a_n"], "o-", ms=3, label="raw moments")
        axes[2, col].plot(n, predicted, "--", label="WG prediction")
        axes[2, col].set(xlabel="cosine order n", ylabel=r"$a_n=\langle\cos n\theta\rangle$")
        write_table(args.output / f"{row['id']}_gaussian_profile.dat",
                    ["theta_rad", "P", "WG", "R", "Born", "occupied"],
                    [profile["theta_rad"], profile["P"], gaussian, profile["R"], profile["Born"], profile["occupied"]])
        write_table(args.output / f"{row['id']}_gaussian_moments.dat",
                    ["n", "a_n", "WG_prediction", "residual"],
                    [n, moments["a_n"], predicted, moments["a_n"] - predicted])
    axes[0, 0].legend(fontsize=8)
    axes[1, 0].legend(fontsize=8)
    axes[2, 0].legend(fontsize=8)
    fig.suptitle("Nearest-neighbor ring: a more Gaussian core, with non-Gaussian tails remaining\nSaved spectra and fits; shared density display range 1e-5 to 10 per radian")
    fig.tight_layout(rect=(0, 0, 1, .94))
    save_figure(fig, args.output / "gaussian_representatives")

    v = np.linspace(0, config["commuting_v_max"], config["commuting_grid_points"])
    fig, ax = plt.subplots(figsize=(8, 5))
    for field in config["commuting_fields"]:
        theta = commuting_detector_angles(v, hz0=field, time=config["commuting_time"])
        ax.plot(v, theta / np.pi, label=rf"$h_{{z0}}={field:g}$")
        write_table(args.output / f"commuting_field_{field:g}.dat", ["v", "theta_rad"], [v, theta])
    ax.set(xlabel="coupling eigenvalue |v|", ylabel=r"$\theta/\pi$", ylim=(-.02, 1.03),
           title=f"Exact commuting-detector limit at t={config['commuting_time']:g}\nFinite field removes the tangent poles; it does not fix the density")
    ax.legend()
    fig.tight_layout()
    save_figure(fig, args.output / "commuting_field_regularization")
    with (args.output / "field_metrics.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), config=config,
                   python=platform.python_version(), numpy=np.__version__,
                   git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                   audit_manifest_sha256=digest(audit / "manifest.json"), source_cases_checked=len(ids),
                   source_sha256={str(p.relative_to(ROOT)): digest(p) for p in [Path(__file__), args.config, ROOT / "core/commuting_detector_field.py", ROOT / "core/distribution_fit.py", ROOT / "core/born_profile_export.py", ROOT / "core/born_structure_plotting.py"]},
                   outputs={str(p.relative_to(args.output)): digest(p) for p in sorted(args.output.rglob("*")) if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(dict(output=str(args.output), source_cases_checked=len(ids), outputs=len(payload["outputs"]))))


if __name__ == "__main__":
    main()
