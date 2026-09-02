# N=17 all-sector full-Hamiltonian spacings

This campaign computes 512 central eigenvalues and the corresponding unfolded
level-spacing distribution in a maximal, nonduplicated symmetry decomposition
at all 20 values of `hz0`. The exact decomposition changes at `hz0=0`, where
the central operator `X0` becomes conserved.

The PBS array map is:

- indices `0,1`: `X0=+1`, `hz0=0`, `k=0`, reflection `+1,-1`;
- indices `2..9`: `X0=+1`, `hz0=0`, representative momenta `k=1..8`;
- indices `10,11`: nonzero `hz0`, even total parity, `k=0`, reflection `+1,-1`;
- indices `12..19`: nonzero `hz0`, even parity, momenta `k=1..8`;
- indices `20,21`: nonzero `hz0`, odd total parity, `k=0`, reflection `+1,-1`;
- indices `22..29`: nonzero `hz0`, odd parity, momenta `k=1..8`.

At `hz0=0`, the `X0=-1` block is exactly isospectral to `X0=+1` under the
detector transformation `prod_i Zi`, so it is deliberately omitted. Total
excitation parity and `X0` anticommute and cannot be assigned simultaneously.

The omitted momenta `k=9..16` are exact reflection-related spectral copies of
`k=8..1`, respectively. Including them would duplicate levels rather than add
independent sectors.

## Validation before production

From the repository root on Zeus, activate the same Python 3.11 environment
used by the project and run:

```bash
python3.11 scripts/run_ring_hz0_all_sector_spacings.py --list-sectors
python3.11 scripts/run_ring_hz0_all_sector_spacings.py \
  --array-index 0 \
  --config configs/ring_second_neighbor_wd_hz0_all_sector_spacings_N17.json \
  --output-root work/_dry_run_ring_hz0_all_sector_spacings_N17 \
  --dry-run
```

For a one-case, 64-eigenvalue smoke array:

```bash
SMOKE=1 ARRAY_RANGE=0-29 \
  hpc/submit_zeus_ring_hz0_all_sector_spacings_N17.sh
```

Use a fresh output root for production:

```bash
hpc/submit_zeus_ring_hz0_all_sector_spacings_N17.sh
```

If the environment is not already active in PBS jobs, supply its path:

```bash
VIRTUAL_ENV_PATH=/absolute/path/to/python311/venv \
  hpc/submit_zeus_ring_hz0_all_sector_spacings_N17.sh
```

Each array task owns one case-family shard and writes one `.npz` plus one
metadata JSON after every compatible `hz0`. A shard-level `COMPLETE.json` is
written only after its one zero-field case or 19 nonzero-field cases finish.
It records the exact case IDs and hashes every artifact. Failed or timed-out
tasks can therefore resume from validated checkpoints.

## All-sector 3x20 figure

After copying a complete campaign locally, regenerate the diagnostic strip with:

```bash
python3.11 scripts/build_ring_hz0_full_spacing_3x20.py \
  --run-root work/<completed_activation_scan> \
  --all-sector-root work/<collected_all_sector_campaign> \
  --output-dir reports/<new_report_directory> \
  --output-name hz0_scan_global_diagnostics_full_spacing_all_sectors_3x20.png
```

The plotting command requires all 30 `COMPLETE.json` markers, validates every
manifest SHA-256, and requires all 390 NPZ checkpoints. Each sector is unfolded
independently. The `hz0=0` panel contains all ten nonduplicated `X0=+1`
spatial sectors; each nonzero panel contains all twenty parity-resolved spatial
sectors. Their equal-level-weight pooled distribution is the dark curve.

The eigensolver QR-orthonormalizes and Rayleigh--Ritz refines each returned
subspace before residual and orthogonality validation. The PBS request remains
1 hour, 4 CPUs, and 16 GB per shard task.
