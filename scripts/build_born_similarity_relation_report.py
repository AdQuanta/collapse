"""Build figures and numerical summaries for the Born-similarity report."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


@dataclass(frozen=True)
class Record:
    dataset: str
    group: str
    s_born: float
    coverage: float
    rmse: float
    entropy_normalized: float
    d_wg: float
    d_wc: float
    w_degenerate: float
    w_low_gap: float


def theta_metrics(theta: np.ndarray, bins: int = 64) -> tuple[float, float, float]:
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    blue, _ = np.histogram(theta, bins=edges)
    red, _ = np.histogram(np.pi - theta, bins=edges)
    occupied = blue + red > 0
    ratio = np.divide(blue, blue + red, out=np.full(bins, np.nan), where=occupied)
    born = np.cos(centers / 2.0) ** 2
    rmse = float(np.sqrt(np.mean((ratio[occupied] - born[occupied]) ** 2)))
    probabilities = blue / blue.sum()
    nonzero = probabilities > 0
    entropy = float(-np.sum(probabilities[nonzero] * np.log(probabilities[nonzero])) / np.log(bins))
    return float(np.mean(occupied)), rmse, entropy


def gap_metrics(payload: str | dict[str, object]) -> tuple[float, float]:
    gap = json.loads(payload) if isinstance(payload, str) else payload
    weights = np.asarray(gap["weights"], dtype=float)
    edges = np.asarray(gap["edges"], dtype=float)
    low = float(weights[edges[:-1] < 0.025 + 1e-15].sum())
    return float(gap["exact_degenerate_weight"]), low


def load_anisotropic(root: Path) -> list[Record]:
    index = root / "reports/vab_coupling_group_atlas_2026-07-28/flat_ranked_2x3_N14/ranked_index.csv"
    records = []
    with index.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["status"] != "rendered":
                continue
            with np.load(row["raw_path"]) as raw:
                coverage, rmse, entropy = theta_metrics(np.asarray(raw["theta"], dtype=float))
            wdeg, wlow = gap_metrics(row["gap_weight_histogram_json"])
            group = f"hz={row['hz']}|J={row['j']}|Jpm={row['jpm']}"
            records.append(Record(
                "anisotropic grid", group, float(row["computed_s_born"]), coverage, rmse,
                entropy, float(row["wg_fourier_discrepancy"]),
                float(row["wc_fourier_discrepancy"]), wdeg, wlow,
            ))
    return records


def load_sobol(root: Path) -> tuple[list[Record], int]:
    path = root / "work/zeus_sobol_coupling_scans_20260726_200003/flat_ranked_2x3_by_n/render_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for item in manifest["results"]:
        source = Path(item["source_dir"])
        metrics = json.loads((source / "metrics.json").read_text(encoding="utf-8"))
        fits = json.loads((source / "fits.json").read_text(encoding="utf-8"))
        wdeg, wlow = gap_metrics(item["gap_weight_histogram_json"])
        records.append(Record(
            "Sobol scan", f"{item['family']}|{item['config_id']}", float(metrics["S_born"]),
            float(metrics["occupied_fraction"]), float(metrics["born_RMSE_occupied"]),
            float(metrics["theta_entropy"]) / np.log(64.0),
            float(fits["wrapped_gaussian"]["fourier_discrepancy"]),
            float(fits["wrapped_cauchy"]["fourier_discrepancy"]), wdeg, wlow,
        ))
    return records, int(manifest["unavailable_transferred_records"])


def design(records: list[Record]) -> tuple[np.ndarray, np.ndarray]:
    c = np.asarray([r.coverage for r in records])
    e = np.asarray([r.rmse for r in records])
    return np.column_stack([np.ones(len(records)), c, c * e]), np.asarray([r.s_born for r in records])


def fit(records: list[Record]) -> tuple[np.ndarray, float]:
    x, y = design(records)
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    pred = x @ beta
    return beta, float(1.0 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))


def fold(group: str, folds: int = 10) -> int:
    return int.from_bytes(hashlib.sha256(group.encode()).digest()[:8], "little") % folds


def grouped_cv(records: list[Record], folds: int = 10) -> tuple[np.ndarray, float, float]:
    x, y = design(records)
    labels = np.asarray([fold(r.dataset + "|" + r.group, folds) for r in records])
    prediction = np.full(len(records), np.nan)
    for k in range(folds):
        train, test = labels != k, labels == k
        prediction[test] = x[test] @ np.linalg.lstsq(x[train], y[train], rcond=None)[0]
    r2 = 1.0 - np.sum((y - prediction) ** 2) / np.sum((y - y.mean()) ** 2)
    return prediction, float(r2), float(np.sqrt(np.mean((y - prediction) ** 2)))


def rho(records: list[Record], key: str, broad: bool = False) -> float:
    selected = [r for r in records if not broad or r.coverage >= 0.75]
    return float(spearmanr([getattr(r, key) for r in selected], [r.s_born for r in selected]).statistic)


def bootstrap(records: list[Record], draws: int = 1000) -> np.ndarray:
    rng = np.random.default_rng(20260731)
    values = np.empty((draws, 3))
    for index in range(draws):
        values[index] = fit([records[i] for i in rng.integers(0, len(records), len(records))])[0]
    return np.quantile(values, [0.025, 0.975], axis=0)


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9.0, "axes.titlesize": 10.5,
        "axes.labelsize": 9.5, "legend.fontsize": 8.2, "xtick.labelsize": 8,
        "ytick.labelsize": 8, "axes.spines.top": False, "axes.spines.right": False,
        "figure.dpi": 150, "savefig.dpi": 300,
    })


def plot_map(records: list[Record], beta: np.ndarray, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.15, 3.25), sharex=True, sharey=True, constrained_layout=True)
    scatter = None
    for ax, dataset in zip(axes, ["anisotropic grid", "Sobol scan"], strict=True):
        subset = [r for r in records if r.dataset == dataset]
        scatter = ax.scatter(
            [r.rmse for r in subset], [r.coverage for r in subset], c=[r.s_born for r in subset],
            cmap="RdYlGn", vmin=-0.5, vmax=1.0, s=11, alpha=0.74, edgecolors="none", rasterized=True,
        )
        ee, cc = np.meshgrid(np.linspace(0.0, 0.48, 241), np.linspace(0.0, 1.0, 241))
        zz = beta[0] + beta[1] * cc + beta[2] * cc * ee
        contours = ax.contour(ee, cc, zz, levels=[0.4, 0.75], colors=["#4b4b4b", "#111111"],
                              linestyles=["--", "-"], linewidths=[1.0, 1.2])
        ax.clabel(contours, fmt={0.4: r"$\widehat S_B=0.40$", 0.75: r"$\widehat S_B=0.75$"}, fontsize=7)
        ax.set_title(f"{dataset.capitalize()} (n={len(subset)})")
        ax.set_xlabel(r"Occupied-bin error $\varepsilon_R$")
        ax.grid(alpha=0.18, linewidth=0.5)
    axes[0].set_ylabel(r"Angular coverage $C$")
    bar = fig.colorbar(scatter, ax=axes, pad=0.02, shrink=0.92)
    bar.set_label(r"Observed $S_{\rm Born}$")
    fig.savefig(out / "coverage_rmse_map.pdf", bbox_inches="tight")
    fig.savefig(out / "coverage_rmse_map.png", bbox_inches="tight")
    plt.close(fig)


def plot_validation(records: list[Record], prediction: np.ndarray, out: Path) -> dict[str, dict[str, float]]:
    fig, axes = plt.subplots(1, 2, figsize=(8.15, 3.35), constrained_layout=True)
    y = np.asarray([r.s_born for r in records])
    colors = {"anisotropic grid": "#2878b5", "Sobol scan": "#c73e3a"}
    markers = {"anisotropic grid": "o", "Sobol scan": "^"}
    for dataset in colors:
        mask = np.asarray([r.dataset == dataset for r in records])
        axes[0].scatter(y[mask], prediction[mask], s=13, alpha=0.55, color=colors[dataset],
                        marker=markers[dataset], edgecolors="none", label=dataset.capitalize())
    limits = [-0.55, 1.02]
    axes[0].plot(limits, limits, color="#222222", linewidth=1.0, linestyle="--")
    axes[0].set(xlim=limits, ylim=limits, xlabel=r"Observed $S_{\rm Born}$",
                ylabel="Grouped-CV prediction", title="Out-of-sample validation")
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].legend(frameon=False, loc="lower right")
    axes[0].grid(alpha=0.18, linewidth=0.5)

    specs = [
        ("coverage", r"Coverage $C$", False, 1.0),
        ("entropy_normalized", r"Entropy $H_\theta/\log 64$", False, 1.0),
        ("d_wg", r"WG discrepancy $D_{\rm WG}$", False, 1.0),
        ("w_low_gap", r"Low-gap weight $W_{\Delta\leq0.025}$", False, 1.0),
        ("w_degenerate", r"Strict-degenerate weight $W_{\rm deg}$", False, 1.0),
        ("rmse", r"$-\varepsilon_R$ for $C\geq0.75$", True, -1.0),
        ("w_low_gap", r"Low-gap weight for $C\geq0.75$", True, 1.0),
        ("w_degenerate", r"$W_{\rm deg}$ for $C\geq0.75$", True, 1.0),
    ]
    correlations = {name: {} for name in colors}
    positions = np.arange(len(specs))
    for offset, dataset in [(-0.17, "anisotropic grid"), (0.17, "Sobol scan")]:
        subset = [r for r in records if r.dataset == dataset]
        values = []
        for key, label, broad, sign in specs:
            value = sign * rho(subset, key, broad)
            values.append(value)
            correlations[dataset][label] = value
        axes[1].barh(positions + offset, values, height=0.30, color=colors[dataset], alpha=0.82,
                     label=dataset.capitalize())
    axes[1].axvline(0, color="#333333", linewidth=0.8)
    axes[1].set_yticks(positions, [spec[1] for spec in specs])
    axes[1].invert_yaxis()
    axes[1].set_xlim(-0.1, 1.0)
    axes[1].set_xlabel(r"Spearman $\rho$ with $S_{\rm Born}$")
    axes[1].set_title("What tracks Born similarity?")
    axes[1].grid(axis="x", alpha=0.18, linewidth=0.5)
    axes[1].legend(frameon=False, loc="lower right")
    fig.savefig(out / "validation_correlations.pdf", bbox_inches="tight")
    fig.savefig(out / "validation_correlations.png", bbox_inches="tight")
    plt.close(fig)
    return correlations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("reports/born_similarity_relation_2026-07-31"))
    args = parser.parse_args()
    root = args.root.resolve()
    out = (root / args.output).resolve() if not args.output.is_absolute() else args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    style()

    anisotropic = load_anisotropic(root)
    sobol, unavailable = load_sobol(root)
    records = anisotropic + sobol
    beta, r2 = fit(records)
    prediction, cv_r2, cv_rmse = grouped_cv(records)
    ci = bootstrap(records)
    plot_map(records, beta, out)
    correlations = plot_validation(records, prediction, out)

    dataset_fits = {}
    for name, subset in [("anisotropic", anisotropic), ("sobol", sobol)]:
        b, score = fit(subset)
        _, cv_score, cv_error = grouped_cv(subset)
        dataset_fits[name] = {"n": len(subset), "coefficients": b.tolist(), "r2": score,
                              "grouped_cv_r2": cv_score, "grouped_cv_rmse": cv_error}
    summary = {
        "records": len(records), "anisotropic_records": len(anisotropic), "sobol_records": len(sobol),
        "unavailable_sobol_records": unavailable,
        "model": "S_hat = beta_0 + beta_C*C + beta_Ce*C*epsilon_R",
        "coefficients": beta.tolist(), "r2": r2, "grouped_cv_r2": cv_r2,
        "grouped_cv_rmse": cv_rmse, "bootstrap_95_percent_ci": ci.tolist(),
        "dataset_fits": dataset_fits, "spearman_correlations": correlations,
        "definitions": {
            "coverage": "fraction of 64 theta bins with P(theta)+P(pi-theta)>0",
            "rmse": "unweighted RMSE of R(theta) against cos^2(theta/2) on occupied bins",
            "entropy_normalized": "discrete 64-bin entropy of P(theta), divided by log(64)",
            "low_gap_weight": "normalized |V_ab|^2 weight for normalized energy gap below 0.025",
        },
    }
    (out / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (out / "relation_records.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(asdict(records[0])))
        writer.writeheader()
        writer.writerows(asdict(r) for r in records)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

