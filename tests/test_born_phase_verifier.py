"""Solvable controls for the frozen verifier; no fitted candidate thresholds."""
import numpy as np
import pytest
from scipy.optimize import brentq

from core.born_phase_verifier import evaluate_angles, evaluate_spectrum, summarize_conditions
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum


def test_exact_born_density_control_and_haar_negative():
    # Deterministic quantiles of P=(1+cos(theta))/pi, independently inverted.
    probabilities = (np.arange(32768)+.5)/32768
    born = np.array([brentq(lambda t: (t+np.sin(t))/np.pi-p, 0, np.pi)
                     for p in probabilities])
    result = evaluate_angles(born, expected_count=len(born))
    assert result["structural_gate"]
    assert result["balance_binned_relative"] < .004
    assert result["moment_max"] < .002
    assert result["qz_validity"] is None
    haar = evaluate_angles(np.arccos(1-2*probabilities), expected_count=len(probabilities))
    assert not haar["structural_gate"]
    assert haar["coverage"] == 1
    assert haar["balance_binned_relative"] > .49


def test_north_pole_vacuous_moments_do_not_pass():
    result = evaluate_angles(np.zeros(32), expected_count=32)
    assert result["moment_max"] == 0
    assert result["balance_binned_l1"] == 0
    assert result["balance_binned_relative"] is None
    assert result["global_ratio_rmse"] is None
    assert not result["structural_gate"]


def test_discrete_detailed_balance_uses_root_weights_before_binning():
    # At theta=pi/3 and 2pi/3, tilted masses are 3*(1/4) and 1*(3/4).
    result = evaluate_angles(np.array([np.pi/3]*3 + [2*np.pi/3]), expected_count=4)
    assert result["balance_binned_l1"] < 1e-15
    assert result["moment_max"] < 2e-14
    assert not result["structural_gate"]  # support remains just two angles


def test_production_qz_retains_poles_and_singular_failure():
    s = generalized_relative_evolution_spectrum(np.diag([1., 0., 1.]), np.diag([0., 1., 2.]))
    result = evaluate_spectrum(s, expected_count=3)
    assert result["qz_validity"]
    assert result["qz_zero_fraction"] == pytest.approx(1/3)
    assert result["qz_infinite_fraction"] == pytest.approx(1/3)
    assert not result["numerical_and_structural_gate"]
    singular = generalized_relative_evolution_spectrum(np.zeros((2, 2)), np.zeros((2, 2)))
    invalid = evaluate_spectrum(singular, expected_count=2)
    assert invalid["qz_indeterminate_fraction"] == 1
    assert invalid["qz_validity"] is False
    assert invalid["profile"] is None


def test_missing_left_diagnostics_and_count_are_not_success():
    s = generalized_relative_evolution_spectrum(np.eye(2), np.diag([.2, .7]),
                                               compute_left_eigenvectors=False)
    assert evaluate_spectrum(s, expected_count=2)["qz_validity"] is None
    assert evaluate_spectrum(s, expected_count=3)["qz_validity"] is False


@pytest.mark.parametrize("angles,count", [([.1], 2), ([np.nan], 1), ([-.1], 1), ([4.], 1)])
def test_invalid_angles_never_disappear(angles, count):
    with pytest.raises(ValueError):
        evaluate_angles(np.array(angles), expected_count=count)


def test_group_summary_preserves_failures_and_heldout_separation():
    diag = evaluate_angles(np.array([.1, 2.]), expected_count=2)
    base = dict(candidate="test", N=1, time=1., perturbation="baseline", split="discovery", diagnostics=diag)
    rows = [base, dict(base, N=2, diagnostics=None), dict(base, split="heldout")]
    groups = summarize_conditions(rows)["groups"]
    assert len(groups) == 2
    assert groups[0]["failed_conditions"] == 1
    assert groups[0]["worst_moment_max"] is None
    assert not groups[0]["all_structural_gate"]
    assert not groups[0]["all_qz_verified"]
    assert groups[1]["failed_conditions"] == 0
    with pytest.raises(ValueError):
        summarize_conditions([base, base])
