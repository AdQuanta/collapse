# Zeus runbook: Vab-atlas configurations at hz0=0.1

This campaign repeats the exact 880 Hamiltonian parameter triples indexed by
`reports/vab_coupling_group_atlas_2026-07-28/data/case_index.csv`, changing
only the central-qubit field from `hz0=0` to `hz0=0.1`. It keeps:

- `N=14`, `t=1e6`, collective `Jx=0.01`, and `Jy=0`;
- ring detector connectivity and coupling of the central qubit to all detector
  spins;
- the original 11 `hz`, 8 `J`, and 10 `Jpm` values;
- the established raw spectra, metadata, metrics, and blue/red diagnostic
  output schema.

The Hamiltonian implemented by the existing backend is

```text
H = -hz0 Z0 - hz sum_i Zi - J sum_i Zi Z(i+1)
    - Jpm sum_i (sigma_i^+ sigma_(i+1)^- + h.c.)
    - (0.01/sqrt(N)) sum_i X0 Xi,
```

where `i=1,...,N` labels the periodic detector ring and qubit `0` is central.
The displayed exchange term uses the repository's physical `Jpm` convention;
the QuSpin coefficients are normalized internally to reproduce it. All omitted
couplings and transverse fields are zero. Each configuration records these
conventions in its metadata.

## Files to upload

Upload these new files together with the existing repository code:

```text
configs/zeus_vab_atlas_hz0_0p1_N14.json
scripts/run_zeus_vab_atlas_hz0_0p1_N14.py
hpc/zeus_vab_atlas_hz0_0p1_N14_array.pbs
hpc/submit_zeus_vab_atlas_hz0_0p1_N14.sh
hpc/zeus_vab_atlas_hz0_0p1_N14.md
```

The runner uses the existing `core/anisotropic_sweep.py` implementation.

## Validate before submission

From the repository root on Zeus:

```bash
python3.11 scripts/run_zeus_vab_atlas_hz0_0p1_N14.py --help
python3.11 scripts/run_zeus_vab_atlas_hz0_0p1_N14.py \
  --batch-index 0 --output-root work/vab_hz0_dry_run --dry-run
```

The dry run must report ordinals 1--100, exactly 100 unique configurations,
`N=14`, and `hz0=0.1`. Batch 8 reports ordinals 801--880 and 80 cases.

## Submit

```bash
bash hpc/submit_zeus_vab_atlas_hz0_0p1_N14.sh
```

The PBS array has nine jobs. Jobs 0--7 each simulate 100 configurations; the
last job simulates the unavoidable remainder of 80 because the exact atlas has
880 configurations. Each job runs two independent fixed-(`hz`,`J`) row
workers; each row contains all ten `Jpm` values. Numerical libraries receive
four threads per worker, matching the 8-CPU request. Each completed
configuration is saved and plotted immediately.

Rerun with the same `RUN_ROOT` to resume validated rows. After all nine batch
markers exist, one job acquires a project-local finalization lock and creates
the N=14 Born-score heatmaps, metrics CSV, aggregate manifest, and
`CAMPAIGN_COMPLETE.json`.

