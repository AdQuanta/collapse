"""Render all 40 fixed-N network comparisons across the ``hz0`` variants."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import json
import os
from pathlib import Path
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
os.environ.setdefault(
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-network-hz0-variants-all")
)

from examples.build_network_hz0_variants_sample_row import (  # noqa: E402
    DEFAULT_SOURCE,
    DEFAULT_SPECTRAL_N,
    TARGET_N,
    build_sample,
)


DEFAULT_OUTPUT = (
    ROOT
    / "reports"
    / "network_top_hz0_variants_N11_spacings_graph_all_2026-08-20"
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _output_path(output_root: Path, entry: dict[str, Any]) -> Path:
    selection = Path(str(entry["selection_key"]))
    config_id = str(entry["source"]["source_case"]).split("/")[-1]
    return (
        output_root
        / selection.parent.name
        / (
            f"{selection.name}__{config_id}__"
            "N12_hz0_variants_with_N11_spacings_and_graph.png"
        )
    )


def _existing_valid(path: Path) -> bool:
    metadata_path = path.with_suffix(".json")
    if not path.is_file() or not metadata_path.is_file():
        return False
    try:
        metadata = _read_json(metadata_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    hz0_values = [
        float(item["hz0"]) for item in metadata.get("hz0_variants", [])
    ]
    return bool(
        int(metadata.get("target_detector_n", -1)) == TARGET_N
        and int(metadata.get("spectral_detector_n", -1)) == DEFAULT_SPECTRAL_N
        and len(hz0_values) >= 2
        and hz0_values == sorted(hz0_values)
        and metadata.get("output") == str(path.resolve())
    )


def _render_one(payload: tuple[str, str, str, int, bool]) -> dict[str, Any]:
    source_text, selection, output_text, dpi, force = payload
    source = Path(source_text)
    output = Path(output_text)
    started = time.perf_counter()
    if not force and _existing_valid(output):
        metadata = _read_json(output.with_suffix(".json"))
        return {
            "status": "existing",
            "selection": selection,
            "family": metadata["family"],
            "source_rank": metadata["source_rank"],
            "output": str(output.resolve()),
            "hz0_values": [
                float(item["hz0"]) for item in metadata["hz0_variants"]
            ],
            "selected_sector_dimensions": metadata[
                "selected_sector_dimensions"
            ],
            "elapsed_seconds": time.perf_counter() - started,
        }
    result = build_sample(
        source,
        selection,
        output,
        dpi=dpi,
        spectral_n=DEFAULT_SPECTRAL_N,
    )
    return {
        "status": "rendered",
        "selection": selection,
        "family": result["family"],
        "source_rank": result["source_rank"],
        "output": result["output"],
        "hz0_values": [float(item["hz0"]) for item in result["hz0_variants"]],
        "selected_sector_dimensions": result["selected_sector_dimensions"],
        "automorphism_group_order": result["symmetry_resolution"][
            "automorphism_group_order"
        ],
        "elapsed_seconds": time.perf_counter() - started,
    }


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: (
                        json.dumps(value, sort_keys=True)
                        if isinstance(value, (dict, list, tuple))
                        else value
                    )
                    for key, value in row.items()
                }
            )


def build_all(
    source: Path,
    output: Path,
    *,
    workers: int,
    dpi: int,
    force: bool,
) -> dict[str, Any]:
    manifest = _read_json(source / "selection_manifest.json")
    entries = list(manifest["cases"])
    if len(entries) != 40:
        raise ValueError(f"expected 40 selected configurations, found {len(entries)}")
    output.mkdir(parents=True, exist_ok=True)
    payloads = [
        (
            str(source.resolve()),
            str(entry["selection_key"]),
            str(_output_path(output, entry).resolve()),
            dpi,
            force,
        )
        for entry in entries
    ]
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        future_map = {
            pool.submit(_render_one, payload): payload for payload in payloads
        }
        for completed, future in enumerate(as_completed(future_map), start=1):
            payload = future_map[future]
            try:
                results.append(future.result())
            except BaseException as exc:
                failures.append(
                    {
                        "selection": payload[1],
                        "exception_type": type(exc).__name__,
                        "message": str(exc),
                    }
                )
            if completed == 1 or completed % 5 == 0 or completed == len(payloads):
                results.sort(key=lambda row: row["selection"])
                failures.sort(key=lambda row: row["selection"])
                checkpoint = {
                    "completed_attempts": completed,
                    "requested": len(payloads),
                    "successful": len(results),
                    "failed": len(failures),
                    "elapsed_seconds": time.perf_counter() - started,
                    "results": results,
                    "failures": failures,
                }
                _write_json_atomic(output / "checkpoint.json", checkpoint)
                _write_csv(output / "index.partial.csv", results)
                print(
                    f"completed {completed}/{len(payloads)}; "
                    f"successful={len(results)} failed={len(failures)}",
                    flush=True,
                )
    results.sort(key=lambda row: row["selection"])
    failures.sort(key=lambda row: row["selection"])
    summary = {
        "source": str(source.resolve()),
        "output": str(output.resolve()),
        "requested": len(payloads),
        "successful": len(results),
        "failed": len(failures),
        "target_detector_n": TARGET_N,
        "dynamics_columns": (
            "all saved hz0 variants, ordered by increasing numerical hz0"
        ),
        "spectral_detector_n": DEFAULT_SPECTRAL_N,
        "spectral_method": (
            "four largest nonredundant exact sectors after fixed-Hamming-"
            "weight, complete graph-automorphism, half-filling spin-reversal, "
            "and twin-antisymmetric induced-graph resolution"
        ),
        "spectral_independence": (
            "the detector Hamiltonian and its spectrum do not depend on hz0"
        ),
        "graph_policy": (
            "regenerate N_D=11 independently from each saved graph-family "
            "specification and seed; dynamics use the exact saved N=12 graph"
        ),
        "workers": workers,
        "dpi": dpi,
        "elapsed_seconds": time.perf_counter() - started,
        "results": results,
        "failures": failures,
    }
    _write_json_atomic(output / "render_manifest.json", summary)
    _write_csv(output / "index.csv", results)
    _write_csv(output / "failures.csv", failures)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    summary = build_all(
        args.source.resolve(),
        args.output.resolve(),
        workers=args.workers,
        dpi=args.dpi,
        force=args.force,
    )
    print(json.dumps(summary, indent=2))
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
