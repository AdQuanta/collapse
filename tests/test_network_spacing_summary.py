"""Regression checks for compact network level-spacing persistence."""

from __future__ import annotations

import json

import numpy as np

from core.network_spacing_summary import save_detector_spacing_summary


def test_spacing_summary_omits_spectral_samples_and_is_resumable(tmp_path) -> None:
    n_nodes = 7
    edges = tuple((node, (node + 1) % n_nodes) for node in range(n_nodes))
    outcome = save_detector_spacing_summary(
        tmp_path,
        n_nodes=n_nodes,
        edges=edges,
        hz=0.27,
        j=0.63,
        jpm=0.19,
        sector_count=4,
        histogram_bins=16,
    )
    assert outcome["status"] == "success"
    with np.load(tmp_path / "detector_spacing_summary.npz") as archive:
        assert not any(
            "energies" in key or "unfolded" in key for key in archive.files
        )
        for index in range(4):
            prefix = f"sector_{index:02d}"
            assert int(np.sum(archive[f"{prefix}__counts"])) > 0
            assert archive[f"{prefix}__counts"].dtype.kind in "iu"
    metadata = json.loads(
        (tmp_path / "detector_spacing_metadata.json").read_text()
    )
    assert len(metadata["sectors"]) == 4
    assert "detector sector eigenvalues" in metadata["storage"]["omitted"]
    resumed = save_detector_spacing_summary(
        tmp_path,
        n_nodes=n_nodes,
        edges=edges,
        hz=0.27,
        j=0.63,
        jpm=0.19,
        sector_count=4,
        histogram_bins=16,
    )
    assert resumed["status"] == "resumed"
