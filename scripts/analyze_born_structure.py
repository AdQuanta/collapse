"""Audit Born reflection structure in immutable collected Zeus profiles.

No Hamiltonian diagonalization or parameter search is performed here.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born_profile_export import load_profile, validate_profile, write_profile_tables, write_table
from core.born_reciprocity import (
    born_moment_residuals, born_residual_bounds, cosine_moments,
    folded_gaussian_moment_residuals, histogram_cosine_moments,
    reflection_diagnostics, response_cosine_coefficients,
)
from core.born_structure_plotting import profile_grid, scan_figure, moment_figure


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def portable(value):
    """Strip historical host prefixes while retaining repository provenance."""
    if isinstance(value, dict):
        return {str(portable(k)): portable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [portable(v) for v in value]
    if isinstance(value, str) and value.startswith("/"):
        for marker in ["/work/", "/core/", "/configs/", "/scripts/"]:
            if marker in value:
                return marker[1:] + value.split(marker, 1)[1]
        return Path(value).name
    return value


def verify_source(directory: Path, required: set[str]) -> dict:
    """Check the existing case marker and every marker-listed file."""
    marker = read_json(directory / "COMPLETE.json")
    if marker.get("status") != "complete" or not required.issubset(marker["files"]):
        raise ValueError(f"incomplete source: {directory}")
    for name, digest in marker["files"].items():
        path = directory / name
        if path.parent != directory or sha256(path) != digest:
            raise ValueError(f"source checksum mismatch: {path}")
    return {"marker_sha256": sha256(directory / "COMPLETE.json"), "files": marker["files"]}


def load_case(directory: Path, group: dict, config: dict) -> dict:
    activation = (directory / "activation_resolved_metrics.json").exists()
    if activation:
        metadata = read_json(directory / "activation_resolved_metrics.json")
        metrics = next(d for d in metadata["diagnostics"] if d["label"] == "global")
        archive = "activation_resolved_results.npz"
        parameters = metadata["parameters"]
        n = metadata["detector_n"]
        validation = metadata["validation"]
        required = {archive, "activation_resolved_metrics.json"}
    else:
        metadata = read_json(directory / "metadata.json")
        metrics = read_json(directory / "metrics.json")
        archive = "results.npz" if (directory / "results.npz").exists() else "results_summary.npz"
        parameters = metadata.get("source", metadata.get("configuration", {}))
        n = metadata.get("target_N", metadata.get("N"))
        validation = read_json(directory / "validation.json")
        if validation.get("passed") is not True:
            raise ValueError(f"failed source validation: {directory}")
        required = {archive, "metadata.json", "metrics.json", "validation.json"}
    checks = verify_source(directory, required)
    arrays = load_profile(directory / archive, activation_global=activation)
    checks["profile"] = validate_profile(arrays, rmse=metrics["born_RMSE_occupied"])
    with np.load(directory / archive, allow_pickle=False) as data:
        theta = np.array(data["theta"]) if "theta" in data else None
    if theta is not None and theta.size != 2**n:
        raise ValueError(f"unexpected raw-angle count: {directory}")
    order = 2 * config["moment_pairs"]
    estimated, lower, upper = histogram_cosine_moments(arrays["edges"], arrays["P"], order)
    moments = cosine_moments(theta, order) if theta is not None else estimated
    residuals = born_moment_residuals(moments)
    residual_lower, residual_upper = born_residual_bounds(lower, upper)
    if theta is not None and (np.any(moments < lower - 1e-10) or np.any(moments > upper + 1e-10)):
        raise ValueError("raw-angle moments disagree with stored histogram bounds")
    coefficients = response_cosine_coefficients(arrays, config["response_order"])
    hz0 = float(metadata.get("hz0", parameters.get("hz0", 0)))
    hz = float(parameters["hz"])
    sigma = np.nan
    if activation:
        sigma = metadata["fits"]["global"]["wrapped_gaussian"]["shape"]
    gaussian_residual = (folded_gaussian_moment_residuals(moments, sigma)
                         if np.isfinite(sigma) else np.full(moments.size, np.nan))
    graph = metadata.get("detector_graph", {})
    family = graph.get("canonical_kind", "ring")
    record = {
        "group": group["key"], "group_label": group["label"], "scan": group.get("scan", False),
        "source": str(directory.relative_to(ROOT)), "family": family, "N": n,
        "S_born": metrics["S_born"], "hz0": hz0, "hz": hz, "hz0_ratio": hz0 / hz if hz else np.nan,
        "Jx_effective": metadata["Jx_effective"], "parameters": parameters,
        "moment_method": "raw angles" if theta is not None else "histogram estimate with bounds",
        "born_moment_max": float(np.max(np.abs(residuals))),
        "gaussian_sigma": sigma, "gaussian_moment_max": float(np.max(np.abs(gaussian_residual))),
        "visibility": float(2 * coefficients[1]), "offset": float(coefficients[0]),
        "higher_odd_norm": float(np.linalg.norm(2 * coefficients[3::2])),
        "even_harmonic_max": float(np.max(np.abs(coefficients[2::2]))),
        "moments": moments, "born_moment_residuals": residuals,
        "born_residual_lower": residual_lower, "born_residual_upper": residual_upper,
        "response_coefficients": coefficients, "gaussian_residuals": gaussian_residual,
        "theta": theta, "arrays": arrays, "source_checks": checks,
        "source_validation": validation, **reflection_diagnostics(arrays),
    }
    record["source_eigenvector_condition"] = validation.get("maximum_relative_eigenvector_condition_number", np.nan)
    # A descriptive warning, not an accuracy bound or a pass/fail threshold.
    record["conditioning_caution"] = record["source_eigenvector_condition"] > 1e8
    if record["scan"]:
        record["label"] = f"hz0/hz={record['hz0_ratio']:g}" + ("\nconditioning caution" if record["conditioning_caution"] else "")
    else:
        record["label"] = f"{family.replace('_', ' ')} N={n}\n{directory.parent.name}"
    return record


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def rebin_case(record: dict, bins: list[int]) -> list[dict]:
    """Use the existing canonical histogram implementation for sensitivity."""
    if record["theta"] is None:
        return []
    from core.relative_evolution_study import angular_histogram
    rows = []
    for count in bins:
        hist = angular_histogram(record["theta"], count)
        rows.append(dict(id=record["id"], bins=count, S_born_at_bins=hist.born_similarity,
                         RMSE=hist.occupied_rmse, coverage=hist.coverage,
                         support=hist.support_fraction))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/born_structure_audit_2026-09-10.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = read_json(args.config)
    args.output.mkdir(parents=True, exist_ok=False)
    records = []
    for group in config["campaigns"]:
        name = "activation_resolved_metrics.json" if group["scan"] else "metrics.json"
        paths = sorted((ROOT / group["root"]).rglob(name))
        if not paths:
            raise ValueError(f"no source cases in {group['root']}")
        records.extend(load_case(path.parent, group, config) for path in paths)
        print(f"Validated {group['key']}: {len(paths)} cases", flush=True)
    for reference in config["references"]:
        records.append(load_case(ROOT / reference["source"],
                                 dict(key="network_reference", label=reference["label"]), config))
    rebin_rows, provenance = [], []
    for index, record in enumerate(records):
        record["id"] = f"case_{index:03d}"
        directory = args.output / record["id"]
        directory.mkdir()
        write_profile_tables(directory, record["arrays"])
        write_table(directory / "P_moments.dat", ["n", "a_n", "WG_residual"],
                    np.column_stack((np.arange(len(record["moments"])), record["moments"], record["gaussian_residuals"])))
        write_table(directory / "born_moments.dat", ["m", "residual", "histogram_lower", "histogram_upper"],
                    np.column_stack((np.arange(len(record["born_moment_residuals"])), record["born_moment_residuals"],
                                     record["born_residual_lower"], record["born_residual_upper"])))
        write_table(directory / "R_harmonics.dat", ["n", "coefficient"],
                    np.column_stack((np.arange(len(record["response_coefficients"])), record["response_coefficients"])))
        rebin_rows.extend(rebin_case(record, config["rebin_counts"]))
        provenance.append({key: record[key] for key in ["id", "source", "parameters", "source_checks", "source_validation", "moment_method"]})
    columns = ["id", "group", "family", "N", "hz", "hz0", "hz0_ratio", "Jx_effective", "S_born",
               "coverage", "P_support", "entropy_normalized", "occupied_RMSE", "reflection_L1",
               "offset", "visibility", "higher_odd_norm", "even_harmonic_max", "born_moment_max",
               "gaussian_sigma", "gaussian_moment_max", "moment_method", "source_eigenvector_condition", "conditioning_caution", "source"]
    write_csv(args.output / "case_metrics.csv", records, columns)
    write_csv(args.output / "bin_sensitivity.csv", rebin_rows, ["id", "bins", "S_born_at_bins", "RMSE", "coverage", "support"])
    groups = {}
    for group in config["campaigns"]:
        if group["scan"]:
            subset = [r for r in records if r["group"] == group["key"]]
            if len(subset) != 20:
                raise ValueError("field scan is not complete")
            groups[group["label"]] = subset
            selected = [min(subset, key=lambda r: abs(r["hz0_ratio"] - ratio)) for ratio in config["selected_scan_ratios"]]
            profile_grid(selected, args.output / (group["key"] + "_diagnostics"), group["label"] + ", N=17, t=10^6")
    scan_figure(groups, args.output / "field_scan_comparison")
    rings = [r for r in records if r["group"] == "ring_extremes"]
    representatives = []
    for second in [False, True]:
        subset = [r for r in rings if (bool(r["parameters"].get("j2", 0) or r["parameters"].get("jpm2", 0)) == second)]
        representatives.extend([max(subset, key=lambda r: r["S_born"]), min(subset, key=lambda r: r["S_born"])])
    profile_grid(representatives, args.output / "ring_representatives", "Nearest and second-neighbor rings: stored-score extremes")
    moment_figure(representatives, args.output / "ring_moment_tests")
    networks = [r for r in records if r["group"] == "network_reference"]
    controls = [r for r in records if r["group"] == "network_controls"]
    for ref in networks:
        subset = [r for r in controls if r["family"] == ref["family"]]
        control = max(subset, key=lambda r: r["N"])
        profile_grid([ref, control], args.output / (ref["family"] + "_diagnostics"),
                     "Same graph family, different saved realizations/parameters; sizes labeled")
    summary = ["# Born structural audit: numerical inventory", "", config["scope"], "",
               "|scan|hz0/hz|S_born|coverage|RMSE|max Born moment residual|", "|---|---:|---:|---:|---:|---:|"]
    for group, subset in groups.items():
        for ratio in [0, .01, 1]:
            r = min(subset, key=lambda r: abs(r["hz0_ratio"] - ratio))
            summary.append(f"|{group}|{ratio:g}|{r['S_born']:.4f}|{r['coverage']:.3f}|{r['occupied_RMSE']:.4f}|{r['born_moment_max']:.4g}|")
    summary.extend(["", "P moments from full raw angles when available; histogram-only cases carry conservative within-bin bounds.",
                    "R Fourier coefficients are midpoint quadratures and are omitted when reflection coverage is incomplete.",
                    "A finite set of small moment residuals does not establish sufficiency, convergence, or broad support.",
                    "Root multiplicities are deterministic, not independent random observations; no IID confidence intervals are used.",
                    "Stored S_born uses 100 bins; displayed P/R uses 64 bins. S_born_at_bins explicitly varies the score bin count.",
                    "Cases with saved eigenvector condition number >1e8 are flagged as conditioning cautions; this descriptive flag is not a forward-error bound.",
                    "Source validation fields are retained in manifest.json. Small residuals alone do not prove forward accuracy for ill-conditioned roots."])
    (args.output / "summary.md").write_text("\n".join(summary) + "\n")
    sources = [Path(__file__), args.config, ROOT / "core/born_reciprocity.py", ROOT / "core/born_structure_plotting.py",
               ROOT / "core/born_profile_export.py", ROOT / "core/relative_evolution_study.py"]
    manifest = dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(), config=config,
                    python=platform.python_version(), numpy=np.__version__,
                    git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
                    source_sha256={str(p.resolve().relative_to(ROOT)): sha256(p) for p in sources},
                    cases=portable(provenance),
                    outputs={str(p.relative_to(args.output)): sha256(p) for p in sorted(args.output.rglob("*")) if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Completed {len(records)} cases: {args.output}")


if __name__ == "__main__":
    main()
