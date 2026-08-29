#!/usr/bin/env python3.11
"""Run 400 N=14 Sobol samples with hz0=0.1 and hz in [0.0999, 0.1001]."""

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


HZ_LOWER = 0.0999
HZ_UPPER = 0.1001
SPEC = ZeusSobolArraySpec(
    label="hz0=0.1 very-near-hz nearest-neighbor",
    seed=20260806,
    hz0=0.1,
    hz_lower=HZ_LOWER,
    hz_upper=HZ_UPPER,
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
            "scripts/run_zeus_sobol_hz0_0p1_hz_0p0999_0p1001_N14.py",
            "hpc/zeus_sobol_hz0_0p1_hz_0p0999_0p1001_N14_array.pbs",
            "hpc/submit_zeus_sobol_hz0_0p1_hz_0p0999_0p1001_N14.sh",
        ),
    )


if __name__ == "__main__":
    main()
