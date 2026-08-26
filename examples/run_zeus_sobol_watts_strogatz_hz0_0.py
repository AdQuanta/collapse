#!/usr/bin/env python3.11
"""Run a configurable Sobol campaign on Watts-Strogatz detectors."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collapse.zeus_sobol_array import (  # noqa: E402
    ZeusSobolArraySpec,
    build_parser,
    run_array_campaign,
)


SPEC = ZeusSobolArraySpec(
    label="hz0=0 Watts-Strogatz detector",
    seed=20260812,
    hz0=0.0,
    connectivity="watts_strogatz",
    graph_seed=2026081201,
    graph_per_configuration=True,
    watts_strogatz_k=4,
    watts_strogatz_p=0.3,
    detector_n=12,
    count=400,
    batch_size=100,
)


def parser():
    return build_parser(SPEC)


def main() -> None:
    run_array_campaign(
        SPEC,
        parser().parse_args(),
        provenance_files=(
            "examples/run_zeus_sobol_watts_strogatz_hz0_0.py",
            "hpc/zeus_sobol_watts_strogatz_hz0_0_array.pbs",
            "hpc/submit_zeus_sobol_watts_strogatz_hz0_0.sh",
        ),
    )


if __name__ == "__main__":
    main()
