"""Continuous Autonomous Karpathy-style Research Loop for Born-Similarity Optimization at N=10.

Runs continuously in the background, systematically exploring structural Hamiltonian
configurations without fine-tuning, evaluating them with the fixed verifier,
and updating the champion and experiment log.

Usage:
    python scripts/run_autoresearch_loop.py --n-pixel 10 --max-candidates 5000
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

# Ensure repository root is in sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from scripts.eval_born import evaluate_born_score, DEFAULT_LONG_TIMES


def generate_structural_proposals():
    """Generator yielding structurally diverse physical candidate configurations."""
    # 1. Family: Antiferromagnetic Open Chains with Anisotropic Transverse Exchange
    for j_val in [-1.0, -0.75, -1.25, -1.50]:
        for hz in [1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.10]:
            for j_mean_perp in [0.18, 0.20, 0.25, 0.30]:
                for aniso_ratio in [1.5, 1.8, 2.0, 2.33, 2.5, 3.0]:
                    jyy = (2.0 * j_mean_perp) / (1.0 + aniso_ratio)
                    jxx = aniso_ratio * jyy
                    for jx in [0.035, 0.05, 0.065, 0.08]:
                        yield {
                            "name": f"afm_chain_J{j_val}_hz{hz}_perp{j_mean_perp:.2f}_r{aniso_ratio:.2f}_jx{jx}",
                            "hypothesis": f"AFM open chain J={j_val}, hz={hz}, Jxx={jxx:.3f}, Jyy={jyy:.3f}, Jx={jx}",
                            "config": {
                                "connectivity": "chain",
                                "central_coupling": "all",
                                "J": float(j_val),
                                "Jxx": float(round(jxx, 4)),
                                "Jyy": float(round(jyy, 4)),
                                "hz": float(hz),
                                "hz0": 0.0,
                                "hx": 0.0,
                                "hx0": 0.0,
                                "Jx": float(jx),
                                "Jy": 0.0,
                                "Jz": 0.0,
                                "use_symmetry": False,
                            }
                        }

    # 2. Family: Gapped Ferromagnetic Rings with Extended Cohesion J2
    for j_val in [1.0, 0.8, 1.2]:
        for j2_ratio in [0.15, 0.20, 0.25, 0.30]:
            j2 = j_val * j2_ratio
            for hz in [1.60, 1.709, 1.80, 2.0]:
                for jxx_yy in [0.12, 0.15, 0.18, 0.22]:
                    for jx in [0.04, 0.05, 0.06]:
                        yield {
                            "name": f"fm_ring_J{j_val}_j2{j2:.2f}_hz{hz}_jxx{jxx_yy}_jx{jx}",
                            "hypothesis": f"FM ring with extended cohesion J2={j2:.2f}, hz={hz}, Jxx=Jyy={jxx_yy}",
                            "config": {
                                "connectivity": "ring",
                                "central_coupling": "all",
                                "J": float(j_val),
                                "J2": float(round(j2, 4)),
                                "Jxx": float(jxx_yy),
                                "Jyy": float(jxx_yy),
                                "hz": float(hz),
                                "hz0": 0.0,
                                "hx": 0.0,
                                "hx0": 0.0,
                                "Jx": float(jx),
                                "Jy": 0.0,
                                "Jz": 0.0,
                                "use_symmetry": False,
                            }
                        }

    # 3. Family: AFM Chains with Cross-Coupling or Exchange Channels
    for jcpm in [0.01, 0.02, 0.03]:
        for hz in [1.55, 1.60, 1.65, 1.70, 1.75]:
            for jx in [0.04, 0.05, 0.065]:
                yield {
                    "name": f"afm_chain_jcpm{jcpm}_hz{hz}_jx{jx}",
                    "hypothesis": f"AFM XYZ chain with central spin-flip exchange Jcpm={jcpm}, jx={jx}",
                    "config": {
                        "connectivity": "chain",
                        "central_coupling": "all",
                        "J": -1.25,
                        "Jxx": 0.2667,
                        "Jyy": 0.1333,
                        "hz": float(hz),
                        "hz0": 0.0,
                        "hx": 0.0,
                        "hx0": 0.0,
                        "Jx": float(jx),
                        "Jy": 0.0,
                        "Jz": 0.0,
                        "Jcpm": float(jcpm),
                        "use_symmetry": False,
                    }
                }


def main():
    parser = argparse.ArgumentParser(description="Run autonomous research loop for Born similarity.")
    parser.add_argument("--n-pixel", type=int, default=10, help="Number of detector spins.")
    parser.add_argument("--log", type=Path, default=Path("reports/born_optimization/experiment_log.jsonl"))
    parser.add_argument("--champion", type=Path, default=Path("reports/born_optimization/champion.json"))
    parser.add_argument("--max-candidates", type=int, default=5000, help="Maximum candidates to evaluate.")
    args = parser.parse_args()

    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.champion.parent.mkdir(parents=True, exist_ok=True)

    # Read current champion
    current_best_s = -1.0
    if args.champion.is_file():
        try:
            champ = json.loads(args.champion.read_text(encoding="utf-8"))
            current_best_s = float(champ.get("metrics", {}).get("S_born", -1.0))
        except Exception:
            pass

    # Read already evaluated candidate names
    evaluated_names: set[str] = set()
    if args.log.is_file():
        try:
            with open(args.log, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            record = json.loads(line)
                            c_name = record.get("candidate")
                            if c_name:
                                evaluated_names.add(c_name)
                        except Exception:
                            pass
        except Exception:
            pass

    print(f"================================================================================", flush=True)
    print(f"[*] AUTONOMOUS BORN SEARCH LOOP STARTED at N={args.n_pixel}", flush=True)
    print(f"[*] Initial Champion S_Born: {current_best_s:.6f}", flush=True)
    print(f"[*] Prior evaluated candidates in log: {len(evaluated_names)}", flush=True)
    print(f"[*] Log file: {args.log}", flush=True)
    print(f"[*] Champion file: {args.champion}", flush=True)
    print(f"================================================================================", flush=True)

    evaluated_count = 0
    promoted_count = 0

    for proposal in generate_structural_proposals():
        if evaluated_count >= args.max_candidates:
            print(f"[*] Reached maximum candidate limit ({args.max_candidates}). Loop completed.", flush=True)
            break

        name = proposal["name"]
        if name in evaluated_names:
            continue

        evaluated_count += 1
        hypothesis = proposal["hypothesis"]
        config_data = proposal["config"]

        t_start = time.time()
        print(f"\n[#{evaluated_count}] Evaluating: {name}...", flush=True)
        print(f"     Hypothesis: {hypothesis}", flush=True)

        try:
            result = evaluate_born_score(config_data, n_pixel=args.n_pixel)
        except Exception as err:
            print(f"     [ERROR] Evaluation failed: {err}", flush=True)
            result = {"passed": False, "error": str(err), "S_born": -1.0}

        elapsed = time.time() - t_start
        s_born = result.get("S_born", -1.0)
        passed = result.get("passed", False)
        status_str = "PASSED" if passed else "REJECTED"
        coverage = result.get("coverage_bins", 0)
        err_abs = result.get("mean_abs_error", 1.0)

        print(f"     [{status_str}] S_Born = {s_born:.6f} | Error = {err_abs:.6f} | Cov = {coverage}/100 | Time = {elapsed:.2f}s", flush=True)

        decision = "REJECT"
        if passed and s_born > current_best_s:
            decision = "PROMOTE"
            promoted_count += 1
            print(f"     [!!!] NEW CHAMPION: S_Born improved from {current_best_s:.6f} to {s_born:.6f}!", flush=True)
            current_best_s = s_born
            champ_payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config": config_data,
                "metrics": result,
                "hypothesis": hypothesis,
            }
            with open(args.champion, "w", encoding="utf-8") as f:
                json.dump(champ_payload, f, indent=2)

        # Append to experiment log
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "candidate": name,
            "decision": decision,
            "config": config_data,
            "metrics": result,
            "hypothesis": hypothesis,
        }
        with open(args.log, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        evaluated_names.add(name)

    print(f"\n================================================================================", flush=True)
    print(f"[*] AUTONOMOUS BORN SEARCH LOOP FINISHED", flush=True)
    print(f"[*] Total newly evaluated: {evaluated_count} | Total promotions: {promoted_count}", flush=True)
    print(f"[*] Final Champion S_Born: {current_best_s:.6f}", flush=True)
    print(f"================================================================================", flush=True)


if __name__ == "__main__":
    main()
