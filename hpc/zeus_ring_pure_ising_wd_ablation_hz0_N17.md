# N=17 pure-Ising ablation across the WD-ring central-field grid

This production study is a controlled ablation of
`configs/ring_second_neighbor_wd_hz0_scan_N17.json`. It preserves
`N_D=17`, `J`, `hz`, the unscaled collective `Jx`, `t=1e6`, and all 20
absolute `hz0` values, while setting `Jpm=J2=Jpm2=0` exactly. The defining
self-contained configuration is
`configs/ring_pure_ising_wd_ablation_hz0_scan_N17.json`.

The final 3x20 figure has the same layout as the WD-ring atlas:

1. global `P(theta)` and its reflected distribution;
2. global `R(theta)` against `cos(theta/2)^2`;
3. full-Hamiltonian level spacings from all 20 nonduplicated exact sectors.

## Local and remote validation

Use Python 3.11. Before production, run:

```bash
python3.11 -m json.tool \
  configs/ring_pure_ising_wd_ablation_hz0_scan_N17.json >/dev/null
python3.11 scripts/run_three_ring_activation_resolved.py \
  --case-index 0 --n 17 \
  --config configs/ring_pure_ising_wd_ablation_hz0_scan_N17.json \
  --output-root work/_dry_run_pure_ising_activation_N17 --dry-run
python3.11 scripts/run_ring_hz0_all_sector_spacings.py \
  --array-index 0 \
  --config configs/ring_pure_ising_wd_ablation_hz0_scan_N17.json \
  --output-root work/_dry_run_pure_ising_spacings_N17 --dry-run
python3.11 -m pytest -q \
  tests/test_ring_hz0_activation_scan.py \
  tests/test_ring_hz0_all_sector_spacings.py \
  tests/test_ring_hz0_full_spacing_3x20.py
```

The 20 array indices of the spacing campaign are defined in
`zeus_ring_hz0_all_sector_spacings_N17.md`. Each index owns exactly one
translation/parity/reflection sector.

## Production submission

Use fresh, distinct output roots. The activation array has one `hz0` case per
task and checkpoints every momentum:

```bash
CONFIG=configs/ring_pure_ising_wd_ablation_hz0_scan_N17.json \
RUN_ROOT="$PWD/work/zeus_ring_pure_ising_wd_ablation_activation_N17_$(date +%Y%m%d_%H%M%S)" \
  hpc/submit_zeus_ring_born_like_hz0_scan_N17.sh
```

The all-sector spacing array has one exact sector per task and checkpoints
every `hz0` case:

```bash
CONFIG=configs/ring_pure_ising_wd_ablation_hz0_scan_N17.json \
RUN_ROOT="$PWD/work/zeus_ring_pure_ising_wd_ablation_all_sector_spacings_N17_$(date +%Y%m%d_%H%M%S)" \
  hpc/submit_zeus_ring_hz0_all_sector_spacings_N17.sh
```

The activation request is 20 array tasks at 16 CPUs, 256 GB, and at most 120
hours each. The spacing request is 20 array tasks at 4 CPUs, 16 GB, and at
most one hour each. The corresponding completed WD campaigns occupied about
232 MB and 9 MB and had median per-task compute times of about 7.3 hours and
52 minutes, respectively. These measurements are planning estimates, not
predictions of the ablated model's runtime.

## Completion and plotting

Do not collect partial output. Require:

- activation: 20 valid case `COMPLETE.json` markers and 340 NPZ plus 340 JSON
  momentum checkpoints, with every marker-listed artifact present and hashed;
- spacings: 20 valid sector `COMPLETE.json` markers and 400 NPZ checkpoints,
  with every completion-file hash verified;
- no traceback, memory, walltime, or failure marker in either campaign;
- numerical validation fields within their documented tolerances.

Copy both complete remote campaigns into new timestamped local `work/`
directories. Then render:

```bash
python3.11 scripts/build_ring_hz0_full_spacing_3x20.py \
  --config configs/ring_pure_ising_wd_ablation_hz0_scan_N17.json \
  --run-root work/<collected_activation_campaign> \
  --all-sector-root work/<collected_all_sector_spacing_campaign> \
  --output-dir reports/<new_pure_ising_report_directory> \
  --output-name hz0_scan_global_diagnostics_full_spacing_all_20_sectors_3x20.png
```

Each exact sector is unfolded independently before its spacing histogram is
drawn. Raw levels from independent sectors must never be merged before
spacing calculation. The pooled dark curve combines already-unfolded sector
spacings with equal level weight; omitted `k/-k` copies are not duplicated.
