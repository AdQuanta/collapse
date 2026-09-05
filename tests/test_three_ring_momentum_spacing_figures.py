"""Regression checks for the three N=17 ring spacing figures."""

from __future__ import annotations

import numpy as np

from scripts.build_three_ring_momentum_spacing_figures import (
    DEFAULT_CASES,
    HamiltonianParameters,
    _detector_static,
    _load_case,
    select_largest_sectors,
)

from conftest import requires_paths


# Only this test reads stored campaign output; the sector-decomposition test
# below is self-contained and must keep running in a bare checkout.
@requires_paths("work/zeus_top20_last5_largerN_20260810_001532")
def test_attached_n17_diagnostics_are_identified_exactly() -> None:
    loaded = [_load_case(case) for case in DEFAULT_CASES]
    scores = [provenance["N17_S_born"] for _, provenance in loaded]
    np.testing.assert_allclose(
        scores,
        [0.931630323600632, 0.59461470959228, 0.929556803337872],
        rtol=0.0,
        atol=1.0e-15,
    )
    assert loaded[0][0].j2 == loaded[0][0].jpm2 == 0.0
    assert loaded[1][0].j == 0.0
    np.testing.assert_allclose(
        [loaded[2][0].j2, loaded[2][0].jpm2],
        [0.16899859316711222, 0.26453375989687394],
        rtol=0.0,
        atol=1.0e-15,
    )


def test_n17_largest_sector_dimensions_match_dihedral_decomposition() -> None:
    selected = select_largest_sectors(17)
    assert list(selected) == list(range(9))
    assert [(item.n_up, item.reflection_parity, item.dimension) for item in selected[0]] == [
        (8, 1, 750),
        (8, -1, 680),
        (7, 1, 600),
        (7, -1, 544),
        (6, 1, 392),
    ]
    assert [(item.n_up, item.dimension) for item in selected[1]] == [
        (8, 1430),
        (7, 1144),
        (6, 728),
        (5, 364),
        (4, 140),
    ]


def test_even_n_omits_half_filling_and_resolves_both_reflection_momenta() -> None:
    selected = select_largest_sectors(6)
    assert list(selected) == [0, 1, 2, 3]
    assert all(item.n_up < 3 for sectors in selected.values() for item in sectors)
    assert {item.reflection_parity for item in selected[0]} <= {-1, 1}
    assert {item.reflection_parity for item in selected[3]} <= {-1, 1}
    assert all(
        item.reflection_parity is None
        for momentum in (1, 2)
        for item in selected[momentum]
    )


def test_second_neighbor_static_terms_use_simulation_sign_convention() -> None:
    parameters = HamiltonianParameters(hz=0.3, j=0.2, jpm=0.1, j2=0.4, jpm2=0.5)
    static = _detector_static(7, parameters)
    by_operator: dict[str, list[list[list[float | int]]]] = {}
    for operator, couplings in static:
        by_operator.setdefault(operator, []).append(couplings)
    assert by_operator["zz"][0][0] == [-0.2, 0, 1]
    assert by_operator["zz"][1][0] == [-0.4, 0, 2]
    assert by_operator["+-"][0][0] == [-0.025, 0, 1]
    assert by_operator["+-"][1][0] == [-0.125, 0, 2]
    assert by_operator["z"][0][0] == [-0.3, 0]
