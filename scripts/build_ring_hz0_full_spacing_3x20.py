#!/usr/bin/env python3.11
"""Build a 3x20 hz0 diagnostic strip with combined-Hamiltonian spacings.

Rows one and two reproduce the saved global ``P(theta)`` and ``R(theta)``
diagnostics.  Row three shows unfolded level-spacing distributions of the
fully symmetry-resolved full qubit-detector Hamiltonian.  It can either show
one selected sector or aggregate a completed 20-sector Zeus campaign.

The combined Hamiltonian preserves detector translation and total excitation
parity.  For the odd-length ring, nonzero momenta occur in reflection-related
``k``/``-k`` pairs with identical spectra.  The default ``k=1`` and even total
excitation parity therefore selects one nonduplicated large sector (dimension
7710 at ``N_D=17``).  A central eigenvalue window is obtained with sparse
shift-invert diagonalization and checkpointed independently for every ``hz0``.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, fields, replace
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any
import warnings

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))
warnings.filterwarnings("ignore", message=r".*font family.*not found.*")
warnings.filterwarnings("ignore", message=r".*Glyph.*missing from font.*")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from quspin.basis import spin_basis_general  # noqa: E402
from quspin.basis.basis_general.base_general import GeneralBasisWarning  # noqa: E402
from quspin.operators import hamiltonian  # noqa: E402
import scipy  # noqa: E402
from scipy.sparse import csr_matrix  # noqa: E402
from scipy.sparse.linalg import eigsh  # noqa: E402

from core.activation_resolved_projective import (  # noqa: E402
    RingActivationParameters,
    full_pixel_translation,
)
from core.hamiltonians.quspin_hamiltonians import (  # noqa: E402
    SinglePixelHamiltonianQuSpin,
)
from core.level_spacing import (  # noqa: E402
    compute_level_spacing_ratios,
    compute_level_spacings,
    compute_unfolded_spacings,
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)
from core.sobol_coupling_scan import (  # noqa: E402
    _atomic_json,
    _sha256,
    timestamp,
)
from scripts.run_three_ring_activation_resolved import _load_case  # noqa: E402
from scripts.summarize_ring_hz0_activation_scan import (  # noqa: E402
    BLUE,
    MODEL_BLUE,
    MODEL_ORANGE,
    PURPLE,
    RED,
    _ratio_title,
    _read_json,
)


DEFAULT_CONFIG = ROOT / "configs" / "ring_second_neighbor_wd_hz0_scan_N17.json"
DEFAULT_RUN_ROOT = ROOT / "work" / "zeus_ring_second_neighbor_wd_hz0_scan_N17_20260825_225825"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "ring_second_neighbor_wd_hz0_scan_N17_2026-08-26"
DEFAULT_OUTPUT_NAME = "hz0_scan_global_diagnostics_full_spacing_3x20.png"
SCHEMA_VERSION = 1
SPECTRUM_METHOD_VERSION = 1
ALL_SECTOR_COUNT = 20


def excitation_parity_nups(total_qubits: int, parity: int) -> list[int]:
    """Return allowed excitation counts for one exact parity sector.

    The central ``X_0 X_i`` coupling changes total excitation number by zero or
    two, so excitation parity remains exact even though total excitation number
    itself is not conserved.
    """

    if total_qubits < 2:
        raise ValueError("total_qubits must be at least two")
    if parity not in (0, 1):
        raise ValueError("parity must be 0 (even) or 1 (odd)")
    return list(range(parity, total_qubits + 1, 2))


def full_pixel_reflection(detector_n: int) -> np.ndarray:
    """Return detector reflection with the central qubit held fixed."""

    if detector_n < 2:
        raise ValueError("detector_n must be at least two")
    permutation = np.arange(detector_n + 1)
    for site in range(detector_n):
        permutation[1 + site] = 1 + (-site) % detector_n
    return permutation


def load_spectrum_case(
    config: dict[str, Any],
    case: dict[str, Any],
) -> tuple[RingActivationParameters, dict[str, Any]]:
    """Load one case from inline parameters or a legacy result reference."""

    raw_base = config.get("base_parameters")
    if raw_base is None:
        return _load_case(case)
    if not isinstance(raw_base, dict):
        raise ValueError("base_parameters must be a JSON object")
    allowed = {item.name for item in fields(RingActivationParameters)}
    missing = allowed - set(raw_base)
    unknown = set(raw_base) - allowed
    if missing or unknown:
        raise ValueError(
            f"invalid base_parameters: missing={sorted(missing)}, "
            f"unknown={sorted(unknown)}"
        )
    parameters = RingActivationParameters(
        **{name: float(value) for name, value in raw_base.items()}
    )
    if not all(math.isfinite(value) for value in asdict(parameters).values()):
        raise ValueError("all base parameters must be finite")
    raw_overrides = case.get("parameter_overrides", {})
    if not isinstance(raw_overrides, dict):
        raise ValueError("parameter_overrides must be a JSON object")
    unknown_overrides = set(raw_overrides) - allowed
    if unknown_overrides:
        raise ValueError(f"unknown parameter override(s): {sorted(unknown_overrides)}")
    overrides = {name: float(value) for name, value in raw_overrides.items()}
    if not all(math.isfinite(value) for value in overrides.values()):
        raise ValueError("all parameter overrides must be finite")
    parameters = replace(parameters, **overrides)
    if parameters.evolution_time <= 0.0:
        raise ValueError("evolution_time must be positive")
    provenance = {
        **dict(config.get("source_provenance", {})),
        "parameter_overrides": overrides,
        "parameter_source": "inline_base_parameters",
    }
    return parameters, provenance


def build_combined_sector_operator(
    detector_n: int,
    parameters: RingActivationParameters,
    *,
    momentum: int,
    excitation_parity: int,
    reflection_parity: int | None = None,
) -> tuple[Any, csr_matrix]:
    """Construct one fully resolved combined-Hamiltonian sector.

    Reflection can be resolved simultaneously with translation only in the
    zero-momentum block for this odd ring.  ``reflection_parity`` uses the
    physical eigenvalues ``+1`` and ``-1``.
    """

    if detector_n < 2:
        raise ValueError("detector_n must be at least two")
    if not 0 <= momentum < detector_n:
        raise ValueError("momentum must satisfy 0 <= momentum < detector_n")
    if reflection_parity not in (None, -1, 1):
        raise ValueError("reflection_parity must be None, -1, or +1")
    if reflection_parity is not None and momentum != 0:
        raise ValueError("reflection parity can only be resolved at momentum k=0")
    total_qubits = detector_n + 1
    basis_blocks: dict[str, Any] = {
        "Nup": excitation_parity_nups(total_qubits, excitation_parity),
        "kblock": (full_pixel_translation(detector_n), momentum),
    }
    if reflection_parity is not None:
        reflection_quantum_number = 0 if reflection_parity == 1 else 1
        basis_blocks["pblock"] = (
            full_pixel_reflection(detector_n),
            reflection_quantum_number,
        )
    with warnings.catch_warnings():
        if reflection_parity is not None:
            # Reflection and translation do not commute as group generators,
            # but reflection preserves the selected k=0 quantum number.  The
            # reconstruction test verifies that these two reflection blocks
            # exactly partition the unsplit k=0 spectrum.
            warnings.filterwarnings(
                "ignore",
                message=r"using non-commuting symmetries.*",
                category=GeneralBasisWarning,
            )
        basis = spin_basis_general(total_qubits, **basis_blocks)
    model = SinglePixelHamiltonianQuSpin(
        N_pixel=detector_n,
        J=parameters.j,
        Jpm=parameters.jpm,
        J2=parameters.j2,
        Jpm2=parameters.jpm2,
        Jx=parameters.effective_jx(detector_n),
        Jy=0.0,
        Jz=0.0,
        Jzx=0.0,
        hx=0.0,
        hz=parameters.hz,
        hx0=0.0,
        hz0=parameters.hz0,
        connectivity="ring",
        central_coupling="all",
        seed=44,
        use_symmetry=True,
    )
    static, actual_total = model._build_static()
    if actual_total != total_qubits:
        raise RuntimeError("combined Hamiltonian dimension is inconsistent")
    operator = hamiltonian(
        static,
        [],
        basis=basis,
        dtype=np.complex128,
        check_symm=False,
        check_herm=False,
        check_pcon=False,
    ).tocsr()
    antihermitian = operator - operator.getH()
    hermiticity_error = (
        float(np.max(np.abs(antihermitian.data)))
        if antihermitian.nnz
        else 0.0
    )
    if hermiticity_error > 1.0e-12:
        raise RuntimeError(
            f"combined sector is not Hermitian: max error={hermiticity_error:.3e}"
        )
    return basis, operator


def central_sector_spectrum(
    operator: csr_matrix,
    *,
    eigenvalue_count: int,
    solver_tolerance: float,
) -> dict[str, Any]:
    """Compute and validate a contiguous central eigenvalue window.

    Shift-invert targets the mean diagonal energy.  Returned eigenpairs are
    sorted, checked for orthonormality, and checked by relative residuals.
    """

    dimension = int(operator.shape[0])
    if operator.shape[1] != dimension:
        raise ValueError("operator must be square")
    if not 4 <= eigenvalue_count < dimension - 1:
        raise ValueError("eigenvalue_count must satisfy 4 <= count < dimension-1")
    if not 0.0 < solver_tolerance < 1.0:
        raise ValueError("solver_tolerance must lie in (0,1)")
    sigma = float(np.real(np.mean(operator.diagonal())))
    operator_norm_bound = float(np.max(np.asarray(np.abs(operator).sum(axis=1))))
    started = time.perf_counter()
    initial_vector = np.linspace(1.0, 2.0, dimension, dtype=float)
    initial_vector /= np.linalg.norm(initial_vector)
    attempted_tolerances = (
        float(solver_tolerance),
        max(float(solver_tolerance) * 1.0e-2, np.finfo(float).eps),
    )
    for attempt, effective_tolerance in enumerate(attempted_tolerances):
        energies, eigenvectors = eigsh(
            operator,
            k=int(eigenvalue_count),
            sigma=sigma,
            which="LM",
            tol=effective_tolerance,
            v0=initial_vector,
            return_eigenvectors=True,
        )
        order = np.argsort(energies)
        energies = np.asarray(energies[order], dtype=float)
        eigenvectors = np.asarray(eigenvectors[:, order], dtype=np.complex128)
        applied = operator @ eigenvectors
        residual_norms = np.linalg.norm(
            applied - eigenvectors * energies[None, :], axis=0
        )
        denominators = np.maximum(
            operator_norm_bound + np.abs(energies),
            np.finfo(float).eps,
        )
        relative_residuals = residual_norms / denominators
        gram = eigenvectors.conj().T @ eigenvectors
        orthogonality_error = float(
            np.max(np.abs(gram - np.eye(eigenvalue_count, dtype=np.complex128)))
        )
        maximum_residual = float(np.max(relative_residuals))
        if maximum_residual <= 1.0e-8 and orthogonality_error <= 1.0e-8:
            break
        if attempt == len(attempted_tolerances) - 1:
            raise RuntimeError(
                "combined-sector eigensolver validation failed after retry: "
                f"max residual={maximum_residual:.3e}, "
                f"orthogonality error={orthogonality_error:.3e}"
            )
    span = float(np.ptp(energies))
    degeneracy_tolerance = max(1.0e-12, 1.0e-10 * max(span, 1.0))
    raw_spacings = compute_level_spacings(energies, tol=degeneracy_tolerance)
    ratios = compute_level_spacing_ratios(raw_spacings)
    unfolded = compute_unfolded_spacings(
        energies,
        tol=degeneracy_tolerance,
        degree=3,
        trim_fraction=0.1,
    )
    if unfolded.size < 20 or ratios.size < 20:
        raise RuntimeError("combined-sector spectrum has too few resolved spacings")
    return {
        "energies": energies,
        "unfolded_spacings": unfolded,
        "spacing_ratios": ratios,
        "sigma": sigma,
        "operator_infinity_norm_bound": operator_norm_bound,
        "residual_normalization": "operator_inf_bound_plus_abs_eigenvalue",
        "effective_solver_tolerance": effective_tolerance,
        "solver_attempt_count": attempt + 1,
        "runtime_seconds": time.perf_counter() - started,
        "maximum_relative_residual": maximum_residual,
        "orthogonality_error": orthogonality_error,
        "degeneracy_tolerance": degeneracy_tolerance,
        "resolved_level_count": int(raw_spacings.size + 1),
        "mean_r": float(np.mean(ratios)),
    }


def _case_digest(
    case: dict[str, Any],
    parameters: RingActivationParameters,
    *,
    detector_n: int,
    momentum: int,
    excitation_parity: int,
    reflection_parity: int | None,
    eigenvalue_count: int,
    solver_tolerance: float,
) -> str:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "spectrum_method_version": SPECTRUM_METHOD_VERSION,
        "case": case,
        "parameters": asdict(parameters),
        "detector_n": detector_n,
        "momentum": momentum,
        "excitation_parity": excitation_parity,
        "eigenvalue_count": eigenvalue_count,
        "solver_tolerance": solver_tolerance,
    }
    if reflection_parity is not None:
        payload["reflection_parity"] = reflection_parity
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:24]


def _cache_paths(cache_dir: Path, case_id: str) -> tuple[Path, Path]:
    return cache_dir / f"{case_id}.npz", cache_dir / f"{case_id}.json"


def _load_cached_spectrum(
    cache_dir: Path,
    case_id: str,
    digest: str,
) -> tuple[dict[str, np.ndarray], dict[str, Any]] | None:
    archive_path, metadata_path = _cache_paths(cache_dir, case_id)
    if not archive_path.is_file() or not metadata_path.is_file():
        return None
    try:
        metadata = _read_json(metadata_path)
        if metadata.get("case_digest") != digest:
            return None
        if metadata.get("archive_sha256") != _sha256(archive_path):
            return None
        with np.load(archive_path, allow_pickle=False) as archive:
            arrays = {name: np.asarray(archive[name]) for name in archive.files}
        return arrays, metadata
    except (KeyError, OSError, ValueError, json.JSONDecodeError):
        return None


def _save_spectrum_cache(
    cache_dir: Path,
    case_id: str,
    digest: str,
    spectrum: dict[str, Any],
    metadata: dict[str, Any],
) -> tuple[Path, Path]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    archive_path, metadata_path = _cache_paths(cache_dir, case_id)
    temporary = archive_path.with_suffix(".npz.tmp")
    with temporary.open("wb") as stream:
        np.savez_compressed(
            stream,
            energies=spectrum["energies"],
            unfolded_spacings=spectrum["unfolded_spacings"],
            spacing_ratios=spectrum["spacing_ratios"],
        )
    temporary.replace(archive_path)
    _atomic_json(
        metadata_path,
        {
            **metadata,
            "schema_version": SCHEMA_VERSION,
            "case_digest": digest,
            "archive_sha256": _sha256(archive_path),
            "completed": timestamp(),
        },
    )
    return archive_path, metadata_path


def compute_scan_spectra(
    config: dict[str, Any],
    cache_dir: Path,
    *,
    momentum: int,
    excitation_parity: int,
    reflection_parity: int | None = None,
    eigenvalue_count: int,
    solver_tolerance: float,
    resume: bool,
) -> tuple[list[dict[str, np.ndarray]], list[dict[str, Any]]]:
    """Compute or load one combined-sector spectrum for every scan case."""

    detector_n = int(config["detector_n"])
    arrays_by_case: list[dict[str, np.ndarray]] = []
    metadata_by_case: list[dict[str, Any]] = []
    for index, case in enumerate(config["cases"]):
        case_id = str(case["case_id"])
        parameters, provenance = load_spectrum_case(config, case)
        digest = _case_digest(
            case,
            parameters,
            detector_n=detector_n,
            momentum=momentum,
            excitation_parity=excitation_parity,
            reflection_parity=reflection_parity,
            eigenvalue_count=eigenvalue_count,
            solver_tolerance=solver_tolerance,
        )
        cached = _load_cached_spectrum(cache_dir, case_id, digest) if resume else None
        if cached is not None:
            arrays, metadata = cached
            metadata.setdefault(
                "residual_normalization",
                "applied_vector_norm_plus_abs_eigenvalue",
            )
            print(
                f"[{timestamp()}] case={case_id} spectrum=checkpoint_reused "
                f"mean_r={float(metadata['mean_r']):.6f}",
                flush=True,
            )
        else:
            print(
                f"[{timestamp()}] case={case_id} index={index + 1}/{len(config['cases'])} "
                "spectrum=start",
                flush=True,
            )
            basis, operator = build_combined_sector_operator(
                detector_n,
                parameters,
                momentum=momentum,
                excitation_parity=excitation_parity,
                reflection_parity=reflection_parity,
            )
            spectrum = central_sector_spectrum(
                operator,
                eigenvalue_count=eigenvalue_count,
                solver_tolerance=solver_tolerance,
            )
            metadata = {
                "case_id": case_id,
                "case_index": index,
                "description": str(case.get("description", case_id)),
                "parameters": asdict(parameters),
                "provenance": provenance,
                "detector_n": detector_n,
                "total_qubits": detector_n + 1,
                "momentum": momentum,
                "reflection_partner_momentum": (-momentum) % detector_n,
                "excitation_parity": excitation_parity,
                "reflection_parity": reflection_parity,
                "sector_dimension": int(basis.Ns),
                "eigenvalue_count": eigenvalue_count,
                "solver": "scipy.sparse.linalg.eigsh shift-invert",
                "solver_tolerance": solver_tolerance,
                "effective_solver_tolerance": spectrum[
                    "effective_solver_tolerance"
                ],
                "solver_attempt_count": spectrum["solver_attempt_count"],
                "sigma": spectrum["sigma"],
                "operator_infinity_norm_bound": spectrum[
                    "operator_infinity_norm_bound"
                ],
                "residual_normalization": spectrum["residual_normalization"],
                "runtime_seconds": spectrum["runtime_seconds"],
                "maximum_relative_residual": spectrum["maximum_relative_residual"],
                "orthogonality_error": spectrum["orthogonality_error"],
                "degeneracy_tolerance": spectrum["degeneracy_tolerance"],
                "resolved_level_count": spectrum["resolved_level_count"],
                "unfolded_spacing_count": int(spectrum["unfolded_spacings"].size),
                "mean_r": spectrum["mean_r"],
            }
            archive_path, _ = _save_spectrum_cache(
                cache_dir,
                case_id,
                digest,
                spectrum,
                metadata,
            )
            arrays = {
                "energies": np.asarray(spectrum["energies"]),
                "unfolded_spacings": np.asarray(spectrum["unfolded_spacings"]),
                "spacing_ratios": np.asarray(spectrum["spacing_ratios"]),
            }
            metadata["archive_sha256"] = _sha256(archive_path)
            print(
                f"[{timestamp()}] case={case_id} spectrum=finish "
                f"seconds={float(spectrum['runtime_seconds']):.3f} "
                f"mean_r={float(spectrum['mean_r']):.6f} "
                f"max_residual={float(spectrum['maximum_relative_residual']):.3e}",
                flush=True,
            )
        arrays_by_case.append(arrays)
        metadata_by_case.append(metadata)
    return arrays_by_case, metadata_by_case


def expected_all_sector_ids() -> tuple[str, ...]:
    """Return the 20 nonduplicated sector identifiers in PBS-array order."""

    sector_ids: list[str] = []
    for parity_label in ("even", "odd"):
        sector_ids.extend(
            (
                f"k00_{parity_label}_reflection_plus",
                f"k00_{parity_label}_reflection_minus",
            )
        )
        sector_ids.extend(f"k{momentum:02d}_{parity_label}" for momentum in range(1, 9))
    return tuple(sector_ids)


def load_all_sector_campaign(
    campaign_root: Path,
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Validate and aggregate a completed 20-sector Zeus campaign.

    Each sector is unfolded independently before its spacings are pooled.  The
    omitted ``k=9..16`` blocks are reflection-related exact spectral copies of
    ``k=8..1`` and are deliberately not counted a second time.
    """

    campaign_root = campaign_root.resolve()
    sectors_root = campaign_root / "sectors"
    if not sectors_root.is_dir():
        raise FileNotFoundError(f"campaign sectors directory is missing: {sectors_root}")
    cases = config.get("cases")
    if not isinstance(cases, list) or len(cases) != 20:
        raise ValueError("the plotting config must contain exactly 20 hz0 cases")
    case_ids = tuple(str(case["case_id"]) for case in cases)
    expected_ids = expected_all_sector_ids()
    present_ids = tuple(
        sorted(path.name for path in sectors_root.iterdir() if path.is_dir())
    )
    if set(present_ids) != set(expected_ids):
        raise ValueError(
            "sector directory mismatch: "
            f"missing={sorted(set(expected_ids) - set(present_ids))}, "
            f"unexpected={sorted(set(present_ids) - set(expected_ids))}"
        )

    arrays_by_case: dict[str, list[dict[str, np.ndarray]]] = {
        case_id: [] for case_id in case_ids
    }
    metadata_by_case: dict[str, list[dict[str, Any]]] = {
        case_id: [] for case_id in case_ids
    }
    completion_hashes: dict[str, str] = {}
    verified_artifact_count = 0
    for sector_id in expected_ids:
        sector_dir = sectors_root / sector_id
        complete_path = sector_dir / "COMPLETE.json"
        complete = _read_json(complete_path)
        if complete.get("status") != "complete":
            raise ValueError(f"{sector_id}: completion status is not complete")
        if complete.get("sector_id") != sector_id:
            raise ValueError(f"{sector_id}: completion marker sector_id mismatch")
        if int(complete.get("case_count", -1)) != len(case_ids):
            raise ValueError(f"{sector_id}: completion marker case_count mismatch")
        recorded_files = complete.get("files")
        if not isinstance(recorded_files, dict):
            raise ValueError(f"{sector_id}: completion marker files must be an object")
        expected_files = {"sector_summary.json"}
        for case_id in case_ids:
            expected_files.add(f"cases/{case_id}.json")
            expected_files.add(f"cases/{case_id}.npz")
        if set(recorded_files) != expected_files:
            raise ValueError(f"{sector_id}: completion artifact manifest mismatch")
        resolved_sector_dir = sector_dir.resolve()
        for relative_name, expected_hash in recorded_files.items():
            artifact = (sector_dir / str(relative_name)).resolve()
            if not artifact.is_relative_to(resolved_sector_dir):
                raise ValueError(f"{sector_id}: unsafe manifest path {relative_name!r}")
            if not artifact.is_file():
                raise FileNotFoundError(f"{sector_id}: missing artifact {relative_name}")
            actual_hash = _sha256(artifact)
            if actual_hash != str(expected_hash):
                raise ValueError(f"{sector_id}: SHA-256 mismatch for {relative_name}")
            verified_artifact_count += 1
        completion_hashes[sector_id] = _sha256(complete_path)

        summary = _read_json(sector_dir / "sector_summary.json")
        summary_cases = summary.get("cases")
        if not isinstance(summary_cases, list) or len(summary_cases) != len(case_ids):
            raise ValueError(f"{sector_id}: invalid sector summary case list")
        summary_by_id = {str(item.get("case_id")): item for item in summary_cases}
        if set(summary_by_id) != set(case_ids):
            raise ValueError(f"{sector_id}: sector summary case IDs mismatch")
        for case_id in case_ids:
            metadata_path = sector_dir / "cases" / f"{case_id}.json"
            archive_path = sector_dir / "cases" / f"{case_id}.npz"
            metadata = _read_json(metadata_path)
            if str(metadata.get("case_id")) != case_id:
                raise ValueError(f"{sector_id}/{case_id}: metadata case_id mismatch")
            if metadata.get("archive_sha256") != _sha256(archive_path):
                raise ValueError(f"{sector_id}/{case_id}: metadata archive hash mismatch")
            with np.load(archive_path, allow_pickle=False) as archive:
                required_arrays = {"energies", "unfolded_spacings", "spacing_ratios"}
                if set(archive.files) != required_arrays:
                    raise ValueError(f"{sector_id}/{case_id}: archive schema mismatch")
                arrays = {name: np.asarray(archive[name]) for name in archive.files}
            for name, values in arrays.items():
                if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
                    raise ValueError(
                        f"{sector_id}/{case_id}: invalid finite one-dimensional {name}"
                    )
            if int(metadata.get("unfolded_spacing_count", -1)) != int(
                arrays["unfolded_spacings"].size
            ):
                raise ValueError(f"{sector_id}/{case_id}: spacing count mismatch")
            arrays_by_case[case_id].append(arrays)
            metadata_by_case[case_id].append(metadata)

    aggregated_spectra: list[dict[str, Any]] = []
    aggregated_metadata: list[dict[str, Any]] = []
    for case_id in case_ids:
        sector_arrays = arrays_by_case[case_id]
        sector_metadata = metadata_by_case[case_id]
        if len(sector_arrays) != ALL_SECTOR_COUNT:
            raise ValueError(f"{case_id}: expected {ALL_SECTOR_COUNT} sector archives")
        pooled_spacings = np.concatenate(
            [item["unfolded_spacings"] for item in sector_arrays]
        )
        pooled_ratios = np.concatenate([item["spacing_ratios"] for item in sector_arrays])
        aggregated_spectra.append(
            {
                "unfolded_spacings": pooled_spacings,
                "spacing_ratios": pooled_ratios,
                "sector_unfolded_spacings": tuple(
                    item["unfolded_spacings"] for item in sector_arrays
                ),
            }
        )
        aggregated_metadata.append(
            {
                "case_id": case_id,
                "sector_count": len(sector_arrays),
                "eigenvalue_count_per_sector": sorted(
                    {int(item["eigenvalue_count"]) for item in sector_metadata}
                ),
                "unfolded_spacing_count": int(pooled_spacings.size),
                "spacing_ratio_count": int(pooled_ratios.size),
                "mean_r": float(np.mean(pooled_ratios)),
                "sector_mean_r_min": float(
                    min(float(item["mean_r"]) for item in sector_metadata)
                ),
                "sector_mean_r_max": float(
                    max(float(item["mean_r"]) for item in sector_metadata)
                ),
                "maximum_relative_residual": float(
                    max(float(item["maximum_relative_residual"]) for item in sector_metadata)
                ),
                "maximum_orthogonality_error": float(
                    max(float(item["orthogonality_error"]) for item in sector_metadata)
                ),
                "sectors": sector_metadata,
            }
        )
    campaign_metadata = {
        "campaign_root": str(campaign_root),
        "sector_count": len(expected_ids),
        "case_count": len(case_ids),
        "npz_count": len(expected_ids) * len(case_ids),
        "verified_artifact_count": verified_artifact_count,
        "completion_marker_sha256": completion_hashes,
        "sector_ids": list(expected_ids),
        "aggregation": (
            "Each exact sector is unfolded independently; all resulting spacings "
            "and adjacent-spacing ratios are then pooled with equal level weight."
        ),
    }
    return aggregated_spectra, aggregated_metadata, campaign_metadata


def plot_three_row_strip(
    path: Path,
    config: dict[str, Any],
    run_root: Path,
    spectra: list[dict[str, np.ndarray]],
    spectrum_metadata: list[dict[str, Any]],
) -> None:
    """Plot global projective diagnostics and combined-sector spacings."""

    cases = config["cases"]
    if len(cases) != len(spectra) or len(cases) != len(spectrum_metadata):
        raise ValueError("cases and spectrum records must have equal lengths")
    count = len(cases)
    figure, axes = plt.subplots(
        3,
        count,
        figsize=(4.5 * count, 12.0),
        gridspec_kw={
            "height_ratios": (1.0, 0.92, 0.92),
            "hspace": 0.10,
            "wspace": 0.22,
        },
        squeeze=False,
    )
    spacing_bins = np.linspace(0.0, 4.0, 21)
    density_maximum = 1.0
    histogram_values: list[np.ndarray] = []
    sector_histogram_values: list[list[np.ndarray]] = []
    for spectrum in spectra:
        density, _ = np.histogram(
            spectrum["unfolded_spacings"], bins=spacing_bins, density=True
        )
        histogram_values.append(density)
        density_maximum = max(density_maximum, float(np.max(density)))
        sector_densities: list[np.ndarray] = []
        for sector_spacings in spectrum.get("sector_unfolded_spacings", ()):
            sector_density, _ = np.histogram(
                sector_spacings, bins=spacing_bins, density=True
            )
            sector_densities.append(sector_density)
            density_maximum = max(density_maximum, float(np.max(sector_density)))
        sector_histogram_values.append(sector_densities)
    spacing_ylim = max(1.15, 1.08 * density_maximum)
    spacing_grid = np.linspace(0.0, 4.0, 500)

    for column, (case, spectrum, metadata, density, sector_densities) in enumerate(
        zip(
            cases,
            spectra,
            spectrum_metadata,
            histogram_values,
            sector_histogram_values,
            strict=True,
        )
    ):
        case_dir = run_root / str(case["case_id"])
        metrics = _read_json(case_dir / "activation_resolved_metrics.json")
        diagnostic = next(
            item for item in metrics["diagnostics"] if item["label"] == "global"
        )
        with np.load(
            case_dir / "activation_resolved_results.npz", allow_pickle=False
        ) as archive:
            edges = np.asarray(archive["global__edges"])
            centers = np.asarray(archive["global__centers"])
            occupied = np.asarray(archive["global__occupied"], dtype=bool)
            ax_p, ax_r, ax_s = axes[:, column]
            ax_p.stairs(
                np.asarray(archive["global__p_theta"]),
                edges,
                color=BLUE,
                fill=True,
                alpha=0.18,
                linewidth=0.9,
            )
            ax_p.stairs(
                np.asarray(archive["global__p_pi_minus_theta"]),
                edges,
                color=RED,
                fill=True,
                alpha=0.13,
                linewidth=0.9,
            )
            ax_p.plot(
                np.asarray(archive["global__fit_grid"]),
                np.asarray(archive["global__wg_density"]),
                color=MODEL_BLUE,
                linewidth=0.9,
            )
            ax_p.plot(
                np.asarray(archive["global__fit_grid"]),
                np.asarray(archive["global__wc_density"]),
                color=MODEL_ORANGE,
                linestyle="--",
                linewidth=0.9,
            )
            ratio = np.asarray(archive["global__ratio"])
            ax_r.plot(
                centers[occupied],
                ratio[occupied],
                "o-",
                color=PURPLE,
                markersize=1.7,
                linewidth=0.7,
            )
            ax_r.plot(
                centers,
                np.asarray(archive["global__born"]),
                "k--",
                linewidth=0.85,
            )

        centers_s = 0.5 * (spacing_bins[:-1] + spacing_bins[1:])
        for sector_density in sector_densities:
            ax_s.step(
                centers_s,
                sector_density,
                where="mid",
                color="#6f8fa6",
                linewidth=0.45,
                alpha=0.30,
            )
        ax_s.step(
            centers_s,
            density,
            where="mid",
            color="#303030",
            linewidth=1.25,
        )
        ax_s.plot(
            spacing_grid,
            poisson_spacing_distribution(spacing_grid),
            "k--",
            linewidth=0.85,
        )
        ax_s.plot(
            spacing_grid,
            wigner_spacing_distribution(spacing_grid, beta=1),
            color="#777777",
            linestyle=":",
            linewidth=1.0,
        )
        sector_count = int(metadata.get("sector_count", 1))
        spacing_annotation = (
            rf"$\langle\tilde r\rangle_{{\rm pool}}={float(metadata['mean_r']):.3f}$"
            + "\n"
            + rf"{sector_count} sectors; $n_s={int(np.asarray(spectrum['unfolded_spacings']).size)}$"
            if sector_count > 1
            else rf"$\langle\tilde r\rangle={float(metadata['mean_r']):.3f}$"
            + "\n"
            + rf"$n_s={int(np.asarray(spectrum['unfolded_spacings']).size)}$"
        )
        ax_s.text(
            0.96,
            0.92,
            spacing_annotation,
            transform=ax_s.transAxes,
            ha="right",
            va="top",
            fontsize=6.7,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 0.5},
        )

        scan_ratio = float(case["hz0_over_hz"])
        ax_p.set_title(
            rf"$h_{{z0}}/h_z={_ratio_title(scan_ratio)}$", fontsize=8.5, pad=4
        )
        ax_r.text(
            0.04,
            0.07,
            rf"$S={float(diagnostic['S_born']):.3f}$"
            + "\n"
            + rf"RMSE$={float(diagnostic['born_RMSE_occupied']):.3f}$",
            transform=ax_r.transAxes,
            fontsize=6.7,
            va="bottom",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 0.5},
        )
        ax_p.set_xlim(0.0, np.pi)
        ax_p.set_ylim(bottom=0.0)
        ax_r.set_xlim(0.0, np.pi)
        ax_r.set_ylim(-0.04, 1.04)
        ax_r.set_xticks((0.0, np.pi / 2.0, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
        ax_s.set_xlim(0.0, 4.0)
        ax_s.set_ylim(0.0, spacing_ylim)
        ax_s.set_xticks((0.0, 1.0, 2.0, 3.0, 4.0))
        ax_s.set_xlabel(r"unfolded spacing $s$", fontsize=8)
        ax_p.tick_params(labelbottom=False, labelsize=7)
        ax_r.tick_params(labelbottom=False, labelsize=7)
        ax_s.tick_params(labelsize=7)
        for axis in (ax_p, ax_r, ax_s):
            axis.grid(alpha=0.14)
        if column == 0:
            ax_p.set_ylabel("density")
            ax_r.set_ylabel(r"$R(\theta)$")
            ax_s.set_ylabel(r"$P(s)$")
        else:
            ax_p.set_ylabel("")
            ax_r.set_ylabel("")
            ax_s.set_ylabel("")

    first_metadata = spectrum_metadata[0]
    all_sector_plot = int(first_metadata.get("sector_count", 1)) > 1
    handles = [
        Line2D([], [], color=BLUE, linewidth=5, alpha=0.35, label=r"$P(\theta)$"),
        Line2D([], [], color=RED, linewidth=5, alpha=0.30, label=r"$P(\pi-\theta)$"),
        Line2D([], [], color=MODEL_BLUE, label="wrapped Gaussian"),
        Line2D([], [], color=MODEL_ORANGE, linestyle="--", label="wrapped Cauchy"),
        Line2D([], [], color=PURPLE, marker="o", markersize=3, label=r"$R(\theta)$"),
        Line2D([], [], color="black", linestyle="--", label=r"$\cos^2(\theta/2)$ / Poisson"),
        Line2D([], [], color="#777777", linestyle=":", label="GOE"),
    ]
    if all_sector_plot:
        handles.extend(
            (
                Line2D([], [], color="#6f8fa6", alpha=0.45, label="resolved sectors"),
                Line2D([], [], color="#303030", linewidth=1.5, label="pooled sectors"),
            )
        )
    figure.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.925),
        ncol=len(handles),
        frameon=False,
        fontsize=9,
    )
    if all_sector_plot:
        subtitle = (
            rf"$N_D={int(config['detector_n'])}$; all {int(first_metadata['sector_count'])} "
            "nonduplicated exact sectors; 512 central eigenvalues per sector"
        )
        footer = (
            "Third row: 20 thin sector-resolved histograms plus their pooled distribution; "
            "translation, total-excitation parity, and k=0 reflection resolved; omitted k/-k "
            "copies are not duplicated; cubic unfolding with 10% edge trim."
        )
    else:
        parity_label = (
            "even" if int(first_metadata["excitation_parity"]) == 0 else "odd"
        )
        reflection_parity = first_metadata.get("reflection_parity")
        reflection_label = (
            ""
            if reflection_parity is None
            else rf", reflection $p={int(reflection_parity):+d}$"
        )
        subtitle = (
            rf"$N_D={int(config['detector_n'])}$; combined sector "
            + rf"$k={int(first_metadata['momentum'])}$, {parity_label} total-excitation parity"
            + reflection_label
            + "; "
            + rf"{int(first_metadata['eigenvalue_count'])} central eigenvalues"
        )
        footer = (
            "Third row: one nonduplicated reflection-related momentum copy of the full "
            "qubit-detector Hamiltonian; exact translation and total-excitation parity "
            "resolved; cubic unfolding with 10% edge trim."
        )
    figure.suptitle(
        "Central-field scan: global projective diagnostics and full-Hamiltonian spacings\n"
        + subtitle,
        fontsize=14,
        y=0.995,
    )
    figure.text(
        0.5,
        0.012,
        footer,
        ha="center",
        fontsize=9,
    )
    figure.subplots_adjust(left=0.012, right=0.998, bottom=0.075, top=0.86)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    result.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    result.add_argument("--output-name", default=DEFAULT_OUTPUT_NAME)
    result.add_argument("--cache-dir", type=Path)
    result.add_argument(
        "--all-sector-root",
        type=Path,
        help="completed 20-sector Zeus campaign to validate and aggregate",
    )
    result.add_argument("--momentum", type=int, default=1)
    result.add_argument(
        "--excitation-parity",
        type=int,
        choices=(0, 1),
        default=0,
        help="0 selects even and 1 selects odd total excitation parity",
    )
    result.add_argument(
        "--reflection-parity",
        type=int,
        choices=(-1, 1),
        help="resolve k=0 into physical reflection eigenvalue -1 or +1",
    )
    result.add_argument("--eigenvalue-count", type=int, default=512)
    result.add_argument("--solver-tolerance", type=float, default=1.0e-10)
    result.add_argument("--no-resume", action="store_true")
    return result


def main() -> None:
    args = parser().parse_args()
    config_path = args.config.resolve()
    run_root = args.run_root.resolve()
    output_dir = args.output_dir.resolve()
    cache_dir = (
        args.cache_dir.resolve()
        if args.cache_dir
        else run_root
        / (
            f"combined_full_spacing_k{int(args.momentum)}_"
            + ("even" if int(args.excitation_parity) == 0 else "odd")
            + (
                ""
                if args.reflection_parity is None
                else f"_reflection_{int(args.reflection_parity):+d}"
            )
        )
    )
    config = _read_json(config_path)
    if not run_root.is_dir():
        raise FileNotFoundError(f"scan run root does not exist: {run_root}")
    campaign_metadata: dict[str, Any] | None = None
    if args.all_sector_root is not None:
        spectra, spectrum_metadata, campaign_metadata = load_all_sector_campaign(
            args.all_sector_root,
            config,
        )
    else:
        spectra, spectrum_metadata = compute_scan_spectra(
            config,
            cache_dir,
            momentum=int(args.momentum),
            excitation_parity=int(args.excitation_parity),
            reflection_parity=args.reflection_parity,
            eigenvalue_count=int(args.eigenvalue_count),
            solver_tolerance=float(args.solver_tolerance),
            resume=not args.no_resume,
        )
    output_path = output_dir / str(args.output_name)
    plot_three_row_strip(
        output_path,
        config,
        run_root,
        spectra,
        spectrum_metadata,
    )
    provenance_path = output_path.with_name(output_path.stem + "_metadata.json")
    _atomic_json(
        provenance_path,
        {
            "schema_version": SCHEMA_VERSION,
            "created": timestamp(),
            "figure": str(output_path),
            "figure_sha256": _sha256(output_path),
            "config": str(config_path),
            "config_sha256": _sha256(config_path),
            "script": str(Path(__file__).resolve()),
            "script_sha256": _sha256(Path(__file__).resolve()),
            "run_root": str(run_root),
            "cache_dir": str(cache_dir),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "case_count": len(config["cases"]),
            "sector_definition": {
                "momentum": int(args.momentum),
                "reflection_partner_momentum": (-int(args.momentum))
                % int(config["detector_n"]),
                "excitation_parity": int(args.excitation_parity),
                "reflection_parity": args.reflection_parity,
                "note": (
                    "The nonzero k and -k blocks are reflection-related exact "
                    "spectral copies; only k is plotted. Reflection and complex "
                    "conjugation each exchange the blocks, while their antiunitary "
                    "product acts within one block, so the applicable WD reference "
                    "is GOE."
                ),
            },
            "spectrum_method": {
                "version": SPECTRUM_METHOD_VERSION,
                "eigenvalue_count": int(args.eigenvalue_count),
                "solver": "scipy.sparse.linalg.eigsh shift-invert",
                "solver_tolerance": float(args.solver_tolerance),
                "unfolding_degree": 3,
                "unfolding_trim_fraction": 0.1,
            },
            "cases": spectrum_metadata,
            "all_sector_campaign": campaign_metadata,
        },
    )
    print(
        f"[{timestamp()}] figure={output_path} metadata={provenance_path}",
        flush=True,
    )


if __name__ == "__main__":
    main()
