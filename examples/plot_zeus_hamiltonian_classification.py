"""Build publication Figures A--D from a complete Zeus classification run."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "collapse_matplotlib_cache"),
)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


METRICS = (
    ("higher_harmonic_leakage", r"$\mathcal{L}_{\geq 3}$"),
    ("dipole_sharpness", r"$\eta$"),
    ("axis_fidelity", r"$F_{\rm axis}$"),
    ("epsilon_B", r"$\epsilon_B$"),
)
ARCHITECTURE_LABELS = {
    "noninteracting_star": "Noninteracting star",
    "interacting_ising_ring": "Ising ring",
    "xy_ring_collective": "XY ring",
    "xy_chain_edge": "XY chain, edge",
    "cross_architecture_ring_control": "Ring",
    "erdos_renyi": "Erdos-Renyi",
    "watts_strogatz": "Watts-Strogatz",
    "barabasi_albert": "Barabasi-Albert",
    "expander": "Random regular",
    "haar_unitary_null": "Haar null",
}
ARCHITECTURE_SHORT_LABELS = {
    "noninteracting_star": "NI star",
    "interacting_ising_ring": "Ising",
    "xy_ring_collective": "XY ring",
    "xy_chain_edge": "XY edge",
    "cross_architecture_ring_control": "Ring",
    "erdos_renyi": "ER",
    "watts_strogatz": "WS",
    "barabasi_albert": "BA",
    "expander": "RR",
    "haar_unitary_null": "Haar",
}


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "savefig.dpi": 300,
        }
    )


def _save(figure: plt.Figure, stem: Path) -> None:
    figure.savefig(stem.with_suffix(".png"), bbox_inches="tight", facecolor="white")
    figure.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    plt.close(figure)


def _number(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value in {"", "None", "null", "nan", "NaN"}:
        return np.nan
    return float(value)


def load_complete_results(run_root: Path) -> list[dict[str, str]]:
    aggregate = run_root / "aggregated"
    summary_path = aggregate / "collection_summary.json"
    results_path = aggregate / "classification_results.csv"
    if not summary_path.is_file() or not results_path.is_file():
        raise FileNotFoundError("run the classification collector first")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if (
        int(summary["complete"]) != int(summary["expected"])
        or int(summary["missing"]) != 0
        or int(summary["corrupt"]) != 0
    ):
        raise RuntimeError(
            "campaign is incomplete; figures require every expected point"
        )
    with results_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != int(summary["expected"]):
        raise RuntimeError("collector summary and result-table cardinality disagree")
    return rows


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty source table {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _plot_scan(
    rows: list[dict[str, str]],
    *,
    campaign: str,
    figure_title: str,
    x_label: str,
    output_stem: Path,
    source_path: Path,
) -> None:
    selected = [row for row in rows if row["campaign"] == campaign]
    if not selected:
        raise RuntimeError(f"no rows for {campaign}")
    _write_rows(source_path, selected)
    figure, axes = plt.subplots(2, 2, figsize=(7.1, 5.3), constrained_layout=True)
    sizes = sorted({int(row["N"]) for row in selected})
    markers = ("o", "s", "^")
    for axis, (metric, ylabel) in zip(axes.ravel(), METRICS, strict=True):
        for detector_n, marker in zip(sizes, markers, strict=True):
            subset = sorted(
                (row for row in selected if int(row["N"]) == detector_n),
                key=lambda row: float(row["scan_value"]),
            )
            x = np.array([float(row["scan_value"]) for row in subset])
            y = np.array([_number(row, metric) for row in subset])
            valid = np.isfinite(y)
            axis.plot(
                x[valid],
                y[valid],
                marker=marker,
                ms=4,
                lw=1.0,
                label=f"N={detector_n}",
            )
            unresolved = ~valid
            if np.any(unresolved):
                lower, upper = axis.get_ylim()
                axis.scatter(
                    x[unresolved],
                    np.full(np.count_nonzero(unresolved), lower),
                    marker="x",
                    s=20,
                    color="0.45",
                    clip_on=False,
                )
                axis.set_ylim(lower, upper)
        axis.set_xlabel(x_label)
        axis.set_ylabel(ylabel)
    axes[0, 0].legend(frameon=False, ncol=len(sizes))
    figure.suptitle(figure_title, fontsize=11)
    _save(figure, output_stem)


def plot_figure_c(
    rows: list[dict[str, str]], output_stem: Path, source_path: Path
) -> None:
    selected = [
        row
        for row in rows
        if row["campaign"]
        in {
            "cross_network_matched",
            "cross_architecture_ring_control",
            "cross_physical_architectures",
            "haar_unitary_null",
        }
    ]
    normalized: list[dict[str, object]] = []
    for row in selected:
        if row["campaign"] == "cross_network_matched":
            architecture = row["scan_value"]
        elif row["campaign"] == "cross_physical_architectures":
            architecture = row["scan_value"]
        elif row["campaign"] == "cross_architecture_ring_control":
            architecture = "cross_architecture_ring_control"
        else:
            architecture = "haar_unitary_null"
        normalized.append({**row, "architecture": architecture})
    _write_rows(source_path, normalized)
    order = list(ARCHITECTURE_LABELS)
    figure, axes = plt.subplots(2, 3, figsize=(7.1, 5.4), constrained_layout=True)
    metrics = (*METRICS, ("coverage", "coverage"))
    rng = np.random.default_rng(20260815)
    for axis, (metric, ylabel) in zip(axes.ravel()[:5], metrics, strict=True):
        for detector_n, marker, offset in ((8, "o", -0.08), (10, "s", 0.08)):
            for index, architecture in enumerate(order):
                values = np.array(
                    [
                        _number(row, metric)
                        for row in normalized
                        if row["architecture"] == architecture
                        and int(row["N"]) == detector_n
                    ]
                )
                values = values[np.isfinite(values)]
                if not values.size:
                    continue
                jitter = rng.uniform(-0.035, 0.035, size=values.size)
                axis.scatter(
                    index + offset + jitter,
                    values,
                    marker=marker,
                    s=24,
                    alpha=0.8,
                    label=f"N={detector_n}" if index == 0 else None,
                )
        axis.set_xticks(
            range(len(order)),
            [ARCHITECTURE_SHORT_LABELS[key] for key in order],
        )
        axis.tick_params(axis="x", rotation=50)
        axis.set_ylabel(ylabel)
    axes.ravel()[0].legend(frameon=False)
    key_axis = axes.ravel()[5]
    key_axis.axis("off")
    key_axis.text(
        0.0,
        1.0,
        "Architecture key\n"
        + "\n".join(
            f"{ARCHITECTURE_SHORT_LABELS[key]}: {ARCHITECTURE_LABELS[key]}"
            for key in order
        ),
        va="top",
        ha="left",
        fontsize=8,
        linespacing=1.25,
    )
    figure.suptitle(
        "Figure C - common-QZ cross-architecture comparison",
        fontsize=11,
    )
    _save(figure, output_stem)


def _case_dir(run_root: Path, row: dict[str, str]) -> Path:
    candidate = Path(row["case_dir"])
    if candidate.is_dir():
        return candidate
    return (
        run_root
        / "raw"
        / row["campaign"]
        / f"point_{int(row['point_id']):04d}_N{int(row['N'])}_t{float(row['time']):.12g}"
    )


def _power(run_root: Path, row: dict[str, str]) -> np.ndarray:
    path = _case_dir(run_root, row) / "roots_and_full_sphere.npz"
    with np.load(path, allow_pickle=False) as saved:
        power = np.asarray(saved["power_by_l"], dtype=float)
    if power.size == 0:
        raise RuntimeError(f"selected representative has unresolved harmonics: {path}")
    return power


def plot_figure_d(
    rows: list[dict[str, str]],
    run_root: Path,
    output_stem: Path,
    source_path: Path,
) -> None:
    resolved = [row for row in rows if np.isfinite(_number(row, "epsilon_B"))]
    physical = [row for row in resolved if row["campaign"] != "haar_unitary_null"]
    strongest = min(physical, key=lambda row: _number(row, "epsilon_B"))
    distorted = max(physical, key=lambda row: _number(row, "higher_harmonic_leakage"))
    scrambling_candidates = [
        row for row in physical if row["campaign"] == "detector_transverse_scrambling"
    ]
    if not scrambling_candidates:
        raise RuntimeError("no resolved detector-scrambling representative")
    scrambling = max(scrambling_candidates, key=lambda row: float(row["scan_value"]))
    haar = next(row for row in resolved if row["campaign"] == "haar_unitary_null")
    representatives = (
        ("strongest Born-like", strongest),
        ("largest higher-odd leakage", distorted),
        ("strong detector transverse field", scrambling),
        ("Haar null", haar),
    )
    source_rows: list[dict[str, object]] = []
    figure, axis = plt.subplots(figsize=(6.4, 3.6), constrained_layout=True)
    markers = ("o", "s", "^", "D")
    for (label, row), marker in zip(representatives, markers, strict=True):
        power = _power(run_root, row)
        odd_l = np.arange(1, power.size, 2)
        odd_power = power[odd_l]
        total = float(np.sum(odd_power))
        normalized = odd_power / total if total > 0.0 else np.full_like(odd_power, np.nan)
        axis.plot(odd_l, normalized, marker=marker, lw=1.2, label=label)
        for ell, value, raw_value in zip(odd_l, normalized, odd_power, strict=True):
            source_rows.append(
                {
                    "representative": label,
                    "point_id": row["point_id"],
                    "campaign": row["campaign"],
                    "N": row["N"],
                    "ell": int(ell),
                    "power": raw_value,
                    "fraction_of_odd_power": value,
                    "case_dir": str(_case_dir(run_root, row)),
                }
            )
    _write_rows(source_path, source_rows)
    axis.set_yscale("log")
    axis.set_xticks([1, 3, 5, 7])
    axis.set_xlabel(r"odd harmonic degree $\ell$")
    axis.set_ylabel(r"$P_\ell/P_{\rm odd}$")
    axis.legend(frameon=False)
    axis.set_title(
        "Figure D - resolved harmonic spectra\n"
        "strict QND is pole-supported and has no unregularized L2 spectrum"
    )
    _save(figure, output_stem)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    output = (
        args.output.resolve()
        if args.output is not None
        else run_root / "figures" / "hamiltonian_classification"
    )
    output.mkdir(parents=True, exist_ok=True)
    source = output / "source_data"
    source.mkdir(parents=True, exist_ok=True)
    rows = load_complete_results(run_root)
    _style()
    _plot_scan(
        rows,
        campaign="transverse_strength",
        figure_title="Figure A - QND to transverse mixing",
        x_label=r"source transverse coupling $J_x$",
        output_stem=output / "figure_A_transverse_mixing",
        source_path=source / "figure_A_transverse_mixing.csv",
    )
    _plot_scan(
        rows,
        campaign="matched_detuning",
        figure_title="Figure B - matched-field detuning",
        x_label=r"$\delta=(h_{z0}-h_z)/J_{x,\mathrm{source}}$",
        output_stem=output / "figure_B_matched_detuning",
        source_path=source / "figure_B_matched_detuning.csv",
    )
    plot_figure_c(
        rows,
        output / "figure_C_cross_architecture",
        source / "figure_C_cross_architecture.csv",
    )
    plot_figure_d(
        rows,
        run_root,
        output / "figure_D_harmonic_spectra",
        source / "figure_D_harmonic_spectra.csv",
    )
    print(json.dumps({"output": str(output), "figures": 4}, indent=2))


if __name__ == "__main__":
    main()
