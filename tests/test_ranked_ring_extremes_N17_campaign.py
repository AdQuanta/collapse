"""Contracts for the exact ranked-ring N=17 Zeus continuation."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.run_zeus_ranked_ring_extremes_N17 import (
    _prior_result_matches,
    output_dir_for_case,
    select_cases,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "zeus_ranked_ring_extremes_N17.json"


def _config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def test_exact_spacing_study_selection_is_pinned_and_disjoint() -> None:
    config = _config()
    selected = select_cases(config)

    assert config["target_detector_n"] == 17
    assert config["count_per_tail"] == 10
    assert config["cases_per_array_task"] == 2
    assert config["array_size"] == 20
    assert len(selected) == 40
    assert len({(item.family, item.case.source_case) for item in selected}) == 40
    assert {
        (family, tail): sum(
            item.family == family and item.tail == tail for item in selected
        )
        for family in ("nearest_neighbor", "second_neighbor")
        for tail in ("highest", "lowest")
    } == {
        ("nearest_neighbor", "highest"): 10,
        ("nearest_neighbor", "lowest"): 10,
        ("second_neighbor", "highest"): 10,
        ("second_neighbor", "lowest"): 10,
    }
    assert all(item.case.source_n == 14 for item in selected)
    assert all(item.case.hz0 == 0.0 for item in selected)
    assert all(item.case.connectivity == "ring" for item in selected)
    assert all(
        not (item.case.j2 or item.case.jpm2)
        for item in selected
        if item.family == "nearest_neighbor"
    )
    assert all(
        item.case.j2 or item.case.jpm2
        for item in selected
        if item.family == "second_neighbor"
    )


def test_array_shards_are_two_cases_and_cover_selection_once() -> None:
    config = _config()
    selected = select_cases(config)
    shards = [
        selected[index * 2 : (index + 1) * 2]
        for index in range(config["array_size"])
    ]

    assert all(len(shard) == 2 for shard in shards)
    flattened = [item for shard in shards for item in shard]
    assert flattened == selected
    assert [item.config_id for item in shards[0]] == ["config_111", "config_172"]
    assert [item.config_id for item in shards[-1]] == ["config_068", "config_196"]


def test_known_prior_n17_result_is_physically_and_checksum_valid() -> None:
    selected = select_cases(_config())
    first = selected[0]

    assert first.prior_n17_dir is not None
    assert _prior_result_matches(first.prior_n17_dir, first, target_n=17)


def test_output_paths_encode_family_tail_rank_case_and_n(tmp_path: Path) -> None:
    first = select_cases(_config())[0]

    path = output_dir_for_case(tmp_path, first, detector_n=17)

    assert path == (
        tmp_path
        / "nearest_neighbor"
        / "highest"
        / "rank_01__config_111"
        / "N17"
    )


def test_pbs_array_resources_and_submit_defaults() -> None:
    pbs = (ROOT / "hpc" / "zeus_ranked_ring_extremes_N17_array.pbs").read_text()
    submit = (
        ROOT / "hpc" / "submit_zeus_ranked_ring_extremes_N17.sh"
    ).read_text()

    assert "#PBS -J 0-19" in pbs
    assert "#PBS -q zeus_new_q" in pbs
    assert "ncpus=16:mem=256gb" in pbs
    assert "walltime=120:00:00" in pbs
    assert 'ARRAY_RANGE="${ARRAY_RANGE:-0-19}"' in submit
    assert 'qsub -J "$ARRAY_RANGE"' in submit
    assert "REUSE_EXISTING_N17" in pbs
    assert "effective_campaign_config.json" in submit
