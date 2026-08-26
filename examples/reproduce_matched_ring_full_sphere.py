"""Reproduce full-sphere diagnostics from a trusted matched-ring root file.

This is post-processing only.  It validates the input hash, preserves the
production-root convention, constructs the exact labelled antipodes, evaluates
several declared equal-area resolutions, and writes machine-readable source
data.  It does not interpret algebraic root counts as operational
probabilities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "collapse_matplotlib_cache"),
)

from collapse.born import diagnostics_from_radii
from collapse.gleason_diagnostics import diagnose_labeled_bloch_histogram
from collapse.projective_roots import bloch_vectors_from_homogeneous


DEFAULT_INPUT = (
    ROOT
    / "work"
    / "zeus_single_pixel_atlas_scaling_2026-07-14"
    / "hz0"
    / "N16"
    / "raw"
    / "N16"
    / "hz0_+0.1000"
    / "raw_t10000.npz"
)
DEFAULT_OUTPUT = (
    ROOT
    / "work"
    / "hamiltonian_classification_20260815"
    / "matched_ring_reproduction"
    / "N16_t10000"
)
DEFAULT_SHA256 = "e467b5efa6a5b8b7e3e7333a06555007b629a26bbeac2b21cd3da27d88313d59"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_resolution(value: str) -> tuple[int, int]:
    try:
        phi_text, mu_text = value.lower().split("x", maxsplit=1)
        n_phi, n_mu = int(phi_text), int(mu_text)
    except (ValueError, AttributeError) as exc:
        raise argparse.ArgumentTypeError("resolution must have form PHIxMU") from exc
    if n_phi < 2 or n_phi % 2 or n_mu < 1:
        raise argparse.ArgumentTypeError("PHI must be positive and even; MU must be positive")
    return n_phi, n_mu


def _json_value(value: np.ndarray | np.generic | object) -> object:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _diagnostic_record(result) -> dict[str, object]:
    diagnostics = result.diagnostics
    if diagnostics is None:
        return {
            "coverage": result.coverage,
            "full_sphere_diagnostics_available": False,
        }
    return {
        "coverage": result.coverage,
        "full_sphere_diagnostics_available": True,
        "density_ratio_cross_residual": (
            result.born_density_ratio_cross_residual
        ),
        "epsilon_antipodal": diagnostics.epsilon_antipodal,
        "born_rms_area": diagnostics.born_rms_area,
        "born_rms_density_weighted": diagnostics.born_rms_density_weighted,
        "epsilon_born_relative_area": diagnostics.epsilon_born,
        "epsilon_born_relative_density_weighted": (
            diagnostics.epsilon_born_density_weighted
        ),
        "higher_harmonic_leakage": diagnostics.higher_odd_harmonic_leakage,
        "dipole_vector": diagnostics.dipole_vector.tolist(),
        "dipole_sharpness": diagnostics.dipole_sharpness,
        "axis_fidelity": diagnostics.axis_fidelity,
        "axis_defined": diagnostics.axis_defined,
        "P1_over_Podd": diagnostics.p1_over_podd,
        "even_fraction_of_total_power": diagnostics.even_fraction_of_total_power,
        "power_by_l": diagnostics.power_by_l.tolist(),
        "quadrature": diagnostics.quadrature,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--expected-sha256", default=DEFAULT_SHA256)
    parser.add_argument(
        "--resolution",
        type=_parse_resolution,
        action="append",
        default=None,
        help="Equal-area PHIxMU grid; repeat for sensitivity (default: 24x12, 36x18, 48x24)",
    )
    parser.add_argument("--l-max", type=int, default=7)
    args = parser.parse_args()

    input_path = args.input.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    digest = _sha256(input_path)
    if args.expected_sha256 and digest.lower() != args.expected_sha256.lower():
        raise ValueError(
            f"input SHA-256 mismatch: expected {args.expected_sha256}, found {digest}"
        )
    resolutions = args.resolution or [(24, 12), (36, 18), (48, 24)]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with np.load(input_path, allow_pickle=False) as data:
        if "eigenvalues" not in data:
            raise KeyError("input NPZ has no 'eigenvalues' array")
        eigenvalues = np.asarray(data["eigenvalues"], dtype=np.complex128).ravel()
        metadata = {
            key: _json_value(data[key])
            for key in data.files
            if np.asarray(data[key]).ndim == 0 and key != "eigenvalues"
        }
    finite = np.isfinite(eigenvalues.real) & np.isfinite(eigenvalues.imag)
    if not np.all(finite):
        raise ValueError(
            "stored affine roots include nonfinite values; homogeneous QZ data are required "
            "to classify infinity rather than filtering it"
        )
    roots_0 = bloch_vectors_from_homogeneous(eigenvalues, np.ones_like(eigenvalues))
    if not np.allclose(np.linalg.norm(roots_0, axis=1), 1.0, atol=1.0e-12):
        raise ValueError("Bloch mapping failed unit-radius validation")

    polar = diagnostics_from_radii(np.abs(eigenvalues))
    records: list[dict[str, object]] = []
    for n_phi, n_mu in resolutions:
        result = diagnose_labeled_bloch_histogram(
            roots_0,
            n_mu=n_mu,
            n_phi=n_phi,
            l_max=args.l_max,
            target_axis=np.array([0.0, 0.0, 1.0]),
            pseudocount=0.0,
            require_full_coverage=True,
            harmonic_estimator="weighted_least_squares",
        )
        legacy = diagnose_labeled_bloch_histogram(
            roots_0,
            n_mu=n_mu,
            n_phi=n_phi,
            l_max=args.l_max,
            target_axis=np.array([0.0, 0.0, 1.0]),
            pseudocount=0.0,
            require_full_coverage=True,
            harmonic_estimator="midpoint",
        )
        record = {
            "n_phi": n_phi,
            "n_mu": n_mu,
            "pseudocount": 0.0,
            "harmonic_estimator": "weighted_least_squares",
            **_diagnostic_record(result),
            "legacy_midpoint_reproduction": _diagnostic_record(legacy),
        }
        records.append(record)
        diagnostics = result.diagnostics
        np.savez_compressed(
            output_dir / f"full_sphere_source_phi{n_phi}_mu{n_mu}.npz",
            mu_edges=result.mu_edges,
            phi_edges=result.phi_edges,
            counts_0=result.counts_0,
            counts_1=result.counts_1,
            density_0=result.density_0,
            density_1=result.density_1,
            total_density=result.total_density,
            asymmetry=result.asymmetry,
            occupied=result.occupied,
            power_by_l=(
                diagnostics.power_by_l if diagnostics is not None else np.array([])
            ),
            legacy_midpoint_power_by_l=(
                legacy.diagnostics.power_by_l
                if legacy.diagnostics is not None
                else np.array([])
            ),
        )

    manifest = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "postprocessing_only": True,
        "source_file": os.path.relpath(input_path, ROOT),
        "source_sha256": digest,
        "root_count": int(eigenvalues.size),
        "all_roots_finite_in_stored_affine_file": True,
        "production_convention": "C v = lambda A v for U(+t)",
        "forward_interpretation": (
            "The stored U(+t) production roots equal forward outcome-0 roots of U(-t). "
            "For this real Hamiltonian, same-time U(+t) forward roots are obtained by "
            "azimuthal reflection (complex conjugation)."
        ),
        "label_1_construction": "exact Bloch antipodes of label-0 root bins",
        "selection_measure_status": "not supplied; root multiplicity is geometric only",
        "npz_metadata": metadata,
        "polar_diagnostics": {
            "S_born": polar.born_similarity,
            "mean_abs_ratio_error": polar.mean_abs_ratio_error,
            "reciprocity_error": polar.reciprocity_error,
            "tail_density_exponent": polar.tail_density_exponent,
        },
        "full_sphere_resolution_sensitivity": records,
        "harmonic_estimator_note": (
            "Primary values use weighted least squares on cell centers. The nested "
            "legacy_midpoint_reproduction values reproduce the prior manuscript "
            "quadrature and are retained only for auditability."
        ),
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }
    temporary = output_dir / "manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output_dir / "manifest.json")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
