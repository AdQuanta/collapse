#!/usr/bin/env python3.11
"""Rerun one top-Born source case at N=14,15,16,17 with checkpoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collapse.ranked_born_campaign import (  # noqa: E402
    selected_case_output_dir,
    selection_manifest,
    simulate_ranked_case,
    top_ranked_cases,
)
from collapse.sobol_coupling_scan import _atomic_json, timestamp  # noqa: E402


DEFAULT_CONFIG = Path("configs/zeus_top20_last5_largerN.json")


def _load_config(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "source_roots",
        "top_per_source",
        "cases_per_array_task",
        "target_detector_sizes",
    }
    missing = required - set(payload)
    if missing:
        raise ValueError(f"missing configuration keys: {sorted(missing)}")
    return payload


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--array-index", type=int, required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--output-root", type=Path, required=True)
    result.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    result.add_argument("--dry-run", action="store_true")
    return result


def main() -> None:
    args = parser().parse_args()
    config_path = args.config.resolve()
    config = _load_config(config_path)
    sources = [(ROOT / value).resolve() for value in config["source_roots"]]
    top_count = int(config["top_per_source"])
    cases_per_task = int(config["cases_per_array_task"])
    target_sizes = tuple(int(value) for value in config["target_detector_sizes"])
    total_cases = len(sources) * top_count
    if cases_per_task < 1 or total_cases % cases_per_task:
        raise ValueError("total selected cases must be divisible by cases_per_array_task")
    total_tasks = total_cases // cases_per_task
    if args.array_index < 0 or args.array_index >= total_tasks:
        raise ValueError(f"array-index must be in 0..{total_tasks - 1}")
    selected_by_source = [top_ranked_cases(source, top_count) for source in sources]
    global_start = args.array_index * cases_per_task
    global_stop = global_start + cases_per_task
    assigned = []
    for global_index in range(global_start, global_stop):
        source_index, rank_index = divmod(global_index, top_count)
        assigned.append(
            (source_index, rank_index, selected_by_source[source_index][rank_index])
        )
    output_root = args.output_root.resolve()
    if args.array_index == 0:
        output_root.mkdir(parents=True, exist_ok=True)
        _atomic_json(
            output_root / "selection_manifest.json",
            {
                **selection_manifest(sources, top_count),
                "config": config,
                "config_path": str(config_path),
            },
        )
    plan = {
        "array_index": args.array_index,
        "global_case_start": global_start,
        "global_case_stop_exclusive": global_stop,
        "assigned_cases": [
            {
                "source_index": source_index,
                "rank": rank_index + 1,
                "source_case": case.source_case,
                "source_S_born": case.source_s_born,
            }
            for source_index, rank_index, case in assigned
        ],
        "target_detector_sizes": list(target_sizes),
        "checkpoint_policy": (
            "N is the outer loop; every assigned case writes COMPLETE.json "
            "before the task advances"
        ),
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    task_dir = output_root / "tasks" / f"task_{args.array_index:03d}"
    task_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(task_dir / "RUNNING.json", {**plan, "started": timestamp()})
    outcomes = []
    try:
        for detector_n in target_sizes:
            for source_index, rank_index, case in assigned:
                case_dir = selected_case_output_dir(
                    output_root,
                    source_index,
                    rank_index,
                    detector_n,
                )
                outcome = simulate_ranked_case(
                    case,
                    detector_n=detector_n,
                    hz0=case.hz0,
                    case_dir=case_dir,
                    source_index=source_index,
                    rank_index=rank_index,
                    hz0_aliases=("source_hz0",),
                    resume=args.resume,
                )
                outcomes.append(outcome)
                _atomic_json(
                    task_dir / "RUNNING.json",
                    {**plan, "outcomes": outcomes, "updated": timestamp()},
                )
    except BaseException as exc:
        failure = {
            **plan,
            "outcomes_saved_before_failure": outcomes,
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
            "failed": timestamp(),
        }
        _atomic_json(task_dir / "FAILURE.json", failure)
        raise
    _atomic_json(
        task_dir / "COMPLETE.json",
        {**plan, "outcomes": outcomes, "completed": timestamp()},
    )
    (task_dir / "RUNNING.json").unlink(missing_ok=True)
    (task_dir / "FAILURE.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
