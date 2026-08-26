"""Run the declared small-N Hamiltonian-classification hypothesis screen."""

from __future__ import annotations

import argparse
import csv
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

from collapse.hamiltonian_classification import (
    SinglePixelClassificationPoint,
    classify_single_pixel_point,
)


DEFAULT_CONFIG = ROOT / "configs" / "hamiltonian_classification_local_hypotheses.json"
DEFAULT_OUTPUT = (
    ROOT
    / "work"
    / "hamiltonian_classification_20260815"
    / "local_hypothesis_screen_N6"
)


def _point_payload(base: dict[str, object], scan: dict[str, object], value: float):
    payload = dict(base)
    name = str(scan["name"])
    if name == "transverse_strength":
        payload["Jx"] = value
    elif name == "matched_detuning":
        payload["hz0"] = float(payload["hz"]) + value * float(payload["Jx"])
    elif name == "second_transverse_channel":
        payload["Jy"] = value * float(payload["Jx"])
    elif name == "detector_transverse_scrambling":
        payload["hx"] = value
    else:
        raise ValueError(f"unsupported scan {name!r}")
    return payload


def _slug(value: float) -> str:
    return f"{value:+.8g}".replace("+", "p").replace("-", "m").replace(".", "p")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    total = sum(len(scan["values"]) for scan in config["scans"])
    completed = 0
    for scan in config["scans"]:
        for raw_value in scan["values"]:
            value = float(raw_value)
            completed += 1
            case_dir = output / str(scan["name"]) / _slug(value)
            result_path = case_dir / "result.json"
            print(
                f"[{completed}/{total}] {scan['name']} {scan['parameter']}={value:g}",
                flush=True,
            )
            if result_path.is_file() and not args.force:
                summary = json.loads(result_path.read_text(encoding="utf-8"))
            else:
                point = SinglePixelClassificationPoint(
                    **_point_payload(config["base"], scan, value)
                )
                result = classify_single_pixel_point(point, verbose=False)
                summary = dict(result.summary)
                summary["scan_name"] = scan["name"]
                summary["scan_parameter"] = scan["parameter"]
                summary["scan_value"] = value
                summary["claim_status"] = "LOCAL SMALL-N SCREEN"
                case_dir.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(
                    case_dir / "roots_and_full_sphere.npz",
                    alpha=result.alpha,
                    beta=result.beta,
                    bloch_vectors_0=result.bloch_vectors_0,
                    asymmetry=result.asymmetry,
                    power_by_l=result.power_by_l,
                )
                temporary = case_dir / "result.json.tmp"
                temporary.write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                temporary.replace(result_path)
            rows.append(
                {
                    "scan_name": scan["name"],
                    "scan_parameter": scan["parameter"],
                    "scan_value": value,
                    "N": summary["N"],
                    "time": summary["time"],
                    "qz_valid": summary["qz_valid"],
                    "coverage": summary["coverage"],
                    "epsilon_antipodal": summary["epsilon_antipodal"],
                    "epsilon_B": summary["epsilon_B"],
                    "higher_harmonic_leakage": summary["higher_harmonic_leakage"],
                    "dipole_sharpness": summary["dipole_sharpness"],
                    "axis_fidelity": summary["axis_fidelity"],
                    "P1_over_Podd": summary["P1_over_Podd"],
                    "polar_S_born": summary["polar_S_born"],
                    "result_path": str(result_path.relative_to(ROOT)),
                    "status": "LOCAL SMALL-N SCREEN",
                }
            )
    aggregate = output / "local_hypothesis_screen.csv"
    with aggregate.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "config": str(config_path.relative_to(ROOT)),
        "row_count": len(rows),
        "scientific_status": (
            "LOCAL SMALL-N SCREEN: validates pipeline and informs HPC design; "
            "not finite-size evidence"
        ),
        "output_csv": aggregate.name,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

