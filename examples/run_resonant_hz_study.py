"""Noninteractive local study of h_z=0,+/-2 resonances at Jx=0.01.

Run from repository root.  The output contains raw per-time samples, metadata,
machine-readable summaries, and a self-contained manifest.  Plot generation
is intentionally separated into ``examples/plot_resonant_hz_study.py``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.resonant_study import REQUIRED_JX, StudyConfig, run_case, write_summary


# Principal requested long-time grid.  The brief lists both 10000 and 1e4;
# those are one numerical time and are therefore stored once.
TIME_GRID = (100.0, 1_000.0, 10_000.0, 100_000.0, 1_000_000.0)
BROAD_HZ = (-3.0, -2.5, -2.0, -1.5, -1.0, 0.0, 1.0, 1.5, 2.0, 2.5, 3.0)
FOCUSED_HZ = (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, help="Machine-readable JSON configuration; CLI values override it")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--mode", choices=("smoke", "broad", "focused"))
    parser.add_argument("--N", type=int, nargs="+", help="Detector sizes, not total qubits")
    parser.add_argument("--times", type=float, nargs="+", default=list(TIME_GRID))
    parser.add_argument("--hz-values", type=float, nargs="+", default=None, help="Explicit h_z grid; overrides --mode's preset")
    args = parser.parse_args()
    if args.config:
        payload = json.loads(args.config.read_text(encoding="utf-8"))
        args.out = args.out or Path(payload["output"])
        args.mode = args.mode or payload.get("mode", "focused")
        args.N = args.N or payload["N"]
        if args.hz_values is None:
            args.hz_values = payload.get("hz")
        if args.times == list(TIME_GRID):
            configured_times = list(payload.get("times", TIME_GRID))
            if "long_time_grid" in payload:
                grid = payload["long_time_grid"]
                if grid.get("kind") != "logspace":
                    parser.error("only long_time_grid.kind='logspace' is supported")
                configured_times.extend(np.geomspace(float(grid["start"]), float(grid["stop"]), int(grid["count"])).tolist())
            args.times = sorted(set(float(value) for value in configured_times))
    if args.out is None or args.mode is None or args.N is None:
        parser.error("--out, --mode, and --N are required unless supplied by --config")
    hz_values = tuple(args.hz_values) if args.hz_values is not None else ((0.0, -2.0, 2.0) if args.mode == "smoke" else (BROAD_HZ if args.mode == "broad" else FOCUSED_HZ))
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    records = []
    for n in args.N:
        for hz in hz_values:
            case_dir = args.out / f"N{n:02d}" / f"hz_{hz:+.3f}"
            print(f"Running detector N={n}, h_z={hz:+g}, Jx={REQUIRED_JX}", flush=True)
            records.append(run_case(StudyConfig(n, hz, tuple(args.times)), case_dir))
    write_summary(records, args.out / "summary.csv")
    manifest = {"mode": args.mode, "N": args.N, "hz": hz_values, "times": args.times, "fixed_parameters": {"hz0": 0.0, "J": 1.0, "Jx": REQUIRED_JX}, "elapsed_seconds": time.perf_counter() - started}
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
