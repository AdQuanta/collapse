"""Audit every symmetry-resolved N_D=11 detector spectrum used in the figures.

The audit independently regenerates each graph, enumerates its complete
automorphism group with a second backtracking implementation, checks the
commutator of every graph symmetry with every fixed-Hamming-weight Hamiltonian
block, and reruns the sector decomposition and its spectrum-union checks.
"""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
os.environ.setdefault(
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-network-extremes-symmetry-audit")
)

from core.detector_graphs import DetectorGraphSpec, detector_graph_metadata
from core.graph_spectral_sectors import (
    detector_hamiltonian_block,
    fixed_weight_states,
    largest_detector_symmetry_sectors,
)


DEFAULT_REPORT_ROOT = ROOT / "reports" / (
    "network_extremes_largerN_N11_spacings_graph_all_2026-08-20"
)


def _canonical_edges(edges: list[list[int]] | tuple[tuple[int, int], ...]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(tuple(sorted((int(a), int(b)))) for a, b in edges))


def _independent_automorphisms(
    n_nodes: int, edges: tuple[tuple[int, int], ...]
) -> tuple[tuple[int, ...], ...]:
    """Enumerate graph automorphisms using dynamic MRV backtracking.

    This intentionally does not call or reproduce the color-refinement search
    in :mod:`core.graph_symmetry`; it uses degree classes and dynamically
    chooses the unmapped vertex with the fewest adjacency-consistent images.
    """

    adjacency = np.zeros((n_nodes, n_nodes), dtype=np.bool_)
    for left, right in edges:
        adjacency[left, right] = adjacency[right, left] = True
    degree = adjacency.sum(axis=1)
    mapping = np.full(n_nodes, -1, dtype=np.int64)
    used = np.zeros(n_nodes, dtype=np.bool_)
    results: list[tuple[int, ...]] = []

    def valid_targets(source: int) -> list[int]:
        assigned = np.flatnonzero(mapping >= 0)
        candidates: list[int] = []
        for target in np.flatnonzero((degree == degree[source]) & ~used):
            target_int = int(target)
            if all(
                adjacency[source, other]
                == adjacency[target_int, int(mapping[other])]
                for other in assigned
            ):
                candidates.append(target_int)
        return candidates

    def search(depth: int) -> None:
        if depth == n_nodes:
            results.append(tuple(int(value) for value in mapping))
            return
        choices = [
            (len(targets := valid_targets(source)), -int(degree[source]), source, targets)
            for source in range(n_nodes)
            if mapping[source] < 0
        ]
        _, _, source, targets = min(choices, key=lambda item: item[:3])
        for target in targets:
            mapping[source] = target
            used[target] = True
            search(depth + 1)
            used[target] = False
            mapping[source] = -1

    search(0)
    return tuple(sorted(results))


def _basis_action(
    states: np.ndarray, permutation: tuple[int, ...], n_nodes: int
) -> np.ndarray:
    lookup = np.full(1 << n_nodes, -1, dtype=np.int64)
    lookup[states] = np.arange(states.size, dtype=np.int64)
    targets = np.empty(states.size, dtype=np.int64)
    for position, raw_state in enumerate(states):
        transformed = 0
        state = int(raw_state)
        for source, target in enumerate(permutation):
            if (state >> source) & 1:
                transformed |= 1 << target
        targets[position] = lookup[transformed]
    if np.any(targets < 0):
        raise RuntimeError("permutation failed to preserve Hamming weight")
    return targets


def _degeneracy_diagnostic(
    energies: np.ndarray,
) -> tuple[int, int, float, float]:
    values = np.sort(np.asarray(energies, dtype=float))
    if values.size < 2:
        return 0, 1, 0.0, math.inf
    scale = max(float(np.ptp(values)), float(np.max(np.abs(values))), 1.0)
    tolerance = 2.0e-10 * scale
    cluster_sizes: list[int] = []
    current = 1
    for gap in np.diff(values):
        if abs(float(gap)) <= tolerance:
            current += 1
        else:
            cluster_sizes.append(current)
            current = 1
    cluster_sizes.append(current)
    repeated_levels = sum(size for size in cluster_sizes if size > 1)
    return repeated_levels, max(cluster_sizes), tolerance, float(np.min(np.diff(values)))


def _twin_reductions(
    n_nodes: int,
    edges: tuple[tuple[int, int], ...],
    automorphisms: tuple[tuple[int, ...], ...],
) -> list[dict[str, Any]]:
    """Describe induced graphs exposed by antisymmetric twin-site sectors."""

    reductions: list[dict[str, Any]] = []
    for permutation in automorphisms:
        moved = [node for node, target in enumerate(permutation) if node != target]
        if len(moved) != 2 or permutation[moved[0]] != moved[1]:
            continue
        pair = tuple(sorted(moved))
        if any(item["twin_pair"] == list(pair) for item in reductions):
            continue
        retained = [node for node in range(n_nodes) if node not in pair]
        relabel = {old: new for new, old in enumerate(retained)}
        reduced_edges = tuple(
            sorted(
                (relabel[left], relabel[right])
                for left, right in edges
                if left in relabel and right in relabel
            )
        )
        reduced_group = _independent_automorphisms(n_nodes - 2, reduced_edges)
        inherited_restrictions: set[tuple[int, ...]] = set()
        pair_set = set(pair)
        for full_permutation in automorphisms:
            if {full_permutation[pair[0]], full_permutation[pair[1]]} != pair_set:
                continue
            inherited_restrictions.add(
                tuple(relabel[full_permutation[node]] for node in retained)
            )
        extra_reduced = set(reduced_group) - inherited_restrictions
        reductions.append(
            {
                "twin_pair": list(pair),
                "reduced_nodes": retained,
                "reduced_edge_count": len(reduced_edges),
                "reduced_automorphism_group_order": len(reduced_group),
                "inherited_restriction_group_order": len(inherited_restrictions),
                "extra_reduced_automorphism_count": len(extra_reduced),
                "extra_reduced_symmetry_present": bool(extra_reduced),
            }
        )
    return reductions


def _audit_one(path_text: str) -> dict[str, Any]:
    started = time.perf_counter()
    path = Path(path_text)
    payload = json.loads(path.read_text(encoding="utf-8"))
    n_nodes = int(payload["spectral_detector_n"])
    parameters = payload["source_parameters"]
    spec = DetectorGraphSpec(**parameters["graph_spec"])
    regenerated = detector_graph_metadata(n_nodes, spec)
    edges = _canonical_edges(regenerated["edges_zero_based"])
    stored_edges = _canonical_edges(payload["spectral_graph"]["edges_zero_based"])

    independent_group = _independent_automorphisms(n_nodes, edges)
    stored_group = tuple(
        sorted(
            tuple(int(value) for value in permutation)
            for permutation in payload["symmetry_resolution"][
                "automorphisms_zero_based"
            ]
        )
    )

    hz = float(parameters["hz"])
    j = float(parameters["j"])
    jpm = float(parameters["jpm"])
    max_commutator = 0.0
    for weight in range(n_nodes // 2 + 1):
        states = fixed_weight_states(n_nodes, weight)
        block = detector_hamiltonian_block(
            n_nodes, edges, states, hz=hz, j=j, jpm=jpm
        )
        for permutation in independent_group:
            action = _basis_action(states, permutation, n_nodes)
            error = float(np.max(np.abs(block[np.ix_(action, action)] - block)))
            max_commutator = max(max_commutator, error)

    sectors, fresh = largest_detector_symmetry_sectors(
        n_nodes, edges, hz=hz, j=j, jpm=jpm, count=4
    )
    stored = payload["symmetry_resolution"]
    stored_selected = [
        (
            int(item["hamming_weight"]),
            int(item["sector_index"]),
            int(item["dimension"]),
            int(item["equivalent_copy_count"]),
        )
        for item in stored["selected"]
    ]
    fresh_selected = [
        (
            int(item["hamming_weight"]),
            int(item["sector_index"]),
            int(item["dimension"]),
            int(item["equivalent_copy_count"]),
        )
        for item in fresh["selected"]
    ]

    dimension_checks: list[bool] = []
    max_invariant_residual = 0.0
    max_union_error = 0.0
    for weight in range(n_nodes // 2 + 1):
        block = fresh["blocks"][f"weight_{weight}"]
        dimension_checks.append(
            sum(int(value) for value in block["raw_sector_dimensions"])
            == math.comb(n_nodes, weight)
        )
        max_invariant_residual = max(
            max_invariant_residual,
            float(block["invariant_subspace_residual_max_abs"]),
        )
        max_union_error = max(
            max_union_error, float(block["spectrum_union_max_abs"])
        )

    repeated_levels = 0
    maximum_multiplicity = 1
    degeneracy_tolerances: list[float] = []
    degeneracy_details: list[dict[str, Any]] = []
    for sector in sectors:
        repeated, multiplicity, tolerance, minimum_gap = _degeneracy_diagnostic(
            sector.energies
        )
        repeated_levels += repeated
        maximum_multiplicity = max(maximum_multiplicity, multiplicity)
        degeneracy_tolerances.append(tolerance)
        degeneracy_details.append(
            {
                "label": sector.symmetry_label,
                "dimension": sector.dimension,
                "repeated_levels": repeated,
                "maximum_multiplicity": multiplicity,
                "minimum_gap": minimum_gap,
                "tolerance": tolerance,
            }
        )

    twin_reductions = _twin_reductions(n_nodes, edges, independent_group)
    emergent_reduced_symmetry = any(
        bool(item["extra_reduced_symmetry_present"]) for item in twin_reductions
    )
    resolved_twin_pairs = {
        tuple(
            int(node)
            for node in block["twin_antisymmetric_reduction"][
                "twin_pair_zero_based"
            ]
        )
        for block in fresh["blocks"].values()
        if "twin_antisymmetric_reduction" in block
    }
    required_twin_pairs = {
        tuple(int(node) for node in item["twin_pair"])
        for item in twin_reductions
        if bool(item["extra_reduced_symmetry_present"])
    }
    twin_reductions_resolved = required_twin_pairs <= resolved_twin_pairs

    graph_reproduced = edges == stored_edges
    groups_equal = independent_group == stored_group
    selections_equal = fresh_selected == stored_selected
    dimensions_complete = all(dimension_checks)
    odd_n_spin_rule = (
        n_nodes % 2 == 1
        and not bool(fresh["half_filling_spin_reversal_resolved"])
        and all(
            not bool(block["spin_reversal_resolved"])
            for block in fresh["blocks"].values()
        )
    )
    numerical_pass = (
        max_commutator <= 1.0e-12
        and max_invariant_residual <= 1.0e-9
        and max_union_error <= 1.0e-8
    )
    core_pass = all(
        (
            graph_reproduced,
            groups_equal,
            selections_equal,
            dimensions_complete,
            odd_n_spin_rule,
            numerical_pass,
        )
    )
    all_detected_symmetries_resolved = (
        core_pass
        and (not emergent_reduced_symmetry or twin_reductions_resolved)
        and repeated_levels == 0
    )
    return {
        "selection": payload["selection"],
        "family": payload["family"],
        "cohort": payload.get("cohort", "highest"),
        "cohort_rank": int(
            payload.get("cohort_rank", payload.get("source_rank", 0))
        ),
        "graph_kind": spec.kind,
        "graph_seed": int(spec.seed),
        "n_nodes": n_nodes,
        "edge_count": len(edges),
        "connected": bool(regenerated["connected"]),
        "hz": hz,
        "j": j,
        "jpm": jpm,
        "all_structural_couplings_nonzero": bool(j != 0.0 and jpm != 0.0),
        "graph_reproduced": graph_reproduced,
        "stored_group_order": int(stored["automorphism_group_order"]),
        "independent_group_order": len(independent_group),
        "complete_groups_equal": groups_equal,
        "selected_sectors_equal": selections_equal,
        "raw_dimensions_complete": dimensions_complete,
        "odd_n_spin_reversal_rule_correct": odd_n_spin_rule,
        "max_H_symmetry_commutator_abs": max_commutator,
        "max_invariant_subspace_residual_abs": max_invariant_residual,
        "max_spectrum_union_error_abs": max_union_error,
        "selected_dimensions": [sector.dimension for sector in sectors],
        "selected_repeated_levels": repeated_levels,
        "selected_maximum_multiplicity": maximum_multiplicity,
        "degeneracy_tolerance_max": max(degeneracy_tolerances),
        "selected_degeneracy_details": degeneracy_details,
        "twin_reductions": twin_reductions,
        "emergent_reduced_symmetry_detected": emergent_reduced_symmetry,
        "resolved_twin_pairs": [list(pair) for pair in sorted(resolved_twin_pairs)],
        "twin_reductions_resolved": twin_reductions_resolved,
        "core_symmetry_audit_pass": core_pass,
        "strict_no_residual_degeneracy_pass": repeated_levels == 0,
        "all_detected_symmetries_resolved": all_detected_symmetries_resolved,
        "elapsed_seconds": time.perf_counter() - started,
        "source_metadata": str(path),
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(value) if isinstance(value, list) else value
                    for key, value in row.items()
                }
            )


def _summary(rows: list[dict[str, Any]], elapsed: float) -> dict[str, Any]:
    families: dict[str, dict[str, Any]] = {}
    for family in sorted({str(row["family"]) for row in rows}):
        subset = [row for row in rows if row["family"] == family]
        families[family] = {
            "configurations": len(subset),
            "core_passed": sum(bool(row["core_symmetry_audit_pass"]) for row in subset),
            "strict_no_residual_degeneracy_passed": sum(
                bool(row["strict_no_residual_degeneracy_pass"]) for row in subset
            ),
            "all_detected_symmetries_resolved": sum(
                bool(row["all_detected_symmetries_resolved"]) for row in subset
            ),
            "automorphism_group_orders": sorted(
                {int(row["independent_group_order"]) for row in subset}
            ),
            "max_H_symmetry_commutator_abs": max(
                float(row["max_H_symmetry_commutator_abs"]) for row in subset
            ),
            "max_invariant_subspace_residual_abs": max(
                float(row["max_invariant_subspace_residual_abs"]) for row in subset
            ),
            "max_spectrum_union_error_abs": max(
                float(row["max_spectrum_union_error_abs"]) for row in subset
            ),
            "selected_repeated_levels": sum(
                int(row["selected_repeated_levels"]) for row in subset
            ),
        }
    return {
        "scope": (
            "All exact model-implied unitary symmetries at N_D=11: conserved "
            "Hamming weight and the complete automorphism group of each exact "
            "regenerated interaction graph. Complementary weights have equal "
            "spacings; global spin reversal is not an internal sector at odd N_D."
        ),
        "antiunitary_note": (
            "The real Hamiltonian has spinless time-reversal symmetry, fixing "
            "the GOE class; antiunitary time reversal is not a further block label."
        ),
        "limitation": (
            "A zero residual-degeneracy check can detect but cannot mathematically "
            "exclude every accidental parameter-specific conserved operator."
        ),
        "configurations": len(rows),
        "core_passed": sum(bool(row["core_symmetry_audit_pass"]) for row in rows),
        "strict_no_residual_degeneracy_passed": sum(
            bool(row["strict_no_residual_degeneracy_pass"]) for row in rows
        ),
        "all_detected_symmetries_resolved": sum(
            bool(row["all_detected_symmetries_resolved"]) for row in rows
        ),
        "all_structural_couplings_nonzero": all(
            bool(row["all_structural_couplings_nonzero"]) for row in rows
        ),
        "max_H_symmetry_commutator_abs": max(
            float(row["max_H_symmetry_commutator_abs"]) for row in rows
        ),
        "max_invariant_subspace_residual_abs": max(
            float(row["max_invariant_subspace_residual_abs"]) for row in rows
        ),
        "max_spectrum_union_error_abs": max(
            float(row["max_spectrum_union_error_abs"]) for row in rows
        ),
        "families": families,
        "elapsed_seconds": elapsed,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    root = args.report_root.resolve()
    paths = sorted(root.glob("family_*/*.json"))
    if not paths:
        raise FileNotFoundError(f"no per-configuration JSON files found under {root}")
    if args.workers < 1:
        raise ValueError("--workers must be positive")

    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        future_paths = {pool.submit(_audit_one, str(path)): path for path in paths}
        for completed, future in enumerate(as_completed(future_paths), start=1):
            row = future.result()
            rows.append(row)
            print(
                f"[{completed:02d}/{len(paths)}] {row['selection']}: "
                f"core={'PASS' if row['core_symmetry_audit_pass'] else 'FAIL'}, "
                f"|Aut(G)|={row['independent_group_order']}, "
                f"residual-degeneracies={row['selected_repeated_levels']}",
                flush=True,
            )
    rows.sort(key=lambda row: str(row["selection"]))
    summary = _summary(rows, time.perf_counter() - started)
    json_path = root / "symmetry_audit.json"
    csv_path = root / "symmetry_audit.csv"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_csv(csv_path, rows)
    print(
        f"Audited {len(rows)} configurations: {summary['core_passed']} core passes; "
        f"{summary['strict_no_residual_degeneracy_passed']} strict degeneracy passes; "
        f"{summary['all_detected_symmetries_resolved']} fully resolved."
    )
    print(json_path)
    print(csv_path)


if __name__ == "__main__":
    main()
