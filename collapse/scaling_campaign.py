"""Checkpointed multi-size launch infrastructure for diagnostic-atlas studies.

Each detector size runs as an isolated subprocess with its own raw-data,
figure, log, and status directories.  Independent sizes may be scheduled with
``ProcessPoolExecutor``; on Zeus the PBS arrays normally provide this
parallelism across nodes instead.  A size is marked complete only after its
driver exits successfully and its manifest, figures, metrics, and expected raw
spectra have been verified.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
from typing import Sequence


DEFAULT_SIZES = tuple(range(11, 19))
COLLECTIVE_JX = 0.01


@dataclass(frozen=True)
class StudyDefinition:
    """Immutable mapping from one named study to its single-N driver."""

    name: str
    driver: str
    manifest_name: str
    fixed_arguments: tuple[str, ...]
    expected_raw_spectra: int
    expected_atlases: int


STUDIES: dict[str, StudyDefinition] = {
    "hz0": StudyDefinition(
        name="hz0",
        driver="examples/plot_single_pixel_hz0_diagnostic_atlas.py",
        manifest_name="hz0_diagnostic_atlas_manifest.json",
        fixed_arguments=("--J", "1", "--hz", "0.1", "--Jx", "0.01"),
        expected_raw_spectra=28,
        expected_atlases=4,
    ),
    "hz_resonance": StudyDefinition(
        name="hz_resonance",
        driver="examples/plot_single_pixel_hz_resonance_atlas.py",
        manifest_name="hz_resonance_atlas_manifest.json",
        fixed_arguments=("--J", "1", "--hz0", "0", "--Jx", "0.01"),
        expected_raw_spectra=60,
        expected_atlases=12,
    ),
    "jpm_hz": StudyDefinition(
        name="jpm_hz",
        driver="examples/plot_single_pixel_jpm_hz_atlas.py",
        manifest_name="jpm_hz_atlas_manifest.json",
        fixed_arguments=("--J", "0", "--Jpm", "1", "--hz0", "0", "--Jx", "0.01"),
        expected_raw_spectra=100,
        expected_atlases=20,
    ),
    "jpm_coupling": StudyDefinition(
        name="jpm_coupling",
        driver="examples/plot_single_pixel_jpm_sweep_atlas.py",
        manifest_name="jpm_sweep_atlas_manifest.json",
        fixed_arguments=("--J", "1", "--hz", "0.1", "--hz0", "0", "--Jx", "0.01"),
        expected_raw_spectra=48,
        expected_atlases=4,
    ),
}


@dataclass(frozen=True)
class TaskLayout:
    """All paths owned by one size, preventing cross-size collisions."""

    task_root: Path
    raw_root: Path
    figure_root: Path
    log_root: Path
    stdout_log: Path
    stderr_log: Path
    running_status: Path
    done_status: Path
    failed_status: Path


@dataclass(frozen=True)
class TaskSpec:
    """Serializable input to one subprocess worker."""

    repository_root: Path
    campaign_root: Path
    python_executable: str
    study_name: str
    detector_n: int
    force: bool = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def task_layout(campaign_root: Path, study_name: str, detector_n: int) -> TaskLayout:
    task_root = Path(campaign_root).resolve() / study_name / f"N{detector_n:02d}"
    log_root = task_root / "logs"
    return TaskLayout(
        task_root=task_root,
        raw_root=task_root / "raw",
        figure_root=task_root / "figures",
        log_root=log_root,
        stdout_log=log_root / "stdout.log",
        stderr_log=log_root / "stderr.log",
        running_status=task_root / "RUNNING.json",
        done_status=task_root / "DONE.json",
        failed_status=task_root / "FAILED.json",
    )


def build_command(spec: TaskSpec) -> list[str]:
    definition = STUDIES[spec.study_name]
    layout = task_layout(spec.campaign_root, spec.study_name, spec.detector_n)
    command = [
        spec.python_executable,
        str((spec.repository_root / definition.driver).resolve()),
        "--N",
        str(spec.detector_n),
        "--raw-out",
        str(layout.raw_root),
        "--fig-out",
        str(layout.figure_root),
        *definition.fixed_arguments,
    ]
    if spec.force:
        command.append("--force")
    return command


def _write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _resolve_output_path(repository_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repository_root / path


def validate_completed_task(spec: TaskSpec) -> dict:
    definition = STUDIES[spec.study_name]
    layout = task_layout(spec.campaign_root, spec.study_name, spec.detector_n)
    manifest_path = layout.figure_root / definition.manifest_name
    if not manifest_path.is_file():
        raise FileNotFoundError(f"missing manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if int(manifest["detector_n"]) != spec.detector_n:
        raise ValueError("manifest detector_n does not match the task")
    fixed = manifest["fixed_parameters"]
    if not math.isclose(float(fixed["Jx"]), COLLECTIVE_JX, rel_tol=0.0, abs_tol=1.0e-15):
        raise ValueError("manifest Jx is not the required collective Jx=0.01")
    expected_edge = COLLECTIVE_JX / math.sqrt(spec.detector_n)
    if not math.isclose(float(fixed["Jx_edge"]), expected_edge, rel_tol=1.0e-13, abs_tol=1.0e-15):
        raise ValueError("manifest edge coupling is not Jx/sqrt(N)")
    atlas_paths = [_resolve_output_path(spec.repository_root, value) for value in manifest["atlases"]]
    if len(atlas_paths) != definition.expected_atlases:
        raise ValueError("manifest contains the wrong number of atlases")
    missing = [str(path) for path in atlas_paths if not path.is_file()]
    summary_path = _resolve_output_path(spec.repository_root, manifest["summary_plot"])
    metrics_path = _resolve_output_path(spec.repository_root, manifest["metrics_csv"])
    if not summary_path.is_file():
        missing.append(str(summary_path))
    if not metrics_path.is_file():
        missing.append(str(metrics_path))
    if missing:
        raise FileNotFoundError("missing generated outputs: " + ", ".join(missing))
    raw_count = sum(1 for _ in layout.raw_root.rglob("raw_*.npz"))
    if raw_count != definition.expected_raw_spectra:
        raise ValueError(
            f"expected {definition.expected_raw_spectra} raw spectra, found {raw_count}"
        )
    return {
        "manifest": str(manifest_path),
        "metrics": str(metrics_path),
        "summary_plot": str(summary_path),
        "atlas_count": len(atlas_paths),
        "raw_spectrum_count": raw_count,
        "collective_Jx": COLLECTIVE_JX,
        "edge_Jx": expected_edge,
    }


def _runtime_versions() -> dict[str, str]:
    packages = ("quspin", "quspin-extensions", "numpy", "scipy", "matplotlib")
    versions: dict[str, str] = {}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not installed in launcher environment"
    return versions


def run_task(spec: TaskSpec) -> dict:
    """Run and validate one size; all state is persisted before returning."""

    definition = STUDIES[spec.study_name]
    layout = task_layout(spec.campaign_root, spec.study_name, spec.detector_n)
    for path in (layout.raw_root, layout.figure_root, layout.log_root):
        path.mkdir(parents=True, exist_ok=True)
    if layout.done_status.is_file() and not spec.force:
        payload = json.loads(layout.done_status.read_text(encoding="utf-8"))
        payload["result"] = "reused"
        return payload

    for stale in (layout.failed_status, layout.done_status):
        if stale.exists():
            stale.unlink()
    command = build_command(spec)
    started = utc_now()
    running = {
        "status": "running",
        "study": definition.name,
        "detector_n": spec.detector_n,
        "total_qubits": spec.detector_n + 1,
        "collective_Jx": COLLECTIVE_JX,
        "edge_Jx": COLLECTIVE_JX / math.sqrt(spec.detector_n),
        "command": command,
        "started_utc": started,
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "versions": _runtime_versions(),
        "stdout_log": str(layout.stdout_log),
        "stderr_log": str(layout.stderr_log),
    }
    _write_json_atomic(layout.running_status, running)
    with layout.stdout_log.open("a", encoding="utf-8", buffering=1) as stdout_handle, layout.stderr_log.open(
        "a", encoding="utf-8", buffering=1
    ) as stderr_handle:
        stdout_handle.write(f"\n[{started}] START {' '.join(command)}\n")
        result = subprocess.run(
            command,
            cwd=spec.repository_root,
            stdout=stdout_handle,
            stderr=stderr_handle,
            text=True,
            check=False,
        )
    finished = utc_now()
    if result.returncode != 0:
        failed = {
            **running,
            "status": "failed",
            "returncode": result.returncode,
            "finished_utc": finished,
        }
        _write_json_atomic(layout.failed_status, failed)
        return failed
    try:
        validation = validate_completed_task(spec)
    except Exception as error:  # validation failure must remain machine-readable
        failed = {
            **running,
            "status": "failed_validation",
            "returncode": result.returncode,
            "finished_utc": finished,
            "validation_error": f"{type(error).__name__}: {error}",
        }
        _write_json_atomic(layout.failed_status, failed)
        return failed
    completed = {
        **running,
        "status": "complete",
        "result": "computed",
        "returncode": result.returncode,
        "finished_utc": finished,
        "validation": validation,
    }
    _write_json_atomic(layout.done_status, completed)
    if layout.running_status.exists():
        layout.running_status.unlink()
    return completed


def _validate_sizes(sizes: Sequence[int], allow_small_smoke: bool) -> tuple[int, ...]:
    values = tuple(int(value) for value in sizes)
    if not values:
        raise ValueError("at least one N is required")
    if len(set(values)) != len(values):
        raise ValueError("N values must be unique")
    if allow_small_smoke:
        if any(value < 3 for value in values):
            raise ValueError("smoke-test N must be at least 3")
    elif any(value not in DEFAULT_SIZES for value in values):
        raise ValueError("production sizes must be N=11,12,13,14,15,16,17,18")
    return values


def run_campaign(
    *,
    repository_root: Path,
    campaign_root: Path,
    python_executable: str,
    study_name: str,
    sizes: Sequence[int],
    workers: int,
    force: bool,
    dry_run: bool,
    allow_small_smoke: bool,
) -> list[dict]:
    """Run sizes independently and checkpoint the campaign after each result."""

    if study_name not in STUDIES:
        raise ValueError(f"unknown study: {study_name}")
    selected_sizes = _validate_sizes(sizes, allow_small_smoke)
    if workers < 1:
        raise ValueError("workers must be positive")
    root = Path(campaign_root).resolve()
    study_root = root / study_name
    study_root.mkdir(parents=True, exist_ok=True)
    specs = [
        TaskSpec(
            repository_root=Path(repository_root).resolve(),
            campaign_root=root,
            python_executable=python_executable,
            study_name=study_name,
            detector_n=detector_n,
            force=force,
        )
        for detector_n in selected_sizes
    ]
    results: list[dict] = []
    summary_path = study_root / "campaign_summary.json"

    def checkpoint() -> None:
        payload = {
            "study": study_name,
            "requested_sizes": selected_sizes,
            "workers": workers,
            "collective_Jx": COLLECTIVE_JX,
            "edge_scaling": "Jx/sqrt(N)",
            "updated_utc": utc_now(),
            "results": sorted(results, key=lambda row: int(row["detector_n"])),
        }
        _write_json_atomic(summary_path, payload)

    if dry_run:
        for spec in specs:
            layout = task_layout(root, study_name, spec.detector_n)
            result = {
                "status": "dry_run",
                "detector_n": spec.detector_n,
                "edge_Jx": COLLECTIVE_JX / math.sqrt(spec.detector_n),
                "task_root": str(layout.task_root),
                "command": build_command(spec),
            }
            results.append(result)
            print(json.dumps(result, indent=2), flush=True)
            checkpoint()
        return results

    if workers == 1:
        for spec in specs:
            result = run_task(spec)
            results.append(result)
            checkpoint()
            print(json.dumps({"N": spec.detector_n, "status": result["status"]}), flush=True)
    else:
        with ProcessPoolExecutor(max_workers=min(workers, len(specs))) as pool:
            futures = {pool.submit(run_task, spec): spec for spec in specs}
            for future in as_completed(futures):
                spec = futures[future]
                try:
                    result = future.result()
                except Exception as error:
                    result = {
                        "status": "launcher_exception",
                        "detector_n": spec.detector_n,
                        "error": f"{type(error).__name__}: {error}",
                    }
                results.append(result)
                checkpoint()
                print(json.dumps({"N": spec.detector_n, "status": result["status"]}), flush=True)
    return sorted(results, key=lambda row: int(row["detector_n"]))


def main_for_study(study_name: str, description: str) -> None:
    """Shared CLI used by the four small study-specific launchers."""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--N", type=int, nargs="+", default=DEFAULT_SIZES, dest="sizes")
    parser.add_argument("--workers", type=int, default=1, help="parallel N subprocesses; use conservatively because memory grows as 4^N")
    parser.add_argument(
        "--campaign-root",
        type=Path,
        default=Path("work/single_pixel_atlas_scaling_2026-07-14"),
    )
    parser.add_argument("--python", default=sys.executable, dest="python_executable")
    parser.add_argument("--force", action="store_true", help="recompute raw spectra even when checkpoints exist")
    parser.add_argument("--dry-run", action="store_true", help="write and print commands without launching simulations")
    parser.add_argument("--allow-small-smoke", action="store_true", help="permit N below 11 for an explicit smoke test")
    args = parser.parse_args()

    repository_root = Path(__file__).resolve().parent.parent
    results = run_campaign(
        repository_root=repository_root,
        campaign_root=args.campaign_root,
        python_executable=args.python_executable,
        study_name=study_name,
        sizes=args.sizes,
        workers=args.workers,
        force=args.force,
        dry_run=args.dry_run,
        allow_small_smoke=args.allow_small_smoke,
    )
    failures = [row for row in results if row["status"] not in {"complete", "dry_run"}]
    if failures:
        raise SystemExit(1)


__all__ = [
    "COLLECTIVE_JX",
    "DEFAULT_SIZES",
    "STUDIES",
    "StudyDefinition",
    "TaskLayout",
    "TaskSpec",
    "build_command",
    "main_for_study",
    "run_campaign",
    "run_task",
    "task_layout",
    "validate_completed_task",
]
