#!/usr/bin/env python3.11
"""Summarize the completed N=17 Born-like-ring hz0 scan.

The script never recomputes spectra. It validates each completed case against
the scan configuration, writes machine-readable JSON/CSV tables, and plots the
global plus activation-resolved Born diagnostics versus ``hz0/hz``.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
import sys
from typing import Any
import warnings


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
import numpy as np  # noqa: E402

from core.sobol_coupling_scan import _atomic_json, timestamp  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "ring_born_like_hz0_scan_N17.json"
LABELS = ("global", "weak", "intermediate", "strong")
COLORS = {
    "global": "#222222",
    "weak": "#4477aa",
    "intermediate": "#aa4499",
    "strong": "#cc6677",
}
BLUE = "#1f77b4"
RED = "#d95f5f"
PURPLE = "#6b3f7c"
MODEL_BLUE = "#2a80c9"
MODEL_ORANGE = "#ef8a00"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def collect_scan_rows(
    config: dict[str, Any],
    run_root: Path,
    *,
    allow_partial: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Collect and validate completed scan cases in increasing ``hz0/hz``."""

    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    expected_n = int(config["detector_n"])
    source_hz = float(config["source_hz"])
    for case_index, case in enumerate(config["cases"]):
        case_id = str(case["case_id"])
        case_dir = run_root / case_id
        marker_path = case_dir / "COMPLETE.json"
        metrics_path = case_dir / "activation_resolved_metrics.json"
        if not marker_path.is_file() or not metrics_path.is_file():
            missing.append(case_id)
            continue
        marker = _read_json(marker_path)
        if marker.get("status") != "complete":
            missing.append(case_id)
            continue
        metrics = _read_json(metrics_path)
        ratio = float(case["hz0_over_hz"])
        expected_hz0 = float(case["parameter_overrides"]["hz0"])
        actual_hz0 = float(metrics["parameters"]["hz0"])
        actual_hz = float(metrics["parameters"]["hz"])
        if int(metrics["detector_n"]) != expected_n:
            raise ValueError(f"{case_id}: detector N does not match the scan config")
        if not math.isclose(actual_hz, source_hz, rel_tol=1.0e-14, abs_tol=0.0):
            raise ValueError(f"{case_id}: detector hz does not match the scan config")
        if not math.isclose(actual_hz0, expected_hz0, rel_tol=1.0e-14, abs_tol=1.0e-16):
            raise ValueError(f"{case_id}: hz0 does not match the scan config")
        diagnostics = {item["label"]: item for item in metrics["diagnostics"]}
        if set(diagnostics) != set(LABELS):
            raise ValueError(f"{case_id}: incomplete diagnostic labels")
        row: dict[str, Any] = {
            "case_index": case_index,
            "case_id": case_id,
            "detector_n": expected_n,
            "hz": actual_hz,
            "hz0": actual_hz0,
            "hz0_over_hz": ratio,
        }
        for label in LABELS:
            row[f"{label}_S_born"] = float(diagnostics[label]["S_born"])
            row[f"{label}_RMSE"] = float(diagnostics[label]["born_RMSE_occupied"])
            row[f"{label}_N_eff"] = float(diagnostics[label]["effective_root_count"])
        rows.append(row)
    if missing and not allow_partial:
        raise RuntimeError(
            f"{len(missing)} scan cases are incomplete; rerun with --allow-partial "
            f"to summarize available cases: {missing}"
        )
    rows.sort(key=lambda item: float(item["hz0_over_hz"]))
    return rows, missing


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _plot(path: Path, rows: list[dict[str, Any]], study: str) -> None:
    ratio = np.asarray([row["hz0_over_hz"] for row in rows], dtype=float)
    hz = float(rows[0]["hz"])
    figure, axes = plt.subplots(2, 3, figsize=(16.2, 8.0), sharey="row")
    for label in LABELS:
        similarity = np.asarray([row[f"{label}_S_born"] for row in rows])
        rmse = np.asarray([row[f"{label}_RMSE"] for row in rows])
        style = dict(color=COLORS[label], marker="o", markersize=4.2, linewidth=1.25, label=label)
        axes[0, 0].plot(ratio, similarity, **style)
        axes[1, 0].plot(ratio, rmse, **style)

        small = ratio <= 0.11
        axes[0, 1].plot(ratio[small], similarity[small], **style)
        axes[1, 1].plot(ratio[small], rmse[small], **style)

        near = np.abs(ratio - 1.0) <= 0.011
        offset_ppm = 1.0e6 * (ratio[near] - 1.0)
        axes[0, 2].plot(offset_ppm, similarity[near], **style)
        axes[1, 2].plot(offset_ppm, rmse[near], **style)

    axes[0, 0].set_title(r"full scan")
    axes[0, 1].set_title(r"small-$h_{z0}$ regime")
    axes[0, 2].set_title(r"near $h_{z0}=h_z$")
    axes[0, 0].set_ylabel(r"$S_{\rm Born}$")
    axes[1, 0].set_ylabel("Born RMSE")
    axes[1, 0].set_xlabel(r"$h_{z0}/h_z$")
    axes[1, 1].set_xlabel(r"$h_{z0}/h_z$ (symlog)")
    axes[1, 2].set_xlabel(r"$10^6(h_{z0}/h_z-1)$")
    for axis in axes[:, 1]:
        axis.set_xscale("symlog", linthresh=1.0e-4, linscale=0.8)
        axis.set_xlim(-2.0e-5, 0.11)
    for axis in axes[:, 2]:
        axis.axvline(0.0, color="#777777", linestyle="--", linewidth=0.9)
    for axis in axes.flat:
        axis.grid(alpha=0.2)
    axes[0, 0].legend(frameon=False, ncol=2)
    top_axis = axes[0, 0].secondary_xaxis(
        "top",
        functions=(lambda value: value * hz, lambda value: value / hz),
    )
    top_axis.set_xlabel(r"absolute $h_{z0}$")
    figure.suptitle(
        str(study) + "\n"
        + rf"Born similarity versus central field, $N_D={int(rows[0]['detector_n'])}$, $h_z={hz:.8g}$",
        fontsize=14,
    )
    figure.subplots_adjust(left=0.065, right=0.985, bottom=0.085, top=0.865, hspace=0.14, wspace=0.13)
    figure.savefig(path, dpi=190, bbox_inches="tight")
    plt.close(figure)


def _ratio_title(value: float) -> str:
    if value == 0.0:
        return "0"
    if value < 0.01:
        exponent = int(round(math.log10(value)))
        if math.isclose(value, 10.0**exponent, rel_tol=1.0e-12):
            return rf"10^{{{exponent}}}"
    return f"{value:g}"


def _plot_diagnostic_strip(
    path: Path,
    config: dict[str, Any],
    run_root: Path,
) -> None:
    """Plot global P(theta) and R(theta) in an exact 2 x n_hz0 layout."""

    cases = config["cases"]
    count = len(cases)
    figure, axes = plt.subplots(
        2,
        count,
        figsize=(4.5 * count, 8.2),
        gridspec_kw={"height_ratios": (1.0, 0.92), "hspace": 0.08, "wspace": 0.22},
        squeeze=False,
    )
    for column, case in enumerate(cases):
        case_dir = run_root / str(case["case_id"])
        metrics = _read_json(case_dir / "activation_resolved_metrics.json")
        diagnostic = next(
            item for item in metrics["diagnostics"] if item["label"] == "global"
        )
        with np.load(case_dir / "activation_resolved_results.npz", allow_pickle=False) as archive:
            edges = np.asarray(archive["global__edges"])
            centers = np.asarray(archive["global__centers"])
            occupied = np.asarray(archive["global__occupied"], dtype=bool)
            ax_p = axes[0, column]
            ax_r = axes[1, column]
            ax_p.stairs(np.asarray(archive["global__p_theta"]), edges, color=BLUE, fill=True, alpha=0.18, linewidth=0.9)
            ax_p.stairs(np.asarray(archive["global__p_pi_minus_theta"]), edges, color=RED, fill=True, alpha=0.13, linewidth=0.9)
            ax_p.plot(np.asarray(archive["global__fit_grid"]), np.asarray(archive["global__wg_density"]), color=MODEL_BLUE, linewidth=0.9)
            ax_p.plot(np.asarray(archive["global__fit_grid"]), np.asarray(archive["global__wc_density"]), color=MODEL_ORANGE, linestyle="--", linewidth=0.9)
            ratio = np.asarray(archive["global__ratio"])
            ax_r.plot(centers[occupied], ratio[occupied], "o-", color=PURPLE, markersize=1.7, linewidth=0.7)
            ax_r.plot(centers, np.asarray(archive["global__born"]), "k--", linewidth=0.85)
        scan_ratio = float(case["hz0_over_hz"])
        ax_p.set_title(rf"$h_{{z0}}/h_z={_ratio_title(scan_ratio)}$", fontsize=8.5, pad=4)
        ax_r.text(
            0.04,
            0.07,
            rf"$S={float(diagnostic['S_born']):.3f}$" + "\n"
            + rf"RMSE$={float(diagnostic['born_RMSE_occupied']):.3f}$",
            transform=ax_r.transAxes,
            fontsize=6.7,
            va="bottom",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 0.5},
        )
        ax_p.set_xlim(0.0, np.pi)
        ax_p.set_ylim(bottom=0.0)
        ax_r.set_xlim(0.0, np.pi)
        ax_r.set_ylim(-0.04, 1.04)
        ax_r.set_xticks((0.0, np.pi / 2.0, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
        ax_r.set_xlabel(r"$\theta$", fontsize=8)
        ax_p.tick_params(labelbottom=False, labelsize=7)
        ax_r.tick_params(labelsize=7)
        ax_p.grid(alpha=0.14)
        ax_r.grid(alpha=0.14)
        if column == 0:
            ax_p.set_ylabel("density")
            ax_r.set_ylabel(r"$R(\theta)$")
        else:
            ax_p.set_ylabel("")
            ax_r.set_ylabel("")
    handles = (
        Line2D([], [], color=BLUE, linewidth=5, alpha=0.35, label=r"$P(\theta)$"),
        Line2D([], [], color=RED, linewidth=5, alpha=0.30, label=r"$P(\pi-\theta)$"),
        Line2D([], [], color=MODEL_BLUE, label="wrapped Gaussian"),
        Line2D([], [], color=MODEL_ORANGE, linestyle="--", label="wrapped Cauchy"),
        Line2D([], [], color=PURPLE, marker="o", markersize=3, label=r"$R(\theta)$"),
        Line2D([], [], color="black", linestyle="--", label=r"$\cos^2(\theta/2)$"),
    )
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.91), ncol=6, frameon=False, fontsize=9)
    figure.suptitle(
        rf"Central-field scan: global projective diagnostics, $N_D={int(config['detector_n'])}$",
        fontsize=14,
        y=0.995,
    )
    figure.subplots_adjust(left=0.012, right=0.998, bottom=0.09, top=0.84)
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--run-root", type=Path, required=True)
    result.add_argument(
        "--output-dir",
        type=Path,
        help="destination for summary files (defaults to --run-root)",
    )
    result.add_argument("--allow-partial", action="store_true")
    return result


def main() -> None:
    args = parser().parse_args()
    config = _read_json(args.config.resolve())
    run_root = args.run_root.resolve()
    rows, missing = collect_scan_rows(config, run_root, allow_partial=args.allow_partial)
    if not rows:
        raise RuntimeError(f"no completed scan cases found in {run_root}")
    output_dir = args.output_dir.resolve() if args.output_dir else run_root
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "hz0_scan_summary.csv"
    json_path = output_dir / "hz0_scan_summary.json"
    figure_path = output_dir / "hz0_scan_summary.png"
    strip_path = output_dir / "hz0_scan_global_diagnostics_2x20.png"
    _write_csv(csv_path, rows)
    _atomic_json(
        json_path,
        {
            "schema_version": 1,
            "created": timestamp(),
            "config": str(args.config.resolve()),
            "run_root": str(run_root),
            "complete_case_count": len(rows),
            "missing_case_ids": missing,
            "rows": rows,
        },
    )
    _plot(figure_path, rows, str(config.get("study", "central-field scan")))
    _plot_diagnostic_strip(strip_path, config, run_root)
    print(
        f"[{timestamp()}] summarized={len(rows)} missing={len(missing)} "
        f"figures=({figure_path},{strip_path})",
        flush=True,
    )


if __name__ == "__main__":
    main()
