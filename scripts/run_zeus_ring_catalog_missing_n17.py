#!/usr/bin/env python3.11
"""Continue every sub-N17 hz0=0 ring catalog case at N=17 on Zeus."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback
from typing import Any

import numpy as np
from scipy.stats import kstest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))

from core.ranked_born_campaign import (  # noqa: E402
    RankedHamiltonianCase,
    simulate_ranked_case,
)
from core.sobol_coupling_scan import (  # noqa: E402
    _atomic_json,
    _atomic_npz,
    _sha256,
    timestamp,
)
from scripts.build_three_ring_momentum_spacing_figures import (  # noqa: E402
    HamiltonianParameters,
    _spectral_statistics,
    diagonalize_sector,
    select_largest_sectors,
)


DEFAULT_CONFIG = Path("configs/zeus_ring_catalog_missing_n17.json")


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _validate_config(config: dict[str, Any]) -> None:
    required = {
        "target_detector_n",
        "array_size",
        "cases_per_array_task",
        "storage_mode",
        "cases",
    }
    missing = required - set(config)
    if missing:
        raise ValueError(f"missing configuration keys: {sorted(missing)}")
    cases = config["cases"]
    if not isinstance(cases, list) or len(cases) != int(config["array_size"]):
        raise ValueError("case count must equal array_size")
    if int(config["cases_per_array_task"]) != 1:
        raise ValueError("this runner requires exactly one case per array task")
    if int(config["target_detector_n"]) != 17:
        raise ValueError("target_detector_n must be 17")
    if config["storage_mode"] != "summary":
        raise ValueError("storage_mode must be summary")
    keys = [str(case["case_key"]) for case in cases]
    if len(keys) != len(set(keys)):
        raise ValueError("case_key values must be unique")
    for case in cases:
        if int(case["source_detector_n"]) >= 17:
            raise ValueError(f"case does not lack N=17: {case['case_key']}")
        if not math.isclose(float(case["hz0"]), 0.0, abs_tol=1.0e-15):
            raise ValueError(f"nonzero hz0 in {case['case_key']}")
        parameters = case["parameters"]
        has_second_neighbor = bool(
            float(parameters.get("j2", 0.0))
            or float(parameters.get("jpm2", 0.0))
        )
        if has_second_neighbor != (case["family"] == "second_neighbor"):
            raise ValueError(f"family/parameter mismatch in {case['case_key']}")


def _validate_source(case: dict[str, Any]) -> Path:
    source = ROOT / str(case["source_result_dir"])
    files = {
        "COMPLETE.json": case["source_complete_sha256"],
        "metrics.json": case["source_metrics_sha256"],
        "validation.json": case["source_validation_sha256"],
    }
    for name, expected in files.items():
        path = source / name
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError(f"source hash mismatch or missing file: {path}")
    completion = _read_json(source / "COMPLETE.json")
    validation = _read_json(source / "validation.json")
    if completion.get("status") != "complete" or not validation.get("passed", False):
        raise ValueError(f"source is not complete and validation-passed: {source}")
    return source


def _ranked_case(case: dict[str, Any]) -> RankedHamiltonianCase:
    source = _validate_source(case)
    parameters = case["parameters"]
    return RankedHamiltonianCase(
        source_root=str(ROOT),
        source_case=str(source.relative_to(ROOT)),
        source_metric_file=str((source / "metrics.json").relative_to(ROOT)),
        source_s_born=float(case["source_s_born"]),
        source_n=int(case["source_detector_n"]),
        hz=float(parameters["hz"]),
        hz0=float(case["hz0"]),
        j=float(parameters["j"]),
        jpm=float(parameters["jpm"]),
        jx=float(parameters["jx"]),
        jy=float(parameters.get("jy", 0.0)),
        j2=float(parameters.get("j2", 0.0)),
        jpm2=float(parameters.get("jpm2", 0.0)),
        connectivity="ring",
        central_coupling="all",
        evolution_time=float(case["evolution_time"]),
        model_seed=int(case["model_seed"]),
    )


def _spacing_complete_valid(case_dir: Path) -> bool:
    marker_path = case_dir / "ring_spacing_COMPLETE.json"
    if not marker_path.is_file():
        return False
    try:
        marker = _read_json(marker_path)
        return marker.get("status") == "complete" and all(
            (case_dir / name).is_file()
            and _sha256(case_dir / name) == expected
            for name, expected in marker["files"].items()
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def save_ring_spacing_summary(
    case_dir: Path,
    *,
    detector_n: int,
    parameters: HamiltonianParameters,
    sectors_per_momentum: int,
    histogram_bins: int,
    histogram_maximum: float,
    resume: bool,
) -> dict[str, Any]:
    """Save histogram-level statistics after exact ring-symmetry resolution."""
    if resume and _spacing_complete_valid(case_dir):
        return {
            "status": "resumed",
            "marker": str(case_dir / "ring_spacing_COMPLETE.json"),
        }
    sectors_by_momentum = select_largest_sectors(
        detector_n, count=sectors_per_momentum
    )
    sectors = [
        sector
        for momentum in sectors_by_momentum
        for sector in sectors_by_momentum[momentum]
    ]
    edges = np.linspace(0.0, histogram_maximum, histogram_bins + 1)
    counts_by_sector = []
    records = []
    pooled_spacings = []
    pooled_ratio_weight = 0
    pooled_ratio_sum = 0.0
    started = time.perf_counter()
    for sector in sectors:
        energies, elapsed = diagonalize_sector(detector_n, sector, parameters)
        statistics = _spectral_statistics(energies)
        unfolded = np.asarray(
            statistics.pop("unfolded_spacings"), dtype=np.float64
        )
        counts, _ = np.histogram(unfolded, bins=edges)
        counts_by_sector.append(counts.astype(np.int64))
        pooled_spacings.append(unfolded)
        ratio_count = max(int(statistics["resolved_level_count"]) - 2, 0)
        if ratio_count and math.isfinite(float(statistics["mean_r"])):
            pooled_ratio_sum += ratio_count * float(statistics["mean_r"])
            pooled_ratio_weight += ratio_count
        records.append(
            {
                "sector": asdict(sector),
                **statistics,
                "ratio_count": ratio_count,
                "histogram_in_range": int(np.sum(counts)),
                "histogram_overflow": int(unfolded.size - np.sum(counts)),
                "diagonalization_seconds": elapsed,
            }
        )
    pooled = np.concatenate(pooled_spacings)
    pooled_counts = np.sum(np.asarray(counts_by_sector), axis=0)
    mean_r = pooled_ratio_sum / pooled_ratio_weight
    ks_poisson = float(kstest(pooled, lambda x: 1.0 - np.exp(-x)).statistic)
    ks_goe = float(
        kstest(
            pooled,
            lambda x: 1.0 - np.exp(-np.pi * np.asarray(x) ** 2 / 4.0),
        ).statistic
    )
    archive_path = case_dir / "ring_spacing_histograms.npz"
    metadata_path = case_dir / "ring_spacing_metadata.json"
    _atomic_npz(
        archive_path,
        bin_edges=edges,
        sector_histogram_counts=np.asarray(counts_by_sector, dtype=np.int64),
        pooled_histogram_counts=pooled_counts.astype(np.int64),
    )
    _atomic_json(
        metadata_path,
        {
            "schema_version": 1,
            "created": timestamp(),
            "observable": "symmetry-resolved detector-only level spacings",
            "detector_n": detector_n,
            "parameters": asdict(parameters),
            "symmetry_resolution": (
                "fixed N_up; nonredundant dihedral momentum; reflection parity "
                "at k=0; N_up>N/2 omitted as an isospectral global-spin-flip copy"
            ),
            "sector_selection": (
                f"{sectors_per_momentum} largest exact sectors at each of the "
                f"{detector_n // 2 + 1} nonredundant momenta"
            ),
            "unfolding": (
                "exact degeneracies merged; cubic staircase; 10% edge trim"
            ),
            "storage": (
                "histogram counts and scalar statistics only; detector "
                "eigenvalues and individual spacings omitted"
            ),
            "sector_count": len(sectors),
            "sectors": records,
            "pooled": {
                "spacing_count": int(pooled.size),
                "histogram_in_range": int(np.sum(pooled_counts)),
                "histogram_overflow": int(pooled.size - np.sum(pooled_counts)),
                "ratio_count": pooled_ratio_weight,
                "mean_adjacent_gap_ratio": mean_r,
                "ks_poisson": ks_poisson,
                "ks_goe": ks_goe,
            },
            "runtime_seconds": time.perf_counter() - started,
        },
    )
    files = (archive_path.name, metadata_path.name)
    marker_path = case_dir / "ring_spacing_COMPLETE.json"
    _atomic_json(
        marker_path,
        {
            "status": "complete",
            "completed": timestamp(),
            "files": {name: _sha256(case_dir / name) for name in files},
        },
    )
    return {
        "status": "success",
        "marker": str(marker_path),
        "sector_count": len(sectors),
        "spacing_count": int(pooled.size),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--array-index", type=int, required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--output-root", type=Path, required=True)
    result.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    result.add_argument("--dry-run", action="store_true")
    result.add_argument(
        "--smoke",
        action="store_true",
        help="use N=7 and one sector per momentum for a reduced local smoke test",
    )
    return result


def main() -> None:
    args = parser().parse_args()
    config_path = args.config.resolve()
    config = _read_json(config_path)
    _validate_config(config)
    if not 0 <= args.array_index < int(config["array_size"]):
        raise ValueError(f"array-index must lie in 0..{int(config['array_size']) - 1}")
    selected = config["cases"][args.array_index]
    case = _ranked_case(selected)
    target_n = 7 if args.smoke else int(config["target_detector_n"])
    sectors_per_momentum = (
        1 if args.smoke else int(config["level_spacing_sector_count_per_momentum"])
    )
    output_root = args.output_root.resolve()
    case_dir = output_root / "cases" / str(selected["case_key"]) / f"N{target_n}"
    plan = {
        "array_index": args.array_index,
        "array_size": int(config["array_size"]),
        "case_key": selected["case_key"],
        "category": selected["category"],
        "source_detector_n": int(selected["source_detector_n"]),
        "target_detector_n": target_n,
        "hz0": case.hz0,
        "storage_mode": config["storage_mode"],
        "smoke": args.smoke,
        "case_dir": str(case_dir),
    }
    if args.dry_run:
        print(json.dumps({**plan, "case": asdict(case)}, indent=2))
        return

    output_root.mkdir(parents=True, exist_ok=True)
    if args.array_index == 0:
        _atomic_json(
            output_root / "campaign_manifest.json",
            {
                "created": timestamp(),
                "config": str(config_path),
                "config_sha256": _sha256(config_path),
                "target_detector_n": target_n,
                "case_count": len(config["cases"]),
                "storage_mode": config["storage_mode"],
                "cases": config["cases"],
            },
        )
    task_dir = output_root / "tasks" / f"task_{args.array_index:03d}"
    task_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(task_dir / "RUNNING.json", {**plan, "started": timestamp()})
    try:
        dynamics = simulate_ranked_case(
            case,
            detector_n=target_n,
            hz0=case.hz0,
            case_dir=case_dir,
            source_index=args.array_index,
            rank_index=int(selected["catalog_rank"]) - 1,
            hz0_aliases=("zero",),
            bins=int(config["bins"]),
            plot_grid=int(config["plot_grid"]),
            fit_harmonics=int(config["fit_harmonics"]),
            fit_tolerance=float(config["fit_tolerance"]),
            max_bloch_points=int(config["max_bloch_points"]),
            resume=args.resume,
            selection_label=str(selected["case_key"]),
            storage_mode=str(config["storage_mode"]),
        )
        spacing = save_ring_spacing_summary(
            case_dir,
            detector_n=target_n,
            parameters=HamiltonianParameters(
                hz=case.hz,
                j=case.j,
                jpm=case.jpm,
                j2=case.j2,
                jpm2=case.jpm2,
            ),
            sectors_per_momentum=sectors_per_momentum,
            histogram_bins=int(config["level_spacing_bins"]),
            histogram_maximum=float(config["level_spacing_maximum"]),
            resume=args.resume,
        )
    except BaseException as exc:
        _atomic_json(
            task_dir / "FAILURE.json",
            {
                **plan,
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
                "failed": timestamp(),
            },
        )
        raise
    _atomic_json(
        task_dir / "COMPLETE.json",
        {
            **plan,
            "status": "complete",
            "dynamics": dynamics,
            "spacing": spacing,
            "completed": timestamp(),
        },
    )
    (task_dir / "RUNNING.json").unlink(missing_ok=True)
    (task_dir / "FAILURE.json").unlink(missing_ok=True)
    print(json.dumps({"dynamics": dynamics, "spacing": spacing}, indent=2))


if __name__ == "__main__":
    main()
