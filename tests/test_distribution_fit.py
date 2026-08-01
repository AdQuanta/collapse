"""Tests for folded wrapped-distribution fit diagnostics."""

from __future__ import annotations

import numpy as np

from collapse.distribution_fit import (
    fit_folded_circular_models,
    folded_wrapped_cauchy_bin_probabilities,
    folded_wrapped_gaussian_bin_probabilities,
)


def _deterministic_samples(probabilities: np.ndarray, edges: np.ndarray, n: int = 200_000) -> np.ndarray:
    counts = np.floor(probabilities * n).astype(int)
    counts[np.argmax(probabilities)] += n - int(np.sum(counts))
    centers = 0.5 * (edges[:-1] + edges[1:])
    return np.repeat(centers, counts)


def test_folded_model_bin_probabilities_are_normalized():
    edges = np.linspace(0.0, np.pi, 49)
    gaussian = folded_wrapped_gaussian_bin_probabilities(edges, sigma=0.7)
    cauchy = folded_wrapped_cauchy_bin_probabilities(edges, gamma=0.7)
    assert np.isclose(np.sum(gaussian), 1.0)
    assert np.isclose(np.sum(cauchy), 1.0)
    assert np.all(gaussian >= 0.0)
    assert np.all(cauchy >= 0.0)


def test_fit_prefers_wrapped_gaussian_for_wrapped_gaussian_data():
    edges = np.linspace(0.0, np.pi, 49)
    expected = folded_wrapped_gaussian_bin_probabilities(edges, sigma=0.55)
    fit = fit_folded_circular_models(_deterministic_samples(expected, edges), edges)
    assert fit.preferred_model == "wrapped_gaussian"
    assert abs(fit.wrapped_gaussian_sigma - 0.55) < 0.02
    assert fit.wrapped_gaussian_js < fit.wrapped_cauchy_js
    assert fit.cauchy_log_likelihood_advantage_per_sample < 0.0


def test_fit_prefers_wrapped_cauchy_for_wrapped_cauchy_data():
    edges = np.linspace(0.0, np.pi, 49)
    expected = folded_wrapped_cauchy_bin_probabilities(edges, gamma=0.45)
    fit = fit_folded_circular_models(_deterministic_samples(expected, edges), edges)
    assert fit.preferred_model == "wrapped_cauchy"
    assert abs(fit.wrapped_cauchy_gamma - 0.45) < 0.02
    assert fit.wrapped_cauchy_js < fit.wrapped_gaussian_js
    assert fit.cauchy_log_likelihood_advantage_per_sample > 0.0
