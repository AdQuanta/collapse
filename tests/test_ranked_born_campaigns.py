"""Contracts for ranked-case selection and checkpointed Zeus follow-ups."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from core.ranked_born_campaign import (
    RankedHamiltonianCase,
    hz0_variants,
    load_ranked_cases,
    simulate_ranked_case,
)
from core.detector_graphs import DetectorGraphSpec


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_sobol_inventory_ranks_complete_cases_and_skips_incomplete(tmp_path) -> None:
    root = tmp_path / "sobol"
    for index, score in enumerate((0.4, 0.8, 0.6)):
        case = root / "jy_zero" / "N12" / f"config_{index:03d}"
        _json(case / "metrics.json", {"S_born": score})
        _json(
            case / "metadata.json",
            {
                "N": 12,
                "hz0": 0.0,
                "evolution_time": 1.0e6,
                "configuration": {
                    "hz": 0.2,
                    "j": 1.0,
                    "jpm": 0.3,
                    "jx": 0.01,
                    "jy": 0.0,
                    "j2": 0.0,
                    "jpm2": 0.0,
                },
            },
        )
        if index != 1:
            _json(case / "COMPLETE.json", {"status": "complete"})
    ranked = load_ranked_cases(root)
    assert [case.source_s_born for case in ranked] == [0.6, 0.4]
    assert all(case.connectivity == "ring" for case in ranked)


def test_atlas_inventory_reads_case_metadata_and_ranks(tmp_path) -> None:
    root = tmp_path / "atlas"
    for index, score in enumerate((0.1, 0.9)):
        relative = Path("N14") / f"hz_{index}" / "J_1" / "Jpm_0"
        _json(
            root / "metrics" / relative / "diagnostics.json",
            {"S_born": score},
        )
        _json(
            root / "raw" / relative / "metadata.json",
            {
                "case": {
                    "detector_n": 14,
                    "evolution_time": 1.0e6,
                    "hz": float(index),
                    "hz0": 0.0,
                    "j": 1.0,
                    "jpm": 0.0,
                    "jx": 0.001,
                    "seed": 44,
                }
            },
        )
        spectrum = root / "raw" / relative / "spectrum_t1000000.npz"
        spectrum.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(spectrum, eigenvalues=np.ones(2))
    ranked = load_ranked_cases(root)
    assert [case.source_s_born for case in ranked] == [0.9, 0.1]
    assert ranked[0].hz == 1.0
    assert ranked[0].jx == 0.001


def test_hz0_variants_include_zero_matched_offsets_and_collapse_duplicates() -> None:
    variants = hz0_variants(0.0, (-1e-3, -1e-4, 0.0, 1e-4, 1e-3))
    values = [value for _, value, _ in variants]
    assert values == [0.0, -1e-3, -1e-4, 1e-4, 1e-3]
    assert variants[0][2] == ("zero", "matched")


def test_small_ranked_case_simulation_is_checkpointed_and_resumable(tmp_path) -> None:
    case = RankedHamiltonianCase(
        source_root="fixture",
        source_case="case",
        source_metric_file="metrics.json",
        source_s_born=0.75,
        source_n=3,
        hz=0.2,
        hz0=0.0,
        j=0.7,
        jpm=0.1,
        jx=0.01,
    )
    case_dir = tmp_path / "case"
    outcome = simulate_ranked_case(
        case,
        detector_n=3,
        hz0=0.0,
        case_dir=case_dir,
        source_index=0,
        rank_index=0,
        bins=16,
        plot_grid=128,
        fit_harmonics=4,
        max_bloch_points=100,
    )
    assert outcome["status"] == "success"
    assert (case_dir / "COMPLETE.json").is_file()
    metadata = json.loads((case_dir / "metadata.json").read_text())
    assert metadata["Jx_effective"] == case.jx / np.sqrt(3)
    resumed = simulate_ranked_case(
        case,
        detector_n=3,
        hz0=0.0,
        case_dir=case_dir,
        source_index=0,
        rank_index=0,
    )
    assert resumed["status"] == "resumed"


def test_small_ranked_case_summary_storage_omits_full_root_arrays(tmp_path) -> None:
    case = RankedHamiltonianCase(
        source_root="fixture",
        source_case="case",
        source_metric_file="metrics.json",
        source_s_born=0.25,
        source_n=3,
        hz=0.2,
        hz0=0.0,
        j=0.7,
        jpm=0.1,
        jx=0.01,
    )
    case_dir = tmp_path / "summary"
    outcome = simulate_ranked_case(
        case,
        detector_n=3,
        hz0=0.0,
        case_dir=case_dir,
        source_index=0,
        rank_index=0,
        bins=16,
        plot_grid=128,
        fit_harmonics=4,
        max_bloch_points=3,
        storage_mode="summary",
    )
    assert outcome["status"] == "success"
    assert not (case_dir / "results.npz").exists()
    with np.load(case_dir / "results_summary.npz") as archive:
        assert not {"eigenvalues", "theta", "phi", "bloch_blue", "bloch_red"} & set(
            archive.files
        )
        assert int(np.sum(archive["theta_counts"])) == 2**3
        assert int(np.sum(archive["theta_reflected_counts"])) == 2**3
        assert archive["bloch_blue_sample"].shape == (3, 3)
        assert archive["bloch_red_sample"].shape == (3, 3)
    metadata = json.loads((case_dir / "metadata.json").read_text())
    assert metadata["storage"]["mode"] == "summary"
    assert metadata["storage"]["results_file"] == "results_summary.npz"
    marker = json.loads((case_dir / "COMPLETE.json").read_text())
    assert marker["storage_mode"] == "summary"
    assert "results_summary.npz" in marker["files"]


def test_small_ranked_case_records_graph_override_provenance(tmp_path) -> None:
    case = RankedHamiltonianCase(
        source_root="fixture",
        source_case="case",
        source_metric_file="metrics.json",
        source_s_born=0.25,
        source_n=4,
        hz=0.2,
        hz0=0.0,
        j=0.7,
        jpm=0.1,
        jx=0.01,
        connectivity="erdos_renyi",
    )
    graph_spec = DetectorGraphSpec(
        kind="erdos_renyi",
        seed=9182,
        erdos_renyi_p=1.0,
    )
    case_dir = tmp_path / "override"
    simulate_ranked_case(
        case,
        detector_n=3,
        hz0=0.0,
        case_dir=case_dir,
        source_index=0,
        rank_index=0,
        bins=16,
        plot_grid=128,
        fit_harmonics=4,
        max_bloch_points=100,
        graph_spec_override=graph_spec,
        graph_provenance={"mode": "test_override"},
    )

    metadata = json.loads((case_dir / "metadata.json").read_text())
    assert metadata["detector_graph"]["spec"]["seed"] == 9182
    assert metadata["graph_provenance"] == {"mode": "test_override"}


def test_zeus_configs_and_arrays_match_requested_campaign_sizes() -> None:
    larger = json.loads(
        (ROOT / "configs/zeus_top20_last5_largerN.json").read_text()
    )
    hz0 = json.loads(
        (ROOT / "configs/zeus_top400_hz0_variants_N14.json").read_text()
    )
    assert len(larger["source_roots"]) == 5
    assert larger["top_per_source"] == 20
    assert larger["cases_per_array_task"] == 5
    assert larger["target_detector_sizes"] == [14, 15, 16, 17]
    assert hz0["top_count"] == 400
    assert hz0["target_detector_n"] == 14
    assert 0.0 in hz0["hz0_additive_offsets"]
    assert hz0["include_hz0_zero"] is True
    larger_pbs = (ROOT / "hpc/zeus_top20_last5_largerN_array.pbs").read_text()
    hz0_pbs = (ROOT / "hpc/zeus_top400_hz0_variants_N14_array.pbs").read_text()
    assert "#PBS -J 0-19" in larger_pbs
    assert "mem=256gb" in larger_pbs
    assert hz0["shard_size"] == 100
    assert "#PBS -J 0-3" in hz0_pbs
    assert "mem=128gb" in hz0_pbs

    resampled = json.loads(
        (ROOT / "configs/zeus_network_extremes_resampled_N12.json").read_text()
    )
    larger_networks = json.loads(
        (ROOT / "configs/zeus_network_extremes_largerN.json").read_text()
    )
    wd_nonborn_networks = json.loads(
        (ROOT / "configs/zeus_network_wd_nonborn_largerN.json").read_text()
    )
    assert len(resampled["families"]) == 4
    assert resampled["count_per_tail"] == 10
    assert resampled["realizations_per_case"] == 5
    assert resampled["target_detector_n"] == 12
    assert 4 * 20 * 5 == 400
    assert larger_networks["count_per_tail"] == 10
    assert larger_networks["target_detector_sizes"] == [13, 14, 15]
    assert 4 * 20 * 3 == 240
    resampled_pbs = (
        ROOT / "hpc/zeus_network_extremes_resampled_N12_array.pbs"
    ).read_text()
    larger_pbs = (
        ROOT / "hpc/zeus_network_extremes_largerN_array.pbs"
    ).read_text()
    assert "#PBS -J 0-19" in resampled_pbs
    assert "#PBS -q zeus_new_q" in resampled_pbs
    assert larger_networks["cases_per_array_task"] == 8
    assert "#PBS -J 0-9" in larger_pbs
    assert "mem=256gb" in larger_pbs
    assert len(wd_nonborn_networks["cases"]) == 4
    assert wd_nonborn_networks["target_detector_sizes"] == [13, 14, 15]
    assert wd_nonborn_networks["storage_mode"] == "summary"
    assert wd_nonborn_networks["level_spacing_sector_count"] == 4
    wd_nonborn_pbs = (
        ROOT / "hpc/zeus_network_wd_nonborn_largerN_array.pbs"
    ).read_text()
    assert "#PBS -J 0-11" in wd_nonborn_pbs
    assert "mem=256gb" in wd_nonborn_pbs
