# Hamiltonian-classification Zeus campaign

## Scope

The versioned design is
`configs/hamiltonian_classification_zeus_campaign.json`. It expands to 149
independent points:

- 12 matched-field QZ reproductions (`N=10,12,14`, four times);
- 18 transverse-strength points;
- 27 matched-detuning points;
- 18 second-transverse-channel points;
- 18 detector-transverse-field points;
- 40 matched-field random-network controls (four graph families, `N=8,10`,
  five independently seeded graph realizations) using the dense backend;
- two identically parameterized dense ring controls at `N=8,10`;
- eight dense physical-architecture controls at `N=8,10`: a noninteracting
  detector with star-like collective central coupling, an interacting Ising
  ring, a collective-coupling XY ring, and a locally edge-coupled XY chain;
- six Haar-unitary nulls (`N=8,10`, three seeds) with homogeneous QZ.

Every central source coupling is divided by `sqrt(N)` before being assigned to
each detector edge. Detuning is explicitly
`delta_source=(hz0-hz)/Jx_source` with `Jx_source=0.01`.
The sole exception is the explicitly local XY-chain control, where the central
qubit couples to only the first detector site and `central_scale=none`; this
keeps the norm of its one local edge at the recorded source value.

The four added architecture controls use

```text
noninteracting star: H_D=-hz sum_i Z_i,
                     H_QD=-Jx/sqrt(N) X_0 sum_i X_i
Ising ring:          H_D=-hz sum_i Z_i-J sum_<ij>ring Z_i Z_j,
                     H_QD=-Jx/sqrt(N) X_0 sum_i X_i
XY ring:             H_D=-hz sum_i Z_i-(Jpm/2) sum_<ij>ring (X_i X_j+Y_i Y_j),
                     H_QD=-Jx/sqrt(N) X_0 sum_i X_i
XY chain edge:       H_D=-hz sum_i Z_i-(Jpm/2) sum_<ij>chain (X_i X_j+Y_i Y_j),
                     H_QD=-Jx X_0 X_1.
```

All also contain `H_Q=-hz0 Z_0`; their exact numeric parameters and seeds are
serialized per manifest row.

## Local validation and resource estimate

Focused tests validate dense versus QuSpin translation-sector roots. A local
QuSpin/QZ benchmark gave:

| detector N | total dimension | roots | sectors | diagonalization | QZ | total |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 512 | 256 | 8 | 0.47 s | 0.06 s | 0.53 s |
| 10 | 2,048 | 1,024 | 10 | 2.95 s | 5.65 s | 8.61 s |

These are Windows/Python-3.12 smoke timings, not Zeus performance estimates.
No N=12/N=14 local production run was launched. For N=14, a typical
translation sector is of order `2^(N+1)/N ~= 2,340`; a single dense complex
eigenvector array at that scale is about 88 MB. Multiple sector eigenbases and
QZ workspaces make the exact peak implementation-dependent, but the recent
project convention of 16 CPUs, 256 GB, and 120 h is conservative. The first
submitted campaign should be monitored before increasing N or adding times.
The network and Haar controls stop at N=10 because they do not have translation
symmetry; their graph parameters and realization seeds are serialized in each
point configuration.

An end-to-end dense `N=8` Erdos-Renyi smoke point completed in 7.81 s
(2.05 s diagonalization, 5.74 s QZ). It returned 256/256 determined roots,
maximum right/left backward residuals `2.00e-15`/`1.78e-15`, and a regular
representative pencil. Its `0.28125` angular coverage is insufficient for
harmonic claims, as expected for a small smoke point. The collector correctly
accepted this categorical-connectivity row; this smoke result predates the
later ring-control and Haar additions to the manifest.

An `N=8` Haar-unitary smoke point also completed locally in 6.46 s. It was
fully covered, QZ-valid, and regular at the audited root, with maximum
right/left backward residuals `3.26e-15`/`2.99e-15` and isometry residual
`6.76e-17`. Its high leakage (`0.896`) and small dipole (`eta=0.0267`) verify
the intended null behavior for this one seed. Three seeds at each of `N=8,10`
remain in the production manifest.

## Submission

From the repository root on Zeus:

```bash
export RUN_ROOT="$PWD/work/zeus_hamiltonian_classification_$(date +%Y%m%d_%H%M%S)"
bash hpc/submit_zeus_hamiltonian_classification.sh
```

The wrapper generates `scan_manifest.csv`, then submits one 20-element PBS
array to `zeus_new_q`. Each task owns a deterministic strided subset and skips
valid `COMPLETE.json` checkpoints on resubmission.

Inspect with:

```bash
qstat -u "$USER"
tail -f "$RUN_ROOT"/logs/task_*.log
```

## Collection and missing points

After the array finishes:

```bash
python3.11 scripts/collect_hamiltonian_classification_results.py \
  --manifest "$RUN_ROOT/scan_manifest.csv" \
  --output-root "$RUN_ROOT"
```

This writes `aggregated/classification_results.csv`,
`missing_manifest.csv`, `corrupt_manifest.csv`, and a collection summary.
Resubmitting the same array with the same `RUN_ROOT` is safe and recomputes
only missing/incomplete points.

Only when the summary reports all 149 points complete and zero missing/corrupt
rows, build Figures A--D and their source tables:

```bash
python3.11 scripts/plot_zeus_hamiltonian_classification.py \
  --run-root "$RUN_ROOT"

python3.11 scripts/analyze_zeus_spectral_relations.py \
  --run-root "$RUN_ROOT"
```

The plotter enforces this completeness gate and reads harmonic spectra from
each selected case rather than reconstructing them from images. The spectral
postprocessor resolves detector levels by Hamming weight, the complete graph
automorphism group, and half-filling spin reversal before computing adjacent
gap ratios. It reports spacing statistics as undefined for the exactly
noninteracting star detector, whose fixed-weight blocks are degenerate. It also
reports five-seed graph-realization uncertainty separately from deterministic
size and architecture variation.

No Zeus job was submitted while preparing this workflow.
