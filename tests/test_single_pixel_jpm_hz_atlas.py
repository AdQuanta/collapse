"""Focused checks for the J=0, Jpm=1 field-neighborhood atlas."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "plot_single_pixel_jpm_hz_atlas.py"
SPEC = importlib.util.spec_from_file_location("jpm_hz_atlas", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_default_grid_covers_all_requested_neighborhoods():
    grid = MODULE.field_grid(MODULE.DEFAULT_CENTERS, MODULE.DEFAULT_OFFSETS)
    assert len(grid) == 25
    for center in (-2.0, -1.0, 0.0, 1.0, 2.0):
        for offset in (-0.05, -0.01, 0.0, 0.01, 0.05):
            assert round(center + offset, 10) in grid


def test_default_neighborhoods_do_not_overlap():
    grid = MODULE.field_grid(MODULE.DEFAULT_CENTERS, MODULE.DEFAULT_OFFSETS)
    assert len(set(grid)) == len(grid)
    assert np.all(np.diff(sorted(grid)) > 0.0)


def test_raw_path_is_deterministic(tmp_path):
    expected = tmp_path / "N10" / "hz_-1.0100" / "raw_t1000000.npz"
    assert MODULE.raw_path(tmp_path, 10, -1.01, 1e6) == expected


def test_requested_model_defaults_are_explicit_in_source():
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'default=0.0, dest="j"' in source
    assert 'default=1.0, dest="jpm"' in source
    assert 'default=0.01' in source
    assert "PlusMinusSpectralVarianceProvider" in source
