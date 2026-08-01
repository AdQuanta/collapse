"""Build the Born-ranked 2x3 atlas for the 880 raw anisotropic cases."""
from __future__ import annotations
import argparse, csv, json, os, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/".mplconfig-vab-raw-2x3"))
import numpy as np
from collapse.sobol_coupling_scan import PERIOD, _diagnostics, _fit_one, _folded_density
from examples.build_sobol_flat_ranked_1x6_by_n import CaseRecord, compute_spectral
from examples.build_vab_coupling_raw_flat_ranked_1x6 import RawCase, inventory, load_values
from examples.ranked_atlas_2x3 import render_case_2x3

CAMPAIGN=ROOT/"work"/"zeus_single_pixel_anisotropic_20260718_130606"
INDEX=ROOT/"reports"/"vab_activation_all_cases_2026-07-27"/"data"/"atlas_cases.csv"
OUTPUT=ROOT/"reports"/"vab_coupling_group_atlas_2026-07-28"/"flat_ranked_2x3_N14"

def fit_arrays(theta):
    augmented=np.concatenate([theta,(-theta)%PERIOD])
    wg=_fit_one(augmented,"wrapped_gaussian",32,1e-10)
    wc=_fit_one(augmented,"wrapped_cauchy",32,1e-10)
    dense=np.linspace(0.0,np.pi,720)
    return {
        "fit_grid":dense,
        "wg_density":_folded_density(dense,wg),
        "wc_density":_folded_density(dense,wc),
    },wg,wc

def render(case,force,dpi,max_bloch):
    metrics,arrays=_diagnostics(load_values(Path(case.raw_path)),64)
    fits,wg,wc=fit_arrays(arrays["theta"]); arrays.update(fits)
    delta=abs(float(metrics["S_born"])-case.source_s_born)
    if delta>1e-12: raise RuntimeError(f"S_born mismatch {delta:.3e}")
    record=CaseRecord(
        family="jy_zero",dynamics_n=case.n,
        config_id=f"hz={case.hz:g},J={case.j:g},Jpm={case.jpm:g}",
        s_born=float(metrics["S_born"]),born_rmse=float(metrics["born_RMSE_occupied"]),
        hz=case.hz,j=case.j,jpm=case.jpm,jx=0.01,jy=0.0,source_dir=str(Path(case.raw_path).parent),
        rank=case.rank,within_n_rank=case.rank,output_path=case.output_path,
    )
    spectral=compute_spectral(record)
    result=render_case_2x3(
        record,spectral,arrays,output=Path(case.output_path),force=force,dpi=dpi,max_bloch_points=max_bloch,
    )
    return {
        **asdict(case),**result,
        "computed_s_born":record.s_born,"computed_born_rmse":record.born_rmse,"s_born_delta":delta,
        "wg_fourier_discrepancy":float(wg["objective"]),"wc_fourier_discrepancy":float(wc["objective"]),
        "fit_preference_fourier":"wrapped_gaussian" if wg["objective"]<wc["objective"] else "wrapped_cauchy" if wc["objective"]<wg["objective"] else "tie",
        "degeneracy_tolerance":spectral.degeneracy_tolerance,"spectral_validation":spectral.validation,
    }

def write_csv(path,rows):
    if not rows: path.write_text("",encoding="utf-8"); return
    fields=sorted({k for r in rows for k in r if k!="spectral_validation"})
    with path.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,"") for k in fields})

def build(index,campaign,output,workers,force,dpi,max_bloch,limit):
    cases,unavailable=inventory(index,campaign,output)
    if limit is not None: cases=cases[:limit]
    output.mkdir(parents=True,exist_ok=True)
    results,failures=[],[]
    with ProcessPoolExecutor(max_workers=max(1,workers)) as pool:
        futures={pool.submit(render,c,force,dpi,max_bloch):c for c in cases}
        for count,future in enumerate(as_completed(futures),1):
            case=futures[future]
            try: results.append(future.result())
            except Exception as exc: failures.append({**asdict(case),"reason":f"{type(exc).__name__}: {exc}"})
            if count==1 or count%25==0 or count==len(futures):
                print(f"completed {count}/{len(futures)}; failures={len(failures)}",flush=True)
    results.sort(key=lambda r:int(r["rank"])); failures.sort(key=lambda r:int(r.get("rank",0)))
    write_csv(output/"ranked_index.csv",results); write_csv(output/"unavailable_cases.csv",[*unavailable,*failures])
    manifest={
        "source_index":str(index.resolve()),"traced_raw_root":str((campaign/"raw"/"N14").resolve()),
        "output":str(output.resolve()),"completed_records":len(results),"render_failures":len(failures),
        "unavailable_from_index":len(unavailable),"rank_definition":"decreasing S_born",
        "layout":[
            ["energy difference heatmap","multiplicity histogram","P/R diagnostics with WG/WC"],
            ["Vab heatmap","Vab weight by normalized energy difference","Bloch sphere"],
        ],
        "gap_weight_definition":"A separate strict-degeneracy bin contains all |E_a-E_b|<=epsilon_deg (including a=b). Remaining pairs use delta_ab=|E_a-E_b|/(E_max-E_min) for nonzero bandwidth and 40 equal-width bins; zero bandwidth puts all weight in the degeneracy bin. W_deg+sum_k W_k=1.",
        "all_multiplicities_explicitly_ticked":True,"detector_n":8,"dynamics_n":14,"dpi":dpi,
    }
    (output/"render_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (output/"README.md").write_text(
        "# Born-ranked anisotropic 2x3 atlas\n\n"
        "Every multiplicity shown in either histogram has an explicit numbered tick.\n\n"
        "The Vab histogram has a separate strict-degeneracy bin for |E_a-E_b|<=epsilon_deg (including diagonal elements), followed by 40 nondegenerate bins in delta_ab=|E_a-E_b|/(E_max-E_min). All bars together sum to one.\n",
        encoding="utf-8",
    )
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--index",type=Path,default=INDEX); p.add_argument("--campaign",type=Path,default=CAMPAIGN)
    p.add_argument("--output",type=Path,default=OUTPUT); p.add_argument("--workers",type=int,default=min(8,os.cpu_count() or 1))
    p.add_argument("--dpi",type=int,default=160); p.add_argument("--max-bloch-points",type=int,default=5000)
    p.add_argument("--limit",type=int); p.add_argument("--force",action="store_true")
    a=p.parse_args(); print(json.dumps(build(a.index,a.campaign,a.output,a.workers,a.force,a.dpi,a.max_bloch_points,a.limit),indent=2))
if __name__=="__main__": main()





