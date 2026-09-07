#!/usr/bin/env python3.11
"""Plot every completed N17 catalog continuation without new diagonalization."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work/_mplconfig"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from core.born_profile_export import load_profile, validate_profile  # noqa: E402
from core.ring_spacing_report import (  # noqa: E402
    load_spacing_histograms, spacing_density,
)
from scripts.audit_completed_ring_campaign import (  # noqa: E402
    audit, read_json, sha256,
)
from scripts.build_network_wd_nonborn_size_spacing_figures import (  # noqa: E402
    _plot_angular,
)
from scripts.plot_hz0_0_ring_spacing_born_catalog import _plot_ratio  # noqa: E402
from scripts.summarize_lowerN_ring_spacing_born_catalog import (  # noqa: E402
    _profile, _spacing_class,
)


def plot_spacing(axis, edges, counts, total, *, color="#2878b5", alpha=1.0):
    density = spacing_density(counts, edges, total_spacing_count=total)
    axis.stairs(density, edges, color=color, alpha=alpha, linewidth=0.8)


def references(axis, *, legend=False):
    s = np.linspace(0, 4, 400)
    axis.plot(s, np.exp(-s), "k--", lw=0.8, label="Poisson")
    axis.plot(s, np.pi * s / 2 * np.exp(-np.pi * s**2 / 4),
              color="#d9534f", lw=0.8, label="GOE surmise")
    axis.set(xlim=(0, 4), ylim=(0, None))
    axis.grid(alpha=0.12)
    if legend:
        axis.legend(frameon=False, fontsize=7)


def render_case(directory: Path, case: dict, output: Path, *, dpi: int) -> dict:
    metrics = read_json(directory / "metrics.json")
    meta = read_json(directory / "metadata.json")
    spacing = read_json(directory / "ring_spacing_metadata.json")
    profile = load_profile(directory / "results_summary.npz")
    validate_profile(profile, rmse=metrics["born_RMSE_occupied"])
    edges, sectors, pooled = load_spacing_histograms(
        directory / "ring_spacing_histograms.npz", spacing
    )
    with np.load(directory / "results_summary.npz", allow_pickle=False) as a:
        arrays = {key: np.array(a[key]) for key in a.files}
    parameters = case["parameters"]
    label = (
        f"{case['family'].replace('_', ' ')}, {case['config_id']}, "
        r"$N_D=17$, $h_{z0}=0$, $t=10^6$"
    )
    coefficient_text = ", ".join(
        f"{key}={parameters[key]:.5g}" for key in ("hz", "j", "jpm", "j2", "jpm2")
    ) + f"; Jx/sqrt(N)={meta['Jx_effective']:.5g}"
    total = spacing["pooled"]
    figure = plt.figure(figsize=(12, 6.5))
    grid = figure.add_gridspec(2, 2, hspace=0.22, wspace=0.25)
    angular = figure.add_subplot(grid[0, 1])
    ratio = figure.add_subplot(grid[1, 1])
    spectral = figure.add_subplot(grid[:, 0])
    _plot_angular(angular, arrays)
    angular.set_ylabel(r"$P(\theta)$ [rad$^{-1}$]")
    angular.legend(frameon=False, ncol=2, fontsize=6.5)
    _plot_ratio(ratio, arrays, metrics, show_legend=True)
    ratio.set_xlabel(r"$\theta$")
    for counts, record in zip(sectors, spacing["sectors"]):
        plot_spacing(spectral, edges, counts, record["spacing_count"],
                     color="gray", alpha=0.14)
    plot_spacing(spectral, edges, pooled, total["spacing_count"])
    references(spectral, legend=True)
    spectral.set(xlabel=r"Unfolded spacing $s$", ylabel=r"Density $p(s)$",
                 title="Detector-only spacings: 45 resolved sectors")
    spectral.text(
        0.98, 0.69,
        f"mean gap ratio = {total['mean_adjacent_gap_ratio']:.4f}\n"
        f"KS (Poisson/GOE) = {total['ks_poisson']:.4f}/{total['ks_goe']:.4f}\n"
        f"mass above s=4 = {total['histogram_overflow']/total['spacing_count']:.3%}",
        transform=spectral.transAxes, ha="right", va="top", fontsize=8,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.8),
    )
    figure.suptitle(label + "\n" + coefficient_text, fontsize=11)
    figure.text(
        0.5, 0.018,
        "Each sector unfolded separately; blue pools spacings after unfolding. "
        "Gray: individual sectors.\n"
        "Exact degeneracies merged; cubic unfolding, 10% edge trim. "
        "S_Born uses 100 bins; plotted P/R use 64 bins.",
        ha="center", fontsize=8,
    )
    figure.subplots_adjust(top=0.86, bottom=0.14)
    figure.savefig(output / "diagnostics.png", dpi=dpi)
    figure.savefig(output / "diagnostics.pdf")
    plt.close(figure)

    figure, axes = plt.subplots(5, 9, figsize=(24, 12), sharex=True, sharey=True)
    per_momentum = {}
    for index, record in enumerate(spacing["sectors"]):
        sector = record["sector"]
        k = sector["momentum"]
        row = per_momentum.get(k, 0)
        per_momentum[k] = row + 1
        axis = axes[row, k]
        plot_spacing(axis, edges, sectors[index], record["spacing_count"])
        references(axis)
        parity = sector["reflection_parity"]
        parity_text = "" if parity is None else f", reflection={parity:+d}"
        axis.set_title(
            f"k={k}, Nup={sector['n_up']}{parity_text}\n"
            f"dim={sector['dimension']}, mean r={record['mean_r']:.3f}",
            fontsize=8,
        )
        axis.tick_params(labelsize=7)
        if row == 4:
            axis.set_xlabel("s")
        if k == 0:
            axis.set_ylabel("p(s)")
    figure.suptitle(label + " — individual detector sectors\n" + coefficient_text,
                   fontsize=13)
    figure.text(
        0.5, 0.01,
        "Blue: numerical; black dashed: Poisson; red: GOE surmise. "
        "Fixed Nup and nonredundant momenta k=0..8; reflection resolved at k=0.\n"
        "Five largest sectors per momentum; spin-flip and k/-k spectral copies omitted. "
        "Each density retains its omitted s>4 tail mass.",
        ha="center", fontsize=10,
    )
    figure.tight_layout(rect=(0, 0.055, 1, 0.94))
    figure.savefig(output / "resolved_sectors.png", dpi=dpi)
    figure.savefig(output / "resolved_sectors.pdf")
    plt.close(figure)
    return {
        "case_key": case["case_key"], "source_category": case["category"],
        "source_N": case["source_detector_n"], "N": 17,
        "source_S_born": case["source_s_born"], "S_born": metrics["S_born"],
        "S_born_change": metrics["S_born"] - case["source_s_born"],
        "RMSE": metrics["born_RMSE_occupied"],
        "mean_r": total["mean_adjacent_gap_ratio"],
        "ks_poisson": total["ks_poisson"], "ks_goe": total["ks_goe"],
        "spacing_count": total["spacing_count"],
        "histogram_overflow": total["histogram_overflow"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/zeus_ring_catalog_missing_n17.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=160)
    args = parser.parse_args()
    config = read_json(args.config)
    validation = audit(args.run_root, config, kind="catalog")
    args.output.mkdir(parents=True, exist_ok=False)
    classification = read_json(ROOT / "configs/hz0_0_ring_spacing_born_10x4.json")
    rows = []
    for case in config["cases"]:
        output = args.output / case["case_key"]
        output.mkdir()
        directory = args.run_root / "cases" / case["case_key"] / "N17"
        row = render_case(directory, case, output, dpi=args.dpi)
        row["current_profile_class"] = _profile(row["S_born"], row["RMSE"], classification)
        row["current_spacing_class"] = _spacing_class(
            row["mean_r"], row["ks_poisson"], row["ks_goe"], classification
        )[0]
        rows.append(row)
        print(f"Rendered {case['case_key']}: S_Born={row['S_born']:.6f}", flush=True)
    with (args.output / "summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "collection": str(args.run_root.relative_to(ROOT)) if args.run_root.is_absolute()
        else str(args.run_root), "source_validation": validation,
        "classification_rule": classification,
        "classification_note": "Descriptive comparisons, not significance tests; source categories are not reassigned to current results.",
        "rows": rows,
        "output_sha256": {str(p.relative_to(args.output)): sha256(p)
                          for p in sorted(args.output.rglob("*")) if p.is_file()},
        "defining_source_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in (
            Path(__file__), ROOT / "core/ring_spacing_report.py", args.config.resolve(),
            ROOT / "scripts/audit_completed_ring_campaign.py")},
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
