# Born-profile data for TikZ / PGFPlots

Start with `shortlist.csv` (best stored score in each of six families), or
`catalog.csv` (all exported cases). Each ID names a directory. `reviewed_cases.csv`
also lists scored cases below the selection threshold. `manifest.json` records
the frozen campaign scope, excluded incomplete records, source and output SHA-256,
parameters, validation evidence, and export runtime. This is a review of local
collections, not an exhaustive audit of Zeus or a new simulation campaign.

## Files in each case directory

- `profile.dat`: original bin centers, left/right edges, P, reflected P, R,
  Born reference, residual, and occupancy. `theta_rad`, `theta_over_pi`, and
  `theta_deg` are available. P is a probability density **per radian** regardless
  of the displayed x-coordinate; R is dimensionless, not a density.
- `histogram_steps.dat`: two rows per original bin, with exact left and right
  edges. Plot with ordinary lines to preserve the histogram steps. No interpolation,
  fitting, smoothing, or rebinning was applied. Do not use `smooth` in PGFPlots.
- `nodes.dat`: `id x y is_central`. Detector IDs are zero-based 0..N-1; the
  central qubit has ID N. Coordinates give a deterministic unit-circle layout
  centered on the central qubit. They are drawing coordinates, not physical positions.
- `edges.dat`: `source target kind Jzz Jpm Jx_effective Jy_effective`.
  Each undirected edge occurs once per interaction kind. Kind 1 is the saved
  detector graph (nearest-neighbor bonds for a ring), kind 2 is the distinct
  periodic distance-two ring bond set, and kind 0 is central-to-detector coupling.
  The random-network edge list is taken from the actual saved realization at
  its simulated N; it is not regenerated from a seed. The ring shell is
  `{i,(i+2) mod N}`, with undirected duplicates removed. Omit kind 0 for a
  detector-only drawing. `Jzz`/`Jpm` are the model's J/Jpm or J2/Jpm2 parameters;
  they are not signed Hamiltonian matrix elements. The effective central
  couplings already include the saved 1/sqrt(N) factor. Do not scale them again.
- `provenance.json`: source path/hash, full portable metadata, effective hz0,
  detector graph and seed, Hamiltonian parameters, time, validation, and table hashes.

## Meaning and selection

The ensemble is the stored, equally weighted relative-evolution root ensemble,
with theta = 2 arctan(|lambda|) on [0,pi]. P is the normalized theta histogram;
P_reflected is the histogram of pi-theta from the same samples.
R = P/(P+P_reflected) on occupied bins. The numerical reference is
Born = cos(theta/2)^2. Empty bins are retained as `nan` in R with occupied=0;
use `unbounded coords=jump`. No error bars are inferred from these data.

The stored S_born uses **100 bins**, while these original plotting tables use
**64 bins**. Its definition is 1 - 2 sum_i |R_i-cos(theta_i/2)^2|
sin(theta_i) Delta_theta; the score convention assigns R_i=1/2 to empty bins.
The exported RMSE is computed on occupied bins of the 64-bin plotting grid.
Thus recomputing S_born from profile.dat will generally give a different number.
The global ensemble is exported for activation-resolved runs; activation
components are not selected or averaged to produce the exported curve.

High-score selection is stored S_born >= 0.8, a descriptive cutoff, not a
statistical significance threshold. When an entire (family,N) group falls below
0.8, up to three best cases with S_born >= 0.7 are included as explicitly labeled
lower-N references. Exact ties are ordered by source path. Replicated runs and
different campaigns are retained with separate provenance; identical exported
profiles are listed in the manifest and are not independent evidence.
The original low-score/high-score cohort labels are not used to select reruns.
Network size changes can change graph realizations. These selected examples do
not establish typicality, size/time/bin convergence, or robustness across seeds.

Every exported case has all COMPLETE.json-listed artifact checksums verified.
Source validation records are retained; no new eigensolver validation is claimed.
The export additionally checks P normalization, R's defining identity, the Born
reference, stored RMSE, graph integrity, and exact float64 table round trips.

## Compile the example

From this directory, run `pdflatex -interaction=nonstopmode -halt-on-error example.tex`.
Change `\casepath` to any ID in catalog.csv. The first page plots P and R;
the second draws the detector and central-qubit graph. The complete package is
portable: copy this directory alongside your paper and adjust relative paths.

To regenerate from the repository and its local source collections:

```sh
MPLCONFIGDIR=work/_mplconfig ~/.venvs/collapse-py311/bin/python scripts/export_born_profiles.py \
  --config configs/born_profile_export_2026-09-06.json --output reports/NEW_DIRECTORY
```

The output directory must be new. Prior data are never overwritten.
