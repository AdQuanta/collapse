"""
Summarize sector weak-kernel diagnostic result folders.

The sector diagnostic writes one ``sector_weak_kernel_summary.csv`` per run.
This script combines those tables, ranks rows with a Born-rule-search score,
and plots the current scaling trends.  It is intended for local follow-up
runs and for post-processing Zeus outputs after they are copied back.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


NUMERIC_FIELDS = {
    "N",
    "N_pixel",
    "hz0",
    "hz",
    "J",
    "Jpm",
    "Jx_unscaled",
    "Jx_scaled",
    "t",
    "born_similarity",
    "mean_abs_ratio_error",
    "reciprocity_error",
    "tail_density_exponent",
    "radius_q99_over_q50",
    "radius_atomic_fraction",
    "radius_q50",
    "radius_q99",
    "n_eigenvalues",
    "sector_count",
    "max_sector_dimension",
    "max_momentum_block_dimension",
    "wall_seconds",
}


def _float_or_nan(value: Any) -> float:
    if value is None:
        return math.nan
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _fmt(value: Any, digits: int = 3) -> str:
    if not _finite(value):
        return "nan"
    number = float(value)
    if abs(number) >= 1.0e4 or (0.0 < abs(number) < 1.0e-3):
        return f"{number:.{digits}e}"
    return f"{number:.{digits}f}"


def _fmt_g(value: Any) -> str:
    if not _finite(value):
        return "nan"
    return f"{float(value):g}"


def _load_rows(roots: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for root in roots:
        for csv_path in sorted(root.rglob("sector_weak_kernel_summary.csv")):
            csv_path = csv_path.resolve()
            if csv_path in seen:
                continue
            seen.add(csv_path)
            with csv_path.open(newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for raw in reader:
                    row: dict[str, Any] = dict(raw)
                    for field in NUMERIC_FIELDS:
                        if field in row:
                            row[field] = _float_or_nan(row[field])
                    if _finite(row.get("N")):
                        row["N"] = int(float(row["N"]))
                    if _finite(row.get("N_pixel")):
                        row["N_pixel"] = int(float(row["N_pixel"]))
                    row["source_csv"] = str(csv_path)
                    row["source_run"] = csv_path.parent.name
                    row["candidate_score"] = candidate_score(row)
                    rows.append(row)
    return rows


def candidate_score(row: dict[str, Any]) -> float:
    """Balanced score for the perturbative Born-rule target."""

    similarity = _float_or_nan(row.get("born_similarity"))
    recip = _float_or_nan(row.get("reciprocity_error"))
    spread = _float_or_nan(row.get("radius_q99_over_q50"))
    atom = _float_or_nan(row.get("radius_atomic_fraction"))

    s_score = max(0.0, min(1.0, similarity)) if math.isfinite(similarity) else 0.0
    recip_score = math.exp(-abs(recip)) if math.isfinite(recip) else 0.0
    spread_score = 0.0
    if math.isfinite(spread) and spread > 0.0:
        spread_score = min(1.0, math.log1p(spread) / math.log(40.0))
    atom_score = 1.0 - min(1.0, atom) if math.isfinite(atom) else 0.0

    return 0.60 * s_score + 0.18 * recip_score + 0.14 * spread_score + 0.08 * atom_score


def _write_combined_csv(rows: list[dict[str, Any]], out_dir: Path) -> Path:
    csv_path = out_dir / "sector_weak_kernel_combined.csv"
    all_fields: list[str] = []
    for preferred in [
        "candidate_score",
        "label",
        "source_run",
        "N",
        "N_pixel",
        "hz0_mode",
        "hz0",
        "hz",
        "J",
        "Jpm",
        "Jx_unscaled",
        "Jx_scaled",
        "t",
        "born_similarity",
        "reciprocity_error",
        "radius_q99_over_q50",
        "radius_atomic_fraction",
        "tail_density_exponent",
        "max_momentum_block_dimension",
        "wall_seconds",
        "figure",
        "source_csv",
    ]:
        all_fields.append(preferred)
    for row in rows:
        for field in row:
            if field not in all_fields:
                all_fields.append(field)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=all_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return csv_path


def _group_key(row: dict[str, Any]) -> tuple[str, float, float]:
    return (
        str(row.get("hz0_mode", "")),
        _float_or_nan(row.get("Jpm")),
        _float_or_nan(row.get("t")),
    )


def _label_from_key(key: tuple[str, float, float]) -> str:
    hz0_mode, jpm, t_value = key
    return f"hz0={hz0_mode}, Jpm={_fmt_g(jpm)}, t={_fmt_g(t_value)}"


def _dedup_by_best_score(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = (
            row.get("N"),
            row.get("hz0_mode"),
            _fmt_g(row.get("Jpm")),
            _fmt_g(row.get("t")),
            _fmt_g(row.get("hz")),
            _fmt_g(row.get("Jx_unscaled")),
        )
        current = best.get(key)
        if current is None or row.get("candidate_score", -math.inf) > current.get(
            "candidate_score", -math.inf
        ):
            best[key] = row
    return list(best.values())


def _plot_metric(
    rows: list[dict[str, Any]],
    out_dir: Path,
    *,
    metric: str,
    ylabel: str,
    filename: str,
) -> Path | None:
    filtered = [
        row
        for row in _dedup_by_best_score(rows)
        if _finite(row.get("N")) and _finite(row.get(metric))
    ]
    if not filtered:
        return None

    grouped: dict[tuple[str, float, float], list[dict[str, Any]]] = defaultdict(list)
    for row in filtered:
        grouped[_group_key(row)].append(row)

    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    for key, group in sorted(grouped.items(), key=lambda item: str(item[0])):
        group = sorted(group, key=lambda row: int(row["N"]))
        if len(group) == 1:
            ax.scatter(
                [row["N"] for row in group],
                [row[metric] for row in group],
                s=54,
                label=_label_from_key(key),
            )
        else:
            ax.plot(
                [row["N"] for row in group],
                [row[metric] for row in group],
                marker="o",
                linewidth=1.8,
                label=_label_from_key(key),
            )
    ax.set_xlabel("N")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    path = out_dir / filename
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _plot_score_scatter(rows: list[dict[str, Any]], out_dir: Path) -> Path | None:
    filtered = [
        row
        for row in rows
        if _finite(row.get("born_similarity"))
        and _finite(row.get("radius_q99_over_q50"))
        and _finite(row.get("N"))
    ]
    if not filtered:
        return None

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    sizes = [36 + 4 * max(0.0, _float_or_nan(row.get("N")) - 10.0) for row in filtered]
    colors = [_float_or_nan(row.get("candidate_score")) for row in filtered]
    scatter = ax.scatter(
        [row["radius_q99_over_q50"] for row in filtered],
        [row["born_similarity"] for row in filtered],
        c=colors,
        s=sizes,
        cmap="viridis",
        edgecolor="black",
        linewidth=0.35,
    )
    for row in filtered:
        text = f"N{row['N']} {row.get('hz0_mode')} Jpm={_fmt_g(row.get('Jpm'))}"
        ax.annotate(text, (row["radius_q99_over_q50"], row["born_similarity"]), fontsize=7)
    ax.axhline(0.8, color="tab:red", linestyle="--", linewidth=1.0, alpha=0.7)
    ax.set_xlabel("radius q99/q50")
    ax.set_ylabel("Born similarity S")
    ax.grid(True, alpha=0.25)
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("candidate score")
    fig.tight_layout()
    path = out_dir / "born_similarity_vs_tail_spread.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _plot_block_scaling(rows: list[dict[str, Any]], out_dir: Path) -> Path | None:
    filtered = [
        row
        for row in _dedup_by_best_score(rows)
        if _finite(row.get("N")) and _finite(row.get("max_momentum_block_dimension"))
    ]
    if not filtered:
        return None

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    grouped: dict[tuple[str, float, float], list[dict[str, Any]]] = defaultdict(list)
    for row in filtered:
        grouped[_group_key(row)].append(row)
    for key, group in sorted(grouped.items(), key=lambda item: str(item[0])):
        group = sorted(group, key=lambda row: int(row["N"]))
        ax.plot(
            [row["N"] for row in group],
            [row["max_momentum_block_dimension"] for row in group],
            marker="o",
            linewidth=1.8,
            label=_label_from_key(key),
        )
    ax.set_xlabel("N")
    ax.set_ylabel("max momentum block dimension")
    ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    path = out_dir / "max_momentum_block_dimension_vs_N.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _write_markdown(rows: list[dict[str, Any]], out_dir: Path, plots: list[Path]) -> Path:
    md_path = out_dir / "summary.md"
    ranked = sorted(rows, key=lambda row: row.get("candidate_score", -math.inf), reverse=True)

    lines = [
        "# Sector weak-kernel result summary",
        "",
        "This summary combines `sector_weak_kernel_summary.csv` files and keeps the",
        "current Born similarity metric `S_born` for continuity with the main search.",
        "The auxiliary score only helps triage rows; it is not a replacement metric.",
        "",
        f"- Rows combined: {len(rows)}",
        "- Combined CSV: `sector_weak_kernel_combined.csv`",
        "",
    ]
    if plots:
        lines.append("## Overview plots")
        lines.append("")
        for plot in plots:
            lines.append(f"- [{plot.name}]({plot.name})")
        lines.append("")

    lines.extend(
        [
            "## Top rows",
            "",
            "| rank | score | source | N | hz0 | Jpm | t | S_born | reciprocity | q99/q50 | atom frac | max block |",
            "| ---: | ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for rank, row in enumerate(ranked[:20], start=1):
        lines.append(
            "| "
            f"{rank} | {_fmt(row.get('candidate_score'))} | `{row.get('source_run', '')}` | "
            f"{row.get('N', '')} | `{row.get('hz0_mode', '')}` | "
            f"{_fmt_g(row.get('Jpm'))} | {_fmt_g(row.get('t'))} | "
            f"{_fmt(row.get('born_similarity'))} | {_fmt(row.get('reciprocity_error'))} | "
            f"{_fmt(row.get('radius_q99_over_q50'))} | "
            f"{_fmt(row.get('radius_atomic_fraction'))} | "
            f"{_fmt(row.get('max_momentum_block_dimension'), digits=0)} |"
        )

    zero_jpm = [
        row
        for row in _dedup_by_best_score(rows)
        if str(row.get("hz0_mode")) == "zero"
        and _finite(row.get("Jpm"))
        and abs(float(row["Jpm"]) - 0.05) < 1.0e-12
        and _finite(row.get("t"))
        and abs(float(row["t"]) - 1000.0) < 1.0e-9
    ]
    zero_jpm.sort(key=lambda row: int(row["N"]) if _finite(row.get("N")) else 0)
    if zero_jpm:
        lines.extend(
            [
                "",
                "## Slide-8 weak-kernel scaling probe",
                "",
                "This is the current local sector-aware check of the `hz0=0`,",
                "`Jpm=0.05`, `t=1000` mechanism.",
                "",
                "| N | S_born | reciprocity | q99/q50 | atom frac | max momentum block |",
                "| ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in zero_jpm:
            lines.append(
                f"| {row.get('N')} | {_fmt(row.get('born_similarity'))} | "
                f"{_fmt(row.get('reciprocity_error'))} | "
                f"{_fmt(row.get('radius_q99_over_q50'))} | "
                f"{_fmt(row.get('radius_atomic_fraction'))} | "
                f"{_fmt(row.get('max_momentum_block_dimension'), digits=0)} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation checklist",
            "",
            "- A high `S_born` row remains a candidate only if `P(theta)` is broad and",
            "  the radius density is not mostly atomic.",
            "- The `hz0=0, Jpm=0.05` row is testing the zero-frequency dressed-kernel",
            "  explanation of the slide-8 result.",
            "- N15/N16 sector runs are still the decisive tests because N10 is not",
            "  Born-like while the N12/N14 local probes improve with N.",
            "- After Zeus results arrive, rerun this script on the Zeus root and compare",
            "  the same plots and tables.",
            "",
        ]
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="+",
        type=Path,
        help="Result roots to scan recursively for sector_weak_kernel_summary.csv.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("figures/sector_weak_kernel_summary"),
        help="Directory for the combined CSV, plots, and Markdown summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows = _load_rows(args.roots)
    if not rows:
        raise SystemExit("No sector_weak_kernel_summary.csv files found.")

    combined_csv = _write_combined_csv(rows, args.out_dir)
    plots = [
        path
        for path in [
            _plot_metric(
                rows,
                args.out_dir,
                metric="born_similarity",
                ylabel="Born similarity S",
                filename="born_similarity_vs_N.png",
            ),
            _plot_metric(
                rows,
                args.out_dir,
                metric="reciprocity_error",
                ylabel="reciprocity error",
                filename="reciprocity_error_vs_N.png",
            ),
            _plot_metric(
                rows,
                args.out_dir,
                metric="radius_q99_over_q50",
                ylabel="radius q99/q50",
                filename="radius_q99_over_q50_vs_N.png",
            ),
            _plot_block_scaling(rows, args.out_dir),
            _plot_score_scatter(rows, args.out_dir),
        ]
        if path is not None
    ]
    md_path = _write_markdown(rows, args.out_dir, plots)

    print(f"Rows combined: {len(rows)}")
    print(f"Combined CSV: {combined_csv}")
    print(f"Summary: {md_path}")
    for plot in plots:
        print(f"Plot: {plot}")


if __name__ == "__main__":
    main()
