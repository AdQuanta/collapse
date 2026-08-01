"""Analyze the transferred Zeus results for the exact-degeneracy conjecture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.degeneracy_zeus_assessment import (  # noqa: E402
    AssessmentPaths,
    run_assessment,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("reports") / "degeneracy_heavy_tail_zeus_2026-07-26",
    )
    arguments = parser.parse_args()
    project_root = Path(__file__).resolve().parent.parent
    paths = AssessmentPaths.defaults(
        project_root,
        project_root / arguments.output_root,
    )
    summary = run_assessment(paths)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
