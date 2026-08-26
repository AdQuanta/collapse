# Numerical evidence audit for the PRL draft

Audit date: 2026-08-14 (Asia/Jerusalem)

Cutoff enforced: only project-generated numerical evidence generated or independently reproduced on or after 2026-07-01 is eligible. Embedded UTC/local run times and completion records take priority over copied-file dates. This audit did not launch a production simulation or overwrite any output.

## Bottom line

The strongest publication-eligible positive result is a clean, deterministic matched-field ring sequence at detector sizes `N=11,...,16` and four stored times. Its polar root-count statistic becomes substantially more Born-like with size while polar-bin coverage remains one and the measured second azimuthal harmonic is small. It is numerical evidence for a special **relative-evolution root geometry**, not yet for operational probabilities or the detector-record/selection mechanism.

The best trusted full-sphere source is the `N=16` matched-field raw NPZ family. A compact full-sphere figure can be regenerated cheaply from those roots. The current red cloud is the deterministic antipode of the blue production roots and must be labelled as such. This antipodality is not a deficiency: the complementary-minor identity implies that the two forward outcome root multisets of any unitary are also exact Bloch antipodes, with algebraic multiplicity. The actual bridge issue is time direction: production computes the `(C,A)` fixed-input-pole output pencil for `U(t)`, which is a forward-preimage construction for `U(t)^dagger=U(-t)`, rather than directly computing a forward pencil for the same `U(t)`.

The repository's only stored production-scale Haar figure is pre-cutoff and is ineligible. Haar isotropy should be used as an analytical result unless a new, explicitly versioned modest-dimension realization is generated. Such a realization is computationally cheap but would be illustrative only, not a concentration study.

## Audit scope and provenance rules

Inspected sources included:

- the 36-page `C:/Users/matan/Downloads/main.pdf` research map;
- repository code for relative-evolution roots, Hamiltonians, plotting, Sobol campaigns, detector-spectrum analysis, and graph campaigns;
- versioned configs and HPC campaign notes;
- post-cutoff `DONE.json`, `COMPLETE.json`, metadata, validation, logs, raw NPZ files, CSV summaries, figures, and reports;
- pre-cutoff notebooks, logs, and figures as negative-provenance controls;
- the repository Git history (one commit, `c0119b7`, dated 2026-08-01) and the dirty worktree.

The single Git commit is too coarse to date most generated results. Embedded completion records and logs are the primary evidence. Git commit `c0119b7` may be recorded as the imported repository snapshot, but it must not be misreported as the code revision that originally generated every campaign.

Classification used below:

- **POST-CUTOFF VERIFIED**: embedded post-cutoff completion/metadata and traceable current code/configuration exist.
- **POST-CUTOFF REPRODUCED**: a formerly older result was explicitly rerun after the cutoff.
- **PRE-CUTOFF / UNTRUSTED**: embedded evidence predates the cutoff.
- **DATE UNKNOWN / UNTRUSTED**: no reliable embedded provenance.

`POST-CUTOFF VERIFIED` does not imply sufficient finite-size control, uncertainty quantification, or foundational interpretation. Those are assessed separately.

## Candidate evidence table

| ID | Numerical claim / object | Classification | Exact source and provenance | Samples, parameters, seeds, uncertainties | Figure suitability |
|---|---|---|---|---|---|
| M1 | Matched-field ring shows a monotone rise in four-time median `S_born` from `0.19155` at `N=11` to `0.80747` at `N=16`. | **POST-CUTOFF VERIFIED; NUMERICAL RESULT** | `reports/zeus_single_pixel_analysis_2026-07-16/jointly_gated_born_candidates.csv`; raw files under `work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N*/raw/N*/hz0_+0.1000/raw_t*.npz`; per-size `DONE.json`; campaign finish range 2026-07-14 to 2026-07-15 UTC. | 24 spectra: six detector sizes, four deterministic times `10^3,10^4,10^5,10^6`; `hz0=hz=0.1`, `J=1`, `Jpm=0`, collective `Jx=0.01`, edge `Jx/sqrt(N)`; no stochastic seed is active; no CI/error bar. Time-to-time spread is not an ensemble uncertainty. | **Main-text best candidate**, as finite-size/time-sample evidence only. No extrapolation. |
| M2 | All 24 spectra satisfying coverage `>=0.50` and `|c2|<=0.25` among 1,208 completed spectra are the exact matched-field rows. | **POST-CUTOFF VERIFIED; NUMERICAL RESULT with selection caveat** | Same CSV plus `reports/zeus_single_pixel_analysis_2026-07-16/interpretation_summary.json` and `spectrum_metrics.csv`. | 1,208 completed spectra across four studies: central-field 168, detector-field 300, fixed-`Jpm` 240, `J=0,Jpm=1` field 500. Gate selection is descriptive; no multiple-testing or out-of-sample validation. | Main/Supplement sentence or compact table. Avoid calling it a universal Hamiltonian criterion. |
| M3 | Trusted full-sphere matched-field root cloud at `N=16`, including nontrivial azimuthal coverage. | **POST-CUTOFF VERIFIED; NUMERICAL RESULT** | Four N16 NPZs listed in the dedicated section below; existing atlases `work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/figures/N16_hz0_diagnostic_atlas_t1e*.png`; `DONE.json` finished `2026-07-15T14:15:06.704849+00:00`. | 65,536 finite production roots per time; deterministic; `theta=2 atan|lambda|`; no spherical KDE/harmonics beyond `|<exp(2i phi)>|`; no uncertainty. The plotted red branch is exactly `-v(lambda)`, as expected for the companion production branch. | **Main-text full-(theta,phi) source**, but regenerate a compact equal-area/Bloch panel, label antipodality, and state that the stored `+t` production roots correspond to forward preimages for `U(-t)`. For the real matched Hamiltonian, same-time forward polar coordinates agree while `phi` is reflected. |
| M4 | At `N=16`, the matched rows retain full polar coverage and median second azimuthal harmonic `0.01672`; median/max `S_born=0.80747/0.83950`. | **POST-CUTOFF VERIFIED; NUMERICAL RESULT** | Same 24-row CSV; values independently regrouped in this audit. | Four deterministic times; no CI. The second harmonic alone does not establish full azimuthal uniformity or absence of higher harmonics. | Main caption/supporting panel, with the harmonic limitation stated. |
| H1 | Haar root intensity is isotropic. | **ESTABLISHED analytical result, not project numerical evidence** | Analytical spherical-ensemble reduction in the current manuscript materials and theory code context. | No numerical sample required for the one-point ensemble statement. | Main theory/null-model statement. Use no empirical figure unless regenerated post-cutoff. |
| H2 | Stored `N=13`, seed 44 Haar sphere looks isotropic. | **PRE-CUTOFF / UNTRUSTED** | `figures/haar_random_unitary/haar_N13_seed44.png`, last modified 2026-03-12; `examples/logs/haar_random_20260312_215508.log` documents only an `N=5` run that day, not the N13 file. | One realization; seed 44; raw unitary/roots and N13 log absent; no discrepancy statistic or uncertainty. | **Forbidden** in paper and Supplement under cutoff. Remove the copied version from any draft package. |
| A1 | Complete anisotropic grids develop a Born-like polar subset: at `N=14`, 90/880 cases pass `S_born>=0.75`, occupied-bin RMSE `<=0.15`, coverage `>=0.50`; none passes at all `N=11,...,14`. | **POST-CUTOFF VERIFIED; PRELIMINARY NUMERICAL RESULT** | `work/zeus_single_pixel_anisotropic_20260718_130606`; `reports/anisotropic_parameter_study_2026-07-21/anisotropic_spectrum_born_report_2026-07-21.tex`; `analysis_manifest.json`. | Four complete grids of 880 cases at `N=11,...,14`, `t=10^6`; config seed 44 (clean-grid seed is not a statistical ensemble); N15-17 are biased partial subsets; no N18; no finite-size CI. | Supplementary parameter-map/control only. It is weaker than M1 for a Letter because favorable configurations do not persist across all four complete sizes. |
| A2 | All 90 `N=14` Born-gated anisotropic cases have resolved shallow periodic fits with `alpha` in `[0.519,1.270]`, but most low-alpha cases are not Born-like. | **POST-CUTOFF VERIFIED; PRELIMINARY NUMERICAL RESULT** | Same anisotropic report and generated metrics. | One time and one largest complete size for the stated interval; thresholds are analysis choices; no held-out mechanism test. | Supplement/outlook; useful as evidence that broadness is not sufficient. Not central PRL evidence. |
| T1 | Splitting one detector into two pixels lowers family-median polar coverage and `S_born` in the four compared families and destroys the matched-field positive example at the tested equal total size. | **POST-CUTOFF VERIFIED; PRELIMINARY NUMERICAL RESULT** | `work/conjecture_two_pixel_comparison_2026-07-16`; `reports/conjecture_two_pixel_comparison_2026-07-16.tex`; figures under `figures/conjecture_two_pixel_comparison_2026-07-16`. | Four parameter families, four deterministic times; equal-size comparison; no size scaling, time averaging, random ensemble, or CI. | Supplement negative control. Do not elevate to a universal locality/topology claim. |
| D1 | Exact degenerate coupling activation is neither sufficient nor necessary for a broad relative-evolution distribution. | **POST-CUTOFF VERIFIED metrics; PRELIMINARY due absent raw spectra** | `work/zeus_degeneracy_heavy_tail_iff_N13_N18`; `work/zeus_relative_scale_regimes_20260724_144102`; `reports/degeneracy_heavy_tail_zeus_2026-07-26/README.md`, CSVs, JSON. | Primary complete sizes `N=13,...,16`, `t=10^6`, seed 44; 44 targeted and 120 regime rows. Raw NPZ spectra were not transferred for 48 targeted and 125 regime paths; two pipelines agree on eight duplicates. No population p-value is appropriate. | Strong logical counterevidence for a proposed mechanism, but only Supplement/Discussion unless raw spectra are recovered. |
| S1 | In three Sobol campaigns, raw `S_born` correlates strongly with coverage; several spectral/coupling correlations reverse or weaken for occupied-bin accuracy. | **POST-CUTOFF VERIFIED; PRELIMINARY NUMERICAL RESULT** | `reports/three_sobol_born_relations_final_v2_2026-08-09/report.md`, `provenance.json`, CSVs; underlying post-cutoff Sobol campaigns and detector-spectrum products. | Dynamics `N=14`; detector-spectrum `N_D=10`; completed configurations 343+329+400=1,072; Sobol seed 20260726, model seed 44; 500 bootstrap resamples with RNG seed 20260809; deterministic nested 10-fold outer/5-fold inner CV. | Supplement methodological warning or classification outlook. Do not use raw correlations as a Born mechanism; the score is materially coverage-confounded. |
| S2 | For `hz0=0`, effective interaction relative to mean spacing has similar within-campaign Spearman correlations `rho=0.333` and `0.337`, but coverage-controlled effects are only `0.083` and `0.096`. | **POST-CUTOFF VERIFIED; PRELIMINARY NUMERICAL RESULT** | Same three-Sobol report/CSVs. | `n=343` second-neighbor and `n=329` nearest-neighbor; quoted bootstrap CIs exist for raw correlations, not for every partial effect; observational, not causal. | Supplement/outlook at most. Too small/confounded for abstract or main conclusion. |
| G1 | Four non-circular graph families have many validated `N=12` Sobol configurations, but no controlled graph-family Born conclusion has yet been extracted. | **POST-CUTOFF VERIFIED data; RESULT REQUIRED for inference** | `work/zeus_sobol_{erdos_renyi,watts_strogatz,barabasi_albert,expander}_hz0_0_N12_20260809_*`; `reports/network_sobol_graph_ranked_2x3_2026-08-12/render_manifest.json`. | Completed valid configurations: ER 346, WS 334, BA 347, expander 339; one deterministic graph realization per Sobol configuration; dynamics `N=12`, `t=10^6`; graph seed is recorded per configuration. No matched-parameter family comparison, graph-realization uncertainty, or size scaling. | Not main evidence. Ranked examples are selection-biased. A high BA example has `S_born=0.828` but `|c2|=0.9998`, an excellent false-positive control for polar-only claims. |
| V1 | Coupling activation/degeneracy and level-spacing atlases show structure but do not select Born-like cases. | **POST-CUTOFF VERIFIED; PRELIMINARY NUMERICAL RESULT** | `reports/vab_activation_all_cases_2026-07-27`, `detector_degeneracy_group_atlas_2026-07-28`, `vab_coupling_group_atlas_2026-07-28`, and associated manifests. | Mostly `N=14`, `t=10^6` dynamics joined to smaller detector-only spectra (`N_D=8` or 10); 880-case atlas; some level spacings mix unresolved symmetry sectors. | Supplement/outlook only. No chaos/universality claim is defensible from mixed-sector panels. |
| R1 | Fresh resonance-neighborhood rerun confirms that exact resonances broaden polar support but do not recover full Born structure. | **POST-CUTOFF REPRODUCED** | `work/single_pixel_quspin_fresh_2026-07-12`; configs `single_pixel_quspin_fresh_*`; `DONE`/metadata; `reports/resonant_hz_study_2026-07-12.md`; validation JSON. | N10 principal sweep; N8 near-resonance and 68-time long-average; seed 20260712; deterministic clean Hamiltonian; no stochastic CI. Exact resonances have strongly nonuniform azimuth and generally negative `S_born`. | Supplement negative control. This is the clearest explicit post-cutoff reproduction of older resonance observations. |
| O1 | Older logs/notebooks/figures establish model trends. | **PRE-CUTOFF / UNTRUSTED or DATE UNKNOWN / UNTRUSTED** | Root notebooks dated Jan-Feb 2026; `examples/logs/*` dated Feb-May 2026; `tp_size_scan_*.png` dated March 2026; copied legacy result directories lacking post-cutoff embedded rerun records. | Seeds and parameters vary; many raw products/logs are incomplete. Copied/creation dates around July 11 do not cure older embedded dates. | **Forbidden** as quantitative manuscript evidence. May guide a reproduction only. |

## Strongest matched-field evidence in exact numbers

The independently regrouped 24-row sequence is:

| Detector `N` | Roots per spectrum | Four-time `S_born` values (sorted) | Median | Maximum | Median `|<exp(2i phi)>|` |
|---:|---:|---|---:|---:|---:|
| 11 | 2,048 | -0.00843, 0.13909, 0.24401, 0.31964 | 0.19155 | 0.31964 | 0.02830 |
| 12 | 4,096 | 0.35983, 0.37083, 0.45137, 0.46636 | 0.41110 | 0.46636 | 0.02439 |
| 13 | 8,192 | 0.56648, 0.56749, 0.57545, 0.61996 | 0.57147 | 0.61996 | 0.02520 |
| 14 | 16,384 | 0.67392, 0.70740, 0.72298, 0.75282 | 0.71519 | 0.75282 | 0.01526 |
| 15 | 32,768 | 0.75154, 0.77969, 0.79708, 0.80310 | 0.78839 | 0.80310 | 0.01904 |
| 16 | 65,536 | 0.78568, 0.80641, 0.80853, 0.83950 | 0.80747 | 0.83950 | 0.01672 |

All matched rows have reported polar coverage one. These are algebraic-root samples within deterministic spectra, not independent experimental shots. The apparent monotone trend is useful numerical evidence, but it has no declared continuum extrapolation, time-window convergence, bin-count convergence, bootstrap interval, or random-disorder ensemble.

## Exact N=16 raw data and root conventions

Common directory:

`work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/raw/N16/hz0_+0.1000/`

| Time | Raw NPZ | SHA-256 |
|---:|---|---|
| `10^3` | `raw_t1000.npz` | `5786dd123f0cd3b33fb0dfdf2dd9cc3568c9b899af8f0f81c3f6a2b8b168c3d2` |
| `10^4` | `raw_t10000.npz` | `e467b5efa6a5b8b7e3e7333a06555007b629a26bbeac2b21cd3da27d88313d59` |
| `10^5` | `raw_t100000.npz` | `488028be94db4df817e6e396fa9c737f4dc3b1b159702008c48aebe50fa30bef` |
| `10^6` | `raw_t1000000.npz` | `1301f73272898ba6b2b707758e89817f0587cd75d46e73df896f6fa08eb88c45` |

Every file contains:

- `eigenvalues`: complex128, shape `(65536,)`, all finite;
- `theta`: float64, shape `(65536,)`;
- scalar `theory_variance`, `hz0`, `hz`, `J`, `Jx_edge`, `Jx`, `detector_n`, and `total_qubits`.

In all four files, stored `theta` agrees with `2*atan(abs(eigenvalues))` within `4.44e-16`. The reconstructed Bloch vectors have maximum unit-radius error below `8.89e-16`.

The production convention is

`lambda = eig(M)`, with `M(t) = U00(t)^(-1) U10(t)`.

The blue normalized qubit state is `(1, lambda)/sqrt(1+|lambda|^2)`, giving

`x = 2 Re(lambda)/(1+|lambda|^2)`,

`y = 2 Im(lambda)/(1+|lambda|^2)`,

`z = (1-|lambda|^2)/(1+|lambda|^2)`,

`theta = 2 atan|lambda|`, and `phi = arg(lambda)`.

The existing analysis derives `D1=-conj(D0)` and maps the second state as `(D1,1)/sqrt(1+|D1|^2)`. Its Bloch vector is identically the negative of the first. Therefore captions must say, for example:

> Blue: production roots `v(lambda)` of `U00^{-1}U10`; red: their exact companion antipodes `-v(lambda)`. The stored `+t` cloud is a forward-preimage cloud for `U(-t)`; for the real matched Hamiltonian, the `U(+t)` forward cloud has the same polar coordinates and reflected azimuths.

For a unitary `U=[[A,B],[C,D]]`, the complementary-minor theorem gives an exact antipodal pairing between the forward outcome pencils `(alpha C+beta D)` and `(alpha A+beta B)`: one regular forward pencil has `d` independent projective coordinates, and the other labelled root multiset is their antipode, including algebraic multiplicity. Thus two independent coordinate clouds are neither expected nor required. Associated companion detector null vectors and physical record observables are separate questions.

The current production roots can be interpreted as pole-input separable outputs for `U(t)`, or via inverse evolution as exact pole-boundary preimages for `U(t)^dagger=U(-t)`. They must not be silently relabelled as forward roots for the same `U(t)`. For a real symmetric Hamiltonian in the computational basis, `U(-t)=U(t)^*`; the production root multisets at `+t` and `-t` are complex conjugates. Consequently the stored matched-field data transfer exactly to same-time forward **polar** coordinates, while the azimuth transforms as `phi -> -phi`. A full-sphere forward rendering must apply or state this reflection.

## Safe full-sphere figure recipe

No simulation is needed. Load one trusted matched NPZ, preferably `N=16,t=10^6`, compute `phi=angle(lambda)` and `cos(theta)=(1-|lambda|^2)/(1+|lambda|^2)`. If the panel is explicitly a same-time forward-preimage panel for `U(+t)`, use the real-Hamiltonian bridge and plot `phi_forward=-phi_production` (equivalently conjugate the roots), recording that convention. Then render either:

1. a compact Bloch sphere of the blue production roots, plus an adjacent equal-area `(phi, cos theta)` map; or
2. one labelled outcome root multiset and its exact antipodal outcome partner in both panels, with the time-direction/reflection convention in the legend and caption.

Use the raw-root count, SHA-256, `DONE.json` timestamps, and `metadata.json` parameters in the figure's provenance comment. Do not smooth without recording the bandwidth. If point overplotting is controlled by deterministic subsampling, state the exact index rule and preserve a full-count equal-area histogram in a second panel.

The existing seven-column atlas is scientifically traceable but too dense for a PRL column. A fresh compact rendering from the NPZ is a post-processing reproduction, not a new many-body simulation. It should be classified **POST-CUTOFF REPRODUCED (figure post-processing)** while the underlying roots remain **POST-CUTOFF VERIFIED**.

What this figure may support:

- the production root set occupies the full sphere at the matched point, and for the real matched Hamiltonian the same is true of the reflected same-time forward set;
- the specific low second azimuthal harmonic reported for the sampled times;
- the contrast with off-matched meridional/narrow-support controls if shown from equally trusted raw data.

What it may not support:

- a direct same-time forward-pencil computation without invoking and documenting the real-Hamiltonian time-reversal bridge;
- a validated empirical full-sphere Born asymmetry `a(theta,phi)` until the reflected forward density and its antipode are analyzed with odd-parity/multipole diagnostics;
- azimuthal uniformity from the `m=2` harmonic alone;
- finite-size concentration or an operational selection probability.

## Haar audit and feasible reproduction

The current stored N13 Haar image is pre-cutoff and must be rejected. The existing `examples/haar_random_unitary.py` is fast at modest dimension, but it saves only a PNG/log. Its deterministic antipodal red cloud is mathematically appropriate for the companion root locations; the publication limitations are the missing raw roots, completion manifest, hashes, residuals, and rotational discrepancy statistic.

An in-memory feasibility benchmark performed during this audit with the current code path used `N=7` (global `D=128`, detector-pencil dimension 64), seed `20260814`, and 64 roots. Excluding import/font-cache overhead, Haar QR plus the relative pencil took about 0.63 seconds. This demonstrates that a post-cutoff modest-dimension visualization or a small multi-seed check is cheap.

A scientifically acceptable new illustrative Haar artifact should save:

- raw complex roots and stereographic coordinates;
- global dimension and detector-pencil dimension (avoid ambiguous `N` labels);
- RNG algorithm and every seed;
- code snapshot/hash and exact generation time;
- unitarity and pencil residuals;
- an equal-area discrepancy and low-order spherical harmonics for each realization;
- a caption stating that the red branch, if present, is a deterministic antipode.

One modest realization is useful only as a visual check of the exact analytical isotropy theorem. A finite-realization concentration claim needs several dimensions and multiple independent seeds with uncertainty. Since the analytical one-point intensity is already exact, the cleanest PRL option is to omit empirical Haar numerics unless a compact multi-seed validation is deliberately added.

## Numerical claims that must be rejected or weakened

1. **"Haar numerics are post-cutoff."** False for the stored N13 image.
2. **"The two outcome root clouds should be independent."** False. Unitarity forces exact antipodal root multisets. What remains unverified in the highlighted data is the direct same-time forward-pencil bridge and the companion detector vectors/records.
3. **"Full-sphere Born agreement has been demonstrated."** Not yet. Existing evidence is a polar paired-ratio score plus limited azimuthal diagnostics and point-cloud views. The real-Hamiltonian bridge fixes the required `phi` reflection, but the odd asymmetry field has not been decomposed into its Born dipole and higher odd multipoles.
4. **"Born probabilities have been numerically derived."** Not established. Equal root counting is an analysis convention, not a physical preparation/selection measure.
5. **"Generic structured Ising/XY detectors become Born-like."** Too broad. One clean matched-field sequence is strong; many structured controls fail.
6. **"A transverse field produces a Born-to-uniform chaos crossover."** No controlled, publication-grade, symmetry-resolved, post-cutoff dataset was located.
7. **"Heavy tails, exact degeneracy, or chaos explain Born behavior."** The post-cutoff data contain counterexamples and mixed-sector limitations. These are at most proposed predictors/tests.
8. **"The N11-N16 trend is converged."** No controlled size/time extrapolation or resolution study exists.
9. **"The 1,208 spectra are independent samples."** They are deterministic parameter/time evaluations, many on related grids.
10. **"Filesystem modification after July 1 proves eligibility."** False for copied legacy outputs; embedded run records govern.

## Low-cost, high-value reproductions and checks

These are post-processing or small-matrix tasks, not production campaigns:

| Priority | Task | Cost | Acceptance criterion |
|---|---|---:|---|
| Critical | Compact matched N16 full-sphere/equal-area figure from the four hashed NPZs. | Seconds to minutes | Exact root counts/hashes, no smoothing or fully recorded smoothing, antipodal outcome relation labelled, and the real-Hamiltonian `phi -> -phi` bridge stated/applied for a same-time forward interpretation. |
| Critical | Recompute `S_born`, coverage, occupied-bin RMSE, and several azimuthal harmonics directly from the 24 matched NPZs at multiple bin counts. | Minutes | Scores agree with stored values at the original resolution; qualitative trend survives at least three declared resolutions. |
| Critical | Compute one homogeneous forward pencil for a small trusted matched case and store projective/infinite roots and backward residuals; obtain the companion root locations by the exact antipodal theorem and solve its null vectors only if record analysis needs them. | Small-N minutes | Validates the production/forward `U` versus `U^dagger` time-direction bridge and the real-Hamiltonian azimuthal reflection. Scaling direct QZ to N16 is separate. |
| High | Post-cutoff Haar illustration at modest `d`, preferably several seeds and two or three dimensions. | Seconds to minutes at modest `d` | Raw roots, seeds, residuals, equal-area/spherical-harmonic discrepancies, confidence intervals; no finite-d concentration overclaim. |
| High | Recover missing raw NPZs for the degeneracy falsification campaign. | Data transfer only if Zeus outputs exist | Locally recompute all decisive metrics and verify file hashes. |
| High | Aggregate graph campaigns by matched Sobol index and/or multiple graph realizations. | Post-processing for matched indices; new graph ensembles require compute authorization | Avoid ranked-example bias; report family effect with graph-realization uncertainty and control for Hamiltonian parameters. |
| Medium | Time-window resampling of existing matched four-time data. | Seconds | Descriptive spread only. This cannot replace denser predeclared time sampling. |

## Critical missing numerical evidence

- A direct homogeneous forward-pencil validation for highlighted `U(t)` points, with root residuals, singularity/infinity diagnostics, multiplicities, and explicit comparison to the production roots for `U(-t)`. The second forward root multiset follows exactly by antipodes; it is not an independent coordinate calculation.
- A full-sphere outcome asymmetry/density analysis `a(theta,phi)` or `f_k(theta,phi)` built from one forward density and its exact antipode, enforcing `a(-Omega)=-a(Omega)` and separating the Born `ell=1` dipole from allowed non-Born odd `ell>=3` power.
- A physical sampling/preparation measure and detector-state weighting; without it root counts are not operational probabilities.
- Stable and distinguishable detector record diagnostics over a time window.
- Bin/KDE/harmonic robustness, root backward errors, conditioning, infinity handling, and degeneracy audit for the production matched sequence.
- Controlled size/time-window convergence and uncertainty; the present four times are deterministic samples.
- A post-cutoff multi-seed Haar concentration study only if finite-realization claims are desired.
- Symmetry-resolved spectral statistics before any Poisson/GOE/chaos mechanism claim.

## Recommended manuscript use

Main Letter:

- exact theory plus analytical Haar isotropy;
- M1/M4 finite-size matched-field trend, explicitly called a polar root-count statistic;
- M3 compact full-sphere production-root visualization with exact antipodal pairing and the real-Hamiltonian azimuthal-reflection bridge stated;
- one concise sentence that only the matched rows pass the stated polar-coverage/second-harmonic gate across the 1,208-spectrum comparison.

Supplement:

- exact Hamiltonian and numerical conventions;
- full per-time matched table and NPZ hashes;
- resonance, two-pixel, anisotropic, Sobol, and graph counterexamples/controls;
- numerical limitations and the absent-forward-pencil warning.

Exclude:

- the pre-cutoff N13 Haar image;
- all pre-cutoff notebooks/log figures as empirical evidence;
- ranked graph examples as family evidence;
- mixed-symmetry level-spacing panels as chaos classification;
- any claim of operational Born probability or convergence, and any suggestion that the two outcome root coordinates are independent.

## Final audit judgment

The repository contains enough trusted post-cutoff evidence for a sharp, cautious PRL numerical statement: a clean matched-field many-body ring develops a strong finite-size Born-like **polar root-count geometry** while simple meridional false positives are excluded by coverage and a low second azimuthal harmonic. Exact complementary-minor duality supplies the antipodal outcome pairing; two independent coordinate clouds are not required. It does not yet contain the numerical evidence required to call this a full-sphere Born probability law or a completed measurement model. The most damaging numerical gaps are the unvalidated same-time production-to-forward bridge at the highlighted data points, the absence of an odd-multipole full-sphere analysis, and the missing selection measure and detector-record observables.
