"""
Check whether a Zeus Born follow-up retrieval is complete.

This script is intentionally a provenance/import check, not a scientific
analysis step.  It verifies that every expected PBS task directory exists and
contains the data files needed for later aggregation:

``results.json``, ``results.csv``, and ``top_candidates.md``.

It also reports whether the provenance log ``run.log`` was retrieved.  Missing
logs should be fixed, but they do not prevent CSV-based post-processing.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


EXPECTED_RUNS = (
    "primary_matched_ring_N12",
    "primary_matched_ring_N13",
    "primary_matched_ring_N14",
    "primary_matched_ring_long_time_N12_N13",
    "detuning_control_ring_N12_N13",
    "chain_control_N12_N13",
    "sz_exchange_control_N12_N13",
    "cnot_copier_degenerate_N8_N10_N12",
)

REQUIRED_DATA_FILES = (
    "results.json",
    "results.csv",
    "top_candidates.md",
)

PROVENANCE_FILES = (
    "run.log",
)


@dataclass
class FileCheck:
    path: str
    exists: bool
    bytes: int

    @property
    def ok(self) -> bool:
        return self.exists and self.bytes > 0


@dataclass
class RunCheck:
    name: str
    directory: str
    directory_exists: bool
    files: dict[str, FileCheck]
    result_rows: int | None
    scheduler_logs: list[str]

    @property
    def data_ok(self) -> bool:
        return self.directory_exists and all(
            self.files[name].ok for name in REQUIRED_DATA_FILES
        )

    @property
    def provenance_ok(self) -> bool:
        return all(self.files[name].ok for name in PROVENANCE_FILES) or bool(self.scheduler_logs)

    @property
    def full_ok(self) -> bool:
        return self.data_ok and self.provenance_ok

    @property
    def missing_data_files(self) -> list[str]:
        return [name for name in REQUIRED_DATA_FILES if not self.files[name].ok]

    @property
    def missing_provenance_files(self) -> list[str]:
        return [name for name in PROVENANCE_FILES if not self.files[name].ok]


def _relative(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _file_check(path: Path, base: Path) -> FileCheck:
    return FileCheck(
        path=_relative(path, base),
        exists=path.is_file(),
        bytes=path.stat().st_size if path.is_file() else 0,
    )


def _count_csv_rows(path: Path) -> int | None:
    if not path.is_file() or path.stat().st_size == 0:
        return None
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        try:
            next(reader)
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def _scheduler_logs_for(run_name: str, roots: list[Path], base: Path) -> list[str]:
    logs: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.log"):
            if run_name in path.name:
                logs.append(_relative(path, base))
    return sorted(set(logs))


def inspect_import(root: Path, logs_roots: list[Path]) -> list[RunCheck]:
    base = Path.cwd()
    checks: list[RunCheck] = []
    scheduler_roots = [root, *logs_roots]
    for run_name in EXPECTED_RUNS:
        run_dir = root / run_name
        files = {
            file_name: _file_check(run_dir / file_name, base)
            for file_name in (*REQUIRED_DATA_FILES, *PROVENANCE_FILES)
        }
        checks.append(
            RunCheck(
                name=run_name,
                directory=_relative(run_dir, base),
                directory_exists=run_dir.is_dir(),
                files=files,
                result_rows=_count_csv_rows(run_dir / "results.csv"),
                scheduler_logs=_scheduler_logs_for(run_name, scheduler_roots, base),
            )
        )
    return checks


def _print_table(checks: list[RunCheck]) -> None:
    print("| run | data | provenance | rows | missing data | missing logs | scheduler logs |")
    print("|:---|:---:|:---:|---:|:---|:---|---:|")
    for check in checks:
        data = "ok" if check.data_ok else "missing"
        provenance = "ok" if check.provenance_ok else "missing"
        rows = "" if check.result_rows is None else str(check.result_rows)
        missing_data = ", ".join(check.missing_data_files)
        missing_logs = ", ".join(check.missing_provenance_files)
        print(
            f"| {check.name} | {data} | {provenance} | {rows} | {missing_data} | {missing_logs} | {len(check.scheduler_logs)} |"
        )


def _write_json(path: Path, checks: list[RunCheck]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "data_ok": all(check.data_ok for check in checks),
        "full_ok": all(check.full_ok for check in checks),
        "runs": [asdict(check) for check in checks],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("figures/zeus_born_followup"),
        help="Local RUN_ROOT containing expected follow-up result directories.",
    )
    parser.add_argument(
        "--logs-root",
        type=Path,
        action="append",
        default=[],
        help="Optional local LOG_ROOT directory. Can be supplied more than once.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path for a machine-readable import report.",
    )
    parser.add_argument(
        "--require-provenance",
        action="store_true",
        help="Fail when result logs are missing, even if CSV data are ready.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checks = inspect_import(args.root, args.logs_root)
    _print_table(checks)
    if args.json_out is not None:
        _write_json(args.json_out, checks)
        print(f"\nWrote {args.json_out}")

    missing_data = [check for check in checks if not check.data_ok]
    missing_provenance = [check for check in checks if not check.provenance_ok]
    if missing_data:
        print(
            "\nImport data incomplete: retrieve the missing result directories before "
            "running aggregate summaries."
        )
        raise SystemExit(1)
    if missing_provenance:
        print(
            "\nImport data ready, but provenance logs are missing. Aggregate summaries "
            "can run; retrieve run.log or scheduler logs for full provenance."
        )
        if args.require_provenance:
            raise SystemExit(1)
    else:
        print("\nImport complete: data and provenance files are present.")


if __name__ == "__main__":
    main()
