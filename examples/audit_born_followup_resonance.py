"""
Audit the imported Born follow-up rows against the perturbative resonance story.

This is a CSV-only post-processing step.  It does not diagonalize
Hamiltonians.  Its purpose is to keep the analytical and numerical lanes
honest while Zeus metric-stability and visual diagnostics are pending:

* recompute the local-resonance classifier from row parameters,
* separate primary matched-ring evidence from resonance-adjacent controls,
* isolate the true off-resonance ``hz0=zero`` falsifier set,
* summarize which rows pass only the scalar CSV gate.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from summarize_born_search_results import local_resonance_distance, local_resonance_label


NUMERIC_FIELDS = {
    "N",
    "t",
    "J",
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
    "tail_density_exponent",
    "reciprocity_error",
    "radius_q99_over_q50",
    "radius_atomic_fraction",
    "perturbative_balanced_score",
    "local_resonance_distance",
    "shortlist_group_score",
    "min_S",
    "mean_S",
    "max_S",
    "median_alpha",
    "max_reciprocity",
    "max_atom",
    "min_spread",
}


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


def _boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


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


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            row: dict[str, Any] = dict(raw)
            for field in NUMERIC_FIELDS:
                if field in row:
                    row[field] = _float_or_nan(row[field])
            if math.isfinite(_float_or_nan(row.get("N"))):
                row["N"] = int(_float_or_nan(row["N"]))
            rows.append(row)
    return rows


def csv_gate_pass(row: dict[str, Any]) -> bool:
    """Scalar screen only; stability and visual diagnostics are still required."""

    similarity = _float_or_nan(row.get("born_similarity"))
    alpha = _float_or_nan(row.get("tail_density_exponent"))
    recip = _float_or_nan(row.get("reciprocity_error"))
    atom = _float_or_nan(row.get("radius_atomic_fraction"))
    spread = _float_or_nan(row.get("radius_q99_over_q50"))
    return (
        math.isfinite(similarity)
        and similarity >= 0.55
        and math.isfinite(alpha)
        and 1.7 <= alpha <= 3.0
        and math.isfinite(recip)
        and recip <= 1.0
        and math.isfinite(atom)
        and atom < 0.05
        and math.isfinite(spread)
        and spread > 7.0
    )


def csv_gate_strong(row: dict[str, Any]) -> bool:
    return csv_gate_pass(row) and _float_or_nan(row.get("born_similarity")) >= 0.60 and _float_or_nan(
        row.get("reciprocity_error")
    ) <= 0.80


def classify_row(row: dict[str, Any]) -> str:
    family = str(row.get("family", ""))
    model = str(row.get("model", ""))
    connectivity = str(row.get("connectivity", ""))
    hz0_mode = str(row.get("hz0_mode", ""))
    label = str(row.get("local_resonance_label", ""))

    if not _boolish(row.get("perturbative_like")):
        return "outside_perturbative_scope"
    if model == "cnot_copier" or "cnot" in family:
        return "cnot_copier_negative_control"
    if "sz_exchange" in family or "sz_conserving" in family:
        return "conserved_sz_negative_control"
    if connectivity == "chain":
        return "chain_negative_control"
    if model == "single_pixel" and connectivity == "ring" and hz0_mode == "matched" and label in {"exact", "near"}:
        return "primary_matched_ring_evidence"
    if _boolish(row.get("control_like")) and label in {"exact", "near"}:
        return "resonance_adjacent_control"
    if _boolish(row.get("control_like")) and hz0_mode == "zero" and label == "off":
        return "off_resonance_zero_falsifier"
    return "other_perturbative_row"


def _signature(row: dict[str, Any]) -> str:
    return (
        f"{row.get('model')} {row.get('connectivity')} hz0={row.get('hz0_mode')} "
        f"J={_fmt_g(row.get('J'))} Jx={_fmt_g(row.get('Jx_unscaled'))} Jy={_fmt_g(row.get('Jy_unscaled'))} "
        f"hz={_fmt_g(row.get('hz'))} Jpm={_fmt_g(row.get('Jpm'))} "
        f"Jxx={_fmt_g(row.get('Jxx'))} Jyy={_fmt_g(row.get('Jyy'))} Jz={_fmt_g(row.get('Jz'))} "
        f"Jzx={_fmt_g(row.get('Jzx'))} Jcpm={_fmt_g(row.get('Jcpm_unscaled'))} hx={_fmt_g(row.get('hx'))} "
        f"t={_fmt_g(row.get('t'))}"
    )


def resonance_check(rows: list[dict[str, Any]], tolerance: float = 1.0e-9) -> dict[str, Any]:
    checked = 0
    max_abs_error = 0.0
    mismatches: list[dict[str, Any]] = []
    for row in rows:
        if str(row.get("model", "")) != "single_pixel" or str(row.get("connectivity", "")) != "ring":
            continue
        expected = local_resonance_distance(row)
        recorded = _float_or_nan(row.get("local_resonance_distance"))
        if not math.isfinite(expected) or not math.isfinite(recorded):
            continue
        checked += 1
        error = abs(expected - recorded)
        max_abs_error = max(max_abs_error, error)
        expected_label = local_resonance_label(row)
        recorded_label = str(row.get("local_resonance_label"))
        if error > tolerance or expected_label != recorded_label:
            mismatches.append(
                {
                    "family": row.get("family"),
                    "N": row.get("N"),
                    "recorded_distance": recorded,
                    "expected_distance": expected,
                    "recorded_label": recorded_label,
                    "expected_label": expected_label,
                    "signature": _signature(row),
                }
            )
    return {
        "checked_ring_rows": checked,
        "max_abs_error": max_abs_error,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:20],
    }


def bucket_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[classify_row(row)].append(row)

    summaries: list[dict[str, Any]] = []
    for bucket, bucket_rows in buckets.items():
        best_s = max((_float_or_nan(row.get("born_similarity")) for row in bucket_rows), default=math.nan)
        best_score = max((_float_or_nan(row.get("perturbative_balanced_score")) for row in bucket_rows), default=math.nan)
        finite_recips = [
            _float_or_nan(row.get("reciprocity_error"))
            for row in bucket_rows
            if math.isfinite(_float_or_nan(row.get("reciprocity_error")))
        ]
        summaries.append(
            {
                "bucket": bucket,
                "rows": len(bucket_rows),
                "target_like": sum(1 for row in bucket_rows if _boolish(row.get("target_like"))),
                "csv_gate_pass": sum(1 for row in bucket_rows if csv_gate_pass(row)),
                "csv_gate_strong": sum(1 for row in bucket_rows if csv_gate_strong(row)),
                "best_S": best_s,
                "best_score": best_score,
                "best_reciprocity": min(finite_recips) if finite_recips else math.nan,
            }
        )
    return sorted(summaries, key=lambda row: (row["csv_gate_pass"], row["target_like"], row["rows"]), reverse=True)


def resonance_label_counts(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        family = str(row.get("family", ""))
        if "detuning_control" not in family:
            continue
        counts[str(row.get("hz0_mode", ""))][str(row.get("local_resonance_label", ""))] += 1
    return {mode: dict(counter) for mode, counter in sorted(counts.items())}


def _sort_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            csv_gate_pass(row),
            _float_or_nan(row.get("perturbative_balanced_score")),
            _float_or_nan(row.get("born_similarity")),
        ),
        reverse=True,
    )[:limit]


def _load_optional(path: Path) -> list[dict[str, Any]]:
    return load_rows(path) if path.exists() else []


def _json_safe(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _primary_table(rows: list[dict[str, Any]], top: int) -> list[str]:
    lines = [
        "| rank | min S | alpha med | recip max | atom max | q99/q50 min | signature | S by N |",
        "|---:|---:|---:|---:|---:|---:|:---|:---|",
    ]
    for rank, row in enumerate(rows[:top], 1):
        signature = (
            f"{row.get('connectivity')} hz0={row.get('hz0_mode')} "
            f"Jx={_fmt_g(row.get('Jx_unscaled'))} hz={_fmt_g(row.get('hz'))} "
            f"Jpm={_fmt_g(row.get('Jpm'))} t={_fmt_g(row.get('t'))}"
        )
        lines.append(
            "| {rank} | {min_s} | {alpha} | {recip} | {atom} | {spread} | {sig} | {s_by_n} |".format(
                rank=rank,
                min_s=_fmt(row.get("min_S"), 4),
                alpha=_fmt(row.get("median_alpha")),
                recip=_fmt(row.get("max_reciprocity")),
                atom=_fmt(row.get("max_atom")),
                spread=_fmt(row.get("min_spread"), 2),
                sig=signature,
                s_by_n=row.get("S_by_N", ""),
            )
        )
    return lines


def _falsifier_table(rows: list[dict[str, Any]], top: int) -> list[str]:
    lines = [
        "| rank | csv gate | N | S | alpha | recip | atom | q99/q50 | d_res | signature |",
        "|---:|:---:|---:|---:|---:|---:|---:|---:|---:|:---|",
    ]
    for rank, row in enumerate(_sort_rows(rows, top), 1):
        lines.append(
            "| {rank} | {gate} | {N} | {S} | {alpha} | {recip} | {atom} | {spread} | {dres} | {sig} |".format(
                rank=rank,
                gate="yes" if csv_gate_pass(row) else "no",
                N=row.get("N"),
                S=_fmt(row.get("born_similarity"), 4),
                alpha=_fmt(row.get("tail_density_exponent")),
                recip=_fmt(row.get("reciprocity_error")),
                atom=_fmt(row.get("radius_atomic_fraction")),
                spread=_fmt(row.get("radius_q99_over_q50"), 2),
                dres=_fmt(row.get("local_resonance_distance")),
                sig=_signature(row),
            )
        )
    return lines


def write_markdown(
    path: Path,
    rows: list[dict[str, Any]],
    primary_groups: list[dict[str, Any]],
    off_controls: list[dict[str, Any]],
    top: int,
) -> dict[str, Any]:
    check = resonance_check(rows)
    buckets = bucket_summary(rows)
    label_counts = resonance_label_counts(rows)
    off_csv_pass = [row for row in off_controls if csv_gate_pass(row)]
    primary_csv_pass = [
        row for row in rows if classify_row(row) == "primary_matched_ring_evidence" and csv_gate_pass(row)
    ]
    lines = [
        "# Perturbative Resonance Audit",
        "",
        f"Source rows: {len(rows)}",
        "",
        "This report uses imported CSV diagnostics only. It does not replace the N13/N14 metric-stability reruns or visual histogram diagnostics.",
        "",
        "## Classifier Check",
        "",
        "The audit recomputes `d_res = min |hz0 + s(hz + J r)|` for `s=+-1` and `r in {-2,0,2}` on single-pixel ring rows.",
        "",
        f"- Checked ring rows: {check['checked_ring_rows']}",
        f"- Maximum absolute distance mismatch: {_fmt(check['max_abs_error'], 3)}",
        f"- Label/distance mismatches: {check['mismatch_count']}",
        "",
        "## Decision Buckets",
        "",
        "| bucket | rows | target-like | CSV gate | strong CSV gate | best S | best score | best recip |",
        "|:---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for bucket in buckets:
        lines.append(
            "| {bucket} | {rows} | {target} | {gate} | {strong} | {best_s} | {best_score} | {best_recip} |".format(
                bucket=bucket["bucket"],
                rows=bucket["rows"],
                target=bucket["target_like"],
                gate=bucket["csv_gate_pass"],
                strong=bucket["csv_gate_strong"],
                best_s=_fmt(bucket["best_S"], 4),
                best_score=_fmt(bucket["best_score"], 4),
                best_recip=_fmt(bucket["best_reciprocity"]),
            )
        )
    lines.extend(
        [
            "",
            "CSV gate here means `S>=0.55`, `1.7<=alpha<=3.0`, reciprocity `<=1.0`, atom `<0.05`, and `q99/q50>7`.",
            "Strong CSV gate additionally requires `S>=0.60` and reciprocity `<=0.80`.",
            "",
            "## Detuned-control Resonance Labels",
            "",
            "| hz0 mode | exact | near | off |",
            "|:---|---:|---:|---:|",
        ]
    )
    for mode, counts in label_counts.items():
        lines.append(f"| {mode} | {counts.get('exact', 0)} | {counts.get('near', 0)} | {counts.get('off', 0)} |")
    lines.extend(
        [
            "",
            "## Top Primary Matched N13/N14 Groups",
            "",
        ]
    )
    lines.extend(_primary_table(primary_groups, top))
    lines.extend(
        [
            "",
            "## True Off-resonance Zero Falsifiers",
            "",
            "These rows are mechanism-threatening only if the later stability and visual diagnostics look as clean as the matched-ring rows.",
            "",
        ]
    )
    lines.extend(_falsifier_table(off_controls, top))
    lines.extend(
        [
            "",
            "## Current Interpretation",
            "",
            f"- Primary matched-ring CSV-gate rows: {len(primary_csv_pass)}.",
            f"- Off-resonance zero falsifier CSV-gate rows: {len(off_csv_pass)}.",
            "- CSV evidence still favors the matched-ring mechanism, but the off-resonance falsifier set is not empty.",
            "- The next decisive step remains Zeus metric-stability plus visual diagnostics for both sets.",
            "",
            "Run on Zeus:",
            "",
            "```bash",
            'cd "$HOME/research/collapse"',
            "bash hpc/submit_zeus_born_postprocess.sh",
            "```",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "source_rows": len(rows),
        "resonance_check": check,
        "bucket_summary": buckets,
        "detuned_resonance_label_counts": label_counts,
        "primary_csv_gate_rows": len(primary_csv_pass),
        "off_resonance_zero_csv_gate_rows": len(off_csv_pass),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("figures/zeus_born_followup"))
    parser.add_argument("--summary-csv", type=Path)
    parser.add_argument("--primary-csv", type=Path)
    parser.add_argument("--off-controls-csv", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--top", type=int, default=8)
    args = parser.parse_args()

    summary_csv = args.summary_csv or args.root / "summary_rows.csv"
    primary_csv = args.primary_csv or args.root / "shortlist_primary_n13_n14.csv"
    off_controls_csv = args.off_controls_csv or args.root / "shortlist_off_resonance_controls.csv"
    out_md = args.out_md or args.root / "resonance_audit.md"
    out_json = args.out_json or args.root / "resonance_audit.json"

    rows = load_rows(summary_csv)
    primary_groups = _load_optional(primary_csv)
    off_controls = _load_optional(off_controls_csv)
    summary = write_markdown(out_md, rows, primary_groups, off_controls, args.top)
    out_json.write_text(
        json.dumps(_json_safe(summary), allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    check = summary["resonance_check"]
    print(f"Status: checked {check['checked_ring_rows']} ring rows, mismatches={check['mismatch_count']}")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")
    return 1 if check["mismatch_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
