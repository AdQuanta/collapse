#!/usr/bin/env python3.11
"""Run an N=14 shard of the very-narrow-hz two-order Sobol campaign."""

from __future__ import annotations

from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collapse.sobol_coupling_scan import SobolCampaign, timestamp  # noqa: E402
from examples import (  # noqa: E402
    run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_N15 as base,
)


DETECTOR_N = 14
HZ0 = base.HZ0
HZ_LOWER = base.HZ_LOWER
HZ_UPPER = base.HZ_UPPER
TOTAL_CONFIGURATIONS = base.TOTAL_CONFIGURATIONS
BATCH_SIZE = base.BATCH_SIZE
FIXED_JPM = base.FIXED_JPM
FIXED_JY = base.FIXED_JY
_batch_bounds = base._batch_bounds
parser = base.parser


def _copy_provenance_once(campaign: SobolCampaign) -> None:
    """Copy the exact N=14 campaign sources into the result directory."""

    scripts = campaign.parent_root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    lock = scripts / ".copy.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        return
    try:
        campaign._copy_provenance()
        for relative in (
            "examples/run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_N15.py",
            "examples/run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_two_order_N14.py",
            "hpc/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_two_order_N14_array.pbs",
            "hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_two_order_N14.sh",
            "hpc/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_two_order_N14.md",
        ):
            source = ROOT / relative
            if source.is_file():
                shutil.copy2(source, scripts / source.name)
        (scripts / "n14_variant.txt").write_text(
            f"created={timestamp()}\nN=14\nhz0=0.1\nhz=[0.0999,0.1001]\n"
            "Jpm=0\nJy=0\nkappa=0.01\ncoupling_lower=1e-5\n",
            encoding="utf-8",
        )
    finally:
        lock.rmdir()


def main() -> None:
    """Run the shared campaign implementation with N fixed to 14."""

    base.DETECTOR_N = DETECTOR_N
    base._copy_provenance_once = _copy_provenance_once
    base.main()


if __name__ == "__main__":
    main()
