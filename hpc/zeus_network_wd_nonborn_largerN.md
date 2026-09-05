# WD/non-Born network finite-size campaign

This campaign reruns four explicit `N=12`, `hz0=0` random-network
Hamiltonian configurations at detector sizes `N=13,14,15`. The source cases
have detector-only, symmetry-resolved level statistics that favor GOE over
Poisson and strongly non-Born dynamical diagnostics. The exact cases and
their source evidence are frozen in
`configs/zeus_network_wd_nonborn_largerN.json`.

Random graphs have no canonical continuation in size. Each target graph is
therefore regenerated using the source family parameters and the same saved
seed. The complete generated edge list is recorded in every case's
`metadata.json`; it is not claimed to be a subgraph or extension of `N=12`.

## Storage contract

The production runner uses `storage_mode=summary`. It computes the full
relative-root spectrum in memory but does not persist the full eigenvalues,
angles, phases, or Bloch-coordinate arrays. Each completed case stores:

- exact integer `theta` and reflected-`theta` histogram counts;
- bin edges, normalized densities, `R(theta)`, the Born reference and residual;
- wrapped-Gaussian/Cauchy fit curves and full fit metadata;
- a deterministic sample of at most 6000 Bloch points for figure reproduction;
- Hamiltonian parameters, generated graph specification and edge list,
  source identity, numerical/runtime provenance, validation, figures and hashes.

These artifacts reproduce the reported histogram-based conclusions and
figures. Recovering individual relative-root eigenvalues requires rerunning
the committed code and configuration.

Each case also recomputes the four largest nonredundant detector-only sectors
after resolving fixed Hamming weight, the complete graph-automorphism group,
and half-filling spin reversal where applicable. It saves exact spacing-bin
counts, normalized densities, mean adjacent-gap ratios, Poisson/GOE distances,
the full symmetry audit, and a 2x2 figure. Detector-sector eigenvalues and
individual unfolded spacings are not persisted.

## Validate and submit

```bash
python3.11 scripts/run_zeus_network_wd_nonborn_largerN.py \
  --array-index 0 \
  --config configs/zeus_network_wd_nonborn_largerN.json \
  --output-root /tmp/wd_nonborn_dry_run \
  --dry-run

bash hpc/submit_zeus_network_wd_nonborn_largerN.sh
```

The wrapper submits array indices `0-11`. Each task owns one unique
configuration/size pair and writes a dynamics `COMPLETE.json`, a
`detector_spacing_COMPLETE.json`, and one task-level `COMPLETE.json`. A fresh
run therefore requires exactly 12 of each of the three marker types.

Each task requests 16 CPUs, 256 GB and 120 hours. This matches the prior
random-network `N=13,14,15` continuation envelope. Do not treat disappearance
from `qstat` as completion: verify all 36 completion markers, all hashes, all
validation payloads, and absence of failure markers or log tracebacks.
