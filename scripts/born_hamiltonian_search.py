"""
Search single-pixel Hamiltonians for Born-like heavy-tailed angle data.

This is intentionally an exploratory script, not a package API.  It uses
the existing Hamiltonian generators, DisentanglementAnalyzer, and reusable
Born diagnostics to produce ranked CSV/JSON/Markdown search tables.

Example:

    python scripts/born_hamiltonian_search.py --N 10 --top 12
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import itertools
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.analysis import DisentanglementAnalyzer
from core.born import (
    born_ratio_from_radii,
    diagnostics_from_radii,
    phase_uniformity_from_eigenvalues,
)
from core.disorder import create_disorder_strategy
from core.hamiltonians.numpy_hamiltonians import (
    DimerizedPixelHamiltonianNumpy,
    SinglePixelHamiltonianNumpy,
    _pixel_bonds,
    _val,
)
from core.level_spacing import (
    compute_unfolded_spacings,
    mean_level_spacing_ratio,
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)
from core.pauli import build_pauli_operators, build_pauli_y


DISORDER_CHOICES = ("none", "uniform", "gaussian", "lorentzian")
DISORDER_STRENGTH_FIELDS = (
    "disorder_strength_J",
    "disorder_strength_Jpm",
    "disorder_strength_Jx",
    "disorder_strength_Jz",
    "disorder_strength_Jzx",
    "disorder_strength_Jcpm",
    "disorder_strength_hx",
    "disorder_strength_hz",
)
DEFAULT_PHI_BINS = 36


def _default_worker_count() -> int:
    """Default to explicit BORN_WORKERS, then PBS_NP, otherwise serial."""

    for name in ("BORN_WORKERS", "PBS_NP"):
        value = os.environ.get(name)
        if not value:
            continue
        try:
            return max(1, int(value))
        except ValueError:
            pass
    return 1


class TeeWriter:
    """Write progress output to both the terminal and a log file."""

    def __init__(self, *streams):
        self.streams = streams
        self._line_start = True

    def write(self, data: str) -> int:
        if data:
            chunks = data.splitlines(keepends=True)
            stamped = []
            for chunk in chunks:
                if self._line_start and chunk:
                    stamped.append(f"[{time.strftime('%Y-%m-%dT%H:%M:%S%z')}] ")
                stamped.append(chunk)
                self._line_start = chunk.endswith(("\n", "\r"))
            data_to_write = "".join(stamped)
        else:
            data_to_write = data
        for stream in self.streams:
            stream.write(data_to_write)
            stream.flush()
        return len(data)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


@dataclass(frozen=True)
class Candidate:
    model: str
    N: int
    J: float = 1.0
    Jpm: float = 0.0
    Jxx: float = 0.0
    Jyy: float = 0.0
    Jx_unscaled: float = 0.01
    Jy_unscaled: float = 0.0
    Jz: float = 0.0
    Jzx: float = 0.0
    Jcpm_unscaled: float = 0.0
    hx: float = 0.0
    hz: float = 0.1
    hz0_mode: str = "matched"
    connectivity: str = "ring"
    central_coupling: str = "auto"
    seed: int = 44
    disorder: str = "none"
    disorder_strength: float = 0.0
    disorder_strength_J: float = 0.0
    disorder_strength_Jpm: float = 0.0
    disorder_strength_Jx: float = 0.0
    disorder_strength_Jz: float = 0.0
    disorder_strength_Jzx: float = 0.0
    disorder_strength_Jcpm: float = 0.0
    disorder_strength_hx: float = 0.0
    disorder_strength_hz: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "disorder", _normalize_disorder(self.disorder))

    @property
    def N_pixel(self) -> int:
        return self.N - 1

    @property
    def Jx(self) -> float:
        return self.Jx_unscaled / math.sqrt(self.N_pixel)

    @property
    def Jy(self) -> float:
        return self.Jy_unscaled / math.sqrt(self.N_pixel)

    @property
    def Jcpm(self) -> float:
        return self.Jcpm_unscaled / math.sqrt(self.N_pixel)

    @property
    def hz0(self) -> float | None:
        if self.hz0_mode == "matched":
            return None
        if self.hz0_mode == "zero":
            return 0.0
        if self.hz0_mode == "half":
            return 0.5 * self.hz
        if self.hz0_mode == "minus":
            return -self.hz
        raise ValueError(f"Unknown hz0 mode: {self.hz0_mode!r}")


def _as_float_list(values: Iterable[str]) -> list[float]:
    return [float(v) for v in values]


def _normalize_disorder(disorder: str | None) -> str:
    if disorder is None:
        return "none"
    text = str(disorder).strip().lower()
    if text == "":
        return "none"
    if text not in DISORDER_CHOICES:
        raise ValueError(f"Unknown disorder {disorder!r}; choose one of {DISORDER_CHOICES}")
    return text


def _constructor_disorder(candidate: Candidate) -> str | None:
    return None if candidate.disorder == "none" else candidate.disorder


def _has_active_disorder(candidate: Candidate) -> bool:
    if candidate.disorder == "none":
        return False
    return any(abs(float(getattr(candidate, field))) > 0.0 for field in DISORDER_STRENGTH_FIELDS)


def _disorder_signature(candidate: Candidate | dict[str, Any]) -> str:
    get = candidate.get if isinstance(candidate, dict) else lambda key, default=None: getattr(candidate, key, default)
    disorder = _normalize_disorder(get("disorder", "none"))
    if disorder == "none":
        return "none"
    strengths = [
        ("J", float(get("disorder_strength_J", 0.0) or 0.0)),
        ("Jpm", float(get("disorder_strength_Jpm", 0.0) or 0.0)),
        ("Jx", float(get("disorder_strength_Jx", 0.0) or 0.0)),
        ("Jz", float(get("disorder_strength_Jz", 0.0) or 0.0)),
        ("Jzx", float(get("disorder_strength_Jzx", 0.0) or 0.0)),
        ("Jcpm", float(get("disorder_strength_Jcpm", 0.0) or 0.0)),
        ("hx", float(get("disorder_strength_hx", 0.0) or 0.0)),
        ("hz", float(get("disorder_strength_hz", 0.0) or 0.0)),
    ]
    active = [(name, value) for name, value in strengths if abs(value) > 0.0]
    if not active:
        return f"{disorder}:zero"
    values = {value for _name, value in active}
    if len(active) == len(strengths) and len(values) == 1:
        return f"{disorder}:all={active[0][1]:g}"
    return f"{disorder}:" + ",".join(f"{name}={value:g}" for name, value in active)


def _disorder_label_suffix(candidate: Candidate) -> str:
    if not _has_active_disorder(candidate):
        return ""
    signature = _disorder_signature(candidate)
    return "_dis-" + (
        signature.replace(":", "-")
        .replace(",", "_")
        .replace("=", "")
        .replace(".", "p")
        .replace("-", "m")
    )


def _strength_sweep(values: list[float] | None, fallback: float) -> list[float]:
    return list(values) if values is not None else [fallback]


def _candidate_label(candidate: Candidate) -> str:
    if candidate.model == "cnot_copier":
        return f"cnot_copier_N{candidate.N}"
    disorder_suffix = _disorder_label_suffix(candidate)
    if candidate.model == "dimerized_pixel":
        return (
            f"dimerized_pixel_N{candidate.N}"
            f"_cc-{candidate.central_coupling}"
            f"_J{candidate.J:g}_Jx{candidate.Jx_unscaled:g}"
            f"_hz{candidate.hz:g}_hz0-{candidate.hz0_mode}"
            f"_Jz{candidate.Jz:g}"
            f"{disorder_suffix}"
        )
    return (
        f"{candidate.model}_{candidate.connectivity}_N{candidate.N}"
        f"_cc-{candidate.central_coupling}"
        f"_J{candidate.J:g}_Jx{candidate.Jx_unscaled:g}_hz{candidate.hz:g}"
        f"_hz0-{candidate.hz0_mode}_Jpm{candidate.Jpm:g}"
        f"_Jxx{candidate.Jxx:g}_Jyy{candidate.Jyy:g}"
        f"_Jy{candidate.Jy_unscaled:g}_Jz{candidate.Jz:g}"
        f"_Jzx{candidate.Jzx:g}_Jcpm{candidate.Jcpm_unscaled:g}"
        f"{disorder_suffix}"
    )


def cnot_copier_unitary(N: int) -> np.ndarray:
    """Product of CNOT gates with central qubit 0 copied to all pixels."""
    if N < 2:
        raise ValueError("CNOT copier needs at least two qubits")
    D = 2**N
    U = np.zeros((D, D), dtype=np.complex128)
    for col in range(D):
        bits = [(col >> (N - 1 - q)) & 1 for q in range(N)]
        if bits[0]:
            for q in range(1, N):
                bits[q] ^= 1
        row = 0
        for q, bit in enumerate(bits):
            row |= bit << (N - 1 - q)
        U[row, col] = 1.0
    return U


def _make_single_pixel_hamiltonian(candidate: Candidate, backend: str):
    kwargs = dict(
        N_pixel=candidate.N_pixel,
        J=candidate.J,
        Jpm=candidate.Jpm,
        Jxx=candidate.Jxx,
        Jyy=candidate.Jyy,
        Jx=candidate.Jx,
        Jy=candidate.Jy,
        Jz=candidate.Jz,
        Jzx=candidate.Jzx,
        Jcpm=candidate.Jcpm,
        hx=candidate.hx,
        hz=candidate.hz,
        hz0=candidate.hz0,
        connectivity=candidate.connectivity,
        central_coupling=candidate.central_coupling,
        disorder=_constructor_disorder(candidate),
        disorder_strength=candidate.disorder_strength,
        disorder_strength_J=candidate.disorder_strength_J,
        disorder_strength_Jpm=candidate.disorder_strength_Jpm,
        disorder_strength_Jx=candidate.disorder_strength_Jx,
        disorder_strength_Jz=candidate.disorder_strength_Jz,
        disorder_strength_Jzx=candidate.disorder_strength_Jzx,
        disorder_strength_Jcpm=candidate.disorder_strength_Jcpm,
        disorder_strength_hx=candidate.disorder_strength_hx,
        disorder_strength_hz=candidate.disorder_strength_hz,
        seed=candidate.seed,
    )
    if backend == "quspin":
        from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

        return SinglePixelHamiltonianQuSpin(**kwargs, use_symmetry=True)
    return SinglePixelHamiltonianNumpy(**kwargs)


def _make_dimerized_pixel_hamiltonian(candidate: Candidate, backend: str):
    kwargs = dict(
        N_pixel=candidate.N_pixel,
        J=candidate.J,
        Jx=candidate.Jx,
        Jz=candidate.Jz,
        hx=candidate.hx,
        hz=candidate.hz,
        hz0=candidate.hz0,
        central_coupling=candidate.central_coupling if candidate.central_coupling != "auto" else "all",
        disorder=_constructor_disorder(candidate),
        disorder_strength=candidate.disorder_strength,
        disorder_strength_J=candidate.disorder_strength_J,
        disorder_strength_Jx=candidate.disorder_strength_Jx,
        disorder_strength_Jz=candidate.disorder_strength_Jz,
        disorder_strength_hx=candidate.disorder_strength_hx,
        disorder_strength_hz=candidate.disorder_strength_hz,
        seed=candidate.seed,
    )
    if backend == "quspin":
        from core.hamiltonians.quspin_hamiltonians import DimerizedPixelHamiltonianQuSpin

        return DimerizedPixelHamiltonianQuSpin(**kwargs, use_symmetry=True)
    return DimerizedPixelHamiltonianNumpy(**kwargs)


def _make_hamiltonian(candidate: Candidate, backend: str):
    if candidate.model == "single_pixel":
        return _make_single_pixel_hamiltonian(candidate, backend)
    if candidate.model == "dimerized_pixel":
        return _make_dimerized_pixel_hamiltonian(candidate, backend)
    raise ValueError(f"Unknown Hamiltonian model: {candidate.model!r}")


def energy_degeneracy_metrics(eigenvalues: np.ndarray, tol: float = 1e-9) -> dict[str, float]:
    """Measure unresolved eigenenergy multiplets before level-spacing collapse."""

    spectrum = np.sort(np.asarray(eigenvalues, dtype=np.complex128).real.ravel())
    spectrum = spectrum[np.isfinite(spectrum)]
    if spectrum.size == 0:
        return {
            "energy_level_count": 0.0,
            "energy_resolved_level_count": 0.0,
            "energy_degenerate_fraction": math.nan,
            "energy_degenerate_cluster_fraction": math.nan,
            "energy_max_multiplicity": 0.0,
            "energy_min_spacing": math.nan,
            "energy_mean_spacing_ratio": math.nan,
        }

    clusters: list[int] = []
    start = 0
    for idx in range(1, spectrum.size):
        if spectrum[idx] - spectrum[idx - 1] > tol:
            clusters.append(idx - start)
            start = idx
    clusters.append(spectrum.size - start)

    cluster_sizes = np.asarray(clusters, dtype=np.int64)
    degenerate_states = int(np.sum(cluster_sizes[cluster_sizes > 1]))
    degenerate_clusters = int(np.sum(cluster_sizes > 1))
    raw_spacings = np.diff(spectrum)
    positive_spacings = raw_spacings[raw_spacings > tol]
    min_spacing = float(np.min(positive_spacings)) if positive_spacings.size else math.nan

    return {
        "energy_level_count": float(spectrum.size),
        "energy_resolved_level_count": float(cluster_sizes.size),
        "energy_degenerate_fraction": float(degenerate_states / spectrum.size),
        "energy_degenerate_cluster_fraction": float(degenerate_clusters / cluster_sizes.size),
        "energy_max_multiplicity": float(np.max(cluster_sizes)),
        "energy_min_spacing": min_spacing,
        "energy_mean_spacing_ratio": mean_level_spacing_ratio(spectrum, tol=tol),
    }


def _energy_metrics_from_diagonalization(
    diagonalization: dict[str, Any],
    tol: float,
) -> dict[str, float]:
    if diagonalization["kind"] == "sectors":
        eigenvalues = np.concatenate([sector["E"] for sector in diagonalization["data"]])
        return energy_degeneracy_metrics(eigenvalues, tol=tol)
    if diagonalization["kind"] == "eigenbasis":
        eigenvalues, _vectors = diagonalization["data"]
        return energy_degeneracy_metrics(eigenvalues, tol=tol)
    return {
        "energy_level_count": math.nan,
        "energy_resolved_level_count": math.nan,
        "energy_degenerate_fraction": math.nan,
        "energy_degenerate_cluster_fraction": math.nan,
        "energy_max_multiplicity": math.nan,
        "energy_min_spacing": math.nan,
        "energy_mean_spacing_ratio": math.nan,
    }


def _sectors_use_symmetry(sectors: list[dict[str, Any]]) -> bool:
    return any(sec.get("symmetry_label", "full") != "full" for sec in sectors)


def _diagonalize_candidate(candidate: Candidate, backend: str) -> dict[str, Any]:
    start = time.time()
    if backend not in {"auto", "quspin", "numpy"}:
        raise ValueError(f"Unknown backend: {backend!r}")

    if candidate.model == "cnot_copier":
        return {
            "kind": "unitary",
            "backend": "unitary",
            "symmetry_used": False,
            "sector_count": 0,
            "fallback_reason": "",
            "data": cnot_copier_unitary(candidate.N),
            "wall_seconds": time.time() - start,
        }
    if candidate.model not in {"single_pixel", "dimerized_pixel"}:
        raise ValueError(f"Unknown model: {candidate.model!r}")

    if backend in {"auto", "quspin"}:
        try:
            ham = _make_hamiltonian(candidate, "quspin")
            sectors = ham.diagonalize_sectors()
            symmetry_used = _sectors_use_symmetry(sectors)
            return {
                "kind": "sectors",
                "backend": "quspin",
                "symmetry_used": symmetry_used,
                "sector_count": len(sectors),
                "fallback_reason": "",
                "data": sectors,
                "wall_seconds": time.time() - start,
            }
        except ImportError as exc:
            if backend == "quspin":
                raise
            fallback_reason = f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            if backend == "quspin":
                raise
            fallback_reason = f"{type(exc).__name__}: {exc}"
    else:
        fallback_reason = ""

    ham = _make_hamiltonian(candidate, "numpy")
    E, V = np.linalg.eigh(ham.generate())
    return {
        "kind": "eigenbasis",
        "backend": "numpy",
        "symmetry_used": False,
        "sector_count": 0,
        "fallback_reason": fallback_reason,
        "data": (E, V),
        "wall_seconds": time.time() - start,
    }


def _analyzer_from_diagonalization(diagonalization: dict[str, Any], t_value: float, N: int):
    if diagonalization["kind"] == "unitary":
        analyzer = DisentanglementAnalyzer(diagonalization["data"])
        analyzer.diagonalize_subblocks_product()
        return analyzer
    if diagonalization["kind"] == "sectors":
        return DisentanglementAnalyzer.from_sectors(
            diagonalization["data"], t_value, N
        )
    E, V = diagonalization["data"]
    return DisentanglementAnalyzer.from_eigenbasis(E, V, t_value)


def _angles_and_radii(analyzer: DisentanglementAnalyzer) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    radii = np.abs(analyzer.D0)
    theta0 = 2.0 * np.arctan(radii)
    theta1 = np.pi - theta0
    return theta0, theta1, radii


def _safe_plot_name(text: str) -> str:
    import re

    text = re.sub(r"[^A-Za-z0-9_.=-]+", "_", text)
    return text.strip("_")[:180]


def _theta_hist_and_ratio(
    radii: np.ndarray,
    bins: int,
    pseudocount: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    theta0 = 2.0 * np.arctan(radii)
    theta1 = np.pi - theta0
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2.0
    counts0, _ = np.histogram(theta0, bins=edges)
    counts1, _ = np.histogram(theta1, bins=edges)
    total = counts0 + counts1
    density0, _ = np.histogram(theta0, bins=edges, density=True)
    density1, _ = np.histogram(theta1, bins=edges, density=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw_ratio = np.where(total > 0, counts0 / total, np.nan)
    smooth_ratio = (counts0 + pseudocount) / (total + 2.0 * pseudocount)
    return centers, edges, density0, density1, raw_ratio, smooth_ratio, total


def _bloch_vectors_from_eigenvalues(eigenvalues: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lam = np.asarray(eigenvalues, dtype=np.complex128)
    finite = np.isfinite(lam.real) & np.isfinite(lam.imag)
    lam = lam[finite]
    r2 = np.abs(lam) ** 2
    denom = 1.0 + r2
    x0 = 2.0 * np.real(lam) / denom
    y0 = 2.0 * np.imag(lam) / denom
    z0 = (1.0 - r2) / denom
    v0 = np.column_stack([x0, y0, z0])
    return v0, -v0


def _downsample_indices(n_items: int, max_items: int) -> np.ndarray:
    if max_items <= 0 or n_items <= max_items:
        return np.arange(n_items)
    return np.linspace(0, n_items - 1, max_items, dtype=int)


def _plot_theta_mirror_panel(ax, radii: np.ndarray, bins: int, pseudocount: float) -> None:
    centers, edges, density0, density1, _raw_ratio, _smooth_ratio, _total = _theta_hist_and_ratio(
        radii,
        bins,
        pseudocount,
    )
    width = edges[1] - edges[0]
    ax.bar(centers, density0, width=width, color="#4C78A8", alpha=0.34, label=r"$P(\theta)$")
    ax.bar(centers, density1, width=width, color="#F58518", alpha=0.26, label=r"$P(\pi-\theta)$")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("density")
    ax.set_xlim(0.0, np.pi)
    ax.grid(alpha=0.18)
    ax.legend(fontsize=8)


def _plot_ratio_panel(ax, radii: np.ndarray, bins: int, pseudocount: float) -> None:
    centers, _edges, _density0, _density1, raw_ratio, smooth_ratio, total = _theta_hist_and_ratio(
        radii,
        bins,
        pseudocount,
    )
    theta_line = np.linspace(0.0, np.pi, 600)
    ax.plot(theta_line, np.cos(theta_line / 2.0) ** 2, "k--", lw=1.7, label=r"$\cos^2(\theta/2)$")
    mask = total > 0
    ax.plot(centers[mask], raw_ratio[mask], "o", ms=3.0, color="#54A24B", alpha=0.65, label="raw")
    ax.plot(centers, smooth_ratio, "-", lw=1.5, color="#B279A2", alpha=0.9, label=f"smoothed (+{pseudocount:g})")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel(r"$R(\theta)$")
    ax.set_xlim(0.0, np.pi)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.18)
    ax.legend(fontsize=8)


def _plot_bloch_sphere_panel(ax, eigenvalues: np.ndarray, max_points: int) -> None:
    v0, v1 = _bloch_vectors_from_eigenvalues(eigenvalues)
    if v0.size == 0:
        ax.text2D(0.5, 0.5, "no Bloch states", ha="center", va="center", transform=ax.transAxes)
        return

    u = np.linspace(0.0, 2.0 * np.pi, 48)
    v = np.linspace(0.0, np.pi, 24)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(xs, ys, zs, color="#9AA0A6", linewidth=0.35, alpha=0.25)

    idx = _downsample_indices(v0.shape[0], max_points)
    ax.scatter(v0[idx, 0], v0[idx, 1], v0[idx, 2], s=4, color="#4C78A8", alpha=0.30, label=r"$\phi_0$")
    ax.scatter(v1[idx, 0], v1[idx, 1], v1[idx, 2], s=4, color="#F58518", alpha=0.24, label=r"$\phi_1$")
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_zlim(-1.05, 1.05)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("Initial states on Bloch sphere", fontsize=10)
    ax.view_init(elev=22, azim=42)
    ax.legend(fontsize=8, loc="upper left")


def _energy_spectrum_from_diagonalization(diagonalization: dict[str, Any]) -> np.ndarray:
    """Return the full qubit-detector Hamiltonian spectrum represented by a diagonalization."""

    if diagonalization["kind"] == "sectors":
        if not diagonalization["data"]:
            return np.array([], dtype=float)
        eigenvalues = np.concatenate([sector["E"] for sector in diagonalization["data"]])
    elif diagonalization["kind"] == "eigenbasis":
        eigenvalues, _vectors = diagonalization["data"]
    else:
        eigenvalues = np.array([], dtype=float)

    spectrum = np.sort(np.asarray(eigenvalues, dtype=np.complex128).real.ravel())
    return spectrum[np.isfinite(spectrum)]


def _plot_energy_spectrum_panel(
    ax,
    diagonalization: dict[str, Any],
    bins: int,
    title: str = "Full Hamiltonian spectrum",
) -> None:
    spectrum = _energy_spectrum_from_diagonalization(diagonalization)
    _plot_spectrum_histogram_panel(ax, spectrum, bins, title)


def _plot_spectrum_histogram_panel(ax, spectrum: np.ndarray, bins: int, title: str) -> None:
    if spectrum.size == 0:
        ax.text(0.5, 0.5, f"{title}\nnot available", ha="center", va="center")
        ax.set_axis_off()
        return

    spread = float(np.ptp(spectrum))
    if spread <= 1e-12:
        ax.axvline(float(spectrum[0]), color="#4C78A8", lw=2.0)
        ax.text(
            0.5,
            0.86,
            f"{spectrum.size} levels at one energy",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=8,
        )
        ax.set_ylim(0.0, 1.0)
    else:
        hist_bins = max(20, min(120, bins))
        ax.hist(spectrum, bins=hist_bins, density=True, color="#4C78A8", alpha=0.55)
        if spectrum.size <= 4096:
            ymin, ymax = ax.get_ylim()
            ax.plot(spectrum, np.full_like(spectrum, ymin), "|", color="#1F2937", ms=4, alpha=0.25)
            ax.set_ylim(ymin, ymax)

    ax.set_title(title, fontsize=10)
    ax.set_xlabel(r"energy $E$")
    ax.set_ylabel("density")
    ax.grid(alpha=0.18)


def _detector_disorder(candidate: Candidate):
    return None if candidate.disorder == "none" else create_disorder_strategy(candidate.disorder)


def _detector_hamiltonian_numpy(candidate: Candidate) -> np.ndarray:
    if candidate.model not in {"single_pixel", "dimerized_pixel"}:
        return np.array([], dtype=float)

    n_pixel = candidate.N_pixel
    dim = 2**n_pixel
    H = np.zeros((dim, dim), dtype=np.complex128)
    Xs, Zs = build_pauli_operators(n_pixel)

    if candidate.seed is not None:
        np.random.seed(candidate.seed)
    disorder = _detector_disorder(candidate)

    if candidate.model == "dimerized_pixel":
        pixel_bonds = [(2 * k, 2 * k + 1) for k in range(n_pixel // 2)]
    else:
        pixel_bonds = _pixel_bonds(0, n_pixel, candidate.connectivity)

    for i, j in pixel_bonds:
        j_val = _val(disorder, candidate.J, candidate.disorder_strength_J)
        H -= j_val * (Zs[i] @ Zs[j])

    needs_y = (
        candidate.model == "single_pixel"
        and (
            candidate.Jpm != 0.0
            or candidate.Jxx != 0.0
            or candidate.Jyy != 0.0
            or (
                disorder is not None
                and candidate.disorder_strength_Jpm != 0.0
            )
        )
    )
    Ys = [build_pauli_y(i, n_pixel) for i in range(n_pixel)] if needs_y else None

    if candidate.model == "single_pixel":
        if candidate.Jpm != 0.0 or (disorder is not None and candidate.disorder_strength_Jpm != 0.0):
            for i, j in pixel_bonds:
                jpm = _val(disorder, candidate.Jpm, candidate.disorder_strength_Jpm)
                H -= jpm * (Xs[i] @ Xs[j] + Ys[i] @ Ys[j]) / 2.0
        if candidate.Jxx != 0.0:
            for i, j in pixel_bonds:
                H -= candidate.Jxx * (Xs[i] @ Xs[j])
        if candidate.Jyy != 0.0:
            for i, j in pixel_bonds:
                H -= candidate.Jyy * (Ys[i] @ Ys[j])

    for i in range(n_pixel):
        hx_val = _val(disorder, candidate.hx, candidate.disorder_strength_hx)
        hz_val = _val(disorder, candidate.hz, candidate.disorder_strength_hz)
        H -= hx_val * Xs[i]
        H -= hz_val * Zs[i]

    return np.real_if_close(H)


def _detector_spectrum_from_candidate(
    candidate: Candidate,
    max_dense_qubits: int,
) -> np.ndarray:
    if max_dense_qubits < 0:
        max_dense_qubits = candidate.N_pixel
    if candidate.N_pixel <= max_dense_qubits:
        try:
            H_detector = _detector_hamiltonian_numpy(candidate)
            if H_detector.size == 0:
                return np.array([], dtype=float)
            spectrum = np.linalg.eigvalsh(H_detector)
        except Exception:
            spectrum = np.array([], dtype=float)
        if np.asarray(spectrum).size:
            spectrum = np.sort(np.asarray(spectrum, dtype=np.complex128).real.ravel())
            return spectrum[np.isfinite(spectrum)]

    spectrum = _detector_spectrum_quspin(candidate)
    if spectrum.size == 0:
        return np.array([], dtype=float)
    spectrum = np.sort(np.asarray(spectrum, dtype=np.complex128).real.ravel())
    return spectrum[np.isfinite(spectrum)]


def _detector_conserves_sz(candidate: Candidate) -> bool:
    if candidate.hx != 0.0 or candidate.disorder_strength_hx != 0.0:
        return False
    if candidate.model == "dimerized_pixel":
        return True
    if candidate.Jxx != candidate.Jyy:
        return False
    return True


def _detector_static_quspin(candidate: Candidate) -> tuple[list, int] | None:
    if candidate.model not in {"single_pixel", "dimerized_pixel"}:
        return None

    n_pixel = candidate.N_pixel
    if candidate.seed is not None:
        np.random.seed(candidate.seed)
    disorder = _detector_disorder(candidate)
    if candidate.model == "dimerized_pixel":
        bonds = [(2 * k, 2 * k + 1) for k in range(n_pixel // 2)]
    else:
        bonds = _pixel_bonds(0, n_pixel, candidate.connectivity)

    pixel_zz = [
        [-_val(disorder, candidate.J, candidate.disorder_strength_J), i, j]
        for i, j in bonds
    ]
    static: list = [["zz", pixel_zz]]

    if candidate.model == "single_pixel":
        if candidate.Jxx != 0.0:
            static.append(["xx", [[-candidate.Jxx, i, j] for i, j in bonds]])
        if candidate.Jyy != 0.0:
            static.append(["yy", [[-candidate.Jyy, i, j] for i, j in bonds]])
        pm_list = []
        for i, j in bonds:
            jpm = _val(disorder, candidate.Jpm, candidate.disorder_strength_Jpm)
            if jpm != 0.0:
                pm_list.append([-jpm / 4.0, i, j])
        if pm_list:
            static.append(["+-", pm_list])
            static.append(["-+", pm_list])

    hx_list = [
        [-_val(disorder, candidate.hx, candidate.disorder_strength_hx), i]
        for i in range(n_pixel)
    ]
    hz_list = [
        [-_val(disorder, candidate.hz, candidate.disorder_strength_hz), i]
        for i in range(n_pixel)
    ]
    if any(value != 0.0 for value, _site in hx_list):
        static.append(["x", hx_list])
    if any(value != 0.0 for value, _site in hz_list):
        static.append(["z", hz_list])
    return static, n_pixel


def _detector_spectrum_quspin(candidate: Candidate) -> np.ndarray:
    try:
        from quspin.basis import spin_basis_1d
        from quspin.operators import hamiltonian
    except ImportError:
        return np.array([], dtype=float)

    static_and_n = _detector_static_quspin(candidate)
    if static_and_n is None:
        return np.array([], dtype=float)
    static, n_pixel = static_and_n
    clean = not _has_active_disorder(candidate)
    conserves_sz = _detector_conserves_sz(candidate)

    bases = []
    if clean and candidate.connectivity in {"ring", "all_to_all"} and n_pixel > 1:
        if conserves_sz:
            for n_up in range(n_pixel + 1):
                for k_block in range(n_pixel):
                    bases.append(spin_basis_1d(n_pixel, Nup=n_up, kblock=k_block))
        else:
            for k_block in range(n_pixel):
                bases.append(spin_basis_1d(n_pixel, kblock=k_block))
    elif conserves_sz:
        bases = [spin_basis_1d(n_pixel, Nup=n_up) for n_up in range(n_pixel + 1)]
    else:
        return np.array([], dtype=float)

    spectra: list[np.ndarray] = []
    try:
        for basis in bases:
            if basis.Ns == 0:
                continue
            H = hamiltonian(
                static,
                [],
                basis=basis,
                dtype=np.complex128,
                check_symm=False,
                check_herm=False,
            )
            spectra.append(np.linalg.eigvalsh(H.toarray()))
    except Exception:
        return np.array([], dtype=float)
    if not spectra:
        return np.array([], dtype=float)
    return np.concatenate(spectra)


def _plot_level_spacing_panel(
    ax,
    spectrum: np.ndarray,
    bins: int,
    title: str,
    tol: float = 1e-9,
) -> None:
    spacings = compute_unfolded_spacings(spectrum, tol=tol, degree=3, trim_fraction=0.1)
    spacings = spacings[np.isfinite(spacings)]
    if spacings.size < 3 or float(np.ptp(spacings)) <= 1e-12:
        ax.text(
            0.5,
            0.5,
            f"{title}\ninsufficient resolved spacings",
            ha="center",
            va="center",
        )
        ax.set_axis_off()
        return

    hist_bins = max(3, min(80, int(bins), int(spacings.size), int(np.sqrt(spacings.size)) + 1))
    ax.hist(spacings, bins=hist_bins, density=True, alpha=0.52, color="#4C78A8", label="data")
    x_max = max(4.0, float(np.percentile(spacings, 99.0)))
    s = np.linspace(0.0, x_max, 500)
    ax.plot(s, poisson_spacing_distribution(s), color="#54A24B", lw=1.4, label="Poisson")
    ax.plot(s, wigner_spacing_distribution(s, 1), color="#E45756", lw=1.4, label="GOE")
    ax.plot(s, wigner_spacing_distribution(s, 2), color="#B279A2", lw=1.4, label="GUE")
    ax.set_xlim(0.0, x_max)
    ax.set_xlabel(r"unfolded spacing $s$")
    ax.set_ylabel("density")
    ax.set_title(title, fontsize=10)
    ax.grid(alpha=0.18)
    ax.legend(fontsize=7)


def _plot_phi_histogram_panel(ax, eigenvalues: np.ndarray, bins: int = DEFAULT_PHI_BINS) -> None:
    phase = phase_uniformity_from_eigenvalues(eigenvalues, n_phi=bins, include_antipodes=True)
    if phase.n_samples == 0:
        ax.text(0.5, 0.5, "no phi angles", ha="center", va="center")
        ax.set_axis_off()
        return
    centers = (phase.bin_edges[:-1] + phase.bin_edges[1:]) / 2.0
    width = phase.bin_edges[1] - phase.bin_edges[0]
    density = phase.counts / (phase.n_samples * width)
    ax.bar(centers, density, width=width, color="#4C78A8", alpha=0.65)
    ax.axhline(1.0 / (2.0 * np.pi), color="#E45756", ls="--", lw=1.2, label="uniform")
    ax.set_xlim(0.0, 2.0 * np.pi)
    ax.set_xlabel(r"Bloch azimuth $\phi$")
    ax.set_ylabel("density")
    ax.set_title(
        f"phi coverage, U={phase.uniformity_score:.3f}",
        fontsize=10,
    )
    ax.grid(alpha=0.18)
    ax.legend(fontsize=8)


def _plot_radius_tail_panel(ax, radii: np.ndarray, tail_fraction: float, n_log_bins: int) -> None:
    x = np.asarray(radii, dtype=float)
    x = np.sort(x[np.isfinite(x) & (x > 0)])
    if x.size == 0:
        ax.text(0.5, 0.5, "no positive radii", ha="center", va="center")
        return
    survival = np.arange(x.size, 0, -1) / x.size
    tail = diagnostics_from_radii(x, tail_fraction=tail_fraction, n_log_bins=n_log_bins)
    ax.loglog(x, survival, ".", ms=2.5, alpha=0.55, color="#4C78A8")
    ax.set_xlabel(r"$x=|\lambda|$")
    ax.set_ylabel(r"$P(X\geq x)$")
    ax.set_title(rf"radius tail, $\alpha={tail.tail_density_exponent:.3f}$", fontsize=10)
    ax.grid(alpha=0.2, which="both")


def _candidate_from_result(result: dict[str, Any]) -> Candidate:
    cand = result["candidate"]
    fields = Candidate.__dataclass_fields__
    return Candidate(**{key: cand[key] for key in fields if key in cand})


def _result_plot_signature(result: dict[str, Any]) -> str:
    cand = result["candidate"]
    return (
        f"{cand['model']} {cand['connectivity']} N={cand['N']} cc={cand['central_coupling']} "
        f"hz0={cand['hz0_mode']} dis={_disorder_signature(cand)} "
        f"J={cand['J']:g} Jx={cand['Jx_unscaled']:g} Jy={cand['Jy_unscaled']:g} hz={cand['hz']:g} "
        f"Jpm={cand['Jpm']:g} Jxx={cand['Jxx']:g} Jyy={cand['Jyy']:g} "
        f"Jz={cand['Jz']:g} Jzx={cand['Jzx']:g} Jcpm={cand['Jcpm_unscaled']:g} "
        f"t={result['t']:g}"
    )


def plot_result_diagnostics(
    result: dict[str, Any],
    out_dir: Path,
    bins: int,
    tail_fraction: float,
    n_log_bins: int,
    backend: str,
    pseudocount: float,
    max_bloch_points: int,
    max_detector_spectrum_qubits: int,
    include_spectra: bool = True,
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    candidate = _candidate_from_result(result)
    t_value = float(result["t"])
    diagonalization = _diagonalize_candidate(candidate, backend)
    analyzer = _analyzer_from_diagonalization(diagonalization, t_value, candidate.N)
    _theta0, _theta1, radii = _angles_and_radii(analyzer)
    ratio = born_ratio_from_radii(radii, n_theta=bins)
    full_spectrum = np.array([], dtype=float)
    detector_spectrum = np.array([], dtype=float)
    if include_spectra:
        full_spectrum = _energy_spectrum_from_diagonalization(diagonalization)
        detector_spectrum = _detector_spectrum_from_candidate(
            candidate,
            max_dense_qubits=max_detector_spectrum_qubits,
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(19.0, 13.0), dpi=160)
    gs = fig.add_gridspec(3, 4)
    ax_theta = fig.add_subplot(gs[0, 0])
    ax_ratio = fig.add_subplot(gs[0, 1])
    ax_tail = fig.add_subplot(gs[0, 2])
    ax_phi = fig.add_subplot(gs[0, 3])
    ax_bloch = fig.add_subplot(gs[1, 0], projection="3d")
    ax_full_spectrum = fig.add_subplot(gs[1, 1])
    ax_detector_spectrum = fig.add_subplot(gs[1, 2])
    ax_summary = fig.add_subplot(gs[1, 3])
    ax_full_spacing = fig.add_subplot(gs[2, 0:2])
    ax_detector_spacing = fig.add_subplot(gs[2, 2:4])

    _plot_theta_mirror_panel(ax_theta, radii, bins, pseudocount)
    _plot_ratio_panel(ax_ratio, radii, bins, pseudocount)
    _plot_radius_tail_panel(ax_tail, radii, tail_fraction, n_log_bins)
    _plot_phi_histogram_panel(ax_phi, analyzer.D0, DEFAULT_PHI_BINS)
    _plot_bloch_sphere_panel(ax_bloch, analyzer.D0, max_bloch_points)
    if include_spectra:
        _plot_spectrum_histogram_panel(ax_full_spectrum, full_spectrum, bins, "Full Hamiltonian spectrum")
        _plot_spectrum_histogram_panel(ax_detector_spectrum, detector_spectrum, bins, "Detector spectrum")
        _plot_level_spacing_panel(ax_full_spacing, full_spectrum, bins, "Full unfolded spacings")
        _plot_level_spacing_panel(ax_detector_spacing, detector_spectrum, bins, "Detector unfolded spacings")
    else:
        for ax, title in (
            (ax_full_spectrum, "Full Hamiltonian spectrum"),
            (ax_detector_spectrum, "Detector spectrum"),
            (ax_full_spacing, "Full unfolded spacings"),
            (ax_detector_spacing, "Detector unfolded spacings"),
        ):
            ax.axis("off")
            ax.text(
                0.5,
                0.5,
                "disabled\nuse --diagnostic-spectra to include",
                ha="center",
                va="center",
                fontsize=10,
                transform=ax.transAxes,
            )
            ax.set_title(title)
    ax_summary.axis("off")

    metrics = result["metrics"]
    summary_lines = [
        _result_plot_signature(result),
        "",
        f"S_born={ratio.similarity:.4f}",
        f"mean abs ratio error={ratio.mean_abs_error:.4f}",
        f"tail alpha={metrics['tail_density_exponent']:.3f}",
        f"reciprocity={metrics['reciprocity_error']:.3f}",
        f"atom fraction={metrics['radius_atomic_fraction']:.4f}",
        f"phi uniformity={metrics.get('phi_uniformity_score', math.nan):.3f}",
        f"phi entropy={metrics.get('phi_entropy_score', math.nan):.3f}",
        f"phi max bin={metrics.get('phi_max_bin_fraction', math.nan):.3f}",
        f"q99/q50={metrics['radius_q99_over_q50']:.2f}",
        f"E deg frac={metrics['energy_degenerate_fraction']:.3f}",
        f"E max mult={metrics['energy_max_multiplicity']:.0f}",
        (
            f"detector levels plotted={detector_spectrum.size}"
            if include_spectra
            else "spectral panels=disabled"
        ),
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
        fontsize=9.5,
        family="monospace",
        wrap=True,
    )

    fig.suptitle("Born-rule diagnostic evidence from simulation", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    filename = _safe_plot_name(f"{result['label']}_t{t_value:g}_born_diagnostics.png")
    out_path = out_dir / filename
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def write_diagnostic_index(path: Path, plotted: list[dict[str, Any]], include_spectra: bool = True) -> None:
    panel_text = (
        "Panels show \\(P(\\theta)\\) and \\(P(\\pi-\\theta)\\), the ratio \\(R(\\theta)\\) compared with \\(\\cos^2(\\theta/2)\\), the radius tail, phi-angle coverage, the associated initial-state distribution on the Bloch sphere, full and detector Hamiltonian spectra, and unfolded level-spacing histograms."
        if include_spectra
        else "Panels show \\(P(\\theta)\\) and \\(P(\\pi-\\theta)\\), the ratio \\(R(\\theta)\\) compared with \\(\\cos^2(\\theta/2)\\), the radius tail, phi-angle coverage, and the associated initial-state distribution on the Bloch sphere. Spectrum and level-spacing panels were disabled for this run."
    )
    lines = [
        "# Simulation-Time Born Diagnostic Figures",
        "",
        "Each figure is generated by `scripts/born_hamiltonian_search.py` during the simulation run.",
        panel_text,
        "",
        "| rank | S | phi U | alpha | recip | atom | q99/q50 | figure | signature |",
        "|---:|---:|---:|---:|---:|---:|---:|:---|:---|",
    ]
    for rank, item in enumerate(plotted, 1):
        rel = Path(item["path"]).name
        lines.append(
            "| {rank} | {S:.4f} | {phi:.3f} | {alpha:.3f} | {recip:.3f} | {atom:.3f} | {spread:.2f} | [{name}]({name}) | {sig} |".format(
                rank=rank,
                S=item["born_similarity"],
                phi=item["phi_uniformity_score"],
                alpha=item["tail_density_exponent"],
                recip=item["reciprocity_error"],
                atom=item["radius_atomic_fraction"],
                spread=item["radius_q99_over_q50"],
                name=rel,
                sig=item["signature"].replace("|", "-"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_top_results(args: argparse.Namespace, results: list[dict[str, Any]]) -> None:
    if args.plot_top <= 0:
        return
    plot_dir = args.plot_dir or (args.out_dir / "diagnostics")
    selected = results[: args.plot_top]
    plotted: list[dict[str, Any]] = []
    print(f"Plotting {len(selected)} top simulation diagnostics to {plot_dir}")
    for idx, result in enumerate(selected, 1):
        print(f"[plot {idx:03d}/{len(selected):03d}] {_result_plot_signature(result)}")
        path = plot_result_diagnostics(
            result,
            out_dir=plot_dir,
            bins=args.bins,
            tail_fraction=args.tail_fraction,
            n_log_bins=args.log_bins,
            backend=args.backend,
            pseudocount=args.plot_pseudocount,
            max_bloch_points=args.plot_max_bloch_points,
            max_detector_spectrum_qubits=args.max_detector_spectrum_qubits,
            include_spectra=args.diagnostic_spectra,
        )
        result["diagnostic_figure"] = str(path)
        metrics = result["metrics"]
        plotted.append(
            {
                "path": str(path),
                "signature": _result_plot_signature(result),
                "born_similarity": metrics["born_similarity"],
                "phi_uniformity_score": metrics["phi_uniformity_score"],
                "tail_density_exponent": metrics["tail_density_exponent"],
                "reciprocity_error": metrics["reciprocity_error"],
                "radius_atomic_fraction": metrics["radius_atomic_fraction"],
                "radius_q99_over_q50": metrics["radius_q99_over_q50"],
            }
        )
    index_path = plot_dir / "index.md"
    write_diagnostic_index(index_path, plotted, include_spectra=args.diagnostic_spectra)
    print(f"Wrote {index_path}")


def heavy_tail_metrics(theta0: np.ndarray, radii: np.ndarray) -> dict[str, float]:
    theta_q50, theta_q90, theta_q95, theta_q99 = np.quantile(
        theta0, [0.50, 0.90, 0.95, 0.99]
    )
    radius_q50, radius_q90, radius_q95, radius_q99 = np.quantile(
        radii, [0.50, 0.90, 0.95, 0.99]
    )
    rounded = np.round(radii[np.isfinite(radii)], decimals=12)
    unique_count = len(np.unique(rounded)) if rounded.size else 0
    atomic_fraction = 0.0
    if rounded.size:
        _, counts = np.unique(rounded, return_counts=True)
        atomic_fraction = float(np.max(counts) / rounded.size)
    return {
        "theta_mean": float(np.mean(theta0)),
        "theta_std": float(np.std(theta0)),
        "theta_q50": float(theta_q50),
        "theta_q90": float(theta_q90),
        "theta_q95": float(theta_q95),
        "theta_q99": float(theta_q99),
        "theta_mass_gt_0p3": float(np.mean(theta0 > 0.3)),
        "theta_mass_gt_0p5": float(np.mean(theta0 > 0.5)),
        "theta_mass_gt_1p0": float(np.mean(theta0 > 1.0)),
        "radius_q50": float(radius_q50),
        "radius_q90": float(radius_q90),
        "radius_q95": float(radius_q95),
        "radius_q99": float(radius_q99),
        "radius_q99_over_q50": float(radius_q99 / radius_q50) if radius_q50 > 0.0 else np.inf,
        "radius_unique_count": float(unique_count),
        "radius_atomic_fraction": atomic_fraction,
        "radius_zero_fraction": float(np.mean(np.isclose(radii, 0.0))),
        "radius_positive_fraction": float(np.mean(radii > 0.0)),
    }


def objective_score(metrics: dict[str, float]) -> float:
    similarity = metrics["born_similarity"]
    density_exponent = metrics["tail_density_exponent"]
    tail_score = (
        math.exp(-abs(density_exponent - 2.0))
        if math.isfinite(density_exponent)
        else 0.0
    )
    reciprocity = metrics["reciprocity_error"]
    reciprocity_score = math.exp(-reciprocity) if math.isfinite(reciprocity) else 0.0

    spread = metrics["radius_q99_over_q50"]
    spread_score = 0.0
    if math.isfinite(spread) and spread > 0.0:
        spread_score = min(1.0, math.log1p(spread) / math.log(100.0))

    mass_score = min(1.0, metrics["theta_mass_gt_0p5"] / 0.20)
    phi_score = metrics.get("phi_uniformity_score", 0.0)
    if not math.isfinite(phi_score):
        phi_score = 0.0

    return (
        0.57 * similarity
        + 0.18 * tail_score
        + 0.10 * reciprocity_score
        + 0.07 * phi_score
        + 0.05 * spread_score
        + 0.03 * mass_score
    )


def evaluate_candidate(
    candidate: Candidate,
    times: Iterable[float],
    n_bins: int,
    backend: str,
    tail_fraction: float,
    n_log_bins: int,
    energy_degeneracy_tol: float,
) -> list[dict[str, Any]]:
    diagonalization = _diagonalize_candidate(candidate, backend)
    energy_metrics = _energy_metrics_from_diagonalization(
        diagonalization,
        tol=energy_degeneracy_tol,
    )
    results: list[dict[str, Any]] = []
    for t_value in times:
        start = time.time()
        analyzer = _analyzer_from_diagonalization(diagonalization, t_value, candidate.N)
        theta0, theta1, radii = _angles_and_radii(analyzer)
        core = diagnostics_from_radii(
            radii,
            n_theta=n_bins,
            tail_fraction=tail_fraction,
            n_log_bins=n_log_bins,
        )
        metrics = asdict(core)
        metrics.update(heavy_tail_metrics(theta0, radii))
        phase = phase_uniformity_from_eigenvalues(
            analyzer.D0,
            n_phi=DEFAULT_PHI_BINS,
            include_antipodes=True,
        )
        metrics.update(
            {
                "phi_uniformity_score": float(phase.uniformity_score),
                "phi_entropy_score": float(phase.entropy_score),
                "phi_total_variation": float(phase.total_variation),
                "phi_max_bin_fraction": float(phase.max_bin_fraction),
                "phi_rayleigh_r": float(phase.rayleigh_r),
                "phi_sample_count": float(phase.n_samples),
                "phi_bin_count": float(phase.n_bins),
            }
        )
        metrics.update(energy_metrics)
        metrics["objective_score"] = objective_score(metrics)
        metrics["analysis_wall_seconds"] = time.time() - start
        metrics["diagonalization_wall_seconds"] = diagonalization["wall_seconds"]

        row = {
            "label": _candidate_label(candidate),
            "backend": diagonalization["backend"],
            "diagonalization_kind": diagonalization["kind"],
            "symmetry_used": diagonalization["symmetry_used"],
            "sector_count": diagonalization["sector_count"],
            "fallback_reason": diagonalization["fallback_reason"],
            "t": float(t_value),
            "candidate": asdict(candidate) | {
                "N_pixel": candidate.N_pixel,
                "Jx_scaled": candidate.Jx,
                "Jy_scaled": candidate.Jy,
                "Jcpm_scaled": candidate.Jcpm,
                "hz0": candidate.hz0,
            },
            "metrics": metrics,
        }
        results.append(row)
    return results


def _evaluate_candidate_job(payload: tuple[Candidate, list[float], int, str, float, int, float]) -> list[dict[str, Any]]:
    candidate, times, n_bins, backend, tail_fraction, n_log_bins, energy_degeneracy_tol = payload
    return evaluate_candidate(
        candidate,
        times,
        n_bins,
        backend,
        tail_fraction,
        n_log_bins,
        energy_degeneracy_tol,
    )


def generate_candidates(args: argparse.Namespace) -> list[Candidate]:
    candidates = []
    if args.model == "cnot_copier":
        return [
            Candidate(model=args.model, N=N, connectivity=args.connectivity, seed=args.seed)
            for N in args.N
        ]

    disorder = _normalize_disorder(getattr(args, "disorder", "none"))
    disorder_strength = float(getattr(args, "disorder_strength", 0.0))
    disorder_strength_args = {
        "disorder_strength_J": getattr(args, "disorder_strength_J", None),
        "disorder_strength_Jpm": getattr(args, "disorder_strength_Jpm", None),
        "disorder_strength_Jx": getattr(args, "disorder_strength_Jx", None),
        "disorder_strength_Jz": getattr(args, "disorder_strength_Jz", None),
        "disorder_strength_Jzx": getattr(args, "disorder_strength_Jzx", None),
        "disorder_strength_Jcpm": getattr(args, "disorder_strength_Jcpm", None),
        "disorder_strength_hx": getattr(args, "disorder_strength_hx", None),
        "disorder_strength_hz": getattr(args, "disorder_strength_hz", None),
    }
    if disorder == "none":
        strength_sweeps = {field: [0.0] for field in DISORDER_STRENGTH_FIELDS}
    else:
        strength_sweeps = {
            field: _strength_sweep(values, disorder_strength)
            for field, values in disorder_strength_args.items()
        }

    if args.model == "dimerized_pixel":
        unsupported = {
            "Jpm": args.Jpm,
            "Jxx": args.Jxx,
            "Jyy": args.Jyy,
            "jy_unscaled": args.jy_unscaled,
            "Jzx": args.Jzx,
            "jcpm_unscaled": args.jcpm_unscaled,
        }
        nonzero = [
            name
            for name, values in unsupported.items()
            if any(abs(float(value)) > 0.0 for value in values)
        ]
        if nonzero:
            raise ValueError(
                "dimerized_pixel supports only J, Jx, Jz, hx, hz, and hz0; "
                f"nonzero unsupported channels: {', '.join(nonzero)}"
            )
        unsupported_disorder = {
            "disorder_strength_Jpm": disorder_strength_args["disorder_strength_Jpm"],
            "disorder_strength_Jzx": disorder_strength_args["disorder_strength_Jzx"],
            "disorder_strength_Jcpm": disorder_strength_args["disorder_strength_Jcpm"],
        }
        nonzero_disorder = [
            name
            for name, values in unsupported_disorder.items()
            if values is not None and any(abs(float(value)) > 0.0 for value in values)
        ]
        if nonzero_disorder:
            raise ValueError(
                "dimerized_pixel disorder supports only J, Jx, Jz, hx, and hz; "
                f"nonzero unsupported disorder channels: {', '.join(nonzero_disorder)}"
            )
        strength_sweeps["disorder_strength_Jpm"] = [0.0]
        strength_sweeps["disorder_strength_Jzx"] = [0.0]
        strength_sweeps["disorder_strength_Jcpm"] = [0.0]
        odd_pixel = [N for N in args.N if (N - 1) % 2 != 0]
        if odd_pixel:
            raise ValueError(
                "dimerized_pixel requires even N_pixel=N-1; invalid total N: "
                + ", ".join(str(N) for N in odd_pixel)
            )

    for (
        N,
        Jpm,
        Jxx,
        Jyy,
        Jx,
        Jy,
        Jz,
        Jzx,
        Jcpm,
        hx,
        hz,
        hz0_mode,
        central_coupling,
        disorder_strength_J,
        disorder_strength_Jpm,
        disorder_strength_Jx,
        disorder_strength_Jz,
        disorder_strength_Jzx,
        disorder_strength_Jcpm,
        disorder_strength_hx,
        disorder_strength_hz,
    ) in itertools.product(
        args.N,
        args.Jpm,
        args.Jxx,
        args.Jyy,
        args.jx_unscaled,
        args.jy_unscaled,
        args.Jz,
        args.Jzx,
        args.jcpm_unscaled,
        args.hx,
        args.hz,
        args.hz0_modes,
        args.central_coupling,
        strength_sweeps["disorder_strength_J"],
        strength_sweeps["disorder_strength_Jpm"],
        strength_sweeps["disorder_strength_Jx"],
        strength_sweeps["disorder_strength_Jz"],
        strength_sweeps["disorder_strength_Jzx"],
        strength_sweeps["disorder_strength_Jcpm"],
        strength_sweeps["disorder_strength_hx"],
        strength_sweeps["disorder_strength_hz"],
    ):
        candidates.append(
            Candidate(
                model=args.model,
                N=N,
                J=args.J,
                Jpm=Jpm,
                Jxx=Jxx,
                Jyy=Jyy,
                Jx_unscaled=Jx,
                Jy_unscaled=Jy,
                Jz=Jz,
                Jzx=Jzx,
                Jcpm_unscaled=Jcpm,
                hx=hx,
                hz=hz,
                hz0_mode=hz0_mode,
                connectivity=args.connectivity,
                central_coupling=central_coupling,
                seed=args.seed,
                disorder=disorder,
                disorder_strength=disorder_strength if disorder != "none" else 0.0,
                disorder_strength_J=disorder_strength_J,
                disorder_strength_Jpm=disorder_strength_Jpm,
                disorder_strength_Jx=disorder_strength_Jx,
                disorder_strength_Jz=disorder_strength_Jz,
                disorder_strength_Jzx=disorder_strength_Jzx,
                disorder_strength_Jcpm=disorder_strength_Jcpm,
                disorder_strength_hx=disorder_strength_hx,
                disorder_strength_hz=disorder_strength_hz,
            )
        )
    return candidates


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_csv(path: Path, results: list[dict[str, Any]]) -> None:
    fields = [
        "rank",
        "objective_score",
        "N",
        "N_pixel",
        "model",
        "t",
        "backend",
        "diagonalization_kind",
        "symmetry_used",
        "sector_count",
        "fallback_reason",
        "connectivity",
        "central_coupling",
        "hz0_mode",
        "seed",
        "disorder",
        "disorder_strength",
        "disorder_strength_J",
        "disorder_strength_Jpm",
        "disorder_strength_Jx",
        "disorder_strength_Jz",
        "disorder_strength_Jzx",
        "disorder_strength_Jcpm",
        "disorder_strength_hx",
        "disorder_strength_hz",
        "J",
        "Jx_unscaled",
        "Jx_scaled",
        "Jy_unscaled",
        "Jy_scaled",
        "hz",
        "Jpm",
        "Jxx",
        "Jyy",
        "Jz",
        "Jzx",
        "Jcpm_unscaled",
        "Jcpm_scaled",
        "hx",
        "born_similarity",
        "phi_uniformity_score",
        "phi_entropy_score",
        "phi_total_variation",
        "phi_max_bin_fraction",
        "phi_rayleigh_r",
        "phi_sample_count",
        "phi_bin_count",
        "mean_abs_ratio_error",
        "reciprocity_error",
        "tail_density_exponent",
        "tail_survival_exponent",
        "tail_xmin",
        "energy_degenerate_fraction",
        "energy_degenerate_cluster_fraction",
        "energy_max_multiplicity",
        "energy_resolved_level_count",
        "energy_mean_spacing_ratio",
        "energy_min_spacing",
        "radius_q99_over_q50",
        "radius_unique_count",
        "radius_atomic_fraction",
        "radius_zero_fraction",
        "radius_positive_fraction",
        "theta_q95",
        "theta_q99",
        "theta_mass_gt_0p5",
        "theta_mass_gt_1p0",
        "diagonalization_wall_seconds",
        "analysis_wall_seconds",
        "diagnostic_figure",
        "label",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for rank, result in enumerate(results, 1):
            cand = result["candidate"]
            metrics = result["metrics"]
            row = {
                "rank": rank,
                "N": cand["N"],
                "N_pixel": cand["N_pixel"],
                "model": cand["model"],
                "t": result["t"],
                "backend": result["backend"],
                "diagonalization_kind": result["diagonalization_kind"],
                "symmetry_used": result["symmetry_used"],
                "sector_count": result["sector_count"],
                "fallback_reason": result["fallback_reason"],
                "connectivity": cand["connectivity"],
                "central_coupling": cand["central_coupling"],
                "hz0_mode": cand["hz0_mode"],
                "seed": cand["seed"],
                "disorder": cand["disorder"],
                "disorder_strength": cand["disorder_strength"],
                "disorder_strength_J": cand["disorder_strength_J"],
                "disorder_strength_Jpm": cand["disorder_strength_Jpm"],
                "disorder_strength_Jx": cand["disorder_strength_Jx"],
                "disorder_strength_Jz": cand["disorder_strength_Jz"],
                "disorder_strength_Jzx": cand["disorder_strength_Jzx"],
                "disorder_strength_Jcpm": cand["disorder_strength_Jcpm"],
                "disorder_strength_hx": cand["disorder_strength_hx"],
                "disorder_strength_hz": cand["disorder_strength_hz"],
                "J": cand["J"],
                "Jx_unscaled": cand["Jx_unscaled"],
                "Jx_scaled": cand["Jx_scaled"],
                "Jy_unscaled": cand["Jy_unscaled"],
                "Jy_scaled": cand["Jy_scaled"],
                "hz": cand["hz"],
                "Jpm": cand["Jpm"],
                "Jxx": cand["Jxx"],
                "Jyy": cand["Jyy"],
                "Jz": cand["Jz"],
                "Jzx": cand["Jzx"],
                "Jcpm_unscaled": cand["Jcpm_unscaled"],
                "Jcpm_scaled": cand["Jcpm_scaled"],
                "hx": cand["hx"],
                "diagnostic_figure": result.get("diagnostic_figure", ""),
                "label": result["label"],
            }
            row.update({key: metrics[key] for key in fields if key in metrics})
            writer.writerow(_jsonable(row))


def write_markdown(path: Path, results: list[dict[str, Any]], top: int) -> None:
    lines = [
        "# Born Hamiltonian Search",
        "",
        "| rank | score | model | N | backend | sectors | conn | central coupling | disorder | t | hz0 | Jx/sqrt(Np) | Jy/sqrt(Np) | Jcpm/sqrt(Np) | hz | Jpm | Jxx | Jyy | Jz | Jzx | E deg frac | E max mult | S_born | phi U | q exponent | recip err | atom frac | q99/q50 | theta q95 | P(theta>0.5) | figure |",
        "|---:|---:|:---|---:|:---|---:|:---|:---|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---|",
    ]
    for rank, result in enumerate(results[:top], 1):
        cand = result["candidate"]
        m = result["metrics"]
        figure = ""
        if result.get("diagnostic_figure"):
            figure_path = Path(result["diagnostic_figure"])
            try:
                figure_path = figure_path.relative_to(path.parent)
            except ValueError:
                pass
            figure = f"[plot]({figure_path.as_posix()})"
        lines.append(
            "| {rank} | {score:.4f} | {model} | {N} | {backend} | {sectors} | {conn} | {cc} | {disorder} | {t:g} | {hz0} | {Jx:.6g} | {Jy:.6g} | {Jcpm:.6g} | "
            "{hz:g} | {Jpm:g} | {Jxx:g} | {Jyy:g} | {Jz:g} | {Jzx:g} | {Edeg:.3f} | {Emult:.0f} | {S:.4f} | {phi:.3f} | {exponent:.3f} | {recip:.3f} | {atom:.3f} | {spread:.2f} | "
            "{theta_q95:.3f} | {mass:.3f} | {figure} |".format(
                rank=rank,
                score=m["objective_score"],
                model=cand["model"],
                N=cand["N"],
                backend=result["backend"],
                sectors=result["sector_count"],
                conn=cand["connectivity"],
                cc=cand["central_coupling"],
                disorder=_disorder_signature(cand),
                t=result["t"],
                hz0=cand["hz0_mode"],
                Jx=cand["Jx_scaled"],
                Jy=cand["Jy_scaled"],
                Jcpm=cand["Jcpm_scaled"],
                hz=cand["hz"],
                Jpm=cand["Jpm"],
                Jxx=cand["Jxx"],
                Jyy=cand["Jyy"],
                Jz=cand["Jz"],
                Jzx=cand["Jzx"],
                Edeg=m["energy_degenerate_fraction"],
                Emult=m["energy_max_multiplicity"],
                S=m["born_similarity"],
                phi=m.get("phi_uniformity_score", math.nan),
                exponent=m["tail_density_exponent"],
                recip=m["reciprocity_error"],
                atom=m["radius_atomic_fraction"],
                spread=m["radius_q99_over_q50"],
                theta_q95=m["theta_q95"],
                mass=m["theta_mass_gt_0p5"],
                figure=figure,
            )
        )
    lines.append("")
    lines.append("Metric notes:")
    lines.append("- Born-ratio similarity:")
    lines.append("")
    lines.append("  $$S_{\\mathrm{Born}} = 1 - 2 \\int_0^\\pi \\left|R(\\theta)-\\cos^2(\\theta/2)\\right|\\sin\\theta\\,d\\theta.$$") 
    lines.append("")
    lines.append("- `q exponent` is the Hill density exponent for:")
    lines.append("")
    lines.append("  $$q(x) \\sim x^{-p},\\qquad x=|\\lambda|=\\tan(\\theta/2).$$")
    lines.append("- `atom frac` near 1 means the radius distribution is discrete/atomic, so a histogram Born ratio is not a robust continuum diagnostic.")
    lines.append("- `phi U` is a normalized azimuth-uniformity score for the two antipodal Bloch-state branches; 1 is uniform over \\([0,2\\pi)\\), 0 is concentrated in one bin.")
    lines.append("- `E deg frac` and `E max mult` measure unresolved Hamiltonian eigenenergy multiplets before level-spacing degeneracies are collapsed.")
    lines.append("- Analytic matched-field target: heavy radius tail with $p \\simeq 2$, high `S_born`, low reciprocal-envelope error, and high `phi U`.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search single-pixel Hamiltonians for Born-like heavy-tailed theta histograms."
    )
    parser.add_argument("--N", type=int, nargs="+", default=[10])
    parser.add_argument("--model", default="single_pixel", choices=["single_pixel", "dimerized_pixel", "cnot_copier"])
    parser.add_argument("--times", type=float, nargs="+", default=[100.0, 1000.0, 10000.0, 1_000_000.0])
    parser.add_argument("--J", type=float, default=1.0)
    parser.add_argument("--Jpm", type=float, nargs="+", default=[0.0])
    parser.add_argument("--Jxx", type=float, nargs="+", default=[0.0])
    parser.add_argument("--Jyy", type=float, nargs="+", default=[0.0])
    parser.add_argument("--jx-unscaled", type=float, nargs="+", default=[0.005, 0.01, 0.02])
    parser.add_argument("--jy-unscaled", type=float, nargs="+", default=[0.0])
    parser.add_argument("--Jz", type=float, nargs="+", default=[0.0])
    parser.add_argument("--Jzx", type=float, nargs="+", default=[0.0])
    parser.add_argument("--jcpm-unscaled", type=float, nargs="+", default=[0.0])
    parser.add_argument("--hx", type=float, nargs="+", default=[0.0])
    parser.add_argument("--hz", type=float, nargs="+", default=[0.05, 0.1, 0.2])
    parser.add_argument("--hz0-modes", nargs="+", default=["matched", "zero"], choices=["matched", "zero", "half", "minus"])
    parser.add_argument("--connectivity", default="ring", choices=["chain", "ring", "all_to_all"])
    parser.add_argument(
        "--central-coupling",
        nargs="+",
        default=["auto"],
        choices=["auto", "all", "first", "last", "ends"],
    )
    parser.add_argument("--disorder", default="none", choices=DISORDER_CHOICES)
    parser.add_argument(
        "--disorder-strength",
        type=float,
        default=0.0,
        help="Fallback additive disorder width for every supported disordered channel.",
    )
    parser.add_argument("--disorder-strength-J", type=float, nargs="+", default=None)
    parser.add_argument("--disorder-strength-Jpm", type=float, nargs="+", default=None)
    parser.add_argument("--disorder-strength-Jx", type=float, nargs="+", default=None)
    parser.add_argument("--disorder-strength-Jz", type=float, nargs="+", default=None)
    parser.add_argument("--disorder-strength-Jzx", type=float, nargs="+", default=None)
    parser.add_argument("--disorder-strength-Jcpm", type=float, nargs="+", default=None)
    parser.add_argument("--disorder-strength-hx", type=float, nargs="+", default=None)
    parser.add_argument("--disorder-strength-hz", type=float, nargs="+", default=None)
    parser.add_argument("--seed", type=int, default=44)
    parser.add_argument("--bins", type=int, default=80)
    parser.add_argument("--tail-fraction", type=float, default=0.10)
    parser.add_argument("--log-bins", type=int, default=40)
    parser.add_argument("--energy-degeneracy-tol", type=float, default=1e-9)
    parser.add_argument("--backend", default="auto", choices=["auto", "quspin", "numpy"])
    parser.add_argument(
        "--workers",
        type=int,
        default=_default_worker_count(),
        help=(
            "Number of independent Hamiltonian candidates to evaluate in parallel. "
            "Defaults to BORN_WORKERS, then PBS_NP, then 1."
        ),
    )
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--out-dir", type=Path, default=Path("figures/born_hamiltonian_search"))
    parser.add_argument(
        "--plot-top",
        type=int,
        default=None,
        help="Generate simulation-time diagnostic figures for this many top-ranked rows. Defaults to --top; use 0 to disable.",
    )
    parser.add_argument(
        "--plot-dir",
        type=Path,
        default=None,
        help="Directory for simulation-time diagnostic figures. Defaults to <out-dir>/diagnostics.",
    )
    parser.add_argument("--plot-pseudocount", type=float, default=0.5)
    parser.add_argument(
        "--plot-max-bloch-points",
        type=int,
        default=6000,
        help="Maximum points per Bloch-sphere branch in each plotted figure; <=0 plots all points.",
    )
    parser.add_argument(
        "--max-detector-spectrum-qubits",
        type=int,
        default=12,
        help=(
            "Maximum detector-only qubits for dense detector-spectrum plotting. "
            "When larger, the script tries a symmetry-block QuSpin spectrum and "
            "otherwise leaves detector spectral panels marked unavailable. "
            "Use -1 to force dense plotting when memory allows."
        ),
    )
    spectra_group = parser.add_mutually_exclusive_group()
    spectra_group.add_argument(
        "--diagnostic-spectra",
        dest="diagnostic_spectra",
        action="store_true",
        help="Include full/detector spectrum and unfolded level-spacing panels in diagnostic figures.",
    )
    spectra_group.add_argument(
        "--skip-diagnostic-spectra",
        dest="diagnostic_spectra",
        action="store_false",
        help="Skip spectrum and level-spacing panels in diagnostic figures to avoid extra spectral work.",
    )
    parser.set_defaults(diagnostic_spectra=True)
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Progress log path. Defaults to <out-dir>/run.log.",
    )
    return parser.parse_args()


def run_search(args: argparse.Namespace) -> None:
    candidates = generate_candidates(args)
    args.workers = max(1, int(args.workers))
    print(f"Log file: {args.log_file}")
    print(f"Evaluating {len(candidates)} Hamiltonians x {len(args.times)} times")
    print(f"Worker processes: {args.workers}")

    all_results: list[dict[str, Any]] = []
    if args.workers == 1 or len(candidates) <= 1:
        for idx, candidate in enumerate(candidates, 1):
            print(f"[{idx:03d}/{len(candidates):03d}] {_candidate_label(candidate)}", flush=True)
            all_results.extend(
                evaluate_candidate(
                    candidate,
                    args.times,
                    args.bins,
                    args.backend,
                    args.tail_fraction,
                    args.log_bins,
                    args.energy_degeneracy_tol,
                )
            )
    else:
        n_workers = min(args.workers, len(candidates))
        jobs = [
            (
                candidate,
                list(args.times),
                args.bins,
                args.backend,
                args.tail_fraction,
                args.log_bins,
                args.energy_degeneracy_tol,
            )
            for candidate in candidates
        ]
        print(f"Submitting {len(jobs)} candidate jobs to {n_workers} workers", flush=True)
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            future_to_candidate = {
                pool.submit(_evaluate_candidate_job, job): job[0]
                for job in jobs
            }
            for done_idx, future in enumerate(as_completed(future_to_candidate), 1):
                candidate = future_to_candidate[future]
                try:
                    candidate_results = future.result()
                except Exception as exc:
                    label = _candidate_label(candidate)
                    raise RuntimeError(f"Worker failed while evaluating {label}") from exc
                all_results.extend(candidate_results)
                print(
                    f"[{done_idx:03d}/{len(jobs):03d}] completed {_candidate_label(candidate)}",
                    flush=True,
                )

    all_results.sort(key=lambda r: r["metrics"]["objective_score"], reverse=True)
    plot_top_results(args, all_results)

    json_path = args.out_dir / "results.json"
    csv_path = args.out_dir / "results.csv"
    md_path = args.out_dir / "top_candidates.md"
    json_path.write_text(
        json.dumps(_jsonable({"args": vars(args), "results": all_results}), indent=2),
        encoding="utf-8",
    )
    write_csv(csv_path, all_results)
    write_markdown(md_path, all_results, args.top)

    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print("\nTop candidates:")
    for rank, result in enumerate(all_results[: args.top], 1):
        cand = result["candidate"]
        m = result["metrics"]
        print(
            f"{rank:2d}. score={m['objective_score']:.4f} "
            f"S={m['born_similarity']:.4f} qexp={m['tail_density_exponent']:.3f} "
            f"phiU={m['phi_uniformity_score']:.3f} "
            f"recip={m['reciprocity_error']:.3f} "
            f"atom={m['radius_atomic_fraction']:.3f} "
            f"Edeg={m['energy_degenerate_fraction']:.3f} "
            f"Emax={m['energy_max_multiplicity']:.0f} "
            f"q99/q50={m['radius_q99_over_q50']:.2f} "
            f"model={cand['model']} N={cand['N']} conn={cand['connectivity']} "
            f"cc={cand['central_coupling']} t={result['t']:g} "
            f"hz0={cand['hz0_mode']} dis={_disorder_signature(cand)} "
            f"Jx={cand['Jx_scaled']:.6g} Jy={cand['Jy_scaled']:.6g} "
            f"Jcpm={cand['Jcpm_scaled']:.6g} "
            f"hz={cand['hz']:g} Jpm={cand['Jpm']:g} "
            f"Jxx={cand['Jxx']:g} Jyy={cand['Jyy']:g} "
            f"Jz={cand['Jz']:g} Jzx={cand['Jzx']:g}"
        )


def main() -> None:
    args = parse_args()
    if args.plot_top is None:
        args.plot_top = args.top
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.log_file is None:
        args.log_file = args.out_dir / "run.log"
    args.log_file.parent.mkdir(parents=True, exist_ok=True)

    with args.log_file.open("w", encoding="utf-8", buffering=1) as log_fh:
        stdout = TeeWriter(sys.stdout, log_fh)
        stderr = TeeWriter(sys.stderr, log_fh)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            run_search(args)


if __name__ == "__main__":
    main()
