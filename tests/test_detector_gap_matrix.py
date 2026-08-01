from __future__ import annotations

import numpy as np

from collapse.detector_gap_matrix import DetectorGapMatrixAnalyzer, GapMatrixCase


def _case() -> GapMatrixCase:
    return GapMatrixCase(
        key="test",
        regime="test",
        detector_n=3,
        hz=0.37,
        j=0.61,
        jpm=0.19,
        evolution_time=1.0e3,
        collective_jx=0.01,
        dynamics_n=3,
        born_score=0.0,
        born_rmse=0.0,
        angular_coverage=1.0,
        power_law_alpha=1.0,
        power_law_js=0.0,
        power_law_log10_span=1.0,
        wrapped_gaussian_js=0.0,
    )


def test_pair_gap_matrix_invariants() -> None:
    result = DetectorGapMatrixAnalyzer().analyze(_case())
    assert result.signed_gaps.shape == (8, 8)
    assert np.allclose(result.signed_gaps, -result.signed_gaps.T)
    assert np.allclose(np.diag(result.signed_gaps), 0.0)
    assert np.all(np.diff(result.energies) >= 0.0)
    assert np.isclose(result.bandwidth, np.ptp(result.energies))
    assert result.energy_basis_coupling.shape == (8, 8)
    assert np.allclose(result.energy_basis_coupling, result.energy_basis_coupling.conj().T)
    assert np.all(np.isfinite(np.abs(result.energy_basis_coupling)))
    assert 0.0 <= result.active_zero_gap_weight_fraction <= 1.0
    assert 0.0 <= result.active_finite_time_weight_fraction <= 1.0
    assert result.nearest_active_filter_magnitude >= 0.0
    assert result.nearest_active_dimensionless_gain >= 0.0


def test_invalid_degeneracy_tolerance_is_rejected() -> None:
    try:
        DetectorGapMatrixAnalyzer(0.0)
    except ValueError as error:
        assert "positive" in str(error)
    else:
        raise AssertionError("zero tolerance must be rejected")
