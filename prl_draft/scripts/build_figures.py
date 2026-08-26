"""Build the trusted numerical figures for the PRL package.

This script performs post-processing only.  It does not rerun a many-body
simulation.  Inputs are the post-cutoff matched-field root spectra and the
derived 24-row summary table already present in the repository.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplconfig")
)

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import sph_harm_y


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "prl_draft" / "figures"
SUMMARY_CSV = (
    ROOT
    / "reports"
    / "zeus_single_pixel_analysis_2026-07-16"
    / "jointly_gated_born_candidates.csv"
)
RAW_N16_T1E4 = (
    ROOT
    / "work"
    / "zeus_single_pixel_atlas_scaling_2026-07-14"
    / "hz0"
    / "N16"
    / "raw"
    / "N16"
    / "hz0_+0.1000"
    / "raw_t10000.npz"
)
EXPECTED_RAW_SHA256 = (
    "e467b5efa6a5b8b7e3e7333a06555007b629a26bbeac2b21cd3da27d88313d59"
)


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of *path*."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_summary_rows() -> list[dict[str, float]]:
    """Load and validate the 24 matched-field, jointly gated rows."""

    with SUMMARY_CSV.open(newline="", encoding="utf-8") as handle:
        raw = list(csv.DictReader(handle))
    rows = [
        {
            "n": float(row["detector_n"]),
            "t": float(row["t"]),
            "score": float(row["S_born"]),
            "coverage": float(row["angular_bin_coverage"]),
            "harmonic": float(row["phi_harmonic_2"]),
            "hz": float(row["hz"]),
            "hz0": float(row["hz0"]),
            "j": float(row["J"]),
            "jpm": float(row["Jpm"]),
            "jx": float(row["Jx"]),
        }
        for row in raw
    ]
    if len(rows) != 24:
        raise ValueError(f"Expected 24 jointly gated rows, found {len(rows)}")
    for row in rows:
        if not (
            row["hz"] == row["hz0"] == 0.1
            and row["j"] == 1.0
            and row["jpm"] == 0.0
            and row["jx"] == 0.01
            and row["coverage"] == 1.0
        ):
            raise ValueError(f"Unexpected row in matched-field table: {row}")
    return rows


def build_scaling_figure(rows: list[dict[str, float]]) -> dict[str, object]:
    """Render the finite-size polar-score and azimuthal-harmonic panels."""

    sizes = sorted({int(row["n"]) for row in rows})
    times = sorted({row["t"] for row in rows})
    if sizes != list(range(11, 17)) or times != [1e3, 1e4, 1e5, 1e6]:
        raise ValueError(f"Unexpected support: N={sizes}, times={times}")

    plt.rcParams.update(
        {
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "axes.titlesize": 8.5,
            "legend.fontsize": 6.8,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(7.05, 2.55), constrained_layout=True)
    colors = plt.cm.viridis(np.linspace(0.12, 0.88, len(times)))

    for time, color in zip(times, colors, strict=True):
        subset = sorted((r for r in rows if r["t"] == time), key=lambda r: r["n"])
        axes[0].plot(
            [r["n"] for r in subset],
            [r["score"] for r in subset],
            "o-",
            lw=0.9,
            ms=3.0,
            alpha=0.68,
            color=color,
            label=rf"$t=10^{{{int(np.log10(time))}}}$",
        )
    medians = [
        float(np.median([r["score"] for r in rows if int(r["n"]) == n]))
        for n in sizes
    ]
    maxima = [
        float(max(r["score"] for r in rows if int(r["n"]) == n)) for n in sizes
    ]
    axes[0].plot(sizes, medians, "ko-", lw=1.6, ms=4.0, label="four-time median")
    axes[0].plot(sizes, maxima, "k--", lw=1.1, label="maximum")
    axes[0].axhline(0.0, color="0.35", ls=":", lw=1.0)
    axes[0].text(
        0.03,
        0.88,
        r"Haar intensity baseline $S_{\rm B}=0$",
        transform=axes[0].transAxes,
        color="0.25",
        fontsize=6.7,
    )
    axes[0].set(
        xlabel="detector spins $N$",
        ylabel=r"polar root-count score $S_{\rm B}$",
        ylim=(-0.04, 1.0),
    )
    axes[0].legend(frameon=False, ncol=2, loc="lower right")
    axes[0].text(0.02, 0.97, "(a)", transform=axes[0].transAxes, va="top", fontweight="bold")

    for time, color in zip(times, colors, strict=True):
        subset = sorted((r for r in rows if r["t"] == time), key=lambda r: r["n"])
        axes[1].plot(
            [r["n"] for r in subset],
            [r["harmonic"] for r in subset],
            "o-",
            lw=0.9,
            ms=3.0,
            alpha=0.68,
            color=color,
        )
    harmonic_medians = [
        float(np.median([r["harmonic"] for r in rows if int(r["n"]) == n]))
        for n in sizes
    ]
    axes[1].plot(sizes, harmonic_medians, "ko-", lw=1.6, ms=4.0, label="four-time median")
    axes[1].axhline(0.25, color="0.35", ls="--", lw=1.0, label="analysis gate")
    axes[1].set(
        xlabel="detector spins $N$",
        ylabel=r"azimuthal harmonic $|c_2|$",
        ylim=(0.0, 0.27),
    )
    axes[1].legend(frameon=False, loc="upper right", bbox_to_anchor=(0.99, 0.80))
    axes[1].text(
        0.98,
        0.51,
        "polar coverage = 1\nfor all 24 rows",
        transform=axes[1].transAxes,
        ha="right",
        va="bottom",
        fontsize=6.7,
    )
    axes[1].text(0.02, 0.97, "(b)", transform=axes[1].transAxes, va="top", fontweight="bold")

    for axis in axes:
        axis.set_xticks(sizes)
        axis.grid(alpha=0.18, lw=0.6)

    fig.savefig(OUTPUT_DIR / "matched_field_scaling.pdf")
    fig.savefig(OUTPUT_DIR / "matched_field_scaling.png", dpi=260)
    plt.close(fig)
    return {
        "sizes": sizes,
        "times": times,
        "median_score": dict(zip(map(str, sizes), medians, strict=True)),
        "maximum_score": dict(zip(map(str, sizes), maxima, strict=True)),
        "median_abs_c2": dict(zip(map(str, sizes), harmonic_medians, strict=True)),
        "haar_ensemble_mean_score": 0.0,
    }


def antipodal_histograms(
    eigenvalues: np.ndarray, phi_bins: int, mu_bins: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return equal-area root and antipodal-label histograms."""

    phi = np.angle(eigenvalues)
    abs_sq = np.abs(eigenvalues) ** 2
    mu = (1.0 - abs_sq) / (1.0 + abs_sq)
    phi_antipode = (phi + 2.0 * np.pi) % (2.0 * np.pi) - np.pi
    phi_edges = np.linspace(-np.pi, np.pi, phi_bins + 1)
    mu_edges = np.linspace(-1.0, 1.0, mu_bins + 1)
    root_counts = np.histogram2d(mu, phi, bins=[mu_edges, phi_edges])[0]
    antipode_counts = np.histogram2d(
        -mu, phi_antipode, bins=[mu_edges, phi_edges]
    )[0]
    total = root_counts + antipode_counts
    asymmetry = np.divide(
        root_counts - antipode_counts,
        total,
        out=np.full_like(total, np.nan, dtype=float),
        where=total > 0,
    )
    return root_counts, antipode_counts, total, asymmetry, mu_edges


def full_sphere_metrics(
    eigenvalues: np.ndarray, phi_bins: int, mu_bins: int
) -> dict[str, float | int]:
    """Compute declared equal-area full-sphere residual diagnostics."""

    _, _, total, asymmetry, mu_edges = antipodal_histograms(
        eigenvalues, phi_bins, mu_bins
    )
    mu_centers = 0.5 * (mu_edges[:-1] + mu_edges[1:])
    target = np.broadcast_to(mu_centers[:, None], asymmetry.shape)
    mask = np.isfinite(asymmetry)
    residual = asymmetry - target
    weighted_rms = np.sqrt(
        np.sum(total[mask] * residual[mask] ** 2) / np.sum(total[mask])
    )
    correlation = np.corrcoef(asymmetry[mask], target[mask])[0, 1]
    phi_edges = np.linspace(-np.pi, np.pi, phi_bins + 1)
    phi_centers = 0.5 * (phi_edges[:-1] + phi_edges[1:])
    mu_grid, phi_grid = np.meshgrid(mu_centers, phi_centers, indexing="ij")
    transverse = np.sqrt(np.maximum(0.0, 1.0 - mu_grid**2))
    design = np.column_stack(
        [
            (transverse * np.cos(phi_grid)).ravel(),
            (transverse * np.sin(phi_grid)).ravel(),
            mu_grid.ravel(),
        ]
    )
    weights = total.ravel()
    values = asymmetry.ravel()
    valid = np.isfinite(values) & (weights > 0)
    normal = design[valid].T @ (weights[valid, None] * design[valid])
    rhs = design[valid].T @ (weights[valid] * values[valid])
    dipole = np.linalg.solve(normal, rhs)
    fitted = design[valid] @ dipole
    fitted_rms = np.sqrt(
        np.sum(weights[valid] * (values[valid] - fitted) ** 2)
        / np.sum(weights[valid])
    )
    dipole_amplitude = float(np.linalg.norm(dipole))
    dipole_axis = dipole / dipole_amplitude
    return {
        "phi_bins": phi_bins,
        "mu_bins": mu_bins,
        "empty_bins": int(np.sum(~mask)),
        "minimum_positive_count": int(np.min(total[mask])),
        "count_weighted_rms_residual": float(weighted_rms),
        "pearson_correlation_with_mu": float(correlation),
        "fitted_dipole_vector": [float(value) for value in dipole],
        "fitted_dipole_amplitude": dipole_amplitude,
        "fitted_dipole_axis": [float(value) for value in dipole_axis],
        "count_weighted_rms_after_dipole_fit": float(fitted_rms),
    }


def harmonic_power_spectrum(
    asymmetry: np.ndarray,
    mu_edges: np.ndarray,
    phi_bins: int,
    *,
    l_max: int = 7,
) -> dict[str, object]:
    """Project an equal-area asymmetry grid onto harmonics through ``l_max``.

    The bins are uniform in ``mu=cos(theta)`` and ``phi``, so the midpoint
    Riemann weight is the constant solid angle ``dmu*dphi``.  Exact antipodal
    pairing makes even-degree power a numerical-consistency diagnostic.
    """

    if np.any(~np.isfinite(asymmetry)):
        raise ValueError("harmonic projection requires a fully occupied grid")
    mu_centers = 0.5 * (mu_edges[:-1] + mu_edges[1:])
    phi_edges = np.linspace(-np.pi, np.pi, phi_bins + 1)
    phi_centers = 0.5 * (phi_edges[:-1] + phi_edges[1:])
    theta = np.arccos(mu_centers)
    solid_angle = float((mu_edges[1] - mu_edges[0]) * (phi_edges[1] - phi_edges[0]))

    powers: list[float] = []
    for degree in range(l_max + 1):
        power = 0.0
        for order in range(-degree, degree + 1):
            harmonic = sph_harm_y(
                degree,
                order,
                theta[:, None],
                phi_centers[None, :],
            )
            coefficient = solid_angle * np.sum(asymmetry * np.conj(harmonic))
            power += float(abs(coefficient) ** 2)
        powers.append(power)

    odd_power = float(sum(powers[1::2]))
    even_power = float(sum(powers[0::2]))
    total_power = odd_power + even_power
    higher_odd_power = float(sum(powers[3::2]))
    return {
        "l_max": int(l_max),
        "power_by_l": powers,
        "dipole_fraction_of_odd_power": float(powers[1] / odd_power),
        "higher_odd_fraction_of_odd_power": float(higher_odd_power / odd_power),
        "even_fraction_of_total_power": float(even_power / total_power),
    }


def weighted_dipole_fit(
    asymmetry: np.ndarray,
    total_counts: np.ndarray,
    mu_edges: np.ndarray,
    phi_bins: int,
) -> dict[str, object]:
    """Fit ``a(phi,mu)=b dot r`` by total-count-weighted least squares."""

    if np.any(~np.isfinite(asymmetry)):
        raise ValueError("dipole fit requires a fully occupied grid")
    mu = 0.5 * (mu_edges[:-1] + mu_edges[1:])
    phi_edges = np.linspace(-np.pi, np.pi, phi_bins + 1)
    phi = 0.5 * (phi_edges[:-1] + phi_edges[1:])
    transverse = np.sqrt(1.0 - mu[:, None] ** 2)
    design = np.column_stack(
        [
            (transverse * np.cos(phi[None, :])).ravel(),
            (transverse * np.sin(phi[None, :])).ravel(),
            np.broadcast_to(mu[:, None], asymmetry.shape).ravel(),
        ]
    )
    weights = total_counts.ravel()
    values = asymmetry.ravel()
    normal = design.T @ (weights[:, None] * design)
    rhs = design.T @ (weights * values)
    vector = np.linalg.solve(normal, rhs)
    amplitude = float(np.linalg.norm(vector))
    axis = vector / amplitude
    residual = values - design @ vector
    weighted_rms = float(np.sqrt(np.sum(weights * residual**2) / np.sum(weights)))
    return {
        "coefficient_vector_xyz": vector.tolist(),
        "amplitude": amplitude,
        "axis_xyz": axis.tolist(),
        "count_weighted_rms_residual": weighted_rms,
        "intercept_included": False,
    }


def build_full_sphere_figure() -> dict[str, object]:
    """Render a full-(phi, cos theta) outcome-root asymmetry diagnostic."""

    digest = sha256(RAW_N16_T1E4)
    if digest != EXPECTED_RAW_SHA256:
        raise ValueError(f"Unexpected raw-data hash: {digest}")
    with np.load(RAW_N16_T1E4, allow_pickle=False) as data:
        eigenvalues = np.asarray(data["eigenvalues"], dtype=np.complex128)
        scalars = {
            key: data[key].item()
            for key in [
                "hz0",
                "hz",
                "J",
                "Jx_edge",
                "Jx",
                "detector_n",
                "total_qubits",
            ]
        }
    eigenvalues = eigenvalues[np.isfinite(eigenvalues)]
    if eigenvalues.shape != (65536,):
        raise ValueError(f"Expected 65,536 finite roots, found {eigenvalues.shape}")

    phi_bins, mu_bins = 36, 18
    _, _, total, asymmetry, mu_edges = antipodal_histograms(
        eigenvalues, phi_bins, mu_bins
    )
    phi_edges = np.linspace(-np.pi, np.pi, phi_bins + 1)
    mu_centers = 0.5 * (mu_edges[:-1] + mu_edges[1:])
    target = np.broadcast_to(mu_centers[:, None], asymmetry.shape)
    residual = asymmetry - target
    primary_metrics = full_sphere_metrics(eigenvalues, phi_bins, mu_bins)
    harmonic_metrics = harmonic_power_spectrum(
        asymmetry,
        mu_edges,
        phi_bins,
        l_max=7,
    )
    dipole_fit = weighted_dipole_fit(
        asymmetry,
        total,
        mu_edges,
        phi_bins,
    )
    sensitivity = [
        full_sphere_metrics(eigenvalues, p_bins, m_bins)
        for p_bins, m_bins in [(24, 12), (36, 18), (48, 24), (72, 36)]
    ]
    harmonic_sensitivity: list[dict[str, object]] = []
    for p_bins, m_bins in [(24, 12), (36, 18), (48, 24)]:
        _, _, _, grid_asymmetry, grid_mu_edges = antipodal_histograms(
            eigenvalues,
            p_bins,
            m_bins,
        )
        metrics = harmonic_power_spectrum(
            grid_asymmetry,
            grid_mu_edges,
            p_bins,
            l_max=7,
        )
        metrics.update({"phi_bins": p_bins, "mu_bins": m_bins})
        harmonic_sensitivity.append(metrics)

    plt.rcParams.update({"font.size": 8.0, "axes.labelsize": 8.0, "axes.titlesize": 8.0})
    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.35), constrained_layout=True)
    extent = (-np.pi, np.pi, -1.0, 1.0)
    images = [
        axes[0].imshow(
            asymmetry,
            origin="lower",
            aspect="auto",
            extent=extent,
            cmap="coolwarm",
            vmin=-1.0,
            vmax=1.0,
            interpolation="nearest",
        ),
        axes[1].imshow(
            target,
            origin="lower",
            aspect="auto",
            extent=extent,
            cmap="coolwarm",
            vmin=-1.0,
            vmax=1.0,
            interpolation="nearest",
        ),
        axes[2].imshow(
            residual,
            origin="lower",
            aspect="auto",
            extent=extent,
            cmap="PuOr",
            vmin=-0.45,
            vmax=0.45,
            interpolation="nearest",
        ),
    ]
    titles = [
        r"(a) root-label asymmetry $a(\phi,\mu)$",
        r"(b) Born dipole $a_{\rm B}=\mu$",
        r"(c) residual $a-a_{\rm B}$",
    ]
    for axis, title in zip(axes, titles, strict=True):
        axis.set_title(title, pad=3)
        axis.set_xlabel(r"azimuth $\phi$")
        axis.set_xticks([-np.pi, 0.0, np.pi], [r"$-\pi$", "0", r"$\pi$"])
        axis.set_yticks([-1.0, 0.0, 1.0])
    axes[0].set_ylabel(r"$\mu=\cos\theta$")
    axes[1].set_yticklabels([])
    axes[2].set_yticklabels([])
    fig.colorbar(images[0], ax=axes[:2], shrink=0.84, pad=0.015, label="asymmetry")
    fig.colorbar(images[2], ax=axes[2], shrink=0.84, pad=0.02, label="residual")
    axes[2].text(
        0.98,
        0.97,
        (
            rf"weighted RMS $={primary_metrics['count_weighted_rms_residual']:.3f}$"
            "\n"
            rf"$\ell=1$ / odd $\ell\leq7={harmonic_metrics['dipole_fraction_of_odd_power']:.3f}$"
        ),
        transform=axes[2].transAxes,
        ha="right",
        va="top",
        fontsize=6.2,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.8, "edgecolor": "0.7"},
    )
    fig.savefig(OUTPUT_DIR / "full_sphere_matched.pdf")
    fig.savefig(OUTPUT_DIR / "full_sphere_matched.png", dpi=280)
    plt.close(fig)

    return {
        "raw_file": str(RAW_N16_T1E4.relative_to(ROOT)),
        "raw_sha256": digest,
        "finite_root_count": int(eigenvalues.size),
        "time": 1e4,
        "parameters": scalars,
        "branch_convention": (
            "label 0 is the production relative-evolution root cloud; label 1 "
            "is its exact Bloch antipode.  By complementary-minor duality these "
            "are the two forward outcome root locations for the inverse propagator."
        ),
        "primary_binning": primary_metrics,
        "spherical_harmonics": harmonic_metrics,
        "spherical_harmonic_binning_sensitivity": harmonic_sensitivity,
        "weighted_free_dipole_fit": dipole_fit,
        "binning_sensitivity": sensitivity,
        "minimum_total_count_primary_grid": int(np.min(total)),
    }


def main() -> None:
    """Build figures and their machine-readable post-processing manifest."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_summary_rows()
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "postprocessing_only": True,
        "scaling_figure": build_scaling_figure(rows),
        "full_sphere_figure": build_full_sphere_figure(),
        "source_summary_csv": str(SUMMARY_CSV.relative_to(ROOT)),
        "source_summary_sha256": sha256(SUMMARY_CSV),
    }
    with (OUTPUT_DIR / "figure_manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
