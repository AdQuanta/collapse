#!/usr/bin/env python3.11
"""Continue the exact ranked ring spacing-study configurations at N=17.

The selection is reconstructed from the two source campaigns and checked
against explicit source-case lists in the configuration.  Each PBS array task
owns two cases.  A case-level COMPLETE.json is written before advancing.

When a physically identical, checksum-valid N=17 result exists in the earlier
larger-N campaign, it is copied into the new self-contained run root and marked
with REUSED_FROM.json.  Pass ``--no-reuse-existing-n17`` to recompute those
cases in a fresh output root.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import traceback
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ranked_born_campaign import (  # noqa: E402
    RankedHamiltonianCase,
    load_ranked_cases,
    simulate_ranked_case,
)
from core.sobol_coupling_scan import _atomic_json, timestamp  # noqa: E402


DEFAULT_CONFIG = Path("configs/zeus_ranked_ring_extremes_N17.json")


@dataclass(frozen=True)
class SelectedCase:
    family_index: int
    family: str
    tail: str
    rank: int
    case: RankedHamiltonianCase
    prior_n17_dir: Path | None

    @property
    def config_id(self) -> str:
        return Path(self.case.source_case).name

    @property
    def label(self) -> str:
        return f"{self.family} {self.tail} rank {self.rank}"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _complete_valid(case_dir: Path) -> bool:
    marker_path = case_dir / "COMPLETE.json"
    if not marker_path.is_file():
        return False
    try:
        marker = _read_json(marker_path)
        files = marker["files"]
        return marker.get("status") == "complete" and all(
            (case_dir / name).is_file()
            and _sha256(case_dir / name) == expected
            for name, expected in files.items()
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def _validate_source_case(case: RankedHamiltonianCase) -> None:
    case_dir = Path(case.source_root) / case.source_case
    marker = _read_json(case_dir / "COMPLETE.json")
    validation = _read_json(case_dir / "validation.json")
    if marker.get("status") != "complete" or not marker.get(
        "validation_passed", False
    ):
        raise ValueError(f"source case lacks a passing completion marker: {case_dir}")
    if not validation.get("passed", False):
        raise ValueError(f"source validation failed: {case_dir}")
    for filename in ("metrics.json", "metadata.json", "validation.json"):
        expected = marker.get("files", {}).get(filename)
        if not expected or _sha256(case_dir / filename) != expected:
            raise ValueError(f"source checksum mismatch for {case_dir / filename}")


def _same_float(left: Any, right: Any) -> bool:
    return math.isclose(float(left), float(right), rel_tol=2.0e-14, abs_tol=1.0e-16)


def _prior_result_matches(
    prior_dir: Path | None,
    selected: SelectedCase,
    target_n: int,
) -> bool:
    if prior_dir is None or not _complete_valid(prior_dir):
        return False
    try:
        metadata = _read_json(prior_dir / "metadata.json")
        source = metadata["source"]
        case = selected.case
        if int(metadata["target_N"]) != target_n:
            return False
        if str(source["source_case"]) != case.source_case:
            return False
        if int(source["source_n"]) != case.source_n:
            return False
        if str(source["connectivity"]) != case.connectivity:
            return False
        if str(source["central_coupling"]) != case.central_coupling:
            return False
        for key, expected in (
            ("hz", case.hz),
            ("hz0", case.hz0),
            ("j", case.j),
            ("jpm", case.jpm),
            ("j2", case.j2),
            ("jpm2", case.jpm2),
            ("jx", case.jx),
            ("jy", case.jy),
            ("evolution_time", case.evolution_time),
        ):
            if not _same_float(source[key], expected):
                return False
        if not _same_float(metadata["hz0"], case.hz0):
            return False
        if not _same_float(metadata["Jx_effective"], case.jx / math.sqrt(target_n)):
            return False
        validation = _read_json(prior_dir / "validation.json")
        return bool(validation.get("passed", False))
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def _copy_prior_result(prior_dir: Path, target_dir: Path) -> dict[str, Any]:
    """Copy one immutable prior result into a portable, self-contained run."""
    if target_dir.exists() and any(target_dir.iterdir()):
        raise FileExistsError(f"cannot reuse into non-empty directory: {target_dir}")
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{target_dir.name}.reuse-", dir=target_dir.parent)
    )
    marker = _read_json(prior_dir / "COMPLETE.json")
    for filename in marker["files"]:
        shutil.copy2(prior_dir / filename, temporary / filename)
    shutil.copy2(prior_dir / "COMPLETE.json", temporary / "COMPLETE.json")
    provenance = {
        "status": "reused_external_N17",
        "copied": timestamp(),
        "prior_result": str(prior_dir.resolve()),
        "prior_complete_sha256": _sha256(prior_dir / "COMPLETE.json"),
        "copy_policy": (
            "All files covered by the prior COMPLETE.json were copied and "
            "retain their original checksums."
        ),
    }
    _atomic_json(temporary / "REUSED_FROM.json", provenance)
    if target_dir.exists():
        target_dir.rmdir()
    temporary.replace(target_dir)
    if not _complete_valid(target_dir):
        raise RuntimeError(f"copied result failed checksum validation: {target_dir}")
    return provenance


def _load_config(path: Path) -> dict[str, Any]:
    config = _read_json(path)
    required = {
        "target_detector_n",
        "count_per_tail",
        "cases_per_array_task",
        "array_size",
        "families",
    }
    missing = required.difference(config)
    if missing:
        raise ValueError(f"missing configuration keys: {sorted(missing)}")
    return config


def select_cases(config: dict[str, Any]) -> list[SelectedCase]:
    """Reconstruct and validate the exact 40 configurations."""
    count = int(config["count_per_tail"])
    target_n = int(config["target_detector_n"])
    prior_root_value = config.get("prior_n17_root")
    prior_root = (
        (ROOT / str(prior_root_value)).resolve()
        if prior_root_value is not None
        else None
    )
    selected: list[SelectedCase] = []
    for family_index, family in enumerate(config["families"]):
        source_root = (ROOT / str(family["source_root"])).resolve()
        ranked = load_ranked_cases(source_root)
        if len(ranked) < 2 * count:
            raise ValueError(f"{source_root} has fewer than {2 * count} valid cases")
        highest = ranked[:count]
        lowest = sorted(
            ranked, key=lambda case: (case.source_s_born, case.source_case)
        )[:count]
        expected_highest = list(family["expected_highest_source_cases"])
        expected_lowest = list(family["expected_lowest_source_cases"])
        if [case.source_case for case in highest] != expected_highest:
            raise ValueError(f"highest-tail selection drift for {family['name']}")
        if [case.source_case for case in lowest] != expected_lowest:
            raise ValueError(f"lowest-tail selection drift for {family['name']}")
        if {case.source_case for case in highest}.intersection(
            case.source_case for case in lowest
        ):
            raise ValueError(f"overlapping tails for {family['name']}")
        for tail, cases in (("highest", highest), ("lowest", lowest)):
            for rank, case in enumerate(cases, start=1):
                _validate_source_case(case)
                if case.source_n != 14:
                    raise ValueError(f"source N is not 14 for {case.source_case}")
                if case.connectivity != "ring" or case.central_coupling != "all":
                    raise ValueError(f"unexpected connectivity for {case.source_case}")
                if not _same_float(case.hz0, 0.0):
                    raise ValueError(f"source hz0 is nonzero for {case.source_case}")
                has_second = bool(case.j2 or case.jpm2)
                if has_second != bool(family["expects_second_neighbor"]):
                    raise ValueError(f"second-neighbor mismatch for {case.source_case}")
                prior_dir = None
                if tail == "highest" and prior_root is not None:
                    prior_dir = (
                        prior_root
                        / str(family["prior_n17_source"])
                        / f"rank_{rank:03d}"
                        / f"N{target_n}"
                    )
                selected.append(
                    SelectedCase(
                        family_index=family_index,
                        family=str(family["name"]),
                        tail=tail,
                        rank=rank,
                        case=case,
                        prior_n17_dir=prior_dir,
                    )
                )
    return selected


def output_dir_for_case(
    output_root: Path,
    selected: SelectedCase,
    detector_n: int,
) -> Path:
    return (
        output_root
        / selected.family
        / selected.tail
        / f"rank_{selected.rank:02d}__{selected.config_id}"
        / f"N{detector_n}"
    )


def _selection_manifest(
    config: dict[str, Any],
    config_path: Path,
    selected: list[SelectedCase],
) -> dict[str, Any]:
    target_n = int(config["target_detector_n"])
    return {
        "schema_version": 1,
        "created": timestamp(),
        "config_path": str(config_path),
        "config": config,
        "selection_rule": (
            "Per source family: ten highest and ten lowest complete validated "
            "finite source S_born values, checked against explicit source-case lists."
        ),
        "target_detector_n": target_n,
        "case_count": len(selected),
        "cases": [
            {
                "global_index": index,
                "family": item.family,
                "tail": item.tail,
                "rank": item.rank,
                "config_id": item.config_id,
                "source": asdict(item.case),
                "prior_n17_dir": (
                    str(item.prior_n17_dir) if item.prior_n17_dir is not None else None
                ),
                "prior_n17_valid": _prior_result_matches(
                    item.prior_n17_dir, item, target_n
                ),
            }
            for index, item in enumerate(selected)
        ],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--array-index", type=int, required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--output-root", type=Path, required=True)
    result.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    result.add_argument(
        "--reuse-existing-n17",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    result.add_argument("--dry-run", action="store_true")
    return result


def main() -> None:
    args = parser().parse_args()
    config_path = args.config.resolve()
    config = _load_config(config_path)
    selected = select_cases(config)
    target_n = int(config["target_detector_n"])
    cases_per_task = int(config["cases_per_array_task"])
    array_size = int(config["array_size"])
    if len(selected) != array_size * cases_per_task:
        raise ValueError(
            "selected case count does not equal array_size * cases_per_array_task"
        )
    if args.array_index < 0 or args.array_index >= array_size:
        raise ValueError(f"array-index must be in 0..{array_size - 1}")
    start = args.array_index * cases_per_task
    stop = start + cases_per_task
    assigned = selected[start:stop]
    plan = {
        "array_index": args.array_index,
        "global_case_start": start,
        "global_case_stop_exclusive": stop,
        "target_detector_n": target_n,
        "reuse_existing_n17": args.reuse_existing_n17,
        "assigned_cases": [
            {
                "family": item.family,
                "tail": item.tail,
                "rank": item.rank,
                "config_id": item.config_id,
                "source_case": item.case.source_case,
                "source_S_born": item.case.source_s_born,
                "prior_n17_dir": (
                    str(item.prior_n17_dir) if item.prior_n17_dir is not None else None
                ),
                "prior_n17_valid": _prior_result_matches(
                    item.prior_n17_dir, item, target_n
                ),
            }
            for item in assigned
        ],
        "checkpoint_policy": "each configuration writes COMPLETE.json before advancing",
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return

    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    if args.array_index == 0:
        _atomic_json(
            output_root / "selection_manifest.json",
            _selection_manifest(config, config_path, selected),
        )
    task_dir = output_root / "tasks" / f"task_{args.array_index:03d}"
    task_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(task_dir / "RUNNING.json", {**plan, "started": timestamp()})
    outcomes: list[dict[str, Any]] = []
    try:
        for case_number, item in enumerate(assigned, start=1):
            case_dir = output_dir_for_case(output_root, item, target_n)
            print(
                f"[{timestamp()}] task={args.array_index} case={case_number}/"
                f"{len(assigned)} start {item.label} {item.config_id} "
                f"source_S_born={item.case.source_s_born:.9g}",
                flush=True,
            )
            if args.resume and _complete_valid(case_dir):
                outcome = {
                    "status": "resumed",
                    "case_dir": str(case_dir),
                    "family": item.family,
                    "tail": item.tail,
                    "rank": item.rank,
                    "config_id": item.config_id,
                }
            elif (
                args.reuse_existing_n17
                and not case_dir.exists()
                and _prior_result_matches(item.prior_n17_dir, item, target_n)
            ):
                assert item.prior_n17_dir is not None
                provenance = _copy_prior_result(item.prior_n17_dir, case_dir)
                outcome = {
                    "status": "reused_external_N17",
                    "case_dir": str(case_dir),
                    "family": item.family,
                    "tail": item.tail,
                    "rank": item.rank,
                    "config_id": item.config_id,
                    **provenance,
                }
            else:
                outcome = simulate_ranked_case(
                    item.case,
                    detector_n=target_n,
                    hz0=item.case.hz0,
                    case_dir=case_dir,
                    source_index=item.family_index,
                    rank_index=item.rank - 1,
                    hz0_aliases=("source_hz0",),
                    resume=args.resume,
                    selection_label=item.label,
                )
                outcome.update(
                    {
                        "family": item.family,
                        "tail": item.tail,
                        "rank": item.rank,
                        "config_id": item.config_id,
                    }
                )
            outcomes.append(outcome)
            _atomic_json(
                task_dir / "RUNNING.json",
                {**plan, "outcomes": outcomes, "updated": timestamp()},
            )
            print(
                f"[{timestamp()}] task={args.array_index} case={case_number}/"
                f"{len(assigned)} done status={outcome['status']} "
                f"output={case_dir}",
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
