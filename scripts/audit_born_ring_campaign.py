"""Read-only completion audit and frozen-metric aggregation of a ring campaign."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.born_phase_verifier import QZ_RESIDUAL_TOLERANCE,evaluate_angles,summarize_conditions
from scripts.run_born_ring_campaign import DEFINING_FILES,campaign_tasks,digest,verify_marker,write_json
from core.translation_sector_roots import cyclic_translation_multiplicities


def audit_campaign(source: Path,config_path: Path) -> dict:
    """Reject missing coverage, corrupt roots or altered stored diagnostics.

    'Coverage' here means the required task/sector/time set. Poor angular
    coverage is a scientific result and stays in the pooled report.
    This rechecks recorded evidence; it does not rerun QZ or certify an
    asymptotic Born law. No remote file or source artifact is modified.
    """
    cfg=json.loads(config_path.read_text());seed_path=ROOT/cfg["seed_config"]
    tasks=campaign_tasks(cfg,json.loads(seed_path.read_text()))
    times=cfg["discovery_times"]+cfg["heldout_times"]
    records=[];identities=[];checksums={}
    for index,(name,spec) in enumerate(tasks):
        directory=source/f"task_{index:03d}_{name}_N{spec.detector_n}"
        if (directory/"FAILED.json").exists():raise ValueError(f"active failure marker: {directory}")
        marker=verify_marker(directory)
        if not {"provenance.json","results.json"}<=set(marker["files"]):raise ValueError("missing task evidence")
        n=spec.detector_n
        dimensions=cyclic_translation_multiplicities(n)
        expected_markers={f"k{k:02d}/COMPLETE.json" for k in range(n)}
        if set(marker["sector_markers"])!=expected_markers or marker["root_count_per_time"]!=2**n:
            raise ValueError("task sector/root coverage mismatch")
        identity=json.loads((directory/"provenance.json").read_text())["identity"]
        if identity["config_sha256"]!=digest(config_path) or identity["seed_config_sha256"]!=digest(seed_path):
            raise ValueError("campaign config identity mismatch")
        if identity["array_index"]!=index or identity["seed"]!=name:
            raise ValueError("task identity mismatch")
        if identity["parameters"]!=json.loads(json.dumps(asdict(spec))):
            raise ValueError("task parameter mismatch")
        if identity["code_sha256"]!={p:digest(ROOT/p) for p in DEFINING_FILES}:
            raise ValueError("campaign source identity mismatch")
        identities.append(identity)
        stored=json.loads((directory/"results.json").read_text())["records"]
        if len(stored)!=len(times) or {r["time"] for r in stored}!=set(times):
            raise ValueError("missing or duplicate instantaneous result")
        angles={t:[] for t in times}
        for k in range(n):
            sector=directory/f"k{k:02d}"
            sector_marker=verify_marker(sector)
            if sector_marker["momentum"]!=k or sector_marker["root_count"]!=dimensions[k]:
                raise ValueError("momentum multiplicity mismatch")
            required={"diagnostics.json"}|{f"time_{i}.npz" for i in range(len(times))}
            if not required<=set(sector_marker["files"]):raise ValueError("missing sector/time evidence")
            saved=json.loads((sector/"diagnostics.json").read_text())
            if set(saved["times"])!={str(i) for i in range(len(times))}:
                raise ValueError("sector time set mismatch")
            if any(not np.isfinite(v) or v<0 or v>cfg["eigensystem_tolerance"] for v in saved["eigensystem"].values()):
                raise ValueError("failed eigensystem evidence")
            for ti,time in enumerate(times):
                if saved["times"][str(ti)]["time"]!=time:raise ValueError("sector time mismatch")
                d=saved["times"][str(ti)]["diagnostics"]
                if d["qz_validity"] is not True or not np.isfinite(d["column_isometry"]) or not 0<=d["column_isometry"]<=cfg["isometry_tolerance"]:
                    raise ValueError("failed QZ/isometry evidence")
                with np.load(sector/f"time_{ti}.npz",allow_pickle=False) as archive:
                    a,b,theta=(archive[key] for key in ("alpha","beta","theta"))
                    if any(v.shape!=(sector_marker["root_count"],) for v in (a,b,theta)):
                        raise ValueError("sector root count mismatch")
                    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)) or np.any((a==0)&(b==0)):
                        raise ValueError("invalid homogeneous coordinates")
                    if not np.allclose(theta,2*np.arctan2(abs(a),abs(b)),atol=1e-14,rtol=0):
                        raise ValueError("stored polar coordinates disagree with homogeneous roots")
                    for key in ("right_residuals","left_residuals"):
                        residual=archive[key]
                        if residual.shape!=theta.shape or not np.all(np.isfinite(residual)) or np.any(residual<0) or np.any(residual>QZ_RESIDUAL_TOLERANCE):
                            raise ValueError("invalid recorded QZ residuals")
                    angles[time].append(theta.copy())
        for row in stored:
            time=row["time"]
            split="discovery" if time in cfg["discovery_times"] else "heldout"
            if row["candidate"]!=name or row["N"]!=n or row["split"]!=split or row["perturbation"]!="baseline":
                raise ValueError("stored scientific condition mismatch")
            recomputed=evaluate_angles(np.concatenate(angles[time]),expected_count=2**n)
            d=row["diagnostics"]
            for key in ("coverage","moment_max","tilted_mass","balance_binned_l1","balance_binned_relative","global_ratio_rmse"):
                a,b=recomputed[key],d[key]
                if (a is None)!=(b is None) or a is not None and not np.isclose(a,b,rtol=0,atol=1e-12):
                    raise ValueError(f"pooled diagnostic mismatch: {key}")
            if d["qz_validity"] is not True:raise ValueError("pooled QZ evidence failed")
            records.append(row)
        checksums[str((directory/"COMPLETE.json").relative_to(source))]=digest(directory/"COMPLETE.json")
    for identity in identities[1:]:
        if identity["runtime"]!=identities[0]["runtime"] or identity["code_sha256"]!=identities[0]["code_sha256"]:
            raise ValueError("campaign mixes runtime or source versions")
    return dict(status="complete",expected_tasks=len(tasks),expected_conditions=len(tasks)*len(times),
                audited_conditions=len(records),task_marker_sha256=checksums,records=records,
                summary=summarize_conditions(records),scope="Complete recorded campaign audit; no fresh QZ or phase certificate")


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--config",type=Path,default=ROOT/"configs/born_ring_baseline_campaign_v1.json")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=audit_campaign(args.source,args.config)
    args.output.mkdir(parents=True)
    write_json(args.output/"audit.json",result)
    write_json(args.output/"manifest.json",dict(config_sha256=digest(args.config),script_sha256=digest(Path(__file__)),
               outputs={"audit.json":digest(args.output/"audit.json")}))
    print(json.dumps({k:result[k] for k in ("status","expected_tasks","audited_conditions")},indent=2))


if __name__=="__main__":main()
