"""Focused checks for the central-field diagnostic atlas."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

from collapse.resonant_study import wrapped_variance


SCRIPT = Path(__file__).resolve().parents[1] / "examples" / "plot_single_pixel_hz0_diagnostic_atlas.py"
SPEC = importlib.util.spec_from_file_location("hz0_atlas", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_general_variance_reduces_to_zero_central_field_formula():
    collective_jx = 0.01
    for hz in (-2.0, 0.1, 2.0):
        tested = MODULE.central_field_wrapped_variance(
            0.0, hz, 123.0, j=1.0, jx=collective_jx
        )
        expected = wrapped_variance(hz, 123.0, j=1.0, jx=collective_jx)
        assert np.isclose(tested, expected, rtol=1e-12, atol=1e-12)


def test_matched_field_is_exact_local_resonance():
    assert MODULE.local_resonance_distance(0.1, 0.1, 1.0) < 1e-14
    assert np.isclose(MODULE.local_resonance_distance(0.11, 0.1, 1.0), 0.01)


def test_bloch_branches_are_unit_and_antipodal():
    values = np.array([0.0, 1.0 + 2.0j, -0.3j, 20.0])
    blue, red = MODULE.bloch_branches(values)
    assert np.allclose(np.linalg.norm(blue, axis=1), 1.0)
    assert np.allclose(red, -blue)


def test_density_normalizes():
    edges = np.linspace(0.0, np.pi, 49)
    values = np.linspace(0.0, np.pi, 1024, endpoint=False)
    histogram = MODULE.density(values, edges)
    assert np.isclose(np.sum(histogram * np.diff(edges)), 1.0)
