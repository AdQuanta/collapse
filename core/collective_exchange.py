"""Exact collective exchange sectors and a deliberately invalid root limit.

Native model: H=-(g/sqrt(N)) (Xq sum Xi + Yq sum Yi), H_D=H_Q=0.
The scalar Gaussian formulas describe the limit of trace observables, not
the native QZ root limit. See BORN_NONNORMAL_LIMIT.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator

import numpy as np
from scipy.integrate import quad
from scipy.linalg import svdvals
from scipy.special import dawsn


@dataclass(frozen=True)
class ExchangeSector:
    """Spin-j detector sector, ordered m=-j,...,j, with exact multiplicity."""

    two_j: int
    multiplicity: int
    a: np.ndarray
    c: np.ndarray


def exchange_sector_blocks(
    detector_size: int, *, coupling: float, time: float
) -> Iterator[ExchangeSector]:
    """Yield exact-form propagator columns in all detector total-spin sectors.

    A is diagonal; C raises m by one. Columns satisfy A†A+C†C=I.
    Polynomial roots are all zero whenever A is nonsingular. Multiplicity
    weights count the full 2^N detector space, without selecting a spin sector.
    """
    if not isinstance(detector_size, int) or detector_size < 1:
        raise ValueError("detector_size must be a positive integer")
    if not np.isfinite(coupling) or not np.isfinite(time):
        raise ValueError("coupling and time must be finite")
    for k in range(detector_size//2+1):
        two_j = detector_size-2*k
        j = two_j/2
        m = np.arange(two_j+1)-j
        frequency = 2*coupling/np.sqrt(detector_size)*np.sqrt((j-m)*(j+m+1))
        a = np.diag(np.cos(time*frequency)).astype(complex)
        c = np.diag(1j*np.sin(time*frequency[:-1]), k=-1)
        multiplicity = comb(detector_size, k)-(comb(detector_size, k-1) if k else 0)
        yield ExchangeSector(two_j, multiplicity, a, c)


def gaussian_exchange_flip_probability(*, coupling: float, time: float) -> float:
    """Exact limiting normalized trace C†C; not a probability over QZ roots."""
    if not np.isfinite(coupling) or not np.isfinite(time):
        raise ValueError("coupling and time must be finite")
    argument = np.sqrt(2)*coupling*time
    return float(argument*dawsn(argument))


def exchange_log_cutoff_audit(
    detector_size: int, *, coupling: float, time: float,
    log_radii: np.ndarray, singular_cutoffs: np.ndarray,
) -> dict[str, np.ndarray | float]:
    """Compare clipped SVD log integrals with exact triangular determinants.

    All detector spin sectors retain their algebraic multiplicities. Cutoffs
    are diagnostics, never used to change the native root measure. The array
    ``lost_log_integral`` is integral log(max(s,eta)/s), computed using the
    exact-form determinant so unresolved tiny singular values are not logged.
    """
    x = np.asarray(log_radii, dtype=float)
    cutoffs = np.asarray(singular_cutoffs, dtype=float)
    if x.ndim != 1 or x.size == 0 or not np.all(np.isfinite(x)) or np.any(abs(x) > 100):
        raise ValueError("log_radii must be a finite vector with |x| <= 100")
    if cutoffs.ndim != 1 or cutoffs.size == 0 or np.any((cutoffs <= 0) | (cutoffs >= 1)):
        raise ValueError("singular_cutoffs must be a vector in (0,1)")
    if not np.all(np.isfinite(cutoffs)):
        raise ValueError("singular cutoffs must be finite")
    grid = np.r_[0., x]
    clipped = np.zeros((grid.size, cutoffs.size))
    small_mass = np.zeros_like(clipped)
    flip, log_a = 0., 0.
    for sector in exchange_sector_blocks(detector_size, coupling=coupling, time=time):
        weight = sector.multiplicity/2**detector_size
        diagonal = abs(sector.a.diagonal())
        if np.any(diagonal == 0):
            raise ArithmeticError("singular A: exact zero-root regularity is not certified")
        log_a += weight*np.sum(np.log(diagonal))
        flip += weight*np.linalg.norm(sector.c, "fro")**2
        for row, value in enumerate(grid):
            singular = svdvals(sector.c-np.exp(value)*sector.a)
            clipped[row] += weight*np.log(np.maximum(singular[:, None], cutoffs)).sum(axis=0)
            small_mass[row] += weight*(singular[:, None] < cutoffs).sum(axis=0)
    return dict(
        clipped_potential=clipped[1:]-clipped[0],
        lost_log_integral=clipped[1:]-(log_a+x[:, None]),
        reference_lost_log_integral=clipped[0]-log_a,
        below_cutoff_mass=small_mass[1:],
        flip_probability=float(flip),
        exact_log_a=float(log_a),
    )


def gaussian_exchange_root_potential(
    log_radii: np.ndarray, *, coupling: float, time: float, tail_probability: float = 1e-13
) -> tuple[np.ndarray, np.ndarray]:
    """Potential of roots of the scalar Gaussian limit, NOT the native limit.

    Gaussian variables X,Y have variance one, R=sqrt(X²+Y²) is Rayleigh,
    and the scalar radius is |tan(g*t*R)|. Quadrature is split at every
    kernel kink. The reported error adds the explicit omitted tail bound.
    """
    values = np.asarray(log_radii, dtype=float)
    scale = abs(coupling*time)
    if not np.isfinite(scale) or scale == 0:
        raise ValueError("coupling*time must be finite and nonzero")
    if not np.all(np.isfinite(values)) or np.any(np.abs(values) > 100):
        raise ValueError("log radii must be finite with absolute value <= 100")
    if not 0 < tail_probability < 1:
        raise ValueError("tail_probability must lie in (0,1)")
    upper = scale*np.sqrt(-2*np.log(tail_probability))
    outputs, errors = [], []
    for x in values.ravel():
        if x == 0:
            outputs.append(0.)
            errors.append(0.)
            continue
        crossing = np.arctan(np.exp(x))
        offsets = [0., crossing, np.pi/4, np.pi/2, 3*np.pi/4, np.pi-crossing]
        points = sorted({0., upper} | {
            float(k*np.pi+offset)
            for k in range(int(upper/np.pi)+1) for offset in offsets
            if 0 < k*np.pi+offset < upper
        })

        def integrand(phase: float) -> float:
            la, lb = np.log(abs(np.sin(phase))), np.log(abs(np.cos(phase)))
            kernel = max(la, x+lb)-max(la, lb)
            return float(kernel*phase/scale**2*np.exp(-phase**2/(2*scale**2)))

        integral, error = 0., 0.
        for left, right in zip(points[:-1], points[1:]):
            val, err = quad(integrand, left, right, epsabs=1e-12, epsrel=1e-11)
            integral += val
            error += err
        outputs.append(integral)
        errors.append(error+abs(x)*tail_probability)
    return np.array(outputs).reshape(values.shape), np.array(errors).reshape(values.shape)
