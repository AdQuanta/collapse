"""Exact-sector and statistical contracts for Zeus spectral post-processing."""

import importlib.util
import json
from pathlib import Path

import numpy as np


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "analyze_zeus_spectral_relations.py"
)
SPEC = importlib.util.spec_from_file_location("zeus_spectral_relations", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_ring_detector_spectral_features_use_resolved_sectors() -> None:
    parameters = {
        "detector_n": 8,
        "time": 10.0,
        "J": 1.0,
        "Jpm": 0.25,
        "Jx": 0.03,
        "hz": 0.1,
        "hz0": 0.1,
        "connectivity": "ring",
        "backend": "numpy_dense",
        "n_phi": 8,
        "n_mu": 4,
        "l_max": 3,
    }
    row = {
        "point_id": "1",
        "campaign": "cross_architecture_ring_control",
        "parameters": json.dumps(parameters),
        "coverage": "1",
        "density_ratio_cross_residual": "0.2",
        "higher_harmonic_leakage": "0.1",
        "dipole_sharpness": "1.0",
        "axis_fidelity": "1.0",
        "epsilon_B": "0.1",
        "polar_S_born": "0.5",
        "case_dir": "unused",
    }

    result = MODULE.detector_spectral_features(row)

    dimensions = json.loads(result["sector_dimensions"])
    assert len(dimensions) == 4
    assert all(dimension >= 2 for dimension in dimensions)
    assert 0.0 <= result["detector_mean_adjacent_gap_ratio"] <= 1.0
    assert result["detector_bandwidth"] > 0.0
    assert result["graph_automorphism_group_order"] == 16


def test_noninteracting_star_reports_undefined_spacing_without_enumerating_sn() -> None:
    parameters = {
        "detector_n": 8,
        "time": 10.0,
        "J": 0.0,
        "Jpm": 0.0,
        "Jx": 0.03,
        "hz": 0.1,
        "hz0": 0.1,
        "connectivity": "all_to_all",
        "backend": "numpy_dense",
        "n_phi": 8,
        "n_mu": 4,
        "l_max": 3,
    }
    row = {
        "point_id": "2",
        "campaign": "cross_physical_architectures",
        "scan_value": "noninteracting_star",
        "parameters": json.dumps(parameters),
        "coverage": "1",
        "density_ratio_cross_residual": "0.2",
        "higher_harmonic_leakage": "0.1",
        "dipole_sharpness": "1.0",
        "axis_fidelity": "1.0",
        "epsilon_B": "0.1",
        "polar_S_born": "0.5",
        "case_dir": "unused",
    }

    result = MODULE.detector_spectral_features(row)

    assert np.isnan(result["detector_mean_adjacent_gap_ratio"])
    assert np.isnan(result["median_resolved_sector_spacing"])
    assert result["graph_edge_count"] == 0
    assert result["graph_automorphism_group_order"] == 40320


def test_disorder_statistics_records_seed_count() -> None:
    rows = [
        {
            "architecture": "erdos_renyi",
            "N": 8,
            **{feature: 0.1 + 0.01 * index for feature in MODULE.SPECTRAL_FEATURES},
            **{outcome: 0.2 + 0.01 * index for outcome in MODULE.ROOT_OUTCOMES},
        }
        for index in range(5)
    ]

    statistics = MODULE.disorder_statistics(rows, bootstrap_samples=100)

    assert statistics
    assert all(row["independent_graph_realizations"] == 5 for row in statistics)
    assert all(row["uncertainty_status"] == "five-seed exploratory ensemble" for row in statistics)
