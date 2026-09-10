"""Run bounded N<=10 hypothesis controls with the existing ring solver."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born_structure_controls import control_sectors, control_snapshot
from core.born_structure_plotting import profile_grid, control_parameter_figure
from core.born_profile_export import write_profile_tables, write_table


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/born_structure_controls_2026-09-10.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--from-results", type=Path, help="Render coverage-aware parameter plots from existing controls without rerunning dynamics")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    if args.from_results is not None:
        source_manifest = json.loads((args.from_results / "manifest.json").read_text())
        csv_path = args.from_results / "metrics.csv"
        if sha256(csv_path) != source_manifest["outputs"]["metrics.csv"]:
            raise ValueError("control metrics checksum mismatch")
        with csv_path.open() as stream:
            saved = list(csv.DictReader(stream))
        rows = [{k: v if k in ("id", "case", "property", "label") else float(v)
                 for k, v in row.items()} for row in saved]
        control_parameter_figure(rows, source_manifest["config"]["detector_sizes"], args.output / "parameter_errors")
        proof = dict(parent_manifest_sha256=sha256(args.from_results / "manifest.json"),
                     metrics_sha256=sha256(csv_path),
                     plotting_sha256=sha256(ROOT / "core/born_structure_plotting.py"),
                     outputs={p.name: sha256(p) for p in args.output.iterdir() if p.is_file()})
        (args.output / "manifest.json").write_text(json.dumps(proof, indent=2) + "\n")
        print(f"Rendered existing controls: {args.output}")
        return
    rows, selected = [], []
    for size in config["detector_sizes"]:
        for case in config["cases"]:
            parameters = {**config["baseline"], **case["overrides"]}
            sectors = control_sectors(parameters, size)
            for time in config["times"]:
                record = control_snapshot(sectors, size, time, config["bins"])
                name = f"N{size}_{case['key']}_t{time:g}"
                record.update(id=name, case=case["key"], property=case["property"],
                              value=case["value"], N=size, time=time,
                              label=case["label"] + f"\nN={size}, t={time:g}")
                directory = args.output / name
                directory.mkdir()
                write_profile_tables(directory, record["arrays"])
                write_table(directory / "P_moments.dat", ["n", "a_n"],
                            np.column_stack((np.arange(17), record["moments"])))
                np.savez_compressed(directory / "roots.npz", theta=record["theta"])
                scalars = {k: v for k, v in record.items() if isinstance(v, (str, int, float, np.integer, np.floating))}
                scalars["parameters"] = parameters
                (directory / "metrics.json").write_text(json.dumps(scalars, indent=2) + "\n")
                rows.append(scalars)
                if size == max(config["detector_sizes"]) and time == config["representative_time"] and case["key"] in config["representative_cases"]:
                    selected.append(record)
            print(f"Completed N={size}, {case['key']}", flush=True)
    columns = [k for k in rows[0] if k != "parameters"]
    with (args.output / "metrics.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    profile_grid(selected, args.output / "controlled_diagnostics", "Reduced exact Hamiltonian controls; finite-size checks, not a thermodynamic extrapolation")
    control_parameter_figure(rows, config["detector_sizes"], args.output / "parameter_errors")
    paths = [Path(__file__), args.config, ROOT / "core/born_structure_controls.py", ROOT / "core/born_reciprocity.py",
             ROOT / "core/born_structure_plotting.py", ROOT / "core/relative_evolution_sector.py",
             ROOT / "core/relative_evolution_pencil.py", ROOT / "core/relative_evolution_study.py",
             ROOT / "core/hamiltonians/quspin_hamiltonians.py"]
    manifest = dict(config=config, created_utc=datetime.now(timezone.utc).isoformat(),
                    python=platform.python_version(), numpy=np.__version__,
                    git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
                    source_sha256={str(p.resolve().relative_to(ROOT)): sha256(p) for p in paths},
                    outputs={str(p.relative_to(args.output)): sha256(p) for p in args.output.rglob("*") if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Completed {len(rows)} snapshots: {args.output}")


if __name__ == "__main__":
    main()
