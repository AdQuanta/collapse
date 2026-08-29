"""Repeat the six-panel Born-ranked analysis for the raw 2026-07-28 Vab atlas."""
from __future__ import annotations
import argparse, csv, json, os, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig-vab-raw-flat"))
import numpy as np
from core.sobol_coupling_scan import PERIOD, _diagnostics, _fit_one, _folded_density
from scripts.build_sobol_flat_ranked_1x6_by_n import CaseRecord, _render_case, compute_spectral

CAMPAIGN = ROOT / "work" / "zeus_single_pixel_anisotropic_20260718_130606"
INDEX = ROOT / "reports" / "vab_activation_all_cases_2026-07-27" / "data" / "atlas_cases.csv"
OUTPUT = ROOT / "reports" / "vab_coupling_group_atlas_2026-07-28" / "flat_ranked_1x6_N14"

@dataclass(frozen=True)
class RawCase:
    ordinal: int; n: int; hz: float; j: float; jpm: float; t: float
    source_s_born: float; source_rmse: float; raw_path: str
    rank: int = 0; output_path: str = ""

def token(x):
    return ("m" if x < 0 else "p") + f"{abs(x):.6g}".replace(".", "p").replace("+", "")

def inventory(index, campaign, output):
    figure_root = (campaign / "figures" / "N14").resolve()
    raw_root = (campaign / "raw" / "N14").resolve()
    cases, unavailable = [], []
    with index.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            diagnostic = Path(row["source_diagnostic"]).resolve()
            try:
                relative = diagnostic.parent.relative_to(figure_root)
            except ValueError:
                unavailable.append({"ordinal": row["ordinal"], "reason": "outside traced campaign"})
                continue
            raw = raw_root / relative / "spectrum_t1000000.npz"
            if not raw.is_file():
                unavailable.append({"ordinal": row["ordinal"], "reason": "raw spectrum missing", "raw_path": str(raw)})
                continue
            cases.append(RawCase(
                int(row["ordinal"]), int(row["dynamics_n"]), float(row["hz"]),
                float(row["j"]), float(row["jpm"]), float(row["evolution_time"]),
                float(row["born_score"]), float(row["born_rmse"]), str(raw),
            ))
    cases.sort(key=lambda c: (-c.source_s_born, c.hz, c.j, c.jpm, c.ordinal))
    ranked = []
    for rank, case in enumerate(cases, 1):
        score = f"{case.source_s_born:.6f}".replace(".", "p")
        name = f"rank_{rank:04d}__hz_{token(case.hz)}__J_{token(case.j)}__Jpm_{token(case.jpm)}__Sborn_{score}.png"
        ranked.append(RawCase(**{**asdict(case), "rank": rank, "output_path": str((output / name).resolve())}))
    return ranked, unavailable

def load_values(path):
    with np.load(path) as data:
        values = np.asarray(data["eigenvalues"], dtype=np.complex128).reshape(-1)
    if not values.size:
        raise ValueError("empty eigenvalue array")
    return values

def render(case, staging_root, force, dpi, max_bloch):
    output = Path(case.output_path)
    if output.is_file() and not force:
        return {**asdict(case), "status": "existing"}
    metrics, arrays = _diagnostics(load_values(Path(case.raw_path)), 64)
    augmented = np.concatenate([arrays["theta"], (-arrays["theta"]) % PERIOD])
    wg = _fit_one(augmented, "wrapped_gaussian", 32, 1e-10)
    wc = _fit_one(augmented, "wrapped_cauchy", 32, 1e-10)
    dense = np.linspace(0.0, np.pi, 720)
    arrays.update({
        "fit_grid": dense,
        "wg_density": _folded_density(dense, wg),
        "wc_density": _folded_density(dense, wc),
    })
    fits = {
        "wrapped_gaussian": {**wg, "fourier_discrepancy": float(wg["objective"])},
        "wrapped_cauchy": {**wc, "fourier_discrepancy": float(wc["objective"])},
        "ranking": {
            "fourier_discrepancy": (
                "wrapped_gaussian" if wg["objective"] < wc["objective"]
                else "wrapped_cauchy" if wc["objective"] < wg["objective"]
                else "tie"
            )
        },
    }
    delta = abs(float(metrics["S_born"]) - case.source_s_born)
    if delta > 1e-12:
        raise RuntimeError(f"S_born mismatch {delta:.3e}")
    record = CaseRecord(
        family="jy_zero", dynamics_n=case.n,
        config_id=f"hz={case.hz:g},J={case.j:g},Jpm={case.jpm:g}",
        s_born=float(metrics["S_born"]), born_rmse=float(metrics["born_RMSE_occupied"]),
        hz=case.hz, j=case.j, jpm=case.jpm, jx=0.01, jy=0.0, source_dir="",
        rank=case.rank, within_n_rank=case.rank, output_path=str(output),
    )
    spectral = compute_spectral(record)
    staging = Path(staging_root) / f"case_{case.rank:04d}_{os.getpid()}"
    staging.mkdir(parents=True, exist_ok=True)
    try:
        names = ("edges","centers","p_theta","p_pi_minus_theta","R","R_occupied","R_born",
                 "bloch_blue","bloch_red","fit_grid","wg_density","wc_density")
        np.savez_compressed(staging / "results.npz", **{name: np.asarray(arrays[name]) for name in names})
        staged = CaseRecord(**{**asdict(record), "source_dir": str(staging)})
        result = _render_case(staged, spectral, force=force, dpi=dpi, max_bloch_points=max_bloch)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    result.update({
        "source_ordinal": case.ordinal, "raw_path": case.raw_path,
        "source_s_born": case.source_s_born, "source_born_rmse": case.source_rmse,
        "computed_s_born": float(metrics["S_born"]),
        "computed_born_rmse": float(metrics["born_RMSE_occupied"]), "s_born_delta": delta,
        "wg_fourier_discrepancy": float(fits["wrapped_gaussian"]["fourier_discrepancy"]),
        "wc_fourier_discrepancy": float(fits["wrapped_cauchy"]["fourier_discrepancy"]),
        "fit_preference_fourier": fits["ranking"]["fourier_discrepancy"],
    })
    return result

def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8"); return
    fields = sorted({key for row in rows for key in row if key != "spectral_validation"})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})

def build(index, campaign, output, workers, dpi, max_bloch, force, limit):
    cases, unavailable = inventory(index, campaign, output)
    if limit is not None:
        cases = cases[:limit]
    output.mkdir(parents=True, exist_ok=True)
    staging = output / ".staging"; staging.mkdir(exist_ok=True)
    results, failures = [], []
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(render, c, str(staging), force, dpi, max_bloch): c for c in cases}
        for count, future in enumerate(as_completed(futures), 1):
            case = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                failures.append({**asdict(case), "reason": f"{type(exc).__name__}: {exc}"})
            if count == 1 or count % 25 == 0 or count == len(futures):
                print(f"completed {count}/{len(futures)}; failures={len(failures)}", flush=True)
    shutil.rmtree(staging, ignore_errors=True)
    results.sort(key=lambda row: int(row["rank"])); failures.sort(key=lambda row: int(row.get("rank", 0)))
    write_csv(output / "ranked_index.csv", results)
    write_csv(output / "unavailable_cases.csv", [*unavailable, *failures])
    manifest = {
        "source_report": str((ROOT/"reports"/"vab_coupling_group_atlas_2026-07-28").resolve()),
        "source_index": str(index.resolve()), "traced_raw_campaign": str(campaign.resolve()),
        "traced_raw_root": str((campaign/"raw"/"N14").resolve()),
        "output_directory": str(output.resolve()),
        "ranking": "decreasing S_born; ties by hz, J, Jpm, source ordinal",
        "figure_layout": ["energy proximity","Vab","multiplicities","m=2 couplings","P/R + WG/WC","Bloch sphere"],
        "indexed_cases": len(cases), "completed_cases": len(results),
        "unavailable_from_index": len(unavailable), "render_failures": len(failures),
        "dpi": dpi, "detector_n": 8, "dynamics_n": 14,
    }
    (output/"render_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (output/"README.md").write_text(
        "# Born-ranked raw-data atlas\n\n"
        + f"Raw source: {manifest['traced_raw_root']}.\n\n"
        + "Images are flat and ranked by decreasing S_born. The six equal-width panes match "
        + "the previous Sobol analysis. Detector heatmaps use N_D=8; dynamics use N=14.\n",
        encoding="utf-8",
    )
    return manifest

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--index", type=Path, default=INDEX); p.add_argument("--campaign", type=Path, default=CAMPAIGN)
    p.add_argument("--output", type=Path, default=OUTPUT); p.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    p.add_argument("--dpi", type=int, default=160); p.add_argument("--max-bloch-points", type=int, default=5000)
    p.add_argument("--limit", type=int); p.add_argument("--force", action="store_true")
    a = p.parse_args()
    print(json.dumps(build(a.index,a.campaign,a.output,a.workers,a.dpi,a.max_bloch_points,a.force,a.limit), indent=2))

if __name__ == "__main__":
    main()


