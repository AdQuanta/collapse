"""Shared 2x3 renderer for Born-ranked detector/dynamics atlases."""
from __future__ import annotations
from collections import Counter, defaultdict
import json, math, os
from pathlib import Path
from typing import Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from examples.build_sobol_flat_ranked_1x6_by_n import (
    CaseRecord, SpectralData, DETECTOR_N, GAP_FLOOR, VAB_POWER_FLOOR,
    _bloch_panel, _diagnostics_panel, _heatmap_panel, _multiplicity_panel,
)

WEIGHT_FLOOR = 1.0e-32

def degenerate_groups(energies: np.ndarray, tolerance: float):
    groups = []
    for index, energy in enumerate(energies):
        if not groups or abs(float(energy - energies[groups[-1][0]])) > tolerance:
            groups.append([index])
        else:
            groups[-1].append(index)
    return tuple(tuple(group) for group in groups)

def bandwidth_normalized_gaps(spectral: SpectralData):
    """Return |E_a-E_b|/(E_max-E_min), with a zero-bandwidth branch."""
    bandwidth = float(np.ptp(spectral.energies))
    if bandwidth > 0.0:
        gaps = np.abs(
            spectral.energies[:, None] - spectral.energies[None, :]
        ) / bandwidth
        gaps = np.clip(gaps, 0.0, 1.0)
        return gaps, bandwidth, False
    return np.zeros(
        (spectral.energies.size, spectral.energies.size), dtype=float
    ), 0.0, True


def multiplicity_resolved_vab_weight(spectral: SpectralData):
    """Partition all V_ab power by the multiplicity of its two endpoints.

    W_m = [sum_{g:m_g=m}(||P_g V||_F^2 + ||V P_g||_F^2)]/(2||V||_F^2).
    Every matrix element contributes half its normalized power to the
    multiplicity of each endpoint, so sum_m W_m = 1.  This symmetric definition
    remains valid when V is non-Hermitian.
    """
    weights = defaultdict(float)
    for group in degenerate_groups(spectral.energies, spectral.degeneracy_tolerance):
        indices = np.asarray(group, dtype=int)
        row_weight = float(np.sum(spectral.vab_power[indices, :]))
        column_weight = float(np.sum(spectral.vab_power[:, indices]))
        weights[len(group)] += 0.5 * (row_weight + column_weight)
    weights.setdefault(1, 0.0)
    total = float(sum(weights.values()))
    if not np.isfinite(total) or abs(total - 1.0) > 1.0e-12:
        raise RuntimeError(f"multiplicity-resolved Vab weights sum to {total}, expected 1")
    return dict(sorted((m, value / total) for m, value in weights.items()))

def multiplicity_panel_all_ticks(axis: plt.Axes, spectral: SpectralData):
    counts = Counter(spectral.multiplicities)
    multiplicities = np.asarray(sorted(counts), dtype=int)
    values = np.asarray([counts[m] for m in multiplicities], dtype=int)
    positions = np.arange(len(multiplicities))
    axis.bar(
        positions, values, width=0.78, color="#4c78a8",
        edgecolor="white", linewidth=0.45,
    )
    axis.set_xticks(positions, [str(m) for m in multiplicities])
    if len(multiplicities) > 9:
        axis.tick_params(axis="x", labelrotation=45, labelsize=7)
    axis.set(
        title="Detector degeneracy multiplicities",
        xlabel="subspace multiplicity $m_g$",
        ylabel="number of energy subspaces",
    )
    axis.grid(axis="y", alpha=0.20)
    degenerate = [m for m in spectral.multiplicities if m > 1]
    axis.text(
        0.97, 0.96,
        "\n".join((
            rf"$N_D={DETECTOR_N}$, $\dim={1 << DETECTOR_N}$",
            rf"$N_{{\rm groups}}={len(spectral.multiplicities)}$",
            rf"$N_{{m>1}}={len(degenerate)}$",
            rf"$m_{{\max}}={max(spectral.multiplicities)}$",
            rf"$f_{{\rm deg}}={sum(degenerate)/(1 << DETECTOR_N):.3f}$",
        )),
        transform=axis.transAxes, ha="right", va="top", fontsize=7.2,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    axis.set_box_aspect(1)


def energy_gap_weight_panel(axis: plt.Axes, spectral: SpectralData):
    """Plot V_ab power in a strict-degeneracy bin plus normalized-gap bins."""
    edges = np.linspace(0.0, 1.0, 41)
    normalized_gaps, bandwidth, zero_bandwidth = bandwidth_normalized_gaps(spectral)
    absolute_gaps = np.abs(
        spectral.energies[:, None] - spectral.energies[None, :]
    )
    degenerate_mask = absolute_gaps <= spectral.degeneracy_tolerance
    exact_weight = float(np.sum(spectral.vab_power[degenerate_mask]))
    gap_weights, _ = np.histogram(
        normalized_gaps[~degenerate_mask],
        bins=edges,
        weights=spectral.vab_power[~degenerate_mask],
    )
    total = float(exact_weight + np.sum(gap_weights))
    if not np.isfinite(total) or abs(total - 1.0) > 1.0e-12:
        raise RuntimeError(f"energy-gap Vab histogram sums to {total}, expected 1")
    exact_weight = exact_weight / total
    gap_weights = gap_weights / total
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    degenerate_center = -0.05
    axis.bar(
        [degenerate_center], [exact_weight], width=0.035, align="center",
        color="#e45756", edgecolor="white", linewidth=0.45,
        label=r"strictly degenerate: $|E_a-E_b|\leq\epsilon_{\rm deg}$",
    )
    axis.bar(
        centers, gap_weights, width=0.92 * widths, align="center",
        color="#4c78a8", edgecolor="white", linewidth=0.35,
        label=r"nondegenerate gap bins",
    )
    tolerance_normalized = (
        spectral.degeneracy_tolerance / bandwidth if bandwidth > 0.0 else 0.0
    )
    axis.set(
        title=r"$V_{ab}$ weight versus normalized energy difference",
        xlabel=r"$\delta_{ab}=|E_a-E_b|/(E_{\max}-E_{\min})$",
        ylabel=r"$W_k=\sum_{\delta_{ab}\in B_k}|V_{ab}|^2/\mathrm{Tr}(VV^\dagger)$",
        xlim=(-0.075, 1.0),
        ylim=(0.0, max(1.0e-12, 1.08 * exact_weight, 1.08 * float(np.max(gap_weights)))),
    )
    axis.set_xticks(
        [degenerate_center, 0.0, 0.25, 0.50, 0.75, 1.0],
        ["deg.\n" + r"$\leq\epsilon_{\rm deg}$", "0", "0.25", "0.50", "0.75", "1"],
    )
    axis.axvline(-0.018, color="0.55", linewidth=0.7)
    axis.grid(axis="y", alpha=0.20)
    axis.text(
        0.97, 0.96,
        "\n".join((
            rf"$W_{{\rm deg}}+\sum_k W_k={exact_weight + np.sum(gap_weights):.6f}$",
            rf"$W(\delta_{{ab}}\leq\epsilon_{{\rm deg}})={exact_weight:.3g}$",
            rf"$40$ nondegenerate bins; diagonal included in $W_{{\rm deg}}$",
            "zero bandwidth: all weight at " + r"$\delta=0$" if zero_bandwidth else rf"$\Delta E={bandwidth:.3g}$",
        )),
        transform=axis.transAxes, ha="right", va="top", fontsize=7.2,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    axis.set_box_aspect(1)
    return {
        "edges": edges.tolist(),
        "weights": gap_weights.tolist(),
        "sum": float(exact_weight + np.sum(gap_weights)),
        "exact_degenerate_weight": exact_weight,
        "degeneracy_tolerance_normalized": tolerance_normalized,
        "bandwidth": bandwidth,
        "zero_bandwidth": zero_bandwidth,
    }

def render_case_2x3(
    record: CaseRecord,
    spectral: SpectralData,
    arrays: dict[str, np.ndarray],
    *,
    output: Path,
    force: bool,
    dpi: int,
    max_bloch_points: int,
):
    if output.is_file() and not force:
        return {"status": "existing", "output_path": str(output)}
    output.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(18.0, 10.0), dpi=dpi, constrained_layout=False)
    grid = figure.add_gridspec(
        2, 3, left=0.045, right=0.985, bottom=0.07, top=0.88,
        wspace=0.24, hspace=0.30, width_ratios=(1,1,1), height_ratios=(1,1),
    )

    normalized_gaps, _, _ = bandwidth_normalized_gaps(spectral)
    gap_display = -np.log10(np.maximum(normalized_gaps, GAP_FLOOR))
    np.fill_diagonal(gap_display, np.nan)
    gap_cmap = plt.get_cmap("magma").copy(); gap_cmap.set_bad("white")
    gap_axis = _heatmap_panel(
        figure, grid[0,0], gap_display,
        title=rf"Energy proximity ($N_D={DETECTOR_N}$)", cmap=gap_cmap,
        vmin=0.0, vmax=-math.log10(GAP_FLOOR),
        colorbar_label=r"$-\log_{10}(|E_a-E_b|/\Delta E)$",
    )

    multiplicity_axis = figure.add_subplot(grid[0,1])
    multiplicity_panel_all_ticks(multiplicity_axis, spectral)
    _diagnostics_panel(figure, grid[0,2], arrays, record)

    vab_axis = _heatmap_panel(
        figure, grid[1,0], np.log10(np.maximum(spectral.vab_power, VAB_POWER_FLOOR)),
        title=rf"Interaction $V_{{ab}}$ ($N_D={DETECTOR_N}$)", cmap="viridis",
        vmin=math.log10(VAB_POWER_FLOOR), vmax=0.0,
        colorbar_label=r"$\log_{10}(|V_{ab}|^2/\mathrm{Tr}\,VV^\dagger)$",
    )
    weight_axis = figure.add_subplot(grid[1,1])
    gap_histogram = energy_gap_weight_panel(weight_axis, spectral)
    _bloch_panel(figure, grid[1,2], arrays, max_bloch_points)

    figure.canvas.draw()
    gap_box, vab_box = gap_axis.get_position(), vab_axis.get_position()
    if not (
        abs(gap_box.width-vab_box.width) < 1e-8
        and abs(gap_box.height-vab_box.height) < 1e-8
        and np.allclose(gap_axis.get_xlim(), vab_axis.get_xlim())
        and np.allclose(gap_axis.get_ylim(), vab_axis.get_ylim())
        and gap_axis.get_aspect() == vab_axis.get_aspect()
    ):
        raise RuntimeError("heatmap geometry assertion failed")

    family = r"$J_y=0$" if record.family == "jy_zero" else r"$J_y>0$"
    figure.suptitle(
        rf"Born rank {record.rank}: {family}, dynamics $N={record.dynamics_n}$, {record.config_id}, "
        rf"$S_{{\rm Born}}={record.s_born:.4f}$" + "\n"
        + rf"$h_z={record.hz:.3g}$, $J={record.j:.3g}$, $J_\pm={record.jpm:.3g}$, "
        + rf"$J_x={record.jx:.3g}$, $J_y={record.jy:.3g}$, $t=10^6$",
        fontsize=13.0, fontweight="bold", y=0.975,
    )
    temp = output.with_name(output.stem + f".tmp.{os.getpid()}.png")
    figure.savefig(temp, dpi=dpi, facecolor="white")
    plt.close(figure); temp.replace(output)
    return {
        "status": "rendered", "output_path": str(output),
        "image_width_px": int(round(18*dpi)), "image_height_px": int(round(10*dpi)),
        "heatmap_box_width": gap_box.width, "heatmap_box_height": gap_box.height,
        "gap_weight_histogram_json": json.dumps(gap_histogram, sort_keys=True),
        "gap_weight_sum": float(gap_histogram["sum"]),
        "exact_degenerate_weight": float(gap_histogram["exact_degenerate_weight"]),
    }


