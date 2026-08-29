"""Graph construction and single-pixel Hamiltonian regression tests."""

from __future__ import annotations

import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

from core.analysis import (
    DisentanglementAnalyzer,
    prepare_sector_relative_evolution,
)
from core.detector_graphs import (
    DetectorGraphSpec,
    detector_graph_edges,
    detector_graph_metadata,
)
from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin


@pytest.mark.parametrize(
    ("kind", "overrides"),
    [
        ("erdos_renyi", {"erdos_renyi_p": 0.35}),
        ("watts_strogatz", {"watts_strogatz_k": 4, "watts_strogatz_p": 0.4}),
        ("barabasi_albert", {"barabasi_albert_m": 2}),
        ("random_regular", {"regular_degree": 4}),
    ],
)
def test_random_graphs_are_reproducible_connected_and_simple(
    kind: str, overrides: dict[str, float | int]
) -> None:
    spec = DetectorGraphSpec(kind=kind, seed=319, **overrides)
    edges = detector_graph_edges(12, spec)

    assert edges == detector_graph_edges(12, spec)
    assert len(edges) == len(set(edges))
    assert all(0 <= left < right < 12 for left, right in edges)
    assert detector_graph_metadata(12, spec)["connected"] is True


def test_graph_family_structural_contracts() -> None:
    complete = detector_graph_edges(
        7, DetectorGraphSpec(kind="erdos_renyi", seed=1, erdos_renyi_p=1.0)
    )
    assert len(complete) == 7 * 6 // 2

    watts = detector_graph_edges(
        12,
        DetectorGraphSpec(
            kind="watts_strogatz", seed=2, watts_strogatz_k=4,
            watts_strogatz_p=0.7,
        ),
    )
    assert len(watts) == 12 * 4 // 2

    barabasi = detector_graph_edges(
        12, DetectorGraphSpec(kind="barabasi_albert", seed=3, barabasi_albert_m=2)
    )
    assert len(barabasi) == 3 + 2 * (12 - 3)

    regular_spec = DetectorGraphSpec(
        kind="expander", seed=4, regular_degree=4
    )
    regular_metadata = detector_graph_metadata(12, regular_spec)
    assert regular_metadata["canonical_kind"] == "random_regular"
    assert regular_metadata["degree_sequence"] == [4] * 12
    assert regular_metadata["laplacian_algebraic_connectivity"] > 0.0


@pytest.mark.parametrize(
    "spec",
    [
        DetectorGraphSpec(kind="erdos_renyi", seed=11, erdos_renyi_p=0.5),
        DetectorGraphSpec(
            kind="watts_strogatz", seed=12, watts_strogatz_k=2,
            watts_strogatz_p=0.5,
        ),
        DetectorGraphSpec(kind="barabasi_albert", seed=13, barabasi_albert_m=2),
        DetectorGraphSpec(kind="random_regular", seed=14, regular_degree=2),
    ],
)
def test_numpy_and_quspin_graph_hamiltonians_match(spec: DetectorGraphSpec) -> None:
    parameters = dict(
        N_pixel=5,
        J=0.73,
        Jpm=0.29,
        Jx=0.08,
        hz=0.17,
        hz0=0.0,
        connectivity=spec.kind,
        graph_spec=spec,
        central_coupling="all",
    )
    dense_numpy = SinglePixelHamiltonianNumpy(**parameters).generate()
    dense_quspin = SinglePixelHamiltonianQuSpin(
        **parameters, use_symmetry=True
    ).generate()

    np.testing.assert_allclose(dense_quspin, dense_numpy, rtol=0.0, atol=1.0e-12)
    np.testing.assert_allclose(
        dense_quspin, dense_quspin.conj().T, rtol=0.0, atol=1.0e-12
    )


def test_non_circular_graph_uses_only_exact_magnetization_parity() -> None:
    model = SinglePixelHamiltonianQuSpin(
        N_pixel=5,
        J=0.7,
        Jpm=0.3,
        Jx=0.04,
        hz=0.1,
        hz0=0.0,
        connectivity="barabasi_albert",
        graph_spec=DetectorGraphSpec(
            kind="barabasi_albert", seed=17, barabasi_albert_m=2
        ),
        central_coupling="all",
        use_symmetry=True,
    )
    sectors = model.diagonalize_sectors()

    assert len(sectors) == 2
    assert {sector["symmetry_label"] for sector in sectors} == {
        "magnetization_parity"
    }
    assert sum(len(sector["E"]) for sector in sectors) == 2**6
    assert all(not sector["relative_evolution_local"] for sector in sectors)


def test_parity_sector_relative_spectrum_matches_full_diagonalization() -> None:
    parameters = dict(
        N_pixel=4,
        J=0.7,
        Jpm=0.3,
        Jx=0.04,
        hz=0.1,
        hz0=0.0,
        connectivity="barabasi_albert",
        graph_spec=DetectorGraphSpec(
            kind="barabasi_albert", seed=29, barabasi_albert_m=2
        ),
        central_coupling="all",
    )
    sector_model = SinglePixelHamiltonianQuSpin(**parameters, use_symmetry=True)
    full_model = SinglePixelHamiltonianQuSpin(**parameters, use_symmetry=False)
    sectors = sector_model.diagonalize_sectors()
    sector_values = DisentanglementAnalyzer.from_sectors(sectors, 17.0, 5).D0
    prepared_values = prepare_sector_relative_evolution(sectors, 5).eigenvalues(17.0)
    full_values = DisentanglementAnalyzer.from_sectors(
        full_model.diagonalize_sectors(), 17.0, 5
    ).D0

    distances = np.abs(sector_values[:, None] - full_values[None, :])
    rows, columns = linear_sum_assignment(distances)
    assert float(np.max(distances[rows, columns])) < 1.0e-10
    prepared_distances = np.abs(sector_values[:, None] - prepared_values[None, :])
    rows, columns = linear_sum_assignment(prepared_distances)
    assert float(np.max(prepared_distances[rows, columns])) < 1.0e-12


def test_invalid_graph_parameters_fail_explicitly() -> None:
    with pytest.raises(ValueError, match="even"):
        detector_graph_edges(
            12,
            DetectorGraphSpec(
                kind="watts_strogatz", watts_strogatz_k=3
            ),
        )
    with pytest.raises(ValueError, match="must be even"):
        detector_graph_edges(
            11,
            DetectorGraphSpec(kind="random_regular", regular_degree=3),
        )
