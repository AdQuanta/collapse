"""State-level regressions independent of root enumeration and Born scores."""

import numpy as np
import pytest

from core.projective_roots import reconstruct_collapse_state


@pytest.mark.parametrize("outcome", [0, 1])
def test_poles_and_degenerate_kernel_superpositions(outcome):
    detector = np.array([1, 2j, -3])
    result = reconstruct_collapse_state(np.eye(6), outcome, outcome, 1-outcome, detector)
    assert result.forbidden_branch_norm == 0
    assert result.factorization_residual == 0
    assert result.retained_norm_error < 1e-15
    np.testing.assert_allclose(result.detector_input, detector / np.linalg.norm(detector))


@pytest.mark.parametrize("scale", [2-3j, 1e300, 1e-300])
def test_projective_rescaling_changes_only_global_phase(scale):
    swap = np.eye(4)[[0, 2, 1, 3]]
    base = reconstruct_collapse_state(swap, 0, 1j, 2, [1, 0])
    changed = reconstruct_collapse_state(swap, 0, scale*1j, scale*2, [1, 0])
    phase = scale / abs(scale)
    np.testing.assert_allclose(changed.evolved_joint_state, phase*base.evolved_joint_state,
                               rtol=0, atol=1e-15)
    assert changed.forbidden_branch_norm == 0


def test_near_collapse_and_nonunitarity_are_not_hidden_by_normalization():
    near = reconstruct_collapse_state(np.eye(4), 0, 1e-6, 1, [1, 0])
    assert near.forbidden_branch_norm > 1e-7
    assert near.factorization_residual > 1e-7
    assert np.linalg.norm(near.retained_detector_branch)**2 > 1-2e-12
    nonunitary = reconstruct_collapse_state(2*np.eye(4), 0, 0, 1, [1, 0])
    assert nonunitary.forbidden_branch_norm == 0
    assert nonunitary.retained_norm_error == 1


@pytest.mark.parametrize("changes", [
    {"U": np.eye(3)}, {"U": np.zeros((4, 3))}, {"U": np.full((4, 4), np.nan)},
    {"outcome": 2}, {"outcome": 1.0}, {"alpha": 0, "beta": 0}, {"alpha": np.inf},
    {"alpha": [1, 2], "beta": [0, 1]}, {"detector_state": [0, 0]},
    {"detector_state": [1, 0, 0]}, {"detector_state": [[1], [0]]},
    {"detector_state": [1, np.nan]},
])
def test_invalid_inputs(changes):
    args = dict(U=np.eye(4), outcome=0, alpha=0, beta=1, detector_state=[1, 0])
    args.update(changes)
    with pytest.raises(ValueError):
        reconstruct_collapse_state(**args)
