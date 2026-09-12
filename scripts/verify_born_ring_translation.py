"""Cross-check the complete XYZ ring translation method against dense QZ."""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

import numpy as np
import scipy
from scipy.linalg import eigh

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.born_phase_verifier import evaluate_spectrum
from core.projective_potential import homogeneous_radial_potential
from core.projective_roots import production_root_spectrum,bloch_vectors_from_homogeneous,matched_bloch_distance
from core.ring_chain_family import RingChainSpec,build_ring_chain_parts
from core.ring_translation import METHOD_VERSION,build_ring_translation_block,diagonalize_ring_translation_block,evaluate_ring_translation_time,combine_ring_translation_diagnostics


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=ROOT/"configs/born_ring_translation_validation_v1.json")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    cfg=json.loads(args.config.read_text())
    if cfg["method_version"]!=METHOD_VERSION or max(cfg["sizes"])>7:
        raise ValueError("method validation is restricted to reduced N<=7")
    fields=("qubit_field","detector_field","nearest","second","coupling")
    seeds=json.loads((ROOT/cfg["seed_config"]).read_text())["seeds"]
    parameters={s["name"]:{f:tuple(s[f]) for f in fields} for s in seeds}
    parameters["generic_xyz"]={f:tuple(cfg["generic_parameters"][f]) for f in fields}
    args.output.mkdir(parents=True,exist_ok=False)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    sources=["core/ring_translation.py","core/ring_chain_family.py","core/pauli.py","core/translation_sector_roots.py",
             "core/born_phase_verifier.py","core/born.py","core/born_reciprocity.py","core/relative_evolution_pencil.py",
             "core/projective_roots.py","core/projective_potential.py","scripts/verify_born_ring_translation.py"]
    provenance=dict(config=cfg,config_sha256=digest(args.config),seed_config_sha256=digest(ROOT/cfg["seed_config"]),
                    code_sha256={p:digest(ROOT/p) for p in sources},timestamp_utc=datetime.now(timezone.utc).isoformat(),
                    python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,seed=None,
                    commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip())
    (args.output/"preregistration.json").write_text(json.dumps(provenance,indent=2)+"\n")
    records=[];start=perf_counter()
    for name,values in parameters.items():
        for n in cfg["sizes"]:
            spec=RingChainSpec(n,"ring",**values)
            h0,v=build_ring_chain_parts(spec);h=h0+v
            e,v=eigh(h,driver="evd")
            sector_results={t:[] for t in cfg["times"]}
            block_error=0.;eigen_error=0.
            for k in range(n):
                block=build_ring_translation_block(spec,k)
                p=block.basis.get_proj(np.complex128).toarray()
                block_error=max(block_error,float(np.linalg.norm(h@p-p@block.matrix)/max(1.,np.linalg.norm(h))))
                ek,vk,checks=diagonalize_ring_translation_block(block)
                eigen_error=max(eigen_error,max(checks.values()))
                for time in cfg["times"]:
                    sector_results[time].append(evaluate_ring_translation_time(block,ek,vk,time))
            for time in cfg["times"]:
                full=production_root_spectrum((v*np.exp(-1j*time*e))@v.conj().T)
                dense=evaluate_spectrum(full,expected_count=2**n)
                sectors=sector_results[time]
                combined=combine_ring_translation_diagnostics(n,sectors)
                alpha=np.concatenate([a["alpha"] for _,a in sectors]);beta=np.concatenate([a["beta"] for _,a in sectors])
                bloch_max,bloch_rms=matched_bloch_distance(bloch_vectors_from_homogeneous(full.alpha,full.beta),
                                                         bloch_vectors_from_homogeneous(alpha,beta))
                x=np.array(cfg["log_radius_grid"])
                potential=float(np.max(np.abs(homogeneous_radial_potential(alpha,beta,x)
                                              -homogeneous_radial_potential(full.alpha,full.beta,x))))
                passed=bool(block_error<=cfg["matrix_tolerance"] and eigen_error<=cfg["eigensystem_tolerance"]
                            and combined["column_isometry"]<=cfg["isometry_tolerance"] and dense["qz_validity"]
                            and combined["qz_validity"] and bloch_max<=cfg["bloch_tolerance"] and potential<=cfg["potential_tolerance"])
                row=dict(candidate=name,N=n,time=time,projection_residual=block_error,eigensystem_max=eigen_error,
                         bloch_max=bloch_max,bloch_rms=bloch_rms,potential_max=potential,passed=passed,
                         dense_diagnostics=dense,translation_diagnostics=combined)
                records.append(row)
                with (args.output/"records.jsonl").open("a") as stream:stream.write(json.dumps(row,allow_nan=False)+"\n")
            print(f"Verified {name} N={n}",flush=True)
    summary=dict(method_version=METHOD_VERSION,conditions=len(records),passed=sum(r["passed"] for r in records),
                 maxima={k:max(r[k] for r in records) for k in ("projection_residual","eigensystem_max","bloch_max","potential_max")},
                 elapsed_seconds=perf_counter()-start,scope=cfg["scope"])
    (args.output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    manifest=dict(status="complete" if summary["passed"]==len(records) else "complete_with_validation_failures",
                  expected_conditions=len(parameters)*len(cfg["sizes"])*len(cfg["times"]),
                  outputs={p.name:digest(p) for p in args.output.iterdir()})
    (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    if summary["passed"]!=len(records):raise SystemExit(1)


if __name__=="__main__":main()
