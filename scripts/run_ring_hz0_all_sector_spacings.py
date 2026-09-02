#!/usr/bin/env python3.11
"""Compute one N=17 maximal-symmetry shard across the hz0 scan.

Thirty PBS array indices cover two case-dependent decompositions.  At exactly
``hz0=0``, ten shards fix ``X_0=+1`` and the spatial dihedral sector; the
isospectral ``X_0=-1`` partner is omitted.  At nonzero ``hz0``, twenty shards
fix total-excitation parity and the spatial dihedral sector.  Every computed
``hz0`` result is checkpointed independently before the next case begins.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import platform
import sys
from typing import Any

import numpy as np
import scipy


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))

from core.sobol_coupling_scan import _atomic_json, _sha256, timestamp  # noqa: E402
from scripts.build_ring_hz0_full_spacing_3x20 import (  # noqa: E402
    SPECTRUM_METHOD_VERSION,
    compute_scan_spectra,
    load_spectrum_case,
)


DEFAULT_CONFIG = (
    ROOT / "configs" / "ring_second_neighbor_wd_hz0_all_sector_spacings_N17.json"
)
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class SectorSpec:
    """One case-family shard of maximally resolved combined-Hamiltonian sectors."""

    array_index: int
    momentum: int
    excitation_parity: int | None
    central_x: int | None
    reflection_parity: int | None

    @property
    def symmetry_family(self) -> str:
        return "central_x" if self.central_x is not None else "total_excitation_parity"

    @property
    def sector_id(self) -> str:
        if self.central_x is not None:
            internal = "xplus" if self.central_x == 1 else "xminus"
        else:
            internal = "even" if self.excitation_parity == 0 else "odd"
        reflection = (
            ""
            if self.reflection_parity is None
            else "_reflection_" + ("plus" if self.reflection_parity == 1 else "minus")
        )
        return f"k{self.momentum:02d}_{internal}{reflection}"

    def reflection_partner_momentum(self, detector_n: int) -> int:
        return (-self.momentum) % detector_n


def all_unique_sectors() -> tuple[SectorSpec, ...]:
    """Return the fixed 30-element maximal-symmetry array map."""

    sectors: list[SectorSpec] = []
    for central_x, excitation_parity in ((1, None), (None, 0), (None, 1)):
        sectors.append(
            SectorSpec(
                array_index=len(sectors),
                momentum=0,
                excitation_parity=excitation_parity,
                central_x=central_x,
                reflection_parity=1,
            )
        )
        sectors.append(
            SectorSpec(
                array_index=len(sectors),
                momentum=0,
                excitation_parity=excitation_parity,
                central_x=central_x,
                reflection_parity=-1,
            )
        )
        for momentum in range(1, 9):
            sectors.append(
                SectorSpec(
                    array_index=len(sectors),
                    momentum=momentum,
                    excitation_parity=excitation_parity,
                    central_x=central_x,
                    reflection_parity=None,
                )
            )
    return tuple(sectors)


def sector_for_array_index(array_index: int) -> SectorSpec:
    sectors = all_unique_sectors()
    if not 0 <= array_index < len(sectors):
        raise ValueError(f"array_index must lie in 0..{len(sectors) - 1}")
    return sectors[array_index]


def case_indices_for_sector(
    config: dict[str, Any],
    sector: SectorSpec,
) -> tuple[int, ...]:
    """Select exactly the cases where ``sector`` is a maximal exact block."""

    selected: list[int] = []
    for index, case in enumerate(config["cases"]):
        parameters, _ = load_spectrum_case(config, case)
        if sector.central_x is not None:
            include = parameters.hz0 == 0.0
        else:
            include = parameters.hz0 != 0.0
        if include:
            selected.append(index)
    if not selected:
        raise ValueError(f"{sector.sector_id}: no compatible hz0 cases")
    return tuple(selected)


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def validate_scan_config(config: dict[str, Any]) -> None:
    """Validate the self-contained N=17 scan and its normalization."""

    if int(config.get("detector_n", -1)) != 17:
        raise ValueError("this campaign requires detector_n=17")
    cases = config.get("cases")
    if not isinstance(cases, list) or len(cases) != 20:
        raise ValueError("the campaign config must contain exactly 20 hz0 cases")
    case_ids = [str(case.get("case_id", "")) for case in cases]
    if any(not case_id for case_id in case_ids) or len(set(case_ids)) != len(case_ids):
        raise ValueError("case_id values must be nonempty and unique")
    zero_field_count = 0
    for case in cases:
        parameters, _ = load_spectrum_case(config, case)
        zero_field_count += int(parameters.hz0 == 0.0)
        expected_ratio = float(case["hz0_over_hz"])
        actual_ratio = parameters.hz0 / parameters.hz
        if not math.isclose(actual_ratio, expected_ratio, rel_tol=1.0e-12, abs_tol=1.0e-15):
            raise ValueError(
                f"hz0 normalization mismatch for {case['case_id']}: "
                f"expected {expected_ratio}, got {actual_ratio}"
            )
    if zero_field_count != 1:
        raise ValueError(
            "the maximal-symmetry campaign requires exactly one hz0=0 case"
        )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--array-index", type=int)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--output-root", type=Path)
    result.add_argument("--eigenvalue-count", type=int, default=512)
    result.add_argument("--solver-tolerance", type=float, default=1.0e-10)
    result.add_argument(
        "--max-cases",
        type=int,
        help="run only the first N cases for a smoke test; no COMPLETE marker is written",
    )
    result.add_argument("--no-resume", action="store_true")
    result.add_argument("--dry-run", action="store_true")
    result.add_argument("--list-sectors", action="store_true")
    return result


def main() -> None:
    args = parser().parse_args()
    sectors = all_unique_sectors()
    if args.list_sectors:
        for sector in sectors:
            print(json.dumps(asdict(sector) | {"sector_id": sector.sector_id}))
        return
    if args.array_index is None:
        raise ValueError("--array-index is required unless --list-sectors is used")
    if args.output_root is None:
        raise ValueError("--output-root is required")
    if args.max_cases is not None and not 1 <= args.max_cases <= 20:
        raise ValueError("--max-cases must lie in 1..20")

    sector = sector_for_array_index(int(args.array_index))
    config_path = args.config.resolve()
    output_root = args.output_root.resolve()
    config = _read_json(config_path)
    validate_scan_config(config)
    detector_n = int(config["detector_n"])
    selected_case_indices = case_indices_for_sector(config, sector)
    selected_case_ids = [
        str(config["cases"][index]["case_id"]) for index in selected_case_indices
    ]
    sector_collection = "sectors" if args.max_cases is None else "smoke_sectors"
    sector_dir = output_root / sector_collection / sector.sector_id
    cache_dir = sector_dir / "cases"
    if args.max_cases is not None:
        selected_case_indices = selected_case_indices[: int(args.max_cases)]
        selected_case_ids = selected_case_ids[: int(args.max_cases)]

    launch_record = {
        "schema_version": SCHEMA_VERSION,
        "created": timestamp(),
        "config": str(config_path),
        "config_sha256": _sha256(config_path),
        "worker_script": str(Path(__file__).resolve()),
        "worker_script_sha256": _sha256(Path(__file__).resolve()),
        "spectrum_engine": str(
            ROOT / "scripts" / "build_ring_hz0_full_spacing_3x20.py"
        ),
        "spectrum_engine_sha256": _sha256(
            ROOT / "scripts" / "build_ring_hz0_full_spacing_3x20.py"
        ),
        "output_root": str(output_root),
        "sector": asdict(sector),
        "sector_id": sector.sector_id,
        "symmetry_family": sector.symmetry_family,
        "reflection_partner_momentum": sector.reflection_partner_momentum(detector_n),
        "case_count": len(selected_case_indices),
        "case_indices": list(selected_case_indices),
        "case_ids": selected_case_ids,
        "eigenvalue_count": int(args.eigenvalue_count),
        "solver_tolerance": float(args.solver_tolerance),
        "spectrum_method_version": SPECTRUM_METHOD_VERSION,
        "resume": not args.no_resume,
        "dry_run": bool(args.dry_run),
    }
    if args.dry_run:
        print(json.dumps(launch_record, indent=2, sort_keys=True))
        return

    sector_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(sector_dir / "launch.json", launch_record)
    _, case_metadata = compute_scan_spectra(
        config,
        cache_dir,
        momentum=sector.momentum,
        excitation_parity=sector.excitation_parity,
        central_x=sector.central_x,
        reflection_parity=sector.reflection_parity,
        eigenvalue_count=int(args.eigenvalue_count),
        solver_tolerance=float(args.solver_tolerance),
        resume=not args.no_resume,
        case_indices=selected_case_indices,
    )
    summary_path = sector_dir / "sector_summary.json"
    summary = {
        **launch_record,
        "completed": timestamp(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "sector_dimension": sorted(
            {int(metadata["sector_dimension"]) for metadata in case_metadata}
        ),
        "runtime_seconds_sum": float(
            sum(float(metadata["runtime_seconds"]) for metadata in case_metadata)
        ),
        "maximum_relative_residual": float(
            max(float(metadata["maximum_relative_residual"]) for metadata in case_metadata)
        ),
        "maximum_orthogonality_error": float(
            max(float(metadata["orthogonality_error"]) for metadata in case_metadata)
        ),
        "maximum_raw_orthogonality_error": float(
            max(float(metadata["raw_orthogonality_error"]) for metadata in case_metadata)
        ),
        "cases": case_metadata,
    }
    _atomic_json(summary_path, summary)
    if args.max_cases is None:
        files: dict[str, str] = {
            str(summary_path.relative_to(sector_dir)): _sha256(summary_path)
        }
        for case_id in selected_case_ids:
            for suffix in (".json", ".npz"):
                artifact = cache_dir / f"{case_id}{suffix}"
                files[str(artifact.relative_to(sector_dir))] = _sha256(artifact)
        _atomic_json(
            sector_dir / "COMPLETE.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "complete",
                "completed": timestamp(),
                "sector": asdict(sector),
                "sector_id": sector.sector_id,
                "case_count": len(selected_case_ids),
                "case_ids": selected_case_ids,
                "files": files,
            },
        )
    print(
        f"[{timestamp()}] sector={sector.sector_id} cases={len(case_metadata)} "
        f"summary={summary_path}",
        flush=True,
    )


if __name__ == "__main__":
    main()
