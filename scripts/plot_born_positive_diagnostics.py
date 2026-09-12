"""Plot saved positive multichannel leads and reduced return-dynamics checks."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born import born_ratio_from_theta
from core.born_reciprocity import born_moment_residuals, cosine_moments
from core.polar_diagnostic_plotting import plot_polar_diagnostic_grid


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/"configs/born_positive_diagnostics_2026-09-12.json")
    parser.add_argument("--data-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    if cfg["schema_version"] != 1 or cfg["theta_bins"] != 64:
        raise ValueError("requires schema 1 and the unchanged 64-bin diagnostic")
    args.output.mkdir(parents=True, exist_ok=False)
    hashes, metrics = {}, []

    def remember(relative: str) -> Path:
        path = args.data_root/relative
        hashes[relative] = digest(path)
        return path

    def profile(theta: np.ndarray, label: str, **metadata: object) -> dict:
        moments = cosine_moments(theta, 16)
        residuals = born_moment_residuals(moments)
        polar = born_ratio_from_theta(theta, np.pi-theta, n_theta=64)
        edges = np.linspace(0, np.pi, 65)
        counts, reflected = polar.counts_0, polar.counts_1
        occupied = counts+reflected > 0
        ratio = np.where(occupied, polar.ratio, np.nan)
        error = ratio[occupied]-polar.born[occupied]
        density, other = counts/(len(theta)*np.diff(edges)), reflected/(len(theta)*np.diff(edges))
        if not np.isclose(np.dot(density, np.diff(edges)), 1, rtol=0, atol=2e-14):
            raise ArithmeticError("density normalization failed")
        record = dict(
            **metadata, label=label, root_count=len(theta), coverage=float(occupied.mean()),
            occupied_rmse=float(np.sqrt(np.mean(error**2))),
            global_rmse=float(np.sqrt(np.mean(error**2))) if np.all(occupied) else None,
            global_linf=float(max(abs(error))) if np.all(occupied) else None,
            moments=moments.tolist(), moment_residuals=residuals.tolist(),
            moment_max=float(max(abs(residuals))),
            S_born_100=born_ratio_from_theta(theta, np.pi-theta).similarity,
        )
        metrics.append(record)
        return dict(**record, edges=edges, centers=(edges[:-1]+edges[1:])/2,
                    density=density, reflected_density=other, ratio=ratio)

    study = cfg["return_study"]
    records = json.loads(remember(study+"/records.json").read_text())
    remember(study+"/summary.json")
    with np.load(remember(study+"/angles.npz"), allow_pickle=False) as angles:
        for topology in ("ring", "chain"):
            for n in sorted({r["N"] for r in records if r["topology"] == topology}):
                selected = [r for r in records if r["N"] == n and r["topology"] == topology]
                rows = []
                for time in sorted({r["time"] for r in selected}):
                    profiles = []
                    for row in sorted((r for r in selected if r["time"] == time), key=lambda r: r["eta"]):
                        eta = row["eta"]
                        key = f"{topology}_N{n}_eta{eta}_t{time}_theta"
                        result = profile(angles[key], f"eta={eta:g}", family="return_verification",
                                         topology=topology, N=n, time=time, eta=eta, coupling=row["coupling"])
                        if abs(result["occupied_rmse"]-row["occupied_rmse"]) > 1e-12:
                            raise ArithmeticError("saved return-study ratio does not reproduce")
                        profiles.append(result)
                    rows.append(dict(title=f"t={time:g}", profiles=profiles))
                plot_polar_diagnostic_grid(args.output/f"return_{topology}_N{n}", rows,
                                           title=f"Reduced {topology}, N={n}: full propagator; 64 bins; no smoothing")

    remember(cfg["positive_source_generator"])
    for case in cfg["positive_cases"]:
        rows = []
        for n in case["sizes"]:
            directory = cfg["positive_base"]+f"/N{n}/"+case["id"]
            complete = json.loads(remember(directory+"/COMPLETE.json").read_text())
            for filename in ("metadata.json", "metrics.json", "validation.json", "raw_results.npz"):
                path = remember(directory+"/"+filename)
                if digest(path) != complete["files"][filename]:
                    raise ArithmeticError(f"source integrity mismatch: {directory}/{filename}")
            meta = json.loads((args.data_root/directory/"metadata.json").read_text())
            saved = json.loads((args.data_root/directory/"metrics.json").read_text())
            src = meta["configuration"]
            for axis in ("x", "y"):
                if not np.isclose(meta[f"J{axis}_effective"], src[f"j{axis}"]/np.sqrt(n), rtol=1e-13, atol=0):
                    raise ArithmeticError("collective normalization mismatch")
            with np.load(args.data_root/directory/"raw_results.npz", allow_pickle=False) as data:
                theta = data["theta"]
                if len(theta) != 2**n:
                    raise ArithmeticError("saved root count does not equal detector dimension")
                result = profile(theta, "Saved roots", family=case["id"], topology="ring", N=n,
                                 time=meta["evolution_time"], source=directory,
                                 native_parameters=src,
                                 phi_harmonic_2=float(abs(np.mean(np.exp(2j*data["phi"])))),
                                 validation_scope="Saved finite roots; no new homogeneous-QZ certification")
                if abs(result["occupied_rmse"]-saved["born_RMSE_occupied"]) > 1e-12:
                    raise ArithmeticError("saved positive-case metric does not reproduce")
                rows.append(dict(title=f"N={n}; t={meta['evolution_time']:g}; RMSE={result['global_rmse']:.4f}",
                                 profiles=[result]))
        plot_polar_diagnostic_grid(args.output/case["id"], rows,
                                   title=f"Positive multichannel ring {case['id']}; 64 bins; no smoothing\n"
                                         f"Native gx={src['jx']:.6g}, gy={src['jy']:.6g}; both divided by sqrt(N)")
    (args.output/"metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False)+"\n")
    provenance = dict(
        config=cfg, config_sha256=digest(args.config), input_hashes=hashes,
        code_hashes={p: digest(ROOT/p) for p in ("scripts/plot_born_positive_diagnostics.py",
                    "core/polar_diagnostic_plotting.py", "core/born.py", "core/born_reciprocity.py")},
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        python=platform.python_version(), numpy=np.__version__,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        outputs={p.name: digest(p) for p in sorted(args.output.iterdir())},
        scope="Post-processing of saved roots; all roots, no pseudocounts, no smoothing, no time averaging",
    )
    (args.output/"provenance.json").write_text(json.dumps(provenance, indent=2)+"\n")
    print(json.dumps([r for r in metrics if r["family"].startswith("config_")], indent=2))


if __name__ == "__main__":
    main()
