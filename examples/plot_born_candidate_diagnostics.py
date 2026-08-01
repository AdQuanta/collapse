"""
Plot theta-ratio and tail diagnostics for selected Born-search candidates.

This is the visual companion to ``born_candidate_stability.py``.  It reads
rows from ``summary_rows.csv`` or ``results.csv``, selects candidate/time rows
with the same filters, diagonalizes each Hamiltonian, and saves per-row PNG
figures for group-meeting inspection.
"""

from __future__ import annotations

import argparse
import contextlib
import math
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from born_candidate_stability import (  # noqa: E402
    _candidate_from_row,
    _float_or_nan,
    _fmt,
    _load_rows,
    select_rows,
)
from born_hamiltonian_search import (  # noqa: E402
    TeeWriter,
    _analyzer_from_diagonalization,
    _angles_and_radii,
    _candidate_label,
    _diagonalize_candidate,
    _disorder_signature,
    _default_worker_count,
    _energy_metrics_from_diagonalization,
    _plot_energy_spectrum_panel,
    heavy_tail_metrics,
    objective_score,
)
from collapse.born import (  # noqa: E402
    born_ratio_from_radii,
    diagnostics_from_radii,
    hill_tail_exponent,
    reciprocity_error_from_radii,
)


def _safe_name(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.=-]+", "_", text)
    return text.strip("_")[:180]


def _row_signature(row: dict, candidate, time_value: float) -> str:
    return (
        f"{row.get('family', '')} | N={candidate.N}, {candidate.connectivity}, "
        f"cc={candidate.central_coupling}, "
        f"hz0={candidate.hz0_mode}, dis={_disorder_signature(candidate)}, "
        f"J={candidate.J:g}, Jx={candidate.Jx_unscaled:g}, "
        f"Jy={candidate.Jy_unscaled:g}, hz={candidate.hz:g}, "
        f"Jpm={candidate.Jpm:g}, Jxx={candidate.Jxx:g}, Jyy={candidate.Jyy:g}, "
        f"Jz={candidate.Jz:g}, Jzx={candidate.Jzx:g}, "
        f"Jcpm={candidate.Jcpm_unscaled:g}, t={time_value:g}"
    )


def _theta_hist_and_ratio(radii: np.ndarray, bins: int, pseudocount: float):
    theta0 = 2.0 * np.arctan(radii)
    theta1 = np.pi - theta0
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2.0
    h0, _ = np.histogram(theta0, bins=edges)
    h1, _ = np.histogram(theta1, bins=edges)
    total = h0 + h1
    h0_density, _ = np.histogram(theta0, bins=edges, density=True)
    h1_density, _ = np.histogram(theta1, bins=edges, density=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw_ratio = np.where(total > 0, h0 / total, np.nan)
        smooth_ratio = (h0 + pseudocount) / (total + 2.0 * pseudocount)
    return centers, edges, h0_density, h1_density, raw_ratio, smooth_ratio, total


def _plot_theta_panel(ax, radii: np.ndarray, bins: int, pseudocount: float) -> None:
    centers, edges, h0_density, h1_density, raw_ratio, smooth_ratio, total = (
        _theta_hist_and_ratio(radii, bins, pseudocount)
    )
    width = edges[1] - edges[0]
    ax.bar(
        centers,
        h0_density,
        width=width,
        color="#4C78A8",
        alpha=0.22,
        label=r"$\rho(\theta)$",
    )
    ax.bar(
        centers,
        h1_density,
        width=width,
        color="#F58518",
        alpha=0.18,
        label=r"$\rho(\pi-\theta)$",
    )
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("density")
    ax.set_xlim(0.0, np.pi)
    ax.grid(alpha=0.18)

    axr = ax.twinx()
    theta_line = np.linspace(0.0, np.pi, 600)
    axr.plot(theta_line, np.cos(theta_line / 2.0) ** 2, "k--", lw=1.7, label="Born")
    mask = total > 0
    axr.plot(
        centers[mask],
        raw_ratio[mask],
        "o",
        ms=3.0,
        color="#54A24B",
        alpha=0.65,
        label="raw ratio",
    )
    axr.plot(
        centers,
        smooth_ratio,
        "-",
        lw=1.5,
        color="#B279A2",
        alpha=0.9,
        label=f"smoothed (+{pseudocount:g})",
    )
    axr.set_ylim(-0.05, 1.05)
    axr.set_ylabel(r"$P(\theta)/(P(\theta)+P(\pi-\theta))$")
    handles1, labels1 = ax.get_legend_handles_labels()
    handles2, labels2 = axr.get_legend_handles_labels()
    axr.legend(handles1 + handles2, labels1 + labels2, fontsize=8, loc="upper right")


def _plot_tail_panel(ax, radii: np.ndarray, tail_fraction: float) -> None:
    x = np.asarray(radii, dtype=float)
    x = np.sort(x[np.isfinite(x) & (x > 0)])
    if x.size == 0:
        ax.text(0.5, 0.5, "no positive radii", ha="center", va="center")
        return
    survival = np.arange(x.size, 0, -1) / x.size
    tail = hill_tail_exponent(x, tail_fraction=tail_fraction)
    ax.loglog(x, survival, ".", ms=2.5, alpha=0.55, color="#4C78A8")
    if math.isfinite(tail.xmin):
        ax.axvline(tail.xmin, color="#E45756", ls="--", lw=1.2)
    ax.set_xlabel(r"$x=|\lambda|$")
    ax.set_ylabel(r"$P(X \geq x)$")
    ax.grid(alpha=0.2, which="both")
    ax.set_title(
        rf"tail density alpha={tail.density_exponent:.3f} "
        rf"(top {tail_fraction:g})",
        fontsize=10,
    )


def _positive_radii(radii: np.ndarray) -> np.ndarray:
    x = np.asarray(radii, dtype=float)
    return x[np.isfinite(x) & (x > 0)]


def _plot_theta_density_panel(ax, radii: np.ndarray, bins: int, pseudocount: float) -> None:
    centers, edges, h0_density, h1_density, _raw_ratio, _smooth_ratio, _total = (
        _theta_hist_and_ratio(radii, bins, pseudocount)
    )
    width = edges[1] - edges[0]
    ax.bar(centers, h0_density, width=width, color="#4C78A8", alpha=0.34, label=r"$\rho_0(\theta)$")
    ax.bar(centers, h1_density, width=width, color="#F58518", alpha=0.26, label=r"$\rho_1(\pi-\theta)$")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("density")
    ax.set_xlim(0.0, np.pi)
    ax.grid(alpha=0.18)
    ax.legend(fontsize=8)


def _plot_ratio_panel(ax, radii: np.ndarray, bins: int, pseudocount: float) -> None:
    centers, _edges, _h0_density, _h1_density, raw_ratio, smooth_ratio, total = (
        _theta_hist_and_ratio(radii, bins, pseudocount)
    )
    theta_line = np.linspace(0.0, np.pi, 600)
    ax.plot(theta_line, np.cos(theta_line / 2.0) ** 2, "k--", lw=1.7, label=r"$\cos^2(\theta/2)$")
    mask = total > 0
    ax.plot(centers[mask], raw_ratio[mask], "o", ms=3.0, color="#54A24B", alpha=0.65, label="raw ratio")
    ax.plot(centers, smooth_ratio, "-", lw=1.5, color="#B279A2", alpha=0.9, label=f"smoothed (+{pseudocount:g})")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel(r"$R(\theta)$")
    ax.set_xlim(0.0, np.pi)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.18)
    ax.legend(fontsize=8)


def _plot_radius_density_panel(ax, radii: np.ndarray, n_log_bins: int) -> None:
    x = _positive_radii(radii)
    if x.size < 2:
        ax.text(0.5, 0.5, "radius density unavailable", ha="center", va="center")
        return
    lo = float(np.percentile(x, 0.5))
    hi = float(np.percentile(x, 99.5))
    if not math.isfinite(lo) or not math.isfinite(hi) or lo <= 0 or hi <= lo:
        ax.text(0.5, 0.5, "radius density unavailable", ha="center", va="center")
        return
    edges = np.geomspace(lo, hi, max(8, n_log_bins + 1))
    clipped = x[(x >= lo) & (x <= hi)]
    ax.hist(clipped, bins=edges, density=True, color="#4C78A8", alpha=0.65)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$x=|\lambda|$")
    ax.set_ylabel(r"$q(x)$")
    ax.grid(alpha=0.2, which="both")


def _plot_log_radius_symmetry_panel(ax, radii: np.ndarray, n_log_bins: int) -> None:
    x = _positive_radii(radii)
    if x.size < 2:
        ax.text(0.5, 0.5, "log-radius symmetry unavailable", ha="center", va="center")
        return
    u = np.log(x)
    u_max = float(np.percentile(np.abs(u), 99.5))
    if not math.isfinite(u_max) or u_max <= 0:
        ax.text(0.5, 0.5, "log-radius symmetry unavailable", ha="center", va="center")
        return
    edges = np.linspace(-u_max, u_max, n_log_bins + 1)
    counts, _ = np.histogram(u, bins=edges)
    widths = np.diff(edges)
    centers = (edges[:-1] + edges[1:]) / 2.0
    total = counts.sum()
    if total == 0:
        ax.text(0.5, 0.5, "log-radius symmetry unavailable", ha="center", va="center")
        return
    density = counts / (total * widths)
    ax.step(centers, density, where="mid", color="#4C78A8", lw=1.5, label=r"$p(u)$")
    ax.step(centers, density[::-1], where="mid", color="#F58518", lw=1.2, alpha=0.85, label=r"$p(-u)$")
    ax.set_yscale("log")
    ax.set_xlabel(r"$u=\log x$")
    ax.set_ylabel("density")
    ax.grid(alpha=0.2, which="both")
    ax.legend(fontsize=8)


def _plot_distribution_pack(
    row: dict,
    candidate,
    time_value: float,
    diagonalization: dict,
    radii: np.ndarray,
    bins: int,
    tail_fraction: float,
    log_bins: int,
    pseudocount: float,
    out_dir: Path,
) -> Path:
    fig, axes = plt.subplots(2, 4, figsize=(18.5, 8.6), dpi=160)
    _plot_theta_density_panel(axes[0, 0], radii, bins, pseudocount)
    _plot_ratio_panel(axes[0, 1], radii, bins, pseudocount)
    _plot_radius_density_panel(axes[0, 2], radii, log_bins)
    _plot_tail_panel(axes[0, 3], radii, tail_fraction)
    _plot_log_radius_symmetry_panel(axes[1, 0], radii, log_bins)
    _plot_reciprocity_panel(axes[1, 1], radii, log_bins)
    _plot_energy_spectrum_panel(axes[1, 2], diagonalization, bins)
    axes[1, 3].axis("off")
    fig.suptitle(_row_signature(row, candidate, time_value), fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    filename = _safe_name(
        f"{row.get('family', 'candidate')}_{_candidate_label(candidate)}_t{time_value:g}_distributions.png"
    )
    out_path = out_dir / filename
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _reciprocal_envelope(radii: np.ndarray, n_log_bins: int):
    x = np.asarray(radii, dtype=float)
    x = x[np.isfinite(x) & (x > 0)]
    if x.size < 2:
        return np.array([]), np.array([]), np.array([])
    u = np.log(x)
    u_max = float(np.percentile(np.abs(u), 99.5))
    if not math.isfinite(u_max) or u_max <= 0:
        return np.array([]), np.array([]), np.array([])
    edges = np.linspace(-u_max, u_max, n_log_bins + 1)
    counts, _ = np.histogram(u, bins=edges)
    widths = np.diff(edges)
    centers = (edges[:-1] + edges[1:]) / 2.0
    total = counts.sum()
    if total == 0:
        return np.array([]), np.array([]), np.array([])
    p_u = counts / (total * widths)
    x_centers = np.exp(centers)
    envelope = p_u * (1.0 + x_centers**2) ** 2 / x_centers
    return centers, envelope, counts


def _plot_reciprocity_panel(ax, radii: np.ndarray, n_log_bins: int) -> None:
    centers, envelope, counts = _reciprocal_envelope(radii, n_log_bins)
    if centers.size == 0:
        ax.text(0.5, 0.5, "reciprocity unavailable", ha="center", va="center")
        return
    mask = (counts > 0) & np.isfinite(envelope) & (envelope > 0)
    ax.semilogy(centers[mask], envelope[mask], "o-", ms=3.5, lw=1.1, color="#4C78A8")
    ax.semilogy(-centers[mask], envelope[mask], ".", ms=2.0, alpha=0.25, color="#F58518")
    err = reciprocity_error_from_radii(radii, n_log_bins=n_log_bins)
    ax.set_xlabel(r"$u=\log x$")
    ax.set_ylabel(r"$W(u)$ estimate")
    ax.set_title(f"reciprocity error={_fmt(err)}", fontsize=10)
    ax.grid(alpha=0.2, which="both")


def plot_candidate(
    row: dict,
    bins: int,
    tail_fraction: float,
    log_bins: int,
    backend: str,
    pseudocount: float,
    out_dir: Path,
    extra_distribution_plots: bool,
) -> dict:
    candidate = _candidate_from_row(row)
    time_value = _float_or_nan(row.get("t"))
    diagonalization = _diagonalize_candidate(candidate, backend)
    analyzer = _analyzer_from_diagonalization(diagonalization, time_value, candidate.N)
    theta0, _theta1, radii = _angles_and_radii(analyzer)
    core = diagnostics_from_radii(
        radii,
        n_theta=bins,
        tail_fraction=tail_fraction,
        n_log_bins=log_bins,
    )
    metrics = core.__dict__.copy()
    metrics.update(heavy_tail_metrics(theta0, radii))
    metrics.update(_energy_metrics_from_diagonalization(diagonalization, tol=1e-9))
    metrics["objective_score"] = objective_score(metrics)
    ratio = born_ratio_from_radii(radii, n_theta=bins)

    fig = plt.figure(figsize=(14.5, 8.2), dpi=160)
    gs = fig.add_gridspec(2, 3)
    ax_theta = fig.add_subplot(gs[0, 0])
    ax_tail = fig.add_subplot(gs[0, 1])
    ax_reciprocity = fig.add_subplot(gs[0, 2])
    ax_spectrum = fig.add_subplot(gs[1, 0])
    ax_summary = fig.add_subplot(gs[1, 1:])

    _plot_theta_panel(ax_theta, radii, bins, pseudocount)
    _plot_tail_panel(ax_tail, radii, tail_fraction)
    _plot_reciprocity_panel(ax_reciprocity, radii, log_bins)
    _plot_energy_spectrum_panel(ax_spectrum, diagonalization, bins)
    ax_summary.axis("off")

    summary_lines = [
        _row_signature(row, candidate, time_value),
        "",
        f"S_born={ratio.similarity:.4f}",
        f"mean abs error={ratio.mean_abs_error:.4f}",
        f"tail alpha={core.tail_density_exponent:.3f}",
        f"reciprocity={_fmt(core.reciprocity_error)}",
        f"E deg frac={_fmt(metrics['energy_degenerate_fraction'])}",
        f"E max mult={_fmt(metrics['energy_max_multiplicity'], 0)}",
        f"atom fraction={metrics['radius_atomic_fraction']:.4f}",
        f"q99/q50={metrics['radius_q99_over_q50']:.2f}",
        f"theta mass > 0.5={metrics['theta_mass_gt_0p5']:.3f}",
        (
            f"backend={diagonalization['backend']}, "
            f"kind={diagonalization['kind']}, sectors={diagonalization['sector_count']}"
        ),
    ]
    ax_summary.text(
        0.02,
        0.98,
        "\n".join(summary_lines),
        ha="left",
        va="top",
        fontsize=10,
        family="monospace",
    )
    fig.suptitle(_candidate_label(candidate), fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    filename = _safe_name(f"{row.get('family', 'candidate')}_{_candidate_label(candidate)}_t{time_value:g}.png")
    out_path = out_dir / filename
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)

    distribution_path = None
    if extra_distribution_plots:
        distribution_path = _plot_distribution_pack(
            row,
            candidate,
            time_value,
            diagonalization,
            radii,
            bins,
            tail_fraction,
            log_bins,
            pseudocount,
            out_dir,
        )

    return {
        "path": str(out_path),
        "distribution_path": str(distribution_path) if distribution_path is not None else "",
        "signature": _row_signature(row, candidate, time_value),
        "born_similarity": ratio.similarity,
        "tail_density_exponent": core.tail_density_exponent,
        "reciprocity_error": core.reciprocity_error,
        "energy_degenerate_fraction": metrics["energy_degenerate_fraction"],
        "energy_max_multiplicity": metrics["energy_max_multiplicity"],
        "radius_atomic_fraction": metrics["radius_atomic_fraction"],
        "radius_q99_over_q50": metrics["radius_q99_over_q50"],
    }


def write_index(path: Path, plotted: list[dict]) -> None:
    lines = [
        "# Born Candidate Diagnostic Plots",
        "",
        "| rank | S | alpha | recip | E deg frac | E max mult | atom | q99/q50 | summary figure | distribution figure | signature |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|:---|:---|:---|",
    ]
    for rank, item in enumerate(plotted, 1):
        rel = Path(item["path"]).name
        dist_rel = Path(item["distribution_path"]).name if item.get("distribution_path") else ""
        dist_link = f"[{dist_rel}]({dist_rel})" if dist_rel else ""
        signature = str(item["signature"]).replace("|", "-")
        lines.append(
            "| {rank} | {S} | {alpha} | {recip} | {edeg} | {emult} | {atom} | {spread} | [{name}]({name}) | {dist} | {sig} |".format(
                rank=rank,
                S=_fmt(item["born_similarity"], 4),
                alpha=_fmt(item["tail_density_exponent"]),
                recip=_fmt(item["reciprocity_error"]),
                edeg=_fmt(item["energy_degenerate_fraction"]),
                emult=_fmt(item["energy_max_multiplicity"], 0),
                atom=_fmt(item["radius_atomic_fraction"]),
                spread=_fmt(item["radius_q99_over_q50"], 2),
                name=rel,
                dist=dist_link,
                sig=signature,
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot diagnostics for selected Born-search candidates.")
    parser.add_argument(
        "--source-csv",
        type=Path,
        nargs="+",
        default=[Path("figures/zeus_born_hamiltonian_search/summary_rows.csv")],
    )
    parser.add_argument("--out-dir", type=Path, default=Path("figures/born_candidate_diagnostics"))
    parser.add_argument("--mode", choices=["primary", "controls", "all"], default="primary")
    parser.add_argument("--top-rows", type=int, default=6)
    parser.add_argument("--min-n", type=int, default=0)
    parser.add_argument("--max-n", type=int, default=12)
    parser.add_argument("--family", nargs="+", default=[])
    parser.add_argument(
        "--queue-csv",
        type=Path,
        nargs="+",
        default=[],
        help="Optional shortlist CSV whose parameter groups define the row queue.",
    )
    parser.add_argument(
        "--top-groups",
        type=int,
        default=None,
        help="When --queue-csv is set, limit to this many queued parameter groups before row expansion.",
    )
    parser.add_argument("--min-born-similarity", type=float, default=0.35)
    parser.add_argument("--max-atomic-fraction", type=float, default=0.25)
    parser.add_argument("--max-jx-unscaled", type=float, default=0.05)
    parser.add_argument("--max-jy-unscaled", type=float, default=0.05)
    parser.add_argument("--max-jcpm-unscaled", type=float, default=0.05)
    parser.add_argument("--max-hx", type=float, default=0.05)
    parser.add_argument("--bins", type=int, default=80)
    parser.add_argument("--tail-fraction", type=float, default=0.10)
    parser.add_argument("--log-bins", type=int, default=40)
    parser.add_argument("--backend", choices=["auto", "quspin", "numpy"], default="auto")
    parser.add_argument(
        "--workers",
        type=int,
        default=_default_worker_count(),
        help=(
            "Number of selected candidate rows to plot in parallel. "
            "Defaults to BORN_WORKERS, then PBS_NP, then 1."
        ),
    )
    parser.add_argument("--pseudocount", type=float, default=0.5)
    parser.add_argument(
        "--extra-distribution-plots",
        action="store_true",
        help="Write an additional six-panel distribution figure for every selected row.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Progress log path. Defaults to <out-dir>/run.log.",
    )
    return parser.parse_args()


def run_plots(args: argparse.Namespace) -> None:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Log file: {args.log_file}")
    rows = _load_rows(args.source_csv)
    selected = select_rows(rows, args)
    if not selected:
        raise SystemExit("No rows matched the requested filters")

    plotted = []
    args.workers = max(1, int(args.workers))
    print(f"Worker processes: {args.workers}")
    if args.workers == 1 or len(selected) <= 1:
        for idx, row in enumerate(selected, 1):
            candidate = _candidate_from_row(row)
            print(f"[{idx:03d}/{len(selected):03d}] plotting {_candidate_label(candidate)} t={_fmt(row.get('t'))}")
            plotted.append(
                plot_candidate(
                    row,
                    bins=args.bins,
                    tail_fraction=args.tail_fraction,
                    log_bins=args.log_bins,
                    backend=args.backend,
                    pseudocount=args.pseudocount,
                    out_dir=args.out_dir,
                    extra_distribution_plots=args.extra_distribution_plots,
                )
            )
    else:
        n_workers = min(args.workers, len(selected))
        print(f"Submitting {len(selected)} plotting jobs to {n_workers} workers", flush=True)
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            future_to_row = {
                pool.submit(
                    plot_candidate,
                    row,
                    args.bins,
                    args.tail_fraction,
                    args.log_bins,
                    args.backend,
                    args.pseudocount,
                    args.out_dir,
                    args.extra_distribution_plots,
                ): row
                for row in selected
            }
            for done_idx, future in enumerate(as_completed(future_to_row), 1):
                row = future_to_row[future]
                candidate = _candidate_from_row(row)
                try:
                    plotted.append(future.result())
                except Exception as exc:
                    label = _candidate_label(candidate)
                    raise RuntimeError(f"Worker failed while plotting {label}") from exc
                print(
                    f"[{done_idx:03d}/{len(selected):03d}] completed {_candidate_label(candidate)} t={_fmt(row.get('t'))}",
                    flush=True,
                )
    index_path = args.out_dir / "index.md"
    write_index(index_path, plotted)
    print(f"Wrote {index_path}")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.log_file is None:
        args.log_file = args.out_dir / "run.log"
    args.log_file.parent.mkdir(parents=True, exist_ok=True)

    with args.log_file.open("w", encoding="utf-8", buffering=1) as log_fh:
        stdout = TeeWriter(sys.stdout, log_fh)
        stderr = TeeWriter(sys.stderr, log_fh)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            run_plots(args)


if __name__ == "__main__":
    main()
