from __future__ import annotations

import math

import numpy as np
import pytest

from collapse.degenerate_activation import ActivationConfig, DegenerateActivationAnalyzer
from collapse.detector_resonance import DenseRingDetectorBuilder, DetectorSpec, SpectralProjectorAnalyzer


def test_exact_weight_matches_projector_invariant_summary() -> None:
    spec = DetectorSpec(detector_n=4, hz=0.0, j=1.0, jpm=0.0)
    metrics = DegenerateActivationAnalyzer().analyze(spec)
    operators = DenseRingDetectorBuilder().build(spec)
    _, _, summary = SpectralProjectorAnalyzer().analyze(operators, hz0=0.0)
    assert math.isclose(
        metrics.exact_active_weight_fraction,
        summary.detector_degenerate_weight_fraction,
        rel_tol=1.0e-11,
        abs_tol=1.0e-12,
    )
    assert math.isclose(metrics.total_coupling_weight, spec.detector_n * 2**spec.detector_n)


def test_activation_curve_is_monotone_and_metrics_are_bounded() -> None:
    metrics = DegenerateActivationAnalyzer().analyze(
        DetectorSpec(detector_n=4, hz=0.01, j=0.5, jpm=0.1)
    )
    curve = np.asarray(
        [
            metrics.weight_fraction_gap_le_1em6,
            metrics.weight_fraction_gap_le_1em5,
            metrics.weight_fraction_gap_le_1em4,
            metrics.weight_fraction_gap_le_1em3,
            metrics.weight_fraction_gap_le_1em2,
            metrics.weight_fraction_gap_le_1em1,
        ]
    )
    assert np.all(np.diff(curve) >= -1.0e-12)
    bounded = [
        metrics.exact_active_weight_fraction,
        metrics.active_degenerate_subspace_fraction,
        metrics.active_degenerate_state_fraction,
        metrics.exact_activation_rank_fraction,
        metrics.exact_spectral_participation_fraction,
        metrics.exact_block_participation_fraction,
        metrics.exact_largest_block_share,
        metrics.finite_time_kernel_power_fraction,
        metrics.finite_time_transition_participation_fraction,
        metrics.finite_time_largest_transition_share,
    ]
    assert all(0.0 <= value <= 1.0 + 1.0e-12 for value in bounded)


def test_invalid_activation_config_is_rejected() -> None:
    with pytest.raises(ValueError):
        ActivationConfig(evolution_time=0.0)
    with pytest.raises(ValueError):
        ActivationConfig(gap_windows=(1.0e-3, 1.0e-4))
