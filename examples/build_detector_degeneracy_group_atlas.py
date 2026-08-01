"""Build a group-ordered atlas of detector degeneracy and qubit diagnostics.

The script classifies all 880 complete N=14 anisotropic single-pixel cases into

1. resolved broad/heavy-tailed P(theta) with Born-like R(theta);
2. resolved broad/heavy-tailed P(theta) with non-Born R(theta); and
3. non-broad P(theta).

It reuses the already generated minus-log detector energy-gap heatmaps and
cropped P/R diagnostics.  Only the inexpensive N_D=8 detector spectra are
recomputed, because the previous atlas did not persist the full multiplicity
vectors.  For every case the script saves a histogram of degenerate-subspace
multiplicities, a checkpointed numerical index, group-level statistical
comparisons, compact contact sheets, and a self-contained LaTeX report.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont
from scipy.stats import kruskal, mannwhitneyu, spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collapse.detector_resonance import DenseRingDetectorBuilder, DetectorSpec  # noqa: E402


SOURCE_JOINED = (
    ROOT
    / "reports"
    / "vab_degenerate_activation_study_2026-07-22"
    / "data"
    / "vab_activation_N08_to_dynamics_N14.csv"
)
SOURCE_ATLAS = ROOT / "reports" / "vab_activation_all_cases_2026-07-27"
SOURCE_ATLAS_INDEX = SOURCE_ATLAS / "data" / "atlas_cases.csv"
DEFAULT_OUTPUT = ROOT / "reports" / "vab_coupling_group_atlas_2026-07-28"
DEFAULT_TEX = DEFAULT_OUTPUT / "vab_coupling_group_atlas_2026-07-28.tex"

GROUP_ORDER = ("broad_born", "broad_nonborn", "non_broad")
GROUP_LABELS = {
    "broad_born": r"Broad $P(\theta)$; Born-like $R(\theta)$",
    "broad_nonborn": r"Broad $P(\theta)$; non-Born $R(\theta)$",
    "non_broad": r"Non-broad $P(\theta)$",
}
GROUP_PLAIN = {
    "broad_born": "Broad P(theta), Born-like R(theta)",
    "broad_nonborn": "Broad P(theta), non-Born R(theta)",
    "non_broad": "Non-broad P(theta)",
}
GROUP_COLORS = {
    "broad_born": "#198754",
    "broad_nonborn": "#d97706",
    "non_broad": "#64748b",
}

DEGENERACY_METRICS = (
    ("degenerate_state_fraction", r"$f_{\rm deg}$"),
    ("maximum_multiplicity", r"$m_{\max}$"),
    ("degenerate_pair_fraction", r"$F_{\rm pair}$"),
    ("distinct_energy_fraction", r"$N_E/D$"),
    ("degenerate_subspaces", r"$N_{\rm deg}$"),
)

ACTIVATION_METRICS = (
    ("exact_active_weight_fraction", r"exact $V$ weight $D_{\rm act}$"),
    ("active_degenerate_state_fraction", r"active degenerate-state fraction"),
    ("exact_activation_rank_fraction", r"exact-block rank fraction"),
    ("exact_spectral_participation_fraction", r"exact-block spectral participation"),
    ("weight_fraction_gap_le_1em6", r"$V$ weight at $|\Delta E|\leq10^{-6}$"),
    ("weight_fraction_gap_le_1em4", r"$V$ weight at $|\Delta E|\leq10^{-4}$"),
    ("finite_time_kernel_power_fraction", r"finite-time resonant power $F_t$"),
    (
        "finite_time_transition_participation_fraction",
        r"finite-time transition participation",
    ),
)

ALL_METRICS = DEGENERACY_METRICS + ACTIVATION_METRICS


@dataclass(frozen=True)
class ClassificationPolicy:
    """Registered broadness and Born-similarity gates from the prior study."""

    maximum_power_law_js: float = 0.10
    minimum_angular_coverage: float = 0.50
    minimum_power_law_span: float = 1.0
    maximum_broad_alpha: float = 2.0
    minimum_born_score: float = 0.75
    maximum_born_rmse: float = 0.15

    def is_broad(self, row: dict[str, str]) -> bool:
        return (
            float(row["theta_power_law_js"]) <= self.maximum_power_law_js
            and float(row["angular_bin_coverage"]) >= self.minimum_angular_coverage
            and float(row["theta_power_law_log10_span"]) >= self.minimum_power_law_span
            and float(row["theta_power_law_alpha"]) <= self.maximum_broad_alpha
        )

    def is_born_like(self, row: dict[str, str]) -> bool:
        return (
            float(row["S_born"]) >= self.minimum_born_score
            and float(row["born_rmse"]) <= self.maximum_born_rmse
            and float(row["angular_bin_coverage"]) >= self.minimum_angular_coverage
        )

    def group(self, row: dict[str, str]) -> str:
        broad = self.is_broad(row)
        if not broad:
            return "non_broad"
        return "broad_born" if self.is_born_like(row) else "broad_nonborn"


@dataclass(frozen=True)
class CaseInput:
    """One parameter point with existing dynamical assets and metrics."""

    ordinal: int
    detector_n: int
    dynamics_n: int
    hz: float
    j: float
    jpm: float
    evolution_time: float
    born_score: float
    born_rmse: float
    angular_coverage: float
    power_law_alpha: float
    power_law_js: float
    power_law_log10_span: float
    exact_active_weight_fraction: float
    active_degenerate_state_fraction: float
    exact_activation_rank_fraction: float
    exact_spectral_participation_fraction: float
    weight_fraction_gap_le_1em6: float
    weight_fraction_gap_le_1em5: float
    weight_fraction_gap_le_1em4: float
    weight_fraction_gap_le_1em3: float
    weight_fraction_gap_le_1em2: float
    weight_fraction_gap_le_1em1: float
    finite_time_kernel_power_fraction: float
    finite_time_transition_participation_fraction: float
    group: str
    heatmap_path: str
    vab_plot_path: str
    diagnostic_path: str
    multiplicity_plot_path: str

    @property
    def key(self) -> str:
        return f"hz={self.hz:g},J={self.j:g},Jpm={self.jpm:g}"


@dataclass(frozen=True)
class CaseResult:
    """Persisted spectrum-degeneracy result for one parameter point."""

    case: CaseInput
    dimension: int
    distinct_energies: int
    degenerate_subspaces: int
    degenerate_states: int
    degenerate_state_fraction: float
    maximum_multiplicity: int
    mean_degenerate_multiplicity: float
    degenerate_pair_fraction: float
    distinct_energy_fraction: float
    multiplicity_counts: tuple[tuple[int, int], ...]
    hamiltonian_hermiticity_error: float
    coupling_hermiticity_error: float
    eigenvector_orthonormality_error: float
    maximum_relative_eigenpair_residual: float
    coupling_transform_relative_norm_error: float

    def to_row(self) -> dict[str, Any]:
        row = asdict(self.case)
        row.update(
            {
                "dimension": self.dimension,
                "distinct_energies": self.distinct_energies,
                "degenerate_subspaces": self.degenerate_subspaces,
                "degenerate_states": self.degenerate_states,
                "degenerate_state_fraction": self.degenerate_state_fraction,
                "maximum_multiplicity": self.maximum_multiplicity,
                "mean_degenerate_multiplicity": self.mean_degenerate_multiplicity,
                "degenerate_pair_fraction": self.degenerate_pair_fraction,
                "distinct_energy_fraction": self.distinct_energy_fraction,
                "hamiltonian_hermiticity_error": self.hamiltonian_hermiticity_error,
                "coupling_hermiticity_error": self.coupling_hermiticity_error,
                "eigenvector_orthonormality_error": self.eigenvector_orthonormality_error,
                "maximum_relative_eigenpair_residual": self.maximum_relative_eigenpair_residual,
                "coupling_transform_relative_norm_error": self.coupling_transform_relative_norm_error,
                "multiplicity_counts": ";".join(
                    f"{multiplicity}:{count}"
                    for multiplicity, count in self.multiplicity_counts
                ),
            }
        )
        return row


class CaseRepository:
    """Load and validate the joined dynamics and prior atlas indices."""

    def __init__(
        self,
        joined_path: Path,
        atlas_index_path: Path,
        output_root: Path,
        policy: ClassificationPolicy,
    ) -> None:
        self.joined_path = joined_path
        self.atlas_index_path = atlas_index_path
        self.output_root = output_root
        self.policy = policy

    @staticmethod
    def _key(row: dict[str, str]) -> tuple[float, float, float]:
        return float(row["hz"]), float(row["J"]), float(row["Jpm"])

    def load(self) -> list[CaseInput]:
        with self.joined_path.open(newline="", encoding="utf-8") as handle:
            joined_rows = list(csv.DictReader(handle))
        with self.atlas_index_path.open(newline="", encoding="utf-8") as handle:
            atlas_rows = list(csv.DictReader(handle))
        atlas_by_key = {
            (float(row["hz"]), float(row["j"]), float(row["jpm"])): row
            for row in atlas_rows
        }
        if len(joined_rows) != 880 or len(atlas_by_key) != 880:
            raise RuntimeError(
                f"expected 880 joined and atlas cases; got "
                f"{len(joined_rows)} and {len(atlas_by_key)}"
            )

        cases: list[CaseInput] = []
        for joined in joined_rows:
            key = self._key(joined)
            if key not in atlas_by_key:
                raise KeyError(f"missing prior atlas entry for {key}")
            atlas = atlas_by_key[key]
            broad = self.policy.is_broad(joined)
            if broad != (joined["heavy_tailed"] == "True"):
                raise RuntimeError(f"broad classification mismatch for {key}")
            heatmap = Path(atlas["heatmap_output"])
            diagnostic = Path(atlas["diagnostic_output"])
            if not heatmap.is_file() or not diagnostic.is_file():
                raise FileNotFoundError(
                    f"prior atlas assets missing for {key}: {heatmap}, {diagnostic}"
                )
            relative = heatmap.resolve().relative_to(
                (SOURCE_ATLAS / "figures").resolve()
            ).parent
            multiplicity_plot = (
                self.output_root
                / "figures"
                / "multiplicities"
                / relative
                / "degeneracy_multiplicities.png"
            )
            vab_plot = (
                self.output_root
                / "figures"
                / "vab"
                / relative
                / "vab_magnitude.png"
            )
            cases.append(
                CaseInput(
                    ordinal=int(atlas["ordinal"]),
                    detector_n=int(float(joined["detector_n"])),
                    dynamics_n=int(atlas["dynamics_n"]),
                    hz=key[0],
                    j=key[1],
                    jpm=key[2],
                    evolution_time=float(atlas["evolution_time"]),
                    born_score=float(joined["S_born"]),
                    born_rmse=float(joined["born_rmse"]),
                    angular_coverage=float(joined["angular_bin_coverage"]),
                    power_law_alpha=float(joined["theta_power_law_alpha"]),
                    power_law_js=float(joined["theta_power_law_js"]),
                    power_law_log10_span=float(
                        joined["theta_power_law_log10_span"]
                    ),
                    exact_active_weight_fraction=float(
                        joined["exact_active_weight_fraction"]
                    ),
                    active_degenerate_state_fraction=float(
                        joined["active_degenerate_state_fraction"]
                    ),
                    exact_activation_rank_fraction=float(
                        joined["exact_activation_rank_fraction"]
                    ),
                    exact_spectral_participation_fraction=float(
                        joined["exact_spectral_participation_fraction"]
                    ),
                    weight_fraction_gap_le_1em6=float(
                        joined["weight_fraction_gap_le_1em6"]
                    ),
                    weight_fraction_gap_le_1em5=float(
                        joined["weight_fraction_gap_le_1em5"]
                    ),
                    weight_fraction_gap_le_1em4=float(
                        joined["weight_fraction_gap_le_1em4"]
                    ),
                    weight_fraction_gap_le_1em3=float(
                        joined["weight_fraction_gap_le_1em3"]
                    ),
                    weight_fraction_gap_le_1em2=float(
                        joined["weight_fraction_gap_le_1em2"]
                    ),
                    weight_fraction_gap_le_1em1=float(
                        joined["weight_fraction_gap_le_1em1"]
                    ),
                    finite_time_kernel_power_fraction=float(
                        joined["finite_time_kernel_power_fraction"]
                    ),
                    finite_time_transition_participation_fraction=float(
                        joined["finite_time_transition_participation_fraction"]
                    ),
                    group=self.policy.group(joined),
                    heatmap_path=str(heatmap.resolve()),
                    vab_plot_path=str(vab_plot.resolve()),
                    diagnostic_path=str(diagnostic.resolve()),
                    multiplicity_plot_path=str(multiplicity_plot.resolve()),
                )
            )
        cases.sort(key=lambda case: case.ordinal)
        if [case.ordinal for case in cases] != list(range(1, 881)):
            raise RuntimeError("prior atlas ordinals are incomplete or non-unique")
        return cases


def _energy_groups(
    energies: np.ndarray, tolerance: float
) -> tuple[tuple[int, int], ...]:
    groups: list[tuple[int, int]] = []
    start = 0
    while start < energies.size:
        stop = start + 1
        while (
            stop < energies.size
            and abs(float(energies[stop] - energies[start])) <= tolerance
        ):
            stop += 1
        groups.append((start, stop))
        start = stop
    return tuple(groups)


def _render_multiplicity_histogram(
    multiplicity_counts: Sequence[tuple[int, int]],
    result_metrics: dict[str, float | int],
    output: Path,
) -> None:
    """Render the number of distinct energy subspaces at each multiplicity."""

    multiplicities = np.asarray([item[0] for item in multiplicity_counts], dtype=int)
    counts = np.asarray([item[1] for item in multiplicity_counts], dtype=int)
    colors = ["#94a3b8" if value == 1 else "#0f766e" for value in multiplicities]
    figure, axis = plt.subplots(figsize=(3.45, 3.0))
    axis.bar(multiplicities, counts, width=0.72, color=colors, edgecolor="white", linewidth=0.5)
    axis.set_yscale("log")
    axis.set_ylim(0.8, max(2.0, float(np.max(counts)) * 1.8))
    axis.set(
        xlabel="subspace multiplicity $m$",
        ylabel="number of energy subspaces",
        title="Degenerate-subspace multiplicities",
    )
    if multiplicities.size <= 10:
        axis.set_xticks(multiplicities)
    else:
        selected = np.unique(
            np.concatenate(
                (
                    multiplicities[:4],
                    multiplicities[-4:],
                    np.asarray([int(result_metrics["maximum_multiplicity"])]),
                )
            )
        )
        axis.set_xticks(selected)
    axis.grid(axis="y", which="both", alpha=0.20)
    axis.text(
        0.98,
        0.96,
        "\n".join(
            (
                rf"$N_{{\rm deg}}={int(result_metrics['degenerate_subspaces'])}$",
                rf"$f_{{\rm deg}}={float(result_metrics['degenerate_state_fraction']):.3f}$",
                rf"$m_{{\max}}={int(result_metrics['maximum_multiplicity'])}$",
                rf"$F_{{\rm pair}}={float(result_metrics['degenerate_pair_fraction']):.3g}$",
            )
        ),
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=8.2,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2.0},
    )
    figure.tight_layout(pad=0.65)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=190, bbox_inches="tight")
    plt.close(figure)


def _render_vab_heatmap(coupling: np.ndarray, output: Path) -> None:
    """Render solver-basis V_ab using the established normalized power scale."""

    total_weight = max(float(np.sum(np.abs(coupling) ** 2)), 1.0)
    display = np.log10(
        np.maximum(np.abs(coupling) ** 2 / total_weight, 1.0e-12)
    )
    figure, axis = plt.subplots(figsize=(3.45, 3.0))
    image = axis.imshow(
        display,
        origin="lower",
        cmap="viridis",
        vmin=-12.0,
        vmax=0.0,
        interpolation="nearest",
        rasterized=True,
    )
    axis.set(
        xlabel="sorted eigenstate index $b$",
        ylabel="sorted eigenstate index $a$",
        title=r"Interaction $V_{ab}$",
    )
    colorbar = figure.colorbar(image, ax=axis, fraction=0.046, pad=0.035)
    colorbar.set_label(r"$\log_{10}(|V_{ab}|^2/\mathrm{Tr}\,V^2)$")
    figure.tight_layout(pad=0.65)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=190, bbox_inches="tight")
    plt.close(figure)


def _analyze_case(
    case: CaseInput,
    degeneracy_tolerance: float,
    force: bool,
) -> CaseResult:
    """Worker entry point for one inexpensive N_D=8 spectrum."""

    builder = DenseRingDetectorBuilder()
    operators = builder.build(
        DetectorSpec(case.detector_n, case.hz, case.j, case.jpm)
    )
    hamiltonian = np.asarray(operators.hamiltonian, dtype=np.complex128)
    physical_coupling = np.asarray(operators.coupling, dtype=np.complex128)
    h_scale = max(float(np.linalg.norm(hamiltonian, ord="fro")), 1.0)
    v_scale = max(float(np.linalg.norm(physical_coupling, ord="fro")), 1.0)
    h_hermiticity = float(
        np.linalg.norm(hamiltonian - hamiltonian.conj().T, ord="fro") / h_scale
    )
    v_hermiticity = float(
        np.linalg.norm(
            physical_coupling - physical_coupling.conj().T, ord="fro"
        )
        / v_scale
    )
    if h_hermiticity > 1.0e-12 or v_hermiticity > 1.0e-12:
        raise RuntimeError(f"non-Hermitian detector operators for {case.key}")
    energies, vectors = np.linalg.eigh(hamiltonian)
    energies = np.asarray(energies, dtype=float)
    coupling = vectors.conj().T @ physical_coupling @ vectors
    if np.any(np.diff(energies) < -1.0e-11):
        raise RuntimeError(f"unordered eigenspectrum for {case.key}")
    identity = np.eye(energies.size, dtype=np.complex128)
    orthonormality_error = float(
        np.linalg.norm(vectors.conj().T @ vectors - identity, ord="fro")
        / math.sqrt(energies.size)
    )
    residuals = hamiltonian @ vectors - vectors * energies[None, :]
    column_norms = np.linalg.norm(residuals, axis=0)
    residual_scale = np.maximum(
        np.abs(energies) + np.linalg.norm(hamiltonian, ord=2), 1.0
    )
    maximum_residual = float(np.max(column_norms / residual_scale))
    coupling_norm_error = float(
        abs(
            np.linalg.norm(coupling, ord="fro")
            - np.linalg.norm(physical_coupling, ord="fro")
        )
        / v_scale
    )
    if (
        orthonormality_error > 1.0e-10
        or maximum_residual > 1.0e-10
        or coupling_norm_error > 1.0e-10
    ):
        raise RuntimeError(f"failed eigensystem validation for {case.key}")
    groups = _energy_groups(energies, degeneracy_tolerance)
    multiplicities = np.asarray(
        [stop - start for start, stop in groups], dtype=int
    )
    counts = tuple(sorted(Counter(multiplicities.tolist()).items()))
    degenerate = multiplicities > 1
    dimension = int(energies.size)
    degenerate_states = int(np.sum(multiplicities[degenerate]))
    degenerate_subspaces = int(np.count_nonzero(degenerate))
    pair_numerator = float(np.sum(multiplicities * (multiplicities - 1)))
    pair_denominator = float(dimension * (dimension - 1))
    metrics: dict[str, float | int] = {
        "degenerate_subspaces": degenerate_subspaces,
        "degenerate_state_fraction": degenerate_states / dimension,
        "maximum_multiplicity": int(np.max(multiplicities)),
        "degenerate_pair_fraction": (
            pair_numerator / pair_denominator if pair_denominator else 0.0
        ),
    }
    output = Path(case.multiplicity_plot_path)
    if force or not output.is_file():
        _render_multiplicity_histogram(counts, metrics, output)
    vab_output = Path(case.vab_plot_path)
    if force or not vab_output.is_file():
        _render_vab_heatmap(coupling, vab_output)
    return CaseResult(
        case=case,
        dimension=dimension,
        distinct_energies=int(multiplicities.size),
        degenerate_subspaces=degenerate_subspaces,
        degenerate_states=degenerate_states,
        degenerate_state_fraction=float(metrics["degenerate_state_fraction"]),
        maximum_multiplicity=int(metrics["maximum_multiplicity"]),
        mean_degenerate_multiplicity=(
            float(np.mean(multiplicities[degenerate]))
            if np.any(degenerate)
            else 1.0
        ),
        degenerate_pair_fraction=float(metrics["degenerate_pair_fraction"]),
        distinct_energy_fraction=float(multiplicities.size / dimension),
        multiplicity_counts=counts,
        hamiltonian_hermiticity_error=h_hermiticity,
        coupling_hermiticity_error=v_hermiticity,
        eigenvector_orthonormality_error=orthonormality_error,
        maximum_relative_eigenpair_residual=maximum_residual,
        coupling_transform_relative_norm_error=coupling_norm_error,
    )


def _atomic_write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    last_error: PermissionError | None = None
    for attempt in range(1, 11):
        try:
            temporary.replace(path)
            return
        except PermissionError as error:
            last_error = error
            time.sleep(0.10 * attempt)
    if last_error is not None:
        raise last_error


def _result_from_row(row: dict[str, str]) -> CaseResult:
    case_integer = {"ordinal", "detector_n", "dynamics_n"}
    case_strings = {
        "group",
        "heatmap_path",
        "vab_plot_path",
        "diagnostic_path",
        "multiplicity_plot_path",
    }
    case_fields: dict[str, Any] = {
        name: row[name] for name in CaseInput.__dataclass_fields__
    }
    for name in case_integer:
        case_fields[name] = int(case_fields[name])
    for name in set(case_fields) - case_integer - case_strings:
        case_fields[name] = float(case_fields[name])
    counts = tuple(
        (int(part.split(":")[0]), int(part.split(":")[1]))
        for part in row["multiplicity_counts"].split(";")
        if part
    )
    return CaseResult(
        case=CaseInput(**case_fields),
        dimension=int(row["dimension"]),
        distinct_energies=int(row["distinct_energies"]),
        degenerate_subspaces=int(row["degenerate_subspaces"]),
        degenerate_states=int(row["degenerate_states"]),
        degenerate_state_fraction=float(row["degenerate_state_fraction"]),
        maximum_multiplicity=int(row["maximum_multiplicity"]),
        mean_degenerate_multiplicity=float(row["mean_degenerate_multiplicity"]),
        degenerate_pair_fraction=float(row["degenerate_pair_fraction"]),
        distinct_energy_fraction=float(row["distinct_energy_fraction"]),
        multiplicity_counts=counts,
        hamiltonian_hermiticity_error=float(
            row["hamiltonian_hermiticity_error"]
        ),
        coupling_hermiticity_error=float(row["coupling_hermiticity_error"]),
        eigenvector_orthonormality_error=float(
            row["eigenvector_orthonormality_error"]
        ),
        maximum_relative_eigenpair_residual=float(
            row["maximum_relative_eigenpair_residual"]
        ),
        coupling_transform_relative_norm_error=float(
            row["coupling_transform_relative_norm_error"]
        ),
    )


def _load_checkpoint(path: Path) -> dict[str, CaseResult]:
    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [_result_from_row(row) for row in csv.DictReader(handle)]
    return {result.case.key: result for result in rows}


def _multiplicity_rows(results: Iterable[CaseResult]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        for multiplicity, count in result.multiplicity_counts:
            rows.append(
                {
                    "ordinal": result.case.ordinal,
                    "group": result.case.group,
                    "hz": result.case.hz,
                    "J": result.case.j,
                    "Jpm": result.case.jpm,
                    "multiplicity": multiplicity,
                    "subspace_count": count,
                    "state_count": multiplicity * count,
                }
            )
    return rows


def _quantiles(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
        "q1": float(np.quantile(values, 0.25)),
        "median": float(np.median(values)),
        "q3": float(np.quantile(values, 0.75)),
    }


def _rank_auc(values: np.ndarray, positive: np.ndarray) -> float:
    """Return the probability that a random positive has the larger score."""

    values = np.asarray(values, dtype=float)
    positive = np.asarray(positive, dtype=bool)
    n_positive = int(np.count_nonzero(positive))
    n_negative = int(values.size - n_positive)
    if not n_positive or not n_negative:
        return float("nan")
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=float)
    start = 0
    while start < values.size:
        stop = start + 1
        while stop < values.size and values[order[stop]] == values[order[start]]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + 1 + stop)
        start = stop
    rank_sum = float(np.sum(ranks[positive]))
    return (
        rank_sum - n_positive * (n_positive + 1) / 2.0
    ) / (n_positive * n_negative)


def _holm_adjust(p_values: Sequence[float]) -> list[float]:
    order = np.argsort(np.asarray(p_values, dtype=float))
    adjusted = np.empty(len(p_values), dtype=float)
    running = 0.0
    count = len(p_values)
    for rank, index in enumerate(order):
        candidate = min(1.0, (count - rank) * float(p_values[index]))
        running = max(running, candidate)
        adjusted[index] = running
    return adjusted.tolist()


class StatisticalAnalyzer:
    """Compute group summaries and nonparametric comparisons."""

    def __init__(self, results: Sequence[CaseResult]) -> None:
        self.results = list(results)

    @staticmethod
    def _value(result: CaseResult, metric: str) -> float:
        if hasattr(result, metric):
            return float(getattr(result, metric))
        return float(getattr(result.case, metric))

    def summarize(self) -> dict[str, Any]:
        grouped = {
            group: [result for result in self.results if result.case.group == group]
            for group in GROUP_ORDER
        }
        group_summary: dict[str, Any] = {}
        for group, selected in grouped.items():
            group_summary[group] = {
                "label": GROUP_PLAIN[group],
                "count": len(selected),
                "metrics": {
                    metric: _quantiles(
                        np.asarray(
                            [self._value(result, metric) for result in selected],
                            dtype=float,
                        )
                    )
                    for metric, _ in ALL_METRICS
                },
            }

        omnibus: list[dict[str, Any]] = []
        pairwise: list[dict[str, Any]] = []
        discrimination: list[dict[str, Any]] = []
        for metric, _ in ALL_METRICS:
            arrays = [
                np.asarray(
                    [self._value(result, metric) for result in grouped[group]],
                    dtype=float,
                )
                for group in GROUP_ORDER
            ]
            test = kruskal(*arrays)
            omnibus.append(
                {
                    "metric": metric,
                    "kruskal_H": float(test.statistic),
                    "p_value": float(test.pvalue),
                }
            )
            local_rows: list[dict[str, Any]] = []
            raw_p: list[float] = []
            for group_a, group_b in combinations(GROUP_ORDER, 2):
                a = np.asarray(
                    [self._value(result, metric) for result in grouped[group_a]],
                    dtype=float,
                )
                b = np.asarray(
                    [self._value(result, metric) for result in grouped[group_b]],
                    dtype=float,
                )
                comparison = mannwhitneyu(a, b, alternative="two-sided")
                probability_a_greater = float(
                    comparison.statistic / (a.size * b.size)
                )
                local_rows.append(
                    {
                        "metric": metric,
                        "group_a": group_a,
                        "group_b": group_b,
                        "n_a": int(a.size),
                        "n_b": int(b.size),
                        "mann_whitney_U": float(comparison.statistic),
                        "probability_a_greater": probability_a_greater,
                        "rank_biserial_a_minus_b": 2.0
                        * probability_a_greater
                        - 1.0,
                        "p_value": float(comparison.pvalue),
                    }
                )
                raw_p.append(float(comparison.pvalue))
            adjusted = _holm_adjust(raw_p)
            for row, corrected in zip(local_rows, adjusted, strict=True):
                row["holm_p_value"] = corrected
                pairwise.append(row)

            all_values = np.asarray(
                [self._value(result, metric) for result in self.results],
                dtype=float,
            )
            broad = np.asarray(
                [result.case.group != "non_broad" for result in self.results],
                dtype=bool,
            )
            broad_results = [
                result
                for result in self.results
                if result.case.group != "non_broad"
            ]
            broad_values = np.asarray(
                [self._value(result, metric) for result in broad_results],
                dtype=float,
            )
            born_within_broad = np.asarray(
                [result.case.group == "broad_born" for result in broad_results],
                dtype=bool,
            )
            discrimination.append(
                {
                    "metric": metric,
                    "auc_broad_vs_non_broad": _rank_auc(all_values, broad),
                    "auc_born_vs_nonborn_within_broad": _rank_auc(
                        broad_values, born_within_broad
                    ),
                }
            )

        correlations: list[dict[str, Any]] = []
        broad_results = [
            result
            for result in self.results
            if result.case.group != "non_broad"
        ]
        for metric, _ in ACTIVATION_METRICS:
            all_values = np.asarray(
                [self._value(result, metric) for result in self.results],
                dtype=float,
            )
            alpha = np.asarray(
                [result.case.power_law_alpha for result in self.results],
                dtype=float,
            )
            broad_values = np.asarray(
                [self._value(result, metric) for result in broad_results],
                dtype=float,
            )
            born_score = np.asarray(
                [result.case.born_score for result in broad_results],
                dtype=float,
            )
            alpha_test = spearmanr(all_values, alpha)
            born_test = spearmanr(broad_values, born_score)
            correlations.append(
                {
                    "metric": metric,
                    "spearman_rho_with_alpha": float(alpha_test.statistic),
                    "p_value_with_alpha": float(alpha_test.pvalue),
                    "spearman_rho_with_S_born_within_broad": float(
                        born_test.statistic
                    ),
                    "p_value_with_S_born_within_broad": float(
                        born_test.pvalue
                    ),
                }
            )

        return {
            "group_counts": {
                group: int(group_summary[group]["count"]) for group in GROUP_ORDER
            },
            "group_summary": group_summary,
            "omnibus_tests": omnibus,
            "pairwise_tests": pairwise,
            "discrimination": discrimination,
            "correlations": correlations,
        }


def _summary_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in GROUP_ORDER:
        entry = summary["group_summary"][group]
        row: dict[str, Any] = {
            "group": group,
            "label": entry["label"],
            "count": entry["count"],
        }
        for metric, _ in ALL_METRICS:
            for statistic, value in entry["metrics"][metric].items():
                row[f"{metric}_{statistic}"] = value
        rows.append(row)
    return rows


def _plot_group_distributions(
    results: Sequence[CaseResult], output: Path
) -> None:
    selected_metrics = (
        ("degenerate_state_fraction", r"degenerate-state fraction $f_{\rm deg}$"),
        ("maximum_multiplicity", r"maximum multiplicity $m_{\max}$"),
        ("degenerate_pair_fraction", r"degenerate-pair fraction $F_{\rm pair}$"),
        ("distinct_energy_fraction", r"distinct-energy fraction $N_E/D$"),
    )
    figure, axes = plt.subplots(2, 2, figsize=(12.2, 7.3), constrained_layout=True)
    positions = np.arange(1, len(GROUP_ORDER) + 1)
    for axis, (metric, label) in zip(axes.flat, selected_metrics, strict=True):
        arrays = [
            np.asarray(
                [
                    float(getattr(result, metric))
                    for result in results
                    if result.case.group == group
                ],
                dtype=float,
            )
            for group in GROUP_ORDER
        ]
        violin = axis.violinplot(
            arrays,
            positions=positions,
            widths=0.82,
            showmeans=False,
            showmedians=False,
            showextrema=False,
        )
        for body, group in zip(violin["bodies"], GROUP_ORDER, strict=True):
            body.set_facecolor(GROUP_COLORS[group])
            body.set_edgecolor("none")
            body.set_alpha(0.33)
        boxes = axis.boxplot(
            arrays,
            positions=positions,
            widths=0.36,
            patch_artist=True,
            showfliers=False,
            medianprops={"color": "black", "linewidth": 1.5},
            whiskerprops={"color": "0.35"},
            capprops={"color": "0.35"},
        )
        for patch, group in zip(boxes["boxes"], GROUP_ORDER, strict=True):
            patch.set_facecolor(GROUP_COLORS[group])
            patch.set_alpha(0.70)
        axis.set_xticks(
            positions,
            ("broad\nBorn", "broad\nnon-Born", "non-broad"),
        )
        axis.set_ylabel(label)
        axis.grid(axis="y", alpha=0.22)
        if metric == "degenerate_pair_fraction":
            axis.set_yscale("log")
    figure.suptitle(
        "Raw detector degeneracy overlaps strongly across the three dynamical groups",
        fontsize=15,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def _plot_aggregate_profiles(
    results: Sequence[CaseResult], output: Path
) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12.2, 4.5), constrained_layout=True)
    for group in GROUP_ORDER:
        counter: Counter[int] = Counter()
        for result in results:
            if result.case.group == group:
                counter.update(dict(result.multiplicity_counts))
        multiplicities = np.asarray(sorted(counter), dtype=int)
        subspaces = np.asarray([counter[value] for value in multiplicities], dtype=float)
        subspace_probability = subspaces / np.sum(subspaces)
        state_probability = multiplicities * subspaces
        state_probability /= np.sum(state_probability)
        axes[0].plot(
            multiplicities,
            subspace_probability,
            "o-",
            ms=4,
            lw=1.5,
            color=GROUP_COLORS[group],
            label=GROUP_PLAIN[group],
        )
        axes[1].plot(
            multiplicities,
            state_probability,
            "o-",
            ms=4,
            lw=1.5,
            color=GROUP_COLORS[group],
            label=GROUP_PLAIN[group],
        )
    axes[0].set(
        xlabel="multiplicity $m$",
        ylabel="fraction of energy subspaces",
        title="Subspace-weighted multiplicity profile",
    )
    axes[1].set(
        xlabel="multiplicity $m$",
        ylabel="fraction of detector states",
        title="State-weighted multiplicity profile",
    )
    for axis in axes:
        axis.set_yscale("log")
        axis.grid(alpha=0.22, which="both")
    axes[0].legend(fontsize=8.4, frameon=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def _rank_bins(
    results: Sequence[CaseResult], metric: str, bins: int = 5
) -> list[list[CaseResult]]:
    ordered = sorted(results, key=lambda result: float(getattr(result, metric)))
    return [
        list(chunk)
        for chunk in np.array_split(np.asarray(ordered, dtype=object), bins)
        if len(chunk)
    ]


def _plot_binned_rates(results: Sequence[CaseResult], output: Path) -> None:
    metrics = (
        ("degenerate_state_fraction", r"$f_{\rm deg}$"),
        ("maximum_multiplicity", r"$m_{\max}$"),
        ("degenerate_pair_fraction", r"$F_{\rm pair}$"),
    )
    figure, axes = plt.subplots(1, 3, figsize=(13.2, 4.2), constrained_layout=True)
    for axis, (metric, label) in zip(axes, metrics, strict=True):
        chunks = _rank_bins(results, metric)
        x = [
            float(np.median([float(getattr(result, metric)) for result in chunk]))
            for chunk in chunks
        ]
        broad_rate = [
            float(np.mean([result.case.group != "non_broad" for result in chunk]))
            for chunk in chunks
        ]
        born_rate = []
        for chunk in chunks:
            broad = [
                result
                for result in chunk
                if result.case.group != "non_broad"
            ]
            born_rate.append(
                float(
                    np.mean(
                        [result.case.group == "broad_born" for result in broad]
                    )
                )
                if broad
                else float("nan")
            )
        axis.plot(
            x,
            broad_rate,
            "o-",
            color="#7c3aed",
            label="broad fraction",
        )
        axis.plot(
            x,
            born_rate,
            "s-",
            color="#198754",
            label="Born-like fraction within broad",
        )
        axis.set(
            xlabel=f"rank-bin median {label}",
            ylabel="fraction",
            ylim=(-0.03, 1.03),
        )
        axis.grid(alpha=0.22)
        if metric == "degenerate_pair_fraction":
            axis.set_xscale("log")
    axes[0].legend(frameon=False, fontsize=8.3)
    figure.suptitle(
        "Outcome rates across equal-count bins of raw degeneracy extent",
        fontsize=14,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def _metric_value(result: CaseResult, metric: str) -> float:
    if hasattr(result, metric):
        return float(getattr(result, metric))
    return float(getattr(result.case, metric))


def _plot_activation_distributions(
    results: Sequence[CaseResult], output: Path
) -> None:
    selected = (
        ("exact_active_weight_fraction", r"$\log_{10}(D_{\rm act}+10^{-14})$", True),
        ("weight_fraction_gap_le_1em6", r"$\log_{10}(W_{|\Delta E|\leq10^{-6}}+10^{-14})$", True),
        ("weight_fraction_gap_le_1em4", r"$\log_{10}(W_{|\Delta E|\leq10^{-4}}+10^{-14})$", True),
        ("finite_time_kernel_power_fraction", r"$\log_{10}(F_t+10^{-14})$", True),
        ("active_degenerate_state_fraction", r"active degenerate-state fraction", False),
        (
            "finite_time_transition_participation_fraction",
            r"finite-time transition participation",
            False,
        ),
    )
    figure, axes = plt.subplots(2, 3, figsize=(13.0, 7.1), constrained_layout=True)
    positions = np.arange(1, 4)
    for axis, (metric, label, log_transform) in zip(
        axes.flat, selected, strict=True
    ):
        arrays = []
        for group in GROUP_ORDER:
            values = np.asarray(
                [
                    _metric_value(result, metric)
                    for result in results
                    if result.case.group == group
                ],
                dtype=float,
            )
            arrays.append(
                np.log10(values + 1.0e-14) if log_transform else values
            )
        violin = axis.violinplot(
            arrays,
            positions=positions,
            widths=0.82,
            showextrema=False,
            showmedians=False,
        )
        for body, group in zip(violin["bodies"], GROUP_ORDER, strict=True):
            body.set_facecolor(GROUP_COLORS[group])
            body.set_edgecolor("none")
            body.set_alpha(0.32)
        boxes = axis.boxplot(
            arrays,
            positions=positions,
            widths=0.34,
            patch_artist=True,
            showfliers=False,
            medianprops={"color": "black", "linewidth": 1.5},
        )
        for patch, group in zip(boxes["boxes"], GROUP_ORDER, strict=True):
            patch.set_facecolor(GROUP_COLORS[group])
            patch.set_alpha(0.72)
        axis.set_xticks(
            positions, ("broad\nBorn", "broad\nnon-Born", "non-broad")
        )
        axis.set_ylabel(label)
        axis.grid(axis="y", alpha=0.22)
    figure.suptitle(
        r"How $V_{ab}$ activates exact and finite-time near-degenerate channels",
        fontsize=15,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def _plot_activation_statistics(
    summary: dict[str, Any], output: Path
) -> None:
    labels = [label for _, label in ACTIVATION_METRICS]
    discrimination = {
        row["metric"]: row for row in summary["discrimination"]
    }
    correlations = {row["metric"]: row for row in summary["correlations"]}
    broad_auc = np.asarray(
        [
            discrimination[metric]["auc_broad_vs_non_broad"]
            for metric, _ in ACTIVATION_METRICS
        ]
    )
    born_auc = np.asarray(
        [
            discrimination[metric]["auc_born_vs_nonborn_within_broad"]
            for metric, _ in ACTIVATION_METRICS
        ]
    )
    alpha_rho = np.asarray(
        [
            correlations[metric]["spearman_rho_with_alpha"]
            for metric, _ in ACTIVATION_METRICS
        ]
    )
    born_rho = np.asarray(
        [
            correlations[metric]["spearman_rho_with_S_born_within_broad"]
            for metric, _ in ACTIVATION_METRICS
        ]
    )
    y = np.arange(len(labels))
    figure, axes = plt.subplots(1, 2, figsize=(13.0, 6.2), constrained_layout=True)
    axes[0].barh(y - 0.18, broad_auc, height=0.34, color="#7c3aed", label="broad vs non-broad")
    axes[0].barh(y + 0.18, born_auc, height=0.34, color="#198754", label="Born vs non-Born within broad")
    axes[0].axvline(0.5, color="black", linestyle="--", linewidth=1.0)
    axes[0].set(xlim=(0.0, 1.0), xlabel="rank AUC (0.5 = no separation)")
    axes[0].legend(frameon=False, fontsize=8.5)
    axes[1].barh(y - 0.18, alpha_rho, height=0.34, color="#7c3aed", label=r"with $\alpha$")
    axes[1].barh(y + 0.18, born_rho, height=0.34, color="#198754", label=r"with $S_{\rm Born}$ within broad")
    axes[1].axvline(0.0, color="black", linestyle="--", linewidth=1.0)
    axes[1].set(xlim=(-1.0, 1.0), xlabel="Spearman rank correlation")
    axes[1].legend(frameon=False, fontsize=8.5)
    for axis in axes:
        axis.set_yticks(y, labels, fontsize=8.2)
        axis.invert_yaxis()
        axis.grid(axis="x", alpha=0.20)
    figure.suptitle(
        "Activation predicts broadness far better than Born similarity",
        fontsize=15,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def _plot_gap_window_scan(
    results: Sequence[CaseResult], output: Path
) -> None:
    windows = np.asarray([1.0e-9, 1.0e-6, 1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1])
    metrics = (
        "exact_active_weight_fraction",
        "weight_fraction_gap_le_1em6",
        "weight_fraction_gap_le_1em5",
        "weight_fraction_gap_le_1em4",
        "weight_fraction_gap_le_1em3",
        "weight_fraction_gap_le_1em2",
        "weight_fraction_gap_le_1em1",
    )
    broad = np.asarray(
        [result.case.group != "non_broad" for result in results], dtype=bool
    )
    alpha = np.asarray(
        [result.case.power_law_alpha for result in results], dtype=float
    )
    broad_results = [result for result in results if result.case.group != "non_broad"]
    born = np.asarray(
        [result.case.group == "broad_born" for result in broad_results],
        dtype=bool,
    )
    born_score = np.asarray(
        [result.case.born_score for result in broad_results], dtype=float
    )
    broad_auc = []
    born_auc = []
    alpha_rho = []
    born_rho = []
    for metric in metrics:
        values = np.asarray(
            [_metric_value(result, metric) for result in results], dtype=float
        )
        broad_values = np.asarray(
            [_metric_value(result, metric) for result in broad_results],
            dtype=float,
        )
        broad_auc.append(_rank_auc(values, broad))
        born_auc.append(_rank_auc(broad_values, born))
        alpha_rho.append(float(spearmanr(values, alpha).statistic))
        born_rho.append(float(spearmanr(broad_values, born_score).statistic))
    figure, axes = plt.subplots(1, 2, figsize=(12.6, 4.5), constrained_layout=True)
    axes[0].semilogx(windows, broad_auc, "o-", color="#7c3aed", label="broad AUC")
    axes[0].semilogx(windows, born_auc, "s-", color="#198754", label="Born AUC within broad")
    axes[0].axhline(0.5, color="black", linestyle="--", linewidth=1.0)
    axes[0].set(ylabel="rank AUC", ylim=(0.0, 1.0))
    axes[1].semilogx(windows, alpha_rho, "o-", color="#7c3aed", label=r"$\rho$ with $\alpha$")
    axes[1].semilogx(windows, born_rho, "s-", color="#198754", label=r"$\rho$ with $S_{\rm Born}$")
    axes[1].axhline(0.0, color="black", linestyle="--", linewidth=1.0)
    axes[1].set(ylabel="Spearman correlation", ylim=(-1.0, 1.0))
    for axis in axes:
        axis.set_xlabel(r"energy-gap window $\epsilon$")
        axis.grid(alpha=0.22, which="both")
        axis.legend(frameon=False, fontsize=8.5)
    figure.suptitle(
        r"Exact-to-near-degenerate scan of cumulative $V_{ab}$ weight",
        fontsize=15,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def _fit_image(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = min(width / image.width, height / image.height)
    size = (
        max(1, int(round(image.width * scale))),
        max(1, int(round(image.height * scale))),
    )
    return image.resize(size, Image.Resampling.LANCZOS)


class ContactSheetRenderer:
    """Compose group-separated A4-landscape sheets with four equal plot boxes."""

    def __init__(
        self,
        output_root: Path,
        cases_per_page: int = 21,
        columns: int = 3,
    ) -> None:
        if cases_per_page % columns:
            raise ValueError("cases_per_page must be divisible by columns")
        self.output_root = output_root
        self.cases_per_page = cases_per_page
        self.columns = columns
        self.rows = cases_per_page // columns
        font_path = font_manager.findfont("DejaVu Sans")
        self.header_font = ImageFont.truetype(font_path, 24)
        self.title_font = ImageFont.truetype(font_path, 14)

    def _ordered(self, results: Sequence[CaseResult], group: str) -> list[CaseResult]:
        return sorted(
            (result for result in results if result.case.group == group),
            key=lambda result: (
                -result.degenerate_pair_fraction,
                -result.maximum_multiplicity,
                result.case.hz,
                result.case.j,
                result.case.jpm,
            ),
        )

    def render(self, results: Sequence[CaseResult]) -> list[dict[str, Any]]:
        sheets: list[dict[str, Any]] = []
        for group in GROUP_ORDER:
            sheet_root = self.output_root / "figures" / "contact_sheets" / group
            if sheet_root.is_dir():
                for stale in sheet_root.glob("page_*.png"):
                    stale.unlink()
            selected = self._ordered(results, group)
            for page_in_group, start in enumerate(
                range(0, len(selected), self.cases_per_page), start=1
            ):
                page_results = selected[start : start + self.cases_per_page]
                path = self._render_page(
                    group,
                    page_in_group,
                    start + 1,
                    len(selected),
                    page_results,
                )
                sheets.append(
                    {
                        "group": group,
                        "page_in_group": page_in_group,
                        "group_case_start": start + 1,
                        "group_case_stop": start + len(page_results),
                        "path": path,
                    }
                )
        return sheets

    def _render_page(
        self,
        group: str,
        page_in_group: int,
        group_start: int,
        group_total: int,
        page_results: Sequence[CaseResult],
    ) -> Path:
        width, height = 3508, 2480
        margin_x, margin_y, header_h = 24, 20, 44
        tile_w = (width - 2 * margin_x) // self.columns
        tile_h = (height - 2 * margin_y - header_h) // self.rows
        canvas = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(canvas)
        heading = (
            f"{GROUP_PLAIN[group]} - group cases "
            f"{group_start}-{group_start + len(page_results) - 1} of {group_total}; "
            "gap heatmap | V_ab heatmap | multiplicities | P(theta), P(pi-theta), R(theta)"
        )
        draw.text((margin_x, 4), heading, fill=GROUP_COLORS[group], font=self.header_font)

        for local_index, result in enumerate(page_results):
            row, column = divmod(local_index, self.columns)
            x0 = margin_x + column * tile_w
            y0 = margin_y + header_h + row * tile_h
            x1 = x0 + tile_w - 5
            y1 = y0 + tile_h - 5
            draw.rectangle((x0, y0, x1, y1), outline="#cbd5e1", width=2)
            case = result.case
            title = (
                f"#{case.ordinal} hz={case.hz:g},J={case.j:g},Jpm={case.jpm:g}; "
                f"S_B={case.born_score:.3f},alpha={case.power_law_alpha:.3f}; "
                f"mmax={result.maximum_multiplicity},Fpair={result.degenerate_pair_fraction:.3g}"
            )
            draw.text((x0 + 5, y0 + 3), title, fill="#111827", font=self.title_font)

            top = y0 + 25
            usable_h = tile_h - 32
            gap = 4
            box_w = (tile_w - 5 * gap) // 4
            specifications = (
                case.heatmap_path,
                case.vab_plot_path,
                case.multiplicity_plot_path,
                case.diagnostic_path,
            )
            x = x0 + gap
            for source_path in specifications:
                draw.rectangle(
                    (x, top, x + box_w - 1, top + usable_h - 1),
                    outline="#94a3b8",
                    width=2,
                )
                with Image.open(source_path) as source:
                    fitted = _fit_image(
                        source.convert("RGB"), box_w - 6, usable_h - 6
                    )
                paste_x = x + 3 + (box_w - 6 - fitted.width) // 2
                paste_y = top + 3 + (usable_h - 6 - fitted.height) // 2
                canvas.paste(fitted, (paste_x, paste_y))
                x += box_w + gap

        sheet_root = self.output_root / "figures" / "contact_sheets" / group
        sheet_root.mkdir(parents=True, exist_ok=True)
        path = sheet_root / (
            f"page_{page_in_group:02d}_group_cases_{group_start:03d}_"
            f"{group_start + len(page_results) - 1:03d}.png"
        )
        canvas.save(path, format="PNG", compress_level=6, dpi=(300, 300))
        return path


def _tex_path(path: str | Path) -> str:
    return Path(
        os.path.relpath(Path(path).resolve(), DEFAULT_OUTPUT.resolve())
    ).as_posix()


def _fmt_interval(statistics: dict[str, float], digits: int = 3) -> str:
    return (
        f"{statistics['median']:.{digits}g} "
        f"[{statistics['q1']:.{digits}g}, {statistics['q3']:.{digits}g}]"
    )


class LatexReportWriter:
    """Write the activation analysis followed by every group contact sheet."""

    def __init__(
        self,
        output_path: Path,
        policy: ClassificationPolicy,
    ) -> None:
        self.output_path = output_path
        self.policy = policy

    @staticmethod
    def _discrimination(
        summary: dict[str, Any], metric: str
    ) -> dict[str, Any]:
        return next(
            row
            for row in summary["discrimination"]
            if row["metric"] == metric
        )

    @staticmethod
    def _pairwise(
        summary: dict[str, Any],
        metric: str,
        group_a: str,
        group_b: str,
    ) -> dict[str, Any]:
        return next(
            row
            for row in summary["pairwise_tests"]
            if row["metric"] == metric
            and row["group_a"] == group_a
            and row["group_b"] == group_b
        )

    def write(
        self,
        results: Sequence[CaseResult],
        summary: dict[str, Any],
        analysis_figures: dict[str, Path],
        sheets: Sequence[dict[str, Any]],
    ) -> None:
        counts = summary["group_counts"]
        group_summary = summary["group_summary"]
        mmax_born = group_summary["broad_born"]["metrics"]["maximum_multiplicity"]
        mmax_nonborn = group_summary["broad_nonborn"]["metrics"]["maximum_multiplicity"]
        fdeg_born = group_summary["broad_born"]["metrics"]["degenerate_state_fraction"]
        fdeg_nonborn = group_summary["broad_nonborn"]["metrics"]["degenerate_state_fraction"]
        broad_auc_pair = self._discrimination(
            summary, "degenerate_pair_fraction"
        )["auc_broad_vs_non_broad"]
        born_auc_pair = self._discrimination(
            summary, "degenerate_pair_fraction"
        )["auc_born_vs_nonborn_within_broad"]
        born_mmax_test = self._pairwise(
            summary,
            "maximum_multiplicity",
            "broad_born",
            "broad_nonborn",
        )
        exact_discrimination = self._discrimination(
            summary, "exact_active_weight_fraction"
        )
        kernel_discrimination = self._discrimination(
            summary, "finite_time_kernel_power_fraction"
        )
        correlations = {
            row["metric"]: row for row in summary["correlations"]
        }
        exact_correlation = correlations["exact_active_weight_fraction"]
        kernel_correlation = correlations[
            "finite_time_kernel_power_fraction"
        ]
        exact_active_counts = {
            group: sum(
                result.case.group == group
                and result.case.exact_active_weight_fraction > 1.0e-12
                for result in results
            )
            for group in GROUP_ORDER
        }

        lines = [
            r"\documentclass[10pt]{article}",
            r"\usepackage[a4paper,landscape,margin=0.28in,headheight=13pt,headsep=5pt,footskip=13pt]{geometry}",
            r"\usepackage{amsmath,amssymb,graphicx,xcolor,microtype,fancyhdr,booktabs,hyperref}",
            r"\hypersetup{colorlinks=true,linkcolor=blue!55!black,urlcolor=blue!55!black}",
            r"\setlength{\parindent}{0pt}",
            r"\setlength{\parskip}{0.45em}",
            r"\pagestyle{fancy}",
            r"\fancyhf{}",
            r"\fancyhead[L]{\footnotesize Detector spectrum and $V_{ab}$ activation versus broad/Born behavior}",
            r"\fancyhead[R]{\footnotesize $N_D=8$ spectra; $N=14$, $t=10^6$ dynamics}",
            r"\cfoot{\footnotesize\thepage}",
            r"\begin{document}",
            r"\begin{center}",
            r"{\LARGE\bfseries Detector spectrum and $V_{ab}$ activation across all 880 cases}\\[0.35em]",
            r"{\large Broadness of $P(\theta)$ and Born similarity of $R(\theta)$}\\[0.35em]",
            r"{\small 28 July 2026}",
            r"\end{center}",
            r"\textbf{System and observables.} The detector Hamiltonian is",
            (
                r"\[H_D=h_z\sum_{i=1}^{N_D}\sigma_i^z"
                r"+J\sum_{i=1}^{N_D}\sigma_i^z\sigma_{i+1}^z"
                r"+J_{\pm}\sum_{i=1}^{N_D}(\sigma_i^+\sigma_{i+1}^-"
                r"+\sigma_i^-\sigma_{i+1}^+),\]"
            ),
            (
                r"with periodic boundary conditions and $N_D=8$ for the spectral "
                r"comparison. The already computed dynamics use $N=14$, $t=10^6$, "
                r"$h_{z0}=0$, and collective $J_x=0.01$ (edge coefficient "
                r"$J_x/\sqrt N$). The minus-log heatmap is "
                r"$-\log_{10}\max(|E_a-E_b|/(E_{\max}-E_{\min}),10^{-12})$, "
                r"with the trivial diagonal blank."
            ),
            (
                r"The qubit couples through $X_0\otimes V$, "
                r"$V=\sum_i\sigma_i^x$, and "
                r"$V_{ab}=\langle E_a|V|E_b\rangle$. Each atlas tile shows "
                r"$\log_{10}(|V_{ab}|^2/\mathrm{Tr}\,V^2)$ in the solver-produced "
                r"energy eigenbasis, using the same color limits in every case."
            ),
            r"\textbf{Operational three-way split.} A case is called broad when the periodic power-law fit is resolved "
            + (
                rf"($D_{{\rm JS}}\le {self.policy.maximum_power_law_js:g}$, "
                rf"angular coverage $\ge {self.policy.minimum_angular_coverage:g}$, "
                rf"fit span $\ge {self.policy.minimum_power_law_span:g}$ decade) "
                rf"and $\alpha\le {self.policy.maximum_broad_alpha:g}$."
            ),
            (
                rf" It is Born-like when $S_{{\rm Born}}\ge "
                rf"{self.policy.minimum_born_score:g}$, RMSE $\le "
                rf"{self.policy.maximum_born_rmse:g}$, and coverage $\ge "
                rf"{self.policy.minimum_angular_coverage:g}$. These are exactly the "
                r"original registered threshold and safeguards from the "
                r"preceding activation study."
            ),
            r"\begin{center}",
            r"\renewcommand{\arraystretch}{1.15}",
            r"\begin{tabular}{lrrl}",
            r"\toprule Group & Count & Fraction & Definition\\\midrule",
            (
                rf"Broad, Born-like & {counts['broad_born']} & "
                rf"{100*counts['broad_born']/len(results):.1f}\% & broad and Born-like\\"
            ),
            (
                rf"Broad, non-Born & {counts['broad_nonborn']} & "
                rf"{100*counts['broad_nonborn']/len(results):.1f}\% & broad and not Born-like\\"
            ),
            (
                rf"Non-broad & {counts['non_broad']} & "
                rf"{100*counts['non_broad']/len(results):.1f}\% & all cases failing the broad gate\\"
            ),
            r"\bottomrule\end{tabular}",
            r"\end{center}",
            r"\textbf{Degeneracy convention.} Sorted eigenvalues belong to one subspace when "
            r"$|E_a-E_b|\le10^{-9}$. If its dimension is $m_g$, the case plot shows "
            r"the number of energy subspaces at each $m_g$. We summarize extent by "
            r"$f_{\rm deg}=D^{-1}\sum_{m_g>1}m_g$, $m_{\max}=\max_gm_g$, and",
            r"\[F_{\rm pair}=\frac{\sum_gm_g(m_g-1)}{D(D-1)},\]",
            r"the probability that two distinct uniformly sampled detector eigenstates lie in the same degenerate subspace.",
            r"\textbf{Activation measures.} Individual entries inside an exactly degenerate block depend on the arbitrary eigenbasis returned by the solver. The quantitative analysis therefore uses basis-invariant projector-block weights. Exact activation is",
            r"\[D_{\rm act}=\frac{\sum_g\|P_gVP_g\|_F^2}{\|V\|_F^2},\]",
            r"where $P_g$ projects onto a detector energy subspace. Near-degenerate activation in a window $\epsilon$ is the analogous cumulative weight over pairs with $|E_g-E_h|\le\epsilon$. At finite time $t$, the physically resolved resonant fraction is",
            r"\[F_t=\frac{\sum_{g,h}\|P_gVP_h\|_F^2\,\mathrm{sinc}^2[(E_g-E_h)t/2]}{\sum_{g,h}\|P_gVP_h\|_F^2}.\]",
            r"\vfill",
            r"\textit{All 880 original gap heatmaps and $P/R$ diagnostics are reused. The $N_D=8$ spectra were fully diagonalized to generate the new $V_{ab}$ heatmaps and validate the projector-block analysis.}",
            r"\clearpage",
            r"\section*{$V_{ab}$ activation: exact, near-degenerate, and finite-time channels}",
            (
                rf"\includegraphics[width=\textwidth,height=0.70\textheight,"
                rf"keepaspectratio]{{{_tex_path(analysis_figures['activation_distributions'])}}}"
            ),
            r"\vspace{0.4em}",
            (
                r"\small Exact activation alone separates broad from non-broad "
                rf"with rank AUC {exact_discrimination['auc_broad_vs_non_broad']:.3f}; "
                r"the finite-time resonant fraction gives AUC "
                rf"{kernel_discrimination['auc_broad_vs_non_broad']:.3f}. "
                r"The latter correlates with the fitted tail exponent as "
                rf"$\rho={kernel_correlation['spearman_rho_with_alpha']:.3f}$ "
                r"(smaller $\alpha$ means broader tails). Within already broad cases, "
                r"the corresponding AUCs for Born-like versus non-Born are "
                rf"{exact_discrimination['auc_born_vs_nonborn_within_broad']:.3f} "
                rf"and {kernel_discrimination['auc_born_vs_nonborn_within_broad']:.3f}; "
                r"their correlations with $S_{\rm Born}$ are "
                rf"{exact_correlation['spearman_rho_with_S_born_within_broad']:.3f} "
                rf"and {kernel_correlation['spearman_rho_with_S_born_within_broad']:.3f}."
            ),
            (
                r" Only "
                rf"{exact_active_counts['broad_born']}/{counts['broad_born']} "
                r"broad/Born cases and "
                rf"{exact_active_counts['broad_nonborn']}/{counts['broad_nonborn']} "
                r"broad/non-Born cases have $D_{\rm act}>10^{-12}$, while "
                rf"{exact_active_counts['non_broad']}/{counts['non_broad']} "
                r"non-broad cases do. Exact activation is therefore neither "
                r"necessary nor sufficient for broadness and is not the Born selector."
            ),
            r"\clearpage",
            r"\section*{Discrimination and the relevant energy-resolution scale}",
            (
                rf"\includegraphics[width=0.55\textwidth,height=0.72\textheight,"
                rf"keepaspectratio]{{{_tex_path(analysis_figures['activation_statistics'])}}}"
                r"\hfill"
                rf"\includegraphics[width=0.43\textwidth,height=0.72\textheight,"
                rf"keepaspectratio]{{{_tex_path(analysis_figures['window_scan'])}}}"
            ),
            r"\vspace{0.35em}",
            r"\small\textbf{Reading the scale scan.} Exact degeneracy is the leftmost point. Moving right admits progressively less resonant transitions. Broadness is most strongly associated with coupling weight that survives the finite-time energy filter, rather than with an arbitrary wide energy window. The heatmaps expose where the solver-basis entries lie; the plotted scalar weights are invariant under rotations inside degenerate eigenspaces.",
            r"\begin{center}\fcolorbox{blue!55!black}{blue!4}{\begin{minipage}{0.92\textwidth}\small",
            r"\textbf{Main conclusion.} Degenerate or unresolved near-degenerate detector levels are only available resonant channels. Broad $P(\theta)$ occurs when $V$ actually carries appreciable, sufficiently distributed weight through those channels. This activation is strongly favorable and highly predictive, but it is not an iff condition at finite size because near-degenerate channels contribute and some exactly activated blocks remain dynamically ineffective. Born-like $R(\theta)$ is a separate conditional-branch balance property: after conditioning on broadness, the exact/near-degenerate activation measures have much weaker discriminatory power.",
            r"\end{minipage}}\end{center}",
            r"\clearpage",
            r"\section*{Group-level comparison of degeneracy extent}",
            (
                rf"\includegraphics[width=0.67\textwidth,height=0.70\textheight,"
                rf"keepaspectratio]{{{_tex_path(analysis_figures['distributions'])}}}"
                r"\hfill"
                r"\begin{minipage}[b]{0.30\textwidth}\small\raggedright"
            ),
            r"\textbf{Median [IQR] at $N_D=8$}\\[0.4em]",
            r"\renewcommand{\arraystretch}{1.12}",
            r"\resizebox{\linewidth}{!}{%",
            r"\begin{tabular}{@{}lccc@{}}\toprule",
            r"Group & $f_{\rm deg}$ & $m_{\max}$ & $F_{\rm pair}$\\\midrule",
        ]
        for group, short in (
            ("broad_born", "broad/Born"),
            ("broad_nonborn", "broad/non-Born"),
            ("non_broad", "non-broad"),
        ):
            metrics = group_summary[group]["metrics"]
            lines.append(
                rf"{short} & "
                rf"{_fmt_interval(metrics['degenerate_state_fraction'])} & "
                rf"{_fmt_interval(metrics['maximum_multiplicity'])} & "
                rf"{_fmt_interval(metrics['degenerate_pair_fraction'], 2)}\\"
            )
        lines.extend(
            [
                r"\bottomrule\end{tabular}}",
                r"\vspace{0.8em}",
                (
                    r"\textbf{Direct reading.} Broad and non-broad cases have "
                    r"strongly overlapping raw-degeneracy distributions. For "
                    rf"$F_{{\rm pair}}$, the rank AUC for broad versus non-broad is "
                    rf"{broad_auc_pair:.3f} (0.5 means no discrimination). "
                ),
                (
                    r"Within the broad subset, the Born-like group is shifted toward "
                    r"less extreme degeneracy: its $m_{\max}$ is "
                    rf"{_fmt_interval(mmax_born)} versus "
                    rf"{_fmt_interval(mmax_nonborn)} for broad/non-Born, and "
                    rf"$f_{{\rm deg}}$ is {_fmt_interval(fdeg_born)} versus "
                    rf"{_fmt_interval(fdeg_nonborn)}. The $m_{{\max}}$ comparison "
                    rf"has Holm-corrected $p={born_mmax_test['holm_p_value']:.2g}$ "
                    rf"and rank-biserial effect "
                    rf"{born_mmax_test['rank_biserial_a_minus_b']:.3f}."
                ),
                (
                    r"Even this shift is not a deterministic separator: the "
                    rf"$F_{{\rm pair}}$ AUC for Born-like versus non-Born within "
                    rf"broad cases is {born_auc_pair:.3f}, and the violins overlap."
                ),
                r"\end{minipage}",
                r"\clearpage",
                r"\section*{Multiplicity profiles, outcome rates, and conclusion}",
                (
                    rf"\includegraphics[width=0.48\textwidth,height=0.55\textheight,"
                    rf"keepaspectratio]{{{_tex_path(analysis_figures['profiles'])}}}"
                    r"\hfill"
                    rf"\includegraphics[width=0.49\textwidth,height=0.55\textheight,"
                    rf"keepaspectratio]{{{_tex_path(analysis_figures['rates'])}}}"
                ),
                r"\vspace{0.5em}",
                r"\begin{minipage}[t]{0.48\textwidth}\small",
                r"\textbf{What multiplicity does explain.} Large degenerate blocks raise the number of exactly equal-frequency channels available to perturbation theory. They are therefore a reservoir of potentially resonant transitions. This is visible in the state-weighted profile, where high-$m$ blocks contribute disproportionately even when they are rare as subspaces.",
                r"\end{minipage}\hfill",
                r"\begin{minipage}[t]{0.49\textwidth}\small",
                r"\textbf{What multiplicity does not explain.} Neither $f_{\rm deg}$, $m_{\max}$, nor $F_{\rm pair}$ alone decides whether $P(\theta)$ is broad. A degenerate block matters dynamically only when the qubit-detector coupling has non-negligible matrix weight inside it; finite-time near-resonances can broaden $P$ without exact degeneracy. Likewise, a Born-like $R(\theta)$ additionally requires reciprocal balance of the two conditional branches, which raw detector multiplicities do not encode.",
                r"\end{minipage}",
                r"\vspace{0.6em}",
                r"\begin{center}\fcolorbox{blue!55!black}{blue!4}{\begin{minipage}{0.91\textwidth}\small",
                r"\textbf{Conclusion.} Extensive detector degeneracy is neither necessary nor sufficient for broad $P(\theta)$. It is best viewed as available resonant capacity. The realized broadness is controlled by whether $V_{ab}$ activates that capacity (and by near-degenerate finite-time channels). Among already broad cases, very large multiplicities are mildly unfavorable to Born similarity, but the substantial overlap shows that multiplicity is not the missing Born criterion; branch reciprocity remains independent.",
                r"\end{minipage}}\end{center}",
            ]
        )

        for sheet in sheets:
            lines.append(r"\clearpage")
            lines.extend(
                [
                    r"\begin{center}",
                    (
                        rf"\includegraphics[width=\textwidth,height=0.92\textheight,"
                        rf"keepaspectratio]{{{_tex_path(sheet['path'])}}}"
                    ),
                    r"\end{center}",
                ]
            )
        lines.append(r"\end{document}")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--joined", type=Path, default=SOURCE_JOINED)
    parser.add_argument("--atlas-index", type=Path, default=SOURCE_ATLAS_INDEX)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tex", type=Path, default=DEFAULT_TEX)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--degeneracy-tolerance", type=float, default=1.0e-9)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    started = time.perf_counter()
    policy = ClassificationPolicy()
    repository = CaseRepository(args.joined, args.atlas_index, args.output, policy)
    cases = repository.load()
    if args.limit is not None:
        if args.limit < len(GROUP_ORDER):
            raise ValueError(
                f"--limit must be at least {len(GROUP_ORDER)} so every group is represented"
            )
        quotas = {
            group: args.limit // len(GROUP_ORDER) for group in GROUP_ORDER
        }
        for group in GROUP_ORDER[: args.limit % len(GROUP_ORDER)]:
            quotas[group] += 1
        cases = [
            case
            for group in GROUP_ORDER
            for case in [
                item for item in cases if item.group == group
            ][: quotas[group]]
        ]

    checkpoint_path = args.output / "data" / "case_index.csv"
    checkpoint = {} if args.force else _load_checkpoint(checkpoint_path)
    results: dict[str, CaseResult] = {
        case.key: replace(checkpoint[case.key], case=case)
        for case in cases
        if case.key in checkpoint
        and Path(checkpoint[case.key].case.multiplicity_plot_path).is_file()
        and Path(checkpoint[case.key].case.vab_plot_path).is_file()
    }
    pending = [case for case in cases if case.key not in results]
    print(
        f"[{datetime.now().astimezone().isoformat()}] cases={len(cases)} "
        f"reused={len(results)} pending={len(pending)} workers={args.workers}",
        flush=True,
    )

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                _analyze_case,
                case,
                args.degeneracy_tolerance,
                args.force,
            ): case
            for case in pending
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            case = futures[future]
            result = future.result()
            results[case.key] = result
            ordered_checkpoint = [
                results[item.key] for item in cases if item.key in results
            ]
            _atomic_write_csv(
                checkpoint_path,
                [item.to_row() for item in ordered_checkpoint],
            )
            if completed == 1 or completed % 20 == 0 or completed == len(pending):
                print(
                    f"[{datetime.now().astimezone().isoformat()}] "
                    f"completed={completed}/{len(pending)} case={case.key}",
                    flush=True,
                )

    ordered_results = [results[case.key] for case in cases]
    _atomic_write_csv(
        checkpoint_path, [result.to_row() for result in ordered_results]
    )
    _atomic_write_csv(
        args.output / "data" / "multiplicity_distribution.csv",
        _multiplicity_rows(ordered_results),
    )

    analyzer = StatisticalAnalyzer(ordered_results)
    summary = analyzer.summarize()
    _atomic_write_csv(
        args.output / "data" / "group_summary.csv", _summary_rows(summary)
    )
    _atomic_write_csv(
        args.output / "data" / "pairwise_tests.csv",
        summary["pairwise_tests"],
    )
    _atomic_write_csv(
        args.output / "data" / "discrimination_auc.csv",
        summary["discrimination"],
    )
    _atomic_write_csv(
        args.output / "data" / "activation_correlations.csv",
        summary["correlations"],
    )
    _write_json(args.output / "data" / "analysis_summary.json", summary)

    analysis_root = args.output / "figures" / "analysis"
    analysis_figures = {
        "distributions": analysis_root / "degeneracy_group_distributions.png",
        "profiles": analysis_root / "aggregate_multiplicity_profiles.png",
        "rates": analysis_root / "degeneracy_binned_outcome_rates.png",
        "activation_distributions": analysis_root
        / "activation_group_distributions.png",
        "activation_statistics": analysis_root
        / "activation_discrimination_and_correlations.png",
        "window_scan": analysis_root / "activation_gap_window_scan.png",
    }
    _plot_group_distributions(
        ordered_results, analysis_figures["distributions"]
    )
    _plot_aggregate_profiles(ordered_results, analysis_figures["profiles"])
    _plot_binned_rates(ordered_results, analysis_figures["rates"])
    _plot_activation_distributions(
        ordered_results, analysis_figures["activation_distributions"]
    )
    _plot_activation_statistics(
        summary, analysis_figures["activation_statistics"]
    )
    _plot_gap_window_scan(ordered_results, analysis_figures["window_scan"])

    renderer = ContactSheetRenderer(args.output)
    sheets = renderer.render(ordered_results)
    writer = LatexReportWriter(args.tex, policy)
    writer.write(
        ordered_results,
        summary,
        analysis_figures,
        sheets,
    )
    elapsed = time.perf_counter() - started
    manifest = {
        "created_at": datetime.now().astimezone().isoformat(),
        "case_count": len(ordered_results),
        "group_counts": summary["group_counts"],
        "detector_n": 8,
        "dynamics_n": 14,
        "evolution_time": 1.0e6,
        "degeneracy_tolerance": args.degeneracy_tolerance,
        "classification_policy": asdict(policy),
        "source_joined_metrics": _tex_path(args.joined),
        "source_atlas_index": _tex_path(args.atlas_index),
        "dynamics_recomputed": False,
        "detector_spectra_recomputed": True,
        "vab_heatmaps_generated": True,
        "vab_display": (
            "solver-basis log10(|V_ab|^2/Tr(V^2)), common limits [-12,0]"
        ),
        "basis_invariant_activation_metrics_reused": True,
        "multiplicity_definition": (
            "sorted eigenvalues are one group when their difference from the "
            "group's first eigenvalue is <= 1e-9"
        ),
        "degenerate_pair_fraction": (
            "sum_g m_g*(m_g-1)/(D*(D-1))"
        ),
        "contact_sheet_count": len(sheets),
        "expected_pdf_pages": 5 + len(sheets),
        "latex": _tex_path(args.tex),
        "elapsed_seconds": elapsed,
        "workers": args.workers,
        "validation_maxima": {
            "hamiltonian_hermiticity_error": max(
                result.hamiltonian_hermiticity_error
                for result in ordered_results
            ),
            "coupling_hermiticity_error": max(
                result.coupling_hermiticity_error
                for result in ordered_results
            ),
            "eigenvector_orthonormality_error": max(
                result.eigenvector_orthonormality_error
                for result in ordered_results
            ),
            "maximum_relative_eigenpair_residual": max(
                result.maximum_relative_eigenpair_residual
                for result in ordered_results
            ),
            "coupling_transform_relative_norm_error": max(
                result.coupling_transform_relative_norm_error
                for result in ordered_results
            ),
        },
        "contact_sheets": [
            {
                **{key: value for key, value in sheet.items() if key != "path"},
                "path": _tex_path(sheet["path"]),
            }
            for sheet in sheets
        ],
    }
    _write_json(args.output / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
