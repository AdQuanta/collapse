"""Bounded verification of the commuting-vector detuning no-go theorem."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import scipy
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born import born_ratio_from_theta
from core.born_reciprocity import born_moment_residuals
from core.commuting_vector_field import (
    gaussian_resonance_coefficient, gaussian_resonant_cap, vector_field_column,
)
from core.commuting_vector_field_plotting import plot_resonant_caps
from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/born_detuning_interval_2026-09-12.json")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    if cfg["schema_version"] != 1 or max(cfg["qz_sizes"]) > 5:
        raise ValueError("requires schema 1 and a reduced native QZ check")
    args.output.mkdir(parents=True, exist_ok=False)
    g, h, c = [cfg[k] for k in ["transverse_slope", "transverse_offset",
                               "longitudinal_slope"]]
    eps = np.logspace(cfg["epsilon_log10_min"], cfg["epsilon_log10_max"],
                      cfg["epsilon_points"])
    caps, coefficients, errors, records = [], [], [], []
    for b in cfg["detunings"]:
        params = dict(transverse_slope=g, transverse_offset=h,
                      longitudinal_slope=c, detuning=b)
        values = [gaussian_resonant_cap(**params, epsilon=e) for e in eps]
        caps.append([v[0] for v in values])
        errors.extend(v[1] for v in values)
        coefficients.append(gaussian_resonance_coefficient(**params))
        for size in cfg["qz_sizes"]:
            matrix = SinglePixelHamiltonianNumpy(
                N_pixel=size, J=0., Jx=g / np.sqrt(size),
                Jzx=c / np.sqrt(size), hx=cfg["detector_x_field"], hz=0.,
                hx0=h, hz0=b, central_coupling="all",
            ).generate()
            d = 2**size
            s = np.array([size - 2 * n.bit_count() for n in range(d)]) / np.sqrt(size)
            for time in cfg["qz_times"]:
                unitary = expm(-1j * time * matrix)
                roots = generalized_relative_evolution_spectrum(
                    unitary[:d, :d], unitary[d:, :d],
                )
                if np.any(roots.indeterminate):
                    raise ArithmeticError("indeterminate native root")
                a, cc = vector_field_column(h + g * s, b + c * s, time=time)
                expected = 2 * np.arctan2(abs(cc), abs(a))
                error = float(max(abs(np.sort(roots.theta) - np.sort(expected))))
                if error > 1e-10 or roots.maximum_homogeneous_residual > 1e-11:
                    raise ArithmeticError("native QZ verification failed")
                polar = born_ratio_from_theta(roots.theta, np.pi - roots.theta, n_theta=64)
                occupied = polar.counts_0 + polar.counts_1 > 0
                delta = polar.ratio[occupied] - polar.born[occupied]
                moments = np.cos(np.outer(roots.theta, np.arange(17))).mean(axis=0)
                records.append(dict(
                    size=size, time=time, detuning=b, angle_error=error,
                    qz_residual=roots.maximum_homogeneous_residual,
                    coverage=float(np.mean(occupied)),
                    moments=moments.tolist(),
                    moment_residuals=born_moment_residuals(moments).tolist(),
                    occupied_rmse=float(np.sqrt(np.mean(delta**2))),
                    occupied_epsilon_infinity=float(max(abs(delta))),
                    global_rmse=None, global_epsilon_infinity=None,
                    S_born=born_ratio_from_theta(roots.theta, np.pi - roots.theta).similarity,
                ))
    caps, coefficients = np.array(caps), np.array(coefficients)
    np.savez_compressed(args.output / "caps.npz", epsilon=eps, caps=caps,
                        coefficients=coefficients, detunings=cfg["detunings"])
    (args.output / "qz_snapshots.json").write_text(json.dumps(records, indent=2) + "\n")
    plot_resonant_caps(args.output, eps, cfg["detunings"], caps, coefficients,
                       g=g, h=h, c=c)
    sources = ["core/commuting_vector_field.py", "core/commuting_vector_field_plotting.py",
               "scripts/analyze_born_detuning_interval.py",
               "core/hamiltonians/numpy_hamiltonians.py", "core/relative_evolution_pencil.py",
               "core/born.py", "core/born_reciprocity.py"]
    summary = dict(
        config=cfg, config_sha256=digest(args.config), python=platform.python_version(),
        numpy=np.__version__, scipy=scipy.__version__,
        created_utc=datetime.now(timezone.utc).isoformat(),
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        source_hashes={name: digest(ROOT / name) for name in sources},
        qz_snapshots=len(records), max_angle_error=max(r["angle_error"] for r in records),
        max_qz_residual=max(r["qz_residual"] for r in records),
        coverage_range=[min(r["coverage"] for r in records), max(r["coverage"] for r in records)],
        resonance_coefficients=coefficients.tolist(),
        smallest_cap_ratios=(caps[:, 0] / eps[0]).tolist(),
        max_cap_quadrature_error=max(errors),
        outputs={p.name: digest(p) for p in sorted(args.output.iterdir()) if p.is_file()},
        scope="Commuting detector-field no-go; the full native objective remains open",
    )
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: summary[k] for k in ["qz_snapshots", "max_angle_error",
                                            "max_qz_residual", "resonance_coefficients",
                                            "smallest_cap_ratios"]}))


if __name__ == "__main__":
    main()
