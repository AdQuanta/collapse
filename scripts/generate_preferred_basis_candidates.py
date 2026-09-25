"""Generate the WP3 (region cloud) and WP5 (mechanism rotation) candidate
lists for the preferred-basis campaign (``goal_preferred_basis.md``).

Candidate lists are data, not code, matching the house convention in
``wiki/campaigns/chain-born-regions.md``: this script is run once per batch
and its JSON output is committed/logged, not regenerated implicitly by the
evaluator.

WP3: eight generic perturbation directions per seed at a stated relative
radius (goal section 4, WP3), confined to `screen_00`'s active parameters and
scaled componentwise (see ``wp3_region_cloud``'s docstring for why). The same
directions per seed are reused at every radius in ``--radii`` so the
degradation profile is genuinely about those directions, not fresh draws at
each radius.

WP5: eight fixed directions for ``h_0`` at constant ``|h_0|``, holding every
other parameter at `screen_00`. Three are the coordinate axes (including
``h_0 || x``, the known null control from `wiki/campaigns/chain-born-regions.md`
item 8, which this WP is explicitly checking is a mechanism-breaking control
and not an accident of that one cell), one is the `screen_00` direction
itself as a reference point, and four are additional generic directions from
a fixed seed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

SCREEN_00 = {
    "h0x": -1.35, "h0y": -1.69, "h0z": 2.01,
    "hx": -1.34, "hy": 0.0, "hz": 1.00,
    "Jxx": 1.32, "Jyy": 2.53, "Jzz": 1.10,
    "gx": 0.10, "gy": 0.05, "gz": 0.06,
}
PARAMETER_ORDER = (
    "h0x", "h0y", "h0z", "hx", "hy", "hz", "Jxx", "Jyy", "Jzz", "gx", "gy", "gz",
)
H0_KEYS = ("h0x", "h0y", "h0z")
H0_MAGNITUDE = float(np.linalg.norm([SCREEN_00[k] for k in H0_KEYS]))


def _base_vector() -> np.ndarray:
    return np.array([SCREEN_00[key] for key in PARAMETER_ORDER], dtype=float)


def _unit_directions(seed: int, count: int, dimension: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=(count, dimension))
    return raw / np.linalg.norm(raw, axis=1, keepdims=True)


def wp3_region_cloud(seeds: tuple[int, ...], n_directions: int, radii: tuple[float, ...]) -> list[dict]:
    """Perturb `screen_00` in ``n_directions`` generic directions per seed.

    Directions are confined to the already-active subspace (the nonzero
    parameters; `screen_00` has ``h_y = 0``): a dense direction with a
    component in a currently-zero coordinate collapses the perturbative-rule
    denominator (``detector_scale`` = the *minimum* nonzero non-coupling
    parameter) and rejects essentially every candidate, exactly the failure
    mode `wiki/campaigns/chain-born-regions.md` already documents ("the
    perturbative rule blocks generic perturbation testing... introducing a
    small term in a currently-inactive direction makes it the minimum and
    collapses the coupling ceiling"). Restricting to the active subspace is
    not a gate change -- it matches how that page's own 20%/35%/50% cloud
    tables were necessarily produced, since a dense direction would have hit
    the same collapse there. The unresolved "rule decision" that page calls
    for is left unresolved here too (CLAUDE.md forbids tuning gates after
    seeing results), and this restriction -- and the reasoning above -- is
    disclosed in the result packet as WP3's own limitation.

    Each parameter is displaced by ``radius`` times *its own* magnitude, not a
    globally-normalized displacement applied uniformly across all eleven
    active parameters: `screen_00`'s couplings (``|g| <= 0.10``) are roughly
    thirty times smaller than its fields and detector couplings (down to
    ``h_z = 1.00``), a scale separation the perturbative rule itself demands,
    so a single global-norm perturbation vector applies a wildly
    disproportionate *relative* shift to the couplings and reliably pushes
    the ratio past 0.1 regardless of direction. Componentwise scaling is the
    only reading of "20% relative radius" under which "relative" can mean the
    same thing for every parameter at once.
    """

    base = _base_vector()
    active = base != 0.0
    candidates: list[dict] = []
    for seed in seeds:
        raw_directions = _unit_directions(seed, n_directions, int(np.count_nonzero(active)))
        for direction_index, raw_direction in enumerate(raw_directions):
            direction = np.zeros_like(base)
            direction[active] = raw_direction
            for radius in radii:
                displaced = base + radius * np.abs(base) * direction
                params = dict(zip(PARAMETER_ORDER, displaced.tolist()))
                name = f"wp3_seed{seed}_dir{direction_index}_r{int(round(radius * 100)):02d}"
                candidates.append({
                    "name": name,
                    "hypothesis": (
                        f"WP3 region cloud: seed {seed}, direction {direction_index}, "
                        f"radius {radius:.0%} of |screen_00|"
                    ),
                    "rung": f"wp3_r{int(round(radius * 100)):02d}",
                    "reference_axis": [SCREEN_00["h0x"], SCREEN_00["h0y"], SCREEN_00["h0z"]],
                    **params,
                })
    return candidates


def wp5_mechanism_rotation(seed: int, n_generic: int) -> list[dict]:
    base = SCREEN_00
    fixed = {key: base[key] for key in PARAMETER_ORDER if key not in H0_KEYS}
    directions: dict[str, np.ndarray] = {
        "axis_x": np.array([1.0, 0.0, 0.0]),
        "axis_y": np.array([0.0, 1.0, 0.0]),
        "axis_z": np.array([0.0, 0.0, 1.0]),
        "screen_00_direction": np.array([base[k] for k in H0_KEYS]) / H0_MAGNITUDE,
    }
    for index, direction in enumerate(_unit_directions(seed, n_generic, 3)):
        directions[f"generic_{index}"] = direction

    candidates: list[dict] = []
    for label, direction in directions.items():
        h0 = H0_MAGNITUDE * direction
        params = dict(zip(H0_KEYS, h0.tolist()))
        params.update(fixed)
        candidates.append({
            "name": f"wp5_{label}",
            "hypothesis": (
                f"WP5 mechanism rotation: h_0 direction '{label}' at fixed |h_0|"
            ),
            "rung": "wp5",
            "reference_axis": h0.tolist(),
            **params,
        })
    return candidates


def wp4_weak_coupling_sweep(epsilons: tuple[float, ...]) -> list[dict]:
    """Rescale only the coupling magnitude, holding its direction and every
    other parameter fixed at `screen_00` (already normalized to
    ``detector_scale = 1``, so ``epsilon`` and ``max|g|`` coincide there).

    ``screen_00`` itself sits at ``epsilon = 0.10`` (``gx=0.10`` is already the
    campaign's minimum nonzero non-coupling parameter, ``hz=1.00``), so this
    sweep asks whether ``B1`` moves toward 1 as the coupling is weakened from
    that point, holding the coupling's direction ``(g_x, g_y, g_z) /
    max|g|`` fixed (goal section 4, WP4).
    """

    g_direction = np.array([SCREEN_00["gx"], SCREEN_00["gy"], SCREEN_00["gz"]])
    g_direction = g_direction / np.max(np.abs(g_direction))
    fixed = {key: SCREEN_00[key] for key in PARAMETER_ORDER if key not in ("gx", "gy", "gz")}
    candidates: list[dict] = []
    for epsilon in epsilons:
        g = epsilon * g_direction
        params = dict(zip(("gx", "gy", "gz"), g.tolist()))
        params.update(fixed)
        candidates.append({
            "name": f"wp4_eps{epsilon:.3f}".replace(".", "p"),
            "hypothesis": f"WP4 weak-coupling sweep: epsilon = {epsilon}",
            "rung": "wp4",
            "reference_axis": [SCREEN_00["h0x"], SCREEN_00["h0y"], SCREEN_00["h0z"]],
            **params,
        })
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wp3-out", type=Path, default=Path("batches/preferred_basis_wp3.json"))
    parser.add_argument("--wp4-out", type=Path, default=Path("batches/preferred_basis_wp4.json"))
    parser.add_argument("--wp5-out", type=Path, default=Path("batches/preferred_basis_wp5.json"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[101, 102])
    parser.add_argument("--n-directions", type=int, default=8)
    parser.add_argument("--radii", type=float, nargs="+", default=[0.20, 0.35, 0.50])
    parser.add_argument("--epsilons", type=float, nargs="+", default=[0.025, 0.05, 0.1])
    parser.add_argument("--wp5-seed", type=int, default=2026)
    parser.add_argument("--wp5-n-generic", type=int, default=4)
    args = parser.parse_args()

    wp3 = wp3_region_cloud(tuple(args.seeds), args.n_directions, tuple(args.radii))
    wp4 = wp4_weak_coupling_sweep(tuple(args.epsilons))
    wp5 = wp5_mechanism_rotation(args.wp5_seed, args.wp5_n_generic)

    args.wp3_out.parent.mkdir(parents=True, exist_ok=True)
    args.wp3_out.write_text(json.dumps(wp3, indent=2), encoding="utf-8")
    args.wp4_out.write_text(json.dumps(wp4, indent=2), encoding="utf-8")
    args.wp5_out.write_text(json.dumps(wp5, indent=2), encoding="utf-8")
    print(f"wrote {len(wp3)} WP3 candidates to {args.wp3_out}")
    print(f"wrote {len(wp4)} WP4 candidates to {args.wp4_out}")
    print(f"wrote {len(wp5)} WP5 candidates to {args.wp5_out}")


if __name__ == "__main__":
    main()
