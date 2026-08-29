"""Render one revised 2x3 atlas sample with detector level statistics.

The established periodic N_D=8 full-detector spectrum and degeneracy tolerance
are reused. Symmetry sectors remain mixed, so RMT curves are descriptive.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig-vab-spacing-sample"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from core.level_spacing import (
    MEAN_R_GOE, MEAN_R_GUE, MEAN_R_POISSON,
    compute_level_spacing_ratios, compute_level_spacings,
    compute_unfolded_spacings, poisson_spacing_distribution,
    wigner_spacing_distribution,
)
from core.sobol_coupling_scan import _diagnostics
from scripts.build_sobol_flat_ranked_1x6_by_n import (
    CaseRecord, DETECTOR_N, GAP_FLOOR, VAB_POWER_FLOOR,
    _diagnostics_panel, _heatmap_panel, compute_spectral,
)
from scripts.build_vab_coupling_raw_flat_ranked_1x6 import inventory, load_values
from scripts.build_vab_coupling_raw_flat_ranked_2x3 import CAMPAIGN, INDEX, fit_arrays
from scripts.ranked_atlas_2x3 import (
    bandwidth_normalized_gaps, multiplicity_panel_all_ticks,
)

OUTPUT = (
    ROOT / "reports" / "vab_coupling_group_atlas_2026-07-28"
    / "sample_log_gap_spacing_no_bloch_2026-08-02"
)


def log_gap_weight_data(spectral):
    """Partition normalized V_ab power into degeneracy and log-gap bins."""
    normalized, bandwidth, zero_bandwidth = bandwidth_normalized_gaps(spectral)
    absolute = np.abs(spectral.energies[:, None] - spectral.energies[None, :])
    degenerate = absolute <= spectral.degeneracy_tolerance
    gaps = normalized[~degenerate]
    power = spectral.vab_power[~degenerate]
    exact = float(np.sum(spectral.vab_power[degenerate]))
    lower = 1.0e-12
    if gaps.size:
        lower = max(lower, 10.0 ** math.floor(math.log10(float(np.min(gaps)))))
        lower = min(lower, 1.0e-2)
    edges = np.geomspace(lower, 1.0, 33)
    weights, _ = np.histogram(
        np.clip(gaps, edges[0], edges[-1]), bins=edges, weights=power
    )
    total = float(exact + np.sum(weights))
    if not np.isfinite(total) or abs(total - 1.0) > 1.0e-12:
        raise RuntimeError(f"Vab gap weights sum to {total}, expected one")
    return {
        "edges": edges, "weights": weights / total, "exact": exact / total,
        "sum": 1.0, "bandwidth": bandwidth,
        "zero_bandwidth": zero_bandwidth, "lower": lower,
    }


def plot_log_gap_weight(axis, spectral):
    """Draw a categorical degeneracy bin before logarithmic physical bins."""
    data = log_gap_weight_data(spectral)
    edges = data["edges"]
    centers = np.sqrt(edges[:-1] * edges[1:])
    deg_left, deg_right = data["lower"] / 100.0, data["lower"] / 10.0
    deg_center = math.sqrt(deg_left * deg_right)
    axis.bar(
        [deg_center], [data["exact"]], width=[deg_right - deg_left],
        color="#e45756", edgecolor="white", linewidth=0.45,
        label=r"strict degeneracy: $|E_a-E_b|\leq\epsilon_{\rm deg}$",
    )
    axis.bar(
        centers, data["weights"], width=0.90 * np.diff(edges),
        color="#4c78a8", edgecolor="white", linewidth=0.35,
        label="nondegenerate log bins",
    )
    axis.set_xscale("log")
    axis.set_xlim(deg_left / 1.4, 1.15)
    axis.set_ylim(
        0.0,
        max(1.0e-12, 1.10 * data["exact"], 1.10 * float(np.max(data["weights"]))),
    )
    axis.axvline(
        math.sqrt(deg_right * data["lower"]),
        color="0.45", linestyle="--", linewidth=0.8,
    )
    powers = list(range(int(math.ceil(math.log10(data["lower"]))), 1))
    if len(powers) > 6:
        powers = powers[::2]
        if powers[-1] != 0:
            powers.append(0)
    axis.set_xticks(
        [deg_center, *[10.0**power for power in powers]],
        [r"deg. $\leq\epsilon_{\rm deg}$",
         *[rf"$10^{{{power}}}$" for power in powers]],
    )
    axis.tick_params(axis="x", labelrotation=22, labelsize=7)
    axis.set(
        title=r"$V_{ab}$ weight versus detector energy difference",
        xlabel=r"$\delta_{ab}=|E_a-E_b|/(E_{\max}-E_{\min})$ (log scale)",
        ylabel=r"$W_k=\sum_{\delta_{ab}\in B_k}|V_{ab}|^2/\mathrm{Tr}(VV^\dagger)$",
    )
    axis.grid(axis="y", alpha=0.20)
    axis.text(
        0.97, 0.96,
        "\n".join((
            rf"$W_{{\rm deg}}+\sum_kW_k={data['sum']:.6f}$",
            rf"$W_{{\rm deg}}={data['exact']:.3g}$; diagonal included",
            rf"$\epsilon_{{\rm deg}}={spectral.degeneracy_tolerance:.2e}$",
            "zero bandwidth" if data["zero_bandwidth"]
            else rf"$\Delta E={data['bandwidth']:.3g}$",
        )),
        transform=axis.transAxes, ha="right", va="top", fontsize=6.9,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    axis.set_box_aspect(1)
    return data



def log_resonance_weight_data(spectral, hz0: float):
    """Partition V_ab power by detuning from the qubit-flip resonance."""
    bandwidth = float(np.ptp(spectral.energies))
    if not bandwidth > 0.0:
        raise RuntimeError("resonance histogram requires nonzero bandwidth")
    energy_gaps = np.abs(spectral.energies[:, None] - spectral.energies[None, :])
    target = 2.0 * abs(float(hz0))
    detuning = np.abs(energy_gaps - target)
    resonant = detuning <= spectral.degeneracy_tolerance
    normalized = detuning / bandwidth
    values = normalized[~resonant]
    power = spectral.vab_power[~resonant]
    exact = float(np.sum(spectral.vab_power[resonant]))
    lower = 1.0e-12
    if values.size:
        lower = max(lower, 10.0 ** math.floor(math.log10(float(np.min(values)))))
        lower = min(lower, 1.0e-2)
    upper = max(1.0, float(np.max(values)) if values.size else 1.0)
    edges = np.geomspace(lower, upper, 33)
    weights, _ = np.histogram(
        np.clip(values, edges[0], edges[-1]), bins=edges, weights=power
    )
    total = float(exact + np.sum(weights))
    if not np.isfinite(total) or abs(total - 1.0) > 1.0e-12:
        raise RuntimeError(f"resonance-detuning weights sum to {total}, expected one")
    return {
        "edges": edges, "weights": weights / total, "exact": exact / total,
        "sum": 1.0, "bandwidth": bandwidth, "lower": lower, "target": target,
    }


def plot_log_resonance_weight(axis, spectral, hz0: float):
    """Draw exact-resonance weight plus logarithmic detuning bins."""
    data = log_resonance_weight_data(spectral, hz0)
    edges = data["edges"]
    centers = np.sqrt(edges[:-1] * edges[1:])
    special_left, special_right = data["lower"] / 100.0, data["lower"] / 10.0
    special_center = math.sqrt(special_left * special_right)
    axis.bar(
        [special_center], [data["exact"]], width=[special_right - special_left],
        color="#e45756", edgecolor="white", linewidth=0.45,
        label=r"exact resonance: $\left||E_a-E_b|-2|h_{z0}|\right|\leq\epsilon_{\rm spec}$",
    )
    axis.bar(
        centers, data["weights"], width=0.90 * np.diff(edges),
        color="#4c78a8", edgecolor="white", linewidth=0.35,
        label="nonresonant log bins",
    )
    axis.set_xscale("log")
    axis.set_xlim(special_left / 1.4, edges[-1] * 1.15)
    axis.set_ylim(
        0.0,
        max(1.0e-12, 1.10 * data["exact"], 1.10 * float(np.max(data["weights"]))),
    )
    axis.axvline(
        math.sqrt(special_right * data["lower"]),
        color="0.45", linestyle="--", linewidth=0.8,
    )
    powers = list(range(int(math.ceil(math.log10(data["lower"]))), 1))
    if len(powers) > 6:
        powers = powers[::2]
        if powers[-1] != 0:
            powers.append(0)
    axis.set_xticks(
        [special_center, *[10.0**power for power in powers]],
        [r"res. $\leq\epsilon_{\rm spec}$",
         *[rf"$10^{{{power}}}$" for power in powers]],
    )
    axis.tick_params(axis="x", labelrotation=22, labelsize=7)
    axis.set(
        title=r"$V_{ab}$ weight versus qubit-flip detuning",
        xlabel=(
            r"$\delta^{(0)}_{ab}=\left||E_a-E_b|-2|h_{z0}|\right|/"
            r"(E_{\max}-E_{\min})$ (log scale)"
        ),
        ylabel=r"$W_k=\sum_{\delta^{(0)}_{ab}\in B_k}|V_{ab}|^2/\mathrm{Tr}(VV^\dagger)$",
    )
    axis.grid(axis="y", alpha=0.20)
    axis.text(
        0.97, 0.96,
        "\n".join((
            rf"$W_{{\rm res}}+\sum_kW_k={data['sum']:.6f}$",
            rf"$W_{{\rm res}}={data['exact']:.3g}$",
            rf"$2|h_{{z0}}|={data['target']:.3g}$",
            rf"$\epsilon_{{\rm spec}}={spectral.degeneracy_tolerance:.2e}$",
            r"$E_a,E_b$ from $H_D$ only",
        )),
        transform=axis.transAxes, ha="right", va="top", fontsize=6.8,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    axis.set_box_aspect(1)
    return data


def level_spacing_data(spectral):
    """Compute unfolded spacings, Atas ratio, and L1 reference distances."""
    unfolded = compute_unfolded_spacings(
        spectral.energies, tol=spectral.degeneracy_tolerance,
        degree=3, trim_fraction=0.10,
    )
    raw = compute_level_spacings(
        spectral.energies, tol=spectral.degeneracy_tolerance
    )
    ratios = compute_level_spacing_ratios(raw)
    if not unfolded.size or not ratios.size:
        edges = np.linspace(0.0, 4.0, 31)
        return {
            "unfolded": unfolded,
            "edges": edges,
            "histogram": np.zeros(edges.size - 1, dtype=float),
            "mean_ratio": float("nan"),
            "distances": {
                "Poisson": float("nan"),
                "GOE": float("nan"),
                "GUE": float("nan"),
            },
            "best": "undefined",
            "defined": False,
        }
    upper = max(4.0, float(np.percentile(unfolded, 99.5)))
    upper = min(upper, max(4.0, float(np.max(unfolded))))
    edges = np.linspace(0.0, upper, 31)
    histogram, _ = np.histogram(unfolded, bins=edges, density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    references = {
        "Poisson": poisson_spacing_distribution(centers),
        "GOE": wigner_spacing_distribution(centers, beta=1),
        "GUE": wigner_spacing_distribution(centers, beta=2),
    }
    distances = {
        label: float(np.sum(np.abs(histogram - values) * widths))
        for label, values in references.items()
    }
    return {
        "unfolded": unfolded, "edges": edges, "histogram": histogram,
        "mean_ratio": float(np.mean(ratios)), "distances": distances,
        "best": min(distances, key=distances.get),
        "defined": True,
    }


def plot_level_spacings(axis, spectral):
    """Plot unfolded full-spectrum spacings and parameter-free references."""
    data = level_spacing_data(spectral)
    edges = data["edges"]
    centers = 0.5 * (edges[:-1] + edges[1:])
    axis.bar(
        centers, data["histogram"], width=0.92 * np.diff(edges),
        color="#9ecae1", edgecolor="white", linewidth=0.45,
        label="unfolded detector spacings",
    )
    grid = np.linspace(0.0, float(edges[-1]), 600)
    axis.plot(
        grid, poisson_spacing_distribution(grid),
        color="#222222", linestyle="--", linewidth=1.5, label="Poisson",
    )
    axis.plot(
        grid, wigner_spacing_distribution(grid, beta=1),
        color="#e45756", linestyle="-", linewidth=1.5, label="GOE",
    )
    axis.plot(
        grid, wigner_spacing_distribution(grid, beta=2),
        color="#59a14f", linestyle="-.", linewidth=1.5, label="GUE",
    )
    distance = data["distances"]
    axis.set(
        title="Unfolded detector level spacings",
        xlabel=r"unfolded spacing $s$ ($\langle s\rangle=1$)",
        ylabel=r"density $p(s)$",
        xlim=(0.0, float(edges[-1])),
    )
    axis.set_ylim(bottom=0.0)
    axis.grid(axis="y", alpha=0.20)
    axis.legend(loc="upper right", fontsize=7.0, frameon=False)
    if data["defined"]:
        annotation = "\n".join((
            rf"Atas $\langle\widetilde r\rangle={data['mean_ratio']:.3f}$",
            (
                rf"Poisson/GOE/GUE: ${MEAN_R_POISSON:.3f}/"
                rf"{MEAN_R_GOE:.3f}/{MEAN_R_GUE:.3f}$"
            ),
            (
                rf"$D_1(P,\mathrm{{GOE}},\mathrm{{GUE}})="
                rf"{distance['Poisson']:.2f}/{distance['GOE']:.2f}/"
                rf"{distance['GUE']:.2f}$"
            ),
            rf"best displayed reference: {data['best']}",
            rf"{data['unfolded'].size} spacings; cubic unfold, 10\% edge trim",
            "full spectrum; symmetry sectors mixed",
        ))
    else:
        annotation = "\n".join((
            r"Atas $\langle\widetilde r\rangle$: undefined",
            r"$D_1$ reference distances: undefined",
            "no empirical fit",
            "one resolved detector level",
            "full spectrum; symmetry sectors mixed",
        ))
        axis.text(
            0.50, 0.42,
            "No resolved spacings\n$H_D$ has one energy level",
            transform=axis.transAxes, ha="center", va="center", fontsize=9.0,
            bbox={"facecolor": "white", "edgecolor": "0.75", "alpha": 0.94, "pad": 4},
        )
    axis.text(
        0.97, 0.60, annotation,
        transform=axis.transAxes, ha="right", va="top", fontsize=6.7,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    axis.set_box_aspect(1)
    return data

def render_sample(
    record,
    spectral,
    arrays,
    output,
    dpi,
    hz0: float | None = None,
    title_label: str = "Sample from 2026-07-28 atlas",
):
    """Render the requested six panels in a true 2x3 layout."""
    output.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(18.0, 10.0), dpi=dpi)
    grid = figure.add_gridspec(
        2, 3,
        left=0.045, right=0.985, bottom=0.07, top=0.88,
        wspace=0.25, hspace=0.30,
        width_ratios=(1.0, 1.0, 1.0),
    )

    normalized, _, _ = bandwidth_normalized_gaps(spectral)
    gap_values = -np.log10(np.maximum(normalized, GAP_FLOOR))
    np.fill_diagonal(gap_values, np.nan)
    gap_cmap = plt.get_cmap("magma").copy()
    gap_cmap.set_bad("white")
    gap_axis = _heatmap_panel(
        figure,
        grid[0, 0],
        gap_values,
        title=rf"Energy proximity ($N_D={DETECTOR_N}$)",
        cmap=gap_cmap,
        vmin=0.0,
        vmax=-math.log10(GAP_FLOOR),
        colorbar_label=r"$-\log_{10}(|E_a-E_b|/\Delta E)$",
    )
    multiplicity_panel_all_ticks(figure.add_subplot(grid[0, 1]), spectral)
    _diagnostics_panel(figure, grid[0, 2], arrays, record)

    vab_axis = _heatmap_panel(
        figure,
        grid[1, 0],
        np.log10(np.maximum(spectral.vab_power, VAB_POWER_FLOOR)),
        title=rf"Interaction $V_{{ab}}$ ($N_D={DETECTOR_N}$)",
        cmap="viridis",
        vmin=math.log10(VAB_POWER_FLOOR),
        vmax=0.0,
        colorbar_label=r"$\log_{10}(|V_{ab}|^2/\mathrm{Tr}\,VV^\dagger)$",
    )
    gap_histogram = (
        plot_log_gap_weight(figure.add_subplot(grid[1, 1]), spectral)
        if hz0 is None
        else plot_log_resonance_weight(figure.add_subplot(grid[1, 1]), spectral, hz0)
    )
    spacing = plot_level_spacings(
        figure.add_subplot(grid[1, 2]), spectral
    )


    figure.canvas.draw()
    gap_box = gap_axis.get_position()
    vab_box = vab_axis.get_position()
    if not (
        abs(gap_box.width - vab_box.width) < 1.0e-8
        and abs(gap_box.height - vab_box.height) < 1.0e-8
        and np.allclose(gap_axis.get_xlim(), vab_axis.get_xlim())
        and np.allclose(gap_axis.get_ylim(), vab_axis.get_ylim())
        and gap_axis.get_aspect() == vab_axis.get_aspect()
    ):
        raise RuntimeError("heatmap geometry assertion failed")

    central_field = "" if hz0 is None else rf", $h_{{z0}}={hz0:.3g}$"
    figure.suptitle(
        rf"{title_label}: Born rank {record.rank}, "
        rf"dynamics $N={record.dynamics_n}$, $S_{{\rm Born}}={record.s_born:.4f}$"
        + "\n"
        + rf"$h_z={record.hz:.3g}$" + central_field + rf", $J={record.j:.3g}$, "
        + rf"$J_\pm={record.jpm:.3g}$, $J_x={record.jx:.3g}$, "
        + rf"$J_y={record.jy:.3g}$, $t=10^6$",
        fontsize=13.0,
        fontweight="bold",
        y=0.975,
    )
    temporary = output.with_name(output.stem + f".tmp.{os.getpid()}.png")
    figure.savefig(temporary, dpi=dpi, facecolor="white")
    plt.close(figure)
    temporary.replace(output)
    return {
        "output": str(output.resolve()),
        "heatmap_geometry_equal": True,
        "heatmap_box_width": gap_box.width,
        "heatmap_box_height": gap_box.height,
        "gap_weight_sum": gap_histogram["sum"],
        "special_weight": gap_histogram["exact"],
        "special_weight_kind": "degenerate" if hz0 is None else "resonant",
        "mean_atas_ratio": spacing["mean_ratio"],
        "level_spacing_l1": spacing["distances"],
        "best_level_spacing_reference": spacing["best"],
    }



def build(rank, output, dpi):
    """Load one existing atlas case and create a new, non-overwriting sample."""
    cases, _ = inventory(INDEX, CAMPAIGN, output)
    selected = next((case for case in cases if case.rank == rank), None)
    if selected is None:
        raise ValueError(f"rank {rank} is unavailable in the traced atlas")

    metrics, arrays = _diagnostics(load_values(Path(selected.raw_path)), 64)
    fits, wg, wc = fit_arrays(arrays["theta"])
    arrays.update(fits)
    delta = abs(float(metrics["S_born"]) - selected.source_s_born)
    if delta > 1.0e-12:
        raise RuntimeError(f"S_born mismatch {delta:.3e}")

    record = CaseRecord(
        family="jy_zero",
        dynamics_n=selected.n,
        config_id=f"hz={selected.hz:g},J={selected.j:g},Jpm={selected.jpm:g}",
        s_born=float(metrics["S_born"]),
        born_rmse=float(metrics["born_RMSE_occupied"]),
        hz=selected.hz,
        j=selected.j,
        jpm=selected.jpm,
        jx=0.01,
        jy=0.0,
        source_dir=str(Path(selected.raw_path).parent),
        rank=selected.rank,
        within_n_rank=selected.rank,
        output_path="",
    )
    spectral = compute_spectral(record)
    result = render_sample(
        record,
        spectral,
        arrays,
        output / f"sample_rank_{rank:04d}_loggap_spacing_no_bloch.png",
        dpi,

    )
    result.update({
        "source_raw": str(Path(selected.raw_path).resolve()),
        "source_report": str(
            (ROOT / "reports" / "vab_coupling_group_atlas_2026-07-28").resolve()
        ),
        "rank": rank,
        "parameters": {
            "N": selected.n,
            "detector_N": DETECTOR_N,
            "hz": selected.hz,
            "J": selected.j,
            "Jpm": selected.jpm,
            "Jx": 0.01,
            "Jy": 0.0,
            "t": selected.t,
        },
        "S_born": record.s_born,
        "born_rmse": record.born_rmse,
        "wg_fourier_discrepancy": float(wg["objective"]),
        "wc_fourier_discrepancy": float(wc["objective"]),
        "spectral_validation": spectral.validation,
        "level_spacing_convention": (
            "full ND=8 detector spectrum; numerical degeneracies clustered; "
            "cubic unfolding; 10% edge trim; symmetry sectors not separated"
        ),
    })
    output.mkdir(parents=True, exist_ok=True)
    (output / "sample_metadata.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rank",
        type=int,
        default=471,
        help="rank 471 visibly exercises the strict-degeneracy bin",
    )
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--dpi", type=int, default=160)

    args = parser.parse_args()
    print(json.dumps(
        build(args.rank, args.output, args.dpi),
        indent=2,
    ))


if __name__ == "__main__":
    main()






