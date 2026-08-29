"""Build flat, per-family/per-N Born-ranked 2x3 atlases for Sobol scans."""
from __future__ import annotations
import argparse, csv, json, os, sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig-sobol-2x3"))

from scripts.build_sobol_flat_ranked_1x6_by_n import (
    CaseRecord, FAMILIES, _load_result_arrays, _rank_records,
    compute_spectral, inventory,
)
from scripts.ranked_atlas_2x3 import render_case_2x3

SOURCE = ROOT / "work" / "zeus_sobol_coupling_scans_20260726_200003"
OUTPUT = SOURCE / "flat_ranked_2x3_by_n"

def render_group(payloads, force, dpi, max_bloch):
    records = [CaseRecord(**payload) for payload in payloads]
    spectral = compute_spectral(records[0])
    results = []
    for record in records:
        arrays = _load_result_arrays(Path(record.source_dir))
        result = render_case_2x3(
            record, spectral, arrays, output=Path(record.output_path),
            force=force, dpi=dpi, max_bloch_points=max_bloch,
        )
        results.append({
            **asdict(record), **result,
            "degeneracy_tolerance": spectral.degeneracy_tolerance,
            "spectral_validation": spectral.validation,
        })
    return results

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8"); return
    fields = sorted({key for row in rows for key in row if key != "spectral_validation"})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})

def build(source, output, workers, force, dpi, max_bloch, limit):
    records, unavailable = inventory(source)
    ranked = _rank_records(records, output)
    if limit is not None:
        chosen = []
        for family in FAMILIES:
            for n in sorted({r.dynamics_n for r in ranked if r.family == family}):
                chosen.extend(sorted(
                    (r for r in ranked if r.family == family and r.dynamics_n == n),
                    key=lambda r:r.rank,
                )[:limit])
        ranked = chosen

    groups = defaultdict(list)
    for record in ranked:
        groups[record.spectral_key].append(record)
    for group in groups.values():
        group.sort(key=lambda r:(r.dynamics_n,r.rank))

    results, failures = [], []
    with ProcessPoolExecutor(max_workers=max(1,workers)) as pool:
        futures = {
            pool.submit(render_group,[asdict(r) for r in group],force,dpi,max_bloch): group
            for group in groups.values()
        }
        for count, future in enumerate(as_completed(futures),1):
            group = futures[future]
            try:
                results.extend(future.result())
            except Exception as exc:
                failures.extend({
                    **asdict(r), "reason": f"{type(exc).__name__}: {exc}"
                } for r in group)
            if count == 1 or count % 20 == 0 or count == len(futures):
                print(f"spectral groups {count}/{len(futures)}; failures={len(failures)}",flush=True)

    results.sort(key=lambda r:(r["family"],int(r["dynamics_n"]),int(r["rank"])))
    for family in FAMILIES:
        for n in sorted({r.dynamics_n for r in ranked if r.family == family}):
            rows=[r for r in results if r["family"]==family and int(r["dynamics_n"])==n]
            write_csv(output/family/f"N{n:02d}"/"ranked_index.csv",rows)
    write_csv(output/"unavailable_cases.csv",[*unavailable,*failures])
    manifest={
        "source":str(source.resolve()),"output":str(output.resolve()),
        "completed_records":len(results),"render_failures":len(failures),
        "unavailable_transferred_records":len(unavailable),
        "family_counts":dict(Counter(r["family"] for r in results)),
        "n_counts":{family:dict(Counter(str(r["dynamics_n"]) for r in results if r["family"]==family)) for family in FAMILIES},
        "rank_definition":"independent within each (Jy family,dynamics N), decreasing S_born",
        "layout":[
            ["energy difference heatmap","multiplicity histogram","P/R diagnostics with WG/WC"],
            ["Vab heatmap","Vab weight by normalized energy difference","Bloch sphere"],
        ],
        "gap_weight_definition":"A separate strict-degeneracy bin contains all |E_a-E_b|<=epsilon_deg (including a=b). Remaining pairs use delta_ab=|E_a-E_b|/(E_max-E_min) for nonzero bandwidth and 40 equal-width bins; zero bandwidth puts all weight in the degeneracy bin. W_deg+sum_k W_k=1.",
        "detector_n":8,"dpi":dpi,"results":results,
    }
    output.mkdir(parents=True,exist_ok=True)
    (output/"render_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (output/"README.md").write_text(
        "# Flat per-N Born-ranked Sobol 2x3 atlas\n\n"
        "Each family/N directory is independently ranked by decreasing S_born.\n\n"
        "Rows: energy gaps, multiplicities, diagnostics / Vab, Vab weight by normalized energy difference, Bloch sphere.\n\n"
        "The weight panel has a separate strict-degeneracy bin for |E_a-E_b|<=epsilon_deg (including diagonal elements), followed by 40 equal-width nondegenerate bins in normalized energy difference delta_ab. All bars together sum to one.\n",
        encoding="utf-8",
    )
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=SOURCE); p.add_argument("--output",type=Path,default=OUTPUT)
    p.add_argument("--workers",type=int,default=min(8,os.cpu_count() or 1)); p.add_argument("--dpi",type=int,default=160)
    p.add_argument("--max-bloch-points",type=int,default=6000); p.add_argument("--limit",type=int); p.add_argument("--force",action="store_true")
    a=p.parse_args(); print(json.dumps(build(a.source,a.output,a.workers,a.force,a.dpi,a.max_bloch_points,a.limit),indent=2))

if __name__=="__main__":
    main()





