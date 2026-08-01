"""Verify the resonance--mixing--reciprocity conjecture and export successes."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collapse.joint_hamiltonian_conjecture import (  # noqa: E402
    HamiltonianPoint,
    JointProfileClassifier,
    confusion,
)


INPUT = ROOT / "reports" / "anisotropic_parameter_study_2026-07-21" / "data" / "spectrum_metrics.csv"
OUTPUT = ROOT / "reports" / "detector_gap_matrix_study_2026-07-21"


def read_points(path: Path) -> list[HamiltonianPoint]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [HamiltonianPoint.from_csv_row(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def point_row(point: HamiltonianPoint, classifier: JointProfileClassifier) -> dict[str, object]:
    return {
        "detector_n": point.detector_n,
        "hz": point.hz,
        "J": point.j,
        "Jpm": point.jpm,
        "family": classifier.family(point),
        "resonance_corridor": classifier.corridor(point),
        "S_born": point.born_score,
        "born_rmse": point.born_rmse,
        "angular_coverage": point.coverage,
        "theta_power_law_alpha": point.alpha,
        "theta_power_law_js": point.power_law_js,
        "theta_power_law_log10_span": point.power_law_span,
        "source_npz": point.source_npz,
    }


def plot_verification(
    points: list[HamiltonianPoint],
    successes: list[HamiltonianPoint],
    classifier: JointProfileClassifier,
    path: Path,
) -> None:
    ns = sorted({point.detector_n for point in points})
    heavy_counts = [sum(point.detector_n == n and classifier.is_heavy(point) for point in points) for n in ns]
    born_counts = [sum(point.detector_n == n and classifier.is_born_like(point) for point in points) for n in ns]
    joint_counts = [sum(point.detector_n == n and classifier.is_joint(point) for point in points) for n in ns]

    figure, axes = plt.subplots(1, 3, figsize=(14.5, 4.5))
    x = np.arange(len(ns))
    axes[0].plot(x, heavy_counts, "o-", color="#355C7D", label="resolved heavy")
    axes[0].plot(x, born_counts, "o-", color="#C06C84", label="Born-like")
    axes[0].plot(x, joint_counts, "o-", color="#2A9D55", linewidth=2.5, label="joint")
    axes[0].set_xticks(x, [str(n) if n <= 14 else f"{n}*" for n in ns])
    axes[0].set_xlabel("detector size N")
    axes[0].set_ylabel("number of configurations")
    axes[0].set_title("Finite-size emergence")
    axes[0].legend(frameon=False)
    axes[0].text(
        0.98,
        0.02,
        "* partial transfer",
        transform=axes[0].transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#555555",
    )

    n14 = [point for point in successes if point.detector_n == 14]
    corridor_colors = {
        "zero field": "#2A9D55",
        "|hz|=J": "#E9C46A",
        "|hz|=2J": "#E76F51",
        "|hz|=Jpm": "#457B9D",
        "|hz|=2Jpm": "#7B2CBF",
        "off corridor": "#555555",
    }
    for label in corridor_colors:
        subset = [point for point in n14 if classifier.corridor(point) == label]
        if subset:
            axes[1].scatter(
                [point.j for point in subset],
                [point.jpm for point in subset],
                s=45,
                alpha=0.85,
                color=corridor_colors[label],
                label=label,
            )
    axes[1].set_xlabel("J")
    axes[1].set_ylabel(r"$J_{\pm}$")
    axes[1].set_title("N=14 validated joint collection")
    axes[1].legend(frameon=False, fontsize=8)

    family_counts = Counter(classifier.family(point) for point in successes)
    labels = ["mixed ZZ+exchange", "pure exchange", "pure ZZ", "uncoupled detector"]
    values = [family_counts.get(label, 0) for label in labels]
    axes[2].barh(labels, values, color=["#2A9D55", "#457B9D", "#E76F51", "#999999"])
    axes[2].set_xlabel("joint successes across delivered sizes")
    axes[2].set_title("Verification by Hamiltonian family")
    for index, value in enumerate(values):
        axes[2].text(value + 0.8, index, str(value), va="center")
    axes[2].set_xlim(0, max(values) * 1.18)

    figure.suptitle("Resonance--mixing--reciprocity conjecture: verification on 3,722 spectra", fontsize=14)
    figure.tight_layout(rect=(0, 0, 1, 0.93))
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=220)
    plt.close(figure)


def main() -> None:
    classifier = JointProfileClassifier()
    points = read_points(INPUT)
    successes = [point for point in points if classifier.is_joint(point)]

    grouped: dict[tuple[float, float, float], list[HamiltonianPoint]] = defaultdict(list)
    for point in successes:
        grouped[point.parameter_key].append(point)
    robust_groups = [group for group in grouped.values() if len(group) >= 2]
    robust_groups.sort(key=lambda group: (-len(group), group[0].hz, group[0].j, group[0].jpm))

    success_rows = [point_row(point, classifier) for point in sorted(successes, key=lambda p: (p.detector_n, p.hz, p.j, p.jpm))]
    robust_rows: list[dict[str, object]] = []
    for group in robust_groups:
        ordered = sorted(group, key=lambda point: point.detector_n)
        robust_rows.append(
            {
                "hz": ordered[0].hz,
                "J": ordered[0].j,
                "Jpm": ordered[0].jpm,
                "family": classifier.family(ordered[0]),
                "resonance_corridor": classifier.corridor(ordered[0]),
                "successful_N": ";".join(str(point.detector_n) for point in ordered),
                "success_count": len(ordered),
                "minimum_S_born": min(point.born_score for point in ordered),
                "maximum_born_rmse": max(point.born_rmse for point in ordered),
                "maximum_alpha": max(point.alpha for point in ordered),
                "maximum_power_law_js": max(point.power_law_js for point in ordered),
                "minimum_coverage": min(point.coverage for point in ordered),
            }
        )

    considered = [point for point in points if point.detector_n >= 12]
    screen = confusion(
        [classifier.microscopic_candidate(point) for point in considered],
        [classifier.is_joint(point) for point in considered],
    )
    by_n: dict[int, dict[str, int]] = {}
    for n in sorted({point.detector_n for point in points}):
        rows = [point for point in points if point.detector_n == n]
        by_n[n] = {
            "available": len(rows),
            "heavy": sum(classifier.is_heavy(point) for point in rows),
            "born_like": sum(classifier.is_born_like(point) for point in rows),
            "joint": sum(classifier.is_joint(point) for point in rows),
        }

    n13 = {point.parameter_key for point in successes if point.detector_n == 13}
    n14 = {point.parameter_key for point in successes if point.detector_n == 14}
    retained = len(n13 & n14)
    cross_size = {
        "N13_joint": len(n13),
        "N14_joint": len(n14),
        "N13_to_N14_retained": retained,
        "N13_to_N14_precision": retained / len(n13) if n13 else 0.0,
        "N13_to_N14_recall": retained / len(n14) if n14 else 0.0,
    }

    data_root = OUTPUT / "data"
    figure_root = OUTPUT / "figures"
    write_csv(data_root / "validated_joint_hamiltonians.csv", success_rows)
    write_csv(data_root / "robust_joint_hamiltonians.csv", robust_rows)
    figure_path = figure_root / "joint_conjecture_verification.png"
    plot_verification(points, successes, classifier, figure_path)

    summary = {
        "conjecture": "resonance--mixing--reciprocity (RMR)",
        "tested_spectra": len(points),
        "joint_successes": len(successes),
        "robust_parameter_triples_successful_at_two_or_more_N": len(robust_rows),
        "gates": classifier.gates.__dict__,
        "by_N": by_n,
        "successes_by_family": dict(Counter(classifier.family(point) for point in successes)),
        "successes_by_corridor": dict(Counter(classifier.corridor(point) for point in successes)),
        "microscopic_candidate_screen_N_ge_12": screen,
        "cross_size_holdout": cross_size,
        "falsified_simplifications": [
            "exact active degeneracy is sufficient",
            "a resonance corridor alone is sufficient",
            "a nonzero exchange term alone is sufficient",
            "a heavy tail alone implies the Born ratio",
        ],
        "interpretation": (
            "RMR is two-stage: resonance plus noncommuting exchange is a high-recall candidate generator; "
            "the decisive condition is reciprocal balance of the folded relative-unitary phase law."
        ),
        "outputs": {
            "all_validated": str((data_root / "validated_joint_hamiltonians.csv").relative_to(ROOT)),
            "robust_collection": str((data_root / "robust_joint_hamiltonians.csv").relative_to(ROOT)),
            "figure": str(figure_path.relative_to(ROOT)),
        },
    }
    (data_root / "joint_conjecture_verification.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
