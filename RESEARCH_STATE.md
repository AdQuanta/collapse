# RESEARCH_STATE.md — Current Frontier

> **2026-09-13 analytic goal — OPEN.** Follow `goal-analytic.md`'s
> thermodynamic-first **Cesàro** order, distinct from the older objective below.
> **PROVED, central-X rings:** an exact Pauli/Newton recurrence and locality
> argument give the interacting detector root law as a folded Gaussian with
> recurrence-defined autocorrelation variance. Both ordered limits and an
> exact measure formula for R are established in this scope; hx!=0 forces
> the explicitly uniform late-time law R=1/2 for gx!=0, even with full
> detector NN/NNN XYZ. **PROVED, central-X chains:** the fixed-time root law
> has a norm-controlled thermodynamic limit. **PROVED, report 10:** with
> every detector coefficient retained, all ordered Cesàro moments vanish
> for Lebesgue-a.e. h0x, giving dtheta/pi and R=1/2. Arbitrary prescribed
> exceptional fields and additional central coupling axes/non-X fields
> remain OPEN. No field randomization is added to the observable.
> Frozen v3 symbolic checks and 36 further QZ comparisons passed; small-N
> Gaussian errors are nonmonotone and are retained. See reports 05–07 and
> `wiki/campaigns/analytic_distribution_ring_master_ledger.md` / `wiki/campaigns/analytic_distribution_chain_master_ledger.md`.
> Focus correction: park the restricted boundary-Majorana benchmark; it is
> not an established prerequisite for the full goal. Its v4 candidate check
> failed (bound pole equation); preserve that record without promotion.
> Report 09 retains all detector terms: PROVED first-moment mean as a
> Liouvillian zero-frequency atom, but the higher-moment replica functional
> has norm 2^(N(ell-1)). Frozen v5 passes; 24 QZ checks pass. Actual second-
> moment frequency variation rises 2.14→6.27 at N=2–5 (INCONCLUSIVE for
> boundedness). Report 10 bypasses that bound using scalar modulation and
> Plancherel; frozen v6 passes, including a nonzero-field exception with
> b1=0,b2=1/2. Next: characterize exceptional prescribed h0x (especially
> zero) or cross the next central-axis/nonnormal-root obstruction.
> Exact exchange singular pencils still obstruct an everywhere-defined P.


> **2026-09-12 audited correction — objective OPEN.** The perturbative
> completion claim is withdrawn; density is J'' rather than J'. Existing
> Theorem C excludes a full-parameter open phase containing an X-conserving
> seed. Frozen verifier v1 reproduces all 15 saved positive snapshots, with
> largest-size normalized balance residuals .05808/.05675 (X-only rings),
> .27107 (079), .36732 (047). Fresh QZ validity, multiple times and generic
> perturbations remain missing. Next: genuinely multichannel seeds.
> See `research_reports/BORN_PHASE_AUDIT_2026-09-12.md`.

> **Reduced follow-up:** 162 full-QZ conditions at N=5–7 and three times
> passed numerical validation, but all lack full coverage and no tested
> central-field/gz direction uniformly improves the reduced seeds. The
> larger-N question remains OPEN. Next: verify full-parameter ring translation
> sectors before a larger-N campaign. Evidence:
> `research_reports/BORN_MULTICHANNEL_SENSITIVITY_2026-09-12.md`.

> **2026-09-13 method ready:** full-parameter ring translation blocks pass
> 36 dense comparisons (through t=1e7) and 38 focused tests. Six larger-N
> baseline campaign submitted with user approval as 4682629[].zeus-master.
> Task 0 failed the fixed orthogonality gate (1.23e-12 > 1e-12); other tasks
> are running/queued. Preserve failures and inspect the eigensolver. Runbook:
> `hpc/zeus_born_ring_baseline_v1.md`.

> **Analytical follow-up:** ring gz changes vanish in the fixed-time normalized
> propagator 2-norm. Equality of the actual thermodynamic root laws follows
> only with logarithmic-tail control, still OPEN for the seeds. This settles
> neither the other 14 directions nor chains. Proof:
> `research_reports/BORN_RING_LONGITUDINAL_STABILITY_2026-09-13.md`.

Last updated: 2026-09-12

This file is a **short handoff**, not the project archive. Detailed derivations,
historical scans, and failed mechanisms belong in `wiki/` and
`research_reports/`.

Evidence labels:
`PROVED`, `VERIFIED_NUMERICALLY`, `PRELIMINARY_NUMERIC`, `CONJECTURE`,
`FALSIFIED`, `OPEN`.

## 1. Active objective

**OPEN.** Find and prove a nonempty open region of the implemented ring or
chain Hamiltonian families whose thermodynamic-first, instantaneous late-time
projective-root statistics satisfy the exact Born reflected profile

\[
R_*(\theta)=\cos^2(\theta/2),
\]

or prove a full-family no-go theorem.

This concerns projective-root geometry/statistics, not yet an operational
measurement probability law.

The active contract for this task was supplied as
`/Users/matanhaller/.codex/attachments/5a6ffaca-8580-480b-a8e3-1906d23880dd/goal-objective.md`;
there is currently no repository `goal.md`.

**Audit correction (2026-09-12):** the recent perturbative report's completion
claim is withdrawn. It did not prove a full-parameter open phase or the
required limits, and misidentified J' as a density (the interior density is
J''). Existing Theorem C already excludes any full-parameter open phase
containing an X-conserving seed. This does not exclude disjoint multichannel
regions. See `research_reports/BORN_PHASE_AUDIT_2026-09-12.md`.

## 2. Canonical projective object

With the central qubit first,

\[
U_N(t)=
\begin{pmatrix}
A_N&B_N\\
C_N&D_N
\end{pmatrix},
\qquad
C_Nv=\lambda A_Nv.
\]

Use production homogeneous QZ. The polar coordinate is

\[
\theta=2\operatorname{atan2}(|\alpha|,|\beta|),
\qquad
\lambda=\alpha/\beta.
\]

The finite-resolution September structural gate remains a **diagnostic only**:
64-bin full reflected polar coverage, ratio RMSE \(\le 0.05\), and first-eight
Born moment maximum residual \(\le 0.05\). It is not the theorem.

## 3. Exact effective Born condition

**PROVED, conditional on the limiting measure existing and being
nondegenerate.**

Let \(r=|\lambda|\), \(x=\log r\), and let \(S(\theta)=\pi-\theta\).

Exact Born reflection balance is equivalent to projective detailed balance:

\[
q_*(1/r)=r^4q_*(r),
\]

equivalently

\[
p_*(-x)=e^{2x}p_*(x),
\]

equivalently

\[
S_*\!\left[
\sin^2(\theta/2)\,\mu_*
\right]
=
\sin^2(\theta/2)\,\mu_*.
\]

All-order moment relations

\[
2a_{2m+1}-a_{2m}-a_{2m+2}=0
\]

are equivalent only together with the limiting-measure statement; collapsed
laws such as \(\delta_0\) satisfy the moment equations vacuously.

## 4. Correct asymptotic order

**PROVED, finite-N obstruction.** Generic finite-dimensional unitary dynamics
is recurrent, so an ordinary nontrivial fixed-\(N\) limit
\(\lim_{t\to\infty}\mu_{N,t}\) does not exist.

The relevant candidate is therefore

\[
\mu_{\infty,t}=\mathrm{w}\!-\!\lim_{N\to\infty}\mu_{N,t},
\qquad
\mu_*=\mathrm{w}\!-\!\lim_{t\to\infty}\mu_{\infty,t},
\]

if both limits exist.

Do not use time averaging, favorable subsequences, or optimized readout times
as substitutes.

Detailed proofs:
- `research_reports/BORN_ASYMPTOTIC_OBSTRUCTIONS.md`
- `research_reports/BORN_NONNORMAL_LIMIT.md`
- `research_reports/BORN_DETUNING_INTERVAL.md`

## 5. Established exclusions / cautions

**PROVED / FALSIFIED in the stated scopes:**

- strict pointer-QND evolution gives only pole roots;
- common central-X conserved models can be confined to a great circle;
- additive charge-conserving sectors can yield nilpotent root dynamics and
  collapsed polar laws;
- quadratic/matchgate endpoint-chain sectors can have a one-radius root law;
- complete Haar/spherical mixing gives \(R=1/2\), not Born;
- ordinary equal-multiplicity reciprocal pairing is weaker than Born detailed
  balance;
- asymptotic operator-moment/Gaussian limits do not by themselves control the
  nonnormal root law;
- commuting-vector detuning intervals are excluded under the proved moment and
  phase-mixing assumptions;
- detector level statistics alone are neither sufficient nor necessary for
  high finite-size Born scores.

Do not generalize any scoped no-go to the full interacting family.

## 6. Current positive numerical leads

### Interacting X-coupled ring sequences

**VERIFIED_NUMERICALLY / POSITIVE LEAD, not an asymptotic theorem.**

At fixed microscopic parameters and \(t=10^6\):

- nearest-neighbor interacting ring, \(N=14,15,16,17\):
  ratio RMSE \(0.051086, 0.046515, 0.033764, 0.015923\);
- second-neighbor interacting ring, \(N=14,15,16,17\):
  ratio RMSE \(0.057754, 0.050724, 0.024587, 0.017574\).

All have full reflected 64-bin polar coverage. Largest-size eight-moment
maxima are approximately \(0.0141\) and \(0.0152\).

These reference cases still have special structure (including central-X/great-
circle issues) and do not establish a full-sphere open phase.

Primary report:
`research_reports/BORN_WEAK_COUPLING_SEARCH.md`.

### Multichannel ring leads

**REPRODUCED_NUMERIC / POSITIVE LEAD.**

Archived ring configs 079 and 047 have both \(g_x,g_y\neq0\), full reflected
coverage, and improving ratio RMSE with size:

- config 079: \(0.097703,0.068593,0.054979\) for \(N=13,14,15\);
- config 047: \(0.123585,0.120579,0.087264,0.062789\) for
  \(N=13,14,15,16\).

Largest-size eight-moment maxima are approximately \(0.0530\) and \(0.0454\).
Higher azimuthal harmonics remain substantial. These are search seeds, not
phase evidence.

Primary report:
`research_reports/BORN_POSITIVE_MULTICHANNEL.md`.

## 7. Exact structural tools now available

**PROVED / IMPLEMENTED in stated scopes:**

- production homogeneous projective-QZ root pipeline;
- circle-averaged log-determinant/root-limit potential with endpoint handling;
- exact Schur/Volterra return representation for requested XYZ families;
- interaction-picture finite-time kernel with phase-retaining sinc filter;
- symmetry-resolved level statistics;
- activation-resolved cross-sector diagnostics;
- ring/chain family implementations and weak-coupling evidence tooling.

Relevant files include:

- `core/relative_evolution_pencil.py`
- `core/projective_roots.py`
- `core/projective_potential.py`
- `core/ring_chain_family.py`
- `core/weak_coupling_picture.py`
- `core/activation_resolved_projective.py`
- `core/level_spacing.py`

Check the repository before adding parallel infrastructure.

## 8. Current champion and baseline

**Baseline:** the strongest reproducible matched/interacting ring reference
documented in the weak-coupling reports.

**Current champion:** no Hamiltonian has yet earned "open-phase champion"
status. The best current objects are **candidate seeds** only.

A candidate may be promoted only by surviving:

1. increasing \(N\);
2. multiple widely separated late times;
3. direct projective-detailed-balance verification;
4. multidirectional microscopic perturbations;
5. nonshrinking parameter width away from exact resonance/symmetry surfaces.

Store exact champion config/path here when one is promoted.

## 9. Highest-value unknowns

1. Does any positive ring seed possess a nonshrinking basin width as \(N\)
   increases, especially normal to matched-field/resonance surfaces?
2. Can generic nonzero central fields and \(g_z\) preserve/improve the
   projective-detailed-balance law?
3. Do genuinely interacting non-Gaussian endpoint chains develop the same
   effective law?
4. What microscopic mechanism produces the exact tilt
   \(p(-x)=e^{2x}p(x)\)?
5. Can the thermodynamic root potential/determinant machinery control the
   nonnormal small-singular-value tails in the surviving interacting regime?

## 10. Immediate next loop

The 2026-09-12 audit supersedes the X-only basin-search priority below:
`core/born_phase_verifier.py` now freezes schema `born-phase-verifier-v1`.
All 15 saved positive snapshots reproduce; largest-size normalized binned
balance residuals are .05808/.05675 (X-only rings), .27107 (079), .36732 (047).
Fresh QZ validity, multiple times and generic perturbations remain missing.
Use genuinely multichannel seeds for the next reduced production-QZ checks;
do not repeat the already-proved central-X field exclusion.
Evidence: `reports/born_phase_archive_audit_v1_2026-09-12/`.

The remaining general search sequence is:

1. reproduce the best positive ring seed with the canonical verifier;
2. map its local sensitivity in all admissible parameter directions;
3. measure normal-direction basin width versus \(N\);
4. test one mechanism at a time for widening/stabilizing that basin
   (NNN/XYZ/central fields/\(g_y,g_z\));
5. retain only candidates that improve worst-case size/time/perturbation
   behavior;
6. transfer the learned structure to the endpoint chain;
7. if a basin survives, prioritize analytical derivation over broader search.

Detailed history and proofs belong in the wiki/reports, not here.
