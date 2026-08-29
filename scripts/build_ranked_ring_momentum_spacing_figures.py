"""Build N=17 symmetry-resolved spacing figures for ranked ring campaigns.

The detector Hamiltonian is

    H_D = -hz sum_i Z_i - J sum_i Z_i Z_(i+1)
          - Jpm/4 sum_i (sigma_i^+ sigma_(i+1)^- + h.c.)
          - J2 sum_i Z_i Z_(i+2)
          - Jpm2/4 sum_i (sigma_i^+ sigma_(i+2)^- + h.c.),

with periodic indices.  Each source campaign is ranked independently by its
stored finite S_Born value after requiring COMPLETE.json and a passing
validation.json.  The requested examples are the highest and lowest ranking
tails, without silently imposing an additional threshold.

For odd detector size N, the exact conventional symmetries are fixed N_up and
the dihedral ring symmetry.  Reflection is resolved at k=0; each nonzero k
panel represents one of the two identical spectral copies in the paired
(k, N-k) dihedral irrep.  For every nonredundant momentum, the five blocks with
the largest multiplicity-space dimensions are diagonalised.  Exact numerical
degeneracies are merged before cubic staircase unfolding with a 10% edge trim.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Each process diagonalises one sector at a time.  Avoid multiplying BLAS
# threads by the number of case workers.
for variable in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(variable, "1")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from core.level_spacing import (  # noqa: E402
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)
from scripts.build_three_ring_momentum_spacing_figures import (  # noqa: E402
    HamiltonianParameters,
    SectorSpec,
    _spectral_statistics,
    diagonalize_sector,
    select_largest_sectors,
)


DEFAULT_NEAREST_ROOT = (
    ROOT / "work" / "zeus_sobol_hz0_0_N14_20260805_224341" / "jy_zero" / "N14"
)
DEFAULT_SECOND_ROOT = (
    ROOT
    / "work"
    / "zeus_sobol_second_neighbor_hz0_0_N14_20260805_224342"
    / "jy_zero"
    / "N14"
)
DEFAULT_OUTPUT = (
    ROOT / "reports" / "ranked_ring_symmetry_resolved_spacings_N17_2026-08-25"
)
ANALYSIS_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CampaignSpec:
    family: str
    description: str
    root: Path
    expects_second_neighbor: bool


@dataclass(frozen=True)
class RankedCase:
    family: str
    family_description: str
    tail: str
    rank_within_tail: int
    config_id: str
    source_dir: Path
    source_n: int
    s_born: float
    born_rmse: float
    occupied_fraction: float
    parameters: HamiltonianParameters
    jx_unscaled: float
    source_sobol_index: int

    @property
    def case_key(self) -> str:
        return (
            f"{self.family}__{self.tail}__rank_{self.rank_within_tail:02d}__"
            f"{self.config_id}"
        )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_source_files(source_dir: Path, complete: dict[str, Any]) -> None:
    for filename in ("metrics.json", "metadata.json", "validation.json"):
        expected = complete.get("files", {}).get(filename)
        if not expected:
            raise ValueError(f"{source_dir}: COMPLETE.json omits {filename}")
        actual = _sha256(source_dir / filename)
        if actual != expected:
            raise ValueError(f"{source_dir}: checksum mismatch for {filename}")


def load_valid_campaign(spec: CampaignSpec) -> list[RankedCase]:
    """Load complete, validated cases from one source campaign."""
    if not spec.root.is_dir():
        raise FileNotFoundError(spec.root)
    loaded: list[RankedCase] = []
    rejected: list[str] = []
    incomplete_count = 0
    for source_dir in sorted(spec.root.glob("config_*")):
        if not (source_dir / "COMPLETE.json").is_file():
            incomplete_count += 1
            continue
        try:
            complete = _load_json(source_dir / "COMPLETE.json")
            validation = _load_json(source_dir / "validation.json")
            if complete.get("status") != "complete" or not complete.get(
                "validation_passed", False
            ):
                continue
            if not validation.get("passed", False):
                continue
            _validate_source_files(source_dir, complete)
            metrics = _load_json(source_dir / "metrics.json")
            metadata = _load_json(source_dir / "metadata.json")
            configuration = metadata["configuration"]
            s_born = float(metrics["S_born"])
            if not math.isfinite(s_born):
                continue
            parameters = HamiltonianParameters(
                hz=float(configuration["hz"]),
                j=float(configuration["j"]),
                jpm=float(configuration["jpm"]),
                j2=float(configuration.get("j2", 0.0)),
                jpm2=float(configuration.get("jpm2", 0.0)),
            )
            has_second_neighbor = bool(parameters.j2 or parameters.jpm2)
            if spec.expects_second_neighbor != bool(
                metadata.get("second_neighbor_ring", False)
            ):
                raise ValueError("stored second-neighbor family flag is inconsistent")
            if spec.expects_second_neighbor != has_second_neighbor:
                raise ValueError("couplings are inconsistent with the campaign family")
            loaded.append(
                RankedCase(
                    family=spec.family,
                    family_description=spec.description,
                    tail="unranked",
                    rank_within_tail=0,
                    config_id=str(configuration["config_id"]),
                    source_dir=source_dir,
                    source_n=int(metadata["N"]),
                    s_born=s_born,
                    born_rmse=float(metrics["born_RMSE_occupied"]),
                    occupied_fraction=float(metrics["occupied_fraction"]),
                    parameters=parameters,
                    jx_unscaled=float(metadata["Jx_unscaled"]),
                    source_sobol_index=int(configuration["sobol_index"]),
                )
            )
        except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            rejected.append(f"{source_dir.name}: {exc}")
    if incomplete_count:
        print(
            f"[{spec.family}] skipped {incomplete_count} configurations without "
            "completion markers",
            flush=True,
        )
    if rejected:
        print(f"[{spec.family}] rejected {len(rejected)} malformed cases", flush=True)
        for message in rejected[:10]:
            print(f"  {message}", flush=True)
    if not loaded:
        raise RuntimeError(f"no complete validated configurations in {spec.root}")
    return loaded


def select_ranked_tails(cases: list[RankedCase], count: int) -> list[RankedCase]:
    if count < 1:
        raise ValueError("count must be positive")
    if len(cases) < 2 * count:
        raise ValueError(f"need at least {2 * count} cases, found {len(cases)}")
    ordered = sorted(cases, key=lambda case: (case.s_born, case.config_id))
    selected: list[RankedCase] = []
    for tail, rows in (
        ("lowest", ordered[:count]),
        ("highest", list(reversed(ordered[-count:]))),
    ):
        for rank, case in enumerate(rows, start=1):
            payload = asdict(case)
            payload["tail"] = tail
            payload["rank_within_tail"] = rank
            payload["parameters"] = case.parameters
            selected.append(RankedCase(**payload))
    return selected


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def _analysis_digest(case: RankedCase, detector_n: int) -> str:
    payload = {
        "schema": ANALYSIS_SCHEMA_VERSION,
        "detector_n": detector_n,
        "sectors_per_momentum": 5,
        "case": {
            "family": case.family,
            "tail": case.tail,
            "rank": case.rank_within_tail,
            "config_id": case.config_id,
            "s_born": case.s_born,
            "parameters": asdict(case.parameters),
        },
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def _write_npz_atomic(path: Path, payload: dict[str, np.ndarray]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **payload)
    temporary.replace(path)


def _plot_case(
    case: RankedCase,
    sector_data: dict[int, list[dict[str, Any]]],
    detector_n: int,
    output: Path,
    dpi: int,
) -> None:
    colors = plt.get_cmap("tab10").colors[:5]
    momentum_count = detector_n // 2 + 1
    column_count = min(3, momentum_count)
    row_count = math.ceil(momentum_count / column_count)
    figure, axes = plt.subplots(
        row_count,
        column_count,
        figsize=(6.0 * column_count, 4.8 * row_count + 0.1),
        sharex=True,
        sharey=True,
        squeeze=False,
    )
    s_grid = np.linspace(0.0, 4.0, 600)
    for momentum, axis in zip(range(momentum_count), axes.flat):
        for color, row in zip(colors, sector_data[momentum]):
            spacings = row["unfolded_spacings"]
            counts, edges = np.histogram(spacings, bins=np.linspace(0.0, 4.0, 33))
            density = counts / (max(spacings.size, 1) * np.diff(edges))
            centers = 0.5 * (edges[:-1] + edges[1:])
            sector = row["sector"]
            axis.step(
                centers,
                density,
                where="mid",
                color=color,
                linewidth=1.15,
                alpha=0.92,
                label=(
                    f"{sector.label}, d={sector.dimension}, "
                    rf"$\langle\tilde r\rangle={row['mean_r']:.3f}$"
                ),
            )
        axis.plot(
            s_grid,
            poisson_spacing_distribution(s_grid),
            color="black",
            linestyle="--",
            linewidth=1.15,
            label="Poisson",
        )
        axis.plot(
            s_grid,
            wigner_spacing_distribution(s_grid, beta=1),
            color="black",
            linestyle=":",
            linewidth=1.25,
            label="GOE",
        )
        momentum_label = "0" if momentum == 0 else rf"\pm{momentum}"
        axis.set_title(rf"$k={momentum_label}$", fontsize=11)
        axis.set_xlim(0.0, 4.0)
        axis.set_ylim(bottom=0.0)
        axis.grid(alpha=0.18)
        axis.legend(loc="upper right", fontsize=6.3, framealpha=0.88)
    for axis in axes.flat[momentum_count:]:
        axis.set_visible(False)
    for axis in axes[-1, :]:
        axis.set_xlabel(r"unfolded spacing $s$")
    for axis in axes[:, 0]:
        axis.set_ylabel(r"density $P(s)$")

    parameters = case.parameters
    second_text = ""
    if parameters.j2 or parameters.jpm2:
        second_text = (
            rf", $J_2={parameters.j2:.6g}$, "
            rf"$J_{{\pm2}}={parameters.jpm2:.6g}$"
        )
    tail_label = "most Born-like" if case.tail == "highest" else "least Born-like"
    figure.suptitle(
        "\n".join(
            (
                rf"{case.family_description}: {tail_label} rank "
                rf"{case.rank_within_tail}, {case.config_id}; $N_D={detector_n}$ spacing",
                rf"source $N={case.source_n}$: $S_{{\rm Born}}={case.s_born:.6f}$; "
                rf"$h_z={parameters.hz:.6g}$, $J={parameters.j:.6g}$, "
                rf"$J_{{\pm}}={parameters.jpm:.6g}${second_text}",
            )
        ),
        fontsize=14,
        y=0.995,
    )
    figure.text(
        0.5,
        0.008,
        (
            rf"Exact sectors: fixed $N_\uparrow$ and $D_{{{detector_n}}}$; "
            r"each nonzero-k pane represents the equivalent $\pm k$ pair. "
            r"Exact degeneracies merged; cubic unfolding with 10% edge trim."
        ),
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0.025, 0.03, 0.99, 0.945), h_pad=2.0, w_pad=1.4)
    temporary = output.with_suffix(".tmp.png")
    figure.savefig(temporary, dpi=dpi, bbox_inches="tight")
    plt.close(figure)
    temporary.replace(output)


def _case_paths(case: RankedCase, output_dir: Path, detector_n: int) -> dict[str, Path]:
    case_dir = output_dir / case.family / case.tail
    stem = f"rank_{case.rank_within_tail:02d}__{case.config_id}__N{detector_n}"
    return {
        "dir": case_dir,
        "figure": case_dir / f"{stem}_momentum_level_spacings.png",
        "checkpoint": case_dir / f"{stem}_checkpoint.json",
        "archive": case_dir / f"{stem}_spectra.npz",
    }


def _load_completed_case(
    case: RankedCase, output_dir: Path, detector_n: int
) -> dict[str, Any] | None:
    paths = _case_paths(case, output_dir, detector_n)
    if not all(paths[key].is_file() for key in ("figure", "checkpoint", "archive")):
        return None
    checkpoint = _load_json(paths["checkpoint"])
    if checkpoint.get("analysis_digest") != _analysis_digest(case, detector_n):
        return None
    return checkpoint


def _compute_case(
    case: RankedCase,
    output_dir: Path,
    detector_n: int,
    dpi: int,
    force: bool,
) -> dict[str, Any]:
    if not force:
        completed = _load_completed_case(case, output_dir, detector_n)
        if completed is not None:
            completed["resumed"] = True
            return completed

    paths = _case_paths(case, output_dir, detector_n)
    paths["dir"].mkdir(parents=True, exist_ok=True)
    selected = select_largest_sectors(detector_n, count=5)
    sector_data: dict[int, list[dict[str, Any]]] = {}
    sector_summary: list[dict[str, Any]] = []
    archive_payload: dict[str, np.ndarray] = {}
    started = time.perf_counter()
    for momentum, sectors in selected.items():
        sector_data[momentum] = []
        for sector in sectors:
            energies, diagonalization_seconds = diagonalize_sector(
                detector_n, sector, case.parameters
            )
            statistics = _spectral_statistics(energies)
            unfolded = statistics.pop("unfolded_spacings")
            sector_data[momentum].append(
                {"sector": sector, **statistics, "unfolded_spacings": unfolded}
            )
            archive_payload[f"{sector.key}__energies"] = energies
            archive_payload[f"{sector.key}__unfolded_spacings"] = unfolded
            sector_summary.append(
                {
                    **asdict(sector),
                    **statistics,
                    "diagonalization_seconds": diagonalization_seconds,
                }
            )
        print(
            f"[{case.case_key}] completed k={momentum}/{detector_n // 2}",
            flush=True,
        )

    _write_npz_atomic(paths["archive"], archive_payload)
    _plot_case(case, sector_data, detector_n, paths["figure"], dpi)
    checkpoint = {
        "schema_version": ANALYSIS_SCHEMA_VERSION,
        "analysis_digest": _analysis_digest(case, detector_n),
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "case": {
            **asdict(case),
            "source_dir": _relative(case.source_dir),
        },
        "detector_n": detector_n,
        "runtime_seconds": time.perf_counter() - started,
        "figure": _relative(paths["figure"]),
        "spectral_archive": _relative(paths["archive"]),
        "sectors": sector_summary,
        "resumed": False,
    }
    _write_json_atomic(paths["checkpoint"], checkpoint)
    return checkpoint


def _selection_record(case: RankedCase) -> dict[str, Any]:
    payload = asdict(case)
    payload["source_dir"] = _relative(case.source_dir)
    return payload


def run(
    nearest_root: Path,
    second_root: Path,
    output_dir: Path,
    detector_n: int,
    count_per_tail: int,
    workers: int,
    dpi: int,
    force: bool,
    dry_run: bool,
) -> dict[str, Any]:
    if detector_n % 2 == 0:
        raise ValueError("use odd detector N; even N requires additional half-filling symmetry")
    if workers < 1:
        raise ValueError("workers must be positive")
    campaigns = (
        CampaignSpec(
            family="nearest_neighbor",
            description="Nearest-neighbor ring",
            root=nearest_root.resolve(),
            expects_second_neighbor=False,
        ),
        CampaignSpec(
            family="second_neighbor",
            description="First- and second-neighbor ring",
            root=second_root.resolve(),
            expects_second_neighbor=True,
        ),
    )
    selected: list[RankedCase] = []
    campaign_counts: dict[str, int] = {}
    for campaign in campaigns:
        valid = load_valid_campaign(campaign)
        campaign_counts[campaign.family] = len(valid)
        ranked = select_ranked_tails(valid, count_per_tail)
        selected.extend(ranked)
        print(f"[{campaign.family}] valid={len(valid)}", flush=True)
        for tail in ("highest", "lowest"):
            rows = [case for case in ranked if case.tail == tail]
            print(
                f"  {tail}: "
                + ", ".join(
                    f"{case.config_id} (S={case.s_born:.6f})" for case in rows
                ),
                flush=True,
            )

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    selection_path = output_dir / "selection_manifest.json"
    selection_manifest = {
        "schema_version": ANALYSIS_SCHEMA_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "detector_n": detector_n,
        "selection_rule": (
            "Within each campaign: complete and validation-passed finite-S_Born "
            "cases, then the highest and lowest count_per_tail cases."
        ),
        "terminology_note": (
            "highest means most Born-like by relative rank; it does not imply "
            "passing an absolute S_Born threshold"
        ),
        "count_per_tail": count_per_tail,
        "campaign_valid_counts": campaign_counts,
        "selected_cases": [_selection_record(case) for case in selected],
    }
    _write_json_atomic(selection_path, selection_manifest)
    if dry_run:
        return {**selection_manifest, "dry_run": True, "cases": []}

    started = time.perf_counter()
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=min(workers, len(selected))) as pool:
        futures = {
            pool.submit(
                _compute_case,
                case,
                output_dir,
                detector_n,
                dpi,
                force,
            ): case
            for case in selected
        }
        for completed_count, future in enumerate(as_completed(futures), start=1):
            case = futures[future]
            result = future.result()
            results.append(result)
            print(
                f"[{completed_count:02d}/{len(selected)}] {case.case_key} "
                f"done in {result['runtime_seconds']:.1f}s"
                + (" (resumed)" if result.get("resumed") else ""),
                flush=True,
            )

    results.sort(
        key=lambda row: (
            row["case"]["family"],
            0 if row["case"]["tail"] == "highest" else 1,
            row["case"]["rank_within_tail"],
        )
    )
    summary = {
        **selection_manifest,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_seconds": time.perf_counter() - started,
        "workers": workers,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "hamiltonian_convention": (
            "H_D=-hz sum_i Z_i-J sum_i ZiZ(i+1)-Jpm/4 sum_i[(+-)+(-+)]"
            "_i,i+1-J2 sum_i ZiZ(i+2)-Jpm2/4 sum_i[(+-)+(-+)]_i,i+2"
        ),
        "symmetry_resolution": (
            "fixed N_up; k=0 split by reflection parity; nonzero k represents "
            "one spectral copy of the paired dihedral irrep (k,N-k); "
            "complementary N_up>N/2 omitted because spacings are identical"
        ),
        "unfolding": {
            "method": "cubic staircase with monotone local-spacing fallback",
            "edge_trim_fraction": 0.1,
            "degeneracy_tolerance": "1e-10 times sector bandwidth",
            "exact_degeneracies": "merged before unfolding",
        },
        "cases": results,
    }
    summary_path = output_dir / f"summary_N{detector_n}.json"
    _write_json_atomic(summary_path, summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nearest-root", type=Path, default=DEFAULT_NEAREST_ROOT)
    parser.add_argument("--second-root", type=Path, default=DEFAULT_SECOND_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--n", type=int, default=17, help="Odd detector size.")
    parser.add_argument("--count-per-tail", type=int, default=10)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--dpi", type=int, default=190)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(
        nearest_root=args.nearest_root,
        second_root=args.second_root,
        output_dir=args.output,
        detector_n=args.n,
        count_per_tail=args.count_per_tail,
        workers=args.workers,
        dpi=args.dpi,
        force=args.force,
        dry_run=args.dry_run,
    )
    if args.dry_run:
        print(
            f"Dry run selected {len(summary['selected_cases'])} cases; "
            f"manifest: {args.output.resolve() / 'selection_manifest.json'}",
            flush=True,
        )
    else:
        print(
            f"Completed {len(summary['cases'])} cases in "
            f"{summary['runtime_seconds'] / 60.0:.2f} min; "
            f"outputs: {args.output.resolve()}",
            flush=True,
        )


if __name__ == "__main__":
    main()
