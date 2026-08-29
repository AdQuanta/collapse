#!/usr/bin/env python3.11
"""Rerun high/low Born network cases with five new N=12 graph realizations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.network_ranked_followup import (  # noqa: E402
    resampled_graph_spec,
    select_all_families,
    selection_manifest,
)
from core.ranked_born_campaign import simulate_ranked_case  # noqa: E402
from core.sobol_coupling_scan import _atomic_json, timestamp  # noqa: E402


DEFAULT_CONFIG = Path("configs/zeus_network_extremes_resampled_N12.json")


def _load_config(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "families",
        "count_per_tail",
        "realizations_per_case",
        "cases_per_array_task",
        "target_detector_n",
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
    count_per_tail = int(config["count_per_tail"])
    realizations = int(config["realizations_per_case"])
    cases_per_task = int(config["cases_per_array_task"])
    detector_n = int(config["target_detector_n"])
    if detector_n != 12:
        raise ValueError("this campaign requires target_detector_n=12")
    if realizations < 1 or cases_per_task < 1:
        raise ValueError("realizations_per_case and cases_per_array_task must be positive")
    selected = select_all_families(
        list(config["families"]),
        repository_root=ROOT,
        count_per_tail=count_per_tail,
    )
    if len(selected) % cases_per_task:
        raise ValueError("selected case count must be divisible by cases_per_array_task")
    total_tasks = len(selected) // cases_per_task
    if not 0 <= args.array_index < total_tasks:
        raise ValueError(f"array-index must be in 0..{total_tasks - 1}")
    start = args.array_index * cases_per_task
    assigned = selected[start : start + cases_per_task]
    output_root = args.output_root.resolve()
    plan = {
        "array_index": args.array_index,
        "global_case_start": start,
        "global_case_stop_exclusive": start + cases_per_task,
        "target_detector_n": detector_n,
        "realizations_per_case": realizations,
        "assigned_cases": [
            {
                "selection_key": item.selection_key,
                "source_case": item.case.source_case,
                "source_S_born": item.case.source_s_born,
            }
            for item in assigned
        ],
        "checkpoint_policy": "every realization writes its own COMPLETE.json",
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    output_root.mkdir(parents=True, exist_ok=True)
    if args.array_index == 0:
        _atomic_json(
            output_root / "selection_manifest.json",
            {
                **selection_manifest(selected),
                "config": config,
                "config_path": str(config_path),
            },
        )
    task_dir = output_root / "tasks" / f"task_{args.array_index:03d}"
    task_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(task_dir / "RUNNING.json", {**plan, "started": timestamp()})
    outcomes = []
    try:
        for item in assigned:
            for realization_index in range(realizations):
                graph_spec, graph_provenance = resampled_graph_spec(
                    item, realization_index
                )
                case_dir = (
                    output_root
                    / item.selection_key
                    / f"realization_{realization_index + 1:02d}"
                    / "N12"
                )
                outcome = simulate_ranked_case(
                    item.case,
                    detector_n=detector_n,
                    hz0=item.case.hz0,
                    case_dir=case_dir,
                    source_index=item.family_index,
                    rank_index=item.cohort_rank - 1,
                    hz0_aliases=("source_hz0",),
                    resume=args.resume,
                    graph_spec_override=graph_spec,
                    graph_provenance={
                        **graph_provenance,
                        "family": item.family,
                        "cohort": item.cohort,
                        "cohort_rank": item.cohort_rank,
                    },
                    selection_label=(
                        f"{item.family} {item.cohort} S_born rank "
                        f"{item.cohort_rank}, graph realization "
                        f"{realization_index + 1}"
                    ),
                )
                outcomes.append(outcome)
                _atomic_json(
                    task_dir / "RUNNING.json",
                    {**plan, "outcomes": outcomes, "updated": timestamp()},
                )
    except BaseException as exc:
        _atomic_json(
            task_dir / "FAILURE.json",
            {
                **plan,
                "outcomes_saved_before_failure": outcomes,
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
                "failed": timestamp(),
            },
        )
        raise
    _atomic_json(
        task_dir / "COMPLETE.json",
        {**plan, "outcomes": outcomes, "completed": timestamp()},
    )
    (task_dir / "RUNNING.json").unlink(missing_ok=True)
    (task_dir / "FAILURE.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
