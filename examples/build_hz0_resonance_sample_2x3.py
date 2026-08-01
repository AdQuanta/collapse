"""Build one approval sample for the hz0=0.1 detector-resonance atlas."""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import asdict
import json, math, os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from examples.build_sobol_flat_ranked_1x6_by_n import (
    CaseRecord, SpectralData, DETECTOR_N, GAP_FLOOR, VAB_POWER_FLOOR,
    _bloch_panel, _diagnostics_panel, _heatmap_panel, _multiplicity_panel,
    _load_result_arrays, compute_spectral, inventory,
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


def resonance_gap_weight_panel(
    axis: plt.Axes,
    spectral: SpectralData,
    *,
    hz0: float,
):
    """Bin normalized Vab power by distance from the qubit-flip resonance.

    The energies are eigenvalues of the detector Hamiltonian only. The central
    field enters only through the comparison target 2*abs(hz0).
    """
    bandwidth = float(np.ptp(spectral.energies))
    if not bandwidth > 0.0:
        raise RuntimeError("resonance histogram requires nonzero detector bandwidth")
    absolute_gaps = np.abs(
        spectral.energies[:, None] - spectral.energies[None, :]
    )
    target_gap = 2.0 * abs(float(hz0))
    absolute_detuning = np.abs(absolute_gaps - target_gap)
    normalized_detuning = absolute_detuning / bandwidth
    if float(np.max(normalized_detuning)) > 1.0 + 1.0e-12:
        raise RuntimeError("normalized resonance detuning exceeds [0,1]")

    resonance_tolerance = spectral.degeneracy_tolerance
    resonance_mask = absolute_detuning <= resonance_tolerance
    resonant_weight = float(np.sum(spectral.vab_power[resonance_mask]))
    edges = np.linspace(0.0, 1.0, 41)
    resolved_weights, _ = np.histogram(
        normalized_detuning[~resonance_mask],
        bins=edges,
        weights=spectral.vab_power[~resonance_mask],
    )
    total = float(resonant_weight + np.sum(resolved_weights))
    if not np.isfinite(total) or abs(total - 1.0) > 1.0e-12:
        raise RuntimeError(
            f"resonance-detuning Vab histogram sums to {total}, expected 1"
        )
    resonant_weight /= total
    resolved_weights /= total
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    resonance_center = -0.05

    axis.bar(
        [resonance_center], [resonant_weight], width=0.035,
        color="#e45756", edgecolor="white", linewidth=0.45,
        label=r"$\delta^{(0)}_{ab}\leq\epsilon_{\rm spec}$",
    )
    axis.bar(
        centers, resolved_weights, width=0.92 * widths,
        color="#4c78a8", edgecolor="white", linewidth=0.35,
        label=r"$\delta^{(0)}_{ab}>\epsilon_{\rm spec}$",
    )
    axis.set(
        title=r"$|V_{ab}|^2$ weight versus qubit-flip detuning",
        xlabel=(r"$\delta^{(0)}_{ab}=\left||E_a-E_b|-2|h_{z0}|\right|$" + chr(10) + r"$/(E_{\max}-E_{\min})$"),
        ylabel=r"$W_k=\sum_{\delta^{(0)}_{ab}\in B_k}|V_{ab}|^2/\operatorname{Tr}(VV^\dagger)$",
        xlim=(-0.075, 1.0),
        ylim=(
            0.0,
            max(
                1.0e-12,
                1.08 * resonant_weight,
                1.08 * float(np.max(resolved_weights)),
            ),
        ),
    )
    axis.set_xticks(
        [resonance_center, 0.0, 0.25, 0.50, 0.75, 1.0],
        [r"$\mathrm{res.}$", "0", "0.25", "0.50", "0.75", "1"],
    )
    axis.axvline(-0.018, color="0.55", linewidth=0.7)
    axis.grid(axis="y", alpha=0.20)
    axis.legend(loc="upper left", fontsize=7.0, framealpha=0.90)
    axis.text(
        0.97, 0.96,
        chr(10).join((
            rf"$W_{{\rm res}}+\sum_kW_k={resonant_weight + np.sum(resolved_weights):.6f}$",
            rf"$W_{{\rm res}}={resonant_weight:.3g}$",
            rf"$2|h_{{z0}}|={target_gap:.6g}$",
            rf"$E_{{\max}}-E_{{\min}}={bandwidth:.4g}$",
            rf"$\epsilon_{{\rm spec}}={resonance_tolerance:.2g}$",
            r"$E_a,E_b\ \mathrm{from}\ H_D\ \mathrm{only}$",
        )),
        transform=axis.transAxes, ha="right", va="top", fontsize=7.2,
        bbox={"facecolor": "white", "edgecolor": "0.8", "alpha": 0.90, "pad": 2},
    )
    axis.set_box_aspect(1)
    return {
        "edges": edges.tolist(),
        "weights": resolved_weights.tolist(),
        "sum": float(resonant_weight + np.sum(resolved_weights)),
        "resonant_weight": resonant_weight,
        "resonance_tolerance": resonance_tolerance,
        "target_gap": target_gap,
        "bandwidth": bandwidth,
        "definition": "abs(abs(Ea-Eb)-2*abs(hz0))/(Emax-Emin); detector eigenvalues only",
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
    hz0: float,
):
    if output.is_file() and not force:
        return {"status": "existing", "output_path": str(output)}
    output.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(18.0, 10.0), dpi=dpi, constrained_layout=False)
    grid = figure.add_gridspec(
        2, 3, left=0.045, right=0.985, bottom=0.12, top=0.88,
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
    gap_histogram = resonance_gap_weight_panel(weight_axis, spectral, hz0=hz0)
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
        + rf"$h_z={record.hz:.6g}$, $h_{{z0}}={hz0:.3g}$, $J={record.j:.3g}$, $J_\pm={record.jpm:.3g}$, "
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
        "resonant_weight": float(gap_histogram["resonant_weight"]),
    }



DEFAULT_SOURCES = (
    ROOT / "work/zeus_sobol_hz0_0p1_jpm0_jy0_N15_20260731_194359",
    ROOT / "work/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p05_0p5_N15_20260731_203102",
    ROOT / "work/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p09_0p11_N15_20260731_215132",
    ROOT / "work/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_N15_20260731_222248",
    ROOT / "work/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_N15_20260731_222933",
)
DEFAULT_OUTPUT = ROOT / "reports/hz0_resonance_sample_2x3_2026-08-01"


def select_best_case() -> tuple[CaseRecord, float, Path]:
    candidates: list[tuple[CaseRecord, float, Path]] = []
    for source in DEFAULT_SOURCES:
        records, _ = inventory(source)
        for record in records:
            metadata_path = Path(record.source_dir) / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            hz0 = float(metadata["hz0"])
            if hz0 == 0.1:
                candidates.append((record, hz0, source))
    if not candidates:
        raise RuntimeError("no successful hz0=0.1 cases were found")
    return max(candidates, key=lambda item: (item[0].s_born, item[0].config_id))


def main() -> None:
    record, hz0, source = select_best_case()
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
    output = DEFAULT_OUTPUT / (
        f"sample__{source.name}__{record.config_id}__"
        f"Sborn_{record.s_born:.6f}.png"
    )
    ranked = CaseRecord(
        **{
            **asdict(record),
            "rank": 1,
            "within_n_rank": 1,
            "output_path": str(output.resolve()),
        }
    )
    spectral = compute_spectral(ranked)
    arrays = _load_result_arrays(Path(ranked.source_dir))
    result = render_case_2x3(
        ranked,
        spectral,
        arrays,
        output=output,
        force=True,
        dpi=180,
        max_bloch_points=6000,
        hz0=hz0,
    )
    manifest = {
        "created": "2026-08-01",
        "selection": "maximum finite S_born among successful cases in the five downloaded hz0=0.1 campaigns",
        "source_campaign": str(source.resolve()),
        "source_case": ranked.source_dir,
        "output": str(output.resolve()),
        "parameters": {
            "N": ranked.dynamics_n,
            "detector_heatmap_N": DETECTOR_N,
            "hz0": hz0,
            "hz": ranked.hz,
            "J": ranked.j,
            "Jpm": ranked.jpm,
            "Jx": ranked.jx,
            "Jy": ranked.jy,
            "S_born": ranked.s_born,
            "born_RMSE_occupied": ranked.born_rmse,
        },
        "spectral_scope": "energies and eigenvectors are from the detector Hamiltonian H_D only",
        "histogram_definition": "delta0_ab=abs(abs(Ea-Eb)-2*abs(hz0))/(Emax-Emin), weighted by normalized |Vab|^2",
        "spectral_validation": spectral.validation,
        "render": result,
    }
    (DEFAULT_OUTPUT / "sample_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()