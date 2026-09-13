"""Display every reduced sensitivity condition without choosing favorable times."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    source = args.source/"records.jsonl"
    records = [json.loads(line) for line in source.read_text().splitlines()]
    args.output.mkdir(parents=True,exist_ok=False)
    candidates = sorted({r["candidate"] for r in records})
    labels = ["baseline"]+sorted({r["perturbation"] for r in records}-{ "baseline" })
    sizes = sorted({r["N"] for r in records})
    times = sorted({r["time"] for r in records})
    fig, axes = plt.subplots(2,3,figsize=(14,8),layout="constrained")
    for i,candidate in enumerate(candidates):
        rows = [r for r in records if r["candidate"]==candidate]
        for j,(metric,title,aggregate) in enumerate([
                ("coverage","Minimum coverage",min),
                ("moment_max","Worst eight-moment error",max),
                ("balance_binned_relative","Worst relative balance error",max)]):
            values = np.array([[aggregate(r["diagnostics"][metric] for r in rows
                                if r["N"]==n and r["perturbation"]==label) for n in sizes] for label in labels])
            vmax = 4 if metric=="moment_max" else 1
            ax = axes[i,j]
            mesh = ax.imshow(values,aspect="auto",vmin=0,vmax=vmax,cmap="viridis")
            ax.set_title(f"{candidate}: {title}")
            ax.set_xticks(range(len(sizes)),[f"N={n}" for n in sizes])
            ax.set_yticks(range(len(labels)),labels if j==0 else [""]*len(labels),fontsize=8)
            for row in range(len(labels)):
                for column in range(len(sizes)):
                    v=values[row,column]
                    ax.text(column,row,f"{v:.3f}",ha="center",va="center",fontsize=8,
                            color="white" if v<vmax*.5 else "black")
            fig.colorbar(mesh,ax=ax,shrink=.7)
    fig.suptitle("Reduced multichannel sensitivity: extrema over t=10³, 10⁵, 10⁶\nN=5–7; no condition has full coverage; no asymptotic inference",fontsize=12)
    fig.savefig(args.output/"worst_time.png",dpi=180)
    fig.savefig(args.output/"worst_time.pdf")
    plt.close(fig)
    for candidate in candidates:
        with PdfPages(args.output/f"{candidate}_all_profiles.pdf") as pdf:
            for n in sizes:
                for time in times:
                    fig,axes = plt.subplots(len(labels),2,figsize=(9,19),layout="constrained")
                    for label,pair in zip(labels,axes):
                        row=next(r for r in records if r["candidate"]==candidate and r["N"]==n
                                 and r["time"]==time and r["perturbation"]==label)
                        d=row["diagnostics"]
                        p=d["profile"]
                        theta=p["centers"]
                        pair[0].plot(theta,p["density"],label="P",lw=1)
                        pair[0].plot(theta,p["reflected_density"],label="reflected P",lw=1)
                        pair[1].plot(theta,[np.nan if v is None else v for v in p["ratio"]],"o-",ms=2,lw=.7,label="root ratio")
                        pair[1].plot(theta,p["born"],"k--",lw=1,label="Born")
                        pair[1].set_ylim(-.05,1.05)
                        pair[0].set_ylabel(label,fontsize=8)
                        for ax in pair:
                            ax.set_xlim(0,np.pi)
                            ax.set_xlabel("polar angle (radians)",fontsize=8)
                            ax.tick_params(labelsize=8)
                        pair[1].text(.03,.06,f"coverage {d['coverage']:.3f}; moment {d['moment_max']:.3f}",
                                     transform=pair[1].transAxes,fontsize=8)
                    for ax in axes[0]:
                        ax.legend(fontsize=8)
                    fig.suptitle(f"{candidate}, N={n}, t={time:g}: every perturbation\nMissing ratio bins remain undefined; all roots retained",fontsize=12)
                    pdf.savefig(fig)
                    if n==max(sizes) and time==max(times):
                        fig.savefig(args.output/f"{candidate}_N{n}_last_time.png",dpi=120)
                    plt.close(fig)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    manifest=dict(source=str(source),source_sha256=digest(source),script_sha256=digest(Path(__file__)),
                  conditions_displayed=len(records),profile_pages=len(candidates)*len(sizes)*len(times),
                  outputs={p.name:digest(p) for p in args.output.iterdir()})
    (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(f"Displayed {len(records)} conditions on {manifest['profile_pages']} profile pages")


if __name__=="__main__":
    main()
