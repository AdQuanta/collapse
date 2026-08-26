"""Scientific contracts for detector graph symmetry-sector spectra."""

from __future__ import annotations

import math

from collapse.graph_spectral_sectors import largest_detector_symmetry_sectors


def test_asymmetric_graph_sectors_reduce_only_by_hamming_weight() -> None:
    edges = ((0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (5, 6))
    sectors, validation = largest_detector_symmetry_sectors(
        7, edges, hz=0.31, j=0.77, jpm=0.23, count=3
    )

    assert validation["automorphism_group_order"] == 1
    assert [sector.dimension for sector in sectors] == [
        math.comb(7, 3),
        math.comb(7, 2),
        math.comb(7, 1),
    ]


def test_path_graph_is_split_by_reflection_parity() -> None:
    edges = ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5))
    sectors, validation = largest_detector_symmetry_sectors(
        6, edges, hz=0.19, j=0.83, jpm=0.37
    )

    assert validation["automorphism_group_order"] == 2
    assert validation["half_filling_spin_reversal_resolved"] is True
    for block in validation["blocks"].values():
        assert block["spectrum_union_max_abs"] < 1.0e-10
        assert block["invariant_subspace_residual_max_abs"] < 1.0e-10


def test_asymmetric_even_graph_splits_half_filling_by_spin_reversal() -> None:
    edges = (
        (0, 1),
        (0, 5),
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 3),
        (3, 4),
        (4, 5),
    )
    sectors, validation = largest_detector_symmetry_sectors(
        6, edges, hz=0.23, j=0.71, jpm=0.29, count=4
    )

    assert validation["automorphism_group_order"] == 1
    half_block = validation["blocks"]["weight_3"]
    assert half_block["spin_reversal_resolved"] is True
    assert half_block["total_symmetry_group_order"] == 2
    assert half_block["raw_sector_dimensions"] == [10, 10]
    half_sectors = [sector for sector in sectors if sector.hamming_weight == 3]
    assert {sector.dimension for sector in half_sectors} == {10}
    assert {sector.symmetry_label for sector in half_sectors} == {
        r"$N_\uparrow=3,\ f=+$",
        r"$N_\uparrow=3,\ f=-$",
    }


def test_twin_antisymmetric_sector_resolves_induced_graph_symmetry() -> None:
    # Nodes 5 and 6 are false twins attached to node 0.  Removing them leaves
    # the path 0-1-2-3-4, whose reflection is not an automorphism of the full
    # seven-node graph and therefore emerges only in the twin-odd sector.
    edges = (
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        (0, 5),
        (0, 6),
    )
    sectors, validation = largest_detector_symmetry_sectors(
        7, edges, hz=0.17, j=0.73, jpm=0.31, count=4
    )

    assert validation["automorphism_group_order"] == 2
    weight_three = validation["blocks"]["weight_3"]
    reduction = weight_three["twin_antisymmetric_reduction"]
    assert reduction["twin_pair_zero_based"] == [5, 6]
    assert reduction["reduced_automorphism_group_order"] == 2
    assert reduction["reduction_residual_max_abs"] < 1.0e-12
    assert sum(weight_three["raw_sector_dimensions"]) == math.comb(7, 3)
    assert 10 not in weight_three["nonredundant_sector_dimensions"]
    assert sorted(weight_three["nonredundant_sector_dimensions"]) == [4, 6, 25]
    assert weight_three["spectrum_union_max_abs"] < 1.0e-10
    assert any(r"p=-,\ \beta=" in sector.symmetry_label for sector in sectors)
