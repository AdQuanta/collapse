"""Operational tests for the resonance--mixing--reciprocity conjecture."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from core.anisotropic_sweep import AngularDiagnosticCalculator, AnisotropicSample
from core.detector_resonance import DenseRingDetectorBuilder, DetectorSpec


@dataclass(frozen=True)
class JointProfileGates:
    born_score_min: float = 0.75
    born_rmse_max: float = 0.15
    coverage_min: float = 0.50
    alpha_max: float = 2.0
    power_law_js_max: float = 0.10
    power_law_span_min: float = 1.0


@dataclass(frozen=True)
class HamiltonianPoint:
    detector_n: int
    hz: float
    j: float
    jpm: float
    born_score: float
    born_rmse: float
    coverage: float
    alpha: float
    power_law_js: float
    power_law_span: float
    source_npz: str

    @classmethod
    def from_csv_row(cls, row: Mapping[str, str]) -> "HamiltonianPoint":
        return cls(
            detector_n=int(row["detector_n"]),
            hz=float(row["hz"]),
            j=float(row["J"]),
            jpm=float(row["Jpm"]),
            born_score=float(row["S_born"]),
            born_rmse=float(row["born_rmse"]),
            coverage=float(row["angular_bin_coverage"]),
            alpha=float(row["theta_power_law_alpha"]),
            power_law_js=float(row["theta_power_law_js"]),
            power_law_span=float(row["theta_power_law_log10_span"]),
            source_npz=row["source_npz"],
        )

    @property
    def parameter_key(self) -> tuple[float, float, float]:
        return (self.hz, self.j, self.jpm)


class JointProfileClassifier:
    """Separate exact output gates from a Hamiltonian-level candidate screen."""

    def __init__(self, gates: JointProfileGates | None = None, corridor_tolerance: float = 0.011):
        self.gates = gates or JointProfileGates()
        if corridor_tolerance <= 0.0:
            raise ValueError("corridor_tolerance must be positive")
        self.corridor_tolerance = float(corridor_tolerance)

    def is_heavy(self, point: HamiltonianPoint) -> bool:
        g = self.gates
        return (
            point.coverage >= g.coverage_min
            and point.alpha <= g.alpha_max
            and point.power_law_js <= g.power_law_js_max
            and point.power_law_span >= g.power_law_span_min
        )

    def is_born_like(self, point: HamiltonianPoint) -> bool:
        g = self.gates
        return (
            point.coverage >= g.coverage_min
            and point.born_score >= g.born_score_min
            and point.born_rmse <= g.born_rmse_max
        )

    def is_joint(self, point: HamiltonianPoint) -> bool:
        return self.is_heavy(point) and self.is_born_like(point)

    @staticmethod
    def family(point: HamiltonianPoint) -> str:
        if point.jpm == 0.0 and point.j == 0.0:
            return "uncoupled detector"
        if point.jpm == 0.0:
            return "pure ZZ"
        if point.j == 0.0:
            return "pure exchange"
        return "mixed ZZ+exchange"

    @staticmethod
    def corridor_distances(point: HamiltonianPoint) -> dict[str, float]:
        field = abs(point.hz)
        j = abs(point.j)
        jpm = abs(point.jpm)
        return {
            "zero field": field,
            "|hz|=J": abs(field - j),
            "|hz|=2J": abs(field - 2.0 * j),
            "|hz|=Jpm": abs(field - jpm),
            "|hz|=2Jpm": abs(field - 2.0 * jpm),
        }

    def corridor(self, point: HamiltonianPoint) -> str:
        distances = self.corridor_distances(point)
        label = min(distances, key=distances.get)
        return label if distances[label] <= self.corridor_tolerance else "off corridor"

    def microscopic_candidate(self, point: HamiltonianPoint) -> bool:
        """High-recall screen; reciprocal kernel balance is checked separately."""

        return point.jpm > 0.0 and self.corridor(point) != "off corridor"


@dataclass(frozen=True)
class KernelBalanceResult:
    born_score: float
    born_rmse: float
    coverage: float
    non_atomic_fraction: float


class FiniteTimeKernelBalance:
    """Concrete parameter-to-kernel proxy for the reciprocity ingredient."""

    def __init__(
        self,
        probe_n: int = 6,
        evolution_time: float = 1.0e6,
        bins: int = 24,
        jx: float = 0.01,
    ):
        if probe_n < 3:
            raise ValueError("probe_n must be at least three")
        self.probe_n = int(probe_n)
        self.evolution_time = float(evolution_time)
        self.jx = float(jx)
        self.builder = DenseRingDetectorBuilder()
        self.diagnostics = AngularDiagnosticCalculator(bins)

    def kernel_eigenvalues(self, point: HamiltonianPoint) -> np.ndarray:
        operators = self.builder.build(DetectorSpec(self.probe_n, point.hz, point.j, point.jpm))
        energies, vectors = np.linalg.eigh(operators.hamiltonian)
        coupling = vectors.T @ operators.coupling @ vectors
        gaps = energies[:, None] - energies[None, :]
        scaled = gaps * self.evolution_time
        filter_matrix = np.empty_like(gaps, dtype=np.complex128)
        zero = np.abs(gaps) <= 1.0e-12
        filter_matrix[zero] = self.evolution_time
        filter_matrix[~zero] = np.expm1(1j * scaled[~zero]) / (1j * gaps[~zero])
        kernel = coupling * filter_matrix
        kernel = 0.5 * (kernel + kernel.conj().T)
        return np.linalg.eigvalsh(kernel)

    def analyze(self, point: HamiltonianPoint) -> KernelBalanceResult:
        kappa = self.kernel_eigenvalues(point)
        g = self.jx / np.sqrt(point.detector_n)
        approximate_eigenvalues = -1j * np.tan(g * kappa)
        theta = 2.0 * np.arctan(np.abs(approximate_eigenvalues))
        diagnostic = self.diagnostics.calculate(
            AnisotropicSample(
                eigenvalues=approximate_eigenvalues,
                theta=theta,
                sector_count=1,
                diagonalization_seconds=0.0,
                analysis_seconds=0.0,
            )
        )
        rounded = np.round(theta, decimals=10)
        non_atomic_fraction = len(np.unique(rounded)) / max(theta.size, 1)
        return KernelBalanceResult(
            born_score=diagnostic.born_score,
            born_rmse=diagnostic.born_rmse,
            coverage=diagnostic.coverage,
            non_atomic_fraction=float(non_atomic_fraction),
        )


def confusion(predicted: list[bool], observed: list[bool]) -> dict[str, float | int]:
    if len(predicted) != len(observed):
        raise ValueError("predicted and observed must have equal length")
    tp = int(sum(bool(p) and bool(o) for p, o in zip(predicted, observed, strict=True)))
    fp = int(sum(bool(p) and not bool(o) for p, o in zip(predicted, observed, strict=True)))
    fn = int(sum(not bool(p) and bool(o) for p, o in zip(predicted, observed, strict=True)))
    tn = int(sum(not bool(p) and not bool(o) for p, o in zip(predicted, observed, strict=True)))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision, "recall": recall}
