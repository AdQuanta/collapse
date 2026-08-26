#!/usr/bin/env python3.11
"""Run one 25-case batch with hz in [0.099,0.101], hz0=0.1, Jpm=Jy=0, and N=15."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import json
from pathlib import Path
import shutil
import sys
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.sobol_coupling_scan import (  # noqa: E402
    SobolCampaign,
    _atomic_json,
    _case_worker,
    _checkpoint_report,
    _complete_valid,
    _write_summary_csv,
    build_settings,
    recommended_workers,
    timestamp,
)


HZ0 = 0.1
DETECTOR_N = 15
TOTAL_CONFIGURATIONS = 100
BATCH_SIZE = 25
FAMILY = "jy_zero"
SEED = 20260805
FIXED_JPM = 0.0
FIXED_JY = 0.0
HZ_LOWER = 0.099
HZ_UPPER = 0.101


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--batch-index", type=int, required=True, choices=range(4))
    result.add_argument("--output-root", type=Path, required=True)
    result.add_argument("--workers", type=int, default=2)
    result.add_argument("--lower", type=float, default=1e-3)
    result.add_argument("--upper", type=float, default=10.0)
    result.add_argument("--kappa", type=float, default=0.1)
    result.add_argument("--coupling-lower", type=float)
    result.add_argument("--evolution-time", type=float, default=1e6)
    result.add_argument("--bins", type=int, default=64)
    result.add_argument("--plot-grid", type=int, default=720)
    result.add_argument("--fit-harmonics", type=int, default=32)
    result.add_argument("--fit-tolerance", type=float, default=1e-10)
    result.add_argument("--max-bloch-points", type=int, default=6000)
    result.add_argument("--resume", action="store_true")
    result.add_argument("--overwrite", action="store_true")
    result.add_argument("--dry-run", action="store_true")
    return result


def _copy_provenance_once(campaign: SobolCampaign) -> None:
    scripts = campaign.parent_root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    lock = scripts / ".copy.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        return
    try:
        campaign._copy_provenance()  # The campaign owns this stable provenance format.
        for relative in (
            "examples/run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_N15.py",
            "hpc/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_N15_array.pbs",
            "hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_N15.sh",
            "hpc/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_N15.md",
            "hpc/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N15_array.pbs",
            "hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N15.sh",
            "hpc/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N15.md",
        ):
            source = Path(__file__).resolve().parents[1] / relative
            if source.is_file():
                shutil.copy2(source, scripts / source.name)
    finally:
        lock.rmdir()


def _batch_bounds(batch_index: int) -> tuple[int, int]:
    start = batch_index * BATCH_SIZE
    return start, start + BATCH_SIZE


def _terminal_rows(scan_root: Path, points: list, n: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for point in points:
        case_dir = scan_root / f"N{n}" / point.config_id
        if _complete_valid(case_dir):
            rows.append({"config_id": point.config_id, "N": n, "status": "resumed", "runtime_seconds": 0.0})
            continue
        failure_path = case_dir / "FAILURE.json"
        message = "missing terminal result"
        if failure_path.is_file():
            try:
                message = str(json.loads(failure_path.read_text(encoding="utf-8")).get("message", message))
            except (OSError, ValueError):
                message = "unreadable FAILURE.json"
        rows.append({"config_id": point.config_id, "N": n, "status": "failed", "runtime_seconds": 0.0, "error": message})
    return rows


def _finalize_if_ready(campaign: SobolCampaign, points: list, n: int) -> None:
    n_dir = campaign.scan_root / f"N{n}"
    batches = n_dir / "batches"
    expected = [batches / f"batch_{index:02d}" / "BATCH_COMPLETE.json" for index in range(4)]
    if not all(path.is_file() for path in expected):
        return
    final_marker = n_dir / "FINALIZED.json"
    if final_marker.is_file():
        return
    lock = n_dir / ".finalize.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        print(f"[{timestamp()}] family={campaign.settings.name} finalization=owned_by_other_batch", flush=True)
        return
    try:
        if final_marker.is_file():
            return
        rows = _terminal_rows(campaign.scan_root, points, n)
        try:
            _checkpoint_report(campaign.scan_root, campaign.settings, n, points, rows)
            aggregation_error = None
        except BaseException as exc:
            aggregation_error = f"{type(exc).__name__}: {exc}"
            _atomic_json(
                n_dir / "AGGREGATION_FAILURE.json",
                {"time": timestamp(), "message": str(exc), "traceback": traceback.format_exc(),
                 "policy": "non-fatal; successful case outputs remain valid"},
            )
        complete = sum(_complete_valid(n_dir / point.config_id) for point in points)
        failed = len(points) - complete
        _atomic_json(
            final_marker,
            {
                "family": campaign.settings.name,
                "N": n,
                "hz0": HZ0,
                "Jpm": FIXED_JPM,
                "Jy": FIXED_JY,
                "requested": len(points),
                "validated_complete": complete,
                "failed_or_incomplete": failed,
                "aggregation_error": aggregation_error,
                "completed": timestamp(),
                "policy": "fit and simulation failures are retained but excluded from success-only aggregation",
            },
        )
        _atomic_json(
            campaign.scan_root / "run_manifest.json",
            {"settings": asdict(campaign.settings), "status": "finished", "updated": timestamp(),
             "validated_complete": complete, "failed_or_incomplete": failed},
        )
        print(
            f"[{timestamp()}] family={campaign.settings.name} N={n} "
            f"finalized={complete}/{len(points)} failures={failed}",
            flush=True,
        )
    finally:
        lock.rmdir()


def main() -> None:
    args = parser().parse_args()
    settings = build_settings(
        FAMILY,
        seed=SEED,
        count=TOTAL_CONFIGURATIONS,
        sizes=(DETECTOR_N,),
        lower=args.lower,
        upper=args.upper,
        kappa=args.kappa,
        coupling_lower=args.coupling_lower,
        evolution_time=args.evolution_time,
        bins=args.bins,
        plot_grid=args.plot_grid,
        fit_harmonics=args.fit_harmonics,
        fit_tolerance=args.fit_tolerance,
        max_bloch_points=args.max_bloch_points,
        hz0=HZ0,
        fixed_jpm=FIXED_JPM,
        hz_lower=HZ_LOWER,
        hz_upper=HZ_UPPER,
    )
    if (
        settings.hz0 != HZ0
        or settings.fixed_jpm != FIXED_JPM
        or settings.jy_nonzero
        or settings.hz_lower != HZ_LOWER
        or settings.hz_upper != HZ_UPPER
        or settings.count != TOTAL_CONFIGURATIONS
        or settings.sizes != (DETECTOR_N,)
    ):
        raise RuntimeError("production invariants changed: require hz in [0.099,0.101], hz0=0.1, Jpm=Jy=0, count=100, N=15")

    campaign = SobolCampaign(args.output_root, settings, workers=args.workers, resume=args.resume, overwrite=args.overwrite)
    points, coverage = campaign.prepare()
    _copy_provenance_once(campaign)
    start, stop = _batch_bounds(args.batch_index)
    selected = points[start:stop]
    if len(points) != TOTAL_CONFIGURATIONS or len(selected) != BATCH_SIZE:
        raise RuntimeError("invalid Sobol manifest or batch partition")
    batch_dir = campaign.scan_root / f"N{DETECTOR_N}" / "batches" / f"batch_{args.batch_index:02d}"
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
        "campaign_count": TOTAL_CONFIGURATIONS,
        "batch_size": BATCH_SIZE,
        "settings": asdict(settings),
        "coverage": coverage,
    }
    _atomic_json(batch_dir / "batch_manifest.json", batch_metadata)
    if args.dry_run:
        _atomic_json(batch_dir / "DRY_RUN.json", {**batch_metadata, "validated": True, "time": timestamp()})
        print(f"[{timestamp()}] dry_run family={FAMILY} batch={args.batch_index} ids=config_{start:03d}..config_{stop-1:03d}")
        return

    n_dir = campaign.scan_root / f"N{DETECTOR_N}"
    rows: list[dict[str, object]] = []
    tasks = []
    for point in selected:
        case_dir = n_dir / point.config_id
        if args.resume and _complete_valid(case_dir):
            rows.append({"config_id": point.config_id, "N": DETECTOR_N, "status": "resumed", "runtime_seconds": 0.0})
        elif _complete_valid(case_dir) and not args.overwrite:
            raise FileExistsError(f"validated output exists at {case_dir}; use --resume")
        else:
            if args.overwrite:
                (case_dir / "COMPLETE.json").unlink(missing_ok=True)
            tasks.append((asdict(settings), asdict(point), DETECTOR_N, str(case_dir)))

    worker_count = recommended_workers(DETECTOR_N, args.workers)
    print(
        f"[{timestamp()}] family={FAMILY} N={DETECTOR_N} hz0={HZ0} hz=[{HZ_LOWER},{HZ_UPPER}] "
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
                result = {"config_id": point["config_id"], "N": DETECTOR_N, "status": "failed",
                          "runtime_seconds": 0.0, "error": f"worker-process failure: {type(exc).__name__}: {exc}"}
                _atomic_json(
                    case_dir / "FAILURE.json",
                    {"status": "failed", "simulation": FAMILY, "configuration": point,
                     "N": DETECTOR_N, "time": timestamp(), "stage": "process executor",
                     "exception_type": type(exc).__name__, "message": str(exc),
                     "traceback": traceback.format_exc()},
                )
            rows.append(result)
            print(
                f"[{timestamp()}] family={FAMILY} batch={args.batch_index} "
                f"config={result['config_id']} status={result['status']}",
                flush=True,
            )

    _write_summary_csv(batch_dir / "summary.csv", rows)
    validated = sum(_complete_valid(n_dir / point.config_id) for point in selected)
    _atomic_json(
        batch_dir / "BATCH_COMPLETE.json",
        {**batch_metadata, "completed": timestamp(), "validated_complete": validated,
         "failed_or_incomplete": BATCH_SIZE - validated,
         "policy": "failures are non-fatal and excluded from final success-only aggregation"},
    )
    print(f"[{timestamp()}] family={FAMILY} batch={args.batch_index} checkpoint={validated}/{BATCH_SIZE}", flush=True)
    _finalize_if_ready(campaign, points, DETECTOR_N)


if __name__ == "__main__":
    main()
