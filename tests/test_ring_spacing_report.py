"""Independent count conservation and collection-integrity regressions."""

import hashlib
import json

import numpy as np
import pytest

from core.ring_spacing_report import load_spacing_histograms, spacing_density
from scripts.audit_completed_ring_campaign import verify_marker


def test_density_retains_tail_mass():
    density = spacing_density(np.array([2, 3]), np.array([0, 1, 3]),
                              total_spacing_count=10)
    np.testing.assert_allclose(density, [0.2, 0.15])
    assert density @ np.array([1, 2]) == pytest.approx(0.5)


def test_sector_pooling_preserves_counts(tmp_path):
    path = tmp_path / "histograms.npz"
    counts = np.array([[1, 2], [3, 1]])
    np.savez(path, bin_edges=[0, 1, 2], sector_histogram_counts=counts,
             pooled_histogram_counts=counts.sum(axis=0))
    records = [
        dict(sector=dict(momentum=k, n_up=2, reflection_parity=None),
             spacing_count=5, histogram_in_range=int(counts[k].sum()),
             histogram_overflow=5-int(counts[k].sum()))
        for k in range(2)
    ]
    metadata = dict(sector_count=2, sectors=records,
                    pooled=dict(spacing_count=10, histogram_overflow=3))
    _, restored, pooled = load_spacing_histograms(path, metadata)
    np.testing.assert_array_equal(restored, counts)
    np.testing.assert_array_equal(pooled, [4, 3])
    metadata["sectors"][1]["sector"]["momentum"] = 0
    with pytest.raises(ValueError, match="duplicate symmetry sector"):
        load_spacing_histograms(path, metadata)


def test_completion_rejects_tampered_and_escaping_artifacts(tmp_path):
    artifact = tmp_path / "result.dat"
    artifact.write_bytes(b"verified data")
    marker = tmp_path / "COMPLETE.json"
    marker.write_text(json.dumps(dict(status="complete", files={
        "result.dat": hashlib.sha256(artifact.read_bytes()).hexdigest()
    })))
    assert verify_marker(marker) == 1
    artifact.write_bytes(b"changed data")
    with pytest.raises(ValueError, match="checksum mismatch"):
        verify_marker(marker)
    marker.write_text(json.dumps(dict(status="complete", files={"../escape": "x"})))
    with pytest.raises(ValueError, match="unsafe artifact path"):
        verify_marker(marker)


@pytest.mark.parametrize("counts,total", [([1.5, 2], 4), ([-1, 2], 4), ([3, 2], 4)])
def test_invalid_spacing_counts_rejected(counts, total):
    with pytest.raises(ValueError):
        spacing_density(np.array(counts), np.array([0, 1, 2]),
                        total_spacing_count=total)
