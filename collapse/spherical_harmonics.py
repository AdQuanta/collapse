"""
Spherical Harmonic Projection
=============================

Efficient projection of functions on the sphere onto the complex
spherical-harmonic basis. The implementation separates the azimuthal
Fourier transform from the polar Gauss-Legendre quadrature so repeated
projections can reuse the same precomputed basis tables.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from scipy.fft import fft, next_fast_len
from scipy.special import gammaln, lpmv, roots_legendre


class SphericalFunction(Protocol):
    """Protocol for broadcast-friendly spherical functions."""

    def __call__(self, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Evaluate the function at polar angles *theta* and azimuthal angles *phi*."""
        ...


def _validate_non_negative_int(value: int, name: str) -> int:
    if value < 0:
        raise ValueError(f"{name} must be non-negative.")
    return value


def _validate_positive_int(value: int, name: str) -> int:
    if value <= 0:
        raise ValueError(f"{name} must be positive.")
    return value


def _validate_degree_and_order(degree: int, order: int, l_max: int) -> None:
    if degree < 0 or degree > l_max:
        raise ValueError(f"degree must satisfy 0 <= degree <= {l_max}.")
    if abs(order) > degree:
        raise ValueError("order must satisfy |order| <= degree.")


def _normalization(degrees: np.ndarray, order: int) -> np.ndarray:
    log_norm = 0.5 * (
        np.log(2 * degrees + 1)
        - np.log(4.0 * np.pi)
        + gammaln(degrees - order + 1)
        - gammaln(degrees + order + 1)
    )
    return np.exp(log_norm)


@dataclass(frozen=True)
class SphericalHarmonicExpansion:
    """
    Immutable spherical-harmonic coefficient container.

    Coefficients are stored in a dense matrix with
    ``coefficients[degree, order + l_max] = a_{degree, order}``.
    Entries with ``|order| > degree`` are always zero.
    """

    l_max: int
    coefficients: np.ndarray

    def __post_init__(self) -> None:
        l_max = _validate_non_negative_int(self.l_max, "l_max")
        coeffs = np.asarray(self.coefficients, dtype=np.complex128)
        expected_shape = (l_max + 1, 2 * l_max + 1)
        if coeffs.shape != expected_shape:
            raise ValueError(
                "coefficients must have shape "
                f"{expected_shape}, got {coeffs.shape}."
            )
        coeffs = coeffs.copy()
        coeffs.setflags(write=False)
        object.__setattr__(self, "coefficients", coeffs)

    def coefficient(self, degree: int, order: int) -> complex:
        """Return the coefficient ``a_{degree, order}``."""
        _validate_degree_and_order(degree, order, self.l_max)
        return complex(self.coefficients[degree, order + self.l_max])

    def as_array(self, copy: bool = True) -> np.ndarray:
        """Return the dense coefficient matrix."""
        return self.coefficients.copy() if copy else self.coefficients


def evaluate_spherical_harmonic(
    degree: int,
    order: int,
    theta: np.ndarray,
    phi: np.ndarray,
) -> np.ndarray:
    """
    Evaluate the complex spherical harmonic ``Y_degree^order(theta, phi)``.

    The convention is

    ``Y_l^m(theta, phi) = N_lm P_l^m(cos(theta)) exp(i m phi)``

    with ``theta`` the polar angle in ``[0, pi]`` and ``phi`` the
    azimuthal angle in ``[0, 2*pi]``.
    """
    _validate_degree_and_order(degree, order, degree)

    abs_order = abs(order)
    normalization = _normalization(np.array([degree]), abs_order)[0]
    values = normalization * lpmv(abs_order, degree, np.cos(theta))
    if order < 0:
        values = ((-1) ** abs_order) * values
    return values * np.exp(1j * order * phi)


class SphericalHarmonicProjector:
    """
    Reusable projector onto the complex spherical-harmonic basis.

    Parameters
    ----------
    l_max : int
        Maximum spherical-harmonic degree to retain.
    n_theta : int or None
        Number of Gauss-Legendre nodes in ``cos(theta)``. Defaults to
        ``l_max + 1``.
    n_phi : int or None
        Number of uniform azimuthal samples. Defaults to the next FFT-
        friendly size greater than or equal to ``2 * l_max + 1``.
    """

    def __init__(
        self,
        l_max: int,
        n_theta: int | None = None,
        n_phi: int | None = None,
    ) -> None:
        self.l_max = _validate_non_negative_int(l_max, "l_max")
        self.n_theta = _validate_positive_int(
            n_theta if n_theta is not None else self.l_max + 1,
            "n_theta",
        )
        self.n_phi = _validate_positive_int(
            n_phi if n_phi is not None else next_fast_len(2 * self.l_max + 1),
            "n_phi",
        )

        cos_theta, theta_weights = roots_legendre(self.n_theta)
        self.cos_theta = cos_theta[::-1]
        self.theta = np.arccos(self.cos_theta)
        self.theta_weights = theta_weights[::-1]
        self.phi = 2.0 * np.pi * np.arange(self.n_phi) / self.n_phi

        self._polar_weights = 2.0 * np.pi * self.theta_weights
        self._basis_by_order = tuple(
            self._build_polar_basis(order) for order in range(self.l_max + 1)
        )

    @property
    def grid_shape(self) -> tuple[int, int]:
        """Return the underlying transform grid shape."""
        return (self.n_theta, self.n_phi)

    def sample_function(self, function: SphericalFunction) -> np.ndarray:
        """Sample ``function`` on the projector grid."""
        return self._coerce_samples(
            function(self.theta[:, None], self.phi[None, :])
        )

    def project_function(
        self,
        function: SphericalFunction,
        real_input: bool | None = None,
    ) -> SphericalHarmonicExpansion:
        """Project a callable spherical function onto the basis."""
        raw_samples = function(self.theta[:, None], self.phi[None, :])
        if real_input is None:
            real_input = np.isrealobj(raw_samples)
        samples = self._coerce_samples(raw_samples)
        return self._project_sample_matrix(samples, real_input=real_input)

    def project_samples(
        self,
        samples: np.ndarray,
        real_input: bool | None = None,
    ) -> SphericalHarmonicExpansion:
        """
        Project pre-sampled data defined on this projector's grid.

        ``samples`` must be broadcastable to ``(n_theta, n_phi)``.
        """
        if real_input is None:
            real_input = np.isrealobj(samples)
        sample_matrix = self._coerce_samples(samples)
        return self._project_sample_matrix(sample_matrix, real_input=real_input)

    def _build_polar_basis(self, order: int) -> np.ndarray:
        degrees = np.arange(order, self.l_max + 1)
        legendre = lpmv(order, degrees[None, :], self.cos_theta[:, None])
        return legendre * _normalization(degrees, order)

    def _coerce_samples(self, samples: np.ndarray) -> np.ndarray:
        array = np.asarray(samples)
        expected_shape = self.grid_shape

        if array.shape == expected_shape:
            return np.asarray(array, dtype=np.complex128)

        try:
            broadcast = np.broadcast_to(array, expected_shape)
        except ValueError as exc:
            raise ValueError(
                f"samples must be broadcastable to shape {expected_shape}, "
                f"got {array.shape}."
            ) from exc

        return np.asarray(broadcast, dtype=np.complex128)

    def _project_sample_matrix(
        self,
        samples: np.ndarray,
        real_input: bool,
    ) -> SphericalHarmonicExpansion:
        fourier_modes = fft(samples, axis=1) / self.n_phi
        coefficients = np.zeros(
            (self.l_max + 1, 2 * self.l_max + 1),
            dtype=np.complex128,
        )

        for order, basis in enumerate(self._basis_by_order):
            degrees = np.arange(order, self.l_max + 1)
            coefficients[degrees, self.l_max + order] = self._project_order(
                fourier_modes[:, order],
                basis,
            )

            if order == 0:
                continue

            if real_input:
                coefficients[degrees, self.l_max - order] = (
                    (-1) ** order
                ) * np.conj(coefficients[degrees, self.l_max + order])
                continue

            coefficients[degrees, self.l_max - order] = (
                (-1) ** order
            ) * self._project_order(fourier_modes[:, -order], basis)

        return SphericalHarmonicExpansion(self.l_max, coefficients)

    def _project_order(
        self,
        azimuthal_mode: np.ndarray,
        basis: np.ndarray,
    ) -> np.ndarray:
        return (self._polar_weights * azimuthal_mode) @ basis


def project_onto_spherical_harmonics(
    function: SphericalFunction,
    l_max: int,
    n_theta: int | None = None,
    n_phi: int | None = None,
    real_input: bool | None = None,
) -> SphericalHarmonicExpansion:
    """
    Convenience wrapper for one-off spherical-harmonic projections.
    """
    projector = SphericalHarmonicProjector(
        l_max=l_max,
        n_theta=n_theta,
        n_phi=n_phi,
    )
    return projector.project_function(function, real_input=real_input)
