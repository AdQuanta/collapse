"""Focused checks for the collective-Jx h_z resonance atlas."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "plot_single_pixel_hz_resonance_atlas.py"
SPEC = importlib.util.spec_from_file_location("hz_resonance_atlas", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_default_grid_contains_exact_and_near_resonances():
    grid = MODULE.field_grid(MODULE.DEFAULT_CENTERS, MODULE.DEFAULT_OFFSETS)
    assert len(grid) == 15
    for center in (-2.0, 0.0, 2.0):
        for offset in (-0.05, -0.01, 0.0, 0.01, 0.05):
            assert round(center + offset, 10) in grid


def test_variance_peaks_at_all_three_resonances():
    spec = MODULE.SinglePixelSpec(detector_n=10, j=1.0, jx=0.01, hz0=0.0)
    t = 1000.0
    for center in (-2.0, 0.0, 2.0):
        at_resonance = MODULE.central_field_wrapped_variance(spec, center, t)
        detuned = MODULE.central_field_wrapped_variance(spec, center + 0.01, t)
        assert at_resonance > 100.0 * detuned


def test_raw_path_is_exact_and_deterministic(tmp_path):
    expected = tmp_path / "N10" / "hz_+2.0100" / "raw_t1000.npz"
    assert MODULE.raw_path(tmp_path, 10, 2.01, 1000.0) == expected


def test_resonance_neighborhoods_do_not_overlap():
    grid = MODULE.field_grid((-2.0, 0.0, 2.0), (-0.05, -0.01, 0.0, 0.01, 0.05))
    assert len(set(grid)) == len(grid)
    assert np.all(np.diff(sorted(grid)) > 0)
