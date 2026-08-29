"""Build the Born-ranked level-spacing 2x3 atlas for the Jx=1e-3 Zeus run."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
os.environ.setdefault(
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-jx-1em3-level-spacing-atlas")
)

import numpy as np  # noqa: E402

from core.sobol_coupling_scan import _diagnostics  # noqa: E402
from scripts.build_sobol_flat_ranked_1x6_by_n import (  # noqa: E402
    CaseRecord,
    compute_spectral,
)
from scripts.build_vab_coupling_level_spacing_sample import (  # noqa: E402
    render_sample,
)
from scripts.build_vab_coupling_raw_flat_ranked_1x6 import (  # noqa: E402
    load_values,
    token,
)
from scripts.build_vab_coupling_raw_flat_ranked_2x3 import (  # noqa: E402
    fit_arrays,
)


CAMPAIGN = ROOT / "work" / "zeus_vab_atlas_jx_1em3_N14_20260802_162728"
METRICS = CAMPAIGN / "aggregates" / "N14" / "anisotropic_metrics_N14.csv"
OUTPUT = (
    ROOT / "reports"
    / "vab_atlas_jx_1em3_N14_flat_ranked_2x3_level_spacing_2026-08-03"
)


@dataclass(frozen=True)
class AtlasCase:
    ordinal: int
    dynamics_n: int
    hz: float
    j: float
    jpm: float
    jx: float
    hz0: float
    evolution_time: float
    source_s_born: float
    source_rmse: float
    angular_bin_coverage: float
    raw_path: str
    rank: int = 0
    output_path: str = ""


def _local_raw_path(campaign: Path, source_path: str) -> Path:
    """Map an absolute Zeus raw path onto the downloaded campaign root."""

    parts = PurePosixPath(source_path.replace("\\", "/")).parts
    try:
        raw_index = parts.index("raw")
    except ValueError as exc:
        raise ValueError(f"raw path has no raw/ component: {source_path}") from exc
    return campaign.joinpath(*parts[raw_index:]).resolve()


def load_cases(
    metrics_path: Path,
    campaign: Path,
    output: Path,
) -> tuple[list[AtlasCase], list[dict[str, Any]]]:
    """Load, validate, and rank all successful CSV records by S_born."""

    cases: list[AtlasCase] = []
    unavailable: list[dict[str, Any]] = []
    with metrics_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for ordinal, row in enumerate(csv.DictReader(handle), start=1):
            raw = _local_raw_path(campaign, row["raw_path"])
            if not raw.is_file():
                unavailable.append(
                    {"ordinal": ordinal, "raw_path": str(raw), "reason": "missing raw NPZ"}
                )
                continue
            score = float(row["S_born"])
            if not math.isfinite(score):
                unavailable.append(
                    {"ordinal": ordinal, "raw_path": str(raw), "reason": "non-finite S_born"}
                )
                continue
            cases.append(
                AtlasCase(
                    ordinal=ordinal,
                    dynamics_n=int(row["detector_n"]),
                    hz=float(row["hz"]),
                    j=float(row["J"]),
                    jpm=float(row["Jpm"]),
                    jx=float(row["jx"]),
                    hz0=float(row["hz0"]),
                    evolution_time=float(row["evolution_time"]),
                    source_s_born=score,
                    source_rmse=float(row["born_rmse"]),
                    angular_bin_coverage=float(row["angular_bin_coverage"]),
                    raw_path=str(raw),
                )
            )
    cases.sort(
        key=lambda case: (
            -case.source_s_born,
            case.hz,
            case.j,
            case.jpm,
            case.ordinal,
        )
    )
    ranked: list[AtlasCase] = []
    for rank, case in enumerate(cases, start=1):
        score = f"{case.source_s_born:.6f}".replace(".", "p")
        name = (
            f"rank_{rank:04d}__hz_{token(case.hz)}__J_{token(case.j)}__"
            f"Jpm_{token(case.jpm)}__Sborn_{score}.png"
        )
        ranked.append(
            AtlasCase(
                **{
                    **asdict(case),
                    "rank": rank,
                    "output_path": str((output / name).resolve()),
                }
            )
        )
    return ranked, unavailable


def _render(payload: tuple[AtlasCase, int, bool]) -> dict[str, Any]:
    case, dpi, force = payload
    target = Path(case.output_path)
    if target.is_file() and not force:
        return {**asdict(case), "status": "existing"}

    metrics, arrays = _diagnostics(load_values(Path(case.raw_path)), 64)
    fits, wrapped_gaussian, wrapped_cauchy = fit_arrays(arrays["theta"])
    arrays.update(fits)
    score_delta = abs(float(metrics["S_born"]) - case.source_s_born)
    if score_delta > 1.0e-12:
        raise RuntimeError(f"S_born mismatch {score_delta:.3e}")

    record = CaseRecord(
        family="jy_zero",
        dynamics_n=case.dynamics_n,
        config_id=f"hz={case.hz:g},J={case.j:g},Jpm={case.jpm:g}",
        s_born=float(metrics["S_born"]),
        born_rmse=float(metrics["born_RMSE_occupied"]),
        hz=case.hz,
        j=case.j,
        jpm=case.jpm,
        jx=case.jx,
        jy=0.0,
        source_dir=str(Path(case.raw_path).parent),
        rank=case.rank,
        within_n_rank=case.rank,
        output_path=str(target),
    )
    spectral = compute_spectral(record)
    result = render_sample(
        record,
        spectral,
        arrays,
        target,
        dpi,
        title_label=r"$J_x=10^{-3}$ Zeus atlas",
    )
    return {
        **asdict(case),
        **result,
        "status": "rendered",
        "computed_s_born": record.s_born,
        "computed_born_rmse": record.born_rmse,
        "s_born_delta": score_delta,
        "wg_fourier_discrepancy": float(wrapped_gaussian["objective"]),
        "wc_fourier_discrepancy": float(wrapped_cauchy["objective"]),
        "fit_preference_fourier": (
            "wrapped_gaussian"
            if wrapped_gaussian["objective"] < wrapped_cauchy["objective"]
            else "wrapped_cauchy"
            if wrapped_cauchy["objective"] < wrapped_gaussian["objective"]
            else "tie"
        ),
        "spectral_validation": spectral.validation,
    }


def _write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    materialized = list(rows)
    if not materialized:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted(
        {
            key
            for row in materialized
            for key in row
            if key not in {"spectral_validation", "level_spacing_l1"}
        }
    )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def _group_rates(cases: list[AtlasCase], field: str, threshold: float) -> list[dict[str, Any]]:
    values = sorted({float(getattr(case, field)) for case in cases})
    rows: list[dict[str, Any]] = []
    for value in values:
        group = [case for case in cases if float(getattr(case, field)) == value]
        high = [case for case in group if case.source_s_born >= threshold]
        rows.append(
            {
                "value": value,
                "count": len(group),
                "high_count": len(high),
                "high_rate": len(high) / len(group),
                "mean_s_born": float(
                    sum(case.source_s_born for case in group) / len(group)
                ),
            }
        )
    return rows


def summarize_scores(cases: list[AtlasCase]) -> dict[str, Any]:
    """Return reproducible descriptive statistics for high-S_born cases."""

    scores = [case.source_s_born for case in cases]
    threshold = 0.75
    high = [case for case in cases if case.source_s_born >= threshold]
    small_field = [case for case in high if abs(case.hz) <= 0.0100000001]
    intermediate_jpm = [case for case in high if 0.01 <= case.jpm <= 0.25]
    return {
        "count": len(cases),
        "score_quantiles": {
            "minimum": float(min(scores)),
            "q25": float(np.quantile(scores, 0.25)),
            "median": float(np.quantile(scores, 0.50)),
            "q75": float(np.quantile(scores, 0.75)),
            "q90": float(np.quantile(scores, 0.90)),
            "maximum": float(max(scores)),
        },
        "high_definition": "S_born >= 0.75",
        "high_count": len(high),
        "high_small_field_count": len(small_field),
        "high_small_field_fraction": len(small_field) / max(1, len(high)),
        "high_intermediate_jpm_count": len(intermediate_jpm),
        "high_intermediate_jpm_fraction": len(intermediate_jpm) / max(1, len(high)),
        "all_high_have_full_angular_coverage": all(
            case.angular_bin_coverage == 1.0 for case in high
        ),
        "group_rates": {
            "hz": _group_rates(cases, "hz", threshold),
            "J": _group_rates(cases, "j", threshold),
            "Jpm": _group_rates(cases, "jpm", threshold),
        },
        "top_cases": [asdict(case) for case in cases[:20]],
    }


def build(
    metrics_path: Path,
    campaign: Path,
    output: Path,
    *,
    workers: int,
    dpi: int,
    force: bool,
    limit: int | None,
) -> dict[str, Any]:
    cases, unavailable = load_cases(metrics_path, campaign, output)
    all_cases = cases
    if limit is not None:
        cases = cases[:limit]
    output.mkdir(parents=True, exist_ok=True)
    summary = summarize_scores(all_cases)
    (output / "high_s_born_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    payloads = [(case, dpi, force) for case in cases]
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(_render, payload): payload[0] for payload in payloads}
        for completed, future in enumerate(as_completed(futures), start=1):
            case = futures[future]
            try:
                results.append(future.result())
            except BaseException as exc:
                failures.append(
                    {
                        **asdict(case),
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                )
            if completed == 1 or completed % 25 == 0 or completed == len(futures):
                print(
                    f"completed {completed}/{len(futures)}; failures={len(failures)}",
                    flush=True,
                )

    results.sort(key=lambda row: int(row["rank"]))
    failures.sort(key=lambda row: int(row["rank"]))
    _write_csv(output / "ranked_index.csv", results)
    _write_csv(output / "unavailable_cases.csv", [*unavailable, *failures])
    manifest = {
        "source_campaign": str(campaign.resolve()),
        "source_metrics": str(metrics_path.resolve()),
        "output": str(output.resolve()),
        "requested_records": len(cases),
        "available_records": len(all_cases),
        "completed_records": len(results),
        "unavailable_source_records": len(unavailable),
        "render_failures": len(failures),
        "ranking": "decreasing S_born; ties by hz, J, Jpm, source ordinal",
        "dynamics_n": 14,
        "detector_spectrum_n": 8,
        "collective_jx": 0.001,
        "edge_jx": 0.001 / math.sqrt(14.0),
        "dpi": dpi,
        "workers": workers,
        "layout": [
            ["energy proximity", "degeneracy multiplicities", "P/R diagnostics"],
            ["Vab heatmap", "logarithmic Vab gap weight", "unfolded spacings"],
        ],
        "level_spacing": {
            "spectrum": "full detector-only N_D=8 spectrum",
            "degeneracy_handling": "established scale-aware tolerance",
            "unfolding": "cubic staircase fit with 10% edge trim",
            "references": ["Poisson", "GOE", "GUE"],
            "ratio": "Atas mean min(s_n,s_n+1)/max(s_n,s_n+1)",
            "caveat": "symmetry sectors are mixed; RMT comparison is descriptive",
        },
        "vab_histogram": (
            "logarithmic bins of |Ea-Eb|/(Emax-Emin), plus a separate strict "
            "degeneracy bin; Ea and Eb are detector-only energies"
        ),
    }
    (output / "render_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, default=METRICS)
    parser.add_argument("--campaign", type=Path, default=CAMPAIGN)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    manifest = build(
        args.metrics,
        args.campaign,
        args.output,
        workers=args.workers,
        dpi=args.dpi,
        force=args.force,
        limit=args.limit,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
