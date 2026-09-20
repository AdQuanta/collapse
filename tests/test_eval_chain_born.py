"""Contract tests for the frozen endpoint-chain Born campaign evaluator.

These tests exist to make the campaign's frozen decisions hard to change by
accident. ``SPEC.md`` §23 hard-FAIL 9 forbids the research agent from altering a
verifier mid-campaign, and the project's standing rule forbids retuning
thresholds after seeing results; a test that pins the constant turns either
mistake into a visible failure rather than a quiet drift in the numbers.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest

from scripts.eval_chain_born import (
    COUPLING_NAMES,
    FIXED_ZERO,
    MIN_COVERAGE_BINS,
    N_LADDER,
    PARAMETER_NAMES,
    PERTURBATIVE_RATIO,
    DIAGNOSTIC_BIN_COUNTS,
    PERTURBATIVE_TOLERANCE,
    PROFILE_BINS,
    ROOT_BUDGET,
    S_BORN_BINS,
    TIMES,
    ChainConfig,
    _thinned_score,
    born_profile,
    coupling_scale,
    detector_scale,
    evaluate_config,
    normalize,
    perturbative_ratio,
)


def _candidate(**overrides) -> ChainConfig:
    base = dict(
        name="test",
        hypothesis="fixture",
        rung="test",
        Jzz=1.0,
        hx=1.0,
        hz=1.5,
        h0x=1.0,
        h0z=2.0,
        gz=0.1,
    )
    base.update(overrides)
    return ChainConfig(**base)


# --- frozen contract -------------------------------------------------------


def test_frozen_constants_have_their_declared_values():
    """Pin the campaign contract so a silent retune fails loudly."""

    assert N_LADDER == (8, 9, 10)
    assert S_BORN_BINS == 100
    assert PROFILE_BINS == 64
    assert PERTURBATIVE_RATIO == 0.1
    assert PERTURBATIVE_TOLERANCE == 1.0e-9
    assert MIN_COVERAGE_BINS == 20
    assert len(TIMES) == 6
    assert TIMES[0] == pytest.approx(100.0)
    assert TIMES[-1] == pytest.approx(1000.0)
    assert ROOT_BUDGET == len(TIMES) * 2 ** min(N_LADDER)


def test_diagnostic_bins_never_include_the_frozen_metric_bins():
    """The sweep must probe bin counts other than the scoring one.

    Including 100 would make the spread understate estimator dependence by
    comparing the metric against itself.
    """

    assert S_BORN_BINS not in DIAGNOSTIC_BIN_COUNTS
    assert len(set(DIAGNOSTIC_BIN_COUNTS)) == len(DIAGNOSTIC_BIN_COUNTS)


def test_estimator_sweep_is_reported_per_size():
    record = evaluate_config(_candidate(), n_values=(4,))
    block = record["by_size"]["4"]
    assert set(block["S_born_by_bins"]) == {str(b) for b in DIAGNOSTIC_BIN_COUNTS}
    assert block["S_born_bin_spread"] >= 0.0


def test_parameter_set_is_the_twelve_campaign_parameters():
    assert PARAMETER_NAMES == (
        "h0x", "h0y", "h0z",
        "hx", "hy", "hz",
        "Jxx", "Jyy", "Jzz",
        "gx", "gy", "gz",
    )
    assert COUPLING_NAMES == ("gx", "gy", "gz")


# --- perturbative rule -----------------------------------------------------


def test_perturbative_ratio_uses_the_smallest_nonzero_scale():
    """The coupling must be small against every scale, not just the largest.

    A max-based denominator would pass a configuration whose coupling is larger
    than one of the model's own energy scales.
    """

    config = _candidate(Jzz=5.0, hz=1.0, hx=0.0, h0x=0.0, h0z=0.0, gz=0.5)
    assert detector_scale(config) == 1.0
    assert coupling_scale(config) == 0.5
    assert perturbative_ratio(config) == pytest.approx(0.5)


def test_zero_parameters_are_excluded_from_the_scale():
    config = _candidate(hy=0.0, Jxx=0.0)
    assert detector_scale(config) == 1.0


def test_boundary_coupling_is_admitted_but_a_stronger_one_is_not():
    """The gate must not turn a rounding error into a physical rejection.

    A candidate built as ``g = PERTURBATIVE_RATIO * scale`` can divide back to a
    value one ulp above the threshold. That is admitted; anything measurably
    stronger is not.
    """

    scale = 1.5
    at_boundary = _candidate(
        Jzz=scale, hx=scale, hz=2.0, h0x=scale, h0z=3.0,
        gz=PERTURBATIVE_RATIO * scale,
    )
    assert perturbative_ratio(at_boundary) >= PERTURBATIVE_RATIO
    assert evaluate_config(at_boundary, n_values=(4,))["by_size"], (
        "a boundary candidate must reach diagonalization"
    )

    just_over = _candidate(
        Jzz=scale, hx=scale, hz=2.0, h0x=scale, h0z=3.0,
        gz=1.01 * PERTURBATIVE_RATIO * scale,
    )
    record = evaluate_config(just_over, n_values=(4,))
    assert not record["passed"]
    assert "non-perturbative" in record["rejection_reasons"][0]


def test_non_perturbative_candidate_is_rejected_without_diagonalizing():
    record = evaluate_config(_candidate(gz=0.5), n_values=(4,))
    assert not record["passed"]
    assert record["by_size"] == {}
    assert "non-perturbative" in record["rejection_reasons"][0]


def test_decoupled_candidate_is_rejected():
    """``g = 0`` is excluded: SPEC §8 requires an open weak-coupling window."""

    record = evaluate_config(_candidate(gx=0.0, gy=0.0, gz=0.0), n_values=(4,))
    assert not record["passed"]
    assert "decoupled" in record["rejection_reasons"][0]


def test_configuration_without_any_energy_scale_is_rejected():
    config = ChainConfig(name="empty", hypothesis="", rung="test", gz=0.01)
    assert not np.isfinite(perturbative_ratio(config))
    record = evaluate_config(config, n_values=(4,))
    assert not record["passed"]
    with pytest.raises(ValueError, match="energy scale is undefined"):
        normalize(config)


# --- normalization ---------------------------------------------------------


def test_normalize_sets_the_smallest_nonzero_scale_to_one():
    config = _candidate(Jzz=2.0, hx=4.0, hz=6.0, h0x=4.0, h0z=8.0, gz=0.2)
    normalized, factor = normalize(config)
    assert factor == pytest.approx(0.5)
    assert detector_scale(normalized) == pytest.approx(1.0)


def test_normalize_leaves_the_perturbative_ratio_invariant():
    """Rescaling all parameters together is a change of energy unit only."""

    config = _candidate(Jzz=3.0, hx=3.0, hz=4.5, h0x=3.0, h0z=6.0, gz=0.3)
    normalized, _ = normalize(config)
    assert perturbative_ratio(normalized) == pytest.approx(perturbative_ratio(config))


def test_normalize_is_idempotent():
    once, _ = normalize(_candidate())
    twice, factor = normalize(once)
    assert factor == 1.0
    assert twice.parameters() == once.parameters()


# --- builder mapping -------------------------------------------------------


def test_builder_kwargs_map_every_campaign_parameter():
    config = _candidate(
        h0x=1.0, h0y=2.0, h0z=3.0, hx=1.0, hy=4.0, hz=5.0,
        Jxx=6.0, Jyy=7.0, Jzz=8.0, gx=0.05, gy=0.06, gz=0.07,
    )
    kwargs = config.builder_kwargs(5)
    assert kwargs["hx0"] == 1.0 and kwargs["hy0"] == 2.0 and kwargs["hz0"] == 3.0
    assert kwargs["hx"] == 1.0 and kwargs["hy"] == 4.0 and kwargs["hz"] == 5.0
    assert kwargs["Jxx"] == 6.0 and kwargs["Jyy"] == 7.0 and kwargs["J"] == 8.0
    assert kwargs["Jx"] == 0.05 and kwargs["Jy"] == 0.06 and kwargs["Jz"] == 0.07
    assert kwargs["connectivity"] == "chain"
    assert kwargs["central_coupling"] == "first"


def test_qubit_fields_are_always_explicit():
    """Never let the builder infer a qubit field from the detector field.

    ``SinglePixelHamiltonian*`` treats an unset ``hx0``/``hy0``/``hz0`` as
    inheriting ``hx``/``hy``/``hz``, so an omitted qubit field silently builds a
    different model.
    """

    kwargs = _candidate(h0x=0.0, h0y=0.0, h0z=0.0, hx=1.0, hy=1.0, hz=1.0).builder_kwargs(4)
    for key in ("hx0", "hy0", "hz0"):
        assert kwargs[key] is not None
        assert kwargs[key] == 0.0


def test_excluded_terms_are_pinned_to_zero():
    kwargs = _candidate().builder_kwargs(4)
    for name in FIXED_ZERO:
        assert kwargs[name] == 0.0


# --- estimator control -----------------------------------------------------


def test_thinning_is_exact_and_spread_free_at_the_budget():
    theta = np.linspace(0.1, np.pi - 0.1, ROOT_BUDGET)
    result = _thinned_score(theta, ROOT_BUDGET, draws=8, seed=0)
    assert result["thinning_applied"] is False
    assert result["S_born_thinned_sd"] == 0.0


def test_thinning_reports_a_spread_above_the_budget():
    rng = np.random.default_rng(0)
    theta = rng.uniform(0.0, np.pi, size=4 * ROOT_BUDGET)
    result = _thinned_score(theta, ROOT_BUDGET, draws=32, seed=1)
    assert result["thinning_applied"] is True
    assert result["S_born_thinned_sd"] > 0.0


def test_thinning_is_reproducible_for_a_fixed_seed():
    rng = np.random.default_rng(3)
    theta = rng.uniform(0.0, np.pi, size=4 * ROOT_BUDGET)
    first = _thinned_score(theta, ROOT_BUDGET, draws=16, seed=11)
    second = _thinned_score(theta, ROOT_BUDGET, draws=16, seed=11)
    assert first == second


def test_born_profile_emits_the_house_schema():
    """The keys must match the stored ``results.npz`` schema used by the
    ring-catalog plotters and ``core.born_profile_export``."""

    rng = np.random.default_rng(5)
    profile = born_profile(rng.uniform(0.0, np.pi, size=2048))
    assert set(profile) == {
        "edges", "centers", "p_theta", "p_pi_minus_theta",
        "R", "R_occupied", "R_born",
    }
    assert profile["edges"].size == PROFILE_BINS + 1
    assert profile["centers"].size == PROFILE_BINS
    assert np.allclose(profile["R_born"], np.cos(profile["centers"] / 2.0) ** 2)
    # Empty bins are masked, never imputed.
    assert np.all(np.isnan(profile["R"][~profile["R_occupied"]]))


# --- physics regression ----------------------------------------------------


def test_conserved_qubit_z_collapses_the_root_distribution():
    """With ``h0x = h0y = gx = gy = 0`` the qubit's ``Z`` is conserved.

    The off-diagonal propagator block then vanishes identically, every root sits
    at ``theta = 0``, and the candidate must fail the coverage gate rather than
    score as an uninformative near-zero success.
    """

    record = evaluate_config(
        _candidate(h0x=0.0, h0y=0.0, hx=0.0, hy=0.0, gx=0.0, gy=0.0, gz=0.1),
        n_values=(4,),
    )
    assert not record["passed"]
    assert record["by_size"]["4"]["coverage_bins"] < MIN_COVERAGE_BINS
    assert any("coverage" in reason for reason in record["rejection_reasons"])


def test_azimuthal_moments_are_reported_with_their_noise_floor():
    """Azimuthal structure must be reported, not silently marginalised away.

    The exact Born profile contains only the (0,0) and (1,0) spherical-harmonic
    sectors and is azimuthally symmetric, so any `m != 0` circular moment is
    strong-Born leakage that the polar marginal hides (``SPEC.md`` §5.2, §6.3).
    The moments are only interpretable against the finite-sampling floor, so both
    are recorded.
    """

    record = evaluate_config(_candidate(), n_values=(4,))
    block = record["by_size"]["4"]
    assert set(block["azimuthal_moments"]) == {"1", "2", "3", "4"}
    assert all(0.0 <= v <= 1.0 for v in block["azimuthal_moments"].values())
    assert block["azimuthal_moment_max"] == max(block["azimuthal_moments"].values())
    assert block["azimuthal_noise_floor"] > 0.0


def test_pooled_roots_returns_polar_and_azimuthal_sets_per_time():
    """Per-time sets are kept separate so time-averaged agreement stays
    distinguishable from actual convergence (``SPEC.md`` §7.2)."""

    from scripts.eval_chain_born import TIMES, pooled_roots

    theta_sets, phi_sets, diagnostics = pooled_roots(_candidate(), 4, TIMES)
    assert len(theta_sets) == len(TIMES)
    assert len(phi_sets) == len(TIMES)
    assert all(t.size == 2 ** 4 for t in theta_sets)
    assert "max_isometry_residual" in diagnostics


def test_evaluation_record_is_self_describing():
    record = evaluate_config(_candidate(), n_values=(4,))
    for key in (
        "campaign_version", "parameters", "parameters_as_given", "scale_factor",
        "perturbative_ratio", "times", "root_budget", "by_size",
    ):
        assert key in record
    assert set(record["parameters"]) == set(PARAMETER_NAMES)
