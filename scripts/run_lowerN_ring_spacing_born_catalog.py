#!/usr/bin/env python3.11
"""Compute symmetry-resolved detector spacings for selected lower-N rings.

The source dynamics are immutable completed ``hz0=0`` simulations.  This
runner inventories them from a versioned selection config and assigns one
detector Hamiltonian to each PBS array index.  It saves per-sector and pooled
spacing histograms and statistics, but deliberately does not retain detector
eigenvalues or individual spacings.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any

import numpy as np
import scipy
from scipy.stats import kstest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for variable in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(variable, "1")

from scripts.build_three_ring_momentum_spacing_figures import (  # noqa: E402
    HamiltonianParameters,
    _spectral_statistics,
    diagonalize_sector,
    select_largest_sectors,
)


DEFAULT_CONFIG = ROOT / "configs" / "lowerN_ring_spacing_born_catalog.json"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CatalogCase:
    array_index: int
    source_name: str
    family: str
    profile: str
    source_dir: str
    detector_n: int
    config_id: str
    s_born: float
    born_rmse: float
    hz0: float
    jx_unscaled: float
    parameters: HamiltonianParameters

    @property
    def result_id(self) -> str:
        return (
            f"case_{self.array_index:03d}__N{self.detector_n}__"
            f"{self.family}__{self.config_id}"
        )


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def _validated_source(source_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    required = [
        source_dir / "COMPLETE.json",
        source_dir / "validation.json",
        source_dir / "metadata.json",
        source_dir / "metrics.json",
    ]
    if not all(path.is_file() for path in required):
        raise ValueError("missing completion, validation, metadata, or metrics file")
    complete = _read_json(required[0])
    validation = _read_json(required[1])
    if complete.get("status") != "complete" or not validation.get("passed", False):
        raise ValueError("source is not complete and validation-passed")
    recorded = complete.get("files", {})
    for name in ("metadata.json", "metrics.json", "validation.json"):
        expected = recorded.get(name)
        if expected and _sha256(source_dir / name) != expected:
            raise ValueError(f"source checksum mismatch: {name}")
    return _read_json(required[2]), _read_json(required[3])


def _source_parameters(
    metadata: dict[str, Any], *, expected_hz0: float
) -> tuple[dict[str, Any], float, float]:
    if isinstance(metadata.get("source"), dict):
        source = metadata["source"]
        hz0 = float(source.get("hz0", metadata.get("hz0", expected_hz0)))
        return source, hz0, float(source["jx"])
    configuration = metadata["configuration"]
    return (
        configuration,
        float(metadata.get("hz0", expected_hz0)),
        float(metadata["Jx_unscaled"]),
    )


def inventory_cases(config: dict[str, Any]) -> list[CatalogCase]:
    """Return the deterministic array map after source-integrity checks."""
    thresholds = config["classification"]
    pending: list[dict[str, Any]] = []
    for source in config["sources"]:
        root = ROOT / source["root"]
        source_rows: list[dict[str, Any]] = []
        for source_dir in sorted(root.glob(source["glob"])):
            try:
                metadata, metrics = _validated_source(source_dir)
                expected_hz0 = float(source["expected_hz0"])
                parameters, hz0, jx = _source_parameters(
                    metadata, expected_hz0=expected_hz0
                )
                detector_n = int(
                    metadata.get(
                        "detector_n", metadata.get("N", metadata.get("target_N"))
                    )
                )
                s_born = float(metrics["S_born"])
                born_rmse = float(metrics["born_RMSE_occupied"])
                if not all(math.isfinite(value) for value in (s_born, born_rmse, hz0)):
                    continue
                if not math.isclose(hz0, expected_hz0, rel_tol=0.0, abs_tol=1.0e-14):
                    continue
                profile = str(source["profile"])
                if profile == "born":
                    accepted = (
                        s_born >= float(thresholds["born_minimum"])
                        and born_rmse <= float(thresholds["born_rmse_maximum"])
                    )
                elif profile == "clearly_nonborn":
                    accepted = (
                        s_born < float(thresholds["clearly_nonborn_maximum"])
                        and born_rmse > float(thresholds["clearly_nonborn_rmse_minimum"])
                    )
                else:
                    raise ValueError(f"unknown profile selector: {profile}")
                if not accepted:
                    continue
                source_case = str(parameters.get("source_case", source_dir.name))
                config_id = source_case.split("/")[-1]
                source_rows.append(
                    {
                        "source_name": str(source["name"]),
                        "family": str(source["family"]),
                        "profile": profile,
                        "source_dir": str(source_dir.relative_to(ROOT)),
                        "detector_n": detector_n,
                        "config_id": config_id,
                        "s_born": s_born,
                        "born_rmse": born_rmse,
                        "hz0": hz0,
                        "jx_unscaled": jx,
                        "parameters": HamiltonianParameters(
                            hz=float(parameters["hz"]),
                            j=float(parameters["j"]),
                            jpm=float(parameters["jpm"]),
                            j2=float(parameters.get("j2", metadata.get("J2", 0.0))),
                            jpm2=float(
                                parameters.get("jpm2", metadata.get("Jpm2", 0.0))
                            ),
                        ),
                    }
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
        reverse = source["order"] == "descending_s_born"
        source_rows.sort(
            key=lambda row: (row["s_born"], row["config_id"]), reverse=reverse
        )
        pending.extend(source_rows[: int(source["limit"])])
    cases = [CatalogCase(array_index=index, **row) for index, row in enumerate(pending)]
    expected = int(config["expected_case_count"])
    if len(cases) != expected:
        raise ValueError(f"inventory produced {len(cases)} cases, expected {expected}")
    return cases


def _classify(mean_r: float, ks_poisson: float, ks_goe: float, config: dict[str, Any]) -> str:
    thresholds = config["classification"]
    mean_class = (
        "wigner_dyson"
        if abs(mean_r - float(thresholds["mean_r_goe"]))
        < abs(mean_r - float(thresholds["mean_r_poisson"]))
        else "poisson"
    )
    ks_class = "wigner_dyson" if ks_goe < ks_poisson else "poisson"
    return mean_class if mean_class == ks_class else "mixed"


def compute_case(
    case: CatalogCase,
    config: dict[str, Any],
    output_root: Path,
    *,
    max_sectors: int | None,
) -> dict[str, Any]:
    result_dir = output_root / "cases" / case.result_id
    complete_path = result_dir / "COMPLETE.json"
    if max_sectors is None and complete_path.is_file():
        complete = _read_json(complete_path)
        if complete.get("status") == "complete":
            for name, expected in complete.get("files", {}).items():
                if not (result_dir / name).is_file() or _sha256(result_dir / name) != expected:
                    break
            else:
                return {"status": "existing", "result_dir": str(result_dir)}

    sectors_by_momentum = select_largest_sectors(
        case.detector_n, count=int(config["sector_count_per_momentum"])
    )
    sectors = [sector for momentum in sectors_by_momentum for sector in sectors_by_momentum[momentum]]
    if max_sectors is not None:
        sectors = sectors[:max_sectors]
    bins_spec = config["histogram"]
    edges = np.linspace(
        float(bins_spec["minimum"]),
        float(bins_spec["maximum"]),
        int(bins_spec["bins"]) + 1,
    )
    sector_rows: list[dict[str, Any]] = []
    histograms: list[np.ndarray] = []
    all_spacings: list[np.ndarray] = []
    all_ratios: list[np.ndarray] = []
    started = time.perf_counter()
    for sector in sectors:
        energies, diagonalization_seconds = diagonalize_sector(
            case.detector_n, sector, case.parameters
        )
        statistics = _spectral_statistics(energies)
        unfolded = np.asarray(statistics.pop("unfolded_spacings"), dtype=np.float64)
        raw = np.diff(np.sort(energies))
        tolerance = float(statistics["degeneracy_tolerance"])
        raw = raw[raw > tolerance]
        ratios = (
            np.minimum(raw[:-1], raw[1:]) / np.maximum(raw[:-1], raw[1:])
            if raw.size >= 2
            else np.empty(0, dtype=np.float64)
        )
        counts, _ = np.histogram(unfolded, bins=edges)
        histograms.append(counts.astype(np.int64))
        all_spacings.append(unfolded)
        all_ratios.append(ratios)
        sector_rows.append(
            {
                "sector": asdict(sector),
                **statistics,
                "ratio_count": int(ratios.size),
                "histogram_in_range": int(np.sum(counts)),
                "histogram_overflow": int(np.count_nonzero(unfolded >= edges[-1])),
                "diagonalization_seconds": diagonalization_seconds,
            }
        )
    pooled_spacings = np.concatenate(all_spacings)
    pooled_ratios = np.concatenate(all_ratios)
    mean_r = float(np.mean(pooled_ratios))
    ks_poisson = float(kstest(pooled_spacings, lambda x: 1.0 - np.exp(-x)).statistic)
    ks_goe = float(
        kstest(pooled_spacings, lambda x: 1.0 - np.exp(-np.pi * x * x / 4.0)).statistic
    )
    pooled_histogram, _ = np.histogram(pooled_spacings, bins=edges)
    result_dir.mkdir(parents=True, exist_ok=True)
    histogram_path = result_dir / "spacing_histograms.npz"
    np.savez_compressed(
        histogram_path,
        bin_edges=edges,
        sector_histogram_counts=np.asarray(histograms, dtype=np.int64),
        pooled_histogram_counts=pooled_histogram.astype(np.int64),
    )
    summary = {
        "schema_version": SCHEMA_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "case": asdict(case),
        "symmetry_resolution": (
            "fixed N_up below half filling; nonredundant momentum; reflection parity "
            "at k=0 and, for even N, k=N/2; half filling omitted to avoid unresolved "
            "global spin reversal; complementary N_up sectors are isospectral copies"
        ),
        "sector_selection": "five largest exact sectors per nonredundant momentum",
        "unfolding": "exact degeneracies merged; cubic staircase; 10% edge trim",
        "sector_count": len(sectors),
        "sectors": sector_rows,
        "pooled": {
            "spacing_count": int(pooled_spacings.size),
            "ratio_count": int(pooled_ratios.size),
            "mean_adjacent_gap_ratio": mean_r,
            "ks_poisson": ks_poisson,
            "ks_goe": ks_goe,
            "spacing_class": _classify(mean_r, ks_poisson, ks_goe, config),
            "histogram_in_range": int(np.sum(pooled_histogram)),
            "histogram_overflow": int(np.count_nonzero(pooled_spacings >= edges[-1])),
        },
        "runtime_seconds": time.perf_counter() - started,
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "storage_note": "Eigenvalues and individual spacings were intentionally not saved.",
    }
    summary_path = result_dir / "summary.json"
    _atomic_json(summary_path, summary)
    if max_sectors is None:
        complete = {
            "status": "complete",
            "case_id": case.result_id,
            "files": {
                summary_path.name: _sha256(summary_path),
                histogram_path.name: _sha256(histogram_path),
            },
        }
        _atomic_json(complete_path, complete)
    return summary


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--output-root", type=Path)
    result.add_argument("--array-index", type=int)
    result.add_argument(
        "--all",
        action="store_true",
        help="run every selected case sequentially (appropriate for the modest lower-N catalog)",
    )
    result.add_argument("--list-cases", action="store_true")
    result.add_argument("--dry-run", action="store_true")
    result.add_argument(
        "--max-sectors",
        type=int,
        help="smoke-test only; truncate sector list and do not write COMPLETE.json",
    )
    return result


def main() -> None:
    args = parser().parse_args()
    config_path = args.config.resolve()
    config = _read_json(config_path)
    cases = inventory_cases(config)
    if args.list_cases:
        for case in cases:
            print(json.dumps(asdict(case), sort_keys=True))
        return
    if args.all and args.array_index is not None:
        raise ValueError("choose either --all or --array-index")
    if args.all:
        if args.output_root is None:
            raise ValueError("--output-root is required")
        if args.max_sectors is not None:
            raise ValueError("--max-sectors cannot be combined with --all")
        output_root = args.output_root.resolve()
        started = time.perf_counter()
        for position, case in enumerate(cases, start=1):
            result = compute_case(case, config, output_root, max_sectors=None)
            status = result.get("status", "computed")
            print(
                f"[{position}/{len(cases)}] {case.result_id}: {status}",
                flush=True,
            )
        completion_files = sorted((output_root / "cases").glob("*/COMPLETE.json"))
        if len(completion_files) != len(cases):
            raise RuntimeError(
                f"completion gate found {len(completion_files)} markers, expected {len(cases)}"
            )
        campaign_complete = {
            "status": "complete",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "case_count": len(cases),
            "runtime_seconds": time.perf_counter() - started,
            "config": str(config_path.relative_to(ROOT)),
            "config_sha256": _sha256(config_path),
            "worker": str(Path(__file__).relative_to(ROOT)),
            "worker_sha256": _sha256(Path(__file__)),
            "case_completion_sha256": {
                path.parent.name: _sha256(path) for path in completion_files
            },
        }
        _atomic_json(output_root / "COMPLETE.json", campaign_complete)
        print(json.dumps(campaign_complete, indent=2, sort_keys=True))
        return
    if args.array_index is None:
        raise ValueError("--array-index is required")
    if not 0 <= args.array_index < len(cases):
        raise ValueError(f"array index must lie in 0..{len(cases) - 1}")
    case = cases[args.array_index]
    if args.dry_run:
        print(json.dumps(asdict(case), indent=2, sort_keys=True))
        return
    if args.output_root is None:
        raise ValueError("--output-root is required")
    if args.max_sectors is not None and args.max_sectors < 1:
        raise ValueError("--max-sectors must be positive")
    result = compute_case(
        case,
        config,
        args.output_root.resolve(),
        max_sectors=args.max_sectors,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
