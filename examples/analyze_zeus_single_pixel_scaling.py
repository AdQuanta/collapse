"""Aggregate completed Zeus single-pixel scaling spectra with fit diagnostics.

Only directories carrying ``DONE.json`` are treated as complete evidence.
Partial and failed directories remain in the inventory but are excluded from
the quantitative summary, so interrupted cluster runs cannot silently bias a
finite-size trend.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.born import diagnostics_from_radii
from collapse.single_pixel_atlas import AngularDiagnosticCalculator, SpectrumSample


TIME_PATTERN = re.compile(r"raw_t(?P<time>[0-9.eE+-]+)\.npz$")


def _float(raw: Any, key: str, default: float = math.nan) -> float:
    if key not in raw:
        return default
    return float(np.asarray(raw[key]).item())


def _status(case: Path) -> str:
    if (case / "DONE.json").is_file():
        return "complete"
    if (case / "FAILED.json").is_file():
        return "failed"
    if (case / "RUNNING.json").is_file():
        return "partial"
    return "unknown"


def _parameter_coordinates(study: str, hz: float, hz0: float, jpm: float) -> tuple[str, float, float, float]:
    if study == "hz0":
        return "hz0", hz0, hz, hz0 - hz
    if study == "jpm_coupling":
        return "Jpm", jpm, jpm, 0.0
    centers = (-2.0, 0.0, 2.0) if study == "hz_resonance" else (-2.0, -1.0, 0.0, 1.0, 2.0)
    center = min(centers, key=lambda value: abs(hz - value))
    return "hz", hz, center, hz - center


def _radius_metrics(radii: np.ndarray) -> dict[str, float]:
    finite = np.asarray(radii, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return {
            "radius_q50": math.nan,
            "radius_q95": math.nan,
            "radius_q99": math.nan,
            "radius_q99_over_q50": math.nan,
            "radius_atomic_fraction": math.nan,
            "theta_mass_gt_0p5": math.nan,
        }
    q50, q95, q99 = np.quantile(finite, (0.50, 0.95, 0.99))
    rounded = np.round(finite, decimals=12)
    _, counts = np.unique(rounded, return_counts=True)
    theta = 2.0 * np.arctan(finite)
    return {
        "radius_q50": float(q50),
        "radius_q95": float(q95),
        "radius_q99": float(q99),
        "radius_q99_over_q50": float(q99 / q50) if q50 > 0.0 else math.inf,
        "radius_atomic_fraction": float(np.max(counts) / rounded.size),
        "theta_mass_gt_0p5": float(np.mean(theta > 0.5)),
    }


def analyze_spectrum(path: Path, study: str, detector_n: int, bins: int) -> dict[str, Any]:
    match = TIME_PATTERN.match(path.name)
    if match is None:
        raise ValueError(f"cannot parse time from {path}")
    time_value = float(match.group("time"))
    with np.load(path) as raw:
        theta = np.asarray(raw["theta"], dtype=float)
        eigenvalues = np.asarray(raw["eigenvalues"], dtype=np.complex128)
        variance = _float(raw, "theory_variance")
        hz = _float(raw, "hz")
        hz0 = _float(raw, "hz0")
        j = _float(raw, "J")
        jpm = _float(raw, "Jpm", 0.0)
        jx = _float(raw, "Jx")
    sample = SpectrumSample(
        hz=hz,
        t=time_value,
        eigenvalues=eigenvalues,
        theta=theta,
        theory_variance=variance,
    )
    angular = AngularDiagnosticCalculator(bins).calculate(sample)
    radii = np.abs(eigenvalues[np.isfinite(eigenvalues.real) & np.isfinite(eigenvalues.imag)])
    born = diagnostics_from_radii(radii)
    parameter_name, parameter_value, reference_value, detuning = _parameter_coordinates(study, hz, hz0, jpm)
    row: dict[str, Any] = {
        "study": study,
        "detector_n": detector_n,
        "total_qubits": detector_n + 1,
        "t": time_value,
        "parameter_name": parameter_name,
        "parameter_value": parameter_value,
        "reference_value": reference_value,
        "detuning": detuning,
        "hz": hz,
        "hz0": hz0,
        "J": j,
        "Jpm": jpm,
        "Jx": jx,
        "sample_count": int(radii.size),
        "S_born": angular.born_score,
        "born_rmse": angular.born_rmse,
        "angular_bin_coverage": angular.coverage,
        "phi_harmonic_2": angular.phi_harmonic_2,
        "no_fit_wrapped_gaussian_l1": angular.wrapped_gaussian_l1,
        "best_fit_wrapped_gaussian_sigma": angular.best_fit_wrapped_gaussian_sigma,
        "best_fit_wrapped_gaussian_l1": angular.best_fit_wrapped_gaussian_l1,
        "best_fit_wrapped_gaussian_js": angular.best_fit_wrapped_gaussian_js,
        "best_fit_wrapped_cauchy_gamma": angular.best_fit_wrapped_cauchy_gamma,
        "best_fit_wrapped_cauchy_l1": angular.best_fit_wrapped_cauchy_l1,
        "best_fit_wrapped_cauchy_js": angular.best_fit_wrapped_cauchy_js,
        "cauchy_log_likelihood_advantage_per_sample": angular.cauchy_log_likelihood_advantage_per_sample,
        "preferred_wrapped_model": angular.preferred_wrapped_model,
        "reciprocity_error": born.reciprocity_error,
        "tail_density_exponent": born.tail_density_exponent,
        "tail_survival_exponent": born.tail_survival_exponent,
        "max_radius": born.max_radius,
        "source_npz": str(path),
    }
    row.update(_radius_metrics(radii))
    return row


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"no rows available for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, Any]]:
    """Load previously analyzed rows for an incremental completed-case update."""
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _source_key(path: str | Path) -> str:
    """Return a stable, case-insensitive key for a spectrum source path."""
    return str(Path(path).resolve()).casefold()


def _finite_median(rows: list[dict[str, Any]], key: str) -> float:
    values = np.asarray([float(row[key]) for row in rows], dtype=float)
    values = values[np.isfinite(values)]
    return float(np.median(values)) if values.size else math.nan


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault((str(row["study"]), int(row["detector_n"])), []).append(row)
    summary: list[dict[str, Any]] = []
    for (study, detector_n), group in sorted(groups.items()):
        best_born = max(group, key=lambda row: float(row["S_born"]))
        strongest_cauchy = max(group, key=lambda row: float(row["cauchy_log_likelihood_advantage_per_sample"]))
        summary.append(
            {
                "study": study,
                "detector_n": detector_n,
                "spectra": len(group),
                "median_S_born": _finite_median(group, "S_born"),
                "max_S_born": float(best_born["S_born"]),
                "best_born_parameter": float(best_born["parameter_value"]),
                "best_born_t": float(best_born["t"]),
                "median_cauchy_advantage": _finite_median(group, "cauchy_log_likelihood_advantage_per_sample"),
                "cauchy_preferred_fraction": float(np.mean([row["preferred_wrapped_model"] == "wrapped_cauchy" for row in group])),
                "max_cauchy_advantage": float(strongest_cauchy["cauchy_log_likelihood_advantage_per_sample"]),
                "strongest_cauchy_parameter": float(strongest_cauchy["parameter_value"]),
                "strongest_cauchy_t": float(strongest_cauchy["t"]),
                "median_gaussian_js": _finite_median(group, "best_fit_wrapped_gaussian_js"),
                "median_cauchy_js": _finite_median(group, "best_fit_wrapped_cauchy_js"),
                "median_q99_over_q50": _finite_median(group, "radius_q99_over_q50"),
                "median_tail_density_exponent": _finite_median(group, "tail_density_exponent"),
                "median_phi_harmonic_2": _finite_median(group, "phi_harmonic_2"),
            }
        )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("work/zeus_single_pixel_atlas_scaling_2026-07-14"))
    parser.add_argument("--out", type=Path, default=Path("reports/zeus_single_pixel_analysis_2026-07-16"))
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument(
        "--reuse-existing",
        action="store_true",
        help="Reuse rows already present in the output spectrum_metrics.csv and analyze only new sources.",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    inventory: list[dict[str, Any]] = []
    rows = _read_csv(args.out / "spectrum_metrics.csv") if args.reuse_existing else []
    existing_sources = {
        _source_key(str(row["source_npz"]))
        for row in rows
        if row.get("source_npz")
    }
    for study_dir in sorted(path for path in args.root.iterdir() if path.is_dir() and path.name != ".mplconfig"):
        for case in sorted(path for path in study_dir.iterdir() if path.is_dir() and re.fullmatch(r"N\d+", path.name)):
            detector_n = int(case.name[1:])
            raw_paths = sorted(case.rglob("raw_t*.npz"))
            status = _status(case)
            inventory.append(
                {
                    "study": study_dir.name,
                    "detector_n": detector_n,
                    "status": status,
                    "raw_spectra": len(raw_paths),
                    "metrics_csv_count": len(list(case.rglob("*metrics.csv"))),
                }
            )
            if status != "complete":
                continue
            for index, raw_path in enumerate(raw_paths, start=1):
                if _source_key(raw_path) in existing_sources:
                    continue
                print(f"[{study_dir.name} N={detector_n}] {index}/{len(raw_paths)} {raw_path.name}", flush=True)
                row = analyze_spectrum(raw_path, study_dir.name, detector_n, args.bins)
                rows.append(row)
                existing_sources.add(_source_key(raw_path))

    summary = summarize(rows)
    _write_csv(args.out / "inventory.csv", inventory)
    _write_csv(args.out / "spectrum_metrics.csv", rows)
    _write_csv(args.out / "size_summary.csv", summary)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(args.root.resolve()),
        "complete_spectra_analyzed": len(rows),
        "bins": args.bins,
        "selection_rule": "Only N directories with DONE.json; partial/failed runs appear only in inventory.csv",
        "fit_models": {
            "wrapped_gaussian": "centered folded wrapped normal, fitted sigma",
            "wrapped_cauchy": "centered folded wrapped Cauchy, fitted gamma",
            "preference": "positive cauchy_log_likelihood_advantage_per_sample favors wrapped Cauchy",
        },
        "files": {
            "inventory": "inventory.csv",
            "spectrum_metrics": "spectrum_metrics.csv",
            "size_summary": "size_summary.csv",
        },
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
