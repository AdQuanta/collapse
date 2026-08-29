"""Deterministic interaction graphs for single-pixel detectors.

The graph only selects detector pairs.  Hamiltonian coefficients remain the
responsibility of the Hamiltonian backend: every returned edge receives the
same ``J`` ZZ term and ``Jpm`` exchange term for a given configuration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable

import numpy as np


LEGACY_CONNECTIVITIES = frozenset({"chain", "ring", "all_to_all"})
RANDOM_CONNECTIVITIES = frozenset(
    {"erdos_renyi", "watts_strogatz", "barabasi_albert", "random_regular"}
)
VALID_CONNECTIVITIES = LEGACY_CONNECTIVITIES | RANDOM_CONNECTIVITIES | {"expander"}


@dataclass(frozen=True)
class DetectorGraphSpec:
    """Parameters defining one detector interaction graph realization.

    ``expander`` is accepted as an alias for ``random_regular``.  A random
    regular graph is an expander candidate; expansion is not assumed without
    checking its recorded Laplacian spectral gap.
    """

    kind: str = "ring"
    seed: int = 0
    erdos_renyi_p: float = 0.3
    watts_strogatz_k: int = 4
    watts_strogatz_p: float = 0.3
    barabasi_albert_m: int = 2
    regular_degree: int = 4
    require_connected: bool = True
    max_attempts: int = 10_000

    @property
    def canonical_kind(self) -> str:
        return "random_regular" if self.kind == "expander" else self.kind

    def validate(self, n_nodes: int) -> None:
        if self.kind not in VALID_CONNECTIVITIES:
            raise ValueError(
                f"unknown detector connectivity {self.kind!r}; "
                f"choose from {sorted(VALID_CONNECTIVITIES)}"
            )
        if n_nodes < 1:
            raise ValueError("n_nodes must be positive")
        if not isinstance(self.seed, int) or self.seed < 0:
            raise ValueError("graph seed must be a nonnegative integer")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if self.canonical_kind == "erdos_renyi" and not (
            0.0 <= self.erdos_renyi_p <= 1.0
        ):
            raise ValueError("erdos_renyi_p must lie in [0,1]")
        if self.canonical_kind == "watts_strogatz":
            if not (0.0 <= self.watts_strogatz_p <= 1.0):
                raise ValueError("watts_strogatz_p must lie in [0,1]")
            if (
                self.watts_strogatz_k < 2
                or self.watts_strogatz_k >= n_nodes
                or self.watts_strogatz_k % 2
            ):
                raise ValueError(
                    "watts_strogatz_k must be even and satisfy 2 <= k < n_nodes"
                )
        if self.canonical_kind == "barabasi_albert" and not (
            1 <= self.barabasi_albert_m < n_nodes
        ):
            raise ValueError("barabasi_albert_m must satisfy 1 <= m < n_nodes")
        if self.canonical_kind == "random_regular":
            degree = self.regular_degree
            if not (1 <= degree < n_nodes):
                raise ValueError("regular_degree must satisfy 1 <= d < n_nodes")
            if n_nodes * degree % 2:
                raise ValueError("n_nodes * regular_degree must be even")
            if self.require_connected and degree < 2 and n_nodes > 2:
                raise ValueError("a connected regular graph with n_nodes > 2 needs d >= 2")


def _canonical_edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("self-edges are not allowed")
    return (left, right) if left < right else (right, left)


def _is_connected(n_nodes: int, edges: Iterable[tuple[int, int]]) -> bool:
    if n_nodes <= 1:
        return True
    adjacency = [[] for _ in range(n_nodes)]
    for left, right in edges:
        adjacency[left].append(right)
        adjacency[right].append(left)
    seen = {0}
    stack = [0]
    while stack:
        node = stack.pop()
        for neighbor in adjacency[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == n_nodes


def _erdos_renyi_edges(
    n_nodes: int, spec: DetectorGraphSpec, rng: np.random.Generator
) -> set[tuple[int, int]]:
    for _ in range(spec.max_attempts):
        edges = {
            (left, right)
            for left in range(n_nodes)
            for right in range(left + 1, n_nodes)
            if rng.random() < spec.erdos_renyi_p
        }
        if not spec.require_connected or _is_connected(n_nodes, edges):
            return edges
    raise RuntimeError(
        "failed to sample a connected Erdos-Renyi graph; increase p or max_attempts"
    )


def _watts_strogatz_once(
    n_nodes: int, spec: DetectorGraphSpec, rng: np.random.Generator
) -> set[tuple[int, int]]:
    half = spec.watts_strogatz_k // 2
    edges = {
        _canonical_edge(node, (node + offset) % n_nodes)
        for node in range(n_nodes)
        for offset in range(1, half + 1)
    }
    for node in range(n_nodes):
        for offset in range(1, half + 1):
            neighbor = (node + offset) % n_nodes
            old_edge = _canonical_edge(node, neighbor)
            if rng.random() >= spec.watts_strogatz_p:
                continue
            candidates = [
                target
                for target in range(n_nodes)
                if target != node and _canonical_edge(node, target) not in edges
            ]
            if not candidates:
                continue
            edges.remove(old_edge)
            target = int(rng.choice(candidates))
            edges.add(_canonical_edge(node, target))
    return edges


def _watts_strogatz_edges(
    n_nodes: int, spec: DetectorGraphSpec, rng: np.random.Generator
) -> set[tuple[int, int]]:
    for _ in range(spec.max_attempts):
        edges = _watts_strogatz_once(n_nodes, spec, rng)
        if not spec.require_connected or _is_connected(n_nodes, edges):
            return edges
    raise RuntimeError("failed to sample a connected Watts-Strogatz graph")


def _barabasi_albert_edges(
    n_nodes: int, spec: DetectorGraphSpec, rng: np.random.Generator
) -> set[tuple[int, int]]:
    m = spec.barabasi_albert_m
    initial = m + 1
    edges = {
        (left, right)
        for left in range(initial)
        for right in range(left + 1, initial)
    }
    degrees = np.full(initial, m, dtype=float)
    for node in range(initial, n_nodes):
        probabilities = degrees / np.sum(degrees)
        targets = np.asarray(
            rng.choice(node, size=m, replace=False, p=probabilities), dtype=int
        )
        for target in targets:
            edges.add((int(target), node))
        degrees[targets] += 1.0
        degrees = np.append(degrees, float(m))
    return edges


def _random_regular_edges(
    n_nodes: int, spec: DetectorGraphSpec, rng: np.random.Generator
) -> set[tuple[int, int]]:
    degree = spec.regular_degree
    stubs_template = np.repeat(np.arange(n_nodes, dtype=int), degree)
    for _ in range(spec.max_attempts):
        stubs = rng.permutation(stubs_template)
        edges: set[tuple[int, int]] = set()
        valid = True
        for left, right in stubs.reshape(-1, 2):
            if left == right:
                valid = False
                break
            edge = _canonical_edge(int(left), int(right))
            if edge in edges:
                valid = False
                break
            edges.add(edge)
        if valid and (not spec.require_connected or _is_connected(n_nodes, edges)):
            return edges
    raise RuntimeError(
        "failed to sample a simple random regular graph; increase max_attempts"
    )


def detector_graph_edges(
    n_nodes: int, spec: DetectorGraphSpec
) -> tuple[tuple[int, int], ...]:
    """Return sorted zero-based, distinct undirected detector edges."""

    spec.validate(n_nodes)
    kind = spec.canonical_kind
    if kind == "chain":
        edges = {(node, node + 1) for node in range(n_nodes - 1)}
    elif kind == "ring":
        edges = {
            _canonical_edge(node, (node + 1) % n_nodes)
            for node in range(n_nodes)
            if n_nodes > 1
        }
    elif kind == "all_to_all":
        edges = {
            (left, right)
            for left in range(n_nodes)
            for right in range(left + 1, n_nodes)
        }
    else:
        rng = np.random.default_rng(spec.seed)
        if kind == "erdos_renyi":
            edges = _erdos_renyi_edges(n_nodes, spec, rng)
        elif kind == "watts_strogatz":
            edges = _watts_strogatz_edges(n_nodes, spec, rng)
        elif kind == "barabasi_albert":
            edges = _barabasi_albert_edges(n_nodes, spec, rng)
        elif kind == "random_regular":
            edges = _random_regular_edges(n_nodes, spec, rng)
        else:  # pragma: no cover - guarded by validate
            raise AssertionError(kind)
    return tuple(sorted(edges))


def offset_detector_edges(
    pixel_start: int, n_nodes: int, spec: DetectorGraphSpec
) -> list[tuple[int, int]]:
    """Return detector edges shifted into the full Hamiltonian indexing."""

    return [
        (pixel_start + left, pixel_start + right)
        for left, right in detector_graph_edges(n_nodes, spec)
    ]


def detector_graph_metadata(n_nodes: int, spec: DetectorGraphSpec) -> dict[str, object]:
    """Return reproducibility and basic spectral metadata for one graph."""

    edges = detector_graph_edges(n_nodes, spec)
    adjacency = np.zeros((n_nodes, n_nodes), dtype=float)
    for left, right in edges:
        adjacency[left, right] = adjacency[right, left] = 1.0
    degrees = np.sum(adjacency, axis=1).astype(int)
    laplacian = np.diag(degrees) - adjacency
    eigenvalues = np.linalg.eigvalsh(laplacian)
    algebraic_connectivity = float(eigenvalues[1]) if n_nodes > 1 else 0.0
    return {
        "spec": asdict(spec),
        "canonical_kind": spec.canonical_kind,
        "nodes": n_nodes,
        "edge_count": len(edges),
        "edges_zero_based": [list(edge) for edge in edges],
        "degree_sequence": degrees.tolist(),
        "connected": _is_connected(n_nodes, edges),
        "laplacian_algebraic_connectivity": algebraic_connectivity,
        "mean_degree": float(np.mean(degrees)),
        "degree_variance": float(np.var(degrees)),
    }
