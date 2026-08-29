"""Build approved 3x5 comparisons for every resampled-network configuration.

The campaign contains 20 selected source configurations for each of four graph
families.  Each output compares the five independent graph realizations of one
source configuration.  Existing complete PNG/JSON pairs are skipped so the
batch is restart-safe.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_network_extremes_resampled_sample_3x5 import (  # noqa: E402
    DEFAULT_SOURCE,
    build_sample,
)


DEFAULT_OUTPUT_DIR = (
    ROOT / "reports" / "network_extremes_resampled_3x5_all_2026-08-14"
)


def discover_selections(source: Path) -> tuple[str, ...]:
    """Return campaign selections with exactly five completed N=12 results."""
    selections: list[str] = []
    for family_dir in sorted(source.glob("family_*")):
        if not family_dir.is_dir():
            continue
        for cohort_dir in sorted(family_dir.glob("*_??")):
            if not cohort_dir.is_dir():
                continue
            complete = all(
                (
                    cohort_dir
                    / f"realization_{realization:02d}"
                    / "N12"
                    / "COMPLETE.json"
                ).is_file()
                for realization in range(1, 6)
            )
            if complete:
                selections.append(cohort_dir.relative_to(source).as_posix())
    return tuple(selections)


def output_path(output_dir: Path, selection: str) -> Path:
    """Map a campaign selection to a unique, readable PNG path."""
    family, cohort = Path(selection).parts
    short_family = family.removeprefix("family_")
    return output_dir / short_family / f"{cohort}.png"


def _build_one(
    source: Path,
    selection: str,
    output: Path,
    dpi: int,
) -> dict[str, Any]:
    result = build_sample(source, selection, output, dpi=dpi)
    return {
        "selection": selection,
        "output": result["output"],
        "status": "generated",
    }


def build_all(
    source: Path,
    output_dir: Path,
    *,
    dpi: int,
    max_workers: int,
) -> dict[str, Any]:
    """Generate all campaign figures and return a reproducibility manifest."""
    selections = discover_selections(source)
    if len(selections) != 80:
        raise RuntimeError(
            f"expected 80 complete configurations, found {len(selections)} in {source}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    pending: list[tuple[str, Path]] = []
    for selection in selections:
        output = output_path(output_dir, selection)
        if output.is_file() and output.with_suffix(".json").is_file():
            results.append(
                {
                    "selection": selection,
                    "output": str(output.resolve()),
                    "status": "skipped_existing",
                }
            )
        else:
            pending.append((selection, output))

    if max_workers == 1:
        for selection, output in pending:
            results.append(_build_one(source, selection, output, dpi))
            print(f"completed {selection}", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_build_one, source, selection, output, dpi): selection
                for selection, output in pending
            }
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(f"completed {result['selection']}", flush=True)

    results.sort(key=lambda item: str(item["selection"]))
    manifest = {
        "source": str(source.resolve()),
        "output_dir": str(output_dir.resolve()),
        "configuration_count": len(selections),
        "realizations_per_configuration": 5,
        "dpi": dpi,
        "max_workers": max_workers,
        "generated_count": sum(item["status"] == "generated" for item in results),
        "skipped_existing_count": sum(
            item["status"] == "skipped_existing" for item in results
        ),
        "results": results,
    }
    manifest_path = output_dir / "manifest.json"
    temporary = manifest_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    temporary.replace(manifest_path)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--max-workers", type=int, default=2)
    args = parser.parse_args()
    if args.dpi <= 0:
        parser.error("--dpi must be positive")
    if args.max_workers <= 0:
        parser.error("--max-workers must be positive")
    manifest = build_all(
        args.source.resolve(),
        args.output_dir.resolve(),
        dpi=args.dpi,
        max_workers=args.max_workers,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
