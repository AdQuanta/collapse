#!/usr/bin/env python3.11
"""Run matched fixed-Jx Sobol scans for four random-network families."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

from collapse.zeus_sobol_array import (  # noqa: E402
    ZeusSobolArraySpec,
    build_parser,
    run_array_campaign,
)


DETECTOR_N = 13
CONFIGURATIONS_PER_FAMILY = 100
BATCH_SIZE = 25
SOBOL_SEED = 20260816
DETECTOR_LOWER = 1.0
DETECTOR_UPPER = 1.0e2
FIXED_JX_UNSCALED = 1.0e-2
MAX_WEAK_RATIO = 1.0e-2
EVOLUTION_TIME = 1.0e6


SPECS = (
    ZeusSobolArraySpec(
        label="fixed Jx=0.01, hz0=0 Erdos-Renyi detector",
        seed=SOBOL_SEED,
        hz0=0.0,
        connectivity="erdos_renyi",
        graph_seed=2026081601,
        graph_per_configuration=True,
        erdos_renyi_p=0.3,
        detector_n=DETECTOR_N,
        count=CONFIGURATIONS_PER_FAMILY,
        batch_size=BATCH_SIZE,
        lower=DETECTOR_LOWER,
        upper=DETECTOR_UPPER,
        kappa=MAX_WEAK_RATIO,
        fixed_jx=FIXED_JX_UNSCALED,
        evolution_time=EVOLUTION_TIME,
    ),
    ZeusSobolArraySpec(
        label="fixed Jx=0.01, hz0=0 Watts-Strogatz detector",
        seed=SOBOL_SEED,
        hz0=0.0,
        connectivity="watts_strogatz",
        graph_seed=2026082601,
        graph_per_configuration=True,
        watts_strogatz_k=4,
        watts_strogatz_p=0.3,
        detector_n=DETECTOR_N,
        count=CONFIGURATIONS_PER_FAMILY,
        batch_size=BATCH_SIZE,
        lower=DETECTOR_LOWER,
        upper=DETECTOR_UPPER,
        kappa=MAX_WEAK_RATIO,
        fixed_jx=FIXED_JX_UNSCALED,
        evolution_time=EVOLUTION_TIME,
    ),
    ZeusSobolArraySpec(
        label="fixed Jx=0.01, hz0=0 Barabasi-Albert detector",
        seed=SOBOL_SEED,
        hz0=0.0,
        connectivity="barabasi_albert",
        graph_seed=2026083601,
        graph_per_configuration=True,
        barabasi_albert_m=2,
        detector_n=DETECTOR_N,
        count=CONFIGURATIONS_PER_FAMILY,
        batch_size=BATCH_SIZE,
        lower=DETECTOR_LOWER,
        upper=DETECTOR_UPPER,
        kappa=MAX_WEAK_RATIO,
        fixed_jx=FIXED_JX_UNSCALED,
        evolution_time=EVOLUTION_TIME,
    ),
    ZeusSobolArraySpec(
        label="fixed Jx=0.01, hz0=0 random 4-regular detector",
        seed=SOBOL_SEED,
        hz0=0.0,
        connectivity="random_regular",
        graph_seed=2026084601,
        graph_per_configuration=True,
        regular_degree=4,
        detector_n=DETECTOR_N,
        count=CONFIGURATIONS_PER_FAMILY,
        batch_size=BATCH_SIZE,
        lower=DETECTOR_LOWER,
        upper=DETECTOR_UPPER,
        kappa=MAX_WEAK_RATIO,
        fixed_jx=FIXED_JX_UNSCALED,
        evolution_time=EVOLUTION_TIME,
    ),
)


def _selected_family_index(argv: Sequence[str]) -> int:
    selector = argparse.ArgumentParser(add_help=False)
    selector.add_argument(
        "--family-index", type=int, choices=range(len(SPECS)), required=True
    )
    arguments, _ = selector.parse_known_args(argv)
    return int(arguments.family_index)


def parser(family_index: int) -> argparse.ArgumentParser:
    """Return a parser whose scientific defaults match ``family_index``."""

    if family_index not in range(len(SPECS)):
        raise ValueError(f"family_index must be in [0,{len(SPECS) - 1}]")
    result = build_parser(SPECS[family_index])
    result.add_argument(
        "--family-index", type=int, choices=range(len(SPECS)), required=True
    )
    return result


def main(argv: Sequence[str] | None = None) -> None:
    arguments = list(sys.argv[1:] if argv is None else argv)
    family_index = _selected_family_index(arguments)
    args = parser(family_index).parse_args(arguments)
    run_array_campaign(
        SPECS[family_index],
        args,
        provenance_files=(
            "examples/run_zeus_sobol_network_families_fixed_jx_N13.py",
            "hpc/zeus_sobol_network_families_fixed_jx_N13_array.pbs",
            "hpc/submit_zeus_sobol_network_families_fixed_jx_N13.sh",
            "hpc/zeus_sobol_network_families_fixed_jx_N13.md",
        ),
    )


if __name__ == "__main__":
    main()
