"""Path and table-contract tests for matched-ring scaling reproduction."""

import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "reproduce_matched_ring_scaling_full_sphere.py"
)
SPEC = importlib.util.spec_from_file_location("matched_scaling", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_windows_style_source_path_resolves_inside_repository() -> None:
    path = MODULE._resolve_source("work\\campaign\\raw.npz")

    assert path == MODULE.ROOT / "work" / "campaign" / "raw.npz"

