"""Correlation-aware uncertainty from resampling whole saved time blocks."""
from __future__ import annotations
import argparse,csv
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import numpy as np
from core.born import born_ratio_from_radii

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--replicates',type=int,default=1000);p.add_argument('--seed',type=int,default=20260712);a=p.parse_args();rng=np.random.default_rng(a.seed); rows=[]
 for case in sorted(a.root.glob('N*/hz_*')):
  files=sorted(case.glob('raw_*.npz'))
  blocks=[np.abs(np.load(f)['eigenvalues']) for f in files]
  if len(blocks)<2: continue
  scores=[]; harmonics=[]
  for _ in range(a.replicates):
   chosen=rng.integers(0,len(blocks),len(blocks)); radii=np.concatenate([blocks[i] for i in chosen]); finite=radii[np.isfinite(radii)]
   scores.append(born_ratio_from_radii(finite,n_theta=100).similarity)
   ph=[]
   for i in chosen:
    raw=np.load(files[i]); phi=raw['phi'];ph.append(phi[np.isfinite(phi)])
   phi=np.concatenate(ph); harmonics.append(abs(np.mean(np.exp(2j*phi))))
  rows.append({'N':int(case.parent.name[1:]),'hz':float(case.name.split('_')[-1]),'time_blocks':len(blocks),'replicates':a.replicates,'S_born_block_mean':float(np.mean(scores)),'S_born_block_se':float(np.std(scores,ddof=1)),'phi_harmonic2_block_mean':float(np.mean(harmonics)),'phi_harmonic2_block_se':float(np.std(harmonics,ddof=1))})
 out=a.root/'time_block_uncertainty.csv'
 with out.open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(out)
if __name__=='__main__':main()
