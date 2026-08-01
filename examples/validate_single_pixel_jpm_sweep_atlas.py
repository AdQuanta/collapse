"""Validate the production fixed-J plus-minus-coupling atlas."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from plot_single_pixel_jpm_sweep_atlas import DEFAULT_JPM_VALUES, DEFAULT_TIMES, raw_path


ROOT = Path(__file__).resolve().parent.parent
RAW_ROOT = ROOT / "work" / "single_pixel_jpm_sweep_2026-07-14"
FIGURE_ROOT = ROOT / "figures" / "single_pixel_jpm_sweep_atlas_2026-07-14"
REPORT_PATH = ROOT / "reports" / "single_pixel_jpm_sweep_atlas_validation_2026-07-14.json"


def main() -> None:
    detector_n = 10
    hz = 0.1
    expected_dimension = 2**detector_n
    manifest_path = FIGURE_ROOT / "jpm_sweep_atlas_manifest.json"
    metrics_path = FIGURE_ROOT / f"N{detector_n}_jpm_sweep_metrics.csv"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["detector_n"] == detector_n
    assert manifest["total_qubits"] == detector_n + 1
    assert tuple(manifest["Jpm_values"]) == DEFAULT_JPM_VALUES
    assert tuple(manifest["times"]) == DEFAULT_TIMES
    assert manifest["Jpm_equals_J_included"] is True
    assert manifest["fixed_parameters"]["J"] == 1.0
    assert manifest["fixed_parameters"]["hz"] == hz
    assert manifest["fixed_parameters"]["hz0"] == 0.0
    assert manifest["fixed_parameters"]["Jx"] == 0.01
    assert math.isclose(manifest["fixed_parameters"]["Jx_edge"], 0.01 / math.sqrt(detector_n))
    assert "stairs histograms" in manifest["empirical_distribution_rendering"]
    assert "connected by lines" in manifest["ratio_rendering"]

    raw_checks: list[dict[str, float | int | str]] = []
    for jpm in DEFAULT_JPM_VALUES:
        for time_value in DEFAULT_TIMES:
            path = raw_path(RAW_ROOT, detector_n, jpm, hz, time_value)
            assert path.is_file(), path
            with np.load(path) as raw:
                eigenvalues = np.asarray(raw["eigenvalues"], dtype=np.complex128)
                theta = np.asarray(raw["theta"], dtype=float)
                assert eigenvalues.shape == (expected_dimension,)
                assert theta.shape == (expected_dimension,)
                assert np.all(np.isfinite(eigenvalues.real))
                assert np.all(np.isfinite(eigenvalues.imag))
                assert np.all(np.isfinite(theta))
                assert np.all((0.0 <= theta) & (theta <= np.pi))
                assert float(raw["J"]) == 1.0
                assert float(raw["Jpm"]) == jpm
                assert float(raw["Jx"]) == 0.01
                assert math.isclose(float(raw["Jx_edge"]), 0.01 / math.sqrt(detector_n))
                assert float(raw["hz"]) == hz
                assert float(raw["hz0"]) == 0.0
                assert float(raw["theory_variance"]) >= 0.0
            raw_checks.append({"Jpm": jpm, "t": time_value, "path": str(path)})

    with metrics_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len(DEFAULT_JPM_VALUES) * len(DEFAULT_TIMES)
    combinations = {(float(row["Jpm"]), float(row["t"])) for row in rows}
    assert combinations == {(jpm, t) for jpm in DEFAULT_JPM_VALUES for t in DEFAULT_TIMES}
    for row in rows:
        assert int(float(row["finite_eigenvalues"])) == expected_dimension
        assert 0.0 <= float(row["angular_bin_coverage"]) <= 1.0
        assert 0.0 <= float(row["phi_harmonic_2"]) <= 1.0 + 1.0e-12
        assert float(row["born_rmse"]) >= 0.0
        assert float(row["wrapped_gaussian_l1"]) >= 0.0

    figure_paths = [FIGURE_ROOT / f"N{detector_n}_jpm_sweep_atlas_t1e{power}.png" for power in (3, 4, 5, 6)]
    figure_paths.append(FIGURE_ROOT / f"N{detector_n}_jpm_sweep_summary.png")
    figure_checks: list[dict[str, object]] = []
    for path in figure_paths:
        assert path.is_file(), path
        with Image.open(path) as image:
            width, height = image.size
            assert width >= 2500
            assert height >= 1500
            rgb = image.convert("RGB")
            corners = [rgb.getpixel((0, 0)), rgb.getpixel((width - 1, 0)), rgb.getpixel((0, height - 1))]
            assert all(min(pixel) >= 245 for pixel in corners)
        figure_checks.append({"path": str(path), "width": width, "height": height})

    source = (ROOT / "examples" / "plot_single_pixel_jpm_sweep_atlas.py").read_text(encoding="utf-8")
    assert source.count(".stairs(") >= 2
    assert '"o-"' in source

    equality_rows = [row for row in rows if float(row["Jpm"]) == 1.0]
    report = {
        "status": "passed",
        "raw_spectrum_count": len(raw_checks),
        "finite_eigenvalues_per_spectrum": expected_dimension,
        "figure_count": len(figure_checks),
        "figures": figure_checks,
        "Jpm_values": DEFAULT_JPM_VALUES,
        "times": DEFAULT_TIMES,
        "Jpm_equals_J_metrics": equality_rows,
        "rendering_contract": {
            "P_distributions": "histogram stairs",
            "R_theta": "occupied-bin points connected by lines",
        },
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
