"""Scientific checks for activation-resolved projective diagnostics."""

from __future__ import annotations

import numpy as np

from collapse.activation_resolved_projective import (
    RingActivationParameters,
    activation_quantile_partition,
    all_detector_activation_channels,
    central_flip_activation_kernel,
    finite_time_transition_kernel,
    momentum_projective_components,
    pooled_component_diagnostics,
    validate_component_reconstruction,
)


def test_finite_time_kernel_is_even_and_has_exact_resonant_limit() -> None:
    detuning = np.array([-0.3, -1.0e-14, 0.0, 1.0e-14, 0.3])
    kernel = finite_time_transition_kernel(detuning, time=7.0)
    np.testing.assert_allclose(kernel, kernel[::-1], rtol=0.0, atol=1.0e-13)
    np.testing.assert_allclose(kernel[1:4], 49.0, rtol=0.0, atol=1.0e-12)
    shifted = central_flip_activation_kernel(np.array([-0.4, 0.4]), 0.1, 7.0)
    np.testing.assert_allclose(shifted[0], shifted[1], rtol=0.0, atol=1.0e-13)


def test_small_ring_components_are_positive_complete_and_reconstruct_global() -> None:
    detector_n = 3
    parameters = RingActivationParameters(
        hz=0.17,
        hz0=0.03,
        j=0.29,
        jpm=0.11,
        jx_unscaled=0.021,
        evolution_time=13.0,
    )
    activation = all_detector_activation_channels(detector_n, parameters)
    assert sum(item.scores.size for item in activation) == 2**detector_n
    assert min(float(np.min(item.scores)) for item in activation) >= 0.0
    partition = activation_quantile_partition(
        activation,
        lower_quantile=0.25,
        upper_quantile=0.75,
    )
    components = tuple(
        momentum_projective_components(
            detector_n,
            momentum,
            partition,
            parameters,
        )
        for momentum in activation
    )
    assert sum(item.theta.size for item in components) == 2**detector_n
    assert max(item.maximum_weight_sum_error for item in components) < 1.0e-11
    assert max(item.detector_basis_completeness_error for item in components) < 1.0e-11
    assert max(item.maximum_eigenpair_residual for item in components) < 1.0e-11

    diagnostics = pooled_component_diagnostics(components, partition, bins=16)
    reconstruction = validate_component_reconstruction(diagnostics)
    assert max(reconstruction.values()) < 1.0e-11
    assert all(abs(np.sum(item.p_theta * np.diff(item.edges)) - 1.0) < 1.0e-12 for item in diagnostics)
