"""
Evaluate postprocessed Born-rule gate outputs.

This script reads the postprocess outputs produced by
``hpc/zeus_born_postprocess_stability.pbs`` and
``hpc/zeus_born_postprocess_diagnostics.pbs``.  It is intentionally
conservative: scalar metrics can decide whether a candidate is ready for
visual review, but they do not by themselves complete the scientific goal.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GateWorkflow:
    name: str
    label: str
    primary_stability: str
    control_stability: str
    primary_diagnostics: str
    control_diagnostics: str
    required_n_values: tuple[int, ...]


GATE_WORKFLOWS = [
    GateWorkflow(
        name="n15_n16",
        label="N15/N16 anisotropic larger-N",
        primary_stability="metric_stability_primary_N15_N16",
        control_stability="metric_stability_controls_N15_N16",
        primary_diagnostics="diagnostics_primary_N15_N16",
        control_diagnostics="diagnostics_controls_N15_N16",
        required_n_values=(15, 16),
    ),
    GateWorkflow(
        name="n13_n14",
        label="N13/N14 follow-up",
        primary_stability="metric_stability_primary_N13_N14",
        control_stability="metric_stability_off_resonance_controls_N12_N13",
        primary_diagnostics="diagnostics_primary_N13_N14",
        control_diagnostics="diagnostics_off_resonance_controls",
        required_n_values=(13, 14),
    ),
]


@dataclass
class GateThresholds:
    primary_min_s: float = 0.55
    primary_strong_min_s: float = 0.60
    max_range_s: float = 0.25
    strong_range_s: float = 0.15
    alpha_min: float = 1.7
    alpha_max: float = 3.0
    atom_max: float = 0.05
    atom_warning: float = 0.10
    q99_q50_min: float = 7.0
    q99_q50_strong: float = 10.0
    reciprocity_max: float = 1.0
    reciprocity_preferred: float = 0.8
    control_challenge_min_s: float = 0.60
    control_challenge_reciprocity: float = 1.0


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


def _load_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def _count_diagnostic_figures(index_path: Path) -> int:
    if not index_path.exists():
        return 0
    text = index_path.read_text(encoding="utf-8")
    return len(re.findall(r"\]\(([^)]+\.png)\)", text))


def _exists_nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def _workflow_required_paths(root: Path, workflow: GateWorkflow) -> dict[str, Path]:
    primary_stability_dir = root / workflow.primary_stability
    control_stability_dir = root / workflow.control_stability
    primary_diag_dir = root / workflow.primary_diagnostics
    control_diag_dir = root / workflow.control_diagnostics
    return {
        "primary_stability_csv": primary_stability_dir / "stability_summary.csv",
        "primary_stability_log": primary_stability_dir / "run.log",
        "control_stability_csv": control_stability_dir / "stability_summary.csv",
        "control_stability_log": control_stability_dir / "run.log",
        "primary_diagnostics_index": primary_diag_dir / "index.md",
        "primary_diagnostics_log": primary_diag_dir / "run.log",
        "control_diagnostics_index": control_diag_dir / "index.md",
        "control_diagnostics_log": control_diag_dir / "run.log",
    }


def _select_workflow(root: Path, requested: str = "auto") -> GateWorkflow:
    if requested != "auto":
        for workflow in GATE_WORKFLOWS:
            if workflow.name == requested:
                return workflow
        raise ValueError(f"Unknown workflow: {requested!r}")

    scored = []
    for workflow in GATE_WORKFLOWS:
        paths = _workflow_required_paths(root, workflow)
        present = sum(1 for path in paths.values() if _exists_nonempty(path))
        dirs = [
            root / workflow.primary_stability,
            root / workflow.control_stability,
            root / workflow.primary_diagnostics,
            root / workflow.control_diagnostics,
        ]
        existing_dirs = sum(1 for path in dirs if path.exists())
        scored.append((present, existing_dirs, workflow))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    best_present, best_dirs, best_workflow = scored[0]
    if best_present == 0 and best_dirs == 0:
        return next(workflow for workflow in GATE_WORKFLOWS if workflow.name == "n13_n14")
    return best_workflow


def _metric_values(row: dict[str, Any]) -> dict[str, float]:
    return {
        "min_s": _float_or_nan(row.get("min_born_similarity")),
        "mean_s": _float_or_nan(row.get("mean_born_similarity")),
        "range_s": _float_or_nan(row.get("range_born_similarity")),
        "alpha": _float_or_nan(row.get("median_tail_density_exponent")),
        "reciprocity": _float_or_nan(row.get("median_reciprocity_error")),
        "spread": _float_or_nan(row.get("max_radius_q99_over_q50")),
        "atom": _float_or_nan(row.get("min_radius_atomic_fraction")),
        "n": _float_or_nan(row.get("N")),
    }


def _row_signature(row: dict[str, Any]) -> str:
    fields = [
        "model",
        "connectivity",
        "central_coupling",
        "hz0_mode",
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
        "t",
    ]
    return "|".join(str(row.get(field, "")).strip() for field in fields)


def _display_signature(row: dict[str, Any]) -> str:
    return (
        f"{row.get('family', '')} N={row.get('N', '')} "
        f"{row.get('connectivity', '')} hz0={row.get('hz0_mode', '')} "
        f"J={row.get('J', '')} Jx={row.get('Jx_unscaled', '')} Jy={row.get('Jy_unscaled', '')} "
        f"hz={row.get('hz', '')} Jpm={row.get('Jpm', '')} "
        f"Jxx={row.get('Jxx', '')} Jyy={row.get('Jyy', '')} "
        f"Jz={row.get('Jz', '')} Jzx={row.get('Jzx', '')} "
        f"Jcpm={row.get('Jcpm_unscaled', '')} hx={row.get('hx', '')} t={row.get('t', '')}"
    )


def _passes_primary_row(row: dict[str, Any], thresholds: GateThresholds) -> tuple[bool, list[str]]:
    values = _metric_values(row)
    reasons: list[str] = []
    checks = [
        ("min_s", values["min_s"] >= thresholds.primary_min_s, f"min S {_fmt(values['min_s'])}"),
        ("range_s", values["range_s"] <= thresholds.max_range_s, f"range S {_fmt(values['range_s'])}"),
        (
            "alpha",
            thresholds.alpha_min <= values["alpha"] <= thresholds.alpha_max,
            f"alpha {_fmt(values['alpha'])}",
        ),
        ("atom", values["atom"] < thresholds.atom_max, f"atom {_fmt(values['atom'])}"),
        ("spread", values["spread"] > thresholds.q99_q50_min, f"q99/q50 {_fmt(values['spread'])}"),
        (
            "reciprocity",
            values["reciprocity"] <= thresholds.reciprocity_max,
            f"recip {_fmt(values['reciprocity'])}",
        ),
    ]
    passed = True
    for _name, ok, reason in checks:
        reasons.append(("PASS " if ok else "FAIL ") + reason)
        passed = passed and ok
    return passed, reasons


def _challenges_with_control(row: dict[str, Any], thresholds: GateThresholds) -> tuple[bool, list[str]]:
    values = _metric_values(row)
    checks = [
        values["min_s"] >= thresholds.control_challenge_min_s,
        values["range_s"] <= thresholds.max_range_s,
        thresholds.alpha_min <= values["alpha"] <= thresholds.alpha_max,
        values["atom"] < thresholds.atom_max,
        values["spread"] > thresholds.q99_q50_min,
        values["reciprocity"] <= thresholds.control_challenge_reciprocity,
    ]
    reasons = [
        f"min S {_fmt(values['min_s'])}",
        f"range S {_fmt(values['range_s'])}",
        f"alpha {_fmt(values['alpha'])}",
        f"atom {_fmt(values['atom'])}",
        f"q99/q50 {_fmt(values['spread'])}",
        f"recip {_fmt(values['reciprocity'])}",
    ]
    return all(checks), reasons


def _paired_primary_passes(
    rows: list[dict[str, Any]],
    thresholds: GateThresholds,
    required_n_values: tuple[int, ...],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    passing_rows: list[dict[str, Any]] = []
    row_reports: list[dict[str, Any]] = []
    by_signature: dict[str, set[int]] = defaultdict(set)
    display_by_signature: dict[str, str] = {}

    for row in rows:
        passed, reasons = _passes_primary_row(row, thresholds)
        values = _metric_values(row)
        n_value = int(values["n"]) if math.isfinite(values["n"]) else -1
        sig = _row_signature(row)
        display_by_signature[sig] = _display_signature(row)
        if passed:
            passing_rows.append(row)
            by_signature[sig].add(n_value)
        row_reports.append(
            {
                "signature": _display_signature(row),
                "passed": passed,
                "reasons": reasons,
            }
        )

    paired = []
    required = set(required_n_values)
    for sig, ns in by_signature.items():
        if required.issubset(ns):
            paired.append({"signature_key": sig, "signature": display_by_signature[sig], "n_values": sorted(ns)})
    return paired, row_reports


def evaluate_gate(
    root: Path,
    scheduler_log_roots: list[Path],
    thresholds: GateThresholds,
    workflow_name: str = "auto",
) -> dict[str, Any]:
    workflow = _select_workflow(root, workflow_name)
    required = _workflow_required_paths(root, workflow)
    files = {
        name: {"path": str(path), "exists_nonempty": _exists_nonempty(path)}
        for name, path in required.items()
    }
    missing = [name for name, info in files.items() if not info["exists_nonempty"]]

    scheduler_logs = []
    for log_root in scheduler_log_roots:
        scheduler_logs.extend(str(path) for path in sorted(log_root.glob("*.log")) if path.is_file())

    primary_rows = _load_csv(required["primary_stability_csv"])
    control_rows = _load_csv(required["control_stability_csv"])
    paired_passes, primary_row_reports = _paired_primary_passes(
        primary_rows,
        thresholds,
        workflow.required_n_values,
    )

    control_challenges = []
    control_row_reports = []
    for row in control_rows:
        challenge, reasons = _challenges_with_control(row, thresholds)
        report = {"signature": _display_signature(row), "challenges": challenge, "reasons": reasons}
        control_row_reports.append(report)
        if challenge:
            control_challenges.append(report)

    primary_figures = _count_diagnostic_figures(required["primary_diagnostics_index"])
    control_figures = _count_diagnostic_figures(required["control_diagnostics_index"])

    if missing:
        status = "pending_outputs"
    elif not paired_passes:
        status = "primary_scalar_gate_failed"
    elif control_challenges:
        status = "off_resonance_falsifier_challenge"
    elif primary_figures == 0 or control_figures == 0:
        status = "pending_visual_figures"
    else:
        status = "ready_for_visual_review"

    return {
        "status": status,
        "root": str(root),
        "workflow": asdict(workflow),
        "thresholds": asdict(thresholds),
        "files": files,
        "missing": missing,
        "scheduler_logs": scheduler_logs,
        "primary_rows": len(primary_rows),
        "control_rows": len(control_rows),
        "primary_paired_passes": paired_passes,
        "primary_row_reports": primary_row_reports,
        "control_challenges": control_challenges,
        "control_row_reports": control_row_reports,
        "diagnostics": {
            "primary_figures": primary_figures,
            "control_figures": control_figures,
        },
        "completion_note": (
            "CSV gates are not enough to complete the goal; visual diagnostics "
            "must still be inspected for smooth Born-ratio and reciprocal-core behavior."
        ),
    }


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# Born Postprocess Gate Status",
        "",
        f"Root: `{result['root']}`",
        f"Workflow: `{result['workflow']['label']}`",
        f"Status: `{result['status']}`",
        "",
        "## Required Files",
        "",
        "| item | present | path |",
        "|:---|:---:|:---|",
    ]
    for name, info in result["files"].items():
        present = "yes" if info["exists_nonempty"] else "no"
        lines.append(f"| {name} | {present} | `{info['path']}` |")

    lines.extend(["", "## Primary Scalar Gate", ""])
    required_ns = "/".join(str(value) for value in result["workflow"]["required_n_values"])
    if result["primary_paired_passes"]:
        lines.extend([f"Paired N{required_ns} primary passes:", ""])
        for item in result["primary_paired_passes"]:
            ns = ",".join(str(value) for value in item["n_values"])
            lines.append(f"- `{item['signature']}` with N={ns}")
    else:
        lines.append(f"No same-parameter N{required_ns} pair currently passes the scalar gate.")

    lines.extend(["", "Top primary row checks:", ""])
    for report in result["primary_row_reports"][:8]:
        flag = "PASS" if report["passed"] else "FAIL"
        lines.append(f"- {flag}: `{report['signature']}`; " + "; ".join(report["reasons"]))

    lines.extend(["", "## Off-Resonance Falsifier Gate", ""])
    if result["control_challenges"]:
        lines.append("Off-resonance rows challenge the local-resonance mechanism:")
        for report in result["control_challenges"][:8]:
            lines.append(f"- `{report['signature']}`; " + "; ".join(report["reasons"]))
    elif result["control_rows"]:
        lines.append("No off-resonance row currently passes the scalar falsifier-challenge gate.")
    else:
        lines.append("No off-resonance stability rows found yet.")

    lines.extend(
        [
            "",
            "## Diagnostics",
            "",
            f"- Primary diagnostic figures: {result['diagnostics']['primary_figures']}",
            f"- Off-resonance diagnostic figures: {result['diagnostics']['control_figures']}",
            "",
            "## Scheduler Logs",
            "",
        ]
    )
    if result["scheduler_logs"]:
        for log in result["scheduler_logs"]:
            lines.append(f"- `{log}`")
    else:
        lines.append("- No scheduler logs were found under the supplied log roots.")

    lines.extend(["", "## Completion Note", "", result["completion_note"], ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate postprocessed Born-rule gate outputs.")
    parser.add_argument("--root", type=Path, default=Path("figures/zeus_born_followup"))
    parser.add_argument(
        "--workflow",
        choices=["auto"] + [workflow.name for workflow in GATE_WORKFLOWS],
        default="auto",
        help="Postprocess workflow to evaluate. Default auto-detects from root.",
    )
    parser.add_argument(
        "--scheduler-log-root",
        type=Path,
        action="append",
        default=[],
        help="Optional scheduler log root. May be passed multiple times.",
    )
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
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
    result = evaluate_gate(args.root, args.scheduler_log_root, thresholds, workflow_name=args.workflow)
    out_md = args.out_md or (args.root / "postprocess_gate_status.md")
    out_json = args.out_json or (args.root / "postprocess_gate_status.json")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(out_md, result)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Status: {result['status']}")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")


if __name__ == "__main__":
    main()
