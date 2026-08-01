"""Aggregate independently completed resonance-study case directories."""
from __future__ import annotations
import argparse, csv, json, shutil
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument('--input-root',type=Path,nargs='+',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 records=[]
 for source_root in a.input_root:
  for meta in source_root.glob('**/metadata.json'):
   payload=json.loads(meta.read_text(encoding='utf-8')); records.append(payload['summary'])
   config=payload['config']; target=a.out/f"N{config['detector_n']:02d}"/f"hz_{config['hz']:+.3f}"
   if target.exists(): raise SystemExit(f'refusing to overwrite {target}')
   target.parent.mkdir(parents=True,exist_ok=True); shutil.copytree(meta.parent,target)
 if not records: raise SystemExit('no completed case metadata found')
 fields=sorted({k for r in records for k in r if k!='time_diagnostics'})
 a.out.mkdir(parents=True,exist_ok=True)
 with (a.out/'summary.csv').open('w',newline='',encoding='utf-8') as h:
  w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows([{k:v for k,v in r.items() if k!='time_diagnostics'} for r in records])
 (a.out/'summary.json').write_text(json.dumps(records,indent=2,default=str),encoding='utf-8')
 print(f'aggregated {len(records)} runs to {a.out}')
if __name__=='__main__':main()
