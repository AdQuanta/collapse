# N=17 all-sector full-Hamiltonian spacings

This campaign computes 512 central eigenvalues and the corresponding unfolded
level-spacing distribution for every one of the 20 nonduplicated exact symmetry
sectors at all 20 values of `hz0`.

The PBS array map is:

- indices `0,1`: even total-excitation parity, `k=0`, reflection `+1,-1`;
- indices `2..9`: even parity, representative momenta `k=1..8`;
- indices `10,11`: odd total-excitation parity, `k=0`, reflection `+1,-1`;
- indices `12..19`: odd parity, representative momenta `k=1..8`.

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
SMOKE=1 ARRAY_RANGE=0-19 \
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

Each array task owns one sector and writes one `.npz` plus one metadata JSON
after every `hz0`. A sector-level `COMPLETE.json` is written only after all 20
cases finish and includes hashes for its 40 case artifacts and summary. Failed
or timed-out tasks can therefore be resubmitted with the same `RUN_ROOT` and
will resume from validated checkpoints.

## All-sector 3x20 figure

After copying a complete campaign locally, regenerate the diagnostic strip with:

```bash
python3.11 scripts/build_ring_hz0_full_spacing_3x20.py \
  --run-root work/<completed_activation_scan> \
  --all-sector-root work/<collected_all_sector_campaign> \
  --output-dir reports/<new_report_directory> \
  --output-name hz0_scan_global_diagnostics_full_spacing_all_20_sectors_3x20.png
```

The plotting command requires all 20 `COMPLETE.json` markers, validates every
manifest SHA-256, and requires all 400 NPZ checkpoints. Each sector is unfolded
independently. The third row shows the 20 sector histograms as thin curves and
their equal-level-weight pooled distribution as a dark curve; reflection-related
`k/-k` copies are not duplicated.

Measured locally, one 20-case sector took 16.5 minutes and about 2 GB peak
memory. The PBS request allows 1 hour, 4 CPUs, and 16 GB per sector task.
