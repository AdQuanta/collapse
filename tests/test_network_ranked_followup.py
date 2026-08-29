"""Contracts for high/low random-network follow-up campaigns."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

from core.detector_graphs import DetectorGraphSpec, detector_graph_edges
from core.network_ranked_followup import (
    resampled_graph_spec,
    select_extreme_cases,
    select_top_cases,
)
from core.ranked_born_campaign import hz0_variants
from scripts.run_zeus_network_top_hz0_variants_N12 import _exact_source_graph


ROOT = Path(__file__).resolve().parents[1]


def _write_case(root: Path, index: int, score: float) -> None:
    case = root / "jy_zero" / "N12" / f"config_{index:03d}"
    case.mkdir(parents=True)
    graph_spec = {
        "kind": "erdos_renyi",
        "seed": 1000 + index,
        "erdos_renyi_p": 0.3,
        "watts_strogatz_k": 4,
        "watts_strogatz_p": 0.3,
        "barabasi_albert_m": 2,
        "regular_degree": 4,
        "require_connected": True,
        "max_attempts": 10000,
    }
    edges = detector_graph_edges(12, DetectorGraphSpec(**graph_spec))
    (case / "metrics.json").write_text(
        json.dumps({"S_born": score}), encoding="utf-8"
    )
    (case / "metadata.json").write_text(
        json.dumps(
            {
                "N": 12,
                "hz0": 0.0,
                "evolution_time": 1.0e6,
                "configuration": {
                    "hz": 0.2,
                    "j": 0.7,
                    "jpm": 0.3,
                    "jx": 0.01,
                },
                "detector_graph": {
                    "canonical_kind": "erdos_renyi",
                    "spec": graph_spec,
                    "edges_zero_based": [list(edge) for edge in edges],
                },
            }
        ),
        encoding="utf-8",
    )
    (case / "COMPLETE.json").write_text(
        json.dumps({"status": "complete"}), encoding="utf-8"
    )


def test_extreme_selection_is_disjoint_and_ranked(tmp_path) -> None:
    for index, score in enumerate((0.2, 0.8, 0.1, 0.6, 0.4, 0.3)):
        _write_case(tmp_path, index, score)
    selected = select_extreme_cases(
        tmp_path,
        family="erdos_renyi",
        family_index=0,
        count_per_tail=2,
    )

    assert [item.case.source_s_born for item in selected] == [0.8, 0.6, 0.1, 0.2]
    assert [item.cohort for item in selected] == [
        "highest",
        "highest",
        "lowest",
        "lowest",
    ]


def test_top_selection_keeps_only_decreasing_highest_tail(tmp_path) -> None:
    for index, score in enumerate((0.2, 0.8, 0.1, 0.6, 0.4, 0.3)):
        _write_case(tmp_path, index, score)

    selected = select_top_cases(
        tmp_path,
        family="erdos_renyi",
        family_index=0,
        count=3,
    )

    assert [item.case.source_s_born for item in selected] == [0.8, 0.6, 0.4]
    assert [item.cohort_rank for item in selected] == [1, 2, 3]
    assert all(item.cohort == "highest" for item in selected)


def test_exact_source_graph_verifies_saved_edges(tmp_path) -> None:
    _write_case(tmp_path, 0, 0.8)
    selected = select_top_cases(
        tmp_path,
        family="erdos_renyi",
        family_index=0,
        count=1,
    )[0]

    graph_spec, provenance = _exact_source_graph(selected, detector_n=12)

    assert graph_spec.seed == 1000
    assert provenance["edge_validation"] == "saved edge list exactly reproduced"
    assert provenance["is_same_edge_set_as_source"] is True

    bad_metadata = dict(selected.case.source_graph_metadata or {})
    bad_metadata["edges_zero_based"] = [[0, 1]]
    bad_case = replace(selected.case, source_graph_metadata=bad_metadata)
    bad_selection = replace(selected, case=bad_case)
    try:
        _exact_source_graph(bad_selection, detector_n=12)
    except ValueError as exc:
        assert "saved graph is not reproduced" in str(exc)
    else:
        raise AssertionError("mismatched source edges were accepted")


def test_resampled_graph_seeds_are_distinct_and_preserve_parameters(tmp_path) -> None:
    for index, score in enumerate((0.8, 0.7, 0.2, 0.1)):
        _write_case(tmp_path, index, score)
    selected = select_extreme_cases(
        tmp_path,
        family="erdos_renyi",
        family_index=0,
        count_per_tail=1,
    )[0]
    source_seed = selected.case.graph_spec["seed"]
    generated = [resampled_graph_spec(selected, index)[0] for index in range(5)]
    edge_sets = [detector_graph_edges(12, spec) for spec in generated]
    source_edges = detector_graph_edges(
        12,
        DetectorGraphSpec(**selected.case.graph_spec),
    )

    assert len({spec.seed for spec in generated}) == 5
    assert all(spec.seed != source_seed for spec in generated)
    assert all(spec.erdos_renyi_p == 0.3 for spec in generated)
    assert len(set(edge_sets)) == 5
    assert all(edges != source_edges for edges in edge_sets)


def test_top_network_hz0_campaign_cardinality_and_pbs_contract() -> None:
    config = json.loads(
        (ROOT / "configs/zeus_network_top_hz0_variants_N12.json").read_text()
    )
    assert len(config["families"]) == 4
    assert config["top_count_per_family"] == 10
    assert config["target_detector_n"] == 12
    assert config["include_hz0_zero"] is True
    assert config["hz0_additive_offsets"] == [
        -0.001,
        -0.0001,
        0.0,
        0.0001,
        0.001,
    ]
    assert len(hz0_variants(0.2, config["hz0_additive_offsets"])) == 6
    selected_count = len(config["families"]) * config["top_count_per_family"]
    assert selected_count == 40
    assert selected_count // config["cases_per_array_task"] == 20
    assert selected_count * 6 == 240

    pbs = (ROOT / "hpc/zeus_network_top_hz0_variants_N12_array.pbs").read_text()
    wrapper = (
        ROOT / "hpc/submit_zeus_network_top_hz0_variants_N12.sh"
    ).read_text()
    assert "#PBS -q zeus_new_q" in pbs
    assert "#PBS -J 0-19" in pbs
    assert "mem=128gb" in pbs
    assert "ProcessPoolExecutor" not in pbs
    assert "--describe" in wrapper
    assert 'qsub -J "0-$ARRAY_LAST"' in wrapper
