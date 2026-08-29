"""Run the single-pixel relative-scale regime campaign."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.relative_scale_campaign import (  # noqa: E402
    RelativeScaleAggregator,
    RelativeScaleCampaignService,
    RelativeScaleConfig,
    RelativeScaleRepository,
    describe_config,
    smoke_config,
)


DEFAULT_CONFIG = Path("configs/zeus_relative_scale_regimes_N13_N18.json")
DEFAULT_ROOT = Path("work/zeus_relative_scale_regimes_N13_N18")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--smoke", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("describe")
    simulate = commands.add_parser("simulate-N")
    simulate.add_argument("--N", type=int, required=True)
    simulate.add_argument("--workers", type=int, default=0)
    simulate.add_argument("--force", action="store_true")
    simulate.add_argument("--dry-run", action="store_true")
    aggregate = commands.add_parser("aggregate-all")
    aggregate.add_argument("--allow-partial", action="store_true")
    return parser


def run(args: argparse.Namespace) -> None:
    config = RelativeScaleConfig.from_json(args.config)
    if args.smoke:
        config = smoke_config(config)
    root = args.run_root / "smoke" if args.smoke else args.run_root
    repository = RelativeScaleRepository(root)

    if args.command == "describe":
        print(json.dumps(describe_config(config), indent=2))
        return
    if args.command == "simulate-N":
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "mode": "dry-run",
                        "N": args.N,
                        "workers": args.workers,
                        "case_ids": [case.case_id for case in config.cases],
                        "run_root": str(root),
                        "config_digest": config.digest,
                    },
                    indent=2,
                )
            )
            return
        done = RelativeScaleCampaignService(repository).run_n(
            config,
            args.N,
            workers=args.workers,
            force=args.force,
        )
        print(f"Completed N={args.N}: {done}")
        return
    if args.command == "aggregate-all":
        summary = RelativeScaleAggregator(repository).aggregate_all_locked(
            config,
            allow_partial=args.allow_partial,
        )
        print(f"Aggregated all N: {summary}")
        return
    raise RuntimeError(f"unknown command {args.command!r}")


def main() -> None:
    run(_parser().parse_args())


if __name__ == "__main__":
    main()
