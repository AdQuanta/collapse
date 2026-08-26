#!/usr/bin/env python3.11
"""Build cross-configuration diagnostics for the N=17 activation-band study."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
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

from collapse.sobol_coupling_scan import _atomic_json, timestamp  # noqa: E402


DEFAULT_RUN_ROOT = ROOT / "work" / "zeus_three_ring_activation_resolved_N17_20260823_125039"
DEFAULT_OUTPUT = ROOT / "reports" / "ring_activation_hz0_diagnostics_2026-08-24"
LABELS = ("global", "weak", "intermediate", "strong")
CASE_ORDER = (
    "case_01_born_like_nearest_neighbor",
    "case_02_non_born_exchange_only",
    "case_03_born_like_second_neighbor",
)
CASE_SHORT = {
    CASE_ORDER[0]: "Born-like nearest-neighbor",
    CASE_ORDER[1]: "Exchange-only ($J=0$)",
    CASE_ORDER[2]: "Born-like second-neighbor",
}
BLUE = "#1f77b4"
RED = "#d95f5f"
PURPLE = "#6b3f7c"
MODEL_BLUE = "#2a80c9"
MODEL_ORANGE = "#ef8a00"
BAND_COLORS = {
    "global": "#222222",
    "weak": "#4477aa",
    "intermediate": "#aa4499",
    "strong": "#cc6677",
}


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_cases(run_root: Path) -> list[tuple[str, dict[str, Any], dict[str, np.ndarray]]]:
    """Load the three completed cases and validate their completion hashes."""

    cases = []
    for case_id in CASE_ORDER:
        case_dir = run_root / case_id
        marker = _read_json(case_dir / "COMPLETE.json")
        if marker.get("status") != "complete":
            raise RuntimeError(f"{case_id} is not marked complete")
        for name, expected in marker.get("files", {}).items():
            path = case_dir / name
            if not path.is_file() or _sha256(path) != expected:
                raise RuntimeError(f"{case_id}: invalid completion hash for {name}")
        metrics = _read_json(case_dir / "activation_resolved_metrics.json")
        if int(metrics["detector_n"]) != 17:
            raise ValueError(f"{case_id}: expected N=17")
        with np.load(case_dir / "activation_resolved_results.npz", allow_pickle=False) as archive:
            arrays = {name: np.asarray(archive[name]) for name in archive.files}
        cases.append((case_id, metrics, arrays))
    return cases


def _diagnostic_map(metrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    diagnostics = {item["label"]: item for item in metrics["diagnostics"]}
    if set(diagnostics) != set(LABELS):
        raise ValueError("activation diagnostics do not contain the expected four labels")
    return diagnostics


def plot_montage(
    path: Path,
    cases: list[tuple[str, dict[str, Any], dict[str, np.ndarray]]],
) -> None:
    """Plot P(theta), fits, and R(theta) for every case and activation band."""

    figure = plt.figure(figsize=(18.2, 14.2))
    outer = figure.add_gridspec(3, 4, hspace=0.27, wspace=0.20)
    for row, (case_id, metrics, arrays) in enumerate(cases):
        diagnostics = _diagnostic_map(metrics)
        for column, label in enumerate(LABELS):
            cell = outer[row, column].subgridspec(2, 1, height_ratios=(1.0, 0.88), hspace=0.06)
            ax_p = figure.add_subplot(cell[0, 0])
            ax_r = figure.add_subplot(cell[1, 0], sharex=ax_p)
            prefix = f"{label}__"
            edges = arrays[prefix + "edges"]
            centers = arrays[prefix + "centers"]
            occupied = arrays[prefix + "occupied"].astype(bool)
            ax_p.stairs(arrays[prefix + "p_theta"], edges, color=BLUE, fill=True, alpha=0.18, linewidth=1.0)
            ax_p.stairs(arrays[prefix + "p_pi_minus_theta"], edges, color=RED, fill=True, alpha=0.13, linewidth=1.0)
            ax_p.plot(arrays[prefix + "fit_grid"], arrays[prefix + "wg_density"], color=MODEL_BLUE, linewidth=1.0)
            ax_p.plot(arrays[prefix + "fit_grid"], arrays[prefix + "wc_density"], color=MODEL_ORANGE, linestyle="--", linewidth=1.0)
            ax_r.plot(centers[occupied], arrays[prefix + "ratio"][occupied], "o-", color=PURPLE, markersize=1.9, linewidth=0.75)
            ax_r.plot(centers, arrays[prefix + "born"], "k--", linewidth=0.9)
            diagnostic = diagnostics[label]
            if row == 0:
                title = "global" if label == "global" else f"{label} activation"
                ax_p.set_title(title, fontsize=11.5, pad=5)
            ax_r.text(
                0.035,
                0.07,
                rf"$S_{{\rm Born}}={float(diagnostic['S_born']):.3f}$" + "\n"
                + rf"RMSE$={float(diagnostic['born_RMSE_occupied']):.3f}$",
                transform=ax_r.transAxes,
                fontsize=8,
                va="bottom",
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 0.7},
            )
            if column == 0:
                ax_p.set_ylabel("density")
                ax_r.set_ylabel(r"$R(\theta)$")
            if row == 2:
                ax_r.set_xlabel(r"$\theta$")
            ax_p.set_xlim(0.0, np.pi)
            ax_p.set_ylim(bottom=0.0)
            ax_r.set_ylim(-0.04, 1.04)
            ax_r.set_xticks((0.0, np.pi / 2.0, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
            ax_p.tick_params(labelbottom=False)
            ax_p.grid(alpha=0.15)
            ax_r.grid(alpha=0.15)
    handles = (
        Line2D([], [], color=BLUE, linewidth=5, alpha=0.35, label=r"$P(\theta)$"),
        Line2D([], [], color=RED, linewidth=5, alpha=0.30, label=r"$P(\pi-\theta)$"),
        Line2D([], [], color=MODEL_BLUE, label="wrapped Gaussian"),
        Line2D([], [], color=MODEL_ORANGE, linestyle="--", label="wrapped Cauchy"),
        Line2D([], [], color=PURPLE, marker="o", markersize=3, label=r"$R(\theta)$"),
        Line2D([], [], color="black", linestyle="--", label=r"$\cos^2(\theta/2)$"),
    )
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.942), ncol=6, frameon=False)
    figure.suptitle(r"Activation-resolved projective diagnostics at $N_D=17$", fontsize=15, y=0.988)
    for y, case_id in zip((0.755, 0.485, 0.215), CASE_ORDER, strict=True):
        figure.text(
            0.012,
            y,
            CASE_SHORT[case_id],
            rotation=90,
            fontsize=10.5,
            ha="center",
            va="center",
        )
    figure.text(
        0.5,
        0.012,
        "Bands are global detector-channel activation quantiles (20% weak, 60% intermediate, 20% strong); component curves use root projection weights.",
        ha="center",
        fontsize=9,
    )
    figure.subplots_adjust(left=0.075, right=0.992, bottom=0.055, top=0.885)
    figure.savefig(path, dpi=190, bbox_inches="tight")
    plt.close(figure)


def plot_score_summary(
    path: Path,
    cases: list[tuple[str, dict[str, Any], dict[str, np.ndarray]]],
) -> None:
    x = np.arange(len(cases), dtype=float)
    figure, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), constrained_layout=True)
    for label in LABELS:
        diagnostics = [_diagnostic_map(metrics)[label] for _, metrics, _ in cases]
        axes[0].plot(x, [item["S_born"] for item in diagnostics], "o-", color=BAND_COLORS[label], label=label)
        axes[1].plot(x, [item["born_RMSE_occupied"] for item in diagnostics], "o-", color=BAND_COLORS[label], label=label)
    axes[0].axhline(0.75, color="#777777", linestyle="--", linewidth=0.9, label="Born gate")
    axes[1].axhline(0.15, color="#777777", linestyle="--", linewidth=0.9, label="RMSE gate")
    axes[0].set_ylabel(r"$S_{\rm Born}$")
    axes[1].set_ylabel("Born RMSE")
    names = ("nearest\nneighbor", "exchange only\n($J=0$)", "second\nneighbor")
    for axis in axes:
        axis.set_xticks(x, names)
        axis.grid(alpha=0.2)
    axes[0].legend(frameon=False, ncol=2)
    axes[1].legend(frameon=False)
    figure.suptitle(r"Born diagnostics by activation band, $N_D=17$", fontsize=14)
    figure.savefig(path, dpi=190)
    plt.close(figure)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    result.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return result


def main() -> None:
    args = parser().parse_args()
    run_root = args.run_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = load_cases(run_root)
    montage_path = output_dir / "activation_band_diagnostic_montage.png"
    summary_path = output_dir / "activation_band_score_summary.png"
    plot_montage(montage_path, cases)
    plot_score_summary(summary_path, cases)
    records = []
    for case_id, metrics, _ in cases:
        records.append(
            {
                "case_id": case_id,
                "description": metrics["description"],
                "parameters": metrics["parameters"],
                "diagnostics": metrics["diagnostics"],
                "validation": metrics["validation"],
            }
        )
    manifest_path = output_dir / "activation_band_summary.json"
    _atomic_json(
        manifest_path,
        {
            "schema_version": 1,
            "created": timestamp(),
            "source_run_root": str(run_root),
            "records": records,
            "figures": {
                montage_path.name: _sha256(montage_path),
                summary_path.name: _sha256(summary_path),
            },
        },
    )
    print(f"[{timestamp()}] cases={len(cases)} output={output_dir}", flush=True)


if __name__ == "__main__":
    main()
