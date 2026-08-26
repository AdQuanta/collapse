"""Run one reproducible dense single-pixel classification point from JSON."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
import tempfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "collapse_matplotlib_cache"),
)

from collapse.hamiltonian_classification import (
    SinglePixelClassificationPoint,
    classify_single_pixel_point,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    complete = output / "COMPLETE.json"
    if complete.is_file() and not args.force:
        print(f"already complete: {output}")
        return
    payload = json.loads(args.config.resolve().read_text(encoding="utf-8"))
    point = SinglePixelClassificationPoint(**payload)
    result = classify_single_pixel_point(point, verbose=not args.quiet)
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output / "roots_and_full_sphere.npz",
        alpha=result.alpha,
        beta=result.beta,
        bloch_vectors_0=result.bloch_vectors_0,
        asymmetry=result.asymmetry,
        power_by_l=result.power_by_l,
    )
    summary = dict(result.summary)
    summary["provenance"] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "config_file": str(args.config.resolve()),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pbs_job_id": os.environ.get("PBS_JOBID"),
        "pbs_array_index": os.environ.get("PBS_ARRAY_INDEX"),
    }
    temporary = output / "result.json.tmp"
    temporary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output / "result.json")
    complete_temporary = output / "COMPLETE.json.tmp"
    complete_temporary.write_text(
        json.dumps(
            {
                "schema_version": summary["schema_version"],
                "completed_utc": datetime.now(timezone.utc).isoformat(),
                "qz_valid": summary["qz_valid"],
                "root_count": summary["root_count"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    complete_temporary.replace(complete)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
