from __future__ import annotations

import json
from pathlib import Path

import pytest

from collapse.degeneracy_zeus_assessment import (
    AssessmentPaths,
    DegeneracyConjectureAssessment,
    run_assessment,
)

from conftest import requires_paths


ROOT = Path(__file__).resolve().parent.parent


@requires_paths(
    "work/zeus_degeneracy_heavy_tail_iff_N13_N18",
    "work/zeus_relative_scale_regimes_20260724_144102",
)
def test_transferred_zeus_results_falsify_both_directions(tmp_path: Path) -> None:
    paths = AssessmentPaths.defaults(ROOT, tmp_path / "assessment")
    summary = run_assessment(paths)

    assert summary["verdict"] == "universal_iff_falsified_both_directions"
    assert summary["primary_complete_target_sizes"] == [13, 14, 15, 16]
    assert summary["primary_complete_relative_sizes"] == [13, 14, 15, 16]
    truth = summary["pooled_target_truth_table"]
    assert truth["active_not_broad"] > 0
    assert truth["inactive_but_broad"] > 0
    assert summary["stable_sufficiency_counterexamples"] == [
        "active_flat_atomic",
        "nonising_su2_active_hz0",
    ]
    assert summary["stable_necessity_counterexamples"] == [
        "inactive_near_plus_2J",
        "inactive_near_minus_2J",
    ]
    assert summary["cross_pipeline_reproducibility"][
        "maximum_primary_metric_absolute_difference"
    ] == 0.0
    assert summary["positive_negative_hz_symmetry"][
        "maximum_primary_metric_absolute_difference"
    ] <= 2.0e-5
    assert summary["target_validation"]["figure_paths_present"]
    assert summary["relative_validation"]["figure_paths_present"]
    assert (paths.output_root / "targeted_logic_matrix.png").is_file()
    assert (paths.output_root / "decisive_metrics_vs_N.png").is_file()
    assert (paths.output_root / "relative_scale_broadness_persistence.png").is_file()
    persisted = json.loads(
        (paths.output_root / "analysis_summary.json").read_text(encoding="utf-8")
    )
    assert persisted["verdict"] == summary["verdict"]


def test_empty_truth_table_fails_closed_instead_of_dividing_by_zero() -> None:
    """An absent checkpoint set must not be summarized as a 0/0 agreement.

    The pooled agreement fraction previously divided by the number of complete
    rows, so a missing or incomplete transfer surfaced as a bare
    ``ZeroDivisionError`` deep in the analysis rather than as a statement about
    the data.  This is the repository's fail-closed convention, matching
    ``reproduce_matched_ring_full_sphere.py``.
    """

    assessment = DegeneracyConjectureAssessment(
        targeted_rows=[],
        relative_rows=[],
        complete_target_sizes=[],
        complete_relative_sizes=[],
        project_root=ROOT,
    )

    with pytest.raises(ValueError, match="no complete targeted rows"):
        assessment.truth_table_rows()
