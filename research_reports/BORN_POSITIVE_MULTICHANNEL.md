# Positive multichannel ring leads and polar diagnostics

12 September 2026. **REPRODUCED_NUMERIC; exact phase remains open.** Two
saved interacting ring sequences with both gx and gy nonzero improve their
64-bin reflected-ratio RMSE with detector size. They provide concrete leads
for extending the positive weak-coupling search beyond X-only coupling.
The eight-moment error does not decrease along these sequences; this
counterevidence must accompany the improving histogram curves.

## Hamiltonians and source conventions

Use Pauli spins, hbar=1, central qubit first, and central Z readout. In the
user's positive-coefficient convention these saved cases have

\[
\mathbf h_D=(0,0,-h_z),\quad
\mathbf J_1=(-J_{pm}/2,-J_{pm}/2,-J),\quad
\mathbf g=(-g_x,-g_y,0),\quad \mathbf h_0=\mathbf J_2=0.
\]

The table gives the **native** positive parameters before these minus
signs. Both transverse collective couplings are divided by sqrt(N) exactly
once. The general search retains gz/N for rings and unscaled endpoint
couplings for open chains.

| Case | hz | J | Jpm | gx | gy |
|---|---:|---:|---:|---:|---:|
| config_079 | 0.13289388114917208 | 2.532451303152143 | 0.1699789863790785 | 0.0018956904663967606 | 0.012527361172537119 |
| config_047 | 3.3877092607196566 | 5.86769881537915 | 5.2279417611347485 | 0.21538120964223245 | 0.009162024068483241 |

The source weak-coupling ratios max(gx,gy)/min(J,Jpm,hz) are 0.094266 and
0.063577. These are microscopic comparisons, not bounds against every
many-body level spacing or size-uniform operator-norm perturbation bounds.

## Recomputed evidence

All snapshots have t=1e6 and full reflected coverage in 64 bins. Every
one of the 2^N saved roots is included. No smoothing, pseudocounts,
time averaging, or fitted extrapolation is used.

| Case | N | Ratio RMSE | Ratio Linf | Eight-moment maximum | S_born (100 bins) |
|---|---:|---:|---:|---:|---:|
| 079 | 13 | 0.09770265 | 0.23673280 | 0.05256411 | 0.56268801 |
| 079 | 14 | 0.06859326 | 0.22242326 | 0.04780445 | 0.74169538 |
| 079 | 15 | 0.05497888 | 0.11069376 | 0.05299406 | 0.74130249 |
| 047 | 13 | 0.12358457 | 0.32005248 | 0.03876521 | 0.36136126 |
| 047 | 14 | 0.12057875 | 0.29737934 | 0.03639733 | 0.42522442 |
| 047 | 15 | 0.08726364 | 0.26278981 | 0.04381150 | 0.62976159 |
| 047 | 16 | 0.06278925 | 0.11639603 | 0.04544132 | 0.71742803 |

The maximum is over all eight repository constraints
2 a_(2m+1)-a_(2m)-a_(2m+2), with a_k the raw-root cosine moment.
At the largest available sizes the second azimuthal harmonic magnitudes
are 0.403694 and 0.435970. These are not the unit harmonic of a single
great circle, and do not establish azimuthal uniformity or full-sphere
Born behavior. Polar agreement alone remains a root-statistical diagnostic.

The saved sources are
`work/zeus_sobol_coupling_scans_20260726_200003/jy_nonzero/N{N}/config_{id}/`.
The archived generator `scripts/sobol_coupling_scan.py` within that campaign
records the normalization. The audit reads it for provenance, never imports
active code from work. COMPLETE manifests verify raw NPZ, metadata, metrics,
and validation hashes; recomputed ratio RMSE agrees within 1e-12. This
postprocessing does not newly certify the old roots with homogeneous QZ.
No absent N values are interpolated and no new production run was submitted.

## Diagnostic figures and reproduction

The generated directory is `reports/born_positive_diagnostics_2026-09-12/`.
Each figure is available as vector PDF and PNG:

- `config_079`: P(theta) and reflected P, alongside R(theta) versus Born,
  for N=13,14,15.
- `config_047`: the same for N=13,14,15,16.
- `return_ring_N5`, `return_ring_N6`, `return_ring_N7`,
  `return_chain_N3`, `return_chain_N4`, `return_chain_N5`: all 48 full
  propagator snapshots from [the return study](BORN_RESONANT_RETURN.md),
  at four separated times and two transverse coupling choices.

Born is a reference for R, not a unique reference density P. Each row
therefore shows P and its reflected counterpart without imposing an
extra density ansatz. Empty ratio bins are visibly undefined; global
RMSE and Linf are null when reflected coverage is incomplete. The reduced
return cases illustrate this explicitly and are not thermodynamic controls.
All 55 profiles retain the eight moment residuals, coverage, and canonical
S_born in `metrics.json`; `provenance.json` records inputs and output hashes.

```bash
python scripts/plot_born_positive_diagnostics.py --output reports/born_positive_diagnostics_fresh
```

Use `--data-root` when the saved data reside outside the code checkout.
Configuration is `configs/born_positive_diagnostics_2026-09-12.json`.

## Constructive direction and limits

These are selected positive leads, not an unbiased success rate or a
verified open neighborhood. They still have zero central field, gz=0,
and a charge-conserving detector. The next construction should retain both
transverse channels, conditional longitudinal shifts, and the exact return
operator while admitting independent central fields, gz, and generic XYZ
detector perturbations. The [return representation](BORN_RESONANT_RETURN.md)
provides that framework without dividing by vanishing energy differences.
Fixed-time leading equivalence does not establish full-dynamics equivalence.

Multiple late times and independent microscopic neighborhoods remain
unchecked for these two high-N sequences. No exact thermodynamic law,
nonzero stability radius, or operational outcome probability follows from
these plots. The user's request to include P/R diagnostics is now part of
the ongoing study protocol wherever a candidate is numerically assessed.
