from __future__ import annotations

import numpy as np

from collapse.joint_hamiltonian_conjecture import (
    FiniteTimeKernelBalance,
    HamiltonianPoint,
    JointProfileClassifier,
    confusion,
)


def _point(**updates: float | int | str) -> HamiltonianPoint:
    values: dict[str, float | int | str] = {
        "detector_n": 14,
        "hz": 0.01,
        "j": 0.75,
        "jpm": 0.5,
        "born_score": 0.89,
        "born_rmse": 0.03,
        "coverage": 1.0,
        "alpha": 0.88,
        "power_law_js": 0.02,
        "power_law_span": 1.9,
        "source_npz": "source.npz",
    }
    values.update(updates)
    return HamiltonianPoint(**values)  # type: ignore[arg-type]


def test_joint_gate_and_candidate_corridor() -> None:
    classifier = JointProfileClassifier()
    point = _point()
    assert classifier.is_joint(point)
    assert classifier.family(point) == "mixed ZZ+exchange"
    assert classifier.corridor(point) == "zero field"
    assert classifier.microscopic_candidate(point)


def test_heavy_non_born_counterexample_is_rejected() -> None:
    classifier = JointProfileClassifier()
    point = _point(hz=2.0, j=1.0, jpm=0.0, born_score=-0.41, born_rmse=0.40, alpha=0.42)
    assert classifier.is_heavy(point)
    assert not classifier.is_born_like(point)
    assert not classifier.is_joint(point)
    assert not classifier.microscopic_candidate(point)


def test_confusion_metrics() -> None:
    result = confusion([True, True, False, False], [True, False, True, False])
    assert result == {"tp": 1, "fp": 1, "fn": 1, "tn": 1, "precision": 0.5, "recall": 0.5}


def test_finite_time_kernel_balance_is_parameter_determined() -> None:
    probe = FiniteTimeKernelBalance(probe_n=3, evolution_time=100.0, bins=8, jx=0.02)
    first = probe.analyze(_point(hz=0.01, j=2.0, jpm=0.05))
    second = probe.analyze(_point(hz=0.01, j=2.0, jpm=0.05))
    assert first == second
    assert np.isfinite(first.born_score)
    assert 0.0 <= first.coverage <= 1.0
    assert 0.0 <= first.non_atomic_fraction <= 1.0
