"""Apply strict full-sphere diagnostics to three saved Sobol ring campaigns.

These campaigns store affine roots and blue/red Bloch coordinates but not the
homogeneous QZ pairs. The adapter therefore preserves QZ status as unavailable
and refuses harmonic metrics whenever the common equal-area sphere is not
fully covered.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
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

from collapse.gleason_diagnostics import diagnose_labeled_bloch_histogram  # noqa: E402


CAMPAIGNS = {
    "sobol_second_neighbor_hz0_0": (
        "zeus_sobol_second_neighbor_hz0_0_N14_20260805_224342"
    ),
    "sobol_ring_hz0_0": "zeus_sobol_hz0_0_N14_20260805_224341",
    "sobol_ring_hz0_0p1_matched_band": (
        "zeus_sobol_hz0_0p1_hz_0p0999_0p1001_N14_20260805_224341"
    ),
}
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


def classify_saved_sobol_config(
    config_dir: Path,
    family: str,
    *,
    n_phi: int = 16,
    n_mu: int = 8,
    l_max: int = 7,
) -> dict[str, object]:
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
    hz0 = float(metadata["hz0"])
    great_circle_theorem_applies = hz0 == 0.0 and float(metadata["Jy_unscaled"]) == 0.0
    maximum_x = float(np.max(np.abs(blue[:, 0])))
    parameters = {
        "configuration": metadata["configuration"],
        "hz0": hz0,
        "Jx_effective": metadata["Jx_effective"],
        "Jy_effective": metadata["Jy_effective"],
        "scaling": metadata["scaling"],
        "second_neighbor_ring": metadata["second_neighbor_ring"],
        "second_neighbor_bond_convention": metadata["second_neighbor_bond_convention"],
        "max_abs_bloch_x": maximum_x,
        "central_x_conservation_theorem_applies": great_circle_theorem_applies,
        "angular_grid": {"n_phi": n_phi, "n_mu": n_mu, "l_max": l_max},
    }
    try:
        source = str(config_dir.resolve().relative_to(ROOT))
    except ValueError:
        source = str(config_dir.resolve())
    if great_circle_theorem_applies:
        status = (
            "PROVED ANALYTICALLY and VERIFIED NUMERICALLY: X_Q-conserved "
            "great-circle support; saved roots not QZ audited"
        )
    elif diagnostics is None:
        status = "INSUFFICIENT ANGULAR COVERAGE; saved roots not QZ audited"
    else:
        status = "SUPPORTED NUMERICALLY; saved-root post-processing; not QZ audited"
    return {
        "family": family,
        "N": metadata["N"],
        "dimension": 2 ** (int(metadata["N"]) + 1),
        "time": metadata["evolution_time"],
        "parameters": json.dumps(parameters, sort_keys=True),
        "seed": "",
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
            diagnostics.born_rms_density_weighted if diagnostics is not None else np.nan
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
        "P1_over_Podd": diagnostics.p1_over_podd if diagnostics is not None else np.nan,
        "composition_error": np.nan,
        "composition_status": "not tested for this configuration",
        "harmonic_estimator": "weighted_least_squares",
        "polar_S_born": metrics.get("S_born", np.nan),
        "source": source,
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            ROOT / "work" / "hamiltonian_classification_20260815"
            / "sobol_ring_full_sphere" / "sobol_ring_classification_results.csv"
        ),
    )
    args = parser.parse_args()
    rows: list[dict[str, object]] = []
    counts: dict[str, int] = {}
    for family, directory_name in CAMPAIGNS.items():
        campaign_root = ROOT / "work" / directory_name
        config_dirs = sorted(
            path.parent
            for path in campaign_root.rglob("results.npz")
            if path.parent.name.startswith("config_")
        )
        family_rows = [
            classify_saved_sobol_config(config_dir, family)
            for config_dir in config_dirs
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
