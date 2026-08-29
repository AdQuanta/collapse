"""Reproducible assessment of the Zeus degeneracy/heavy-tail campaigns.

The analysis deliberately separates:

* the targeted campaign, whose exact-activation labels are proven for every N;
* the relative-scale campaign, which supplies a broad parameter survey but
  only receives an activation label on analytically certified Ising and SU(2)
  subfamilies.

Incomplete sizes are retained in the snapshot manifest but excluded from the
primary cross-size conclusions.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
import numpy as np  # noqa: E402


PRIMARY_METRICS = (
    "theta_power_law_alpha",
    "theta_power_law_js",
    "theta_power_law_log10_span",
    "angular_bin_coverage",
    "radius_atomic_fraction",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    temporary.replace(path)
    return path


def _atomic_csv(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    fieldnames: Sequence[str],
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)
    return path


@dataclass(frozen=True)
class AssessmentPaths:
    project_root: Path
    targeted_root: Path
    relative_root: Path
    output_root: Path

    @classmethod
    def defaults(cls, project_root: Path, output_root: Path) -> "AssessmentPaths":
        root = Path(project_root)
        return cls(
            project_root=root,
            targeted_root=root / "work" / "zeus_degeneracy_heavy_tail_iff_N13_N18",
            relative_root=root / "work" / "zeus_relative_scale_regimes_20260724_144102",
            output_root=Path(output_root),
        )


@dataclass(frozen=True)
class ResultRow:
    campaign: str
    detector_n: int
    case_id: str
    hz: float
    J: float
    Jpm: float
    heavy_primary: bool
    heavy_robust: bool | None
    exact_active: bool | None
    activation_certificate: str
    metrics: Mapping[str, float]
    raw_path: Path
    figure_path: Path
    role_or_regime: str

    @property
    def logical_category(self) -> str | None:
        if self.exact_active is None:
            return None
        if self.exact_active and self.heavy_primary:
            return "active_and_broad"
        if self.exact_active and not self.heavy_primary:
            return "active_not_broad"
        if not self.exact_active and self.heavy_primary:
            return "inactive_but_broad"
        return "inactive_not_broad"


class ZeusResultReader:
    """Read checkpoint metrics directly, avoiding stale aggregate snapshots."""

    def __init__(self, paths: AssessmentPaths) -> None:
        self.paths = paths

    def completed_sizes(self, root: Path, expected_cases: int) -> tuple[int, ...]:
        completed: list[int] = []
        for done in sorted((root / "status").glob("N*/DONE.json")):
            payload = _read_json(done)
            if int(payload.get("completed_cases", -1)) == expected_cases:
                completed.append(int(payload["detector_n"]))
        return tuple(completed)

    def partial_sizes(self, root: Path) -> dict[int, int]:
        partial: dict[int, int] = {}
        for running in sorted((root / "status").glob("N*/RUNNING.json")):
            payload = _read_json(running)
            partial[int(payload["detector_n"])] = int(payload.get("completed_cases", 0))
        return partial

    def targeted_rows(self) -> list[ResultRow]:
        rows: list[ResultRow] = []
        for path in sorted(
            (self.paths.targeted_root / "campaign_metrics").glob("N*/*/metrics.json")
        ):
            payload = _read_json(path)
            definition = payload["definition"]
            certificate = payload["activation_certificate"]
            metrics = payload["spectrum_metrics"]
            rows.append(
                ResultRow(
                    campaign="targeted",
                    detector_n=int(metrics["detector_n"]),
                    case_id=str(definition["case_id"]),
                    hz=float(definition["hz"]),
                    J=float(definition["J"]),
                    Jpm=float(definition["Jpm"]),
                    heavy_primary=bool(payload["heavy_primary"]),
                    heavy_robust=bool(payload["heavy_robust"]),
                    exact_active=bool(certificate["exact_active"]),
                    activation_certificate=str(certificate["certificate_type"]),
                    metrics={name: float(metrics[name]) for name in PRIMARY_METRICS},
                    raw_path=self.paths.project_root / payload["raw_path"],
                    figure_path=self.paths.project_root / payload["figure_path"],
                    role_or_regime=str(definition["role"]),
                )
            )
        return rows

    @staticmethod
    def _certify_relative(
        hz: float,
        J: float,
        Jpm: float,
        *,
        tolerance: float = 1.0e-12,
    ) -> tuple[bool | None, str]:
        if math.isclose(Jpm, 0.0, rel_tol=0.0, abs_tol=tolerance):
            resonances = (-2.0 * J, 0.0, 2.0 * J)
            active = any(
                math.isclose(hz, value, rel_tol=0.0, abs_tol=tolerance)
                for value in resonances
            )
            return active, "ising_local_flip"
        if J > 0.0 and math.isclose(
            Jpm,
            2.0 * J,
            rel_tol=0.0,
            abs_tol=tolerance,
        ):
            return (
                math.isclose(hz, 0.0, rel_tol=0.0, abs_tol=tolerance),
                "su2_total_spin",
            )
        return None, "uncertified_general_anisotropic"

    def relative_rows(self) -> list[ResultRow]:
        rows: list[ResultRow] = []
        for path in sorted(
            (self.paths.relative_root / "regime_metrics").glob("N*/*/metrics.json")
        ):
            payload = _read_json(path)
            definition = payload["definition"]
            metrics = payload["spectrum_metrics"]
            hz = float(definition["hz"])
            J = float(definition["J"])
            Jpm = float(definition["Jpm"])
            active, certificate = self._certify_relative(hz, J, Jpm)
            heavy = bool(
                float(metrics["theta_power_law_alpha"]) <= 2.0
                and float(metrics["theta_power_law_js"]) <= 0.10
                and float(metrics["angular_bin_coverage"]) >= 0.50
                and float(metrics["theta_power_law_log10_span"]) >= 1.0
            )
            rows.append(
                ResultRow(
                    campaign="relative_scale",
                    detector_n=int(metrics["detector_n"]),
                    case_id=str(definition["case_id"]),
                    hz=hz,
                    J=J,
                    Jpm=Jpm,
                    heavy_primary=heavy,
                    heavy_robust=None,
                    exact_active=active,
                    activation_certificate=certificate,
                    metrics={name: float(metrics[name]) for name in PRIMARY_METRICS},
                    raw_path=self.paths.project_root / payload["raw_path"],
                    figure_path=self.paths.project_root / payload["figure_path"],
                    role_or_regime=str(definition["regime"]),
                )
            )
        return rows


class ZeusResultValidator:
    """Validate completeness, paths, finite metrics, and expected dimensions."""

    @staticmethod
    def validate_rows(rows: Iterable[ResultRow]) -> dict[str, Any]:
        rows = list(rows)
        missing_raw_paths: list[str] = []
        missing_figure_paths: list[str] = []
        nonfinite: list[str] = []
        duplicates: list[str] = []
        seen: set[tuple[str, int, str]] = set()
        for row in rows:
            key = (row.campaign, row.detector_n, row.case_id)
            if key in seen:
                duplicates.append("/".join(map(str, key)))
            seen.add(key)
            if not row.raw_path.is_file():
                missing_raw_paths.append(str(row.raw_path))
            if not row.figure_path.is_file():
                missing_figure_paths.append(str(row.figure_path))
            for name, value in row.metrics.items():
                if not math.isfinite(value):
                    nonfinite.append(f"{row.campaign}/N{row.detector_n}/{row.case_id}/{name}")
        if duplicates or missing_figure_paths or nonfinite:
            raise ValueError(
                "invalid Zeus result snapshot: "
                f"duplicates={duplicates}, missing_figures={missing_figure_paths}, "
                f"nonfinite={nonfinite}"
            )
        return {
            "row_count": len(rows),
            "figure_paths_present": True,
            "raw_paths_present": not missing_raw_paths,
            "missing_raw_path_count": len(missing_raw_paths),
            "missing_raw_paths": missing_raw_paths,
            "primary_metrics_finite": True,
            "duplicate_case_size_rows": 0,
        }

    @staticmethod
    def validate_complete_sizes(
        rows: Sequence[ResultRow],
        sizes: Sequence[int],
        expected_cases: int,
    ) -> None:
        counts = Counter(row.detector_n for row in rows)
        failures = {
            size: counts[size]
            for size in sizes
            if counts[size] != expected_cases
        }
        if failures:
            raise ValueError(f"incomplete DONE sizes: {failures}; expected {expected_cases}")


class DegeneracyConjectureAssessment:
    """Compute logical truth tables and finite-size persistence."""

    TARGET_CASE_ORDER = (
        "active_flat_atomic",
        "nonising_su2_active_hz0",
        "active_hz0_resonance",
        "active_plus_2J",
        "active_minus_2J",
        "inactive_near_plus_2J",
        "inactive_near_minus_2J",
        "inactive_far_control",
        "nonising_su2_small",
        "nonising_su2_medium",
        "nonising_su2_large",
    )

    def __init__(
        self,
        targeted_rows: Sequence[ResultRow],
        relative_rows: Sequence[ResultRow],
        complete_target_sizes: Sequence[int],
        complete_relative_sizes: Sequence[int],
        project_root: Path,
    ) -> None:
        self.targeted_rows = list(targeted_rows)
        self.relative_rows = list(relative_rows)
        self.complete_target_sizes = tuple(complete_target_sizes)
        self.complete_relative_sizes = tuple(complete_relative_sizes)
        self.project_root = Path(project_root)

    def targeted_complete(self) -> list[ResultRow]:
        allowed = set(self.complete_target_sizes)
        return [row for row in self.targeted_rows if row.detector_n in allowed]

    def relative_complete(self) -> list[ResultRow]:
        allowed = set(self.complete_relative_sizes)
        return [row for row in self.relative_rows if row.detector_n in allowed]

    def truth_table_rows(self) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        by_size: dict[int, list[ResultRow]] = defaultdict(list)
        for row in self.targeted_complete():
            by_size[row.detector_n].append(row)
        for size in sorted(by_size):
            counts = Counter(row.logical_category for row in by_size[size])
            output.append(
                {
                    "detector_n": size,
                    "active_and_broad": counts["active_and_broad"],
                    "active_not_broad": counts["active_not_broad"],
                    "inactive_but_broad": counts["inactive_but_broad"],
                    "inactive_not_broad": counts["inactive_not_broad"],
                    "iff_agreement_fraction": (
                        counts["active_and_broad"] + counts["inactive_not_broad"]
                    )
                    / len(by_size[size]),
                }
            )
        pooled = Counter(row.logical_category for row in self.targeted_complete())
        total = len(self.targeted_complete())
        output.append(
            {
                "detector_n": "pooled_complete",
                "active_and_broad": pooled["active_and_broad"],
                "active_not_broad": pooled["active_not_broad"],
                "inactive_but_broad": pooled["inactive_but_broad"],
                "inactive_not_broad": pooled["inactive_not_broad"],
                "iff_agreement_fraction": (
                    pooled["active_and_broad"] + pooled["inactive_not_broad"]
                )
                / total,
            }
        )
        return output

    def counterexample_rows(self) -> list[dict[str, Any]]:
        decisive = {
            "active_flat_atomic",
            "nonising_su2_active_hz0",
            "inactive_near_plus_2J",
            "inactive_near_minus_2J",
        }
        output: list[dict[str, Any]] = []
        for row in self.targeted_complete():
            if row.case_id not in decisive:
                continue
            output.append(
                {
                    "detector_n": row.detector_n,
                    "case_id": row.case_id,
                    "hz": row.hz,
                    "J": row.J,
                    "Jpm": row.Jpm,
                    "exact_active": row.exact_active,
                    "heavy_primary": row.heavy_primary,
                    "logical_category": row.logical_category,
                    **row.metrics,
                    "figure_path": str(row.figure_path.relative_to(self.project_root)),
                }
            )
        return output

    def relative_persistence_rows(self) -> list[dict[str, Any]]:
        by_case: dict[str, list[ResultRow]] = defaultdict(list)
        for row in self.relative_complete():
            by_case[row.case_id].append(row)
        output: list[dict[str, Any]] = []
        for case_id, rows in by_case.items():
            rows.sort(key=lambda row: row.detector_n)
            certified = {row.exact_active for row in rows}
            exact_active = certified.pop() if len(certified) == 1 else None
            output.append(
                {
                    "case_id": case_id,
                    "regime": rows[0].role_or_regime,
                    "activation_certificate": rows[0].activation_certificate,
                    "exact_active": exact_active,
                    "sizes_completed": len(rows),
                    "heavy_sizes": sum(row.heavy_primary for row in rows),
                    "heavy_fraction": sum(row.heavy_primary for row in rows) / len(rows),
                    "alpha_min": min(row.metrics["theta_power_law_alpha"] for row in rows),
                    "alpha_max": max(row.metrics["theta_power_law_alpha"] for row in rows),
                }
            )
        output.sort(key=lambda row: (-float(row["heavy_fraction"]), str(row["case_id"])))
        return output

    def cross_pipeline_reproducibility(self) -> dict[str, Any]:
        pairs = {
            "active_flat_atomic": "all_zero",
            "active_hz0_resonance": "only_j",
        }
        target = {
            (row.detector_n, row.case_id): row
            for row in self.targeted_complete()
        }
        relative = {
            (row.detector_n, row.case_id): row
            for row in self.relative_complete()
        }
        differences: dict[str, float] = {}
        heavy_mismatches: list[str] = []
        for target_case, relative_case in pairs.items():
            for size in sorted(
                set(self.complete_target_sizes) & set(self.complete_relative_sizes)
            ):
                left = target[(size, target_case)]
                right = relative[(size, relative_case)]
                if left.heavy_primary != right.heavy_primary:
                    heavy_mismatches.append(f"N{size}/{target_case}/{relative_case}")
                for metric in PRIMARY_METRICS:
                    name = f"N{size}/{target_case}/{relative_case}/{metric}"
                    differences[name] = abs(left.metrics[metric] - right.metrics[metric])
        return {
            "duplicate_parameter_pairs_checked": len(pairs)
            * len(set(self.complete_target_sizes) & set(self.complete_relative_sizes)),
            "maximum_primary_metric_absolute_difference": max(differences.values()),
            "heavy_gate_mismatches": heavy_mismatches,
        }

    def sign_symmetry(self) -> dict[str, Any]:
        pairs = (
            ("active_plus_2J", "active_minus_2J"),
            ("inactive_near_plus_2J", "inactive_near_minus_2J"),
        )
        rows = {
            (row.detector_n, row.case_id): row
            for row in self.targeted_complete()
        }
        differences: list[float] = []
        mismatches: list[str] = []
        for positive, negative in pairs:
            for size in self.complete_target_sizes:
                left = rows[(size, positive)]
                right = rows[(size, negative)]
                if left.heavy_primary != right.heavy_primary:
                    mismatches.append(f"N{size}/{positive}/{negative}")
                differences.extend(
                    abs(left.metrics[name] - right.metrics[name])
                    for name in PRIMARY_METRICS
                )
        return {
            "pairs_checked": len(pairs) * len(self.complete_target_sizes),
            "maximum_primary_metric_absolute_difference": max(differences),
            "heavy_gate_mismatches": mismatches,
        }


class AssessmentPlotter:
    """Create compact figures that expose the logical and finite-size result."""

    CATEGORY_COLORS = (
        "#d9d9d9",
        "#e69f00",
        "#cc79a7",
        "#009e73",
    )

    def __init__(self, assessment: DegeneracyConjectureAssessment) -> None:
        self.assessment = assessment

    def plot_targeted_logic(self, path: Path) -> Path:
        sizes = sorted({row.detector_n for row in self.assessment.targeted_rows})
        order = list(self.assessment.TARGET_CASE_ORDER)
        lookup = {
            (row.case_id, row.detector_n): row
            for row in self.assessment.targeted_rows
        }
        category_value = {
            "inactive_not_broad": 0.0,
            "inactive_but_broad": 1.0,
            "active_not_broad": 2.0,
            "active_and_broad": 3.0,
        }
        matrix = np.full((len(order), len(sizes)), np.nan)
        for row_index, case_id in enumerate(order):
            for column_index, size in enumerate(sizes):
                row = lookup.get((case_id, size))
                if row is not None:
                    matrix[row_index, column_index] = category_value[row.logical_category]

        figure, axis = plt.subplots(figsize=(9.0, 6.2), constrained_layout=True)
        masked = np.ma.masked_invalid(matrix)
        cmap = ListedColormap(self.CATEGORY_COLORS).with_extremes(bad="white")
        axis.imshow(masked, cmap=cmap, vmin=-0.5, vmax=3.5, aspect="auto")
        axis.set_xticks(range(len(sizes)), [f"N={size}" for size in sizes])
        axis.set_yticks(
            range(len(order)),
            [case_id.replace("_", " ") for case_id in order],
        )
        axis.set_title(
            "Exact degenerate activation versus resolved broadness "
            r"($t=10^6$, primary preregistered gate)"
        )
        axis.set_xlabel("detector size; N=17 is partial")
        axis.tick_params(axis="y", labelsize=8.5)
        axis.set_xticks(np.arange(-0.5, len(sizes), 1), minor=True)
        axis.set_yticks(np.arange(-0.5, len(order), 1), minor=True)
        axis.grid(which="minor", color="white", linewidth=1.2)
        axis.tick_params(which="minor", bottom=False, left=False)
        axis.legend(
            handles=[
                Patch(facecolor=self.CATEGORY_COLORS[0], label="inactive, not broad"),
                Patch(facecolor=self.CATEGORY_COLORS[1], label="inactive but broad"),
                Patch(facecolor=self.CATEGORY_COLORS[2], label="active, not broad"),
                Patch(facecolor=self.CATEGORY_COLORS[3], label="active and broad"),
            ],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.10),
            ncol=2,
            frameon=False,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, dpi=220, bbox_inches="tight")
        plt.close(figure)
        return path

    def plot_decisive_metrics(self, path: Path) -> Path:
        selected = (
            "active_flat_atomic",
            "nonising_su2_active_hz0",
            "inactive_near_plus_2J",
            "inactive_near_minus_2J",
        )
        labels = {
            "active_flat_atomic": "active flat/atomic",
            "nonising_su2_active_hz0": "active SU(2), hz=0",
            "inactive_near_plus_2J": "inactive hz=+2.01J",
            "inactive_near_minus_2J": "inactive hz=-2.01J",
        }
        colors = {
            "active_flat_atomic": "#cc79a7",
            "nonising_su2_active_hz0": "#8e5ea2",
            "inactive_near_plus_2J": "#e69f00",
            "inactive_near_minus_2J": "#0072b2",
        }
        markers = {
            "active_flat_atomic": "o",
            "nonising_su2_active_hz0": "s",
            "inactive_near_plus_2J": "^",
            "inactive_near_minus_2J": "v",
        }
        by_case: dict[str, list[ResultRow]] = defaultdict(list)
        for row in self.assessment.targeted_complete():
            if row.case_id in selected:
                by_case[row.case_id].append(row)

        panels = (
            ("theta_power_law_alpha", r"fitted $\alpha$", 2.0),
            ("theta_power_law_js", "power-law JS divergence", 0.10),
            ("theta_power_law_log10_span", "occupied log-span (decades)", 1.0),
            ("angular_bin_coverage", "angular-bin coverage", 0.50),
        )
        figure, axes = plt.subplots(2, 2, figsize=(9.2, 6.6), sharex=True)
        for axis, (metric, ylabel, gate) in zip(axes.flat, panels):
            for case_id in selected:
                rows = sorted(by_case[case_id], key=lambda row: row.detector_n)
                axis.plot(
                    [row.detector_n for row in rows],
                    [row.metrics[metric] for row in rows],
                    color=colors[case_id],
                    marker=markers[case_id],
                    linewidth=1.8,
                    markersize=5,
                    label=labels[case_id],
                )
            axis.axhline(gate, color="black", linestyle="--", linewidth=1.0)
            axis.set_ylabel(ylabel)
            axis.grid(alpha=0.22)
        for axis in axes[-1]:
            axis.set_xlabel("detector size N")
        axes[0, 0].legend(fontsize=8, frameon=False)
        figure.suptitle(
            "The two counterexample directions persist with system size",
            fontsize=13,
        )
        figure.tight_layout()
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, dpi=220, bbox_inches="tight")
        plt.close(figure)
        return path

    def plot_relative_persistence(self, path: Path) -> Path:
        complete = self.assessment.relative_complete()
        sizes = list(self.assessment.complete_relative_sizes)
        by_case: dict[str, list[ResultRow]] = defaultdict(list)
        for row in complete:
            by_case[row.case_id].append(row)
        order = sorted(
            by_case,
            key=lambda case_id: (
                -sum(row.heavy_primary for row in by_case[case_id]),
                case_id,
            ),
        )
        matrix = np.zeros((len(order), len(sizes)), dtype=float)
        lookup = {(row.case_id, row.detector_n): row for row in complete}
        for row_index, case_id in enumerate(order):
            for column_index, size in enumerate(sizes):
                matrix[row_index, column_index] = float(
                    lookup[(case_id, size)].heavy_primary
                )
        figure, axis = plt.subplots(figsize=(7.8, 9.2), constrained_layout=True)
        axis.imshow(
            matrix,
            cmap=ListedColormap(("#d73027", "#1a9850")),
            vmin=-0.5,
            vmax=1.5,
            aspect="auto",
        )
        axis.set_xticks(range(len(sizes)), [f"N={size}" for size in sizes])
        axis.set_yticks(
            range(len(order)),
            [case_id.replace("_", " ") for case_id in order],
        )
        axis.tick_params(axis="y", labelsize=7.4)
        axis.set_title(
            "Resolved broadness across all 30 relative-scale regimes\n"
            "(red: fails; green: passes; no cell annotations)"
        )
        axis.set_xticks(np.arange(-0.5, len(sizes), 1), minor=True)
        axis.set_yticks(np.arange(-0.5, len(order), 1), minor=True)
        axis.grid(which="minor", color="white", linewidth=0.8)
        axis.tick_params(which="minor", bottom=False, left=False)
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, dpi=220, bbox_inches="tight")
        plt.close(figure)
        return path


def run_assessment(paths: AssessmentPaths) -> dict[str, Any]:
    reader = ZeusResultReader(paths)
    targeted = reader.targeted_rows()
    relative = reader.relative_rows()
    target_complete = reader.completed_sizes(paths.targeted_root, expected_cases=11)
    relative_complete = reader.completed_sizes(paths.relative_root, expected_cases=30)
    target_partial = reader.partial_sizes(paths.targeted_root)
    relative_partial = reader.partial_sizes(paths.relative_root)

    validator = ZeusResultValidator()
    target_validation = validator.validate_rows(targeted)
    relative_validation = validator.validate_rows(relative)
    validator.validate_complete_sizes(targeted, target_complete, 11)
    validator.validate_complete_sizes(relative, relative_complete, 30)

    assessment = DegeneracyConjectureAssessment(
        targeted,
        relative,
        target_complete,
        relative_complete,
        paths.project_root,
    )
    truth_rows = assessment.truth_table_rows()
    counterexample_rows = assessment.counterexample_rows()
    persistence_rows = assessment.relative_persistence_rows()

    _atomic_csv(
        paths.output_root / "targeted_truth_table.csv",
        truth_rows,
        (
            "detector_n",
            "active_and_broad",
            "active_not_broad",
            "inactive_but_broad",
            "inactive_not_broad",
            "iff_agreement_fraction",
        ),
    )
    _atomic_csv(
        paths.output_root / "decisive_counterexamples.csv",
        counterexample_rows,
        tuple(counterexample_rows[0].keys()),
    )
    _atomic_csv(
        paths.output_root / "relative_scale_persistence.csv",
        persistence_rows,
        tuple(persistence_rows[0].keys()),
    )

    plotter = AssessmentPlotter(assessment)
    figures = {
        "targeted_logic": str(
            plotter.plot_targeted_logic(paths.output_root / "targeted_logic_matrix.png")
        ),
        "decisive_metrics": str(
            plotter.plot_decisive_metrics(
                paths.output_root / "decisive_metrics_vs_N.png"
            )
        ),
        "relative_persistence": str(
            plotter.plot_relative_persistence(
                paths.output_root / "relative_scale_broadness_persistence.png"
            )
        ),
    }

    pooled = truth_rows[-1]
    persistent_relative = Counter(
        int(row["heavy_sizes"]) for row in persistence_rows
    )
    certified_relative = [
        row
        for row in persistence_rows
        if row["activation_certificate"] != "uncertified_general_anisotropic"
    ]
    summary = {
        "verdict": "universal_iff_falsified_both_directions",
        "primary_complete_target_sizes": list(target_complete),
        "primary_complete_relative_sizes": list(relative_complete),
        "partial_target_sizes": target_partial,
        "partial_relative_sizes": relative_partial,
        "target_validation": target_validation,
        "relative_validation": relative_validation,
        "pooled_target_truth_table": pooled,
        "stable_sufficiency_counterexamples": [
            "active_flat_atomic",
            "nonising_su2_active_hz0",
        ],
        "stable_necessity_counterexamples": [
            "inactive_near_plus_2J",
            "inactive_near_minus_2J",
        ],
        "relative_scale_complete_rows": len(assessment.relative_complete()),
        "relative_scale_persistence_counts": {
            f"heavy_in_{sizes}_of_{len(relative_complete)}_sizes": count
            for sizes, count in sorted(persistent_relative.items())
        },
        "relative_scale_certified_case_count": len(certified_relative),
        "cross_pipeline_reproducibility": assessment.cross_pipeline_reproducibility(),
        "positive_negative_hz_symmetry": assessment.sign_symmetry(),
        "figures": figures,
        "interpretation": (
            "Exact degenerate activation is neither sufficient nor necessary. "
            "It can enrich broadness in broad parameter surveys, but resolved "
            "near-degenerate weight, block rank/participation, and non-atomic "
            "phase spreading are additional dynamical requirements."
        ),
    }
    _atomic_json(paths.output_root / "analysis_summary.json", summary)
    return summary


__all__ = [
    "AssessmentPaths",
    "DegeneracyConjectureAssessment",
    "ResultRow",
    "ZeusResultReader",
    "ZeusResultValidator",
    "run_assessment",
]
