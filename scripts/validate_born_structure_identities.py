"""Validate exact structural predictions against the reduced ring controls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.stats import wasserstein_distance

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born_structure_controls import control_sectors
from core.born_structure_identities import shifted_symmetric_phase_angles, charge_grading_check
from core.born_reciprocity import cosine_moments
from core.relative_evolution_study import angular_histogram
from core.born_structure_plotting import save_figure


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.controls / "manifest.json").read_text())
    for name, expected in manifest["outputs"].items():
        if digest(args.controls / name) != expected:
            raise ValueError("control output checksum mismatch")
    config = manifest["config"]
    args.output.mkdir(parents=True, exist_ok=False)
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    results = []
    for col, n in enumerate(config["detector_sizes"]):
        for t in config["times"]:
            base = np.load(args.controls / f"N{n}_baseline_t{t:g}" / "roots.npz")["theta"]
            actual = np.load(args.controls / f"N{n}_hx0_t{t:g}" / "roots.npz")["theta"]
            delta = -2 * config["baseline"]["jx"] * t
            predicted = shifted_symmetric_phase_angles(base, delta)
            expected_moments = cosine_moments(base, 16) * np.cos(np.arange(17) * delta)
            numerical_moments = cosine_moments(actual, 16)
            error = float(np.max(np.abs(expected_moments - numerical_moments)))
            transport = float(wasserstein_distance(actual, predicted))
            if error > 1e-7 or transport > 1e-7:
                raise ValueError("conditional phase-shift identity failed the long-time rounding tolerance")
            results.append(dict(N=n, time=t, moment_max_error=error, angle_Wasserstein=transport))
            if t == config["representative_time"]:
                hist = angular_histogram(actual, config["bins"])
                theory = angular_histogram(predicted, config["bins"])
                axes[0, col].plot(hist.centers / np.pi, hist.ratio, "o", markersize=3, label="full Hamiltonian")
                axes[0, col].plot(theory.centers / np.pi, theory.ratio, "-", label="phase-shift prediction")
                axes[0, col].plot(hist.centers / np.pi, hist.born, "--", color="0.5", label="Born")
                axes[0, col].set(title=f"N={n}, t={t:g}", xlabel=r"$\theta/\pi$", ylabel="R")
                axes[1, col].plot(range(17), numerical_moments - expected_moments, "o-")
                axes[1, col].set(xlabel="cosine moment n", ylabel="numerical minus predicted")
        for jy, shift in [(1, 2), (-1, -2)]:
            sectors = control_sectors({**config["baseline"], "jy": jy * config["baseline"]["jx"]}, n)
            for t in config["times"]:
                check = charge_grading_check(sectors, n, t, shift)
                if check["M_charge_error"] > 1e-6 or check["normalized_nilpotence_error"] > 1e-7:
                    raise ValueError("charge grading/nilpotence check failed")
                results.append(dict(N=n, time=t, Jy_over_Jx=jy, **check))
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Exact Hq mechanism: a field parallel to X shifts auxiliary phases\nPrediction uses the baseline spectrum; no fit parameters")
    fig.tight_layout(rect=(0, 0, 1, .92))
    save_figure(fig, args.output / "qubit_phase_shift_prediction")
    payload = dict(results=results, control_manifest_sha256=digest(args.controls / "manifest.json"),
                   tolerances=dict(moment=1e-7, angular_transport=1e-7, charge=1e-6, nilpotence=1e-7),
                   source_sha256={str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__), ROOT / "core/born_structure_identities.py"]})
    (args.output / "identity_checks.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
