from __future__ import annotations

import math

import numpy as np

from examples.analyze_network_sobol_born_relations import (
    graph_features,
    level_features,
)


def test_graph_features_for_four_cycle() -> None:
    metadata = {
        "nodes": 4,
        "edges_zero_based": [[0, 1], [1, 2], [2, 3], [3, 0]],
        "laplacian_algebraic_connectivity": 2.0,
    }
    result = graph_features(metadata)
    assert math.isclose(result["edge_density"], 2.0 / 3.0)
    assert math.isclose(result["degree_cv"], 0.0)
    assert math.isclose(result["mean_clustering"], 0.0)
    assert math.isclose(result["mean_path_length"], 4.0 / 3.0)
    assert result["diameter"] == 2.0
    assert math.isclose(result["normalized_laplacian_gap"], 1.0)


def test_level_features_exclude_half_filling() -> None:
    data = {
        "sector_1": {
            "hamming_weight": 6,
            "dimension": 924,
            "spacing_count": 1000,
            "mean_ratio": 0.1,
            "l1_distances": {"GOE": 0.9, "Poisson": 0.1},
        },
        "sector_2": {
            "hamming_weight": 5,
            "dimension": 792,
            "spacing_count": 3,
            "mean_ratio": 0.5,
            "l1_distances": {"GOE": 0.2, "Poisson": 0.5},
        },
        "sector_3": {
            "hamming_weight": 4,
            "dimension": 495,
            "spacing_count": 1,
            "mean_ratio": 0.4,
            "l1_distances": {"GOE": 0.4, "Poisson": 0.3},
        },
    }
    result = level_features(data, n_nodes=12)
    assert math.isclose(result["level_r_mean"], 0.475)
    assert math.isclose(result["level_l1_goe"], 0.25)
    assert math.isclose(result["level_l1_poisson"], 0.45)
    assert math.isclose(result["level_goe_advantage"], 0.2)
    assert math.isclose(result["largest_nonhalf_r"], 0.5)
    assert np.isfinite(result["level_r_std"])
