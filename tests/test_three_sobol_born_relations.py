from __future__ import annotations

import math

import numpy as np

from examples.analyze_three_sobol_born_relations import (
    _benjamini_hochberg,
    _histogram_cdf_at,
    _weighted_histogram_features,
    cross_validated_ridge,
)


def test_log_histogram_cdf_interpolates_partial_bin() -> None:
    edges = np.asarray([0.1, 1.0, 10.0])
    weights = np.asarray([0.4, 0.6])

    assert math.isclose(_histogram_cdf_at(edges, weights, 1.0), 0.4)
    assert math.isclose(_histogram_cdf_at(edges, weights, math.sqrt(10.0)), 0.7)


def test_weighted_histogram_features_preserve_special_weight() -> None:
    features = _weighted_histogram_features(
        np.asarray([0.01, 0.1, 1.0, 10.0]),
        np.asarray([0.2, 0.3, 0.4]),
        special_weight=0.1,
    )

    assert math.isclose(features["vab_weight_delta_lt_0p1"], 0.3)
    assert math.isclose(features["vab_weight_delta_lt_1"], 0.6)
    assert math.isclose(features["vab_weight_delta_lt_10"], 1.0)
    assert 0.0 <= features["vab_hist_entropy"] <= 1.0


def test_benjamini_hochberg_is_bounded_and_rank_monotone() -> None:
    p_values = np.asarray([0.04, 0.001, 0.2, 0.02])
    q_values = _benjamini_hochberg(p_values)
    order = np.argsort(p_values)

    assert np.all((0.0 <= q_values) & (q_values <= 1.0))
    assert np.all(np.diff(q_values[order]) >= 0.0)


def test_nested_ridge_predicts_a_deterministic_linear_relation() -> None:
    rows = []
    for index, x in enumerate(np.linspace(-2.0, 2.0, 120)):
        rows.append(
            {
                "campaign": "synthetic",
                "config_id": f"config_{index:03d}",
                "S_born": 0.25 + 0.3 * x,
                "x": x,
            }
        )

    metrics, predictions = cross_validated_ridge(rows, ["x"])

    assert predictions.shape == (120,)
    assert metrics["r2"] > 0.99
    assert metrics["rmse"] < 0.02
