"""
Summarize Born-rule Hamiltonian search result folders.

The search script writes one ``results.csv`` per parameter family.  This
post-processing script combines those tables, adds a target-oriented ranking,
and writes a compact Markdown report for deciding the next Zeus scan.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any


NUMERIC_FIELDS = {
    "rank",
    "objective_score",
    "N",
    "N_pixel",
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
    "Jx_unscaled",
    "Jx_scaled",
    "Jy_unscaled",
    "Jy_scaled",
    "hz",
    "Jpm",
    "Jxx",
    "Jyy",
    "J",
    "Jz",
    "Jzx",
    "Jcpm_unscaled",
    "Jcpm_scaled",
    "hx",
    "born_similarity",
    "mean_abs_ratio_error",
    "reciprocity_error",
    "tail_density_exponent",
    "tail_survival_exponent",
    "tail_xmin",
    "energy_degenerate_fraction",
    "energy_degenerate_cluster_fraction",
    "energy_max_multiplicity",
    "energy_resolved_level_count",
    "energy_mean_spacing_ratio",
    "energy_min_spacing",
    "radius_q99_over_q50",
    "radius_unique_count",
    "radius_atomic_fraction",
    "radius_zero_fraction",
    "radius_positive_fraction",
    "theta_q95",
    "theta_q99",
    "theta_mass_gt_0p5",
    "theta_mass_gt_1p0",
    "diagonalization_wall_seconds",
    "analysis_wall_seconds",
}

GROUP_FIELDS = (
    "family",
    "model",
    "N",
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
)


def _float_or_nan(value: Any) -> float:
    if value is None:
        return math.nan
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


def _is_finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _fmt(value: Any, digits: int = 3) -> str:
    if not _is_finite(value):
        return "nan"
    number = float(value)
    if abs(number) >= 10000 or (0 < abs(number) < 0.001):
        return f"{number:.{digits}e}"
    return f"{number:.{digits}f}"


def _fmt_g(value: Any) -> str:
    if not _is_finite(value):
        return "nan"
    return f"{float(value):g}"


def _as_key_value(value: Any) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        return f"{value:.12g}"
    return str(value)


def _group_field_value(row: dict[str, Any], field: str) -> Any:
    value = row.get(field, "")
    if field == "central_coupling" and str(value).strip() == "":
        return "auto"
    if field == "disorder" and str(value).strip() == "":
        return "none"
    if field == "seed" and str(value).strip() == "":
        return 44
    if field.startswith("disorder_strength") and str(value).strip() == "":
        return 0.0
    return value


def _load_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for csv_path in sorted(root.rglob("results.csv")):
        family = csv_path.parent.name
        with csv_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for raw in reader:
                row: dict[str, Any] = dict(raw)
                row["family"] = family
                row["source_csv"] = str(csv_path)
                for field in NUMERIC_FIELDS:
                    if field in row:
                        row[field] = _float_or_nan(row[field])
                row["N"] = int(row["N"]) if _is_finite(row.get("N")) else row.get("N")
                row["N_pixel"] = (
                    int(row["N_pixel"]) if _is_finite(row.get("N_pixel")) else row.get("N_pixel")
                )
                row["balanced_score"] = balanced_score(row)
                row["perturbative_coupling_score"] = perturbative_coupling_score(row)
                row["perturbative_balanced_score"] = perturbative_balanced_score(row)
                row["local_resonance_distance"] = local_resonance_distance(row)
                row["local_resonance_label"] = local_resonance_label(row)
                row["perturbative_like"] = is_perturbative_like(row)
                row["target_like"] = is_target_like(row)
                row["control_like"] = is_control_like(row)
                rows.append(row)
    return rows


def balanced_score(row: dict[str, Any]) -> float:
    """Score rows against the analytic target instead of only high S_born."""

    similarity = _float_or_nan(row.get("born_similarity"))
    alpha = _float_or_nan(row.get("tail_density_exponent"))
    recip = _float_or_nan(row.get("reciprocity_error"))
    spread = _float_or_nan(row.get("radius_q99_over_q50"))
    atom = _float_or_nan(row.get("radius_atomic_fraction"))
    mass = _float_or_nan(row.get("theta_mass_gt_0p5"))

    s_score = similarity if math.isfinite(similarity) else 0.0
    tail_score = math.exp(-abs(alpha - 2.0) / 0.65) if math.isfinite(alpha) else 0.0
    recip_score = math.exp(-recip) if math.isfinite(recip) else 0.0
    spread_score = 0.0
    if math.isfinite(spread) and spread > 0:
        spread_score = min(1.0, math.log1p(spread) / math.log(40.0))
    atom_score = 1.0 - min(1.0, atom) if math.isfinite(atom) else 0.0
    mass_score = min(1.0, mass / 0.25) if math.isfinite(mass) else 0.0

    return (
        0.48 * s_score
        + 0.22 * tail_score
        + 0.13 * recip_score
        + 0.08 * spread_score
        + 0.05 * atom_score
        + 0.04 * mass_score
    )


def perturbative_coupling_score(row: dict[str, Any]) -> float:
    """Prefer small central detector couplings for the physical search target."""

    jx = abs(_float_or_nan(row.get("Jx_unscaled")))
    jy = abs(_float_or_nan(row.get("Jy_unscaled")))
    jcpm = abs(_float_or_nan(row.get("Jcpm_unscaled")))
    hx = abs(_float_or_nan(row.get("hx")))
    if not math.isfinite(jx):
        jx = 0.0
    if not math.isfinite(jy):
        jy = 0.0
    if not math.isfinite(jcpm):
        jcpm = 0.0
    if not math.isfinite(hx):
        hx = 0.0
    scale = max(jx / 0.05, jy / 0.05, jcpm / 0.05, hx / 0.05)
    return float(math.exp(-max(0.0, scale - 1.0)))


def is_perturbative_like(row: dict[str, Any]) -> bool:
    jx = abs(_float_or_nan(row.get("Jx_unscaled")))
    jy = abs(_float_or_nan(row.get("Jy_unscaled")))
    jcpm = abs(_float_or_nan(row.get("Jcpm_unscaled")))
    hx = abs(_float_or_nan(row.get("hx")))
    jx = jx if math.isfinite(jx) else 0.0
    jy = jy if math.isfinite(jy) else 0.0
    jcpm = jcpm if math.isfinite(jcpm) else 0.0
    hx = hx if math.isfinite(hx) else 0.0
    return jx <= 0.05 and jy <= 0.05 and jcpm <= 0.05 and hx <= 0.05


def perturbative_balanced_score(row: dict[str, Any]) -> float:
    return _float_or_nan(row.get("balanced_score")) * perturbative_coupling_score(row)


def _effective_hz0(row: dict[str, Any]) -> float:
    hz = _float_or_nan(row.get("hz"))
    mode = str(row.get("hz0_mode", "matched"))
    if not math.isfinite(hz):
        return math.nan
    if mode == "matched":
        return hz
    if mode == "zero":
        return 0.0
    if mode == "half":
        return 0.5 * hz
    if mode == "minus":
        return -hz
    return math.nan


def local_resonance_distance(row: dict[str, Any]) -> float:
    """Distance to the ring local-field resonance surface."""

    if str(row.get("model", "")) != "single_pixel" or str(row.get("connectivity", "")) != "ring":
        return math.nan
    hz0 = _effective_hz0(row)
    hz = _float_or_nan(row.get("hz"))
    J = _float_or_nan(row.get("J"))
    if not math.isfinite(J):
        J = 1.0
    if not math.isfinite(hz0) or not math.isfinite(hz):
        return math.nan
    distances = [
        abs(hz0 + s * (hz + J * r))
        for s in (-1.0, 1.0)
        for r in (-2.0, 0.0, 2.0)
    ]
    return min(distances)


def local_resonance_label(row: dict[str, Any]) -> str:
    distance = local_resonance_distance(row)
    if not math.isfinite(distance):
        return "n/a"
    if distance <= 1.0e-9:
        return "exact"
    if distance <= 0.05:
        return "near"
    return "off"


def is_target_like(row: dict[str, Any]) -> bool:
    alpha = _float_or_nan(row.get("tail_density_exponent"))
    atom = _float_or_nan(row.get("radius_atomic_fraction"))
    spread = _float_or_nan(row.get("radius_q99_over_q50"))
    similarity = _float_or_nan(row.get("born_similarity"))
    return (
        math.isfinite(alpha)
        and 1.5 <= alpha <= 3.0
        and math.isfinite(atom)
        and atom <= 0.25
        and math.isfinite(spread)
        and spread >= 5.0
        and math.isfinite(similarity)
        and similarity >= 0.35
        and is_perturbative_like(row)
    )


def is_control_like(row: dict[str, Any]) -> bool:
    family = str(row.get("family", ""))
    hz0 = str(row.get("hz0_mode", ""))
    connectivity = str(row.get("connectivity", ""))
    return (
        "chain" in family
        or "sz_conserving" in family
        or connectivity == "chain"
        or hz0 in {"zero", "minus", "half"}
    )


def _sort_rows(rows: list[dict[str, Any]], key: str, reverse: bool = True) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: _sort_score(row.get(key)),
        reverse=reverse,
    )


def _sort_score(value: Any) -> float:
    number = _float_or_nan(value)
    return number if math.isfinite(number) else -math.inf


def _group_key(row: dict[str, Any]) -> tuple[str, ...]:
    values = []
    for field in GROUP_FIELDS:
        value = _group_field_value(row, field)
        values.append(_as_key_value(value))
    return tuple(values)


def _summarize_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_group_key(row)].append(row)

    summaries: list[dict[str, Any]] = []
    for key, group_rows in grouped.items():
        if len(group_rows) < 2:
            continue
        best = max(group_rows, key=lambda row: _float_or_nan(row.get("balanced_score")))
        similarities = [_float_or_nan(row.get("born_similarity")) for row in group_rows]
        alphas = [_float_or_nan(row.get("tail_density_exponent")) for row in group_rows]
        recips = [_float_or_nan(row.get("reciprocity_error")) for row in group_rows]
        atoms = [_float_or_nan(row.get("radius_atomic_fraction")) for row in group_rows]
        spreads = [_float_or_nan(row.get("radius_q99_over_q50")) for row in group_rows]
        scores = [_float_or_nan(row.get("balanced_score")) for row in group_rows]
        perturbative_rows = [row for row in group_rows if row["perturbative_like"]]
        finite = lambda values: [value for value in values if math.isfinite(value)]
        finite_sim = finite(similarities)
        finite_alpha = finite(alphas)
        finite_recip = finite(recips)
        finite_atom = finite(atoms)
        finite_spread = finite(spreads)
        finite_score = finite(scores)
        target_rows = [row for row in group_rows if row["target_like"]]
        summary = {field: value for field, value in zip(GROUP_FIELDS, key)}
        summary.update(
            {
                "n_times": len({row.get("t") for row in group_rows}),
                "times": ",".join(_fmt_g(row.get("t")) for row in sorted(group_rows, key=lambda r: _float_or_nan(r.get("t")))),
                "best_t": best.get("t"),
                "best_score": best.get("balanced_score"),
                "mean_score": mean(finite_score) if finite_score else math.nan,
                "max_S": max(finite_sim) if finite_sim else math.nan,
                "mean_S": mean(finite_sim) if finite_sim else math.nan,
                "median_alpha": median(finite_alpha) if finite_alpha else math.nan,
                "median_alpha_error": (
                    median(abs(value - 2.0) for value in finite_alpha) if finite_alpha else math.nan
                ),
                "median_reciprocity": median(finite_recip) if finite_recip else math.nan,
                "min_atom": min(finite_atom) if finite_atom else math.nan,
                "max_spread": max(finite_spread) if finite_spread else math.nan,
                "target_like_times": len(target_rows),
                "control_like": best["control_like"],
                "perturbative_like": len(perturbative_rows) == len(group_rows),
                "label": best.get("label", ""),
            }
        )
        summary["robust_score"] = (
            0.45 * _float_or_nan(summary["mean_S"])
            + 0.25 * math.exp(-_float_or_nan(summary["median_alpha_error"]) / 0.65)
            + 0.15 * math.exp(-_float_or_nan(summary["median_reciprocity"]))
            + 0.10 * min(
                1.0,
                math.log1p(_float_or_nan(summary["max_spread"])) / math.log(40.0),
            )
            + 0.05 * (summary["target_like_times"] / max(1, summary["n_times"]))
        )
        summaries.append(summary)

    return sorted(summaries, key=lambda row: _sort_score(row["robust_score"]), reverse=True)


def _row_signature(row: dict[str, Any]) -> str:
    return (
        f"{row['family']} N={row['N']} {row['connectivity']} "
        f"cc={row.get('central_coupling', 'auto')} hz0={row['hz0_mode']} "
        f"dis={row.get('disorder', 'none') or 'none'} "
        f"J={_fmt_g(row.get('J'))} Jx={_fmt_g(row['Jx_unscaled'])} Jy={_fmt_g(row.get('Jy_unscaled'))} "
        f"hz={_fmt_g(row['hz'])} Jpm={_fmt_g(row['Jpm'])} "
        f"Jxx={_fmt_g(row.get('Jxx'))} Jyy={_fmt_g(row.get('Jyy'))} "
        f"Jz={_fmt_g(row.get('Jz'))} Jzx={_fmt_g(row.get('Jzx'))} "
        f"Jcpm={_fmt_g(row['Jcpm_unscaled'])} "
        f"t={_fmt_g(row['t'])}"
    )


def _row_table(
    rows: list[dict[str, Any]],
    top: int,
    score_key: str = "balanced_score",
    score_label: str = "score",
) -> list[str]:
    lines = [
        f"| rank | {score_label} | S | alpha | recip | E deg frac | E max mult | atom | q99/q50 | d_res | pert | signature |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---|",
    ]
    for rank, row in enumerate(rows[:top], 1):
        lines.append(
            "| {rank} | {score} | {S} | {alpha} | {recip} | {edeg} | {emult} | {atom} | {spread} | {dres} | {pert} | {sig} |".format(
                rank=rank,
                score=_fmt(row.get(score_key), 4),
                S=_fmt(row.get("born_similarity"), 4),
                alpha=_fmt(row.get("tail_density_exponent")),
                recip=_fmt(row.get("reciprocity_error")),
                edeg=_fmt(row.get("energy_degenerate_fraction")),
                emult=_fmt(row.get("energy_max_multiplicity"), 0),
                atom=_fmt(row.get("radius_atomic_fraction")),
                spread=_fmt(row.get("radius_q99_over_q50"), 2),
                dres=_fmt(row.get("local_resonance_distance")),
                pert="yes" if row.get("perturbative_like") else "no",
                sig=_row_signature(row),
            )
        )
    return lines


def _group_table(groups: list[dict[str, Any]], top: int) -> list[str]:
    lines = [
        "| rank | robust | mean S | max S | median alpha | recip | target times | signature |",
        "|---:|---:|---:|---:|---:|---:|---:|:---|",
    ]
    for rank, group in enumerate(groups[:top], 1):
        signature = (
            f"{group['family']} N={group['N']} {group['connectivity']} "
            f"cc={group.get('central_coupling', 'auto')} "
            f"hz0={group['hz0_mode']} dis={group.get('disorder', 'none') or 'none'} "
            f"J={group.get('J', 'nan')} "
            f"Jx={group['Jx_unscaled']} Jy={group.get('Jy_unscaled', 'nan')} "
            f"hz={group['hz']} Jpm={group['Jpm']} Jxx={group.get('Jxx', 'nan')} "
            f"Jyy={group.get('Jyy', 'nan')} Jz={group.get('Jz', 'nan')} "
            f"Jzx={group.get('Jzx', 'nan')} Jcpm={group['Jcpm_unscaled']} times={group['times']}"
        )
        lines.append(
            "| {rank} | {score} | {mean_s} | {max_s} | {alpha} | {recip} | {target}/{times} | {sig} |".format(
                rank=rank,
                score=_fmt(group.get("robust_score"), 4),
                mean_s=_fmt(group.get("mean_S"), 4),
                max_s=_fmt(group.get("max_S"), 4),
                alpha=_fmt(group.get("median_alpha")),
                recip=_fmt(group.get("median_reciprocity")),
                target=group.get("target_like_times"),
                times=group.get("n_times"),
                sig=signature,
            )
        )
    return lines


def _family_notes(rows: list[dict[str, Any]]) -> list[str]:
    lines = []
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_family[str(row["family"])].append(row)
    for family in sorted(by_family):
        family_rows = by_family[family]
        best_score = max(family_rows, key=lambda row: _float_or_nan(row["balanced_score"]))
        best_s = max(family_rows, key=lambda row: _float_or_nan(row["born_similarity"]))
        targets = [row for row in family_rows if row["target_like"]]
        lines.append(
            "- `{family}`: {count} rows, {targets} target-like. Best balanced: {balanced}. "
            "Best S: S={S} at {sig}.".format(
                family=family,
                count=len(family_rows),
                targets=len(targets),
                balanced=_row_signature(best_score),
                S=_fmt(best_s.get("born_similarity"), 4),
                sig=_row_signature(best_s),
            )
        )
    return lines


def write_enriched_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    base_fields = [
        "family",
        "balanced_score",
        "perturbative_balanced_score",
        "perturbative_coupling_score",
        "perturbative_like",
        "local_resonance_distance",
        "local_resonance_label",
        "target_like",
        "control_like",
        "objective_score",
        "N",
        "model",
        "t",
        "backend",
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
        "Jx_scaled",
        "Jy_unscaled",
        "Jy_scaled",
        "hz",
        "Jpm",
        "Jxx",
        "Jyy",
        "Jz",
        "Jzx",
        "Jcpm_unscaled",
        "Jcpm_scaled",
        "hx",
        "born_similarity",
        "mean_abs_ratio_error",
        "reciprocity_error",
        "tail_density_exponent",
        "tail_survival_exponent",
        "energy_degenerate_fraction",
        "energy_degenerate_cluster_fraction",
        "energy_max_multiplicity",
        "energy_resolved_level_count",
        "energy_mean_spacing_ratio",
        "energy_min_spacing",
        "radius_q99_over_q50",
        "radius_atomic_fraction",
        "theta_q95",
        "theta_q99",
        "theta_mass_gt_0p5",
        "theta_mass_gt_1p0",
        "label",
        "source_csv",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=base_fields, extrasaction="ignore")
        writer.writeheader()
        for row in sorted(rows, key=lambda r: _sort_score(r["perturbative_balanced_score"]), reverse=True):
            writer.writerow(row)


def write_markdown(path: Path, rows: list[dict[str, Any]], top: int) -> None:
    target_rows = [row for row in rows if row["target_like"]]
    noncontrol_targets = [row for row in target_rows if not row["control_like"]]
    primary_large_targets = [
        row for row in noncontrol_targets if _is_finite(row.get("N")) and float(row["N"]) >= 12
    ]
    control_targets = [row for row in target_rows if row["control_like"]]
    groups = _summarize_groups(rows)
    noncontrol_groups = [
        group for group in groups if not group["control_like"] and group["perturbative_like"]
    ]

    lines = [
        "# Zeus Born Hamiltonian Search Summary",
        "",
        f"Root: `{path.parent}`",
        f"Rows: {len(rows)}",
        f"Families: {len({row['family'] for row in rows})}",
        f"Perturbative target-like rows: {len(target_rows)} ({len(noncontrol_targets)} primary, {len(control_targets)} controls)",
        "",
        "Target-like means: finite tail density exponent in [1.5, 3.0], atomic fraction <= 0.25, q99/q50 >= 5, S_born >= 0.35, and central detector couplings `Jx_unscaled`, `Jy_unscaled`, `Jcpm_unscaled`, `hx` <= 0.05.",
        "",
        "## Perturbative Primary Target Rows",
        "",
    ]
    lines.extend(
        _row_table(
            _sort_rows(noncontrol_targets, "perturbative_balanced_score"),
            top,
            score_key="perturbative_balanced_score",
            score_label="pert score",
        )
    )
    lines.extend(
        [
            "",
            "## Primary Rows With N >= 12",
            "",
        ]
    )
    lines.extend(
        _row_table(
            _sort_rows(primary_large_targets, "perturbative_balanced_score"),
            top,
            score_key="perturbative_balanced_score",
            score_label="pert score",
        )
    )
    lines.extend(
        [
            "",
            "## Control Or Detuned Rows",
            "",
        ]
    )
    lines.extend(
        _row_table(
            _sort_rows(control_targets, "perturbative_balanced_score"),
            top,
            score_key="perturbative_balanced_score",
            score_label="pert score",
        )
    )
    lines.extend(
        [
            "",
            "## Best Rows By Original Objective",
            "",
        ]
    )
    lines.extend(
        _row_table(
            _sort_rows(rows, "objective_score"),
            top,
            score_key="objective_score",
            score_label="objective",
        )
    )
    lines.extend(
        [
            "",
            "## Robust Parameter Groups",
            "",
        ]
    )
    lines.extend(_group_table(noncontrol_groups, top))
    lines.extend(
        [
            "",
            "## Family Notes",
            "",
        ]
    )
    lines.extend(_family_notes(rows))
    lines.extend(
        [
            "",
            "## Current Interpretation",
            "",
            "- The cleanest primary candidate remains the perturbative matched single-pixel ring near `N=12`, `Jx_unscaled=0.05`, `hz=0.1`, with `Jpm=0` or `Jpm=0.1` and times around `1000` to `10000`.",
            "- The exact-Sz exchange scan produces heavy radius spreads and tail exponents near 2, but its Born similarity is essentially zero; tail heaviness alone is not enough.",
            "- Chain controls are weaker than ring candidates in this scan.",
            "- Detuned and `hz0=zero` rows can score surprisingly well at `N=11`; treat them as finite-size/sign-symmetry controls until they survive larger-N checks.",
            "",
            "## Recommended Next Zeus Scan",
            "",
            "- Primary finite-size sweep: matched ring, `N=12 13 14`, perturbative `Jx_unscaled=0.02 0.03 0.04 0.05`, `hz=0.08 0.1 0.12`, `Jpm=0 0.05 0.1`, times `316 1000 3162 10000 31623`.",
            "- Control validation: repeat the high-scoring detuned/zero-field rows at `N=12 13 14` with `hz0-modes zero minus`, `Jpm=0 0.1 0.2`, perturbative `Jx_unscaled=0.03 0.05`, `hz=0.05 0.1`, times `100 1000 10000`.",
            "- Negative controls: chain at the matched primary grid, and exact-Sz exchange with `Jx_unscaled=0`, `Jcpm_unscaled=0.02 0.05`, to confirm the no-Born-ratio result.",
            "- Anisotropy follow-up: compare `Jpm` exchange against independent `Jxx`/`Jyy` bath weights and central `Jy_unscaled`, keeping detector couplings perturbative.",
            "",
            "The next follow-up should prioritize N-scaling over wider coupling sweeps: the promising effect is already localized, and the main risk is finite-size aliasing.",
            "",
            "Detuned controls should be interpreted against `local_resonance_distance`: `matched` and `minus` are exact local-field resonance surfaces for the `r=0` ring channel, while `zero` can be near-resonant when `hz` is small.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize Born Hamiltonian search result CSVs.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("figures/zeus_born_hamiltonian_search"),
        help="Directory containing one or more results.csv files.",
    )
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--out-csv", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = _load_rows(args.root)
    if not rows:
        raise SystemExit(f"No results.csv files found under {args.root}")

    out_md = args.out_md or args.root / "summary.md"
    out_csv = args.out_csv or args.root / "summary_rows.csv"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    write_enriched_csv(out_csv, rows)
    write_markdown(out_md, rows, args.top)
    print(f"Wrote {out_md}")
    print(f"Wrote {out_csv}")


if __name__ == "__main__":
    main()
