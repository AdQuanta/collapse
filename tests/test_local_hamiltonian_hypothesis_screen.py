"""Configuration expansion checks for the local hypothesis screen."""

import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "run_local_hamiltonian_hypothesis_screen.py"
)
SPEC = importlib.util.spec_from_file_location("local_hypothesis_screen", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


BASE = {"Jx": 0.03, "Jy": 0.0, "hx": 0.0, "hz": 0.1, "hz0": 0.1}


def test_detuning_definition_uses_declared_source_jx() -> None:
    payload = MODULE._point_payload(
        BASE,
        {"name": "matched_detuning"},
        3.0,
    )

    assert payload["hz0"] == 0.19


def test_second_channel_scan_preserves_jx_and_sets_jy_ratio() -> None:
    payload = MODULE._point_payload(
        BASE,
        {"name": "second_transverse_channel"},
        0.5,
    )

    assert payload["Jx"] == 0.03
    assert payload["Jy"] == 0.015



def test_recorded_path_is_repository_relative_inside_the_repository() -> None:
    """Provenance records must not embed machine-specific absolute paths."""

    inside = MODULE.ROOT / "configs" / "hamiltonian_classification_local_hypotheses.json"

    recorded = MODULE._recorded_path(inside)

    assert not Path(recorded).is_absolute()
    assert Path(recorded).parts[0] == "configs"


def test_recorded_path_falls_back_to_absolute_outside_the_repository(tmp_path) -> None:
    """An out-of-repository --output-dir must not abort a completed run.

    ``Path.relative_to`` raises ``ValueError`` for a path outside the root, which
    previously killed the runner after the first point had already been computed.
    """

    outside = tmp_path / "result.json"

    recorded = MODULE._recorded_path(outside)

    assert Path(recorded).is_absolute()
    assert Path(recorded) == outside.resolve()
