"""Reduced native QZ verification of scoped asymptotic Born obstructions."""

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
from scipy.linalg import eigh

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.analysis import evolution_subblocks_from_eigenbasis
from core.born import born_ratio_from_theta
from core.born_asymptotic import (
    collective_cosine_moments, conditional_phase_traces,
    field_interval_first_residual, gaussian_limit_density, shifted_cosine_moments,
)
from core.born_asymptotic_plotting import plot_asymptotic_audit
from core.born_reciprocity import born_moment_residuals, cosine_moments
from core.exact_born_limits import histogram_born_errors
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum


def digest(path: Path) -> str:
    """Hash an input or output file for reproducibility."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/"configs/born_asymptotic_2026-09-11.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if config["schema_version"] != 1 or config["detector_sizes"] != [3, 4, 5]:
        raise ValueError("this local verification protocol requires schema 1 and N=3,4,5")
    args.output.mkdir(parents=True, exist_ok=False)
    records, field_means = [], []
    root_arrays = {}
    order, bins = config["moment_order"], config["bins"]
    edges = np.linspace(0, np.pi, bins+1)
    for index, seed in enumerate(config["seeds"]):
        rng = np.random.default_rng(seed)
        j, jpm, jxx, hx, hz, g = rng.uniform(*config["random_parameter_range"], 6)
        graph = config["graphs"][index % len(config["graphs"])]
        for size in config["detector_sizes"]:
            params = dict(N_pixel=size, J=j, Jpm=jpm, Jxx=jxx,
                          Jx=g/np.sqrt(size), hx=hx, hz=hz,
                          hx0=0., hz0=0., connectivity=graph,
                          central_coupling="all", use_symmetry=False)
            baseline = SinglePixelHamiltonianQuSpin(**params).generate()
            d = 2**size
            k, v = baseline[:d, :d], -baseline[d:, :d]
            traces = {t: conditional_phase_traces(k, v, t, order) for t in config["times"]}
            if size == 5:
                for t in config["times"]:
                    mean = field_interval_first_residual(
                        traces[t], time=t, center=0., width=config["field_interval_width"]
                    )
                    field_means.append([seed, t, mean])
            cases = [(field, False) for field in config["transverse_fields"]]
            # One symmetry-breaking control per native baseline.
            cases.append((0., True))
            for field, control in cases:
                effective = dict(params, hx0=field, hz0=(
                    config["control_longitudinal_field"] if control else 0.
                ))
                h = SinglePixelHamiltonianQuSpin(**effective).generate()
                energy, vectors = eigh(h)
                for t in config["times"]:
                    a, c = evolution_subblocks_from_eigenbasis(energy, vectors, t)
                    spectrum = generalized_relative_evolution_spectrum(a, c)
                    if np.any(spectrum.indeterminate):
                        raise ArithmeticError("indeterminate pencil in reduced verification")
                    moments = cosine_moments(spectrum.theta, order)
                    residuals = born_moment_residuals(moments)
                    prediction = shifted_cosine_moments(traces[t], field=field, time=t)
                    error = float(np.max(np.abs(moments-prediction)))
                    if spectrum.maximum_homogeneous_residual > config["qz_residual_tolerance"]:
                        raise ArithmeticError("QZ backward residual exceeded tolerance")
                    if not control and error > config["trace_agreement_tolerance"]:
                        raise ArithmeticError("conditional trace identity failed")
                    polar = born_ratio_from_theta(spectrum.theta, np.pi-spectrum.theta,
                                                 n_theta=bins, empty_value=np.nan)
                    occupied = polar.counts_0+polar.counts_1 > 0
                    delta = polar.ratio[occupied]-polar.born[occupied]
                    whole = histogram_born_errors(edges, polar.ratio)
                    canonical = born_ratio_from_theta(spectrum.theta, np.pi-spectrum.theta)
                    key = f"case_{len(records):04d}"
                    root_arrays[key] = spectrum.theta
                    records.append(dict(
                        key=key, seed=seed, size=size, graph=graph, field=field,
                        time=t, control=control, effective_parameters=effective,
                        moments=moments.tolist(), moment_residuals=residuals.tolist(),
                        d0=float(residuals[0]), moment_max=float(np.max(np.abs(residuals))),
                        trace_error=error, qz_residual=spectrum.maximum_homogeneous_residual,
                        infinite_roots=int(np.count_nonzero(spectrum.infinite)),
                        coverage=float(np.mean(occupied)),
                        rmse_occupied=float(np.sqrt(np.mean(delta**2))),
                        max_occupied=float(np.max(np.abs(delta))),
                        rmse_global=(float(np.sqrt(np.mean(delta**2))) if np.all(occupied) else None),
                        epsilon_infinity=(whole["supremum"] if np.all(occupied) else None),
                        S_born=canonical.similarity,
                    ))
        print(f"verified seed {seed}; {len(records)} native snapshots", flush=True)

    g, t = config["collective_coupling"], config["scaling_time"]
    limiting = np.exp(-2*g*g*t*t)
    scaling = []
    for size in config["scaling_sizes"]:
        moment = collective_cosine_moments(size, coupling=g, time=t, maximum_order=1)[1]
        coefficient = 4*g**4*t**4/3
        scaling.append([size, abs(moment-limiting), limiting*coefficient/size,
                        abs(np.log(moment)+2*g*g*t*t+coefficient/size)])
    scaling = np.array(scaling)
    theta = np.linspace(0, np.pi, 1001)
    density, tail_bounds = [], []
    for t in config["collective_plot_times"]:
        values, tail = gaussian_limit_density(theta, coupling=g, time=t)
        density.append(values)
        tail_bounds.append(tail)
    profiles = dict(theta=theta, density=np.array(density),
                    times=np.array(config["collective_plot_times"]), g=np.array(g),
                    scaling_time=np.array(config["scaling_time"]),
                    field_width=np.array(config["field_interval_width"]))
    np.savez_compressed(args.output/"native_root_angles.npz", **root_arrays)
    np.savez_compressed(args.output/"continuum_profiles.npz", **profiles)
    np.savetxt(args.output/"finite_size_correction.dat", scaling,
               header="N moment_error leading_1_over_N log_remainder")
    np.savetxt(args.output/"field_means.dat", field_means, header="seed t mean_d0")
    (args.output/"snapshots.json").write_text(json.dumps(records, indent=2, allow_nan=False)+"\n")
    plot_asymptotic_audit(args.output, records, profiles, scaling, np.array(field_means), root_arrays)
    sources = ["core/born_asymptotic.py", "core/born_asymptotic_plotting.py",
               "scripts/analyze_born_asymptotic.py", "core/analysis.py", "core/born.py",
               "core/born_reciprocity.py", "core/relative_evolution_pencil.py",
               "core/hamiltonians/quspin_hamiltonians.py"]
    summary = dict(
        created_utc=datetime.now(timezone.utc).isoformat(), config=config,
        python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
        source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        source_hashes={name: digest(ROOT/name) for name in sources},
        config_sha256=digest(args.config), native_snapshots=len(records),
        maximum_qz_residual=max(r["qz_residual"] for r in records),
        maximum_in_scope_trace_error=max(r["trace_error"] for r in records if not r["control"]),
        symmetry_breaking_control_error_range=[
            min(r["trace_error"] for r in records if r["control"]),
            max(r["trace_error"] for r in records if r["control"])],
        coverage_range=[min(r["coverage"] for r in records), max(r["coverage"] for r in records)],
        continuum_fourier_tail_bounds=tail_bounds,
        evidence_scope="Reduced snapshot checks of A-D; E checked in focused tests; full-model phase unresolved",
        outputs={path.name: digest(path) for path in sorted(args.output.iterdir()) if path.is_file()},
    )
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    print(json.dumps({key: summary[key] for key in ["native_snapshots", "maximum_qz_residual",
                                                  "maximum_in_scope_trace_error", "coverage_range"]}))


if __name__ == "__main__":
    main()
