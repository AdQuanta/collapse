"""Focused checks for the fixed-J plus-minus-coupling atlas."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "examples" / "plot_single_pixel_jpm_sweep_atlas.py"
SPEC = importlib.util.spec_from_file_location("jpm_sweep_atlas", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_default_grid_spans_weak_equal_and_larger_than_j():
    values = MODULE.DEFAULT_JPM_VALUES
    MODULE.validate_grid(values, 1.0)
    assert 0.001 in values
    assert 1.0 in values
    assert max(values) > 1.0


def test_grid_rejects_missing_jpm_equals_j():
    with pytest.raises(ValueError, match="Jpm=J"):
        MODULE.validate_grid((0.001, 0.01, 0.1, 2.0), 1.0)


def test_raw_paths_separate_coupling_values(tmp_path):
    first = MODULE.raw_path(tmp_path, 10, 0.1, 0.1, 1.0e6)
    second = MODULE.raw_path(tmp_path, 10, 1.0, 0.1, 1.0e6)
    assert first != second
    assert "Jpm_0p1" in str(first)
    assert "Jpm_1" in str(second)


def test_requested_model_defaults_are_explicit_in_source():
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'default=1.0, dest="j"' in source
    assert 'default=0.1' in source
    assert 'default=0.0' in source
    assert 'default=0.01' in source
    assert "DetectorSpectralVarianceProvider" in source
    assert '"o-"' in source
    assert ".stairs(" in source
