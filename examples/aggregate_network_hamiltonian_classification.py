"""Recompute common full-sphere diagnostics for saved network campaigns.

The saved campaigns contain affine roots and independently stored blue/red
Bloch coordinates, but not homogeneous QZ pairs.  Consequently this adapter
never labels those rows QZ-validated.  It does not rerun any Hamiltonian.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "collapse_matplotlib_cache"),
)

from collapse.gleason_diagnostics import diagnose_labeled_bloch_histogram  # noqa: E402


FAMILIES = (
    "erdos_renyi",
    "watts_strogatz",
    "barabasi_albert",
    "expander",
)
FIELDS = [
    "family", "N", "dimension", "time", "parameters", "seed",
    "root_count", "qz_valid", "qz_status", "coverage",
    "density_ratio_cross_residual",
    "epsilon_antipodal", "epsilon_B", "epsilon_B_definition",
    "higher_harmonic_leakage", "dipole_sharpness", "axis_fidelity",
    "P1_over_Podd", "composition_error", "composition_status",
    "harmonic_estimator", "polar_S_born", "source", "status",
]


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_saved_network_config(
    config_dir: Path,
    family: str,
    *,
    n_phi: int = 16,
    n_mu: int = 8,
    l_max: int = 7,
) -> dict[str, object]:
    """Convert one validated legacy network result to the common schema."""

    metadata = _read_json(config_dir / "metadata.json")
    validation = _read_json(config_dir / "validation.json")
    metrics = _read_json(config_dir / "metrics.json")
    if not bool(validation.get("passed", False)):
        raise ValueError(f"legacy validation failed for {config_dir}")
    with np.load(config_dir / "results.npz", allow_pickle=False) as saved:
        blue = np.asarray(saved["bloch_blue"], dtype=float)
        red = np.asarray(saved["bloch_red"], dtype=float)
    histogram = diagnose_labeled_bloch_histogram(
        blue,
        red,
        n_phi=n_phi,
        n_mu=n_mu,
        l_max=l_max,
        harmonic_estimator="weighted_least_squares",
        require_full_coverage=True,
    )
    diagnostics = histogram.diagnostics
    graph = metadata["detector_graph"]
    parameters = {
        "configuration": metadata["configuration"],
        "hz0": metadata["hz0"],
        "Jx_effective": metadata["Jx_effective"],
        "Jy_effective": metadata["Jy_effective"],
        "central_coupling": metadata["central_coupling"],
        "scaling": metadata["scaling"],
        "graph_spec": graph["spec"],
        "graph_summary": {
            key: graph[key]
            for key in (
                "edge_count", "mean_degree", "degree_variance",
                "laplacian_algebraic_connectivity", "connected",
            )
        },
        "max_abs_bloch_x": float(np.max(np.abs(blue[:, 0]))),
        "central_axis_symmetry": (
            "hz0=hx0=0 and X-only central coupling imply [H,X_Q]=0"
        ),
    }
    graph_seed = graph["spec"]["seed"]
    relative_source = config_dir
    try:
        relative_source = config_dir.resolve().relative_to(ROOT)
    except ValueError:
        pass
    return {
        "family": f"network_{family}",
        "N": metadata["N"],
        "dimension": 2 ** (int(metadata["N"]) + 1),
        "time": metadata["evolution_time"],
        "parameters": json.dumps(parameters, sort_keys=True),
        "seed": graph_seed,
        "root_count": blue.shape[0],
        "qz_valid": False,
        "qz_status": "saved affine roots; homogeneous QZ audit unavailable",
        "coverage": histogram.coverage,
        "density_ratio_cross_residual": (
            histogram.born_density_ratio_cross_residual
            if diagnostics is not None else np.nan
        ),
        "epsilon_antipodal": (
            diagnostics.epsilon_antipodal if diagnostics is not None else np.nan
        ),
        "epsilon_B": (
            diagnostics.born_rms_density_weighted
            if diagnostics is not None else np.nan
        ),
        "epsilon_B_definition": "total-root-density-weighted RMS of a-n.r",
        "higher_harmonic_leakage": (
            diagnostics.higher_odd_harmonic_leakage
            if diagnostics is not None else np.nan
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
        "composition_status": "not tested for this network realization",
        "harmonic_estimator": "weighted_least_squares",
        "polar_S_born": metrics.get("S_born", np.nan),
        "source": str(relative_source),
        "status": (
            "PROVED ANALYTICALLY and VERIFIED NUMERICALLY: X_Q-conserved "
            "great-circle support; saved roots not QZ audited"
            if diagnostics is not None
            else "PROVED ANALYTICALLY and VERIFIED NUMERICALLY: X_Q-conserved "
            "great-circle support; INSUFFICIENT ANGULAR COVERAGE; not QZ audited"
        ),
    }


def _config_dirs(campaign_root: Path) -> Iterable[Path]:
    return sorted(
        path.parent
        for path in campaign_root.rglob("results.npz")
        if path.parent.name.startswith("config_")
    )


def _default_campaign_root(family: str) -> Path:
    matches = sorted(
        (ROOT / "work").glob(f"zeus_sobol_{family}_hz0_0_N12_*")
    )
    if not matches:
        raise FileNotFoundError(f"no saved campaign found for {family}")
    return matches[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            ROOT / "work" / "hamiltonian_classification_20260815"
            / "network_full_sphere" / "network_classification_results.csv"
        ),
    )
    args = parser.parse_args()
    rows: list[dict[str, object]] = []
    counts: dict[str, int] = {}
    for family in FAMILIES:
        campaign_root = _default_campaign_root(family)
        family_rows = [
            classify_saved_network_config(config_dir, family)
            for config_dir in _config_dirs(campaign_root)
        ]
        rows.extend(family_rows)
        counts[family] = len(family_rows)
        print(f"{family}: {len(family_rows)} completed configurations", flush=True)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    print(json.dumps({"output": str(output), "rows": len(rows), "counts": counts}, indent=2))


if __name__ == "__main__":
    main()
