# Numerical provenance

Cutoff policy: only project numerics generated or independently reproduced on or after **2026-07-01** may support the manuscript. Analytical derivations and published literature are not subject to this cutoff.

Repository base commit during manuscript assembly: `c0119b75909a73d9ee4b4b175afa44920d1338dd` (working tree dirty with pre-existing research changes; the manuscript does not treat the base hash as a clean snapshot). Figure-generation metadata is additionally captured in `figures/figure_manifest.json`.

## Main Fig. 3 — full-sphere matched-ring asymmetry

- **Classification:** POST-CUTOFF VERIFIED roots; POST-CUTOFF REPRODUCED figure post-processing.
- **Underlying generation:** Zeus run started `2026-07-14T20:07:01.595399Z`, finished `2026-07-15T14:15:06.704849Z`.
- **Post-processing generation:** UTC timestamp recorded in `prl_draft/figures/figure_manifest.json`.
- **Figure:** `prl_draft/figures/full_sphere_matched.pdf` (PNG inspection copy alongside it).
- **Manuscript location:** Main Letter Fig. 3; Supplemental Sec. VII and Table S2.
- **Script:** `prl_draft/scripts/build_figures.py`.
- **Raw data:** `work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/raw/N16/hz0_+0.1000/raw_t10000.npz`.
- **Raw SHA-256:** `e467b5efa6a5b8b7e3e7333a06555007b629a26bbeac2b21cd3da27d88313d59`.
- **Completion/metadata:** `work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/DONE.json`; matched-point `metadata.json` in the raw directory.
- **Hamiltonian:** periodic detector ring; `h_z0=h_z=0.1`, `J=1`, `J_pm=J_y=0`, collective `J_x=0.01`, per-edge `J_x/sqrt(N)=0.0025`; the manuscript displays the repository's overall minus-sign convention.
- **System size/time:** 16 detector spins, 17 total qubits, `t=10^4` in repository dimensionless units.
- **Root count:** 65,536 finite complex roots stored as `complex128`.
- **Outcome convention:** label 0 is the production `C v=lambda A v` cloud; label 1 is the exact Bloch antipode. By complementary-minor duality this pair gives the two forward outcome root locations for `U(-t)`. For the real matched Hamiltonian, same-time forward `theta` is unchanged and `phi` is reflected.
- **Binning:** equal-area `36 x 18` grid in `(phi, cos(theta))`; no smoothing; all 648 cells occupied; minimum labelled count 10.
- **Reported diagnostics:** count-weighted unit-Born residual `0.0890867`; correlation with `cos(theta)` `0.971498`; fitted dipole amplitude `1.06225`, axis numerically aligned with `+z`, post-fit residual `0.070243`; `ell=1` carries `0.981803` of odd power through `ell<=7`.
- **Sensitivity:** three fully occupied grids (`24x12`, `36x18`, `48x24`) give dipole fraction `0.952–0.985`; the residual grows at sparse finer resolution. No continuum extrapolation or confidence interval is claimed.
- **Seeds/realizations:** none; one deterministic Hamiltonian and one stored time. Root bins are not independent experimental trials.
- **Known numerical limitations:** production did not store homogeneous QZ pairs, root backward residuals, block condition estimates, nullities, or singular/infinite-root diagnostics.

The other trusted N16 matched arrays are:

| Time | Relative path suffix | SHA-256 |
|---:|---|---|
| `10^3` | `raw_t1000.npz` | `5786dd123f0cd3b33fb0dfdf2dd9cc3568c9b899af8f0f81c3f6a2b8b168c3d2` |
| `10^4` | `raw_t10000.npz` | `e467b5efa6a5b8b7e3e7333a06555007b629a26bbeac2b21cd3da27d88313d59` |
| `10^5` | `raw_t100000.npz` | `488028be94db4df817e6e396fa9c737f4dc3b1b159702008c48aebe50fa30bef` |
| `10^6` | `raw_t1000000.npz` | `1301f73272898ba6b2b707758e89817f0587cd75d46e73df896f6fa08eb88c45` |

## Main Fig. 4 — matched-field finite-size trend

- **Classification:** POST-CUTOFF VERIFIED derived rows; POST-CUTOFF REPRODUCED visualization.
- **Figure:** `prl_draft/figures/matched_field_scaling.pdf`.
- **Manuscript location:** Main Letter Fig. 4; Supplemental Table S1.
- **Script:** `prl_draft/scripts/build_figures.py`.
- **Input table:** `reports/zeus_single_pixel_analysis_2026-07-16/jointly_gated_born_candidates.csv`.
- **Input SHA-256:** `9c462fde32e234f33649fb644d09656075730551162c1204f74998a051f0ecce`.
- **Source analysis manifest:** `reports/zeus_single_pixel_analysis_2026-07-16/manifest.json`, created `2026-07-17T07:15:06.967592Z`.
- **Underlying raw data:** versioned `work/zeus_single_pixel_atlas_scaling_2026-07-14/{hz0,hz_resonance,jpm_coupling,jpm_hz}/...` directories referenced row-by-row in the CSV.
- **Hamiltonian:** same matched ring as Main Fig. 3 for every included row.
- **System sizes:** `N=11,...,16` detector spins; `2^N` roots per spectrum.
- **Times:** `10^3,10^4,10^5,10^6` for every size.
- **Samples:** 24 deterministic size-time rows; selected by polar coverage `>=0.5` and second azimuthal harmonic `|c2|<=0.25` from 1,208 completed spectra in four declared parameter studies.
- **Seeds/uncertainty:** none for the clean matched family; no stochastic error bars. Median and maximum summarize four saved times only.
- **Reported trend:** four-time median `S_B = 0.19155, 0.41110, 0.57147, 0.71519, 0.78839, 0.80747` for `N=11,...,16`; all matched rows have polar coverage one.
- **Analytical reference:** the dotted Haar `S_B=0` line is not empirical data; it follows from the exact uniform Haar one-point intensity.
- **Limitations:** no preregistered dense time window, controlled size extrapolation, QZ conditioning audit, or population inference.

## Supplemental Fig. S1 — diagnostic tradeoffs

- **Classification:** POST-CUTOFF VERIFIED descriptive analysis.
- **Figure source:** `reports/zeus_single_pixel_analysis_2026-07-16/regime_tradeoffs.png`; copied without scientific modification to `prl_draft/figures/regime_tradeoffs.png`.
- **Figure SHA-256:** `b5ef3820462eb178d4dcc9a42b52388357c993f0326bf200805ffa2403beece2`.
- **Manuscript location:** Supplemental Fig. S1.
- **Script:** `examples/interpret_zeus_single_pixel_scaling.py`.
- **Data:** `reports/zeus_single_pixel_analysis_2026-07-16/spectrum_metrics.csv` (SHA-256 `d69332e0bec1ce181b8fd2b80bbf5c14dcfcf2647c89096bb7ceb5f90958ce7d`).
- **Manifest:** `reports/zeus_single_pixel_analysis_2026-07-16/manifest.json` (SHA-256 `6e657f931ae8e3b1138c094087ff4579784b04c09a7f9db943300119fef7e32f`).
- **Generation date:** analysis manifest created `2026-07-17T07:15:06.967592Z`.
- **System sizes/samples:** 1,208 completed deterministic spectra; central-field study 168 (`N=11–16`), detector-field resonance 300 (`N=11–15`), fixed-exchange 240 (`N=11–15`), exchange-plus-field 500 (`N=11–15`).
- **Seeds:** model-specific; the matched clean rows have none. The figure makes no ensemble-frequency claim.
- **Purpose:** demonstrates that radial heavy tails, polar coverage, Born score, and azimuthal support are distinct gates. It is descriptive, not causal or held-out.

## Trusted older results reproduced after the cutoff

- The resonance-neighborhood study was independently rerun July 12–13, 2026 under `work/single_pixel_quspin_fresh_2026-07-12` with seed `20260712`. It confirms that exact resonances can broaden polar support without producing full Born structure. It is retained as a Supplemental/control result in the evidence audit but not plotted in the Letter.
- The matched-field finite-size figure and full-sphere map in this package are fresh post-processing reproductions from post-cutoff raw data; no production simulation was rerun during manuscript assembly.

## Rejected or excluded numerical evidence

- `figures/haar_random_unitary/haar_N13_seed44.png`: **PRE-CUTOFF / UNTRUSTED** for this paper. File and embedded context trace it to March 2026; raw roots and a post-cutoff completion record are absent. It is excluded from both PDFs. Haar claims are analytical only.
- `tp_size_scan_all_to_all.png`, `tp_size_scan_chain.png`, `tp_size_scan_ring.png`: **PRE-CUTOFF / UNTRUSTED** (March 2026); excluded.
- Root notebooks and legacy logs from January–June 2026: **PRE-CUTOFF / UNTRUSTED** unless a specific post-cutoff reproduction exists; excluded from quantitative claims.
- Copied outputs whose only evidence is a post-cutoff filesystem modification time: **DATE UNKNOWN / UNTRUSTED**; excluded.
- Mixed-symmetry level-spacing atlases: post-cutoff files exist, but they do not support a chaos/Poisson/GOE mechanism without symmetry resolution and ensemble controls; excluded from causal claims.
- Transverse-field Born-to-uniform crossover: no controlled publication-grade post-cutoff dataset was located; excluded.
- Broad statements that generic Ising or XY detectors become Born-like: the eligible evidence supports one matched-field ring, not a universal family claim; excluded.

## Provenance hierarchy used

1. Embedded `DONE.json` and run timestamps.
2. Analysis manifests and logs.
3. Raw-file hashes and row-level source paths.
4. Git history where applicable.
5. Filesystem metadata only as a last resort and never as sole proof after copying.
