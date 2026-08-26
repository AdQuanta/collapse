#!/usr/bin/env python3.11
"""Scan central-field variants for top-Born cases from the 880-case atlas."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collapse.ranked_born_campaign import (  # noqa: E402
    hz0_variants,
    selected_case_output_dir,
    selection_manifest,
    simulate_ranked_case,
    top_ranked_cases,
)
from collapse.sobol_coupling_scan import _atomic_json, timestamp  # noqa: E402


DEFAULT_CONFIG = Path("configs/zeus_top400_hz0_variants_N14.json")


def _load_config(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "source_root",
        "top_count",
        "target_detector_n",
        "hz0_additive_offsets",
        "include_hz0_zero",
        "shard_size",
    }
    missing = required - set(payload)
    if missing:
        raise ValueError(f"missing configuration keys: {sorted(missing)}")
    return payload


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--batch-index", type=int, required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--output-root", type=Path, required=True)
    result.add_argument("--workers", type=int, default=2)
    result.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    result.add_argument("--dry-run", action="store_true")
    return result


def _worker(payload: tuple) -> dict:
    (
        case,
        detector_n,
        hz0,
        case_dir,
        rank_index,
        aliases,
        resume,
    ) = payload
    return simulate_ranked_case(
        case,
        detector_n=detector_n,
        hz0=hz0,
        case_dir=case_dir,
        source_index=0,
        rank_index=rank_index,
        hz0_aliases=aliases,
        resume=resume,
    )


def main() -> None:
    args = parser().parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    config_path = args.config.resolve()
    config = _load_config(config_path)
    source = (ROOT / config["source_root"]).resolve()
    top_count = int(config["top_count"])
    detector_n = int(config["target_detector_n"])
    shard_size = int(config["shard_size"])
    if top_count < 1 or shard_size < 1 or top_count % shard_size:
        raise ValueError("top_count must be positive and divisible by shard_size")
    batch_count = top_count // shard_size
    if args.batch_index < 0 or args.batch_index >= batch_count:
        raise ValueError(f"batch-index must be in 0..{batch_count - 1}")
    offsets = tuple(float(value) for value in config["hz0_additive_offsets"])
    include_zero = bool(config["include_hz0_zero"])
    selected = top_ranked_cases(source, top_count)
    start = args.batch_index * shard_size
    stop = start + shard_size
    output_root = args.output_root.resolve()
    if args.batch_index == 0:
        output_root.mkdir(parents=True, exist_ok=True)
        _atomic_json(
            output_root / "selection_manifest.json",
            {
                **selection_manifest((source,), top_count),
                "config": config,
                "config_path": str(config_path),
                "hz0_definition": "zero plus hz + each additive offset; duplicates collapsed",
            },
        )
    tasks = []
    task_descriptions = []
    for rank_index in range(start, stop):
        case = selected[rank_index]
        for label, hz0, aliases in hz0_variants(
            case.hz,
            offsets,
            include_zero=include_zero,
        ):
            case_dir = selected_case_output_dir(
                output_root,
                0,
                rank_index,
                detector_n,
                label,
            )
            tasks.append(
                (case, detector_n, hz0, case_dir, rank_index, aliases, args.resume)
            )
            task_descriptions.append(
                {
                    "rank": rank_index + 1,
                    "source_case": case.source_case,
                    "source_S_born": case.source_s_born,
                    "hz": case.hz,
                    "hz0": hz0,
                    "aliases": list(aliases),
                    "case_dir": str(case_dir),
                }
            )
    plan = {
        "batch_index": args.batch_index,
        "rank_start": start + 1,
        "rank_stop": stop,
        "target_N": detector_n,
        "tasks": task_descriptions,
        "checkpoint_policy": "each (rank,hz0) case writes COMPLETE.json immediately",
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    batch_dir = output_root / "batches" / f"batch_{args.batch_index:02d}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(batch_dir / "RUNNING.json", {**plan, "started": timestamp()})
    outcomes = []
    failures = []
    with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
        futures = {pool.submit(_worker, task): task for task in tasks}
        for future in as_completed(futures):
            task = futures[future]
            try:
                outcomes.append(future.result())
            except BaseException as exc:
                failure = {
                    "rank": task[4] + 1,
                    "hz0": task[2],
                    "case_dir": str(task[3]),
                    "exception_type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                }
                failures.append(failure)
            _atomic_json(
                batch_dir / "RUNNING.json",
                {
                    **plan,
                    "outcomes": outcomes,
                    "failures": failures,
                    "updated": timestamp(),
                },
            )
    terminal = {
        **plan,
        "outcomes": outcomes,
        "failures": failures,
        "completed": timestamp(),
    }
    if failures:
        _atomic_json(batch_dir / "FAILURE.json", terminal)
        raise RuntimeError(f"batch {args.batch_index} has {len(failures)} failures")
    _atomic_json(batch_dir / "COMPLETE.json", terminal)
    (batch_dir / "RUNNING.json").unlink(missing_ok=True)
    (batch_dir / "FAILURE.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
