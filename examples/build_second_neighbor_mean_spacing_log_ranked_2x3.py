"""Render the approved second-neighbor Sobol campaign as a ranked 2x3 atlas."""

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
os.environ.setdefault(
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-second-neighbor-mean-spacing-atlas")
)

from examples.build_second_neighbor_mean_spacing_sample_2x3 import (  # noqa: E402
    SPECTRAL_N,
    render_sample,
)
from examples.build_sobol_flat_ranked_1x6_by_n import (  # noqa: E402
    CaseRecord,
    _load_result_arrays,
    compute_spectral,
    inventory,
)


SOURCE = ROOT / "work" / "zeus_sobol_second_neighbor_hz0_0_N14_20260805_224342"
OUTPUT = (
    ROOT
    / "reports"
    / "second_neighbor_mean_spacing_log_ranked_2x3_N14_2026-08-06"
)


def rank_records(
    source: Path,
    output: Path,
    *,
    expected_hz0: float,
    limit: int | None = None,
) -> tuple[list[CaseRecord], list[dict[str, Any]]]:
    """Rank validated ``jy_zero/N14`` configurations by decreasing S_born."""

    records, unavailable = inventory(source)
    candidates_unchecked = [
        record
        for record in records
        if record.family == "jy_zero" and record.dynamics_n == 14
    ]
    candidates: list[CaseRecord] = []
    for record in candidates_unchecked:
        metadata_path = Path(record.source_dir) / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        actual_hz0 = float(metadata["hz0"])
        if not abs(actual_hz0 - expected_hz0) <= 1.0e-14:
            unavailable.append(
                {
                    "family": record.family,
                    "N": record.dynamics_n,
                    "config_id": record.config_id,
                    "reason": (
                        f"unexpected hz0={actual_hz0}; expected {expected_hz0}"
                    ),
                }
            )
            continue
        candidates.append(record)
    candidates.sort(key=lambda record: (-record.s_born, record.config_id))
    if limit is not None:
        candidates = candidates[: max(0, limit)]
    ranked: list[CaseRecord] = []
    for rank, record in enumerate(candidates, start=1):
        score_token = f"{record.s_born:.6f}".replace(".", "p")
        filename = (
            f"rank_{rank:04d}__{record.config_id}__"
            f"Sborn_{score_token}.png"
        )
        ranked.append(
            CaseRecord(
                **{
                    **asdict(record),
                    "rank": rank,
                    "within_n_rank": rank,
                    "output_path": str((output / filename).resolve()),
                }
            )
        )
    return ranked, unavailable


def _render_one(
    payload: tuple[dict[str, Any], int, bool, float]
) -> dict[str, Any]:
    record_data, dpi, force, hz0 = payload
    record = CaseRecord(**record_data)
    target = Path(record.output_path)
    metadata_path = target.parent / "metadata" / f"{target.stem}.json"
    if target.is_file() and metadata_path.is_file() and not force:
        stored = json.loads(metadata_path.read_text(encoding="utf-8"))
        return {**stored, "status": "existing"}
    spectral = compute_spectral(
        record,
        detector_n=SPECTRAL_N,
        exploit_magnetization=True,
    )
    arrays = _load_result_arrays(Path(record.source_dir))
    rendered = render_sample(
        record,
        spectral,
        arrays,
        target,
        dpi=dpi,
        approval_sample=False,
        hz0=hz0,
    )
    result = {
        **asdict(record),
        **rendered,
        "status": "rendered",
        "degeneracy_tolerance": spectral.degeneracy_tolerance,
        "spectral_validation": spectral.validation,
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = metadata_path.with_name(
        metadata_path.name + f".tmp.{os.getpid()}"
    )
    temporary.write_text(json.dumps(result, indent=2), encoding="utf-8")
    temporary.replace(metadata_path)
    return result


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    excluded = {"spectral_validation", "histogram_edges", "histogram_weights"}
    fields = sorted({key for row in rows for key in row if key not in excluded})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def _checkpoint(
    output: Path,
    *,
    completed: int,
    requested: int,
    results: list[dict[str, Any]],
    failures: list[dict[str, Any]],
) -> None:
    payload = {
        "completed_attempts": completed,
        "requested": requested,
        "successful": len(results),
        "failure_count": len(failures),
        "failed_ranks": sorted(int(row["rank"]) for row in failures),
    }
    temporary = output / f".checkpoint.{os.getpid()}.tmp"
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(output / "checkpoint.json")


def build(
    source: Path,
    output: Path,
    *,
    workers: int,
    dpi: int,
    force: bool,
    limit: int | None,
    hz0: float,
) -> dict[str, Any]:
    """Build the complete ranked atlas, checkpointing every ten attempts."""

    output.mkdir(parents=True, exist_ok=True)
    ranked, unavailable = rank_records(
        source,
        output,
        expected_hz0=hz0,
        limit=limit,
    )
    _write_csv(output / "ranking_plan.csv", [asdict(record) for record in ranked])
    payloads = [(asdict(record), dpi, force, hz0) for record in ranked]
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(_render_one, payload): payload[0] for payload in payloads}
        for completed, future in enumerate(as_completed(futures), start=1):
            record = futures[future]
            try:
                results.append(future.result())
            except BaseException as exc:
                failures.append(
                    {
                        "rank": int(record["rank"]),
                        "config_id": record["config_id"],
                        "source_dir": record["source_dir"],
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                )
            if completed == 1 or completed % 10 == 0 or completed == len(futures):
                print(
                    f"completed {completed}/{len(futures)}; "
                    f"failures={len(failures)}",
                    flush=True,
                )
                _checkpoint(
                    output,
                    completed=completed,
                    requested=len(futures),
                    results=results,
                    failures=failures,
                )
                _write_csv(
                    output / "ranked_index.partial.csv",
                    sorted(results, key=lambda row: int(row["rank"])),
                )

    results.sort(key=lambda row: int(row["rank"]))
    failures.sort(key=lambda row: int(row["rank"]))
    _write_csv(output / "ranked_index.csv", results)
    configuration_unavailable = [
        row for row in unavailable if "config_id" in row
    ]
    non_case_inventory_entries = [
        row for row in unavailable if "config_id" not in row
    ]
    _write_csv(
        output / "unavailable_or_failed.csv",
        [*configuration_unavailable, *failures],
    )
    manifest = {
        "created": "2026-08-06",
        "source": str(source.resolve()),
        "output": str(output.resolve()),
        "rank_definition": (
            "global decreasing finite S_born across validated jy_zero/N14 results; "
            "config_id breaks exact ties"
        ),
        "requested_valid_records": len(ranked),
        "completed_records": len(results),
        "render_failures": len(failures),
        "failed_or_incomplete_source_configurations": len(configuration_unavailable),
        "non_case_inventory_entries": non_case_inventory_entries,
        "spectral_detector_n": SPECTRAL_N,
        "central_field_hz0": hz0,
        "spectral_diagonalization": (
            "exact block diagonalization in all total-magnetization sectors, "
            "followed by global energy sorting"
        ),
        "dpi": dpi,
        "workers": workers,
        "layout": [
            ["energy proximity", "degeneracy multiplicities", "P/R diagnostics"],
            ["Vab heatmap", "mean-spacing log-gap Vab weights", "unfolded spacings"],
        ],
        "vab_histogram": (
            (
                "strict degeneracy bin plus 40 logarithmically spaced bins in "
                "|Ea-Eb|/<s>"
            )
            if hz0 == 0.0
            else (
                "exact-resonance bin plus 40 logarithmically spaced bins in "
                "abs(|Ea-Eb|-2|hz0|)/<s>"
            )
        )
        + ", weighted by normalized |Vab|^2; <s> is the arithmetic mean of "
        "adjacent spacings after numerical degeneracies are clustered",
        "level_spacing": {
            "spectrum": "full detector-only N_D=10 spectrum",
            "degeneracy_handling": (
                "cluster gaps within the established scale-aware tolerance"
            ),
            "unfolding": "cubic staircase fit with 10% edge trim",
            "references": ["Poisson", "GOE Wigner surmise", "GUE Wigner surmise"],
            "caveat": "symmetry sectors are mixed; RMT comparison is descriptive",
        },
        "results": results,
        "failures": failures,
    }
    (output / "render_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    (output / "README.md").write_text(
        "# Second-neighbor Sobol ranked 2x3 atlas\n\n"
        "Validated N=14 configurations are ranked by decreasing S_born. All "
        "detector spectral panels use N_D=10. The Vab-weight panel uses "
        + (
            "a separate strict-degeneracy bin and 40 logarithmic bins in "
            "|Ea-Eb|/<s>. "
            if hz0 == 0.0
            else "a separate exact-resonance bin and 40 logarithmic bins in "
                 "abs(|Ea-Eb|-2|hz0|)/<s>. "
        )
        + "The bottom-right panel shows unfolded level spacings.\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--hz0", type=float, default=0.0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    manifest = build(
        args.source,
        args.output,
        workers=args.workers,
        dpi=args.dpi,
        force=args.force,
        limit=args.limit,
        hz0=args.hz0,
    )
    print(
        json.dumps(
            {key: value for key, value in manifest.items() if key != "results"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
