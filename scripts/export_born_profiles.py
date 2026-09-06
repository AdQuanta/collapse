"""Review frozen local campaigns and export selected angular and graph tables."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born_profile_export import (  # noqa: E402
    graph_tables, load_profile, validate_profile, write_profile_tables, write_table,
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def portable(value: Any) -> Any:
    """Retain provenance while removing historical machine-specific prefixes."""
    if isinstance(value, dict):
        return {str(portable(k)): portable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [portable(v) for v in value]
    if isinstance(value, str):
        normalized = value.replace("\\", "/")
        if normalized.startswith("/") or (len(normalized) > 2 and normalized[1:3] == ":/"):
            for marker in ("/work/", "/core/", "/configs/", "/scripts/"):
                if marker in normalized:
                    return marker[1:] + normalized.split(marker, 1)[1]
            if "/collapse/" in normalized:
                return normalized.rsplit("/collapse/", 1)[1]
            return Path(normalized).name
    return value


def discover(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    records = []
    excluded = []
    for campaign in config["campaigns"]:
        root = ROOT / campaign
        if not root.is_dir():
            raise FileNotFoundError(root)
        paths = sorted(root.rglob("metrics.json")) + sorted(root.rglob("activation_resolved_metrics.json"))
        for path in paths:
            global_mode = path.name.startswith("activation_")
            required = [path.parent / "COMPLETE.json"]
            if not global_mode:
                required.append(path.parent / "metadata.json")
            missing = [p.name for p in required if not p.is_file()]
            if missing:
                excluded.append({"source": str(path.parent.relative_to(ROOT)),
                                 "reason": "missing " + ", ".join(missing)})
                continue
            payload = read_json(path)
            if global_mode:
                metrics = next(d for d in payload["diagnostics"] if d["label"] == "global")
                meta = payload
                params = meta["parameters"]
                archive = "activation_resolved_results.npz"
                n = meta["detector_n"]
            else:
                metrics = payload
                meta = read_json(path.parent / "metadata.json")
                params = meta.get("source", meta.get("configuration", {}))
                n = meta.get("target_N", meta.get("N"))
                archive = "results.npz" if (path.parent / "results.npz").is_file() else "results_summary.npz"
            if "S_born" not in metrics:
                continue
            graph = meta.get("detector_graph")
            family = graph["canonical_kind"] if graph else "ring"
            if family == "ring":
                family = "ring_second_neighbor" if params.get("j2", 0) or params.get("jpm2", 0) else "ring_nearest_neighbor"
            records.append({
                "campaign": campaign, "source": str(path.parent.relative_to(ROOT)),
                "family": family, "N": int(n), "S_born": float(metrics["S_born"]),
                "RMSE": float(metrics["born_RMSE_occupied"]),
                "occupied_fraction": float(metrics["occupied_fraction"]),
                "archive": archive, "global_mode": global_mode,
                "metrics": metrics, "metadata": meta, "parameters": params,
            })
    return sorted(records, key=lambda r: (-r["S_born"], r["source"])), excluded


def verify_case(record: dict[str, Any]) -> dict[str, Any]:
    directory = ROOT / record["source"]
    marker = read_json(directory / "COMPLETE.json")
    if marker.get("status") != "complete":
        raise ValueError(f"incomplete case: {directory}")
    expected = marker["files"]
    required = {record["archive"], "activation_resolved_metrics.json"} if record["global_mode"] else {
        record["archive"], "metadata.json", "metrics.json", "validation.json"}
    if not required.issubset(expected):
        raise ValueError(f"completion marker does not cover required inputs: {directory}")
    for name, digest in expected.items():
        path = directory / name
        if path.parent != directory or sha256(path) != digest:
            raise ValueError(f"completion checksum mismatch: {path}")
    if record["global_mode"]:
        validation = record["metadata"]["validation"]
    else:
        validation = read_json(directory / "validation.json")
        if validation.get("passed") is not True:
            raise ValueError(f"failed source validation: {directory}")
    return {"completion_sha256": sha256(directory / "COMPLETE.json"),
            "verified_files": expected, "source_validation": validation}


def write_index(path: Path, records: list[dict[str, Any]]) -> None:
    import csv

    columns = ["id", "family", "N", "S_born", "RMSE", "occupied_fraction", "selection", "source"]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/born_profile_export_2026-09-06.json")
    parser.add_argument("--output", type=Path, required=True, help="New output directory; existing paths are refused")
    args = parser.parse_args()
    config = read_json(args.config)
    records, excluded = discover(config)
    selected = [r for r in records if r["S_born"] >= config["score_min"]]
    groups = defaultdict(list)
    for record in records:
        groups[(record["family"], record["N"])].append(record)
    for group in groups.values():
        if group[0]["S_born"] < config["score_min"]:
            selected.extend(r for r in group[:config["reference_top_per_family_size"]]
                            if r["S_born"] >= config["reference_score_min"])
    selected.sort(key=lambda r: (r["family"], r["N"], -r["S_born"], r["source"]))
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = []
    for index, record in enumerate(selected, 1):
        record["id"] = f"{index:03d}_{record['family']}_N{record['N']}"
        record["selection"] = "high_score" if record["S_born"] >= config["score_min"] else "lower_N_reference_below_threshold"
        checks = verify_case(record)
        arrays = load_profile(ROOT / record["source"] / record["archive"], activation_global=record["global_mode"])
        checks["profile"] = validate_profile(arrays, rmse=record["RMSE"])
        directory = args.output / record["id"]
        directory.mkdir()
        write_profile_tables(directory, arrays)
        meta, params = record["metadata"], record["parameters"]
        coupling = meta.get("central_coupling", params.get("central_coupling", "all"))
        if coupling not in ("all", "all detector qubits"):
            raise ValueError(f"unsupported central coupling: {coupling}")
        nodes, edges = graph_tables(record["N"], params, meta.get("detector_graph"),
                                    family=record["family"], jx_effective=meta["Jx_effective"],
                                    jy_effective=meta.get("Jy_effective", 0.0))
        write_table(directory / "nodes.dat", ["id", "x", "y", "is_central"], nodes)
        write_table(directory / "edges.dat", ["source", "target", "kind", "Jzz", "Jpm", "Jx_effective", "Jy_effective"], edges)
        entry = portable({**record, "checks": checks})
        entry["output_sha256"] = {p.name: sha256(p) for p in sorted(directory.glob("*.dat"))}
        (directory / "provenance.json").write_text(json.dumps(entry, indent=2) + "\n")
        provenance.append(entry)
    selected_sources = {r["source"] for r in selected}
    for record in records:
        if record["source"] not in selected_sources:
            record["selection"] = "not_exported_below_threshold"
    write_index(args.output / "catalog.csv", selected)
    write_index(args.output / "reviewed_cases.csv", records)
    shortlist = []
    for family in sorted({r["family"] for r in selected}):
        shortlist.append(max((r for r in selected if r["family"] == family), key=lambda r: r["S_born"]))
    write_index(args.output / "shortlist.csv", shortlist)
    templates = ROOT / "scripts/templates/born_profiles"
    example_case = next(r["id"] for r in shortlist if r["family"] == "ring_second_neighbor")
    for name in ("README.md", "example.tex"):
        content = (templates / name).read_text(encoding="utf-8")
        (args.output / name).write_text(content.replace("CASE_ID", example_case), encoding="utf-8")
    duplicates = defaultdict(list)
    for entry in provenance:
        duplicates[entry["output_sha256"]["profile.dat"]].append(entry["id"])
    manifest = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
                "config": config, "reviewed_count": len(records), "exported_count": len(selected),
                "python": platform.python_version(), "numpy": np.__version__,
                "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "defining_source_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in [
                    Path(__file__), ROOT / "core/born_profile_export.py", args.config.resolve(),
                    templates / "README.md", templates / "example.tex"]},
                "identical_profile_groups": [ids for ids in duplicates.values() if len(ids) > 1],
                "discovery_exclusions": excluded, "cases": provenance}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"reviewed": len(records), "exported": len(selected),
                      "shortlist": [{k: r[k] for k in ("id", "S_born", "source")} for r in shortlist]}, indent=2))


if __name__ == "__main__":
    main()
