"""
Compare matched primary candidates against detuned falsifier controls.

The postprocess gate can report ``off_resonance_falsifier_challenge`` when
detuned controls pass the same scalar thresholds as primary matched candidates.
This script turns that status into a concrete audit:

* which controls pass the falsifier-challenge gate,
* whether an exact same-parameter matched primary row exists,
* how the control metrics compare with the exact or nearest primary row,
* which matched counterparts are missing from the current grid.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from evaluate_born_postprocess_gate import (  # noqa: E402
    GateThresholds,
    _challenges_with_control,
    _fmt,
    _load_csv,
    _metric_values,
    _passes_primary_row,
    _select_workflow,
    _workflow_required_paths,
)


EXACT_MATCH_FIELDS = [
    "model",
    "N",
    "connectivity",
    "central_coupling",
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
    "Jpm",
    "Jxx",
    "Jyy",
    "Jz",
    "Jzx",
    "Jcpm_unscaled",
    "hx",
    "hz",
    "t",
]

DISTANCE_FIELDS = [
    "J",
    "Jx_unscaled",
    "Jy_unscaled",
    "Jpm",
    "Jxx",
    "Jyy",
    "Jz",
    "Jzx",
    "Jcpm_unscaled",
    "hx",
    "hz",
    "disorder_strength",
    "disorder_strength_J",
    "disorder_strength_Jpm",
    "disorder_strength_Jx",
    "disorder_strength_Jz",
    "disorder_strength_Jzx",
    "disorder_strength_Jcpm",
    "disorder_strength_hx",
    "disorder_strength_hz",
]


def _float_or_nan(value: Any) -> float:
    text = "" if value is None else str(value).strip()
    if not text:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


def _norm_text(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    number = _float_or_nan(text)
    if math.isfinite(number):
        return f"{number:.12g}"
    return text


def _exact_key(row: dict[str, Any]) -> tuple[str, ...]:
    values = []
    for field in EXACT_MATCH_FIELDS:
        value = row.get(field)
        if field == "central_coupling" and (value is None or str(value).strip() == ""):
            value = "auto"
        if field == "disorder" and (value is None or str(value).strip() == ""):
            value = "none"
        if field == "seed" and (value is None or str(value).strip() == ""):
            value = 44
        if field.startswith("disorder_strength") and (value is None or str(value).strip() == ""):
            value = 0.0
        values.append(_norm_text(value))
    return tuple(values)


def _display_signature(row: dict[str, Any]) -> str:
    return (
        f"{row.get('family', '')} N={row.get('N', '')} {row.get('connectivity', '')} "
        f"cc={row.get('central_coupling', 'auto')} "
        f"hz0={row.get('hz0_mode', '')} dis={row.get('disorder', 'none') or 'none'} "
        f"J={row.get('J', '')} "
        f"Jx={row.get('Jx_unscaled', '')} Jy={row.get('Jy_unscaled', '')} "
        f"hz={row.get('hz', '')} Jpm={row.get('Jpm', '')} "
        f"Jxx={row.get('Jxx', '')} Jyy={row.get('Jyy', '')} "
        f"Jz={row.get('Jz', '')} Jzx={row.get('Jzx', '')} "
        f"Jcpm={row.get('Jcpm_unscaled', '')} hx={row.get('hx', '')} "
        f"t={row.get('t', '')}"
    )


def _parameter_distance(control: dict[str, Any], primary: dict[str, Any]) -> float:
    if control.get("model") != primary.get("model"):
        return math.inf
    if _norm_text(control.get("N")) != _norm_text(primary.get("N")):
        return math.inf
    if control.get("connectivity") != primary.get("connectivity"):
        return math.inf
    control_cc = str(control.get("central_coupling") or "auto")
    primary_cc = str(primary.get("central_coupling") or "auto")
    if control_cc != primary_cc:
        return math.inf
    control_disorder = str(control.get("disorder") or "none")
    primary_disorder = str(primary.get("disorder") or "none")
    if control_disorder != primary_disorder:
        return math.inf
    if _norm_text(control.get("seed") or 44) != _norm_text(primary.get("seed") or 44):
        return math.inf

    distance = 0.0
    for field in DISTANCE_FIELDS:
        a = _float_or_nan(control.get(field))
        b = _float_or_nan(primary.get(field))
        if not math.isfinite(a) or not math.isfinite(b):
            continue
        distance += abs(a - b) / (abs(a) + abs(b) + 1.0e-12)

    ta = _float_or_nan(control.get("t"))
    tb = _float_or_nan(primary.get("t"))
    if math.isfinite(ta) and math.isfinite(tb) and ta > 0.0 and tb > 0.0:
        distance += 0.5 * abs(math.log(ta / tb))
    return distance


def _best_primary_match(
    control: dict[str, Any],
    exact_by_key: dict[tuple[str, ...], list[dict[str, Any]]],
    primary_rows: list[dict[str, Any]],
) -> tuple[str, dict[str, Any] | None, float]:
    exact = exact_by_key.get(_exact_key(control), [])
    if exact:
        best = max(exact, key=lambda row: _metric_values(row)["min_s"])
        return "exact", best, 0.0

    nearest: dict[str, Any] | None = None
    nearest_distance = math.inf
    for row in primary_rows:
        distance = _parameter_distance(control, row)
        if distance < nearest_distance:
            nearest = row
            nearest_distance = distance
    if nearest is None or not math.isfinite(nearest_distance):
        return "none", None, math.inf
    return "nearest", nearest, nearest_distance


def _challenge_score(values: dict[str, float]) -> float:
    min_s = values["min_s"] if math.isfinite(values["min_s"]) else 0.0
    range_s = values["range_s"] if math.isfinite(values["range_s"]) else 1.0
    reciprocity = values["reciprocity"] if math.isfinite(values["reciprocity"]) else 10.0
    spread = values["spread"] if math.isfinite(values["spread"]) and values["spread"] > 0 else 0.0
    spread_score = min(1.0, math.log1p(spread) / math.log(40.0)) if spread else 0.0
    return min_s + 0.25 * math.exp(-reciprocity) + 0.05 * spread_score - 0.10 * range_s


def audit_challenges(
    root: Path,
    workflow_name: str,
    thresholds: GateThresholds,
    extra_primary_csvs: list[Path] | None = None,
) -> dict[str, Any]:
    workflow = _select_workflow(root, workflow_name)
    required = _workflow_required_paths(root, workflow)
    primary_rows = _load_csv(required["primary_stability_csv"])
    for csv_path in extra_primary_csvs or []:
        primary_rows.extend(_load_csv(csv_path))
    control_rows = _load_csv(required["control_stability_csv"])

    primary_passes = []
    exact_by_key: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in primary_rows:
        passed, _reasons = _passes_primary_row(row, thresholds)
        if passed:
            primary_passes.append(row)
        exact_by_key.setdefault(_exact_key(row), []).append(row)

    challenge_rows = []
    for row in control_rows:
        challenge, _reasons = _challenges_with_control(row, thresholds)
        if challenge:
            challenge_rows.append(row)

    comparisons = []
    for control in challenge_rows:
        match_kind, primary, distance = _best_primary_match(control, exact_by_key, primary_rows)
        control_values = _metric_values(control)
        primary_values = _metric_values(primary) if primary is not None else {}
        comparison = {
            "challenge_score": _challenge_score(control_values),
            "match_kind": match_kind,
            "match_distance": distance,
            "control_signature": _display_signature(control),
            "primary_signature": _display_signature(primary) if primary is not None else "",
            "control_family": control.get("family", ""),
            "control_hz0_mode": control.get("hz0_mode", ""),
            "model": control.get("model", ""),
            "connectivity": control.get("connectivity", ""),
            "N": control.get("N", ""),
            "t": control.get("t", ""),
            "J": control.get("J", ""),
            "Jx_unscaled": control.get("Jx_unscaled", ""),
            "Jy_unscaled": control.get("Jy_unscaled", ""),
            "Jpm": control.get("Jpm", ""),
            "Jxx": control.get("Jxx", ""),
            "Jyy": control.get("Jyy", ""),
            "Jz": control.get("Jz", ""),
            "Jzx": control.get("Jzx", ""),
            "Jcpm_unscaled": control.get("Jcpm_unscaled", ""),
            "hx": control.get("hx", ""),
            "hz": control.get("hz", ""),
            "control_min_s": control_values["min_s"],
            "primary_min_s": primary_values.get("min_s", math.nan),
            "delta_min_s_control_minus_primary": control_values["min_s"] - primary_values.get("min_s", math.nan),
            "control_range_s": control_values["range_s"],
            "primary_range_s": primary_values.get("range_s", math.nan),
            "control_alpha": control_values["alpha"],
            "primary_alpha": primary_values.get("alpha", math.nan),
            "control_reciprocity": control_values["reciprocity"],
            "primary_reciprocity": primary_values.get("reciprocity", math.nan),
            "delta_recip_control_minus_primary": control_values["reciprocity"]
            - primary_values.get("reciprocity", math.nan),
            "control_q99_q50": control_values["spread"],
            "primary_q99_q50": primary_values.get("spread", math.nan),
            "control_atom": control_values["atom"],
            "primary_atom": primary_values.get("atom", math.nan),
        }
        comparisons.append(comparison)

    comparisons.sort(
        key=lambda row: (
            row["match_kind"] != "exact",
            -row["challenge_score"],
            -_float_or_nan(row["control_min_s"]),
        )
    )
    missing_matched = [row for row in comparisons if row["match_kind"] != "exact"]
    request_rows = [_matched_counterpart_request(row) for row in missing_matched]

    return {
        "root": str(root),
        "workflow": {
            "name": workflow.name,
            "label": workflow.label,
            "required_n_values": list(workflow.required_n_values),
        },
        "extra_primary_csvs": [str(path) for path in extra_primary_csvs or []],
        "thresholds": {
            "primary_min_s": thresholds.primary_min_s,
            "max_range_s": thresholds.max_range_s,
            "alpha_min": thresholds.alpha_min,
            "alpha_max": thresholds.alpha_max,
            "atom_max": thresholds.atom_max,
            "q99_q50_min": thresholds.q99_q50_min,
            "reciprocity_max": thresholds.reciprocity_max,
        },
        "counts": {
            "primary_rows": len(primary_rows),
            "primary_pass_rows": len(primary_passes),
            "control_rows": len(control_rows),
            "control_challenge_rows": len(challenge_rows),
            "challenge_rows_with_exact_matched_counterpart": len(comparisons) - len(missing_matched),
            "challenge_rows_missing_exact_matched_counterpart": len(missing_matched),
        },
        "comparisons": comparisons,
        "missing_matched_counterparts": missing_matched,
        "matched_counterpart_requests": request_rows,
    }


def _matched_counterpart_request(row: dict[str, Any]) -> dict[str, Any]:
    """Convert a control challenge into an exact matched-row run request."""

    return {
        "family": "matched_counterpart_for_detuned_controls_N15_N16",
        "model": row["model"] or "single_pixel",
        "N": row["N"],
        "t": row["t"],
        "connectivity": row["connectivity"] or "ring",
        "central_coupling": row.get("central_coupling", "auto") or "auto",
        "seed": row.get("seed", 44) or 44,
        "disorder": row.get("disorder", "none") or "none",
        "disorder_strength": row.get("disorder_strength", 0.0) or 0.0,
        "disorder_strength_J": row.get("disorder_strength_J", 0.0) or 0.0,
        "disorder_strength_Jpm": row.get("disorder_strength_Jpm", 0.0) or 0.0,
        "disorder_strength_Jx": row.get("disorder_strength_Jx", 0.0) or 0.0,
        "disorder_strength_Jz": row.get("disorder_strength_Jz", 0.0) or 0.0,
        "disorder_strength_Jzx": row.get("disorder_strength_Jzx", 0.0) or 0.0,
        "disorder_strength_Jcpm": row.get("disorder_strength_Jcpm", 0.0) or 0.0,
        "disorder_strength_hx": row.get("disorder_strength_hx", 0.0) or 0.0,
        "disorder_strength_hz": row.get("disorder_strength_hz", 0.0) or 0.0,
        "hz0_mode": "matched",
        "control_hz0_mode": row["control_hz0_mode"],
        "J": row["J"],
        "Jx_unscaled": row["Jx_unscaled"],
        "Jy_unscaled": row["Jy_unscaled"],
        "Jpm": row["Jpm"],
        "Jxx": row["Jxx"],
        "Jyy": row["Jyy"],
        "Jz": row["Jz"],
        "Jzx": row["Jzx"],
        "Jcpm_unscaled": row["Jcpm_unscaled"],
        "hx": row["hx"],
        "hz": row["hz"],
        "source_control_min_s": row["control_min_s"],
        "source_control_reciprocity": row["control_reciprocity"],
        "source_challenge_score": row["challenge_score"],
        "source_control_signature": row["control_signature"],
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(_json_safe(rows))


def write_markdown(path: Path, result: dict[str, Any], top: int) -> None:
    counts = result["counts"]
    lines = [
        "# Born Falsifier Challenge Audit",
        "",
        f"Root: `{result['root']}`",
        f"Workflow: `{result['workflow']['label']}`",
        f"Extra primary CSVs: {len(result.get('extra_primary_csvs', []))}",
        "",
        "## Summary",
        "",
        f"- Primary stability rows: {counts['primary_rows']}",
        f"- Primary rows passing scalar gate: {counts['primary_pass_rows']}",
        f"- Control stability rows: {counts['control_rows']}",
        f"- Control rows challenging scalar gate: {counts['control_challenge_rows']}",
        (
            "- Challenge rows with exact matched counterpart: "
            f"{counts['challenge_rows_with_exact_matched_counterpart']}"
        ),
        (
            "- Challenge rows missing exact matched counterpart: "
            f"{counts['challenge_rows_missing_exact_matched_counterpart']}"
        ),
        "",
        "Interpretation:",
        "",
    ]
    if counts["control_challenge_rows"] == 0:
        lines.append("- No scalar falsifier challenge remains under the current thresholds.")
    else:
        lines.append(
            "- Scalar falsifier challenges remain. Rows with exact matched counterparts are the cleanest "
            "matched-vs-detuned comparisons; rows without exact counterparts should be queued as matched "
            "counterpart runs before drawing strong conclusions."
        )

    lines.extend(
        [
            "",
            "## Top Control Challenges",
            "",
            "| rank | match | score | control min S | primary min S | dS | control recip | primary recip | control signature | primary signature |",
            "|---:|:---|---:|---:|---:|---:|---:|---:|:---|:---|",
        ]
    )
    for rank, row in enumerate(result["comparisons"][:top], 1):
        lines.append(
            "| {rank} | {match} | {score} | {cs} | {ps} | {ds} | {cr} | {pr} | `{control}` | `{primary}` |".format(
                rank=rank,
                match=row["match_kind"],
                score=_fmt(row["challenge_score"], 4),
                cs=_fmt(row["control_min_s"], 4),
                ps=_fmt(row["primary_min_s"], 4),
                ds=_fmt(row["delta_min_s_control_minus_primary"], 4),
                cr=_fmt(row["control_reciprocity"], 3),
                pr=_fmt(row["primary_reciprocity"], 3),
                control=row["control_signature"],
                primary=row["primary_signature"] or "(missing exact/nearest)",
            )
        )

    lines.extend(
        [
            "",
            "## Missing Exact Matched Counterparts",
            "",
        ]
    )
    missing = result["missing_matched_counterparts"]
    if not missing:
        lines.append("Every control challenge has an exact matched-row counterpart in the current stability table.")
    else:
        lines.extend(
            [
                "These controls pass the falsifier gate but do not have an exact same-parameter `hz0=matched` row in the stability table.",
                "They should be converted into matched counterpart runs before being interpreted as decisive falsifiers.",
                "",
                "| rank | N | t | hz0 | Jx | hz | Jpm | Jxx | Jyy | Jz | Jcpm | hx | control min S | recip |",
                "|---:|---:|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for rank, row in enumerate(missing[:top], 1):
            lines.append(
                "| {rank} | {N} | {t} | {hz0} | {Jx} | {hz} | {Jpm} | {Jxx} | {Jyy} | {Jz} | {Jcpm} | {hx} | {S} | {recip} |".format(
                    rank=rank,
                    N=row["N"],
                    t=row["t"],
                    hz0=row["control_hz0_mode"],
                    Jx=row["Jx_unscaled"],
                    hz=row["hz"],
                    Jpm=row["Jpm"],
                    Jxx=row["Jxx"],
                    Jyy=row["Jyy"],
                    Jz=row["Jz"],
                    Jcpm=row["Jcpm_unscaled"],
                    hx=row["hx"],
                    S=_fmt(row["control_min_s"], 4),
                    recip=_fmt(row["control_reciprocity"], 3),
                )
            )

    lines.extend(
        [
            "",
            "## Next Use",
            "",
            "- Analytics: decide whether exact-matched control wins are dressed resonances of `M(t)` or true falsifiers.",
            "- Numerics: queue missing exact `hz0=matched` counterparts for the strongest control challenges.",
            "- Publication: report these rows as a live falsifier challenge, not as failure or success by themselves.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare primary rows against detuned falsifier challenges.")
    parser.add_argument("--root", type=Path, default=Path("figures/zeus_born_anisotropic_largerN"))
    parser.add_argument("--workflow", choices=["auto", "n15_n16", "n13_n14"], default="auto")
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--out-csv", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-missing-csv", type=Path, default=None)
    parser.add_argument("--out-requests-csv", type=Path, default=None)
    parser.add_argument(
        "--extra-primary-csv",
        type=Path,
        action="append",
        default=[],
        help="Additional stability_summary.csv files to treat as primary matched rows.",
    )
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--primary-min-s", type=float, default=0.55)
    parser.add_argument("--primary-strong-min-s", type=float, default=0.60)
    parser.add_argument("--max-range-s", type=float, default=0.25)
    parser.add_argument("--alpha-min", type=float, default=1.7)
    parser.add_argument("--alpha-max", type=float, default=3.0)
    parser.add_argument("--atom-max", type=float, default=0.05)
    parser.add_argument("--q99-q50-min", type=float, default=7.0)
    parser.add_argument("--reciprocity-max", type=float, default=1.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    thresholds = GateThresholds(
        primary_min_s=args.primary_min_s,
        primary_strong_min_s=args.primary_strong_min_s,
        max_range_s=args.max_range_s,
        alpha_min=args.alpha_min,
        alpha_max=args.alpha_max,
        atom_max=args.atom_max,
        q99_q50_min=args.q99_q50_min,
        reciprocity_max=args.reciprocity_max,
        control_challenge_min_s=args.primary_strong_min_s,
        control_challenge_reciprocity=args.reciprocity_max,
    )
    result = audit_challenges(
        args.root,
        args.workflow,
        thresholds,
        extra_primary_csvs=args.extra_primary_csv,
    )
    out_md = args.out_md or (args.root / "falsifier_challenge_audit.md")
    out_csv = args.out_csv or (args.root / "falsifier_challenge_audit.csv")
    out_json = args.out_json or (args.root / "falsifier_challenge_audit.json")
    out_missing = args.out_missing_csv or (args.root / "missing_matched_counterparts.csv")
    out_requests = args.out_requests_csv or (args.root / "matched_counterpart_requests.csv")

    write_markdown(out_md, result, args.top)
    write_csv(out_csv, result["comparisons"])
    write_csv(out_missing, result["missing_matched_counterparts"])
    write_csv(out_requests, result["matched_counterpart_requests"])
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(_json_safe(result), indent=2, sort_keys=True), encoding="utf-8")

    print(f"Control challenges: {result['counts']['control_challenge_rows']}")
    print(f"Missing exact matched counterparts: {result['counts']['challenge_rows_missing_exact_matched_counterpart']}")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_missing}")
    print(f"Wrote {out_requests}")
    print(f"Wrote {out_json}")


if __name__ == "__main__":
    main()
