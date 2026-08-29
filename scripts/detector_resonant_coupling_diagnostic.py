"""
Detector-basis resonant-coupling diagnostics for Born-rule search rows.

For a single-pixel Hamiltonian with weak central coupling,

    H = H_D + sum_alpha sigma_0^alpha tensor B_alpha,

the first-order qubit-flip kernel contains detector-basis factors

    (B_alpha)_{ab} F_t(E_a - E_b).

This script computes how much interaction Frobenius weight lies inside exactly
or nearly resonant detector eigenspaces.  It also distinguishes a resonant
action proportional to the identity in each exactly degenerate eigenspace from
one that can split or mix that eigenspace.  The exact-tolerance diagnostic is

    eta_res = sum_{alpha, |Ea-Eb|<=tol} |(B_alpha)_{ab}|^2
              / sum_{alpha, a,b} |(B_alpha)_{ab}|^2.

For finite-time scans the script also reports a time-windowed version using

    delta_t = max(tol, window_factor / t),

which better matches the perturbative denominator

    F_t(Delta) = (exp(i Delta t) - 1) / (i Delta).

It is a dense NumPy diagnostic for small detector sizes. Use it to validate the
resonant-kernel conjecture locally before implementing symmetry-reduced large-N
versions.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.hamiltonians.numpy_hamiltonians import _central_targets, _pixel_bonds  # noqa: E402
from core.pauli import build_pauli_operators, build_pauli_y  # noqa: E402


@dataclass(frozen=True)
class DetectorKey:
    N: int
    connectivity: str
    central_coupling: str
    J: float
    Jpm: float
    Jxx: float
    Jyy: float
    Jx_unscaled: float
    Jy_unscaled: float
    Jz: float
    Jzx: float
    Jcpm_unscaled: float
    hx: float
    hz: float


def _float(row: dict[str, Any], name: str, default: float = 0.0) -> float:
    value = row.get(name, "")
    if value in ("", None):
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _int(row: dict[str, Any], name: str, default: int = 0) -> int:
    value = row.get(name, "")
    if value in ("", None):
        return default
    try:
        return int(float(value))
    except ValueError:
        return default


def _key_from_row(row: dict[str, Any]) -> DetectorKey:
    return DetectorKey(
        N=_int(row, "N"),
        connectivity=row.get("connectivity") or "ring",
        central_coupling=row.get("central_coupling") or "all",
        J=_float(row, "J"),
        Jpm=_float(row, "Jpm"),
        Jxx=_float(row, "Jxx"),
        Jyy=_float(row, "Jyy"),
        Jx_unscaled=_float(row, "Jx_unscaled"),
        Jy_unscaled=_float(row, "Jy_unscaled"),
        Jz=_float(row, "Jz"),
        Jzx=_float(row, "Jzx"),
        Jcpm_unscaled=_float(row, "Jcpm_unscaled"),
        hx=_float(row, "hx"),
        hz=_float(row, "hz"),
    )


def detector_hamiltonian(key: DetectorKey) -> np.ndarray:
    n = key.N
    dim = 2**n
    H = np.zeros((dim, dim), dtype=np.complex128)
    Xs, Zs = build_pauli_operators(n)
    needs_y = key.Jpm != 0.0 or key.Jxx != 0.0 or key.Jyy != 0.0 or key.Jy_unscaled != 0.0 or key.Jcpm_unscaled != 0.0
    Ys = [build_pauli_y(i, n) for i in range(n)] if needs_y else None

    for i, j in _pixel_bonds(0, n, key.connectivity):
        H -= key.J * (Zs[i] @ Zs[j])
        if key.Jpm != 0.0:
            H -= key.Jpm * (Xs[i] @ Xs[j] + Ys[i] @ Ys[j]) / 2.0
        if key.Jxx != 0.0:
            H -= key.Jxx * (Xs[i] @ Xs[j])
        if key.Jyy != 0.0:
            H -= key.Jyy * (Ys[i] @ Ys[j])

    for i in range(n):
        if key.hx != 0.0:
            H -= key.hx * Xs[i]
        if key.hz != 0.0:
            H -= key.hz * Zs[i]
    return H


def detector_interaction_blocks(key: DetectorKey) -> list[np.ndarray]:
    n = key.N
    Xs, Zs = build_pauli_operators(n)
    needs_y = key.Jy_unscaled != 0.0 or key.Jcpm_unscaled != 0.0
    Ys = [build_pauli_y(i, n) for i in range(n)] if needs_y else None
    dim = 2**n
    scale = math.sqrt(max(n, 1))
    targets = _central_targets(0, n, key.connectivity, key.central_coupling)

    Bx = np.zeros((dim, dim), dtype=np.complex128)
    By = np.zeros((dim, dim), dtype=np.complex128)
    Bz = np.zeros((dim, dim), dtype=np.complex128)
    jx = key.Jx_unscaled / scale
    jy = key.Jy_unscaled / scale
    jcpm = key.Jcpm_unscaled / scale
    for i in targets:
        if jx != 0.0:
            Bx -= jx * Xs[i]
        if jy != 0.0:
            By -= jy * Ys[i]
        if key.Jz != 0.0:
            Bz -= key.Jz * Zs[i]
        if key.Jzx != 0.0:
            Bz -= key.Jzx * Xs[i]
        if jcpm != 0.0:
            Bx -= 0.5 * jcpm * Xs[i]
            By -= 0.5 * jcpm * Ys[i]
    return [B for B in (Bx, By, Bz) if np.linalg.norm(B) > 0.0]


def degeneracy_summary(E: np.ndarray, tol: float) -> tuple[float, int]:
    values = np.sort(np.asarray(E, dtype=float))
    if values.size == 0:
        return math.nan, 0
    clusters = []
    start = 0
    for idx in range(1, values.size):
        if abs(values[idx] - values[start]) > tol:
            clusters.append(idx - start)
            start = idx
    clusters.append(values.size - start)
    degenerate = sum(size for size in clusters if size > 1)
    return degenerate / values.size, max(clusters)


def degeneracy_clusters(E: np.ndarray, tol: float) -> list[np.ndarray]:
    """Return index sets of consecutive energy clusters within ``tol``.

    ``np.linalg.eigh`` returns ordered eigenvalues, so consecutive clustering is
    the appropriate detector-basis realization of the tolerance convention used
    by :func:`degeneracy_summary`.
    """

    values = np.asarray(E, dtype=float)
    if values.size == 0:
        return []
    clusters: list[np.ndarray] = []
    start = 0
    for idx in range(1, values.size):
        if abs(values[idx] - values[start]) > tol:
            clusters.append(np.arange(start, idx))
            start = idx
    clusters.append(np.arange(start, values.size))
    return clusters


def resonant_coupling_metrics(key: DetectorKey, tol: float) -> dict[str, float]:
    H_D = detector_hamiltonian(key)
    E, V = np.linalg.eigh(H_D)
    mask = np.abs(E[:, None] - E[None, :]) <= tol
    offdiag = ~np.eye(E.size, dtype=bool)
    deg_frac, max_mult = degeneracy_summary(E, tol)

    total = 0.0
    resonant = 0.0
    resonant_offdiag = 0.0
    diagonal = 0.0
    resonant_traceless = 0.0
    resonant_weights: list[np.ndarray] = []
    clusters = degeneracy_clusters(E, tol)
    for B in detector_interaction_blocks(key):
        B_eig = V.conj().T @ B @ V
        weights = np.abs(B_eig) ** 2
        total += float(weights.sum())
        resonant += float(weights[mask].sum())
        resonant_offdiag += float(weights[mask & offdiag].sum())
        diagonal += float(np.diag(weights).sum())
        resonant_weights.append(weights[mask])

        # Inside an exactly degenerate subspace, a scalar block only shifts the
        # common phase.  Its traceless part is the part that can resolve the
        # degeneracy and generate a non-atomic first-order kernel.
        for cluster in clusters:
            if cluster.size < 2:
                continue
            block = B_eig[np.ix_(cluster, cluster)]
            block -= np.eye(cluster.size, dtype=np.complex128) * np.trace(block) / cluster.size
            resonant_traceless += float(np.vdot(block, block).real)

    if total == 0.0:
        eta = eta_off = eta_diag = eta_traceless = math.nan
        resonant_effective_elements = math.nan
    else:
        eta = resonant / total
        eta_off = resonant_offdiag / total
        eta_diag = diagonal / total
        eta_traceless = resonant_traceless / total
        flat_resonant = np.concatenate(resonant_weights)
        if resonant == 0.0:
            resonant_effective_elements = 0.0
        else:
            probabilities = flat_resonant / resonant
            resonant_effective_elements = float(1.0 / np.square(probabilities).sum())
    return {
        "detector_degenerate_fraction": deg_frac,
        "detector_max_multiplicity": float(max_mult),
        "eta_res": eta,
        "eta_res_offdiag": eta_off,
        "eta_diag": eta_diag,
        "eta_res_traceless": eta_traceless,
        "resonant_effective_elements": resonant_effective_elements,
        "detector_dim": float(E.size),
    }


def load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                row["source_csv"] = str(path)
                if not row.get("S_born") and row.get("born_similarity"):
                    row["S_born"] = row["born_similarity"]
                rows.append(row)
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", type=Path, nargs="+", required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--min-n", type=int, default=0)
    parser.add_argument("--max-n", type=int, default=8)
    parser.add_argument("--top-rows", type=int, default=0, help="Limit to top S_born rows after max-n filtering; 0 keeps all.")
    parser.add_argument("--phi-min", type=float, default=None, help="Keep only rows with phi_uniformity_score at least this value.")
    parser.add_argument(
        "--require-nonzero-coupling",
        action="store_true",
        help="Drop rows whose detector interaction block has zero XX/YY/ZZ/ZX/+-. coupling.",
    )
    parser.add_argument("--energy-tol", type=float, default=1e-9)
    parser.add_argument(
        "--window-factor",
        type=float,
        default=1.0,
        help="Also compute eta_res_window with delta=max(energy_tol, window_factor/t).",
    )
    return parser.parse_args()


def _score(row: dict[str, Any]) -> float:
    return max(_float(row, "born_similarity", -math.inf), _float(row, "S_born", -math.inf))


def _interaction_weight(row: dict[str, Any]) -> float:
    return sum(
        abs(_float(row, name))
        for name in (
            "Jx_unscaled",
            "Jy_unscaled",
            "Jz",
            "Jzx",
            "Jcpm_unscaled",
        )
    )


def _prefixed(metrics: dict[str, float], prefix: str) -> dict[str, float]:
    return {f"{name}_{prefix}": value for name, value in metrics.items()}


def main() -> None:
    args = parse_args()
    rows = [
        row
        for row in load_rows(args.source_csv)
        if args.min_n <= _int(row, "N") <= args.max_n
    ]
    if args.phi_min is not None:
        rows = [
            row
            for row in rows
            if _float(row, "phi_uniformity_score", -math.inf) >= args.phi_min
        ]
    if args.require_nonzero_coupling:
        rows = [row for row in rows if _interaction_weight(row) > 0.0]
    rows.sort(key=_score, reverse=True)
    if args.top_rows > 0:
        rows = rows[: args.top_rows]

    cache: dict[tuple[DetectorKey, float], dict[str, float]] = {}
    out_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, 1):
        key = _key_from_row(row)
        exact_tol = float(args.energy_tol)
        t_value = _float(row, "t", 0.0)
        if t_value > 0.0 and args.window_factor > 0.0:
            window_tol = max(exact_tol, float(args.window_factor) / t_value)
        else:
            window_tol = exact_tol
        for tol in (exact_tol, window_tol):
            cache_key = (key, tol)
            if cache_key not in cache:
                print(
                    f"[{idx:04d}/{len(rows):04d}] N={key.N} J={key.J:g} Jpm={key.Jpm:g} "
                    f"Jx={key.Jx_unscaled:g} Jy={key.Jy_unscaled:g} tol={tol:g}",
                    flush=True,
                )
                cache[cache_key] = resonant_coupling_metrics(key, tol)
        merged = dict(row)
        exact = cache[(key, exact_tol)]
        window = cache[(key, window_tol)]
        for name, value in exact.items():
            merged[name] = value
        for name, value in _prefixed(exact, "exact").items():
            merged[name] = value
        for name, value in _prefixed(window, "window").items():
            merged[name] = value
        merged["eta_res_exact_tol"] = exact_tol
        merged["eta_res_window_tol"] = window_tol
        out_rows.append(merged)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    if not out_rows:
        args.out_csv.write_text("", encoding="utf-8")
        return
    fieldnames = list(out_rows[0].keys())
    for row in out_rows[1:]:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with args.out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Wrote {args.out_csv}")


if __name__ == "__main__":
    main()
