# Ranked Born follow-up campaigns

## 1. Top 20 from each of the five fixed source folders

The source folders and their order are frozen in
`configs/zeus_top20_last5_largerN.json`. Cases are ranked by decreasing stored
`S_born`, with the source case path as a deterministic tie-break. Only cases
with their required completion and metadata artifacts are eligible.

One of 20 array tasks owns five `(source, rank)` cases. Detector size is the
outer loop: it completes and checkpoints all five assigned cases at one N
before advancing to the next. Every case writes `results.npz`, diagnostics,
metadata, plots, validation, and `COMPLETE.json` immediately. Therefore a
timeout or failure at a larger N does not discard smaller-N results. Resubmit
with the same `RUN_ROOT` to resume.

```bash
bash hpc/submit_zeus_top20_last5_largerN.sh
```

The 256 GB, 16-core, 120-hour allocation follows established N=17 ring jobs.
N=17 remains expensive and completion within one allocation is not guaranteed.

## 2. Top 400 from the 880-case atlas with central-field variants

The fixed source is the downloaded `zeus_vab_atlas_jx_1em3` campaign. The top
400 validated cases are ranked by stored `S_born`. At N=14 each case requests

```text
hz0 = 0
hz0 = hz - 1e-3
hz0 = hz - 1e-4
hz0 = hz
hz0 = hz + 1e-4
hz0 = hz + 1e-3
```

Coincident values are simulated once and all aliases are recorded. The offset
list, source, top count, detector size, and shard size are configurable in
`configs/zeus_top400_hz0_variants_N14.json`. Four array tasks own one hundred
ranked source cases each; every `(case,hz0)` output is checkpointed independently.

```bash
bash hpc/submit_zeus_top400_hz0_variants_N14.sh
```

Neither wrapper overwrites an existing output root. No job is submitted by
creating or testing these scripts.
