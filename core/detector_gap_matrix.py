"""Detector pair-gap matrices for the anisotropic single-pixel campaign.

The raw pair-gap matrix is basis independent once the detector eigenvalues are
sorted.  Coupling-aware summary statistics are computed in the detector energy
basis and use Frobenius weights, so rotations inside degenerate subspaces do
not change their totals.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from core.detector_resonance import DenseRingDetectorBuilder, DetectorSpec


@dataclass(frozen=True)
class GapMatrixCase:
    """One Hamiltonian configuration and its N=14 dynamical classification."""

    key: str
    regime: str
    detector_n: int
    hz: float
    j: float
    jpm: float
    evolution_time: float
    collective_jx: float
    dynamics_n: int
    born_score: float
    born_rmse: float
    angular_coverage: float
    power_law_alpha: float
    power_law_js: float
    power_law_log10_span: float
    wrapped_gaussian_js: float

    @property
    def spec(self) -> DetectorSpec:
        return DetectorSpec(self.detector_n, self.hz, self.j, self.jpm)


@dataclass(frozen=True)
class GapMatrixResult:
    """Eigenvalues, pair gaps, and invariant near-resonance summaries."""

    case: GapMatrixCase
    energies: np.ndarray
    signed_gaps: np.ndarray
    energy_basis_coupling: np.ndarray
    bandwidth: float
    distinct_energies: int
    maximum_multiplicity: int
    offdiagonal_zero_pair_fraction: float
    offdiagonal_finite_time_pair_fraction: float
    active_zero_gap_weight_fraction: float
    active_finite_time_weight_fraction: float
    nearest_active_gap: float
    nearest_active_filter_magnitude: float
    nearest_active_dimensionless_gain: float
    coupling_nonzero_fraction: float
    coupling_negative_fraction: float

    def summary(self) -> dict[str, object]:
        return {
            "key": self.case.key,
            "regime": self.case.regime,
            "detector_n": self.case.detector_n,
            "dynamics_n": self.case.dynamics_n,
            "hz": self.case.hz,
            "J": self.case.j,
            "Jpm": self.case.jpm,
            "evolution_time": self.case.evolution_time,
            "dimension": int(self.energies.size),
            "bandwidth": self.bandwidth,
            "distinct_energies": self.distinct_energies,
            "maximum_multiplicity": self.maximum_multiplicity,
            "offdiagonal_zero_pair_fraction": self.offdiagonal_zero_pair_fraction,
            "offdiagonal_finite_time_pair_fraction": self.offdiagonal_finite_time_pair_fraction,
            "active_zero_gap_weight_fraction": self.active_zero_gap_weight_fraction,
            "active_finite_time_weight_fraction": self.active_finite_time_weight_fraction,
            "nearest_active_gap": self.nearest_active_gap,
            "nearest_active_filter_magnitude": self.nearest_active_filter_magnitude,
            "nearest_active_dimensionless_gain": self.nearest_active_dimensionless_gain,
            "coupling_nonzero_fraction": self.coupling_nonzero_fraction,
            "coupling_negative_fraction": self.coupling_negative_fraction,
            "S_born": self.case.born_score,
            "born_rmse": self.case.born_rmse,
            "angular_coverage": self.case.angular_coverage,
            "theta_power_law_alpha": self.case.power_law_alpha,
            "theta_power_law_js": self.case.power_law_js,
            "theta_power_law_log10_span": self.case.power_law_log10_span,
            "wrapped_gaussian_js": self.case.wrapped_gaussian_js,
        }


class DetectorGapMatrixAnalyzer:
    """Diagonalize a dense ring detector and calculate all pair gaps."""

    def __init__(self, degeneracy_tolerance: float = 1.0e-9):
        if degeneracy_tolerance <= 0.0:
            raise ValueError("degeneracy_tolerance must be positive")
        self.degeneracy_tolerance = float(degeneracy_tolerance)
        self.builder = DenseRingDetectorBuilder()

    def analyze(self, case: GapMatrixCase) -> GapMatrixResult:
        operators = self.builder.build(case.spec)
        energies, vectors = np.linalg.eigh(operators.hamiltonian)
        # Fix the otherwise arbitrary U(1) phase of each numerical eigenvector:
        # its largest component is chosen real and non-negative.  Rotations
        # within exactly degenerate subspaces remain non-unique and are called
        # out explicitly wherever elementwise V_ab heatmaps are interpreted.
        pivots = np.argmax(np.abs(vectors), axis=0)
        pivot_values = vectors[pivots, np.arange(vectors.shape[1])]
        pivot_phases = np.ones_like(pivot_values, dtype=np.complex128)
        nonzero_pivots = np.abs(pivot_values) > np.finfo(float).eps
        pivot_phases[nonzero_pivots] = (
            pivot_values[nonzero_pivots] / np.abs(pivot_values[nonzero_pivots])
        )
        vectors = vectors.astype(np.complex128) / pivot_phases[None, :]
        energies = np.asarray(energies, dtype=float)
        signed_gaps = energies[:, None] - energies[None, :]
        absolute_gaps = np.abs(signed_gaps)
        dimension = energies.size
        offdiagonal = ~np.eye(dimension, dtype=bool)
        finite_time_tolerance = max(1.0 / case.evolution_time, self.degeneracy_tolerance)

        energy_coupling = vectors.conj().T @ operators.coupling @ vectors
        weights = np.abs(energy_coupling) ** 2
        total_weight = float(np.sum(weights))
        active_threshold = 1.0e-12 * max(total_weight, 1.0)
        active = weights > active_threshold
        element_threshold = 1.0e-12 * max(float(np.max(np.abs(energy_coupling))), 1.0)
        resolved_elements = np.abs(energy_coupling) > element_threshold
        zero = absolute_gaps <= self.degeneracy_tolerance
        finite_time = absolute_gaps <= finite_time_tolerance

        multiplicities: list[int] = []
        start = 0
        while start < dimension:
            stop = start + 1
            while stop < dimension and abs(float(energies[stop] - energies[start])) <= self.degeneracy_tolerance:
                stop += 1
            multiplicities.append(stop - start)
            start = stop

        offdiagonal_count = int(np.count_nonzero(offdiagonal))
        nearest_active = float(np.min(absolute_gaps[active])) if np.any(active) else float("inf")
        if np.isfinite(nearest_active):
            if nearest_active <= self.degeneracy_tolerance:
                filter_magnitude = float(case.evolution_time)
            else:
                filter_magnitude = float(abs(np.expm1(1j * nearest_active * case.evolution_time) / (1j * nearest_active)))
        else:
            filter_magnitude = 0.0
        edge_coupling = case.collective_jx / np.sqrt(case.detector_n)
        return GapMatrixResult(
            case=case,
            energies=energies,
            signed_gaps=signed_gaps,
            energy_basis_coupling=energy_coupling,
            bandwidth=float(np.ptp(energies)),
            distinct_energies=len(multiplicities),
            maximum_multiplicity=max(multiplicities),
            offdiagonal_zero_pair_fraction=float(np.count_nonzero(zero & offdiagonal) / offdiagonal_count),
            offdiagonal_finite_time_pair_fraction=float(np.count_nonzero(finite_time & offdiagonal) / offdiagonal_count),
            active_zero_gap_weight_fraction=float(np.sum(weights[zero]) / total_weight) if total_weight else 0.0,
            active_finite_time_weight_fraction=float(np.sum(weights[finite_time]) / total_weight) if total_weight else 0.0,
            nearest_active_gap=nearest_active,
            nearest_active_filter_magnitude=filter_magnitude,
            nearest_active_dimensionless_gain=float(edge_coupling * filter_magnitude),
            coupling_nonzero_fraction=float(np.mean(resolved_elements)),
            coupling_negative_fraction=(
                float(np.mean(np.real(energy_coupling[resolved_elements]) < 0.0))
                if np.any(resolved_elements)
                else 0.0
            ),
        )


class DetectorGapMatrixPlotter:
    """Render signed and near-zero pair-gap matrices as aligned small multiples."""

    def __init__(self, near_zero_decades: float = 12.0):
        if near_zero_decades <= 0.0:
            raise ValueError("near_zero_decades must be positive")
        self.near_zero_decades = float(near_zero_decades)

    @staticmethod
    def _title(result: GapMatrixResult) -> str:
        case = result.case
        return (
            f"{case.regime}\n"
            rf"$h_z={case.hz:g},\ J={case.j:g},\ J_{{\pm}}={case.jpm:g}$"
            "\n"
            rf"$S_{{\rm Born}}={case.born_score:.3f},\ \alpha={case.power_law_alpha:.3f}$"
        )

    def plot_comparison(self, results: Sequence[GapMatrixResult], path: Path) -> Path:
        if not results:
            raise ValueError("results must not be empty")
        path.parent.mkdir(parents=True, exist_ok=True)
        columns = len(results)
        figure = plt.figure(figsize=(4.45 * columns, 8.2))
        grid = figure.add_gridspec(
            2,
            columns + 1,
            width_ratios=[1.0] * columns + [0.045],
            left=0.065,
            right=0.925,
            bottom=0.075,
            top=0.895,
            wspace=0.28,
            hspace=0.34,
        )
        axes = np.asarray(
            [[figure.add_subplot(grid[row, column]) for column in range(columns)] for row in range(2)],
            dtype=object,
        )
        color_axes = [figure.add_subplot(grid[row, columns]) for row in range(2)]
        signed_image = None
        resonance_image = None

        for column, result in enumerate(results):
            dimension = result.energies.size
            scale = max(result.bandwidth, np.finfo(float).eps)
            normalized = result.signed_gaps / scale
            signed_image = axes[0, column].imshow(
                normalized,
                origin="lower",
                interpolation="nearest",
                cmap="coolwarm",
                vmin=-1.0,
                vmax=1.0,
                rasterized=True,
            )
            axes[0, column].set_title(self._title(result), fontsize=10.5)

            relative = np.abs(result.signed_gaps) / scale
            resonance = -np.log10(np.maximum(relative, 10.0 ** (-self.near_zero_decades)))
            np.fill_diagonal(resonance, np.nan)
            resonance_image = axes[1, column].imshow(
                resonance,
                origin="lower",
                interpolation="nearest",
                cmap="magma",
                vmin=0.0,
                vmax=self.near_zero_decades,
                rasterized=True,
            )
            axes[1, column].set_title(
                rf"off-diagonal near-zero structure: $D={result.distinct_energies}$, "
                rf"$m_{{\max}}={result.maximum_multiplicity}$",
                fontsize=9.3,
            )
            for row in range(2):
                axes[row, column].set_xlabel("sorted eigenvalue index $b$")
                if column == 0:
                    axes[row, column].set_ylabel("sorted eigenvalue index $a$")
                axes[row, column].set_xlim(-0.5, dimension - 0.5)
                axes[row, column].set_ylim(-0.5, dimension - 0.5)

        if signed_image is not None:
            figure.colorbar(
                signed_image,
                cax=color_axes[0],
                label=r"signed gap $(E_a-E_b)/(E_{\max}-E_{\min})$",
            )
        if resonance_image is not None:
            figure.colorbar(
                resonance_image,
                cax=color_axes[1],
                label=r"$-\log_{10}(|E_a-E_b|/{\rm bandwidth})$ (diagonal omitted)",
            )
        figure.suptitle(
            rf"Detector pair-gap matrices at $N_D={results[0].case.detector_n}$; "
            rf"dynamical labels from $N={results[0].case.dynamics_n}$, $t=10^6$",
            fontsize=13,
            y=0.995,
        )
        figure.savefig(path, dpi=220)
        plt.close(figure)
        return path

    def plot_interaction_comparison(self, results: Sequence[GapMatrixResult], path: Path) -> Path:
        """Plot log-amplitude and phase of V in the sorted energy basis."""

        if not results:
            raise ValueError("results must not be empty")
        path.parent.mkdir(parents=True, exist_ok=True)
        columns = len(results)
        figure = plt.figure(figsize=(4.45 * columns, 8.2))
        grid = figure.add_gridspec(
            2,
            columns + 1,
            width_ratios=[1.0] * columns + [0.045],
            left=0.065,
            right=0.925,
            bottom=0.075,
            top=0.895,
            wspace=0.28,
            hspace=0.34,
        )
        axes = np.asarray(
            [[figure.add_subplot(grid[row, column]) for column in range(columns)] for row in range(2)],
            dtype=object,
        )
        color_axes = [figure.add_subplot(grid[row, columns]) for row in range(2)]
        amplitude_image = None
        phase_image = None

        for column, result in enumerate(results):
            coupling = result.energy_basis_coupling
            amplitude = np.abs(coupling)
            maximum = max(float(np.max(amplitude)), np.finfo(float).eps)
            relative_amplitude = amplitude / maximum
            log_amplitude = np.log10(np.maximum(relative_amplitude, 1.0e-12))
            phase = np.angle(coupling)
            phase = np.ma.masked_where(relative_amplitude <= 1.0e-12, phase)
            amplitude_image = axes[0, column].imshow(
                log_amplitude,
                origin="lower",
                interpolation="nearest",
                cmap="viridis",
                vmin=-12.0,
                vmax=0.0,
                rasterized=True,
            )
            phase_image = axes[1, column].imshow(
                phase,
                origin="lower",
                interpolation="nearest",
                cmap="twilight",
                vmin=-np.pi,
                vmax=np.pi,
                rasterized=True,
            )
            axes[0, column].set_title(self._title(result), fontsize=10.5)
            axes[1, column].set_title(
                r"phase of resolved nonzero $V_{ab}$ (zero entries white)",
                fontsize=9.3,
            )
            dimension = result.energies.size
            for row in range(2):
                axes[row, column].set_xlabel("sorted eigenvalue index $b$")
                if column == 0:
                    axes[row, column].set_ylabel("sorted eigenvalue index $a$")
                axes[row, column].set_xlim(-0.5, dimension - 0.5)
                axes[row, column].set_ylim(-0.5, dimension - 0.5)

        if amplitude_image is not None:
            figure.colorbar(
                amplitude_image,
                cax=color_axes[0],
                label=r"$\log_{10}(|V_{ab}|/\max |V|)$",
            )
        if phase_image is not None:
            colorbar = figure.colorbar(
                phase_image,
                cax=color_axes[1],
                ticks=[-np.pi, -np.pi / 2.0, 0.0, np.pi / 2.0, np.pi],
                label=r"$\arg V_{ab}$",
            )
            colorbar.ax.set_yticklabels([r"$-\pi$", r"$-\pi/2$", "$0$", r"$\pi/2$", r"$\pi$"])
        figure.suptitle(
            rf"Interaction matrix $V_{{ab}}=\langle E_a|\sum_iX_i|E_b\rangle$ at "
            rf"$N_D={results[0].case.detector_n}$ (phase-fixed numerical energy basis)",
            fontsize=13,
            y=0.995,
        )
        figure.savefig(path, dpi=220)
        plt.close(figure)
        return path
