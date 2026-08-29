"""
Sector-aware finite-time weak-kernel diagnostics for symmetric detector rings.

This script targets the large-N follow-up to the slide-8 ``hz0=0`` result.
It diagonalizes the detector Hamiltonian in magnetization and ring-momentum
sectors, assembles the first-order weak relative-evolution kernel

    K_t ~ U00(t)^(-1) U10(t)

within each momentum block, and scores its angle statistics.  The supported
model is intentionally narrow: single-pixel ring, all-site central coupling,
no disorder, no longitudinal central conditional term, and detector terms that
conserve detector Sz (ZZ + Jpm + hz).  That is the perturbative family needed
for the ``hz0=0`` ZZ+Jpm slide-8 explanation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402
from quspin.basis import spin_basis_1d, spin_basis_general  # noqa: E402
from quspin.operators import hamiltonian  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from born_hamiltonian_search import Candidate, TeeWriter, _candidate_label, _default_worker_count, _safe_plot_name  # noqa: E402
from core.born import diagnostics_from_radii  # noqa: E402
from detector_spectral_response import plot_kernel_diagnostics  # noqa: E402


@dataclass(frozen=True)
class DetectorSector:
    magnetization_up: int
    momentum: int
    basis: Any
    energies: np.ndarray
    vectors: np.ndarray

    @property
    def dimension(self) -> int:
        return int(self.energies.size)


def _build_candidate_grid(args: argparse.Namespace) -> list[Candidate]:
    candidates: list[Candidate] = []
    for N in args.N:
        for hz0_mode in args.hz0_modes:
            for jpm in args.Jpm:
                for jx in args.jx_unscaled:
                    for hz in args.hz:
                        candidates.append(
                            Candidate(
                                model="single_pixel",
                                N=N,
                                J=args.J,
                                Jpm=jpm,
                                Jxx=0.0,
                                Jyy=0.0,
                                Jx_unscaled=jx,
                                Jy_unscaled=0.0,
                                Jz=0.0,
                                Jzx=0.0,
                                Jcpm_unscaled=0.0,
                                hx=0.0,
                                hz=hz,
                                hz0_mode=hz0_mode,
                                connectivity="ring",
                                central_coupling="all",
                                seed=args.seed,
                            )
                        )
    return candidates


def _hz0_value(candidate: Candidate) -> float:
    if candidate.hz0 is None:
        return float(candidate.hz)
    return float(candidate.hz0)


def _translation_permutation(n: int) -> np.ndarray:
    return np.array([(i + 1) % n for i in range(n)])


def _detector_static(candidate: Candidate) -> tuple[list, int]:
    n = candidate.N_pixel
    bonds = [(i, (i + 1) % n) for i in range(n)]
    zz = [[-candidate.J, i, j] for i, j in bonds]
    z_fields = [[-candidate.hz, i] for i in range(n)]
    static = [["zz", zz], ["z", z_fields]]
    if candidate.Jpm != 0.0:
        pm = [[-candidate.Jpm / 4.0, i, j] for i, j in bonds]
        static.append(["+-", pm])
        static.append(["-+", pm])
    return static, n


def _central_flip_static(candidate: Candidate) -> tuple[list, int]:
    n = candidate.N_pixel
    x_terms = [[-candidate.Jx, i] for i in range(n)]
    return [["x", x_terms]], n


def _validate_supported(candidate: Candidate) -> None:
    if candidate.model != "single_pixel":
        raise ValueError("sector weak-kernel diagnostics support only single_pixel")
    if candidate.connectivity != "ring":
        raise ValueError("sector weak-kernel diagnostics currently require connectivity=ring")
    if candidate.central_coupling != "all":
        raise ValueError("sector weak-kernel diagnostics currently require central_coupling=all")
    unsupported = {
        "Jxx": candidate.Jxx,
        "Jyy": candidate.Jyy,
        "Jy_unscaled": candidate.Jy_unscaled,
        "Jz": candidate.Jz,
        "Jzx": candidate.Jzx,
        "Jcpm_unscaled": candidate.Jcpm_unscaled,
        "hx": candidate.hx,
        "disorder_strength": candidate.disorder_strength,
        "disorder_strength_J": candidate.disorder_strength_J,
        "disorder_strength_Jpm": candidate.disorder_strength_Jpm,
        "disorder_strength_Jx": candidate.disorder_strength_Jx,
        "disorder_strength_Jz": candidate.disorder_strength_Jz,
        "disorder_strength_Jzx": candidate.disorder_strength_Jzx,
        "disorder_strength_Jcpm": candidate.disorder_strength_Jcpm,
        "disorder_strength_hx": candidate.disorder_strength_hx,
        "disorder_strength_hz": candidate.disorder_strength_hz,
    }
    nonzero = [name for name, value in unsupported.items() if abs(float(value)) > 0.0]
    if candidate.disorder != "none":
        nonzero.append("disorder")
    if nonzero:
        raise ValueError(
            "sector weak-kernel diagnostics require an Sz-conserving clean detector; "
            f"nonzero unsupported fields: {', '.join(nonzero)}"
        )


def diagonalize_detector_sectors(candidate: Candidate) -> list[DetectorSector]:
    _validate_supported(candidate)
    static, n = _detector_static(candidate)
    translation = _translation_permutation(n)
    sectors: list[DetectorSector] = []
    for m in range(n + 1):
        for k in range(n):
            basis = spin_basis_general(n, Nup=m, kblock=(translation, k))
            if basis.Ns == 0:
                continue
            H = hamiltonian(
                static,
                [],
                basis=basis,
                dtype=np.complex128,
                check_symm=False,
                check_herm=False,
                check_pcon=False,
            )
            energies, vectors = np.linalg.eigh(H.toarray())
            sectors.append(
                DetectorSector(
                    magnetization_up=m,
                    momentum=k,
                    basis=basis,
                    energies=energies,
                    vectors=vectors,
                )
            )
    return sectors


def central_flip_operator(candidate: Candidate):
    static, n = _central_flip_static(candidate)
    basis = spin_basis_1d(L=n)
    return hamiltonian(
        static,
        [],
        basis=basis,
        dtype=np.complex128,
        check_symm=False,
        check_herm=False,
        check_pcon=False,
    ).tocsr()


def _finite_time_integral(
    source_energies_A: np.ndarray,
    target_energies_D: np.ndarray,
    t_value: float,
) -> np.ndarray:
    delta = target_energies_D[:, None] - source_energies_A[None, :]
    out = np.empty(delta.shape, dtype=np.complex128)
    small = np.abs(delta) <= 1e-12
    degenerate_value = np.broadcast_to(
        t_value * np.exp(-1j * target_energies_D[:, None] * t_value),
        delta.shape,
    )
    out[small] = degenerate_value[small]
    if np.any(~small):
        phase = np.broadcast_to(
            np.exp(-1j * target_energies_D[:, None] * t_value),
            delta.shape,
        )
        delta_nz = delta[~small]
        out[~small] = (
            phase[~small]
            * (np.exp(1j * delta_nz * t_value) - 1.0)
            / (1j * delta_nz)
        )
    return out


def _projected_vectors(sector: DetectorSector) -> np.ndarray:
    return np.asarray(sector.basis.project_from(sector.vectors, sparse=False))


def _sector_pair_block_from_projected(
    source: DetectorSector,
    target: DetectorSector,
    source_vectors: np.ndarray,
    target_vectors: np.ndarray,
    b_source_vectors: np.ndarray,
    *,
    hz0: float,
    t_value: float,
) -> np.ndarray:
    b_matrix = target_vectors.conj().T @ b_source_vectors
    source_A = source.energies - hz0
    target_D = target.energies + hz0
    integral = _finite_time_integral(source_A, target_D, t_value)
    left_phase = np.exp(1j * (target.energies - hz0) * t_value)[:, None]
    return -1j * left_phase * b_matrix * integral


def weak_kernel_eigenvalues_by_momentum(
    sectors: list[DetectorSector],
    B_sparse,
    *,
    hz0: float,
    t_value: float,
) -> tuple[np.ndarray, list[dict[str, float]]]:
    by_key = {(sector.magnetization_up, sector.momentum): sector for sector in sectors}
    momenta = sorted({sector.momentum for sector in sectors})
    eigenvalues: list[np.ndarray] = []
    block_rows: list[dict[str, float]] = []
    for k in momenta:
        sectors_k = [sector for sector in sectors if sector.momentum == k]
        sectors_k.sort(key=lambda sector: sector.magnetization_up)
        offsets: dict[int, int] = {}
        cursor = 0
        for sector in sectors_k:
            offsets[sector.magnetization_up] = cursor
            cursor += sector.dimension
        if cursor == 0:
            continue
        block = np.zeros((cursor, cursor), dtype=np.complex128)
        projected = {
            sector.magnetization_up: _projected_vectors(sector)
            for sector in sectors_k
        }
        for source in sectors_k:
            col0 = offsets[source.magnetization_up]
            col1 = col0 + source.dimension
            source_vectors = projected[source.magnetization_up]
            b_source_vectors = B_sparse @ source_vectors
            for target_m in (source.magnetization_up - 1, source.magnetization_up + 1):
                target = by_key.get((target_m, k))
                if target is None:
                    continue
                row0 = offsets[target_m]
                row1 = row0 + target.dimension
                block[row0:row1, col0:col1] = _sector_pair_block_from_projected(
                    source,
                    target,
                    source_vectors,
                    projected[target_m],
                    b_source_vectors,
                    hz0=hz0,
                    t_value=t_value,
                )
        values = np.linalg.eigvals(block)
        eigenvalues.append(values)
        radii = np.abs(values)
        positive = radii[np.isfinite(radii) & (radii > 0)]
        block_rows.append(
            {
                "momentum": float(k),
                "block_dimension": float(cursor),
                "radius_q50": float(np.percentile(positive, 50)) if positive.size else math.nan,
                "radius_q99": float(np.percentile(positive, 99)) if positive.size else math.nan,
                "block_norm": float(np.linalg.norm(block, ord="fro")),
            }
        )
    if not eigenvalues:
        return np.asarray([], dtype=np.complex128), block_rows
    return np.concatenate(eigenvalues), block_rows


def diagnostics_from_eigenvalues(
    eigenvalues: np.ndarray,
    *,
    n_theta: int,
    tail_fraction: float,
    n_log_bins: int,
) -> dict[str, float]:
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
    return {
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
        "radius_q50": q50,
        "radius_q99": q99,
        "n_eigenvalues": float(eigenvalues.size),
    }


def _time_tag(value: float) -> str:
    return f"{value:g}".replace(".", "p").replace("-", "m")


def _candidate_metadata(candidate: Candidate) -> dict[str, Any]:
    return {
        "label": _candidate_label(candidate),
        "N": candidate.N,
        "N_pixel": candidate.N_pixel,
        "model": candidate.model,
        "connectivity": candidate.connectivity,
        "central_coupling": candidate.central_coupling,
        "hz0_mode": candidate.hz0_mode,
        "hz0": _hz0_value(candidate),
        "hz": candidate.hz,
        "J": candidate.J,
        "Jpm": candidate.Jpm,
        "Jx_unscaled": candidate.Jx_unscaled,
        "Jx_scaled": candidate.Jx,
        "seed": candidate.seed,
    }


def write_outputs(
    out_dir: Path,
    rows: list[dict[str, Any]],
    block_rows: list[dict[str, Any]],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = out_dir / "sector_weak_kernel_summary.csv"
    fields = [
        "label",
        "N",
        "N_pixel",
        "connectivity",
        "central_coupling",
        "hz0_mode",
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
        "figure",
    ]
    with summary_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    block_csv = out_dir / "sector_weak_kernel_blocks.csv"
    block_fields = [
        "label",
        "N",
        "hz0_mode",
        "Jpm",
        "t",
        "momentum",
        "block_dimension",
        "radius_q50",
        "radius_q99",
        "block_norm",
    ]
    with block_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=block_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(block_rows)

    lines = [
        "# Sector weak-kernel diagnostics",
        "",
        "This run diagonalizes the first-order weak kernel in detector",
        "magnetization and ring-momentum sectors.",
        "",
        f"- Summary CSV: `{summary_csv.name}`",
        f"- Momentum-block CSV: `{block_csv.name}`",
        "",
        "| label | t | S_born | reciprocity | q99/q50 | max block dim | figure |",
        "|:---|---:|---:|---:|---:|---:|:---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['label']}` | {row['t']:.6g} | "
            f"{row['born_similarity']:.4g} | {row['reciprocity_error']:.4g} | "
            f"{row['radius_q99_over_q50']:.4g} | "
            f"{row['max_momentum_block_dimension']:.0f} | "
            f"[figure]({Path(row['figure']).name}) |"
        )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, nargs="+", default=[10])
    parser.add_argument("--J", type=float, default=1.0)
    parser.add_argument("--Jpm", type=float, nargs="+", default=[0.05])
    parser.add_argument("--jx-unscaled", type=float, nargs="+", default=[0.05])
    parser.add_argument("--hz", type=float, nargs="+", default=[0.1])
    parser.add_argument("--hz0-modes", nargs="+", default=["zero", "matched"], choices=["matched", "zero", "half", "minus"])
    parser.add_argument("--times", type=float, nargs="+", default=[1000.0, 3162.0])
    parser.add_argument("--seed", type=int, default=44)
    parser.add_argument("--n-theta", type=int, default=100)
    parser.add_argument("--tail-fraction", type=float, default=0.10)
    parser.add_argument("--log-bins", type=int, default=50)
    parser.add_argument(
        "--workers",
        type=int,
        default=_default_worker_count(),
        help="Number of independent candidates to evaluate in parallel.",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("figures/sector_weak_kernel_diagnostics"))
    parser.add_argument("--log-file", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    log_file = args.log_file or args.out_dir / "run.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with log_file.open("w", encoding="utf-8") as log_fh:
        tee = TeeWriter(sys.stdout, log_fh)
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
    start_all = time.time()
    candidates = _build_candidate_grid(args)
    args.workers = max(1, int(args.workers))
    print(f"Candidates: {len(candidates)}")
    print(f"Times: {args.times}")
    print(f"Output: {args.out_dir}")
    print(f"Worker processes: {args.workers}")

    rows: list[dict[str, Any]] = []
    block_rows_all: list[dict[str, Any]] = []
    manifest: list[dict[str, Any]] = []

    jobs = [
        (candidate, list(args.times), args.n_theta, args.tail_fraction, args.log_bins, args.out_dir)
        for candidate in candidates
    ]
    if args.workers == 1 or len(jobs) <= 1:
        for idx, job in enumerate(jobs, start=1):
            print(f"[{idx}/{len(jobs)}] {_candidate_label(job[0])}", flush=True)
            candidate_rows, candidate_block_rows, manifest_item, log_lines = _evaluate_sector_candidate_job(job)
            rows.extend(candidate_rows)
            block_rows_all.extend(candidate_block_rows)
            manifest.append(manifest_item)
            for line in log_lines:
                print(line)
    else:
        n_workers = min(args.workers, len(jobs))
        print(f"Submitting {len(jobs)} sector weak-kernel jobs to {n_workers} workers", flush=True)
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            future_to_candidate = {
                pool.submit(_evaluate_sector_candidate_job, job): job[0]
                for job in jobs
            }
            for done_idx, future in enumerate(as_completed(future_to_candidate), start=1):
                candidate = future_to_candidate[future]
                try:
                    candidate_rows, candidate_block_rows, manifest_item, log_lines = future.result()
                except Exception as exc:
                    raise RuntimeError(f"Worker failed for {_candidate_label(candidate)}") from exc
                rows.extend(candidate_rows)
                block_rows_all.extend(candidate_block_rows)
                manifest.append(manifest_item)
                print(f"[{done_idx}/{len(jobs)}] completed {_candidate_label(candidate)}", flush=True)
                for line in log_lines:
                    print(line)

    write_outputs(args.out_dir, rows, block_rows_all)
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Wrote {args.out_dir / 'summary.md'}")
    print(f"Elapsed seconds: {time.time() - start_all:.2f}")


def _evaluate_sector_candidate_job(
    payload: tuple[Candidate, list[float], int, float, int, Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], list[str]]:
    candidate, times, n_theta, tail_fraction, log_bins, out_dir = payload
    label = _candidate_label(candidate)
    candidate_start = time.time()
    log_lines: list[str] = []
    sectors = diagonalize_detector_sectors(candidate)
    B_sparse = central_flip_operator(candidate)
    sector_count = len(sectors)
    max_sector_dimension = max((sector.dimension for sector in sectors), default=0)
    log_lines.append(f"  sectors={sector_count}, max sector dim={max_sector_dimension}")

    rows: list[dict[str, Any]] = []
    block_rows_all: list[dict[str, Any]] = []
    for t_value in times:
        values, block_rows = weak_kernel_eigenvalues_by_momentum(
            sectors,
            B_sparse,
            hz0=_hz0_value(candidate),
            t_value=t_value,
        )
        metrics = diagnostics_from_eigenvalues(
            values,
            n_theta=n_theta,
            tail_fraction=tail_fraction,
            n_log_bins=log_bins,
        )
        metadata = _candidate_metadata(candidate)
        max_block_dimension = max((row["block_dimension"] for row in block_rows), default=0.0)
        figure = out_dir / f"{_safe_plot_name(label)}_sector_weak_kernel_t{_time_tag(t_value)}.png"
        plot_kernel_diagnostics(
            np.abs(values),
            {"t": t_value, **metrics, "weak_kernel_norm": float(np.linalg.norm(values))},
            figure,
            title=f"{label} sector weak kernel",
            n_theta=n_theta,
        )
        row = {
            **metadata,
            "t": float(t_value),
            **metrics,
            "sector_count": float(sector_count),
            "max_sector_dimension": float(max_sector_dimension),
            "max_momentum_block_dimension": float(max_block_dimension),
            "wall_seconds": time.time() - candidate_start,
            "figure": str(figure),
        }
        rows.append(row)
        log_lines.append(
            "    "
            f"t={t_value:g}: S={row['born_similarity']:.4g}, "
            f"recip={row['reciprocity_error']:.4g}, "
            f"q99/q50={row['radius_q99_over_q50']:.4g}, "
            f"max block={row['max_momentum_block_dimension']:.0f}"
        )
        for block_row in block_rows:
            block_rows_all.append(
                {
                    "label": label,
                    "N": candidate.N,
                    "hz0_mode": candidate.hz0_mode,
                    "Jpm": candidate.Jpm,
                    "t": float(t_value),
                    **block_row,
                }
            )

    manifest_item = {
        "candidate": asdict(candidate),
        "label": label,
        "sector_count": sector_count,
        "max_sector_dimension": max_sector_dimension,
        "rows": rows,
    }
    return rows, block_rows_all, manifest_item, log_lines


if __name__ == "__main__":
    main()
