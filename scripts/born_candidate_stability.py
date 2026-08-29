"""
Re-evaluate selected Born-search candidates across metric settings.

The broad search ranks rows using one theta-bin count and one tail fraction.
This script is deliberately narrower: it takes promising rows from existing
``results.csv`` or ``summary_rows.csv`` files, diagonalizes each unique
Hamiltonian once, and recomputes diagnostics over several bin counts and tail
fractions.  The output is meant to catch histogram/tail-estimator artifacts
before sending larger finite-size jobs to Zeus.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import math
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from statistics import mean, median
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from born_hamiltonian_search import (  # noqa: E402
    Candidate,
    TeeWriter,
    _analyzer_from_diagonalization,
    _angles_and_radii,
    _candidate_label,
    _diagonalize_candidate,
    _disorder_signature,
    _default_worker_count,
    _energy_metrics_from_diagonalization,
    heavy_tail_metrics,
    objective_score,
)
from core.born import diagnostics_from_radii  # noqa: E402


NUMERIC_FIELDS = {
    "N",
    "t",
    "seed",
    "disorder_strength",
    "disorder_strength_J",
    "disorder_strength_Jpm",
    "disorder_strength_Jx",
    "disorder_strength_Jz",
    "disorder_strength_Jzx",
    "disorder_strength_Jcpm",
    "disorder_strength_hx",
    "disorder_strength_hz",
    "J",
    "Jpm",
    "Jxx",
    "Jyy",
    "Jx_unscaled",
    "Jy_unscaled",
    "Jz",
    "Jzx",
    "Jcpm_unscaled",
    "hx",
    "hz",
    "born_similarity",
    "tail_density_exponent",
    "reciprocity_error",
    "energy_degenerate_fraction",
    "energy_degenerate_cluster_fraction",
    "energy_max_multiplicity",
    "energy_resolved_level_count",
    "energy_mean_spacing_ratio",
    "energy_min_spacing",
    "radius_q99_over_q50",
    "radius_atomic_fraction",
    "balanced_score",
    "objective_score",
}

QUEUE_GROUP_FIELDS = (
    "model",
    "connectivity",
    "central_coupling",
    "hz0_mode",
    "seed",
    "disorder",
    "disorder_strength",
    "disorder_strength_J",
    "disorder_strength_Jpm",
    "disorder_strength_Jx",
    "disorder_strength_Jz",
    "disorder_strength_Jzx",
    "disorder_strength_Jcpm",
    "disorder_strength_hx",
    "disorder_strength_hz",
    "J",
    "Jx_unscaled",
    "Jy_unscaled",
    "hz",
    "Jpm",
    "Jxx",
    "Jyy",
    "Jz",
    "Jzx",
    "Jcpm_unscaled",
    "t",
)


def _float_or_nan(value: Any) -> float:
    text = "" if value is None else str(value).strip()
    if not text:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


def _boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _field_float(row: dict[str, Any], field: str, default: float) -> float:
    value = _float_or_nan(row.get(field))
    return value if math.isfinite(value) else default


def _field_text(row: dict[str, Any], field: str, default: str) -> str:
    value = row.get(field)
    text = "" if value is None else str(value).strip()
    return text if text else default


def _fmt(value: Any, digits: int = 3) -> str:
    number = _float_or_nan(value)
    if not math.isfinite(number):
        return "nan"
    if abs(number) >= 10000 or (0 < abs(number) < 0.001):
        return f"{number:.{digits}e}"
    return f"{number:.{digits}f}"


def _fmt_g(value: Any) -> str:
    number = _float_or_nan(value)
    if not math.isfinite(number):
        return "nan"
    return f"{number:g}"


def _key_value(value: Any) -> str:
    number = _float_or_nan(value)
    if math.isfinite(number):
        return f"{number:.12g}"
    return str(value)


def _load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for raw in reader:
                row: dict[str, Any] = dict(raw)
                row.setdefault("family", path.parent.name)
                row["source_csv"] = str(path)
                for field in NUMERIC_FIELDS:
                    if field in row:
                        row[field] = _float_or_nan(row[field])
                if "N" in row and math.isfinite(_float_or_nan(row["N"])):
                    row["N"] = int(row["N"])
                rows.append(row)
    return rows


def _candidate_from_row(row: dict[str, Any]) -> Candidate:
    return Candidate(
        model=str(row.get("model", "single_pixel")),
        N=int(row["N"]),
        J=_field_float(row, "J", 1.0),
        Jpm=_field_float(row, "Jpm", 0.0),
        Jxx=_field_float(row, "Jxx", 0.0),
        Jyy=_field_float(row, "Jyy", 0.0),
        Jx_unscaled=_field_float(row, "Jx_unscaled", 0.01),
        Jy_unscaled=_field_float(row, "Jy_unscaled", 0.0),
        Jz=_field_float(row, "Jz", 0.0),
        Jzx=_field_float(row, "Jzx", 0.0),
        Jcpm_unscaled=_field_float(row, "Jcpm_unscaled", 0.0),
        hx=_field_float(row, "hx", 0.0),
        hz=_field_float(row, "hz", 0.1),
        hz0_mode=str(row.get("hz0_mode", "matched")),
        connectivity=str(row.get("connectivity", "ring")),
        central_coupling=str(row.get("central_coupling") or "auto"),
        seed=int(_field_float(row, "seed", 44.0)),
        disorder=_field_text(row, "disorder", "none"),
        disorder_strength=_field_float(row, "disorder_strength", 0.0),
        disorder_strength_J=_field_float(row, "disorder_strength_J", 0.0),
        disorder_strength_Jpm=_field_float(row, "disorder_strength_Jpm", 0.0),
        disorder_strength_Jx=_field_float(row, "disorder_strength_Jx", 0.0),
        disorder_strength_Jz=_field_float(row, "disorder_strength_Jz", 0.0),
        disorder_strength_Jzx=_field_float(row, "disorder_strength_Jzx", 0.0),
        disorder_strength_Jcpm=_field_float(row, "disorder_strength_Jcpm", 0.0),
        disorder_strength_hx=_field_float(row, "disorder_strength_hx", 0.0),
        disorder_strength_hz=_field_float(row, "disorder_strength_hz", 0.0),
    )


def _candidate_key(candidate: Candidate) -> tuple[Any, ...]:
    return (
        candidate.model,
        candidate.N,
        candidate.J,
        candidate.Jpm,
        candidate.Jxx,
        candidate.Jyy,
        candidate.Jx_unscaled,
        candidate.Jy_unscaled,
        candidate.Jz,
        candidate.Jzx,
        candidate.Jcpm_unscaled,
        candidate.hx,
        candidate.hz,
        candidate.hz0_mode,
        candidate.connectivity,
        candidate.central_coupling,
        candidate.seed,
        candidate.disorder,
        candidate.disorder_strength,
        candidate.disorder_strength_J,
        candidate.disorder_strength_Jpm,
        candidate.disorder_strength_Jx,
        candidate.disorder_strength_Jz,
        candidate.disorder_strength_Jzx,
        candidate.disorder_strength_Jcpm,
        candidate.disorder_strength_hx,
        candidate.disorder_strength_hz,
    )


def _queue_group_key(row: dict[str, Any]) -> tuple[str, ...]:
    values = []
    for field in QUEUE_GROUP_FIELDS:
        value = row.get(field, "")
        if field == "central_coupling" and str(value).strip() == "":
            value = "auto"
        if field == "disorder" and str(value).strip() == "":
            value = "none"
        if field == "seed" and str(value).strip() == "":
            value = 44
        if field.startswith("disorder_strength") and str(value).strip() == "":
            value = 0.0
        values.append(_key_value(value))
    return tuple(values)


def _queue_n_values(row: dict[str, Any]) -> set[int]:
    text = str(row.get("n_values", "")).strip()
    values: set[int] = set()
    if text:
        for part in text.split(","):
            try:
                values.add(int(float(part.strip())))
            except ValueError:
                pass
    n_value = _float_or_nan(row.get("N"))
    if math.isfinite(n_value):
        values.add(int(n_value))
    return values


def _load_queue_entries(paths: list[Path]) -> list[tuple[tuple[str, ...], set[int]]]:
    entries: list[tuple[tuple[str, ...], set[int]]] = []
    seen: set[tuple[tuple[str, ...], tuple[int, ...]]] = set()
    for path in paths:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for raw in reader:
                key = _queue_group_key(raw)
                n_values = _queue_n_values(raw)
                marker = (key, tuple(sorted(n_values)))
                if marker in seen:
                    continue
                seen.add(marker)
                entries.append((key, n_values))
    return entries


def _row_sort_key(row: dict[str, Any]) -> float:
    for field in ("shortlist_group_score", "shortlist_score", "balanced_score", "objective_score", "born_similarity"):
        value = _float_or_nan(row.get(field))
        if math.isfinite(value):
            return value
    return -math.inf


def select_rows(rows: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    queue_entries = _load_queue_entries(args.queue_csv) if args.queue_csv else []
    if queue_entries and args.top_groups is not None:
        queue_entries = queue_entries[: args.top_groups]
    queue_lookup = {key: n_values for key, n_values in queue_entries}
    selected = []
    for row in rows:
        n_value = _float_or_nan(row.get("N"))
        if math.isfinite(n_value) and n_value < args.min_n:
            continue
        if math.isfinite(n_value) and n_value > args.max_n:
            continue
        if queue_entries:
            n_int = int(n_value) if math.isfinite(n_value) else None
            n_values = queue_lookup.get(_queue_group_key(row))
            if n_values is None:
                continue
            if n_values and n_int not in n_values:
                continue
        if args.family and str(row.get("family", "")) not in set(args.family):
            continue
        if args.mode == "primary" and _boolish(row.get("control_like")):
            continue
        if args.mode == "controls" and not _boolish(row.get("control_like")):
            continue
        if args.mode != "all" and "target_like" in row and not _boolish(row.get("target_like")):
            continue
        if abs(_field_float(row, "Jx_unscaled", 0.0)) > args.max_jx_unscaled:
            continue
        if abs(_field_float(row, "Jy_unscaled", 0.0)) > args.max_jy_unscaled:
            continue
        if abs(_field_float(row, "Jcpm_unscaled", 0.0)) > args.max_jcpm_unscaled:
            continue
        if abs(_field_float(row, "hx", 0.0)) > args.max_hx:
            continue
        if _float_or_nan(row.get("born_similarity")) < args.min_born_similarity:
            continue
        if _float_or_nan(row.get("radius_atomic_fraction")) > args.max_atomic_fraction:
            continue
        selected.append(row)

    if queue_entries:
        order = {key: idx for idx, (key, _n_values) in enumerate(queue_entries)}
        selected.sort(
            key=lambda row: (
                order.get(_queue_group_key(row), len(order)),
                _float_or_nan(row.get("N")),
                -_row_sort_key(row),
            )
        )
    else:
        selected.sort(key=_row_sort_key, reverse=True)
    unique: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for row in selected:
        candidate = _candidate_from_row(row)
        key = _candidate_key(candidate) + (_float_or_nan(row.get("t")),)
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
        if len(unique) >= args.top_rows:
            break
    return unique


def evaluate_stability(
    rows: list[dict[str, Any]],
    bins: list[int],
    tail_fractions: list[float],
    log_bins: int,
    backend: str,
    workers: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_candidate: dict[tuple[Any, ...], dict[str, Any]] = {}
    times_by_candidate: dict[tuple[Any, ...], set[float]] = defaultdict(set)
    source_by_pair: dict[tuple[tuple[Any, ...], float], dict[str, Any]] = {}

    for row in rows:
        candidate = _candidate_from_row(row)
        key = _candidate_key(candidate)
        time_value = _float_or_nan(row.get("t"))
        if not math.isfinite(time_value):
            continue
        by_candidate[key] = {"candidate": candidate}
        times_by_candidate[key].add(float(time_value))
        source_by_pair[(key, float(time_value))] = row

    jobs = []
    for idx, (key, payload) in enumerate(by_candidate.items(), 1):
        candidate: Candidate = payload["candidate"]
        source_by_time = {
            time_value: source_by_pair[(key, time_value)]
            for time_value in sorted(times_by_candidate[key])
        }
        jobs.append(
            (
                idx,
                candidate,
                sorted(times_by_candidate[key]),
                source_by_time,
                bins,
                tail_fractions,
                log_bins,
                backend,
            )
        )

    detailed_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    workers = max(1, int(workers))
    print(f"Worker processes: {workers}")

    if workers == 1 or len(jobs) <= 1:
        for idx, candidate, times, source_by_time, bins, tail_fractions, log_bins, backend in jobs:
            print(
                f"[{idx:03d}/{len(jobs):03d}] diagonalizing {_candidate_label(candidate)}",
                flush=True,
            )
            detailed, summary = _evaluate_stability_candidate_job(
                (candidate, times, source_by_time, bins, tail_fractions, log_bins, backend)
            )
            detailed_rows.extend(detailed)
            summary_rows.extend(summary)
    else:
        n_workers = min(workers, len(jobs))
        print(f"Submitting {len(jobs)} stability jobs to {n_workers} workers", flush=True)
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            future_to_candidate = {
                pool.submit(
                    _evaluate_stability_candidate_job,
                    (candidate, times, source_by_time, bins, tail_fractions, log_bins, backend),
                ): candidate
                for _idx, candidate, times, source_by_time, bins, tail_fractions, log_bins, backend in jobs
            }
            for done_idx, future in enumerate(as_completed(future_to_candidate), 1):
                candidate = future_to_candidate[future]
                try:
                    detailed, summary = future.result()
                except Exception as exc:
                    label = _candidate_label(candidate)
                    raise RuntimeError(f"Worker failed while evaluating stability for {label}") from exc
                detailed_rows.extend(detailed)
                summary_rows.extend(summary)
                print(
                    f"[{done_idx:03d}/{len(jobs):03d}] completed {_candidate_label(candidate)}",
                    flush=True,
                )

    summary_rows.sort(key=lambda row: row["stability_score"], reverse=True)
    detailed_rows.sort(key=lambda row: row["stability_group"])
    return detailed_rows, summary_rows


def _evaluate_stability_candidate_job(
    payload: tuple[Candidate, list[float], dict[float, dict[str, Any]], list[int], list[float], int, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidate, times, source_by_time, bins, tail_fractions, log_bins, backend = payload
    diagonalization = _diagonalize_candidate(candidate, backend)
    energy_metrics = _energy_metrics_from_diagonalization(diagonalization, tol=1e-9)
    detailed_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for time_value in sorted(times):
        source = source_by_time[time_value]
        start = time.time()
        analyzer = _analyzer_from_diagonalization(diagonalization, time_value, candidate.N)
        theta0, _theta1, radii = _angles_and_radii(analyzer)
        tail_free_metrics = heavy_tail_metrics(theta0, radii)
        per_setting: list[dict[str, Any]] = []

        for n_bins in bins:
            for tail_fraction in tail_fractions:
                core = diagnostics_from_radii(
                    radii,
                    n_theta=n_bins,
                    tail_fraction=tail_fraction,
                    n_log_bins=log_bins,
                )
                metrics = asdict(core)
                metrics.update(tail_free_metrics)
                metrics.update(energy_metrics)
                metrics["objective_score"] = objective_score(metrics)
                row_out = {
                    "stability_group": f"{_candidate_label(candidate)}__t{time_value:g}",
                    "family": source.get("family", ""),
                    "label": _candidate_label(candidate),
                    "model": candidate.model,
                    "N": candidate.N,
                    "t": time_value,
                    "connectivity": candidate.connectivity,
                    "central_coupling": candidate.central_coupling,
                    "hz0_mode": candidate.hz0_mode,
                    "seed": candidate.seed,
                    "disorder": candidate.disorder,
                    "disorder_strength": candidate.disorder_strength,
                    "disorder_strength_J": candidate.disorder_strength_J,
                    "disorder_strength_Jpm": candidate.disorder_strength_Jpm,
                    "disorder_strength_Jx": candidate.disorder_strength_Jx,
                    "disorder_strength_Jz": candidate.disorder_strength_Jz,
                    "disorder_strength_Jzx": candidate.disorder_strength_Jzx,
                    "disorder_strength_Jcpm": candidate.disorder_strength_Jcpm,
                    "disorder_strength_hx": candidate.disorder_strength_hx,
                    "disorder_strength_hz": candidate.disorder_strength_hz,
                    "J": candidate.J,
                    "Jx_unscaled": candidate.Jx_unscaled,
                    "Jy_unscaled": candidate.Jy_unscaled,
                    "Jpm": candidate.Jpm,
                    "Jxx": candidate.Jxx,
                    "Jyy": candidate.Jyy,
                    "Jz": candidate.Jz,
                    "Jzx": candidate.Jzx,
                    "Jcpm_unscaled": candidate.Jcpm_unscaled,
                    "hx": candidate.hx,
                    "hz": candidate.hz,
                    "n_bins": n_bins,
                    "tail_fraction": tail_fraction,
                    "backend": diagonalization["backend"],
                    "diagonalization_kind": diagonalization["kind"],
                    "symmetry_used": diagonalization["symmetry_used"],
                    "sector_count": diagonalization["sector_count"],
                    "fallback_reason": diagonalization["fallback_reason"],
                    "source_born_similarity": source.get("born_similarity", ""),
                    "source_tail_density_exponent": source.get("tail_density_exponent", ""),
                    "source_balanced_score": source.get("balanced_score", ""),
                    "analysis_wall_seconds": time.time() - start,
                }
                row_out.update(metrics)
                detailed_rows.append(row_out)
                per_setting.append(row_out)

        summary_rows.append(_summarize_setting_rows(candidate, time_value, source, per_setting))

    return detailed_rows, summary_rows


def _summarize_setting_rows(
    candidate: Candidate,
    time_value: float,
    source: dict[str, Any],
    setting_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    similarities = [row["born_similarity"] for row in setting_rows if math.isfinite(row["born_similarity"])]
    alphas = [row["tail_density_exponent"] for row in setting_rows if math.isfinite(row["tail_density_exponent"])]
    recips = [row["reciprocity_error"] for row in setting_rows if math.isfinite(row["reciprocity_error"])]
    objective_scores = [row["objective_score"] for row in setting_rows if math.isfinite(row["objective_score"])]
    spreads = [row["radius_q99_over_q50"] for row in setting_rows if math.isfinite(row["radius_q99_over_q50"])]
    atom_values = [row["radius_atomic_fraction"] for row in setting_rows if math.isfinite(row["radius_atomic_fraction"])]

    min_s = min(similarities) if similarities else math.nan
    mean_s = mean(similarities) if similarities else math.nan
    s_range = (max(similarities) - min_s) if similarities else math.nan
    median_alpha = median(alphas) if alphas else math.nan
    alpha_error = abs(median_alpha - 2.0) if math.isfinite(median_alpha) else math.nan
    median_recip = median(recips) if recips else math.nan
    max_spread = max(spreads) if spreads else math.nan
    min_atom = min(atom_values) if atom_values else math.nan

    stability_score = 0.0
    if math.isfinite(min_s):
        stability_score += 0.42 * min_s
    if math.isfinite(mean_s):
        stability_score += 0.18 * mean_s
    if math.isfinite(s_range):
        stability_score += 0.12 * math.exp(-s_range / 0.25)
    if math.isfinite(alpha_error):
        stability_score += 0.16 * math.exp(-alpha_error / 0.7)
    if math.isfinite(median_recip):
        stability_score += 0.07 * math.exp(-median_recip)
    if math.isfinite(max_spread):
        stability_score += 0.03 * min(1.0, math.log1p(max_spread) / math.log(40.0))
    if math.isfinite(min_atom):
        stability_score += 0.02 * (1.0 - min(1.0, min_atom))

    label = _candidate_label(candidate)
    return {
        "stability_group": f"{label}__t{time_value:g}",
        "stability_score": stability_score,
        "family": source.get("family", ""),
        "label": label,
        "model": candidate.model,
        "N": candidate.N,
        "t": time_value,
        "connectivity": candidate.connectivity,
        "central_coupling": candidate.central_coupling,
        "hz0_mode": candidate.hz0_mode,
        "seed": candidate.seed,
        "disorder": candidate.disorder,
        "disorder_strength": candidate.disorder_strength,
        "disorder_strength_J": candidate.disorder_strength_J,
        "disorder_strength_Jpm": candidate.disorder_strength_Jpm,
        "disorder_strength_Jx": candidate.disorder_strength_Jx,
        "disorder_strength_Jz": candidate.disorder_strength_Jz,
        "disorder_strength_Jzx": candidate.disorder_strength_Jzx,
        "disorder_strength_Jcpm": candidate.disorder_strength_Jcpm,
        "disorder_strength_hx": candidate.disorder_strength_hx,
        "disorder_strength_hz": candidate.disorder_strength_hz,
        "J": candidate.J,
        "Jx_unscaled": candidate.Jx_unscaled,
        "Jy_unscaled": candidate.Jy_unscaled,
        "Jpm": candidate.Jpm,
        "Jxx": candidate.Jxx,
        "Jyy": candidate.Jyy,
        "Jz": candidate.Jz,
        "Jzx": candidate.Jzx,
        "Jcpm_unscaled": candidate.Jcpm_unscaled,
        "hx": candidate.hx,
        "hz": candidate.hz,
        "source_born_similarity": source.get("born_similarity", ""),
        "source_tail_density_exponent": source.get("tail_density_exponent", ""),
        "source_balanced_score": source.get("balanced_score", ""),
        "backend": setting_rows[0].get("backend", "") if setting_rows else "",
        "diagonalization_kind": setting_rows[0].get("diagonalization_kind", "") if setting_rows else "",
        "symmetry_used": setting_rows[0].get("symmetry_used", "") if setting_rows else "",
        "sector_count": setting_rows[0].get("sector_count", "") if setting_rows else "",
        "fallback_reason": setting_rows[0].get("fallback_reason", "") if setting_rows else "",
        "energy_degenerate_fraction": setting_rows[0].get("energy_degenerate_fraction", math.nan) if setting_rows else math.nan,
        "energy_degenerate_cluster_fraction": setting_rows[0].get("energy_degenerate_cluster_fraction", math.nan) if setting_rows else math.nan,
        "energy_max_multiplicity": setting_rows[0].get("energy_max_multiplicity", math.nan) if setting_rows else math.nan,
        "energy_resolved_level_count": setting_rows[0].get("energy_resolved_level_count", math.nan) if setting_rows else math.nan,
        "energy_mean_spacing_ratio": setting_rows[0].get("energy_mean_spacing_ratio", math.nan) if setting_rows else math.nan,
        "energy_min_spacing": setting_rows[0].get("energy_min_spacing", math.nan) if setting_rows else math.nan,
        "mean_born_similarity": mean_s,
        "min_born_similarity": min_s,
        "range_born_similarity": s_range,
        "median_tail_density_exponent": median_alpha,
        "median_tail_error": alpha_error,
        "median_reciprocity_error": median_recip,
        "mean_objective_score": mean(objective_scores) if objective_scores else math.nan,
        "max_radius_q99_over_q50": max_spread,
        "min_radius_atomic_fraction": min_atom,
        "settings_count": len(setting_rows),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, summary_rows: list[dict[str, Any]], top: int) -> None:
    lines = [
        "# Born Candidate Metric Stability",
        "",
        "| rank | stability | mean S | min S | range S | alpha med | recip med | E deg frac | E max mult | atom min | q99/q50 max | signature |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---|",
    ]
    for rank, row in enumerate(summary_rows[:top], 1):
        signature = (
            f"{row['family']} N={row['N']} {row['connectivity']} hz0={row['hz0_mode']} "
            f"cc={row.get('central_coupling', 'auto')} "
            f"dis={_disorder_signature(row)} "
            f"J={_fmt_g(row.get('J'))} Jx={_fmt_g(row['Jx_unscaled'])} Jy={_fmt_g(row.get('Jy_unscaled'))} "
            f"hz={_fmt_g(row['hz'])} Jpm={_fmt_g(row['Jpm'])} "
            f"Jxx={_fmt_g(row.get('Jxx'))} Jyy={_fmt_g(row.get('Jyy'))} "
            f"Jz={_fmt_g(row.get('Jz'))} Jzx={_fmt_g(row.get('Jzx'))} "
            f"Jcpm={_fmt_g(row['Jcpm_unscaled'])} t={_fmt_g(row['t'])}"
        )
        lines.append(
            "| {rank} | {score} | {mean_s} | {min_s} | {range_s} | {alpha} | {recip} | {edeg} | {emult} | {atom} | {spread} | {sig} |".format(
                rank=rank,
                score=_fmt(row["stability_score"], 4),
                mean_s=_fmt(row["mean_born_similarity"], 4),
                min_s=_fmt(row["min_born_similarity"], 4),
                range_s=_fmt(row["range_born_similarity"], 4),
                alpha=_fmt(row["median_tail_density_exponent"]),
                recip=_fmt(row["median_reciprocity_error"]),
                edeg=_fmt(row["energy_degenerate_fraction"]),
                emult=_fmt(row["energy_max_multiplicity"], 0),
                atom=_fmt(row["min_radius_atomic_fraction"]),
                spread=_fmt(row["max_radius_q99_over_q50"], 2),
                sig=signature,
            )
        )
    lines.extend(
        [
            "",
            "Metric notes:",
            "- `min S` is the conservative score across all requested theta-bin and tail-fraction settings.",
            "- A good candidate should retain moderate/high `min S`, small `range S`, low atomic fraction, and tail exponent near 2.",
            "- Degenerate-spectrum candidates should be interpreted together with `E deg frac`, `E max mult`, and atom fraction to separate real reciprocal tails from discrete multiplet artifacts.",
            "- This is a metric-stability screen only; finite-size stability still requires Zeus `N>=13` runs.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recompute selected Born candidates across metric settings.")
    parser.add_argument(
        "--source-csv",
        type=Path,
        nargs="+",
        default=[Path("figures/zeus_born_hamiltonian_search/summary_rows.csv")],
    )
    parser.add_argument("--out-dir", type=Path, default=Path("figures/born_candidate_stability"))
    parser.add_argument("--mode", choices=["primary", "controls", "all"], default="primary")
    parser.add_argument("--top-rows", type=int, default=8)
    parser.add_argument("--min-n", type=int, default=0)
    parser.add_argument("--max-n", type=int, default=12)
    parser.add_argument("--family", nargs="+", default=[])
    parser.add_argument(
        "--queue-csv",
        type=Path,
        nargs="+",
        default=[],
        help="Optional shortlist CSV whose parameter groups define the row queue.",
    )
    parser.add_argument(
        "--top-groups",
        type=int,
        default=None,
        help="When --queue-csv is set, limit to this many queued parameter groups before row expansion.",
    )
    parser.add_argument("--min-born-similarity", type=float, default=0.35)
    parser.add_argument("--max-atomic-fraction", type=float, default=0.25)
    parser.add_argument("--max-jx-unscaled", type=float, default=0.05)
    parser.add_argument("--max-jy-unscaled", type=float, default=0.05)
    parser.add_argument("--max-jcpm-unscaled", type=float, default=0.05)
    parser.add_argument("--max-hx", type=float, default=0.05)
    parser.add_argument("--bins", type=int, nargs="+", default=[60, 80, 120])
    parser.add_argument("--tail-fractions", type=float, nargs="+", default=[0.05, 0.10, 0.20])
    parser.add_argument("--log-bins", type=int, default=40)
    parser.add_argument("--backend", choices=["auto", "quspin", "numpy"], default="auto")
    parser.add_argument(
        "--workers",
        type=int,
        default=_default_worker_count(),
        help=(
            "Number of independent candidate Hamiltonians to evaluate in parallel. "
            "Defaults to BORN_WORKERS, then PBS_NP, then 1."
        ),
    )
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Progress log path. Defaults to <out-dir>/run.log.",
    )
    return parser.parse_args()


def run_stability(args: argparse.Namespace) -> None:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Log file: {args.log_file}")
    rows = _load_rows(args.source_csv)
    selected = select_rows(rows, args)
    if not selected:
        raise SystemExit("No rows matched the requested filters")
    print(f"Selected {len(selected)} candidate/time rows")
    detailed_rows, summary_rows = evaluate_stability(
        selected,
        bins=args.bins,
        tail_fractions=args.tail_fractions,
        log_bins=args.log_bins,
        backend=args.backend,
        workers=args.workers,
    )

    detailed_path = args.out_dir / "stability_detailed.csv"
    summary_path = args.out_dir / "stability_summary.csv"
    md_path = args.out_dir / "stability_summary.md"
    write_csv(detailed_path, detailed_rows)
    write_csv(summary_path, summary_rows)
    write_markdown(md_path, summary_rows, args.top)
    print(f"Wrote {detailed_path}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {md_path}")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.log_file is None:
        args.log_file = args.out_dir / "run.log"
    args.log_file.parent.mkdir(parents=True, exist_ok=True)

    with args.log_file.open("w", encoding="utf-8", buffering=1) as log_fh:
        stdout = TeeWriter(sys.stdout, log_fh)
        stderr = TeeWriter(sys.stderr, log_fh)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            run_stability(args)


if __name__ == "__main__":
    main()
