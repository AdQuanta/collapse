"""Basis-invariant activation diagnostics for degenerate detector eigenspaces.

The individual entries of ``V_ab`` depend on the eigenbasis chosen inside an
exactly degenerate eigenspace.  This module therefore works with Frobenius
weights, ranks, and singular-value participation ratios of complete spectral
projector blocks ``P_E V P_F``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np

from core.detector_resonance import DenseRingDetectorBuilder, DetectorSpec


DEFAULT_GAP_WINDOWS = (1.0e-6, 1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1)


@dataclass(frozen=True)
class ActivationConfig:
    """Numerical conventions for one detector activation calculation."""

    evolution_time: float = 1.0e6
    degeneracy_tolerance: float = 1.0e-9
    relative_weight_tolerance: float = 1.0e-12
    rank_relative_tolerance: float = 1.0e-10
    gap_windows: tuple[float, ...] = DEFAULT_GAP_WINDOWS

    def __post_init__(self) -> None:
        if self.evolution_time <= 0.0:
            raise ValueError("evolution_time must be positive")
        if self.degeneracy_tolerance <= 0.0:
            raise ValueError("degeneracy_tolerance must be positive")
        if self.relative_weight_tolerance < 0.0 or self.rank_relative_tolerance < 0.0:
            raise ValueError("relative tolerances must be non-negative")
        if any(value <= 0.0 for value in self.gap_windows):
            raise ValueError("gap windows must be positive")
        if tuple(sorted(self.gap_windows)) != self.gap_windows:
            raise ValueError("gap windows must be sorted")


@dataclass(frozen=True)
class DegenerateActivationMetrics:
    """Scalar diagnostics suitable for joining to dynamical sweep outcomes."""

    detector_n: int
    hz: float
    J: float
    Jpm: float
    dimension: int
    distinct_energies: int
    degenerate_subspaces: int
    degenerate_states: int
    maximum_multiplicity: int
    degenerate_state_fraction: float
    exact_active_weight_fraction: float
    active_degenerate_subspace_fraction: float
    active_degenerate_state_fraction: float
    exact_activation_rank_fraction: float
    exact_spectral_participation_fraction: float
    exact_block_participation_count: float
    exact_block_participation_fraction: float
    exact_largest_block_share: float
    weight_fraction_gap_le_1em6: float
    weight_fraction_gap_le_1em5: float
    weight_fraction_gap_le_1em4: float
    weight_fraction_gap_le_1em3: float
    weight_fraction_gap_le_1em2: float
    weight_fraction_gap_le_1em1: float
    finite_time_kernel_power_fraction: float
    finite_time_transition_participation_count: float
    finite_time_transition_participation_fraction: float
    finite_time_largest_transition_share: float
    nearest_active_gap: float
    total_coupling_weight: float

    def to_row(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass(frozen=True)
class DegenerateActivationDetail:
    """Arrays used for representative mechanism figures."""

    metrics: DegenerateActivationMetrics
    subspace_energies: np.ndarray
    subspace_multiplicities: np.ndarray
    block_gaps: np.ndarray
    block_weights: np.ndarray
    exact_block_weights: np.ndarray
    exact_singular_weight: np.ndarray


class DegenerateActivationAnalyzer:
    """Measure how ``V`` activates exact and near-degenerate energy blocks."""

    def __init__(self, config: ActivationConfig | None = None) -> None:
        self.config = config or ActivationConfig()
        self.builder = DenseRingDetectorBuilder()

    def analyze(self, spec: DetectorSpec) -> DegenerateActivationMetrics:
        return self.analyze_detail(spec).metrics

    def analyze_detail(self, spec: DetectorSpec) -> DegenerateActivationDetail:
        operators = self.builder.build(spec)
        energies, vectors = np.linalg.eigh(operators.hamiltonian)
        coupling = vectors.conj().T @ operators.coupling @ vectors
        groups = self._energy_groups(energies)
        group_energies = np.asarray(
            [float(np.mean(energies[start:stop])) for start, stop in groups],
            dtype=float,
        )
        multiplicities = np.asarray([stop - start for start, stop in groups], dtype=int)
        block_weights = self._block_weights(coupling, groups)
        block_gaps = group_energies[:, None] - group_energies[None, :]
        total_weight = float(np.sum(block_weights))
        active_threshold = self.config.relative_weight_tolerance * max(total_weight, 1.0)
        active_pairs = block_weights > active_threshold
        physical_block_weights = np.where(active_pairs, block_weights, 0.0)

        degenerate_mask = multiplicities > 1
        diagonal_weights = np.diag(physical_block_weights)
        exact_block_weights = diagonal_weights[degenerate_mask]
        active_exact_blocks = exact_block_weights > active_threshold
        degenerate_states = int(np.sum(multiplicities[degenerate_mask]))
        active_degenerate_states = int(
            np.sum(multiplicities[degenerate_mask][active_exact_blocks])
        )

        exact_singular_weights: list[float] = []
        exact_rank = 0
        for (start, stop), is_degenerate, block_weight in zip(
            groups,
            degenerate_mask,
            diagonal_weights,
            strict=True,
        ):
            if not is_degenerate or block_weight <= active_threshold:
                continue
            block = coupling[start:stop, start:stop]
            singular_values = np.linalg.svd(block, compute_uv=False)
            if singular_values.size:
                cutoff = self.config.rank_relative_tolerance * float(np.max(singular_values))
                exact_rank += int(np.count_nonzero(singular_values > cutoff))
                exact_singular_weights.extend((singular_values**2).tolist())

        exact_singular_array = np.asarray(exact_singular_weights, dtype=float)
        exact_weight = float(np.sum(exact_block_weights))
        exact_pr = self._participation_count(exact_block_weights[active_exact_blocks])
        singular_pr = self._participation_count(exact_singular_array)
        active_exact_count = int(np.count_nonzero(active_exact_blocks))

        window_values = [
            float(np.sum(physical_block_weights[np.abs(block_gaps) <= window]) / total_weight)
            if total_weight
            else 0.0
            for window in self.config.gap_windows
        ]
        if len(window_values) != 6:
            raise ValueError("the public metric schema requires exactly six gap windows")

        time = self.config.evolution_time
        filter_magnitude = time * np.abs(np.sinc(block_gaps * time / (2.0 * np.pi)))
        finite_time_power = physical_block_weights * filter_magnitude**2
        finite_time_total = float(np.sum(finite_time_power))
        finite_active = finite_time_power > (
            self.config.relative_weight_tolerance * max(finite_time_total, 1.0)
        )
        finite_values = finite_time_power[finite_active]
        finite_pr = self._participation_count(finite_values)
        active_pair_count = int(np.count_nonzero(active_pairs))

        nearest_active_gap = (
            float(np.min(np.abs(block_gaps[active_pairs])))
            if np.any(active_pairs)
            else float("inf")
        )
        metrics = DegenerateActivationMetrics(
            detector_n=spec.detector_n,
            hz=spec.hz,
            J=spec.j,
            Jpm=spec.jpm,
            dimension=int(energies.size),
            distinct_energies=len(groups),
            degenerate_subspaces=int(np.count_nonzero(degenerate_mask)),
            degenerate_states=degenerate_states,
            maximum_multiplicity=int(np.max(multiplicities)),
            degenerate_state_fraction=degenerate_states / energies.size,
            exact_active_weight_fraction=exact_weight / total_weight if total_weight else 0.0,
            active_degenerate_subspace_fraction=(
                active_exact_count / int(np.count_nonzero(degenerate_mask))
                if np.any(degenerate_mask)
                else 0.0
            ),
            active_degenerate_state_fraction=(
                active_degenerate_states / degenerate_states if degenerate_states else 0.0
            ),
            exact_activation_rank_fraction=exact_rank / degenerate_states if degenerate_states else 0.0,
            exact_spectral_participation_fraction=(
                singular_pr / degenerate_states if degenerate_states else 0.0
            ),
            exact_block_participation_count=exact_pr,
            exact_block_participation_fraction=(
                exact_pr / active_exact_count if active_exact_count else 0.0
            ),
            exact_largest_block_share=(
                float(np.max(exact_block_weights)) / exact_weight if exact_weight else 0.0
            ),
            weight_fraction_gap_le_1em6=window_values[0],
            weight_fraction_gap_le_1em5=window_values[1],
            weight_fraction_gap_le_1em4=window_values[2],
            weight_fraction_gap_le_1em3=window_values[3],
            weight_fraction_gap_le_1em2=window_values[4],
            weight_fraction_gap_le_1em1=window_values[5],
            finite_time_kernel_power_fraction=(
                finite_time_total / (time**2 * total_weight) if total_weight else 0.0
            ),
            finite_time_transition_participation_count=finite_pr,
            finite_time_transition_participation_fraction=(
                finite_pr / active_pair_count if active_pair_count else 0.0
            ),
            finite_time_largest_transition_share=(
                float(np.max(finite_values)) / finite_time_total
                if finite_time_total and finite_values.size
                else 0.0
            ),
            nearest_active_gap=nearest_active_gap,
            total_coupling_weight=total_weight,
        )
        return DegenerateActivationDetail(
            metrics=metrics,
            subspace_energies=group_energies,
            subspace_multiplicities=multiplicities,
            block_gaps=block_gaps,
            block_weights=physical_block_weights,
            exact_block_weights=exact_block_weights,
            exact_singular_weight=exact_singular_array,
        )

    def _energy_groups(self, energies: np.ndarray) -> tuple[tuple[int, int], ...]:
        groups: list[tuple[int, int]] = []
        start = 0
        while start < energies.size:
            stop = start + 1
            while (
                stop < energies.size
                and abs(float(energies[stop] - energies[start]))
                <= self.config.degeneracy_tolerance
            ):
                stop += 1
            groups.append((start, stop))
            start = stop
        return tuple(groups)

    @staticmethod
    def _block_weights(
        coupling: np.ndarray,
        groups: Sequence[tuple[int, int]],
    ) -> np.ndarray:
        entry_weights = np.abs(coupling) ** 2
        starts = np.asarray([start for start, _ in groups], dtype=int)
        row_reduced = np.add.reduceat(entry_weights, starts, axis=0)
        return np.asarray(np.add.reduceat(row_reduced, starts, axis=1), dtype=float)

    @staticmethod
    def _participation_count(weights: np.ndarray) -> float:
        values = np.asarray(weights, dtype=float)
        total = float(np.sum(values))
        denominator = float(np.sum(values**2))
        return total**2 / denominator if denominator > 0.0 else 0.0
