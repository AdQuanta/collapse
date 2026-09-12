"""Independent native QZ and asymptotic checks of the detuning obstruction."""

import numpy as np
import pytest
from scipy.linalg import expm

from core.commuting_vector_field import (
    gaussian_resonance_coefficient, gaussian_resonant_cap,
    mixed_south_probability, vector_field_column,
)
from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum


@pytest.mark.parametrize("size,time", [(2, .31), (3, 1.7), (4, 11.3), (4, 83.)])
def test_native_zx_qz_matches_joint_field_solution(size, time):
    g, c, h, b = .7, .5, .2, .8
    matrix = SinglePixelHamiltonianNumpy(
        N_pixel=size, J=0., Jx=g / np.sqrt(size),
        Jzx=c / np.sqrt(size), hx=.13, hz=0., hx0=h, hz0=b,
        central_coupling="all",
    ).generate()
    d = 2**size
    unitary = expm(-1j * time * matrix)
    roots = generalized_relative_evolution_spectrum(
        unitary[:d, :d], unitary[d:, :d],
    )
    assert not np.any(roots.indeterminate | roots.infinite)
    assert roots.maximum_homogeneous_residual < 2e-13
    collective = np.array([size - 2 * n.bit_count() for n in range(d)]) / np.sqrt(size)
    a, cc = vector_field_column(h + g * collective, b + c * collective, time=time)
    expected = 2 * np.arctan2(abs(cc), abs(a))
    np.testing.assert_allclose(np.sort(roots.theta), np.sort(expected), atol=3e-12)
    np.testing.assert_allclose(abs(a)**2 + abs(cc)**2, 1., atol=1e-14)


@pytest.mark.parametrize("b,h", [(.8, .2), (-.6, .2), (.3, -.1)])
def test_derived_resonance_coefficient(b, h):
    args = dict(transverse_slope=.7, transverse_offset=h,
                longitudinal_slope=.5, detuning=b)
    coefficient = gaussian_resonance_coefficient(**args)
    errors = []
    for epsilon in [1e-2, 1e-3, 1e-4]:
        cap, error = gaussian_resonant_cap(**args, epsilon=epsilon)
        assert error < 1e-11
        errors.append(abs(cap / epsilon - coefficient))
    assert errors[0] > errors[1] > errors[2]
    assert errors[-1] / coefficient < .002


def test_proportional_fields_have_a_strict_support_gap():
    args = dict(transverse_slope=.75, transverse_offset=.375,
                longitudinal_slope=.5, detuning=.25)
    assert gaussian_resonance_coefficient(**args) < 1e-15
    cap, _ = gaussian_resonant_cap(**args, epsilon=.01)
    assert cap < 1e-20
    np.testing.assert_allclose(mixed_south_probability([0, .5, 1], epsilon=.01),
                               [0, 0, 2 / np.pi * np.arcsin(.1)])


def test_nearly_coincident_field_zeros_are_resolved_without_cancellation():
    args = dict(transverse_slope=.75, transverse_offset=.375 + 1e-12,
                longitudinal_slope=.5, detuning=.25)
    coefficient = gaussian_resonance_coefficient(**args)
    cap, error = gaussian_resonant_cap(**args, epsilon=1e-4)
    assert abs(cap / 1e-4 - coefficient) / coefficient < .002
    assert error < cap * 1e-6
