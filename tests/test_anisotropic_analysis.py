"""Tests for anisotropic Zeus post-processing."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from collapse.anisotropic_analysis import (
    DetectorDegeneracyCalculator,
    ParameterRegimeSummarizer,
    SpectrumMetricCalculator,
    SpectrumMetrics,
    fit_periodic_power_law,
    wrapped_heavy_score,
)
from collapse.detector_resonance import DetectorSpec
from collapse.distribution_fit import (
    fit_folded_circular_models,
    folded_wrapped_cauchy_bin_probabilities,
    folded_wrapped_gaussian_bin_probabilities,
)


def _samples(probabilities: np.ndarray, edges: np.ndarray, count: int = 50_000) -> np.ndarray:
    counts = np.floor(probabilities * count).astype(int)
    counts[np.argmax(probabilities)] += count - int(counts.sum())
    return np.repeat(0.5 * (edges[:-1] + edges[1:]), counts)


def test_wrapped_heavy_score_requires_cauchy_preference():
    edges = np.linspace(0.0, np.pi, 49)
    gaussian = _samples(folded_wrapped_gaussian_bin_probabilities(edges, 0.55), edges)
    cauchy = _samples(folded_wrapped_cauchy_bin_probabilities(edges, 0.45), edges)
    gaussian_score = wrapped_heavy_score(fit_folded_circular_models(gaussian, edges))
    cauchy_score = wrapped_heavy_score(fit_folded_circular_models(cauchy, edges))
    assert gaussian_score == 0.0
    assert cauchy_score > 0.95


def test_periodic_power_law_recovers_exponent():
    edges = np.linspace(0.0, np.pi, 49)
    centers = 0.5 * (edges[:-1] + edges[1:])
    target_alpha = 1.6
    probabilities = centers ** (-target_alpha)
    probabilities /= probabilities.sum()
    theta = _samples(probabilities, edges, count=100_000)
    fit = fit_periodic_power_law(theta, edges)
    assert abs(fit.alpha - target_alpha) < 0.03
    assert fit.jensen_shannon_divergence < 1.0e-5
    assert fit.log10_distance_span > 1.5


def test_spectrum_calculator_reconstructs_theta(tmp_path: Path):
    radii = np.geomspace(0.02, 50.0, 4096)
    phase = np.linspace(-np.pi, np.pi, radii.size, endpoint=False)
    eigenvalues = radii * np.exp(1j * phase)
    theta = 2.0 * np.arctan(radii)
    path = tmp_path / "spectrum_t1000000.npz"
    np.savez_compressed(
        path,
        eigenvalues=eigenvalues,
        theta=theta,
        detector_n=11,
        hz=0.1,
        hz0=0.0,
        J=1.0,
        Jpm=0.5,
        Jx=0.01,
        t=1.0e6,
    )
    metrics = SpectrumMetricCalculator(48).calculate(path)
    assert metrics.detector_n == 11
    assert metrics.sample_count == radii.size
    assert metrics.theta_reconstruction_max_error < 1.0e-14
    assert 0.0 <= metrics.S_wrapped_heavy <= 1.0
    assert 0.0 <= metrics.theta_power_law_alpha <= 8.0
    assert 0.0 <= metrics.theta_power_law_js <= np.log(2.0)


def _metric(**updates: float) -> SpectrumMetrics:
    values = dict(
        detector_n=11,
        total_qubits=12,
        hz=0.1,
        J=1.0,
        Jpm=0.5,
        evolution_time=1.0e6,
        Jx=0.01,
        hz0=0.0,
        sample_count=1024,
        theta_reconstruction_max_error=0.0,
        S_born=0.8,
        born_rmse=0.1,
        angular_bin_coverage=0.8,
        phi_harmonic_2=0.2,
        wrapped_gaussian_sigma=1.0,
        wrapped_gaussian_l1=0.2,
        wrapped_gaussian_js=0.1,
        wrapped_cauchy_gamma=1.0,
        wrapped_cauchy_l1=0.1,
        wrapped_cauchy_js=0.02,
        cauchy_log_likelihood_advantage_per_sample=0.01,
        cauchy_log_likelihood_advantage_total=10.24,
        preferred_wrapped_model="wrapped_cauchy",
        S_wrapped_heavy=0.9,
        theta_power_law_alpha=1.5,
        theta_power_law_js=0.02,
        theta_power_law_log_likelihood_per_sample=-2.0,
        theta_power_law_log10_span=1.8,
        radius_q50=1.0,
        radius_q95=10.0,
        radius_q99=100.0,
        radius_q99_over_q50=100.0,
        radius_atomic_fraction=0.01,
        tail_density_exponent=2.0,
        tail_survival_exponent=1.0,
        reciprocity_error=0.1,
        max_radius=1000.0,
        source_npz="synthetic.npz",
    )
    values.update(updates)
    return SpectrumMetrics(**values)


def test_regime_summary_uses_joint_born_gate():
    strong = _metric()
    low_coverage = _metric(J=0.5, angular_bin_coverage=0.2, S_born=0.95)
    summary = ParameterRegimeSummarizer().summarize([strong, low_coverage])
    assert summary["configuration_count"] == 2
    assert summary["born_like_count"] == 1
    assert summary["wrapped_heavy_count"] == 2
    assert summary["joint_count"] == 1


def test_detector_degeneracy_metric_is_bounded_and_normalized():
    metric = DetectorDegeneracyCalculator().calculate(DetectorSpec(4, 0.0, 1.0, 0.0))
    assert 0.0 <= metric.detector_degenerate_state_fraction <= 1.0
    assert 0.0 <= metric.active_zero_gap_weight_fraction <= 1.0
    assert np.isclose(metric.total_active_weight, 4 * 2**4)
