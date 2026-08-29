"""
Pairwise stability heatmaps for Born-rule Hamiltonian candidates.

This script sweeps two parameters around a selected base Hamiltonian, evaluates
the current Born-search metrics, writes a flat table, and saves heatmaps of
``S_born`` together with degeneracy and tail diagnostics.  Optional top-row
diagnostic figures are generated through ``born_hamiltonian_search.py``; their
spectrum/level-spacing panels can be disabled for large runs.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from born_hamiltonian_search import (  # noqa: E402
    Candidate,
    TeeWriter,
    _candidate_label,
    _default_worker_count,
    _jsonable,
    _safe_plot_name,
    evaluate_candidate,
    plot_result_diagnostics,
)


PARAM_ALIASES = {
    "J": "J",
    "Jpm": "Jpm",
    "Jxx": "Jxx",
    "Jyy": "Jyy",
    "Jx_unscaled": "Jx_unscaled",
    "jx_unscaled": "Jx_unscaled",
    "jx": "Jx_unscaled",
    "Jy_unscaled": "Jy_unscaled",
    "jy_unscaled": "Jy_unscaled",
    "jy": "Jy_unscaled",
    "Jz": "Jz",
    "Jzx": "Jzx",
    "Jcpm_unscaled": "Jcpm_unscaled",
    "jcpm_unscaled": "Jcpm_unscaled",
    "jcpm": "Jcpm_unscaled",
    "hx": "hx",
    "hz": "hz",
    "disorder_strength_J": "disorder_strength_J",
    "disorder_strength_Jpm": "disorder_strength_Jpm",
    "disorder_strength_Jx": "disorder_strength_Jx",
    "disorder_strength_Jz": "disorder_strength_Jz",
    "disorder_strength_Jzx": "disorder_strength_Jzx",
    "disorder_strength_Jcpm": "disorder_strength_Jcpm",
    "disorder_strength_hx": "disorder_strength_hx",
    "disorder_strength_hz": "disorder_strength_hz",
}


def _resolve_param(name: str) -> str:
    if name not in PARAM_ALIASES:
        valid = ", ".join(sorted(PARAM_ALIASES))
        raise ValueError(f"Unsupported sweep parameter {name!r}. Valid choices: {valid}")
    return PARAM_ALIASES[name]


def _base_candidate(args: argparse.Namespace) -> Candidate:
    return Candidate(
        model=args.model,
        N=args.N,
        J=args.J,
        Jpm=args.Jpm,
        Jxx=args.Jxx,
        Jyy=args.Jyy,
        Jx_unscaled=args.jx_unscaled,
        Jy_unscaled=args.jy_unscaled,
        Jz=args.Jz,
        Jzx=args.Jzx,
        Jcpm_unscaled=args.jcpm_unscaled,
        hx=args.hx,
        hz=args.hz,
        hz0_mode=args.hz0_mode,
        connectivity=args.connectivity,
        central_coupling=args.central_coupling,
        seed=args.seed,
        disorder=args.disorder,
        disorder_strength=args.disorder_strength,
        disorder_strength_J=args.disorder_strength_J,
        disorder_strength_Jpm=args.disorder_strength_Jpm,
        disorder_strength_Jx=args.disorder_strength_Jx,
        disorder_strength_Jz=args.disorder_strength_Jz,
        disorder_strength_Jzx=args.disorder_strength_Jzx,
        disorder_strength_Jcpm=args.disorder_strength_Jcpm,
        disorder_strength_hx=args.disorder_strength_hx,
        disorder_strength_hz=args.disorder_strength_hz,
    )


def _candidate_grid(args: argparse.Namespace) -> list[tuple[float, float, Candidate]]:
    x_param = _resolve_param(args.x_param)
    y_param = _resolve_param(args.y_param)
    if x_param == y_param:
        raise ValueError("x-param and y-param must be different")

    base = _base_candidate(args)
    grid: list[tuple[float, float, Candidate]] = []
    for x_value in args.x_values:
        for y_value in args.y_values:
            grid.append(
                (
                    float(x_value),
                    float(y_value),
                    replace(base, **{x_param: float(x_value), y_param: float(y_value)}),
                )
            )
    return grid


def _evaluate_grid_job(
    payload: tuple[float, float, Candidate, list[float], int, str, float, int, float],
) -> list[dict[str, Any]]:
    x_value, y_value, candidate, times, bins, backend, tail_fraction, log_bins, energy_tol = payload
    rows = evaluate_candidate(
        candidate,
        times,
        bins,
        backend,
        tail_fraction,
        log_bins,
        energy_tol,
    )
    for row in rows:
        row["sweep_x_value"] = x_value
        row["sweep_y_value"] = y_value
    return rows


def _flat_row(result: dict[str, Any], x_param: str, y_param: str) -> dict[str, Any]:
    cand = result["candidate"]
    metrics = result["metrics"]
    row = {
        "x_param": x_param,
        "x_value": result["sweep_x_value"],
        "y_param": y_param,
        "y_value": result["sweep_y_value"],
        "label": result["label"],
        "model": cand["model"],
        "N": cand["N"],
        "t": result["t"],
        "connectivity": cand["connectivity"],
        "central_coupling": cand["central_coupling"],
        "hz0_mode": cand["hz0_mode"],
        "J": cand["J"],
        "Jpm": cand["Jpm"],
        "Jxx": cand["Jxx"],
        "Jyy": cand["Jyy"],
        "Jx_unscaled": cand["Jx_unscaled"],
        "Jy_unscaled": cand["Jy_unscaled"],
        "Jz": cand["Jz"],
        "Jzx": cand["Jzx"],
        "Jcpm_unscaled": cand["Jcpm_unscaled"],
        "hx": cand["hx"],
        "hz": cand["hz"],
        "backend": result["backend"],
        "diagonalization_kind": result["diagonalization_kind"],
        "sector_count": result["sector_count"],
    }
    for key in (
        "objective_score",
        "born_similarity",
        "phi_uniformity_score",
        "phi_entropy_score",
        "phi_total_variation",
        "phi_max_bin_fraction",
        "phi_rayleigh_r",
        "phi_bin_count",
        "mean_abs_ratio_error",
        "tail_density_exponent",
        "reciprocity_error",
        "radius_q99_over_q50",
        "radius_atomic_fraction",
        "energy_degenerate_fraction",
        "energy_degenerate_cluster_fraction",
        "energy_max_multiplicity",
        "energy_mean_spacing_ratio",
        "energy_min_spacing",
        "diagonalization_wall_seconds",
        "analysis_wall_seconds",
    ):
        row[key] = metrics.get(key, math.nan)
    row["diagnostic_figure"] = result.get("diagnostic_figure", "")
    return row


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(_jsonable(row))


def _metric_matrix(
    flat_rows: list[dict[str, Any]],
    x_values: list[float],
    y_values: list[float],
    t_value: float,
    metric: str,
) -> np.ndarray:
    matrix = np.full((len(y_values), len(x_values)), np.nan, dtype=float)
    x_index = {float(value): idx for idx, value in enumerate(x_values)}
    y_index = {float(value): idx for idx, value in enumerate(y_values)}
    for row in flat_rows:
        if not math.isclose(float(row["t"]), float(t_value), rel_tol=0.0, abs_tol=1e-12):
            continue
        x_idx = x_index.get(float(row["x_value"]))
        y_idx = y_index.get(float(row["y_value"]))
        if x_idx is None or y_idx is None:
            continue
        value = row.get(metric, math.nan)
        matrix[y_idx, x_idx] = float(value) if value not in ("", None) else math.nan
    return matrix


def _heatmap_context(args: argparse.Namespace, x_param: str, y_param: str) -> str:
    base = _base_candidate(args)
    j_label = "J=swept" if "J" in {x_param, y_param} else f"J={base.J:g}"
    jpm_label = "Jpm=swept" if "Jpm" in {x_param, y_param} else f"Jpm={base.Jpm:g}"
    return (
        f"{base.model} {base.connectivity}, N={base.N}, cc={base.central_coupling}, "
        f"hz0={base.hz0_mode}, {j_label}, {jpm_label}, hz={base.hz:g}"
    )


def _heatmap_file_stem(args: argparse.Namespace, x_param: str, y_param: str) -> str:
    base = _base_candidate(args)
    j_label = "Jscan" if "J" in {x_param, y_param} else f"J{base.J:g}"
    jpm_label = "Jpmscan" if "Jpm" in {x_param, y_param} else f"Jpm{base.Jpm:g}"
    return _safe_plot_name(
        f"{base.model}_{base.connectivity}_N{base.N}_cc-{base.central_coupling}"
        f"_hz0-{base.hz0_mode}_{j_label}_{jpm_label}_hz{base.hz:g}"
    )


def _plot_heatmaps(
    flat_rows: list[dict[str, Any]],
    args: argparse.Namespace,
    x_param: str,
    y_param: str,
) -> list[Path]:
    paths: list[Path] = []
    metrics = [
        ("born_similarity", r"$S_{\mathrm{born}}$"),
        ("phi_uniformity_score", r"$\phi$ uniformity"),
        ("mean_abs_ratio_error", "mean |R-Born|"),
        ("tail_density_exponent", "tail alpha"),
        ("radius_atomic_fraction", "radius atom frac"),
        ("energy_degenerate_fraction", "E deg frac"),
    ]
    for t_value in args.times:
        fig, axes = plt.subplots(2, 3, figsize=(13.8, 7.8), dpi=160)
        for ax, (metric, title) in zip(axes.ravel(), metrics):
            matrix = _metric_matrix(flat_rows, args.x_values, args.y_values, t_value, metric)
            imshow_kwargs = {}
            if metric == "born_similarity":
                imshow_kwargs = {"vmin": 0.0, "vmax": 1.0}
            im = ax.imshow(
                matrix,
                origin="lower",
                aspect="auto",
                cmap=args.born_colormap if metric == "born_similarity" else "viridis",
                **imshow_kwargs,
            )
            ax.set_title(title, fontsize=10)
            ax.set_xlabel(x_param)
            ax.set_ylabel(y_param)
            ax.set_xticks(range(len(args.x_values)))
            ax.set_xticklabels([f"{value:g}" for value in args.x_values], rotation=35, ha="right")
            ax.set_yticks(range(len(args.y_values)))
            ax.set_yticklabels([f"{value:g}" for value in args.y_values])
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.suptitle(
            f"Pairwise Born stability, {_heatmap_context(args, x_param, y_param)}, "
            f"t={t_value:g}: {x_param} vs {y_param}",
            fontsize=13,
        )
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        stem = _heatmap_file_stem(args, x_param, y_param)
        path = args.out_dir / (
            f"heatmap_{stem}_t{_safe_plot_name(f'{t_value:g}')}_{x_param}_vs_{y_param}.png"
        )
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    return paths


def _write_index(
    path: Path,
    flat_rows: list[dict[str, Any]],
    heatmaps: list[Path],
    diagnostics: list[dict[str, Any]],
) -> None:
    top = sorted(flat_rows, key=lambda row: float(row["born_similarity"]), reverse=True)[:12]
    lines = [
        "# Pairwise Born-Stability Heatmaps",
        "",
        "The heatmaps show the current Born similarity metric together with tail, atom, and full-Hamiltonian degeneracy diagnostics.",
        "",
        "## Heatmaps",
        "",
    ]
    for path_item in heatmaps:
        lines.append(f"- [{path_item.name}]({path_item.name})")
    lines.extend(
        [
            "",
            "## Top Rows",
            "",
            "| rank | t | x | y | S | phi U | alpha | atom | E deg frac | E max mult | diagnostic |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---|",
        ]
    )
    diag_by_label_time = {
        (item["label"], float(item["t"])): Path(item["path"]).name
        for item in diagnostics
    }
    for rank, row in enumerate(top, 1):
        diag = diag_by_label_time.get((row["label"], float(row["t"])), "")
        diag_link = f"[figure](diagnostics/{diag})" if diag else ""
        lines.append(
            "| {rank} | {t:g} | {x:g} | {y:g} | {S:.4f} | {phi:.3f} | {alpha:.3g} | {atom:.3f} | {edeg:.3f} | {emax:.0f} | {diag} |".format(
                rank=rank,
                t=float(row["t"]),
                x=float(row["x_value"]),
                y=float(row["y_value"]),
                S=float(row["born_similarity"]),
                phi=float(row.get("phi_uniformity_score", math.nan)),
                alpha=float(row["tail_density_exponent"]),
                atom=float(row["radius_atomic_fraction"]),
                edeg=float(row["energy_degenerate_fraction"]),
                emax=float(row["energy_max_multiplicity"]),
                diag=diag_link,
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["single_pixel", "dimerized_pixel", "cnot_copier"], default="single_pixel")
    parser.add_argument("--N", type=int, default=10)
    parser.add_argument("--connectivity", choices=["chain", "ring", "all_to_all"], default="ring")
    parser.add_argument("--central-coupling", choices=["auto", "all", "first", "last", "ends"], default="all")
    parser.add_argument("--hz0-mode", choices=["matched", "zero", "half", "minus"], default="matched")
    parser.add_argument("--J", type=float, default=1.0)
    parser.add_argument("--Jpm", type=float, default=0.0)
    parser.add_argument("--Jxx", type=float, default=0.0)
    parser.add_argument("--Jyy", type=float, default=0.0)
    parser.add_argument("--jx-unscaled", type=float, default=0.05)
    parser.add_argument("--jy-unscaled", type=float, default=0.0)
    parser.add_argument("--Jz", type=float, default=0.0)
    parser.add_argument("--Jzx", type=float, default=0.0)
    parser.add_argument("--jcpm-unscaled", type=float, default=0.0)
    parser.add_argument("--hx", type=float, default=0.0)
    parser.add_argument("--hz", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=44)
    parser.add_argument("--disorder", choices=["none", "uniform", "gaussian", "lorentzian"], default="none")
    parser.add_argument("--disorder-strength", type=float, default=0.0)
    parser.add_argument("--disorder-strength-J", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jpm", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jx", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jz", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jzx", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jcpm", type=float, default=0.0)
    parser.add_argument("--disorder-strength-hx", type=float, default=0.0)
    parser.add_argument("--disorder-strength-hz", type=float, default=0.0)
    parser.add_argument("--x-param", required=True)
    parser.add_argument("--x-values", type=float, nargs="+", required=True)
    parser.add_argument("--y-param", required=True)
    parser.add_argument("--y-values", type=float, nargs="+", required=True)
    parser.add_argument("--times", type=float, nargs="+", default=[1000.0])
    parser.add_argument("--bins", type=int, default=100)
    parser.add_argument("--tail-fraction", type=float, default=0.10)
    parser.add_argument("--log-bins", type=int, default=50)
    parser.add_argument("--energy-degeneracy-tol", type=float, default=1e-9)
    parser.add_argument("--backend", choices=["auto", "quspin", "numpy"], default="auto")
    parser.add_argument("--workers", type=int, default=_default_worker_count())
    parser.add_argument("--plot-top", type=int, default=6)
    parser.add_argument("--plot-pseudocount", type=float, default=0.5)
    parser.add_argument("--plot-max-bloch-points", type=int, default=6000)
    parser.add_argument("--max-detector-spectrum-qubits", type=int, default=12)
    spectra_group = parser.add_mutually_exclusive_group()
    spectra_group.add_argument(
        "--diagnostic-spectra",
        dest="diagnostic_spectra",
        action="store_true",
        help="Include full/detector spectrum and unfolded level-spacing panels in diagnostic figures.",
    )
    spectra_group.add_argument(
        "--skip-diagnostic-spectra",
        dest="diagnostic_spectra",
        action="store_false",
        help="Skip spectrum and level-spacing panels in diagnostic figures to avoid extra spectral work.",
    )
    parser.set_defaults(diagnostic_spectra=True)
    parser.add_argument(
        "--born-colormap",
        default="RdYlGn",
        help="Colormap for S_born heatmaps. Defaults to red/yellow/green with vmin=0, vmax=1.",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("figures/born_pairwise_heatmap"))
    parser.add_argument("--log-file", type=Path, default=None)
    return parser.parse_args()


def run(args: argparse.Namespace) -> None:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    x_param = _resolve_param(args.x_param)
    y_param = _resolve_param(args.y_param)
    grid = _candidate_grid(args)
    args.workers = max(1, int(args.workers))
    print(f"Log file: {args.log_file}")
    print(f"Base candidate: {_candidate_label(_base_candidate(args))}")
    print(f"Grid: {x_param} ({len(args.x_values)}) x {y_param} ({len(args.y_values)})")
    print(f"Times: {args.times}")
    print(f"Worker processes: {args.workers}")
    print(f"Diagnostic spectra: {'enabled' if args.diagnostic_spectra else 'disabled'}")

    jobs = [
        (
            x_value,
            y_value,
            candidate,
            list(args.times),
            args.bins,
            args.backend,
            args.tail_fraction,
            args.log_bins,
            args.energy_degeneracy_tol,
        )
        for x_value, y_value, candidate in grid
    ]

    results: list[dict[str, Any]] = []
    if args.workers == 1 or len(jobs) <= 1:
        for idx, job in enumerate(jobs, 1):
            print(f"[{idx:03d}/{len(jobs):03d}] x={job[0]:g}, y={job[1]:g}", flush=True)
            results.extend(_evaluate_grid_job(job))
    else:
        n_workers = min(args.workers, len(jobs))
        print(f"Submitting {len(jobs)} grid jobs to {n_workers} workers", flush=True)
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            future_to_job = {pool.submit(_evaluate_grid_job, job): job for job in jobs}
            for idx, future in enumerate(as_completed(future_to_job), 1):
                job = future_to_job[future]
                results.extend(future.result())
                print(f"[{idx:03d}/{len(jobs):03d}] completed x={job[0]:g}, y={job[1]:g}", flush=True)

    results.sort(key=lambda row: row["metrics"]["born_similarity"], reverse=True)
    flat_rows = [_flat_row(result, x_param, y_param) for result in results]
    heatmaps = _plot_heatmaps(flat_rows, args, x_param, y_param)

    diagnostics = []
    diag_dir = args.out_dir / "diagnostics"
    if args.plot_top > 0:
        for rank, result in enumerate(results[: args.plot_top], 1):
            path = plot_result_diagnostics(
                result,
                diag_dir,
                bins=args.bins,
                tail_fraction=args.tail_fraction,
                n_log_bins=args.log_bins,
                backend=args.backend,
                pseudocount=args.plot_pseudocount,
                max_bloch_points=args.plot_max_bloch_points,
                max_detector_spectrum_qubits=args.max_detector_spectrum_qubits,
                include_spectra=args.diagnostic_spectra,
            )
            result["diagnostic_figure"] = str(path)
            diagnostics.append(
                {
                    "rank": rank,
                    "label": result["label"],
                    "t": result["t"],
                    "path": str(path),
                }
            )

    json_path = args.out_dir / "results.json"
    csv_path = args.out_dir / "pairwise_summary.csv"
    index_path = args.out_dir / "index.md"
    json_path.write_text(
        json.dumps(_jsonable({"args": vars(args), "results": results}), indent=2),
        encoding="utf-8",
    )
    _write_csv(csv_path, flat_rows)
    _write_index(index_path, flat_rows, heatmaps, diagnostics)
    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {index_path}")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.log_file is None:
        args.log_file = args.out_dir / "run.log"
    args.log_file.parent.mkdir(parents=True, exist_ok=True)

    with args.log_file.open("w", encoding="utf-8", buffering=1) as log_fh:
        stdout = TeeWriter(sys.stdout, log_fh)
        stderr = TeeWriter(sys.stderr, log_fh)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            run(args)


if __name__ == "__main__":
    main()
