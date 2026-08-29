"""Render the full-coupling hz0=0.1 Sobol campaign as ranked 2x3 figures."""

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
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig-hz0-flat-2x3"))

from scripts.build_hz0_resonance_sample_2x3 import render_case_2x3  # noqa: E402
from scripts.build_sobol_flat_ranked_1x6_by_n import (  # noqa: E402
    CaseRecord,
    _load_result_arrays,
    compute_spectral,
    inventory,
)


SOURCES = (
    ("full_coupling", ROOT / "work/zeus_sobol_hz0_0p1_N15_20260731_175938"),
)
DEFAULT_OUTPUT = ROOT / "reports/hz0_sobol_full_coupling_flat_ranked_2x3_2026-08-01"


def _inventory_all(output: Path) -> tuple[list[tuple[CaseRecord, float, str]], list[dict[str, Any]]]:
    candidates: list[tuple[CaseRecord, float, str]] = []
    unavailable: list[dict[str, Any]] = []
    for tag, source in SOURCES:
        records, missing = inventory(source)
        for row in missing:
            # The downloaded campaign currently contains only the Jy-nonzero family.
            if row.get("family") == "jy_zero" and row.get("reason") == "family directory missing":
                continue
            unavailable.append({"campaign": tag, "source": str(source), **row})
        for record in records:
            metadata = json.loads((Path(record.source_dir) / "metadata.json").read_text(encoding="utf-8"))
            hz0 = float(metadata["hz0"])
            if hz0 != 0.1:
                unavailable.append({
                    "campaign": tag,
                    "source": str(source),
                    "config_id": record.config_id,
                    "reason": f"unexpected hz0={hz0}",
                })
                continue
            candidates.append((record, hz0, tag))
    candidates.sort(key=lambda item: (-item[0].s_born, item[2], item[0].config_id))
    ranked: list[tuple[CaseRecord, float, str]] = []
    for rank, (record, hz0, tag) in enumerate(candidates, start=1):
        s_token = f"{record.s_born:.6f}".replace(".", "p")
        filename = f"rank_{rank:04d}__{tag}__{record.config_id}__Sborn_{s_token}.png"
        ranked.append((CaseRecord(**{
            **asdict(record),
            "rank": rank,
            "within_n_rank": rank,
            "output_path": str((output / filename).resolve()),
        }), hz0, tag))
    return ranked, unavailable


def _render(payload: tuple[dict[str, Any], float, str, int, int, bool]) -> dict[str, Any]:
    record_data, hz0, tag, dpi, max_bloch_points, force = payload
    record = CaseRecord(**record_data)
    output_path = Path(record.output_path)
    if output_path.is_file() and not force:
        return {
            **asdict(record),
            "campaign": tag,
            "hz0": hz0,
            "status": "existing",
            "output_path": str(output_path),
        }
    spectral = compute_spectral(record)
    arrays = _load_result_arrays(Path(record.source_dir))
    result = render_case_2x3(
        record,
        spectral,
        arrays,
        output=Path(record.output_path),
        force=force,
        dpi=dpi,
        max_bloch_points=max_bloch_points,
        hz0=hz0,
    )
    return {
        **asdict(record),
        "campaign": tag,
        "hz0": hz0,
        **result,
        "spectral_validation": spectral.validation,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row if key != "spectral_validation"})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def build(output: Path, workers: int, dpi: int, max_bloch_points: int, force: bool) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    ranked, unavailable = _inventory_all(output)
    payloads = [
        (asdict(record), hz0, tag, dpi, max_bloch_points, force)
        for record, hz0, tag in ranked
    ]
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(_render, payload): payload for payload in payloads}
        for count, future in enumerate(as_completed(futures), start=1):
            record_data, _, tag, _, _, _ = futures[future]
            try:
                results.append(future.result())
            except BaseException as exc:
                failures.append({
                    "campaign": tag,
                    "config_id": record_data["config_id"],
                    "rank": record_data["rank"],
                    "reason": f"{type(exc).__name__}: {exc}",
                })
            if count == 1 or count % 25 == 0 or count == len(futures):
                print(f"rendered {count}/{len(futures)}; failures={len(failures)}", flush=True)
    results.sort(key=lambda row: int(row["rank"]))
    _write_csv(output / "ranked_index.csv", results)
    _write_csv(output / "unavailable_or_failed.csv", [*unavailable, *failures])
    manifest = {
        "sources": [{"tag": tag, "path": str(path.resolve())} for tag, path in SOURCES],
        "output": str(output.resolve()),
        "rank_definition": "global decreasing finite S_born across the validated campaign results",
        "requested_successful_records": len(ranked),
        "rendered_records": len(results),
        "render_failures": len(failures),
        "unavailable_records": len(unavailable),
        "spectral_scope": "E_a and E_b are eigenvalues of detector H_D only at N_D=8",
        "histogram_definition": "abs(abs(Ea-Eb)-2*abs(hz0))/(Emax-Emin), weighted by normalized |Vab|^2",
        "dpi": dpi,
        "workers": workers,
        "results": results,
        "failures": failures,
    }
    (output / "render_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--max-bloch-points", type=int, default=6000)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    manifest = build(args.output, args.workers, args.dpi, args.max_bloch_points, args.force)
    print(json.dumps({key: value for key, value in manifest.items() if key != "results"}, indent=2))


if __name__ == "__main__":
    main()
