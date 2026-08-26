"""Build one approval sample for the second-neighbor Sobol 2x3 atlas."""

from __future__ import annotations

from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-second-neighbor-mean-spacing-sample")
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from examples.build_sobol_flat_ranked_1x6_by_n import (  # noqa: E402
    CaseRecord,
    GAP_FLOOR,
    SpectralData,
    VAB_POWER_FLOOR,
    _diagnostics_panel,
    _heatmap_panel,
    _load_result_arrays,
    compute_spectral,
    inventory,
)
from examples.build_vab_coupling_level_spacing_sample import (  # noqa: E402
    plot_level_spacings,
)
from examples.ranked_atlas_2x3 import (  # noqa: E402
    bandwidth_normalized_gaps,
    degenerate_groups,
    multiplicity_panel_all_ticks,
)


SOURCE = ROOT / "work" / "zeus_sobol_second_neighbor_hz0_0_N14_20260805_224342"
OUTPUT = (
    ROOT
    / "reports"
    / "second_neighbor_mean_spacing_log_sample_2x3_2026-08-06"
)
SPECTRAL_N = 10


def mean_spacing_gap_weight_data(spectral: SpectralData) -> dict[str, Any]:
    """Bin normalized ``|V_ab|^2`` by ``|E_a-E_b|/<s>``.

    ``<s>`` is the arithmetic mean of adjacent spacings between numerically
    resolved detector-energy subspaces. Exact/numerical degeneracies are first
    clustered with ``spectral.degeneracy_tolerance`` and retain a separate
    weight bin, including diagonal matrix elements.
    """

    groups = degenerate_groups(spectral.energies, spectral.degeneracy_tolerance)
    resolved_energies = np.asarray(
        [float(np.mean(spectral.energies[np.asarray(group)])) for group in groups],
        dtype=float,
    )
    if resolved_energies.size < 2:
        raise RuntimeError("mean-spacing normalization requires two resolved levels")
    resolved_spacings = np.diff(resolved_energies)
    if np.any(resolved_spacings <= 0.0):
        raise RuntimeError("resolved detector energies are not strictly increasing")
    mean_spacing = float(np.mean(resolved_spacings))
    if not np.isfinite(mean_spacing) or mean_spacing <= 0.0:
        raise RuntimeError("mean detector spacing must be finite and positive")

    absolute_gaps = np.abs(
        spectral.energies[:, None] - spectral.energies[None, :]
    )
    degenerate_mask = absolute_gaps <= spectral.degeneracy_tolerance
    normalized_gaps = absolute_gaps / mean_spacing
    nondegenerate = normalized_gaps[~degenerate_mask]
    if not nondegenerate.size:
        raise RuntimeError("no nondegenerate detector-energy differences")
    minimum = float(np.min(nondegenerate))
    maximum = float(np.max(nondegenerate))
    lower = max(1.0e-12, 10.0 ** math.floor(math.log10(minimum)))
    upper = maximum if maximum > lower else 10.0 * lower
    edges = np.geomspace(lower, upper, 41)
    exact_weight = float(np.sum(spectral.vab_power[degenerate_mask]))
    weights, _ = np.histogram(
        nondegenerate,
        bins=edges,
        weights=spectral.vab_power[~degenerate_mask],
    )
    total = float(exact_weight + np.sum(weights))
    if not np.isfinite(total) or abs(total - 1.0) > 1.0e-12:
        raise RuntimeError(f"mean-spacing Vab histogram sums to {total}, expected 1")

    return {
        "edges": edges,
        "weights": weights / total,
        "exact": exact_weight / total,
        "sum": 1.0,
        "mean_spacing": mean_spacing,
        "resolved_level_count": int(resolved_energies.size),
        "resolved_spacing_count": int(resolved_spacings.size),
        "minimum_normalized_gap": minimum,
        "maximum_normalized_gap": maximum,
        "histogram_lower": lower,
        "histogram_upper": upper,
        "degeneracy_tolerance_normalized": (
            spectral.degeneracy_tolerance / mean_spacing
        ),
    }


def mean_spacing_resonance_weight_data(
    spectral: SpectralData, *, hz0: float
) -> dict[str, Any]:
    """Bin ``|V_ab|^2`` by detuning from ``2|hz0|``, normalized by ``<s>``."""

    groups = degenerate_groups(spectral.energies, spectral.degeneracy_tolerance)
    resolved_energies = np.asarray(
        [float(np.mean(spectral.energies[np.asarray(group)])) for group in groups],
        dtype=float,
    )
    if resolved_energies.size < 2:
        raise RuntimeError("mean-spacing normalization requires two resolved levels")
    resolved_spacings = np.diff(resolved_energies)
    if np.any(resolved_spacings <= 0.0):
        raise RuntimeError("resolved detector energies are not strictly increasing")
    mean_spacing = float(np.mean(resolved_spacings))
    if not np.isfinite(mean_spacing) or mean_spacing <= 0.0:
        raise RuntimeError("mean detector spacing must be finite and positive")

    absolute_gaps = np.abs(
        spectral.energies[:, None] - spectral.energies[None, :]
    )
    target_gap = 2.0 * abs(float(hz0))
    absolute_detuning = np.abs(absolute_gaps - target_gap)
    resonance_mask = absolute_detuning <= spectral.degeneracy_tolerance
    normalized_detuning = absolute_detuning / mean_spacing
    nonresonant = normalized_detuning[~resonance_mask]
    if not nonresonant.size:
        raise RuntimeError("no nonresonant detector-energy differences")
    minimum = float(np.min(nonresonant))
    maximum = float(np.max(nonresonant))
    lower = max(1.0e-12, 10.0 ** math.floor(math.log10(minimum)))
    upper = maximum if maximum > lower else 10.0 * lower
    edges = np.geomspace(lower, upper, 41)
    resonant_weight = float(np.sum(spectral.vab_power[resonance_mask]))
    weights, _ = np.histogram(
        nonresonant,
        bins=edges,
        weights=spectral.vab_power[~resonance_mask],
    )
    total = float(resonant_weight + np.sum(weights))
    if not np.isfinite(total) or abs(total - 1.0) > 1.0e-12:
        raise RuntimeError(
            f"mean-spacing resonance histogram sums to {total}, expected 1"
        )

    return {
        "edges": edges,
        "weights": weights / total,
        "exact": resonant_weight / total,
        "sum": 1.0,
        "mean_spacing": mean_spacing,
        "resolved_level_count": int(resolved_energies.size),
        "resolved_spacing_count": int(resolved_spacings.size),
        "minimum_normalized_detuning": minimum,
        "maximum_normalized_detuning": maximum,
        "histogram_lower": lower,
        "histogram_upper": upper,
        "target_gap": target_gap,
        "resonance_tolerance_normalized": (
            spectral.degeneracy_tolerance / mean_spacing
        ),
    }


def plot_mean_spacing_gap_weight(
    axis: plt.Axes, spectral: SpectralData
) -> dict[str, Any]:
    """Draw the strict-degeneracy bin and 40 mean-spacing gap bins."""

    data = mean_spacing_gap_weight_data(spectral)
    edges = data["edges"]
    weights = data["weights"]
    widths = np.diff(edges)
    centers = np.sqrt(edges[:-1] * edges[1:])
    degenerate_left = float(data["histogram_lower"]) / 100.0
    degenerate_right = float(data["histogram_lower"]) / 10.0
    degenerate_center = math.sqrt(degenerate_left * degenerate_right)

    axis.bar(
        [degenerate_center],
        [data["exact"]],
        width=degenerate_right - degenerate_left,
        color="#e45756",
        edgecolor="white",
        linewidth=0.45,
        label=r"$|E_a-E_b|\leq\epsilon_{\rm deg}$",
    )
    axis.bar(
        centers,
        weights,
        width=0.92 * widths,
        color="#4c78a8",
        edgecolor="white",
        linewidth=0.35,
        label="nondegenerate gaps",
    )
    maximum = float(data["maximum_normalized_gap"])
    axis.set_xscale("log")
    axis.axvline(
        math.sqrt(degenerate_right * float(data["histogram_lower"])),
        color="0.55",
        linestyle="--",
        linewidth=0.7,
    )
    powers = range(
        int(math.ceil(math.log10(float(data["histogram_lower"])))),
        int(math.floor(math.log10(float(data["histogram_upper"])))) + 1,
    )
    physical_ticks = [10.0**power for power in powers]
    axis.set_xticks(
        [degenerate_center, *physical_ticks],
        [
            r"deg. $\leq\epsilon_{\rm deg}$",
            *[rf"$10^{{{power}}}$" for power in powers],
        ],
    )
    axis.tick_params(axis="x", labelrotation=22, labelsize=7)
    axis.set(
        title=r"$V_{ab}$ weight versus detector energy difference",
        xlabel=r"$\delta_{ab}=|E_a-E_b|/\langle s\rangle$ (log scale)",
        ylabel=(
            r"$W_k=\sum_{\delta_{ab}\in B_k}|V_{ab}|^2/"
            r"\operatorname{Tr}(VV^\dagger)$"
        ),
        xlim=(degenerate_left / 1.4, 1.15 * float(data["histogram_upper"])),
        ylim=(
            0.0,
            max(
                1.0e-12,
                1.08 * float(data["exact"]),
                1.08 * float(np.max(weights)),
            ),
        ),
    )
    axis.grid(axis="y", alpha=0.20)
    axis.text(
        0.97,
        0.96,
        "\n".join(
            (
                rf"$W_{{\rm deg}}+\sum_kW_k={data['sum']:.6f}$",
                rf"$W_{{\rm deg}}={data['exact']:.3g}$; diagonal included",
                rf"$\langle s\rangle={data['mean_spacing']:.4g}$",
                rf"${data['resolved_level_count']}$ resolved levels",
                rf"$40$ logarithmic bins; $\delta_{{\max}}={maximum:.3g}$",
            )
        ),
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=7.0,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    axis.set_box_aspect(1)
    return data


def plot_mean_spacing_resonance_weight(
    axis: plt.Axes, spectral: SpectralData, *, hz0: float
) -> dict[str, Any]:
    """Draw exact resonance weight and 40 logarithmic detuning bins."""

    data = mean_spacing_resonance_weight_data(spectral, hz0=hz0)
    edges = data["edges"]
    weights = data["weights"]
    widths = np.diff(edges)
    centers = np.sqrt(edges[:-1] * edges[1:])
    resonance_left = float(data["histogram_lower"]) / 100.0
    resonance_right = float(data["histogram_lower"]) / 10.0
    resonance_center = math.sqrt(resonance_left * resonance_right)

    axis.bar(
        [resonance_center],
        [data["exact"]],
        width=resonance_right - resonance_left,
        color="#e45756",
        edgecolor="white",
        linewidth=0.45,
        label=r"$\left||E_a-E_b|-2|h_{z0}|\right|\leq\epsilon_{\rm spec}$",
    )
    axis.bar(
        centers,
        weights,
        width=0.92 * widths,
        color="#4c78a8",
        edgecolor="white",
        linewidth=0.35,
        label="nonresonant detunings",
    )
    axis.set_xscale("log")
    axis.axvline(
        math.sqrt(resonance_right * float(data["histogram_lower"])),
        color="0.55",
        linestyle="--",
        linewidth=0.7,
    )
    powers = range(
        int(math.ceil(math.log10(float(data["histogram_lower"])))),
        int(math.floor(math.log10(float(data["histogram_upper"])))) + 1,
    )
    physical_ticks = [10.0**power for power in powers]
    axis.set_xticks(
        [resonance_center, *physical_ticks],
        [
            r"res. $\leq\epsilon_{\rm spec}$",
            *[rf"$10^{{{power}}}$" for power in powers],
        ],
    )
    axis.tick_params(axis="x", labelrotation=22, labelsize=7)
    maximum = float(data["maximum_normalized_detuning"])
    axis.set(
        title=r"$V_{ab}$ weight versus qubit-flip detuning",
        xlabel=(
            r"$\delta^{(0)}_{ab}=\left||E_a-E_b|-2|h_{z0}|\right|/"
            r"\langle s\rangle$ (log scale)"
        ),
        ylabel=(
            r"$W_k=\sum_{\delta^{(0)}_{ab}\in B_k}|V_{ab}|^2/"
            r"\operatorname{Tr}(VV^\dagger)$"
        ),
        xlim=(resonance_left / 1.4, 1.15 * float(data["histogram_upper"])),
        ylim=(
            0.0,
            max(
                1.0e-12,
                1.08 * float(data["exact"]),
                1.08 * float(np.max(weights)),
            ),
        ),
    )
    axis.grid(axis="y", alpha=0.20)
    axis.text(
        0.97,
        0.96,
        "\n".join(
            (
                rf"$W_{{\rm res}}+\sum_kW_k={data['sum']:.6f}$",
                rf"$W_{{\rm res}}={data['exact']:.3g}$",
                rf"$2|h_{{z0}}|={data['target_gap']:.6g}$",
                rf"$\langle s\rangle={data['mean_spacing']:.4g}$",
                rf"${data['resolved_level_count']}$ resolved levels",
                rf"$40$ logarithmic bins; $\delta^{{(0)}}_{{\max}}={maximum:.3g}$",
            )
        ),
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=6.8,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    axis.set_box_aspect(1)
    return data


def render_sample(
    record: CaseRecord,
    spectral: SpectralData,
    arrays: dict[str, np.ndarray],
    output: Path,
    *,
    dpi: int,
    approval_sample: bool = True,
    hz0: float = 0.0,
) -> dict[str, Any]:
    """Render the established 2x3 layout with the revised weight histogram."""

    output.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(18.0, 10.0), dpi=dpi, constrained_layout=False)
    grid = figure.add_gridspec(
        2,
        3,
        left=0.045,
        right=0.985,
        bottom=0.07,
        top=0.86,
        wspace=0.24,
        hspace=0.30,
        width_ratios=(1.0, 1.0, 1.0),
        height_ratios=(1.0, 1.0),
    )

    bandwidth_gaps, _, _ = bandwidth_normalized_gaps(spectral)
    gap_display = -np.log10(np.maximum(bandwidth_gaps, GAP_FLOOR))
    np.fill_diagonal(gap_display, np.nan)
    gap_cmap = plt.get_cmap("magma").copy()
    gap_cmap.set_bad("white")
    gap_axis = _heatmap_panel(
        figure,
        grid[0, 0],
        gap_display,
        title=rf"Energy proximity ($N_D={SPECTRAL_N}$)",
        cmap=gap_cmap,
        vmin=0.0,
        vmax=-math.log10(GAP_FLOOR),
        colorbar_label=r"$-\log_{10}(|E_a-E_b|/(E_{\max}-E_{\min}))$",
    )
    multiplicity_panel_all_ticks(figure.add_subplot(grid[0, 1]), spectral)
    _diagnostics_panel(figure, grid[0, 2], arrays, record)

    vab_axis = _heatmap_panel(
        figure,
        grid[1, 0],
        np.log10(np.maximum(spectral.vab_power, VAB_POWER_FLOOR)),
        title=rf"Interaction $V_{{ab}}$ ($N_D={SPECTRAL_N}$)",
        cmap="viridis",
        vmin=math.log10(VAB_POWER_FLOOR),
        vmax=0.0,
        colorbar_label=r"$\log_{10}(|V_{ab}|^2/\operatorname{Tr}(VV^\dagger))$",
    )
    weight_axis = figure.add_subplot(grid[1, 1])
    if abs(float(hz0)) > 0.0:
        histogram = plot_mean_spacing_resonance_weight(
            weight_axis,
            spectral,
            hz0=hz0,
        )
    else:
        histogram = plot_mean_spacing_gap_weight(weight_axis, spectral)
    plot_level_spacings(figure.add_subplot(grid[1, 2]), spectral)

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

    title_prefix = "Approval sample (log gap axis): " if approval_sample else ""
    second_neighbor_text = ""
    if record.j2 != 0.0 or record.jpm2 != 0.0:
        second_neighbor_text = (
            rf", $J_2={record.j2:.3g}$, $J_{{\pm2}}={record.jpm2:.3g}$"
        )
    figure.suptitle(
        title_prefix
        + rf"Born rank {record.rank}, dynamics $N={record.dynamics_n}$, "
        rf"{record.config_id}, $S_{{\rm Born}}={record.s_born:.4f}$"
        + "\n"
        + rf"$h_z={record.hz:.3g}$, $J={record.j:.3g}$, "
        + rf"$J_\pm={record.jpm:.3g}$"
        + second_neighbor_text
        + rf", $J_x={record.jx:.3g}$, $J_y=0$, $h_{{z0}}={hz0:.3g}$, "
        + r"$t=10^6$",
        fontsize=12.5,
        fontweight="bold",
        y=0.975,
    )
    temporary = output.with_name(output.stem + f".tmp.{os.getpid()}.png")
    figure.savefig(temporary, dpi=dpi, facecolor="white")
    plt.close(figure)
    temporary.replace(output)
    render_data = {
        "output": str(output.resolve()),
        "heatmap_geometry_equal": True,
        "gap_weight_sum": float(histogram["sum"]),
        "special_weight": float(histogram["exact"]),
        "mean_spacing": float(histogram["mean_spacing"]),
        "resolved_level_count": int(histogram["resolved_level_count"]),
        "histogram_edges": histogram["edges"].tolist(),
        "histogram_weights": histogram["weights"].tolist(),
    }
    if abs(float(hz0)) > 0.0:
        render_data.update(
            {
                "resonant_weight": float(histogram["exact"]),
                "target_gap": float(histogram["target_gap"]),
                "maximum_normalized_detuning": float(
                    histogram["maximum_normalized_detuning"]
                ),
            }
        )
    else:
        render_data.update(
            {
                "degenerate_weight": float(histogram["exact"]),
                "maximum_normalized_gap": float(
                    histogram["maximum_normalized_gap"]
                ),
            }
        )
    return render_data


def select_sample() -> tuple[CaseRecord, list[dict[str, Any]], int]:
    """Select the maximum finite ``S_born`` among validated N=14 cases."""

    records, unavailable = inventory(SOURCE)
    candidates = [
        record
        for record in records
        if record.family == "jy_zero" and record.dynamics_n == 14
    ]
    if not candidates:
        raise RuntimeError("no validated N=14 second-neighbor cases were found")
    selected = max(candidates, key=lambda record: (record.s_born, record.config_id))
    return CaseRecord(
        **{
            **asdict(selected),
            "rank": 1,
            "within_n_rank": 1,
        }
    ), unavailable, len(records)


def main() -> None:
    record, unavailable, successful_case_count = select_sample()
    spectral = compute_spectral(
        record,
        detector_n=SPECTRAL_N,
        exploit_magnetization=True,
    )
    arrays = _load_result_arrays(Path(record.source_dir))
    output = OUTPUT / (
        f"sample_rank_0001__{record.config_id}__"
        f"Sborn_{record.s_born:.6f}".replace(".", "p")
        + ".png"
    )
    render = render_sample(
        record,
        spectral,
        arrays,
        output,
        dpi=180,
    )
    manifest = {
        "created": "2026-08-06",
        "status": "approval sample only; full atlas not generated",
        "source_campaign": str(SOURCE.resolve()),
        "source_case": record.source_dir,
        "selection": "maximum finite S_born among validated jy_zero/N14 cases",
        "successful_case_count": successful_case_count,
        "failed_or_incomplete_configuration_count": sum(
            "config_id" in entry for entry in unavailable
        ),
        "non_case_inventory_entries": [
            entry for entry in unavailable if "config_id" not in entry
        ],
        "parameters": {
            "dynamics_N": record.dynamics_n,
            "spectral_detector_N": SPECTRAL_N,
            "hz": record.hz,
            "hz0": 0.0,
            "J": record.j,
            "Jpm": record.jpm,
            "J2": record.j2,
            "Jpm2": record.jpm2,
            "Jx_unscaled": record.jx,
            "Jy_unscaled": record.jy,
            "S_born": record.s_born,
            "born_RMSE_occupied": record.born_rmse,
        },
        "spectral_scope": (
            "N_D=10 detector Hamiltonian with uniform first- and second-neighbor "
            "ring terms; central spin excluded; total-magnetization sectors "
            "diagonalized independently"
        ),
        "mean_spacing_definition": (
            "arithmetic mean of adjacent spacings after detector energies are "
            "clustered using the recorded numerical degeneracy tolerance"
        ),
        "histogram_definition": (
            "strict degeneracy bin plus 40 logarithmically spaced bins in "
            "|Ea-Eb|/<s>, weighted by normalized |Vab|^2"
        ),
        "bottom_right_panel": (
            "unfolded detector level-spacing distribution with Poisson, GOE, "
            "and GUE references"
        ),
        "spectral_validation": spectral.validation,
        "render": render,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "sample_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
