"""Build simplified figures for the three-page V_ab activation brief."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.ticker import NullFormatter

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "vab_activation_brief_2026-07-22" / "figures"


def relative_unitary_map() -> Path:
    source = (
        ROOT
        / "reports"
        / "detector_gap_matrix_study_2026-07-21"
        / "data"
        / "relative_unitary_validation.csv"
    )
    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    coupling = np.asarray([float(row["g"]) for row in rows])
    operator_error = np.asarray(
        [float(row["leading_magnus_operator_error"]) for row in rows]
    )
    angle_error = np.asarray(
        [float(row["leading_magnus_max_theta_error"]) for row in rows]
    )
    order = np.argsort(coupling)
    slope = float(np.polyfit(np.log(coupling), np.log(operator_error), 1)[0])

    phase = np.linspace(-np.pi + 0.015, np.pi - 0.015, 1200)
    radius = np.abs(np.tan(phase / 2.0))
    theta = np.abs(phase)

    figure, axes = plt.subplots(1, 2, figsize=(12.2, 3.8))
    axes[0].loglog(
        coupling[order],
        operator_error[order],
        "o-",
        color="#2563eb",
        linewidth=2,
        label=r"operator error",
    )
    axes[0].loglog(
        coupling[order],
        angle_error[order],
        "s--",
        color="#dc2626",
        linewidth=1.8,
        label=r"maximum angle error",
    )
    axes[0].set_xticks(coupling[order])
    axes[0].set_xticklabels([f"{value:g}" for value in coupling[order]])
    axes[0].xaxis.set_minor_formatter(NullFormatter())
    axes[0].set(
        xlabel=r"weak coupling $g$",
        ylabel="absolute error",
        title=rf"Finite-time approximation converges as $g^{{{slope:.2f}}}$",
    )
    axes[0].grid(alpha=0.22)
    axes[0].legend(frameon=False)

    axes[1].plot(
        phase,
        radius,
        color="#7c3aed",
        linewidth=2.0,
        label=r"radius $|\lambda|=|\tan(\varphi/2)|$",
    )
    twin = axes[1].twinx()
    twin.plot(
        phase,
        theta,
        color="#059669",
        linewidth=1.8,
        linestyle="--",
        label=r"polar angle $\theta=|\varphi|$",
    )
    axes[1].axvspan(-np.pi, -2.8, color="#f59e0b", alpha=0.12)
    axes[1].axvspan(2.8, np.pi, color="#f59e0b", alpha=0.12)
    axes[1].set(
        xlabel=r"relative-unitary eigenphase $\varphi$",
        ylabel=r"radius $|\lambda|$",
        title="Exact phase-to-radius map",
    )
    twin.set_ylabel(r"polar angle $\theta$")
    axes[1].set_ylim(0.0, 20.0)
    twin.set_ylim(0.0, np.pi)
    lines = axes[1].lines + twin.lines
    axes[1].legend(
        lines,
        [line.get_label() for line in lines],
        frameon=False,
        loc="upper center",
    )
    axes[1].grid(alpha=0.22)
    figure.tight_layout()
    output = OUTPUT / "relative_unitary_map_brief.png"
    figure.savefig(output, dpi=240, bbox_inches="tight")
    plt.close(figure)
    return output


def three_outcomes() -> Path:
    campaign = ROOT / "work" / "zeus_single_pixel_anisotropic_20260718_130606"
    cases = (
        (
            "Heavy and Born-like",
            "$h_z=.01,\\ J=.75,\\ J_{\\pm}=.5$\n$S_{\\rm Born}=.889,\\ \\alpha=.877$",
            campaign
            / "figures/N14/hz_p0p01/J_p0p75/Jpm_p0p5/blue_red_t1000000.png",
        ),
        (
            "Heavy, but not Born-like",
            "$h_z=2,\\ J=1,\\ J_{\\pm}=0$\n$S_{\\rm Born}=-.411,\\ \\alpha=.415$",
            campaign / "figures/N14/hz_p2/J_p1/Jpm_p0/blue_red_t1000000.png",
        ),
        (
            "Narrow control",
            "$h_z=1,\\ J=.25,\\ J_{\\pm}=0$\n$S_{\\rm Born}=.009,\\ \\alpha=8$",
            campaign / "figures/N14/hz_p1/J_p0p25/Jpm_p0/blue_red_t1000000.png",
        ),
    )
    figure, axes = plt.subplots(1, 3, figsize=(15.2, 5.0))
    for axis, (title, subtitle, path) in zip(axes, cases, strict=True):
        image = plt.imread(path)
        crop = image[: int(0.625 * image.shape[0]), :, :]
        axis.imshow(crop)
        axis.axis("off")
        axis.set_title(f"{title}\n{subtitle}", fontsize=11, pad=8)
    figure.subplots_adjust(left=0.008, right=0.992, bottom=0.01, top=0.84, wspace=0.025)
    output = OUTPUT / "three_outcomes_brief.png"
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)
    return output


def active_gap_comparison() -> Path:
    source = ROOT / "reports" / "detector_gap_matrix_study_2026-07-21" / "data"
    cases = (
        ("Heavy and Born-like", source / "heavy_born_gap_matrix.npz"),
        ("Heavy, not Born-like", source / "heavy_not_born_gap_matrix.npz"),
        ("Narrow control", source / "wrapped_gaussian_control_gap_matrix.npz"),
    )
    figure, axes = plt.subplots(3, 3, figsize=(14.8, 8.7))
    gap_images = []
    active_images = []
    degenerate_images = []
    degeneracy_tolerance = 2.0e-2
    for column, (title, path) in enumerate(cases):
        with np.load(path) as archive:
            gaps = np.asarray(archive["signed_gaps"], dtype=float)
            coupling = np.asarray(archive["energy_basis_coupling"])
        bandwidth = max(float(np.max(gaps) - np.min(gaps)), 1.0)
        near = -np.log10(np.maximum(np.abs(gaps) / bandwidth, 1.0e-12))
        np.fill_diagonal(near, np.nan)

        time = 1.0e6
        filter_magnitude = time * np.abs(np.sinc(gaps * time / (2.0 * np.pi)))
        power = np.abs(coupling) ** 2 * filter_magnitude**2
        np.fill_diagonal(power, 0.0)
        scale = max(float(np.max(power)), 1.0)
        active = np.log10(np.maximum(power / scale, 1.0e-12))

        total_coupling_weight = max(float(np.sum(np.abs(coupling) ** 2)), 1.0)
        degenerate_pair = np.abs(gaps) <= degeneracy_tolerance
        np.fill_diagonal(degenerate_pair, False)
        resolved_degenerate = degenerate_pair & (
            np.abs(coupling) ** 2 > 1.0e-12 * total_coupling_weight
        )
        degenerate_vab = np.full(gaps.shape, np.nan, dtype=float)
        degenerate_vab[resolved_degenerate] = np.log10(
            np.abs(coupling[resolved_degenerate]) ** 2 / total_coupling_weight
        )

        gap_images.append(
            axes[0, column].imshow(near, origin="lower", cmap="magma", vmin=0.0, vmax=12.0)
        )
        active_images.append(
            axes[1, column].imshow(active, origin="lower", cmap="viridis", vmin=-12.0, vmax=0.0)
        )
        degenerate_cmap = plt.get_cmap("magma_r").copy()
        degenerate_cmap.set_bad("#f7f7f7")
        degenerate_images.append(
            axes[2, column].imshow(
                degenerate_vab,
                origin="lower",
                cmap=degenerate_cmap,
                vmin=-12.0,
                vmax=0.0,
            )
        )
        if not np.any(resolved_degenerate):
            axes[2, column].text(
                0.5,
                0.5,
                "no resolved $\\epsilon$-degenerate $V_{ab}$",
                transform=axes[2, column].transAxes,
                ha="center",
                va="center",
                fontsize=9,
                color="#374151",
            )
        else:
            resolved_count = int(np.count_nonzero(resolved_degenerate))
            resolved_weight = float(
                np.sum(np.abs(coupling[resolved_degenerate]) ** 2)
                / total_coupling_weight
            )
            axes[2, column].text(
                0.03,
                0.97,
                f"{resolved_count} entries; {100.0 * resolved_weight:.2f}% weight",
                transform=axes[2, column].transAxes,
                ha="left",
                va="top",
                fontsize=8,
                color="#374151",
            )
        axes[0, column].set_title(title, fontsize=12)
        axes[2, column].set_xlabel("sorted eigenstate index")
        if column == 0:
            axes[0, column].set_ylabel("raw near-degenerate pairs")
            axes[1, column].set_ylabel(r"active finite-time weight")
            axes[2, column].set_ylabel(r"$V_{ab}$ in $\epsilon$-degenerate blocks")
        for row in range(3):
            axes[row, column].set_xticks([])
            axes[row, column].set_yticks([])

    gap_cax = figure.add_axes([0.925, 0.695, 0.012, 0.205])
    gap_bar = figure.colorbar(gap_images[-1], cax=gap_cax)
    gap_bar.set_label(r"$-\log_{10}(|E_a-E_b|/\mathrm{bandwidth})$")
    active_cax = figure.add_axes([0.925, 0.385, 0.012, 0.205])
    active_bar = figure.colorbar(active_images[-1], cax=active_cax)
    active_bar.set_label(r"$\log_{10}$ normalized $|V_{ab}F_t(E_a-E_b)|^2$")
    degenerate_cax = figure.add_axes([0.925, 0.075, 0.012, 0.205])
    degenerate_bar = figure.colorbar(degenerate_images[-1], cax=degenerate_cax)
    degenerate_bar.set_label(r"$\log_{10}(|V_{ab}|^2/\operatorname{Tr}V^2)$")
    figure.suptitle(
        r"Raw degeneracy versus interaction activation ($\epsilon=2\times10^{-2}$)",
        fontsize=14,
    )
    figure.subplots_adjust(left=0.055, right=0.895, bottom=0.045, top=0.90, wspace=0.07, hspace=0.13)
    output = OUTPUT / "active_gap_comparison_brief.png"
    figure.savefig(output, dpi=230, bbox_inches="tight")
    plt.close(figure)
    return output


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    print(relative_unitary_map())
    print(three_outcomes())
    print(active_gap_comparison())


if __name__ == "__main__":
    main()
