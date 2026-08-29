"""Shared Zeus array runner for configurable fixed-size Sobol campaigns."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import shutil
import sys
import traceback
from typing import Iterator, Sequence

from core.sobol_coupling_scan import (
    ScanSettings,
    SobolCampaign,
    _atomic_json,
    _case_worker,
    _checkpoint_report,
    _complete_valid,
    _write_summary_csv,
    recommended_workers,
    timestamp,
)


@dataclass(frozen=True)
class ZeusSobolArraySpec:
    """Default scientific contract for one Zeus campaign.

    Detector size, sample count, shard size, and graph parameters may be
    overridden explicitly at the command line; all effective values are saved.
    """

    label: str
    seed: int
    hz0: float
    hz_lower: float | None = None
    hz_upper: float | None = None
    second_neighbor: bool = False
    connectivity: str = "ring"
    graph_seed: int = 20260810
    graph_per_configuration: bool = False
    graph_require_connected: bool = True
    erdos_renyi_p: float = 0.3
    watts_strogatz_k: int = 4
    watts_strogatz_p: float = 0.3
    barabasi_albert_m: int = 2
    regular_degree: int = 4
    detector_n: int = 14
    count: int = 400
    batch_size: int = 100
    lower: float = 1.0e-3
    upper: float = 10.0
    kappa: float = 0.1
    fixed_jx: float | None = None
    evolution_time: float = 1.0e6

    @property
    def batch_count(self) -> int:
        if self.detector_n < 3:
            raise ValueError("detector_n must be at least three")
        if self.count < 1 or self.batch_size < 1:
            raise ValueError("count and batch_size must be positive")
        if self.count % self.batch_size:
            raise ValueError("count must be divisible by batch_size")
        return self.count // self.batch_size


def build_parser(spec: ZeusSobolArraySpec) -> argparse.ArgumentParser:
    """Return the common worker parser for ``spec``."""

    parser = argparse.ArgumentParser(
        description=f"Run one Zeus shard of {spec.label}."
    )
    parser.add_argument("--batch-index", type=int, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--detector-n", type=int, default=spec.detector_n)
    parser.add_argument("--count", type=int, default=spec.count)
    parser.add_argument("--batch-size", type=int, default=spec.batch_size)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lower", type=float, default=spec.lower)
    parser.add_argument("--upper", type=float, default=spec.upper)
    parser.add_argument("--kappa", type=float, default=spec.kappa)
    parser.add_argument("--fixed-jx", type=float, default=spec.fixed_jx)
    parser.add_argument(
        "--evolution-time", type=float, default=spec.evolution_time
    )
    parser.add_argument("--bins", type=int, default=64)
    parser.add_argument("--plot-grid", type=int, default=720)
    parser.add_argument("--fit-harmonics", type=int, default=32)
    parser.add_argument("--fit-tolerance", type=float, default=1.0e-10)
    parser.add_argument("--max-bloch-points", type=int, default=6000)
    parser.add_argument("--connectivity", default=spec.connectivity)
    parser.add_argument("--graph-seed", type=int, default=spec.graph_seed)
    parser.add_argument(
        "--graph-per-configuration",
        action=argparse.BooleanOptionalAction,
        default=spec.graph_per_configuration,
    )
    parser.add_argument(
        "--graph-require-connected",
        action=argparse.BooleanOptionalAction,
        default=spec.graph_require_connected,
    )
    parser.add_argument("--erdos-renyi-p", type=float, default=spec.erdos_renyi_p)
    parser.add_argument("--watts-strogatz-k", type=int, default=spec.watts_strogatz_k)
    parser.add_argument("--watts-strogatz-p", type=float, default=spec.watts_strogatz_p)
    parser.add_argument("--barabasi-albert-m", type=int, default=spec.barabasi_albert_m)
    parser.add_argument("--regular-degree", type=int, default=spec.regular_degree)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def resolve_array_spec(
    spec: ZeusSobolArraySpec, args: argparse.Namespace
) -> ZeusSobolArraySpec:
    """Apply runtime size and graph overrides to a campaign specification."""

    resolved = replace(
        spec,
        detector_n=int(getattr(args, "detector_n", spec.detector_n)),
        count=int(getattr(args, "count", spec.count)),
        batch_size=int(getattr(args, "batch_size", spec.batch_size)),
        lower=float(getattr(args, "lower", spec.lower)),
        upper=float(getattr(args, "upper", spec.upper)),
        kappa=float(getattr(args, "kappa", spec.kappa)),
        fixed_jx=getattr(args, "fixed_jx", spec.fixed_jx),
        evolution_time=float(
            getattr(args, "evolution_time", spec.evolution_time)
        ),
        connectivity=str(getattr(args, "connectivity", spec.connectivity)),
        graph_seed=int(getattr(args, "graph_seed", spec.graph_seed)),
        graph_per_configuration=bool(
            getattr(args, "graph_per_configuration", spec.graph_per_configuration)
        ),
        graph_require_connected=bool(
            getattr(args, "graph_require_connected", spec.graph_require_connected)
        ),
        erdos_renyi_p=float(
            getattr(args, "erdos_renyi_p", spec.erdos_renyi_p)
        ),
        watts_strogatz_k=int(
            getattr(args, "watts_strogatz_k", spec.watts_strogatz_k)
        ),
        watts_strogatz_p=float(
            getattr(args, "watts_strogatz_p", spec.watts_strogatz_p)
        ),
        barabasi_albert_m=int(
            getattr(args, "barabasi_albert_m", spec.barabasi_albert_m)
        ),
        regular_degree=int(
            getattr(args, "regular_degree", spec.regular_degree)
        ),
    )
    resolved.batch_count
    return resolved


def batch_bounds(spec: ZeusSobolArraySpec, batch_index: int) -> tuple[int, int]:
    """Return the half-open configuration range owned by one array element."""

    if batch_index not in range(spec.batch_count):
        raise ValueError(f"batch_index must be in [0,{spec.batch_count - 1}]")
    start = batch_index * spec.batch_size
    return start, start + spec.batch_size


def build_scan_settings(
    spec: ZeusSobolArraySpec, args: argparse.Namespace
) -> ScanSettings:
    """Translate CLI values and fixed campaign constants into validated settings."""

    spec = resolve_array_spec(spec, args)
    return ScanSettings(
        name="jy_zero",
        jy_nonzero=False,
        seed=spec.seed,
        count=spec.count,
        sizes=(spec.detector_n,),
        lower=spec.lower,
        upper=spec.upper,
        kappa=spec.kappa,
        fixed_jx=spec.fixed_jx,
        evolution_time=spec.evolution_time,
        bins=args.bins,
        plot_grid=args.plot_grid,
        fit_harmonics=args.fit_harmonics,
        fit_tolerance=args.fit_tolerance,
        max_bloch_points=args.max_bloch_points,
        hz0=spec.hz0,
        hz_lower=spec.hz_lower,
        hz_upper=spec.hz_upper,
        second_neighbor=spec.second_neighbor,
        connectivity=spec.connectivity,
        graph_seed=spec.graph_seed,
        graph_per_configuration=spec.graph_per_configuration,
        graph_require_connected=spec.graph_require_connected,
        erdos_renyi_p=spec.erdos_renyi_p,
        watts_strogatz_k=spec.watts_strogatz_k,
        watts_strogatz_p=spec.watts_strogatz_p,
        barabasi_albert_m=spec.barabasi_albert_m,
        regular_degree=spec.regular_degree,
    )


def _copy_provenance_once(
    campaign: SobolCampaign, relative_files: Sequence[str]
) -> None:
    scripts = campaign.parent_root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    lock = scripts / ".copy.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        return
    try:
        repository = Path(__file__).resolve().parents[1]
        sources = [
            Path(__file__),
            repository / "core" / "sobol_coupling_scan.py",
            repository / "core" / "detector_graphs.py",
            *(repository / relative for relative in relative_files),
        ]
        for source in sources:
            if source.is_file():
                shutil.copy2(source, scripts / source.name)
        _atomic_json(
            campaign.parent_root / "environment" / "runtime.json",
            {
                "python": sys.version,
                "platform": sys.platform,
                "timestamp": timestamp(),
                "command": sys.argv,
            },
        )
    finally:
        lock.rmdir()


def _terminal_rows(campaign: SobolCampaign, points: list) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    n = campaign.settings.sizes[0]
    for point in points:
        case_dir = campaign.scan_root / f"N{n}" / point.config_id
        if _complete_valid(case_dir):
            rows.append(
                {
                    "config_id": point.config_id,
                    "N": n,
                    "status": "resumed",
                    "runtime_seconds": 0.0,
                }
            )
            continue
        failure_path = case_dir / "FAILURE.json"
        message = "missing terminal result"
        if failure_path.is_file():
            try:
                payload = json.loads(failure_path.read_text(encoding="utf-8"))
                message = str(payload.get("message", message))
            except (OSError, ValueError):
                message = "unreadable FAILURE.json"
        rows.append(
            {
                "config_id": point.config_id,
                "N": n,
                "status": "failed",
                "runtime_seconds": 0.0,
                "error": message,
            }
        )
    return rows


def _worker_failure_result(
    payload: tuple[dict[str, object], dict[str, object], int, str],
    spec: ZeusSobolArraySpec,
    exc: BaseException,
    *,
    stage: str,
) -> dict[str, object]:
    """Persist an unexpected executor-level failure for one case."""

    point = payload[1]
    case_dir = Path(payload[3])
    result: dict[str, object] = {
        "config_id": point["config_id"],
        "N": spec.detector_n,
        "status": "failed",
        "runtime_seconds": 0.0,
        "error": f"{stage} failure: {type(exc).__name__}: {exc}",
    }
    _atomic_json(
        case_dir / "FAILURE.json",
        {
            "status": "failed",
            "simulation": spec.label,
            "configuration": point,
            "N": spec.detector_n,
            "time": timestamp(),
            "stage": stage,
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        },
    )
    return result


def _run_inline(
    tasks: list[tuple[dict[str, object], dict[str, object], int, str]],
    spec: ZeusSobolArraySpec,
) -> Iterator[dict[str, object]]:
    """Run tasks without multiprocessing or POSIX semaphore allocation."""

    total = len(tasks)
    for position, payload in enumerate(tasks, start=1):
        print(
            f"[{timestamp()}] executor=inline dispatch={position}/{total} "
            f"config={payload[1]['config_id']}",
            flush=True,
        )
        try:
            result = _case_worker(payload)
        except BaseException as exc:
            result = _worker_failure_result(
                payload, spec, exc, stage="inline worker"
            )
        yield result


def _finalize_if_ready(
    campaign: SobolCampaign, spec: ZeusSobolArraySpec, points: list
) -> None:
    n = spec.detector_n
    n_dir = campaign.scan_root / f"N{n}"
    expected = [
        n_dir / "batches" / f"batch_{index:02d}" / "BATCH_COMPLETE.json"
        for index in range(spec.batch_count)
    ]
    if not all(path.is_file() for path in expected):
        return
    final_marker = n_dir / "FINALIZED.json"
    if final_marker.is_file():
        return
    lock = n_dir / ".finalize.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        print(f"[{timestamp()}] finalization=owned_by_other_batch", flush=True)
        return
    try:
        if final_marker.is_file():
            return
        rows = _terminal_rows(campaign, points)
        try:
            _checkpoint_report(campaign.scan_root, campaign.settings, n, points, rows)
            aggregation_error = None
        except BaseException as exc:
            aggregation_error = f"{type(exc).__name__}: {exc}"
            _atomic_json(
                n_dir / "AGGREGATION_FAILURE.json",
                {
                    "time": timestamp(),
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                    "policy": "non-fatal; successful case outputs remain valid",
                },
            )
        complete = sum(_complete_valid(n_dir / point.config_id) for point in points)
        _atomic_json(
            final_marker,
            {
                "label": spec.label,
                "N": n,
                "requested": len(points),
                "validated_complete": complete,
                "failed_or_incomplete": len(points) - complete,
                "aggregation_error": aggregation_error,
                "completed": timestamp(),
            },
        )
        _atomic_json(
            campaign.scan_root / "run_manifest.json",
            {
                "settings": asdict(campaign.settings),
                "status": "finished",
                "updated": timestamp(),
                "validated_complete": complete,
                "failed_or_incomplete": len(points) - complete,
            },
        )
    finally:
        lock.rmdir()


def run_array_campaign(
    spec: ZeusSobolArraySpec,
    args: argparse.Namespace,
    *,
    provenance_files: Sequence[str] = (),
) -> None:
    """Prepare and execute exactly one deterministic array shard."""

    spec = resolve_array_spec(spec, args)
    settings = build_scan_settings(spec, args)
    settings.validate()

    campaign = SobolCampaign(
        args.output_root,
        settings,
        workers=args.workers,
        resume=args.resume,
        overwrite=args.overwrite,
    )
    points, coverage = campaign.prepare()
    _copy_provenance_once(campaign, provenance_files)
    start, stop = batch_bounds(spec, args.batch_index)
    selected = points[start:stop]
    if len(points) != spec.count or len(selected) != spec.batch_size:
        raise RuntimeError("invalid Sobol manifest or batch partition")

    batch_dir = (
        campaign.scan_root
        / f"N{spec.detector_n}"
        / "batches"
        / f"batch_{args.batch_index:02d}"
    )
    batch_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "label": spec.label,
        "batch_index": args.batch_index,
        "config_start": start,
        "config_stop_exclusive": stop,
        "config_ids": [point.config_id for point in selected],
        "N": spec.detector_n,
        "campaign_count": spec.count,
        "batch_size": spec.batch_size,
        "settings": asdict(settings),
        "coverage": coverage,
    }
    _atomic_json(batch_dir / "batch_manifest.json", metadata)
    if args.dry_run:
        _atomic_json(
            batch_dir / "DRY_RUN.json",
            {**metadata, "validated": True, "time": timestamp()},
        )
        print(
            f"[{timestamp()}] dry_run batch={args.batch_index} "
            f"ids=config_{start:03d}..config_{stop - 1:03d}",
            flush=True,
        )
        return

    n_dir = campaign.scan_root / f"N{spec.detector_n}"
    rows: list[dict[str, object]] = []
    tasks = []
    for point in selected:
        case_dir = n_dir / point.config_id
        if args.resume and _complete_valid(case_dir):
            rows.append(
                {
                    "config_id": point.config_id,
                    "N": spec.detector_n,
                    "status": "resumed",
                    "runtime_seconds": 0.0,
                }
            )
        elif _complete_valid(case_dir) and not args.overwrite:
            raise FileExistsError(f"validated output exists at {case_dir}; use --resume")
        else:
            if args.overwrite:
                (case_dir / "COMPLETE.json").unlink(missing_ok=True)
            tasks.append((asdict(settings), asdict(point), spec.detector_n, str(case_dir)))

    worker_count = recommended_workers(spec.detector_n, args.workers)
    print(
        f"[{timestamp()}] label={spec.label} N={spec.detector_n} "
        f"batch={args.batch_index} workers={worker_count} pending={len(tasks)}",
        flush=True,
    )
    if worker_count == 1:
        print(
            f"[{timestamp()}] executor=inline reason=single_worker "
            "posix_semaphores=not_required",
            flush=True,
        )
        task_results = _run_inline(tasks, spec)
    else:
        try:
            pool = ProcessPoolExecutor(max_workers=worker_count)
        except PermissionError as exc:
            print(
                f"[{timestamp()}] executor=inline reason=process_pool_permission "
                f"error={type(exc).__name__}: {exc}",
                flush=True,
            )
            task_results = _run_inline(tasks, spec)
        else:
            task_results = []
            with pool:
                futures = {
                    pool.submit(_case_worker, payload): payload
                    for payload in tasks
                }
                for future in as_completed(futures):
                    payload = futures[future]
                    try:
                        result = future.result()
                    except BaseException as exc:
                        result = _worker_failure_result(
                            payload, spec, exc, stage="process executor"
                        )
                    task_results.append(result)

    for result in task_results:
        rows.append(result)
        print(
            f"[{timestamp()}] batch={args.batch_index} "
            f"config={result['config_id']} status={result['status']}",
            flush=True,
        )

    _write_summary_csv(batch_dir / "summary.csv", rows)
    validated = sum(_complete_valid(n_dir / point.config_id) for point in selected)
    _atomic_json(
        batch_dir / "BATCH_COMPLETE.json",
        {
            **metadata,
            "completed": timestamp(),
            "validated_complete": validated,
            "failed_or_incomplete": spec.batch_size - validated,
        },
    )
    print(
        f"[{timestamp()}] batch={args.batch_index} "
        f"checkpoint={validated}/{spec.batch_size}",
        flush=True,
    )
    _finalize_if_ready(campaign, spec, points)
