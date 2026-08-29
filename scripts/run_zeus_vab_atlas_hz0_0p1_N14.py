#!/usr/bin/env python3.11
"""Run one shard of the N=14, hz0=0.1 counterpart to the Vab atlas grid.

The source atlas contains 880 ordered configurations.  Array shards 0--7
each own 100 configurations; shard 8 owns the remaining 80.  Every shard is
composed of complete fixed-(hz, J) rows, so each row contains all ten Jpm
values and no Hamiltonian is duplicated or omitted.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import sys
import traceback
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.anisotropic_sweep import (  # noqa: E402
    AnisotropicCase,
    AnisotropicRepository,
    AnisotropicSweepConfig,
    AnisotropicSweepService,
    BlueRedDiagnosticPlotter,
    BornHeatmapAggregator,
    QuSpinAnisotropicBackend,
    SweepRowTask,
    _atomic_json,
)


DEFAULT_CONFIG = Path("configs/zeus_vab_atlas_hz0_0p1_N14.json")
DETECTOR_N = 14
HZ0 = 0.1
COLLECTIVE_JX = 0.01
EVOLUTION_TIME = 1.0e6
TOTAL_CONFIGURATIONS = 880
CONFIGURATIONS_PER_FULL_SHARD = 100
SHARD_COUNT = 9
MAX_WORKERS = 2
ATLAS_INDEX = Path("reports/vab_coupling_group_atlas_2026-07-28/data/case_index.csv")

EXPECTED_HZ = (-2.01, -2.0, -1.0, -0.1, -0.01, 0.0, 0.01, 0.1, 1.0, 2.0, 2.01)
EXPECTED_J = (0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0)
EXPECTED_JPM = (0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0)


def timestamp() -> str:
    """Return a timezone-aware timestamp for batch and worker logs."""

    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass(frozen=True)
class BatchPlan:
    """Deterministic mapping from one PBS array index to atlas rows."""

    batch_index: int
    task_indices: tuple[int, ...]
    ordinal_start: int
    ordinal_stop_exclusive: int
    configuration_count: int


def validate_production_config(config: AnisotropicSweepConfig) -> None:
    """Fail closed if any physical or numerical campaign invariant changed."""

    expected = {
        "detector_sizes": (DETECTOR_N,),
        "hz_values": EXPECTED_HZ,
        "j_values": EXPECTED_J,
        "jpm_values": EXPECTED_JPM,
        "evolution_time": EVOLUTION_TIME,
        "jx": COLLECTIVE_JX,
        "hz0": HZ0,
        "connectivity": "ring",
        "central_coupling": "all",
    }
    actual = {key: getattr(config, key) for key in expected}
    if actual != expected:
        raise ValueError(
            "production configuration does not match the 880-case atlas counterpart: "
            f"expected={expected!r}, actual={actual!r}"
        )
    if config.total_case_count != TOTAL_CONFIGURATIONS:
        raise ValueError(
            f"expected {TOTAL_CONFIGURATIONS} configurations, got {config.total_case_count}"
        )
    if config.cases_per_task != len(EXPECTED_JPM):
        raise ValueError("each fixed-(hz, J) row must contain all ten Jpm values")


def build_batch_plan(config: AnisotropicSweepConfig, batch_index: int) -> BatchPlan:
    """Map an array index to consecutive atlas ordinals without overlap."""

    validate_production_config(config)
    if batch_index < 0 or batch_index >= SHARD_COUNT:
        raise ValueError(f"batch_index must be in 0..{SHARD_COUNT - 1}")
    rows_per_full_shard, remainder = divmod(
        CONFIGURATIONS_PER_FULL_SHARD, config.cases_per_task
    )
    if remainder:
        raise RuntimeError("shard size must be divisible by the Jpm row size")
    first_task = batch_index * rows_per_full_shard + 1
    stop_task_exclusive = min(first_task + rows_per_full_shard, config.task_count + 1)
    task_indices = tuple(range(first_task, stop_task_exclusive))
    if not task_indices:
        raise RuntimeError(f"batch {batch_index} maps to no tasks")
    ordinal_start = (task_indices[0] - 1) * config.cases_per_task + 1
    ordinal_stop_exclusive = task_indices[-1] * config.cases_per_task + 1
    return BatchPlan(
        batch_index=batch_index,
        task_indices=task_indices,
        ordinal_start=ordinal_start,
        ordinal_stop_exclusive=ordinal_stop_exclusive,
        configuration_count=len(task_indices) * config.cases_per_task,
    )


def _case(config: AnisotropicSweepConfig, task: SweepRowTask, jpm: float) -> AnisotropicCase:
    return AnisotropicCase(
        detector_n=task.detector_n,
        hz=task.hz,
        j=task.j,
        jpm=float(jpm),
        evolution_time=config.evolution_time,
        jx=config.jx,
        hz0=config.hz0,
        seed=config.seed,
    )


def _row_complete(
    repository: AnisotropicRepository,
    config: AnisotropicSweepConfig,
    task: SweepRowTask,
) -> bool:
    """Require a valid DONE marker and every reusable per-case artifact."""

    done_path = repository.row_status_path(task, "DONE.json")
    if not done_path.is_file():
        return False
    try:
        done = json.loads(done_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if done.get("config_digest") != config.digest:
        return False
    completed = done.get("completed")
    if not isinstance(completed, list) or len(completed) != config.cases_per_task:
        return False
    for jpm in config.jpm_values:
        case = _case(config, task, jpm)
        required = (
            repository.raw_path(case),
            repository.metadata_path(case),
            repository.metrics_path(case),
            repository.figure_path(case),
        )
        if not all(path.is_file() and path.stat().st_size > 0 for path in required):
            return False
    return True


def _row_worker(
    config: AnisotropicSweepConfig,
    task: SweepRowTask,
    output_root: str,
    force: bool,
) -> dict[str, Any]:
    """Run one ten-configuration row inside a process worker."""

    repository = AnisotropicRepository(Path(output_root))
    service = AnisotropicSweepService(
        repository,
        QuSpinAnisotropicBackend(),
        BlueRedDiagnosticPlotter(),
    )
    done_path = service.run_task(config, task, force=force)
    if not _row_complete(repository, config, task):
        raise RuntimeError(f"row task {task.task_index} failed post-write validation")
    return {
        "task_index": task.task_index,
        "hz": task.hz,
        "J": task.j,
        "configuration_count": config.cases_per_task,
        "done_path": str(done_path),
        "status": "completed",
        "worker_pid": os.getpid(),
        "finished": timestamp(),
    }


def _batch_dir(output_root: Path, batch_index: int) -> Path:
    return output_root / "status" / f"N{DETECTOR_N:02d}" / "batches" / f"batch_{batch_index:02d}"


def _configuration_payloads(
    config: AnisotropicSweepConfig,
    plan: BatchPlan,
) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    ordinal = plan.ordinal_start
    for task_index in plan.task_indices:
        task = config.task_for_index(task_index)
        for jpm in config.jpm_values:
            payloads.append(
                {
                    "ordinal": ordinal,
                    "N": task.detector_n,
                    "hz": task.hz,
                    "J": task.j,
                    "Jpm": float(jpm),
                    "Jx": config.jx,
                    "Jy": 0.0,
                    "hz0": config.hz0,
                    "t": config.evolution_time,
                }
            )
            ordinal += 1
    if len(payloads) != plan.configuration_count:
        raise RuntimeError("batch payload count does not match its plan")
    return payloads


def _copy_provenance_once(output_root: Path, config_path: Path) -> None:
    scripts = output_root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    lock = scripts / ".copy.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        return
    try:
        for relative in (
            Path("scripts/run_zeus_vab_atlas_hz0_0p1_N14.py"),
            Path("hpc/zeus_vab_atlas_hz0_0p1_N14_array.pbs"),
            Path("hpc/submit_zeus_vab_atlas_hz0_0p1_N14.sh"),
            Path("hpc/zeus_vab_atlas_hz0_0p1_N14.md"),
            Path("core/anisotropic_sweep.py"),
        ):
            source = ROOT / relative
            if source.is_file():
                shutil.copy2(source, scripts / source.name)
        shutil.copy2(config_path, scripts / config_path.name)
        _atomic_json(
            scripts / "provenance.json",
            {
                "copied": timestamp(),
                "source_atlas_index": str(ATLAS_INDEX),
                "physics": {
                    "N": DETECTOR_N,
                    "hz0": HZ0,
                    "Jx_collective": COLLECTIVE_JX,
                    "Jx_edge": "0.01/sqrt(N)",
                    "Jy": 0.0,
                    "t": EVOLUTION_TIME,
                    "connectivity": "ring",
                    "central_coupling": "all detector spins",
                },
            },
        )
    finally:
        lock.rmdir()


def _finalize_if_ready(
    output_root: Path,
    config: AnisotropicSweepConfig,
) -> None:
    status_root = output_root / "status" / f"N{DETECTOR_N:02d}"
    markers = [
        _batch_dir(output_root, index) / "BATCH_COMPLETE.json"
        for index in range(SHARD_COUNT)
    ]
    if not all(path.is_file() for path in markers):
        return
    final_marker = status_root / "CAMPAIGN_COMPLETE.json"
    if final_marker.is_file():
        return
    lock = status_root / ".finalize.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        print(f"[{timestamp()}] finalization=owned_by_other_batch", flush=True)
        return
    try:
        if final_marker.is_file():
            return
        repository = AnisotropicRepository(output_root)
        manifest = BornHeatmapAggregator(repository).aggregate_n(config, DETECTOR_N)
        _atomic_json(
            final_marker,
            {
                "N": DETECTOR_N,
                "hz0": HZ0,
                "Jx": COLLECTIVE_JX,
                "Jy": 0.0,
                "t": EVOLUTION_TIME,
                "configuration_count": TOTAL_CONFIGURATIONS,
                "batch_count": SHARD_COUNT,
                "aggregate_manifest": str(manifest),
                "config_digest": config.digest,
                "completed": timestamp(),
            },
        )
        print(f"[{timestamp()}] finalized=880/880 manifest={manifest}", flush=True)
    finally:
        lock.rmdir()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--batch-index", type=int, choices=range(SHARD_COUNT), required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--output-root", type=Path, required=True)
    result.add_argument("--workers", type=int, default=MAX_WORKERS)
    result.add_argument("--resume", action="store_true")
    result.add_argument("--force", action="store_true")
    result.add_argument("--dry-run", action="store_true")
    return result


def main() -> None:
    args = parser().parse_args()
    if args.resume and args.force:
        raise ValueError("--resume and --force are mutually exclusive")
    if args.workers < 1 or args.workers > MAX_WORKERS:
        raise ValueError(f"N=14 production permits 1..{MAX_WORKERS} row workers")

    config_path = args.config.resolve()
    output_root = args.output_root.resolve()
    config = AnisotropicSweepConfig.from_json(config_path)
    validate_production_config(config)
    plan = build_batch_plan(config, args.batch_index)
    tasks = [config.task_for_index(index) for index in plan.task_indices]
    batch_dir = _batch_dir(output_root, args.batch_index)
    batch_dir.mkdir(parents=True, exist_ok=True)
    _copy_provenance_once(output_root, config_path)

    batch_manifest = {
        "batch": asdict(plan),
        "config_digest": config.digest,
        "source_atlas_index": str(ATLAS_INDEX),
        "physics": {
            "N": DETECTOR_N,
            "hz0": HZ0,
            "Jx_collective": COLLECTIVE_JX,
            "Jx_edge": COLLECTIVE_JX / DETECTOR_N**0.5,
            "Jy": 0.0,
            "t": EVOLUTION_TIME,
        },
        "configurations": _configuration_payloads(config, plan),
    }
    _atomic_json(batch_dir / "batch_manifest.json", batch_manifest)
    if args.dry_run:
        _atomic_json(
            batch_dir / "DRY_RUN.json",
            {**batch_manifest, "validated": True, "time": timestamp()},
        )
        print(json.dumps(batch_manifest, indent=2))
        return

    repository = AnisotropicRepository(output_root)
    if args.force:
        (batch_dir / "BATCH_COMPLETE.json").unlink(missing_ok=True)
    rows: list[dict[str, Any]] = []
    pending: list[SweepRowTask] = []
    for task in tasks:
        if args.resume and _row_complete(repository, config, task):
            rows.append(
                {
                    "task_index": task.task_index,
                    "hz": task.hz,
                    "J": task.j,
                    "configuration_count": config.cases_per_task,
                    "status": "resumed",
                }
            )
        elif _row_complete(repository, config, task) and not args.force:
            raise FileExistsError(
                f"validated row task {task.task_index} exists; use --resume or --force"
            )
        else:
            pending.append(task)

    _atomic_json(
        batch_dir / "RUNNING.json",
        {
            **batch_manifest,
            "workers": min(args.workers, max(len(pending), 1)),
            "pending_task_indices": [task.task_index for task in pending],
            "rows": rows,
            "started": timestamp(),
        },
    )
    print(
        f"[{timestamp()}] batch={args.batch_index} N={DETECTOR_N} hz0={HZ0} "
        f"ordinals={plan.ordinal_start}..{plan.ordinal_stop_exclusive - 1} "
        f"configurations={plan.configuration_count} workers={args.workers} "
        f"pending_rows={len(pending)}",
        flush=True,
    )

    failures: list[dict[str, Any]] = []
    if pending:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(pending))) as pool:
            futures = {
                pool.submit(_row_worker, config, task, str(output_root), args.force): task
                for task in pending
            }
            for future in as_completed(futures):
                task = futures[future]
                try:
                    row = future.result()
                    rows.append(row)
                    row_status = str(row.get("status", "unknown"))
                except BaseException as exc:
                    failure = {
                        "task_index": task.task_index,
                        "hz": task.hz,
                        "J": task.j,
                        "status": "failed",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                    }
                    rows.append(failure)
                    failures.append(failure)
                    row_status = "failed"
                rows.sort(key=lambda item: int(item["task_index"]))
                _atomic_json(
                    batch_dir / "RUNNING.json",
                    {
                        **batch_manifest,
                        "workers": args.workers,
                        "rows": rows,
                        "failures": failures,
                        "updated": timestamp(),
                    },
                )
                print(
                    f"[{timestamp()}] batch={args.batch_index} row={task.task_index} "
                    f"status={row_status}",
                    flush=True,
                )

    valid_rows = sum(_row_complete(repository, config, task) for task in tasks)
    terminal = {
        **batch_manifest,
        "workers": args.workers,
        "validated_rows": valid_rows,
        "validated_configurations": valid_rows * config.cases_per_task,
        "rows": sorted(rows, key=lambda item: int(item["task_index"])),
        "failures": failures,
        "completed": timestamp(),
    }
    if failures or valid_rows != len(tasks):
        _atomic_json(batch_dir / "BATCH_FAILED.json", terminal)
        raise RuntimeError(
            f"batch {args.batch_index} incomplete: rows={valid_rows}/{len(tasks)}, "
            f"failures={len(failures)}"
        )
    _atomic_json(batch_dir / "BATCH_COMPLETE.json", terminal)
    (batch_dir / "RUNNING.json").unlink(missing_ok=True)
    (batch_dir / "BATCH_FAILED.json").unlink(missing_ok=True)
    print(
        f"[{timestamp()}] batch={args.batch_index} status=complete "
        f"configurations={plan.configuration_count}",
        flush=True,
    )
    _finalize_if_ready(output_root, config)


if __name__ == "__main__":
    main()
