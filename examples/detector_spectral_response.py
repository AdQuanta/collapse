"""
Detector spectral-response diagnostic for Born-rule candidate Hamiltonians.

This script tests the weak-coupling explanation

    M_{nu,mu}(t) ~ B_{nu,mu} F_t(E_D,nu - E_A,mu)

by extracting the central-qubit blocks of a candidate Hamiltonian,
diagonalizing the two detector-sector blocks, and plotting the weighted
transition-frequency density of the central-flip block B=H10.

It is intended for local N<=12 checks and for preparing focused Zeus follow-up
runs.  For larger N, the dense block diagonalization here can become too slow;
use the printed command parameters in a PBS job instead.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from born_hamiltonian_search import (  # noqa: E402
    Candidate,
    TeeWriter,
    _analyzer_from_diagonalization,
    _candidate_label,
    _default_worker_count,
    _diagonalize_candidate,
    _make_hamiltonian,
    _safe_plot_name,
)
from collapse.born import (  # noqa: E402
    born_ratio_from_radii,
    diagnostics_from_radii,
    theta_pair_from_radii,
)


def _as_float_list(values: Iterable[str]) -> list[float]:
    return [float(v) for v in values]


def _mode_to_hz0(mode: str, hz: float) -> float | None:
    if mode == "matched":
        return None
    if mode == "zero":
        return 0.0
    if mode == "half":
        return 0.5 * hz
    if mode == "minus":
        return -hz
    raise ValueError(f"Unknown hz0 mode: {mode!r}")


def _build_candidate_grid(args: argparse.Namespace) -> list[Candidate]:
    candidates: list[Candidate] = []
    for N in args.N:
        for hz in args.hz:
            for hz0_mode in args.hz0_modes:
                for jpm in args.Jpm:
                    for jxx in args.Jxx:
                        for jyy in args.Jyy:
                            for jz in args.Jz:
                                for jx in args.jx_unscaled:
                                    candidates.append(
                                        Candidate(
                                            model=args.model,
                                            N=N,
                                            J=args.J,
                                            Jpm=jpm,
                                            Jxx=jxx,
                                            Jyy=jyy,
                                            Jx_unscaled=jx,
                                            Jy_unscaled=args.jy_unscaled,
                                            Jz=jz,
                                            Jzx=args.Jzx,
                                            Jcpm_unscaled=args.jcpm_unscaled,
                                            hx=args.hx,
                                            hz=hz,
                                            hz0_mode=hz0_mode,
                                            connectivity=args.connectivity,
                                            central_coupling=args.central_coupling,
                                            seed=args.seed,
                                            disorder=args.disorder,
                                            disorder_strength=args.disorder_strength,
                                            disorder_strength_J=args.disorder_strength_J,
                                            disorder_strength_Jpm=args.disorder_strength_Jpm,
                                            disorder_strength_Jx=args.disorder_strength_Jx,
                                            disorder_strength_Jz=args.disorder_strength_Jz,
                                            disorder_strength_Jzx=args.disorder_strength_Jzx,
                                            disorder_strength_Jcpm=args.disorder_strength_Jcpm,
                                            disorder_strength_hx=args.disorder_strength_hx,
                                            disorder_strength_hz=args.disorder_strength_hz,
                                        )
                                    )
    return candidates


def central_blocks(candidate: Candidate) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return detector blocks A=H00, D=H11, and central-flip block B=H10."""

    if candidate.model == "cnot_copier":
        raise ValueError("CNOT copier is a unitary control, not a Hamiltonian response")
    ham = _make_hamiltonian(candidate, "numpy")
    H = np.asarray(ham.generate(), dtype=np.complex128)
    if H.shape[0] % 2:
        raise ValueError("Hamiltonian dimension must be even")
    half = H.shape[0] // 2
    A = H[:half, :half]
    D = H[half:, half:]
    B = H[half:, :half]
    return A, D, B


def spectral_response(
    candidate: Candidate,
    *,
    bins: int,
    delta_max: float | None,
    windows: list[float],
) -> dict[str, Any]:
    """Compute weighted transition-frequency density of the central-flip block."""

    A, D, B = central_blocks(candidate)
    EA, VA = np.linalg.eigh(A)
    ED, VD = np.linalg.eigh(D)
    B_eig = VD.conj().T @ B @ VA
    overlap_A_D = VA.conj().T @ VD
    weights = np.abs(B_eig) ** 2
    deltas = ED[:, None] - EA[None, :]

    flat_delta = deltas.ravel()
    flat_weight = weights.ravel()
    finite = np.isfinite(flat_delta) & np.isfinite(flat_weight) & (flat_weight > 0)
    flat_delta = flat_delta[finite]
    flat_weight = flat_weight[finite]

    total_weight = float(np.sum(flat_weight))
    if total_weight <= 0:
        raise ValueError("central-flip block has zero spectral weight")

    if delta_max is None:
        q = np.quantile(np.abs(flat_delta), 0.995)
        delta_max = float(max(q, max(windows, default=0.0) * 4.0, 1e-12))
    if delta_max <= 0:
        raise ValueError("delta_max must be positive")

    edges = np.linspace(-delta_max, delta_max, bins + 1)
    hist, _ = np.histogram(flat_delta, bins=edges, weights=flat_weight)
    density = hist / (total_weight * np.diff(edges))
    centers = (edges[:-1] + edges[1:]) / 2.0

    near_rows: list[dict[str, float]] = []
    for window in windows:
        if window <= 0:
            continue
        mask = np.abs(flat_delta) <= window
        weight = float(np.sum(flat_weight[mask]))
        near_rows.append(
            {
                "window": float(window),
                "near_zero_weight": weight,
                "near_zero_fraction": weight / total_weight,
                "near_zero_count": float(np.count_nonzero(mask)),
            }
        )

    norm_weights = flat_weight / total_weight
    participation = 1.0 / float(np.sum(norm_weights**2))
    entropy = -float(np.sum(norm_weights * np.log(norm_weights)))
    entropy_participation = math.exp(entropy)

    return {
        "candidate": candidate,
        "EA": EA,
        "ED": ED,
        "VA": VA,
        "VD": VD,
        "B_eig": B_eig,
        "overlap_A_D": overlap_A_D,
        "centers": centers,
        "density": density,
        "edges": edges,
        "deltas": flat_delta,
        "weights": flat_weight,
        "total_weight": total_weight,
        "frobenius_norm": math.sqrt(total_weight),
        "delta_max": float(delta_max),
        "near_rows": near_rows,
        "participation": participation,
        "entropy_participation": entropy_participation,
        "max_weight_fraction": float(np.max(norm_weights)),
    }


def _finite_time_integral(EA: np.ndarray, ED: np.ndarray, t_value: float) -> np.ndarray:
    """Return I_{nu,mu}=int exp[-i ED_nu(t-s)] exp[-i EA_mu s] ds."""

    delta = ED[:, None] - EA[None, :]
    out = np.empty(delta.shape, dtype=np.complex128)
    small = np.abs(delta) <= 1e-12
    degenerate_value = np.broadcast_to(
        t_value * np.exp(-1j * ED[:, None] * t_value),
        delta.shape,
    )
    out[small] = degenerate_value[small]
    if np.any(~small):
        phase = np.broadcast_to(np.exp(-1j * ED[:, None] * t_value), delta.shape)
        delta_nz = delta[~small]
        out[~small] = (
            phase[~small]
            * (np.exp(1j * delta_nz * t_value) - 1.0)
            / (1j * delta_nz)
        )
    return out


def weak_relative_evolution_matrix(response: dict[str, Any], t_value: float) -> np.ndarray:
    """First-order weak-coupling matrix for M(t)=U00^{-1}U10.

    The matrix is returned in the A-eigenbasis.  When A and D commute, this
    reduces to the familiar elementwise kernel B_{nu,mu} F_t(d_nu-a_mu), up to
    a unit-modulus phase.  Keeping the overlap matrix also covers weak
    longitudinal conditional terms where A and D have different eigenvectors.
    """

    EA = response["EA"]
    ED = response["ED"]
    B_eig = response["B_eig"]
    overlap = response["overlap_A_D"]
    integral = _finite_time_integral(EA, ED, t_value)
    return -1j * (np.exp(1j * EA * t_value)[:, None] * (overlap @ (B_eig * integral)))


def weak_kernel_diagnostics(
    response: dict[str, Any],
    times: list[float],
    *,
    n_theta: int,
    tail_fraction: float,
    n_log_bins: int,
) -> list[dict[str, Any]]:
    """Diagonalize the first-order weak kernel and score its angle statistics."""

    rows: list[dict[str, Any]] = []
    for t_value in times:
        matrix = weak_relative_evolution_matrix(response, t_value)
        eigenvalues = np.linalg.eigvals(matrix)
        radii = np.abs(eigenvalues)
        diag = diagnostics_from_radii(
            radii,
            n_theta=n_theta,
            tail_fraction=tail_fraction,
            n_log_bins=n_log_bins,
        )
        positive = radii[np.isfinite(radii) & (radii > 0)]
        q50 = float(np.percentile(positive, 50)) if positive.size else math.nan
        q99 = float(np.percentile(positive, 99)) if positive.size else math.nan
        rows.append(
            {
                "t": float(t_value),
                "born_similarity": float(diag.born_similarity),
                "mean_abs_ratio_error": float(diag.mean_abs_ratio_error),
                "reciprocity_error": float(diag.reciprocity_error),
                "tail_density_exponent": float(diag.tail_density_exponent),
                "radius_q99_over_q50": float(q99 / q50) if q50 > 0 else math.nan,
                "radius_atomic_fraction": float(
                    1.0 - np.unique(np.round(positive, decimals=12)).size / positive.size
                )
                if positive.size
                else math.nan,
                "weak_kernel_norm": float(np.linalg.norm(matrix, ord="fro")),
                "_radii": radii,
            }
        )
    return rows


def m_diagnostics(
    candidate: Candidate,
    times: list[float],
    *,
    backend: str,
    n_theta: int,
    tail_fraction: float,
    n_log_bins: int,
) -> list[dict[str, float]]:
    """Compute the existing M(t)-based Born diagnostics for comparison."""

    diagonalization = _diagonalize_candidate(candidate, backend)
    rows: list[dict[str, float]] = []
    for t_value in times:
        analyzer = _analyzer_from_diagonalization(diagonalization, t_value, candidate.N)
        radii = np.abs(analyzer.D0)
        diag = diagnostics_from_radii(
            radii,
            n_theta=n_theta,
            tail_fraction=tail_fraction,
            n_log_bins=n_log_bins,
        )
        positive = radii[np.isfinite(radii) & (radii > 0)]
        q50 = float(np.percentile(positive, 50)) if positive.size else math.nan
        q99 = float(np.percentile(positive, 99)) if positive.size else math.nan
        rows.append(
            {
                "t": float(t_value),
                "born_similarity": float(diag.born_similarity),
                "mean_abs_ratio_error": float(diag.mean_abs_ratio_error),
                "reciprocity_error": float(diag.reciprocity_error),
                "tail_density_exponent": float(diag.tail_density_exponent),
                "radius_q99_over_q50": float(q99 / q50) if q50 > 0 else math.nan,
                "radius_atomic_fraction": float(
                    1.0 - np.unique(np.round(positive, decimals=12)).size / positive.size
                )
                if positive.size
                else math.nan,
            }
        )
    return rows


def _time_tag(value: float) -> str:
    return f"{value:g}".replace(".", "p").replace("-", "m")


def plot_kernel_diagnostics(
    radii: np.ndarray,
    row: dict[str, Any],
    path: Path,
    *,
    title: str,
    n_theta: int,
) -> None:
    """Plot weak-kernel P(theta), mirror image, ratio, and radius density."""

    finite = np.asarray(radii, dtype=float)
    finite = finite[np.isfinite(finite) & (finite >= 0)]
    theta0, theta1 = theta_pair_from_radii(finite)
    ratio = born_ratio_from_radii(finite, n_theta=n_theta)

    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.0), dpi=150)

    ax = axes[0, 0]
    edges = np.linspace(0.0, np.pi, n_theta + 1)
    ax.hist(theta0, bins=edges, density=True, alpha=0.62, label=r"$P(\theta)$", color="#4C78A8")
    ax.hist(theta1, bins=edges, density=True, alpha=0.42, label=r"$P(\pi-\theta)$", color="#F58518")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("density")
    ax.set_title("weak-kernel angle distributions")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.18)

    ax = axes[0, 1]
    ax.plot(ratio.theta_centers, ratio.ratio, "o-", ms=3, lw=1.2, label=r"$R(\theta)$", color="#4C78A8")
    ax.plot(ratio.theta_centers, ratio.born, "-", lw=1.6, label=r"$\cos^2(\theta/2)$", color="#E45756")
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("ratio")
    ax.set_title("weak-kernel ratio")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.18)

    ax = axes[1, 0]
    positive = finite[finite > 0]
    if positive.size:
        log_edges = np.linspace(np.percentile(np.log10(positive), 1), np.percentile(np.log10(positive), 99), 50)
        if np.all(np.isfinite(log_edges)) and log_edges[-1] > log_edges[0]:
            ax.hist(np.log10(positive), bins=log_edges, density=True, color="#54A24B", alpha=0.72)
    ax.set_xlabel(r"$\log_{10} |\lambda(K_t)|$")
    ax.set_ylabel("density")
    ax.set_title("weak-kernel radius density")
    ax.grid(alpha=0.18)

    ax = axes[1, 1]
    ax.axis("off")
    text_lines = [
        title,
        "",
        f"t={row['t']:.6g}",
        f"S_born={row['born_similarity']:.6g}",
        f"mean |R-Born|={row['mean_abs_ratio_error']:.6g}",
        f"reciprocity={row['reciprocity_error']:.6g}",
        f"tail alpha={row['tail_density_exponent']:.6g}",
        f"q99/q50={row['radius_q99_over_q50']:.6g}",
        f"atom frac={row['radius_atomic_fraction']:.6g}",
        f"||K_t||_F={row['weak_kernel_norm']:.6g}",
    ]
    ax.text(0.02, 0.98, "\n".join(text_lines), va="top", family="monospace", fontsize=9)

    fig.suptitle(title, fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def plot_response(
    response: dict[str, Any],
    m_rows: list[dict[str, float]],
    path: Path,
    *,
    title: str,
) -> None:
    centers = response["centers"]
    density = response["density"]
    candidate: Candidate = response["candidate"]

    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.0), dpi=150)
    ax = axes[0, 0]
    width = response["edges"][1] - response["edges"][0]
    ax.bar(centers, density, width=width, color="#4C78A8", alpha=0.75)
    ax.axvline(0.0, color="black", lw=1.2, ls="--")
    for row in response["near_rows"]:
        window = row["window"]
        ax.axvspan(-window, window, color="#F58518", alpha=0.10)
    ax.set_xlabel(r"$\Delta=E_D-E_A$")
    ax.set_ylabel("weighted density")
    ax.set_title("central-flip spectral response")
    ax.grid(alpha=0.18)

    ax = axes[0, 1]
    windows = [row["window"] for row in response["near_rows"]]
    fracs = [row["near_zero_fraction"] for row in response["near_rows"]]
    if windows:
        ax.plot(windows, fracs, "o-", color="#54A24B")
        ax.set_xscale("log")
    ax.set_xlabel("near-zero window")
    ax.set_ylabel("weight fraction")
    ax.set_ylim(0.0, max(1e-6, min(1.0, max(fracs, default=0.0) * 1.25)))
    ax.grid(alpha=0.18, which="both")
    ax.set_title("weight near selected frequency")

    ax = axes[1, 0]
    if m_rows:
        times = [row["t"] for row in m_rows]
        scores = [row["born_similarity"] for row in m_rows]
        alphas = [row["tail_density_exponent"] for row in m_rows]
        ax.plot(times, scores, "o-", label=r"$S_{\rm born}$", color="#4C78A8")
        ax2 = ax.twinx()
        ax2.plot(times, alphas, "s--", label="tail alpha", color="#E45756")
        ax.set_xscale("log")
        ax.set_ylim(-0.05, 1.05)
        ax.set_xlabel("t")
        ax.set_ylabel(r"$S_{\rm born}$")
        ax2.set_ylabel("tail alpha")
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, fontsize=8, loc="best")
    else:
        ax.text(0.5, 0.5, "M(t) diagnostics skipped", ha="center", va="center")
    ax.grid(alpha=0.18, which="both")
    ax.set_title("existing M(t) diagnostics")

    ax = axes[1, 1]
    ax.axis("off")
    text_lines = [
        title,
        "",
        f"N={candidate.N}, model={candidate.model}, conn={candidate.connectivity}",
        f"cc={candidate.central_coupling}, hz0={candidate.hz0_mode}, hz={candidate.hz:g}",
        f"Jx_unscaled={candidate.Jx_unscaled:g}, Jpm={candidate.Jpm:g}",
        f"Jxx={candidate.Jxx:g}, Jyy={candidate.Jyy:g}, Jz={candidate.Jz:g}",
        "",
        f"||B||_F={response['frobenius_norm']:.6g}",
        f"participation={response['participation']:.3g}",
        f"entropy participation={response['entropy_participation']:.3g}",
        f"max weight fraction={response['max_weight_fraction']:.3g}",
    ]
    if response["near_rows"]:
        text_lines.append("")
        text_lines.append("near-zero windows:")
        for row in response["near_rows"]:
            text_lines.append(
                f"  |Delta|<={row['window']:.3g}: "
                f"{row['near_zero_fraction']:.3g}"
            )
    ax.text(0.02, 0.98, "\n".join(text_lines), va="top", family="monospace", fontsize=9)

    fig.suptitle(title, fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def write_outputs(
    out_dir: Path,
    response_rows: list[dict[str, Any]],
    m_rows_all: list[dict[str, Any]],
    kernel_rows_all: list[dict[str, Any]],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    response_csv = out_dir / "spectral_response_summary.csv"
    response_fields = [
        "label",
        "N",
        "model",
        "connectivity",
        "central_coupling",
        "hz0_mode",
        "hz",
        "Jpm",
        "Jxx",
        "Jyy",
        "Jz",
        "Jx_unscaled",
        "frobenius_norm",
        "participation",
        "entropy_participation",
        "max_weight_fraction",
        "window",
        "near_zero_fraction",
        "near_zero_count",
        "figure",
    ]
    with response_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=response_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(response_rows)

    m_csv = out_dir / "m_diagnostics_summary.csv"
    m_fields = [
        "label",
        "N",
        "model",
        "connectivity",
        "central_coupling",
        "hz0_mode",
        "hz",
        "Jpm",
        "Jxx",
        "Jyy",
        "Jz",
        "Jx_unscaled",
        "t",
        "born_similarity",
        "mean_abs_ratio_error",
        "reciprocity_error",
        "tail_density_exponent",
        "radius_q99_over_q50",
        "radius_atomic_fraction",
    ]
    with m_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=m_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(m_rows_all)

    kernel_csv = out_dir / "weak_kernel_diagnostics_summary.csv"
    kernel_fields = [
        "label",
        "N",
        "model",
        "connectivity",
        "central_coupling",
        "hz0_mode",
        "hz",
        "Jpm",
        "Jxx",
        "Jyy",
        "Jz",
        "Jx_unscaled",
        "t",
        "born_similarity",
        "mean_abs_ratio_error",
        "reciprocity_error",
        "tail_density_exponent",
        "radius_q99_over_q50",
        "radius_atomic_fraction",
        "weak_kernel_norm",
        "weak_kernel_figure",
    ]
    with kernel_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=kernel_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(kernel_rows_all)

    md = out_dir / "summary.md"
    lines = [
        "# Detector spectral-response diagnostic",
        "",
        "This diagnostic extracts the central-qubit Hamiltonian blocks and checks",
        "the weak-coupling spectral kernel behind the first-order expression",
        "",
        "$$",
        "M_{\\nu\\mu}^{(1)}(t)\\sim\\epsilon B_{\\nu\\mu}F_t(d_\\nu-a_\\mu).",
        "$$",
        "",
        f"- Spectral summary CSV: `{response_csv.name}`",
        f"- M(t) diagnostics CSV: `{m_csv.name}`",
        f"- Weak-kernel diagnostics CSV: `{kernel_csv.name}`",
        "",
        "| label | window | near-zero fraction | participation | figure |",
        "|:---|---:|---:|---:|:---|",
    ]
    for row in response_rows:
        lines.append(
            f"| `{row['label']}` | {row['window']:.4g} | "
            f"{row['near_zero_fraction']:.4g} | {row['participation']:.4g} | "
            f"[figure]({Path(row['figure']).name}) |"
        )
    if kernel_rows_all:
        lines.extend(
            [
                "",
                "## Weak-kernel finite-time diagnostics",
                "",
                "| label | t | S_born | reciprocity | q99/q50 | figure |",
                "|:---|---:|---:|---:|---:|:---|",
            ]
        )
        for row in kernel_rows_all:
            figure = row.get("weak_kernel_figure", "")
            lines.append(
                f"| `{row['label']}` | {row['t']:.6g} | "
                f"{row['born_similarity']:.4g} | {row['reciprocity_error']:.4g} | "
                f"{row['radius_q99_over_q50']:.4g} | "
                f"[figure]({Path(figure).name}) |"
            )
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, nargs="+", default=[10])
    parser.add_argument("--model", choices=["single_pixel", "dimerized_pixel"], default="single_pixel")
    parser.add_argument("--connectivity", choices=["chain", "ring", "all_to_all"], default="ring")
    parser.add_argument(
        "--central-coupling",
        choices=["auto", "all", "first", "last", "ends"],
        default="all",
    )
    parser.add_argument("--hz0-modes", nargs="+", default=["zero", "matched"], choices=["matched", "zero", "half", "minus"])
    parser.add_argument("--J", type=float, default=1.0)
    parser.add_argument("--Jpm", type=float, nargs="+", default=[0.05])
    parser.add_argument("--Jxx", type=float, nargs="+", default=[0.0])
    parser.add_argument("--Jyy", type=float, nargs="+", default=[0.0])
    parser.add_argument("--Jz", type=float, nargs="+", default=[0.0])
    parser.add_argument("--Jzx", type=float, default=0.0)
    parser.add_argument("--jx-unscaled", type=float, nargs="+", default=[0.05])
    parser.add_argument("--jy-unscaled", type=float, default=0.0)
    parser.add_argument("--jcpm-unscaled", type=float, default=0.0)
    parser.add_argument("--hx", type=float, default=0.0)
    parser.add_argument("--hz", type=float, nargs="+", default=[0.1])
    parser.add_argument("--seed", type=int, default=44)
    parser.add_argument("--disorder", choices=["none", "uniform", "gaussian", "lorentzian"], default="none")
    parser.add_argument("--disorder-strength", type=float, default=0.0)
    parser.add_argument("--disorder-strength-J", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jpm", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jx", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jz", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jzx", type=float, default=0.0)
    parser.add_argument("--disorder-strength-Jcpm", type=float, default=0.0)
    parser.add_argument("--disorder-strength-hx", type=float, default=0.0)
    parser.add_argument("--disorder-strength-hz", type=float, default=0.0)
    parser.add_argument("--times", type=float, nargs="+", default=[1000.0, 3162.0])
    parser.add_argument("--windows", type=float, nargs="+", default=None, help="Near-zero Delta windows. Defaults to 1/t for each time.")
    parser.add_argument("--bins", type=int, default=180)
    parser.add_argument("--delta-max", type=float, default=None)
    parser.add_argument("--m-backend", choices=["auto", "quspin", "numpy"], default="numpy")
    parser.add_argument("--n-theta", type=int, default=100)
    parser.add_argument("--tail-fraction", type=float, default=0.10)
    parser.add_argument("--log-bins", type=int, default=50)
    parser.add_argument(
        "--workers",
        type=int,
        default=_default_worker_count(),
        help="Number of independent candidates to evaluate in parallel.",
    )
    parser.add_argument("--skip-m-diagnostics", action="store_true")
    parser.add_argument(
        "--compute-kernel-diagnostics",
        action="store_true",
        help="Diagonalize the first-order finite-time weak kernel K_t and plot its P(theta), mirror image, and ratio.",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("figures/detector_spectral_response"))
    parser.add_argument("--log-file", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    log_file = args.log_file or args.out_dir / "run.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with log_file.open("w", encoding="utf-8") as log_fh:
        tee = TeeWriter(sys.stdout, log_fh)
        with np.printoptions(precision=5, suppress=True):
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = tee
            sys.stderr = tee
            try:
                _main_impl(args)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr


def _main_impl(args: argparse.Namespace) -> None:
    start = time.time()
    candidates = _build_candidate_grid(args)
    args.workers = max(1, int(args.workers))
    windows = args.windows if args.windows is not None else sorted({1.0 / t for t in args.times if t > 0})
    print(f"Candidates: {len(candidates)}")
    print(f"Windows: {windows}")
    print(f"Output: {args.out_dir}")
    print(f"Worker processes: {args.workers}")

    response_rows: list[dict[str, Any]] = []
    m_rows_all: list[dict[str, Any]] = []
    kernel_rows_all: list[dict[str, Any]] = []
    manifest: list[dict[str, Any]] = []

    jobs = [
        (
            candidate,
            windows,
            list(args.times),
            args.bins,
            args.delta_max,
            args.skip_m_diagnostics,
            args.m_backend,
            args.n_theta,
            args.tail_fraction,
            args.log_bins,
            args.compute_kernel_diagnostics,
            args.out_dir,
        )
        for candidate in candidates
    ]
    if args.workers == 1 or len(jobs) <= 1:
        for idx, job in enumerate(jobs, start=1):
            print(f"[{idx}/{len(jobs)}] {_candidate_label(job[0])}", flush=True)
            response_part, m_part, kernel_part, manifest_item, log_lines = _evaluate_detector_candidate_job(job)
            response_rows.extend(response_part)
            m_rows_all.extend(m_part)
            kernel_rows_all.extend(kernel_part)
            manifest.append(manifest_item)
            for line in log_lines:
                print(line)
    else:
        n_workers = min(args.workers, len(jobs))
        print(f"Submitting {len(jobs)} detector spectral-response jobs to {n_workers} workers", flush=True)
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            future_to_candidate = {
                pool.submit(_evaluate_detector_candidate_job, job): job[0]
                for job in jobs
            }
            for done_idx, future in enumerate(as_completed(future_to_candidate), start=1):
                candidate = future_to_candidate[future]
                try:
                    response_part, m_part, kernel_part, manifest_item, log_lines = future.result()
                except Exception as exc:
                    raise RuntimeError(f"Worker failed for {_candidate_label(candidate)}") from exc
                response_rows.extend(response_part)
                m_rows_all.extend(m_part)
                kernel_rows_all.extend(kernel_part)
                manifest.append(manifest_item)
                print(f"[{done_idx}/{len(jobs)}] completed {_candidate_label(candidate)}", flush=True)
                for line in log_lines:
                    print(line)

    write_outputs(args.out_dir, response_rows, m_rows_all, kernel_rows_all)
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Wrote {args.out_dir / 'summary.md'}")
    print(f"Elapsed seconds: {time.time() - start:.2f}")


def _candidate_output_fields(candidate: Candidate, label: str) -> dict[str, Any]:
    return {
        "label": label,
        "N": candidate.N,
        "model": candidate.model,
        "connectivity": candidate.connectivity,
        "central_coupling": candidate.central_coupling,
        "hz0_mode": candidate.hz0_mode,
        "hz": candidate.hz,
        "Jpm": candidate.Jpm,
        "Jxx": candidate.Jxx,
        "Jyy": candidate.Jyy,
        "Jz": candidate.Jz,
        "Jx_unscaled": candidate.Jx_unscaled,
    }


def _evaluate_detector_candidate_job(
    payload: tuple[
        Candidate,
        list[float],
        list[float],
        int,
        float | None,
        bool,
        str,
        int,
        float,
        int,
        bool,
        Path,
    ],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], list[str]]:
    (
        candidate,
        windows,
        times,
        bins,
        delta_max,
        skip_m_diagnostics,
        m_backend,
        n_theta,
        tail_fraction,
        log_bins,
        compute_kernel_diagnostics,
        out_dir,
    ) = payload
    label = _candidate_label(candidate)
    log_lines: list[str] = []
    response = spectral_response(candidate, bins=bins, delta_max=delta_max, windows=windows)
    if skip_m_diagnostics:
        m_rows: list[dict[str, float]] = []
    else:
        m_rows = m_diagnostics(
            candidate,
            times,
            backend=m_backend,
            n_theta=n_theta,
            tail_fraction=tail_fraction,
            n_log_bins=log_bins,
        )
    if compute_kernel_diagnostics:
        kernel_rows = weak_kernel_diagnostics(
            response,
            times,
            n_theta=n_theta,
            tail_fraction=tail_fraction,
            n_log_bins=log_bins,
        )
    else:
        kernel_rows = []

    figure = out_dir / f"{_safe_plot_name(label)}_spectral_response.png"
    plot_response(response, m_rows, figure, title=label)
    log_lines.append(f"  figure: {figure}")
    for row in kernel_rows:
        kernel_figure = out_dir / f"{_safe_plot_name(label)}_weak_kernel_t{_time_tag(row['t'])}.png"
        plot_kernel_diagnostics(
            row["_radii"],
            row,
            kernel_figure,
            title=f"{label} weak kernel",
            n_theta=n_theta,
        )
        row["weak_kernel_figure"] = str(kernel_figure)
        log_lines.append(f"  weak-kernel figure: {kernel_figure}")

    base_fields = _candidate_output_fields(candidate, label)
    response_rows = []
    for row in response["near_rows"]:
        response_rows.append(
            {
                **base_fields,
                "frobenius_norm": response["frobenius_norm"],
                "participation": response["participation"],
                "entropy_participation": response["entropy_participation"],
                "max_weight_fraction": response["max_weight_fraction"],
                "window": row["window"],
                "near_zero_fraction": row["near_zero_fraction"],
                "near_zero_count": row["near_zero_count"],
                "figure": str(figure),
            }
        )

    m_rows_all = []
    for row in m_rows:
        m_rows_all.append({**dict(row), **base_fields})

    kernel_rows_all: list[dict[str, Any]] = []
    for row in kernel_rows:
        output_row = dict(row)
        output_row.pop("_radii", None)
        output_row.update(base_fields)
        kernel_rows_all.append(output_row)

    manifest_item = {
        "candidate": asdict(candidate),
        "label": label,
        "figure": str(figure),
        "spectral": {
            "frobenius_norm": response["frobenius_norm"],
            "participation": response["participation"],
            "entropy_participation": response["entropy_participation"],
            "max_weight_fraction": response["max_weight_fraction"],
            "near_rows": response["near_rows"],
        },
        "m_diagnostics": m_rows,
        "weak_kernel_diagnostics": kernel_rows_all,
    }
    return response_rows, m_rows_all, kernel_rows_all, manifest_item, log_lines


if __name__ == "__main__":
    main()
