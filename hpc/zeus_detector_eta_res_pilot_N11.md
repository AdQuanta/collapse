# Zeus handoff: detector-basis `eta_res` N=11 pilot

Purpose: quantify whether candidate Born-like rows have detector-basis resonant interaction weight, not merely full-Hamiltonian or detector spectral degeneracy.

The PBS script runs:

\[
\eta_{\mathrm{res}}(\delta)
=
\frac{\sum_{\alpha}\sum_{\lvert E_a-E_b\rvert\le\delta}
\lvert (B_\alpha)_{ab}\rvert^2}
{\sum_{\alpha}\sum_{a,b}\lvert (B_\alpha)_{ab}\rvert^2}
\]

and a finite-time windowed version with

\[
\delta_t=\max(\epsilon_E, c/t).
\]

The current implementation is dense in the detector Hilbert space. Keep this pilot at detector `N=11`; larger detector sizes require a sector/sampled estimator.

The CSV now also contains `eta_res_traceless`: the interaction Frobenius weight
in the traceless part of exactly degenerate detector blocks. It vanishes when
the resonant interaction is scalar within every exactly degenerate block and
therefore cannot split that block at first order. `resonant_effective_elements`
is an inverse-participation count for the resonant detector-basis matrix
elements; it distinguishes one or two isolated resonances from a broad kernel.

## Submit

Paste from the repository root on Zeus:

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_detector_eta_res_pilot_N11_${RUN_TAG}"
LOG_ROOT="logs/zeus_detector_eta_res_pilot_N11_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-2 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",MIN_N=11,MAX_N=11,TOP_ROWS=24,PHI_MIN=0.7,ENERGY_TOL=1e-9,WINDOW_FACTOR=1.0,REQUIRE_NONZERO_COUPLING=1 \
  hpc/zeus_detector_eta_res_pilot_N11.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Outputs

- Task logs:
  - `logs/zeus_detector_eta_res_pilot_N11_<tag>/task_1_eta_res.log`
  - `logs/zeus_detector_eta_res_pilot_N11_<tag>/task_2_eta_res.log`
- Result CSVs:
  - `figures/zeus_detector_eta_res_pilot_N11_<tag>/j_jpm_jy0_N11_eta_res.csv`
  - `figures/zeus_detector_eta_res_pilot_N11_<tag>/j0_jpm1_jx_jy_N11_eta_res.csv`

## Notes

- Task `1` reads the imported J-Jpm/Jy=0 N=11 matched and zero summaries.
- Task `2` reads the imported fixed `J=0,Jpm=1` Jx-Jy N=11 matched and zero summaries.
- `PHI_MIN=0.7` focuses the dense diagnostic on rows with reasonable Bloch-sphere azimuth coverage.
- `TOP_ROWS=24` keeps the pilot bounded while still sampling several successful and near-successful candidates.
