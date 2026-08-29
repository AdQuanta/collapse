# Candidate numerical evidence table

This compact table is the manuscript-facing extract of `NUMERICAL_AUDIT.md`. It enforces the 2026-07-01 cutoff.

| Rank | Candidate | Status | Primary source | Suitable use | Blocking caveat |
|---:|---|---|---|---|---|
| 1 | Matched-field `N=11,...,16`, four-time `S_born` trend | POST-CUTOFF VERIFIED | `reports/zeus_single_pixel_analysis_2026-07-16/jointly_gated_born_candidates.csv`; raw `work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N*/raw/...` | Main finite-size figure | Deterministic times; no extrapolation or CI; root counts are not operational probabilities. |
| 2 | Matched `N=16` full-sphere production-root cloud | POST-CUTOFF VERIFIED | `work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/raw/N16/hz0_+0.1000/raw_t*.npz` | Main full-sphere figure after compact re-render | Exact unitarity makes the outcome root multisets antipodal. Stored `+t` production roots correspond to forward preimages for `U(-t)`; for the real matched Hamiltonian, same-time forward `theta` agrees and `phi` reflects. |
| 3 | 24/1,208 joint coverage/second-harmonic gate isolation | POST-CUTOFF VERIFIED | `interpretation_summary.json`, `spectrum_metrics.csv`, 24-row CSV | Main/Supplement selection statement | Descriptive grid result, not universal classifier. |
| 4 | Fresh resonant-field negative control | POST-CUTOFF REPRODUCED | `work/single_pixel_quspin_fresh_2026-07-12`; `reports/resonant_hz_study_2026-07-12.md` | Supplement | Polar spreading with non-Born ratio/azimuth; not positive Born evidence. |
| 5 | Anisotropic 880-case N14 atlas | POST-CUTOFF VERIFIED, PRELIMINARY | `work/zeus_single_pixel_anisotropic_20260718_130606`; July 21 report | Supplement parameter map | No configuration passes at all complete N11-N14 sizes. |
| 6 | Two-pixel topology comparison | POST-CUTOFF VERIFIED, PRELIMINARY | `work/conjecture_two_pixel_comparison_2026-07-16`; report/figures | Supplement negative control | Equal-size, four-time comparison only. |
| 7 | Degeneracy/heavy-tail iff falsification | POST-CUTOFF VERIFIED metrics, PRELIMINARY | July 24-26 campaigns/report | Supplement mechanism falsifier | Raw NPZ spectra missing locally. |
| 8 | Three-Sobol correlation study (1,072 configurations) | POST-CUTOFF VERIFIED, PRELIMINARY | `reports/three_sobol_born_relations_final_v2_2026-08-09` | Supplement/outlook | `S_born` is materially coverage-confounded; observational. |
| 9 | Four graph-family N12 campaigns (1,366 valid configs) | POST-CUTOFF VERIFIED data, inference absent | Aug 9-12 work/report manifests | Result required / negative examples only | One graph per config; no matched family analysis; high polar scores can have `|c2|~1`. |
| 10 | Stored Haar N13 seed44 image | PRE-CUTOFF / UNTRUSTED | `figures/haar_random_unitary/haar_N13_seed44.png` | Exclude | March 2026; raw roots and matching log absent. |

The recommended numerical main-text pair is ranks 1 and 2, with analytical Haar isotropy as the null model and no empirical Haar figure unless it is regenerated post-cutoff with raw roots, seeds, and residuals. Captions should present antipodality as an exact complementary-minor theorem, not as an independence defect, and should distinguish the production cloud for `U(t)` from the forward-preimage cloud for `U(-t)`.
