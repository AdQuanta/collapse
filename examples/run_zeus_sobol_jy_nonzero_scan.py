#!/usr/bin/env python3.11
"""Run Simulation B: 100 Sobol points in (Jx,Jy,J,Jpm,hz) with Jy>0."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.sobol_coupling_scan import SobolCampaign, build_settings  # noqa: E402


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-root", type=Path, default=None, help="Shared timestamped parent directory.")
    p.add_argument("--seed", type=int, default=20260727)
    p.add_argument("--count", type=int, default=100)
    p.add_argument("--sizes", type=int, nargs="+", default=[13, 14, 15, 16])
    p.add_argument("--only-N", type=int, default=None, help="Run one N subjob while retaining the full shared size manifest.")
    p.add_argument("--lower", type=float, default=1e-3)
    p.add_argument("--upper", type=float, default=10.0)
    p.add_argument("--kappa", type=float, default=0.1)
    p.add_argument("--evolution-time", type=float, default=1e6)
    p.add_argument("--workers", type=int, default=0, help="0 selects conservative N-dependent defaults.")
    p.add_argument("--bins", type=int, default=64)
    p.add_argument("--plot-grid", type=int, default=720)
    p.add_argument("--fit-harmonics", type=int, default=32)
    p.add_argument("--fit-tolerance", type=float, default=1e-10)
    p.add_argument("--max-bloch-points", type=int, default=6000)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--overwrite", action="store_true", help="Rerun individual cases without deleting prior files.")
    p.add_argument("--dry-run", action="store_true", help="Generate and validate sampling only.")
    return p


def main() -> None:
    args = parser().parse_args()
    root = args.output_root or Path("work") / f"zeus_sobol_coupling_scans_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    settings = build_settings(
        "jy_nonzero", seed=args.seed, count=args.count, sizes=tuple(args.sizes),
        lower=args.lower, upper=args.upper, kappa=args.kappa,
        evolution_time=args.evolution_time, bins=args.bins, plot_grid=args.plot_grid,
        fit_harmonics=args.fit_harmonics, fit_tolerance=args.fit_tolerance,
        max_bloch_points=args.max_bloch_points,
    )
    SobolCampaign(root, settings, workers=args.workers, resume=args.resume, overwrite=args.overwrite).run(
        dry_run=args.dry_run, only_n=args.only_N
    )
    print(f"Simulation B {'dry-run prepared' if args.dry_run else 'finished'}: {root.resolve()}")


if __name__ == "__main__":
    main()
