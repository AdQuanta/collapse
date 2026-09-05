"""Tests for the hz0=0 spacing/Born diagnostic-atlas builder."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts.plot_hz0_0_ring_spacing_born_catalog import (
    _density,
    _spacing_histograms,
    parser,
)


def test_histogram_only_spacing_archive_round_trip(tmp_path: Path) -> None:
    edges = np.linspace(0.0, 4.0, 5)
    sectors = np.asarray([[1, 2, 3, 4], [4, 3, 2, 1]], dtype=np.int64)
    path = tmp_path / "histograms.npz"
    np.savez_compressed(
        path,
        bin_edges=edges,
        sector_histogram_counts=sectors,
        pooled_histogram_counts=np.sum(sectors, axis=0),
    )

    loaded_sectors, pooled = _spacing_histograms(path, edges=edges)

    np.testing.assert_array_equal(loaded_sectors, sectors)
    np.testing.assert_array_equal(pooled, np.sum(sectors, axis=0))
    assert np.isclose(np.sum(_density(pooled, edges) * np.diff(edges)), 1.0)


def test_unfolded_spacing_archive_is_histogrammed_per_sector(tmp_path: Path) -> None:
    edges = np.linspace(0.0, 4.0, 5)
    path = tmp_path / "spectra.npz"
    np.savez_compressed(
        path,
        sector_a__unfolded_spacings=np.asarray([0.2, 1.2, 1.8]),
        sector_b__unfolded_spacings=np.asarray([2.1, 3.9]),
        ignored=np.asarray([99.0]),
    )

    sectors, pooled = _spacing_histograms(path, edges=edges)

    np.testing.assert_array_equal(sectors, [[1, 2, 0, 0], [0, 0, 1, 1]])
    np.testing.assert_array_equal(pooled, [1, 2, 1, 1])


def test_parser_accepts_selected_individual_categories(tmp_path: Path) -> None:
    args = parser().parse_args(
        [
            "--output",
            str(tmp_path / "figures"),
            "--category",
            "wd_clearly_nonborn",
            "--category",
            "poisson_clearly_nonborn",
            "--individual",
        ]
    )

    assert args.individual
    assert args.category == ["wd_clearly_nonborn", "poisson_clearly_nonborn"]
