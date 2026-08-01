"""
Level Spacing Diagnostics
=========================

Compute spectral diagnostics used to distinguish integrable from chaotic
quantum systems.

Two complementary observables are supported:

1. The ratio of consecutive spacings, which is insensitive to unfolding.
2. The unfolded spacing distribution, which requires a smooth estimate of
   the integrated density of states.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from scipy.integrate import quad

# ===================================================================
# Reference mean values
# ===================================================================
MEAN_R_POISSON: float = 2.0 * math.log(2.0) - 1.0
MEAN_R_GOE: float = 0.5307
MEAN_R_GUE: float = 0.6027
MEAN_R_GSE: float = 0.6762

_WIGNER_SPACING_PARAMETERS = {
    1: (np.pi / 2.0, 1, np.pi / 4.0),
    2: (32.0 / np.pi**2, 2, 4.0 / np.pi),
    4: (2.0**18 / (3.0**6 * np.pi**3), 4, 64.0 / (9.0 * np.pi)),
}


# ===================================================================
# Internal helpers
# ===================================================================
def _validate_tol(tol: float) -> float:
    """Validate the degeneracy tolerance."""
    tol = float(tol)
    if tol < 0.0:
        raise ValueError(f"tol must be non-negative; got {tol}")
    return tol


def _validate_beta(beta: int) -> int:
    """Validate the Dyson index used in Wigner surmises."""
    if beta not in _WIGNER_SPACING_PARAMETERS:
        raise ValueError(f"beta must be 1, 2, or 4; got {beta}")
    return beta


def _validate_trim_fraction(trim_fraction: float) -> float:
    """Validate the edge-trimming fraction used during unfolding."""
    trim_fraction = float(trim_fraction)
    if not 0.0 <= trim_fraction < 0.5:
        raise ValueError(
            f"trim_fraction must satisfy 0 <= trim_fraction < 0.5; got {trim_fraction}"
        )
    return trim_fraction


def _sorted_clustered_eigenvalues(
    eigenvalues: np.ndarray,
    tol: float = 1e-12,
) -> np.ndarray:
    """
    Sort the spectrum and merge degenerate clusters into single levels.

    Levels separated by at most ``tol`` are treated as belonging to the
    same cluster. Each cluster is represented by its mean energy so the
    resulting spectrum contains one value per resolved level.
    """
    tol = _validate_tol(tol)
    spectrum = np.sort(np.asarray(eigenvalues, dtype=np.complex128).real.ravel())
    if spectrum.size == 0:
        return np.array([], dtype=np.float64)

    cluster_start = 0
    representatives: list[float] = []

    for idx in range(1, spectrum.size):
        if spectrum[idx] - spectrum[idx - 1] > tol:
            representatives.append(float(np.mean(spectrum[cluster_start:idx])))
            cluster_start = idx

    representatives.append(float(np.mean(spectrum[cluster_start:])))
    return np.asarray(representatives, dtype=np.float64)


def _smoothed_local_spacings(spacings: np.ndarray) -> np.ndarray:
    """
    Estimate the local mean spacing with a moving average.

    This is used as a monotone fallback if the polynomial unfolding fit
    becomes locally non-monotone on a finite sample.
    """
    spacings = np.asarray(spacings, dtype=np.float64)
    if spacings.size == 0:
        return spacings

    if spacings.size < 5:
        return np.full_like(spacings, np.mean(spacings))

    window = max(5, spacings.size // 20)
    if window % 2 == 0:
        window += 1
    window = min(window, spacings.size if spacings.size % 2 == 1 else spacings.size - 1)

    if window < 3:
        return np.full_like(spacings, np.mean(spacings))

    pad = window // 2
    padded = np.pad(spacings, (pad, pad), mode="edge")
    kernel = np.ones(window, dtype=np.float64) / window
    smooth = np.convolve(padded, kernel, mode="valid")
    return np.clip(smooth, np.finfo(np.float64).eps, None)


# ===================================================================
# Core computation
# ===================================================================
def compute_level_spacings(
    eigenvalues: np.ndarray,
    tol: float = 1e-12,
) -> np.ndarray:
    """
    Compute consecutive spacings between resolved energy levels.

    Parameters
    ----------
    eigenvalues : np.ndarray
        Energy eigenvalues (unsorted is fine; they will be sorted).
    tol : float
        Levels separated by at most ``tol`` are treated as degenerate and
        merged before spacings are computed.

    Returns
    -------
    np.ndarray
        Consecutive spacings between resolved levels.
    """
    levels = _sorted_clustered_eigenvalues(eigenvalues, tol=tol)
    if levels.size < 2:
        return np.array([], dtype=np.float64)
    return np.diff(levels)


def compute_level_spacing_ratios(spacings: np.ndarray) -> np.ndarray:
    """
    Compute the ratios of consecutive spacings.

    .. math::
        \\tilde{r}_n = \\frac{\\min(s_n,\\, s_{n+1})}{\\max(s_n,\\, s_{n+1})}

    Parameters
    ----------
    spacings : np.ndarray
        Array of consecutive spacings.

    Returns
    -------
    np.ndarray
        Ratios :math:`\\tilde{r}_n \\in [0, 1]`, length ``len(spacings) - 1``.
    """
    spacings = np.asarray(spacings, dtype=np.float64)
    if spacings.size < 2:
        return np.array([], dtype=np.float64)

    s_n = spacings[:-1]
    s_n1 = spacings[1:]
    return np.minimum(s_n, s_n1) / np.maximum(s_n, s_n1)


def mean_level_spacing_ratio(
    eigenvalues: np.ndarray,
    tol: float = 1e-12,
) -> float:
    """
    Compute the mean level-spacing ratio :math:`\\langle \\tilde{r} \\rangle`.

    The ratio statistic does not require unfolding.
    """
    spacings = compute_level_spacings(eigenvalues, tol=tol)
    ratios = compute_level_spacing_ratios(spacings)
    if ratios.size == 0:
        return float("nan")
    return float(np.mean(ratios))


def unfold_spectrum(
    eigenvalues: np.ndarray,
    tol: float = 1e-12,
    degree: int = 3,
) -> np.ndarray:
    """
    Unfold a spectrum by fitting a smooth staircase function.

    The sorted, non-degenerate levels are mapped to a smooth estimate of
    the integrated density of states :math:`\\overline{N}(E)` obtained
    from a polynomial fit of degree ``degree``.

    Parameters
    ----------
    eigenvalues : np.ndarray
        Energy eigenvalues.
    tol : float
        Degeneracy tolerance.
    degree : int
        Polynomial degree for the smooth staircase fit.

    Returns
    -------
    np.ndarray
        Unfolded energy levels corresponding to the resolved spectrum.
    """
    if degree < 1:
        raise ValueError(f"degree must be at least 1; got {degree}")

    levels = _sorted_clustered_eigenvalues(eigenvalues, tol=tol)
    if levels.size == 0:
        return np.array([], dtype=np.float64)
    if levels.size == 1:
        return np.array([1.0], dtype=np.float64)

    fit_degree = min(int(degree), levels.size - 1)
    staircase = np.arange(1, levels.size + 1, dtype=np.float64)
    coefficients = np.polyfit(levels, staircase, deg=fit_degree)
    unfolded = np.polyval(coefficients, levels)

    if np.any(np.diff(unfolded) <= 0.0):
        raw_spacings = np.diff(levels)
        local_mean = _smoothed_local_spacings(raw_spacings)
        unfolded_spacings = raw_spacings / local_mean
        unfolded = np.concatenate(([0.0], np.cumsum(unfolded_spacings)))

    return unfolded.astype(np.float64, copy=False)


def compute_unfolded_spacings(
    eigenvalues: np.ndarray,
    tol: float = 1e-12,
    degree: int = 3,
    trim_fraction: float = 0.1,
) -> np.ndarray:
    """
    Compute spacings from the unfolded spectrum.

    A fraction of the spectrum can be trimmed from each edge to suppress
    fit artefacts near the boundaries. The returned spacings are then
    normalised to unit mean.

    Parameters
    ----------
    eigenvalues : np.ndarray
        Energy eigenvalues.
    tol : float
        Degeneracy tolerance.
    degree : int
        Polynomial degree used in :func:`unfold_spectrum`.
    trim_fraction : float
        Fraction of resolved levels to discard from each spectral edge.

    Returns
    -------
    np.ndarray
        Unfolded spacings with exact unit mean, suitable for :math:`P(s)`.
    """
    trim_fraction = _validate_trim_fraction(trim_fraction)
    unfolded = unfold_spectrum(eigenvalues, tol=tol, degree=degree)
    if unfolded.size < 2:
        return np.array([], dtype=np.float64)

    edge = int(trim_fraction * unfolded.size)
    if edge > 0 and unfolded.size - 2 * edge >= 2:
        unfolded = unfolded[edge:-edge]

    spacings = np.diff(unfolded)
    spacings = spacings[spacings > 0.0]
    if spacings.size == 0:
        return np.array([], dtype=np.float64)
    return spacings / np.mean(spacings)


# ===================================================================
# Theoretical distributions
# ===================================================================
def poisson_surmise(r: np.ndarray | float) -> np.ndarray:
    r"""
    Level-spacing-ratio distribution for Poisson spectra.

    .. math::
        P_{\mathrm{Poisson}}(r) = \frac{2}{(1 + r)^2}
    """
    r = np.asarray(r, dtype=np.float64)
    return 2.0 / (1.0 + r) ** 2


def poisson_spacing_distribution(s: np.ndarray | float) -> np.ndarray:
    r"""
    Unfolded level-spacing distribution for Poisson spectra.

    .. math::
        P_{\mathrm{Poisson}}(s) = e^{-s}
    """
    s = np.asarray(s, dtype=np.float64)
    return np.where(s >= 0.0, np.exp(-s), 0.0)


@lru_cache(maxsize=8)
def _wigner_ratio_normalisation(beta: int) -> float:
    r"""Compute :math:`C_\beta` such that :math:`\int_0^1 P_\beta(r)\,dr = 1`."""
    _validate_beta(beta)

    def integrand(r: float) -> float:
        return (r + r**2) ** beta / (1.0 + r + r**2) ** (1.0 + 1.5 * beta)

    integral, _ = quad(integrand, 0.0, 1.0)
    return 1.0 / integral


def wigner_surmise(
    r: np.ndarray | float,
    beta: int,
) -> np.ndarray:
    r"""
    Wigner-like surmise for the level-spacing-ratio distribution.

    From Atas et al. (2013), Eq. (7):

    .. math::
        P_\beta(r) = C_\beta
            \frac{(r + r^2)^\beta}
                 {(1 + r + r^2)^{1 + 3\beta/2}}
    """
    beta = _validate_beta(beta)
    r = np.asarray(r, dtype=np.float64)
    normalisation = _wigner_ratio_normalisation(beta)
    return normalisation * (r + r**2) ** beta / (1.0 + r + r**2) ** (1.0 + 1.5 * beta)


def wigner_spacing_distribution(
    s: np.ndarray | float,
    beta: int,
) -> np.ndarray:
    r"""
    Wigner surmise for the unfolded spacing distribution.

    The spacing variable is assumed to satisfy :math:`\langle s \rangle = 1`.
    """
    beta = _validate_beta(beta)
    prefactor, power, exponent = _WIGNER_SPACING_PARAMETERS[beta]
    s = np.asarray(s, dtype=np.float64)
    return np.where(s >= 0.0, prefactor * s**power * np.exp(-exponent * s**2), 0.0)
