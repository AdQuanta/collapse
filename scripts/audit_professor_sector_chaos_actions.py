#!/usr/bin/env python3.11
"""Audit the professor's sector-coupling, chaos, and simple-ring action items.

This script uses completed, immutable repository results only.  It does not
run a simulation.  The output is a compact evidence table, a four-panel
summary figure, and a Markdown report with explicit finite-size limitations.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from core.sobol_coupling_scan import _atomic_json, timestamp  # noqa: E402


DEFAULT_OUTPUT = ROOT / "reports" / "professor_action_items_2026-09-05"
CATALOG = ROOT / "reports" / "hz0_0_ring_spacing_born_10x4_2026-09-05" / "catalog.csv"
ACTIVATION = ROOT / "reports" / "ring_activation_hz0_diagnostics_2026-08-24" / "activation_band_summary.json"
RING_HZ0 = ROOT / "reports" / "ring_second_neighbor_wd_hz0_scan_N17_2026-08-26" / "hz0_scan_summary.csv"
NETWORK_HZ0 = ROOT / "reports" / "network_top_hz0_variants_N11_spacings_graph_all_2026-08-20"
FEATURES = ROOT / "reports" / "three_sobol_born_relations_final_2026-08-09" / "configuration_features.csv"
NETWORK_AUDIT = NETWORK_HZ0 / "symmetry_audit.json"

MEAN_R_POISSON = 2.0 * math.log(2.0) - 1.0
MEAN_R_GOE = 0.5307
VARIANT_ORDER = (
    "zero",
    "matched_m1em03",
    "matched_m1em04",
    "matched",
    "matched_p1em04",
    "matched_p1em03",
)
VARIANT_LABELS = (
    r"$0$",
    r"$h_z-10^{-3}$",
    r"$h_z-10^{-4}$",
    r"$h_z$",
    r"$h_z+10^{-4}$",
    r"$h_z+10^{-3}$",
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sector_is_wd(statistics: dict[str, Any]) -> bool:
    mean_r = float(statistics["mean_ratio"])
    distances = statistics["l1_distances"]
    mean_selects_goe = abs(mean_r - MEAN_R_GOE) < abs(mean_r - MEAN_R_POISSON)
    l1_selects_goe = float(distances["GOE"]) < float(distances["Poisson"])
    return mean_selects_goe and l1_selects_goe


def collect_network_wd_scan() -> tuple[list[dict[str, Any]], dict[str, list[float]]]:
    records: list[dict[str, Any]] = []
    for path in sorted(NETWORK_HZ0.glob("family_*/*.json")):
        payload = _read_json(path)
        spacings = payload["spacing_statistics"]
        if len(spacings) != 4:
            raise ValueError(f"expected four selected sectors: {path}")
        if not all(_sector_is_wd(item) for item in spacings.values()):
            continue
        variants: dict[str, float] = {}
        for item in payload["hz0_variants"]:
            aliases = item["hz0_aliases"]
            if len(aliases) != 1:
                raise ValueError(f"unexpected merged hz0 aliases: {path}")
            variants[str(aliases[0])] = float(item["S_born"])
        if set(variants) != set(VARIANT_ORDER):
            raise ValueError(f"incomplete hz0 variants: {path}")
        records.append(
            {
                "selection": payload["selection"],
                "family": payload["family"],
                "source_rank": int(payload["source_rank"]),
                "variants": variants,
            }
        )
    by_variant = {
        variant: [record["variants"][variant] for record in records]
        for variant in VARIANT_ORDER
    }
    return records, by_variant


def collect_simple_pair() -> dict[str, dict[str, float]]:
    wanted = {"config_111", "config_175"}
    output: dict[str, dict[str, float]] = {}
    for row in _read_csv(FEATURES):
        if row["campaign"] != "nearest_hz0_0" or row["config_id"] not in wanted:
            continue
        output[row["config_id"]] = {
            name: float(row[name])
            for name in (
                "S_born",
                "born_RMSE",
                "hz",
                "J",
                "Jpm",
                "Jx",
                "Jx_effective",
                "mean_spacing",
                "theta_entropy",
                "occupied_fraction",
                "vab_weight_delta_lt_0p1",
                "vab_weight_delta_lt_1",
                "vab_weight_delta_lt_10",
            )
        }
    if set(output) != wanted:
        raise RuntimeError(f"missing simple-ring records: {wanted - set(output)}")
    return output


def _summary(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {
        "minimum": float(np.min(array)),
        "median": float(np.median(array)),
        "maximum": float(np.max(array)),
    }


def plot_summary(
    path: Path,
    ring_rows: list[dict[str, str]],
    network_values: dict[str, list[float]],
    pair: dict[str, dict[str, float]],
    category_counts: dict[str, int],
) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(13.8, 9.4), constrained_layout=True)

    ratio = np.asarray([float(row["hz0_over_hz"]) for row in ring_rows])
    score = np.asarray([float(row["global_S_born"]) for row in ring_rows])
    axes[0, 0].plot(ratio, score, "o-", color="#315b7d", linewidth=1.3, markersize=4.5)
    axes[0, 0].set_xscale("symlog", linthresh=1.0e-4, linscale=0.8)
    axes[0, 0].set_xlabel(r"$h_{z0}/h_z$")
    axes[0, 0].set_ylabel(r"$S_{\rm Born}$")
    axes[0, 0].set_title("(a) One WD ring: detailed central-field scan")

    values = [network_values[name] for name in VARIANT_ORDER]
    axes[0, 1].boxplot(values, tick_labels=VARIANT_LABELS, showfliers=False)
    rng = np.random.default_rng(20260905)
    for index, series in enumerate(values, start=1):
        jitter = rng.uniform(-0.09, 0.09, size=len(series))
        axes[0, 1].scatter(index + jitter, series, s=12, alpha=0.5, color="#8f4770")
    axes[0, 1].set_ylabel(r"$S_{\rm Born}$")
    axes[0, 1].set_title("(b) 24 network cases: four selected sectors WD")
    axes[0, 1].tick_params(axis="x", labelrotation=24)

    thresholds = ("vab_weight_delta_lt_0p1", "vab_weight_delta_lt_1", "vab_weight_delta_lt_10")
    x = np.arange(len(thresholds))
    width = 0.36
    for offset, (case_id, color) in zip((-width / 2, width / 2), (("config_111", "#2f7d5b"), ("config_175", "#b24b45")), strict=True):
        axes[1, 0].bar(
            x + offset,
            [pair[case_id][name] for name in thresholds],
            width,
            label=case_id,
            color=color,
        )
    axes[1, 0].set_yscale("log")
    axes[1, 0].set_xticks(x, (r"$\delta<0.1\langle s\rangle$", r"$\delta<\langle s\rangle$", r"$\delta<10\langle s\rangle$"))
    axes[1, 0].set_ylabel(r"normalized $|V_{ab}|^2$ weight")
    axes[1, 0].set_title("(c) Simple rings: qubit-accessible near-resonant weight")
    axes[1, 0].legend(frameon=False)

    order = ("wd_born", "poisson_born", "wd_clearly_nonborn", "poisson_clearly_nonborn")
    labels = ("WD / Born", "Poisson / Born", "WD / non-Born", "Poisson / non-Born")
    axes[1, 1].bar(np.arange(4), [category_counts[name] for name in order], color=("#4c78a8", "#72b7b2", "#e45756", "#f2cf5b"))
    axes[1, 1].set_xticks(np.arange(4), labels, rotation=20, ha="right")
    axes[1, 1].set_ylabel("robust examples")
    axes[1, 1].set_title(r"(d) Clean-ring catalog at $h_{z0}=0$")
    axes[1, 1].set_ylim(0.0, max(category_counts.values()) + 1.5)

    for axis in axes.flat:
        axis.grid(alpha=0.2, axis="y")
    figure.suptitle("Audit of sector coupling, chaos, and Born-profile action items", fontsize=15)
    figure.savefig(path, dpi=190)
    plt.close(figure)


def build_report(
    category_counts: dict[str, int],
    activation: dict[str, Any],
    ring_rows: list[dict[str, str]],
    network_records: list[dict[str, Any]],
    network_values: dict[str, list[float]],
    pair: dict[str, dict[str, float]],
) -> str:
    activation_rows = {
        record["case_id"]: next(
            item for item in record["diagnostics"] if item["label"] == "global"
        )
        for record in activation["records"]
    }
    ring_scores = [float(row["global_S_born"]) for row in ring_rows]
    network_summary = {name: _summary(values) for name, values in network_values.items()}
    ratio_01 = pair["config_111"]["vab_weight_delta_lt_0p1"] / pair["config_175"]["vab_weight_delta_lt_0p1"]
    ratio_1 = pair["config_111"]["vab_weight_delta_lt_1"] / pair["config_175"]["vab_weight_delta_lt_1"]
    ratio_10 = pair["config_111"]["vab_weight_delta_lt_10"] / pair["config_175"]["vab_weight_delta_lt_10"]
    return f"""# Professor action-item audit

Generated {timestamp()} from completed repository results. Numerical claims below are finite-size and descriptive unless explicitly stated otherwise.

![Summary](summary.png)

## Status at a glance

| Remark / action item | Status | Evidence |
|---|---|---|
| Include the fact that the qubit changes detector magnetization sector, not momentum | **Addressed methodologically; finite-size evidence available** | The activation-resolved implementation uses `(k, N_up)` detector blocks, only connects `N_up -> N_up +/- 1` at fixed `k`, treats degeneracies basis-invariantly, and reconstructs the full root distribution from activation-weighted components. |
| Search many WD cases for non-Born behavior | **Addressed at finite size** | The strict clean-ring catalog contains {category_counts['wd_clearly_nonborn']} WD / clearly-non-Born examples; separate network studies contain additional finite-size examples. |
| Vary `hz0` in small steps for WD cases | **Addressed** | One detailed N=17 WD ring has 20 values; a separate 40-network-case scan uses `hz0=0` and `hz0=h_z+delta`, `delta=0,+/-1e-4,+/-1e-3`. Of those, {len(network_records)} cases have all four selected fully resolved sectors classified WD by both mean-r proximity and spacing-distribution L1 distance. |
| Explain the contrasting simple-ring examples | **Premise corrected; mechanism partly diagnosed** | After full symmetry resolution, both representative nearest-neighbor rings are Poisson-like. Their dynamical contrast tracks angular support and qubit-accessible cross-sector resonance weight, not a Poisson/non-Poisson change. This is observational, not yet a causal matched-parameter test. |
| Search many Poisson cases for non-Born behavior | **Addressed at finite size** | The strict catalog contains {category_counts['poisson_clearly_nonborn']} Poisson / clearly-non-Born examples. |

## 1. How the qubit's sector coupling must enter the analysis

For the clean ring used here,

`V = -Jx_eff X_0 sum_j X_j`.

The isolated detector conserves magnetization `N_up` and translation momentum `k`. The uniform collective operator commutes with detector translation but contains raising and lowering terms. Therefore its exact selection rule is

`(k, N_up) -> (k, N_up +/- 1)`.

This information should **not** be incorporated by mixing levels from different detector sectors into one spacing sequence. Level repulsion remains an intra-sector property. Instead, the complementary dynamical statistic is the cross-sector transition measure

`|<b,k,N_up+/-1| sum_j X_j |a,k,N_up>|^2 K_t(E_b-E_a +/- 2 h_z0)`,

where `K_t(Delta)=4 sin^2(Delta t/2)/Delta^2`, with its finite limit at zero. Inside an exactly degenerate energy subspace, the code diagonalizes the positive activation operator assembled from these weighted transitions, making the result invariant under arbitrary rotations of degenerate eigenvectors.

The completed N=17 activation study already applies this construction. Its global scores are {float(activation_rows['case_01_born_like_nearest_neighbor']['S_born']):.3f} for the Born-like nearest-neighbor ring, {float(activation_rows['case_02_non_born_exchange_only']['S_born']):.3f} for the exchange-only ring, and {float(activation_rows['case_03_born_like_second_neighbor']['S_born']):.3f} for the second-neighbor WD ring. Conditioning on weak/intermediate/strong activation changes the profiles substantially, but activation strength is not monotonically equivalent to Born similarity. The decomposition is diagnostic, not a new conserved symmetry.

Existing figure: [activation-resolved montage](../ring_activation_hz0_diagnostics_2026-08-24/activation_band_diagnostic_montage.png).

## 2. Chaotic (WD) cases

### WD but non-Born

The strict `hz0=0` catalog requires agreement of mean adjacent-gap-ratio and unfolded-spacing KS classifications, with a margin of at least 0.03 for each, plus `S_Born < 0.5` and occupied-bin RMSE above 0.1. It contains {category_counts['wd_clearly_nonborn']} such examples. This falsifies detector-WD sufficiency at the sampled finite sizes; it does not establish an asymptotic phase statement.

Existing figure: [ten WD / clearly-non-Born examples](../hz0_0_ring_spacing_born_10x4_diagnostics_2026-09-05/wd_clearly_nonborn__diagnostics_and_resolved_spacings.png).

### Small central-field changes

The detailed fixed-detector N=17 WD-ring scan spans 20 `hz0/hz` values and gives global `S_Born` from {min(ring_scores):.3f} to {max(ring_scores):.3f}. It includes ratios `0, 1e-4, 1e-3, 1e-2` near zero and offsets `+/-1e-5, +/-1e-3, +/-1e-2` around `hz0=hz`. Because the detector Hamiltonian is fixed, its spacing distribution is identical across all 20 columns.

The independent network scan generalizes the sensitivity across {len(network_records)} all-selected-sector-WD configurations. At `hz0=0`, the median score is {network_summary['zero']['median']:.3f} (range {network_summary['zero']['minimum']:.3f}--{network_summary['zero']['maximum']:.3f}); at the matched field and its `+/-1e-4,+/-1e-3` offsets, medians lie between {min(network_summary[name]['median'] for name in VARIANT_ORDER[1:]):.3f} and {max(network_summary[name]['median'] for name in VARIANT_ORDER[1:]):.3f}. Thus small field changes near resonance do not restore a universal Born profile; they expose sharp, non-monotone finite-time spectral sensitivity.

Existing figures: [N=17 all-sector 3x20 scan](../ring_second_neighbor_wd_hz0_scan_N17_all_sectors_2026-08-31/hz0_scan_global_diagnostics_full_spacing_all_20_sectors_3x20.png) and [40 network scans with resolved spacings](../network_top_hz0_variants_N11_spacings_graph_all_2026-08-20/).

## 3. Symmetric nearest-neighbor ring

The earlier “Poisson/Born versus non-Poisson/non-Born” framing is not supported by the corrected N=17 symmetry-resolved calculation:

| case | corrected spacing | mean r | KS(Poisson) | KS(GOE) | N=17 S_Born |
|---|---|---:|---:|---:|---:|
| config_111 | Poisson | 0.384 | 0.007 | 0.215 | 0.932 |
| config_175 | Poisson | 0.378 | 0.059 | 0.275 | 0.020 |

The two detectors share the same nearest-neighbor integrable family, so their equal spacing class is expected. Their dynamics differ because the qubit samples **matrix-element-weighted gaps between adjacent magnetization sectors**, and because microscopic scale ratios differ. In the existing N=10 detector / N=14 dynamics `V_ab` analysis, config_111 has {ratio_01:.0f} times more normalized coupling weight within `0.1` mean spacings of resonance, {ratio_1:.0f} times more within one spacing, and {ratio_10:.1f} times more within ten spacings than config_175. Its occupied angular fraction is {pair['config_111']['occupied_fraction']:.3f} versus {pair['config_175']['occupied_fraction']:.3f}, and its theta entropy is {pair['config_111']['theta_entropy']:.3f} versus {pair['config_175']['theta_entropy']:.3f}.

This supports the mechanism “available resonant channels and angular coverage,” not “different level-repulsion class.” It remains a correlation because the two parameter sets also differ in `h_z`, `J`, `Jpm`, and `Jx`. A causal follow-up should interpolate one dimensionless ratio at a time and repeat the activation-resolved calculation at several N.

Existing figure: [Poisson/Born examples](../hz0_0_ring_spacing_born_10x4_diagnostics_2026-09-05/poisson_born__diagnostics_and_resolved_spacings.png) and [Poisson / clearly-non-Born examples](../hz0_0_ring_spacing_born_10x4_diagnostics_2026-09-05/poisson_clearly_nonborn__diagnostics_and_resolved_spacings.png).

## 4. What is complete and what is still open

No new production simulation is needed to answer the professor's listed searches: the relevant campaigns already exist. The ongoing N=17 continuation of the lower-N 10x4 catalog is a robustness extension, not a prerequisite for the finite-size conclusions above.

Still open:

- whether WD/non-Born and Poisson/non-Born assignments persist along controlled finite-size sequences;
- a matched intervention study isolating `h_z/J`, `Jpm/J`, and `Jx_eff/<s>` in the simple-ring pair;
- whether activation-resolved cross-sector statistics predict occupied-bin Born error after controlling for angular coverage;
- full-sphere conclusions: `hz0=0` with only central-X coupling confines roots to a great circle.

## Reproducibility and limitations

- Clean-ring catalog: N=13,14,16,17; finite-size descriptive labels; lower-N selection uses five largest exact sectors per nonredundant momentum and omits even-N half filling because of its extra internal spin-reversal symmetry.
- Network scan: N=11 detector spacings and N=12 dynamics; four largest fully symmetry-resolved sectors per configuration; 24/40 configurations pass the strict all-four-sector WD screen used here.
- `V_ab` comparison: N=10 detector spectra paired with N=14 dynamics, hence suggestive rather than a same-N causal demonstration.
- The current `S_Born` score depends partly on angular support; occupied-bin RMSE and coverage must be reported with it.
"""


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return result


def main() -> None:
    args = parser().parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    catalog_rows = _read_csv(CATALOG)
    category_counts: dict[str, int] = {}
    for row in catalog_rows:
        category_counts[row["category"]] = category_counts.get(row["category"], 0) + 1
    expected_categories = {
        "wd_born",
        "poisson_born",
        "wd_clearly_nonborn",
        "poisson_clearly_nonborn",
    }
    if set(category_counts) != expected_categories or any(value != 10 for value in category_counts.values()):
        raise RuntimeError(f"unexpected catalog composition: {category_counts}")

    activation = _read_json(ACTIVATION)
    ring_rows = _read_csv(RING_HZ0)
    if len(ring_rows) != 20:
        raise RuntimeError(f"expected 20 detailed ring hz0 rows, found {len(ring_rows)}")
    network_audit = _read_json(NETWORK_AUDIT)
    if int(network_audit["configurations"]) != 40 or int(network_audit["all_detected_symmetries_resolved"]) != 40:
        raise RuntimeError("network symmetry audit is incomplete")
    network_records, network_values = collect_network_wd_scan()
    if len(network_records) != 24:
        raise RuntimeError(f"expected 24 all-selected-sector-WD network cases, found {len(network_records)}")
    pair = collect_simple_pair()

    figure_path = output_dir / "summary.png"
    plot_summary(figure_path, ring_rows, network_values, pair, category_counts)
    report_path = output_dir / "README.md"
    report_path.write_text(
        build_report(category_counts, activation, ring_rows, network_records, network_values, pair),
        encoding="utf-8",
    )

    inputs = (CATALOG, ACTIVATION, RING_HZ0, NETWORK_AUDIT, FEATURES)
    _atomic_json(
        output_dir / "provenance.json",
        {
            "schema_version": 1,
            "created": timestamp(),
            "script": str(Path(__file__).resolve().relative_to(ROOT)),
            "script_sha256": _sha256(Path(__file__).resolve()),
            "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in inputs},
            "network_figure_metadata_count": len(list(NETWORK_HZ0.glob("family_*/*.json"))),
            "all_selected_sector_wd_network_count": len(network_records),
            "catalog_category_counts": category_counts,
            "outputs": {
                figure_path.name: _sha256(figure_path),
                report_path.name: _sha256(report_path),
            },
        },
    )
    print(f"report={report_path}")
    print(f"figure={figure_path}")


if __name__ == "__main__":
    main()
