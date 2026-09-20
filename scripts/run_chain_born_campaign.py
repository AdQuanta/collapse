"""Evaluate one agent-authored batch of endpoint-chain Born candidates.

The loop this serves is adaptive: the agent writes a batch file, runs it, reads
the results, and writes the next batch in light of them. Nothing here proposes
candidates, and nothing here decides what to try next. Committing a candidate
list to code would freeze it before any result is seen, which is exactly what the
adaptive loop forbids — so the batch is data, not a Python module.

A batch file is a JSON list of objects, each carrying a ``name``, a
``hypothesis`` stating the mechanism under test, a ``rung`` label, and whichever
of the twelve campaign parameters are nonzero::

    [
      {
        "name": "b2_chaotic_hz0.5",
        "rung": "2a",
        "hypothesis": "mixed-field Ising detector at the chaotic point; tests
                       whether detector ergodicity drives the roots toward Born",
        "Jzz": 1.0, "hx": 1.0, "hz": 0.5, "h0x": 1.0, "h0z": 1.0, "gz": 0.05
      }
    ]

Usage::

    python scripts/run_chain_born_campaign.py --batch batches/iteration_02.json
    python scripts/run_chain_born_campaign.py --summarize
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval_chain_born import (
    CAMPAIGN_VERSION,
    N_LADDER,
    TIMES,
    PARAMETER_NAMES,
    ChainConfig,
    detector_scale,
    evaluate_config,
    perturbative_ratio,
)

DEFAULT_LOG = Path("reports/chain_born_regions/experiment_log.jsonl")


def load_batch(path: Path) -> list[tuple[ChainConfig, list[float] | None]]:
    """Read and validate a batch file.

    Validation is strict on purpose. An unknown key is far more likely to be a
    typo for a real parameter — which would silently evaluate a different model
    than intended — than a deliberate annotation.
    """

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a JSON list of candidates")

    allowed = set(PARAMETER_NAMES) | {"name", "hypothesis", "rung", "times"}
    configs: list[tuple[ChainConfig, list[float] | None]] = []
    names: set[str] = set()
    for index, entry in enumerate(payload):
        entry = dict(entry)
        times = entry.pop("times", None)
        if times is not None and (not isinstance(times, list) or not times):
            raise ValueError(f"candidate {index} has a malformed 'times' override")
        unknown = set(entry) - allowed
        if unknown:
            raise ValueError(f"candidate {index} has unknown keys: {sorted(unknown)}")
        for required in ("name", "hypothesis", "rung"):
            if not entry.get(required):
                raise ValueError(f"candidate {index} is missing {required!r}")
        if entry["name"] in names:
            raise ValueError(f"duplicate candidate name {entry['name']!r}")
        names.add(entry["name"])
        configs.append((ChainConfig(**entry), times))
    return configs


def _evaluate(payload: dict) -> dict:
    """Worker entry point. Only plain data crosses the process boundary."""

    config = ChainConfig(**payload["config"])
    started = time.time()
    times = payload.get("times") or TIMES
    record = evaluate_config(config, n_values=tuple(payload["n_ladder"]), times=times)
    record["elapsed_seconds"] = time.time() - started
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    record["batch"] = payload["batch"]
    return record


def _already_evaluated(log_path: Path) -> set[str]:
    if not log_path.is_file():
        return set()
    seen: set[str] = set()
    with open(log_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                seen.add(json.loads(line)["name"])
            except (json.JSONDecodeError, KeyError):
                # A malformed line means an interrupted write, not a reason to
                # discard the rest of the log.
                continue
    return seen


def _read_log(log_path: Path) -> list[dict]:
    if not log_path.is_file():
        return []
    records = []
    with open(log_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _format_row(record: dict, n_ladder: list[int]) -> str:
    largest = str(max(n_ladder))
    block = record.get("by_size", {}).get(largest, {})
    if "S_born" not in block:
        reason = (record.get("rejection_reasons") or [""])[0]
        return f"{record['name']:<30s} {'FAIL':<5s} {reason[:64]}"
    summary = record.get("summary", {})
    window = "" if record.get("frozen_window", True) else " [diag-window]"
    return (
        f"{record['name']:<30s} "
        f"{'PASS' if record['passed'] else 'FAIL':<5s} "
        f"S={block['S_born']:+.4f}  "
        f"thin={block['S_born_thinned_mean']:+.4f}+/-{block['S_born_thinned_sd']:.3f}  "
        f"Emarg={block['E_marg_occupied']:.4f}  "
        f"cov={block['coverage_bins']:3d}  "
        f"raw={summary.get('raw_trend', float('nan')):+.4f}  "
        f"thin_trend={summary.get('thinned_trend', float('nan')):+.4f}" + window
    )


def summarize(log_path: Path, n_ladder: list[int], top: int) -> None:
    """Print the log ranked by the budget-controlled score.

    The ranking uses the thinned score at the largest size, never the raw one:
    the raw score rises with root count for reasons unrelated to Born, so ranking
    on it would systematically promote the largest models rather than the best
    ones.
    """

    records = _read_log(log_path)
    if not records:
        print(f"[*] no records in {log_path}")
        return
    largest = str(max(n_ladder))

    def key(record: dict) -> float:
        # Diagnostic-window records are never ranked against frozen-window ones.
        if not record.get("frozen_window", True):
            return float("-inf")
        block = record.get("by_size", {}).get(largest, {})
        value = block.get("S_born_thinned_mean")
        return value if value is not None else float("-inf")

    ranked = sorted(records, key=key, reverse=True)
    passed = [r for r in ranked if r.get("passed")]
    print(f"[*] {len(records)} candidates, {len(passed)} passed the frozen gates")
    print(f"[*] ranked by budget-controlled S_born at N={largest}\n")
    for record in ranked[:top]:
        print("   " + _format_row(record, n_ladder))
    print("\n[*] rungs present:",
          ", ".join(sorted({r.get("rung", "?") for r in records})))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path,
                        help="JSON batch file authored for this iteration.")
    parser.add_argument("--summarize", action="store_true",
                        help="Print the existing log instead of evaluating.")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--n-ladder", type=int, nargs="+", default=list(N_LADDER))
    parser.add_argument("--workers", type=int, default=4,
                        help="Parallel workers. Each holds a dense eigenbasis, "
                             "and heavy oversubscription inflates per-candidate "
                             "wall time well past the serial cost.")
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--rerun", action="store_true",
                        help="Re-evaluate candidates already present in the log.")
    args = parser.parse_args()

    if args.summarize:
        summarize(args.log, args.n_ladder, args.top)
        return
    if not args.batch:
        parser.error("either --batch or --summarize is required")

    # One BLAS thread per worker: the dense eigensolvers scale poorly across
    # threads here, so oversubscribing costs more than it returns.
    for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                     "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(variable, "1")

    batch = load_batch(args.batch)
    for config, _ in batch:
        if detector_scale(config) == 0.0:
            raise ValueError(f"{config.name!r} has no nonzero non-coupling parameter")
        ratio = perturbative_ratio(config)
        if ratio > 0.1 * (1 + 1e-9):
            raise ValueError(
                f"{config.name!r} violates the perturbative rule before it is run: "
                f"max|g| / min|nonzero other| = {ratio:.4f} > 0.1"
            )

    if not args.rerun:
        seen = _already_evaluated(args.log)
        skipped = [c for c, _ in batch if c.name in seen]
        batch = [(c, t) for c, t in batch if c.name not in seen]
        if skipped:
            print(f"[*] skipping {len(skipped)} already in the log: "
                  f"{', '.join(c.name for c in skipped[:5])}"
                  f"{' ...' if len(skipped) > 5 else ''}")
    if not batch:
        print("[*] nothing new to evaluate")
        return

    args.log.parent.mkdir(parents=True, exist_ok=True)
    print(f"[*] batch {args.batch.name}: {len(batch)} candidates "
          f"over N={tuple(args.n_ladder)} on {args.workers} workers")

    payloads = [
        {"config": vars(config), "n_ladder": list(args.n_ladder),
         "batch": args.batch.stem, "times": times}
        for config, times in batch
    ]
    results: list[dict] = []
    started = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_evaluate, p): p for p in payloads}
        for index, future in enumerate(as_completed(futures), start=1):
            try:
                record = future.result()
            except Exception as error:
                # One candidate must never abort the batch. Record the failure
                # against its name so the loop keeps its place and the cause is
                # visible in the log rather than only in a traceback.
                payload = futures[future]
                record = {
                    "campaign_version": CAMPAIGN_VERSION,
                    "name": payload["config"]["name"],
                    "rung": payload["config"]["rung"],
                    "hypothesis": payload["config"]["hypothesis"],
                    "parameters": {k: v for k, v in payload["config"].items()
                                   if k in PARAMETER_NAMES},
                    "by_size": {},
                    "passed": False,
                    "rejection_reasons": [f"worker raised {type(error).__name__}: {error}"],
                    "elapsed_seconds": float("nan"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "batch": payload["batch"],
                }
            results.append(record)
            with open(args.log, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
            print(f"[{index:3d}/{len(payloads)}] " + _format_row(record, args.n_ladder),
                  flush=True)

    elapsed = time.time() - started
    passed = sum(1 for r in results if r["passed"])
    print(f"\n[*] {passed}/{len(results)} passed the frozen gates in {elapsed:.1f}s")
    print("[*] a region, not a point, is the unit of promotion: no candidate here "
          "is promoted on its score alone")


if __name__ == "__main__":
    main()
