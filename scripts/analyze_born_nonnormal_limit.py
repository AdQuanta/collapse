"""Verify the native exchange/Gaussian root mismatch with exact sector weights."""

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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born import born_ratio_from_theta
from core.born_reciprocity import born_moment_residuals
from core.collective_exchange import (
    exchange_log_cutoff_audit, exchange_sector_blocks,
    gaussian_exchange_flip_probability, gaussian_exchange_root_potential,
)
from core.projective_potential import homogeneous_radial_potential
from core.projective_potential_plotting import plot_nonnormal_limit
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/"configs/born_nonnormal_limit_2026-09-12.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    if cfg["schema_version"] != 1:
        raise ValueError("only schema version 1 is supported")
    if max(cfg["qz_sizes"]) > 8 or max(cfg["sector_sizes"]) > 128:
        raise ValueError("this is a bounded local verification, not a production campaign")
    args.output.mkdir(parents=True, exist_ok=False)
    g, time = cfg["coupling"], cfg["time"]
    radii, cutoffs = np.array(cfg["log_radii"]), np.array(cfg["singular_cutoffs"])
    if not np.array_equal(radii, [-1., 0., 1.]):
        raise ValueError("the plotted cutoff audit uses the fixed radii -1,0,1")
    records = []
    for size in cfg["qz_sizes"]:
        for t in cfg["qz_times"]:
            max_angle, max_residual = 0., 0.
            qz_potential = np.zeros_like(radii)
            roots_count = 0
            for sector in exchange_sector_blocks(size, coupling=g, time=t):
                spectrum = generalized_relative_evolution_spectrum(sector.a, sector.c)
                if np.any(spectrum.indeterminate | spectrum.infinite):
                    raise ArithmeticError("QZ did not certify finite determined roots")
                weight = sector.multiplicity*(sector.two_j+1)/2**size
                qz_potential += weight*homogeneous_radial_potential(spectrum.alpha, spectrum.beta, radii)
                max_angle = max(max_angle, float(max(spectrum.theta)))
                max_residual = max(max_residual, spectrum.maximum_homogeneous_residual)
                roots_count += sector.multiplicity*(sector.two_j+1)
            if roots_count != 2**size or max_angle > cfg["qz_angle_tolerance"]:
                raise ArithmeticError("native exchange root identity failed")
            if max_residual > cfg["qz_residual_tolerance"]:
                raise ArithmeticError("native QZ residual exceeded tolerance")
            if np.max(abs(qz_potential-radii)) > 1e-12:
                raise ArithmeticError("QZ potential failed to preserve pole roots")
            # Every algebraic root is exactly zero; repeats do not alter diagnostics.
            polar = born_ratio_from_theta(np.zeros(1), np.full(1, np.pi), n_theta=64)
            occupied = polar.counts_0+polar.counts_1 > 0
            delta = polar.ratio[occupied]-polar.born[occupied]
            records.append(dict(size=size, time=t, root_count=roots_count,
                                maximum_angle=max_angle, qz_residual=max_residual,
                                potential=qz_potential.tolist(), coverage=float(np.mean(occupied)),
                                moment_residuals=born_moment_residuals(np.ones(17)).tolist(),
                                occupied_center_rmse=float(np.sqrt(np.mean(delta**2))),
                                occupied_center_maximum=float(np.max(abs(delta))),
                                global_rmse=None, global_epsilon_infinity=None,
                                S_born=born_ratio_from_theta(np.zeros(1), np.full(1, np.pi)).similarity))

    audits = [exchange_log_cutoff_audit(n, coupling=g, time=time, log_radii=radii,
                                       singular_cutoffs=cutoffs) for n in cfg["sector_sizes"]]
    clipped = np.stack([a["clipped_potential"] for a in audits])
    lost = np.stack([a["lost_log_integral"] for a in audits])
    flips = np.array([a["flip_probability"] for a in audits])
    x = np.linspace(cfg["profile_log_radius_min"], cfg["profile_log_radius_max"],
                    cfg["profile_log_radius_points"])
    gaussian_j, errors = gaussian_exchange_root_potential(
        x, coupling=g, time=time, tail_probability=cfg["quadrature_tail_probability"]
    )
    gaussian_flip = gaussian_exchange_flip_probability(coupling=g, time=time)
    np.savez_compressed(args.output/"potential_data.npz", sizes=cfg["sector_sizes"],
                        cutoffs=cutoffs, log_radii=radii, clipped_potential=clipped,
                        lost_log_integral=lost,
                        reference_lost=np.stack([a["reference_lost_log_integral"] for a in audits]),
                        below_cutoff_mass=np.stack([a["below_cutoff_mass"] for a in audits]),
                        flip_probability=flips, profile_x=x, gaussian_potential=gaussian_j,
                        gaussian_potential_error=errors, gaussian_flip=gaussian_flip)
    (args.output/"qz_snapshots.json").write_text(json.dumps(records, indent=2, allow_nan=False)+"\n")
    plot_nonnormal_limit(args.output, np.array(cfg["sector_sizes"]), cutoffs, clipped,
                         lost, flips, x, gaussian_j, gaussian_flip, coupling=g, time=time)
    sources = ["core/projective_potential.py", "core/collective_exchange.py",
               "core/projective_potential_plotting.py", "scripts/analyze_born_nonnormal_limit.py",
               "core/relative_evolution_pencil.py", "core/born.py", "core/born_reciprocity.py"]
    summary = dict(config=cfg, python=platform.python_version(), numpy=np.__version__,
                   scipy=scipy.__version__, created_utc=datetime.now(timezone.utc).isoformat(),
                   commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                   source_hashes={name:digest(ROOT/name) for name in sources},
                   config_sha256=digest(args.config), qz_snapshots=len(records),
                   max_qz_angle=max(r["maximum_angle"] for r in records),
                   max_qz_residual=max(r["qz_residual"] for r in records),
                   gaussian_flip=gaussian_flip, largest_size_flip=float(flips[-1]),
                   gaussian_first_root_moment=1-2*gaussian_flip,
                   native_first_root_moment=1.,
                   max_gaussian_potential_quadrature_error=float(max(errors)),
                   scope="Counterexample and limit criterion, not a full-model Born phase resolution",
                   outputs={p.name:digest(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    print(json.dumps({k:summary[k] for k in ["qz_snapshots", "max_qz_angle", "max_qz_residual",
                                           "gaussian_flip", "largest_size_flip"]}))


if __name__ == "__main__":
    main()
