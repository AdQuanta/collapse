import numpy as np

from core.relative_evolution_pencil import matched_projective_angle_error
from core.relative_evolution_study import (
    RelativeEvolutionCase,
    angular_histogram,
    build_sector_eigenbases,
    detector_resonance_summary,
    evaluate_snapshot,
    exact_zero_field_j0_angles,
)


def test_angular_histogram_is_normalized_and_masks_empty_ratio_bins():
    theta = np.asarray([0.1, 0.2, np.pi - 0.1, np.pi - 0.2])
    histogram = angular_histogram(theta, bins=16)

    np.testing.assert_allclose(
        np.sum(histogram.density * np.diff(histogram.edges)), 1.0
    )
    assert np.all(np.isnan(histogram.ratio[~histogram.occupied]))
    assert histogram.sample_count == theta.size


def test_zero_field_independent_spin_formula_matches_exact_sector_pencil():
    case = RelativeEvolutionCase(
        key="zero_field",
        model="Model 1",
        description="exact collective-spin check",
        hz=0.0,
        j=0.0,
        jpm=0.0,
        hz0=0.0,
        collective_jx=0.2,
    )
    detector_n = 4
    time_value = 2.3
    sectors, _ = build_sector_eigenbases(case, detector_n)
    numerical = evaluate_snapshot(case, detector_n, time_value, sectors)
    analytical = exact_zero_field_j0_angles(
        detector_n, case.collective_jx, time_value
    )

    maximum, rms = matched_projective_angle_error(numerical.spectrum.theta, analytical)
    assert maximum < 1.0e-12
    assert rms < 1.0e-13


def test_matched_ising_field_has_exact_first_order_resonant_weight():
    matched = RelativeEvolutionCase(
        key="matched",
        model="Model 2",
        description="matched fields",
        hz=0.1,
        j=1.0,
        jpm=0.0,
        hz0=0.1,
        collective_jx=0.01,
    )
    detuned = RelativeEvolutionCase(
        key="detuned",
        model="Model 2",
        description="detuned fields",
        hz=0.1,
        j=1.0,
        jpm=0.0,
        hz0=0.13,
        collective_jx=0.01,
    )

    matched_summary = detector_resonance_summary(matched, detector_n=4)
    detuned_summary = detector_resonance_summary(detuned, detector_n=4)

    assert matched_summary.target_signed_gap == -0.2
    assert matched_summary.resonant_weight_fraction > 0.0
    assert detuned_summary.resonant_weight_fraction == 0.0
    assert detuned_summary.nearest_active_detuning > 0.0
