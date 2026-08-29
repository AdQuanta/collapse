from __future__ import annotations

from dataclasses import replace

import matplotlib
import numpy as np

matplotlib.use("Agg")

from scripts.build_sobol_flat_ranked_1x6_by_n import CaseRecord, compute_spectral
from scripts.build_vab_coupling_level_spacing_sample import (
    level_spacing_data,
    log_gap_weight_data,
    log_resonance_weight_data,
)


def _record() -> CaseRecord:
    return CaseRecord(
        family="jy_zero",
        dynamics_n=14,
        config_id="test",
        s_born=0.0,
        born_rmse=0.0,
        hz=0.0,
        j=0.75,
        jpm=0.05,
        jx=0.01,
        jy=0.0,
        source_dir="",
        rank=1,
        within_n_rank=1,
        output_path="",
    )


def test_log_gap_weights_are_normalized_and_have_degeneracy_bin() -> None:
    spectral = compute_spectral(_record())
    result = log_gap_weight_data(spectral)

    np.testing.assert_allclose(
        result["exact"] + np.sum(result["weights"]),
        1.0,
        rtol=0.0,
        atol=1.0e-12,
    )
    assert result["exact"] > 0.0
    assert np.all(np.diff(result["edges"]) > 0.0)
    assert np.all(result["edges"] > 0.0)


def test_level_spacing_statistics_are_finite() -> None:
    spectral = compute_spectral(_record())
    result = level_spacing_data(spectral)

    assert result["defined"] is True
    assert result["unfolded"].size > 10
    np.testing.assert_allclose(np.mean(result["unfolded"]), 1.0, atol=1.0e-12)
    assert 0.0 <= result["mean_ratio"] <= 1.0
    assert set(result["distances"]) == {"Poisson", "GOE", "GUE"}
    assert all(np.isfinite(value) for value in result["distances"].values())



def test_resonance_detuning_weights_are_normalized() -> None:
    spectral = compute_spectral(_record())
    result = log_resonance_weight_data(spectral, hz0=0.1)

    np.testing.assert_allclose(
        result["exact"] + np.sum(result["weights"]),
        1.0,
        rtol=0.0,
        atol=1.0e-12,
    )
    assert result["target"] == 0.2
    assert np.all(np.diff(result["edges"]) > 0.0)



def test_level_spacing_statistics_are_undefined_for_single_level_spectrum() -> None:
    record = replace(_record(), hz=0.0, j=0.0, jpm=0.0)
    spectral = compute_spectral(record)
    result = level_spacing_data(spectral)

    assert result["defined"] is False
    assert result["unfolded"].size == 0
    assert np.isnan(result["mean_ratio"])
    assert result["best"] == "undefined"
    assert all(np.isnan(value) for value in result["distances"].values())