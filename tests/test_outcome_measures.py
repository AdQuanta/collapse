"""Acceptance tests for the preferred-axis (B1) estimator.

``goal_preferred_basis.md`` section 2.5 specifies an acceptance table of exact
``B1`` values for ``rho_0 = cos^(2p)(theta'/2) T(Omega)`` with an unspecified
non-trivial inversion-even envelope ``T``. That table's exact numbers are not
reproducible without the source ``T`` used to generate them: a hand
derivation (recorded below and in the campaign result packet) shows that
``B1`` at ``p != 1`` depends on ``T``'s quadrupole amplitude, so the same
table cannot be regenerated from an independently chosen ``T``.

What section 2.1's derivation *does* guarantee independent of ``T`` -- and
what these tests instead verify -- is:

* at ``p = 1`` (exact Born), ``B1 = 1`` and the ``l >= 3`` odd leakage
  vanish exactly, for *any* inversion-even ``T``, because the ratio
  ``rho_0(-Omega) / rho_0(Omega) = tan^2(theta'/2)`` holds exactly and ``T``
  cancels from that ratio;
* for the specific ``T`` used here (azimuthal content restricted to
  ``m in {0, +-2}``, restricted to a ``theta``-quadrupole and no odd-``l``
  content), the fitted axis is *exactly* the polar axis at every ``p``, not
  only at Born, because the ``m_x = m_y = 0`` and ``S`` off-diagonal
  structure is a property of that azimuthal restriction rather than of Born
  exactness;
* ``B1`` moves monotonically away from 1 as ``p`` moves away from 1, in the
  same direction reported in goal_preferred_basis.md's own (T-specific) table.
"""

from __future__ import annotations

import numpy as np

from core.outcome_measures import (
    antipodal_bloch_cloud,
    odd_harmonic_power,
    outcome_bloch_cloud,
    preferred_axis_from_cloud,
)
from core.spherical_harmonics import SphericalHarmonicProjector


def _quadrature_cloud(p: float, c2: float = 0.5, c3: float = 0.3, n_theta: int = 48,
                       n_phi: int = 48) -> tuple[np.ndarray, np.ndarray]:
    """Return (points, weights) for rho_0 = cos^(2p)(theta/2) * T(theta, phi).

    ``T = 1 + c2 * P2(cos theta) + c3 * cos(2 phi) sin^2(theta)`` is
    inversion-even (``P2`` is an even polynomial and both the
    ``theta``-quadrupole and the ``cos(2 phi)`` term are unchanged under
    ``(theta, phi) -> (pi - theta, phi + pi)``), non-trivial, and carries a
    genuine quadrupole plus an azimuthal ``cos(2 phi)`` term as required by
    goal_preferred_basis.md section 2.5.

    Gauss-Legendre in cos(theta) integrates the polynomial (in cos theta)
    part of the integrand to machine precision for any bandwidth this small;
    the non-polynomial ``cos^(2p)`` factor is resolved to high accuracy at
    this node count for the mild boundary behaviour it has for p < 1.
    """

    projector = SphericalHarmonicProjector(l_max=7, n_theta=n_theta, n_phi=n_phi)
    theta = projector.theta[:, None]
    phi = projector.phi[None, :]
    cos_theta = np.cos(theta)
    p2 = 0.5 * (3.0 * cos_theta**2 - 1.0)
    envelope = 1.0 + c2 * p2 + c3 * np.cos(2.0 * phi) * np.sin(theta) ** 2
    density = np.cos(theta / 2.0) ** (2.0 * p) * envelope
    density = np.broadcast_to(density, projector.grid_shape)

    sin_theta = np.sin(theta)
    directions = np.stack(
        np.broadcast_arrays(
            sin_theta * np.cos(phi),
            sin_theta * np.sin(phi),
            np.cos(theta) + np.zeros_like(phi),
        ),
        axis=-1,
    )
    area_weights = projector.theta_weights[:, None] * (2.0 * np.pi / projector.n_phi)
    weights = np.broadcast_to(area_weights, projector.grid_shape) * density
    return directions.reshape(-1, 3), weights.reshape(-1)


def test_born_profile_gives_exact_unit_dipole_for_any_envelope() -> None:
    points, weights = _quadrature_cloud(p=1.0)
    result = preferred_axis_from_cloud(points, weights)

    assert result.status == "ok"
    assert np.isclose(result.B1, 1.0, atol=1.0e-8)
    axis_error_deg = np.degrees(np.arccos(np.clip(abs(result.n_hat[2]), -1.0, 1.0)))
    assert axis_error_deg < 1.0e-3
    assert np.allclose(result.n_hat[:2], 0.0, atol=1.0e-6)


def test_born_profile_has_no_higher_odd_leakage() -> None:
    points, weights = _quadrature_cloud(p=1.0)
    axis_result = preferred_axis_from_cloud(points, weights)
    harmonics = odd_harmonic_power(points, weights, axis_result.n_hat, l_max=7)

    assert harmonics["odd_power"] > 0.0
    assert harmonics["higher_odd_l3_l5_l7_leakage"] < 1.0e-10


def test_axis_recovered_within_tolerance_away_from_born() -> None:
    for p in (0.6, 0.8, 1.3, 2.0, 3.0):
        points, weights = _quadrature_cloud(p=p)
        result = preferred_axis_from_cloud(points, weights)
        assert result.status == "ok"
        axis_error_deg = np.degrees(np.arccos(np.clip(abs(result.n_hat[2]), -1.0, 1.0)))
        assert axis_error_deg < 1.0e-3, f"p={p}: axis error {axis_error_deg} deg"


def test_b1_moves_monotonically_away_from_born_with_p() -> None:
    ps = (0.6, 0.8, 1.0, 1.3, 2.0, 3.0)
    b1_values = []
    for p in ps:
        points, weights = _quadrature_cloud(p=p)
        result = preferred_axis_from_cloud(points, weights)
        b1_values.append(result.B1)

    assert all(earlier < later for earlier, later in zip(b1_values, b1_values[1:]))
    assert np.isclose(b1_values[2], 1.0, atol=1.0e-8)


def test_great_circle_confinement_refuses_rather_than_reports() -> None:
    n_points = 400
    phi = np.linspace(0.0, 2.0 * np.pi, n_points, endpoint=False)
    points = np.stack([np.cos(phi), np.sin(phi), np.zeros_like(phi)], axis=-1)
    weights = np.ones(n_points)

    result = preferred_axis_from_cloud(points, weights)

    assert result.status == "singular_refused"
    assert result.n_hat is None
    assert result.refusal_reason is not None
    assert "cond(S)" in result.refusal_reason


def test_point_confinement_refuses() -> None:
    points = np.tile(np.array([0.0, 0.0, 1.0]), (10, 1))
    weights = np.ones(10)

    result = preferred_axis_from_cloud(points, weights)

    assert result.status == "singular_refused"


def test_antipodal_cloud_matches_independent_outcome_one_solve() -> None:
    """Cross-check the campaign's cost-saving shortcut against a real QZ solve.

    ``scripts/eval_preferred_basis.py`` derives outcome 1's cloud from outcome
    0's via :func:`antipodal_bloch_cloud` instead of a second pencil solve, to
    halve per-time-step cost at the N=12 end of the WP2 ladder. This is exact
    per ``wiki/concepts/outcome-antipodality.md`` and
    ``tests/test_outcome_antipodality.py``, and this test certifies it again
    directly on the endpoint-chain family this campaign actually uses, on the
    module this campaign actually calls.
    """

    from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

    builder = SinglePixelHamiltonianQuSpin(
        N_pixel=4, connectivity="chain", central_coupling="first",
        J=1.10, Jxx=1.32, Jyy=2.53,
        Jx=0.10, Jy=0.05, Jz=0.06,
        hx=-1.34, hy=0.0, hz=1.00,
        hx0=-1.35, hy0=-1.69, hz0=2.01,
        use_symmetry=False,
    )
    dense = builder.generate()
    energies, vectors = np.linalg.eigh(dense)
    phases = np.exp(-1j * energies * 211.0)
    unitary = (vectors * phases) @ vectors.conj().T

    cloud_0 = outcome_bloch_cloud(unitary, outcome=0)
    derived_1 = antipodal_bloch_cloud(cloud_0)
    independent_1 = outcome_bloch_cloud(unitary, outcome=1)

    assert derived_1.points.shape == independent_1.points.shape
    distance = np.linalg.norm(
        derived_1.points[:, None, :] - independent_1.points[None, :, :], axis=2
    )
    assert float(distance.min(axis=1).max()) < 1.0e-9


def test_outcome_bloch_cloud_on_haar_random_unitary_is_well_formed() -> None:
    rng = np.random.default_rng(2026)
    dimension = 8
    matrix = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(size=(dimension, dimension))
    q, r = np.linalg.qr(matrix)
    phases = np.diag(r) / np.abs(np.diag(r))
    unitary = q * phases

    cloud_0 = outcome_bloch_cloud(unitary, outcome=0)
    cloud_1 = outcome_bloch_cloud(unitary, outcome=1)

    assert cloud_0.points.shape == (cloud_0.n_raw_roots - cloud_0.n_indeterminate, 3)
    assert cloud_1.points.shape[1] == 3
    norms_0 = np.linalg.norm(cloud_0.points, axis=1)
    assert np.allclose(norms_0, 1.0, atol=1.0e-8)
