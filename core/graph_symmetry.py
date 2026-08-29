"""Exact permutation symmetries of small detector interaction graphs.

The routines here are intentionally limited to the small simple graphs used by
the single-pixel detector studies.  A symmetry is represented by a tuple
``permutation`` with ``permutation[i]`` equal to the image of node ``i``.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def graph_automorphisms(
    n_nodes: int,
    edges: Iterable[tuple[int, int]],
    *,
    max_automorphisms: int = 100_000,
) -> tuple[tuple[int, ...], ...]:
    """Enumerate all adjacency-preserving node permutations exactly.

    Iterative color refinement restricts candidate images before a
    backtracking isomorphism search.  This is suitable for the detector graphs
    in this repository (currently at most 12 nodes), but is not intended as a
    replacement for a general-purpose graph-isomorphism package.
    """

    if n_nodes < 1:
        raise ValueError("n_nodes must be positive")
    if max_automorphisms < 1:
        raise ValueError("max_automorphisms must be positive")
    adjacency = np.zeros((n_nodes, n_nodes), dtype=np.bool_)
    for raw_left, raw_right in edges:
        left, right = int(raw_left), int(raw_right)
        if not (0 <= left < n_nodes and 0 <= right < n_nodes):
            raise ValueError("edge endpoint lies outside the graph")
        if left == right:
            raise ValueError("self-edges are not allowed")
        adjacency[left, right] = True
        adjacency[right, left] = True

    colors = np.sum(adjacency, axis=1).astype(np.int64)
    while True:
        signatures = [
            (
                int(colors[node]),
                tuple(sorted(int(colors[neighbor]) for neighbor in np.flatnonzero(adjacency[node]))),
            )
            for node in range(n_nodes)
        ]
        unique = {signature: index for index, signature in enumerate(sorted(set(signatures)))}
        refined = np.asarray([unique[signature] for signature in signatures], dtype=np.int64)
        if np.array_equal(refined, colors):
            break
        colors = refined

    mapping = np.full(n_nodes, -1, dtype=np.int64)
    used = np.zeros(n_nodes, dtype=np.bool_)
    automorphisms: list[tuple[int, ...]] = []
    color_sizes = {
        int(color): int(np.count_nonzero(colors == color)) for color in np.unique(colors)
    }
    source_order: list[int] = []
    remaining = set(range(n_nodes))
    while remaining:
        source = min(
            remaining,
            key=lambda node: (
                -sum(bool(adjacency[node, chosen]) for chosen in source_order),
                color_sizes[int(colors[node])],
                -int(np.sum(adjacency[node])),
                node,
            ),
        )
        source_order.append(source)
        remaining.remove(source)

    def candidates(source: int) -> list[int]:
        result = []
        assigned = np.flatnonzero(mapping >= 0)
        for target in np.flatnonzero((colors == colors[source]) & ~used):
            if all(
                adjacency[source, other] == adjacency[int(target), mapping[other]]
                for other in assigned
            ):
                result.append(int(target))
        return result

    def search(depth: int) -> None:
        if len(automorphisms) > max_automorphisms:
            raise RuntimeError(
                f"graph has more than {max_automorphisms} automorphisms"
            )
        if depth == n_nodes:
            automorphisms.append(tuple(int(value) for value in mapping))
            return
        source = source_order[depth]
        candidate_targets = candidates(source)
        for target in candidate_targets:
            mapping[source] = target
            used[target] = True
            search(depth + 1)
            used[target] = False
            mapping[source] = -1

    search(0)
    identity = tuple(range(n_nodes))
    if identity not in automorphisms:
        raise RuntimeError("automorphism search failed to recover the identity")
    return tuple(sorted(automorphisms))
