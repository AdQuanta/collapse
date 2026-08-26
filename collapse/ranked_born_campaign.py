"""Rank completed Born-like cases and rerun selected Hamiltonians.

This module provides the shared, importable core for two Zeus follow-ups:

* finite-size continuation of the most Born-like cases; and
* central-field scans of the most Born-like cases in a large atlas.

The source score is always the stored canonical ``S_born``.  Hamiltonian
parameters are read from per-case metadata, and every new result records the
source path, source score, exact graph realization, effective collective
couplings, symmetry sectors, and numerical timings.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import gc
import hashlib
import importlib.metadata
import json
import math
import multiprocessing
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any, Iterable, Sequence

import numpy as np

from collapse.analysis import DisentanglementAnalyzer
from collapse.detector_graphs import DetectorGraphSpec, detector_graph_metadata
from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from collapse.sobol_coupling_scan import (
    _atomic_json,
    _atomic_npz,
    _diagnostics,
    _peak_rss_mb,
    _plot_case,
    _sha256,
    fit_distributions,
    timestamp,
)


@dataclass(frozen=True)
class RankedHamiltonianCase:
    """One source Hamiltonian together with its stored Born score."""

    source_root: str
    source_case: str
    source_metric_file: str
    source_s_born: float
    source_n: int
    hz: float
    hz0: float
    j: float
    jpm: float
    jx: float
    jy: float = 0.0
    j2: float = 0.0
    jpm2: float = 0.0
    connectivity: str = "ring"
    central_coupling: str = "all"
    evolution_time: float = 1.0e6
    model_seed: int = 44
    graph_spec: dict[str, Any] | None = None
    source_graph_metadata: dict[str, Any] | None = None

    @property
    def identity_digest(self) -> str:
        raw = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return payload


def _runtime_provenance() -> dict[str, Any]:
    packages = {}
    for name in ("numpy", "scipy", "matplotlib", "quspin", "quspin-extensions"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "unavailable"
    module_path = Path(__file__).resolve()
    quspin_path = module_path.parent / "hamiltonians" / "quspin_hamiltonians.py"
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "packages": packages,
        "code_sha256": {
            str(module_path): _sha256(module_path),
            str(quspin_path): _sha256(quspin_path),
        },
    }


def _finite_float(payload: dict[str, Any], key: str, source: Path) -> float:
    try:
        value = float(payload[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"missing or invalid {key!r} in {source}") from exc
    if not math.isfinite(value):
        raise ValueError(f"non-finite {key!r} in {source}")
    return value


def _sobol_case(metric_path: Path, source_root: Path) -> RankedHamiltonianCase:
    case_dir = metric_path.parent
    complete = case_dir / "COMPLETE.json"
    metadata_path = case_dir / "metadata.json"
    if not complete.is_file() or not metadata_path.is_file():
        raise ValueError(f"incomplete Sobol case at {case_dir}")
    metrics = _read_json(metric_path)
    metadata = _read_json(metadata_path)
    point = metadata.get("configuration")
    if not isinstance(point, dict):
        raise ValueError(f"missing configuration object in {metadata_path}")
    graph = metadata.get("detector_graph")
    graph_spec = None
    connectivity = "ring"
    if isinstance(graph, dict):
        raw_spec = graph.get("spec")
        if not isinstance(raw_spec, dict):
            raise ValueError(f"missing detector_graph.spec in {metadata_path}")
        graph_spec = dict(raw_spec)
        connectivity = str(graph.get("canonical_kind", raw_spec.get("kind")))
    relative = case_dir.relative_to(source_root).as_posix()
    return RankedHamiltonianCase(
        source_root=str(source_root),
        source_case=relative,
        source_metric_file=str(metric_path.relative_to(source_root)),
        source_s_born=_finite_float(metrics, "S_born", metric_path),
        source_n=int(metadata["N"]),
        hz=_finite_float(point, "hz", metadata_path),
        hz0=_finite_float(metadata, "hz0", metadata_path),
        j=_finite_float(point, "j", metadata_path),
        jpm=_finite_float(point, "jpm", metadata_path),
        jx=_finite_float(point, "jx", metadata_path),
        jy=float(point.get("jy", 0.0)),
        j2=float(point.get("j2", metadata.get("J2", 0.0))),
        jpm2=float(point.get("jpm2", metadata.get("Jpm2", 0.0))),
        connectivity=connectivity,
        central_coupling="all",
        evolution_time=_finite_float(metadata, "evolution_time", metadata_path),
        model_seed=int(metadata.get("model_seed", 44)),
        graph_spec=graph_spec,
        source_graph_metadata=dict(graph) if isinstance(graph, dict) else None,
    )


def _atlas_case(metric_path: Path, source_root: Path) -> RankedHamiltonianCase:
    relative = metric_path.relative_to(source_root / "metrics")
    metadata_path = source_root / "raw" / relative.parent / "metadata.json"
    spectrum_paths = tuple((source_root / "raw" / relative.parent).glob("spectrum_*.npz"))
    if not metadata_path.is_file() or not spectrum_paths:
        raise ValueError(f"incomplete atlas case for {metric_path}")
    metrics = _read_json(metric_path)
    metadata = _read_json(metadata_path)
    case = metadata.get("case")
    if not isinstance(case, dict):
        case = metrics.get("case")
    if not isinstance(case, dict):
        raise ValueError(f"missing case object in {metadata_path}")
    return RankedHamiltonianCase(
        source_root=str(source_root),
        source_case=relative.parent.as_posix(),
        source_metric_file=str(metric_path.relative_to(source_root)),
        source_s_born=_finite_float(metrics, "S_born", metric_path),
        source_n=int(case["detector_n"]),
        hz=_finite_float(case, "hz", metadata_path),
        hz0=_finite_float(case, "hz0", metadata_path),
        j=_finite_float(case, "j", metadata_path),
        jpm=_finite_float(case, "jpm", metadata_path),
        jx=_finite_float(case, "jx", metadata_path),
        connectivity="ring",
        central_coupling="all",
        evolution_time=_finite_float(case, "evolution_time", metadata_path),
        model_seed=int(case.get("seed", 44)),
    )


def load_ranked_cases(source_root: Path) -> list[RankedHamiltonianCase]:
    """Load all validated cases in ``source_root``, ordered by ``S_born``."""

    source_root = Path(source_root).resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(f"source result folder does not exist: {source_root}")
    cases: list[RankedHamiltonianCase] = []
    atlas_metrics = source_root / "metrics"
    if atlas_metrics.is_dir():
        for metric_path in sorted(atlas_metrics.rglob("diagnostics.json")):
            relative = metric_path.relative_to(atlas_metrics)
            raw_dir = source_root / "raw" / relative.parent
            if not (raw_dir / "metadata.json").is_file():
                continue
            if not any(raw_dir.glob("spectrum_*.npz")):
                continue
            cases.append(_atlas_case(metric_path, source_root))
    else:
        for metric_path in sorted(source_root.rglob("metrics.json")):
            if not (metric_path.parent / "COMPLETE.json").is_file():
                continue
            if not (metric_path.parent / "metadata.json").is_file():
                continue
            cases.append(_sobol_case(metric_path, source_root))
    if not cases:
        raise ValueError(f"no validated cases with S_born found in {source_root}")
    return sorted(
        cases,
        key=lambda case: (-case.source_s_born, case.source_case),
    )


def top_ranked_cases(
    source_root: Path,
    count: int,
) -> list[RankedHamiltonianCase]:
    """Return exactly ``count`` highest-``S_born`` validated source cases."""

    if count < 1:
        raise ValueError("count must be positive")
    cases = load_ranked_cases(source_root)
    if len(cases) < count:
        raise ValueError(
            f"requested top {count}, but {source_root} has only {len(cases)} cases"
        )
    return cases[:count]


def graph_spec_for_case(case: RankedHamiltonianCase) -> DetectorGraphSpec:
    """Resolve the graph generator used by ``case`` for a target detector N."""

    if case.graph_spec is None:
        return DetectorGraphSpec(kind=case.connectivity, seed=case.model_seed)
    return DetectorGraphSpec(**case.graph_spec)


def hz0_variants(
    hz: float,
    offsets: Sequence[float],
    *,
    include_zero: bool = True,
) -> list[tuple[str, float, tuple[str, ...]]]:
    """Return unique central-field values and all requested aliases.

    ``offsets`` are additive: each requests ``hz0 = hz + offset``.  Values
    equal at 14 significant digits are simulated only once.
    """

    requested: list[tuple[str, float]] = []
    if include_zero:
        requested.append(("zero", 0.0))
    for offset in offsets:
        if not math.isfinite(offset):
            raise ValueError("hz0 offsets must be finite")
        if offset == 0.0:
            label = "matched"
        else:
            sign = "p" if offset > 0.0 else "m"
            magnitude = f"{abs(offset):.0e}".replace("-", "m").replace("+", "p")
            label = f"matched_{sign}{magnitude}"
        requested.append((label, float(hz + offset)))
    grouped: dict[float, tuple[float, list[str]]] = {}
    for label, value in requested:
        key = round(value, 14)
        if key not in grouped:
            grouped[key] = (value, [])
        grouped[key][1].append(label)
    return [
        ("__".join(aliases), value, tuple(aliases))
        for value, aliases in grouped.values()
    ]


def selected_case_output_dir(
    output_root: Path,
    source_index: int,
    rank_index: int,
    detector_n: int,
    variant_label: str | None = None,
) -> Path:
    path = (
        Path(output_root)
        / f"source_{source_index + 1:02d}"
        / f"rank_{rank_index + 1:03d}"
        / f"N{detector_n}"
    )
    return path if variant_label is None else path / f"hz0_{variant_label}"


def _complete_valid(case_dir: Path) -> bool:
    marker_path = case_dir / "COMPLETE.json"
    if not marker_path.is_file():
        return False
    try:
        marker = _read_json(marker_path)
        files = marker["files"]
        return marker.get("status") == "complete" and all(
            (case_dir / name).is_file()
            and _sha256(case_dir / name) == expected
            for name, expected in files.items()
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def simulate_ranked_case(
    case: RankedHamiltonianCase,
    *,
    detector_n: int,
    hz0: float,
    case_dir: Path,
    source_index: int,
    rank_index: int,
    hz0_aliases: Sequence[str] = (),
    bins: int = 64,
    plot_grid: int = 720,
    fit_harmonics: int = 32,
    fit_tolerance: float = 1.0e-10,
    max_bloch_points: int = 6000,
    resume: bool = True,
    graph_spec_override: DetectorGraphSpec | None = None,
    graph_provenance: dict[str, Any] | None = None,
    selection_label: str | None = None,
) -> dict[str, Any]:
    """Run and atomically persist one selected Hamiltonian configuration."""

    case_dir = Path(case_dir)
    if detector_n < 3:
        raise ValueError("detector_n must be at least three")
    if resume and _complete_valid(case_dir):
        return {
            "status": "resumed",
            "source_index": source_index,
            "rank": rank_index + 1,
            "N": detector_n,
            "case_dir": str(case_dir),
        }
    if case_dir.exists() and any(case_dir.iterdir()) and not resume:
        raise FileExistsError(f"non-empty output case directory: {case_dir}")
    case_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    graph_spec = (
        graph_spec_override
        if graph_spec_override is not None
        else graph_spec_for_case(case)
    )
    graph_metadata = detector_graph_metadata(detector_n, graph_spec)
    jx_effective = case.jx / math.sqrt(detector_n)
    jy_effective = case.jy / math.sqrt(detector_n)
    hamiltonian = SinglePixelHamiltonianQuSpin(
        N_pixel=detector_n,
        J=case.j,
        Jpm=case.jpm,
        J2=case.j2,
        Jpm2=case.jpm2,
        Jx=jx_effective,
        Jy=jy_effective,
        Jz=0.0,
        Jzx=0.0,
        hx=0.0,
        hz=case.hz,
        hx0=0.0,
        hz0=hz0,
        connectivity=case.connectivity,
        graph_spec=graph_spec,
        central_coupling=case.central_coupling,
        seed=case.model_seed,
        use_symmetry=True,
    )
    diagonalization_started = time.perf_counter()
    sectors = hamiltonian.diagonalize_sectors()
    diagonalization_seconds = time.perf_counter() - diagonalization_started
    analysis_started = time.perf_counter()
    analyzer = DisentanglementAnalyzer.from_sectors(
        sectors,
        case.evolution_time,
        detector_n + 1,
    )
    eigenvalues = np.asarray(analyzer.D0, dtype=np.complex128)
    analysis_seconds = time.perf_counter() - analysis_started
    metrics, arrays = _diagnostics(eigenvalues, bins)
    fits, fit_arrays = fit_distributions(
        arrays["theta"],
        bins,
        plot_grid,
        fit_harmonics,
        fit_tolerance,
    )
    expected_count = 2**detector_n
    validation = {
        "passed": bool(
            eigenvalues.size == expected_count
            and np.all(np.isfinite(eigenvalues.real))
            and np.all(np.isfinite(eigenvalues.imag))
            and abs(float(metrics["p_theta_integral"]) - 1.0) < 1.0e-10
            and abs(float(metrics["p_reflected_integral"]) - 1.0) < 1.0e-10
        ),
        "expected_eigenvalue_count": expected_count,
        "actual_eigenvalue_count": int(eigenvalues.size),
        "finite_eigenvalues": bool(
            np.all(np.isfinite(eigenvalues.real))
            and np.all(np.isfinite(eigenvalues.imag))
        ),
    }
    _atomic_npz(case_dir / "results.npz", **arrays, **fit_arrays)
    _atomic_json(case_dir / "metrics.json", metrics)
    _atomic_json(case_dir / "fits.json", fits)
    _atomic_json(case_dir / "validation.json", validation)
    metadata = {
        "created": timestamp(),
        "source_index": source_index,
        "source_rank": rank_index + 1,
        "source": asdict(case),
        "target_N": detector_n,
        "total_qubits": detector_n + 1,
        "hz0": hz0,
        "hz0_aliases": list(hz0_aliases),
        "Jx_unscaled": case.jx,
        "Jx_effective": jx_effective,
        "Jy_unscaled": case.jy,
        "Jy_effective": jy_effective,
        "collective_scaling": "Jx/sqrt(N) and Jy/sqrt(N), applied once",
        "detector_graph": graph_metadata,
        "graph_provenance": (
            dict(graph_provenance)
            if graph_provenance is not None
            else {
                "mode": "source_generator_spec",
                "note": (
                    "The saved generator specification and seed are reused. "
                    "If target_N differs from source_n, this deterministically "
                    "generates a new graph; it is not a scaled source graph."
                ),
            }
        ),
        "selection_label": selection_label,
        "central_coupling": case.central_coupling,
        "symmetry_labels": sorted(
            {str(sector.get("symmetry_label", "unknown")) for sector in sectors}
        ),
        "sector_count": len(sectors),
        "diagonalization_seconds": diagonalization_seconds,
        "analysis_seconds": analysis_seconds,
        "peak_rss_mb": _peak_rss_mb(),
        "worker": multiprocessing.current_process().name,
        "pid": os.getpid(),
        "runtime": _runtime_provenance(),
    }
    _atomic_json(case_dir / "metadata.json", metadata)
    title_lead = selection_label or f"Born rank {rank_index + 1}"
    second_neighbor_title = ""
    if case.j2 or case.jpm2:
        second_neighbor_title = (
            rf", $J_2={case.j2:.4g}$, $J_{{\pm2}}={case.jpm2:.4g}$"
        )
    title = "\n".join(
        (
            rf"Selected {title_lead}: $N={detector_n}$, "
            rf"$h_z={case.hz:.4g}$, $h_{{z0}}={hz0:.4g}$",
            rf"$J={case.j:.4g}$, $J_{{\pm}}={case.jpm:.4g}$"
            + second_neighbor_title,
            rf"$J_{{x,\rm unscaled}}={case.jx:.4g}$, "
            rf"$J_{{x,\rm eff}}=J_x/\sqrt{{N}}={jx_effective:.4g}$, "
            rf"$S_{{Born}}^{{src}}={case.source_s_born:.4f}$",
        )
    )
    _plot_case(
        case_dir / "blue_red_diagnostics.png",
        case_dir / "fit_diagnostics.png",
        title,
        arrays,
        fit_arrays,
        fits,
        metrics,
        max_bloch_points,
    )
    if not validation["passed"]:
        raise RuntimeError(f"scientific validation failed for {case_dir}")
    required = (
        "results.npz",
        "metrics.json",
        "fits.json",
        "validation.json",
        "metadata.json",
        "blue_red_diagnostics.png",
        "fit_diagnostics.png",
    )
    marker = {
        "status": "complete",
        "completed": timestamp(),
        "runtime_seconds": time.perf_counter() - started,
        "source_identity_digest": case.identity_digest,
        "files": {name: _sha256(case_dir / name) for name in required},
    }
    _atomic_json(case_dir / "COMPLETE.json", marker)
    del analyzer, sectors, hamiltonian, eigenvalues, arrays, fit_arrays
    gc.collect()
    return {
        "status": "success",
        "source_index": source_index,
        "rank": rank_index + 1,
        "N": detector_n,
        "hz0": hz0,
        "S_born": metrics["S_born"],
        "runtime_seconds": marker["runtime_seconds"],
        "case_dir": str(case_dir),
    }


def selection_manifest(
    sources: Iterable[Path],
    count: int,
) -> dict[str, Any]:
    """Build a complete, JSON-serializable ranking manifest."""

    records = []
    for source_index, source in enumerate(sources):
        selected = top_ranked_cases(source, count)
        records.append(
            {
                "source_index": source_index,
                "source_root": str(Path(source).resolve()),
                "selected_count": len(selected),
                "ranking_metric": "S_born descending; source_case ascending tie-break",
                "cases": [
                    {"rank": rank + 1, **asdict(case)}
                    for rank, case in enumerate(selected)
                ],
            }
        )
    return {"created": timestamp(), "sources": records}
