"""Contracts for the saved-network Jx/10 finite-size campaign."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from core.detector_graphs import DetectorGraphSpec, detector_graph_edges
from core.network_resampled_scaling_campaign import (
    graph_spec_and_provenance,
    load_resampled_network_cases,
)
from core.ranked_born_time_average import (
    _time_average_complete_valid,
    average_time_diagnostics,
    simulate_ranked_case_time_average,
    validate_evolution_times,
)
from core.ranked_born_campaign import RankedHamiltonianCase


ROOT = Path(__file__).resolve().parents[1]


def _write_source_sample(root: Path, *, saved_edges_match: bool = True) -> None:
    case_dir = (
        root
        / "family_00_erdos_renyi"
        / "highest_01"
        / "realization_01"
        / "N12"
    )
    case_dir.mkdir(parents=True)
    spec = DetectorGraphSpec(kind="erdos_renyi", seed=12345, erdos_renyi_p=0.3)
    edges = detector_graph_edges(12, spec)
    if not saved_edges_match:
        edges = edges[1:]
    metadata = {
        "target_N": 12,
        "hz0": 0.0,
        "central_coupling": "all",
        "source": {
            "hz": 0.2,
            "j": 0.7,
            "jpm": 0.4,
            "jx": 0.03,
            "jy": 0.0,
            "j2": 0.0,
            "jpm2": 0.0,
            "evolution_time": 1.0e6,
            "model_seed": 44,
        },
        "detector_graph": {
            "nodes": 12,
            "canonical_kind": "erdos_renyi",
            "spec": {
                "kind": spec.kind,
                "seed": spec.seed,
                "erdos_renyi_p": spec.erdos_renyi_p,
                "watts_strogatz_k": spec.watts_strogatz_k,
                "watts_strogatz_p": spec.watts_strogatz_p,
                "barabasi_albert_m": spec.barabasi_albert_m,
                "regular_degree": spec.regular_degree,
                "require_connected": spec.require_connected,
                "max_attempts": spec.max_attempts,
            },
            "edges_zero_based": [list(edge) for edge in edges],
        },
        "graph_provenance": {"mode": "test_saved_resample"},
    }
    (case_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (case_dir / "metrics.json").write_text(
        json.dumps({"S_born": 0.75}), encoding="utf-8"
    )
    (case_dir / "validation.json").write_text(
        json.dumps({"passed": True}), encoding="utf-8"
    )
    (case_dir / "COMPLETE.json").write_text(
        json.dumps({"status": "complete"}), encoding="utf-8"
    )


def test_loader_reduces_collective_jx_once_and_preserves_sample_seed(
    tmp_path: Path,
) -> None:
    _write_source_sample(tmp_path)
    items = load_resampled_network_cases(
        tmp_path, jx_scale_factor=0.1, expected_count=1
    )
    assert len(items) == 1
    item = items[0]
    assert math.isclose(item.original_collective_jx, 0.03)
    assert math.isclose(item.case.jx, 0.003)
    assert item.case.graph_spec["seed"] == 12345

    _, n12 = graph_spec_and_provenance(item, 12, jx_scale_factor=0.1)
    _, n15 = graph_spec_and_provenance(item, 15, jx_scale_factor=0.1)
    assert n12["is_same_edge_set_as_source"] is True
    assert n15["is_same_edge_set_as_source"] is False
    assert n15["realization_seed"] == 12345
    assert math.isclose(item.case.jx / math.sqrt(15), 0.003 / math.sqrt(15))


def test_loader_rejects_unreconstructable_saved_graph(tmp_path: Path) -> None:
    _write_source_sample(tmp_path, saved_edges_match=False)
    with pytest.raises(ValueError, match="not reproduced"):
        load_resampled_network_cases(
            tmp_path, jx_scale_factor=0.1, expected_count=1
        )


def test_time_average_forms_r_only_after_averaging_p() -> None:
    eigenvalues_by_time = (
        np.asarray([0.05, 0.2, 0.8, 1.7], dtype=np.complex128),
        np.asarray([0.1j, 0.5j, 1.2j, 4.0j], dtype=np.complex128),
    )
    metrics, arrays, _, time_arrays = average_time_diagnostics(
        eigenvalues_by_time,
        bins=8,
    )
    expected_p = np.mean(time_arrays["p_theta_by_time"], axis=0)
    expected_reflected = np.mean(
        time_arrays["p_pi_minus_theta_by_time"], axis=0
    )
    denominator = expected_p + expected_reflected
    expected_r = np.divide(
        expected_p,
        denominator,
        out=np.full(expected_p.shape, np.nan),
        where=denominator > 0.0,
    )
    occupied = denominator > 0.0
    np.testing.assert_allclose(arrays["p_theta"], expected_p)
    np.testing.assert_allclose(arrays["p_pi_minus_theta"], expected_reflected)
    np.testing.assert_allclose(arrays["R"][occupied], expected_r[occupied])
    assert metrics["R_from_time_averaged_P"] is True
    assert metrics["time_count"] == 2
    assert math.isclose(metrics["p_theta_integral"], 1.0)


def test_evolution_time_grid_validation() -> None:
    expected = tuple(float(index) * 1.0e6 for index in range(1, 11))
    assert validate_evolution_times(expected) == expected
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_evolution_times((1.0e6, 1.0e6))


def test_small_time_average_simulation_reuses_one_diagonalization(
    tmp_path: Path,
) -> None:
    graph_spec = DetectorGraphSpec(
        kind="erdos_renyi",
        seed=9182,
        erdos_renyi_p=0.8,
    )
    case = RankedHamiltonianCase(
        source_root="synthetic",
        source_case="config_000/realization_01",
        source_metric_file="metrics.json",
        source_s_born=0.5,
        source_n=3,
        hz=0.2,
        hz0=0.0,
        j=0.7,
        jpm=0.4,
        jx=0.003,
        connectivity="erdos_renyi",
        graph_spec={
            "kind": graph_spec.kind,
            "seed": graph_spec.seed,
            "erdos_renyi_p": graph_spec.erdos_renyi_p,
            "watts_strogatz_k": graph_spec.watts_strogatz_k,
            "watts_strogatz_p": graph_spec.watts_strogatz_p,
            "barabasi_albert_m": graph_spec.barabasi_albert_m,
            "regular_degree": graph_spec.regular_degree,
            "require_connected": graph_spec.require_connected,
            "max_attempts": graph_spec.max_attempts,
        },
    )
    case_dir = tmp_path / "case"
    outcome = simulate_ranked_case_time_average(
        case,
        detector_n=3,
        hz0=0.0,
        evolution_times=(1.0, 2.0),
        case_dir=case_dir,
        source_index=0,
        rank_index=0,
        bins=16,
        plot_grid=64,
        fit_harmonics=4,
        max_bloch_points=100,
        resume=False,
        graph_spec_override=graph_spec,
    )
    assert outcome["status"] == "success"
    metadata = json.loads((case_dir / "metadata.json").read_text())
    validation = json.loads((case_dir / "validation.json").read_text())
    assert metadata["diagonalization_reused_for_all_times"] is True
    assert metadata["evolution_times"] == [1.0, 2.0]
    assert validation["passed"] is True
    assert _time_average_complete_valid(case_dir, (1.0, 2.0)) is True
    assert _time_average_complete_valid(case_dir, (1.0, 3.0)) is False
    with np.load(case_dir / "time_resolved_diagnostics.npz") as data:
        assert data["p_theta_by_time"].shape == (2, 16)


def test_zeus_campaign_shape_resources_and_queue() -> None:
    config = json.loads(
        (ROOT / "configs/zeus_network_resampled_jx_div10_N12_15.json").read_text()
    )
    assert config["expected_sample_count"] == 400
    assert config["samples_per_array_task"] == 20
    assert config["target_detector_sizes"] == [12, 13, 14, 15]
    assert config["target_time_averaged_sample_count"] == 2**15
    assert config["evolution_time_step"] == 1.0e6
    time_counts = {
        detector_n: config["target_time_averaged_sample_count"] // (2**detector_n)
        for detector_n in config["target_detector_sizes"]
    }
    assert time_counts == {12: 8, 13: 4, 14: 2, 15: 1}
    assert all(
        time_counts[detector_n] * 2**detector_n == 2**15
        for detector_n in time_counts
    )
    assert config["jx_scale_factor"] == 0.1
    assert 400 * 4 == 1600
    assert 400 * sum(time_counts.values()) == 6000

    pbs = (
        ROOT / "hpc/zeus_network_resampled_jx_div10_N12_15_array.pbs"
    ).read_text()
    submit = (
        ROOT / "hpc/submit_zeus_network_resampled_jx_div10_N12_15.sh"
    ).read_text()
    assert "#PBS -J 0-19" in pbs
    assert "#PBS -q zeus_new_q" in pbs
    assert "mem=256gb" in pbs
    assert "walltime=120:00:00" in pbs
    assert "time_counts=8,4,2,1" in pbs
    assert "N<N>_COMPLETE.json" not in pbs
    assert "ARRAY_RANGE=\"${ARRAY_RANGE:-0-19}\"" in submit
    assert 'qsub -J "$ARRAY_RANGE"' in submit
    assert "SOURCE_ROOT=$SOURCE_ROOT" in submit
