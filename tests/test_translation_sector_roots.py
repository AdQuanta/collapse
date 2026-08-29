"""Checks for recovering momentum-resolved projective roots."""

from __future__ import annotations

import numpy as np

from core.translation_sector_roots import (
    cyclic_translation_multiplicities,
    nonredundant_momentum_roots,
    split_concatenated_translation_roots,
)


def test_prime_n17_translation_dimensions_reconstruct_detector_space() -> None:
    dimensions = cyclic_translation_multiplicities(17)
    assert dimensions == (7712,) + (7710,) * 16
    assert sum(dimensions) == 2**17


def test_split_preserves_exact_concatenation_and_pairs_reflections() -> None:
    values = np.arange(2**5, dtype=float).astype(np.complex128)
    sectors = split_concatenated_translation_roots(values, detector_n=5)
    assert np.array_equal(np.concatenate([sector.eigenvalues for sector in sectors]), values)
    assert [sector.dimension for sector in sectors] == list(
        cyclic_translation_multiplicities(5)
    )

    paired = nonredundant_momentum_roots(sectors)
    assert [momenta for momenta, _ in paired] == [(0,), (1, 4), (2, 3)]
    assert sum(roots.size for _, roots in paired) == values.size


def test_even_ring_keeps_pi_momentum_unpaired() -> None:
    values = np.arange(2**4, dtype=float).astype(np.complex128)
    sectors = split_concatenated_translation_roots(values, detector_n=4)
    paired = nonredundant_momentum_roots(sectors)
    assert [momenta for momenta, _ in paired] == [(0,), (1, 3), (2,)]
