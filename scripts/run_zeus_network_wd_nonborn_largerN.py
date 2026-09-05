#!/usr/bin/env python3.11
"""Rerun four explicit WD/non-Born network cases at N=13,14,15."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.detector_graphs import detector_graph_edges  # noqa: E402
from core.network_ranked_followup import (  # noqa: E402
    same_seed_larger_n_provenance,
    select_named_cases,
)
from core.network_spacing_summary import (  # noqa: E402
    save_detector_spacing_summary,
)
from core.ranked_born_campaign import simulate_ranked_case  # noqa: E402
from core.sobol_coupling_scan import _atomic_json, _sha256, timestamp  # noqa: E402


DEFAULT_CONFIG = Path("configs/zeus_network_wd_nonborn_largerN.json")


def _load_config(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {"cases", "target_detector_sizes", "storage_mode"}
    missing = required - set(payload)
    if missing:
        raise ValueError(f"missing configuration keys: {sorted(missing)}")
    if tuple(int(value) for value in payload["target_detector_sizes"]) != (13, 14, 15):
        raise ValueError("target_detector_sizes must be exactly [13, 14, 15]")
    if payload["storage_mode"] != "summary":
        raise ValueError("this campaign requires storage_mode='summary'")
    if len(payload["cases"]) != 4:
        raise ValueError("this campaign requires exactly four named cases")
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
    target_sizes = tuple(int(value) for value in config["target_detector_sizes"])
    selected = select_named_cases(list(config["cases"]), repository_root=ROOT)
    total_tasks = len(selected) * len(target_sizes)
    if not 0 <= args.array_index < total_tasks:
        raise ValueError(f"array-index must be in 0..{total_tasks - 1}")
    case_index, size_index = divmod(args.array_index, len(target_sizes))
    item = selected[case_index]
    detector_n = target_sizes[size_index]
    output_root = args.output_root.resolve()
    case_dir = output_root / item.selection_key / f"N{detector_n}"
    plan = {
        "array_index": args.array_index,
        "array_task_count": total_tasks,
        "family": item.family,
        "source_case": item.case.source_case,
        "source_scientific_identity_digest": item.case.scientific_identity_digest,
        "target_detector_n": detector_n,
        "storage_mode": config["storage_mode"],
        "case_dir": str(case_dir),
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return

    output_root.mkdir(parents=True, exist_ok=True)
    if args.array_index == 0:
        _atomic_json(
            output_root / "campaign_manifest.json",
            {
                "created": timestamp(),
                "config_path": str(config_path),
                "config_sha256": _sha256(config_path),
                "config": config,
                "task_count": total_tasks,
                "expected_case_completion_markers": total_tasks,
                "selected": [
                    {
                        "family": selected_item.family,
                        "selection_key": selected_item.selection_key,
                        "source": asdict(selected_item.case),
                        "source_identity_digest": selected_item.case.identity_digest,
                        "source_scientific_identity_digest": (
                            selected_item.case.scientific_identity_digest
                        ),
                        "selection_evidence": config["cases"][index],
                    }
                    for index, selected_item in enumerate(selected)
                ],
            },
        )
    task_dir = output_root / "tasks" / f"task_{args.array_index:03d}"
    task_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(task_dir / "RUNNING.json", {**plan, "started": timestamp()})
    try:
        graph_spec, graph_provenance = same_seed_larger_n_provenance(
            item, detector_n
        )
        graph_edges = detector_graph_edges(detector_n, graph_spec)
        outcome = simulate_ranked_case(
            item.case,
            detector_n=detector_n,
            hz0=item.case.hz0,
            case_dir=case_dir,
            source_index=item.family_index,
            rank_index=0,
            hz0_aliases=("source_hz0",),
            bins=int(config.get("bins", 64)),
            plot_grid=int(config.get("plot_grid", 720)),
            fit_harmonics=int(config.get("fit_harmonics", 32)),
            fit_tolerance=float(config.get("fit_tolerance", 1.0e-10)),
            max_bloch_points=int(config.get("max_bloch_points", 6000)),
            resume=args.resume,
            graph_spec_override=graph_spec,
            graph_provenance=graph_provenance,
            selection_label=f"{item.family} WD/non-Born source case",
            storage_mode=str(config["storage_mode"]),
        )
        spacing_outcome = save_detector_spacing_summary(
            case_dir,
            n_nodes=detector_n,
            edges=graph_edges,
            hz=item.case.hz,
            j=item.case.j,
            jpm=item.case.jpm,
            sector_count=int(config.get("level_spacing_sector_count", 4)),
            histogram_bins=int(config.get("level_spacing_bins", 32)),
            resume=args.resume,
        )
    except BaseException as exc:
        _atomic_json(
            task_dir / "FAILURE.json",
            {
                **plan,
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
                "failed": timestamp(),
            },
        )
        raise
    _atomic_json(
        task_dir / "COMPLETE.json",
        {
            **plan,
            "dynamics_outcome": outcome,
            "detector_spacing_outcome": spacing_outcome,
            "completed": timestamp(),
        },
    )
    (task_dir / "RUNNING.json").unlink(missing_ok=True)
    (task_dir / "FAILURE.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
