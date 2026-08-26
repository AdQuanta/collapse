"""Basis-invariant detector-spectrum and resonance diagnostics.

The central interaction in the single-pixel models is ``X0 tensor V`` with
``V = sum_i X_i``. Resonance statements must therefore be made from detector
spectral projectors, not an arbitrary eigenbasis inside a degenerate space.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

import numpy as np


@dataclass(frozen=True)
class DetectorSpec:
    detector_n: int
    hz: float
    j: float
    jpm: float
    j2: float = 0.0
    jpm2: float = 0.0

    def __post_init__(self) -> None:
        if self.detector_n < 3:
            raise ValueError("detector_n must be at least three")


@dataclass(frozen=True)
class DetectorOperators:
    hamiltonian: np.ndarray
    coupling: np.ndarray


class DetectorOperatorBuilder(Protocol):
    def build(self, spec: DetectorSpec) -> DetectorOperators:
        ...


class DenseRingDetectorBuilder:
    """Build the displayed-sign first- and second-neighbor ring detector."""

    def build(self, spec: DetectorSpec) -> DetectorOperators:
        n = spec.detector_n
        dimension = 1 << n
        hamiltonian = np.zeros((dimension, dimension), dtype=np.float64)
        coupling = np.zeros_like(hamiltonian)
        nearest_bonds = _ring_bonds(n, step=1)
        second_bonds = _ring_bonds(n, step=2)
        for state in range(dimension):
            spins = np.array(
                [1.0 if ((state >> site) & 1) == 0 else -1.0 for site in range(n)],
                dtype=np.float64,
            )
            hamiltonian[state, state] = (
                spec.hz * float(np.sum(spins))
                + spec.j * float(
                    sum(spins[left] * spins[right] for left, right in nearest_bonds)
                )
                + spec.j2 * float(
                    sum(spins[left] * spins[right] for left, right in second_bonds)
                )
            )
            for site in range(n):
                coupling[state ^ (1 << site), state] += 1.0
            for left, right in nearest_bonds:
                if ((state >> left) & 1) != ((state >> right) & 1):
                    swapped = state ^ (1 << left) ^ (1 << right)
                    hamiltonian[swapped, state] += spec.jpm
            for left, right in second_bonds:
                if ((state >> left) & 1) != ((state >> right) & 1):
                    swapped = state ^ (1 << left) ^ (1 << right)
                    hamiltonian[swapped, state] += spec.jpm2
        if not np.allclose(hamiltonian, hamiltonian.T, atol=1.0e-12):
            raise RuntimeError("detector Hamiltonian is not Hermitian")
        return DetectorOperators(hamiltonian=hamiltonian, coupling=coupling)


def _ring_bonds(n: int, *, step: int) -> tuple[tuple[int, int], ...]:
    """Return distinct undirected ``step``-neighbor bonds on an ``n``-ring."""

    bonds = {
        tuple(sorted((site, (site + step) % n)))
        for site in range(n)
        if site != (site + step) % n
    }
    return tuple(sorted(bonds))


@dataclass(frozen=True)
class EnergySubspace:
    energy: float
    basis: np.ndarray

    @property
    def multiplicity(self) -> int:
        return int(self.basis.shape[1])


@dataclass(frozen=True)
class ActiveTransition:
    source_energy: float
    target_energy: float
    gap: float
    weight: float
    source_multiplicity: int
    target_multiplicity: int


@dataclass(frozen=True)
class ResonanceSummary:
    distinct_energies: int
    degenerate_subspaces: int
    maximum_multiplicity: int
    detector_degenerate_weight_fraction: float
    target_gap: float
    nearest_active_detuning: float
    exact_resonant_weight_fraction: float
    total_active_weight: float


class SpectralProjectorAnalyzer:
    """Compute basis-invariant weights ``||P_a V P_b||_F^2``."""

    def __init__(self, degeneracy_tolerance: float = 1.0e-9, weight_tolerance: float = 1.0e-12):
        if degeneracy_tolerance <= 0.0 or weight_tolerance < 0.0:
            raise ValueError("invalid tolerance")
        self.degeneracy_tolerance = float(degeneracy_tolerance)
        self.weight_tolerance = float(weight_tolerance)

    def energy_subspaces(self, hamiltonian: np.ndarray) -> tuple[EnergySubspace, ...]:
        energies, vectors = np.linalg.eigh(np.asarray(hamiltonian, dtype=np.complex128))
        output: list[EnergySubspace] = []
        start = 0
        while start < energies.size:
            stop = start + 1
            while stop < energies.size and abs(float(energies[stop] - energies[start])) <= self.degeneracy_tolerance:
                stop += 1
            output.append(
                EnergySubspace(
                    energy=float(np.mean(energies[start:stop])),
                    basis=np.asarray(vectors[:, start:stop], dtype=np.complex128),
                )
            )
            start = stop
        return tuple(output)

    def active_transitions(
        self,
        subspaces: Sequence[EnergySubspace],
        coupling: np.ndarray,
    ) -> tuple[ActiveTransition, ...]:
        operator = np.asarray(coupling, dtype=np.complex128)
        output: list[ActiveTransition] = []
        for source in subspaces:
            action = operator @ source.basis
            for target in subspaces:
                block = target.basis.conj().T @ action
                weight = float(np.linalg.norm(block, ord="fro") ** 2)
                if weight <= self.weight_tolerance:
                    continue
                output.append(
                    ActiveTransition(
                        source_energy=source.energy,
                        target_energy=target.energy,
                        gap=target.energy - source.energy,
                        weight=weight,
                        source_multiplicity=source.multiplicity,
                        target_multiplicity=target.multiplicity,
                    )
                )
        return tuple(output)

    def summarize(
        self,
        subspaces: Sequence[EnergySubspace],
        transitions: Sequence[ActiveTransition],
        hz0: float,
    ) -> ResonanceSummary:
        total = float(sum(item.weight for item in transitions))
        target_gap = 2.0 * float(hz0)
        nearest = min((abs(item.gap - target_gap) for item in transitions), default=float("inf"))
        resonant = sum(
            item.weight for item in transitions
            if abs(item.gap - target_gap) <= self.degeneracy_tolerance
        )
        degenerate = sum(
            item.weight for item in transitions
            if abs(item.gap) <= self.degeneracy_tolerance
        )
        multiplicities = [item.multiplicity for item in subspaces]
        return ResonanceSummary(
            distinct_energies=len(subspaces),
            degenerate_subspaces=sum(value > 1 for value in multiplicities),
            maximum_multiplicity=max(multiplicities, default=0),
            detector_degenerate_weight_fraction=degenerate / total if total else 0.0,
            target_gap=target_gap,
            nearest_active_detuning=float(nearest),
            exact_resonant_weight_fraction=resonant / total if total else 0.0,
            total_active_weight=total,
        )

    def analyze(self, operators: DetectorOperators, hz0: float):
        subspaces = self.energy_subspaces(operators.hamiltonian)
        transitions = self.active_transitions(subspaces, operators.coupling)
        return subspaces, transitions, self.summarize(subspaces, transitions, hz0)


def rotate_subspaces(subspaces: Sequence[EnergySubspace], seed: int = 0) -> tuple[EnergySubspace, ...]:
    """Apply independent unitary rotations within all degenerate spaces."""

    rng = np.random.default_rng(seed)
    output: list[EnergySubspace] = []
    for subspace in subspaces:
        width = subspace.multiplicity
        raw = rng.normal(size=(width, width)) + 1j * rng.normal(size=(width, width))
        unitary, triangular = np.linalg.qr(raw)
        diagonal = np.diag(triangular)
        phases = np.ones_like(diagonal)
        nonzero = np.abs(diagonal) > 0.0
        phases[nonzero] = diagonal[nonzero] / np.abs(diagonal[nonzero])
        unitary = unitary @ np.diag(np.conj(phases))
        output.append(EnergySubspace(subspace.energy, subspace.basis @ unitary))
    return tuple(output)


def transition_weight_map(transitions: Sequence[ActiveTransition], digits: int = 10):
    return {
        (round(item.source_energy, digits), round(item.target_energy, digits)): item.weight
        for item in transitions
    }


def relative_weight_map_error(reference, candidate) -> float:
    if reference.keys() != candidate.keys():
        return float("inf")
    scale = max(max(reference.values(), default=0.0), 1.0)
    return float(max((abs(reference[key] - candidate[key]) / scale for key in reference), default=0.0))
