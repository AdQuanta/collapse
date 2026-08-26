"""Symmetry-sector evaluation of the relative-evolution matrix pencil."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from collapse.analysis import evolution_subblocks_from_eigenbasis
from collapse.relative_evolution_pencil import (
    RelativeEvolutionPencilSpectrum,
    generalized_relative_evolution_spectrum,
    matched_projective_angle_error,
)


@dataclass(frozen=True)
class SectorPencilAggregate:
    """Concatenated projective spectrum with per-sector validation data."""

    eigenvalues: np.ndarray
    radii: np.ndarray
    theta: np.ndarray
    finite: np.ndarray
    infinite: np.ndarray
    indeterminate: np.ndarray
    sector_dimensions: tuple[int, ...]
    detector_block_dimensions: tuple[int, ...]
    maximum_condition_number_u00: float
    minimum_singular_value_u00: float
    maximum_homogeneous_residual: float
    maximum_column_isometry_residual: float
    maximum_direct_angle_error: float
    direct_comparison_sectors: int
    direct_skipped_sectors: int
    spectra: tuple[RelativeEvolutionPencilSpectrum, ...]


def generalized_relative_evolution_from_eigenbasis(
    energies: np.ndarray,
    eigenvectors: np.ndarray,
    time: float,
) -> tuple[RelativeEvolutionPencilSpectrum, float]:
    """Evaluate the pencil from a full eigenbasis and check column unitarity."""

    u00, u10 = evolution_subblocks_from_eigenbasis(energies, eigenvectors, time)
    identity = np.eye(u00.shape[1], dtype=np.complex128)
    isometry = u00.conj().T @ u00 + u10.conj().T @ u10
    residual = float(np.linalg.norm(isometry - identity) / max(np.linalg.norm(identity), 1.0))
    return generalized_relative_evolution_spectrum(u00, u10), residual


def _central_indices(sector: dict, total_qubits: int) -> tuple[np.ndarray, np.ndarray]:
    states = np.asarray(sector["states"], dtype=np.int64)
    top_bit = int(sector.get("central_top_bit", 1 if states[0] > states[-1] else 0))
    central_bits = (states >> (total_qubits - 1)) & 1
    return np.where(central_bits == top_bit)[0], np.where(central_bits != top_bit)[0]


def generalized_relative_evolution_from_sectors(
    sectors: list[dict],
    time: float,
    total_qubits: int,
    *,
    compare_direct: bool = False,
    maximum_direct_condition_number: float = 1.0e10,
) -> SectorPencilAggregate:
    """Evaluate independent symmetry-sector pencils without dense projection.

    This routine is valid only when each sector is explicitly marked
    ``relative_evolution_local=True`` and its two central-qubit slices have the
    same dimension.  It fails closed otherwise; magnetization sectors whose
    slices couple across sector boundaries must use the projected full-basis
    path instead.
    """

    if total_qubits < 1:
        raise ValueError("total_qubits must be positive")
    if not sectors:
        raise ValueError("sectors must not be empty")

    spectra: list[RelativeEvolutionPencilSpectrum] = []
    sector_dimensions: list[int] = []
    block_dimensions: list[int] = []
    isometry_residuals: list[float] = []
    direct_errors: list[float] = []
    direct_skipped = 0
    for sector_index, sector in enumerate(sectors):
        if not bool(sector.get("relative_evolution_local", False)):
            raise ValueError(
                f"sector {sector_index} is not safe for a local relative-evolution pencil"
            )
        energies = np.asarray(sector["E"], dtype=float)
        vectors = np.asarray(sector["V"], dtype=np.complex128)
        top, bottom = _central_indices(sector, total_qubits)
        if top.size == 0 or bottom.size == 0:
            continue
        if top.size != bottom.size:
            raise ValueError(
                f"sector {sector_index} central slices have dimensions {top.size} and {bottom.size}"
            )
        if vectors.shape != (energies.size, energies.size):
            raise ValueError(f"sector {sector_index} eigenbasis shape is inconsistent")

        phases = np.exp(-1j * energies * float(time))
        top_vectors = vectors[top, :]
        evolved_columns = (vectors * phases) @ top_vectors.conj().T
        u00 = evolved_columns[top, :]
        u10 = evolved_columns[bottom, :]
        identity = np.eye(top.size, dtype=np.complex128)
        isometry = u00.conj().T @ u00 + u10.conj().T @ u10
        isometry_residuals.append(
            float(np.linalg.norm(isometry - identity) / max(np.linalg.norm(identity), 1.0))
        )
        spectrum = generalized_relative_evolution_spectrum(u00, u10)
        spectra.append(spectrum)
        if compare_direct:
            eligible = (
                spectrum.condition_number_u00 <= maximum_direct_condition_number
                and not np.any(spectrum.infinite)
                and not np.any(spectrum.indeterminate)
            )
            if eligible:
                direct = 2.0 * np.arctan(
                    np.abs(np.linalg.eigvals(np.linalg.solve(u00, u10)))
                )
                maximum, _ = matched_projective_angle_error(direct, spectrum.theta)
                direct_errors.append(maximum)
            else:
                direct_skipped += 1
        sector_dimensions.append(int(energies.size))
        block_dimensions.append(int(top.size))

    expected = 2 ** (total_qubits - 1)
    actual = sum(block_dimensions)
    if actual != expected:
        raise ValueError(
            f"sector pencils produced {actual} detector roots, expected {expected}"
        )
    if not spectra:
        raise ValueError("no sector contained both central-qubit slices")

    concatenate = lambda name: np.concatenate([getattr(item, name) for item in spectra])
    condition_numbers = np.asarray(
        [item.condition_number_u00 for item in spectra], dtype=float
    )
    minimum_singular = min(item.smallest_singular_value_u00 for item in spectra)
    maximum_residual = max(item.maximum_homogeneous_residual for item in spectra)
    return SectorPencilAggregate(
        eigenvalues=concatenate("eigenvalues"),
        radii=concatenate("radii"),
        theta=concatenate("theta"),
        finite=concatenate("finite"),
        infinite=concatenate("infinite"),
        indeterminate=concatenate("indeterminate"),
        sector_dimensions=tuple(sector_dimensions),
        detector_block_dimensions=tuple(block_dimensions),
        maximum_condition_number_u00=float(np.max(condition_numbers)),
        minimum_singular_value_u00=float(minimum_singular),
        maximum_homogeneous_residual=float(maximum_residual),
        maximum_column_isometry_residual=float(max(isometry_residuals)),
        maximum_direct_angle_error=(
            float(max(direct_errors)) if direct_errors else np.nan
        ),
        direct_comparison_sectors=len(direct_errors),
        direct_skipped_sectors=direct_skipped,
        spectra=tuple(spectra),
    )
