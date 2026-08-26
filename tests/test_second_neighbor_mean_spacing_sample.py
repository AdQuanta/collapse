"""Checks for the second-neighbor detector and revised Vab histogram."""

from __future__ import annotations

import numpy as np

from collapse.detector_resonance import (
    DenseRingDetectorBuilder,
    DetectorSpec,
    _ring_bonds,
)
from examples.build_second_neighbor_mean_spacing_sample_2x3 import (
    mean_spacing_gap_weight_data,
    mean_spacing_resonance_weight_data,
)
from examples.build_sobol_flat_ranked_1x6_by_n import SpectralData
from examples.build_sobol_flat_ranked_1x6_by_n import CaseRecord, compute_spectral


def test_second_neighbor_detector_bonds_are_not_double_counted() -> None:
    assert len(_ring_bonds(8, step=1)) == 8
    assert len(_ring_bonds(8, step=2)) == 8
    assert _ring_bonds(4, step=2) == ((0, 2), (1, 3))


def test_second_neighbor_terms_change_a_hermitian_detector_matrix() -> None:
    builder = DenseRingDetectorBuilder()
    base = builder.build(DetectorSpec(5, hz=0.1, j=0.2, jpm=0.3))
    extended = builder.build(
        DetectorSpec(5, hz=0.1, j=0.2, jpm=0.3, j2=0.4, jpm2=0.5)
    )

    assert not np.allclose(base.hamiltonian, extended.hamiltonian)
    np.testing.assert_allclose(
        extended.hamiltonian,
        extended.hamiltonian.T,
        rtol=0.0,
        atol=1.0e-12,
    )
    assert extended.hamiltonian[0, 0] - base.hamiltonian[0, 0] == 5 * 0.4


def test_vab_gap_histogram_uses_resolved_mean_spacing() -> None:
    energies = np.asarray([0.0, 0.0, 2.0, 5.0])
    spectral = SpectralData(
        energies=energies,
        normalized_gaps=np.abs(energies[:, None] - energies[None, :]) / 5.0,
        vab_power=np.full((4, 4), 1.0 / 16.0),
        multiplicities=(2, 1, 1),
        multiplicity_two_pairs=np.asarray([[0, 1]], dtype=np.int64),
        multiplicity_two_couplings=np.zeros((1, 3)),
        degeneracy_tolerance=1.0e-9,
        validation={},
    )

    data = mean_spacing_gap_weight_data(spectral)

    assert data["resolved_level_count"] == 3
    assert data["resolved_spacing_count"] == 2
    assert data["mean_spacing"] == 2.5
    assert data["maximum_normalized_gap"] == 2.0
    assert np.all(data["edges"] > 0.0)
    np.testing.assert_allclose(
        data["edges"][1:] / data["edges"][:-1],
        np.full(40, data["edges"][1] / data["edges"][0]),
        rtol=1.0e-13,
        atol=0.0,
    )
    assert data["exact"] == 6.0 / 16.0
    assert abs(data["sum"] - 1.0) < 1.0e-15
    assert abs(data["exact"] + np.sum(data["weights"]) - 1.0) < 1.0e-15


def test_magnetization_sector_spectrum_matches_dense_diagonalization() -> None:
    record = CaseRecord(
        family="jy_zero",
        dynamics_n=14,
        config_id="sector-check",
        s_born=0.0,
        born_rmse=0.0,
        hz=0.07,
        j=0.13,
        jpm=0.11,
        jx=0.02,
        jy=0.0,
        source_dir="",
        j2=0.17,
        jpm2=0.19,
    )
    dense = compute_spectral(record, detector_n=6)
    sector = compute_spectral(
        record,
        detector_n=6,
        exploit_magnetization=True,
    )

    np.testing.assert_allclose(sector.energies, dense.energies, rtol=0.0, atol=1e-12)
    dense_histogram = mean_spacing_gap_weight_data(dense)
    sector_histogram = mean_spacing_gap_weight_data(sector)
    np.testing.assert_allclose(
        sector_histogram["edges"], dense_histogram["edges"], rtol=1e-12, atol=1e-12
    )
    np.testing.assert_allclose(
        sector_histogram["weights"],
        dense_histogram["weights"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        sector_histogram["exact"], dense_histogram["exact"], rtol=0.0, atol=1e-12
    )
    assert sector.validation["magnetization_sectors_exploited"] is True


def test_resonance_histogram_uses_detuning_from_twice_hz0() -> None:
    energies = np.asarray([0.0, 0.2, 0.5])
    spectral = SpectralData(
        energies=energies,
        normalized_gaps=np.abs(energies[:, None] - energies[None, :]) / 0.5,
        vab_power=np.full((3, 3), 1.0 / 9.0),
        multiplicities=(1, 1, 1),
        multiplicity_two_pairs=np.empty((0, 2), dtype=np.int64),
        multiplicity_two_couplings=np.empty((0, 3)),
        degeneracy_tolerance=1.0e-9,
        validation={},
    )

    data = mean_spacing_resonance_weight_data(spectral, hz0=0.1)

    assert data["target_gap"] == 0.2
    assert data["mean_spacing"] == 0.25
    assert data["exact"] == 2.0 / 9.0
    assert np.all(data["edges"] > 0.0)
    np.testing.assert_allclose(
        data["edges"][1:] / data["edges"][:-1],
        np.full(40, data["edges"][1] / data["edges"][0]),
        rtol=1.0e-13,
        atol=0.0,
    )
    assert abs(data["exact"] + np.sum(data["weights"]) - 1.0) < 1.0e-15
