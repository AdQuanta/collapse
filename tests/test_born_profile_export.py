"""Independent identity, serialization, and graph-integrity export checks."""

import numpy as np
import pytest

from core.born_profile_export import (
    graph_tables, validate_profile, write_profile_tables,
)


def test_exact_born_density_and_roundtrip(tmp_path):
    edges = np.linspace(0, np.pi, 65)
    centers = (edges[:-1] + edges[1:]) / 2
    born = np.cos(centers / 2) ** 2
    arrays = dict(edges=edges, centers=centers, P=2 * born / np.pi,
                  P_reflected=2 * (1 - born) / np.pi, R=born,
                  Born=born, occupied=np.ones(64, dtype=bool))
    validate_profile(arrays, rmse=0)
    write_profile_tables(tmp_path, arrays)
    data = np.genfromtxt(tmp_path / "profile.dat", names=True)
    np.testing.assert_array_equal(data["P"], arrays["P"])
    steps = np.genfromtxt(tmp_path / "histogram_steps.dat", names=True)
    integral = np.sum(steps["P"][::2] * np.diff(steps["theta_rad"].reshape(-1, 2), axis=1).ravel())
    assert integral == pytest.approx(1)


def test_empty_ratio_is_exported_as_nan(tmp_path):
    arrays = dict(edges=np.linspace(0, np.pi, 5), centers=np.arange(4),
                  P=np.ones(4), P_reflected=np.ones(4), R=np.full(4, 0.5),
                  Born=np.full(4, 0.5), occupied=np.array([0, 1, 1, 0]))
    write_profile_tables(tmp_path, arrays)
    data = np.genfromtxt(tmp_path / "profile.dat", names=True)
    assert np.isnan(data["R"][[0, 3]]).all()


def test_ring_second_neighbors_and_central_edges():
    n = 17
    nodes, edges = graph_tables(n, dict(j=1, jpm=2, j2=3, jpm2=4), None,
                               family="ring_second_neighbor", jx_effective=0.1,
                               jy_effective=0)
    assert nodes.shape == (18, 4)
    for shell in (1, 2):
        bonds = edges[edges[:, 2] == shell, :2].astype(int)
        assert len(bonds) == n
        degree = np.bincount(bonds.ravel(), minlength=n)
        np.testing.assert_array_equal(degree, np.full(n, 2))
        distance = (bonds[:, 1] - bonds[:, 0]) % n
        assert np.isin(distance, [shell, n - shell]).all()
    assert (edges[edges[:, 2] == 0, 0] == n).all()


def test_saved_network_is_preserved_and_missing_edges_refused():
    graph = dict(nodes=5, edges_zero_based=[[0, 4], [2, 4], [1, 2]])
    args = dict(n=5, parameters=dict(j=1, jpm=0), family="erdos_renyi",
                jx_effective=0.2, jy_effective=0)
    _, edges = graph_tables(graph=graph, **args)
    np.testing.assert_array_equal(edges[edges[:, 2] == 1, :2], [[0, 4], [1, 2], [2, 4]])
    with pytest.raises(ValueError, match="saved edge list"):
        graph_tables(graph=None, **args)
