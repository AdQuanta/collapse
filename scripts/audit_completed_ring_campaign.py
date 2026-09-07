#!/usr/bin/env python3.11
"""Audit a completed ring campaign without modifying it; emit portable JSON.

This stdlib-only script can run through SSH stdin before collection and then
locally. It never submits jobs or treats missing scheduler records as success.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_marker(path: Path) -> int:
    """Validate status and every listed artifact, rejecting path traversal."""
    marker = read_json(path)
    if marker.get("status") != "complete":
        raise ValueError(f"not complete: {path}")
    for name, digest in marker.get("files", {}).items():
        artifact = (path.parent / name).resolve()
        if not artifact.is_relative_to(path.parent.resolve()):
            raise ValueError(f"unsafe artifact path: {name}")
        if sha256(artifact) != digest:
            raise ValueError(f"checksum mismatch: {artifact}")
    return len(marker.get("files", {}))


def audit(root: Path, config: dict[str, Any], *, kind: str) -> dict[str, Any]:
    """Check exact task coverage, hashes, logs, and saved numerical evidence."""
    root = root.resolve()
    failures = list(root.rglob("FAILURE.json")) + list(root.rglob("RUNNING.json"))
    if failures:
        raise ValueError(f"failure/running markers remain: {failures}")
    error_pattern = re.compile(
        r"Traceback|MemoryError|out.of.memory|walltime.*exceed|killed|error:",
        re.IGNORECASE,
    )
    log_count = 0
    for path in sorted((root / "logs").glob("*")):
        if path.is_file():
            log_count += 1
            if error_pattern.search(path.read_text(errors="replace")):
                raise ValueError(f"error signature in {path}")
    expected_cases = config["cases"]
    marker_paths = list(root.rglob("COMPLETE.json"))
    numerical = []
    if kind == "catalog":
        expected_tasks = {f"task_{i:03d}" for i in range(len(expected_cases))}
        actual_tasks = {p.parent.name for p in (root / "tasks").glob("*/COMPLETE.json")}
        if actual_tasks != expected_tasks or len(marker_paths) != 2 * len(expected_cases):
            raise ValueError("catalog task/dynamics completion count mismatch")
        spacing_markers = list(root.rglob("ring_spacing_COMPLETE.json"))
        if len(spacing_markers) != len(expected_cases):
            raise ValueError("catalog spacing completion count mismatch")
        marker_paths += spacing_markers
        manifest = read_json(root / "campaign_manifest.json")
        if manifest["cases"] != expected_cases:
            raise ValueError("catalog campaign/config case mismatch")
        for index, case in enumerate(expected_cases):
            task = read_json(root / "tasks" / f"task_{index:03d}" / "COMPLETE.json")
            if task["case_key"] != case["case_key"] or task["smoke"]:
                raise ValueError("task identity mismatch or smoke data")
            directory = root / "cases" / case["case_key"] / "N17"
            validation = read_json(directory / "validation.json")
            if validation.get("passed") is not True:
                raise ValueError(f"dynamics validation failed: {directory}")
            if validation["actual_eigenvalue_count"] != 2**17:
                raise ValueError("incomplete relative spectrum")
            meta = read_json(directory / "metadata.json")
            if meta["target_N"] != 17 or meta["hz0"] != 0:
                raise ValueError("N/hz0 mismatch")
            for name, value in case["parameters"].items():
                if meta["source"][name] != value:
                    raise ValueError(f"parameter mismatch: {directory}/{name}")
            spacing = read_json(directory / "ring_spacing_metadata.json")
            if spacing["sector_count"] != 45 or len(spacing["sectors"]) != 45:
                raise ValueError("wrong number of detector sectors")
            for name, value in spacing["parameters"].items():
                if case["parameters"][name] != value:
                    raise ValueError(f"detector parameter mismatch: {name}")
            numerical.append({"case_id": case["case_key"], **validation})
    elif kind == "activation":
        if len(marker_paths) != len(expected_cases):
            raise ValueError("activation case completion count mismatch")
        expected_n = int(config["detector_n"])
        for case in expected_cases:
            directory = root / case["case_id"]
            metrics = read_json(directory / "activation_resolved_metrics.json")
            if metrics["detector_n"] != expected_n:
                raise ValueError("activation detector size mismatch")
            if metrics["parameters"]["hz0"] != case["parameter_overrides"]["hz0"]:
                raise ValueError("activation field mismatch")
            checkpoints = directory / "momentum_checkpoints"
            if len(list(checkpoints.glob("*.npz"))) != expected_n:
                raise ValueError("missing activation momentum checkpoints")
            if len(list(checkpoints.glob("*.json"))) != expected_n:
                raise ValueError("missing activation checkpoint metadata")
            for k in range(expected_n):
                checkpoint = read_json(checkpoints / f"k_{k:02d}.json")
                if sha256(checkpoints / f"k_{k:02d}.npz") != checkpoint["archive_sha256"]:
                    raise ValueError("activation checkpoint checksum mismatch")
            validation = metrics["validation"]
            # Same residual/normalization tolerance as the focused activation tests.
            for name in (
                "maximum_relative_eigenpair_residual",
                "maximum_detector_basis_completeness_error",
                "maximum_root_weight_sum_error",
                "p_theta_max_abs_error", "p_reflected_max_abs_error",
            ):
                value = float(validation[name])
                if not math.isfinite(value) or abs(value) >= 1e-11:
                    raise ValueError(f"activation validation failed: {case['case_id']}/{name}")
            # This field is an extensive sum over 2**N roots, unlike the
            # per-root and density errors above (see validate_component_reconstruction).
            relative_weight_error = validation["component_weight_sum_error"] / 2**expected_n
            if not math.isfinite(relative_weight_error) or relative_weight_error >= 1e-11:
                raise ValueError("activation total weight normalization failed")
            numerical.append({
                "case_id": case["case_id"], **validation,
                "relative_component_weight_sum_error": relative_weight_error,
            })
    else:
        raise ValueError(f"unsupported campaign kind: {kind}")
    verified = sum(verify_marker(path) for path in marker_paths)
    files = {
        str(path.relative_to(root)): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".mplconfig" not in path.parts
    }
    return {
        "schema_version": 1, "kind": kind,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": root.name, "case_count": len(expected_cases),
        "completion_marker_count": len(marker_paths),
        "verified_marker_artifacts": verified, "checked_log_count": log_count,
        "numerical_validation": numerical, "files_sha256": files,
        "status": "passed",
        "scope": "artifact gate only; scheduler state must be checked separately",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--kind", choices=("catalog", "activation"), required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.root, read_json(args.config), kind=args.kind), indent=2))


if __name__ == "__main__":
    main()
