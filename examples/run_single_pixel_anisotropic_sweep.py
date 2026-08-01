"""Run or aggregate the Zeus anisotropic single-pixel J--Jpm--hz campaign."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.anisotropic_sweep import (  # noqa: E402
    AnisotropicRepository,
    AnisotropicSweepConfig,
    AnisotropicSweepService,
    BlueRedDiagnosticPlotter,
    BornHeatmapAggregator,
    QuSpinAnisotropicBackend,
    describe_config,
    smoke_config,
)


DEFAULT_CONFIG = Path("configs/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.json")
DEFAULT_ROOT = Path("work/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Use a separate N=4, four-case J--Jpm, t=100 validation grid.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("describe", help="Print task counts and per-N array ranges without writing files.")

    task = subparsers.add_parser("describe-task", help="Print the fixed N, hz, and J mapped to one array index.")
    task.add_argument("--task-index", type=int, required=True)

    simulate = subparsers.add_parser("simulate-task", help="Simulate and plot one fixed-N, fixed-hz, fixed-J Jpm row.")
    simulate.add_argument("--task-index", type=int, required=True)
    simulate.add_argument("--force", action="store_true")
    simulate.add_argument("--dry-run", action="store_true")

    simulate_n = subparsers.add_parser(
        "simulate-N",
        help="Simulate all hz/J/Jpm configurations for one N with process workers, then aggregate that N.",
    )
    simulate_n.add_argument("--N", type=int, required=True)
    simulate_n.add_argument(
        "--workers",
        type=int,
        default=0,
        help="Process workers; 0 selects the memory-aware N-dependent default.",
    )
    simulate_n.add_argument("--force", action="store_true")
    simulate_n.add_argument("--dry-run", action="store_true")

    aggregate = subparsers.add_parser("aggregate", help="Create all S_born heatmaps and metrics for one or more N.")
    aggregate.add_argument("--N", type=int, nargs="+", required=True)
    aggregate.add_argument("--allow-partial", action="store_true")
    return parser


def _load_config(args: argparse.Namespace) -> AnisotropicSweepConfig:
    config = AnisotropicSweepConfig.from_json(args.config)
    return smoke_config(config) if args.smoke else config


def run(args: argparse.Namespace) -> None:
    config = _load_config(args)
    if args.command == "describe":
        print(json.dumps(describe_config(config), indent=2))
        return

    if args.command == "describe-task":
        print(json.dumps(asdict(config.task_for_index(args.task_index)), indent=2))
        return

    run_root = args.run_root / "smoke" if args.smoke else args.run_root
    repository = AnisotropicRepository(run_root)
    if args.command == "simulate-N":
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "mode": "dry-run",
                        "N": args.N,
                        "workers": args.workers,
                        "hz_values": list(config.hz_values),
                        "j_values": list(config.j_values),
                        "jpm_values": list(config.jpm_values),
                        "configuration_count": len(config.hz_values) * len(config.j_values) * len(config.jpm_values),
                        "run_root": str(run_root),
                        "config_digest": config.digest,
                    },
                    indent=2,
                )
            )
            return
        service = AnisotropicSweepService(
            repository,
            QuSpinAnisotropicBackend(),
            BlueRedDiagnosticPlotter(),
        )
        done_path = service.run_n(config, args.N, workers=args.workers, force=args.force)
        manifest = BornHeatmapAggregator(repository).aggregate_n(config, args.N)
        print(f"Completed and plotted N={args.N}: {done_path}")
        print(f"Aggregated N={args.N}: {manifest}")
        return

    if args.command == "simulate-task":
        task = config.task_for_index(args.task_index)
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "mode": "dry-run",
                        "task": asdict(task),
                        "jpm_values": list(config.jpm_values),
                        "run_root": str(run_root),
                        "config_digest": config.digest,
                    },
                    indent=2,
                )
            )
            return
        service = AnisotropicSweepService(
            repository,
            QuSpinAnisotropicBackend(),
            BlueRedDiagnosticPlotter(),
        )
        done_path = service.run_task(config, task, force=args.force)
        print(f"Completed task {args.task_index}: {done_path}")
        return

    if args.command == "aggregate":
        aggregator = BornHeatmapAggregator(repository)
        for detector_n in args.N:
            manifest = aggregator.aggregate_n(config, detector_n, allow_partial=args.allow_partial)
            print(f"Aggregated N={detector_n}: {manifest}")
        return

    raise RuntimeError(f"unknown command {args.command!r}")


def main() -> None:
    run(_parser().parse_args())


if __name__ == "__main__":
    main()
