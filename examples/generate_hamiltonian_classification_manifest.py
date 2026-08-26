"""Generate a deterministic CSV manifest for the Zeus classification array."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "hamiltonian_classification_zeus_campaign.json"


def expanded_points(config: dict[str, object]) -> list[dict[str, object]]:
    points: list[dict[str, object]] = []
    for campaign in config["campaigns"]:
        detector_sizes = campaign.get("detector_sizes", config["detector_sizes"])
        backend = campaign.get("backend", config["backend"])
        seeds = campaign.get("seeds", [config["common"]["seed"]])
        for detector_n in detector_sizes:
            for evolution_time in campaign["times"]:
                for raw_value in campaign["values"]:
                    for raw_seed in seeds:
                        name = campaign["name"]
                        value: float | str = (
                            str(raw_value)
                            if campaign.get("value_kind") == "categorical"
                            else float(raw_value)
                        )
                        parameters = dict(config["common"])
                        parameters.update(campaign.get("overrides", {}))
                        if "variant_overrides" in campaign:
                            variant_overrides = campaign["variant_overrides"]
                            if str(value) not in variant_overrides:
                                raise ValueError(
                                    f"missing overrides for variant {value!r}"
                                )
                            parameters.update(variant_overrides[str(value)])
                        parameters.update(
                            {
                                "detector_n": int(detector_n),
                                "time": float(evolution_time),
                                "backend": backend,
                                "seed": int(raw_seed),
                            }
                        )
                        if name == "transverse_strength":
                            parameters["Jx"] = value
                        elif name == "matched_detuning":
                            parameters["hz0"] = (
                                float(parameters["hz"])
                                + float(value) * float(parameters["Jx"])
                            )
                        elif name == "second_transverse_channel":
                            parameters["Jy"] = float(value) * float(parameters["Jx"])
                        elif name == "detector_transverse_scrambling":
                            parameters["hx"] = value
                        elif campaign["parameter"] == "connectivity":
                            parameters["connectivity"] = value
                        elif name == "cross_physical_architectures":
                            pass
                        elif name not in {
                            "matched_qz_reproduction",
                            "haar_unitary_null",
                        }:
                            raise ValueError(f"unsupported campaign {name!r}")
                        points.append(
                            {
                                "point_id": len(points),
                                "campaign": name,
                                "scan_parameter": campaign["parameter"],
                                "scan_value": value,
                                "detector_n": int(detector_n),
                                "time": float(evolution_time),
                                "parameters_json": json.dumps(parameters, sort_keys=True),
                            }
                        )
    return points


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.resolve().read_text(encoding="utf-8"))
    points = expanded_points(config)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(points[0]))
        writer.writeheader()
        writer.writerows(points)
    temporary.replace(output)
    print(
        json.dumps(
            {
                "manifest": str(output),
                "points": len(points),
                "array_size": config["array_size"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
