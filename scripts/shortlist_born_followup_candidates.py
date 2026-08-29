"""
Create a shortlist of Born-rule follow-up candidates and falsifiers.

The input is an enriched ``summary_rows.csv`` file produced by
``summarize_born_search_results.py``.  This script does not diagonalize
Hamiltonians.  It groups the imported Zeus diagnostics into:

* primary perturbative matched-ring candidates that survive at N=13 and N=14,
* full N=12/13/14 matched-ring candidates,
* off-resonance detuned controls that are the cleanest falsifier set.
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
    "local_resonance_distance",
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

PRIMARY_FAMILIES = {
    "primary_matched_ring_N12",
    "primary_matched_ring_N13",
    "primary_matched_ring_N14",
    "primary_matched_ring_long_time_N12_N13",
    "ring_baseline_matched_N15_N16",
    "ring_anisotropic_xx_yy_N15_N16",
    "ring_weak_zz_anisotropic_N15_N16",
    "ring_strong_zz_anisotropic_N15_N16",
    "ring_central_coupling_channels_N15_N16",
}


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


def _load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows: list[dict[str, Any]] = []
        for raw in reader:
            row: dict[str, Any] = dict(raw)
            for field in NUMERIC_FIELDS:
                if field in row:
                    row[field] = _float_or_nan(row[field])
            if math.isfinite(_float_or_nan(row.get("N"))):
                row["N"] = int(row["N"])
            rows.append(row)
    return rows


def _group_key(row: dict[str, Any]) -> tuple[str, ...]:
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
        values.append(_key_value(value))
    return tuple(values)


def _finite(values: list[float]) -> list[float]:
    return [value for value in values if math.isfinite(value)]


def _signature(group: dict[str, Any]) -> str:
    return (
        f"{group['connectivity']} cc={group.get('central_coupling', 'auto')} "
        f"hz0={group['hz0_mode']} dis={group.get('disorder', 'none') or 'none'} "
        f"J={group.get('J', 'nan')} "
        f"Jx={group['Jx_unscaled']} "
        f"Jy={group.get('Jy_unscaled', 'nan')} hz={group['hz']} Jpm={group['Jpm']} "
        f"Jxx={group.get('Jxx', 'nan')} Jyy={group.get('Jyy', 'nan')} "
        f"Jz={group['Jz']} Jzx={group['Jzx']} "
        f"Jcpm={group['Jcpm_unscaled']} t={group['t']}"
    )


def _summarize_group(group_rows: list[dict[str, Any]], key: tuple[str, ...]) -> dict[str, Any]:
    by_n = {int(row["N"]): row for row in group_rows if isinstance(row.get("N"), int)}
    n_values = sorted(by_n)
    s_values = _finite([_float_or_nan(row.get("born_similarity")) for row in by_n.values()])
    alphas = _finite([_float_or_nan(row.get("tail_density_exponent")) for row in by_n.values()])
    recips = _finite([_float_or_nan(row.get("reciprocity_error")) for row in by_n.values()])
    atoms = _finite([_float_or_nan(row.get("radius_atomic_fraction")) for row in by_n.values()])
    spreads = _finite([_float_or_nan(row.get("radius_q99_over_q50")) for row in by_n.values()])
    scores = _finite([_float_or_nan(row.get("perturbative_balanced_score")) for row in by_n.values()])
    summary = {field: value for field, value in zip(GROUP_FIELDS, key)}
    target_count = sum(1 for row in by_n.values() if _boolish(row.get("target_like")))
    summary.update(
        {
            "n_values": ",".join(str(n) for n in n_values),
            "n_count": len(n_values),
            "target_count": target_count,
            "min_S": min(s_values) if s_values else math.nan,
            "mean_S": mean(s_values) if s_values else math.nan,
            "max_S": max(s_values) if s_values else math.nan,
            "median_alpha": median(alphas) if alphas else math.nan,
            "max_reciprocity": max(recips) if recips else math.nan,
            "max_atom": max(atoms) if atoms else math.nan,
            "min_spread": min(spreads) if spreads else math.nan,
            "mean_pert_score": mean(scores) if scores else math.nan,
            "S_by_N": ", ".join(f"N{n}:{_fmt(by_n[n].get('born_similarity'), 3)}" for n in n_values),
            "alpha_by_N": ", ".join(f"N{n}:{_fmt(by_n[n].get('tail_density_exponent'), 3)}" for n in n_values),
            "source_rows": len(group_rows),
        }
    )
    summary["shortlist_score"] = (
        0.42 * _float_or_nan(summary["min_S"])
        + 0.22 * math.exp(-abs(_float_or_nan(summary["median_alpha"]) - 2.0) / 0.65)
        + 0.16 * math.exp(-_float_or_nan(summary["max_reciprocity"]))
        + 0.08 * (1.0 - min(1.0, _float_or_nan(summary["max_atom"])))
        + 0.07 * min(1.0, math.log1p(_float_or_nan(summary["min_spread"])) / math.log(40.0))
        + 0.05 * target_count / max(1, len(n_values))
    )
    return summary


def _primary_groups(rows: list[dict[str, Any]], required_n: set[int]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("family") not in PRIMARY_FAMILIES:
            continue
        if _boolish(row.get("control_like")):
            continue
        if not _boolish(row.get("perturbative_like")):
            continue
        if str(row.get("model")) != "single_pixel":
            continue
        if str(row.get("connectivity")) != "ring":
            continue
        if str(row.get("hz0_mode")) != "matched":
            continue
        if not isinstance(row.get("N"), int) or int(row["N"]) not in required_n:
            continue
        grouped[_group_key(row)].append(row)

    summaries = []
    for key, group_rows in grouped.items():
        present = {int(row["N"]) for row in group_rows if isinstance(row.get("N"), int)}
        if required_n <= present:
            summaries.append(_summarize_group(group_rows, key))
    return sorted(summaries, key=lambda row: _float_or_nan(row["shortlist_score"]), reverse=True)


def _off_resonance_controls(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    controls = [
        row
        for row in rows
        if _boolish(row.get("target_like"))
        and _boolish(row.get("control_like"))
        and str(row.get("local_resonance_label")) == "off"
        and _boolish(row.get("perturbative_like"))
    ]
    return sorted(controls, key=_off_control_sort_key, reverse=True)


def _csv_gate_pass(row: dict[str, Any]) -> bool:
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


def _csv_gate_strong(row: dict[str, Any]) -> bool:
    return _csv_gate_pass(row) and _float_or_nan(row.get("born_similarity")) >= 0.60 and _float_or_nan(
        row.get("reciprocity_error")
    ) <= 0.80


def _off_control_sort_key(row: dict[str, Any]) -> tuple[bool, bool, float, float]:
    return (
        _csv_gate_pass(row),
        _csv_gate_strong(row),
        _float_or_nan(row.get("perturbative_balanced_score")),
        _float_or_nan(row.get("born_similarity")),
    )


def _raw_rows_for_groups(
    rows: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    required_n: set[int],
    kind: str,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for rank, group in enumerate(groups, 1):
        group_key = tuple(group[field] for field in GROUP_FIELDS)
        matches = [
            row
            for row in rows
            if _group_key(row) == group_key
            and isinstance(row.get("N"), int)
            and int(row["N"]) in required_n
        ]
        by_n: dict[int, dict[str, Any]] = {}
        for row in matches:
            n_value = int(row["N"])
            current = by_n.get(n_value)
            if current is None or _float_or_nan(row.get("perturbative_balanced_score")) > _float_or_nan(
                current.get("perturbative_balanced_score")
            ):
                by_n[n_value] = row
        for row in [by_n[n_value] for n_value in sorted(by_n)]:
            enriched = dict(row)
            enriched["shortlist_kind"] = kind
            enriched["shortlist_group_rank"] = rank
            enriched["shortlist_group_score"] = group["shortlist_score"]
            enriched["shortlist_group_n_values"] = group["n_values"]
            enriched["shortlist_group_S_by_N"] = group["S_by_N"]
            output.append(enriched)
    return output


def _ranked_raw_rows(rows: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for rank, row in enumerate(rows, 1):
        enriched = dict(row)
        enriched["shortlist_kind"] = kind
        enriched["shortlist_group_rank"] = rank
        enriched["shortlist_group_score"] = row.get("perturbative_balanced_score", math.nan)
        enriched["shortlist_group_n_values"] = row.get("N", "")
        enriched["shortlist_group_S_by_N"] = f"N{row.get('N')}:{_fmt(row.get('born_similarity'), 3)}"
        output.append(enriched)
    return output


def _negative_control_counts(rows: list[dict[str, Any]]) -> list[str]:
    counts: Counter[tuple[str, int]] = Counter()
    targets: Counter[tuple[str, int]] = Counter()
    for row in rows:
        if not isinstance(row.get("N"), int):
            continue
        family = str(row.get("family", ""))
        if family not in {
            "chain_control_N12_N13",
            "sz_exchange_control_N12_N13",
            "cnot_copier_degenerate_N8_N10_N12",
            "chain_sz_conserving_N13_N14",
            "chain_sz_conserving_N15_N16",
            "chain_transverse_perturbative_N13_N14",
            "chain_transverse_perturbative_N15",
            "all_to_all_sz_conserving_N15_N16",
        }:
            continue
        key = (family, int(row["N"]))
        counts[key] += 1
        if _boolish(row.get("target_like")):
            targets[key] += 1
    lines = ["| family | N | target-like | rows |", "|:---|---:|---:|---:|"]
    for key in sorted(counts):
        lines.append(f"| {key[0]} | {key[1]} | {targets[key]} | {counts[key]} |")
    return lines


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _candidate_table(rows: list[dict[str, Any]], top: int) -> list[str]:
    lines = [
        "| rank | score | Ns | targets | min S | mean S | alpha med | recip max | atom max | q99/q50 min | signature | S by N |",
        "|---:|---:|:---|---:|---:|---:|---:|---:|---:|---:|:---|:---|",
    ]
    for rank, row in enumerate(rows[:top], 1):
        lines.append(
            "| {rank} | {score} | {ns} | {targets}/{n_count} | {min_s} | {mean_s} | {alpha} | {recip} | {atom} | {spread} | {sig} | {s_by_n} |".format(
                rank=rank,
                score=_fmt(row.get("shortlist_score"), 4),
                ns=row.get("n_values"),
                targets=row.get("target_count"),
                n_count=row.get("n_count"),
                min_s=_fmt(row.get("min_S"), 4),
                mean_s=_fmt(row.get("mean_S"), 4),
                alpha=_fmt(row.get("median_alpha")),
                recip=_fmt(row.get("max_reciprocity")),
                atom=_fmt(row.get("max_atom")),
                spread=_fmt(row.get("min_spread"), 2),
                sig=_signature(row),
                s_by_n=row.get("S_by_N"),
            )
        )
    return lines


def _control_table(rows: list[dict[str, Any]], top: int) -> list[str]:
    lines = [
        "| rank | CSV gate | score | family | N | hz0 | d_res | S | alpha | recip | atom | signature |",
        "|---:|:---:|---:|:---|---:|:---|---:|---:|---:|---:|---:|:---|",
    ]
    for rank, row in enumerate(rows[:top], 1):
        signature = (
            f"J={_fmt_g(row.get('J'))} Jx={_fmt_g(row.get('Jx_unscaled'))} "
            f"Jy={_fmt_g(row.get('Jy_unscaled'))} hz={_fmt_g(row.get('hz'))} "
            f"Jpm={_fmt_g(row.get('Jpm'))} Jxx={_fmt_g(row.get('Jxx'))} "
            f"Jyy={_fmt_g(row.get('Jyy'))} Jz={_fmt_g(row.get('Jz'))} "
            f"Jzx={_fmt_g(row.get('Jzx'))} Jcpm={_fmt_g(row.get('Jcpm_unscaled'))} "
            f"t={_fmt_g(row.get('t'))}"
        )
        lines.append(
            "| {rank} | {gate} | {score} | {family} | {N} | {hz0} | {dres} | {S} | {alpha} | {recip} | {atom} | {sig} |".format(
                rank=rank,
                gate="yes" if _csv_gate_pass(row) else "no",
                score=_fmt(row.get("perturbative_balanced_score"), 4),
                family=row.get("family"),
                N=row.get("N"),
                hz0=row.get("hz0_mode"),
                dres=_fmt(row.get("local_resonance_distance")),
                S=_fmt(row.get("born_similarity"), 4),
                alpha=_fmt(row.get("tail_density_exponent")),
                recip=_fmt(row.get("reciprocity_error")),
                atom=_fmt(row.get("radius_atomic_fraction")),
                sig=signature,
            )
        )
    return lines


def write_markdown(
    path: Path,
    primary_pair: list[dict[str, Any]],
    primary_triplet: list[dict[str, Any]],
    off_controls: list[dict[str, Any]],
    all_rows: list[dict[str, Any]],
    top: int,
    pair_label: str,
    triplet_label: str,
) -> None:
    detuned_targets = [
        row
        for row in all_rows
        if row.get("family") in {"detuning_control_ring_N12_N13", "ring_detuned_controls_N15_N16"}
        and _boolish(row.get("target_like"))
    ]
    detuned_labels = Counter(str(row.get("local_resonance_label")) for row in detuned_targets)
    lines = [
        "# Born Follow-up Candidate Shortlist",
        "",
        "This shortlist is computed from imported Zeus summary rows. It does not re-diagonalize Hamiltonians.",
        "",
        f"## Primary {pair_label.upper()} Candidates",
        "",
    ]
    lines.extend(_candidate_table(primary_pair, top))
    lines.extend(
        [
            "",
            f"## Full {triplet_label.upper()} Candidates",
            "",
        ]
    )
    lines.extend(_candidate_table(primary_triplet, top))
    lines.extend(
        [
            "",
            "## Off-resonance Detuned Falsifiers",
            "",
            "These are target-like detuned-control rows with `local_resonance_label=off`; they are the cleanest falsifier set because exact/near local-resonance rows likely belong to the same mechanism.",
            "",
        ]
    )
    lines.extend(_control_table(off_controls, top))
    lines.extend(
        [
            "",
            "## Detuned Target-like Resonance Labels",
            "",
            "| label | count |",
            "|:---|---:|",
        ]
    )
    for label, count in sorted(detuned_labels.items()):
        lines.append(f"| {label} | {count} |")
    lines.extend(
        [
            "",
            "## Negative Control Counts",
            "",
        ]
    )
    lines.extend(_negative_control_counts(all_rows))
    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            f"- Run metric-stability reruns for the primary {pair_label.upper()} shortlist.",
            "- Generate visual angle/radius diagnostics for the top candidates after stability reruns identify robust rows.",
            "- Treat off-resonance detuned rows as the falsifier set; exact/near detuned rows should be reclassified as local-resonance variants.",
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
    parser.add_argument("--out-dir", type=Path, default=Path("figures/zeus_born_followup"))
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--primary-pair-n", type=int, nargs="+", default=[13, 14])
    parser.add_argument("--primary-triplet-n", type=int, nargs="+", default=[12, 13, 14])
    parser.add_argument("--pair-label", default="n13_n14")
    parser.add_argument("--triplet-label", default="n12_n14")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = _load_rows(args.source_csv)
    pair_ns = set(args.primary_pair_n)
    triplet_ns = set(args.primary_triplet_n)
    primary_pair = _primary_groups(rows, pair_ns)
    primary_triplet = _primary_groups(rows, triplet_ns)
    off_controls = _off_resonance_controls(rows)
    primary_pair_rows = _raw_rows_for_groups(
        rows,
        primary_pair,
        pair_ns,
        f"primary_{args.pair_label}",
    )
    primary_triplet_rows = _raw_rows_for_groups(
        rows,
        primary_triplet,
        triplet_ns,
        f"primary_{args.triplet_label}",
    )
    off_control_rows = _ranked_raw_rows(off_controls, "off_resonance_control")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    pair_csv = args.out_dir / f"shortlist_primary_{args.pair_label}.csv"
    triplet_csv = args.out_dir / f"shortlist_primary_{args.triplet_label}.csv"
    pair_rows_csv = args.out_dir / f"shortlist_primary_{args.pair_label}_rows.csv"
    triplet_rows_csv = args.out_dir / f"shortlist_primary_{args.triplet_label}_rows.csv"
    _write_csv(pair_csv, primary_pair)
    _write_csv(triplet_csv, primary_triplet)
    _write_csv(pair_rows_csv, primary_pair_rows)
    _write_csv(triplet_rows_csv, primary_triplet_rows)
    _write_csv(args.out_dir / "shortlist_off_resonance_controls.csv", off_control_rows)
    write_markdown(
        args.out_dir / "shortlist.md",
        primary_pair,
        primary_triplet,
        off_controls,
        rows,
        args.top,
        args.pair_label,
        args.triplet_label,
    )
    print(f"Wrote {args.out_dir / 'shortlist.md'}")
    print(f"Wrote {pair_csv}")
    print(f"Wrote {triplet_csv}")
    print(f"Wrote {pair_rows_csv}")
    print(f"Wrote {triplet_rows_csv}")
    print(f"Wrote {args.out_dir / 'shortlist_off_resonance_controls.csv'}")


if __name__ == "__main__":
    main()
