"""Audit the fresh study namespace without consulting prior result directories."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FRESH = ROOT / "work" / "single_pixel_quspin_fresh_2026-07-12"
OUT = ROOT / "reports" / "single_pixel_quspin_fresh_validation_2026-07-12.json"
REQUIRED_TIMES = np.array([100.0, 1_000.0, 10_000.0, 100_000.0, 1_000_000.0])


def raw_times(case: Path) -> np.ndarray:
    return np.array(sorted(float(path.stem.split("_t")[-1]) for path in case.glob("raw_*.npz")))


def main() -> None:
    failures: list[str] = []
    result: dict = {"fresh_root": str(FRESH), "checks": {}, "failures": failures}

    mandatory_cases = sorted((FRESH / "mandatory_N10" / "N10").glob("hz_*"))
    near_cases = sorted((FRESH / "near_resonance_N8" / "N08").glob("hz_*"))
    long_cases = sorted((FRESH / "long_average_N8_v2" / "N08").glob("hz_*"))
    result["checks"]["case_counts"] = {"mandatory": len(mandatory_cases), "near": len(near_cases), "long": len(long_cases)}
    if (len(mandatory_cases), len(near_cases), len(long_cases)) != (7, 27, 7):
        failures.append("unexpected case counts")

    max_solve = 0.0
    max_eigen = 0.0
    max_norm_error = 0.0
    mandatory_sborn: dict[float, list[float]] = {}
    for case in mandatory_cases:
        times = raw_times(case)
        if times.size != 5 or not np.allclose(times, REQUIRED_TIMES):
            failures.append(f"mandatory time mismatch: {case}")
        metadata = json.loads((case / "metadata.json").read_text(encoding="utf-8"))
        distributions = metadata["runtime"]["distributions"]
        if distributions["quspin"] != "1.0.0" or distributions["quspin-extensions"] != "0.1.6":
            failures.append(f"environment mismatch: {case}")
        if metadata["summary"]["status"] != "completed":
            failures.append(f"incomplete metadata: {case}")
        if metadata["summary"]["detector_spacing_sector"]["sectors_combined"]:
            failures.append(f"mixed spacing sectors: {case}")
        hz = float(metadata["config"]["hz"])
        mandatory_sborn[hz] = [float(row["S_born"]) for row in metadata["summary"]["time_diagnostics"]]
        for path in case.glob("raw_*.npz"):
            raw = np.load(path)
            if not np.all(np.isfinite(raw["theta"])) or np.any(raw["theta"] < 0) or np.any(raw["theta"] > np.pi):
                failures.append(f"invalid theta: {path}")
            max_solve = max(max_solve, float(raw["solve_residual"]))
            max_eigen = max(max_eigen, float(raw["eigen_residual_max"]))
        aggregate = np.load(case / "aggregate.npz")
        widths = np.diff(aggregate["theta_edges"])
        max_norm_error = max(max_norm_error, abs(float(np.sum(aggregate["p_theta"] * widths)) - 1.0))

    for hz in (1.0, 2.0, 3.0):
        if not np.allclose(mandatory_sborn[hz], mandatory_sborn[-hz], atol=1e-12):
            failures.append(f"positive/negative symmetry failed at |hz|={hz}")

    for case in near_cases:
        times = raw_times(case)
        if times.size != 5 or not np.allclose(times, REQUIRED_TIMES):
            failures.append(f"near-resonance time mismatch: {case}")

    long_time_counts = []
    for case in long_cases:
        times = raw_times(case)
        if times.size != 68:
            failures.append(f"long-grid raw count mismatch: {case} ({times.size})")
        summary = json.loads((case / "long_time_summary.json").read_text(encoding="utf-8"))
        long_time_counts.append(int(summary["time_count"]))
        average = np.load(case / "long_time_average.npz")
        norm = float(np.sum(average["p_theta"] * np.diff(average["theta_edges"])))
        if not np.isclose(norm, 1.0, atol=1e-12):
            failures.append(f"long-time normalization mismatch: {case}")

    result["checks"].update({
        "raw_time_points": {"mandatory": sum(raw_times(case).size for case in mandatory_cases), "near": sum(raw_times(case).size for case in near_cases), "long": sum(raw_times(case).size for case in long_cases)},
        "long_time_average_counts": long_time_counts,
        "max_solve_residual": max_solve,
        "max_eigen_residual": max_eigen,
        "max_histogram_normalization_error": max_norm_error,
        "positive_negative_symmetry": "passed" if not any("symmetry" in item for item in failures) else "failed",
        "fresh_only_policy": "validated paths are descendants of the dedicated fresh root",
    })
    result["status"] = "passed" if not failures else "failed"
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
