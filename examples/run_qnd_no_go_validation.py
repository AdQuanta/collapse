"""Validate the strict pointer-QND pole-only root geometry at small sizes.

The tested family contains an interacting and internally noncommuting detector,
but every qubit--detector term commutes with the central pointer ``Z_0``.  The
script checks the commutator and propagator blocks directly, then uses the
homogeneous production and forward pencils.  It writes only small derived
validation files and performs no production-scale scan.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
import tempfile

import numpy as np
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "collapse_matplotlib_cache"),
)

from collapse.gleason_diagnostics import diagnose_labeled_bloch_histogram
from collapse.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy
from collapse.pauli import build_pauli_z
from collapse.projective_roots import (
    bloch_vectors_from_homogeneous,
    forward_pole_root_spectrum,
    production_root_spectrum,
    split_qubit_first_blocks,
)


DEFAULT_OUTPUT = (
    ROOT
    / "work"
    / "hamiltonian_classification_20260815"
    / "qnd_no_go_validation"
)


def _model(detector_n: int) -> SinglePixelHamiltonianNumpy:
    return SinglePixelHamiltonianNumpy(
        N_pixel=detector_n,
        J=1.0,
        Jpm=0.25,
        Jx=0.0,
        Jy=0.0,
        Jz=0.30,
        Jzx=0.20,
        Jcpm=0.0,
        hx=0.17,
        hz=0.10,
        hx0=0.0,
        hz0=0.10,
        connectivity="ring",
        central_coupling="all",
        seed=20260815,
    )


def _pole_distance(vectors: np.ndarray, pole: np.ndarray) -> float:
    return float(np.max(np.linalg.norm(vectors - pole[None, :], axis=1)))


def evaluate_size(detector_n: int, time: float) -> dict[str, object]:
    hamiltonian = _model(detector_n).generate()
    total_qubits = detector_n + 1
    dimension = hamiltonian.shape[0]
    central_z = build_pauli_z(0, total_qubits)
    commutator = hamiltonian @ central_z - central_z @ hamiltonian
    commutator_relative = float(
        np.linalg.norm(commutator)
        / max(np.linalg.norm(hamiltonian) * np.linalg.norm(central_z), 1.0)
    )

    unitary = expm(-1.0j * hamiltonian * time)
    unitarity_residual = float(
        np.linalg.norm(unitary.conj().T @ unitary - np.eye(dimension))
        / np.sqrt(dimension)
    )
    blocks = split_qubit_first_blocks(unitary)
    off_diagonal_relative = float(
        np.hypot(np.linalg.norm(blocks.B), np.linalg.norm(blocks.C))
        / np.linalg.norm(unitary)
    )

    production = production_root_spectrum(
        unitary,
        audit_root_indices=[0],
        assess_regularity=True,
        duplicate_tolerance=1.0e-10,
    )
    forward_zero = forward_pole_root_spectrum(unitary, outcome=0)
    forward_one = forward_pole_root_spectrum(unitary, outcome=1)
    production_vectors = bloch_vectors_from_homogeneous(
        production.alpha,
        production.beta,
    )
    forward_zero_vectors = bloch_vectors_from_homogeneous(
        forward_zero.alpha,
        forward_zero.beta,
    )
    forward_one_vectors = bloch_vectors_from_homogeneous(
        forward_one.alpha,
        forward_one.beta,
    )
    histogram = diagnose_labeled_bloch_histogram(
        production_vectors,
        n_mu=8,
        n_phi=16,
        require_full_coverage=True,
    )
    root_audit = production.root_audits[0]
    regularity = production.regularity_audit
    assert regularity is not None
    return {
        "family": "strict_qnd_interacting_ring",
        "detector_n": detector_n,
        "total_qubits": total_qubits,
        "dimension": dimension,
        "detector_dimension": dimension // 2,
        "time": time,
        "parameters": {
            "J": 1.0,
            "Jpm": 0.25,
            "Jx": 0.0,
            "Jy": 0.0,
            "Jz": 0.30,
            "Jzx": 0.20,
            "Jcpm": 0.0,
            "hx": 0.17,
            "hz": 0.10,
            "hx0": 0.0,
            "hz0": 0.10,
            "connectivity": "ring",
            "central_coupling": "all",
        },
        "commutator_relative_frobenius": commutator_relative,
        "unitarity_residual": unitarity_residual,
        "off_diagonal_block_relative_frobenius": off_diagonal_relative,
        "root_count": int(production.theta.size),
        "finite_roots": int(np.count_nonzero(production.finite)),
        "infinite_roots": int(np.count_nonzero(production.infinite)),
        "indeterminate_roots": int(np.count_nonzero(production.indeterminate)),
        "maximum_production_theta": float(np.nanmax(production.theta)),
        "maximum_qz_backward_residual": production.maximum_homogeneous_residual,
        "maximum_qz_left_backward_residual": production.maximum_left_homogeneous_residual,
        "pencil_regularity_status": regularity.status,
        "representative_root_nullity": root_audit.nullity,
        "largest_projective_root_multiplicity": (
            production.duplicate_diagnostics.largest_multiplicity
        ),
        "production_north_pole_max_distance": _pole_distance(
            production_vectors,
            np.array([0.0, 0.0, 1.0]),
        ),
        "forward_outcome_0_north_pole_max_distance": _pole_distance(
            forward_zero_vectors,
            np.array([0.0, 0.0, 1.0]),
        ),
        "forward_outcome_1_south_pole_max_distance": _pole_distance(
            forward_one_vectors,
            np.array([0.0, 0.0, -1.0]),
        ),
        "equal_area_coverage": histogram.coverage,
        "full_sphere_harmonics_available": histogram.diagnostics is not None,
        "claim_status": "VERIFIED NUMERICALLY",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--detector-n", type=int, nargs="+", default=[2, 3, 4, 5, 6])
    parser.add_argument("--time", type=float, default=3.7)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if any(size < 2 for size in args.detector_n):
        raise ValueError("all detector sizes must be at least two")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [evaluate_size(size, args.time) for size in args.detector_n]
    manifest = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "analytic_statement": (
            "If [H,Z0]=0, U is block diagonal in the Z0 basis. The production "
            "pencil has C=0 and hence only z=0 (north-pole) roots, while the "
            "second forward label is the antipodal south pole, counted with "
            "detector-space algebraic multiplicity."
        ),
        "analytic_claim_status": "PROVED ANALYTICALLY",
        "selection_measure_status": "not supplied",
        "rows": rows,
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }
    temporary = output_dir / "manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output_dir / "manifest.json")

    csv_path = output_dir / "qnd_size_validation.csv"
    fields = [
        key for key in rows[0] if key != "parameters"
    ] + ["parameters"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            record = dict(row)
            record["parameters"] = json.dumps(record["parameters"], sort_keys=True)
            writer.writerow(record)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

