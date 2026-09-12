"""Recompute positive ring leads from immutable saved root arrays."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.born import born_ratio_from_theta
from core.born_reciprocity import cosine_moments, born_moment_residuals
from core.weak_coupling_evidence_plotting import plot_ring_evidence


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/born_weak_coupling_2026-09-12.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    if cfg["schema_version"] != 1 or cfg["theta_bins"] != 64 or cfg["moment_order"] != 16:
        raise ValueError("audit requires schema 1, 64 bins and eight moment relations")
    args.output.mkdir(parents=True, exist_ok=False)
    records, scans, source_hashes = [], {}, {}
    for candidate in cfg["candidates"]:
        name = candidate["name"]
        scan_path = ROOT / candidate["field_scan"]
        scans[name] = [
            {k: row[k] for k in ("hz0_over_hz", "global_RMSE", "global_S_born")}
            for row in json.loads(scan_path.read_text())["rows"]
        ]
        source_hashes[candidate["field_scan"]] = digest(scan_path)
        for n in cfg["sizes"]:
            directory = ROOT / candidate["source"] / f"N{n}"
            complete = json.loads((directory / "COMPLETE.json").read_text())
            for filename in ("results.npz", "metadata.json", "metrics.json", "validation.json"):
                path = directory / filename
                actual = digest(path)
                if actual != complete["files"][filename]:
                    raise ArithmeticError(f"saved source hash mismatch: {path.relative_to(ROOT)}")
                source_hashes[str(path.relative_to(ROOT))] = actual
            metadata = json.loads((directory / "metadata.json").read_text())
            saved = json.loads((directory / "metrics.json").read_text())
            src = metadata["source"]
            if (metadata["target_N"] != n or src["jy"] != 0 or src["hz0"] != 0
                    or src["evolution_time"] != 1e6):
                raise ValueError("source does not match the documented X-only reference")
            if not np.isclose(metadata["Jx_effective"], src["jx"] / np.sqrt(n), rtol=1e-13, atol=0):
                raise ArithmeticError("source transverse normalization mismatch")
            with np.load(directory / "results.npz", allow_pickle=False) as data:
                theta = data["theta"]
                if len(theta) != 2**n or not np.all(np.isfinite(theta)):
                    raise ArithmeticError("invalid saved root count or angle")
                polar = born_ratio_from_theta(theta, np.pi-theta, n_theta=64)
                counts, _ = np.histogram(theta, bins=np.linspace(0, np.pi, 65))
                reflected, _ = np.histogram(np.pi-theta, bins=np.linspace(0, np.pi, 65))
                occupied = counts + reflected > 0
                delta = polar.ratio[occupied] - polar.born[occupied]
                rmse = float(np.sqrt(np.mean(delta**2)))
                if abs(rmse - saved["born_RMSE_occupied"]) > 1e-12:
                    raise ArithmeticError("recomputed ratio differs from saved metric")
                moments = cosine_moments(theta, cfg["moment_order"])
                residuals = born_moment_residuals(moments)
                record = dict(
                    candidate=name, N=n, time=src["evolution_time"],
                    source=str(directory.relative_to(ROOT)),
                    positive_sign_parameters=dict(
                        qubit_field=[0., 0., -src["hz0"]],
                        detector_field=[0., 0., -src["hz"]],
                        nearest=[-src["jpm"]/2, -src["jpm"]/2, -src["j"]],
                        second=[-src["jpm2"]/2, -src["jpm2"]/2, -src["j2"]],
                        coupling=[-src["jx"], -src["jy"], 0.],
                    ),
                    coverage=float(np.mean(occupied)),
                    global_rmse=rmse if np.all(occupied) else None,
                    global_linf=float(max(abs(delta))) if np.all(occupied) else None,
                    moments=moments.tolist(), moment_residuals=residuals.tolist(),
                    moment_max=float(max(abs(residuals))),
                    S_born_100=born_ratio_from_theta(theta, np.pi-theta).similarity,
                    saved_S_born=saved["S_born"],
                    centers=((np.arange(64)+.5)*np.pi/64).tolist(),
                    density=(counts/len(theta)*64/np.pi).tolist(),
                    reflected_density=(reflected/len(theta)*64/np.pi).tolist(),
                    ratio=[float(v) if ok else None for v, ok in zip(polar.ratio, occupied)],
                    saved_phi_harmonic_2=saved["phi_harmonic_2"],
                    validation_scope="Source integrity and histogram recomputation; no new QZ residual certification",
                )
                records.append(record)
    plot_ring_evidence(args.output, records, scans)
    payload = dict(records=records, field_scans=scans)
    (args.output / "evidence.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    sources = ["scripts/audit_born_weak_coupling.py", "core/weak_coupling_evidence_plotting.py",
               "core/ring_chain_family.py", "core/weak_coupling_picture.py",
               "core/born.py", "core/born_reciprocity.py",
               "tests/test_ring_chain_weak_coupling.py"]
    provenance = dict(
        config=cfg, config_sha256=digest(args.config),
        source_hashes=source_hashes,
        defining_code_hashes={p: digest(ROOT/p) for p in sources},
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        python=platform.python_version(), numpy=np.__version__,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        output_hashes={p.name: digest(p) for p in sorted(args.output.iterdir())},
        scope="Selected existing finite-N single-time leads; exact robust Born phase remains unproved",
    )
    (args.output / "provenance.json").write_text(json.dumps(provenance, indent=2)+"\n")
    print(json.dumps([{k: r[k] for k in ("candidate", "N", "global_rmse", "moment_max", "coverage")}
                      for r in records], indent=2))


if __name__ == "__main__":
    main()
