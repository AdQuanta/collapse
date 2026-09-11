"""Test isotropic cancellation and anisotropic detector controls in saved grids.

The legacy campaign has completion inventories but no historical file hashes
or matrix residuals. Audit counts, parameter provenance, root geometry and
saved metrics; record current hashes and keep this limitation explicit.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
from scipy.stats import wasserstein_distance

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born import born_ratio_from_theta
from core.born_detector_grid_plotting import detector_plane, exchange_slices
from core.born_profile_export import write_profile_tables, write_table
from core.born_reciprocity import (
    born_moment_residuals, cosine_moments, reflection_diagnostics,
    response_cosine_coefficients,
)
from core.born_structure_plotting import profile_grid
from core.isotropic_detector_identity import isotropic_root_measure
from core.relative_evolution_study import angular_histogram


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def arrays_from_angles(theta: np.ndarray, bins: int) -> dict[str, np.ndarray]:
    hist = angular_histogram(theta, bins)
    return dict(edges=hist.edges, centers=hist.centers, P=hist.density,
                P_reflected=hist.reflected_density, R=hist.ratio,
                occupied=hist.occupied, Born=hist.born)


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/born_detector_grid_audit_2026-09-11.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    source = ROOT / config["source"]
    expected = set(itertools.product(config["hz_values"], config["j_values"], config["jpm_values"]))
    args.output.mkdir(parents=True, exist_ok=False)
    records, representatives, isotropic_checks, input_hashes = [], [], [], {}
    moments_by_case = {}
    for n in config["detector_sizes"]:
        marker = source / f"status/N{n}/DONE.json"
        aggregate = source / f"aggregates/N{n}/manifest.json"
        inventory = source / f"aggregates/N{n}/anisotropic_metrics_N{n}.csv"
        done, complete = json.loads(marker.read_text()), json.loads(aggregate.read_text())
        if (done["completed_cases"] != len(expected) or not complete["complete"]
                or complete["missing_cases"] or complete["expected_cases"] != len(expected)
                or done["config_digest"] != complete["config_digest"]):
            raise ValueError(f"incomplete legacy N={n} grid")
        with inventory.open() as stream:
            rows = list(csv.DictReader(stream))
        done_keys = {(r["hz"], r["J"], r["Jpm"]) for r in done["completed"]}
        keys = {(float(r["hz"]), float(r["J"]), float(r["Jpm"])) for r in rows}
        if keys != expected or done_keys != expected or len(rows) != len(expected):
            raise ValueError("parameter grid inventory mismatch")
        for path in (marker, aggregate, inventory):
            input_hashes[str(path.relative_to(ROOT))] = digest(path)
        for row in rows:
            raw_path = ROOT / row["raw_path"]
            metadata_path = raw_path.parent / "metadata.json"
            case_suffix = raw_path.parent.relative_to(source / "raw")
            metrics_path = source / "metrics" / case_suffix / "diagnostics.json"
            metadata = json.loads(metadata_path.read_text())
            metrics = json.loads(metrics_path.read_text())
            params = metadata["case"]
            if metadata["config_digest"] != done["config_digest"]:
                raise ValueError("case configuration digest mismatch")
            if not (ROOT / row["figure_path"]).is_file():
                raise ValueError("completion inventory has a missing figure")
            if metrics["excluded_eigenvalues"] or metrics["finite_eigenvalues"] != 2**n:
                raise ValueError("legacy source excluded roots")
            with np.load(raw_path, allow_pickle=False) as archive:
                theta, eigenvalues = archive["theta"], archive["eigenvalues"]
                checks = dict(detector_n=n, hz=float(row["hz"]), J=float(row["J"]),
                              Jpm=float(row["Jpm"]), hz0=config["hz0"],
                              Jx=config["collective_jx"], t=config["time"])
                for key, value in checks.items():
                    if not np.isclose(float(archive[key]), value, rtol=0, atol=1e-14):
                        raise ValueError(f"raw parameter mismatch: {raw_path}: {key}")
                if not np.isclose(float(archive["Jx_edge"]), config["collective_jx"] / np.sqrt(n), rtol=0, atol=1e-14):
                    raise ValueError("incorrect collective coupling normalization")
            for key, value in dict(detector_n=n, hz=checks["hz"], j=checks["J"], jpm=checks["Jpm"], hz0=config["hz0"], jx=config["collective_jx"], evolution_time=config["time"], seed=config["seed"]).items():
                if params[key] != value or metrics["case"][key] != value:
                    raise ValueError("metadata parameters disagree")
            if theta.shape != (2**n,) or not np.all(np.isfinite(eigenvalues)):
                raise ValueError("incomplete/nonfinite spectrum")
            np.testing.assert_allclose(theta, 2 * np.arctan(np.abs(eigenvalues)), rtol=0, atol=1e-13)
            legacy = angular_histogram(theta, config["legacy_bins"])
            score = born_ratio_from_theta(theta, np.pi - theta, n_theta=100).similarity
            for actual, saved in [(legacy.occupied_rmse, metrics["born_rmse"]), (legacy.coverage, metrics["angular_bin_coverage"]), (score, metrics["S_born"])]:
                if not np.isclose(actual, saved, rtol=0, atol=1e-10):
                    raise ValueError(f"legacy metric mismatch: {raw_path}")
            moments = cosine_moments(theta, config["maximum_moment_order"])
            arrays = arrays_from_angles(theta, config["bins"])
            coeff = response_cosine_coefficients(arrays, config["response_order"])
            record = dict(N=n, hz=checks["hz"], J=checks["J"], Jpm=checks["Jpm"],
                          anisotropy=checks["J"] - checks["Jpm"] / 2,
                          S_born=float(score), **reflection_diagnostics(arrays),
                          born_moment_max=float(np.max(np.abs(born_moment_residuals(moments)))),
                          visibility=float(2 * coeff[1]), higher_odd_norm=float(np.linalg.norm(2 * coeff[3::2])),
                          imaginary_axis_defect=float(np.max(abs(eigenvalues.real) / np.maximum(1., abs(eigenvalues)))),
                          source=str(raw_path.relative_to(ROOT)))
            record["descriptive_born_gate"] = (record["coverage"] == 1. and record["occupied_RMSE"] <= config["descriptive_born_rmse_limit"] and record["born_moment_max"] <= config["descriptive_moment_limit"])
            records.append(record)
            moments_by_case[(n, record["hz"], record["J"], record["Jpm"])] = moments
            if record["anisotropy"] == 0:
                predicted, weights = isotropic_root_measure(n, collective_jx=config["collective_jx"], hz=record["hz"], time=config["time"])
                distance = wasserstein_distance(theta, predicted, v_weights=weights)
                if distance > config["isotropic_wasserstein_tolerance"]:
                    raise ValueError("isotropic identity exceeds long-time rounding tolerance")
                isotropic_checks.append(dict(N=n, hz=record["hz"], J=record["J"], Jpm=record["Jpm"], angular_Wasserstein=distance, coverage=record["coverage"]))
            if n == max(config["detector_sizes"]) and record["hz"] == config["selected_hz"] and record["J"] == config["selected_j"] and record["Jpm"] in config["representative_jpm"]:
                label = f"Jpm={record['Jpm']:g}" + (" (isotropic)" if record["anisotropy"] == 0 else "")
                representatives.append(dict(**record, label=label, arrays=arrays, response_coefficients=coeff))
                folder = args.output / f"representative_Jpm_{record['Jpm']:g}"
                folder.mkdir()
                write_profile_tables(folder, arrays)
                write_table(folder / "moments.dat", ["n", "a_n"], np.column_stack([np.arange(len(moments)), moments]))
                write_table(folder / "R_harmonics.dat", ["n", "coefficient"], np.column_stack([np.arange(len(coeff)), coeff]))
            for path in (raw_path, metadata_path, metrics_path):
                input_hashes[str(path.relative_to(ROOT))] = digest(path)
        print(f"Audited N={n}: {len(rows)} complete legacy cases", flush=True)
    sign_checks = []
    for (n, hz, j, jpm), moments in moments_by_case.items():
        if hz > 0:
            error = float(np.max(abs(moments - moments_by_case[(n, -hz, j, jpm)])))
            sign_checks.append(dict(N=n, hz=hz, J=j, Jpm=jpm, moment_max_error=error))
    write_csv(args.output / "case_metrics.csv", records)
    write_csv(args.output / "isotropic_identity_checks.csv", isotropic_checks)
    write_csv(args.output / "field_sign_checks.csv", sign_checks)
    detector_plane(records, config, args.output / "detector_parameter_plane")
    exchange_slices(records, config, args.output / "matched_exchange_slices")
    profile_grid(sorted(representatives, key=lambda r: r["Jpm"]), args.output / "representative_diagnostics", "Fixed N=14, J=0.5, hz=0.1, Jx=0.01, hz0=0, t=1e6")
    counts = []
    for n in config["detector_sizes"]:
        for label, selector in [("isotropic", lambda r: r["anisotropy"] == 0), ("pure_ZZ_anisotropic", lambda r: r["Jpm"] == 0 and r["anisotropy"] != 0), ("exchange_anisotropic", lambda r: r["Jpm"] != 0 and r["anisotropy"] != 0)]:
            subset = [r for r in records if r["N"] == n and selector(r)]
            counts.append(dict(N=n, family=label, cases=len(subset), full_coverage=sum(r["coverage"] == 1 for r in subset), descriptive_born_gate=sum(r["descriptive_born_gate"] for r in subset)))
    summary = dict(cases=len(records), isotropic_checks=len(isotropic_checks), maximum_isotropic_angle_Wasserstein=max(r["angular_Wasserstein"] for r in isotropic_checks), field_sign_pairs=len(sign_checks), maximum_field_sign_moment_error=max(r["moment_max_error"] for r in sign_checks), maximum_imaginary_axis_defect=max(r["imaginary_axis_defect"] for r in records), counts=counts,
                   limitations="Legacy source lacks historical file checksums and matrix residuals. Current hashes establish this audit's input provenance; exact isotropic checks do not validate every anisotropic solve. Fixed-time finite-size comparisons are not a thermodynamic extrapolation.")
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    defining = [Path(__file__), args.config, ROOT / "core/isotropic_detector_identity.py", ROOT / "core/born_detector_grid_plotting.py", ROOT / "core/born_reciprocity.py", ROOT / "core/born_profile_export.py", ROOT / "core/born_structure_plotting.py", ROOT / "core/relative_evolution_study.py", ROOT / "core/born.py"]
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(), config=config, python=platform.python_version(), numpy=np.__version__, git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), source_hashes={str(p.relative_to(ROOT)): digest(p) for p in defining}, input_hashes=input_hashes, outputs={str(p.relative_to(args.output)): digest(p) for p in sorted(args.output.rglob("*")) if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
