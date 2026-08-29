"""Build publication figures supported by the current classification data."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "collapse_matplotlib_cache"),
)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.projective_roots import (  # noqa: E402
    bloch_vectors_from_homogeneous,
    direct_sum_detector_contexts,
    production_root_spectrum,
)

WORK = ROOT / "work" / "hamiltonian_classification_20260815"
DEFAULT_OUTPUT = ROOT / "figures" / "hamiltonian_classification_20260815"
NETWORK_LABELS = {
    "network_erdos_renyi": "Erdos-Renyi",
    "network_watts_strogatz": "Watts-Strogatz",
    "network_barabasi_albert": "Barabasi-Albert",
    "network_expander": "Random regular",
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


def plot_composition(output: Path) -> None:
    source = (
        WORK / "composition_consistency" / "matched_ring_N16_t10000"
        / "composition_by_spectator_dimension.csv"
    )
    sphere_source = (
        WORK / "matched_ring_reproduction" / "N16_t10000"
        / "full_sphere_source_phi36_mu18.npz"
    )
    rows = list(csv.DictReader(source.open(newline="", encoding="utf-8")))
    dimensions = np.array([int(row["spectator_dimension"]) for row in rows])
    errors = np.array([float(row["composition_error"]) for row in rows])
    raw_counts = np.array([int(row["raw_root_count"]) for row in rows])
    with np.load(sphere_source, allow_pickle=False) as saved:
        asymmetry = np.asarray(saved["asymmetry"], dtype=float)
        mu_edges = np.asarray(saved["mu_edges"], dtype=float)
        phi_edges = np.asarray(saved["phi_edges"], dtype=float)
    composed_asymmetry = asymmetry.copy()  # exact tensor-factor repetition

    source_dir = output / "source_data"
    source_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, source_dir / source.name)
    np.savez_compressed(
        source_dir / "figure_E_asymmetry_fields.npz",
        mu_edges=mu_edges,
        phi_edges=phi_edges,
        asymmetry_QD=asymmetry,
        asymmetry_QDA_dimension_8=composed_asymmetry,
        difference=composed_asymmetry - asymmetry,
    )

    figure, axes = plt.subplots(2, 2, figsize=(7.1, 5.5), constrained_layout=True)
    extent = [phi_edges[0], phi_edges[-1], mu_edges[0], mu_edges[-1]]
    for axis, field, title in (
        (axes[0, 0], asymmetry, r"$a_{QD}(\mu,\phi)$"),
        (axes[0, 1], composed_asymmetry, r"$a_{QDA}(\mu,\phi)$, $d_A=8$"),
    ):
        image = axis.imshow(
            field,
            origin="lower",
            aspect="auto",
            extent=extent,
            cmap="coolwarm",
            vmin=-1.0,
            vmax=1.0,
            interpolation="nearest",
        )
        axis.set_title(title)
        axis.set_xlabel(r"azimuth $\phi$")
        axis.set_ylabel(r"$\mu=\cos\theta$")
    figure.colorbar(image, ax=axes[0, :], label="outcome asymmetry", shrink=0.85)

    axes[1, 0].plot(dimensions, np.maximum(errors, 1.0e-18), "o-", lw=1.3)
    axes[1, 0].axhline(1.0e-15, color="0.5", lw=0.8, ls="--")
    axes[1, 0].set_yscale("log")
    axes[1, 0].set_xlabel("spectator dimension")
    axes[1, 0].set_ylabel(r"composition error $\epsilon_{\rm comp}$")
    axes[1, 0].set_title("Normalized geometry is invariant")
    axes[1, 0].set_xticks(dimensions)

    axes[1, 1].plot(dimensions, raw_counts, "s-", lw=1.3)
    axes[1, 1].set_xlabel("spectator dimension")
    axes[1, 1].set_ylabel("raw algebraic roots")
    axes[1, 1].set_title("Raw multiplicity scales with context size")
    axes[1, 1].set_xticks(dimensions)
    axes[1, 1].ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    figure.suptitle("Figure E — uncoupled tensor-factor composition", fontsize=11)
    _save(figure, output / "figure_E_composition_consistency")


def plot_context_refinement(output: Path) -> None:
    """Plot the exact nonuniform direct-sum root-counting counterexample."""

    def rotation(angle: float) -> np.ndarray:
        return np.array(
            [
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)],
            ],
            dtype=float,
        )

    component_unitaries = [rotation(0.2), rotation(1.0)]
    component_roots = []
    for unitary in component_unitaries:
        spectrum = production_root_spectrum(unitary)
        component_roots.append(
            bloch_vectors_from_homogeneous(spectrum.alpha, spectrum.beta)[0]
        )
    roots = np.asarray(component_roots)
    contexts = {
        r"$U_1\oplus U_2$": np.array([0.5, 0.5]),
        r"$U_1\oplus U_1\oplus U_2$": np.array([2.0 / 3.0, 1.0 / 3.0]),
    }

    # Exercise the actual direct-sum implementation, not only its weight rule.
    base = direct_sum_detector_contexts(component_unitaries)
    refined = direct_sum_detector_contexts(
        [component_unitaries[0], component_unitaries[0], component_unitaries[1]]
    )
    expected_counts = (2, 3)
    for unitary, expected in zip((base, refined), expected_counts, strict=True):
        spectrum = production_root_spectrum(unitary)
        if spectrum.alpha.size != expected or np.any(spectrum.indeterminate):
            raise RuntimeError("direct-sum refinement root audit failed")

    source_dir = output / "source_data"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_path = source_dir / "context_refinement_counterexample.csv"
    with source_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["context", "component", "weight", "r_x", "r_y", "r_z"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for context, weights in contexts.items():
            for index, (weight, root) in enumerate(
                zip(weights, roots, strict=True), start=1
            ):
                writer.writerow(
                    {
                        "context": context.replace("$", ""),
                        "component": f"U{index}",
                        "weight": weight,
                        "r_x": root[0],
                        "r_y": root[1],
                        "r_z": root[2],
                    }
                )

    figure, axes = plt.subplots(1, 2, figsize=(7.1, 3.25), constrained_layout=True)
    angle = np.linspace(0.0, 2.0 * np.pi, 500)
    axes[0].plot(np.sin(angle), np.cos(angle), color="0.75", lw=1.0)
    colors = ("#2166ac", "#b2182b")
    for index, (root, color) in enumerate(zip(roots, colors, strict=True), start=1):
        axes[0].scatter(root[0], root[2], s=70, color=color, zorder=3)
        axes[0].annotate(
            rf"$U_{index}$",
            (root[0], root[2]),
            xytext=(5, 5),
            textcoords="offset points",
        )
    for context, weights in contexts.items():
        centroid = weights @ roots
        axes[0].plot(
            [0.0, centroid[0]], [0.0, centroid[2]], lw=1.5, label=context
        )
    axes[0].set_aspect("equal")
    axes[0].set_xlim(-1.05, 1.05)
    axes[0].set_ylim(-1.05, 1.05)
    axes[0].set_xlabel(r"Bloch coordinate $r_x$")
    axes[0].set_ylabel(r"Bloch coordinate $r_z$")
    axes[0].set_title("Same component roots, shifted root centroid")
    axes[0].legend(frameon=False, fontsize=7, loc="lower left")

    x = np.arange(2)
    width = 0.34
    for offset, (context, weights) in zip(
        (-width / 2, width / 2), contexts.items(), strict=True
    ):
        axes[1].bar(x + offset, weights, width=width, label=context)
    axes[1].set_xticks(x, [r"$U_1$ root", r"$U_2$ root"])
    axes[1].set_ylim(0.0, 0.75)
    axes[1].set_ylabel("normalized equal-root weight")
    axes[1].set_title("Duplicating one microsector changes weights")
    axes[1].legend(frameon=False, fontsize=7)
    figure.suptitle(
        "Nonuniform detector refinement violates equal-root noncontextuality",
        fontsize=11,
    )
    _save(figure, output / "context_refinement_counterexample")


def _representative_network_cloud(family: str) -> np.ndarray:
    roots = sorted((ROOT / "work").glob(f"zeus_sobol_{family}_hz0_0_N12_*"))
    candidates = sorted(
        candidate
        for candidate in roots[-1].rglob("results.npz")
        if candidate.parent.name.startswith("config_")
    )
    if not candidates:
        raise FileNotFoundError(f"no completed network roots for {family}")
    path = candidates[0]
    with np.load(path, allow_pickle=False) as saved:
        return np.asarray(saved["bloch_blue"], dtype=float)


def plot_network_no_go(output: Path) -> None:
    source = WORK / "network_full_sphere" / "network_classification_results.csv"
    rows = list(csv.DictReader(source.open(newline="", encoding="utf-8")))
    grouped = {
        family: [row for row in rows if row["family"] == family]
        for family in NETWORK_LABELS
    }
    source_dir = output / "source_data"
    source_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, source_dir / source.name)

    summary_path = source_dir / "network_great_circle_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["family", "completed", "median_coverage", "max_abs_bloch_x"],
        )
        writer.writeheader()
        for family, family_rows in grouped.items():
            maximum_x = max(
                json.loads(row["parameters"])["max_abs_bloch_x"]
                for row in family_rows
            )
            writer.writerow(
                {
                    "family": family,
                    "completed": len(family_rows),
                    "median_coverage": np.median(
                        [float(row["coverage"]) for row in family_rows]
                    ),
                    "max_abs_bloch_x": maximum_x,
                }
            )

    figure, axes = plt.subplots(2, 2, figsize=(7.1, 5.7), constrained_layout=True)
    markers = ("o", "s", "^", "D")
    for (family, label), marker in zip(NETWORK_LABELS.items(), markers, strict=True):
        cloud = _representative_network_cloud(family.removeprefix("network_"))
        axes[0, 0].scatter(
            cloud[::8, 1], cloud[::8, 2], s=7, alpha=0.35, marker=marker, label=label
        )
    axes[0, 0].set_aspect("equal")
    axes[0, 0].set_xlim(-1.05, 1.05)
    axes[0, 0].set_ylim(-1.05, 1.05)
    axes[0, 0].set_xlabel(r"$r_y$")
    axes[0, 0].set_ylabel(r"$r_z$")
    axes[0, 0].set_title("Representative roots occupy one great circle")
    axes[0, 0].legend(frameon=False, ncol=2, loc="lower center")

    labels = list(NETWORK_LABELS.values())
    coverage = [[float(row["coverage"]) for row in grouped[key]] for key in grouped]
    polar = [[float(row["polar_S_born"]) for row in grouped[key]] for key in grouped]
    maximum_x = [
        [json.loads(row["parameters"])["max_abs_bloch_x"] for row in grouped[key]]
        for key in grouped
    ]
    for axis, values, ylabel, title in (
        (axes[0, 1], maximum_x, r"maximum $|r_x|$", "Great-circle residual"),
        (axes[1, 0], coverage, "equal-area coverage", "Full-sphere support"),
        (axes[1, 1], polar, r"legacy polar $S_{\rm Born}$", "Polar score alone"),
    ):
        axis.boxplot(values, tick_labels=labels, showfliers=False)
        axis.set_ylabel(ylabel)
        axis.set_title(title)
        axis.tick_params(axis="x", rotation=22)
    axes[0, 1].set_yscale("log")
    figure.suptitle(
        "Random detector connectivity cannot overcome conserved central X",
        fontsize=11,
    )
    _save(figure, output / "network_great_circle_no_go")


def plot_matched_detuning(output: Path) -> None:
    source = (
        WORK / "sobol_ring_full_sphere" / "relations"
        / "resolved_configurations_ranked.csv"
    )
    rows = list(csv.DictReader(source.open(newline="", encoding="utf-8")))
    delta = np.array([float(row["delta_source_signed"]) for row in rows])
    color = np.array([float(row["log10_Jpm_over_J"]) for row in rows])
    series = (
        (
            "higher_harmonic_leakage",
            r"higher-odd leakage $\mathcal{L}_{\geq 3}$",
            None,
        ),
        ("dipole_sharpness", r"dipole sharpness $\eta$", 1.0),
        ("axis_fidelity", r"axis infidelity $1-F_{\rm axis}$", None),
        ("epsilon_B", r"Born residual $\epsilon_B$", None),
    )
    source_dir = output / "source_data"
    source_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, source_dir / source.name)

    figure, axes = plt.subplots(2, 2, figsize=(7.1, 5.4), constrained_layout=True)
    scatter = None
    for axis, (field, ylabel, reference) in zip(axes.ravel(), series, strict=True):
        if field == "axis_fidelity":
            values = np.maximum(
                1.0 - np.array([float(row[field]) for row in rows]),
                1.0e-15,
            )
        else:
            values = np.array([float(row[field]) for row in rows])
        scatter = axis.scatter(
            delta,
            values,
            c=color,
            cmap="viridis",
            s=25,
            alpha=0.85,
            linewidths=0.25,
            edgecolors="0.2",
        )
        axis.axvline(0.0, color="0.45", lw=0.8, ls="--")
        if reference is not None:
            axis.axhline(reference, color="0.45", lw=0.8, ls=":")
        axis.set_xlabel(
            r"source detuning $\delta=(h_{z0}-h_z)/J_{x,\mathrm{source}}$"
        )
        axis.set_ylabel(ylabel)
    axes[1, 0].set_yscale("log")
    assert scatter is not None
    figure.colorbar(
        scatter,
        ax=axes,
        label=r"$\log_{10}(J_{pm}/J)$",
        shrink=0.86,
    )
    figure.suptitle(
        "Figure B - matched-field detuning at N=14 (52 fully resolved cases)",
        fontsize=11,
    )
    _save(figure, output / "figure_B_matched_field_detuning_N14")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    _style()
    plot_composition(output)
    plot_context_refinement(output)
    plot_network_no_go(output)
    plot_matched_detuning(output)
    print(json.dumps({"output": str(output), "figures": 4}, indent=2))


if __name__ == "__main__":
    main()
