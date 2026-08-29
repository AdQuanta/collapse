"""Canonical family definitions for the heavy-tail/Born two-pixel study."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import wasserstein_distance

from core.two_pixel_study import (
    AngularDiagnosticService,
    ComparisonSimulator,
    ComparisonSpec,
    load_raw,
)


@dataclass(frozen=True)
class ConjectureFamily:
    """One parameter sweep used in the 2026-07-16 conjecture evidence."""

    name: str
    title: str
    parameter_name: str
    parameter_symbol: str
    values: tuple[float, ...]
    j: float
    jpm_mode: str
    hz_mode: str
    hz0_mode: str

    def parameters(self, value: float) -> dict[str, float]:
        jpm = value if self.jpm_mode == "parameter" else float(self.jpm_mode)
        hz = value if self.hz_mode == "parameter" else float(self.hz_mode)
        hz0 = value if self.hz0_mode == "parameter" else float(self.hz0_mode)
        return {"j": self.j, "jpm": jpm, "hz": hz, "hz0": hz0}


def _neighborhoods(centers: tuple[float, ...]) -> tuple[float, ...]:
    offsets = (-0.05, -0.01, 0.0, 0.01, 0.05)
    return tuple(round(center + offset, 10) for center in centers for offset in offsets)


def conjecture_families() -> tuple[ConjectureFamily, ...]:
    """Return the exact four grids underlying the conjecture report."""

    return (
        ConjectureFamily(
            name="hz0",
            title="central-field matching",
            parameter_name="hz0",
            parameter_symbol=r"$h_{z0}$",
            values=(0.0, 0.05, 0.09, 0.10, 0.11, 0.15, 0.20),
            j=1.0,
            jpm_mode="0",
            hz_mode="0.1",
            hz0_mode="parameter",
        ),
        ConjectureFamily(
            name="hz_resonance",
            title="Ising-field resonance neighborhoods",
            parameter_name="hz",
            parameter_symbol=r"$h_z$",
            values=_neighborhoods((-2.0, 0.0, 2.0)),
            j=1.0,
            jpm_mode="0",
            hz_mode="parameter",
            hz0_mode="0",
        ),
        ConjectureFamily(
            name="jpm_coupling",
            title="plus-minus coupling sweep",
            parameter_name="Jpm",
            parameter_symbol=r"$J_{\pm}$",
            values=(0.0, 0.001, 0.01, 0.03, 0.1, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0),
            j=1.0,
            jpm_mode="parameter",
            hz_mode="0.1",
            hz0_mode="0",
        ),
        ConjectureFamily(
            name="jpm_hz",
            title=r"$J=0$, $J_{\pm}=1$ field neighborhoods",
            parameter_name="hz",
            parameter_symbol=r"$h_z$",
            values=_neighborhoods((-2.0, -1.0, 0.0, 1.0, 2.0)),
            j=0.0,
            jpm_mode="1",
            hz_mode="parameter",
            hz0_mode="0",
        ),
    )


def _value_tag(value: float) -> str:
    return f"{value:+.6g}".replace("+", "p").replace("-", "m").replace(".", "p")


def family_specs(
    family: ConjectureFamily,
    *,
    detector_spins: int = 8,
) -> tuple[ComparisonSpec, ...]:
    specs: list[ComparisonSpec] = []
    for index, value in enumerate(family.values):
        parameters = family.parameters(value)
        label = rf"{family.parameter_symbol}=${value:g}$"
        base_key = f"{family.name}_{index:02d}_{_value_tag(value)}"
        for kind in ("single", "two"):
            specs.append(
                ComparisonSpec(
                    key=f"{base_key}_{kind}",
                    label=("single: " if kind == "single" else "two: ") + label,
                    kind=kind,
                    detector_spins=detector_spins,
                    family=family.name,
                    parameter_name=family.parameter_name,
                    parameter_value=value,
                    **parameters,
                )
            )
    return tuple(specs)


def all_specs(detector_spins: int = 8) -> tuple[ComparisonSpec, ...]:
    return tuple(
        spec
        for family in conjecture_families()
        for spec in family_specs(family, detector_spins=detector_spins)
    )


def pair_specs(specs: tuple[ComparisonSpec, ...]) -> tuple[tuple[ComparisonSpec, ComparisonSpec], ...]:
    groups: dict[tuple[str, float], dict[str, ComparisonSpec]] = {}
    for spec in specs:
        groups.setdefault((spec.family, spec.parameter_value), {})[spec.kind] = spec
    output = []
    for key in sorted(groups, key=lambda item: (item[0], item[1])):
        models = groups[key]
        output.append((models["single"], models["two"]))
    return tuple(output)


def paired_distance_records(
    raw_root: Path,
    specs: tuple[ComparisonSpec, ...],
    times: tuple[float, ...],
    diagnostics: AngularDiagnosticService,
) -> list[dict[str, float | str]]:
    """Quantify the distribution change caused by detector splitting."""

    simulator = ComparisonSimulator(raw_root)
    rows: list[dict[str, float | str]] = []
    for single, two in pair_specs(specs):
        for time_value in times:
            raw_single = load_raw(simulator.raw_path(single, time_value))
            raw_two = load_raw(simulator.raw_path(two, time_value))
            ds = diagnostics.distributions(raw_single)
            dt = diagnostics.distributions(raw_two)
            probability_single = ds["p_theta"] * np.diff(diagnostics.edges)
            probability_two = dt["p_theta"] * np.diff(diagnostics.edges)
            joint = np.isfinite(ds["ratio"]) & np.isfinite(dt["ratio"])
            ratio_rmse = (
                float(np.sqrt(np.mean((ds["ratio"][joint] - dt["ratio"][joint]) ** 2)))
                if np.any(joint)
                else float("nan")
            )
            rows.append(
                {
                    "family": single.family,
                    "parameter_name": single.parameter_name,
                    "parameter_value": single.parameter_value,
                    "time": time_value,
                    "theta_wasserstein": float(
                        wasserstein_distance(raw_single["theta"], raw_two["theta"])
                    ),
                    "theta_js_divergence": float(
                        jensenshannon(probability_single, probability_two, base=2.0) ** 2
                    ),
                    "R_rmse_between_models": ratio_rmse,
                    "common_R_bin_fraction": float(np.mean(joint)),
                }
            )
    return rows
