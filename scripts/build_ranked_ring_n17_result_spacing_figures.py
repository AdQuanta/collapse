"""Render fresh N=17 dynamics beside the matching resolved detector spacings.

The fresh ranked-ring campaign repeats the same 40 Hamiltonian parameter sets
used by ``build_ranked_ring_momentum_spacing_figures.py``, now with N=17
dynamical diagnostics.  The detector-only N=17 spectra therefore already
exist and are reused exactly rather than diagonalised a second time.

Before rendering, this script verifies completion checksums, the validation
record, case identity, detector size, all detector Hamiltonian coefficients,
and the collective-coupling convention.  The resulting figure has the same
layout as the previous combined report: P(theta) and R(theta) on the left,
with the five largest resolved sectors at every nonredundant momentum on the
right.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))

from scripts.build_ranked_ring_diagnostics_spacing_figures import (  # noqa: E402
    render_case,
)


DEFAULT_RESULTS_ROOT = (
    ROOT / "work" / "zeus_ranked_ring_extremes_N17_fresh_20260826_212815"
)
DEFAULT_SPACING_ROOT = (
    ROOT / "reports" / "ranked_ring_symmetry_resolved_spacings_N17_2026-08-25"
)
DEFAULT_OUTPUT = (
    ROOT
    / "reports"
    / "ranked_ring_N17_fresh_diagnostics_and_symmetry_spacings_2026-08-27"
)
SCHEMA_VERSION = 1
DETECTOR_PARAMETERS = ("hz", "j", "jpm", "j2", "jpm2")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def _runtime_provenance() -> dict[str, Any]:
    packages: dict[str, str] = {}
    for name in (
        "numpy",
        "scipy",
        "matplotlib",
        "pytest",
        "quspin",
        "quspin-extensions",
    ):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "unavailable"
    return {
        "python": platform.python_version(),
        "executable": sys.executable,
        "prefix": sys.prefix,
        "platform": platform.platform(),
        "packages": packages,
    }


def fresh_result_dir(
    results_root: Path,
    case_info: dict[str, Any],
    detector_n: int,
) -> Path:
    """Return the canonical fresh-result directory for one ranked case."""
    stem = (
        f"rank_{int(case_info['rank_within_tail']):02d}__"
        f"{case_info['config_id']}"
    )
    return (
        results_root
        / str(case_info["family"])
        / str(case_info["tail"])
        / stem
        / f"N{detector_n}"
    )


def validate_detector_parameters(
    case_info: dict[str, Any],
    fresh_metadata: dict[str, Any],
    *,
    absolute_tolerance: float = 1e-14,
) -> None:
    """Require the fresh result and spacing archive to use the same H_D."""
    expected = case_info["parameters"]
    actual = fresh_metadata["source"]
    for name in DETECTOR_PARAMETERS:
        expected_value = float(expected[name])
        actual_value = float(actual.get(name, 0.0))
        if not math.isclose(
            expected_value,
            actual_value,
            rel_tol=0.0,
            abs_tol=absolute_tolerance,
        ):
            raise ValueError(
                f"detector parameter mismatch for {name}: "
                f"spacing={expected_value!r}, fresh={actual_value!r}"
            )


def _validate_completion(result_dir: Path) -> dict[str, str]:
    complete = _load_json(result_dir / "COMPLETE.json")
    if complete.get("status") != "complete":
        raise ValueError(f"result is not complete: {result_dir}")
    required = ("metadata.json", "metrics.json", "results.npz", "validation.json")
    checksums: dict[str, str] = {}
    for filename in required:
        path = result_dir / filename
        expected = complete.get("files", {}).get(filename)
        actual = _sha256(path)
        if not expected or actual != expected:
            raise ValueError(f"checksum mismatch or omission: {path}")
        checksums[filename] = actual
    validation = _load_json(result_dir / "validation.json")
    if not validation.get("passed", False):
        raise ValueError(f"validation did not pass: {result_dir}")
    return checksums


def adapt_spacing_case(
    spacing_case: dict[str, Any],
    results_root: Path,
    detector_n: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Point a spacing checkpoint at its matching fresh dynamical result."""
    adapted = deepcopy(spacing_case)
    case_info = adapted["case"]
    result_dir = fresh_result_dir(results_root, case_info, detector_n)
    checksums = _validate_completion(result_dir)
    metadata = _load_json(result_dir / "metadata.json")
    metrics = _load_json(result_dir / "metrics.json")
    selection_source_n = int(case_info["source_n"])

    if int(metadata["target_N"]) != detector_n:
        raise ValueError(f"target_N mismatch in {result_dir}")
    if int(metadata["source_rank"]) != int(case_info["rank_within_tail"]):
        raise ValueError(f"rank mismatch in {result_dir}")
    source_case = Path(str(metadata["source"]["source_case"])).name
    if source_case != str(case_info["config_id"]):
        raise ValueError(f"configuration identity mismatch in {result_dir}")
    validate_detector_parameters(case_info, metadata)

    expected_jx = float(case_info["jx_unscaled"])
    actual_jx = float(metadata["Jx_unscaled"])
    if not math.isclose(expected_jx, actual_jx, rel_tol=0.0, abs_tol=1e-14):
        raise ValueError(f"unscaled Jx mismatch in {result_dir}")
    expected_effective_jx = actual_jx / math.sqrt(detector_n)
    if not math.isclose(
        expected_effective_jx,
        float(metadata["Jx_effective"]),
        rel_tol=0.0,
        abs_tol=1e-15,
    ):
        raise ValueError(f"effective Jx scaling mismatch in {result_dir}")

    case_info.update(
        {
            "source_dir": _relative(result_dir),
            "source_n": detector_n,
            "s_born": float(metrics["S_born"]),
            "born_rmse": float(metrics["born_RMSE_occupied"]),
            "occupied_fraction": float(metrics["occupied_fraction"]),
            "jx_unscaled": actual_jx,
            "selection_label": (
                f"source-N{selection_source_n} "
                + (
                    "most Born-like"
                    if case_info["tail"] == "highest"
                    else "least Born-like"
                )
                + f" rank {int(case_info['rank_within_tail'])}"
            ),
        }
    )
    provenance = {
        "family": case_info["family"],
        "tail": case_info["tail"],
        "rank": int(case_info["rank_within_tail"]),
        "config_id": case_info["config_id"],
        "fresh_result_dir": _relative(result_dir),
        "fresh_checksums": checksums,
        "spectral_archive": spacing_case["spectral_archive"],
        "fresh_S_born": float(metrics["S_born"]),
    }
    return adapted, provenance


def run(
    results_root: Path,
    spacing_root: Path,
    output_root: Path,
    workers: int,
    dpi: int,
    force: bool,
) -> dict[str, Any]:
    """Validate, match, and render all fresh ranked N=17 results."""
    if workers < 1:
        raise ValueError("workers must be positive")
    results_root = results_root.resolve()
    spacing_root = spacing_root.resolve()
    output_root = output_root.resolve()
    spacing_summary_path = spacing_root / "summary_N17.json"
    spacing_summary = _load_json(spacing_summary_path)
    detector_n = int(spacing_summary["detector_n"])
    if detector_n != 17:
        raise ValueError(f"expected N=17 spacing data, found N={detector_n}")
    if len(spacing_summary["cases"]) != 40:
        raise ValueError("expected exactly 40 ranked spacing cases")

    adapted_cases: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    for spacing_case in spacing_summary["cases"]:
        adapted, record = adapt_spacing_case(
            spacing_case, results_root, detector_n
        )
        adapted_cases.append(adapted)
        provenance.append(record)
    print(
        f"Validated {len(adapted_cases)} fresh results against their N=17 "
        "detector spectra",
        flush=True,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    rendered: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=min(workers, len(adapted_cases))) as pool:
        futures = {
            pool.submit(
                render_case,
                case,
                output_root,
                detector_n,
                dpi,
                force,
            ): case
            for case in adapted_cases
        }
        for index, future in enumerate(as_completed(futures), start=1):
            row = future.result()
            rendered.append(row)
            info = row["case"]
            print(
                f"[{index:02d}/{len(adapted_cases)}] {info['family']} "
                f"{info['tail']} rank {int(info['rank_within_tail']):02d} "
                f"{info['config_id']}"
                + (" (resumed)" if row["resumed"] else ""),
                flush=True,
            )
    rendered.sort(
        key=lambda row: (
            row["case"]["family"],
            0 if row["case"]["tail"] == "highest" else 1,
            int(row["case"]["rank_within_tail"]),
        )
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "detector_n": detector_n,
        "fresh_results_root": _relative(results_root),
        "spacing_summary": _relative(spacing_summary_path),
        "spacing_summary_sha256": _sha256(spacing_summary_path),
        "reuse_justification": (
            "The fresh campaign and spacing archive have identical N=17 "
            "detector Hamiltonians. Detector level spacings are independent "
            "of the central-qubit coupling and dynamical evolution output."
        ),
        "validation": (
            "Completion checksums, validation records, case identity, N, "
            "hz/J/Jpm/J2/Jpm2, and Jx scaling were checked before rendering."
        ),
        "runtime": _runtime_provenance(),
        "runtime_seconds": time.perf_counter() - started,
        "case_count": len(rendered),
        "provenance": provenance,
        "cases": rendered,
    }
    _write_json_atomic(output_root / "render_manifest.json", manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--spacing-root", type=Path, default=DEFAULT_SPACING_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = run(
        results_root=args.results_root,
        spacing_root=args.spacing_root,
        output_root=args.output,
        workers=args.workers,
        dpi=args.dpi,
        force=args.force,
    )
    print(
        f"Rendered {manifest['case_count']} N=17 combined figures in "
        f"{manifest['runtime_seconds']:.1f}s: {args.output.resolve()}",
        flush=True,
    )


if __name__ == "__main__":
    main()
