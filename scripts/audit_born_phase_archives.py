"""Reproduce saved positive seeds through frozen verifier v1; no new simulation."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.born_phase_verifier import SCHEMA_VERSION, evaluate_angles, summarize_conditions


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plot_profiles(output: Path, records: list[dict]) -> None:
    """Show P/reflected P and R/Born separately for each size sequence."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for name in sorted({r["candidate"] for r in records}):
        rows = [r for r in records if r["candidate"] == name and r["diagnostics"] is not None]
        if not rows:
            continue
        fig, axes = plt.subplots(len(rows), 2, figsize=(9, 2.3*len(rows)), squeeze=False)
        for row, pair in zip(rows, axes):
            d = row["diagnostics"]
            p = d["profile"]
            pair[0].plot(p["centers"], p["density"], label="P")
            pair[0].plot(p["centers"], p["reflected_density"], label="reflected P")
            pair[1].plot(p["centers"], p["ratio"], label="root ratio")
            pair[1].plot(p["centers"], p["born"], "k--", label="Born")
            pair[0].set_ylabel(f"N={row['N']} density")
            pair[1].set_ylim(-.04, 1.04)
            for ax in pair:
                ax.set_xlabel("polar angle (radians)")
                ax.legend(fontsize=8)
        fig.suptitle(f"{name}: saved t=1e6 roots; QZ certification unavailable")
        fig.tight_layout()
        for extension in ("png", "pdf"):
            fig.savefig(output/f"{name}.{extension}", dpi=150)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/"configs/born_phase_archive_audit_v1.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if config["schema_version"] != SCHEMA_VERSION:
        raise ValueError("verifier schema mismatch")
    args.output.mkdir(parents=True, exist_ok=False)
    records, hashes = [], {}
    for case in config["cases"]:
        for n in case["sizes"]:
            source = case["source"].format(N=n)
            row = dict(candidate=case["candidate"], N=n, time=1e6, perturbation="baseline",
                       split="discovery", source=source, diagnostics=None)
            try:
                directory = ROOT/source
                marker = json.loads((directory/"COMPLETE.json").read_text())
                if marker.get("status") != "complete":
                    raise ValueError("source not complete")
                for filename in ("results.npz", "metadata.json", "metrics.json", "validation.json"):
                    actual = digest(directory/filename)
                    if actual != marker["files"][filename]:
                        raise ValueError(f"source hash mismatch: {filename}")
                    hashes[f"{source}/{filename}"] = actual
                hashes[f"{source}/COMPLETE.json"] = digest(directory/"COMPLETE.json")
                metadata = json.loads((directory/"metadata.json").read_text())
                validation = json.loads((directory/"validation.json").read_text())
                metrics = json.loads((directory/"metrics.json").read_text())
                parameters = metadata.get("source", metadata.get("configuration", metadata))
                if metadata.get("target_N", metadata.get("N")) != n:
                    raise ValueError("metadata detector size mismatch")
                time = metadata.get("evolution_time", parameters.get("evolution_time"))
                if time != 1e6:
                    raise ValueError("metadata time does not match preregistered snapshot")
                row["time"] = time
                for channel in ("x", "y"):
                    if not np.isclose(metadata[f"J{channel}_effective"], parameters[f"j{channel}"]/np.sqrt(n),
                                      rtol=1e-13, atol=0):
                        raise ValueError("source collective normalization mismatch")
                row["source_parameters"] = parameters
                row["source_validation"] = validation
                if validation.get("passed") is not True:
                    raise ValueError("archived validation failed")
                row["source_metadata"] = metadata
                with np.load(directory/"results.npz", allow_pickle=False) as archive:
                    row["diagnostics"] = evaluate_angles(archive["theta"], expected_count=2**n)
                    row["archive_arrays"] = list(archive.files)
                delta = row["diagnostics"]["occupied_ratio_rmse"]-metrics["born_RMSE_occupied"]
                if abs(delta) > 1e-12:
                    raise ValueError(f"saved ratio disagreement: {delta}")
                row["saved_ratio_difference"] = delta
            except (OSError, ValueError, KeyError) as error:
                row["diagnostics"] = None
                row["failure"] = str(error)
            records.append(row)
    summary = summarize_conditions(records)
    (args.output/"results.json").write_text(json.dumps(dict(records=records, summary=summary), indent=2, allow_nan=False)+"\n")
    plot_profiles(args.output, records)
    code = [Path(__file__), ROOT/"core/born_phase_verifier.py", ROOT/"core/born.py",
            ROOT/"core/born_reciprocity.py", ROOT/"core/relative_evolution_pencil.py"]
    manifest = dict(schema_version=SCHEMA_VERSION, config=config, config_sha256=digest(args.config),
                    timestamp_utc=datetime.now(timezone.utc).isoformat(),
                    python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                    git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                    code_sha256={str(p.relative_to(ROOT)): digest(p) for p in code},
                    input_sha256=hashes, output_sha256={p.name: digest(p) for p in args.output.iterdir()},
                    status="failed" if any(r["diagnostics"] is None for r in records) else "complete",
                    scope="Archive reanalysis; no new QZ certificate or asymptotic inference")
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False)+"\n")
    print(json.dumps(summary, indent=2))
    if manifest["status"] == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
