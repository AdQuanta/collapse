"""Independent quadrature and adversarial finite-harmonic/count checks."""

import itertools

import numpy as np
import pytest
from scipy.integrate import quad

from core.exact_born_limits import (
    circular_count_harmonics, histogram_born_errors,
    minimum_uniform_histogram_tv, uniform_bin_born_limits,
)


@pytest.mark.parametrize("bins", [1, 2, 5, 16, 64, 100])
def test_optimal_step_bounds_against_independent_quadrature(bins):
    edges = np.linspace(0, np.pi, bins + 1)
    born = lambda x: np.cos(x / 2)**2
    means = np.array([quad(born, a, b, epsabs=1e-13)[0] / (b-a) for a, b in zip(edges[:-1], edges[1:])])
    midpoint_values = (born(edges[:-1]) + born(edges[1:])) / 2
    bounds = uniform_bin_born_limits(bins)
    assert histogram_born_errors(edges, midpoint_values)["supremum"] == pytest.approx(bounds["supremum"], abs=1e-14)
    square_integral = sum(quad(lambda x: (r-born(x))**2, a, b, epsabs=1e-13)[0] for r, a, b in zip(means, edges[:-1], edges[1:]))
    assert np.sqrt(square_integral / np.pi) == pytest.approx(bounds["rms"], abs=1e-13)
    assert histogram_born_errors(edges, means)["rms"] == pytest.approx(bounds["rms"], abs=1e-13)
    # Exact bin-center target values are still a nonzero-error step function.
    assert histogram_born_errors(edges, born((edges[:-1]+edges[1:])/2))["supremum"] > 0


@pytest.mark.parametrize("count,bins", [(3, 2), (4, 3), (5, 4), (8, 4)])
def test_count_tv_bound_by_exhaustive_small_inventories(count, bins):
    distances = []
    for counts in itertools.product(range(count + 1), repeat=bins):
        if sum(counts) == count:
            distances.append(.5 * np.sum(abs(np.array(counts) / count - 1 / bins)))
    assert min(distances) == pytest.approx(minimum_uniform_histogram_tv(count, bins), abs=1e-15)


def test_uniform_bins_and_zero_low_harmonics_do_not_certify_continuous_uniformity():
    count = 32
    phases = 2 * np.pi * (np.arange(count) + .5) / count
    histogram, _ = np.histogram(phases, np.linspace(0, 2*np.pi, count + 1))
    np.testing.assert_array_equal(histogram, 1)
    moments = circular_count_harmonics(phases, count)
    assert np.max(abs(moments[1:count])) < 1e-13
    assert abs(moments[count]) == pytest.approx(1., abs=1e-14)


def test_antipodal_cloud_hides_from_first_harmonic():
    moments = circular_count_harmonics(np.array([np.pi/2, 3*np.pi/2]), 4)
    assert abs(moments[1]) < 1e-14
    assert abs(moments[2]) == pytest.approx(1.)


def test_missing_bins_and_invalid_inputs():
    assert np.isnan(histogram_born_errors(np.linspace(0, np.pi, 3), np.array([1., np.nan]))["supremum"])
    with pytest.raises(ValueError):
        uniform_bin_born_limits(0)
    with pytest.raises(ValueError):
        minimum_uniform_histogram_tv(0, 36)


def test_native_equatorial_family_is_only_born_on_its_support():
    from core.born_structure_controls import control_sectors
    from core.relative_evolution_sector import generalized_relative_evolution_from_sectors

    n, jx = 5, .21
    time = np.pi * np.sqrt(n) / (4 * jx)
    params = dict(j=.13, jpm=.26, j2=.07, jpm2=.14, hz=0., hz0=0., jx=jx)
    sectors = control_sectors(params, n)
    result = generalized_relative_evolution_from_sectors(sectors, time, n + 1)
    np.testing.assert_allclose(result.theta, np.pi/2, rtol=0, atol=1e-12)
    assert result.maximum_homogeneous_residual < 1e-11
    # An equatorial atom and its reflection coincide, giving R=1/2 there;
    # the measure has no support at other polar angles.
    assert len(result.theta) == 2**n
