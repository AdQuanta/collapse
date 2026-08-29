"""CLI parsing and small-data smoke checks for matched-ring post-processing."""

import importlib.util
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reproduce_matched_ring_full_sphere.py"
SPEC = importlib.util.spec_from_file_location("reproduce_matched", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_resolution_parser_uses_phi_then_mu() -> None:
    assert MODULE._parse_resolution("36x18") == (36, 18)


def test_diagnostic_record_preserves_full_sphere_fields() -> None:
    rng = np.random.default_rng(20260815)
    roots = rng.normal(size=(20_000, 3))
    roots /= np.linalg.norm(roots, axis=1)[:, None]
    result = MODULE.diagnose_labeled_bloch_histogram(
        roots,
        n_mu=4,
        n_phi=8,
        l_max=3,
    )

    record = MODULE._diagnostic_record(result)

    assert record["full_sphere_diagnostics_available"] is True
    assert record["epsilon_antipodal"] == 0.0
    assert len(record["power_by_l"]) == 4

