"""Tests for exact detector-graph permutation symmetries."""

from __future__ import annotations

from core.graph_symmetry import graph_automorphisms


def test_path_and_cycle_automorphism_counts() -> None:
    path_edges = ((0, 1), (1, 2), (2, 3), (3, 4))
    cycle_edges = tuple((node, (node + 1) % 6) for node in range(6))

    assert len(graph_automorphisms(5, path_edges)) == 2
    assert len(graph_automorphisms(6, cycle_edges)) == 12


def test_asymmetric_graph_has_only_identity() -> None:
    edges = ((0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (5, 6))
    assert graph_automorphisms(7, edges) == (tuple(range(7)),)

