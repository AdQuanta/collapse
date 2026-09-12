"""Preregistered reduced XYZ-ring sensitivity using full production QZ."""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time as clock

import numpy as np
import scipy
from scipy.linalg import eigh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.born_phase_verifier import SCHEMA_VERSION, evaluate_spectrum, summarize_conditions
from core.projective_potential import homogeneous_radial_potential
from core.projective_roots import production_root_spectrum
from core.ring_chain_family import RingChainSpec, build_ring_chain_parts


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def variants(spec: RingChainSpec, config: dict) -> list[tuple[str, RingChainSpec]]:
    """Change exactly one permitted microscopic coefficient from the seed."""
    scale = config["relative_amplitude"]*max(abs(g) for g in spec.coupling[:2])
    result = [("baseline", spec)]
    for direction in config["directions"]:
        field, index = direction.rsplit("_", 1)
        if field not in ("qubit_field", "coupling") or int(index) not in range(3):
            raise ValueError("invalid microscopic direction")
        for sign in config["signs"]:
            values = list(getattr(spec, field))
            values[int(index)] += sign*scale
            result.append((f"{direction}_{'plus' if sign > 0 else 'minus'}",
                           replace(spec, **{field: tuple(values)})))
    return result


def paired_decisions(records: list[dict]) -> list[dict]:
    """Apply the preregistered per-size worst-time Pareto comparison."""
    decisions = []
    for candidate in sorted({r["candidate"] for r in records}):
        rows = [r for r in records if r["candidate"] == candidate]
        sizes = sorted({r["N"] for r in rows})
        for perturbation in sorted({r["perturbation"] for r in rows}-{ "baseline" }):
            comparisons = []
            for n in sizes:
                pair = []
                for name in ("baseline", perturbation):
                    group = [r for r in rows if r["N"] == n and r["perturbation"] == name]
                    valid = bool(group) and all(r["diagnostics"] is not None
                                               and r["diagnostics"]["qz_validity"] is True
                                               and "failure" not in r and "validation_failure" not in r for r in group)
                    if not valid:
                        pair.append(None)
                    else:
                        ds = [r["diagnostics"] for r in group]
                        balance = [d["balance_binned_relative"] for d in ds]
                        pair.append(None if any(v is None for v in balance) else dict(
                            balance=max(balance), moment=max(d["moment_max"] for d in ds),
                            coverage=min(d["coverage"] for d in ds)))
                comparisons.append(dict(N=n, baseline=pair[0], perturbation=pair[1]))
            valid = all(c["baseline"] is not None and c["perturbation"] is not None for c in comparisons)
            improves = valid and all(
                c["perturbation"]["balance"] <= c["baseline"]["balance"]
                and c["perturbation"]["moment"] <= c["baseline"]["moment"]
                and c["perturbation"]["coverage"] >= c["baseline"]["coverage"]
                for c in comparisons)
            strict = valid and any(c["perturbation"]["balance"] < c["baseline"]["balance"] for c in comparisons)
            decisions.append(dict(candidate=candidate, perturbation=perturbation,
                                  decision="KEEP" if improves and strict else "REJECT" if valid else "INCONCLUSIVE",
                                  scope="Reduced worst-time comparison only", comparisons=comparisons))
    return decisions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/"configs/born_multichannel_sensitivity_v1.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    if cfg["schema_version"] != "born-multichannel-sensitivity-v1" or cfg["verifier_schema"] != SCHEMA_VERSION:
        raise ValueError("schema mismatch")
    if cfg["topology"] != "ring" or not all(5 <= n <= 7 for n in cfg["sizes"]):
        raise ValueError("this local runner is limited to reduced N=5..7 rings")
    if len(set(cfg["times"])) != len(cfg["times"]) or any(t <= 0 for t in cfg["times"]):
        raise ValueError("times must be distinct and positive")
    specs, source_hashes = [], {}
    for seed in cfg["seeds"]:
        path = ROOT/seed["source"]
        native = json.loads(path.read_text())["configuration"]
        expected = dict(qubit_field=(0,0,0), detector_field=(0,0,-native["hz"]),
                        nearest=(-native["jpm"]/2,-native["jpm"]/2,-native["j"]),
                        second=(0,0,0), coupling=(-native["jx"],-native["jy"],0))
        for key, value in expected.items():
            if not np.allclose(seed[key], value, rtol=1e-14, atol=0):
                raise ValueError(f"seed/source convention mismatch: {seed['name']} {key}")
        source_hashes[seed["source"]] = digest(path)
        for n in cfg["sizes"]:
            base = RingChainSpec(n, cfg["topology"], **{key: tuple(seed[key]) for key in expected})
            specs.extend((seed["name"], label, spec) for label, spec in variants(base, cfg))
    print(f"Validated {len(specs)} Hamiltonians, {len(specs)*len(cfg['times'])} QZ conditions", flush=True)
    if args.dry_run:
        return
    args.output.mkdir(parents=True, exist_ok=False)
    started = clock.perf_counter()
    records = []
    sources = ["scripts/run_born_multichannel_sensitivity.py", "core/ring_chain_family.py", "core/pauli.py",
               "core/born_phase_verifier.py", "core/born.py", "core/born_reciprocity.py",
               "core/projective_roots.py", "core/relative_evolution_pencil.py", "core/projective_potential.py"]
    provenance = dict(config=cfg, config_sha256=digest(args.config), source_sha256=source_hashes,
                      code_sha256={p: digest(ROOT/p) for p in sources},
                      git_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                      timestamp_utc=datetime.now(timezone.utc).isoformat(),
                      python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, seed=None,
                      thread_environment={k:os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","VECLIB_MAXIMUM_THREADS")})
    (args.output/"preregistration.json").write_text(json.dumps(provenance,indent=2)+"\n")
    for candidate, label, spec in specs:
        d = 2**spec.detector_n
        h0, v = build_ring_chain_parts(spec)
        h = h0+v
        energy, vectors = eigh(h, driver="evr")
        norm = np.linalg.norm(h)
        eig_error = float(np.linalg.norm(h@vectors-vectors*energy)/max(1.,norm))
        ortho_error = float(np.linalg.norm(vectors.conj().T@vectors-np.eye(2*d))/np.sqrt(2*d))
        cross = cfg["driver_crosscheck"]
        alternative = (eigh(h,driver="evd") if spec.detector_n == cross["size"]
                       and label in cross["perturbations"] else None)
        for time in cfg["times"]:
            row = dict(candidate=candidate,N=spec.detector_n,time=time,perturbation=label,split="discovery",
                       parameters=asdict(spec),diagnostics=None,eigen_residual=eig_error,orthogonality=ortho_error)
            try:
                if max(eig_error,ortho_error) > cfg["eigensystem_tolerance"]:
                    raise ArithmeticError("eigensystem tolerance failed")
                u = (vectors*np.exp(-1j*time*energy))@vectors.conj().T
                row["unitarity_error"] = float(np.linalg.norm(u.conj().T@u-np.eye(2*d))/np.sqrt(2*d))
                if row["unitarity_error"] > cfg["unitarity_tolerance"]:
                    raise ArithmeticError("unitarity tolerance failed")
                roots = production_root_spectrum(u)
                row["diagnostics"] = evaluate_spectrum(roots,expected_count=d)
                filename = f"{candidate}_N{spec.detector_n}_{label}_t{time:g}.npz"
                np.savez_compressed(args.output/filename,alpha=roots.alpha,beta=roots.beta,theta=roots.theta,
                                    right_residuals=roots.homogeneous_residuals,left_residuals=roots.left_homogeneous_residuals)
                row["roots"] = filename
                if alternative is not None:
                    other_e,other_v = alternative
                    other_u = (other_v*np.exp(-1j*time*other_e))@other_v.conj().T
                    other = production_root_spectrum(other_u)
                    check = evaluate_spectrum(other,expected_count=d)
                    x = np.array(cfg["log_radius_grid"])
                    diff = float(np.max(np.abs(homogeneous_radial_potential(roots.alpha,roots.beta,x)
                                                -homogeneous_radial_potential(other.alpha,other.beta,x))))
                    angle = float(np.max(np.abs(np.sort(roots.theta)-np.sort(other.theta))))
                    row["driver_crosscheck"] = dict(potential_max=diff,sorted_polar_max=angle,
                        unitary_relative=float(np.linalg.norm(u-other_u)/np.sqrt(2*d)),qz_validity=check["qz_validity"],
                        passed=bool(check["qz_validity"] and diff<=cross["potential_tolerance"] and angle<=cross["angle_tolerance"]))
                    if not row["driver_crosscheck"]["passed"]:
                        row["validation_failure"] = "independent eigensolver driver sensitivity"
            except (ValueError,ArithmeticError,np.linalg.LinAlgError) as error:
                row["failure"] = str(error)
            records.append(row)
            with (args.output/"records.jsonl").open("a") as stream:
                stream.write(json.dumps(row,allow_nan=False)+"\n")
        print(f"Completed {candidate} N={spec.detector_n} {label}",flush=True)
    decisions = paired_decisions(records)
    result = dict(summary=summarize_conditions(records),decisions=decisions)
    (args.output/"summary.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    manifest = dict(expected_conditions=len(specs)*len(cfg["times"]),actual_conditions=len(records),
                    failed_conditions=sum(r["diagnostics"] is None or r["diagnostics"]["qz_validity"] is not True
                                          or "failure" in r or "validation_failure" in r for r in records),
                    elapsed_seconds=clock.perf_counter()-started,
                    outputs={p.name:digest(p) for p in args.output.iterdir()})
    manifest["status"] = "complete" if manifest["failed_conditions"]==0 else "complete_with_validation_failures"
    (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({k:v for k,v in manifest.items() if k!="outputs"},indent=2))


if __name__ == "__main__":
    main()
