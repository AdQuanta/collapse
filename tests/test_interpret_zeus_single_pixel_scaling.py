from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from examples.interpret_zeus_single_pixel_scaling import (
    AnalysisConfig,
    CsvRowRepository,
    ScalingAnalyzer,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "reports" / "zeus_single_pixel_analysis_2026-07-16"


def test_completed_aggregate_joint_gate_is_exact_matched_field_family() -> None:
    rows = CsvRowRepository(ANALYSIS / "spectrum_metrics.csv").load()
    analyzer = ScalingAnalyzer(
        AnalysisConfig(source=ANALYSIS / "spectrum_metrics.csv", output=ANALYSIS)
    )

    jointly_gated = analyzer.jointly_gated_born(rows)

    assert len(rows) == 1208
    assert len(jointly_gated) == 24
    assert {row["study"] for row in jointly_gated} == {"hz0"}
    assert {float(row["hz0"]) for row in jointly_gated} == {0.1}
    assert {float(row["hz"]) for row in jointly_gated} == {0.1}
    assert {int(float(row["detector_n"])) for row in jointly_gated} == set(range(11, 17))
    assert {float(row["t"]) for row in jointly_gated} == {1e3, 1e4, 1e5, 1e6}


def test_interpretation_summary_and_artifacts_match_source_count() -> None:
    summary = json.loads((ANALYSIS / "interpretation_summary.json").read_text(encoding="utf-8"))

    assert summary["spectra"] == 1208
    assert summary["jointly_gated_born_count"] == 24
    assert summary["studies"]["jpm_hz"]["cauchy_preferred_fraction"] == 1.0
    assert summary["studies"]["jpm_hz"]["detector_n_max"] == 15
    assert summary["studies"]["hz0"]["detector_n_max"] == 16
    for name in (
        "parameter_summary.csv",
        "correlations.csv",
        "top_born_candidates.csv",
        "jointly_gated_born_candidates.csv",
        "top_heavy_tail_candidates.csv",
        "finite_size_diagnostics.png",
        "regime_tradeoffs.png",
        "conclusions.md",
    ):
        path = ANALYSIS / name
        assert path.is_file()
        assert path.stat().st_size > 0


def test_born_radius_law_has_required_reciprocity_and_ratio() -> None:
    radii = np.geomspace(1e-4, 1e4, 200)
    q = lambda value: 4.0 / (math.pi * (1.0 + value**2) ** 2)

    assert np.allclose(q(1.0 / radii), radii**4 * q(radii), rtol=1e-12, atol=1e-12)

    theta = np.linspace(1e-4, math.pi - 1e-4, 200)
    radius = np.tan(theta / 2.0)
    p_theta = q(radius) * 0.5 * (1.0 + radius**2)
    p_reflected = (1.0 - np.cos(theta)) / math.pi
    ratio = p_theta / (p_theta + p_reflected)

    assert np.allclose(p_theta, (1.0 + np.cos(theta)) / math.pi)
    assert np.allclose(ratio, np.cos(theta / 2.0) ** 2)
