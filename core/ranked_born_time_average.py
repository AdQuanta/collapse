"""Time-averaged Born diagnostics for one ranked Hamiltonian case.

The Hamiltonian is diagonalized once.  Relative-evolution eigenvalues are then
computed at each requested time.  Per-time angular densities receive equal
weight, and the reported ratio is formed only after averaging:

``R_bar(theta) = P_bar(theta) / (P_bar(theta) + P_bar(pi - theta))``.
"""

from __future__ import annotations

from dataclasses import asdict
import gc
import json
import math
import multiprocessing
import os
from pathlib import Path
import time
from typing import Any, Sequence

import numpy as np

from core.analysis import prepare_sector_relative_evolution
from core.detector_graphs import DetectorGraphSpec, detector_graph_metadata
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.ranked_born_campaign import (
    RankedHamiltonianCase,
    _complete_valid,
    _runtime_provenance,
    graph_spec_for_case,
)
from core.sobol_coupling_scan import (
    _atomic_json,
    _atomic_npz,
    _diagnostics,
    _peak_rss_mb,
    _plot_case,
    _sha256,
    fit_distributions,
    timestamp,
)


def validate_evolution_times(values: Sequence[float]) -> tuple[float, ...]:
    """Return strictly increasing, finite, positive evolution times."""

    times = tuple(float(value) for value in values)
    if not times:
        raise ValueError("evolution_times must not be empty")
    if any(not math.isfinite(value) or value <= 0.0 for value in times):
        raise ValueError("evolution_times must be finite and positive")
    if any(right <= left for left, right in zip(times, times[1:])):
        raise ValueError("evolution_times must be strictly increasing")
    return times


def _time_average_complete_valid(case_dir: Path, times: tuple[float, ...]) -> bool:
    """Require both valid checksums and the exact requested time grid."""

    if not _complete_valid(case_dir):
        return False
    try:
        marker = json.loads((case_dir / "COMPLETE.json").read_text(encoding="utf-8"))
        return marker.get("evolution_times") == list(times)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def _load_time_checkpoint(
    path: Path,
    expected_times: tuple[float, ...],
    expected_eigenvalue_count: int,
) -> np.ndarray | None:
    """Load one valid time chunk, or return ``None`` for recomputation."""

    if not path.is_file():
        return None
    try:
        with np.load(path, allow_pickle=False) as payload:
            stored_times = np.asarray(payload["evolution_times"], dtype=float)
            eigenvalues = np.asarray(payload["eigenvalues"], dtype=np.complex128)
        if not np.array_equal(stored_times, np.asarray(expected_times, dtype=float)):
            return None
        if eigenvalues.shape != (len(expected_times), expected_eigenvalue_count):
            return None
        return eigenvalues
    except (KeyError, OSError, TypeError, ValueError):
        return None


def average_time_diagnostics(
    eigenvalues_by_time: Sequence[np.ndarray],
    *,
    bins: int,
) -> tuple[
    dict[str, Any],
    dict[str, np.ndarray],
    list[dict[str, Any]],
    dict[str, np.ndarray],
]:
    """Average per-time ``P`` densities and derive ``R`` from that average."""

    values = [np.asarray(item, dtype=np.complex128) for item in eigenvalues_by_time]
    if not values:
        raise ValueError("eigenvalues_by_time must not be empty")
    if any(item.ndim != 1 for item in values):
        raise ValueError("each eigenvalue sample must be one-dimensional")
    if len({item.size for item in values}) != 1:
        raise ValueError("each time must contribute the same number of eigenvalues")

    per_time_metrics: list[dict[str, Any]] = []
    per_time_arrays: list[dict[str, np.ndarray]] = []
    for item in values:
        metrics, arrays = _diagnostics(item, bins)
        per_time_metrics.append(metrics)
        per_time_arrays.append(arrays)

    pooled = np.concatenate(values)
    metrics, arrays = _diagnostics(pooled, bins)
    p_theta_by_time = np.stack([item["p_theta"] for item in per_time_arrays])
    p_reflected_by_time = np.stack(
        [item["p_pi_minus_theta"] for item in per_time_arrays]
    )
    p_theta = np.mean(p_theta_by_time, axis=0)
    p_reflected = np.mean(p_reflected_by_time, axis=0)
    denominator = p_theta + p_reflected
    occupied = denominator > 0.0
    ratio = np.divide(
        p_theta,
        denominator,
        out=np.full(p_theta.shape, np.nan),
        where=occupied,
    )
    born = np.asarray(arrays["R_born"])
    residual = ratio - born
    widths = np.diff(arrays["edges"])
    probability_mass = p_theta * widths
    nonzero_mass = probability_mass > 0.0

    arrays.update(
        {
            "p_theta": p_theta,
            "p_pi_minus_theta": p_reflected,
            "p_product": p_theta * p_reflected,
            "R": ratio,
            "R_occupied": occupied,
            "R_residual": residual,
        }
    )
    metrics.update(
        {
            "time_count": len(values),
            "time_average_definition": (
                "equal arithmetic mean of normalized per-time P(theta) "
                "densities; R is computed from the averaged P and its reflection"
            ),
            "R_from_time_averaged_P": True,
            "p_theta_integral": float(np.sum(p_theta * widths)),
            "p_reflected_integral": float(np.sum(p_reflected * widths)),
            "born_L1_occupied": (
                float(np.sum(np.abs(residual[occupied]) * widths[occupied]))
                if np.any(occupied)
                else float("nan")
            ),
            "born_Linf_occupied": (
                float(np.max(np.abs(residual[occupied])))
                if np.any(occupied)
                else float("nan")
            ),
            "born_RMSE_occupied": (
                float(np.sqrt(np.mean(residual[occupied] ** 2)))
                if np.any(occupied)
                else float("nan")
            ),
            "R_min_occupied": (
                float(np.min(ratio[occupied]))
                if np.any(occupied)
                else float("nan")
            ),
            "R_max_occupied": (
                float(np.max(ratio[occupied]))
                if np.any(occupied)
                else float("nan")
            ),
            "occupied_fraction": float(np.mean(occupied)),
            "theta_entropy": float(
                -np.sum(probability_mass[nonzero_mass] * np.log(probability_mass[nonzero_mass]))
            ),
            "product_integral": float(
                np.sum(p_theta * p_reflected * widths)
            ),
            "per_time_finite_eigenvalue_counts": [
                int(item["finite_eigenvalues"]) for item in per_time_metrics
            ],
        }
    )
    time_arrays = {
        "p_theta_by_time": p_theta_by_time,
        "p_pi_minus_theta_by_time": p_reflected_by_time,
        "R_by_time": np.stack([item["R"] for item in per_time_arrays]),
        "R_occupied_by_time": np.stack(
            [item["R_occupied"] for item in per_time_arrays]
        ),
        "S_born_by_time": np.asarray(
            [item["S_born"] for item in per_time_metrics], dtype=float
        ),
        "born_RMSE_occupied_by_time": np.asarray(
            [item["born_RMSE_occupied"] for item in per_time_metrics], dtype=float
        ),
    }
    return metrics, arrays, per_time_metrics, time_arrays


def simulate_ranked_case_time_average(
    case: RankedHamiltonianCase,
    *,
    detector_n: int,
    hz0: float,
    evolution_times: Sequence[float],
    case_dir: Path,
    source_index: int,
    rank_index: int,
    hz0_aliases: Sequence[str] = (),
    bins: int = 64,
    plot_grid: int = 720,
    fit_harmonics: int = 32,
    fit_tolerance: float = 1.0e-10,
    max_bloch_points: int = 6000,
    resume: bool = True,
    graph_spec_override: DetectorGraphSpec | None = None,
    graph_provenance: dict[str, Any] | None = None,
    selection_label: str | None = None,
) -> dict[str, Any]:
    """Simulate requested times from one diagonalization and persist their average."""

    times = validate_evolution_times(evolution_times)
    case_dir = Path(case_dir)
    if detector_n < 3:
        raise ValueError("detector_n must be at least three")
    if resume and _time_average_complete_valid(case_dir, times):
        return {
            "status": "resumed",
            "source_index": source_index,
            "rank": rank_index + 1,
            "N": detector_n,
            "time_count": len(times),
            "case_dir": str(case_dir),
        }
    if case_dir.exists() and any(case_dir.iterdir()) and not resume:
        raise FileExistsError(f"non-empty output case directory: {case_dir}")
    case_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    print(
        f"[time-average] start N={detector_n} times={len(times)} "
        f"pooled_samples={len(times) * 2**detector_n} case={case_dir}",
        flush=True,
    )
    graph_spec = (
        graph_spec_override
        if graph_spec_override is not None
        else graph_spec_for_case(case)
    )
    graph_metadata = detector_graph_metadata(detector_n, graph_spec)
    jx_effective = case.jx / math.sqrt(detector_n)
    jy_effective = case.jy / math.sqrt(detector_n)
    hamiltonian = SinglePixelHamiltonianQuSpin(
        N_pixel=detector_n,
        J=case.j,
        Jpm=case.jpm,
        J2=case.j2,
        Jpm2=case.jpm2,
        Jx=jx_effective,
        Jy=jy_effective,
        Jz=0.0,
        Jzx=0.0,
        hx=0.0,
        hz=case.hz,
        hx0=0.0,
        hz0=hz0,
        connectivity=case.connectivity,
        graph_spec=graph_spec,
        central_coupling=case.central_coupling,
        seed=case.model_seed,
        use_symmetry=True,
    )
    diagonalization_started = time.perf_counter()
    sectors = hamiltonian.diagonalize_sectors()
    diagonalization_seconds = time.perf_counter() - diagonalization_started
    print(
        f"[time-average] diagonalization complete N={detector_n} "
        f"sectors={len(sectors)} seconds={diagonalization_seconds:.1f}",
        flush=True,
    )
    preparation_started = time.perf_counter()
    prepared_evolution = prepare_sector_relative_evolution(
        sectors,
        detector_n + 1,
    )
    relative_evolution_preparation_seconds = (
        time.perf_counter() - preparation_started
    )
    print(
        f"[time-average] reusable sector projection ready N={detector_n} "
        f"mode={'local' if prepared_evolution.local_sector_split else 'projected'} "
        f"seconds={relative_evolution_preparation_seconds:.1f}",
        flush=True,
    )
    symmetry_labels = sorted(
        {str(sector.get("symmetry_label", "unknown")) for sector in sectors}
    )
    sector_count = len(sectors)
    del sectors, hamiltonian
    gc.collect()
    print(
        f"[time-average] released source Hamiltonian/sector objects N={detector_n}",
        flush=True,
    )

    eigenvalues_by_time: list[np.ndarray] = []
    analysis_seconds_by_time: list[float] = []
    checkpoint_resumed_by_time: list[bool] = []
    expected_per_time = 2**detector_n
    chunk_size = max(1, math.ceil(len(times) / 16))
    checkpoint_dir = case_dir / "time_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_paths: list[Path] = []
    time_loop_started = time.perf_counter()
    for chunk_index, chunk_start in enumerate(range(0, len(times), chunk_size), start=1):
        chunk_stop = min(chunk_start + chunk_size, len(times))
        chunk_times = times[chunk_start:chunk_stop]
        checkpoint_path = checkpoint_dir / f"chunk_{chunk_index:02d}.npz"
        checkpoint_paths.append(checkpoint_path)
        checkpoint_values = (
            _load_time_checkpoint(
                checkpoint_path,
                chunk_times,
                expected_per_time,
            )
            if resume
            else None
        )
        if checkpoint_values is not None:
            eigenvalues_by_time.extend(
                np.asarray(row, dtype=np.complex128) for row in checkpoint_values
            )
            analysis_seconds_by_time.extend([0.0] * len(chunk_times))
            checkpoint_resumed_by_time.extend([True] * len(chunk_times))
            print(
                f"[time-average] checkpoint resumed N={detector_n} "
                f"chunk={chunk_index} times={chunk_start + 1}:{chunk_stop}",
                flush=True,
            )
        else:
            chunk_values: list[np.ndarray] = []
            for local_index, evolution_time in enumerate(chunk_times, start=1):
                analysis_started = time.perf_counter()
                values_at_time = np.asarray(
                    prepared_evolution.eigenvalues(evolution_time),
                    dtype=np.complex128,
                )
                elapsed_at_time = time.perf_counter() - analysis_started
                chunk_values.append(values_at_time)
                eigenvalues_by_time.append(values_at_time)
                analysis_seconds_by_time.append(elapsed_at_time)
                checkpoint_resumed_by_time.append(False)
                global_time_index = chunk_start + local_index
                print(
                    f"[time-average] time complete N={detector_n} "
                    f"time={global_time_index}/{len(times)} "
                    f"t={evolution_time:.6g} seconds={elapsed_at_time:.1f}",
                    flush=True,
                )
            _atomic_npz(
                checkpoint_path,
                evolution_times=np.asarray(chunk_times, dtype=float),
                eigenvalues=np.stack(chunk_values),
            )
            print(
                f"[time-average] checkpoint saved N={detector_n} "
                f"chunk={chunk_index} times={chunk_start + 1}:{chunk_stop} "
                f"path={checkpoint_path}",
                flush=True,
            )
        completed_count = chunk_stop
        elapsed = time.perf_counter() - time_loop_started
        rate = elapsed / completed_count
        eta = rate * (len(times) - completed_count)
        print(
            f"[time-average] progress N={detector_n} "
            f"time={completed_count}/{len(times)} elapsed_s={elapsed:.1f} "
            f"eta_s={eta:.1f}",
            flush=True,
        )

    print(
        f"[time-average] aggregating N={detector_n} "
        f"time_count={len(times)}",
        flush=True,
    )
    metrics, arrays, per_time_metrics, time_arrays = average_time_diagnostics(
        eigenvalues_by_time,
        bins=bins,
    )
    fits, fit_arrays = fit_distributions(
        arrays["theta"],
        bins,
        plot_grid,
        fit_harmonics,
        fit_tolerance,
    )
    expected_pooled = len(times) * expected_per_time
    direct_p_average = np.mean(time_arrays["p_theta_by_time"], axis=0)
    direct_reflected_average = np.mean(
        time_arrays["p_pi_minus_theta_by_time"], axis=0
    )
    denominator = direct_p_average + direct_reflected_average
    direct_ratio = np.divide(
        direct_p_average,
        denominator,
        out=np.full(direct_p_average.shape, np.nan),
        where=denominator > 0.0,
    )
    ratio_mask = np.asarray(arrays["R_occupied"], dtype=bool)
    p_consistency = float(np.max(np.abs(arrays["p_theta"] - direct_p_average)))
    reflected_consistency = float(
        np.max(np.abs(arrays["p_pi_minus_theta"] - direct_reflected_average))
    )
    ratio_consistency = (
        float(np.max(np.abs(arrays["R"][ratio_mask] - direct_ratio[ratio_mask])))
        if np.any(ratio_mask)
        else 0.0
    )
    validation = {
        "passed": bool(
            all(item.size == expected_per_time for item in eigenvalues_by_time)
            and all(
                np.all(np.isfinite(item.real)) and np.all(np.isfinite(item.imag))
                for item in eigenvalues_by_time
            )
            and int(metrics["finite_eigenvalues"]) == expected_pooled
            and abs(float(metrics["p_theta_integral"]) - 1.0) < 1.0e-10
            and abs(float(metrics["p_reflected_integral"]) - 1.0) < 1.0e-10
            and p_consistency < 1.0e-14
            and reflected_consistency < 1.0e-14
            and ratio_consistency < 1.0e-14
        ),
        "time_count": len(times),
        "expected_eigenvalue_count_per_time": expected_per_time,
        "actual_eigenvalue_counts_per_time": [
            int(item.size) for item in eigenvalues_by_time
        ],
        "expected_pooled_eigenvalue_count": expected_pooled,
        "actual_pooled_finite_eigenvalue_count": int(metrics["finite_eigenvalues"]),
        "finite_eigenvalues_at_every_time": bool(
            all(
                np.all(np.isfinite(item.real)) and np.all(np.isfinite(item.imag))
                for item in eigenvalues_by_time
            )
        ),
        "p_average_max_abs_consistency": p_consistency,
        "p_reflected_average_max_abs_consistency": reflected_consistency,
        "R_from_averaged_P_max_abs_consistency": ratio_consistency,
    }
    _atomic_npz(
        case_dir / "results.npz",
        **arrays,
        **fit_arrays,
        evolution_times=np.asarray(times, dtype=float),
    )
    _atomic_npz(
        case_dir / "time_resolved_diagnostics.npz",
        evolution_times=np.asarray(times, dtype=float),
        edges=np.asarray(arrays["edges"]),
        centers=np.asarray(arrays["centers"]),
        **time_arrays,
    )
    _atomic_json(case_dir / "metrics.json", metrics)
    _atomic_json(
        case_dir / "per_time_metrics.json",
        {
            "evolution_times": list(times),
            "metrics": [
                {"evolution_time": value, **item}
                for value, item in zip(times, per_time_metrics)
            ],
        },
    )
    _atomic_json(case_dir / "fits.json", fits)
    _atomic_json(case_dir / "validation.json", validation)
    metadata = {
        "created": timestamp(),
        "source_index": source_index,
        "source_rank": rank_index + 1,
        "source": asdict(case),
        "target_N": detector_n,
        "total_qubits": detector_n + 1,
        "hz0": hz0,
        "hz0_aliases": list(hz0_aliases),
        "evolution_times": list(times),
        "time_average_definition": metrics["time_average_definition"],
        "Jx_unscaled": case.jx,
        "Jx_effective": jx_effective,
        "Jy_unscaled": case.jy,
        "Jy_effective": jy_effective,
        "collective_scaling": "Jx/sqrt(N) and Jy/sqrt(N), applied once",
        "detector_graph": graph_metadata,
        "graph_provenance": (
            dict(graph_provenance)
            if graph_provenance is not None
            else {"mode": "source_generator_spec"}
        ),
        "selection_label": selection_label,
        "central_coupling": case.central_coupling,
        "symmetry_labels": symmetry_labels,
        "sector_count": sector_count,
        "diagonalization_reused_for_all_times": True,
        "sector_projection_reused_for_all_times": True,
        "diagonalization_seconds": diagonalization_seconds,
        "relative_evolution_preparation_seconds": (
            relative_evolution_preparation_seconds
        ),
        "analysis_seconds_by_time": analysis_seconds_by_time,
        "time_checkpoint_resumed_by_time": checkpoint_resumed_by_time,
        "time_checkpoint_chunk_size": chunk_size,
        "time_checkpoint_count": len(checkpoint_paths),
        "analysis_seconds_total": float(sum(analysis_seconds_by_time)),
        "peak_rss_mb": _peak_rss_mb(),
        "worker": multiprocessing.current_process().name,
        "pid": os.getpid(),
        "runtime": _runtime_provenance(),
    }
    _atomic_json(case_dir / "metadata.json", metadata)
    title_lead = selection_label or f"Born rank {rank_index + 1}"
    canonical_times = tuple(float(index) * 1.0e6 for index in range(1, len(times) + 1))
    if times == (1.0e6,):
        time_label = r"$t=10^6$"
    elif times == canonical_times:
        time_label = rf"$t=(1,\ldots,{len(times)})\times10^6$"
    else:
        time_label = rf"$t={times[0]:.4g},\ldots,{times[-1]:.4g}$"
    title = (
        rf"Time-averaged {title_lead}: $N={detector_n}$, "
        rf"$h_z={case.hz:.4g}$, $h_{{z0}}={hz0:.4g}$, "
        rf"$J={case.j:.4g}$, $J_{{\pm}}={case.jpm:.4g}$, "
        rf"$J_x={case.jx:.4g}$, {time_label}"
    )
    _plot_case(
        case_dir / "blue_red_diagnostics.png",
        case_dir / "fit_diagnostics.png",
        title,
        arrays,
        fit_arrays,
        fits,
        metrics,
        max_bloch_points,
    )
    if not validation["passed"]:
        raise RuntimeError(f"scientific validation failed for {case_dir}")
    required = (
        "results.npz",
        "time_resolved_diagnostics.npz",
        "metrics.json",
        "per_time_metrics.json",
        "fits.json",
        "validation.json",
        "metadata.json",
        "blue_red_diagnostics.png",
        "fit_diagnostics.png",
    ) + tuple(path.relative_to(case_dir).as_posix() for path in checkpoint_paths)
    marker = {
        "status": "complete",
        "completed": timestamp(),
        "runtime_seconds": time.perf_counter() - started,
        "source_identity_digest": case.identity_digest,
        "evolution_times": list(times),
        "files": {name: _sha256(case_dir / name) for name in required},
    }
    _atomic_json(case_dir / "COMPLETE.json", marker)
    print(
        f"[time-average] complete N={detector_n} "
        f"S_born={metrics['S_born']:.6f} seconds={marker['runtime_seconds']:.1f} "
        f"case={case_dir}",
        flush=True,
    )
    del prepared_evolution, eigenvalues_by_time, arrays, fit_arrays
    gc.collect()
    return {
        "status": "success",
        "source_index": source_index,
        "rank": rank_index + 1,
        "N": detector_n,
        "hz0": hz0,
        "time_count": len(times),
        "S_born": metrics["S_born"],
        "runtime_seconds": marker["runtime_seconds"],
        "case_dir": str(case_dir),
    }
