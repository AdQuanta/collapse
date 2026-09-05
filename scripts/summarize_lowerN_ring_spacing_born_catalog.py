#!/usr/bin/env python3.11
"""Select ten hz0=0 ring examples in each spacing/Born combination."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.stats import kstest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_CONFIG = ROOT / "configs" / "hz0_0_ring_spacing_born_10x4.json"
DEFAULT_N17_SPACING = (
    ROOT / "reports" / "ranked_ring_symmetry_resolved_spacings_N17_2026-08-25" / "summary_N17.json"
)
DEFAULT_N17_DYNAMICS = (
    ROOT
    / "reports"
    / "ranked_ring_N17_fresh_diagnostics_and_symmetry_spacings_2026-08-27"
    / "render_manifest.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _spacing_class(
    mean_r: float, ks_poisson: float, ks_goe: float, classification: dict[str, Any]
) -> tuple[str, float, float]:
    poisson = float(classification["mean_r_poisson"])
    goe = float(classification["mean_r_goe"])
    mean_class = "wigner_dyson" if abs(mean_r - goe) < abs(mean_r - poisson) else "poisson"
    ks_class = "wigner_dyson" if ks_goe < ks_poisson else "poisson"
    if mean_class != ks_class:
        return "mixed", 0.0, 0.0
    if mean_class == "wigner_dyson":
        mean_advantage = abs(mean_r - poisson) - abs(mean_r - goe)
        ks_advantage = ks_poisson - ks_goe
    else:
        mean_advantage = abs(mean_r - goe) - abs(mean_r - poisson)
        ks_advantage = ks_goe - ks_poisson
    return mean_class, float(mean_advantage), float(ks_advantage)


def _profile(s_born: float, born_rmse: float, classification: dict[str, Any]) -> str:
    if (
        s_born >= float(classification["born_minimum"])
        and born_rmse <= float(classification["born_rmse_maximum"])
    ):
        return "born"
    if (
        s_born < float(classification["clearly_nonborn_maximum"])
        and born_rmse > float(classification["clearly_nonborn_rmse_minimum"])
    ):
        return "clearly_nonborn"
    return "intermediate"


def _case_record(
    *,
    family: str,
    detector_n: int,
    config_id: str,
    s_born: float,
    born_rmse: float,
    parameters: dict[str, float],
    jx_unscaled: float,
    source_dir: str,
    diagnostic_figure: str,
    spacing_source: str,
    mean_r: float,
    ks_poisson: float,
    ks_goe: float,
    classification: dict[str, Any],
) -> dict[str, Any]:
    spacing, mean_advantage, ks_advantage = _spacing_class(
        mean_r, ks_poisson, ks_goe, classification
    )
    return {
        "family": family,
        "detector_n": detector_n,
        "hz0": 0.0,
        "config_id": config_id,
        "S_born": s_born,
        "born_RMSE_occupied": born_rmse,
        "profile_class": _profile(s_born, born_rmse, classification),
        "spacing_class": spacing,
        "mean_adjacent_gap_ratio": mean_r,
        "ks_poisson": ks_poisson,
        "ks_goe": ks_goe,
        "mean_reference_advantage": mean_advantage,
        "ks_advantage": ks_advantage,
        "parameters": parameters,
        "jx_unscaled": jx_unscaled,
        "source_dir": source_dir,
        "diagnostic_figure": diagnostic_figure,
        "spacing_source": spacing_source,
    }


def load_lower_n(run_root: Path, classification: dict[str, Any]) -> list[dict[str, Any]]:
    complete = _read_json(run_root / "COMPLETE.json")
    if complete.get("status") != "complete":
        raise ValueError("lower-N campaign is not complete")
    expected = int(complete["case_count"])
    summaries = sorted((run_root / "cases").glob("*/summary.json"))
    if len(summaries) != expected:
        raise ValueError(f"found {len(summaries)} lower-N summaries, expected {expected}")
    records = []
    for path in summaries:
        case_dir = path.parent
        marker = _read_json(case_dir / "COMPLETE.json")
        for name, digest in marker["files"].items():
            if _sha256(case_dir / name) != digest:
                raise ValueError(f"checksum mismatch: {case_dir / name}")
        payload = _read_json(path)
        case = payload["case"]
        pooled = payload["pooled"]
        source_dir = str(case["source_dir"])
        records.append(
            _case_record(
                family=str(case["family"]),
                detector_n=int(case["detector_n"]),
                config_id=str(case["config_id"]),
                s_born=float(case["s_born"]),
                born_rmse=float(case["born_rmse"]),
                parameters={key: float(value) for key, value in case["parameters"].items()},
                jx_unscaled=float(case["jx_unscaled"]),
                source_dir=source_dir,
                diagnostic_figure=str(Path(source_dir) / "blue_red_diagnostics.png"),
                spacing_source=str(case_dir.relative_to(ROOT) / "spacing_histograms.npz"),
                mean_r=float(pooled["mean_adjacent_gap_ratio"]),
                ks_poisson=float(pooled["ks_poisson"]),
                ks_goe=float(pooled["ks_goe"]),
                classification=classification,
            )
        )
    return records


def load_n17(classification: dict[str, Any]) -> list[dict[str, Any]]:
    spacing_summary = _read_json(DEFAULT_N17_SPACING)
    dynamics_manifest = _read_json(DEFAULT_N17_DYNAMICS)
    dynamics = {
        (item["family"], item["config_id"]): item
        for item in dynamics_manifest["provenance"]
    }
    records = []
    for item in spacing_summary["cases"]:
        case = item["case"]
        family = str(case["family"])
        config_id = str(case["config_id"])
        fresh = dynamics[(family, config_id)]
        result_dir = ROOT / fresh["fresh_result_dir"]
        metrics = _read_json(result_dir / "metrics.json")
        archive = ROOT / str(item["spectral_archive"]).replace("\\", "/")
        arrays = np.load(archive)
        spacings = []
        ratios = []
        for key in arrays.files:
            if key.endswith("__unfolded_spacings"):
                spacings.append(np.asarray(arrays[key], dtype=np.float64))
            elif key.endswith("__energies"):
                delta = np.diff(np.asarray(arrays[key], dtype=np.float64))
                ratios.append(np.minimum(delta[:-1], delta[1:]) / np.maximum(delta[:-1], delta[1:]))
        pooled_spacings = np.concatenate(spacings)
        pooled_ratios = np.concatenate(ratios)
        ks_poisson = float(kstest(pooled_spacings, lambda x: 1.0 - np.exp(-x)).statistic)
        ks_goe = float(
            kstest(pooled_spacings, lambda x: 1.0 - np.exp(-np.pi * x * x / 4.0)).statistic
        )
        figure_matches = sorted(
            (DEFAULT_N17_DYNAMICS.parent / family).glob(f"**/*{config_id}*.png")
        )
        records.append(
            _case_record(
                family=family,
                detector_n=17,
                config_id=config_id,
                s_born=float(metrics["S_born"]),
                born_rmse=float(metrics["born_RMSE_occupied"]),
                parameters={key: float(value) for key, value in case["parameters"].items()},
                jx_unscaled=float(case["jx_unscaled"]),
                source_dir=str(result_dir.relative_to(ROOT)),
                diagnostic_figure=(
                    str(figure_matches[0].relative_to(ROOT)) if figure_matches else ""
                ),
                spacing_source=str(archive.relative_to(ROOT)),
                mean_r=float(np.mean(pooled_ratios)),
                ks_poisson=ks_poisson,
                ks_goe=ks_goe,
                classification=classification,
            )
        )
    return records


def _physical_key(record: dict[str, Any]) -> tuple[Any, ...]:
    parameters = record["parameters"]
    return (
        record["family"],
        *(round(float(parameters[name]), 14) for name in ("hz", "j", "jpm", "j2", "jpm2")),
        round(float(record["jx_unscaled"]), 14),
    )


def select_catalog(records: list[dict[str, Any]], classification: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    minimum_mean = float(classification["catalog_minimum_mean_reference_advantage"])
    minimum_ks = float(classification["catalog_minimum_ks_advantage"])
    definitions = {
        "wd_born": ("wigner_dyson", "born"),
        "poisson_born": ("poisson", "born"),
        "wd_clearly_nonborn": ("wigner_dyson", "clearly_nonborn"),
        "poisson_clearly_nonborn": ("poisson", "clearly_nonborn"),
    }
    selected: dict[str, list[dict[str, Any]]] = {}
    for label, (spacing, profile) in definitions.items():
        eligible = [
            row
            for row in records
            if row["spacing_class"] == spacing
            and row["profile_class"] == profile
            and row["mean_reference_advantage"] >= minimum_mean
            and row["ks_advantage"] >= minimum_ks
        ]
        best_by_configuration: dict[tuple[Any, ...], dict[str, Any]] = {}
        for row in eligible:
            key = _physical_key(row)
            prior = best_by_configuration.get(key)
            if prior is None or (
                profile == "born" and row["S_born"] > prior["S_born"]
            ) or (
                profile == "clearly_nonborn" and row["S_born"] < prior["S_born"]
            ):
                best_by_configuration[key] = row
        ordered = sorted(
            best_by_configuration.values(),
            key=lambda row: (row["S_born"], row["config_id"]),
            reverse=profile == "born",
        )
        if len(ordered) < 10:
            raise RuntimeError(f"{label}: only {len(ordered)} eligible configurations")
        selected[label] = ordered[:10]
    return selected


def write_outputs(output: Path, selected: dict[str, list[dict[str, Any]]], provenance: dict[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for category, examples in selected.items():
        for rank, row in enumerate(examples, start=1):
            rows.append({"category": category, "rank": rank, **row})
    manifest = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(), **provenance, "examples": rows}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    flat_rows = []
    for row in rows:
        flat = {key: value for key, value in row.items() if key != "parameters"}
        flat.update(row["parameters"])
        flat_rows.append(flat)
    with (output / "catalog.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat_rows[0]))
        writer.writeheader()
        writer.writerows(flat_rows)
    titles = {
        "wd_born": "WD and Born-like",
        "poisson_born": "Poisson and Born-like",
        "wd_clearly_nonborn": "WD and clearly non-Born",
        "poisson_clearly_nonborn": "Poisson and clearly non-Born",
    }
    lines = [
        "# hz0=0 ring spacing/Born catalog",
        "",
        "Every example pairs dynamics and detector spacings at the same detector size.",
        "Born-like means `S_Born >= 0.80` and occupied-bin RMSE `<= 0.05`; clearly",
        "non-Born means `S_Born < 0.50` and RMSE `> 0.10`. The spacing label requires",
        "agreement between mean-gap-ratio proximity and unfolded-spacing KS distance,",
        "plus advantages of at least 0.03 in both comparisons.",
        "",
    ]
    for category, examples in selected.items():
        lines.extend(
            [
                f"## {titles[category]}",
                "",
                "| rank | family | N | config | S_Born | RMSE | mean r | KS P | KS GOE |",
                "|---:|---|---:|---|---:|---:|---:|---:|---:|",
            ]
        )
        for rank, row in enumerate(examples, start=1):
            lines.append(
                f"| {rank} | {row['family']} | {row['detector_n']} | {row['config_id']} | "
                f"{row['S_born']:.3f} | {row['born_RMSE_occupied']:.3f} | "
                f"{row['mean_adjacent_gap_ratio']:.3f} | {row['ks_poisson']:.3f} | {row['ks_goe']:.3f} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Limitations",
            "",
            "These are finite-size descriptive classifications, not proofs of random-matrix",
            "universality. The lower-N calculation omits even-N half filling and uses the five",
            "largest exact sectors at each nonredundant momentum. No independent finite-size",
            "stability requirement was imposed on each selected configuration.",
            "",
        ]
    )
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--lower-n-root", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return result


def main() -> None:
    args = parser().parse_args()
    classification = _read_json(args.config)
    lower = load_lower_n(args.lower_n_root.resolve(), classification)
    n17 = load_n17(classification)
    selected = select_catalog(lower + n17, classification)
    write_outputs(
        args.output.resolve(),
        selected,
        {
            "scope": "clean one-dimensional rings with hz0=0",
            "classification": classification,
            "selection_config": str(args.config.resolve().relative_to(ROOT)),
            "selection_config_sha256": _sha256(args.config.resolve()),
            "lower_n_campaign": str(args.lower_n_root.resolve().relative_to(ROOT)),
            "lower_n_campaign_sha256": _sha256(args.lower_n_root.resolve() / "COMPLETE.json"),
            "n17_spacing_summary": str(DEFAULT_N17_SPACING.relative_to(ROOT)),
            "n17_spacing_summary_sha256": _sha256(DEFAULT_N17_SPACING),
            "n17_dynamics_manifest": str(DEFAULT_N17_DYNAMICS.relative_to(ROOT)),
            "n17_dynamics_manifest_sha256": _sha256(DEFAULT_N17_DYNAMICS),
        },
    )
    print(json.dumps({key: len(value) for key, value in selected.items()}, indent=2))


if __name__ == "__main__":
    main()
