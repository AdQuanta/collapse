"""Validate the 2026-07-14 h_z resonance-neighborhood sweep."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures" / "single_pixel_hz_resonance_atlas_2026-07-14"
RAW = ROOT / "work" / "single_pixel_hz_resonance_sweep_2026-07-14"
MANIFEST = FIGURES / "hz_resonance_atlas_manifest.json"
METRICS = FIGURES / "N10_hz_resonance_metrics.csv"
REPORT = ROOT / "reports" / "single_pixel_hz_resonance_atlas_validation_2026-07-14.json"
SCRIPT = ROOT / "examples" / "plot_single_pixel_hz_resonance_atlas.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def raw_path(detector_n: int, hz: float, time_value: float) -> Path:
    return RAW / f"N{detector_n}" / f"hz_{hz:+.4f}" / f"raw_t{time_value:.12g}.npz"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_centers = [-2.0, 0.0, 2.0]
    expected_offsets = [-0.05, -0.01, 0.0, 0.01, 0.05]
    expected_hz = [round(center + offset, 10) for center in expected_centers for offset in expected_offsets]
    expected_times = [1e3, 1e4, 1e5, 1e6]

    require(manifest["detector_n"] == 10 and manifest["total_qubits"] == 11, "unexpected system size")
    require(manifest["resonance_centers"] == expected_centers, "unexpected resonance centers")
    require(manifest["offsets"] == expected_offsets, "unexpected detuning grid")
    require(manifest["hz"] == expected_hz, "unexpected h_z grid")
    require(manifest["times"] == expected_times, "unexpected time grid")
    fixed = manifest["fixed_parameters"]
    require(fixed["J"] == 1.0 and fixed["hz0"] == 0.0, "unexpected fixed Hamiltonian parameters")
    require(fixed["Jx"] == 0.01, "collective Jx must equal 0.01")
    require(math.isclose(fixed["Jx_edge"], 0.01 / math.sqrt(10)), "incorrect per-edge Jx metadata")

    require(len(manifest["atlases"]) == 12, "expected 3 centers x 4 times atlases")
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
    require(len(rows) == 60, "expected 15 fields x 4 times")
    require({float(row["hz"]) for row in rows} == set(expected_hz), "metrics h_z grid is incomplete")
    require({float(row["t"]) for row in rows} == set(expected_times), "metrics time grid is incomplete")
    require({float(row["resonance_center"]) for row in rows} == set(expected_centers), "metrics centers are incomplete")

    for row in rows:
        for key in ("S_born", "born_rmse", "angular_bin_coverage", "phi_harmonic_2", "theory_variance", "wrapped_gaussian_l1"):
            require(math.isfinite(float(row[key])), f"non-finite metric {key}")
        require(0.0 <= float(row["angular_bin_coverage"]) <= 1.0, "coverage outside [0,1]")
        require(float(row["finite_eigenvalues"]) == 1024, "relative spectrum is incomplete")
        path = raw_path(10, float(row["hz"]), float(row["t"]))
        require(path.is_file(), f"missing raw spectrum: {path}")
        with np.load(path) as raw:
            require(raw["eigenvalues"].shape == (1024,), f"wrong eigenvalue count in {path}")
            require(raw["theta"].shape == (1024,), f"wrong theta count in {path}")
            require(np.isfinite(raw["eigenvalues"]).all(), f"non-finite eigenvalues in {path}")
            require(math.isclose(float(raw["Jx"]), 0.01), f"wrong collective Jx in {path}")
            require(math.isclose(float(raw["Jx_edge"]), 0.01 / math.sqrt(10)), f"wrong edge Jx in {path}")

    lookup = {(float(row["hz"]), float(row["t"])): row for row in rows}
    symmetry_max_error: dict[str, float] = {}
    for metric in ("S_born", "born_rmse", "angular_bin_coverage", "phi_harmonic_2"):
        differences = []
        for hz in expected_hz:
            if hz < 0 and -hz in expected_hz:
                for time_value in expected_times:
                    differences.append(abs(float(lookup[(hz, time_value)][metric]) - float(lookup[(-hz, time_value)][metric])))
        symmetry_max_error[metric] = max(differences)
        tolerance = 0.02 if metric == "phi_harmonic_2" else 1e-9
        # Polar diagnostics are exactly symmetric.  The azimuthal harmonic is
        # basis-sensitive inside degenerate subspaces, so only its small
        # numerical spread is constrained.
        require(symmetry_max_error[metric] < tolerance, f"+/-h_z symmetry failed for {metric}")

    exact = [row for row in rows if abs(float(row["detuning"])) < 1e-14]
    require(len(exact) == 12, "expected three exact resonances at four times")
    require(all(float(row["S_born"]) < 0.0 for row in exact), "exact resonances should have negative Born score")

    source = SCRIPT.read_text(encoding="utf-8")
    require("ax_hist.stairs(diagnostic.p_theta" in source, "P(theta) is not rendered as histogram stairs")
    require("ax_hist.stairs(diagnostic.p_reflected" in source, "P(pi-theta) is not rendered as histogram stairs")
    require('"o-"' in source and "diagnostic.centers[diagnostic.occupied]" in source, "R(theta) points are not line-connected")

    result = {
        "status": "passed",
        "detector_n": 10,
        "total_qubits": 11,
        "collective_Jx": 0.01,
        "edge_Jx": 0.01 / math.sqrt(10),
        "resonance_centers": expected_centers,
        "offsets": expected_offsets,
        "times": expected_times,
        "metric_rows": len(rows),
        "raw_spectra": len(rows),
        "finite_eigenvalues_per_spectrum": 1024,
        "figures": image_checks,
        "symmetry_max_abs_error": symmetry_max_error,
        "exact_resonance_S_born": {
            f"hz={float(row['hz']):g},t={float(row['t']):.0e}": float(row["S_born"])
            for row in exact
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
