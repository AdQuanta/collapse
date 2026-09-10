"""Exact large-N Hq perturbations reconstructed from conditional phase symmetry.

Requires hz0=Jy=hx0=0, X-only coupling and detector parity symmetry in the
recorded model. No new Hamiltonian diagonalization or random sampling.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born import born_ratio_from_theta
from core.born_reciprocity import reflection_diagnostics, response_cosine_coefficients
from core.born_structure_identities import shifted_symmetric_phase_angles
from core.born_structure_plotting import profile_grid, save_figure
from core.born_profile_export import load_profile, write_profile_tables
from core.relative_evolution_study import angular_histogram


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/born_qubit_phase_robustness_2026-09-10.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    rows, sources = [], []
    for case in config["cases"]:
        directory = ROOT / case["source"]
        marker = json.loads((directory / "COMPLETE.json").read_text())
        if marker["status"] != "complete":
            raise ValueError("incomplete source")
        for name, expected in marker["files"].items():
            path = directory / name
            if path.parent != directory or digest(path) != expected:
                raise ValueError("source checksum mismatch")
        metadata = json.loads((directory / "metadata.json").read_text())
        parameters = metadata["source"]
        if any(parameters.get(k, 0.) != 0 for k in ["hz0", "hx0", "jy", "hx", "jzx", "jz"]):
            raise ValueError("source does not satisfy the conditional-unitary/parity hypothesis")
        if metadata.get("hz0", 0.) != 0 or metadata.get("Jy_effective", 0.) != 0:
            raise ValueError("effective source fields violate the hypothesis")
        validation = json.loads((directory / "validation.json").read_text())
        if validation.get("passed") is not True:
            raise ValueError("failed source validation")
        source_metrics = json.loads((directory / "metrics.json").read_text())
        with np.load(directory / "results.npz") as archive:
            theta = np.array(archive["theta"])
        time = parameters["evolution_time"]
        if theta.size != 2**metadata["target_N"]:
            raise ValueError("unexpected root count")
        original = load_profile(directory / "results.npz")
        representatives = []
        for index, shift in enumerate(config["phase_shifts"]):
            predicted = shifted_symmetric_phase_angles(theta, shift)
            hist = angular_histogram(predicted, config["bins"])
            arrays = dict(edges=hist.edges, centers=hist.centers, P=hist.density,
                          P_reflected=hist.reflected_density, R=hist.ratio,
                          occupied=hist.occupied, Born=hist.born)
            coefficients = response_cosine_coefficients(arrays, 9)
            score = born_ratio_from_theta(predicted, np.pi - predicted, n_theta=100).similarity
            row = dict(case=case["key"], N=metadata["target_N"], time=time, phase_shift=shift,
                       hx0=-shift/(2*time), S_born=score, visibility=2*coefficients[1],
                       higher_odd_norm=float(np.linalg.norm(2*coefficients[3::2])),
                       **reflection_diagnostics(arrays))
            if shift == 0:
                np.testing.assert_allclose(arrays["P"], original["P"], atol=1e-11, rtol=0)
                np.testing.assert_allclose(score, source_metrics["S_born"], atol=1e-11, rtol=0)
            if abs(shift - np.pi/2) < 1e-14:
                np.testing.assert_allclose(hist.ratio[hist.occupied], .5, atol=1e-12, rtol=0)
            out = args.output / case["key"] / f"shift_{index:03d}"
            out.mkdir(parents=True)
            write_profile_tables(out, arrays)
            if any(abs(shift - value) < 1e-14 for value in config["representative_shifts"]):
                representatives.append(dict(**row, arrays=arrays, response_coefficients=coefficients,
                                            label=f"phase shift={shift:.3g}\n|hx0|={abs(row['hx0']):.3g}"))
            rows.append(row)
        profile_grid(representatives, args.output / (case["key"] + "_diagnostics"),
                     f"{case['label']}, N={metadata['target_N']}: exact conditional-phase reconstruction")
        sources.append(dict(source=case["source"], marker_sha256=digest(directory / "COMPLETE.json"),
                            archive_sha256=digest(directory / "results.npz"),
                            hypothesis="X-only; zero baseline Hq; parity-preserving detector; symmetric auxiliary phases"))
    with (args.output / "metrics.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True)
    for case in config["cases"]:
        subset = [r for r in rows if r["case"] == case["key"]]
        for ax, field in zip(axes, ["occupied_RMSE", "visibility", "higher_odd_norm", "coverage"]):
            ax.plot([abs(r["hx0"]) for r in subset], [r[field] for r in subset], ".-", label=case["label"])
    for ax, label in zip(axes, ["R RMSE", "Fundamental visibility", "Higher odd harmonic norm", "Reflection coverage"]):
        ax.set_ylabel(label)
        ax.grid(alpha=.2)
        ax.set_xscale("symlog", linthresh=1e-9)
    axes[0].legend(fontsize=8)
    axes[-1].set_xlabel(r"$|h_{x0}|$ [energy units], at $t=10^6$")
    fig.suptitle("Large-N Born robustness to a qubit field parallel to X\nReconstructed by an exact identity; no Hamiltonian refit or new diagonalization")
    fig.tight_layout(rect=(0, 0, 1, .94))
    save_figure(fig, args.output / "qubit_field_errors")
    paths = [Path(__file__), args.config, ROOT / "core/born_structure_identities.py", ROOT / "core/born_reciprocity.py",
             ROOT / "core/born_structure_plotting.py", ROOT / "core/relative_evolution_study.py", ROOT / "core/born.py"]
    manifest = dict(config=config, sources=sources,
                    source_sha256={str(p.resolve().relative_to(ROOT)):digest(p) for p in paths},
                    outputs={str(p.relative_to(args.output)):digest(p) for p in args.output.rglob("*") if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Completed {len(rows)} exact phase reconstructions: {args.output}")


if __name__ == "__main__":
    main()
