from __future__ import annotations

import math

from collapse.detector_resonance import (
    DenseRingDetectorBuilder,
    DetectorSpec,
    SpectralProjectorAnalyzer,
    relative_weight_map_error,
    rotate_subspaces,
    transition_weight_map,
)


def analyze(spec: DetectorSpec, hz0: float = 0.0):
    operators = DenseRingDetectorBuilder().build(spec)
    analyzer = SpectralProjectorAnalyzer()
    return operators, analyzer, analyzer.analyze(operators, hz0)


def test_projector_weights_exhaust_collective_x_norm():
    spec = DetectorSpec(detector_n=5, hz=0.1, j=1.0, jpm=0.3)
    _, _, (_, _, summary) = analyze(spec)
    assert math.isclose(summary.total_active_weight, spec.detector_n * 2**spec.detector_n, rel_tol=1e-12)


def test_ising_detector_degeneracy_is_active_only_on_flip_resonance():
    _, _, (_, _, generic) = analyze(DetectorSpec(6, hz=0.1, j=1.0, jpm=0.0))
    _, _, (_, _, resonant) = analyze(DetectorSpec(6, hz=2.0, j=1.0, jpm=0.0))
    assert generic.detector_degenerate_weight_fraction == 0.0
    assert resonant.detector_degenerate_weight_fraction > 0.0


def test_matched_central_field_selects_nonzero_detector_gap():
    _, _, (_, _, unmatched) = analyze(DetectorSpec(6, hz=0.1, j=1.0, jpm=0.0), hz0=0.0)
    _, _, (_, _, matched) = analyze(DetectorSpec(6, hz=0.1, j=1.0, jpm=0.0), hz0=0.1)
    assert unmatched.exact_resonant_weight_fraction == 0.0
    assert matched.exact_resonant_weight_fraction > 0.0


def test_projector_transition_weights_are_degenerate_basis_invariant():
    operators, analyzer, (subspaces, transitions, _) = analyze(
        DetectorSpec(6, hz=0.1, j=1.0, jpm=1.0)
    )
    rotated = rotate_subspaces(subspaces, seed=17)
    rotated_transitions = analyzer.active_transitions(rotated, operators.coupling)
    error = relative_weight_map_error(
        transition_weight_map(transitions),
        transition_weight_map(rotated_transitions),
    )
    assert error < 1.0e-12
