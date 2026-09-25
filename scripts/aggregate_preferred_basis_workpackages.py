"""Aggregate WP3/WP4/WP5 results from the preferred-basis experiment log.

Pure aggregation over already-evaluated records in
``reports/preferred_basis/experiment_log.jsonl`` (written by
``scripts/run_preferred_basis_campaign.py``) plus the center's own N=8/N=10
profile metadata (written by ``scripts/export_preferred_basis_profile.py``,
which does not append to the JSONL log). No new Hamiltonians are evaluated
here.

Usage::

    python scripts/aggregate_preferred_basis_workpackages.py
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median, pstdev

LOG_PATH = Path("reports/preferred_basis/experiment_log.jsonl")
CENTER_N8 = Path("reports/preferred_basis/screen_00_N8/metadata.json")
CENTER_N10 = Path("reports/preferred_basis/screen_00_N10/metadata.json")


def load_records() -> dict[str, list[dict]]:
    records: dict[str, list[dict]] = {}
    with open(LOG_PATH, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            records.setdefault(record["name"], []).append(record)
    return records


def block_at(records: dict[str, list[dict]], name: str, n_pixel: str) -> dict | None:
    if name not in records:
        return None
    for record in records[name]:
        block = record.get("by_size", {}).get(n_pixel)
        if block is not None and block.get("axis_status") == "ok":
            return block
    return None


def cloud_stats(values: list[float]) -> dict[str, float]:
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "std": pstdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def wp3(records: dict[str, list[dict]]) -> dict:
    out: dict = {}
    for radius, sizes in (("r20", ("8", "10")), ("r35", ("8",)), ("r50", ("8",))):
        out[radius] = {}
        for n_pixel in sizes:
            b1_values, axis_deg_values, names = [], [], []
            for name in records:
                if not (name.startswith("wp3_") and name.endswith(f"_{radius}")):
                    continue
                block = block_at(records, name, n_pixel)
                if block is None:
                    continue
                b1_values.append(block["B1"])
                axis_deg_values.append(block["axis_angle_deg_from_reference"])
                names.append(name)
            if not b1_values:
                continue
            worst_axis_idx = max(range(len(axis_deg_values)), key=lambda i: axis_deg_values[i])
            worst_b1_idx = min(range(len(b1_values)), key=lambda i: abs(b1_values[i] - 1.0))
            out[radius][f"N{n_pixel}"] = {
                "B1": cloud_stats(b1_values),
                "axis_angle_deg": cloud_stats(axis_deg_values),
                "worst_axis_direction": names[worst_axis_idx],
                "worst_axis_deg": axis_deg_values[worst_axis_idx],
                "directions": names,
            }
    return out


def wp4(records: dict[str, list[dict]]) -> dict:
    out: dict = {}
    eps_names = {
        "wp4_eps0p025": 0.025,
        "wp4_eps0p050": 0.050,
        "wp4_eps0p100": 0.100,
    }
    for n_pixel in ("8", "10"):
        out[f"N{n_pixel}"] = []
        for name, eps in sorted(eps_names.items(), key=lambda kv: kv[1]):
            block = block_at(records, name, n_pixel)
            if block is None:
                continue
            out[f"N{n_pixel}"].append({
                "epsilon": eps, "B1": block["B1"],
                "axis_angle_deg": block["axis_angle_deg_from_reference"],
                "odd_l3_l5_l7": block.get("odd_harmonic", {}).get("higher_odd_l3_l5_l7_leakage"),
            })
    return out


def wp5(records: dict[str, list[dict]]) -> dict:
    out: dict = {}
    direction_names = [
        "wp5_axis_x", "wp5_axis_y", "wp5_axis_z",
        "wp5_screen_00_direction",
        "wp5_generic_0", "wp5_generic_1", "wp5_generic_2", "wp5_generic_3",
    ]
    for n_pixel in ("8", "10"):
        out[f"N{n_pixel}"] = []
        for name in direction_names:
            block = block_at(records, name, n_pixel)
            entry = {"name": name}
            if block is None:
                # rejected (perturbative gate) or not evaluated at this size
                latest = records.get(name, [{}])[-1]
                entry["status"] = "rejected" if latest.get("rejection_reasons") else "missing"
                entry["rejection_reasons"] = latest.get("rejection_reasons", [])
            else:
                entry["status"] = "ok"
                entry["B1"] = block["B1"]
                entry["axis_angle_deg"] = block["axis_angle_deg_from_reference"]
            out[f"N{n_pixel}"].append(entry)
    return out


def center_summary() -> dict:
    out = {}
    for label, path, n_pixel in (("N8", CENTER_N8, "8"), ("N10", CENTER_N10, "10")):
        meta = json.loads(path.read_text())
        out[label] = {"B1": meta["B1"], "axis_angle_deg": meta["axis_angle_deg_from_reference"]}
    # N=12 comes from the JSONL log only (no exported profile with raw points).
    records = load_records()
    block = block_at(records, "screen_00", "12")
    if block is not None:
        out["N12"] = {"B1": block["B1"], "axis_angle_deg": block["axis_angle_deg_from_reference"]}
    return out


def main() -> None:
    records = load_records()
    report = {
        "center": center_summary(),
        "wp3": wp3(records),
        "wp4": wp4(records),
        "wp5": wp5(records),
    }
    out_path = Path("reports/preferred_basis/wp345_aggregate.json")
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"\n[*] wrote {out_path}")


if __name__ == "__main__":
    main()
