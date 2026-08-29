"""Validate the 2026-07-14 J=0, Jpm=1 field-neighborhood atlas."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures" / "single_pixel_jpm_hz_atlas_2026-07-14"
RAW = ROOT / "work" / "single_pixel_jpm_hz_sweep_2026-07-14"
MANIFEST = FIGURES / "jpm_hz_atlas_manifest.json"
METRICS = FIGURES / "N10_jpm_hz_metrics.csv"
REPORT = ROOT / "reports" / "single_pixel_jpm_hz_atlas_validation_2026-07-14.json"
SCRIPT = ROOT / "scripts" / "plot_single_pixel_hz_resonance_atlas.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def raw_path(hz: float, time_value: float) -> Path:
    return RAW / "N10" / f"hz_{hz:+.4f}" / f"raw_t{time_value:.12g}.npz"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    centers = [-2.0, -1.0, 0.0, 1.0, 2.0]
    offsets = [-0.05, -0.01, 0.0, 0.01, 0.05]
    fields = [round(center + offset, 10) for center in centers for offset in offsets]
    times = [1e3, 1e4, 1e5, 1e6]
    fixed = manifest["fixed_parameters"]

    require(manifest["detector_n"] == 10 and manifest["total_qubits"] == 11, "unexpected system size")
    require(manifest["reference_centers"] == centers, "unexpected reference centers")
    require(manifest["offsets"] == offsets and manifest["hz"] == fields, "unexpected field grid")
    require(manifest["times"] == times, "unexpected time grid")
    require(fixed["J"] == 0.0 and fixed["Jpm"] == 1.0 and fixed["hz0"] == 0.0, "wrong detector model")
    require(fixed["Jx"] == 0.01, "collective Jx must equal 0.01")
    require(math.isclose(fixed["Jx_edge"], 0.01 / math.sqrt(10)), "incorrect edge Jx")
    require("Eq. (6.4)" in manifest["wrapped_gaussian_reference"], "spectral theory provenance is missing")

    require(len(manifest["atlases"]) == 20, "expected 5 neighborhoods x 4 times")
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
    require(len(rows) == 100, "expected 25 fields x 4 times")
    require({float(row["hz"]) for row in rows} == set(fields), "metrics field grid is incomplete")
    require({float(row["t"]) for row in rows} == set(times), "metrics time grid is incomplete")

    for row in rows:
        for key in ("S_born", "born_rmse", "angular_bin_coverage", "phi_harmonic_2", "theory_variance", "wrapped_gaussian_l1"):
            require(math.isfinite(float(row[key])), f"non-finite metric {key}")
        require(float(row["finite_eigenvalues"]) == 1024, "relative spectrum is incomplete")
        require(0.0 <= float(row["angular_bin_coverage"]) <= 1.0, "coverage outside [0,1]")
        path = raw_path(float(row["hz"]), float(row["t"]))
        require(path.is_file(), f"missing raw spectrum: {path}")
        with np.load(path) as raw:
            require(raw["eigenvalues"].shape == (1024,), f"wrong eigenvalue count in {path}")
            require(raw["theta"].shape == (1024,), f"wrong theta count in {path}")
            require(np.isfinite(raw["eigenvalues"]).all(), f"non-finite eigenvalues in {path}")
            require(float(raw["J"]) == 0.0 and float(raw["Jpm"]) == 1.0, f"wrong J/Jpm in {path}")
            require(math.isclose(float(raw["Jx_edge"]), 0.01 / math.sqrt(10)), f"wrong edge Jx in {path}")

    lookup = {(float(row["hz"]), float(row["t"])): row for row in rows}
    symmetry: dict[str, float] = {}
    for metric in ("S_born", "born_rmse", "angular_bin_coverage", "theory_variance", "wrapped_gaussian_l1", "phi_harmonic_2"):
        differences = [
            abs(float(lookup[(hz, t)][metric]) - float(lookup[(-hz, t)][metric]))
            for hz in fields if hz < 0.0 and -hz in fields for t in times
        ]
        symmetry[metric] = max(differences)
        tolerance = 0.02 if metric == "phi_harmonic_2" else (1e-6 if metric == "theory_variance" else 1e-8)
        require(symmetry[metric] < tolerance, f"+/-h_z symmetry failed for {metric}")

    edge_rows = [lookup[(edge, t)] for edge in (-1.0, 1.0) for t in times]
    require(all(float(row["S_born"]) < 0.0 for row in edge_rows), "band-edge S_born should be negative")
    require(all(float(row["angular_bin_coverage"]) >= 0.70 for row in edge_rows), "band-edge polar support is unexpectedly narrow")
    center_rows = [lookup[(0.0, t)] for t in times]
    require(all(float(row["S_born"]) > 0.0 for row in center_rows), "h_z=0 S_born should be positive")
    require(float(lookup[(1.0, 1e6)]["theory_variance"]) > 100.0 * float(lookup[(2.0, 1e6)]["theory_variance"]), "band-edge theory enhancement is missing")

    source = SCRIPT.read_text(encoding="utf-8")
    require("ax_hist.stairs(diagnostic.p_theta" in source, "P(theta) is not histogram stairs")
    require("ax_hist.stairs(diagnostic.p_reflected" in source, "P(pi-theta) is not histogram stairs")
    require('"o-"' in source and "diagnostic.centers[diagnostic.occupied]" in source, "R(theta) is not line-connected")

    result = {
        "status": "passed",
        "detector_n": 10,
        "total_qubits": 11,
        "J": 0.0,
        "Jpm": 1.0,
        "collective_Jx": 0.01,
        "edge_Jx": 0.01 / math.sqrt(10),
        "reference_centers": centers,
        "offsets": offsets,
        "times": times,
        "metric_rows": len(rows),
        "raw_spectra": len(rows),
        "finite_eigenvalues_per_spectrum": 1024,
        "figures": image_checks,
        "symmetry_max_abs_error": symmetry,
        "reference_S_born": {
            f"hz={center:g},t={t:.0e}": float(lookup[(center, t)]["S_born"])
            for center in centers for t in times
        },
        "rendering_contract": {
            "P_theta": "histogram stairs",
            "P_pi_minus_theta": "histogram stairs",
            "R_theta": "occupied-bin points connected by lines",
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
