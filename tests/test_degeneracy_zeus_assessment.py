from __future__ import annotations

import json
from pathlib import Path

from core.degeneracy_zeus_assessment import AssessmentPaths, run_assessment


ROOT = Path(__file__).resolve().parent.parent


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
