#!/usr/bin/env python3.11
"""Compute activation-resolved P(theta) and R(theta) for selected rings.

The calculation checkpoints every momentum after processing its relative
eigenvectors.  Detector activation eigenchannels are recomputed on restart,
but completed expensive full-Hamiltonian momentum blocks are reused.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, fields, replace
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
import traceback
from typing import Any
import warnings

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))
warnings.filterwarnings("ignore", message=r".*font family.*not found.*")
warnings.filterwarnings("ignore", message=r".*Glyph.*missing from font.*")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from core.activation_resolved_projective import (  # noqa: E402
    ActivationPartition,
    MomentumProjectiveComponents,
    RingActivationParameters,
    WeightedAngularFits,
    WeightedProjectiveDiagnostics,
    activation_quantile_partition,
    all_detector_activation_channels,
    fit_weighted_angular_distributions,
    momentum_projective_components,
    pooled_component_diagnostics,
    validate_component_reconstruction,
)
from core.sobol_coupling_scan import (  # noqa: E402
    _atomic_json,
    _atomic_npz,
    _peak_rss_mb,
    _sha256,
    timestamp,
)


DEFAULT_CONFIG = ROOT / "configs" / "three_ring_activation_resolved.json"
DEFAULT_OUTPUT = ROOT / "work" / "ring_activation_resolved_three_cases_N14_20260823"
BLUE = "#1f77b4"
RED = "#d95f5f"
PURPLE = "#6b3f7c"
MODEL_BLUE = "#2a80c9"
MODEL_ORANGE = "#ef8a00"
CLASS_COLORS = {"weak": "#4477aa", "intermediate": "#aa4499", "strong": "#cc6677"}


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _apply_parameter_overrides(
    parameters: RingActivationParameters,
    config_case: dict[str, Any],
) -> tuple[RingActivationParameters, dict[str, float]]:
    """Apply explicit, finite per-case parameter overrides.

    Overrides are recorded in both the case digest and output provenance. The
    helper rejects unknown names rather than ignoring a misspelled parameter.
    """

    raw = config_case.get("parameter_overrides", {})
    if not isinstance(raw, dict):
        raise ValueError("parameter_overrides must be a JSON object")
    allowed = {item.name for item in fields(RingActivationParameters)}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown parameter override(s): {sorted(unknown)}")
    overrides = {name: float(value) for name, value in raw.items()}
    if not all(math.isfinite(value) for value in overrides.values()):
        raise ValueError("all parameter overrides must be finite")
    if overrides.get("evolution_time", parameters.evolution_time) <= 0.0:
        raise ValueError("evolution_time must be positive")
    return replace(parameters, **overrides), overrides


def _load_case(config_case: dict[str, Any]) -> tuple[RingActivationParameters, dict[str, Any]]:
    source_dir = (ROOT / str(config_case["source_result"])).resolve()
    metadata_path = source_dir / "metadata.json"
    metrics_path = source_dir / "metrics.json"
    metadata = _read_json(metadata_path)
    metrics = _read_json(metrics_path)
    source = metadata["source"]
    parameters = RingActivationParameters(
        hz=float(source["hz"]),
        hz0=float(source["hz0"]),
        j=float(source["j"]),
        jpm=float(source["jpm"]),
        j2=float(source.get("j2", 0.0)),
        jpm2=float(source.get("jpm2", 0.0)),
        jx_unscaled=float(source["jx"]),
        evolution_time=float(source["evolution_time"]),
    )
    parameters, overrides = _apply_parameter_overrides(parameters, config_case)
    provenance = {
        "source_result": str(source_dir.relative_to(ROOT)),
        "source_metadata": str(metadata_path.relative_to(ROOT)),
        "source_metrics": str(metrics_path.relative_to(ROOT)),
        "source_case": source["source_case"],
        "source_N": int(metadata["target_N"]),
        "source_S_born": float(metrics["S_born"]),
        "source_RMSE": float(metrics["born_RMSE_occupied"]),
        "source_Jx_effective": float(metadata["Jx_effective"]),
        "parameter_overrides": overrides,
    }
    return parameters, provenance


def _case_digest(
    case: dict[str, Any],
    parameters: RingActivationParameters,
    detector_n: int,
    config: dict[str, Any],
) -> str:
    payload = {
        "case": case,
        "parameters": asdict(parameters),
        "detector_n": detector_n,
        "lower": config["activation_lower_quantile"],
        "upper": config["activation_upper_quantile"],
        "bins": config["bins"],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:20]


def _complete_valid(case_dir: Path, digest: str) -> bool:
    marker_path = case_dir / "COMPLETE.json"
    if not marker_path.is_file():
        return False
    try:
        marker = _read_json(marker_path)
        return (
            marker.get("case_digest") == digest
            and marker.get("status") == "complete"
            and all(
                (case_dir / name).is_file()
                and _sha256(case_dir / name) == expected
                for name, expected in marker["files"].items()
            )
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def _checkpoint_paths(case_dir: Path, momentum: int) -> tuple[Path, Path]:
    checkpoint_dir = case_dir / "momentum_checkpoints"
    return (
        checkpoint_dir / f"k_{momentum:02d}.npz",
        checkpoint_dir / f"k_{momentum:02d}.json",
    )


def _load_checkpoint(
    case_dir: Path,
    momentum: int,
    digest: str,
    partition: ActivationPartition,
) -> MomentumProjectiveComponents | None:
    archive_path, metadata_path = _checkpoint_paths(case_dir, momentum)
    if not archive_path.is_file() or not metadata_path.is_file():
        return None
    try:
        metadata = _read_json(metadata_path)
        if (
            metadata.get("case_digest") != digest
            or metadata.get("archive_sha256") != _sha256(archive_path)
            or metadata.get("partition_labels") != list(partition.labels)
            or not math.isclose(
                float(metadata["lower_threshold"]),
                partition.lower_threshold,
                rel_tol=1.0e-12,
                abs_tol=1.0e-15,
            )
            or not math.isclose(
                float(metadata["upper_threshold"]),
                partition.upper_threshold,
                rel_tol=1.0e-12,
                abs_tol=1.0e-15,
            )
        ):
            return None
        with np.load(archive_path, allow_pickle=False) as archive:
            return MomentumProjectiveComponents(
                momentum=momentum,
                eigenvalues=np.asarray(archive["eigenvalues"]),
                theta=np.asarray(archive["theta"]),
                class_weights=np.asarray(archive["class_weights"]),
                pencil_condition_number=float(archive["pencil_condition_number"]),
                eigenvector_condition_number=float(archive["eigenvector_condition_number"]),
                maximum_eigenpair_residual=float(archive["maximum_eigenpair_residual"]),
                maximum_weight_sum_error=float(archive["maximum_weight_sum_error"]),
                detector_basis_completeness_error=float(archive["detector_basis_completeness_error"]),
            )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _save_checkpoint(
    case_dir: Path,
    component: MomentumProjectiveComponents,
    digest: str,
    partition: ActivationPartition,
    runtime_seconds: float,
) -> None:
    archive_path, metadata_path = _checkpoint_paths(case_dir, component.momentum)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_npz(
        archive_path,
        eigenvalues=component.eigenvalues,
        theta=component.theta,
        class_weights=component.class_weights,
        pencil_condition_number=np.asarray(component.pencil_condition_number),
        eigenvector_condition_number=np.asarray(component.eigenvector_condition_number),
        maximum_eigenpair_residual=np.asarray(component.maximum_eigenpair_residual),
        maximum_weight_sum_error=np.asarray(component.maximum_weight_sum_error),
        detector_basis_completeness_error=np.asarray(component.detector_basis_completeness_error),
    )
    _atomic_json(
        metadata_path,
        {
            "case_digest": digest,
            "momentum": component.momentum,
            "partition_labels": list(partition.labels),
            "lower_threshold": partition.lower_threshold,
            "upper_threshold": partition.upper_threshold,
            "runtime_seconds": runtime_seconds,
            "root_count": int(component.theta.size),
            "archive_sha256": _sha256(archive_path),
            "completed": timestamp(),
        },
    )


def _diagnostic_payload(result: WeightedProjectiveDiagnostics) -> dict[str, Any]:
    return {
        "label": result.label,
        "total_weight": result.total_weight,
        "effective_root_count": result.effective_root_count,
        "S_born": result.similarity,
        "born_RMSE_occupied": result.rmse_occupied,
        "born_L1_occupied": result.l1_occupied,
        "occupied_fraction": result.occupied_fraction,
        "p_theta_integral": float(np.sum(result.p_theta * np.diff(result.edges))),
        "p_reflected_integral": float(
            np.sum(result.p_pi_minus_theta * np.diff(result.edges))
        ),
    }


def _fit_payload(fit: WeightedAngularFits) -> dict[str, Any]:
    return {
        "wrapped_gaussian": fit.wrapped_gaussian,
        "wrapped_cauchy": fit.wrapped_cauchy,
    }


def _plot_diagnostics(
    path: Path,
    case: dict[str, Any],
    parameters: RingActivationParameters,
    detector_n: int,
    diagnostics: tuple[WeightedProjectiveDiagnostics, ...],
    fits: tuple[WeightedAngularFits, ...],
    class_mass_fractions: dict[str, float],
) -> None:
    figure = plt.figure(figsize=(18.0, 8.2))
    outer = figure.add_gridspec(1, 4, wspace=0.22)
    for column, (result, fit) in enumerate(zip(diagnostics, fits, strict=True)):
        cell = outer[0, column].subgridspec(2, 1, height_ratios=(1.0, 0.92), hspace=0.08)
        ax_p = figure.add_subplot(cell[0, 0])
        ax_r = figure.add_subplot(cell[1, 0], sharex=ax_p)
        ax_p.stairs(result.p_theta, result.edges, color=BLUE, fill=True, alpha=0.18, linewidth=1.25)
        ax_p.stairs(result.p_pi_minus_theta, result.edges, color=RED, fill=True, alpha=0.13, linewidth=1.15)
        ax_p.plot(fit.grid, fit.wrapped_gaussian_density, color=MODEL_BLUE, linewidth=1.2)
        ax_p.plot(fit.grid, fit.wrapped_cauchy_density, color=MODEL_ORANGE, linestyle="--", linewidth=1.15)
        mask = result.occupied
        ax_r.plot(result.centers[mask], result.ratio[mask], "o-", color=PURPLE, markersize=2.3, linewidth=0.9)
        ax_r.plot(result.centers, result.born, "k--", linewidth=1.05)
        title = "global" if result.label == "global" else f"{result.label} activation"
        if result.label != "global":
            title += f" ({100.0 * class_mass_fractions[result.label]:.1f}% root weight)"
        ax_p.set_title(title, fontsize=11)
        ax_p.set_ylabel("density")
        ax_r.set_ylabel(r"$R(\theta)$")
        ax_r.set_xlabel(r"$\theta$")
        ax_p.set_xlim(0.0, np.pi)
        ax_p.set_ylim(bottom=0.0)
        ax_r.set_ylim(-0.04, 1.04)
        ax_r.set_xticks((0.0, np.pi / 2.0, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
        ax_p.tick_params(labelbottom=False)
        ax_p.grid(alpha=0.16)
        ax_r.grid(alpha=0.16)
        ax_r.text(
            0.04,
            0.08,
            rf"$S_{{\rm Born}}={result.similarity:.3f}$" + "\n"
            + rf"RMSE$={result.rmse_occupied:.3f}$" + "\n"
            + rf"$N_{{\rm eff}}={result.effective_root_count:.0f}$",
            transform=ax_r.transAxes,
            fontsize=8.5,
            va="bottom",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.0},
        )
    second = ""
    if parameters.j2 or parameters.jpm2:
        second = rf", $J_2={parameters.j2:.5g}$, $J_{{\pm2}}={parameters.jpm2:.5g}$"
    figure.suptitle(
        str(case["description"]) + "\n"
        + rf"activation-resolved projective diagnostics, $N_D={detector_n}$, "
        + rf"$h_z={parameters.hz:.5g}$, $h_{{z0}}={parameters.hz0:.5g}$, "
        + rf"$J={parameters.j:.5g}$, $J_{{\pm}}={parameters.jpm:.5g}${second}",
        fontsize=14,
        y=0.995,
    )
    handles = (
        Line2D([], [], color=BLUE, linewidth=5, alpha=0.35, label=r"$P(\theta)$"),
        Line2D([], [], color=RED, linewidth=5, alpha=0.30, label=r"$P(\pi-\theta)$"),
        Line2D([], [], color=MODEL_BLUE, label="wrapped Gaussian"),
        Line2D([], [], color=MODEL_ORANGE, linestyle="--", label="wrapped Cauchy"),
        Line2D([], [], color=PURPLE, marker="o", markersize=3, label=r"$R(\theta)$"),
        Line2D([], [], color="black", linestyle="--", label=r"$\cos^2(\theta/2)$"),
    )
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.91), ncol=6, frameon=False)
    figure.text(
        0.5,
        0.012,
        (
            "Activation classes are global 20% / 60% / 20% canonical detector-channel quantiles. "
            "Component histograms use each relative root's Hilbert-space projection weight."
        ),
        ha="center",
        fontsize=9,
    )
    figure.subplots_adjust(left=0.05, right=0.99, bottom=0.09, top=0.84)
    figure.savefig(path, dpi=190, bbox_inches="tight")
    plt.close(figure)


def _plot_activation_spectrum(
    path: Path,
    activation: tuple,
    partition: ActivationPartition,
) -> None:
    scores = np.concatenate([item.scores for item in activation])
    energies = np.concatenate([item.energies for item in activation])
    classes = partition.class_indices(scores)
    positive = scores[scores > 0.0]
    floor = max(float(np.min(positive)) * 0.1 if positive.size else 1.0e-300, 1.0e-300)
    log_score = np.log10(np.maximum(scores, floor))
    figure, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), constrained_layout=True)
    axes[0].hist(log_score, bins=70, color="#777777", alpha=0.82)
    for threshold, label in (
        (partition.lower_threshold, "20% threshold"),
        (partition.upper_threshold, "80% threshold"),
    ):
        axes[0].axvline(np.log10(max(threshold, floor)), linestyle="--", linewidth=1.2, label=label)
    axes[0].set(xlabel=r"$\log_{10} G_b(t)$", ylabel="activation-channel count")
    axes[0].legend(frameon=False)
    for index, label in enumerate(partition.labels):
        mask = classes == index
        axes[1].scatter(
            energies[mask],
            log_score[mask],
            s=4,
            alpha=0.35,
            color=CLASS_COLORS[label],
            label=f"{label} ({np.count_nonzero(mask)})",
        )
    axes[1].set(xlabel="detector energy", ylabel=r"$\log_{10} G_b(t)$")
    axes[1].legend(frameon=False, markerscale=2)
    for axis in axes:
        axis.grid(alpha=0.17)
    figure.savefig(path, dpi=190)
    plt.close(figure)


def run_case(
    config: dict[str, Any],
    case_index: int,
    detector_n: int,
    output_root: Path,
    *,
    resume: bool,
) -> dict[str, Any]:
    cases = config["cases"]
    if case_index < 0 or case_index >= len(cases):
        raise ValueError(f"case-index must be in 0..{len(cases) - 1}")
    case = cases[case_index]
    parameters, provenance = _load_case(case)
    digest = _case_digest(case, parameters, detector_n, config)
    case_dir = output_root / str(case["case_id"])
    if resume and _complete_valid(case_dir, digest):
        print(f"[{timestamp()}] {case['case_id']} N={detector_n} already complete", flush=True)
        return {
            "status": "resumed_complete",
            "case_id": case["case_id"],
            "case_dir": str(case_dir),
        }
    case_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    def progress(message: str) -> None:
        print(f"[{timestamp()}] case={case['case_id']} N={detector_n} {message}", flush=True)

    progress("stage=detector_activation start")
    activation_started = time.perf_counter()
    activation = all_detector_activation_channels(
        detector_n,
        parameters,
        progress=progress,
    )
    activation_seconds = time.perf_counter() - activation_started
    partition = activation_quantile_partition(
        activation,
        lower_quantile=float(config["activation_lower_quantile"]),
        upper_quantile=float(config["activation_upper_quantile"]),
    )
    progress(
        "stage=detector_activation finish "
        f"seconds={activation_seconds:.3f} counts={partition.channel_counts} "
        f"thresholds=({partition.lower_threshold:.6g},{partition.upper_threshold:.6g})"
    )
    _atomic_json(
        case_dir / "activation_partition.json",
        {
            **asdict(partition),
            "detector_channel_count": 2**detector_n,
            "effective_Jx": parameters.effective_jx(detector_n),
            "activation_definition": (
                "eigenvalues of the finite-time positive activation operator "
                "within each degenerate (N_up,k,E) detector subspace"
            ),
            "kernel": "0.5 * sum_sigma 4 sin^2[(DeltaE + sigma*2hz0)t/2]/(DeltaE + sigma*2hz0)^2",
        },
    )

    components: list[MomentumProjectiveComponents] = []
    momentum_times: list[float] = []
    for momentum, momentum_data in enumerate(activation):
        checkpoint = _load_checkpoint(case_dir, momentum, digest, partition) if resume else None
        if checkpoint is not None:
            progress(f"stage=relative_k k={momentum} status=checkpoint_reused")
            components.append(checkpoint)
            momentum_times.append(0.0)
            continue
        progress(f"stage=relative_k k={momentum} status=start")
        block_started = time.perf_counter()
        component = momentum_projective_components(
            detector_n,
            momentum_data,
            partition,
            parameters,
        )
        block_seconds = time.perf_counter() - block_started
        _save_checkpoint(case_dir, component, digest, partition, block_seconds)
        components.append(component)
        momentum_times.append(block_seconds)
        peak_rss = _peak_rss_mb()
        rss_text = "unavailable" if peak_rss is None else f"{peak_rss:.1f}"
        progress(
            f"stage=relative_k k={momentum} status=finish seconds={block_seconds:.3f} "
            f"roots={component.theta.size} weight_error={component.maximum_weight_sum_error:.3e} "
            f"residual={component.maximum_eigenpair_residual:.3e} rss_mb={rss_text}"
        )
        gc.collect()

    diagnostics = pooled_component_diagnostics(
        components,
        partition,
        bins=int(config["bins"]),
    )
    reconstruction = validate_component_reconstruction(diagnostics)
    theta = np.concatenate([item.theta for item in components])
    class_weights = np.concatenate([item.class_weights for item in components], axis=1)
    fit_weights = [np.ones(theta.size)] + [class_weights[index] for index in range(3)]
    fits = tuple(
        fit_weighted_angular_distributions(
            theta,
            weights,
            plot_grid=int(config["fit_grid"]),
            nmax=int(config["fit_harmonics"]),
            tolerance=float(config["fit_tolerance"]),
        )
        for weights in fit_weights
    )
    class_mass_fractions = {
        label: diagnostics[index + 1].total_weight / diagnostics[0].total_weight
        for index, label in enumerate(partition.labels)
    }
    diagnostics_path = case_dir / "activation_resolved_diagnostics.png"
    activation_path = case_dir / "activation_spectrum.png"
    _plot_diagnostics(
        diagnostics_path,
        case,
        parameters,
        detector_n,
        diagnostics,
        fits,
        class_mass_fractions,
    )
    _plot_activation_spectrum(activation_path, activation, partition)

    archive_payload: dict[str, np.ndarray] = {
        "theta": theta,
        "eigenvalues": np.concatenate([item.eigenvalues for item in components]),
        "class_weights": class_weights,
    }
    for result, fit in zip(diagnostics, fits, strict=True):
        prefix = result.label
        for name in (
            "edges",
            "centers",
            "p_theta",
            "p_pi_minus_theta",
            "ratio",
            "occupied",
            "born",
            "residual",
        ):
            archive_payload[f"{prefix}__{name}"] = np.asarray(getattr(result, name))
        archive_payload[f"{prefix}__fit_grid"] = fit.grid
        archive_payload[f"{prefix}__wg_density"] = fit.wrapped_gaussian_density
        archive_payload[f"{prefix}__wc_density"] = fit.wrapped_cauchy_density
    results_path = case_dir / "activation_resolved_results.npz"
    _atomic_npz(results_path, **archive_payload)
    metrics = {
        "schema_version": 1,
        "created": timestamp(),
        "case_id": case["case_id"],
        "description": case["description"],
        "detector_n": detector_n,
        "parameters": asdict(parameters),
        "Jx_effective": parameters.effective_jx(detector_n),
        "collective_scaling": "Jx_unscaled/sqrt(N), applied exactly once",
        "provenance": provenance,
        "partition": asdict(partition),
        "class_mass_fractions_in_root_ensemble": class_mass_fractions,
        "diagnostics": [_diagnostic_payload(item) for item in diagnostics],
        "fits": {
            result.label: _fit_payload(fit)
            for result, fit in zip(diagnostics, fits, strict=True)
        },
        "validation": {
            **reconstruction,
            "maximum_root_weight_sum_error": max(item.maximum_weight_sum_error for item in components),
            "maximum_detector_basis_completeness_error": max(item.detector_basis_completeness_error for item in components),
            "maximum_relative_eigenpair_residual": max(item.maximum_eigenpair_residual for item in components),
            "maximum_pencil_condition_number": max(item.pencil_condition_number for item in components),
            "maximum_relative_eigenvector_condition_number": max(item.eigenvector_condition_number for item in components),
            "minimum_activation_eigenvalue_before_clipping": min(item.minimum_activation_eigenvalue for item in activation),
            "maximum_activation_hermiticity_residual": max(item.maximum_activation_hermiticity_residual for item in activation),
        },
        "runtime": {
            "detector_activation_seconds": activation_seconds,
            "momentum_relative_seconds": momentum_times,
            "total_seconds": time.perf_counter() - started,
            "peak_rss_mb": _peak_rss_mb(),
            "python": sys.version,
            "platform": platform.platform(),
        },
        "interpretation": (
            "components are weighted projections of relative-root right eigenvectors, "
            "not independently conserved Hamiltonian sectors"
        ),
    }
    metrics_path = case_dir / "activation_resolved_metrics.json"
    _atomic_json(metrics_path, metrics)
    required = (
        "activation_partition.json",
        "activation_resolved_results.npz",
        "activation_resolved_metrics.json",
        "activation_resolved_diagnostics.png",
        "activation_spectrum.png",
    )
    marker = {
        "status": "complete",
        "case_digest": digest,
        "completed": timestamp(),
        "runtime_seconds": time.perf_counter() - started,
        "files": {name: _sha256(case_dir / name) for name in required},
    }
    _atomic_json(case_dir / "COMPLETE.json", marker)
    progress(
        "stage=case status=finish "
        f"seconds={marker['runtime_seconds']:.3f} "
        + " ".join(
            f"{item.label}_S={item.similarity:.6f}" for item in diagnostics
        )
    )
    return {
        "status": "success",
        "case_id": case["case_id"],
        "case_dir": str(case_dir),
        "runtime_seconds": marker["runtime_seconds"],
        "diagnostics": [_diagnostic_payload(item) for item in diagnostics],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    selection = result.add_mutually_exclusive_group(required=True)
    selection.add_argument("--case-index", type=int)
    selection.add_argument("--all", action="store_true")
    result.add_argument("--n", type=int, required=True)
    result.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    result.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    result.add_argument("--dry-run", action="store_true")
    return result


def main() -> None:
    args = parser().parse_args()
    config_path = args.config.resolve()
    config = _read_json(config_path)
    indices = range(len(config["cases"])) if args.all else (args.case_index,)
    plan = {
        "config": str(config_path),
        "detector_n": args.n,
        "output_root": str(args.output_root.resolve()),
        "case_indices": list(indices),
        "cases": [config["cases"][index] for index in indices],
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    record_suffix = "" if args.all else f"_case_{args.case_index:03d}"
    plan_path = output_root / f"run_plan{record_suffix}.json"
    status_path = output_root / f"run_status{record_suffix}.json"
    failure_path = output_root / f"FAILURE{record_suffix}.json"
    _atomic_json(plan_path, plan)
    outcomes = []
    try:
        for case_index in plan["case_indices"]:
            outcomes.append(
                run_case(
                    config,
                    case_index,
                    args.n,
                    output_root,
                    resume=args.resume,
                )
            )
            _atomic_json(status_path, {"outcomes": outcomes, "updated": timestamp()})
    except BaseException as exc:
        _atomic_json(
            failure_path,
            {
                "plan": plan,
                "outcomes": outcomes,
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
                "failed": timestamp(),
            },
        )
        raise
    _atomic_json(status_path, {"outcomes": outcomes, "completed": timestamp()})
    failure_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
