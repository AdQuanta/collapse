"""Contract tests for the preferred-basis campaign evaluator.

Companion to ``tests/test_eval_chain_born.py``: pins the frozen constants this
campaign shares with (or deliberately reuses from) ``eval_chain_born.py``, and
exercises ``evaluate_config`` end to end at a small, fast ``N`` so a broken
wiring (e.g. the axis result not reaching the record, or the antipodal
shortcut silently falling back to something else) fails a test rather than
surfacing only in an expensive N=10/N=12 run.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import numpy as np

from eval_chain_born import ChainConfig, PARAMETER_NAMES
from eval_preferred_basis import (
    CAMPAIGN_VERSION,
    L_MAX,
    PENCIL_SOLVER_OPTIONS,
    TIMES,
    evaluate_config,
    pooled_outcome_clouds,
    score_pooled_clouds,
)


def _candidate(**overrides) -> ChainConfig:
    base = dict(
        name="test", hypothesis="fixture", rung="test",
        h0x=-1.35, h0y=-1.69, h0z=2.01, hx=-1.34, hy=0.0, hz=1.00,
        Jxx=1.32, Jyy=2.53, Jzz=1.10, gx=0.10, gy=0.05, gz=0.06,
    )
    base.update(overrides)
    return ChainConfig(**base)


def test_frozen_contract_constants() -> None:
    assert CAMPAIGN_VERSION == "preferred-basis-v1"
    assert len(TIMES) == 6
    assert np.isclose(TIMES[0], 100.0) and np.isclose(TIMES[-1], 1000.0)
    assert L_MAX == 7
    assert PENCIL_SOLVER_OPTIONS["compute_left_eigenvectors"] is False


def test_evaluate_config_end_to_end_small_n() -> None:
    config = _candidate()
    reference_axis = np.array([-1.35, -1.69, 2.01])
    record = evaluate_config(config, (6,), reference_axis)

    assert record["passed"] is True
    block = record["by_size"]["6"]
    assert block["axis_status"] == "ok"
    assert block["B1"] > 0.0
    assert -1.0 <= block["axis_dot_reference"] <= 1.0
    assert 0.0 <= block["axis_angle_deg_from_reference"] <= 90.0
    assert "odd_harmonic" in block and "power_by_l" in block["odd_harmonic"]
    assert "quartet" in block and "E_marg" in block["quartet"]
    assert len(block["per_time"]) == 6


def test_evaluate_config_rejects_non_perturbative_coupling() -> None:
    config = _candidate(gx=5.0)
    record = evaluate_config(config, (6,), np.array([-1.35, -1.69, 2.01]))

    assert record["passed"] is False
    assert any("non-perturbative" in reason for reason in record["rejection_reasons"])
    assert record["by_size"] == {}


def test_score_pooled_clouds_matches_directly_computed_axis() -> None:
    """The evaluator's own pipeline must not silently diverge from calling
    ``core.outcome_measures`` directly on the same pooled clouds."""

    from core.outcome_measures import preferred_axis_from_cloud

    config = _candidate()
    pooled = pooled_outcome_clouds(config, 6, TIMES)
    metrics = score_pooled_clouds(pooled)
    direct = preferred_axis_from_cloud(pooled["points_0"], pooled["weights_0"])

    assert metrics["axis_status"] == direct.status == "ok"
    assert np.isclose(metrics["B1"], direct.B1)
    assert np.allclose(metrics["n_hat"], direct.n_hat)
