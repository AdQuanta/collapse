"""Launch the validated detector-spectrum atlas at N=13 on Zeus.

This is a thin project-scoped launcher around the implementation archived in
``reports/relative_scale_detector_spectra_20260726_112930``.  It resolves all
paths at runtime, records execution-node resources, and preserves the
implementation's per-regime checkpoint/restart behavior.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = REPO_ROOT / "configs" / "zeus_detector_spectra_N13.json"
ANALYZER = (
    REPO_ROOT
    / "reports"
    / "relative_scale_detector_spectra_20260726_112930"
    / "analyze_detector_spectra.py"
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def memory_snapshot() -> dict[str, float | str]:
    snapshot: dict[str, float | str] = {
        "cpu": platform.processor() or platform.machine(),
        "platform": platform.platform(),
        "logical_cores": os.cpu_count() or 0,
        "gpu": "not used",
        "numerical_backend": "Python 3.11 NumPy CPU LAPACK",
    }
    meminfo = Path("/proc/meminfo")
    if meminfo.is_file():
        values: dict[str, int] = {}
        for line in meminfo.read_text(encoding="utf-8").splitlines():
            key, value = line.split(":", maxsplit=1)
            values[key] = int(value.strip().split()[0])
        snapshot["total_ram_gib"] = values.get("MemTotal", 0) / 2**20
        snapshot["free_ram_gib"] = values.get("MemAvailable", 0) / 2**20
    return snapshot


def resolve_from_repo(value: str) -> Path:
    candidate = Path(value)
    return candidate.resolve() if candidate.is_absolute() else (REPO_ROOT / candidate).resolve()


def build_runtime_config(
    template_path: Path,
    run_root: Path,
    numeric_threads: int,
) -> tuple[Path, dict[str, Any]]:
    config = read_json(template_path)
    config["selected_n"] = 13
    config["threads"] = numeric_threads
    config["source_campaign_config"] = str(
        resolve_from_repo(str(config["source_campaign_config"]))
    )
    config["output_directory"] = str(run_root)
    config["hardware_assessment"] = memory_snapshot()
    runtime_path = run_root / "runtime_analysis_config.json"
    write_json_atomic(runtime_path, config)
    return runtime_path, config


def validate_inputs(config: dict[str, Any]) -> list[dict[str, Any]]:
    if not ANALYZER.is_file():
        raise FileNotFoundError(f"missing validated analyzer: {ANALYZER}")
    campaign_path = Path(str(config["source_campaign_config"]))
    if not campaign_path.is_file():
        raise FileNotFoundError(f"missing campaign configuration: {campaign_path}")
    campaign = read_json(campaign_path)
    cases = list(campaign.get("cases", []))
    if len(cases) != 30:
        raise ValueError(f"expected 30 relative-scale regimes, found {len(cases)}")
    if int(config["selected_n"]) != 13:
        raise ValueError("this launcher is deliberately restricted to N=13")
    if int(config["threads"]) < 1:
        raise ValueError("numeric thread count must be positive")
    return cases


def describe(config: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    dimension = 1 << 13
    bytes_per_dense_matrix = dimension * dimension * 8
    conservative_peak_gib = 11.5 * bytes_per_dense_matrix / 2**30 + 0.20
    print("Detector-spectrum Zeus campaign")
    print(f"N=13, Hilbert-space dimension={dimension}")
    print(f"Regimes={len(cases)}")
    print(f"Numerical threads={config['threads']}")
    print(f"Output={config['output_directory']}")
    print(f"Conservative peak estimate per active regime={conservative_peak_gib:.2f} GiB")
    print("Execution policy=one regime process at a time; BLAS uses all numeric threads")
    for index, case in enumerate(cases, start=1):
        print(
            f"{index:02d} {case['case_id']}: "
            f"hz={case['hz']}, J={case['J']}, Jpm={case['Jpm']} "
            f"({case['regime']})"
        )


def run(args: argparse.Namespace) -> int:
    template_path = resolve_from_repo(args.config)
    run_root = resolve_from_repo(args.run_root)
    runtime_path, config = build_runtime_config(
        template_path=template_path,
        run_root=run_root,
        numeric_threads=args.numeric_threads,
    )
    cases = validate_inputs(config)
    describe(config, cases)
    if args.dry_run:
        print("DRY_RUN complete: no diagonalization was started.")
        return 0

    run_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(config["source_campaign_config"]), run_root / "submitted_campaign_config.json")
    shutil.copy2(template_path, run_root / "submitted_analysis_template.json")
    shutil.copy2(Path(__file__), run_root / Path(__file__).name)

    environment = os.environ.copy()
    thread_value = str(args.numeric_threads)
    for name in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "BLIS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        environment[name] = thread_value
    environment["MPLBACKEND"] = "Agg"
    environment["MPLCONFIGDIR"] = str(run_root / ".mplconfig")
    environment["PYTHONUNBUFFERED"] = "1"
    existing_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = (
        str(REPO_ROOT)
        if not existing_pythonpath
        else str(REPO_ROOT) + os.pathsep + existing_pythonpath
    )

    command = [
        sys.executable,
        str(ANALYZER),
        "run",
        "--config",
        str(runtime_path),
    ]
    print("Command:", " ".join(command))
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=environment,
        check=False,
    )
    if completed.returncode:
        print(
            "The campaign stopped before completion. Resubmit with the same RUN_ROOT; "
            "validated regime checkpoints will be reused.",
            file=sys.stderr,
        )
    return int(completed.returncode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(DEFAULT_TEMPLATE.relative_to(REPO_ROOT)),
        help="N=13 analysis template, relative to the repository root by default.",
    )
    parser.add_argument(
        "--run-root",
        default="work/zeus_detector_spectra_N13",
        help="Persistent output/checkpoint directory.",
    )
    parser.add_argument("--numeric-threads", type=int, default=8)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if sys.version_info[:2] != (3, 11) and not args.dry_run:
        raise RuntimeError(f"Python 3.11 is required on Zeus; got {sys.version}")
    if sys.version_info[:2] != (3, 11):
        print(
            f"WARNING: configuration-only dry run under Python "
            f"{sys.version_info.major}.{sys.version_info.minor}; production requires 3.11."
        )
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
