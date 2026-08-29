#!/usr/bin/env python3.11
"""Run 400 N=14 Sobol samples in (J, hz, Jpm, Jx, J2, Jpm2)."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.zeus_sobol_array import (  # noqa: E402
    ZeusSobolArraySpec,
    build_parser,
    run_array_campaign,
)


SPEC = ZeusSobolArraySpec(
    label="hz0=0 nearest-and-second-neighbor",
    seed=20260807,
    hz0=0.0,
    second_neighbor=True,
)
DETECTOR_N = SPEC.detector_n
TOTAL_CONFIGURATIONS = SPEC.count
BATCH_SIZE = SPEC.batch_size


def parser():
    return build_parser(SPEC)


def main() -> None:
    run_array_campaign(
        SPEC,
        parser().parse_args(),
        provenance_files=(
            "scripts/run_zeus_sobol_second_neighbor_hz0_0_N14.py",
            "hpc/zeus_sobol_second_neighbor_hz0_0_N14_array.pbs",
            "hpc/submit_zeus_sobol_second_neighbor_hz0_0_N14.sh",
        ),
    )


if __name__ == "__main__":
    main()
