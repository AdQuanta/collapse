"""Statistical-contract tests for the resolved Sobol relation analysis."""

import importlib.util
import json
from pathlib import Path

import numpy as np


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "analyze_sobol_full_sphere_relations.py"
)
SPEC = importlib.util.spec_from_file_location("sobol_relations", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_benjamini_hochberg_is_monotone_in_ranked_order() -> None:
    p_values = [0.04, 0.001, 0.02, 0.8]
    adjusted = MODULE.benjamini_hochberg(p_values)
    order = np.argsort(p_values)
    ranked = np.asarray(adjusted)[order]

    assert np.all(np.diff(ranked) >= 0.0)
    assert np.all((0.0 <= np.asarray(adjusted)) & (np.asarray(adjusted) <= 1.0))


def test_parameter_features_use_source_coupling_for_detuning() -> None:
    row = {
        "parameters": json.dumps(
            {
                "hz0": 0.1,
                "configuration": {
                    "j": 2.0,
                    "jpm": 0.5,
                    "jx": 0.01,
                    "hz": 0.099,
                    "weak_ratio": 0.02,
                },
            }
        )
    }
    features = MODULE.parameter_features(row)

    assert np.isclose(features["delta_source_signed"], 0.1)
    assert np.isclose(features["delta_source_absolute"], 0.1)
    assert np.isclose(features["log10_J_over_Jx"], np.log10(200.0))
