"""Validation of symmetry-sector relative-evolution pencils."""

import numpy as np

from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.relative_evolution_pencil import matched_projective_angle_error
from core.relative_evolution_sector import (
    generalized_relative_evolution_from_eigenbasis,
    generalized_relative_evolution_from_sectors,
)


def test_translation_sector_pencils_match_full_basis() -> None:
    detector_n = 4
    hamiltonian = SinglePixelHamiltonianQuSpin(
        N_pixel=detector_n,
        J=1.0,
        Jpm=0.2,
        Jx=0.01 / np.sqrt(detector_n),
        Jy=0.0,
        Jz=0.0,
        Jzx=0.0,
        hx=0.0,
        hz=0.3,
        hx0=0.0,
        hz0=0.1,
        connectivity="ring",
        central_coupling="all",
        seed=44,
        use_symmetry=True,
    )
    energies, vectors = np.linalg.eigh(hamiltonian.generate())
    full, full_isometry = generalized_relative_evolution_from_eigenbasis(
        energies, vectors, 3.7
    )
    sector = generalized_relative_evolution_from_sectors(
        hamiltonian.diagonalize_sectors(),
        3.7,
        detector_n + 1,
        compare_direct=True,
    )
    maximum, rms = matched_projective_angle_error(full.theta, sector.theta)

    assert sum(sector.detector_block_dimensions) == 2**detector_n
    assert maximum < 1.0e-11
    assert rms < 1.0e-12
    assert full.maximum_homogeneous_residual < 1.0e-12
    assert sector.maximum_homogeneous_residual < 1.0e-12
    assert full_isometry < 1.0e-12
    assert sector.maximum_column_isometry_residual < 1.0e-12
    assert sector.direct_comparison_sectors == detector_n
    assert sector.maximum_direct_angle_error < 1.0e-11
