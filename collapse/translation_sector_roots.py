"""Recover translation-sector projective roots from concatenated results.

For a clean ring with uniform central coupling, the full Hamiltonian is
diagonalised in detector-translation sectors ordered by QuSpin ``kblock``.
The relative-evolution implementation preserves that order when concatenating
the roots of ``U10 v = lambda U00 v``.  This module supplies the exact cyclic
representation multiplicities needed to split such an archived root array
without repeating the expensive Hamiltonian diagonalisation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class TranslationRootSector:
    r"""Projective roots in one detector momentum sector.

    ``momentum_index`` denotes :math:`k=2\pi m/N`.  The dimension is the
    multiplicity of that cyclic irrep in the detector Hilbert space, and hence
    the number of roots contributed by the sector.
    """

    momentum_index: int
    detector_n: int
    eigenvalues: np.ndarray

    @property
    def dimension(self) -> int:
        return int(self.eigenvalues.size)


def cyclic_translation_multiplicities(detector_n: int) -> tuple[int, ...]:
    r"""Return exact detector-Hilbert-space dimensions for every momentum.

    The character of a one-site translation by ``r`` on ``N`` binary spins is
    :math:`2^{\gcd(N,r)}`.  Fourier projection therefore gives

    .. math::

       d_m=\frac1N\sum_{r=0}^{N-1}
       e^{-2\pi i m r/N}2^{\gcd(N,r)}.

    Floating-point Fourier evaluation is rounded only after checking that it
    lies within a tight tolerance of a non-negative integer.
    """

    if detector_n < 2:
        raise ValueError("detector_n must be at least two")
    dimensions: list[int] = []
    for momentum in range(detector_n):
        projected = sum(
            np.exp(-2j * np.pi * momentum * shift / detector_n)
            * (2 ** math.gcd(detector_n, shift))
            for shift in range(detector_n)
        ) / detector_n
        rounded = int(round(float(projected.real)))
        if (
            rounded < 0
            or abs(float(projected.real) - rounded) > 1.0e-7
            or abs(float(projected.imag)) > 1.0e-7
        ):
            raise RuntimeError(
                "cyclic character projection did not produce an integer "
                f"for N={detector_n}, momentum={momentum}: {projected}"
            )
        dimensions.append(rounded)
    if sum(dimensions) != 2**detector_n:
        raise RuntimeError("translation-sector dimensions do not reconstruct the Hilbert space")
    return tuple(dimensions)


def split_concatenated_translation_roots(
    eigenvalues: np.ndarray,
    detector_n: int,
) -> tuple[TranslationRootSector, ...]:
    """Split roots concatenated in increasing QuSpin momentum-block order."""

    values = np.asarray(eigenvalues, dtype=np.complex128)
    if values.ndim != 1:
        raise ValueError("eigenvalues must be one-dimensional")
    dimensions = cyclic_translation_multiplicities(detector_n)
    expected = sum(dimensions)
    if values.size != expected:
        raise ValueError(f"received {values.size} roots, expected {expected}")
    sectors: list[TranslationRootSector] = []
    offset = 0
    for momentum, dimension in enumerate(dimensions):
        stop = offset + dimension
        sectors.append(
            TranslationRootSector(
                momentum_index=momentum,
                detector_n=detector_n,
                eigenvalues=values[offset:stop],
            )
        )
        offset = stop
    return tuple(sectors)


def nonredundant_momentum_roots(
    sectors: tuple[TranslationRootSector, ...],
) -> tuple[tuple[tuple[int, ...], np.ndarray], ...]:
    """Return ``k``/``-k`` pairs, with self-conjugate momenta left single.

    Reflection relates the two members of a generic pair.  Concatenating them
    retains their physical multiplicity and improves histogram statistics.
    No reflection-parity split is inferred at self-conjugate momentum because
    archived eigenvalues alone do not contain the corresponding eigenvectors.
    """

    if not sectors:
        raise ValueError("sectors must not be empty")
    detector_n = sectors[0].detector_n
    if len(sectors) != detector_n or any(
        sector.detector_n != detector_n or sector.momentum_index != index
        for index, sector in enumerate(sectors)
    ):
        raise ValueError("sectors must contain every momentum in increasing order")
    output: list[tuple[tuple[int, ...], np.ndarray]] = [
        ((0,), sectors[0].eigenvalues)
    ]
    for momentum in range(1, detector_n // 2 + 1):
        partner = (-momentum) % detector_n
        if partner == momentum:
            output.append(((momentum,), sectors[momentum].eigenvalues))
        else:
            output.append(
                (
                    (momentum, partner),
                    np.concatenate(
                        (sectors[momentum].eigenvalues, sectors[partner].eigenvalues)
                    ),
                )
            )
    return tuple(output)
