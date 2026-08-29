"""Second-neighbor ring Hamiltonian and symmetry regression tests."""

from __future__ import annotations

import numpy as np
import pytest

from core.hamiltonians.numpy_hamiltonians import (
    SinglePixelHamiltonianNumpy,
    _pixel_ring_second_neighbor_bonds,
)
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin


def test_second_neighbor_ring_bonds_are_distinct_and_undirected() -> None:
    bonds = _pixel_ring_second_neighbor_bonds(1, 14)
    expected = {
        tuple(sorted((1 + index, 1 + (index + 2) % 14)))
        for index in range(14)
    }
    assert len(bonds) == 14
    assert set(bonds) == expected
    assert _pixel_ring_second_neighbor_bonds(1, 4) == [(1, 3), (2, 4)]
    assert _pixel_ring_second_neighbor_bonds(1, 2) == []


def test_second_neighbor_numpy_and_quspin_matrices_match() -> None:
    parameters = dict(
        N_pixel=4,
        J=0.7,
        Jpm=0.3,
        J2=0.23,
        Jpm2=0.17,
        Jx=0.04,
        hz=0.11,
        hz0=0.0,
        connectivity="ring",
        central_coupling="all",
        use_symmetry=True,
    )
    numpy_parameters = {key: value for key, value in parameters.items() if key != "use_symmetry"}
    dense_numpy = SinglePixelHamiltonianNumpy(**numpy_parameters).generate()
    quspin = SinglePixelHamiltonianQuSpin(**parameters)
    dense_quspin = quspin.generate()

    np.testing.assert_allclose(dense_quspin, dense_numpy, rtol=0.0, atol=1.0e-12)
    np.testing.assert_allclose(dense_quspin, dense_quspin.conj().T, rtol=0.0, atol=1.0e-12)


def test_second_neighbor_model_keeps_translation_sector_diagonalization() -> None:
    detector_n = 4
    model = SinglePixelHamiltonianQuSpin(
        N_pixel=detector_n,
        J=0.7,
        Jpm=0.3,
        J2=0.23,
        Jpm2=0.17,
        Jx=0.04,
        hz=0.11,
        hz0=0.0,
        connectivity="ring",
        central_coupling="all",
        use_symmetry=True,
    )
    sectors = model.diagonalize_sectors()

    assert len(sectors) == detector_n
    assert sum(len(sector["E"]) for sector in sectors) == 2 ** (detector_n + 1)
    assert {sector["symmetry_label"] for sector in sectors} == {"pixel_shift"}
    assert all(sector["relative_evolution_local"] for sector in sectors)


@pytest.mark.parametrize("implementation", [SinglePixelHamiltonianNumpy, SinglePixelHamiltonianQuSpin])
def test_second_neighbor_terms_require_ring_connectivity(implementation) -> None:
    with pytest.raises(ValueError, match="only for ring"):
        implementation(N_pixel=4, connectivity="chain", J2=0.1)
