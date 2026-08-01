"""
Compare Zeus Born follow-up diagnostics across system size.

This is a post-processing step for imported ``summary_rows.csv`` files.  It
does not diagonalize Hamiltonians; it groups already-computed diagnostics by
Hamiltonian/time parameters and checks whether perturbative candidates persist
from N=12 through larger N.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any


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
    "Jx_unscaled",
    "Jy_unscaled",
    "hz",
    "Jpm",
    "Jxx",
    "Jyy",
    "Jz",
    "Jzx",
    "Jcpm_unscaled",
    "hx",
    "born_similarity",
    "tail_density_exponent",
    "reciprocity_error",
    "radius_atomic_fraction",
    "radius_q99_over_q50",
    "perturbative_balanced_score",
}

PRIMARY_FAMILIES = {
    "primary_matched_ring_N12",
    "primary_matched_ring_N13",
    "primary_matched_ring_N14",
    "ring_baseline_matched_N15_N16",
    "ring_anisotropic_xx_yy_N15_N16",
    "ring_weak_zz_anisotropic_N15_N16",
    "ring_strong_zz_anisotropic_N15_N16",
    "ring_central_coupling_channels_N15_N16",
}

GROUP_FIELDS = (
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


def _boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            row: dict[str, Any] = dict(raw)
            for field in NUMERIC_FIELDS:
                if field in row:
                    row[field] = _float_or_nan(row[field])
            if math.isfinite(_float_or_nan(row.get("N"))):
                row["N"] = int(row["N"])
            rows.append(row)
    return rows


def _key(row: dict[str, Any]) -> tuple[str, ...]:
    values = []
    for field in GROUP_FIELDS:
        value = row.get(field, "")
        if field == "central_coupling" and str(value).strip() == "":
            value = "auto"
        if field == "disorder" and str(value).strip() == "":
            value = "none"
        if field == "seed" and str(value).strip() == "":
            value = 44
        if field.startswith("disorder_strength") and str(value).strip() == "":
            value = 0.0
        values.append(_fmt_g(value) if field in NUMERIC_FIELDS else str(value))
    return tuple(values)


def _signature(group: dict[str, Any]) -> str:
    return (
        f"{group['connectivity']} cc={group.get('central_coupling', 'auto')} hz0={group['hz0_mode']} "
        f"dis={group.get('disorder', 'none') or 'none'} "
        f"J={group.get('J', 'nan')} Jx={group['Jx_unscaled']} Jy={group.get('Jy_unscaled', 'nan')} "
        f"hz={group['hz']} Jpm={group['Jpm']} "
        f"Jxx={group.get('Jxx', 'nan')} Jyy={group.get('Jyy', 'nan')} "
        f"Jz={group.get('Jz', 'nan')} Jzx={group.get('Jzx', 'nan')} "
        f"Jcpm={group['Jcpm_unscaled']} t={group['t']}"
    )


def _summarize_primary_scaling(
    rows: list[dict[str, Any]],
    n_filter: set[int] | None = None,
) -> list[dict[str, Any]]:
    primary = [
        row
        for row in rows
        if row.get("family") in PRIMARY_FAMILIES
        and _boolish(row.get("perturbative_like"))
        and not _boolish(row.get("control_like"))
    ]
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in primary:
        grouped[_key(row)].append(row)

    summaries: list[dict[str, Any]] = []
    for key, group_rows in grouped.items():
        by_n = {
            int(row["N"]): row
            for row in group_rows
            if isinstance(row.get("N"), int) and (n_filter is None or int(row["N"]) in n_filter)
        }
        n_values = sorted(by_n)
        if not n_values:
            continue
        finite_s = [_float_or_nan(row.get("born_similarity")) for row in by_n.values()]
        finite_alpha = [_float_or_nan(row.get("tail_density_exponent")) for row in by_n.values()]
        finite_recip = [_float_or_nan(row.get("reciprocity_error")) for row in by_n.values()]
        finite_atom = [_float_or_nan(row.get("radius_atomic_fraction")) for row in by_n.values()]
        finite_spread = [_float_or_nan(row.get("radius_q99_over_q50")) for row in by_n.values()]
        finite_score = [_float_or_nan(row.get("perturbative_balanced_score")) for row in by_n.values()]
        finite = lambda values: [value for value in values if math.isfinite(value)]
        s_vals = finite(finite_s)
        alpha_vals = finite(finite_alpha)
        recip_vals = finite(finite_recip)
        atom_vals = finite(finite_atom)
        spread_vals = finite(finite_spread)
        score_vals = finite(finite_score)
        target_count = sum(1 for row in by_n.values() if _boolish(row.get("target_like")))
        summary = {field: value for field, value in zip(GROUP_FIELDS, key)}
        summary.update(
            {
                "n_values": ",".join(str(n) for n in n_values),
                "n_count": len(n_values),
                "target_count": target_count,
                "min_S": min(s_vals) if s_vals else math.nan,
                "mean_S": mean(s_vals) if s_vals else math.nan,
                "max_S": max(s_vals) if s_vals else math.nan,
                "median_alpha": median(alpha_vals) if alpha_vals else math.nan,
                "max_reciprocity": max(recip_vals) if recip_vals else math.nan,
                "max_atom": max(atom_vals) if atom_vals else math.nan,
                "min_spread": min(spread_vals) if spread_vals else math.nan,
                "mean_pert_score": mean(score_vals) if score_vals else math.nan,
                "complete_N12_N14": all(n in by_n for n in (12, 13, 14)),
                "S_by_N": ", ".join(f"N{n}:{_fmt(by_n[n].get('born_similarity'), 3)}" for n in n_values),
                "alpha_by_N": ", ".join(f"N{n}:{_fmt(by_n[n].get('tail_density_exponent'), 3)}" for n in n_values),
            }
        )
        complete_bonus = 0.08 if summary["complete_N12_N14"] else 0.0
        target_bonus = 0.04 * target_count / max(1, len(n_values))
        summary["scaling_score"] = (
            0.45 * _float_or_nan(summary["min_S"])
            + 0.20 * math.exp(-abs(_float_or_nan(summary["median_alpha"]) - 2.0) / 0.65)
            + 0.15 * math.exp(-_float_or_nan(summary["max_reciprocity"]))
            + 0.08 * (1.0 - min(1.0, _float_or_nan(summary["max_atom"])))
            + 0.08 * min(1.0, math.log1p(_float_or_nan(summary["min_spread"])) / math.log(40.0))
            + complete_bonus
            + target_bonus
        )
        summaries.append(summary)
    return sorted(
        summaries,
        key=lambda row: _float_or_nan(row.get("scaling_score")),
        reverse=True,
    )


def _has_all_n(group: dict[str, Any], required: set[int]) -> bool:
    values = {
        int(text)
        for text in str(group.get("n_values", "")).split(",")
        if text.strip().isdigit()
    }
    return required <= values


def _scaling_table(groups: list[dict[str, Any]], top: int) -> list[str]:
    lines = [
        "| rank | scaling | Ns | targets | min S | mean S | alpha med | recip max | atom max | q99/q50 min | signature | S by N |",
        "|---:|---:|:---|---:|---:|---:|---:|---:|---:|---:|:---|:---|",
    ]
    for rank, group in enumerate(groups[:top], 1):
        lines.append(
            "| {rank} | {score} | {ns} | {targets}/{n_count} | {min_s} | {mean_s} | {alpha} | {recip} | {atom} | {spread} | {sig} | {s_by_n} |".format(
                rank=rank,
                score=_fmt(group.get("scaling_score"), 4),
                ns=group.get("n_values"),
                targets=group.get("target_count"),
                n_count=group.get("n_count"),
                min_s=_fmt(group.get("min_S"), 4),
                mean_s=_fmt(group.get("mean_S"), 4),
                alpha=_fmt(group.get("median_alpha")),
                recip=_fmt(group.get("max_reciprocity")),
                atom=_fmt(group.get("max_atom")),
                spread=_fmt(group.get("min_spread"), 2),
                sig=_signature(group),
                s_by_n=group.get("S_by_N"),
            )
        )
    return lines


def _family_counts(rows: list[dict[str, Any]]) -> list[str]:
    counts: Counter[tuple[str, int]] = Counter()
    targets: Counter[tuple[str, int]] = Counter()
    for row in rows:
        n_value = row.get("N")
        if not isinstance(n_value, int):
            continue
        key = (str(row.get("family", "")), n_value)
        counts[key] += 1
        if _boolish(row.get("target_like")):
            targets[key] += 1

    lines = ["| family | N | target-like | rows |", "|:---|---:|---:|---:|"]
    for family, n_value in sorted(counts):
        lines.append(f"| {family} | {n_value} | {targets[(family, n_value)]} | {counts[(family, n_value)]} |")
    return lines


def write_markdown(path: Path, rows: list[dict[str, Any]], top: int) -> None:
    scaling = _summarize_primary_scaling(rows)
    scaling_n13_n14 = [
        group
        for group in _summarize_primary_scaling(rows, n_filter={13, 14})
        if _has_all_n(group, {13, 14})
    ]
    lines = [
        "# Zeus Follow-up N-scaling Check",
        "",
        f"Source rows: {len(rows)}",
        "",
        "This report uses imported CSV diagnostics only; it does not re-diagonalize Hamiltonians.",
        "",
        "## Target Counts",
        "",
    ]
    lines.extend(_family_counts(rows))
    lines.extend(
        [
            "",
            "## Perturbative Matched-ring Scaling Groups",
            "",
        ]
    )
    lines.extend(_scaling_table(scaling, top))
    lines.extend(
        [
            "",
            "## N13-N14 Matched-ring Pairs",
            "",
            "This view ignores N=12 when ranking but still requires both N=13 and N=14.",
            "",
        ]
    )
    lines.extend(_scaling_table(scaling_n13_n14, top))
    lines.extend(
        [
            "",
            "## Interpretation Rules",
            "",
            "- Rows are strongest when they appear at all of `N=12,13,14`, retain moderate/high `min S`, keep low atomic mass, and avoid large reciprocity error.",
            "- This is a finite-size screen over the already-computed Zeus diagnostics. Histogram-bin stability still requires a separate rerun if the raw eigenvalue data are unavailable.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-csv",
        type=Path,
        default=Path("figures/zeus_born_followup/summary_rows.csv"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("figures/zeus_born_followup/scaling_summary.md"),
    )
    parser.add_argument("--top", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = _load_rows(args.source_csv)
    if not rows:
        raise SystemExit(f"No rows found in {args.source_csv}")
    write_markdown(args.out_md, rows, args.top)
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
