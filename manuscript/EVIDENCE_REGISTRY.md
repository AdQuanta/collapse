# Evidence registry

Cutoff rule: only numerical runs whose provenance records show completion after
2026-07-01 are eligible as empirical evidence.  Pre-cutoff material may be used
only as background or as a prompt for a documented post-cutoff reproduction.

| ID | Claim supported | Status | Primary artifact | Qualification |
|---|---|---|---|---|
| T1 | A regular forward outcome pencil has `d` roots in `CP1`, counted with algebraic multiplicity. | Exact theorem | `main.tex`, Eqs. (2)-(3); `supplement.tex`, Sec. I | Singular pencils require homogeneous/Kronecker analysis. |
| T2 | The two same-unitary forward outcome-root multisets are exact Bloch antipodes. | Exact theorem | `main.tex`, Eq. (4); complementary-minor proof in `supplement.tex` | Applies to root coordinates and multiplicities; it does not supply detector records or a selection law. |
| T3 | Haar forward roots have the complex spherical-ensemble law and uniform one-point intensity. | Exact ensemble theorem | `main.tex`, Haar-null paragraph; `supplement.tex`, Sec. III | Not a finite-realization concentration result. |
| T4 | The compatible product-state set is generically not closed under addition. | Exact conditional statement | `supplement.tex`, Sec. II | The full pole-preimage subspace is linear; nonclosure belongs only to its product intersection. |
| N1 | In the matched ring, the four-time median polar score rises from 0.192 at N=11 to 0.807 at N=16. | Trusted post-cutoff numerical evidence | `reports/zeus_single_pixel_analysis_2026-07-16/jointly_gated_born_candidates.csv`; Fig. 4 | Deterministic saved times, not stochastic samples; no thermodynamic extrapolation. |
| N2 | The N=16, t=10^4 full-sphere root asymmetry is strongly dipolar. | Trusted post-cutoff numerical evidence | `work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/raw/N16/hz0_+0.1000/raw_t10000.npz`; Fig. 3 | 65,536 finite roots; 36x18 equal-area bins; no smoothing; count-weighted fixed-Born RMS 0.089. |
| N3 | The full-sphere map satisfies exact outcome-antipodal parity and has a dipole-dominated resolved odd sector. | Derived post-cutoff diagnostic | `figures/figure_manifest.json` | Even-power leakage is numerical zero; the ell=1 fraction is 0.952-0.985 across three fully occupied grids, but the higher odd residual is nonzero. |
| N4 | Exactly 24 matched-field rows pass the declared coverage and azimuthal gates among 1,208 completed spectra. | Trusted post-cutoff numerical audit | `reports/zeus_single_pixel_analysis_2026-07-16/jointly_gated_born_candidates.csv`; `audits/NUMERICAL_AUDIT.md` | This is a repository-wide statement for the four audited sweep tables, not for all possible Hamiltonians. |
| X1 | Algebraic root counts are operational Born probabilities. | Not established | `RESULTS_NEEDED.md` | Requires a preparation/selection measure tied to a common detector-ready ensemble. |
| X2 | The compatible roots produce stable, redundant, distinguishable records. | Not established | `RESULTS_NEEDED.md` | Requires detector-vector reconstruction and record-stability diagnostics. |
| X3 | The matched-ring trend converges to the Born law as N tends to infinity. | Not established | `RESULTS_NEEDED.md` | N=11-16 and four saved times are insufficient for controlled extrapolation. |
| X4 | Chaos, integrability, or many-body localization causes the observed geometry. | Rejected claim | `audits/NUMERICAL_AUDIT.md` | The eligible evidence does not isolate any of these mechanisms. |

## Excluded numerical artifacts

- `figures/haar_random_unitary/haar_N13_seed44.png`: pre-cutoff (March 2026).
  Haar isotropy is retained only as an analytical ensemble result.
- The March 2026 `tp_size_scan` figures: pre-cutoff and not empirical evidence
  in the Letter.
- Conceptual figures in the supplied `main.pdf`, including its explicitly
  hypothetical Fig. 4: used only to recover the research question.

