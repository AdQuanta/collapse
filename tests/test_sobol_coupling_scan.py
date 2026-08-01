from __future__ import annotations

import numpy as np

from collapse.sobol_coupling_scan import (
    PERIOD,
    ParameterPoint,
    ScanSettings,
    _diagnostics,
    _parameter_correlation_outputs,
    fit_distributions,
    generate_sobol_points,
)


def test_sobol_sampling_is_exact_unique_and_constrained() -> None:
    settings = ScanSettings(name="jy_nonzero", jy_nonzero=True, count=100, upper=10.0)
    points, coverage = generate_sobol_points(settings)
    assert len(points) == 100
    assert len({(p.jx, p.jy, p.j, p.jpm, p.hz) for p in points}) == 100
    assert [p.config_id for p in points] == [f"config_{i:03d}" for i in range(100)]
    assert all(settings.lower <= value <= settings.upper for p in points for value in (p.jx, p.jy, p.j, p.jpm, p.hz))
    assert all(p.weak_ratio <= settings.kappa + 1e-12 for p in points)
    assert coverage["accepted"] == 100
    assert coverage["minimum_pairwise_distance_unit_cube"] > 0


def test_jy_zero_sampling_keeps_jy_zero() -> None:
    settings = ScanSettings(name="jy_zero", jy_nonzero=False, count=12, upper=10.0)
    points, _ = generate_sobol_points(settings)
    assert all(p.jy == 0.0 for p in points)


def test_wrapped_fits_are_normalized_and_deterministic() -> None:
    theta = np.mod(np.linspace(0.05, 2.7, 256), np.pi)
    fit1, _ = fit_distributions(theta, bins=32, plot_grid=256, nmax=16, tol=1e-9)
    fit2, _ = fit_distributions(theta, bins=32, plot_grid=256, nmax=16, tol=1e-9)
    for key in ("wrapped_gaussian", "wrapped_cauchy"):
        assert abs(fit1[key]["integral_full_period"] - 1.0) < 5e-3
        assert abs(fit1[key]["integral_folded_interval"] - 1.0) < 5e-3
        assert fit1[key]["objective"] == fit2[key]["objective"]
        assert 0.0 <= fit1[key]["mu"] < PERIOD


def test_standard_red_blue_diagnostics_validate_geometry() -> None:
    eigenvalues = np.exp(1j * np.linspace(-np.pi, np.pi, 64, endpoint=False))
    metrics, arrays = _diagnostics(eigenvalues, bins=24)
    assert metrics["red_blue_count_consistency"]
    assert abs(metrics["p_theta_integral"] - 1.0) < 1e-12
    assert abs(metrics["p_reflected_integral"] - 1.0) < 1e-12
    assert metrics["lambda_reconstruction_max_abs"] < 1e-12
    assert metrics["bloch_radius_max_error"] < 1e-12
    assert arrays["bloch_blue"].shape == (64, 3)


def test_correlations_include_parameter_ratios(tmp_path) -> None:
    settings = ScanSettings(name="jy_nonzero", jy_nonzero=True, count=6, upper=10.0)
    records = []
    for index in range(6):
        scale = 1.2 + index
        point = ParameterPoint(
            config_id=f"config_{index:03d}", sobol_index=index,
            unit=(0.1,) * 5, jx=0.001 * scale, jy=0.0012 * scale,
            j=0.1 * scale, jpm=0.2 * scale**1.2, hz=0.3 * scale**0.8,
            weak_limit=0.01 * scale, weak_ratio=0.012,
        )
        fit = {
            model: {metric: (index + 1) * (1.0 if model == "wrapped_gaussian" else 1.5) for metric in (
                "fourier_discrepancy", "integrated_absolute_residual",
                "maximum_density_residual", "circular_transport",
            )}
            for model in ("wrapped_gaussian", "wrapped_cauchy")
        }
        records.append((point, {"S_born": index / 5}, fit))
    _parameter_correlation_outputs(tmp_path, settings, records, label="test")
    text = (tmp_path / "parameter_metric_correlations.csv").read_text()
    assert "jx_over_j" in text
    assert "jx_over_jy" in text
    assert "jpm_over_hz" in text
    assert "weak_ratio" in text
