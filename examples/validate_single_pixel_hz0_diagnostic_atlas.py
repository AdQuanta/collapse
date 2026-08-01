"""Validate the 2026-07-14 central-field sweep and diagnostic atlases."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures" / "single_pixel_hz0_diagnostic_atlas_2026-07-14"
RAW = ROOT / "work" / "single_pixel_hz0_sweep_2026-07-14"
MANIFEST = FIGURES / "hz0_diagnostic_atlas_manifest.json"
METRICS = FIGURES / "N10_hz0_diagnostic_metrics.csv"
REPORT = ROOT / "reports" / "single_pixel_hz0_diagnostic_atlas_validation_2026-07-14.json"
SCRIPT = ROOT / "examples" / "plot_single_pixel_hz0_diagnostic_atlas.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_hz0 = [0.0, 0.05, 0.09, 0.1, 0.11, 0.15, 0.2]
    expected_times = [1e3, 1e4, 1e5, 1e6]
    require(manifest["detector_n"] == 10 and manifest["total_qubits"] == 11, "unexpected system size")
    require(manifest["hz0"] == expected_hz0, "unexpected central-field grid")
    require(manifest["times"] == expected_times, "unexpected time grid")
    fixed = manifest["fixed_parameters"]
    require(fixed["J"] == 1.0 and fixed["hz"] == 0.1, "unexpected fixed Hamiltonian parameters")
    require(fixed["Jx"] == 0.01, "collective Jx must equal 0.01")
    require(math.isclose(fixed["Jx_edge"], 0.01 / math.sqrt(10)), "incorrect per-edge Jx metadata")

    image_checks: dict[str, dict[str, int]] = {}
    for relative in [*manifest["atlases"], manifest["summary_plot"]]:
        path = ROOT / relative
        require(path.is_file() and path.stat().st_size > 100_000, f"missing or undersized figure: {path}")
        with Image.open(path) as image:
            width, height = image.size
        require(width >= 3000 and height >= 1000, f"figure resolution is too low: {path}")
        image_checks[path.name] = {"width": width, "height": height, "bytes": path.stat().st_size}

    with METRICS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 28, "expected 7 fields x 4 times")
    require({float(row["hz0"]) for row in rows} == set(expected_hz0), "metrics central-field grid is incomplete")
    require({float(row["t"]) for row in rows} == set(expected_times), "metrics time grid is incomplete")
    for row in rows:
        for key in ("S_born", "born_rmse", "angular_bin_coverage", "phi_harmonic_2", "theory_variance", "wrapped_gaussian_l1"):
            require(math.isfinite(float(row[key])), f"non-finite metric {key}")
        require(0 <= float(row["angular_bin_coverage"]) <= 1, "coverage outside [0,1]")
        require(float(row["finite_eigenvalues"]) == 1024, "relative spectrum is incomplete")
        path = RAW / "N10" / f"hz0_{float(row['hz0']):+.4f}" / f"raw_t{float(row['t']):.12g}.npz"
        require(path.is_file(), f"missing raw spectrum: {path}")
        raw = np.load(path)
        require(raw["eigenvalues"].shape == (1024,), f"wrong eigenvalue count in {path}")
        require(raw["theta"].shape == (1024,), f"wrong theta count in {path}")

    matched = [row for row in rows if float(row["hz0"]) == 0.1]
    require(all(float(row["local_resonance_distance"]) < 1e-14 for row in matched), "matched field is not marked exact-resonant")
    source = SCRIPT.read_text(encoding="utf-8")
    require("ax_hist.stairs(p_theta" in source and "ax_hist.stairs(p_reflected" in source, "empirical P distributions are not histogram stairs")
    require('"o-"' in source and "centers[occupied]" in source, "R(theta) points are not line-connected")

    result = {
        "status": "passed",
        "detector_n": 10,
        "total_qubits": 11,
        "hz0": expected_hz0,
        "times": expected_times,
        "metric_rows": len(rows),
        "raw_spectra": len(rows),
        "finite_eigenvalues_per_spectrum": 1024,
        "figures": image_checks,
        "matched_S_born": {row["t"]: float(row["S_born"]) for row in matched},
        "rendering_contract": {
            "P_theta": "histogram stairs",
            "P_pi_minus_theta": "histogram stairs",
            "R_theta": "occupied-bin points connected by lines",
        },
    }
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
