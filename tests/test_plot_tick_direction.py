from __future__ import annotations

from pathlib import Path
import re

import matplotlib as mpl


ROOT = Path(__file__).resolve().parents[1]
INWARD_TICK_PATTERN = re.compile(
    r"(?:[xy]tick\.direction|tick_params\([^)]*direction\s*=)\s*[^\n]*['\"]in['\"]"
)


def test_project_plotting_code_does_not_force_inward_ticks() -> None:
    offenders: list[str] = []
    for directory in (ROOT / "core", ROOT / "scripts", ROOT / "archive"):
        for path in directory.rglob("*.py"):
            if INWARD_TICK_PATTERN.search(path.read_text(encoding="utf-8")):
                offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def test_matplotlib_default_tick_direction_is_outward() -> None:
    assert mpl.rcParamsDefault["xtick.direction"] == "out"
    assert mpl.rcParamsDefault["ytick.direction"] == "out"

