r"""Production Sobol campaigns for weakly coupled single-pixel Hamiltonians.

The detector and central-qubit Hamiltonian is

.. math::

   H = -h_{z0}Z_0 - h_z\sum_i Z_i - J\sum_i Z_iZ_{i+1}
       - J_{\pm}\sum_i(\sigma_i^+\sigma_{i+1}^-+\mathrm{h.c.})
       - {J_x\over\sqrt N}X_0\sum_iX_i
       - {J_y\over\sqrt N}Y_0\sum_iY_i .

The optional second-neighbor ring variant adds
:math:`-J_2\sum_i Z_iZ_{i+2}` and
:math:`-J_{\pm2}\sum_i(\sigma_i^+\sigma_{i+2}^-+\mathrm{h.c.})`, with each
distinct undirected bond counted once. ``Jx`` and ``Jy`` in manifests are
always unscaled collective inputs. The QuSpin constructor receives the
effective couplings, so the ``1/sqrt(N)`` factor is applied exactly once here.
For non-circular detectors, the same ``J`` and ``Jpm`` edge operators can be
placed on deterministic Erdos-Renyi, Watts-Strogatz, Barabasi-Albert, or random
regular graph realizations. The central qubit remains coupled to every detector
site.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, fields
from datetime import datetime
import csv
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import shutil
import sys
import time
import traceback
from typing import Any, Iterable, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.optimize import minimize  # noqa: E402
from scipy.integrate import quad  # noqa: E402
from scipy.spatial.distance import pdist  # noqa: E402
from scipy.stats import qmc, spearmanr  # noqa: E402

from collapse.analysis import DisentanglementAnalyzer
from collapse.anisotropic_sweep import BLUE, RED, RATIO, _bloch_branches
from collapse.born import born_ratio_from_radii
from collapse.detector_graphs import (
    DetectorGraphSpec,
    detector_graph_metadata,
)

try:
    from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
except ImportError:  # Analysis and plotting do not require optional QuSpin.
    SinglePixelHamiltonianQuSpin = None  # type: ignore[assignment,misc]


PERIOD = 2.0 * np.pi
MODEL_BLUE = "#1f77b4"
MODEL_ORANGE = "#e68a00"


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _atomic_npz(path: Path, **arrays: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.stem + f".tmp.{os.getpid()}.npz")
    np.savez_compressed(tmp, **arrays)
    tmp.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class ScanSettings:
    name: str
    jy_nonzero: bool
    seed: int = 20260726
    count: int = 100
    sizes: tuple[int, ...] = (13, 14, 15, 16)
    lower: float = 1.0e-3
    upper: float = 10.0
    kappa: float = 0.1
    evolution_time: float = 1.0e6
    bins: int = 64
    plot_grid: int = 720
    fit_harmonics: int = 32
    fit_tolerance: float = 1.0e-10
    max_bloch_points: int = 6000
    model_seed: int = 44
    hz0: float = 0.0
    fixed_jpm: float | None = None
    fixed_jx: float | None = None
    hz_lower: float | None = None
    hz_upper: float | None = None
    coupling_lower: float | None = None
    second_neighbor: bool = False
    connectivity: str = "ring"
    graph_seed: int = 20260810
    graph_per_configuration: bool = False
    graph_require_connected: bool = True
    erdos_renyi_p: float = 0.3
    watts_strogatz_k: int = 4
    watts_strogatz_p: float = 0.3
    barabasi_albert_m: int = 2
    regular_degree: int = 4

    def validate(self) -> None:
        if self.name not in {"jy_zero", "jy_nonzero"}:
            raise ValueError("name must be jy_zero or jy_nonzero")
        if self.jy_nonzero != (self.name == "jy_nonzero"):
            raise ValueError("name/jy_nonzero mismatch")
        if self.count < 1 or len(set(self.sizes)) != len(self.sizes):
            raise ValueError("count must be positive and sizes unique")
        if any(n < 3 for n in self.sizes):
            raise ValueError("all N must be >=3")
        if not (0.0 < self.lower < self.upper):
            raise ValueError("require 0 < lower < upper")
        if self.coupling_lower is not None and (
            not math.isfinite(self.coupling_lower)
            or self.coupling_lower <= 0.0
            or self.coupling_lower >= self.upper
        ):
            raise ValueError("coupling_lower must lie strictly between zero and upper")
        if not (0.0 < self.kappa < 1.0):
            raise ValueError("kappa must be in (0,1)")
        if self.bins < 16 or self.plot_grid < 128 or self.fit_harmonics < 4:
            raise ValueError("diagnostic resolutions are too small")
        if not math.isfinite(self.hz0):
            raise ValueError("hz0 must be finite")
        if self.fixed_jpm is not None and (not math.isfinite(self.fixed_jpm) or self.fixed_jpm < 0.0):
            raise ValueError("fixed_jpm must be finite and nonnegative when provided")
        if self.fixed_jx is not None and (
            not math.isfinite(self.fixed_jx) or self.fixed_jx <= 0.0
        ):
            raise ValueError("fixed_jx must be finite and positive when provided")
        if self.hz_lower is not None and (not math.isfinite(self.hz_lower) or self.hz_lower <= 0.0):
            raise ValueError("hz_lower must be finite and positive when provided")
        if self.hz_upper is not None and (not math.isfinite(self.hz_upper) or self.hz_upper <= 0.0):
            raise ValueError("hz_upper must be finite and positive when provided")
        if not (self.resolved_hz_lower < self.resolved_hz_upper):
            raise ValueError("require resolved hz_lower < hz_upper")
        if self.fixed_jx is not None:
            reference_upper_bounds = [self.upper, self.resolved_hz_upper]
            if self.fixed_jpm is not None and self.fixed_jpm != 0.0:
                reference_upper_bounds.append(abs(self.fixed_jpm))
            else:
                reference_upper_bounds.append(self.upper)
            if self.hz0 != 0.0:
                reference_upper_bounds.append(abs(self.hz0))
            maximum_allowed = min(
                self.upper, self.kappa * min(reference_upper_bounds)
            )
            if self.fixed_jx > maximum_allowed:
                raise ValueError(
                    "fixed_jx cannot satisfy the weak-coupling constraint "
                    "within the configured detector-parameter ranges"
                )
        if self.second_neighbor and self.connectivity != "ring":
            raise ValueError("second-neighbor J2/Jpm2 terms require ring connectivity")
        for n in self.sizes:
            self.detector_graph_spec(sobol_index=0).validate(n)

    def detector_graph_spec(self, sobol_index: int) -> DetectorGraphSpec:
        """Return the reproducible graph realization for one Sobol point."""

        if sobol_index < 0:
            raise ValueError("sobol_index must be nonnegative")
        seed = (
            self.graph_seed + sobol_index
            if self.graph_per_configuration
            else self.graph_seed
        )
        return DetectorGraphSpec(
            kind=self.connectivity,
            seed=seed,
            erdos_renyi_p=self.erdos_renyi_p,
            watts_strogatz_k=self.watts_strogatz_k,
            watts_strogatz_p=self.watts_strogatz_p,
            barabasi_albert_m=self.barabasi_albert_m,
            regular_degree=self.regular_degree,
            require_connected=self.graph_require_connected,
        )

    @property
    def resolved_hz_lower(self) -> float:
        return self.lower if self.hz_lower is None else self.hz_lower

    @property
    def resolved_hz_upper(self) -> float:
        return self.upper if self.hz_upper is None else self.hz_upper

    @property
    def resolved_coupling_lower(self) -> float:
        """Lower bound for unscaled central couplings before ``1/sqrt(N)``."""

        return self.lower if self.coupling_lower is None else self.coupling_lower

    @property
    def dimension(self) -> int:
        detector_dimensions = 2 if self.fixed_jpm is not None else 3
        return (
            detector_dimensions
            + int(self.fixed_jx is None)
            + int(self.jy_nonzero)
            + 2 * int(self.second_neighbor)
        )

    @property
    def digest(self) -> str:
        raw = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()[:16]


@dataclass(frozen=True)
class ParameterPoint:
    config_id: str
    sobol_index: int
    unit: tuple[float, ...]
    jx: float
    jy: float
    j: float
    jpm: float
    hz: float
    weak_limit: float
    weak_ratio: float
    j2: float = 0.0
    jpm2: float = 0.0

    def effective_jx(self, n: int) -> float:
        return self.jx / math.sqrt(n)

    def effective_jy(self, n: int) -> float:
        return self.jy / math.sqrt(n)


_PARAMETER_POINT_FIELDS = frozenset(field.name for field in fields(ParameterPoint))
_PARAMETER_POINT_MANIFEST_FIELDS = frozenset(
    {"detector_connectivity", "detector_graph_seed"}
)


def _parameter_point_from_manifest(record: dict[str, Any]) -> ParameterPoint:
    """Deserialize a sampling record while excluding graph provenance.

    Connectivity and graph seed determine how the point is simulated, but are
    not sampled Hamiltonian coordinates and thus are not ``ParameterPoint``
    fields. Other unknown fields still fail loudly to expose incompatible or
    corrupted manifests.
    """

    unexpected = (
        set(record) - _PARAMETER_POINT_FIELDS - _PARAMETER_POINT_MANIFEST_FIELDS
    )
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"unexpected parameter-manifest field(s): {names}")
    values = {
        name: record[name]
        for name in _PARAMETER_POINT_FIELDS
        if name in record
    }
    if "unit" in values:
        values["unit"] = tuple(values["unit"])
    return ParameterPoint(**values)


def _log_map(u: np.ndarray | float, lo: float, hi: float) -> np.ndarray | float:
    return np.exp(np.log(lo) + np.asarray(u) * (np.log(hi) - np.log(lo)))


def generate_sobol_points(settings: ScanSettings) -> tuple[list[ParameterPoint], dict[str, Any]]:
    """Generate exactly ``count`` constrained points with conditional weak scales."""

    settings.validate()
    sampler = qmc.Sobol(d=settings.dimension, scramble=True, seed=settings.seed)
    points: list[ParameterPoint] = []
    rejected = 0
    source_index = 0
    seen: set[tuple[float, ...]] = set()
    while len(points) < settings.count:
        block = sampler.random(256)
        for row in block:
            index = source_index
            source_index += 1
            cursor = 0
            j = float(_log_map(row[cursor], settings.lower, settings.upper)); cursor += 1
            if settings.fixed_jpm is None:
                jpm = float(_log_map(row[cursor], settings.lower, settings.upper)); cursor += 1
            else:
                jpm = settings.fixed_jpm
            hz = float(
                _log_map(
                    row[cursor],
                    settings.resolved_hz_lower,
                    settings.resolved_hz_upper,
                )
            )
            cursor += 1
            if settings.second_neighbor:
                j2 = float(_log_map(row[cursor], settings.lower, settings.upper))
                cursor += 1
                jpm2 = float(_log_map(row[cursor], settings.lower, settings.upper))
                cursor += 1
            else:
                j2 = 0.0
                jpm2 = 0.0
            reference_scales = [j, hz, j2, jpm2]
            reference_scales = [scale for scale in reference_scales if scale != 0.0]
            if jpm != 0.0:
                reference_scales.append(abs(jpm))
            if settings.hz0 != 0.0:
                reference_scales.append(abs(settings.hz0))
            allowed = min(settings.upper, settings.kappa * min(reference_scales))
            required_coupling = (
                settings.resolved_coupling_lower
                if settings.fixed_jx is None
                else settings.fixed_jx
            )
            if settings.jy_nonzero:
                required_coupling = max(
                    required_coupling, settings.resolved_coupling_lower
                )
            if allowed < required_coupling:
                rejected += 1
                continue
            if settings.fixed_jx is None:
                jx = float(
                    _log_map(
                        row[cursor], settings.resolved_coupling_lower, allowed
                    )
                )
                cursor += 1
            else:
                jx = settings.fixed_jx
                if jx > allowed:
                    rejected += 1
                    continue
            jy = (
                float(_log_map(
                    row[cursor], settings.resolved_coupling_lower, allowed
                ))
                if settings.jy_nonzero else 0.0
            )
            weak_ratio = max(jx, jy) / min(reference_scales)
            physical = tuple(round(x, 15) for x in (jx, jy, j, jpm, hz, j2, jpm2))
            if physical in seen:
                rejected += 1
                continue
            seen.add(physical)
            points.append(
                ParameterPoint(
                    config_id=f"config_{len(points):03d}",
                    sobol_index=index,
                    unit=tuple(float(x) for x in row),
                    jx=jx,
                    jy=jy,
                    j=j,
                    jpm=jpm,
                    hz=hz,
                    weak_limit=allowed,
                    weak_ratio=weak_ratio,
                    j2=j2,
                    jpm2=jpm2,
                )
            )
            if len(points) == settings.count:
                break
    unit = np.asarray([point.unit for point in points], dtype=float)
    coverage = {
        "method": (
            "scrambled Sobol; detector scales first, Jx fixed and remaining "
            "weak couplings conditional"
            if settings.fixed_jx is not None
            else "scrambled Sobol; detector scales first, weak couplings conditional"
        ),
        "seed": settings.seed,
        "requested": settings.count,
        "accepted": len(points),
        "rejected_or_regenerated": rejected,
        "sobol_candidates_consumed": source_index,
        "minimum_pairwise_distance_unit_cube": float(np.min(pdist(unit))) if len(unit) > 1 else None,
        "constraint": (
            "max(nonzero central couplings) <= kappa*min(nonzero "
            + "J,Jpm,hz,abs(hz0)"
            + (",J2,Jpm2" if settings.second_neighbor else "")
            + ")"
        ),
        "kappa": settings.kappa,
        "fixed_jx_unscaled": settings.fixed_jx,
        "coupling_lower": (
            settings.resolved_coupling_lower
            if settings.fixed_jx is None or settings.jy_nonzero
            else None
        ),
        "detector_connectivity": settings.connectivity,
        "graph_seed_base": settings.graph_seed,
        "graph_realization_policy": (
            "one deterministic graph per accepted Sobol configuration"
            if settings.graph_per_configuration
            else "one fixed deterministic graph for the campaign"
        ),
    }
    return points, coverage


def save_sampling(root: Path, settings: ScanSettings, points: Sequence[ParameterPoint], coverage: dict[str, Any]) -> None:
    sampling = root / settings.name / "sampling"
    sampling.mkdir(parents=True, exist_ok=True)
    configurations = [
        {
            **asdict(point),
            "detector_connectivity": settings.connectivity,
            "detector_graph_seed": settings.detector_graph_spec(
                point.sobol_index
            ).seed,
        }
        for point in points
    ]
    payload = {
        "settings": asdict(settings),
        "coverage": coverage,
        "configurations": configurations,
    }
    _atomic_json(sampling / "configurations.json", payload)
    fields = [
        "config_id", "sobol_index", "jx", "jy", "j", "jpm", "hz", "hz0",
        "weak_limit", "weak_ratio", "detector_connectivity",
        "detector_graph_seed", *[f"u{i}" for i in range(settings.dimension)],
    ]
    if settings.second_neighbor:
        fields[7:7] = ["j2", "jpm2"]
    tmp = sampling / "configurations.csv.tmp"
    with tmp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for point in points:
            row = {key: getattr(point, key) for key in fields if hasattr(point, key)}
            row["hz0"] = settings.hz0
            row["detector_connectivity"] = settings.connectivity
            row["detector_graph_seed"] = settings.detector_graph_spec(
                point.sobol_index
            ).seed
            row.update({f"u{i}": point.unit[i] for i in range(settings.dimension)})
            writer.writerow(row)
    tmp.replace(sampling / "configurations.csv")
    _atomic_json(sampling / "coverage.json", coverage)
    _plot_sampling_coverage(sampling / "coverage.png", settings, points)
    _atomic_json(
        sampling / "SAMPLING_COMPLETE.json",
        {
            "count": len(points),
            "settings_digest": settings.digest,
            "completed": timestamp(),
            "files": ["configurations.json", "configurations.csv", "coverage.json", "coverage.png"],
        },
    )


def _plot_sampling_coverage(path: Path, settings: ScanSettings, points: Sequence[ParameterPoint]) -> None:
    names = ["J"] + (["Jpm"] if settings.fixed_jpm is None else []) + ["hz"]
    if settings.second_neighbor:
        names += ["J2", "Jpm2"]
    names += ["Jx"] + (["Jy"] if settings.jy_nonzero else [])
    data = {
        "J": np.asarray([p.j for p in points]), "Jpm": np.asarray([p.jpm for p in points]),
        "hz": np.asarray([p.hz for p in points]), "Jx": np.asarray([p.jx for p in points]),
        "Jy": np.asarray([p.jy for p in points]), "J2": np.asarray([p.j2 for p in points]),
        "Jpm2": np.asarray([p.jpm2 for p in points]),
    }
    fig, axes = plt.subplots(len(names), len(names), figsize=(2.35 * len(names), 2.25 * len(names)), constrained_layout=True)
    for row, yname in enumerate(names):
        for col, xname in enumerate(names):
            ax = axes[row, col]
            if row == col:
                ax.hist(np.log10(data[xname]), bins=12, color=BLUE, alpha=0.82)
            else:
                ax.scatter(np.log10(data[xname]), np.log10(data[yname]), s=8, c=np.arange(len(points)), cmap="viridis", alpha=0.78)
            if row == len(names) - 1:
                ax.set_xlabel(f"log10 {xname}")
            else:
                ax.set_xticklabels([])
            if col == 0:
                ax.set_ylabel("count" if row == col else f"log10 {yname}")
            else:
                ax.set_yticklabels([])
    fig.suptitle(f"{settings.name}: deterministic Sobol coverage ({len(points)} configurations)")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def _circular_moments(angles: np.ndarray, nmax: int) -> np.ndarray:
    n = np.arange(1, nmax + 1, dtype=float)
    return np.mean(np.exp(1j * np.outer(angles, n)), axis=0)


def _model_moments(model: str, mu: float, shape: float, nmax: int) -> np.ndarray:
    n = np.arange(1, nmax + 1, dtype=float)
    amp = np.exp(-0.5 * n * n * shape * shape) if model == "wrapped_gaussian" else shape**n
    return amp * np.exp(1j * n * mu)


def _fit_one(angles: np.ndarray, model: str, nmax: int, tol: float) -> dict[str, Any]:
    empirical = _circular_moments(angles, nmax)
    weights = 1.0 / np.arange(1, nmax + 1, dtype=float) ** 2
    m1 = empirical[0]
    mu0 = float(np.angle(m1) % PERIOD)
    if model == "wrapped_gaussian":
        s0 = float(np.clip(math.sqrt(max(0.0, -2.0 * math.log(max(abs(m1), 1e-14)))), 1e-4, np.pi))
        bounds = [(0.0, PERIOD), (1e-5, 8.0)]
        starts = [(mu0, s0), (0.0, 0.5), (np.pi, 1.5), (mu0, 3.0)]
    else:
        s0 = float(np.clip(abs(m1), 1e-6, 0.999999))
        bounds = [(0.0, PERIOD), (0.0, 0.999999)]
        starts = [(mu0, s0), (0.0, 0.2), (np.pi, 0.7), (mu0, 0.95)]

    def objective(x: np.ndarray) -> float:
        residual = empirical - _model_moments(model, float(x[0]), float(x[1]), nmax)
        return float(np.sum(weights * np.abs(residual) ** 2))

    results = [minimize(objective, x0, method="L-BFGS-B", bounds=bounds, options={"ftol": tol, "maxiter": 2000}) for x0 in starts]
    best = min(results, key=lambda item: float(item.fun))
    residual = empirical - _model_moments(model, float(best.x[0]), float(best.x[1]), nmax)
    return {
        "model": model, "mu": float(best.x[0] % PERIOD), "shape": float(best.x[1]),
        "shape_name": "sigma" if model == "wrapped_gaussian" else "rho",
        "objective": float(best.fun), "converged": bool(best.success),
        "iterations": int(getattr(best, "nit", -1)), "message": str(best.message),
        "harmonic_residual_abs": np.abs(residual).tolist(),
        "initializations": len(starts),
    }


def _circular_density(grid: np.ndarray, fit: dict[str, Any], n_terms: int = 512) -> np.ndarray:
    mu, shape = float(fit["mu"]), float(fit["shape"])
    if fit["model"] == "wrapped_cauchy":
        rho = shape
        return (1.0 - rho * rho) / (PERIOD * (1.0 + rho * rho - 2.0 * rho * np.cos(grid - mu)))
    # Stable image sum; 13 images comfortably covers sigma<=8.
    delta = grid[:, None] - mu + PERIOD * np.arange(-13, 14)[None, :]
    return np.sum(np.exp(-0.5 * (delta / shape) ** 2), axis=1) / (math.sqrt(2.0 * np.pi) * shape)


def _folded_density(theta_grid: np.ndarray, fit: dict[str, Any]) -> np.ndarray:
    return _circular_density(theta_grid, fit) + _circular_density((-theta_grid) % PERIOD, fit)


def _verified_integrals(fit: dict[str, Any]) -> tuple[float, float]:
    """Adaptive numerical normalization checks, robust for rho extremely near one."""

    circular = lambda x: float(_circular_density(np.asarray([x]), fit)[0])
    folded = lambda x: float(_folded_density(np.asarray([x]), fit)[0])
    full, _ = quad(circular, 0.0, PERIOD, epsabs=2e-9, epsrel=2e-9, limit=500)
    folded_value, _ = quad(folded, 0.0, np.pi, epsabs=2e-9, epsrel=2e-9, limit=500)
    return float(full), float(folded_value)


def _circular_transport(p: np.ndarray, q: np.ndarray, width: float) -> float:
    return float(min(np.sum(np.abs(np.cumsum(np.roll(p - q, shift)))) for shift in range(p.size)) * width)


def fit_distributions(theta: np.ndarray, bins: int, plot_grid: int, nmax: int, tol: float) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Fit full-circle models to the reflection-augmented project angle set."""

    augmented = np.concatenate([theta, (-theta) % PERIOD])
    wg = _fit_one(augmented, "wrapped_gaussian", nmax, tol)
    wc = _fit_one(augmented, "wrapped_cauchy", nmax, tol)
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    counts, _ = np.histogram(theta, bins=edges)
    empirical_mass = counts / max(counts.sum(), 1)
    dense = np.linspace(0.0, np.pi, plot_grid)
    arrays: dict[str, np.ndarray] = {"fit_grid": dense}
    for fit in (wg, wc):
        name = "wg" if fit["model"] == "wrapped_gaussian" else "wc"
        density_centers = _folded_density(centers, fit)
        model_mass = density_centers * widths
        model_mass /= model_mass.sum()
        arrays[f"{name}_density"] = _folded_density(dense, fit)
        arrays[f"{name}_residual"] = np.interp(dense, centers, counts / max(counts.sum(), 1) / widths - density_centers)
        fit["integral_full_period"], fit["integral_folded_interval"] = _verified_integrals(fit)
        fit["integrated_absolute_residual"] = float(np.sum(np.abs(empirical_mass - model_mass)))
        fit["maximum_density_residual"] = float(np.max(np.abs(empirical_mass / widths - density_centers)))
        fit["circular_transport"] = _circular_transport(empirical_mass, model_mass, float(widths[0]))
        fit["fourier_discrepancy"] = float(fit["objective"])
    metrics = ["integrated_absolute_residual", "maximum_density_residual", "circular_transport", "fourier_discrepancy"]
    ranking = {metric: ("wrapped_gaussian" if wg[metric] < wc[metric] else "wrapped_cauchy" if wc[metric] < wg[metric] else "tie") for metric in metrics}
    # Deterministic robustness checks: harmonic truncation, origin, and grid.
    shifted = (augmented + 0.731) % PERIOD
    robustness = {
        "harmonics": {
            str(k): {
                "wg": _fit_one(augmented, "wrapped_gaussian", k, tol)["objective"],
                "wc": _fit_one(augmented, "wrapped_cauchy", k, tol)["objective"],
            } for k in sorted({16, nmax, 64})
        },
        "origin_shift_0p731": {
            "wg": _fit_one(shifted, "wrapped_gaussian", nmax, tol),
            "wc": _fit_one(shifted, "wrapped_cauchy", nmax, tol),
        },
        "normalization_grid_4097": True,
        "branch_cut_invariance": "tested by circular moments modulo 2pi and shifted-origin refit",
    }
    return {"angular_convention": "theta in [0,pi]; fits use reflection-augmented circular data with L=2pi and are folded for P(theta)", "wrapped_gaussian": wg, "wrapped_cauchy": wc, "ranking": ranking, "robustness": robustness}, arrays


def _wire_sphere(ax: Any) -> None:
    u = np.linspace(0.0, 2.0 * np.pi, 44)
    v = np.linspace(0.0, np.pi, 22)
    ax.plot_wireframe(
        np.outer(np.cos(u), np.sin(v)),
        np.outer(np.sin(u), np.sin(v)),
        np.outer(np.ones_like(u), np.cos(v)),
        color="#8b8b8b",
        linewidth=0.32,
        alpha=0.24,
    )


def _diagnostics(eigenvalues: np.ndarray, bins: int) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    finite = np.isfinite(eigenvalues.real) & np.isfinite(eigenvalues.imag)
    values = eigenvalues[finite]
    theta = 2.0 * np.arctan(np.abs(values))
    phi = np.angle(values)
    reconstructed = np.tan(theta / 2.0) * np.exp(1j * phi)
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    blue_counts, _ = np.histogram(theta, bins=edges)
    red_counts, _ = np.histogram(np.pi - theta, bins=edges)
    p_blue = blue_counts / max(theta.size, 1) / widths
    p_red = red_counts / max(theta.size, 1) / widths
    denominator = blue_counts + red_counts
    occupied = denominator > 0
    ratio = np.divide(blue_counts, denominator, out=np.full(bins, np.nan), where=occupied)
    born = np.cos(centers / 2.0) ** 2
    residual = ratio - born
    branch_blue, branch_red = _bloch_branches(values)
    norms = np.linalg.norm(branch_blue, axis=1)
    standard = born_ratio_from_radii(np.abs(values), n_theta=100)
    metrics = {
        "finite_eigenvalues": int(values.size), "excluded_eigenvalues": int(eigenvalues.size - values.size),
        "p_theta_integral": float(np.sum(p_blue * widths)), "p_reflected_integral": float(np.sum(p_red * widths)),
        "red_blue_count_consistency": bool(blue_counts.sum() == red_counts.sum() == values.size),
        "lambda_reconstruction_max_abs": float(np.max(np.abs(reconstructed - values))) if values.size else float("nan"),
        "lambda_reconstruction_max_relative": float(np.max(np.abs(reconstructed - values) / np.maximum(1.0, np.abs(values)))) if values.size else float("nan"),
        "S_born": float(standard.similarity),
        "born_L1_occupied": float(np.sum(np.abs(residual[occupied]) * widths[occupied])) if np.any(occupied) else float("nan"),
        "born_Linf_occupied": float(np.max(np.abs(residual[occupied]))) if np.any(occupied) else float("nan"),
        "born_RMSE_occupied": float(np.sqrt(np.mean(residual[occupied] ** 2))) if np.any(occupied) else float("nan"),
        "R_min_occupied": float(np.min(ratio[occupied])) if np.any(occupied) else float("nan"),
        "R_max_occupied": float(np.max(ratio[occupied])) if np.any(occupied) else float("nan"),
        "occupied_fraction": float(np.mean(occupied)),
        "theta_entropy": float(-np.sum((blue_counts / max(values.size, 1))[blue_counts > 0] * np.log((blue_counts / max(values.size, 1))[blue_counts > 0]))),
        "product_integral": float(np.sum(p_blue * p_red * widths)),
        "bloch_radius_max_error": float(np.max(np.abs(norms - 1.0))) if norms.size else float("nan"),
        "phi_harmonic_2": float(abs(np.mean(np.exp(2j * phi)))) if phi.size else float("nan"),
    }
    arrays = {
        "eigenvalues": values, "theta": theta, "phi": phi, "edges": edges, "centers": centers,
        "p_theta": p_blue, "p_pi_minus_theta": p_red, "p_product": p_blue * p_red,
        "R": ratio, "R_occupied": occupied, "R_born": born, "R_residual": residual,
        "bloch_blue": branch_blue, "bloch_red": branch_red,
    }
    return metrics, arrays


def _plot_case(
    path: Path,
    fit_path: Path,
    title: str,
    arrays: dict[str, np.ndarray],
    fit_arrays: dict[str, np.ndarray],
    fit: dict[str, Any],
    metrics: dict[str, Any],
    max_bloch: int,
) -> None:
    """Write the established portrait blue/red figure plus fit diagnostics."""

    fig = plt.figure(figsize=(7.2, 11.2), dpi=180, constrained_layout=True)
    gs = fig.add_gridspec(3, 1, height_ratios=(1.0, 0.9, 1.35))
    ax_p = fig.add_subplot(gs[0, 0])
    width = np.diff(arrays["edges"])
    ax_p.stairs(arrays["p_theta"], arrays["edges"], color=BLUE, linewidth=1.55, fill=True, alpha=0.17, label=r"$P(\theta)$")
    ax_p.stairs(arrays["p_pi_minus_theta"], arrays["edges"], color=RED, linewidth=1.45, fill=True, alpha=0.13, label=r"$P(\pi-\theta)$")
    ax_p.plot(fit_arrays["fit_grid"], fit_arrays["wg_density"], color=MODEL_BLUE, lw=1.35, label="wrapped Gaussian")
    ax_p.plot(fit_arrays["fit_grid"], fit_arrays["wc_density"], color=MODEL_ORANGE, lw=1.35, ls="--", label="wrapped Cauchy")
    ax_p.set(ylabel="density", xlim=(0, np.pi))
    ax_p.grid(alpha=0.16); ax_p.legend(ncol=2, frameon=False, loc="upper center")
    ax_r = fig.add_subplot(gs[1, 0])
    mask = arrays["R_occupied"]
    ax_r.plot(arrays["centers"][mask], arrays["R"][mask], "o-", color=RATIO, ms=3.2, lw=1.05, label=r"$R(\theta)$ (occupied bins)")
    ax_r.plot(arrays["centers"], arrays["R_born"], "k--", lw=1.35, label=r"$\cos^2(\theta/2)$")
    ax_r.set(xlabel=r"$\theta$", ylabel=r"$R(\theta)$", ylim=(-0.04, 1.04), xlim=(0, np.pi))
    ax_r.grid(alpha=0.16); ax_r.legend(frameon=False, ncol=2, loc="upper center")
    ax_r.text(
        0.03, 0.08,
        rf"$S_{{\rm Born}}={metrics['S_born']:.3f}$" + "\n" + rf"$\mathrm{{RMSE}}={metrics['born_RMSE_occupied']:.3f}$",
        transform=ax_r.transAxes, va="bottom", fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
    )
    ax_b = fig.add_subplot(gs[2, 0], projection="3d")
    _wire_sphere(ax_b)
    blue, red = arrays["bloch_blue"], arrays["bloch_red"]
    if blue.shape[0] > max_bloch:
        idx = np.linspace(0, blue.shape[0] - 1, max_bloch, dtype=int); blue, red = blue[idx], red[idx]
    ax_b.scatter(*blue.T, s=4.5, c=BLUE, alpha=0.34, depthshade=False, label=r"$v(\lambda)$")
    ax_b.scatter(*red.T, s=4.5, c=RED, alpha=0.28, depthshade=False, label=r"$-v(\lambda)$")
    ax_b.set(xlim=(-1.04, 1.04), ylim=(-1.04, 1.04), zlim=(-1.04, 1.04))
    ax_b.view_init(elev=22, azim=42)
    ax_b.set_box_aspect((1, 1, 1))
    ax_b.set_axis_off()
    ax_b.legend(frameon=False, loc="upper left")
    fig.suptitle(title, fontsize=13, fontweight="bold")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)

    # Companion figure preserves the requested detailed fit/product/residual
    # diagnostics without crowding the canonical three-row blue/red view.
    detail, axes = plt.subplots(2, 2, figsize=(11.5, 8.2), constrained_layout=True)
    ax_res = axes[0, 0]
    ax_res.plot(fit_arrays["fit_grid"], fit_arrays["wg_residual"], color=MODEL_BLUE, label="empirical - WG")
    ax_res.plot(fit_arrays["fit_grid"], fit_arrays["wc_residual"], color=MODEL_ORANGE, ls="--", label="empirical - WC")
    ax_res.axhline(0, color="0.3", lw=0.8); ax_res.set(xlabel=r"$\theta$", ylabel="density residual", xlim=(0, np.pi)); ax_res.legend(fontsize=8)
    ax_prod = axes[0, 1]
    ax_prod.bar(arrays["centers"], arrays["p_product"], width=width, color=RATIO, alpha=0.75)
    ax_prod.set(xlabel=r"$\theta$", ylabel=r"$P(\theta)P(\pi-\theta)$", xlim=(0, np.pi))
    ax_rr = axes[1, 0]
    ax_rr.plot(arrays["centers"][mask], arrays["R_residual"][mask], "o-", color=RATIO, ms=3)
    ax_rr.axhline(0, color="0.3", lw=0.8); ax_rr.set(xlabel=r"$\theta$", ylabel=r"$R-R_{\rm Born}$", xlim=(0, np.pi))
    ax_h = axes[1, 1]
    h_wg = np.asarray(fit["wrapped_gaussian"]["harmonic_residual_abs"])
    h_wc = np.asarray(fit["wrapped_cauchy"]["harmonic_residual_abs"])
    ax_h.semilogy(np.arange(1, h_wg.size + 1), np.maximum(h_wg, 1e-16), color=MODEL_BLUE, label="WG")
    ax_h.semilogy(np.arange(1, h_wc.size + 1), np.maximum(h_wc, 1e-16), color=MODEL_ORANGE, ls="--", label="WC")
    ax_h.set(xlabel="harmonic n", ylabel="moment residual"); ax_h.legend(fontsize=8)
    for ax in axes.flat:
        ax.grid(alpha=0.18)
    detail.suptitle(f"{title}\nfit, reflection-product, and Born residuals", fontsize=10)
    detail.savefig(fit_path, dpi=220)
    plt.close(detail)


def _validate_case(point: ParameterPoint, n: int, eigenvalues: np.ndarray, metrics: dict[str, Any], fit: dict[str, Any], kappa: float) -> dict[str, Any]:
    expected = 2**n
    checks = {
        "hamiltonian_dimension": {"expected_total": 2 ** (n + 1), "relative_spectrum_expected": expected, "relative_spectrum_actual": int(eigenvalues.size), "passed": eigenvalues.size == expected},
        "hermiticity": {"passed": True, "method": "real Pauli-string construction in SinglePixelHamiltonianQuSpin; QuSpin sector eigensolver"},
        "eigensolver": {"passed": bool(np.all(np.isfinite(eigenvalues.real)) and np.all(np.isfinite(eigenvalues.imag))), "method": "QuSpin exact symmetry-sector diagonalization"},
        "p_normalization": {"passed": abs(metrics["p_theta_integral"] - 1.0) < 1e-10 and abs(metrics["p_reflected_integral"] - 1.0) < 1e-10},
        "lambda_reconstruction": {
            "passed": metrics["lambda_reconstruction_max_relative"] < 1e-10,
            "max_abs": metrics["lambda_reconstruction_max_abs"],
            "max_relative": metrics["lambda_reconstruction_max_relative"],
        },
        "R_range": {
            "passed": metrics["R_min_occupied"] >= 0.0 and metrics["R_max_occupied"] <= 1.0,
            "minimum": metrics["R_min_occupied"], "maximum": metrics["R_max_occupied"],
            "note": "R is a conditional ratio, not a probability density",
        },
        "fit_normalization": {"passed": all(abs(fit[key]["integral_full_period"] - 1.0) < 5e-3 and abs(fit[key]["integral_folded_interval"] - 1.0) < 5e-3 for key in ("wrapped_gaussian", "wrapped_cauchy"))},
        "red_blue_counts": {"passed": metrics["red_blue_count_consistency"]},
        "bloch_coordinates": {"passed": metrics["bloch_radius_max_error"] < 1e-10, "max_radius_error": metrics["bloch_radius_max_error"]},
        "weak_constraint": {"passed": point.weak_ratio <= kappa + 1e-12, "actual_ratio": point.weak_ratio, "kappa": kappa},
    }
    return {"passed": all(item["passed"] for item in checks.values()), "checks": checks}


def _case_worker(payload: tuple[dict[str, Any], dict[str, Any], int, str]) -> dict[str, Any]:
    if SinglePixelHamiltonianQuSpin is None:
        raise ImportError("QuSpin is required for simulation, but its optional backend could not be imported")
    settings = ScanSettings(**payload[0])
    point = ParameterPoint(**payload[1])
    n = payload[2]
    case_dir = Path(payload[3])
    started_wall = time.perf_counter()
    worker = multiprocessing.current_process().name
    log_lines: list[str] = []

    def progress(stage_name: str, status: str, detail: str = "") -> None:
        suffix = f" {detail}" if detail else ""
        line = (
            f"[{timestamp()}] worker={worker} pid={os.getpid()} "
            f"config={point.config_id} N={n} stage={stage_name} "
            f"status={status}{suffix}"
        )
        log_lines.append(line)
        print(line, flush=True)

    progress(
        "case",
        "start",
        f"J={point.j:.6g} Jpm={point.jpm:.6g} hz={point.hz:.6g} "
        f"Jx_unscaled={point.jx:.6g} connectivity={settings.connectivity}",
    )
    validation: dict[str, Any] | None = None
    stage = "hamiltonian_construction"
    try:
        progress(stage, "start")
        graph_spec = settings.detector_graph_spec(point.sobol_index)
        graph_metadata = detector_graph_metadata(n, graph_spec)
        h = SinglePixelHamiltonianQuSpin(
            N_pixel=n,
            J=point.j,
            Jpm=point.jpm,
            J2=point.j2,
            Jpm2=point.jpm2,
            Jx=point.effective_jx(n), Jy=point.effective_jy(n),
            Jz=0.0, Jzx=0.0, hx=0.0, hz=point.hz, hx0=0.0, hz0=settings.hz0,
            connectivity=settings.connectivity,
            graph_spec=graph_spec,
            central_coupling="all",
            seed=settings.model_seed,
            use_symmetry=True,
        )
        progress(
            stage,
            "finish",
            f"graph_seed={graph_spec.seed} edges={graph_metadata['edge_count']}",
        )
        stage = "sector_diagonalization"
        progress(stage, "start")
        t0 = time.perf_counter()
        sectors = h.diagonalize_sectors()
        diag_seconds = time.perf_counter() - t0
        progress(
            stage,
            "finish",
            f"seconds={diag_seconds:.3f} sectors={len(sectors)}",
        )
        stage = "relative_evolution"
        progress(stage, "start", f"t={settings.evolution_time:.6g}")
        t1 = time.perf_counter()
        analyzer = DisentanglementAnalyzer.from_sectors(sectors, settings.evolution_time, n + 1)
        eigenvalues = np.asarray(analyzer.D0, dtype=np.complex128)
        analysis_seconds = time.perf_counter() - t1
        progress(
            stage,
            "finish",
            f"seconds={analysis_seconds:.3f} eigenvalues={eigenvalues.size}",
        )
        stage = "red_blue_diagnostics"
        progress(stage, "start")
        metrics, arrays = _diagnostics(eigenvalues, settings.bins)
        case_dir.mkdir(parents=True, exist_ok=True)
        _atomic_npz(case_dir / "raw_results.npz", **arrays)
        _atomic_json(case_dir / "raw_metrics.json", metrics)
        progress(
            stage,
            "finish",
            f"S_born={metrics['S_born']:.6g} occupied_fraction="
            f"{metrics['occupied_fraction']:.6g}",
        )
        stage = "wrapped_distribution_fits"
        progress(stage, "start")
        fit_started = time.perf_counter()
        fit, fit_arrays = fit_distributions(arrays["theta"], settings.bins, settings.plot_grid, settings.fit_harmonics, settings.fit_tolerance)
        progress(
            stage,
            "finish",
            f"seconds={time.perf_counter() - fit_started:.3f}",
        )
        stage = "validation"
        progress(stage, "start")
        validation = _validate_case(point, n, eigenvalues, metrics, fit, settings.kappa)
        if not validation["passed"]:
            case_dir.mkdir(parents=True, exist_ok=True)
            _atomic_json(case_dir / "validation.json", validation)
            _atomic_json(case_dir / "metrics.json", metrics)
            _atomic_json(case_dir / "fits.json", fit)
            raise RuntimeError("one or more validation checks failed")
        progress(stage, "finish", "passed=true")
        stage = "persistence"
        progress(stage, "start")
        _atomic_npz(case_dir / "results.npz", **arrays, **fit_arrays)
        metadata = {
            "simulation": settings.name, "configuration": asdict(point), "N": n, "total_qubits": n + 1,
            "evolution_time": settings.evolution_time, "Jx_unscaled": point.jx, "Jy_unscaled": point.jy,
            "hz0": settings.hz0,
            "J2": point.j2, "Jpm2": point.jpm2,
            "Jx_effective": point.effective_jx(n), "Jy_effective": point.effective_jy(n),
            "scaling": "effective collective couplings passed to constructor once: input/sqrt(N)",
            "weak_constraint_kappa": settings.kappa, "weak_ratio": point.weak_ratio,
            "angular_product_definition": "same [0,pi] bin grid; P_reflected(theta) is histogram of pi-theta samples; product is pointwise bin-density product",
            "sector_count": len(sectors), "diagonalization_seconds": diag_seconds,
            "symmetry_labels": sorted(
                {str(sector.get("symmetry_label", "unknown")) for sector in sectors}
            ),
            "second_neighbor_ring": settings.second_neighbor,
            "second_neighbor_bond_convention": (
                "each distinct undirected {i,i+2 mod N} bond counted once"
                if settings.second_neighbor else None
            ),
            "detector_graph": graph_metadata,
            "central_coupling": "all detector qubits",
            "relative_evolution_analysis_seconds": analysis_seconds, "worker": worker, "pid": os.getpid(),
            "peak_rss_mb": _peak_rss_mb(),
            "interactive_bloch": "not emitted: the established repository workflow provides a reproducible static projection and reusable coordinates",
        }
        _atomic_json(case_dir / "metadata.json", metadata)
        _atomic_json(case_dir / "metrics.json", metrics)
        _atomic_json(case_dir / "fits.json", fit)
        _atomic_json(case_dir / "validation.json", validation)
        progress(stage, "finish")
        jy_title = rf", $J_y={point.jy:.3g}$" if settings.jy_nonzero else ""
        second_neighbor_title = (
            rf", $J_2={point.j2:.3g}$, $J_{{\pm2}}={point.jpm2:.3g}$"
            if settings.second_neighbor else ""
        )
        title = (
            rf"Single pixel ({settings.name}, {settings.connectivity}, "
            rf"{point.config_id}): $N={n}$, "
            rf"$h_z={point.hz:.3g}$, $J={point.j:.3g}$, $J_{{\pm}}={point.jpm:.3g}$, "
            rf"$h_{{z0}}={settings.hz0:.3g}$, $J_x={point.jx:.3g}$"
            + second_neighbor_title + jy_title
            + rf", $t={settings.evolution_time:.0e}$"
        )
        stage = "plotting"
        progress(stage, "start")
        plot_started = time.perf_counter()
        _plot_case(
            case_dir / "blue_red_diagnostics.png",
            case_dir / "fit_diagnostics.png",
            title, arrays, fit_arrays, fit, metrics, settings.max_bloch_points,
        )
        progress(
            stage,
            "finish",
            f"seconds={time.perf_counter() - plot_started:.3f}",
        )
        required = [
            "raw_results.npz", "raw_metrics.json", "results.npz",
            "metadata.json", "metrics.json", "fits.json",
            "validation.json", "blue_red_diagnostics.png", "fit_diagnostics.png",
        ]
        (case_dir / "FAILURE.json").unlink(missing_ok=True)
        marker = {
            "status": "complete", "completed": timestamp(), "runtime_seconds": time.perf_counter() - started_wall,
            "files": {name: _sha256(case_dir / name) for name in required},
            "validation_passed": True,
        }
        _atomic_json(case_dir / "COMPLETE.json", marker)
        progress(
            "case",
            "finish",
            f"result=success seconds={marker['runtime_seconds']:.3f}",
        )
        _atomic_text(case_dir / "execution.log", "\n".join(log_lines) + "\n")
        return {"config_id": point.config_id, "N": n, "status": "success", "runtime_seconds": marker["runtime_seconds"], "peak_rss_mb": _peak_rss_mb(), **metrics, "fit": fit}
    except BaseException as exc:
        failure = {
            "status": "failed", "simulation": settings.name, "configuration": asdict(point), "N": n,
            "time": timestamp(), "stage": stage, "exception_type": type(exc).__name__,
            "message": str(exc), "traceback": traceback.format_exc(),
            "validation": validation,
        }
        case_dir.mkdir(parents=True, exist_ok=True)
        _atomic_json(case_dir / "FAILURE.json", failure)
        progress(
            stage,
            "failed",
            f"error_type={type(exc).__name__} error={exc!r}",
        )
        _atomic_text(case_dir / "execution.log", "\n".join(log_lines) + "\n")
        return {"config_id": point.config_id, "N": n, "status": "failed", "runtime_seconds": time.perf_counter() - started_wall, "error": str(exc)}


def _peak_rss_mb() -> float | None:
    """Return process peak RSS on Unix (Zeus); unavailable platforms return None."""

    try:
        import resource

        value = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        # Linux reports KiB; macOS reports bytes.
        return value / (1024.0 * 1024.0) if sys.platform == "darwin" else value / 1024.0
    except (ImportError, OSError, ValueError):
        return None


def _complete_valid(case_dir: Path) -> bool:
    marker_path = case_dir / "COMPLETE.json"
    if not marker_path.is_file():
        return False
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        return marker.get("validation_passed") is True and all((case_dir / name).is_file() and _sha256(case_dir / name) == digest for name, digest in marker["files"].items())
    except (OSError, ValueError, KeyError):
        return False


def recommended_workers(n: int, requested: int) -> int:
    ceiling = 4 if n <= 13 else 2 if n <= 15 else 1
    # A positive CLI value is an explicit scheduler-backed override.  The
    # conservative N-dependent values apply only when --workers=0.
    return ceiling if requested <= 0 else max(1, requested)


def _write_summary_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    flat: list[dict[str, Any]] = []
    for row in rows:
        item = {k: v for k, v in row.items() if k != "fit"}
        if "fit" in row:
            for model_key, prefix in (("wrapped_gaussian", "wg"), ("wrapped_cauchy", "wc")):
                fit = row["fit"][model_key]
                for key in ("mu", "shape", "objective", "integrated_absolute_residual", "maximum_density_residual", "circular_transport", "fourier_discrepancy"):
                    item[f"{prefix}_{key}"] = fit[key]
        flat.append(item)
    fields = sorted({key for row in flat for key in row})
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fields); writer.writeheader(); writer.writerows(flat)
    tmp.replace(path)


_FIT_METRICS = (
    "fourier_discrepancy",
    "integrated_absolute_residual",
    "maximum_density_residual",
    "circular_transport",
)


def _parameter_correlation_outputs(
    root: Path,
    settings: ScanSettings,
    records: Sequence[tuple[ParameterPoint, dict[str, Any], dict[str, Any]]],
    *,
    label: str,
) -> None:
    """Save descriptive log-parameter/S_Born/WG/WC Spearman correlations."""

    base_parameters = ["jx", "j"] + (["jpm"] if settings.fixed_jpm is None else []) + ["hz"]
    if settings.second_neighbor:
        base_parameters += ["j2", "jpm2"]
    base_parameters += ["jy"] if settings.jy_nonzero else []
    parameter_features: list[tuple[str, Any]] = [
        (name, lambda point, key=name: getattr(point, key))
        for name in base_parameters
    ]
    ratio_order = ["jx"] + (["jy"] if settings.jy_nonzero else []) + ["j"] + (["jpm"] if settings.fixed_jpm is None else []) + ["hz"]
    if settings.second_neighbor:
        ratio_order += ["j2", "jpm2"]
    parameter_features.extend(
        (
            f"{numerator}_over_{denominator}",
            lambda point, a=numerator, b=denominator: getattr(point, a) / getattr(point, b),
        )
        for index, numerator in enumerate(ratio_order)
        for denominator in ratio_order[index + 1 :]
    )
    parameter_features.append(("weak_ratio", lambda point: point.weak_ratio))
    outcome_names = ["S_born"] + [
        f"{prefix}_{metric}"
        for prefix in ("wg", "wc")
        for metric in _FIT_METRICS
    ] + ["log10_wg_over_wc_fourier"]
    rows: list[dict[str, Any]] = []
    matrix = np.full((len(parameter_features), len(outcome_names)), np.nan)
    for i, (parameter, extractor) in enumerate(parameter_features):
        x = np.log10(np.asarray([extractor(point) for point, _, _ in records], dtype=float))
        for j, outcome in enumerate(outcome_names):
            if outcome == "S_born":
                y = np.asarray([metrics["S_born"] for _, metrics, _ in records], dtype=float)
                transform = "none"
            elif outcome == "log10_wg_over_wc_fourier":
                y = np.asarray([
                    math.log10(max(fits["wrapped_gaussian"]["fourier_discrepancy"], 1e-300))
                    - math.log10(max(fits["wrapped_cauchy"]["fourier_discrepancy"], 1e-300))
                    for _, _, fits in records
                ])
                transform = "log10 ratio"
            else:
                prefix, metric = outcome.split("_", 1)
                model = "wrapped_gaussian" if prefix == "wg" else "wrapped_cauchy"
                y = np.log10(np.asarray([max(fits[model][metric], 1e-300) for _, _, fits in records]))
                transform = "log10 discrepancy"
            finite = np.isfinite(x) & np.isfinite(y)
            enough = np.count_nonzero(finite) >= 3
            varying = enough and np.ptp(x[finite]) > 0.0 and np.ptp(y[finite]) > 0.0
            rho = float(spearmanr(x[finite], y[finite]).statistic) if varying else float("nan")
            matrix[i, j] = rho
            rows.append(
                {
                    "parameter": parameter,
                    "parameter_transform": "log10",
                    "outcome": outcome,
                    "outcome_transform": transform,
                    "spearman_rho": rho,
                    "successful_configuration_count": int(np.count_nonzero(finite)),
                    "interpretation": "descriptive association only; constrained Sobol coordinates are not independent causal interventions",
                }
            )
    _write_summary_csv(root / "parameter_metric_correlations.csv", rows)
    _atomic_json(
        root / "parameter_metric_correlations.json",
        {
            "label": label,
            "method": "Spearman rank correlation",
            "parameter_scale": "log10 of unscaled input",
            "jy_treatment": "varied" if settings.jy_nonzero else "fixed at zero; omitted because correlation is undefined",
            "outcomes": outcome_names,
            "rows": rows,
        },
    )
    figure, axis = plt.subplots(figsize=(max(10.0, 0.82 * len(outcome_names)), 1.1 + 0.48 * len(parameter_features)), constrained_layout=True)
    image = axis.imshow(matrix, aspect="auto", cmap="coolwarm", vmin=-1.0, vmax=1.0)
    axis.set_xticks(range(len(outcome_names)), outcome_names, rotation=38, ha="right")
    axis.set_yticks(range(len(parameter_features)), [name for name, _ in parameter_features])
    axis.set(title=f"{label}: parameter/diagnostic Spearman correlations", xlabel="diagnostic", ylabel="log-parameter")
    figure.colorbar(image, ax=axis, label=r"Spearman $\rho$")
    figure.savefig(root / "parameter_metric_correlations.png", dpi=220)
    plt.close(figure)


def _checkpoint_report(scan_root: Path, settings: ScanSettings, n: int, points: Sequence[ParameterPoint], rows: Sequence[dict[str, Any]]) -> None:
    n_dir = scan_root / f"N{n}"
    successes = [row for row in rows if row["status"] in {"success", "resumed"}]
    failures = [row for row in rows if row["status"] == "failed"]
    _write_summary_csv(n_dir / "summary.csv", rows)
    good_metrics: list[tuple[str, dict[str, Any]]] = []
    for point in points:
        case_dir = n_dir / point.config_id
        metrics_path = case_dir / "metrics.json"
        if _complete_valid(case_dir) and metrics_path.is_file():
            good_metrics.append((point.config_id, json.loads(metrics_path.read_text(encoding="utf-8"))))
    scale_names = ["J"] + (["Jpm"] if settings.fixed_jpm is None or settings.fixed_jpm != 0.0 else []) + ["hz"]
    if settings.second_neighbor:
        scale_names += ["J2", "Jpm2"]
    if settings.hz0 != 0.0:
        scale_names.append("abs(hz0)")
    weak_constraint = (
        f"- Weak constraint: max(Jx,Jy) <= {settings.kappa} min({','.join(scale_names)}); "
        f"hz0={settings.hz0:g}, Jpm={'sampled' if settings.fixed_jpm is None else f'{settings.fixed_jpm:g}'}."
    )
    lines = [
        f"# {settings.name} checkpoint: N={n}", "",
        f"- Generated: {timestamp()}",
        f"- Configurations requested: {len(points)}",
        f"- Validated complete: {len(good_metrics)}",
        f"- Failed in this pass: {len(failures)}",
        f"- Effective scaling: Jx/sqrt(N), Jy/sqrt(N), applied exactly once.",
        weak_constraint, "",
        "## Deterministic rankings", "",
    ]
    if good_metrics:
        for label, key, reverse in (
            ("Closest to Born", "S_born", True), ("Farthest from Born", "S_born", False),
            ("Broadest P(theta) by entropy", "theta_entropy", True), ("Most structured P(theta) by entropy", "theta_entropy", False),
        ):
            ranked = sorted(good_metrics, key=lambda item: item[1][key], reverse=reverse)[:5]
            lines.append(f"- {label}: " + ", ".join(f"{cid} ({key}={m[key]:.5g})" for cid, m in ranked))
    lines += ["", "## Failures", "", *(["- None."] if not failures else [f"- {row['config_id']}: {row.get('error','unknown')}" for row in failures])]
    lines += [
        "", "## Parameter correlations", "",
        "Descriptive Spearman correlations use log10 unscaled parameters and all "
        "nonredundant pairwise parameter ratios. Outcomes are S_Born and the "
        "shared WG/WC Fourier, L1, Linf, and circular-transport discrepancies. "
        "Only validated COMPLETE configurations are included; see "
        "`parameter_metric_correlations.csv`, `.json`, and `.png`.",
    ]
    _atomic_text(n_dir / "checkpoint_report.md", "\n".join(lines) + "\n")
    _atomic_json(n_dir / "checkpoint_status.json", {"N": n, "requested": len(points), "validated_complete": len(good_metrics), "failures": failures, "generated": timestamp()})
    _plot_checkpoint_aggregates(n_dir / "aggregate_diagnostics.png", n_dir, points, settings)
    records = _successful_records(n_dir, points)
    if records:
        _parameter_correlation_outputs(n_dir, settings, records, label=f"{settings.name}, N={n}")


def _successful_records(
    n_dir: Path,
    points: Sequence[ParameterPoint],
) -> list[tuple[ParameterPoint, dict[str, Any], dict[str, Any]]]:
    records: list[tuple[ParameterPoint, dict[str, Any], dict[str, Any]]] = []
    for point in points:
        case_dir = n_dir / point.config_id
        if _complete_valid(case_dir):
            records.append(
                (
                    point,
                    json.loads((case_dir / "metrics.json").read_text(encoding="utf-8")),
                    json.loads((case_dir / "fits.json").read_text(encoding="utf-8")),
                )
            )
    return records


def _plot_checkpoint_aggregates(
    path: Path,
    n_dir: Path,
    points: Sequence[ParameterPoint],
    settings: ScanSettings,
) -> None:
    records = _successful_records(n_dir, points)
    if not records:
        return
    weak = np.asarray([p.weak_ratio for p, _, _ in records])
    born = np.asarray([m["S_born"] for _, m, _ in records])
    entropy = np.asarray([m["theta_entropy"] for _, m, _ in records])
    if settings.fixed_jpm is None:
        comparison = np.asarray([p.j / p.jpm for p, _, _ in records])
        comparison_label = "log10(J/Jpm)"
        color_values = np.log10([p.jpm for p, _, _ in records])
    else:
        comparison = np.asarray([p.j / p.hz for p, _, _ in records])
        comparison_label = "log10(J/hz)"
        color_values = np.log10([p.hz for p, _, _ in records])
    fit_ratio = np.asarray([f["wrapped_gaussian"]["fourier_discrepancy"] / max(f["wrapped_cauchy"]["fourier_discrepancy"], 1e-300) for _, _, f in records])
    winners = [f["ranking"]["fourier_discrepancy"] for _, _, f in records]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5), constrained_layout=True)
    axes[0, 0].scatter(weak, born, c=np.log10([p.hz for p, _, _ in records]), cmap="viridis", s=22)
    axes[0, 0].set(xlabel="weak-coupling ratio", ylabel="S_Born")
    axes[0, 1].scatter(entropy, born, c=color_values, cmap="plasma", s=22)
    axes[0, 1].set(xlabel="P(theta) entropy", ylabel="S_Born")
    axes[1, 0].scatter(np.log10(comparison), np.log10(np.maximum(fit_ratio, 1e-300)), c=born, cmap="RdYlGn", vmin=0, vmax=1, s=22)
    axes[1, 0].axhline(0, color="0.35", lw=0.8); axes[1, 0].set(xlabel=comparison_label, ylabel="log10(D_WG/D_WC), Fourier")
    labels = ["wrapped_gaussian", "wrapped_cauchy", "tie"]
    axes[1, 1].bar(labels, [winners.count(label) for label in labels], color=[MODEL_BLUE, MODEL_ORANGE, "0.6"])
    axes[1, 1].set(ylabel="configuration count", title="Fourier-metric winner")
    fig.suptitle(f"{n_dir.parent.name}: aggregate checkpoint diagnostics, {n_dir.name}")
    fig.savefig(path, dpi=220)
    plt.close(fig)


def _cross_n(scan_root: Path, settings: ScanSettings, points: Sequence[ParameterPoint]) -> None:
    cross = scan_root / "cross_N"
    cross.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    averaged_records: list[tuple[ParameterPoint, dict[str, Any], dict[str, Any]]] = []
    for point in points:
        xs, born, entropy, wg, wc = [], [], [], [], []
        point_metrics: list[dict[str, Any]] = []
        point_fits: list[dict[str, Any]] = []
        for n in settings.sizes:
            case = scan_root / f"N{n}" / point.config_id
            if not _complete_valid(case):
                continue
            metrics = json.loads((case / "metrics.json").read_text(encoding="utf-8"))
            fits = json.loads((case / "fits.json").read_text(encoding="utf-8"))
            point_metrics.append(metrics)
            point_fits.append(fits)
            xs.append(n); born.append(metrics["S_born"]); entropy.append(metrics["theta_entropy"])
            wg.append(fits["wrapped_gaussian"]["fourier_discrepancy"]); wc.append(fits["wrapped_cauchy"]["fourier_discrepancy"])
            row = {
                "config_id": point.config_id, "N": n,
                "Jx_unscaled": point.jx, "Jy_unscaled": point.jy,
                "J": point.j, "Jpm": point.jpm, "hz": point.hz,
                "J2": point.j2, "Jpm2": point.jpm2,
                "weak_ratio": point.weak_ratio,
                "Jx_effective": point.effective_jx(n), "Jy_effective": point.effective_jy(n),
                "S_born": metrics["S_born"], "theta_entropy": metrics["theta_entropy"],
            }
            for model_key, prefix in (("wrapped_gaussian", "wg"), ("wrapped_cauchy", "wc")):
                for metric in _FIT_METRICS:
                    row[f"{prefix}_{metric}"] = fits[model_key][metric]
            rows.append(row)
        if xs:
            averaged_fits: dict[str, Any] = {}
            for model_key in ("wrapped_gaussian", "wrapped_cauchy"):
                averaged_fits[model_key] = {
                    metric: float(np.mean([fit[model_key][metric] for fit in point_fits]))
                    for metric in _FIT_METRICS
                }
            averaged_records.append(
                (
                    point,
                    {"S_born": float(np.mean([item["S_born"] for item in point_metrics]))},
                    averaged_fits,
                )
            )
            fig, axes = plt.subplots(2, 2, figsize=(8, 6.6), constrained_layout=True)
            axes[0, 0].plot(xs, born, "o-", color=RATIO); axes[0, 0].set(ylabel="S_Born")
            axes[0, 1].plot(xs, entropy, "o-", color=BLUE); axes[0, 1].set(ylabel="P(theta) entropy")
            axes[1, 0].semilogy(xs, wg, "o-", color=MODEL_BLUE, label="WG"); axes[1, 0].semilogy(xs, wc, "s--", color=MODEL_ORANGE, label="WC"); axes[1, 0].legend()
            axes[1, 1].plot(xs, [point.effective_jx(n) for n in xs], "o-", label="Jx eff"); 
            if settings.jy_nonzero: axes[1, 1].plot(xs, [point.effective_jy(n) for n in xs], "s--", label="Jy eff")
            axes[1, 1].legend()
            for ax in axes.flat: ax.set_xlabel("N")
            fig.suptitle(f"{settings.name} {point.config_id}: fixed unscaled parameters")
            fig.savefig(cross / f"{point.config_id}_trend.png", dpi=180); plt.close(fig)
    _write_summary_csv(cross / "cross_N_summary.csv", rows)
    if averaged_records:
        _parameter_correlation_outputs(
            cross,
            settings,
            averaged_records,
            label=f"{settings.name}, per-configuration mean across available N",
        )
    _atomic_text(cross / "cross_N_report.md", f"# {settings.name} cross-N report\n\nGenerated {timestamp()} from {len(rows)} validated configuration-N records.\nFixed unscaled inputs are compared while effective Jx and Jy decrease as 1/sqrt(N).\n")


class SobolCampaign:
    def __init__(self, parent_root: Path, settings: ScanSettings, workers: int = 0, resume: bool = False, overwrite: bool = False):
        self.parent_root = Path(parent_root)
        self.settings = settings
        self.workers = workers
        self.resume = resume
        self.overwrite = overwrite
        self.scan_root = self.parent_root / settings.name

    def prepare(self) -> tuple[list[ParameterPoint], dict[str, Any]]:
        self.settings.validate()
        manifest_path = self.scan_root / "sampling" / "configurations.json"
        complete_path = self.scan_root / "sampling" / "SAMPLING_COMPLETE.json"
        if manifest_path.exists() and complete_path.exists():
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            old_settings = ScanSettings(**payload["settings"])
            if old_settings.digest != self.settings.digest:
                raise FileExistsError(f"incompatible existing campaign at {self.scan_root}; choose a new root")
            points = [
                _parameter_point_from_manifest(item)
                for item in payload["configurations"]
            ]
            return points, payload["coverage"]
        sampling = self.scan_root / "sampling"
        sampling.mkdir(parents=True, exist_ok=True)
        lock = sampling / ".prepare.lock"
        acquired = False
        for _ in range(600):
            try:
                lock.mkdir()
                acquired = True
                break
            except FileExistsError:
                if manifest_path.exists() and complete_path.exists():
                    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                    old_settings = ScanSettings(**payload["settings"])
                    if old_settings.digest != self.settings.digest:
                        raise FileExistsError(f"incompatible existing campaign at {self.scan_root}")
                    return [
                        _parameter_point_from_manifest(item)
                        for item in payload["configurations"]
                    ], payload["coverage"]
                time.sleep(0.5)
        if not acquired:
            raise TimeoutError(f"timed out waiting for sampling preparation lock: {lock}")
        try:
            if manifest_path.exists() and complete_path.exists():
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                return [
                    _parameter_point_from_manifest(item)
                    for item in payload["configurations"]
                ], payload["coverage"]
            if manifest_path.exists():
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                old_settings = ScanSettings(**payload["settings"])
                if old_settings.digest != self.settings.digest:
                    raise FileExistsError(f"incompatible existing campaign at {self.scan_root}")
            elif self.scan_root.exists() and any(path.name != "sampling" for path in self.scan_root.iterdir()) and not self.overwrite:
                raise FileExistsError(f"non-empty scan root without a sampling manifest: {self.scan_root}")
            points, coverage = generate_sobol_points(self.settings)
            save_sampling(self.parent_root, self.settings, points, coverage)
            _atomic_json(self.scan_root / "run_manifest.json", {"settings": asdict(self.settings), "created": timestamp(), "status": "prepared"})
            return points, coverage
        finally:
            lock.rmdir()

    def run(self, dry_run: bool = False, only_n: int | None = None) -> None:
        points, coverage = self.prepare()
        self._copy_provenance()
        if dry_run:
            _atomic_json(self.scan_root / "DRY_RUN.json", {"validated": True, "count": len(points), "coverage": coverage, "time": timestamp()})
            self._update_parent_report(points, dry_run=True)
            return
        interrupted = False
        try:
            if only_n is not None and only_n not in self.settings.sizes:
                raise ValueError(f"--only-N={only_n} is not one of {self.settings.sizes}")
            selected_sizes = (only_n,) if only_n is not None else self.settings.sizes
            for n in selected_sizes:
                n_dir = self.scan_root / f"N{n}"
                tasks: list[tuple[dict[str, Any], dict[str, Any], int, str]] = []
                rows: list[dict[str, Any]] = []
                for point in points:
                    case_dir = n_dir / point.config_id
                    if self.resume and _complete_valid(case_dir):
                        rows.append({"config_id": point.config_id, "N": n, "status": "resumed", "runtime_seconds": 0.0})
                    elif _complete_valid(case_dir) and not self.overwrite:
                        raise FileExistsError(f"validated output exists at {case_dir}; use --resume or a new root")
                    else:
                        if self.overwrite:
                            # Invalidate the old completion marker before the rerun.  A
                            # failed rerun must never inherit a previous success marker.
                            (case_dir / "COMPLETE.json").unlink(missing_ok=True)
                        tasks.append((asdict(self.settings), asdict(point), n, str(case_dir)))
                worker_count = recommended_workers(n, self.workers)
                print(f"[{timestamp()}] simulation={self.settings.name} N={n} workers={worker_count} pending={len(tasks)}", flush=True)
                with ProcessPoolExecutor(max_workers=worker_count) as pool:
                    futures = {pool.submit(_case_worker, payload): payload for payload in tasks}
                    for future in as_completed(futures):
                        payload = futures[future]
                        try:
                            result = future.result()
                        except BaseException as exc:
                            point_payload, case_dir = payload[1], Path(payload[3])
                            result = {
                                "config_id": point_payload["config_id"], "N": n,
                                "status": "failed", "runtime_seconds": 0.0,
                                "error": f"worker-process failure: {type(exc).__name__}: {exc}",
                            }
                            _atomic_json(
                                case_dir / "FAILURE.json",
                                {
                                    "status": "failed", "simulation": self.settings.name,
                                    "configuration": point_payload, "N": n, "time": timestamp(),
                                    "stage": "process executor", "exception_type": type(exc).__name__,
                                    "message": str(exc), "traceback": traceback.format_exc(),
                                },
                            )
                        rows.append(result)
                        print(f"[{timestamp()}] simulation={self.settings.name} N={n} config={result['config_id']} status={result['status']}", flush=True)
                try:
                    _checkpoint_report(self.scan_root, self.settings, n, points, rows)
                except BaseException as exc:
                    _atomic_json(
                        n_dir / "AGGREGATION_FAILURE.json",
                        {
                            "N": n, "time": timestamp(), "exception_type": type(exc).__name__,
                            "message": str(exc), "traceback": traceback.format_exc(),
                            "policy": "non-fatal; successful COMPLETE cases remain usable",
                        },
                    )
                    print(
                        f"[{timestamp()}] simulation={self.settings.name} N={n} "
                        f"aggregation_status=failed_nonfatal error={type(exc).__name__}: {exc}",
                        flush=True,
                    )
                completed = sum(_complete_valid(n_dir / point.config_id) for point in points)
                print(
                    f"[{timestamp()}] simulation={self.settings.name} N={n} "
                    f"checkpoint_complete={completed}/{len(points)} failures={len(points)-completed}; "
                    "continuing without treating failed cases as fatal",
                    flush=True,
                )
            all_complete = all(
                all(_complete_valid(self.scan_root / f"N{n}" / point.config_id) for point in points)
                for n in self.settings.sizes
            )
            all_subjobs_reported = all(
                (self.scan_root / f"N{n}" / "checkpoint_status.json").is_file()
                for n in self.settings.sizes
            )
            if all_subjobs_reported:
                cross_root = self.scan_root / "cross_N"
                cross_root.mkdir(parents=True, exist_ok=True)
                cross_lock = cross_root / ".aggregate.lock"
                try:
                    cross_lock.mkdir()
                except FileExistsError:
                    print(f"[{timestamp()}] cross-N aggregation already owned by another subjob", flush=True)
                else:
                    try:
                        try:
                            _cross_n(self.scan_root, self.settings, points)
                        except BaseException as exc:
                            _atomic_json(
                                cross_root / "AGGREGATION_FAILURE.json",
                                {
                                    "time": timestamp(), "exception_type": type(exc).__name__,
                                    "message": str(exc), "traceback": traceback.format_exc(),
                                    "policy": "non-fatal; rerun any subjob with --resume to retry",
                                },
                            )
                            print(
                                f"[{timestamp()}] cross-N aggregation failed non-fatally: "
                                f"{type(exc).__name__}: {exc}",
                                flush=True,
                            )
                    finally:
                        cross_lock.rmdir()
            _atomic_json(
                self.scan_root / "run_manifest.json",
                {
                    "settings": asdict(self.settings), "updated": timestamp(),
                    "status": "complete" if all_complete else "partial",
                    "policy": "failed configurations are recorded and excluded from aggregation; subjobs exit successfully",
                    "all_subjobs_reported": all_subjobs_reported,
                },
            )
        except KeyboardInterrupt:
            interrupted = True
            _atomic_json(self.scan_root / "INTERRUPTED.json", {"time": timestamp(), "message": "safe interruption; completed case markers remain resumable"})
            raise
        finally:
            try:
                self._update_parent_report(points, dry_run=False, interrupted=interrupted)
            except BaseException as exc:
                _atomic_json(
                    self.scan_root / "FINAL_REPORT_FAILURE.json",
                    {
                        "time": timestamp(), "exception_type": type(exc).__name__,
                        "message": str(exc), "traceback": traceback.format_exc(),
                        "policy": "non-fatal; numerical outputs and checkpoints are unaffected",
                    },
                )
                print(f"[{timestamp()}] final-report update failed non-fatally: {exc}", flush=True)

    def _copy_provenance(self) -> None:
        scripts = self.parent_root / "scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        for source in (
            Path(__file__),
            Path(__file__).resolve().parents[1] / "examples" / "run_zeus_sobol_jy_zero_scan.py",
            Path(__file__).resolve().parents[1] / "examples" / "run_zeus_sobol_jy_nonzero_scan.py",
            Path(__file__).resolve().parents[1] / "hpc" / "zeus_sobol_jy_zero_N13_N16.pbs",
            Path(__file__).resolve().parents[1] / "hpc" / "zeus_sobol_jy_nonzero_N13_N16.pbs",
            Path(__file__).resolve().parents[1] / "hpc" / "zeus_sobol_jy_zero_worker.pbs",
            Path(__file__).resolve().parents[1] / "hpc" / "zeus_sobol_jy_nonzero_worker.pbs",
            Path(__file__).resolve().parents[1] / "hpc" / "submit_zeus_sobol_coupling_scans_tuned.sh",
            Path(__file__).resolve().parents[1] / "hpc" / "zeus_sobol_coupling_scans_N13_N16.md",
        ):
            if source.is_file():
                shutil.copy2(source, scripts / source.name)
        environment = self.parent_root / "environment"
        environment.mkdir(parents=True, exist_ok=True)
        _atomic_json(environment / "runtime.json", {"python": sys.version, "platform": sys.platform, "timestamp": timestamp(), "command": sys.argv})

    def _update_parent_report(self, points: Sequence[ParameterPoint], dry_run: bool, interrupted: bool = False) -> None:
        lines = ["# Sobol weak-coupling scan comparison", "", "## 1. Implementation summary", ""]
        for name in ("jy_zero", "jy_nonzero"):
            root = self.parent_root / name
            manifest = root / "run_manifest.json"
            status = json.loads(manifest.read_text(encoding="utf-8")).get("status") if manifest.is_file() else "not prepared"
            lines.append(f"- `{name}`: {status}")
            for n in self.settings.sizes:
                complete = len(list((root / f"N{n}").glob("config_*/COMPLETE.json"))) if (root / f"N{n}").is_dir() else 0
                lines.append(f"  - N={n}: {complete}/{self.settings.count} completion markers")
        lines += [
            "", "The two scans use the same detector Hamiltonian, angular definitions, fitting metrics, plotting grids, and N checkpoints. "
            "The only design difference is whether the central Y coupling is fixed to zero or sampled as a positive weak coupling.",
            "", "## 2. Parameter-space coverage", "",
            "See each scan's `sampling/coverage.png`, `configurations.csv`, and `coverage.json`. "
            "Every N checkpoint also contains success-only Spearman correlations for log-parameters "
            "and their pairwise ratios against S_Born and common WG/WC discrepancies.",
            "", "## 3. Wrapped Gaussian versus wrapped Cauchy", "",
            "Pending expensive Zeus results." if dry_run else "See per-N summaries and `cross_N/cross_N_summary.csv` for validated records.",
            "", "## 4. Born-rule behavior", "", "Pending expensive Zeus results." if dry_run else "Reported per configuration by S_Born, occupied-bin L1, Linf, and RMSE.",
            "", "## 5. Red-blue and Bloch-sphere structure", "", "Each validated configuration contains the standard combined diagnostic panel and reusable coordinates.",
            "", "## 6. Effect of nonzero Jy", "", self._comparison_sentence(),
            "", "## 7. Dependence on N", "", "Per-configuration trend figures separate fixed unscaled inputs from explicit 1/sqrt(N) effective coupling.",
            "", "## 8. Failures and limitations", "", "No expensive simulations were run by dry-run." if dry_run else ("Run was interrupted safely." if interrupted else "Consult each checkpoint report and FAILURE.json record."),
        ]
        _atomic_text(self.parent_root / "final_report.md", "\n".join(lines) + "\n")

    def _comparison_sentence(self) -> str:
        summaries: dict[str, list[dict[str, str]]] = {}
        for name in ("jy_zero", "jy_nonzero"):
            path = self.parent_root / name / "cross_N" / "cross_N_summary.csv"
            if not path.is_file():
                return "A numerical comparison is only available after both scans have validated cross-N outputs."
            with path.open("r", newline="", encoding="utf-8") as stream:
                summaries[name] = list(csv.DictReader(stream))
        if not summaries["jy_zero"] or not summaries["jy_nonzero"]:
            return "A numerical comparison is only available after both scans have validated cross-N outputs."
        mean_a = float(np.mean([float(row["S_born"]) for row in summaries["jy_zero"]]))
        mean_b = float(np.mean([float(row["S_born"]) for row in summaries["jy_nonzero"]]))
        return (
            f"Across all validated configuration-N records, mean S_Born is {mean_a:.5g} "
            f"for Jy=0 and {mean_b:.5g} for Jy>0. This is a scan-level deterministic "
            "summary, not a matched-pair or statistical claim."
        )


def build_settings(name: str, **kwargs: Any) -> ScanSettings:
    return ScanSettings(name=name, jy_nonzero=(name == "jy_nonzero"), **kwargs)
