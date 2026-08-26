#!/usr/bin/env python3.11
"""Scan central-field variants for the top Born-ranked network cases.

The four source graph families are ranked independently by their stored
canonical ``S_born``.  Every rerun keeps the source N=12 Hamiltonian
parameters, graph-generator specification, graph seed, and hence exact edge
set fixed; only the central longitudinal field ``hz0`` changes.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "collapse_matplotlib_cache"),
)

from collapse.detector_graphs import detector_graph_edges  # noqa: E402
from collapse.network_ranked_followup import (  # noqa: E402
    select_top_all_families,
    top_selection_manifest,
)
from collapse.ranked_born_campaign import (  # noqa: E402
    graph_spec_for_case,
    hz0_variants,
    simulate_ranked_case,
)
from collapse.sobol_coupling_scan import _atomic_json, timestamp  # noqa: E402


DEFAULT_CONFIG = Path("configs/zeus_network_top_hz0_variants_N12.json")


def _load_config(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "families",
        "top_count_per_family",
        "target_detector_n",
        "hz0_additive_offsets",
        "include_hz0_zero",
        "cases_per_array_task",
    }
    missing = required - set(payload)
    if missing:
        raise ValueError(f"missing configuration keys: {sorted(missing)}")
    return payload


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--array-index", type=int)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--output-root", type=Path)
    result.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    result.add_argument("--dry-run", action="store_true")
    result.add_argument(
        "--describe",
        action="store_true",
        help="validate selection and print campaign cardinality without running",
    )
    return result


def _exact_source_graph(item, detector_n: int):
    if item.case.source_n != detector_n:
        raise ValueError(
            "exact graph reuse requires target_detector_n to equal source N; "
            f"got source N={item.case.source_n}, target N={detector_n}"
        )
    graph_spec = graph_spec_for_case(item.case)
    generated_edges = detector_graph_edges(detector_n, graph_spec)
    source_graph = item.case.source_graph_metadata or {}
    raw_edges = source_graph.get("edges_zero_based")
    if raw_edges is not None:
        saved_edges = tuple(
            sorted(tuple(int(value) for value in edge) for edge in raw_edges)
        )
        if saved_edges != generated_edges:
            raise ValueError(
                f"saved graph is not reproduced for {item.case.source_case}"
            )
        validation = "saved edge list exactly reproduced"
    else:
        validation = "source edge list absent; deterministic saved spec and seed reused"
    provenance = {
        "mode": "exact_source_graph_same_N",
        "source_detector_n": item.case.source_n,
        "target_detector_n": detector_n,
        "source_graph_spec": asdict(graph_spec),
        "source_graph_seed": graph_spec.seed,
        "edge_count": len(generated_edges),
        "edge_validation": validation,
        "is_same_edge_set_as_source": raw_edges is not None,
        "note": "Only hz0 changes across variants; graph and all other parameters are fixed.",
    }
    return graph_spec, provenance


def _campaign(config: dict):
    top_count = int(config["top_count_per_family"])
    cases_per_task = int(config["cases_per_array_task"])
    detector_n = int(config["target_detector_n"])
    offsets = tuple(float(value) for value in config["hz0_additive_offsets"])
    include_zero = bool(config["include_hz0_zero"])
    if top_count < 1 or cases_per_task < 1:
        raise ValueError("top_count_per_family and cases_per_array_task must be positive")
    selected = select_top_all_families(
        list(config["families"]),
        repository_root=ROOT,
        count_per_family=top_count,
    )
    if len(selected) % cases_per_task:
        raise ValueError("selected case count must be divisible by cases_per_array_task")
    for item in selected:
        _exact_source_graph(item, detector_n)
    variants_by_case = {
        item.selection_key: hz0_variants(
            item.case.hz,
            offsets,
            include_zero=include_zero,
        )
        for item in selected
    }
    return (
        selected,
        variants_by_case,
        detector_n,
        cases_per_task,
        len(selected) // cases_per_task,
    )


def main() -> None:
    args = parser().parse_args()
    config_path = args.config.resolve()
    config = _load_config(config_path)
    selected, variants_by_case, detector_n, cases_per_task, array_tasks = _campaign(
        config
    )
    total_simulations = sum(
        len(variants_by_case[item.selection_key]) for item in selected
    )
    description = {
        "families": [str(item["name"]) for item in config["families"]],
        "top_count_per_family": int(config["top_count_per_family"]),
        "selected_configurations": len(selected),
        "target_detector_n": detector_n,
        "cases_per_array_task": cases_per_task,
        "array_tasks": array_tasks,
        "total_simulations": total_simulations,
        "hz0_definition": (
            "hz0=0 plus hz+offset for every configured additive offset; "
            "numerical duplicates collapse per source case"
        ),
        "graph_policy": "exact saved N=12 graph realization reused",
    }
    if args.describe:
        print(json.dumps(description, indent=2))
        return
    if args.array_index is None or args.output_root is None:
        raise ValueError("--array-index and --output-root are required unless --describe")
    if not 0 <= args.array_index < array_tasks:
        raise ValueError(f"array-index must be in 0..{array_tasks - 1}")

    start = args.array_index * cases_per_task
    assigned = selected[start : start + cases_per_task]
    output_root = args.output_root.resolve()
    plan = {
        **description,
        "array_index": args.array_index,
        "global_case_start": start,
        "global_case_stop_exclusive": start + cases_per_task,
        "assigned_cases": [
            {
                "selection_key": item.selection_key,
                "family": item.family,
                "family_rank": item.cohort_rank,
                "source_case": item.case.source_case,
                "source_S_born": item.case.source_s_born,
                "hz": item.case.hz,
                "hz0_variants": [
                    {"label": label, "hz0": hz0, "aliases": list(aliases)}
                    for label, hz0, aliases in variants_by_case[item.selection_key]
                ],
            }
            for item in assigned
        ],
        "checkpoint_policy": "every (source configuration, hz0) writes COMPLETE.json",
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return

    output_root.mkdir(parents=True, exist_ok=True)
    if args.array_index == 0:
        _atomic_json(
            output_root / "selection_manifest.json",
            {
                **top_selection_manifest(selected),
                "config": config,
                "config_path": str(config_path),
                **description,
            },
        )
    task_dir = output_root / "tasks" / f"task_{args.array_index:03d}"
    task_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(task_dir / "RUNNING.json", {**plan, "started": timestamp()})
    outcomes = []
    try:
        simulation_index = 0
        assigned_total = sum(
            len(variants_by_case[item.selection_key]) for item in assigned
        )
        for item in assigned:
            graph_spec, graph_provenance = _exact_source_graph(item, detector_n)
            for label, hz0, aliases in variants_by_case[item.selection_key]:
                simulation_index += 1
                case_dir = (
                    output_root
                    / item.selection_key
                    / f"N{detector_n}"
                    / f"hz0_{label}"
                )
                print(
                    f"[{simulation_index}/{assigned_total}] family={item.family} "
                    f"rank={item.cohort_rank} source_S_born={item.case.source_s_born:.6f} "
                    f"hz={item.case.hz:.12g} hz0={hz0:.12g} aliases={','.join(aliases)}",
                    flush=True,
                )
                outcome = simulate_ranked_case(
                    item.case,
                    detector_n=detector_n,
                    hz0=hz0,
                    case_dir=case_dir,
                    source_index=item.family_index,
                    rank_index=item.cohort_rank - 1,
                    hz0_aliases=aliases,
                    resume=args.resume,
                    graph_spec_override=graph_spec,
                    graph_provenance={
                        **graph_provenance,
                        "family": item.family,
                        "family_rank": item.cohort_rank,
                    },
                    selection_label=(
                        f"{item.family} highest S_born rank {item.cohort_rank}; "
                        f"hz0 variant {label}"
                    ),
                )
                outcomes.append(outcome)
                _atomic_json(
                    task_dir / "RUNNING.json",
                    {**plan, "outcomes": outcomes, "updated": timestamp()},
                )
                print(
                    f"[{simulation_index}/{assigned_total}] status={outcome['status']} "
                    f"case_dir={case_dir}",
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


if __name__ == "__main__":
    main()
