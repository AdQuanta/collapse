"""Recompute a common full-sphere table for the 24 matched-ring spectra.

The source list is the audited post-cutoff matched-field table.  Every raw NPZ
is reloaded, hashed, checked against its stored polar score, and analyzed on one
common low-resolution equal-area grid suitable for all N=11--16 spectra.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
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

from core.born import diagnostics_from_radii
from core.gleason_diagnostics import diagnose_labeled_bloch_histogram
from core.projective_roots import bloch_vectors_from_homogeneous


DEFAULT_INPUT = (
    ROOT
    / "reports"
    / "zeus_single_pixel_analysis_2026-07-16"
    / "jointly_gated_born_candidates.csv"
)
DEFAULT_OUTPUT = (
    ROOT
    / "work"
    / "hamiltonian_classification_20260815"
    / "matched_ring_reproduction"
    / "scaling"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_source(value: str) -> Path:
    normalized = value.replace("\\", os.sep).replace("/", os.sep)
    path = Path(normalized)
    return path if path.is_absolute() else ROOT / path


def _result_row(source_row: dict[str, str], n_phi: int, n_mu: int, l_max: int):
    source = _resolve_source(source_row["source_npz"])
    if not source.is_file():
        raise FileNotFoundError(source)
    with np.load(source, allow_pickle=False) as data:
        eigenvalues = np.asarray(data["eigenvalues"], dtype=np.complex128).ravel()
    if not np.all(np.isfinite(eigenvalues.real) & np.isfinite(eigenvalues.imag)):
        raise ValueError(f"{source} contains nonfinite affine roots")
    detector_n = int(float(source_row["detector_n"]))
    expected_count = 2**detector_n
    if eigenvalues.size != expected_count:
        raise ValueError(
            f"{source} has {eigenvalues.size} roots, expected {expected_count}"
        )
    polar = diagnostics_from_radii(np.abs(eigenvalues))
    stored_score = float(source_row["S_born"])
    score_error = abs(polar.born_similarity - stored_score)
    if score_error > 1.0e-12:
        raise ValueError(f"stored S_born mismatch {score_error} for {source}")
    vectors = bloch_vectors_from_homogeneous(eigenvalues, np.ones_like(eigenvalues))
    histogram = diagnose_labeled_bloch_histogram(
        vectors,
        n_phi=n_phi,
        n_mu=n_mu,
        l_max=l_max,
        require_full_coverage=True,
        harmonic_estimator="weighted_least_squares",
    )
    diagnostics = histogram.diagnostics
    parameters = {
        "J": float(source_row["J"]),
        "Jpm": float(source_row["Jpm"]),
        "Jx_source": float(source_row["Jx"]),
        "Jx_edge": float(source_row["Jx"]) / np.sqrt(detector_n),
        "hz": float(source_row["hz"]),
        "hz0": float(source_row["hz0"]),
        "connectivity": "ring",
        "central_coupling": "all",
    }
    return {
        "family": "matched_field_ring",
        "N": detector_n,
        "dimension": 2 ** (detector_n + 1),
        "detector_dimension": expected_count,
        "time": float(source_row["t"]),
        "parameters": json.dumps(parameters, sort_keys=True),
        "seed": "",
        "root_count": int(eigenvalues.size),
        "qz_valid": False,
        "qz_status": "stored_affine_roots_not_QZ_audited",
        "coverage": histogram.coverage,
        "density_ratio_cross_residual": (
            histogram.born_density_ratio_cross_residual
            if diagnostics is not None else np.nan
        ),
        "epsilon_antipodal": (
            diagnostics.epsilon_antipodal if diagnostics is not None else np.nan
        ),
        "epsilon_B": (
            diagnostics.born_rms_density_weighted if diagnostics is not None else np.nan
        ),
        "epsilon_B_definition": "total-root-density-weighted RMS of a-n.r",
        "higher_harmonic_leakage": (
            diagnostics.higher_odd_harmonic_leakage
            if diagnostics is not None
            else np.nan
        ),
        "dipole_sharpness": (
            diagnostics.dipole_sharpness if diagnostics is not None else np.nan
        ),
        "axis_fidelity": (
            diagnostics.axis_fidelity if diagnostics is not None else np.nan
        ),
        "P1_over_Podd": (
            diagnostics.p1_over_podd if diagnostics is not None else np.nan
        ),
        "composition_error": np.nan,
        "polar_S_born": polar.born_similarity,
        "stored_S_born_absolute_error": score_error,
        "n_phi": n_phi,
        "n_mu": n_mu,
        "l_max": l_max,
        "harmonic_estimator": "weighted_least_squares",
        "antipodal_status": "label_1_histogram_constructed_by_exact_antipode",
        "source_npz": os.path.relpath(source, ROOT),
        "source_sha256": _sha256(source),
        "status": (
            "SUPPORTED NUMERICALLY"
            if diagnostics is not None
            else "INSUFFICIENT FULL-SPHERE COVERAGE"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--n-phi", type=int, default=16)
    parser.add_argument("--n-mu", type=int, default=8)
    parser.add_argument("--l-max", type=int, default=7)
    args = parser.parse_args()

    with args.input.resolve().open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle))
    if len(source_rows) != 24:
        raise ValueError(f"expected 24 matched rows, found {len(source_rows)}")
    rows = [
        _result_row(row, args.n_phi, args.n_mu, args.l_max)
        for row in source_rows
    ]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / "matched_ring_full_sphere_scaling.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_table": os.path.relpath(args.input.resolve(), ROOT),
        "source_table_sha256": _sha256(args.input.resolve()),
        "row_count": len(rows),
        "grid": {"n_phi": args.n_phi, "n_mu": args.n_mu, "l_max": args.l_max},
        "full_coverage_rows": sum(float(row["coverage"]) == 1.0 for row in rows),
        "qz_limitation": (
            "Raw files contain affine roots only. Full homogeneous QZ validation "
            "requires recomputation from propagator blocks."
        ),
        "selection_measure_status": "not supplied",
        "output_csv": output_csv.name,
    }
    temporary = output_dir / "manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output_dir / "manifest.json")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
