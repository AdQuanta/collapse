"""Bounded QZ checks of the weak transverse equivalence and exact resolvent."""
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

from core.born import born_ratio_from_theta
from core.born_reciprocity import born_moment_residuals, cosine_moments
from core.projective_potential import homogeneous_radial_potential
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum
from core.resonant_return import leading_transverse_matrix, projected_resolvent, transverse_gauge
from core.resonant_return_plotting import plot_return_comparison
from core.ring_chain_family import RingChainSpec, build_ring_chain_parts


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/born_resonant_return_2026-09-12.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    if (cfg["schema_version"] != 1 or max(sum(cfg["sizes"].values(), [])) > 7
            or cfg["anisotropies"][0] != 0 or cfg["qubit_field"] != [0., 0., 0.]
            or cfg["theta_bins"] != 64 or cfg["moment_order"] != 16):
        raise ValueError("requires schema 1, N<=7, zero central field, baseline eta=0, and 64 bins/16 moments")
    args.output.mkdir(parents=True, exist_ok=False)
    parameters = {key: tuple(cfg[key]) for key in ("qubit_field", "detector_field", "nearest", "second")}
    x = np.array(cfg["log_radius_grid"])
    z = complex(*cfg["resolvent_z"])
    records, arrays = [], {}
    for topology, sizes in cfg["sizes"].items():
        for n in sizes:
            d = 2**n
            baseline = {}
            for eta in cfg["anisotropies"]:
                g = cfg["g_effective"]
                gx, gy = g*np.cosh(eta), g*np.sinh(eta)
                spec = RingChainSpec(n, topology, **parameters, coupling=(gx, gy, 0.))
                h0, v = build_ring_chain_parts(spec)
                h = h0+v
                hd, q = h0[:d, :d], v[d:, :d]
                energy, vectors = eigh(h)
                eigen_residual = np.linalg.norm(h@vectors-vectors*energy)/max(1., np.linalg.norm(h))
                orthogonality = np.linalg.norm(vectors.conj().T@vectors-np.eye(2*d))/np.sqrt(2*d)
                if max(eigen_residual, orthogonality) > 1e-12:
                    raise ArithmeticError("Hamiltonian eigensystem verification failed")
                resolved = projected_resolvent(h[:d, :d], h[d:, d:], h[d:, :d], spectral_parameter=z)
                reference = (vectors/(z-energy)) @ vectors[:d, :].conj().T
                difference = np.linalg.norm(np.vstack([resolved.upper, resolved.lower])-reference)/np.linalg.norm(reference)
                if difference > 1e-11 or resolved.column_residual > 1e-11:
                    raise ArithmeticError("native resolvent verification failed")
                magnetizations = np.array([n-2*i.bit_count() for i in range(d)])
                diagonal, scale = transverse_gauge(magnetizations, gx=gx, gy=gy)
                for time in cfg["times"]:
                    unitary = (vectors*np.exp(-1j*time*energy)) @ vectors.conj().T
                    roots = generalized_relative_evolution_spectrum(unitary[:d, :d], unitary[d:, :d])
                    m1 = leading_transverse_matrix(hd, q, central_z=0., time=time)
                    leading = generalized_relative_evolution_spectrum(np.eye(d), m1)
                    if np.any(roots.indeterminate) or np.any(leading.indeterminate):
                        raise ArithmeticError("indeterminate projective root")
                    residual = max(roots.maximum_homogeneous_residual,
                                   leading.maximum_homogeneous_residual,
                                   roots.maximum_left_homogeneous_residual,
                                   leading.maximum_left_homogeneous_residual)
                    if residual > 1e-10:
                        raise ArithmeticError("QZ residual exceeds reduced verification tolerance")
                    potential = homogeneous_radial_potential(roots.alpha, roots.beta, x)
                    leading_potential = homogeneous_radial_potential(leading.alpha, leading.beta, x)
                    if eta == 0:
                        baseline[time] = (m1, potential, leading_potential)
                    base_m, base_j, base_leading = baseline[time]
                    gauge_error = np.linalg.norm(diagonal[:, None]*m1/diagonal[None, :]
                                                 - (scale/g)*base_m)/max(1., np.linalg.norm(base_m))
                    if gauge_error > 1e-7 or max(abs(leading_potential-base_leading)) > 1e-9:
                        raise ArithmeticError("leading transverse equivalence verification failed")
                    polar = born_ratio_from_theta(roots.theta, np.pi-roots.theta, n_theta=64)
                    occupied = polar.counts_0+polar.counts_1 > 0
                    delta = polar.ratio[occupied]-polar.born[occupied]
                    moments = cosine_moments(roots.theta, 16)
                    rows = dict(
                        topology=topology, N=n, eta=eta, time=time, coupling=[gx, gy, 0.],
                        qz_residual=float(residual), resolvent_relative_error=float(difference),
                        hamiltonian_eigen_residual=float(eigen_residual), orthogonality_error=float(orthogonality),
                        resolvent_column_residual=resolved.column_residual,
                        gauge_matrix_error=float(gauge_error), gauge_condition=float(max(abs(diagonal))/min(abs(diagonal))),
                        leading_gauge_potential_difference=float(max(abs(leading_potential-base_leading))),
                        exact_gauge_potential_difference=float(max(abs(potential-base_j))),
                        leading_to_exact_potential_difference=float(max(abs(potential-leading_potential))),
                        coverage=float(np.mean(occupied)), moments=moments.tolist(),
                        moment_residuals=born_moment_residuals(moments).tolist(),
                        occupied_rmse=float(np.sqrt(np.mean(delta**2))),
                        global_rmse=float(np.sqrt(np.mean(delta**2))) if np.all(occupied) else None,
                        global_linf=float(max(abs(delta))) if np.all(occupied) else None,
                        S_born_100=born_ratio_from_theta(roots.theta, np.pi-roots.theta).similarity,
                    )
                    key=f"{topology}_N{n}_eta{eta}_t{time}"
                    arrays[key+"_theta"] = roots.theta
                    arrays[key+"_leading_theta"] = leading.theta
                    records.append(rows)
    np.savez_compressed(args.output/"angles.npz", **arrays)
    (args.output/"records.json").write_text(json.dumps(records, indent=2, allow_nan=False)+"\n")
    plot_return_comparison(args.output, records)
    sources = ["core/resonant_return.py", "core/resonant_return_plotting.py", "core/ring_chain_family.py",
               "core/relative_evolution_pencil.py", "core/projective_potential.py", "core/born.py",
               "core/born_reciprocity.py", "scripts/verify_born_resonant_return.py", "tests/test_resonant_return.py"]
    summary = dict(
        config=cfg, config_sha256=digest(args.config), source_candidate_sha256=digest(ROOT/cfg["source_candidate"]),
        code_hashes={p: digest(ROOT/p) for p in sources},
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        timestamp_utc=datetime.now(timezone.utc).isoformat(), python=platform.python_version(),
        numpy=np.__version__, scipy=scipy.__version__, snapshots=len(records),
        maxima={key: max(r[key] for r in records) for key in
                ("qz_residual", "hamiltonian_eigen_residual", "orthogonality_error",
                 "resolvent_relative_error", "resolvent_column_residual", "gauge_matrix_error",
                 "leading_gauge_potential_difference", "exact_gauge_potential_difference",
                 "leading_to_exact_potential_difference")},
        coverage_range=[min(r["coverage"] for r in records), max(r["coverage"] for r in records)],
        outputs={p.name: digest(p) for p in sorted(args.output.iterdir())},
        scope="Reduced verification of a leading-response identity and exact return representation; no phase or asymptotic extrapolation",
    )
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    print(json.dumps({k: summary[k] for k in ("snapshots", "maxima", "coverage_range")}, indent=2))


if __name__ == "__main__":
    main()
