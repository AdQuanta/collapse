"""Parallel batch runner for the preferred-basis campaign (WP3, WP4, WP5).

Companion to ``scripts/run_chain_born_campaign.py``, adapted for
``scripts/eval_preferred_basis.py``. Candidate lists are JSON files produced
by ``scripts/generate_preferred_basis_candidates.py`` (data, not code, per the
house convention in ``wiki/campaigns/chain-born-regions.md``). Results are
appended to a JSONL log; a candidate already in the log is skipped unless
``--rerun`` is passed.

Usage::

    python scripts/run_preferred_basis_campaign.py \
        --batch batches/preferred_basis_wp3.json --n-ladder 8 --workers 6
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
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

DEFAULT_LOG = Path("reports/preferred_basis/experiment_log.jsonl")


def _already_evaluated(log_path: Path, n_ladder: tuple[int, ...]) -> set[str]:
    """Return candidate names whose *latest* record already covers every size
    in ``n_ladder``. A name evaluated only at other sizes (e.g. N=8 in an
    earlier batch) is not considered done for a different ``n_ladder``: the
    log is one file shared across every size this campaign runs, and the
    dedup must be size-aware or a later N-ladder silently reuses an earlier
    one's skip list."""

    if not log_path.exists():
        return set()
    latest: dict[str, dict] = {}
    with open(log_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                latest[record["name"]] = record
            except (json.JSONDecodeError, KeyError):
                continue
    required = {str(n) for n in n_ladder}
    return {
        name for name, record in latest.items()
        if required.issubset(set(record.get("by_size", {}).keys()))
    }


def _evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    # Imported inside the worker: ProcessPoolExecutor workers each import
    # fresh, and this keeps the parent process free of the heavy numpy/scipy
    # import cost until a worker actually needs it.
    from eval_chain_born import ChainConfig
    from eval_preferred_basis import evaluate_config
    import numpy as np

    config = ChainConfig(**payload["config"])
    reference_axis = np.asarray(payload["reference_axis"], dtype=float)
    started = time.time()
    record = evaluate_config(config, tuple(payload["n_ladder"]), reference_axis)
    record["elapsed_seconds"] = time.time() - started
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    record["batch"] = payload["batch"]
    return record


def _format_row(record: dict[str, Any], n_ladder: tuple[int, ...]) -> str:
    status = "PASS" if record.get("passed") else "REJECT"
    parts = [f"{record.get('name', '?'):28s} {status:6s}"]
    for n_pixel in n_ladder:
        block = record.get("by_size", {}).get(str(n_pixel), {})
        if "error" in block:
            parts.append(f"N={n_pixel}:ERR")
        elif block.get("axis_status") == "ok":
            parts.append(
                f"N={n_pixel}:B1={block['B1']:+.3f}"
                f",ae={block.get('axis_angle_deg_from_reference', float('nan')):.2f}"
            )
        elif block.get("axis_status"):
            parts.append(f"N={n_pixel}:refused")
        else:
            parts.append(f"N={n_pixel}:-")
    elapsed = record.get("elapsed_seconds")
    if elapsed is not None:
        parts.append(f"{elapsed:.1f}s")
    return "  ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--n-ladder", type=int, nargs="+", default=[8])
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()

    for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                     "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(variable, "1")

    candidates = json.loads(args.batch.read_text(encoding="utf-8"))
    if not args.rerun:
        seen = _already_evaluated(args.log, tuple(args.n_ladder))
        before = len(candidates)
        candidates = [c for c in candidates if c["name"] not in seen]
        if before != len(candidates):
            print(f"[*] skipping {before - len(candidates)} already in the log")
    if not candidates:
        print("[*] nothing new to evaluate")
        return

    args.log.parent.mkdir(parents=True, exist_ok=True)
    print(f"[*] batch {args.batch.name}: {len(candidates)} candidates "
          f"over N={tuple(args.n_ladder)} on {args.workers} workers")

    payloads = []
    for candidate in candidates:
        candidate = dict(candidate)
        reference_axis = candidate.pop("reference_axis")
        payloads.append({
            "config": candidate,
            "reference_axis": reference_axis,
            "n_ladder": list(args.n_ladder),
            "batch": args.batch.stem,
        })

    started = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_evaluate, p): p for p in payloads}
        for index, future in enumerate(as_completed(futures), start=1):
            try:
                record = future.result()
            except Exception as error:
                payload = futures[future]
                record = {
                    "name": payload["config"]["name"],
                    "rung": payload["config"].get("rung", ""),
                    "hypothesis": payload["config"].get("hypothesis", ""),
                    "by_size": {},
                    "passed": False,
                    "rejection_reasons": [f"worker raised {type(error).__name__}: {error}"],
                    "elapsed_seconds": float("nan"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "batch": payload["batch"],
                }
            with open(args.log, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
            print(f"[{index:3d}/{len(payloads)}] " + _format_row(record, tuple(args.n_ladder)),
                  flush=True)

    elapsed = time.time() - started
    print(f"\n[*] {len(payloads)} candidates evaluated in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
