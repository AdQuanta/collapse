"""Validated plotting data for independently unfolded ring-symmetry sectors."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def spacing_density(
    counts: np.ndarray, edges: np.ndarray, *, total_spacing_count: int
) -> np.ndarray:
    """Normalize by ALL spacings, retaining probability mass outside the plot.

    The stored histogram covers [0,4]; its integral may be below one because
    the production calculation also recorded spacings larger than four.
    """
    counts = np.asarray(counts)
    edges = np.asarray(edges)
    if counts.ndim != 1 or edges.shape != (counts.size + 1,):
        raise ValueError("invalid spacing histogram shape")
    if not np.all(np.isfinite(edges)) or np.any(np.diff(edges) <= 0):
        raise ValueError("invalid spacing histogram edges")
    if not np.all(np.isfinite(counts)) or np.any(counts < 0):
        raise ValueError("invalid spacing counts")
    if np.any(counts != np.floor(counts)):
        raise ValueError("spacing counts must be integral")
    if total_spacing_count <= 0 or counts.sum() > total_spacing_count:
        raise ValueError("invalid total spacing count")
    return counts / (total_spacing_count * np.diff(edges))


def load_spacing_histograms(
    path: Path, metadata: dict[str, Any]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Verify sector identities and count conservation against saved metadata."""
    with np.load(path, allow_pickle=False) as archive:
        edges = np.array(archive["bin_edges"])
        sectors = np.array(archive["sector_histogram_counts"])
        pooled = np.array(archive["pooled_histogram_counts"])
    records = metadata["sectors"]
    if sectors.shape != (len(records), edges.size - 1):
        raise ValueError("sector histogram shape mismatch")
    if len(records) != metadata["sector_count"]:
        raise ValueError("sector metadata count mismatch")
    identities = [
        (r["sector"]["momentum"], r["sector"]["n_up"],
         r["sector"]["reflection_parity"])
        for r in records
    ]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate symmetry sector")
    np.testing.assert_array_equal(pooled, sectors.sum(axis=0))
    for counts, record in zip(sectors, records):
        spacing_density(counts, edges, total_spacing_count=record["spacing_count"])
        if counts.sum() != record["histogram_in_range"]:
            raise ValueError("sector in-range count mismatch")
        if counts.sum() + record["histogram_overflow"] != record["spacing_count"]:
            raise ValueError("sector overflow count mismatch")
    total = metadata["pooled"]
    if sum(r["spacing_count"] for r in records) != total["spacing_count"]:
        raise ValueError("pooled spacing count mismatch")
    if pooled.sum() + total["histogram_overflow"] != total["spacing_count"]:
        raise ValueError("pooled overflow count mismatch")
    spacing_density(pooled, edges, total_spacing_count=total["spacing_count"])
    return edges, sectors, pooled
