"""Shared pytest configuration for the collapse test suite.

Two concerns are handled here.

**Import path.** The tests import ``collapse`` and ``examples`` as top-level
packages.  Until now that worked only because ``python -m pytest`` puts the
current working directory on ``sys.path``; a bare ``pytest`` invocation from the
repository root failed to collect.  Inserting the repository root explicitly
makes both invocations behave identically.

**Generated campaign data.** Several contract tests read artifacts under
``work/`` and ``reports/``.  Those directories are deliberately gitignored, so a
fresh clone does not contain them.  A test that cannot reach its fixture has not
detected a regression, and reporting it as a failure hides real regressions in
the noise.  :func:`requires_paths` converts the absence into an explicit skip
while leaving every assertion intact whenever the data *is* present.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def missing_paths(*relative_paths: str) -> list[str]:
    """Return the subset of *relative_paths* that does not exist under the root."""

    return [path for path in relative_paths if not (ROOT / path).exists()]


def requires_paths(*relative_paths: str):
    """Skip the marked test(s) when any required generated artifact is absent.

    Use for tests that assert against stored campaign output.  The marker is
    evaluated at import time, so the reason string names the exact missing
    artifacts and the skip is visible in the summary rather than silent.
    """

    missing = missing_paths(*relative_paths)
    return pytest.mark.skipif(
        bool(missing),
        reason=(
            "generated campaign data absent from this checkout (gitignored): "
            + ", ".join(missing)
        ),
    )
