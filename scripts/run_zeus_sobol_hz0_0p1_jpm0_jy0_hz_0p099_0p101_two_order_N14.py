#!/usr/bin/env python3.11
"""Run one 25-case N=14 shard of the narrow-hz two-order Sobol scan."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import json
from pathlib import Path
import shutil
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sobol_coupling_scan import (  # noqa: E402
    SobolCampaign,
    _atomic_json,
    _case_worker,
    _complete_valid,
    _write_summary_csv,
    build_settings,
    recommended_workers,
    timestamp,
)
from scripts.run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_N15 import (  # noqa: E402
    BATCH_SIZE,
    FAMILY,
    FIXED_JPM,
    FIXED_JY,
    HZ0,
    HZ_LOWER,
    HZ_UPPER,
    SEED,
    TOTAL_CONFIGURATIONS,
    _batch_bounds,
    _finalize_if_ready,
)


DETECTOR_N = 14
LOWER = 1.0e-3
UPPER = 10.0
KAPPA = 0.01
COUPLING_LOWER = 1.0e-5
EVOLUTION_TIME = 1.0e6
MAX_WORKERS = 2


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--batch-index", type=int, required=True, choices=range(4))
    result.add_argument("--output-root", type=Path, required=True)
    result.add_argument("--workers", type=int, default=MAX_WORKERS)
    result.add_argument("--resume", action="store_true")
    result.add_argument("--overwrite", action="store_true")
    result.add_argument("--dry-run", action="store_true")
    return result


def build_production_settings():
    """Return the immutable physics and numerical settings for this campaign."""

    settings = build_settings(
        FAMILY,
        seed=SEED,
        count=TOTAL_CONFIGURATIONS,
        sizes=(DETECTOR_N,),
        lower=LOWER,
        upper=UPPER,
        kappa=KAPPA,
        coupling_lower=COUPLING_LOWER,
        evolution_time=EVOLUTION_TIME,
        bins=64,
        plot_grid=720,
        fit_harmonics=32,
        fit_tolerance=1.0e-10,
        max_bloch_points=6000,
        hz0=HZ0,
        fixed_jpm=FIXED_JPM,
        hz_lower=HZ_LOWER,
        hz_upper=HZ_UPPER,
    )
    settings.validate()
    if (
        settings.sizes != (DETECTOR_N,)
        or settings.count != TOTAL_CONFIGURATIONS
        or settings.hz0 != HZ0
        or settings.fixed_jpm != FIXED_JPM
        or settings.jy_nonzero
        or settings.resolved_hz_lower != HZ_LOWER
        or settings.resolved_hz_upper != HZ_UPPER
        or settings.kappa != KAPPA
        or settings.resolved_coupling_lower != COUPLING_LOWER
    ):
        raise RuntimeError("N=14 two-order Sobol production invariants changed")
    return settings


def _copy_provenance_once(campaign: SobolCampaign) -> None:
    scripts = campaign.parent_root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    lock = scripts / ".copy.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        return
    try:
        campaign._copy_provenance()
        for relative in (
            "scripts/run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14.py",
            "hpc/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14_array.pbs",
            "hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14.sh",
            "hpc/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14.md",
        ):
            source = ROOT / relative
            if source.is_file():
                shutil.copy2(source, scripts / source.name)
        _atomic_json(
            scripts / "n14_campaign.json",
            {
                "copied": timestamp(),
                "N": DETECTOR_N,
                "seed": SEED,
                "hz0": HZ0,
                "hz_range": [HZ_LOWER, HZ_UPPER],
                "Jpm": FIXED_JPM,
                "Jy": FIXED_JY,
                "kappa": KAPPA,
                "coupling_lower": COUPLING_LOWER,
                "Jx_scaling": "Jx_edge=Jx/sqrt(N), applied exactly once",
            },
        )
    finally:
        lock.rmdir()


def main() -> None:
    args = parser().parse_args()
    if args.resume and args.overwrite:
        raise ValueError("--resume and --overwrite are mutually exclusive")
    if args.workers < 1 or args.workers > MAX_WORKERS:
        raise ValueError(f"N=14 production permits 1..{MAX_WORKERS} workers")

    settings = build_production_settings()
    campaign = SobolCampaign(
        args.output_root,
        settings,
        workers=args.workers,
        resume=args.resume,
        overwrite=args.overwrite,
    )
    points, coverage = campaign.prepare()
    _copy_provenance_once(campaign)
    start, stop = _batch_bounds(args.batch_index)
    selected = points[start:stop]
    if len(points) != TOTAL_CONFIGURATIONS or len(selected) != BATCH_SIZE:
        raise RuntimeError("invalid Sobol manifest or batch partition")

    batch_dir = (
        campaign.scan_root / f"N{DETECTOR_N}" / "batches"
        / f"batch_{args.batch_index:02d}"
    )
    batch_dir.mkdir(parents=True, exist_ok=True)
    batch_metadata = {
        "family": FAMILY,
        "batch_index": args.batch_index,
        "config_start": start,
        "config_stop_exclusive": stop,
        "config_ids": [point.config_id for point in selected],
        "N": DETECTOR_N,
        "hz0": HZ0,
        "Jpm": FIXED_JPM,
        "Jy": FIXED_JY,
        "hz_range": [HZ_LOWER, HZ_UPPER],
        "kappa": KAPPA,
        "coupling_lower": COUPLING_LOWER,
        "campaign_count": TOTAL_CONFIGURATIONS,
        "batch_size": BATCH_SIZE,
        "settings": asdict(settings),
        "coverage": coverage,
    }
    _atomic_json(batch_dir / "batch_manifest.json", batch_metadata)
    if args.dry_run:
        _atomic_json(
            batch_dir / "DRY_RUN.json",
            {**batch_metadata, "validated": True, "time": timestamp()},
        )
        print(
            f"[{timestamp()}] dry_run N={DETECTOR_N} batch={args.batch_index} "
            f"ids=config_{start:03d}..config_{stop - 1:03d}"
        )
        return

    n_dir = campaign.scan_root / f"N{DETECTOR_N}"
    rows: list[dict[str, object]] = []
    tasks = []
    for point in selected:
        case_dir = n_dir / point.config_id
        if args.resume and _complete_valid(case_dir):
            rows.append({
                "config_id": point.config_id,
                "N": DETECTOR_N,
                "status": "resumed",
                "runtime_seconds": 0.0,
            })
        elif _complete_valid(case_dir) and not args.overwrite:
            raise FileExistsError(f"validated output exists at {case_dir}; use --resume")
        else:
            if args.overwrite:
                (case_dir / "COMPLETE.json").unlink(missing_ok=True)
            tasks.append((asdict(settings), asdict(point), DETECTOR_N, str(case_dir)))

    worker_count = recommended_workers(DETECTOR_N, args.workers)
    print(
        f"[{timestamp()}] family={FAMILY} N={DETECTOR_N} hz0={HZ0} "
        f"hz=[{HZ_LOWER},{HZ_UPPER}] kappa={KAPPA} "
        f"batch={args.batch_index} workers={worker_count} pending={len(tasks)}",
        flush=True,
    )
    with ProcessPoolExecutor(max_workers=worker_count) as pool:
        futures = {pool.submit(_case_worker, payload): payload for payload in tasks}
        for future in as_completed(futures):
            payload = futures[future]
            try:
                result = future.result()
            except BaseException as exc:
                point = payload[1]
                case_dir = Path(payload[3])
                result = {
                    "config_id": point["config_id"],
                    "N": DETECTOR_N,
                    "status": "failed",
                    "runtime_seconds": 0.0,
                    "error": f"worker-process failure: {type(exc).__name__}: {exc}",
                }
                _atomic_json(
                    case_dir / "FAILURE.json",
                    {
                        "status": "failed",
                        "simulation": FAMILY,
                        "configuration": point,
                        "N": DETECTOR_N,
                        "time": timestamp(),
                        "stage": "process executor",
                        "exception_type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    },
                )
            rows.append(result)
            print(
                f"[{timestamp()}] N={DETECTOR_N} batch={args.batch_index} "
                f"config={result['config_id']} status={result['status']}",
                flush=True,
            )

    _write_summary_csv(batch_dir / "summary.csv", rows)
    validated = sum(_complete_valid(n_dir / point.config_id) for point in selected)
    _atomic_json(
        batch_dir / "BATCH_COMPLETE.json",
        {
            **batch_metadata,
            "completed": timestamp(),
            "validated_complete": validated,
            "failed_or_incomplete": BATCH_SIZE - validated,
            "policy": "failures are non-fatal and excluded from aggregation",
        },
    )
    print(
        f"[{timestamp()}] N={DETECTOR_N} batch={args.batch_index} "
        f"checkpoint={validated}/{BATCH_SIZE}",
        flush=True,
    )
    _finalize_if_ready(campaign, points, DETECTOR_N)


if __name__ == "__main__":
    main()
