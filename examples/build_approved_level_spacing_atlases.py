"""Batch-render the approved six-panel level-spacing atlases.

The two collections retain their established physics conventions: the
zero-central-field atlas bins V_ab power by |E_a-E_b|, while the hz0=0.1
collection bins it by detuning from 2|hz0|. Both use logarithmic physical bins
and one separate exact special bin.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig-approved-spacing-atlases"))

from collapse.sobol_coupling_scan import _diagnostics
from examples.build_sobol_flat_ranked_1x6_by_n import (
    CaseRecord, _load_result_arrays, compute_spectral,
)
from examples.build_vab_coupling_level_spacing_sample import render_sample
from examples.build_vab_coupling_raw_flat_ranked_1x6 import load_values
from examples.build_vab_coupling_raw_flat_ranked_2x3 import fit_arrays

HZ0_SOURCE = ROOT / "reports/hz0_sobol_all_flat_ranked_2x3_2026-08-01"
HZ0_OUTPUT = ROOT / "reports/hz0_sobol_all_flat_ranked_2x3_level_spacing_2026-08-02"
VAB_SOURCE = ROOT / "reports/vab_coupling_group_atlas_2026-07-28/flat_ranked_2x3_N14"
VAB_OUTPUT = (
    ROOT / "reports/vab_coupling_group_atlas_2026-07-28"
    / "flat_ranked_2x3_level_spacing_N14_2026-08-02"
)


def _rows(path: Path, limit: int | None) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows.sort(key=lambda row: int(row["rank"]))
    return rows if limit is None else rows[:limit]


def _record_from_hz0(row: dict[str, str], output: Path) -> CaseRecord:
    return CaseRecord(
        family=row["family"], dynamics_n=int(row["dynamics_n"]),
        config_id=row["config_id"], s_born=float(row["s_born"]),
        born_rmse=float(row["born_rmse"]), hz=float(row["hz"]),
        j=float(row["j"]), jpm=float(row["jpm"]), jx=float(row["jx"]),
        jy=float(row["jy"]), source_dir=row["source_dir"],
        rank=int(row["rank"]),
        within_n_rank=int(row.get("within_n_rank") or row["rank"]),
        output_path=str((output / Path(row["output_path"]).name).resolve()),
    )


def _record_from_vab(
    row: dict[str, str],
    output: Path,
    metrics: dict[str, Any],
) -> CaseRecord:
    return CaseRecord(
        family="jy_zero", dynamics_n=int(row["n"]),
        config_id=(
            f"hz={float(row['hz']):g},J={float(row['j']):g},"
            f"Jpm={float(row['jpm']):g}"
        ),
        s_born=float(metrics["S_born"]),
        born_rmse=float(metrics["born_RMSE_occupied"]),
        hz=float(row["hz"]), j=float(row["j"]), jpm=float(row["jpm"]),
        jx=0.01, jy=0.0, source_dir=str(Path(row["raw_path"]).parent),
        rank=int(row["rank"]), within_n_rank=int(row["rank"]),
        output_path=str((output / Path(row["output_path"]).name).resolve()),
    )



def _render_hz0(payload: tuple[dict[str, str], str, int, bool]) -> dict[str, Any]:
    row, output_text, dpi, force = payload
    output = Path(output_text)
    record = _record_from_hz0(row, output)
    target = Path(record.output_path)
    if target.is_file() and not force:
        return {
            **asdict(record), "status": "existing", "collection": "hz0",
            "hz0": float(row["hz0"]),
        }
    spectral = compute_spectral(record)
    arrays = _load_result_arrays(Path(record.source_dir))
    result = render_sample(
        record, spectral, arrays, target, dpi, hz0=float(row["hz0"])
    )
    return {
        **asdict(record), **result, "status": "rendered",
        "collection": "hz0", "hz0": float(row["hz0"]),
        "spectral_validation": spectral.validation,
    }


def _render_vab(payload: tuple[dict[str, str], str, int, bool]) -> dict[str, Any]:
    row, output_text, dpi, force = payload
    output = Path(output_text)
    target = output / Path(row["output_path"]).name
    if target.is_file() and not force:
        return {
            **row, "status": "existing", "collection": "vab",
            "output_path": str(target.resolve()),
        }
    values = load_values(Path(row["raw_path"]))
    metrics, arrays = _diagnostics(values, 64)
    fits, wg, wc = fit_arrays(arrays["theta"])
    arrays.update(fits)
    score_delta = abs(float(metrics["S_born"]) - float(row["computed_s_born"]))
    if score_delta > 1.0e-12:
        raise RuntimeError(f"S_born mismatch {score_delta:.3e}")
    record = _record_from_vab(row, output, metrics)
    spectral = compute_spectral(record)
    result = render_sample(record, spectral, arrays, target, dpi)
    return {
        **asdict(record), **result, "status": "rendered",
        "collection": "vab", "raw_path": row["raw_path"],
        "source_s_born": float(row["computed_s_born"]),
        "source_born_rmse": float(row["computed_born_rmse"]),
        "s_born_delta": score_delta,
        "wg_fourier_discrepancy": float(wg["objective"]),
        "wc_fourier_discrepancy": float(wc["objective"]),
        "spectral_validation": spectral.validation,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({
        key for row in rows for key in row
        if key not in {"spectral_validation", "level_spacing_l1"}
    })
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def _checkpoint(
    output: Path,
    *,
    collection: str,
    completed: int,
    requested: int,
    failures: list[dict[str, Any]],
) -> None:
    payload = {
        "collection": collection, "completed": completed,
        "requested": requested, "failure_count": len(failures),
        "failed_ranks": [row["rank"] for row in failures],
    }
    temporary = output / f".checkpoint.{os.getpid()}.tmp"
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(output / "checkpoint.json")



def build_collection(
    collection: str,
    *,
    output: Path,
    workers: int,
    dpi: int,
    force: bool,
    limit: int | None,
) -> dict[str, Any]:
    if collection == "hz0":
        source = HZ0_SOURCE
        worker = _render_hz0
    elif collection == "vab":
        source = VAB_SOURCE
        worker = _render_vab
    else:
        raise ValueError(f"unknown collection {collection!r}")
    rows = _rows(source / "ranked_index.csv", limit)
    output.mkdir(parents=True, exist_ok=True)
    payloads = [(row, str(output), dpi, force) for row in rows]
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(worker, payload): payload[0] for payload in payloads}
        for count, future in enumerate(as_completed(futures), start=1):
            row = futures[future]
            try:
                results.append(future.result())
            except BaseException as exc:
                failures.append({
                    "rank": int(row["rank"]),
                    "config_id": row.get("config_id", ""),
                    "reason": f"{type(exc).__name__}: {exc}",
                })
            if count == 1 or count % 25 == 0 or count == len(futures):
                print(
                    f"{collection}: completed {count}/{len(futures)}; "
                    f"failures={len(failures)}",
                    flush=True,
                )
                _checkpoint(
                    output, collection=collection, completed=count,
                    requested=len(futures), failures=failures,
                )
    results.sort(key=lambda row: int(row["rank"]))
    failures.sort(key=lambda row: int(row["rank"]))
    _write_csv(output / "ranked_index.csv", results)
    _write_csv(output / "failures.csv", failures)
    manifest = {
        "collection": collection,
        "source": str(source.resolve()),
        "output": str(output.resolve()),
        "rank_definition": "preserved from source ranked_index.csv",
        "requested_records": len(rows),
        "completed_records": len(results),
        "failures": len(failures),
        "workers": workers,
        "dpi": dpi,
        "layout": [
            ["energy proximity", "degeneracy multiplicities", "P/R diagnostics"],
            ["Vab heatmap", "logarithmic Vab energy histogram", "unfolded spacings"],
        ],
        "level_spacing": {
            "spectrum": "full detector-only ND=8 spectrum",
            "degeneracy_handling": "cluster gaps within the established scale-aware tolerance",
            "unfolding": "cubic staircase fit with 10% edge trim",
            "references": ["Poisson", "GOE Wigner surmise", "GUE Wigner surmise"],
            "ratio": "Atas mean min(s_n,s_n+1)/max(s_n,s_n+1)",
            "caveat": "symmetry sectors are mixed; RMT comparison is descriptive",
        },
        "vab_histogram": (
            "logarithmic bins of |Ea-Eb|/(Emax-Emin), with separate strict "
            "degeneracy bin"
            if collection == "vab"
            else "logarithmic bins of ||Ea-Eb|-2|hz0||/(Emax-Emin), with "
                 "separate exact-resonance bin; Ea,Eb are detector-only energies"
        ),
    }
    (output / "render_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--collection", choices=("both", "hz0", "vab"), default="both"
    )
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--hz0-output", type=Path, default=HZ0_OUTPUT)
    parser.add_argument("--vab-output", type=Path, default=VAB_OUTPUT)
    args = parser.parse_args()
    manifests = []
    if args.collection in {"both", "hz0"}:
        manifests.append(build_collection(
            "hz0", output=args.hz0_output, workers=args.workers,
            dpi=args.dpi, force=args.force, limit=args.limit,
        ))
    if args.collection in {"both", "vab"}:
        manifests.append(build_collection(
            "vab", output=args.vab_output, workers=args.workers,
            dpi=args.dpi, force=args.force, limit=args.limit,
        ))
    print(json.dumps(manifests, indent=2))


if __name__ == "__main__":
    main()

