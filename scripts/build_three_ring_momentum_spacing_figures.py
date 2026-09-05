"""Build momentum-resolved detector level-spacing figures for three N=17 cases.

The source cases are identified by their already-computed N=17 diagnostics.
For an odd detector size, the conventional exact symmetries are fixed detector
magnetisation, translations, and reflection.  Reflection is resolved explicitly
at k=0; at nonzero momentum it pairs k with N-k into one dihedral irrep, whose
two representation rows have identical spectra.

For every nonredundant momentum, the five symmetry blocks with the largest
multiplicity-space dimensions are diagonalised.  Exact numerical degeneracies
are merged before cubic unfolding, matching ``core.level_spacing``.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
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
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from core.level_spacing import (  # noqa: E402
    compute_level_spacing_ratios,
    compute_level_spacings,
    compute_unfolded_spacings,
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)


DEFAULT_CAMPAIGN = ROOT / "work" / "zeus_top20_last5_largerN_20260810_001532"
DEFAULT_OUTPUT = ROOT / "work" / "ring_momentum_level_spacing_three_cases_20260823"


@dataclass(frozen=True)
class CaseSource:
    case_id: str
    description: str
    diagnostics_path: Path


@dataclass(frozen=True)
class HamiltonianParameters:
    hz: float
    j: float
    jpm: float
    j2: float
    jpm2: float


@dataclass(frozen=True)
class SectorSpec:
    n_up: int
    momentum: int
    reflection_parity: int | None
    dimension: int

    @property
    def key(self) -> str:
        parity = "none" if self.reflection_parity is None else f"{self.reflection_parity:+d}"
        return f"k{self.momentum:02d}_q{self.n_up:02d}_p{parity}"

    @property
    def label(self) -> str:
        parity = "" if self.reflection_parity is None else f", p={'+' if self.reflection_parity > 0 else '-'}"
        return rf"$N_\uparrow={self.n_up}{parity}$"


DEFAULT_CASES = (
    CaseSource(
        case_id="case_01_born_like_nearest_neighbor",
        description="Born-like nearest-neighbor ring",
        diagnostics_path=DEFAULT_CAMPAIGN / "source_02" / "rank_001" / "N17",
    ),
    CaseSource(
        case_id="case_02_non_born_exchange_only",
        description="Non-Born exchange-only ring",
        diagnostics_path=DEFAULT_CAMPAIGN / "source_04" / "rank_001" / "N17",
    ),
    CaseSource(
        case_id="case_03_born_like_second_neighbor",
        description="Born-like first- and second-neighbor ring",
        diagnostics_path=DEFAULT_CAMPAIGN / "source_03" / "rank_001" / "N17",
    ),
)


def _load_case(case: CaseSource) -> tuple[HamiltonianParameters, dict[str, Any]]:
    metadata_path = case.diagnostics_path / "metadata.json"
    metrics_path = case.diagnostics_path / "metrics.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    source = metadata["source"]
    parameters = HamiltonianParameters(
        hz=float(source["hz"]),
        j=float(source["j"]),
        jpm=float(source["jpm"]),
        j2=float(source.get("j2", 0.0)),
        jpm2=float(source.get("jpm2", 0.0)),
    )
    provenance = {
        "diagnostics_path": str(case.diagnostics_path.relative_to(ROOT)),
        "metadata_path": str(metadata_path.relative_to(ROOT)),
        "metrics_path": str(metrics_path.relative_to(ROOT)),
        "source_case": source["source_case"],
        "source_root_name": Path(source["source_root"]).name,
        "hz0": float(source["hz0"]),
        "jx_unscaled": float(source["jx"]),
        "jx_effective_N17": float(metadata["Jx_effective"]),
        "jy_unscaled": float(source.get("jy", 0.0)),
        "N17_S_born": float(metrics["S_born"]),
        "N17_born_RMSE_occupied": float(metrics["born_RMSE_occupied"]),
    }
    return parameters, provenance


def _basis(n: int, sector: SectorSpec | tuple[int, int, int | None]):
    from quspin.basis import spin_basis_1d

    if isinstance(sector, SectorSpec):
        n_up = sector.n_up
        momentum = sector.momentum
        parity = sector.reflection_parity
    else:
        n_up, momentum, parity = sector
    blocks: dict[str, int] = {"Nup": n_up, "kblock": momentum}
    if parity is not None:
        blocks["pblock"] = parity
    return spin_basis_1d(n, **blocks)


def select_largest_sectors(n: int, count: int = 5) -> dict[int, list[SectorSpec]]:
    """Return the largest fully resolved blocks at each unique momentum.

    For even ``n`` the half-filled block is deliberately omitted because
    global spin reversal is an additional internal symmetry there.  The
    retained ``N_up < n/2`` blocks are complete conventional symmetry sectors;
    their ``N_up > n/2`` partners are isospectral under global spin reversal.
    Reflection parity is resolved at both self-conjugate momenta, ``k=0`` and
    (for even ``n``) ``k=n/2``.
    """
    if n < 3:
        raise ValueError("n must be at least 3")
    if count < 1:
        raise ValueError("count must be positive")
    maximum_weight = (n - 1) // 2
    maximum_momentum = n // 2
    output: dict[int, list[SectorSpec]] = {}
    dimensions: dict[tuple[int, int, int | None], int] = {}
    for momentum in range(maximum_momentum + 1):
        candidates: list[SectorSpec] = []
        for n_up in range(maximum_weight + 1):
            reflection_momentum = momentum == 0 or (
                n % 2 == 0 and momentum == maximum_momentum
            )
            parities: tuple[int | None, ...] = (
                (1, -1) if reflection_momentum else (None,)
            )
            for parity in parities:
                dimension = int(_basis(n, (n_up, momentum, parity)).Ns)
                dimensions[(n_up, momentum, parity)] = dimension
                if dimension:
                    candidates.append(
                        SectorSpec(
                            n_up=n_up,
                            momentum=momentum,
                            reflection_parity=parity,
                            dimension=dimension,
                        )
                    )
        output[momentum] = sorted(
            candidates,
            key=lambda sector: (
                -sector.dimension,
                -sector.n_up,
                -(sector.reflection_parity or 0),
            ),
        )[:count]

    # Exact representation-dimension check for every retained magnetisation.
    for n_up in range(maximum_weight + 1):
        reconstructed = sum(dimensions[(n_up, 0, parity)] for parity in (1, -1))
        if n % 2 == 0:
            reconstructed += sum(
                dimensions[(n_up, maximum_momentum, parity)]
                for parity in (1, -1)
            )
            generic_momenta = range(1, maximum_momentum)
        else:
            generic_momenta = range(1, maximum_momentum + 1)
        reconstructed += 2 * sum(
            dimensions[(n_up, momentum, None)] for momentum in generic_momenta
        )
        expected = math.comb(n, n_up)
        if reconstructed != expected:
            raise RuntimeError(
                f"sector dimensions fail for Nup={n_up}: {reconstructed} != {expected}"
            )
    return output


def _detector_static(n: int, parameters: HamiltonianParameters) -> list[list[Any]]:
    nearest = [(site, (site + 1) % n) for site in range(n)]
    second = [(site, (site + 2) % n) for site in range(n)]
    static: list[list[Any]] = []
    if parameters.j:
        static.append(["zz", [[-parameters.j, left, right] for left, right in nearest]])
    if parameters.jpm:
        exchange = [[-parameters.jpm / 4.0, left, right] for left, right in nearest]
        static.extend((["+-", exchange], ["-+", exchange]))
    if parameters.j2:
        static.append(["zz", [[-parameters.j2, left, right] for left, right in second]])
    if parameters.jpm2:
        exchange2 = [[-parameters.jpm2 / 4.0, left, right] for left, right in second]
        static.extend((["+-", exchange2], ["-+", exchange2]))
    if parameters.hz:
        static.append(["z", [[-parameters.hz, site] for site in range(n)]])
    return static


def diagonalize_sector(
    n: int,
    sector: SectorSpec,
    parameters: HamiltonianParameters,
) -> tuple[np.ndarray, float]:
    from quspin.operators import hamiltonian

    basis = _basis(n, sector)
    if int(basis.Ns) != sector.dimension:
        raise RuntimeError(f"basis dimension changed for {sector.key}")
    dtype = np.float64 if sector.momentum == 0 else np.complex128
    started = time.perf_counter()
    operator = hamiltonian(
        _detector_static(n, parameters),
        [],
        basis=basis,
        dtype=dtype,
        check_herm=False,
        check_symm=False,
        check_pcon=False,
    )
    energies = np.asarray(operator.eigvalsh(), dtype=np.float64)
    elapsed = time.perf_counter() - started
    if energies.size != sector.dimension or not np.all(np.isfinite(energies)):
        raise RuntimeError(f"invalid eigenspectrum for {sector.key}")
    return energies, elapsed


def _spectral_statistics(energies: np.ndarray) -> dict[str, Any]:
    bandwidth = float(np.ptp(energies))
    tolerance = 1.0e-10 * max(bandwidth, np.finfo(float).eps)
    raw_spacings = np.diff(np.sort(energies))
    degeneracy_count = int(np.count_nonzero(raw_spacings <= tolerance))
    resolved_spacings = compute_level_spacings(energies, tol=tolerance)
    ratios = compute_level_spacing_ratios(resolved_spacings)
    unfolded = compute_unfolded_spacings(
        energies,
        tol=tolerance,
        degree=3,
        trim_fraction=0.1,
    )
    return {
        "bandwidth": bandwidth,
        "degeneracy_tolerance": tolerance,
        "degenerate_adjacent_count": degeneracy_count,
        "resolved_level_count": int(resolved_spacings.size + (energies.size > 0)),
        "spacing_count": int(unfolded.size),
        "mean_r": float(np.mean(ratios)) if ratios.size else float("nan"),
        "unfolded_spacings": unfolded,
    }


def _plot_case(
    case: CaseSource,
    parameters: HamiltonianParameters,
    provenance: dict[str, Any],
    sector_data: dict[int, list[dict[str, Any]]],
    n: int,
    output: Path,
    dpi: int,
) -> None:
    colors = plt.get_cmap("tab10").colors[:5]
    figure, axes = plt.subplots(3, 3, figsize=(18.0, 14.5), sharex=True, sharey=True)
    s_grid = np.linspace(0.0, 4.0, 600)
    for momentum, axis in enumerate(axes.flat):
        for color, row in zip(colors, sector_data[momentum], strict=True):
            spacings = row["statistics"]["unfolded_spacings"]
            counts, edges = np.histogram(spacings, bins=np.linspace(0.0, 4.0, 33))
            density = counts / (max(spacings.size, 1) * np.diff(edges))
            centers = 0.5 * (edges[:-1] + edges[1:])
            sector = row["sector"]
            mean_r = row["statistics"]["mean_r"]
            axis.step(
                centers,
                density,
                where="mid",
                color=color,
                linewidth=1.15,
                alpha=0.92,
                label=(
                    f"{sector.label}, d={sector.dimension}, "
                    rf"$\langle\tilde r\rangle={mean_r:.3f}$"
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
    for axis in axes[-1, :]:
        axis.set_xlabel(r"unfolded spacing $s$")
    for axis in axes[:, 0]:
        axis.set_ylabel(r"density $P(s)$")

    second_text = ""
    if parameters.j2 or parameters.jpm2:
        second_text = rf", $J_2={parameters.j2:.6g}$, $J_{{\pm2}}={parameters.jpm2:.6g}$"
    figure.suptitle(
        "\n".join(
            (
                rf"{case.description}: five largest resolved blocks per momentum ($N_D={n}$)",
                rf"$S_{{\rm Born}}={provenance['N17_S_born']:.6f}$, "
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
            r"Conventional sectors: fixed $N_\uparrow$, $D_{17}$ translation/reflection; "
            r"each $k\ne0$ pane represents the equivalent $\pm k$ pair. "
            r"Exact degeneracies are merged before cubic unfolding; 10% spectral-edge trim."
        ),
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0.025, 0.03, 0.99, 0.945), h_pad=2.0, w_pad=1.4)
    figure.savefig(output, dpi=dpi, bbox_inches="tight")
    plt.close(figure)


def run(n: int, output_dir: Path, dpi: int, force: bool) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / f"summary_N{n}.json"
    if summary_path.exists() and not force:
        raise FileExistsError(f"{summary_path} exists; pass --force to replace this exact analysis")

    selected = select_largest_sectors(n, count=5)
    npz_payload: dict[str, np.ndarray] = {}
    case_summaries: list[dict[str, Any]] = []
    total_started = time.perf_counter()
    for case_index, case in enumerate(DEFAULT_CASES, start=1):
        parameters, provenance = _load_case(case)
        print(
            f"[{case_index}/{len(DEFAULT_CASES)}] {case.case_id}: "
            f"J={parameters.j:.8g}, hz={parameters.hz:.8g}, "
            f"Jpm={parameters.jpm:.8g}, J2={parameters.j2:.8g}, "
            f"Jpm2={parameters.jpm2:.8g}",
            flush=True,
        )
        case_started = time.perf_counter()
        sector_data: dict[int, list[dict[str, Any]]] = {}
        sector_summary: list[dict[str, Any]] = []
        case_npz_payload: dict[str, np.ndarray] = {}
        completed = 0
        total = sum(len(items) for items in selected.values())
        for momentum, sectors in selected.items():
            sector_data[momentum] = []
            for sector in sectors:
                energies, diagonalization_seconds = diagonalize_sector(
                    n, sector, parameters
                )
                statistics = _spectral_statistics(energies)
                completed += 1
                print(
                    f"  [{completed:02d}/{total}] {sector.key}: d={sector.dimension}, "
                    f"resolved={statistics['resolved_level_count']}, "
                    f"diag={diagonalization_seconds:.2f}s",
                    flush=True,
                )
                sector_data[momentum].append(
                    {"sector": sector, "statistics": statistics}
                )
                prefix = f"{case.case_id}__{sector.key}"
                npz_payload[f"{prefix}__energies"] = energies
                npz_payload[f"{prefix}__unfolded_spacings"] = statistics[
                    "unfolded_spacings"
                ]
                case_npz_payload[f"{sector.key}__energies"] = energies
                case_npz_payload[f"{sector.key}__unfolded_spacings"] = statistics[
                    "unfolded_spacings"
                ]
                serializable_statistics = {
                    key: value
                    for key, value in statistics.items()
                    if key != "unfolded_spacings"
                }
                sector_summary.append(
                    {
                        **asdict(sector),
                        **serializable_statistics,
                        "diagonalization_seconds": diagonalization_seconds,
                    }
                )

        case_archive_path = output_dir / f"{case.case_id}_N{n}_spectra.npz"
        np.savez_compressed(case_archive_path, **case_npz_payload)
        case_checkpoint_path = output_dir / f"{case.case_id}_N{n}_checkpoint.json"
        case_checkpoint_path.write_text(
            json.dumps(
                {
                    "case_id": case.case_id,
                    "description": case.description,
                    "parameters": asdict(parameters),
                    "provenance": provenance,
                    "detector_n": n,
                    "sectors": sector_summary,
                    "spectral_archive": str(case_archive_path.relative_to(ROOT)),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        figure_path = output_dir / f"{case.case_id}_N{n}_momentum_level_spacings.png"
        _plot_case(
            case,
            parameters,
            provenance,
            sector_data,
            n,
            figure_path,
            dpi,
        )
        case_summaries.append(
            {
                "case_id": case.case_id,
                "description": case.description,
                "parameters": asdict(parameters),
                "provenance": provenance,
                "figure": str(figure_path.relative_to(ROOT)),
                "checkpoint": str(case_checkpoint_path.relative_to(ROOT)),
                "spectral_archive": str(case_archive_path.relative_to(ROOT)),
                "runtime_seconds": time.perf_counter() - case_started,
                "sectors": sector_summary,
            }
        )

    archive_path = output_dir / f"spectra_and_spacings_N{n}.npz"
    np.savez_compressed(archive_path, **npz_payload)
    summary = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "detector_n": n,
        "nonredundant_momenta": list(selected),
        "sectors_per_momentum": 5,
        "hamiltonian_convention": (
            "H_D=-hz sum_i Z_i-J sum_i ZiZ(i+1)-Jpm/4 sum_i "
            "[(+_-)_i,i+1+(-+)_i,i+1]-J2 sum_i ZiZ(i+2)-Jpm2/4 "
            "sum_i[(+_-)_i,i+2+(-+)_i,i+2], periodic indices"
        ),
        "symmetry_resolution": (
            "fixed N_up; k=0 split by reflection p; nonzero k represents one "
            "spectral copy of the D_N pair k and N-k; complementary N_up>N/2 omitted"
        ),
        "unfolding": {
            "method": "cubic polynomial staircase with monotone local-spacing fallback",
            "edge_trim_fraction": 0.1,
            "degeneracy_tolerance": "1e-10 times each sector bandwidth",
            "exact_degeneracies": "merged before unfolding",
        },
        "dimension_validation": "exact binomial reconstruction passed for every N_up=0..floor(N/2)",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "runtime_seconds": time.perf_counter() - total_started,
        "spectral_archive": str(archive_path.relative_to(ROOT)),
        "cases": case_summaries,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=17, help="Odd detector size (default: 17).")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dpi", type=int, default=190)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.n, args.output.resolve(), args.dpi, args.force)
    print(
        f"Completed {len(summary['cases'])} cases in "
        f"{summary['runtime_seconds'] / 60.0:.2f} min; "
        f"outputs: {args.output.resolve()}",
        flush=True,
    )


if __name__ == "__main__":
    main()
