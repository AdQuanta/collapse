"""Run the decisive exact-degeneracy versus heavy-tail campaign."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.degeneracy_heavy_tail_campaign import (  # noqa: E402
    CampaignAggregator,
    CampaignConfig,
    CampaignRepository,
    DegeneracyHeavyTailCampaignService,
    describe_config,
    smoke_config,
)


DEFAULT_CONFIG = Path("configs/zeus_degeneracy_heavy_tail_iff_N13_N18.json")
DEFAULT_ROOT = Path("work/zeus_degeneracy_heavy_tail_iff_N13_N18")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Use a separate N=4, four-case, t=100 validation campaign.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("describe", help="Print the exact activation labels and task count.")

    simulate = subparsers.add_parser(
        "simulate-N",
        help="Simulate all decisive Hamiltonians for one N, checkpoint each case, then aggregate N.",
    )
    simulate.add_argument("--N", type=int, required=True)
    simulate.add_argument(
        "--workers",
        type=int,
        default=0,
        help="Process workers; 0 selects the memory-aware N-dependent default.",
    )
    simulate.add_argument("--force", action="store_true")
    simulate.add_argument("--dry-run", action="store_true")

    aggregate_n = subparsers.add_parser("aggregate-N", help="Rebuild one completed N truth table.")
    aggregate_n.add_argument("--N", type=int, required=True)

    aggregate_all = subparsers.add_parser(
        "aggregate-all",
        help="Combine all N into persistence tables and the final equivalence verdict.",
    )
    aggregate_all.add_argument("--allow-partial", action="store_true")
    return parser


def run(args: argparse.Namespace) -> None:
    config = CampaignConfig.from_json(args.config)
    if args.smoke:
        config = smoke_config(config)
    run_root = args.run_root / "smoke" if args.smoke else args.run_root
    repository = CampaignRepository(run_root)

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
                        "case_ids": [definition.case_id for definition in config.cases],
                        "run_root": str(run_root),
                        "config_digest": config.digest,
                    },
                    indent=2,
                )
            )
            return
        done = DegeneracyHeavyTailCampaignService(repository).run_n(
            config,
            args.N,
            workers=args.workers,
            force=args.force,
        )
        print(f"Completed N={args.N}: {done}")
        return

    aggregator = CampaignAggregator(repository)
    if args.command == "aggregate-N":
        print(f"Aggregated N={args.N}: {aggregator.aggregate_n(config, args.N)}")
        return
    if args.command == "aggregate-all":
        print(
            "Aggregated all N: "
            f"{aggregator.aggregate_all_locked(config, allow_partial=args.allow_partial)}"
        )
        return
    raise RuntimeError(f"unknown command {args.command!r}")


def main() -> None:
    run(_parser().parse_args())


if __name__ == "__main__":
    main()
