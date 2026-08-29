"""Add project-standard S_Born to already saved runs without re-simulating."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
from core.born import born_ratio_from_radii

def main():
 p=argparse.ArgumentParser(); p.add_argument('root',type=Path); a=p.parse_args()
 summary=a.root/'summary.csv'; rows=list(csv.DictReader(summary.open(encoding='utf-8')))
 for row in rows:
  case=a.root/f"N{int(row['N']):02d}"/f"hz_{float(row['hz']):+.3f}"
  eig=np.load(case/'aggregate.npz')['eigenvalues']; radii=np.abs(eig); radii=radii[np.isfinite(radii)]
  row['S_born']=f"{born_ratio_from_radii(radii,n_theta=100).similarity:.16g}"
  raw=np.load(case/'aggregate.npz'); theta=raw['theta']; phi=np.nan_to_num(raw['phi'],nan=0.0); finite=np.isfinite(np.abs(raw['eigenvalues']))
  norm=np.sqrt((np.sin(theta[finite])*np.cos(phi[finite]))**2+(np.sin(theta[finite])*np.sin(phi[finite]))**2+np.cos(theta[finite])**2)
  row['bloch_norm_error_max']=f"{np.max(np.abs(norm-1.0)):.16g}"
 fields=list(rows[0]);
 with summary.open('w',newline='',encoding='utf-8') as h:
  w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(rows)
 print(f'updated {len(rows)} rows in {summary}')
if __name__=='__main__': main()
