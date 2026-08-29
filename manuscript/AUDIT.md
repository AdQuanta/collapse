# Final scientific audit

## Mathematical audit

- The forward construction is homogeneous on `CP1`; the point at infinity and
  singular-pencil caveat are explicit.
- Complementary-minor duality is stated for a unitary block matrix and proved in
  the supplement.  Its consequence is exact antipodality with algebraic
  multiplicity, not statistical independence.
- The nonclosure statement is restricted to the product intersection of a
  linear preimage subspace with the Segre variety.
- Haar isotropy is an ensemble one-point result for every finite `d`; no
  unproved concentration or realization-level uniformity is asserted.

## Numerical audit

- The main empirical files are post-cutoff and their paths, timestamps, array
  sizes, parameters, and hashes are recorded in `NUMERICAL_PROVENANCE.md`.
- The N=16 full-sphere panel is regenerated directly from 65,536 saved roots.
  It uses an equal-area `(phi, cos(theta))` grid and no smoothing.
- The antipodal parity check gives floating-point-zero even harmonic power.
- Binning sensitivity is disclosed.  The 72x36 grid develops empty cells, so
  the Letter uses the occupied 36x18 grid and makes no continuum claim.
- Four saved times are deterministic observations; their spread is not labeled
  as a sampling uncertainty.

## Cutoff and provenance audit

- Pre-July 1, 2026 Haar and size-scan figures are excluded from empirical use.
- Figure manifests connect every numerical panel to a script and source data.
- No new production-scale simulation or Zeus submission was run.
- The repository working tree was already dirty; this package is isolated under
  `manuscript/` and does not overwrite prior results.

## Hostile-foundations audit

The decisive unresolved issue is selection.  Algebraic roots generally require
different detector microstates, so their multiplicities are not probabilities
for repeated preparation of a fixed ready state.  Nor does instantaneous output
factorization establish amplification, redundancy, temporal stability, or a
permanent record.  The manuscript makes these limitations part of its central
conclusion rather than hiding them in the supplement.

## Submission blockers

1. Supply author, affiliation, funding, and contribution information.
2. Deposit the hashed raw arrays and analysis tables in a persistent public or
   controlled-access archive and replace the publisher URL placeholder.
3. Obtain a physically motivated measure on compatible initial states or a
   dynamical preparation mechanism from a common detector-ready ensemble.
4. Reconstruct detector vectors and test record distinguishability and stability.
5. Add larger-N, additional-time, detuned/control, and full-sphere residual
   convergence studies before claiming an asymptotic Born law.
6. Validate one direct same-time homogeneous forward pencil numerically; the
   companion outcome coordinates then follow exactly by antipodal duality.
