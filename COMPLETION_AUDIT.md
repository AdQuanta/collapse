# Completion audit: fresh single-pixel resonant-hz study

Updated: 2026-07-14. For the original resonant-hz study, only outputs below
`work/single_pixel_quspin_fresh_2026-07-12` count as numerical evidence;
yesterday's outputs and the collided first long-average attempt are excluded.
The separately requested central-field and `hz`-neighborhood addenda use only
their explicitly labelled 2026-07-14 work namespaces.

## Plus-minus field-neighborhood addendum completed on 2026-07-14

- A separately labelled detector `N=10`, `J=0`, `Jpm=1` sweep covers 25
  fields around `-2,-1,0,+1,+2` at all four requested late times. Collective
  `Jx=0.01` is normalized to `Jx/sqrt(N)` on every central edge.
- All 100 raw spectra contain 1024 finite eigenvalues. Twenty 3x5 atlases and
  one summary were rendered and visually inspected; histogram and connected
  ratio-line conventions are satisfied.
- The implementation reuses the SOLID service layer and injects an exact
  finite-N plus-minus spectral-variance provider for no-fit wrapped-Gaussian
  references.
- Measured result: the band edges `hz=+-Jpm` maximize polar spreading but have
  increasingly negative Born score; `hz=0` is moderately positive with only
  half-bin coverage; off-band `+-2Jpm` controls remain narrow. The azimuthal
  harmonic remains near one throughout.
- Validation passes for model and coupling metadata, raw arrays, figure sizes,
  `hz -> -hz` polar symmetry, theory provenance, and rendering contracts. The
  focused test suite passes 41/41.

## Corrected `hz` resonance-neighborhood addendum completed on 2026-07-14

- The canonical normalization is collective `Jx=0.01` with per-edge
  coefficient `Jx/sqrt(N)=0.0031622776601683794` at `N=10`.
- Fifteen `hz` values cover `-2,0,+2` and detunings
  `-0.05,-0.01,0,+0.01,+0.05` at all four requested times. Each of the 60 raw
  spectra contains 1024 finite relative-evolution eigenvalues.
- Twelve 3x5 atlases and one coupled summary were rendered and visually
  inspected. Empirical angular distributions are histogram stairs and
  occupied-bin `R(theta)` samples are line-connected.
- Exact resonances have broad polar support but negative Born score, while the
  second azimuthal harmonic stays near one. The polar metrics obey exact
  positive/negative-field symmetry.
- The reusable implementation follows SOLID separation and dependency
  inversion. Validation passes for all raw data, figures, metadata, symmetry,
  and rendering contracts; the focused test set passes 34/34.

## Central-field atlas addendum completed on 2026-07-14

- A separately labelled N=10 central-field sweep was generated under
  `work/single_pixel_hz0_sweep_2026-07-14`; it does not alter the evidence
  namespace of the 2026-07-12 study. It was forcibly regenerated using the
  corrected collective `Jx=0.01`, per-edge `Jx/sqrt(N)` convention.
- Seven `hz0` values around fixed `hz=0.1`, including exact equality and
  +/-0.01 detuning, were evaluated at all four requested times. Each of the 28
  saved spectra contains 1024 finite relative-evolution eigenvalues.
- Four 3x7 atlases and one coupled summary plot were rendered and visually
  inspected. Empirical angular distributions are histogram stairs and
  `R(theta)` samples are line-connected.
- Its validator passes for 28 raw spectra, five high-resolution figures,
  corrected coupling metadata, and the explicit rendering contract.

## Diagnostic-atlas addendum completed on 2026-07-13

- Four N=10 3x7 diagnostic atlases were generated at exactly `1e3`, `1e4`,
  `1e5`, and `1e6`, spanning `hz=-3,-2,-1,0,1,2,3` and including all three
  resonances. Blue `P(theta)`/`v(lambda)` and red
  `P(pi-theta)`/`-v(lambda)` branches are shown consistently.
- Wrapped-Gaussian comparisons use the repository's fixed no-fit prediction.
  Born-ratio points are shown only for occupied bins; empty support is not
  interpolated. Every atlas and the coupled six-metric heatmap was visually
  inspected at full resolution.
- The self-contained LaTeX report compiled to a visually inspected 13-page
  PDF. The group-meeting presentation contains 16 slides, was rendered and
  inspected slide by slide, and passes the automated overflow checker. A
  matching speaker-notes file is present.
- Addendum validation passed: 13 focused tests, the original 646-point fresh
  dataset validator, and the new artifact validator. The latter confirms 28
  metric rows, all 1024 mapped eigenvalues finite in each row, five
  high-resolution figures, 13 PDF pages, and 16 PPTX slides.
- The addendum's central finite-size observation is internally coupled rather
  than based on a single score: resonant polar-bin coverage reaches 95.8%, all
  resonant `S_born` values remain negative, and the second azimuthal harmonic
  remains at least 0.953. This supports polar spreading without Born
  phase-space statistics.

## Completion evidence

- Exact environment verified: Python 3.12.13, QuSpin distribution 1.0.0,
  QuSpin Extensions distribution 0.1.6, NumPy 2.4.6, SciPy 1.18.0, and
  Matplotlib 3.11.0.
- Fresh mandatory N=10 sweep: seven fields (`-3` through `+3`, including all
  three resonances) by all five required times, 35 raw points.
- Fresh near-resonance N=8 sweep: 27 fields with offsets down to 0.01 about
  `-2`, `0`, and `+2`, by all five required times, 135 raw points.
- Fresh N=8 long-time campaign: seven fields by 68 saved times, 476 raw points;
  every average uses 66 distinct times strictly above 1000. Alternative grids,
  time counts, lower-edge inclusion, and histogram bins are compared.
- Raw arrays and metadata are separate from generated figures. Configuration,
  resumability, individual-point execution, aggregation, and deterministic
  paths are implemented.
- Required angular, reflection, Born-ratio, canonical `S_born`, azimuthal,
  Bloch-sphere, full/detector spectrum, resolved-sector spacing, wrapped-
  Gaussian, finite-size, conditioning, stability, and uncertainty diagnostics
  were generated from completed files.
- Fresh validator passed all dataset, normalization, residual, path-isolation,
  long-average-count, and positive/negative symmetry checks. Maximum solve and
  eigen residuals are `7.51e-14` and `1.62e-13`.
- Focused study tests pass (10/10). Full repository suite: 105 passed, one
  pre-existing unrelated handoff-string assertion failed in
  `tests/test_hpc_postprocess_runbook.py`; it was not modified to conceal the
  failure. CLI and end-to-end smoke tests passed.
- The Markdown report and rendered PDF were generated. The 16-slide deck was
  rendered to slide images, every slide was inspected, title clipping was
  corrected, and the slide overflow checker passed.
- PBS environment, array, dry-run, smoke, resume, logs, failure detection,
  aggregation, and report-regeneration instructions are present. No cluster
  execution is claimed.

## Scientific limits, not missing work

- N=10 is the largest completed local principal sweep; N=8 provides the
  finite-size and long-time comparison. Dense scaling makes N>=11 a Zeus task.
- The resolved detector sectors contain only 5--18 usable spacings, so the
  Poisson/GOE/GUE plots are diagnostics and support no ensemble classification.
- Wrapped-Gaussian secular growth is useful near early resonance but overshoots
  late finite-size saturation; fitted and predicted curves are labeled
  separately.
- The study establishes sharp finite-size resonance structure and persistent
  azimuthal localization. It does not establish a thermodynamic-limit result.
- Bash is unavailable on the local Windows machine, so the PBS script received
  static review but no local `bash -n` or scheduler validation.

All goal deliverables are present. The next external action is the documented
N=11 Zeus smoke run, followed by resource-based scaling.
