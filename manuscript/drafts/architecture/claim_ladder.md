# Evidence-Bound Claim Ladder

The manuscript advances from exact existence and symmetry results to a finite numerical diagnostic, then stops at the operational boundary. Each claim below is tied to `manuscript/EVIDENCE_REGISTRY.md`.

## Claim 1: Definite-pole product inputs are homogeneous pencil roots

**Statement.** For a qubit-first unitary $U=\begin{pmatrix}A&B\\C&D\end{pmatrix}$, a product input with qubit coordinate $q=[\alpha:\beta]$ reaches pole $0$ exactly when $(\alpha C+\beta D)\eta=0$, and reaches pole $1$ exactly when $(\alpha A+\beta B)\eta=0$. A regular $d\times d$ pencil has $d$ roots in $\mathbb{CP}^1$, counted with algebraic multiplicity.

- **Evidence:** T1, exact theorem.
- **Comparator:** Replaces an informal search over special inputs with a homogeneous generalized-eigenvalue problem.
- **Caveat:** The count does not imply distinct roots, equal physical weights, or $d$ independent detector rays. Roots at infinity must be retained; singular pencils require Kronecker analysis.
- **Figure/equation:** Fig. 2; block and pole-condition equations.
- **Wording ceiling:** “Characterizes pole-compatible product inputs as projective pencil roots and counts them for regular pencils.”

## Claim 2: Unitarity fixes exact antipodal outcome geometry

**Statement.** Jacobi complementary-minor duality pairs every outcome-$0$ root with the Bloch antipode of an outcome-$1$ root, preserving algebraic multiplicity. Hence $\rho_1(\Omega)=\rho_0(-\Omega)$ and the paired asymmetry is inversion odd.

- **Evidence:** T2, exact theorem.
- **Comparator:** The outcome labels form one root multiset and its deterministic antipodal partner, not two independent point clouds.
- **Caveat:** Antipodal root coordinates do not provide the companion detector vectors, a selection law, or a detector record.
- **Figure/equation:** Fig. 2; complementary-minor identity and asymmetry equation.
- **Wording ceiling:** “Proves exact antipodal pairing of the two same-unitary outcome-root multisets.”

## Claim 3: Haar scrambling is an exact isotropic ensemble null

**Statement.** For Haar $U(2d)$, the forward roots have the complex spherical-ensemble law and uniform one-point intensity $d/(4\pi)$ on the Bloch sphere.

- **Evidence:** T3, exact ensemble theorem.
- **Comparator:** An isotropic ensemble intensity has no fixed preferred measurement axis and gives the intensity-level baseline $S_{\mathrm B}=0$.
- **Caveat:** This is not a concentration theorem for one finite Haar realization and does not justify claims about generic chaotic Hamiltonians.
- **Figure/equation:** Haar-null result in the text; baseline in Fig. 4(a).
- **Wording ceiling:** “Shows that the Haar ensemble has uniform one-point root intensity and no ensemble-selected axis.”

## Claim 4: One matched ring exhibits a strongly dipolar full-sphere root asymmetry

**Statement.** For the audited $N=16,t=10^4$ matched-field ring, 65,536 finite production roots and their exact antipodal partners yield a fully occupied $36\times18$ equal-area map with no smoothing, count-weighted Born residual $0.089$, correlation $0.971$ with $\mu=\cos\theta$, and dipole fraction $0.982$ of resolved odd power through $\ell=7$.

- **Evidence:** N2 and N3, trusted/derived post-cutoff diagnostics.
- **Comparator:** The map is strongly dipolar, unlike the exact isotropic Haar one-point null.
- **Caveat:** The residual depends on resolution as cells become sparse; the result is a root-count diagnostic at finite size and resolution, not a continuum or probability claim. Even-power suppression checks exact antipodal construction rather than adding independent physics.
- **Figure/equation:** Fig. 3; full-sphere asymmetry and residual definition.
- **Wording ceiling:** “Shows a strongly dipolar finite-resolution root-count asymmetry in the highlighted matched ring.”

## Claim 5: The matched sequence has a monotonic finite-size trend

**Statement.** Across four deterministic saved times at each $N=11,\ldots,16$, the median polar score is $0.192, 0.411, 0.571, 0.715, 0.788,$ and $0.807$, respectively. All 24 matched rows have unit polar coverage and satisfy the declared $|c_2|\le0.25$ gate.

- **Evidence:** N1 and N4, trusted post-cutoff numerical evidence.
- **Comparator:** Among 1,208 completed spectra in the four audited sweep tables, exactly these 24 matched-field rows pass the declared coverage and azimuthal gates.
- **Caveat:** Saved times are deterministic observations, not independent samples. The trend supplies no stochastic uncertainty, controlled $N\to\infty$ extrapolation, or mechanism for the matched-field condition. The second harmonic alone does not establish azimuthal uniformity.
- **Figure/equation:** Fig. 4; polar-score definition.
- **Wording ceiling:** “Reports a monotonic finite-size trend across the audited matched sequence.”

## Claim 6: The result defines a classification problem, not a completed measurement theory

**Statement.** Exact root geometry and the structured-versus-Haar contrast motivate classifying Hamiltonians by their outcome-root geometry, preparation measure, and record structure.

- **Evidence:** Inference from T1–T3 and N1–N4.
- **Comparator:** Separates the proved existence question from unresolved selection and record questions.
- **Caveat:** Algebraic multiplicity is not an operational probability. Different roots generally require different detector microstates, and instantaneous factorization does not establish stable, distinguishable, redundant records.
- **Figure/equation:** Interpretation/discussion; Fig. 1 scope boundary.
- **Wording ceiling:** “Defines a concrete structural classification program for unitary measurement-compatible dynamics.”

## Claims excluded from the manuscript spine

- A derivation of definite outcomes or wave-function collapse.
- Operational Born probabilities from algebraic root counts.
- A universal or asymptotic Born law for structured detectors.
- A chaos, integrability, or many-body-localization mechanism.
- Analytic constructive families, detuning no-go theorems, or non-normal limits not registered in the active evidence base.
