"""Symmetry-resolved detector spectra for small interaction graphs.

The detector Hamiltonian conserves computational-basis Hamming weight and
commutes with every automorphism of its interaction graph.  At half filling it
also commutes with global spin reversal.  This module uses a deterministic
generic Hermitian element of the complete symmetry-group algebra to separate
the corresponding irreducible representation rows.  Equivalent rows of a
multidimensional irrep have identical Hamiltonian spectra and are reported
once, together with their copy multiplicity.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import math
from collections.abc import Iterable

import numpy as np

from collapse.graph_symmetry import graph_automorphisms


@dataclass(frozen=True)
class DetectorSymmetrySector:
    """One nonredundant invariant detector-Hamiltonian sector."""

    hamming_weight: int
    sector_index: int
    dimension: int
    energies: np.ndarray
    symmetry_label: str
    equivalent_copy_count: int
    group_algebra_eigenvalue: float


def fixed_weight_states(n_nodes: int, weight: int) -> np.ndarray:
    """Return sorted computational-basis states with the requested weight."""

    if not 0 <= weight <= n_nodes:
        raise ValueError("weight must lie between zero and n_nodes")
    return np.asarray(
        [state for state in range(1 << n_nodes) if state.bit_count() == weight],
        dtype=np.int64,
    )


def detector_hamiltonian_block(
    n_nodes: int,
    edges: Iterable[tuple[int, int]],
    states: np.ndarray,
    *,
    hz: float,
    j: float,
    jpm: float,
) -> np.ndarray:
    """Construct ``H_D`` in one fixed-Hamming-weight basis.

    The convention matches the network Sobol simulations:

    ``H_D = -hz sum_i Z_i - J sum_(ij) Z_i Z_j
             - Jpm sum_(ij) (sigma_i^+ sigma_j^- + h.c.)``.
    """

    canonical_edges = tuple((int(left), int(right)) for left, right in edges)
    index = {int(state): position for position, state in enumerate(states)}
    block = np.zeros((states.size, states.size), dtype=np.float64)
    for column, raw_state in enumerate(states):
        state = int(raw_state)
        z = np.asarray(
            [1.0 if ((state >> site) & 1) == 0 else -1.0 for site in range(n_nodes)]
        )
        block[column, column] = (
            -hz * float(np.sum(z))
            - j * sum(float(z[left] * z[right]) for left, right in canonical_edges)
        )
        for left, right in canonical_edges:
            if ((state >> left) & 1) != ((state >> right) & 1):
                target = state ^ (1 << left) ^ (1 << right)
                block[index[target], column] -= jpm
    if not np.allclose(block, block.T, rtol=0.0, atol=1.0e-13):
        raise RuntimeError("fixed-weight detector block is not symmetric")
    return block


def _inverse_permutation(permutation: tuple[int, ...]) -> tuple[int, ...]:
    inverse = [0] * len(permutation)
    for source, target in enumerate(permutation):
        inverse[target] = source
    return tuple(inverse)


def _permutation_action(
    states: np.ndarray,
    permutation: tuple[int, ...],
    n_nodes: int,
) -> np.ndarray:
    lookup = np.full(1 << n_nodes, -1, dtype=np.int64)
    lookup[states] = np.arange(states.size, dtype=np.int64)
    targets = np.zeros(states.size, dtype=np.int64)
    for position, raw_state in enumerate(states):
        state = int(raw_state)
        transformed = 0
        for source, target in enumerate(permutation):
            if (state >> source) & 1:
                transformed |= 1 << target
        targets[position] = lookup[transformed]
    if np.any(targets < 0):
        raise RuntimeError("node permutation did not preserve Hamming weight")
    return targets


def _symmetry_action(
    states: np.ndarray,
    permutation: tuple[int, ...],
    n_nodes: int,
    *,
    spin_reversal: bool,
) -> np.ndarray:
    """Return the basis action of a graph permutation and optional spin flip."""

    targets = _permutation_action(states, permutation, n_nodes)
    if not spin_reversal:
        return targets
    lookup = np.full(1 << n_nodes, -1, dtype=np.int64)
    lookup[states] = np.arange(states.size, dtype=np.int64)
    complement = ((1 << n_nodes) - 1) ^ states[targets]
    flipped_targets = lookup[complement]
    if np.any(flipped_targets < 0):
        raise RuntimeError("global spin reversal did not preserve Hamming weight")
    return flipped_targets


def _group_algebra_seed(
    n_nodes: int,
    edges: tuple[tuple[int, int], ...],
    weight: int,
) -> int:
    payload = f"{n_nodes}|{weight}|{edges}".encode("ascii")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def _generic_group_algebra_matrix(
    states: np.ndarray,
    symmetries: tuple[tuple[tuple[int, ...], bool], ...],
    n_nodes: int,
    *,
    seed: int,
) -> tuple[
    np.ndarray,
    dict[tuple[tuple[int, ...], bool], np.ndarray],
]:
    """Return a deterministic generic Hermitian group-algebra element."""

    rng = np.random.default_rng(seed)
    symmetry_indices = {
        symmetry: _symmetry_action(
            states,
            symmetry[0],
            n_nodes,
            spin_reversal=symmetry[1],
        )
        for symmetry in symmetries
    }
    coefficients: dict[tuple[tuple[int, ...], bool], complex] = {}
    visited: set[tuple[tuple[int, ...], bool]] = set()
    for symmetry in symmetries:
        if symmetry in visited:
            continue
        inverse = (_inverse_permutation(symmetry[0]), symmetry[1])
        if inverse == symmetry:
            coefficient = complex(float(rng.normal()), 0.0)
        else:
            coefficient = complex(
                float(rng.normal()) / math.sqrt(2.0),
                float(rng.normal()) / math.sqrt(2.0),
            )
        coefficients[symmetry] = coefficient
        coefficients[inverse] = coefficient.conjugate()
        visited.add(symmetry)
        visited.add(inverse)
    matrix = np.zeros((states.size, states.size), dtype=np.complex128)
    columns = np.arange(states.size, dtype=np.int64)
    for symmetry, coefficient in coefficients.items():
        matrix[symmetry_indices[symmetry], columns] += coefficient
    matrix /= math.sqrt(len(symmetries))
    hermiticity_error = float(np.max(np.abs(matrix - matrix.conj().T)))
    if hermiticity_error > 1.0e-12:
        raise RuntimeError(
            f"group-algebra element is not Hermitian: {hermiticity_error}"
        )
    return matrix, symmetry_indices


def _cluster_sorted(values: np.ndarray, tolerance: float) -> list[np.ndarray]:
    groups: list[list[int]] = []
    for index, value in enumerate(values):
        if not groups or abs(float(value - values[groups[-1][0]])) > tolerance:
            groups.append([index])
        else:
            groups[-1].append(index)
    return [np.asarray(group, dtype=np.int64) for group in groups]


def _centered_spectra_match(left: np.ndarray, right: np.ndarray) -> bool:
    if left.shape != right.shape:
        return False
    left_centered = left - float(np.mean(left))
    right_centered = right - float(np.mean(right))
    scale = max(float(np.ptp(left)), float(np.ptp(right)), 1.0)
    return bool(
        np.allclose(left_centered, right_centered, rtol=1.0e-9, atol=1.0e-9 * scale)
    )


def _asymmetric_half_filling_sectors(
    n_nodes: int,
    states: np.ndarray,
    hamiltonian: np.ndarray,
    *,
    algebra_seed: int,
) -> tuple[list[DetectorSymmetrySector], dict[str, object]]:
    """Split an asymmetric half-filled block directly into spin parities.

    Every computational-basis state is paired with its bitwise complement.
    The normalized sum and difference of each pair form exact ``f=+`` and
    ``f=-`` bases.  Direct submatrix combinations avoid diagonalizing a dense
    924-dimensional representation of the spin-flip operator at N=12.
    """

    lookup = np.full(1 << n_nodes, -1, dtype=np.int64)
    lookup[states] = np.arange(states.size, dtype=np.int64)
    full_mask = (1 << n_nodes) - 1
    left = np.asarray(
        [
            position
            for position, raw_state in enumerate(states)
            if int(raw_state) < (full_mask ^ int(raw_state))
        ],
        dtype=np.int64,
    )
    right = lookup[full_mask ^ states[left]]
    if left.size * 2 != states.size or np.any(right < 0):
        raise RuntimeError("half-filled spin-reversal pairs are incomplete")
    h_ll = hamiltonian[np.ix_(left, left)]
    h_lr = hamiltonian[np.ix_(left, right)]
    h_rl = hamiltonian[np.ix_(right, left)]
    h_rr = hamiltonian[np.ix_(right, right)]
    plus_block = 0.5 * (h_ll + h_lr + h_rl + h_rr)
    minus_block = 0.5 * (h_ll - h_lr - h_rl + h_rr)
    off_diagonal = 0.5 * (h_ll - h_lr + h_rl - h_rr)
    invariant_residual = float(np.max(np.abs(off_diagonal)))
    scale = max(float(np.ptp(np.diag(hamiltonian))), 1.0)
    if invariant_residual > 1.0e-10 * scale:
        raise RuntimeError(
            "spin-reversal parity blocks are not invariant: "
            f"off-diagonal residual={invariant_residual}"
        )
    raw = [
        DetectorSymmetrySector(
            hamming_weight=n_nodes // 2,
            sector_index=index,
            dimension=int(block.shape[0]),
            energies=np.linalg.eigvalsh(block),
            symmetry_label=rf"$N_\uparrow={n_nodes // 2},\ f={symbol}$",
            equivalent_copy_count=1,
            group_algebra_eigenvalue=parity,
        )
        for index, (symbol, parity, block) in enumerate(
            (("+", 1.0, plus_block), ("-", -1.0, minus_block)), start=1
        )
    ]
    representatives: list[DetectorSymmetrySector] = []
    for sector in raw:
        duplicate_index = next(
            (
                position
                for position, representative in enumerate(representatives)
                if _centered_spectra_match(sector.energies, representative.energies)
            ),
            None,
        )
        if duplicate_index is None:
            representatives.append(sector)
        else:
            representative = representatives[duplicate_index]
            representatives[duplicate_index] = replace(
                representative,
                equivalent_copy_count=representative.equivalent_copy_count + 1,
            )
    representatives = [
        replace(sector, sector_index=index)
        for index, sector in enumerate(representatives, start=1)
    ]
    return representatives, {
        "weight": n_nodes // 2,
        "full_dimension": int(states.size),
        "spatial_automorphism_group_order": 1,
        "spin_reversal_resolved": True,
        "total_symmetry_group_order": 2,
        "raw_sector_dimensions": [sector.dimension for sector in raw],
        "nonredundant_sector_dimensions": [
            sector.dimension for sector in representatives
        ],
        "equivalent_copy_counts": [
            sector.equivalent_copy_count for sector in representatives
        ],
        "group_algebra_seed": algebra_seed,
        "group_algebra_eigenvalue_tolerance": 0.0,
        "invariant_subspace_residual_max_abs": invariant_residual,
        "spectrum_union_max_abs": invariant_residual,
        "spectrum_union_validation_method": (
            "exact complementary-bitstring parity basis; reported value is the "
            "maximum off-diagonal parity-block matrix element"
        ),
    }


def _single_transposed_twin_pair(
    automorphisms: tuple[tuple[int, ...], ...],
) -> tuple[int, int] | None:
    """Return the swapped pair when a two-element group is one transposition."""

    if len(automorphisms) != 2:
        return None
    identity = tuple(range(len(automorphisms[0])))
    nonidentity = next(
        (permutation for permutation in automorphisms if permutation != identity),
        None,
    )
    if nonidentity is None:
        return None
    moved = [
        node for node, target in enumerate(nonidentity) if node != target
    ]
    if (
        len(moved) != 2
        or nonidentity[moved[0]] != moved[1]
        or nonidentity[moved[1]] != moved[0]
    ):
        return None
    return moved[0], moved[1]


def _twin_antisymmetric_weight_sectors(
    n_nodes: int,
    edges: tuple[tuple[int, int], ...],
    automorphisms: tuple[tuple[int, ...], ...],
    weight: int,
    twin_pair: tuple[int, int],
    *,
    hz: float,
    j: float,
    jpm: float,
) -> tuple[list[DetectorSymmetrySector], dict[str, object]]:
    """Resolve a twin-swap odd sector through its induced detector graph.

    In the antisymmetric swap sector exactly one twin is occupied.  Exchange
    amplitudes to their common neighbors cancel and their two ZZ contributions
    cancel.  The block is therefore the ``weight - 1`` Hamiltonian on the
    graph with both twins removed, up to a scalar.  Resolving the complete
    automorphism group of that induced graph captures exact sector-specific
    symmetries which need not extend to automorphisms of the original graph.
    """

    states = fixed_weight_states(n_nodes, weight)
    hamiltonian = detector_hamiltonian_block(
        n_nodes, edges, states, hz=hz, j=j, jpm=jpm
    )
    left, right = twin_pair
    retained = [node for node in range(n_nodes) if node not in twin_pair]
    relabel = {old: new for new, old in enumerate(retained)}
    reduced_edges = tuple(
        sorted(
            (relabel[edge_left], relabel[edge_right])
            for edge_left, edge_right in edges
            if edge_left in relabel and edge_right in relabel
        )
    )
    reduced_n = n_nodes - 2
    reduced_weight = weight - 1
    reduced_states = fixed_weight_states(reduced_n, reduced_weight)
    lookup = np.full(1 << n_nodes, -1, dtype=np.int64)
    lookup[states] = np.arange(states.size, dtype=np.int64)

    minus_basis = np.zeros(
        (states.size, reduced_states.size), dtype=np.complex128
    )
    paired_positions: list[tuple[int, int]] = []
    normalization = 1.0 / math.sqrt(2.0)
    for column, raw_reduced_state in enumerate(reduced_states):
        expanded = 0
        reduced_state = int(raw_reduced_state)
        for reduced_node, original_node in enumerate(retained):
            if (reduced_state >> reduced_node) & 1:
                expanded |= 1 << original_node
        left_state = expanded | (1 << left)
        right_state = expanded | (1 << right)
        left_position = int(lookup[left_state])
        right_position = int(lookup[right_state])
        if left_position < 0 or right_position < 0:
            raise RuntimeError("twin-sector basis state has the wrong weight")
        minus_basis[left_position, column] = normalization
        minus_basis[right_position, column] = -normalization
        paired_positions.append((left_position, right_position))

    fixed_positions = [
        position
        for position, raw_state in enumerate(states)
        if ((int(raw_state) >> left) & 1) == ((int(raw_state) >> right) & 1)
    ]
    plus_dimension = len(fixed_positions) + len(paired_positions)
    plus_basis = np.zeros((states.size, plus_dimension), dtype=np.complex128)
    for column, position in enumerate(fixed_positions):
        plus_basis[position, column] = 1.0
    offset = len(fixed_positions)
    for column, (left_position, right_position) in enumerate(paired_positions):
        plus_basis[left_position, offset + column] = normalization
        plus_basis[right_position, offset + column] = normalization

    completeness_error = float(
        np.max(
            np.abs(
                plus_basis @ plus_basis.conj().T
                + minus_basis @ minus_basis.conj().T
                - np.eye(states.size)
            )
        )
    )
    plus_block = plus_basis.conj().T @ hamiltonian @ plus_basis
    minus_block = minus_basis.conj().T @ hamiltonian @ minus_basis
    cross_residual = float(
        np.max(np.abs(plus_basis.conj().T @ hamiltonian @ minus_basis))
    )
    plus_energies = np.linalg.eigvalsh(plus_block)

    reduced_hamiltonian = detector_hamiltonian_block(
        reduced_n,
        reduced_edges,
        reduced_states,
        hz=hz,
        j=j,
        jpm=jpm,
    )
    difference = minus_block - reduced_hamiltonian
    scalar_shift = float(np.real(np.trace(difference)) / difference.shape[0])
    reduction_residual = float(
        np.max(np.abs(difference - scalar_shift * np.eye(difference.shape[0])))
    )
    reduced_automorphisms = graph_automorphisms(reduced_n, reduced_edges)
    reduced_sectors, reduced_validation = _weight_sectors(
        reduced_n,
        reduced_edges,
        reduced_automorphisms,
        reduced_weight,
        hz=hz,
        j=j,
        jpm=jpm,
    )

    representatives = [
        DetectorSymmetrySector(
            hamming_weight=weight,
            sector_index=1,
            dimension=plus_dimension,
            energies=plus_energies,
            symmetry_label=rf"$N_\uparrow={weight},\ p=+$",
            equivalent_copy_count=1,
            group_algebra_eigenvalue=1.0,
        )
    ]
    multiple_reduced_sectors = len(reduced_sectors) > 1
    for index, reduced_sector in enumerate(reduced_sectors, start=1):
        representatives.append(
            replace(
                reduced_sector,
                hamming_weight=weight,
                symmetry_label=(
                    rf"$N_\uparrow={weight},\ p=-,\ \beta={index}$"
                    if multiple_reduced_sectors
                    else rf"$N_\uparrow={weight},\ p=-$"
                ),
                energies=reduced_sector.energies + scalar_shift,
            )
        )
    representatives = [
        replace(sector, sector_index=index)
        for index, sector in enumerate(
            sorted(
                representatives,
                key=lambda sector: (
                    -sector.dimension,
                    sector.group_algebra_eigenvalue,
                ),
            ),
            start=1,
        )
    ]

    split_union = np.sort(
        np.concatenate((plus_energies, np.linalg.eigvalsh(minus_block)))
    )
    full_energies = np.linalg.eigvalsh(hamiltonian)
    union_error = float(np.max(np.abs(full_energies - split_union)))
    invariant_residual = max(
        completeness_error,
        cross_residual,
        reduction_residual,
        float(reduced_validation["invariant_subspace_residual_max_abs"]),
    )
    nested_union_error = float(reduced_validation["spectrum_union_max_abs"])
    scale = max(float(np.ptp(full_energies)), 1.0)
    if invariant_residual > 1.0e-8 * scale or max(
        union_error, nested_union_error
    ) > 1.0e-8 * scale:
        raise RuntimeError(
            "twin-sector symmetry validation failed: "
            f"invariant residual={invariant_residual}, "
            f"union error={union_error}, nested union error={nested_union_error}"
        )

    raw_dimensions = [plus_dimension] + [
        int(value) for value in reduced_validation["raw_sector_dimensions"]
    ]
    return representatives, {
        "weight": weight,
        "full_dimension": int(states.size),
        "spatial_automorphism_group_order": len(automorphisms),
        "spin_reversal_resolved": False,
        "total_symmetry_group_order": len(automorphisms),
        "raw_sector_dimensions": raw_dimensions,
        "nonredundant_sector_dimensions": [
            sector.dimension for sector in representatives
        ],
        "equivalent_copy_counts": [
            sector.equivalent_copy_count for sector in representatives
        ],
        "group_algebra_seed": _group_algebra_seed(n_nodes, edges, weight),
        "group_algebra_eigenvalue_tolerance": 0.0,
        "invariant_subspace_residual_max_abs": invariant_residual,
        "spectrum_union_max_abs": max(union_error, nested_union_error),
        "twin_antisymmetric_reduction": {
            "twin_pair_zero_based": [left, right],
            "reduced_nodes_zero_based": retained,
            "reduced_edge_count": len(reduced_edges),
            "reduced_weight": reduced_weight,
            "reduced_automorphism_group_order": len(reduced_automorphisms),
            "scalar_energy_shift": scalar_shift,
            "reduction_residual_max_abs": reduction_residual,
            "reduced_validation": reduced_validation,
        },
    }


def _weight_sectors(
    n_nodes: int,
    edges: tuple[tuple[int, int], ...],
    automorphisms: tuple[tuple[int, ...], ...],
    weight: int,
    *,
    hz: float,
    j: float,
    jpm: float,
) -> tuple[list[DetectorSymmetrySector], dict[str, object]]:
    states = fixed_weight_states(n_nodes, weight)
    hamiltonian = detector_hamiltonian_block(
        n_nodes, edges, states, hz=hz, j=j, jpm=jpm
    )
    spin_reversal_resolved = n_nodes % 2 == 0 and weight == n_nodes // 2
    algebra_seed = _group_algebra_seed(n_nodes, edges, weight)
    twin_pair = _single_transposed_twin_pair(automorphisms)
    if (
        twin_pair is not None
        and not spin_reversal_resolved
        and 1 <= weight <= n_nodes - 1
    ):
        return _twin_antisymmetric_weight_sectors(
            n_nodes,
            edges,
            automorphisms,
            weight,
            twin_pair,
            hz=hz,
            j=j,
            jpm=jpm,
        )
    if spin_reversal_resolved and len(automorphisms) == 1:
        return _asymmetric_half_filling_sectors(
            n_nodes,
            states,
            hamiltonian,
            algebra_seed=algebra_seed,
        )
    symmetries = tuple(
        (permutation, spin_reversal)
        for spin_reversal in ((False, True) if spin_reversal_resolved else (False,))
        for permutation in automorphisms
    )
    if len(symmetries) == 1:
        symmetry_values = np.zeros(1, dtype=float)
        symmetry_bases = [np.eye(states.size, dtype=np.complex128)]
        symmetry_tolerance = 0.0
        symmetry_indices: dict[tuple[tuple[int, ...], bool], np.ndarray] = {}
    else:
        algebra, symmetry_indices = _generic_group_algebra_matrix(
            states, symmetries, n_nodes, seed=algebra_seed
        )
        values, vectors = np.linalg.eigh(algebra)
        scale = max(float(np.ptp(values)), 1.0)
        symmetry_tolerance = max(1.0e-10, 1.0e-9 * scale)
        clusters = _cluster_sorted(values, symmetry_tolerance)
        symmetry_values = np.asarray(
            [float(np.mean(values[cluster])) for cluster in clusters]
        )
        symmetry_bases = [vectors[:, cluster] for cluster in clusters]

    raw: list[DetectorSymmetrySector] = []
    union: list[np.ndarray] = []
    invariant_residual = 0.0
    for index, (symmetry_value, basis) in enumerate(
        zip(symmetry_values, symmetry_bases, strict=True), start=1
    ):
        sector_block = basis.conj().T @ hamiltonian @ basis
        sector_block = 0.5 * (sector_block + sector_block.conj().T)
        invariant_residual = max(
            invariant_residual,
            float(np.max(np.abs(hamiltonian @ basis - basis @ sector_block))),
        )
        energies = np.linalg.eigvalsh(sector_block)
        union.append(energies)
        parity: int | None = None
        parity_symbol: str | None = None
        if len(symmetries) == 2:
            nonidentity = next(
                symmetry
                for symmetry in symmetries
                if symmetry != (tuple(range(n_nodes)), False)
            )
            action = symmetry_indices[nonidentity]
            transformed = basis[action, :]
            expectation = float(
                np.real(np.trace(basis.conj().T @ transformed)) / basis.shape[1]
            )
            parity = 1 if expectation >= 0.0 else -1
            parity_symbol = "f" if nonidentity[1] else "p"
        label = (
            rf"$N_\uparrow={weight},\ {parity_symbol}={'+' if parity == 1 else '-'}$"
            if parity is not None
            else rf"$N_\uparrow={weight}$"
        )
        raw.append(
            DetectorSymmetrySector(
                hamming_weight=weight,
                sector_index=index,
                dimension=int(basis.shape[1]),
                energies=energies,
                symmetry_label=label,
                equivalent_copy_count=1,
                group_algebra_eigenvalue=float(symmetry_value),
            )
        )

    union_energies = np.sort(np.concatenate(union))
    if len(symmetries) == 1:
        full_energies = union_energies
        union_error = 0.0
    else:
        full_energies = np.linalg.eigvalsh(hamiltonian)
        union_error = float(np.max(np.abs(full_energies - union_energies)))
    scale = max(float(np.ptp(full_energies)), 1.0)
    if invariant_residual > 1.0e-8 * scale or union_error > 1.0e-8 * scale:
        raise RuntimeError(
            "symmetry-sector validation failed: "
            f"invariant residual={invariant_residual}, union error={union_error}"
        )

    representatives: list[DetectorSymmetrySector] = []
    for sector in sorted(
        raw,
        key=lambda item: (-item.dimension, item.group_algebra_eigenvalue),
    ):
        duplicate_index = next(
            (
                position
                for position, representative in enumerate(representatives)
                if _centered_spectra_match(sector.energies, representative.energies)
            ),
            None,
        )
        if duplicate_index is None:
            representatives.append(sector)
        else:
            representative = representatives[duplicate_index]
            representatives[duplicate_index] = replace(
                representative,
                equivalent_copy_count=representative.equivalent_copy_count + 1,
            )
    representatives = [
        replace(
            sector,
            sector_index=index,
            symmetry_label=(
                sector.symmetry_label
                if len(symmetries) <= 2
                else rf"$N_\uparrow={weight},\ \alpha={index}$"
            ),
        )
        for index, sector in enumerate(representatives, start=1)
    ]
    return representatives, {
        "weight": weight,
        "full_dimension": int(states.size),
        "spatial_automorphism_group_order": len(automorphisms),
        "spin_reversal_resolved": spin_reversal_resolved,
        "total_symmetry_group_order": len(symmetries),
        "raw_sector_dimensions": [sector.dimension for sector in raw],
        "nonredundant_sector_dimensions": [
            sector.dimension for sector in representatives
        ],
        "equivalent_copy_counts": [
            sector.equivalent_copy_count for sector in representatives
        ],
        "group_algebra_seed": algebra_seed,
        "group_algebra_eigenvalue_tolerance": symmetry_tolerance,
        "invariant_subspace_residual_max_abs": invariant_residual,
        "spectrum_union_max_abs": union_error,
    }


def largest_detector_symmetry_sectors(
    n_nodes: int,
    edges: Iterable[tuple[int, int]],
    *,
    hz: float,
    j: float,
    jpm: float,
    count: int = 4,
) -> tuple[tuple[DetectorSymmetrySector, ...], dict[str, object]]:
    """Return the largest nonredundant exact symmetry sectors.

    Only weights ``0 <= n <= floor(N/2)`` are considered because the
    complementary sectors have identical spacings up to the constant field
    shift and global spin reversal.  At even-N half filling, global spin
    reversal acts within the block and is included explicitly in the symmetry
    group used for diagonalization.
    """

    if count < 1:
        raise ValueError("count must be positive")
    canonical_edges = tuple(
        sorted(tuple(sorted((int(left), int(right)))) for left, right in edges)
    )
    automorphisms = graph_automorphisms(n_nodes, canonical_edges)
    candidates: list[DetectorSymmetrySector] = []
    block_validation: dict[str, object] = {}
    for weight in range(n_nodes // 2 + 1):
        sectors, validation = _weight_sectors(
            n_nodes,
            canonical_edges,
            automorphisms,
            weight,
            hz=hz,
            j=j,
            jpm=jpm,
        )
        candidates.extend(sector for sector in sectors if sector.dimension >= 2)
        block_validation[f"weight_{weight}"] = validation
    selected = tuple(
        sorted(
            candidates,
            key=lambda sector: (
                -sector.dimension,
                -sector.hamming_weight,
                sector.sector_index,
            ),
        )[:count]
    )
    if len(selected) < count:
        raise RuntimeError(
            f"only {len(selected)} nontrivial sectors are available; requested {count}"
        )
    return selected, {
        "nodes": n_nodes,
        "edge_count": len(canonical_edges),
        "automorphism_group_order": len(automorphisms),
        "automorphisms_zero_based": [list(permutation) for permutation in automorphisms],
        "complementary_weight_sectors_omitted": True,
        "half_filling_spin_reversal_resolved": n_nodes % 2 == 0,
        "selection_rule": (
            "largest nonredundant exact sectors over Hamming weights "
            "0..floor(N/2), resolving the complete graph-automorphism group, "
            "global spin reversal at half filling, and induced-graph "
            "automorphisms exposed by antisymmetric twin-site sectors; "
            "dimension descending"
        ),
        "blocks": block_validation,
        "selected": [
            {
                "hamming_weight": sector.hamming_weight,
                "sector_index": sector.sector_index,
                "dimension": sector.dimension,
                "symmetry_label": sector.symmetry_label,
                "equivalent_copy_count": sector.equivalent_copy_count,
                "group_algebra_eigenvalue": sector.group_algebra_eigenvalue,
            }
            for sector in selected
        ],
    }
