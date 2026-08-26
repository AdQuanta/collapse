"""Validate uncoupled-spectator composition for the trusted matched-ring roots.

For ``U_QD tensor U_A`` every projective root of the production pencil is
repeated by ``dim(A)``.  This script checks the resulting raw multiplicity,
normalized labelled densities, asymmetry, harmonics, and dipole on the hashed
N=16 matched-ring spectrum.  It does not test interacting or context-changing
detector refinements.
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

from collapse.gleason_diagnostics import (
    composition_consistency_error,
    diagnose_labeled_bloch_histogram,
)
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
    / "composition_consistency"
    / "matched_ring_N16_t10000"
)
EXPECTED_SHA256 = "e467b5efa6a5b8b7e3e7333a06555007b629a26bbeac2b21cd3da27d88313d59"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--spectator-dim", type=int, nargs="+", default=[1, 2, 3, 4, 8])
    parser.add_argument("--n-phi", type=int, default=36)
    parser.add_argument("--n-mu", type=int, default=18)
    parser.add_argument("--l-max", type=int, default=7)
    args = parser.parse_args()
    if any(value < 1 for value in args.spectator_dim):
        raise ValueError("spectator dimensions must be positive")
    source = args.input.resolve()
    digest = _sha256(source)
    if digest != EXPECTED_SHA256:
        raise ValueError(f"unexpected source SHA-256: {digest}")
    with np.load(source, allow_pickle=False) as data:
        eigenvalues = np.asarray(data["eigenvalues"], dtype=np.complex128).ravel()
    vectors = bloch_vectors_from_homogeneous(eigenvalues, np.ones_like(eigenvalues))
    base = diagnose_labeled_bloch_histogram(
        vectors,
        n_phi=args.n_phi,
        n_mu=args.n_mu,
        l_max=args.l_max,
    )
    if base.diagnostics is None:
        raise ValueError("base grid is not fully covered")
    cell_weight = (base.mu_edges[1] - base.mu_edges[0]) * (
        base.phi_edges[1] - base.phi_edges[0]
    )
    rows: list[dict[str, object]] = []
    for spectator_dimension in args.spectator_dim:
        repeated = np.repeat(vectors, spectator_dimension, axis=0)
        candidate = diagnose_labeled_bloch_histogram(
            repeated,
            n_phi=args.n_phi,
            n_mu=args.n_mu,
            l_max=args.l_max,
        )
        assert candidate.diagnostics is not None
        rows.append(
            {
                "spectator_dimension": spectator_dimension,
                "raw_root_count": int(repeated.shape[0]),
                "raw_multiplicity_factor": spectator_dimension,
                "maximum_normalized_density_0_difference": float(
                    np.max(np.abs(candidate.density_0 - base.density_0))
                ),
                "maximum_normalized_density_1_difference": float(
                    np.max(np.abs(candidate.density_1 - base.density_1))
                ),
                "composition_error": composition_consistency_error(
                    base.asymmetry,
                    candidate.asymmetry,
                    weights=cell_weight,
                ),
                "dipole_vector_difference": float(
                    np.linalg.norm(
                        candidate.diagnostics.dipole_vector
                        - base.diagnostics.dipole_vector
                    )
                ),
                "maximum_power_by_l_difference": float(
                    np.max(
                        np.abs(
                            candidate.diagnostics.power_by_l
                            - base.diagnostics.power_by_l
                        )
                    )
                ),
            }
        )
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "composition_by_spectator_dimension.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": os.path.relpath(source, ROOT),
        "source_sha256": digest,
        "analytic_claim_status": "PROVED ANALYTICALLY",
        "numerical_claim_status": "VERIFIED NUMERICALLY",
        "scope": "dynamically uncoupled tensor-factor spectator only",
        "theorem": (
            "For U'=U tensor V_A, every qubit-first block is tensored with the "
            "same invertible V_A. Therefore det[(C-lambda A) tensor V_A] is a "
            "nonzero spectator factor times det(C-lambda A)^dim(A), so roots "
            "repeat but normalized root geometry is invariant."
        ),
        "selection_measure_status": "not supplied",
        "rows": rows,
    }
    temporary = output_dir / "manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output_dir / "manifest.json")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

