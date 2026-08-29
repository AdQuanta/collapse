"""Render the expanded Hamiltonian sweep in the established 3xL atlas style.

Rows show mirrored angular histograms, the Born-ratio diagnostic, and the two
antipodal Bloch branches.  Columns are configuration-defined Hamiltonian cases.
Raw relative-unitary eigenvalues are cached per case and time so figure-only
reruns do not repeat diagonalization.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.distribution_fit import fit_folded_circular_models
from scripts.born_hamiltonian_search import (
    _analyzer_from_diagonalization,
    _candidate_from_result,
    _diagonalize_candidate,
)
from scripts.compare_two_pixel_single_pixel import bloch_branches, wire_sphere


BLUE = "#1677b8"
RED = "#df2b2f"
RATIO = "#6a3d7a"


@dataclass(frozen=True)
class AtlasCase:
    case_id: str
    label: str


@dataclass(frozen=True)
class AtlasGroup:
    group_id: str
    title: str
    cases: tuple[AtlasCase, ...]


@dataclass(frozen=True)
class AngularDistributions:
    edges: np.ndarray
    centers: np.ndarray
    p_theta: np.ndarray
    p_reflected: np.ndarray
    ratio: np.ndarray
    born: np.ndarray
    gaussian: np.ndarray
    gaussian_reflected: np.ndarray


class SweepConfiguration:
    """Read rendering groups without embedding study-specific labels in code."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.payload = json.loads(path.read_text(encoding="utf-8"))

    @property
    def groups(self) -> tuple[AtlasGroup, ...]:
        groups: list[AtlasGroup] = []
        for item in self.payload.get("atlas_groups", []):
            cases = tuple(AtlasCase(str(case_id), str(label)) for case_id, label in item["cases"])
            groups.append(AtlasGroup(str(item["id"]), str(item["title"]), cases))
        if not groups:
            raise ValueError(f"No atlas_groups are defined in {self.path}")
        return tuple(groups)


class CampaignResults:
    """Provide completed per-case result records and their raw-cache paths."""

    def __init__(self, run_root: Path) -> None:
        self.run_root = run_root

    def result_path(self, case_id: str) -> Path:
        return self.run_root / case_id / "results.json"

    def raw_path(self, case_id: str, time_value: float) -> Path:
        return self.run_root / case_id / "atlas_raw" / f"raw_t{time_token(time_value)}.npz"

    def load(self, case_id: str) -> list[dict[str, Any]]:
        path = self.result_path(case_id)
        if not path.is_file():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return sorted(payload.get("results", []), key=lambda row: float(row["t"]))

    def available(self, case_id: str) -> bool:
        return bool(self.load(case_id))


class DistributionService:
    """Calculate the three atlas rows independently of plotting and I/O."""

    def __init__(self, bins: int) -> None:
        if bins < 4:
            raise ValueError("bins must be at least 4")
        self.edges = np.linspace(0.0, np.pi, bins + 1)
        self.centers = 0.5 * (self.edges[:-1] + self.edges[1:])

    def calculate(self, eigenvalues: np.ndarray) -> AngularDistributions:
        values = np.asarray(eigenvalues, dtype=np.complex128).ravel()
        finite = np.isfinite(values.real) & np.isfinite(values.imag)
        theta = 2.0 * np.arctan(np.abs(values[finite]))
        counts, _ = np.histogram(theta, bins=self.edges)
        # With a symmetric grid, reversing bin masses is the exact discrete
        # push-forward theta -> pi-theta and avoids floating-point edge drift.
        reflected_counts = counts[::-1]
        widths = np.diff(self.edges)
        normalizer = max(theta.size, 1)
        p_theta = counts / normalizer / widths
        p_reflected = reflected_counts / normalizer / widths
        total = counts + reflected_counts
        ratio = np.divide(
            counts,
            total,
            out=np.full(counts.shape, np.nan, dtype=float),
            where=total > 0,
        )
        fit = fit_folded_circular_models(theta, self.edges)
        gaussian = fit.wrapped_gaussian_probabilities / widths
        return AngularDistributions(
            edges=self.edges,
            centers=self.centers,
            p_theta=p_theta,
            p_reflected=p_reflected,
            ratio=ratio,
            born=np.cos(self.centers / 2.0) ** 2,
            gaussian=gaussian,
            gaussian_reflected=gaussian[::-1],
        )


def time_token(value: float) -> str:
    return f"{float(value):g}".replace("+", "").replace(".", "p")


def _load_eigenvalues(path: Path) -> np.ndarray:
    with np.load(path) as payload:
        return np.asarray(payload["eigenvalues"], dtype=np.complex128)


def _materialize_case(payload: tuple[str, str, bool]) -> tuple[str, int]:
    result_path_text, run_root_text, force = payload
    result_path = Path(result_path_text)
    case_id = result_path.parent.name
    data = json.loads(result_path.read_text(encoding="utf-8"))
    results = sorted(data["results"], key=lambda row: float(row["t"]))
    raw_dir = Path(run_root_text) / case_id / "atlas_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    missing = [
        row for row in results
        if force or not (raw_dir / f"raw_t{time_token(float(row['t']))}.npz").is_file()
    ]
    if not missing:
        return case_id, 0
    candidate = _candidate_from_result(results[0])
    diagonalization = _diagonalize_candidate(candidate, str(results[0].get("backend", "auto")))
    written = 0
    for row in missing:
        time_value = float(row["t"])
        analyzer = _analyzer_from_diagonalization(diagonalization, time_value, candidate.N)
        eigenvalues = np.asarray(analyzer.D0, dtype=np.complex128)
        destination = raw_dir / f"raw_t{time_token(time_value)}.npz"
        np.savez_compressed(
            destination,
            eigenvalues=eigenvalues,
            theta=2.0 * np.arctan(np.abs(eigenvalues)),
            time=time_value,
            case_id=case_id,
            N=candidate.N,
            N_pixel=candidate.N_pixel,
            Jx_scaled=candidate.Jx,
            Jy_scaled=candidate.Jy,
        )
        written += 1
    return case_id, written


class RawSpectrumCache:
    """Checkpoint eigenvalue spectra, parallelizing only independent cases."""

    def __init__(self, repository: CampaignResults) -> None:
        self.repository = repository

    def materialize(self, case_ids: Iterable[str], workers: int, force: bool) -> None:
        unique = sorted({case_id for case_id in case_ids if self.repository.result_path(case_id).is_file()})
        payloads = [
            (str(self.repository.result_path(case_id)), str(self.repository.run_root), force)
            for case_id in unique
        ]
        if workers <= 1:
            for payload in payloads:
                case_id, written = _materialize_case(payload)
                print(f"atlas raw {case_id}: {written} new spectra", flush=True)
            return
        with ProcessPoolExecutor(max_workers=min(workers, len(payloads))) as pool:
            futures = [pool.submit(_materialize_case, payload) for payload in payloads]
            for future in as_completed(futures):
                case_id, written = future.result()
                print(f"atlas raw {case_id}: {written} new spectra", flush=True)


class AtlasPlotter:
    """Apply the reference report's blue/red 3xL rendering policy."""

    def __init__(
        self,
        repository: CampaignResults,
        figure_root: Path,
        bins: int,
        columns_per_page: int,
        max_bloch_points: int,
    ) -> None:
        self.repository = repository
        self.figure_root = figure_root
        self.distributions = DistributionService(bins)
        self.columns_per_page = columns_per_page
        self.max_bloch_points = max_bloch_points

    @staticmethod
    def _metrics_text(result: dict[str, Any]) -> str:
        metrics = result["metrics"]
        try:
            reciprocity = float(metrics.get("reciprocity_error", math.nan))
        except (TypeError, ValueError):
            reciprocity = math.nan
        reciprocity_text = f"{reciprocity:.2f}" if math.isfinite(reciprocity) else "n/a"
        return (
            rf"$S={float(metrics['born_similarity']):.2f}$, "
            rf"$\alpha={float(metrics['tail_density_exponent']):.2f}$" + "\n" +
            rf"$U_\phi={float(metrics['phi_uniformity_score']):.2f}$, "
            rf"$\epsilon_{{rec}}={reciprocity_text}$"
        )

    def _plot_histogram(self, ax, dist: AngularDistributions, first: bool) -> None:
        ax.stairs(dist.p_theta, dist.edges, color=BLUE, linewidth=1.35, fill=True, alpha=0.13,
                  label=r"$P(\theta)$")
        ax.stairs(dist.p_reflected, dist.edges, color=RED, linewidth=1.3, fill=True, alpha=0.10,
                  label=r"$P(\pi-\theta)$")
        ax.plot(dist.centers, dist.gaussian, color=BLUE, linestyle="-.", linewidth=0.9,
                label="best-fit WG")
        ax.plot(dist.centers, dist.gaussian_reflected, color=RED, linestyle=":", linewidth=1.0,
                label="reflected WG")
        ax.set_xlim(0.0, np.pi)
        ax.grid(alpha=0.16)
        ax.tick_params(labelbottom=False, labelsize=8)
        if first:
            ax.set_ylabel("density")
            ax.legend(fontsize=6.8, frameon=False, ncol=2, loc="upper center")

    def _plot_ratio(self, ax, dist: AngularDistributions, result: dict[str, Any], first: bool) -> None:
        occupied = np.isfinite(dist.ratio)
        ax.plot(
            dist.centers[occupied], dist.ratio[occupied], "o-", color=RATIO,
            linewidth=0.9, markersize=2.8, label=r"$R(\theta)$",
        )
        ax.plot(dist.centers, dist.born, color="black", linestyle="--", linewidth=1.15,
                label=r"$\cos^2(\theta/2)$")
        ax.set(xlim=(0.0, np.pi), ylim=(-0.04, 1.04), xlabel=r"$\theta$")
        ax.grid(alpha=0.16)
        ax.tick_params(labelsize=8)
        ax.text(
            0.03, 0.06, self._metrics_text(result), transform=ax.transAxes, fontsize=7.2,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.4},
        )
        if first:
            ax.set_ylabel(r"$R(\theta)$")
            ax.legend(fontsize=7, frameon=False, loc="upper center")

    def _plot_bloch(self, ax, eigenvalues: np.ndarray, first: bool) -> None:
        branch0, branch1 = bloch_branches(eigenvalues)
        wire_sphere(ax)
        if branch0.size:
            indices = np.linspace(
                0, branch0.shape[0] - 1,
                min(branch0.shape[0], self.max_bloch_points), dtype=int,
            )
            ax.scatter(*branch0[indices].T, s=5.0, marker="o", color=BLUE, alpha=0.32,
                       depthshade=False)
            ax.scatter(*branch1[indices].T, s=5.0, marker="o", color=RED, alpha=0.28,
                       depthshade=False)
        ax.set(xlim=(-1.04, 1.04), ylim=(-1.04, 1.04), zlim=(-1.04, 1.04))
        ax.set_box_aspect((1.0, 1.0, 1.0))
        ax.view_init(elev=22.0, azim=42.0)
        ax.set_axis_off()
        if first:
            ax.text2D(0.01, 0.02, "blue: P(theta) branch\nred: antipodal branch",
                      transform=ax.transAxes, fontsize=7.2)

    def plot_page(
        self,
        group: AtlasGroup,
        cases: tuple[AtlasCase, ...],
        time_value: float,
        page_index: int,
    ) -> Path:
        figure = plt.figure(figsize=(3.65 * len(cases), 10.6), constrained_layout=True)
        grid = figure.add_gridspec(3, len(cases), height_ratios=(1.0, 0.9, 1.35))
        n_total: int | None = None
        for column, atlas_case in enumerate(cases):
            result = next(
                row for row in self.repository.load(atlas_case.case_id)
                if math.isclose(float(row["t"]), time_value)
            )
            n_total = int(result["candidate"]["N"])
            eigenvalues = _load_eigenvalues(self.repository.raw_path(atlas_case.case_id, time_value))
            dist = self.distributions.calculate(eigenvalues)
            ax_hist = figure.add_subplot(grid[0, column])
            self._plot_histogram(ax_hist, dist, column == 0)
            ax_hist.set_title(atlas_case.label, fontsize=11)
            ax_ratio = figure.add_subplot(grid[1, column])
            self._plot_ratio(ax_ratio, dist, result, column == 0)
            ax_bloch = figure.add_subplot(grid[2, column], projection="3d")
            self._plot_bloch(ax_bloch, eigenvalues, column == 0)
        figure.suptitle(
            rf"Expanded single-pixel {group.title}: $N={n_total}$, "
            rf"unscaled central couplings $\leq0.01$ (applied$/\sqrt{{N_{{pixel}}}}$), "
            rf"$t={time_value:g}$",
            fontsize=15,
            fontweight="bold",
        )
        destination = (
            self.figure_root / "atlases" /
            f"{group.group_id}_t{time_token(time_value)}_page{page_index:02d}.png"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(destination, dpi=210, bbox_inches="tight", facecolor="white")
        plt.close(figure)
        return destination

    def render(self, groups: tuple[AtlasGroup, ...]) -> list[Path]:
        paths: list[Path] = []
        for group in groups:
            available = tuple(case for case in group.cases if self.repository.available(case.case_id))
            if not available:
                continue
            times = sorted({float(row["t"]) for case in available for row in self.repository.load(case.case_id)})
            for time_value in times:
                at_time = tuple(
                    case for case in available
                    if any(math.isclose(float(row["t"]), time_value) for row in self.repository.load(case.case_id))
                )
                for page_index, start in enumerate(range(0, len(at_time), self.columns_per_page), start=1):
                    paths.append(
                        self.plot_page(
                            group,
                            at_time[start : start + self.columns_per_page],
                            time_value,
                            page_index,
                        )
                    )
        return paths


def write_index(path: Path, figures: list[Path], raw_count: int) -> None:
    lines = [
        "# Expanded Hamiltonian atlas figures",
        "",
        "The figures use the established three-row report style: blue/red angular histograms with separately labelled best-fit wrapped-Gaussian diagnostics, connected R(theta) points against the Born curve, and antipodal Bloch-sphere branches.",
        "",
        f"- Cached raw spectra: {raw_count}",
        f"- Atlas pages: {len(figures)}",
        "",
        "## Pages",
        "",
    ]
    lines.extend(f"- `{figure.as_posix()}`" for figure in figures)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--figure-root", type=Path, required=True)
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument("--columns-per-page", type=int, default=5)
    parser.add_argument("--max-bloch-points", type=int, default=6000)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--force-raw", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.columns_per_page < 1:
        raise SystemExit("--columns-per-page must be positive")
    if args.workers < 1:
        raise SystemExit("--workers must be positive")
    configuration = SweepConfiguration(args.config)
    repository = CampaignResults(args.run_root)
    case_ids = [case.case_id for group in configuration.groups for case in group.cases]
    RawSpectrumCache(repository).materialize(case_ids, args.workers, args.force_raw)
    plotter = AtlasPlotter(
        repository,
        args.figure_root,
        bins=args.bins,
        columns_per_page=args.columns_per_page,
        max_bloch_points=args.max_bloch_points,
    )
    figures = plotter.render(configuration.groups)
    raw_count = sum(1 for case_id in set(case_ids) for _ in (args.run_root / case_id / "atlas_raw").glob("raw_t*.npz"))
    index = args.figure_root / "atlases" / "index.md"
    write_index(index, figures, raw_count)
    manifest = {
        "config": str(args.config.resolve()),
        "run_root": str(args.run_root.resolve()),
        "figure_root": str(args.figure_root.resolve()),
        "bins": args.bins,
        "columns_per_page": args.columns_per_page,
        "raw_spectra": raw_count,
        "atlas_pages": [str(path.resolve()) for path in figures],
        "wrapped_gaussian": "best-fit diagnostic, not a no-fit theoretical prediction",
    }
    (args.figure_root / "atlases" / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"raw_spectra": raw_count, "atlas_pages": len(figures)}, indent=2))


if __name__ == "__main__":
    main()
