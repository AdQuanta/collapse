"""Test a small-N finite-time-kernel condition for the RMR reciprocity term."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.anisotropic_sweep import AngularDiagnosticCalculator, AnisotropicSample  # noqa: E402
from core.joint_hamiltonian_conjecture import (  # noqa: E402
    FiniteTimeKernelBalance,
    HamiltonianPoint,
    JointProfileClassifier,
    confusion,
)


INPUT = ROOT / "reports" / "anisotropic_parameter_study_2026-07-21" / "data" / "spectrum_metrics.csv"
OUTPUT = ROOT / "reports" / "detector_gap_matrix_study_2026-07-21" / "data"


def main() -> None:
    classifier = JointProfileClassifier()
    kernel = FiniteTimeKernelBalance(probe_n=6)
    diagnostic = AngularDiagnosticCalculator(24)
    with INPUT.open(newline="", encoding="utf-8") as handle:
        points = [HamiltonianPoint.from_csv_row(row) for row in csv.DictReader(handle)]
    selected = [point for point in points if point.detector_n in (13, 14)]
    by_parameter = {point.parameter_key: point for point in selected}
    kappa_cache = {key: kernel.kernel_eigenvalues(point) for key, point in by_parameter.items()}

    rows: list[dict[str, object]] = []
    for point in selected:
        kappa = kappa_cache[point.parameter_key]
        values = -1j * np.tan((0.01 / np.sqrt(point.detector_n)) * kappa)
        theta = 2.0 * np.arctan(np.abs(values))
        metrics = diagnostic.calculate(
            AnisotropicSample(values, theta, 1, 0.0, 0.0)
        )
        non_atomic = len(np.unique(np.round(theta, 10))) / theta.size
        rows.append(
            {
                "detector_n": point.detector_n,
                "hz": point.hz,
                "J": point.j,
                "Jpm": point.jpm,
                "microscopic_candidate": classifier.microscopic_candidate(point),
                "observed_joint": classifier.is_joint(point),
                "kernel_born_score": metrics.born_score,
                "kernel_born_rmse": metrics.born_rmse,
                "kernel_coverage": metrics.coverage,
                "kernel_non_atomic_fraction": non_atomic,
            }
        )

    score_grid = np.linspace(-0.5, 0.8, 27)
    coverage_grid = np.linspace(0.1, 0.8, 8)
    atomic_grid = np.linspace(0.05, 0.8, 16)
    training = [row for row in rows if row["detector_n"] == 13]
    best: tuple[float, float, float, float] | None = None
    best_zero_fp: tuple[int, float, float, float] | None = None
    for score in score_grid:
        for coverage in coverage_grid:
            for non_atomic in atomic_grid:
                predicted = [
                    bool(row["microscopic_candidate"])
                    and float(row["kernel_born_score"]) >= score
                    and float(row["kernel_coverage"]) >= coverage
                    and float(row["kernel_non_atomic_fraction"]) >= non_atomic
                    for row in training
                ]
                observed = [bool(row["observed_joint"]) for row in training]
                metrics = confusion(predicted, observed)
                precision = float(metrics["precision"])
                recall = float(metrics["recall"])
                f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
                candidate = (f1, score, coverage, non_atomic)
                if best is None or candidate > best:
                    best = candidate
                if int(metrics["fp"]) == 0 and int(metrics["tp"]) > 0:
                    zero_fp_candidate = (int(metrics["tp"]), score, coverage, non_atomic)
                    if best_zero_fp is None or zero_fp_candidate > best_zero_fp:
                        best_zero_fp = zero_fp_candidate
    assert best is not None
    _, score_threshold, coverage_threshold, non_atomic_threshold = best

    evaluation: dict[str, object] = {}
    for n in (13, 14):
        subset = [row for row in rows if row["detector_n"] == n]
        predicted = [
            bool(row["microscopic_candidate"])
            and float(row["kernel_born_score"]) >= score_threshold
            and float(row["kernel_coverage"]) >= coverage_threshold
            and float(row["kernel_non_atomic_fraction"]) >= non_atomic_threshold
            for row in subset
        ]
        evaluation[f"N{n}"] = confusion(predicted, [bool(row["observed_joint"]) for row in subset])

    zero_fp_summary: dict[str, object] | None = None
    strict_rows: list[dict[str, object]] = []
    if best_zero_fp is not None:
        _, zero_score, zero_coverage, zero_non_atomic = best_zero_fp
        zero_evaluation: dict[str, object] = {}
        for n in (13, 14):
            subset = [row for row in rows if row["detector_n"] == n]
            predicted = [
                bool(row["microscopic_candidate"])
                and float(row["kernel_born_score"]) >= zero_score
                and float(row["kernel_coverage"]) >= zero_coverage
                and float(row["kernel_non_atomic_fraction"]) >= zero_non_atomic
                for row in subset
            ]
            zero_evaluation[f"N{n}"] = confusion(predicted, [bool(row["observed_joint"]) for row in subset])
        zero_fp_summary = {
            "condition": {
                "kernel_born_score_min": zero_score,
                "kernel_coverage_min": zero_coverage,
                "kernel_non_atomic_fraction_min": zero_non_atomic,
            },
            "evaluation": zero_evaluation,
        }
        strict_rows = [
            row
            for row in rows
            if bool(row["microscopic_candidate"])
            and float(row["kernel_born_score"]) >= zero_score
            and float(row["kernel_coverage"]) >= zero_coverage
            and float(row["kernel_non_atomic_fraction"]) >= zero_non_atomic
        ]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT / "kernel_balance_parameter_condition.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    strict_path = OUTPUT / "strict_parameter_certified_hamiltonians.csv"
    with strict_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(strict_rows)

    n14_rows = [row for row in rows if row["detector_n"] == 14]
    base_n14 = confusion(
        [bool(row["microscopic_candidate"]) for row in n14_rows],
        [bool(row["observed_joint"]) for row in n14_rows],
    )
    f1_n14 = evaluation["N14"]
    strict_n14 = zero_fp_summary["evaluation"]["N14"] if zero_fp_summary else {"precision": 0.0, "recall": 0.0}
    labels = ["resonance+mixing", "kernel F1 rule", "strict kernel rule"]
    precision = [float(base_n14["precision"]), float(f1_n14["precision"]), float(strict_n14["precision"])]
    recall = [float(base_n14["recall"]), float(f1_n14["recall"]), float(strict_n14["recall"])]
    x = np.arange(len(labels))
    figure, axis = plt.subplots(figsize=(8.2, 4.5))
    width = 0.34
    axis.bar(x - width / 2.0, precision, width, color="#2A9D55", label="precision")
    axis.bar(x + width / 2.0, recall, width, color="#457B9D", label="recall")
    axis.set_xticks(x, labels)
    axis.set_ylim(0.0, 1.08)
    axis.set_ylabel("held-out N=14 score")
    axis.set_title("Successive parameter-level reciprocity conditions")
    axis.legend(frameon=False)
    for offset, values in ((-width / 2.0, precision), (width / 2.0, recall)):
        for index, value in enumerate(values):
            axis.text(index + offset, value + 0.025, f"{value:.2f}", ha="center", fontsize=9)
    figure.tight_layout()
    figure_path = OUTPUT.parent / "figures" / "kernel_parameter_condition_verification.png"
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(figure_path, dpi=220)
    plt.close(figure)
    summary = {
        "probe_n": 6,
        "trained_on": "N=13 complete grid",
        "held_out": "N=14 complete grid",
        "condition": {
            "kernel_born_score_min": score_threshold,
            "kernel_coverage_min": coverage_threshold,
            "kernel_non_atomic_fraction_min": non_atomic_threshold,
        },
        "evaluation": evaluation,
        "zero_training_false_positive_rule": zero_fp_summary,
        "N14_resonance_mixing_baseline": base_n14,
        "strict_selected_rows": len(strict_rows),
        "strict_collection": str(strict_path.relative_to(ROOT)),
        "figure": str(figure_path.relative_to(ROOT)),
        "conclusion": "accept only if the N=14 holdout materially improves over the resonance-mixing screen",
    }
    (OUTPUT / "kernel_balance_parameter_condition.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
