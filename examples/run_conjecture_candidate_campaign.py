"""Run and synthesize the conjecture-driven Hamiltonian candidate campaign.

The campaign delegates a single physical case at a time to the established
``born_hamiltonian_search.py`` engine.  Case outputs are checkpoints: an
existing, non-empty ``results.csv`` is reused unless ``--force`` is supplied.
This keeps local and PBS runs resumable after every Hamiltonian and every N.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any, Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SEARCH = ROOT / "examples" / "born_hamiltonian_search.py"


@dataclass(frozen=True)
class CandidateCase:
    case_id: str
    priority: int
    local: bool
    zeus: bool
    target: str
    conditions: str
    hypothesis: str
    args: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CandidateCase":
        return cls(
            case_id=str(value["id"]),
            priority=int(value["priority"]),
            local=bool(value["local"]),
            zeus=bool(value["zeus"]),
            target=str(value["target"]),
            conditions=str(value["conditions"]),
            hypothesis=str(value["hypothesis"]),
            args=tuple(str(item) for item in value["args"]),
        )


class CampaignRepository:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.raw = json.loads(config_path.read_text(encoding="utf-8"))

    @property
    def times(self) -> tuple[float, ...]:
        return tuple(float(value) for value in self.raw["default_times"])

    def cases(self, scope: str, requested: set[str]) -> list[CandidateCase]:
        cases = [CandidateCase.from_dict(item) for item in self.raw["cases"]]
        if scope == "local":
            cases = [case for case in cases if case.local]
        elif scope == "zeus":
            cases = [case for case in cases if case.zeus]
        if requested:
            cases = [case for case in cases if case.case_id in requested]
            missing = requested - {case.case_id for case in cases}
            if missing:
                raise ValueError(f"Unknown or out-of-scope cases: {sorted(missing)}")
        return sorted(cases, key=lambda case: case.priority)


class SearchCommandFactory:
    def __init__(self, python: str, n_total: int, times: Iterable[float], workers: int) -> None:
        self.python = python
        self.n_total = n_total
        self.times = tuple(times)
        self.workers = max(1, workers)

    def build(self, case: CandidateCase, output_dir: Path, plot_top: int) -> list[str]:
        return [
            self.python,
            str(SEARCH),
            "--N", str(self.n_total),
            "--times", *(f"{time:g}" for time in self.times),
            *case.args,
            "--backend", "auto",
            "--workers", str(self.workers),
            "--bins", "64",
            "--tail-fraction", "0.15",
            "--log-bins", "40",
            "--top", "4",
            "--plot-top", str(max(0, plot_top)),
            "--plot-max-bloch-points", "6000",
            "--skip-diagnostic-spectra",
            "--out-dir", str(output_dir),
            "--log-file", str(output_dir / "run.log"),
        ]


def _valid_checkpoint(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle)) > 0


def _write_manifest(run_root: Path, payload: dict[str, Any]) -> None:
    (run_root / "campaign_manifest.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def run_cases(
    cases: list[CandidateCase],
    factory: SearchCommandFactory,
    run_root: Path,
    plot_top: int,
    force: bool,
    dry_run: bool,
) -> None:
    run_root.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "N": factory.n_total,
        "times": list(factory.times),
        "python": factory.python,
        "cases": {},
    }
    for index, case in enumerate(cases, 1):
        output_dir = run_root / case.case_id
        output_dir.mkdir(parents=True, exist_ok=True)
        result_path = output_dir / "results.csv"
        command = factory.build(case, output_dir, plot_top)
        print(f"[{index:02d}/{len(cases):02d}] {case.case_id}", flush=True)
        print("  " + subprocess.list2cmdline(command), flush=True)
        if dry_run:
            status = "dry-run"
        elif _valid_checkpoint(result_path) and not force:
            print("  checkpoint found; reusing results.csv", flush=True)
            status = "reused"
        else:
            environment = os.environ.copy()
            environment.setdefault("OMP_NUM_THREADS", "1")
            environment.setdefault("MKL_NUM_THREADS", "1")
            environment.setdefault("OPENBLAS_NUM_THREADS", "1")
            environment.setdefault("NUMEXPR_NUM_THREADS", "1")
            environment.setdefault("MPLBACKEND", "Agg")
            subprocess.run(command, cwd=ROOT, env=environment, check=True)
            if not _valid_checkpoint(result_path):
                raise RuntimeError(f"Missing or empty checkpoint after {case.case_id}: {result_path}")
            status = "completed"
        manifest["cases"][case.case_id] = {
            "status": status,
            "target": case.target,
            "hypothesis": case.hypothesis,
            "command": command,
            "result": str(result_path),
        }
        _write_manifest(run_root, manifest)


def _median(rows: list[dict[str, str]], field: str) -> float:
    values: list[float] = []
    for row in rows:
        try:
            value = float(row[field])
        except (KeyError, TypeError, ValueError):
            continue
        if np.isfinite(value):
            values.append(value)
    return statistics.median(values) if values else float("nan")


def synthesize(cases: list[CandidateCase], run_root: Path, figure_root: Path) -> None:
    aggregate: list[dict[str, str]] = []
    summary: list[dict[str, str | float | int]] = []
    for case in cases:
        result_path = run_root / case.case_id / "results.csv"
        if not _valid_checkpoint(result_path):
            continue
        with result_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            aggregate.append(
                {"case_id": case.case_id, "target": case.target,
                 "conditions": case.conditions, "hypothesis": case.hypothesis, **row}
            )
        summary.append({
            "case_id": case.case_id,
            "target": case.target,
            "n_rows": len(rows),
            "median_born_similarity": _median(rows, "born_similarity"),
            "median_phi_uniformity": _median(rows, "phi_uniformity_score"),
            "median_tail_exponent": _median(rows, "tail_density_exponent"),
            "median_reciprocity_error": _median(rows, "reciprocity_error"),
            "median_q99_over_q50": _median(rows, "radius_q99_over_q50"),
            "median_atomic_fraction": _median(rows, "radius_atomic_fraction"),
            "hypothesis": case.hypothesis,
        })
    if not aggregate:
        raise RuntimeError("No completed results were available to synthesize")

    aggregate_path = run_root / "aggregate_results.csv"
    with aggregate_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(aggregate[0]))
        writer.writeheader()
        writer.writerows(aggregate)
    summary_path = run_root / "case_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    figure_root.mkdir(parents=True, exist_ok=True)
    labels = [str(row["case_id"]).replace("_", "\n") for row in summary]
    x = np.arange(len(summary))
    fig, axes = plt.subplots(2, 3, figsize=(15.5, 8.5), constrained_layout=True)
    panels = [
        ("median_born_similarity", r"median $S_{Born}$", None, False),
        ("median_phi_uniformity", "median phase uniformity", None, False),
        ("median_tail_exponent", "median radius-tail exponent", (2.0, 4.0), False),
        ("median_reciprocity_error", "median reciprocity error", None, False),
        ("median_q99_over_q50", r"median $q_{99}/q_{50}$", None, True),
        ("median_atomic_fraction", "median atomic fraction", None, False),
    ]
    colors = {"Born": "#2563eb", "wrapped-heavy-tail": "#d97706", "hybrid": "#7c3aed",
              "control": "#6b7280", "Born/control": "#0f766e", "control/heavy-tail": "#a16207",
              "wrapped-heavy-tail/control": "#b45309"}
    for ax, (field, title, guides, logarithmic) in zip(axes.flat, panels):
        values = [float(row[field]) for row in summary]
        ax.bar(x, values, color=[colors.get(str(row["target"]), "#64748b") for row in summary])
        ax.set_xticks(x, labels, fontsize=6.5, rotation=35, ha="right")
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.22)
        if logarithmic and all(value > 0 for value in values if np.isfinite(value)):
            ax.set_yscale("log")
        if guides:
            ax.axhline(guides[0], color="#df2b2f", ls="--", lw=1, label=r"$r^{-2}$")
            ax.axhline(guides[1], color="#1677b8", ls=":", lw=1.2, label=r"Born $r^{-4}$")
            ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Expanded perturbative Hamiltonian family comparison", fontsize=15, fontweight="bold")
    figure_path = figure_root / "candidate_campaign_synthesis.png"
    fig.savefig(figure_path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    completed = {str(row["case_id"]): row for row in summary}
    born_rows = [row for row in summary if row["target"] == "Born"]
    heavy_rows = [row for row in summary if row["target"] == "wrapped-heavy-tail"]
    lines = [
        "# Conjecture-driven candidate campaign", "",
        "Each case is tied to a condition and a falsifiable outcome.", "",
        "## Local N=9 findings", "",
    ]
    if born_rows:
        best_born = max(born_rows, key=lambda row: float(row["median_born_similarity"]))
        lines.append(
            f"- Best Born-target median: `{best_born['case_id']}` with "
            f"S_Born={float(best_born['median_born_similarity']):.3f}. This is a screening result, not convergence evidence."
        )
    if heavy_rows:
        closest_heavy = min(heavy_rows, key=lambda row: abs(float(row["median_tail_exponent"]) - 2.0))
        lines.append(
            f"- Strongest inverse-square screening result: `{closest_heavy['case_id']}` with median "
            f"tail exponent {float(closest_heavy['median_tail_exponent']):.3f} and atomic fraction "
            f"{float(closest_heavy['median_atomic_fraction']):.3f}."
        )
    lines.extend([
        "- The dimerized degeneracy control has a steep median exponent and narrow q99/q50, supporting the claim that raw degeneracy without extended non-scalar mixing is insufficient.",
        "- Several reciprocity estimates are unavailable at N=9 because reciprocal logarithmic bins lack enough populated pairs. Zeus size scaling is required before judging B3.",
        "- All local entries use Jx/sqrt(N_pixel) and the four times 1e3, 1e4, 1e5, and 1e6.",
        "",
        "## Case catalog", "",
    ])

    def display(value: float) -> str:
        return f"{value:.3f}" if np.isfinite(value) else "unavailable"

    for case in cases:
        matched = completed.get(case.case_id)
        lines.extend([
            f"### {case.priority}. `{case.case_id}` - {case.target}", "",
            f"- Conditions: {case.conditions}",
            f"- Hypothesis: {case.hypothesis}",
            f"- Local: {'yes' if case.local else 'no'}; Zeus: {'yes' if case.zeus else 'no'}.",
        ])
        if matched:
            lines.append(
                "- Local medians: "
                f"Born={display(float(matched['median_born_similarity']))}, "
                f"phi-uniformity={display(float(matched['median_phi_uniformity']))}, "
                f"tail exponent={display(float(matched['median_tail_exponent']))}, "
                f"reciprocity error={display(float(matched['median_reciprocity_error']))}."
            )
        lines.append("")
    (run_root / "candidate_list_and_local_results.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "conjecture_candidate_campaign_2026-07-16.json")
    parser.add_argument("--N", type=int, default=9, help="Total qubits, including the central qubit.")
    parser.add_argument("--scope", choices=["local", "zeus", "all"], default="local")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--plot-top", type=int, default=1)
    parser.add_argument("--run-root", type=Path, default=ROOT / "work" / "conjecture_candidate_campaign_2026-07-16")
    parser.add_argument("--figure-root", type=Path, default=ROOT / "figures" / "conjecture_candidate_campaign_2026-07-16")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--synthesize-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repository = CampaignRepository(args.config)
    cases = repository.cases(args.scope, set(args.case))
    if not cases:
        raise SystemExit("No cases selected")
    factory = SearchCommandFactory(args.python, args.N, repository.times, args.workers)
    if not args.synthesize_only:
        run_cases(cases, factory, args.run_root, args.plot_top, args.force, args.dry_run)
    if not args.dry_run:
        synthesize(cases, args.run_root, args.figure_root)


if __name__ == "__main__":
    main()
