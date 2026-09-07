# N=17 continuation of the hz0=0 ring catalog

This campaign runs all 23 entries in the four-class ring catalog that currently
lack same-configuration N=17 dynamics. The frozen selection in
`configs/zeus_ring_catalog_missing_n17.json` contains 3 N=16 sources, 17 N=14
sources, and 3 N=13 sources. All have `hz0=0`; their exact `hz`, `J`, `Jpm`,
`J2`, `Jpm2`, unscaled collective `Jx`, evolution time, source metrics, and
source artifact hashes are retained.

The Hamiltonian convention is the established clean periodic ring convention:

```text
H_D = -hz sum_i Z_i - J sum_i Z_i Z_(i+1)
      - Jpm/4 sum_i (sigma_i^+ sigma_(i+1)^- + h.c.)
      - J2 sum_i Z_i Z_(i+2)
      - Jpm2/4 sum_i (sigma_i^+ sigma_(i+2)^- + h.c.).
```

The central coupling is collective and uses `Jx/sqrt(17)` exactly once. Each
task computes the full relative-root dynamics in memory but persists only the
64-bin angular histograms, Born-ratio arrays, fits, diagnostic figures, a
deterministic Bloch sample, metrics, validation, and provenance. Full
eigenvalues, angles, phases, and Bloch arrays are not saved.

Detector-only spacings are computed in 45 exact nonduplicated sectors: the five
largest fixed-`N_up` sectors at each nonredundant dihedral momentum. Reflection
parity is resolved at `k=0`; nonzero momentum represents the isospectral
`+/-k` pair, and `N_up>17/2` is omitted as an isospectral global-spin-flip copy.
Exact degeneracies are merged before cubic unfolding with a 10% edge trim.
Only per-sector and pooled histogram counts plus scalar statistics are saved.

## Validate and submit

```bash
python3.11 scripts/run_zeus_ring_catalog_missing_n17.py \
  --array-index 0 \
  --config configs/zeus_ring_catalog_missing_n17.json \
  --output-root /tmp/ring_catalog_n17_dry_run \
  --dry-run

bash hpc/submit_zeus_ring_catalog_missing_n17.sh
```

The wrapper submits array indices `0-22`, one configuration per task. Each case
writes a dynamics `COMPLETE.json`, a `ring_spacing_COMPLETE.json`, and a
task-level `COMPLETE.json`. A completed campaign therefore requires exactly 23
of each marker type, no `FAILURE.json`, no relevant log errors, and successful
verification of every marker-listed SHA-256 hash and dynamics validation.

Each task requests 16 CPUs, 256 GB, and 120 hours, matching the established
N=17 ring continuation envelope. A scheduler job ID proves submission only;
use the artifact completion gate above before analysis or collection.

## Collection audit and report

Run the stdlib-only audit remotely through SSH stdin before collection, then
again on the fresh local collection with the same frozen config:

```bash
python3.11 scripts/audit_completed_ring_campaign.py \
  --kind catalog --config configs/zeus_ring_catalog_missing_n17.json \
  --root work/<completed_campaign> > catalog_audit.json
```

Check scheduler state separately. Require the remote and local audits' full
`files_sha256` maps to agree; `.mplconfig` caches are excluded. The audit checks
task identities, exact completion counts, every marker-listed checksum, source
validation, Hamiltonian parameters, and logs without changing the campaign.

After collection, render all 23 cases without any new diagonalization:

```bash
python3.11 scripts/build_collected_ring_catalog_report.py \
  --run-root work/<fresh_local_collection> \
  --output reports/<new_report_directory>
```

Each case receives PNG and vector PDF diagnostics plus a labeled 5-by-9 sheet
of its 45 detector sectors. The summary compares source and current Born
scores; source selection categories do not describe the new measurements.
Each spacing density is normalized by its full spacing count, retaining the
omitted probability mass above the plotted limit `s=4`. This differs from
older report plots that renormalized their visible histogram range. Sector
levels are never mixed before unfolding. Histogram-only storage does not
permit a new unfolding-order, trimming, or degeneracy-tolerance study.
