"""Checkpointed baseline campaign with one seed/size per array index."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

import numpy as np
import scipy
import quspin

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.born_phase_verifier import SCHEMA_VERSION
from core.ring_chain_family import RingChainSpec
from core.ring_translation import METHOD_VERSION,build_ring_translation_block,diagonalize_ring_translation_block,evaluate_ring_translation_time,combine_ring_translation_diagnostics
from core.translation_sector_roots import cyclic_translation_multiplicities

DEFINING_FILES=("core/ring_translation.py","core/ring_chain_family.py","core/translation_sector_roots.py",
    "core/born_phase_verifier.py","core/born.py","core/born_reciprocity.py","core/relative_evolution_pencil.py",
    "scripts/run_born_ring_campaign.py")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path,value: dict) -> None:
    """Atomic completion/record writes, with no nonstandard JSON numbers."""
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+"\n")
    temporary.replace(path)


def campaign_tasks(config: dict,seed_config: dict) -> list[tuple[str,RingChainSpec]]:
    if config["schema_version"]!="born-ring-baseline-campaign-v1" or config["method_version"]!=METHOD_VERSION or config["verifier_schema"]!=SCHEMA_VERSION:
        raise ValueError("campaign/method/verifier schema mismatch")
    times=config["discovery_times"]+config["heldout_times"]
    if not times or len(set(times))!=len(times) or any(not np.isfinite(t) or t<=0 for t in times):
        raise ValueError("time sets must be disjoint, nonempty in total, finite and positive")
    seeds={s["name"]:s for s in seed_config["seeds"]}
    result=[]
    for name in config["seed_names"]:
        seed=seeds[name]
        for n in config["sizes"]:
            result.append((name,RingChainSpec(n,"ring",**{f:tuple(seed[f]) for f in
                ("qubit_field","detector_field","nearest","second","coupling")})))
    if len({(name,s.detector_n) for name,s in result})!=len(result):
        raise ValueError("duplicate task ownership")
    return result


def verify_marker(directory: Path) -> dict:
    marker=json.loads((directory/"COMPLETE.json").read_text())
    if marker["status"]!="complete":raise ValueError("checkpoint not complete")
    for name,sha in marker["files"].items():
        if Path(name).name!=name or digest(directory/name)!=sha:raise ValueError("checkpoint hash mismatch")
    for name,sha in marker.get("sector_markers",{}).items():
        relative=Path(name)
        if len(relative.parts)!=2 or not relative.parts[0].startswith("k") or relative.parts[1]!="COMPLETE.json":
            raise ValueError("invalid sector marker path")
        if digest(directory/relative)!=sha:raise ValueError("sector marker hash mismatch")
        verify_marker((directory/relative).parent)
    return marker


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=ROOT/"configs/born_ring_baseline_campaign_v1.json")
    parser.add_argument("--array-index",type=int)
    parser.add_argument("--output-root",type=Path,required=True)
    parser.add_argument("--dry-run",action="store_true")
    parser.add_argument("--resume",action="store_true")
    args=parser.parse_args()
    cfg=json.loads(args.config.read_text());seed_path=ROOT/cfg["seed_config"]
    tasks=campaign_tasks(cfg,json.loads(seed_path.read_text()))
    if args.dry_run:
        print(json.dumps([dict(index=i,seed=name,N=s.detector_n,sector_dimensions=cyclic_translation_multiplicities(s.detector_n))
                          for i,(name,s) in enumerate(tasks)],indent=2));return
    if args.array_index is None or not 0<=args.array_index<len(tasks):raise ValueError("valid array index required")
    name,spec=tasks[args.array_index];n=spec.detector_n
    output=args.output_root/f"task_{args.array_index:03d}_{name}_N{n}"
    identity=dict(config_sha256=digest(args.config),seed_config_sha256=digest(seed_path),
                  code_sha256={p:digest(ROOT/p) for p in DEFINING_FILES},array_index=args.array_index,
                  seed=name,parameters=asdict(spec),runtime=dict(python=platform.python_version(),
                      numpy=np.__version__,scipy=scipy.__version__,quspin=quspin.__version__))
    if output.exists():
        if not args.resume:raise FileExistsError(output)
        old=json.loads((output/"provenance.json").read_text())
        if old["identity"]!=json.loads(json.dumps(identity)):raise ValueError("resume source/config identity mismatch")
        if (output/"COMPLETE.json").exists():
            verify_marker(output)
            print("Already complete and hashes verified");return
        if (output/"FAILED.json").exists():
            history=output/"failure_history"
            history.mkdir(exist_ok=True)
            failure_name=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ.json")
            (output/"FAILED.json").rename(history/failure_name)
    else:
        output.mkdir(parents=True)
        commit=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True)
        write_json(output/"provenance.json",dict(identity=identity,config=cfg,timestamp_utc=datetime.now(timezone.utc).isoformat(),
                   git_commit=commit.stdout.strip() if commit.returncode==0 else None,python=platform.python_version(),
                   numpy=np.__version__,scipy=scipy.__version__,quspin=quspin.__version__,seed=None,
                   threads={k:os.environ.get(k) for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS")}))
    times=cfg["discovery_times"]+cfg["heldout_times"];all_sectors={t:[] for t in times};started=perf_counter()
    try:
        for k in range(n):
            directory=output/f"k{k:02d}"
            if (directory/"COMPLETE.json").exists():
                verify_marker(directory)
            else:
                directory.mkdir(exist_ok=True)
                block=build_ring_translation_block(spec,k)
                e,v,eig=diagonalize_ring_translation_block(block)
                if max(eig.values())>cfg["eigensystem_tolerance"]:raise ArithmeticError(f"eigensystem validation failed k={k}: {eig}")
                results={}
                for ti,time in enumerate(times):
                    diagnostic,arrays=evaluate_ring_translation_time(block,e,v,time)
                    np.savez_compressed(directory/f"time_{ti}.npz",**arrays)
                    results[str(ti)]=dict(time=time,diagnostics=diagnostic)
                    write_json(directory/"diagnostics.json",dict(eigensystem=eig,times=results))
                    if diagnostic["qz_validity"] is not True or diagnostic["column_isometry"]>cfg["isometry_tolerance"]:
                        raise ArithmeticError(f"QZ/isometry validation failed k={k} time={time}")
                write_json(directory/"COMPLETE.json",dict(status="complete",momentum=k,root_count=len(block.top),
                           files={p.name:digest(p) for p in directory.iterdir() if p.name!="COMPLETE.json"}))
                del block,e,v
            saved=json.loads((directory/"diagnostics.json").read_text())
            if set(saved["times"])!={str(i) for i in range(len(times))}:raise ValueError("incomplete checkpoint time set")
            for ti,time in enumerate(times):
                row=saved["times"][str(ti)]
                if row["time"]!=time:raise ValueError("checkpoint time mismatch")
                with np.load(directory/f"time_{ti}.npz",allow_pickle=False) as archive:
                    all_sectors[time].append((row["diagnostics"],{key:archive[key] for key in archive.files}))
            print(f"Validated {name} N={n} k={k}",flush=True)
        records=[]
        for time in times:
            result=combine_ring_translation_diagnostics(n,all_sectors[time])
            records.append(dict(candidate=name,N=n,time=time,perturbation="baseline",
                           split="discovery" if time in cfg["discovery_times"] else "heldout",diagnostics=result))
        write_json(output/"results.json",dict(records=records,elapsed_seconds=perf_counter()-started))
        write_json(output/"COMPLETE.json",dict(status="complete",array_index=args.array_index,momentum_count=n,
                   times=len(times),root_count_per_time=2**n,files={p.name:digest(p) for p in output.iterdir()
                   if p.is_file() and p.name not in ("COMPLETE.json","FAILED.json")},
                   sector_markers={f"k{k:02d}/COMPLETE.json":digest(output/f"k{k:02d}/COMPLETE.json") for k in range(n)}))
    except Exception as error:
        write_json(output/"FAILED.json",dict(status="failed",error=repr(error),timestamp_utc=datetime.now(timezone.utc).isoformat()))
        raise
    print(f"Completed {name} N={n}, {len(times)} times",flush=True)


if __name__=="__main__":main()
