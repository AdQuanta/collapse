"""Analyze a designed multi-factor Hamiltonian sweep against the conjecture gates."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import statistics
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def _float(row: dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError):
        return float("nan")


def _median(values: Iterable[float]) -> float:
    finite = [value for value in values if math.isfinite(value)]
    return statistics.median(finite) if finite else float("nan")


def score_row(row: dict[str, str]) -> dict[str, float]:
    born = max(0.0, _float(row, "born_similarity"))
    phi = min(1.0, max(0.0, _float(row, "phi_uniformity_score")))
    exponent = _float(row, "tail_density_exponent")
    tail = math.exp(-abs(exponent - 2.0) / 0.8) if math.isfinite(exponent) else 0.0
    spread = _float(row, "radius_q99_over_q50")
    spread_score = min(1.0, math.log1p(max(0.0, spread)) / math.log(101.0)) if math.isfinite(spread) else 0.0
    atom = _float(row, "radius_atomic_fraction")
    continuity = 1.0 - min(1.0, max(0.0, atom)) if math.isfinite(atom) else 0.0
    reciprocity = _float(row, "reciprocity_error")
    reciprocity_score = math.exp(-reciprocity) if math.isfinite(reciprocity) else 0.15
    heavy_score = tail * (0.5 + 0.5 * spread_score) * continuity
    born_gate_score = born * phi * reciprocity_score
    joint_score = math.sqrt(max(0.0, heavy_score * born_gate_score))
    return {
        "heavy_score": heavy_score,
        "born_gate_score": born_gate_score,
        "joint_score": joint_score,
    }


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row.update({key: f"{value:.12g}" for key, value in score_row(row).items()})
    return rows


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str | float | int]]:
    cases = sorted({row["case_id"] for row in rows})
    summary: list[dict[str, str | float | int]] = []
    for case_id in cases:
        group = [row for row in rows if row["case_id"] == case_id]
        best = max(group, key=lambda row: _float(row, "joint_score"))
        summary.append({
            "case_id": case_id,
            "target": group[0]["target"],
            "n_rows": len(group),
            "median_born_similarity": _median(_float(row, "born_similarity") for row in group),
            "max_born_similarity": max(_float(row, "born_similarity") for row in group),
            "median_phi_uniformity": _median(_float(row, "phi_uniformity_score") for row in group),
            "median_tail_exponent": _median(_float(row, "tail_density_exponent") for row in group),
            "median_reciprocity_error": _median(_float(row, "reciprocity_error") for row in group),
            "median_q99_over_q50": _median(_float(row, "radius_q99_over_q50") for row in group),
            "median_atomic_fraction": _median(_float(row, "radius_atomic_fraction") for row in group),
            "best_joint_score": _float(best, "joint_score"),
            "best_joint_time": _float(best, "t"),
            "best_joint_born": _float(best, "born_similarity"),
            "best_joint_exponent": _float(best, "tail_density_exponent"),
            "best_joint_phi": _float(best, "phi_uniformity_score"),
            "best_joint_reciprocity": _float(best, "reciprocity_error"),
            "conditions": group[0]["conditions"],
            "hypothesis": group[0]["hypothesis"],
        })
    return sorted(summary, key=lambda row: float(row["best_joint_score"]), reverse=True)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_tradeoffs(rows: list[dict[str, str]], summary: list[dict[str, object]], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    blue = "#1677b8"
    red = "#df2b2f"
    purple = "#6a3d7a"
    fig, axes = plt.subplots(2, 3, figsize=(15.5, 8.5), constrained_layout=True)
    born = np.array([_float(row, "born_similarity") for row in rows])
    exponent = np.array([_float(row, "tail_density_exponent") for row in rows])
    phi = np.array([_float(row, "phi_uniformity_score") for row in rows])
    joint = np.array([_float(row, "joint_score") for row in rows])
    sizes = 20 + 100 * np.clip(joint, 0, 1)
    scatter = axes[0, 0].scatter(
        exponent, born, c=phi, s=sizes, cmap="viridis", alpha=0.82,
        edgecolor="white", linewidth=0.35,
    )
    axes[0, 0].axvline(2, color=red, ls="--", lw=1.1, label=r"$r^{-2}$")
    axes[0, 0].axvline(4, color=blue, ls=":", lw=1.2, label=r"Born $r^{-4}$")
    axes[0, 0].set(xlabel="radius-tail exponent", ylabel="Born similarity", title="Heavy-tail and Born gates")
    axes[0, 0].legend(frameon=False, fontsize=8)
    fig.colorbar(scatter, ax=axes[0, 0], label="phase uniformity")

    reciprocal_rows = [row for row in rows if math.isfinite(_float(row, "reciprocity_error"))]
    axes[0, 1].scatter(
        [_float(row, "reciprocity_error") for row in reciprocal_rows],
        [_float(row, "born_similarity") for row in reciprocal_rows],
        color=blue, alpha=0.78, edgecolor="white", linewidth=0.35,
    )
    axes[0, 1].set(xlabel="reciprocity error (lower is better)", ylabel="Born similarity", title="B3 remains the strict gate")

    top = summary[:10][::-1]
    axes[0, 2].barh(
        [str(row["case_id"]).replace("_", " ") for row in top],
        [float(row["best_joint_score"]) for row in top],
        color=purple,
    )
    axes[0, 2].set(xlabel="joint finite-size screening score", title="Top joint screens")
    axes[0, 2].grid(axis="x", alpha=0.22)

    born_top = sorted(summary, key=lambda row: float(row["max_born_similarity"]))[-10:]
    axes[1, 0].barh(
        [str(row["case_id"]).replace("_", " ") for row in born_top],
        [float(row["max_born_similarity"]) for row in born_top],
        color=blue,
    )
    axes[1, 0].set(xlabel=r"maximum $S_{Born}$", title="Born-profile screen")

    tail_top = sorted(
        summary,
        key=lambda row: abs(float(row["median_tail_exponent"]) - 2.0)
        if math.isfinite(float(row["median_tail_exponent"])) else math.inf,
        reverse=True,
    )[-10:]
    axes[1, 1].barh(
        [str(row["case_id"]).replace("_", " ") for row in tail_top],
        [float(row["median_tail_exponent"]) for row in tail_top],
        color=red,
    )
    axes[1, 1].axvline(2.0, color="black", ls="--", lw=1.0, label=r"$r^{-2}$")
    axes[1, 1].axvline(4.0, color="black", ls=":", lw=1.0, label=r"Born $r^{-4}$")
    axes[1, 1].set(xlabel="median tail exponent", title="Closest inverse-square screens")
    axes[1, 1].legend(frameon=False, fontsize=8)

    targets = sorted({row["target"] for row in rows})
    x = np.arange(len(targets))
    med_born_gate = [_median(_float(row, "born_gate_score") for row in rows if row["target"] == target) for target in targets]
    med_heavy = [_median(_float(row, "heavy_score") for row in rows if row["target"] == target) for target in targets]
    width = 0.36
    axes[1, 2].bar(x - width / 2, med_born_gate, width, label="Born gate", color=blue)
    axes[1, 2].bar(x + width / 2, med_heavy, width, label="heavy-tail gate", color=red)
    axes[1, 2].set_xticks(
        x,
        [target.replace("wrapped-heavy-tail", "heavy") for target in targets],
        rotation=20,
        ha="right",
    )
    axes[1, 2].set_ylabel("median gate score")
    axes[1, 2].set_title("Designed families retain distinct roles")
    axes[1, 2].legend(frameon=False, fontsize=8)

    for ax in axes.flat:
        ax.grid(alpha=0.18)
    fig.suptitle("Expanded perturbative Hamiltonian screen", fontsize=15, fontweight="bold")
    fig.savefig(destination, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _display(value: object) -> str:
    number = float(value)
    return f"{number:.3f}" if math.isfinite(number) else "unavailable"


def write_report(path: Path, rows: list[dict[str, str]], summary: list[dict[str, object]]) -> None:
    top_born = max(rows, key=lambda row: _float(row, "born_similarity"))
    top_heavy = max(rows, key=lambda row: _float(row, "heavy_score"))
    top_joint = max(rows, key=lambda row: _float(row, "joint_score"))
    lines = [
        "# Expanded perturbative Hamiltonian sweep", "",
        "## Scope", "",
        f"- {len(summary)} locally completed Hamiltonians, {len(rows)} spectra, total N={rows[0]['N']}.",
        "- Times: 100, 316, 1000, 10000.",
        "- Every central coupling is an unscaled input no larger than 0.01 and is divided by sqrt(N_pixel) in the Hamiltonian.",
        "- Dimensions varied: Jpm, XX/YY anisotropy, independent X/Y central coupling, hx, Jz, Jzx, hz0 matching, weak hz/Jpm disorder, and graph geometry.",
        "", "## Main findings", "",
        f"- Highest Born similarity: `{top_born['case_id']}` at t={_display(top_born['t'])}, S_Born={_display(top_born['born_similarity'])}, exponent={_display(top_born['tail_density_exponent'])}, phi-uniformity={_display(top_born['phi_uniformity_score'])}.",
        f"- Strongest heavy-tail screen: `{top_heavy['case_id']}` at t={_display(top_heavy['t'])}, exponent={_display(top_heavy['tail_density_exponent'])}, q99/q50={_display(top_heavy['radius_q99_over_q50'])}, atomic fraction={_display(top_heavy['radius_atomic_fraction'])}.",
        f"- Best joint finite-size screen: `{top_joint['case_id']}` at t={_display(top_joint['t'])}, joint score={_display(top_joint['joint_score'])}, S_Born={_display(top_joint['born_similarity'])}, exponent={_display(top_joint['tail_density_exponent'])}, reciprocity={_display(top_joint['reciprocity_error'])}.",
        "- A joint score is only a screening statistic. Exact Born requires q(1/r)=r^4 q(r) and an asymptotic r^-4 tail; a persistent filled-pole r^-2 coefficient is incompatible with exact Born.",
        "", "## Conjecture interpretation", "",
        "- Matched cases test B1 directly; added Y, anisotropy, hx, Jz, and Jzx test whether B2 mixing improves without destroying the matched manifold.",
        "- Detuned and chain-end controls test whether apparent improvement survives loss of B1 or HT3 graph extension.",
        "- Jpm edge/center cases test HT1-HT5 and whether added mixing can reduce azimuthal locking.",
        "- Zeus scaling must decide B3: reciprocity residual, phase moments, and far-tail crossover should improve with N before any Born claim is accepted.",
        "", "## Ranked case summaries", "",
        "| rank | case | target | best joint | best Born | exponent | phi U | reciprocity | t |", "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(summary, 1):
        lines.append(
            f"| {rank} | `{row['case_id']}` | {row['target']} | {_display(row['best_joint_score'])} | "
            f"{_display(row['best_joint_born'])} | {_display(row['best_joint_exponent'])} | "
            f"{_display(row['best_joint_phi'])} | {_display(row['best_joint_reciprocity'])} | {_display(row['best_joint_time'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path, required=True)
    args = parser.parse_args()
    rows = load_rows(args.aggregate)
    summary = summarize(rows)
    write_csv(args.output_dir / "ranked_results.csv", rows)
    write_csv(args.output_dir / "expanded_case_summary.csv", summary)
    plot_tradeoffs(rows, summary, args.figure_dir / "expanded_sweep_tradeoffs.png")
    write_report(args.output_dir / "expanded_sweep_findings.md", rows, summary)


if __name__ == "__main__":
    main()
