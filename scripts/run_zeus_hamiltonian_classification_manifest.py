"""Run one strided shard of the Hamiltonian-classification manifest."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--array-index", type=int, required=True)
    parser.add_argument("--array-size", type=int, default=20)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.array_index < args.array_size:
        raise ValueError("array-index must lie in [0,array-size)")
    with args.manifest.resolve().open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assigned = [
        row for row in rows if int(row["point_id"]) % args.array_size == args.array_index
    ]
    print(
        f"array task {args.array_index}/{args.array_size}: {len(assigned)} of "
        f"{len(rows)} points",
        flush=True,
    )
    for position, row in enumerate(assigned, start=1):
        point_id = int(row["point_id"])
        case_dir = (
            args.output_root.resolve()
            / "raw"
            / row["campaign"]
            / f"point_{point_id:04d}_N{int(row['detector_n'])}_t{float(row['time']):.12g}"
        )
        complete = case_dir / "COMPLETE.json"
        if args.resume and complete.is_file():
            print(f"[{position}/{len(assigned)}] reuse point {point_id}", flush=True)
            continue
        config_dir = args.output_root.resolve() / "effective_configs"
        config_dir.mkdir(parents=True, exist_ok=True)
        point_config = config_dir / f"point_{point_id:04d}.json"
        point_config.write_text(
            json.dumps(json.loads(row["parameters_json"]), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(
            f"[{position}/{len(assigned)}] point={point_id} campaign={row['campaign']} "
            f"N={row['detector_n']} t={row['time']} {row['scan_parameter']}={row['scan_value']}",
            flush=True,
        )
        command = [
            sys.executable,
            str(ROOT / "scripts" / "run_hamiltonian_classification_point.py"),
            "--config",
            str(point_config),
            "--output-dir",
            str(case_dir),
        ]
        if not args.resume:
            command.append("--force")
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()

