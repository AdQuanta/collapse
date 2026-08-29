#!/usr/bin/env python3.11
"""Time-average 2^15 samples per saved network case/N with Jx divided by 10."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLBACKEND", "Agg")
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

from core.network_resampled_scaling_campaign import (  # noqa: E402
    campaign_manifest,
    graph_spec_and_provenance,
    load_resampled_network_cases,
)
from core.ranked_born_time_average import (  # noqa: E402
    simulate_ranked_case_time_average,
    validate_evolution_times,
)
from core.sobol_coupling_scan import _atomic_json, timestamp  # noqa: E402


DEFAULT_CONFIG = Path("configs/zeus_network_resampled_jx_div10_N12_15.json")


def _load_config(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "source_campaign_root",
        "expected_sample_count",
        "samples_per_array_task",
        "target_detector_sizes",
        "target_time_averaged_sample_count",
        "evolution_time_step",
        "jx_scale_factor",
    }
    missing = required - set(payload)
    if missing:
        raise ValueError(f"missing configuration keys: {sorted(missing)}")
    return payload


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--array-index", type=int, required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument(
        "--source-root",
        type=Path,
        help="override source_campaign_root from the configuration",
    )
    result.add_argument("--output-root", type=Path, required=True)
    result.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    result.add_argument("--dry-run", action="store_true")
    return result


def main() -> None:
    args = parser().parse_args()
    config_path = args.config.resolve()
    config = _load_config(config_path)
    source_root = (
        args.source_root.resolve()
        if args.source_root is not None
        else (ROOT / str(config["source_campaign_root"])).resolve()
    )
    expected_count = int(config["expected_sample_count"])
    samples_per_task = int(config["samples_per_array_task"])
    target_sizes = tuple(int(value) for value in config["target_detector_sizes"])
    target_sample_count = int(config["target_time_averaged_sample_count"])
    evolution_time_step = float(config["evolution_time_step"])
    jx_scale_factor = float(config["jx_scale_factor"])
    if target_sizes != (12, 13, 14, 15):
        raise ValueError("target_detector_sizes must be exactly [12, 13, 14, 15]")
    if target_sample_count != 2**15:
        raise ValueError("target_time_averaged_sample_count must be exactly 2^15")
    if evolution_time_step != 1.0e6:
        raise ValueError("evolution_time_step must be exactly 1e6")
    evolution_times_by_n: dict[int, tuple[float, ...]] = {}
    for detector_n in target_sizes:
        samples_per_time = 2**detector_n
        if target_sample_count % samples_per_time:
            raise ValueError(
                f"2^{detector_n} samples per time does not divide the target"
            )
        time_count = target_sample_count // samples_per_time
        evolution_times_by_n[detector_n] = validate_evolution_times(
            tuple(evolution_time_step * index for index in range(1, time_count + 1))
        )
    if expected_count != 400:
        raise ValueError("expected_sample_count must be 400")
    if abs(jx_scale_factor - 0.1) > 1.0e-15:
        raise ValueError("jx_scale_factor must be exactly 0.1")
    if samples_per_task < 1 or expected_count % samples_per_task:
        raise ValueError("samples_per_array_task must divide expected_sample_count")

    items = load_resampled_network_cases(
        source_root,
        jx_scale_factor=jx_scale_factor,
        expected_count=expected_count,
    )
    total_tasks = len(items) // samples_per_task
    if not 0 <= args.array_index < total_tasks:
        raise ValueError(f"array-index must be in 0..{total_tasks - 1}")
    start = args.array_index * samples_per_task
    assigned = items[start : start + samples_per_task]
    plan = {
        "array_index": args.array_index,
        "global_sample_start": start,
        "global_sample_stop_exclusive": start + samples_per_task,
        "target_detector_sizes": list(target_sizes),
        "target_time_averaged_sample_count_per_case_and_N": target_sample_count,
        "evolution_times_by_N": {
            f"N{detector_n}": list(evolution_times_by_n[detector_n])
            for detector_n in target_sizes
        },
        "time_counts_by_N": {
            f"N{detector_n}": len(evolution_times_by_n[detector_n])
            for detector_n in target_sizes
        },
        "time_average_definition": (
            "equal-weight mean of per-time P(theta), then "
            "R=P_bar/(P_bar+P_bar_reflected)"
        ),
        "jx_scale_factor": jx_scale_factor,
        "assigned_samples": [
            {
                "sample_key": item.sample_key,
                "source_S_born": item.case.source_s_born,
                "graph_seed": item.case.graph_spec["seed"],
                "original_collective_Jx": item.original_collective_jx,
                "reduced_collective_Jx": item.case.jx,
            }
            for item in assigned
        ],
        "checkpoint_policy": (
            "every sample/N writes COMPLETE.json; N is the outer loop and the "
            "task writes N<N>_COMPLETE.json before advancing"
        ),
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return

    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    print(
        f"[campaign] task={args.array_index}/{total_tasks - 1} "
        f"samples={len(assigned)} global_range={start}:{start + len(assigned)} "
        f"N={','.join(map(str, target_sizes))} output={output_root}",
        flush=True,
    )
    if args.array_index == 0:
        _atomic_json(
            output_root / "campaign_manifest.json",
            {
                **campaign_manifest(
                    items,
                    jx_scale_factor=jx_scale_factor,
                    target_sizes=target_sizes,
                    evolution_times_by_n=evolution_times_by_n,
                    target_time_averaged_sample_count=target_sample_count,
                ),
                "config": config,
                "config_path": str(config_path),
                "source_campaign_root": str(source_root),
            },
        )
    task_dir = output_root / "tasks" / f"task_{args.array_index:03d}"
    task_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(task_dir / "RUNNING.json", {**plan, "started": timestamp()})
    outcomes: list[dict] = []
    try:
        for detector_n in target_sizes:
            evolution_times = evolution_times_by_n[detector_n]
            stage_started = time.perf_counter()
            print(
                f"[campaign] N-stage start task={args.array_index} N={detector_n} "
                f"samples={len(assigned)} times={len(evolution_times)} "
                f"pooled_samples_per_case={target_sample_count}",
                flush=True,
            )
            n_outcomes: list[dict] = []
            for local_index, item in enumerate(assigned):
                print(
                    f"[campaign] sample start task={args.array_index} N={detector_n} "
                    f"sample={local_index + 1}/{len(assigned)} key={item.sample_key}",
                    flush=True,
                )
                graph_spec, graph_provenance = graph_spec_and_provenance(
                    item,
                    detector_n,
                    jx_scale_factor=jx_scale_factor,
                )
                case_dir = output_root / item.sample_key / f"N{detector_n}"
                outcome = simulate_ranked_case_time_average(
                    item.case,
                    detector_n=detector_n,
                    hz0=item.case.hz0,
                    evolution_times=evolution_times,
                    case_dir=case_dir,
                    source_index=start + local_index,
                    rank_index=item.realization_index - 1,
                    hz0_aliases=("source_hz0",),
                    resume=args.resume,
                    graph_spec_override=graph_spec,
                    graph_provenance=graph_provenance,
                    selection_label=(
                        f"{item.selection_key}, graph realization "
                        f"{item.realization_index}, Jx/10"
                    ),
                )
                outcomes.append(outcome)
                n_outcomes.append(outcome)
                print(
                    f"[campaign] sample done task={args.array_index} N={detector_n} "
                    f"sample={local_index + 1}/{len(assigned)} "
                    f"status={outcome['status']} key={item.sample_key}",
                    flush=True,
                )
                _atomic_json(
                    task_dir / "RUNNING.json",
                    {**plan, "outcomes": outcomes, "updated": timestamp()},
                )
            _atomic_json(
                task_dir / f"N{detector_n}_COMPLETE.json",
                {
                    "array_index": args.array_index,
                    "detector_n": detector_n,
                    "outcomes": n_outcomes,
                    "completed": timestamp(),
                },
            )
            print(
                f"[campaign] N-stage complete task={args.array_index} N={detector_n} "
                f"samples={len(n_outcomes)} "
                f"seconds={time.perf_counter() - stage_started:.1f}",
                flush=True,
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
    print(
        f"[campaign] task complete task={args.array_index} outcomes={len(outcomes)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
