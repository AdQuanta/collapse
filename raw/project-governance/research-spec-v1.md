# Unitary Many-Body Collapse-Like Dynamics and Emergent Born Statistics — Research Specification v1.0

> Source: Repository `SPEC.md` (approved research specification)
> Collected: 2026-09-15
> Published: Unknown

# SPEC.md — Unitary Many-Body Collapse-Like Dynamics and Emergent Born Statistics

**Status:** Initial approved research specification  
**Spec version:** 1.0  
**Research phase:** Pre-manuscript  
**Manuscript gate:** `paper_ready = false` until the frozen verifier certifies all mandatory gates below.

---

## 0. Purpose and governance

This repository studies whether a **closed qubit + many-body detector evolving entirely unitarily** can exhibit measurement-like collapse behavior in the following precise sense:

> Certain initial qubit–detector product states evolve, at a fixed time \(T\), into product states whose qubit component is exactly one of two definite outcome states. For physically reasonable Hamiltonians, the distribution of the initial qubit components of these exact “collapsible” states may approach Born-rule statistics.

The goal is not merely to observe a numerical resemblance to Born’s rule. The project must identify and understand the **physical and mathematical mechanism** responsible for any Born-like regime.

### 0.1 Frozen-spec / frozen-verifier rule

Once a research run begins:

- `SPEC.md` and the verifier define the target.
- The verifier is **frozen and objective**.
- The research agent may propose changes to the spec or verifier, but **must not edit or activate those changes without explicit user approval**.
- Approved changes must be versioned and documented. Results obtained under different verifier versions must not be silently mixed.
- Search strategy may adapt. **The definition of success may not.**

The user may revise this specification later. Such revisions supersede earlier versions only after explicit approval.

### 0.2 Scope control

- Parameter ranges, numerical methods, sampling strategies, and refinement strategies inside an **approved Hamiltonian family** may be changed adaptively.
- A qualitatively new Hamiltonian family may be proposed by the agent, but **must not enter the active search space without explicit user approval**.
- Manuscript writing is out of scope until `paper_ready = true`.

---

# 1. Core scientific claim to test

The target claim is:

> A closed qubit + many-body detector evolving entirely under unitary dynamics can exhibit measurement-like collapse behavior: a subset of exact initial qubit–detector product states evolves into definite qubit outcome states, and for a stable, non-fine-tuned region of physically reasonable Hamiltonians the empirical distribution of the corresponding initial qubit states is consistent with the Born rule.

The project must determine whether this claim is true, approximately true, or false for the approved Hamiltonian families.

A negative result must not be rationalized away by changing the success criteria.

---

# 2. Exact definition of a collapsible state

Let

\[
H = H_q + H_D + H_{qD},
\qquad
U(T)=e^{-iHT},
\]

where:

- \(H_q\) acts on one qubit;
- \(H_D\) acts on a detector of \(N\) qubits;
- \(H_{qD}\) is a perturbative qubit–detector coupling;
- \(T\) is a fixed externally specified evolution time for each calculation and does **not** scale with the coupling strength merely to rescue the effect.

An initial state is required to be a product state

\[
|\Psi_{\mathrm{in}}\rangle
=
|\psi_q\rangle\otimes |D\rangle,
\qquad
|D\rangle\in\mathcal H_D,
\]

with no restriction that \(|D\rangle\) itself be a detector product state.

For a chosen qubit basis \(\{|0\rangle,|1\rangle\}\), an initial state is **exactly collapsible to outcome \(b\in\{0,1\}\)** if

\[
U(T)|\Psi_{\mathrm{in}}\rangle
=
|b\rangle\otimes |D_b'\rangle
\]

for some normalized detector state \(|D_b'\rangle\).

This is an **exact algebraic definition**. Numerical tolerances may be used to locate or verify exact solutions, but may not redefine collapse as “high fidelity.”

---

# 3. Exact matrix-pencil characterization

Define detector-space operator-valued qubit matrix elements

\[
U_{ba}(T)\equiv \langle b|U(T)|a\rangle,
\qquad a,b\in\{0,1\}.
\]

Thus

\[
U(T)=
\begin{pmatrix}
U_{00} & U_{01}\\
U_{10} & U_{11}
\end{pmatrix}_{q}.
\]

Parameterize the initial qubit state by the projective coordinate \(\lambda\),

\[
|\psi_q(\lambda)\rangle
=
\frac{|0\rangle+\lambda |1\rangle}
{\sqrt{1+|\lambda|^2}},
\]

with the point \(\lambda=\infty\) treated separately.

Then

\[
U(T)|\psi_q(\lambda),D\rangle
=
\frac{1}{\sqrt{1+|\lambda|^2}}
\left[
|0\rangle\otimes(U_{00}+\lambda U_{01})|D\rangle
+
|1\rangle\otimes(U_{10}+\lambda U_{11})|D\rangle
\right].
\]

Therefore:

### Outcome 0

\[
\boxed{
(U_{10}+\lambda U_{11})|D\rangle=0
}
\]

### Outcome 1

\[
\boxed{
(U_{00}+\lambda U_{01})|D\rangle=0
}
\]

These are generalized-eigenvalue / matrix-pencil problems.

For every admissible generalized eigenvalue \(\lambda_j^{(b)}\), every nonzero vector in the corresponding kernel gives an exact collapsible state. If

\[
k_j^{(b)}=
\dim\ker M_b(\lambda_j^{(b)}),
\]

that Bloch-sphere point receives weight \(k_j^{(b)}\).

The generic case is expected to have \(k_j=1\). Degenerate or singular pencils must be handled correctly rather than discarded. The \(\lambda=\infty\) sector must also be included.

The project must derive and validate this characterization before using numerical root statistics.

---

# 4. Bloch-sphere representation

Relate \(\lambda\) to Bloch angles by

\[
\lambda=e^{i\phi}\tan\frac{\theta}{2},
\qquad
\Omega=(\theta,\phi).
\]

Thus

\[
|\langle 0|\psi_q\rangle|^2
=
\cos^2\frac{\theta}{2},
\qquad
|\langle 1|\psi_q\rangle|^2
=
\sin^2\frac{\theta}{2}.
\]

At finite \(N\), each outcome set defines a weighted empirical measure on the Bloch sphere,

\[
\rho_b^{(N)}(\Omega;T)
=
\frac{1}{K_b}
\sum_{j\in\mathcal C_b}
k_j^{(b)}
\delta(\Omega-\Omega_j),
\]

with

\[
K_b=\sum_j k_j^{(b)}.
\]

Each outcome density is normalized separately:

\[
\int_{S^2}\rho_b(\Omega)\,d\Omega=1.
\]

Interpretation:

\[
\rho_b(\Omega)=P(\Omega\mid b).
\]

The gedankenexperiment assumes equal outcome priors,

\[
P(0)=P(1)=\frac12.
\]

---

# 5. Born criteria

## 5.1 Strong Born criterion

Define

\[
p_0(\Omega)
=
\frac{\rho_0(\Omega)}
{\rho_0(\Omega)+\rho_1(\Omega)}.
\]

The strong target is

\[
\boxed{
p_0(\Omega)
=
\cos^2\frac{\theta}{2}
}
\]

and therefore

\[
\boxed{
p_1(\Omega)
=
\frac{\rho_1(\Omega)}
{\rho_0(\Omega)+\rho_1(\Omega)}
=
\sin^2\frac{\theta}{2}.
}
\]

The target is asymptotic convergence toward this profile in the prescribed many-body and long-time limits, not merely a visually close finite-size histogram.

## 5.2 Weak Born criterion

Define azimuthally integrated conditional densities

\[
\bar\rho_b(\theta)
=
\int_0^{2\pi}
\rho_b(\theta,\phi)\,d\phi,
\]

with

\[
\int_0^\pi
\bar\rho_b(\theta)\sin\theta\,d\theta=1.
\]

The weaker target is

\[
\boxed{
\bar\rho_0(\theta)
=
\cos^2\frac{\theta}{2},
\qquad
\bar\rho_1(\theta)
=
\sin^2\frac{\theta}{2}
}
\]

in the relevant asymptotic limit.

The strong and weak criteria must be reported separately. Passing the weak criterion does not imply passing the strong one.

---

# 6. Numerical Born diagnostics

No single numerical score is sufficient. At minimum, track the following complementary diagnostics.

## 6.1 Global RMS error

\[
E_2
=
\left[
\frac{1}{4\pi}
\int_{S^2}
\left(
p_0(\Omega)-\cos^2\frac{\theta}{2}
\right)^2
d\Omega
\right]^{1/2}.
\]

This is the primary global strong-Born deviation score.

## 6.2 Worst-case supported error

\[
E_\infty
=
\operatorname*{ess\,sup}_{\Omega}
\left|
p_0(\Omega)-\cos^2\frac{\theta}{2}
\right|.
\]

At finite \(N\), evaluate this only where the density estimator has adequate support. It must not be dominated by empty or numerically unresolved regions.

## 6.3 Spherical-harmonic leakage

Because

\[
\cos^2\frac{\theta}{2}
=
\frac12(1+\cos\theta),
\]

the exact Born profile contains only the \(Y_{00}\) and \(Y_{10}\) sectors in the preferred basis.

If

\[
p_0(\Omega)=\sum_{\ell,m}c_{\ell m}Y_{\ell m}(\Omega),
\]

define a normalized leakage score \(E_{\mathrm{harm}}\) from all components outside \((\ell,m)=(0,0),(1,0)\).

This score must expose, in particular, unwanted \(m\neq0\) azimuthal structure.

## 6.4 Weak marginal error

Define \(E_{\mathrm{marg}}\) from the deviation of \(\bar\rho_0,\bar\rho_1\) from their target cosine- and sine-squared forms, using a normalized \(L^2\)-type measure with weight \(\sin\theta\).

## 6.5 Estimator robustness

At finite \(N\), the distributions are discrete. Any binning, KDE, harmonic reconstruction, or other density estimator must be checked for estimator dependence. Apparent Born agreement that changes materially under reasonable estimator choices is not evidence of convergence.

---

# 7. Required asymptotic structure

## 7.1 Order of limits

The prescribed physical order is

\[
\boxed{
N\to\infty
\quad\text{before}\quad
T\to\infty.
}
\]

The project must not silently interchange these limits.

At fixed \(T\), establish or extrapolate

\[
\rho_b^{(N)}(\Omega;T)
\longrightarrow
\rho_b^{(\infty N)}(\Omega;T).
\]

Then study the long-time behavior of the large-\(N\) distribution.

## 7.2 Long-time convergence

Preferred outcome:

\[
\rho_b^{(\infty N)}(\Omega;T)
\xrightarrow[T\to\infty]{}
\rho_b^{(\infty)}(\Omega).
\]

If the instantaneous distribution does not converge, the accepted fallback is the long-time average

\[
\overline{\rho}_b(\Omega)
=
\lim_{\tau\to\infty}
\frac{1}{\tau}
\int_0^\tau
\rho_b^{(\infty N)}(\Omega;T)\,dT.
\]

Actual convergence is stronger and must be distinguished from time-averaged convergence.

## 7.3 Numerical convergence standard

A convincing finite-size convergence study must include:

- a systematic sequence of increasing \(N\);
- enough sizes to expose an asymptotic trend rather than two or three small-size points;
- decreasing envelopes of the relevant Born-deviation scores, allowing finite-size oscillations;
- stability of the inferred large-\(N\) limit against reasonable extrapolation ansätze;
- numerical-resolution errors smaller than the observed finite-\(N\) trend;
- convergence throughout a successful parameter region, not only at one optimized point.

No particular power law is assumed a priori. The convergence law is scientifically useful but secondary to demonstrating controlled convergence itself.

If the asymptotic residual is convincingly nonzero, the result must be described as approximately Born-like rather than exact.

---

# 8. Weak-coupling requirement

Write

\[
H=H_0+H_{qD},
\qquad
H_0=H_q+H_D.
\]

The coupling must lie in a controlled perturbative regime characterized by a relevant dimensionless parameter of the form

\[
\epsilon
\sim
\frac{\|H_{qD}\|_{\mathrm{relevant}}}
{\Delta_{\mathrm{relevant}}}
\ll1,
\]

with degenerate/resonant sectors treated by the appropriate perturbation theory rather than by an invalid nondegenerate expansion.

The desired phenomenon is required to occupy an **open weak-coupling window**, not to persist at exactly \(g=0\).

At \(g=0\), qubit and detector decouple, so the rich collapse-state distribution is generically expected to become trivial. The \(g\to0^+\) crossover should still be studied and understood.

---

# 9. Approved initial Hamiltonian families

The initial approved search space consists of two 1D local detector geometries.

Use qubit \(0\) and detector spins \(i=1,\ldots,N\).

## 9.1 Ring detector with collective qubit coupling

At the first hierarchy level,

\[
H_{\mathrm{ring}}
=
H_q
+
H_D^{\mathrm{ring}}
+
H_{qD}^{\mathrm{ring}},
\]

with

\[
H_q
=
h_{0z}Z_0
\]

initially, and

\[
H_D^{\mathrm{ring}}
=
h_z\sum_{i=1}^{N}Z_i
+
J\sum_{i=1}^{N}Z_iZ_{i+1},
\qquad
Z_{N+1}\equiv Z_1.
\]

The initial simplest qubit–detector coupling is longitudinal collective coupling,

\[
H_{qD}^{\mathrm{ring}}
=
g_{z,N}\,
Z_0
\sum_{i=1}^{N}Z_i.
\]

More general approved axis-aligned collective couplings may be unlocked according to the hierarchy below:

\[
H_{qD}^{\mathrm{ring}}
=
\sum_{\alpha=x,y,z}
g_{\alpha,N}
\sigma_0^\alpha
\sum_{i=1}^{N}\sigma_i^\alpha.
\]

## 9.2 Endpoint chain with local qubit coupling

At the first hierarchy level,

\[
H_{\mathrm{chain}}
=
H_q
+
H_D^{\mathrm{chain}}
+
H_{qD}^{\mathrm{chain}},
\]

with

\[
H_q=h_{0z}Z_0,
\]

\[
H_D^{\mathrm{chain}}
=
h_z\sum_{i=1}^{N}Z_i
+
J\sum_{i=1}^{N-1}Z_iZ_{i+1},
\]

and

\[
H_{qD}^{\mathrm{chain}}
=
g_z Z_0Z_1.
\]

More general approved axis-aligned endpoint couplings may be unlocked as

\[
H_{qD}^{\mathrm{chain}}
=
g_xX_0X_1+
g_yY_0Y_1+
g_zZ_0Z_1.
\]

## 9.3 No NNN terms initially

Next-nearest-neighbor detector interactions are excluded from the initial search.

They may be proposed later only after simpler NN families are systematically explored and there is a scientific reason to unlock them.

---

# 10. Hamiltonian-complexity hierarchy

The search must proceed from minimal to more general models so that the first ingredient responsible for the phenomenon can be identified.

## 10.1 Detector interaction hierarchy

For both ring and chain:

1. Ising:
   \[
   J_z\neq0,\qquad J_x=J_y=0.
   \]

2. XX / XY:
   \[
   J_x,J_y\neq0,\qquad J_z=0,
   \]
   beginning with symmetric \(J_x=J_y\).

3. XXZ:
   \[
   J_x=J_y\neq0,\qquad J_z\neq0.
   \]

4. XYZ:
   \[
   J_x,J_y,J_z
   \]
   independently variable.

## 10.2 One-body-field hierarchy

1. Longitudinal fields only.
2. Add one transverse direction.
3. Allow fully general \(x,y,z\) fields only if needed.

The same minimality principle applies to \(H_q\).

## 10.3 Qubit–detector coupling hierarchy

1. \(ZZ\).
2. \(XX+YY\) / XY-type.
3. XXZ.
4. XYZ.

Cross-axis terms such as \(X_0Z_i\) are not part of the initial approved search space and require explicit approval if proposed later.

## 10.4 Unlocking the next tier

A simpler tier may be abandoned after **systematic numerical failure**. An analytical no-go theorem is not required.

“Systematic” means sufficient parameter coverage, multiple relevant \(N\) and \(T\), adaptive refinement where warranted, and checks that failure is not due to an obvious numerical pathology.

Negative results must be logged so the agent does not repeatedly rediscover the same dead end.

---

# 11. Collective coupling scaling with detector size

For the ring,

\[
H_{qD}^{\mathrm{ring}}
=
\sum_{\alpha}
g_{\alpha,N}\,
\sigma_0^\alpha S_\alpha,
\qquad
S_\alpha=\sum_{i=1}^{N}\sigma_i^\alpha.
\]

## 11.1 Conservative baseline

Since

\[
\|S_\alpha\|\sim N,
\]

the default operator-norm-controlled scaling is

\[
\boxed{
g_{\alpha,N}\propto \frac{1}{N}.
}
\]

This baseline is axis-independent.

## 11.2 Axis-dependent fluctuation scaling

The research loop may derive a different scaling from the physically relevant collective fluctuations.

If

\[
\mathrm{Var}(S_\alpha)\sim N^{\kappa_\alpha},
\]

then an \(O(1)\) coupling to centered fluctuations naturally suggests

\[
\boxed{
g_{\alpha,N}\propto N^{-\kappa_\alpha/2}.
}
\]

Thus the appropriate scaling may differ between \(x,y,z\).

Any departure from the conservative \(1/N\) baseline must be analytically justified by the detector’s correlations, susceptibility, symmetry, ordered phase, critical scaling, or another physically identified mechanism.

For the endpoint chain, the qubit couples to only one detector spin, so no thermodynamic \(N\)-renormalization is required generically:

\[
g_\alpha=O(1)
\]

with respect to \(N\), while remaining perturbatively small relative to the relevant energy scales.

---

# 12. Preferred measurement basis

The outcome basis must not be treated as arbitrary notation.

The project must identify a preferred Bloch axis

\[
\mathbf n_\ast
\]

such that its eigenstates

\[
|0_{\mathbf n_\ast}\rangle,\qquad
|1_{\mathbf n_\ast}\rangle
\]

define the basis in which the stable Born-like collapsible-state profile emerges.

Operationally, the preferred basis is the basis for which the asymptotic collapsible-state distributions satisfy the Born criteria.

Requirements:

- uniqueness up to
  \[
  \mathbf n_\ast\leftrightarrow-\mathbf n_\ast,
  \]
  which only swaps outcome labels;
- continuity/stability under small Hamiltonian perturbations;
- no broad set of unrelated equally optimal axes;
- a physical explanation of why the full
  \[
  H_q+H_D+H_{qD}
  \]
  selects this axis.

The microscopic origin is not assumed in advance. \(H_q\), \(H_D\), and \(H_{qD}\) may all contribute.

---

# 13. Robust Born-like region requirement

A successful result must behave like a stable **phase/region**, not an accidental fit.

The Born-like behavior must occupy a finite open region of the approved Hamiltonian parameter space.

The following are insufficient:

- a single optimized parameter point;
- an isolated resonance;
- a fragile lower-dimensional fine-tuned manifold;
- a result that disappears under arbitrarily small generic perturbations.

Within the successful region, the Born metrics, preferred axis, and proposed mechanism should vary smoothly and remain qualitatively stable.

Adaptive search and parameter refinement are allowed and encouraged, but the frozen success criteria must not be altered.

---

# 14. Mechanism requirement

Mechanism identification is a **hard scientific requirement**.

The project must explain a causal chain of the form

\[
\boxed{
\text{many-body property}
\rightarrow
\text{structure/statistics of }U_{ba}(T)
\rightarrow
\text{generalized-eigenvalue/root statistics}
\rightarrow
\rho_b(\Omega)
\rightarrow
\text{Born profile}.
}
\]

Possible mechanisms may involve interactions, correlations, mixing, chaos, spectral structure, symmetry, collective fluctuations, criticality, or another emergent many-body property. None is assumed in advance.

### Primary standard

Derive analytically or semi-analytically how the identified mechanism produces the Born distribution.

### Accepted fallback

Derive analytically/semi-analytically how the mechanism produces the required root statistics, then use controlled numerics to complete the final step from root statistics to the Born profile.

### Insufficient

- “The numerics look Born-like.”
- “Chaotic models seem to work better.”
- A correlation between a diagnostic and Born agreement without a causal derivation.

---

# 15. Mandatory controls

## 15.1 Noninteracting detector control

For any successful interacting detector model, construct a matched noninteracting baseline by removing intra-detector interactions while preserving the qubit sector, geometry, coupling architecture, and physical scales as closely as possible.

Compare the same observables:

- root/collapsible-state statistics;
- \(\rho_0,\rho_1\);
- \(E_2,E_\infty,E_{\mathrm{harm}},E_{\mathrm{marg}}\);
- finite-\(N\) convergence;
- long-time behavior;
- preferred basis.

The working hypothesis is that intra-detector interactions may be crucial, but this is a hypothesis to test, not an assumption. If the noninteracting model also succeeds, the mechanism claim must be revised rather than the data suppressed.

## 15.2 Mechanism-breaking controls

Once a mechanism is proposed, deliberately modify the Hamiltonian so as to suppress that mechanism while preserving other ingredients as much as possible.

The predicted Born-like behavior must degrade in the manner implied by the mechanism.

If it does not, the proposed mechanism is falsified or incomplete.

---

# 16. Detector-state interpretation

The null vectors \(|D\rangle\) may be arbitrary states in the detector Hilbert space.

For every successful Born-like regime, characterize the physically relevant detector components of the collapsible states using diagnostics appropriate to the discovered mechanism, potentially including:

- energy and energy density;
- entanglement entropy / entanglement structure;
- correlation functions;
- participation ratios;
- localization/delocalization diagnostics;
- overlap with detector eigenstates or simple variational families;
- symmetry sectors;
- collective observables;
- spectral or dynamical diagnostics.

A recognizable physical interpretation of the detector states is required for the high-impact interpretation, even though it is not part of the mathematical definition of a collapsible state.

---

# 17. Disorder and imperfection tests

Do **not** introduce disorder during the initial discovery stage.

After a clean Born-like region has been established, test robustness under weak physically reasonable disorder/imperfections, e.g.

\[
h_i=h+\delta h_i,
\qquad
J_i=J+\delta J_i.
\]

The purpose is to determine whether the phase-like regime survives generic imperfections rather than depending on exact translational symmetry or perfect parameter equality.

---

# 18. Generality program

The first priority is to establish the complete phenomenon in **one physically reasonable local geometry**.

Only after that should the project test generality across:

- the second approved geometry;
- different local interaction structures;
- additional physically motivated local models;
- physically motivated collective/all-to-all models.

Generality substantially strengthens the paper, but the first positive construction should not be delayed by prematurely exploring many unrelated geometries.

A new Hamiltonian family still requires explicit user approval before activation.

---

# 19. Evidence bookkeeping

This specification is intended for an **existing repository**.

Before creating new files or infrastructure, inspect and obey the repository’s existing:

- `AGENTS.md` / agent instructions;
- environment/dependency files;
- tests and numerical conventions;
- HPC scripts;
- wiki/knowledge-base structure;
- `RESEARCH_STATE.md` or equivalent;
- existing evidence/result formats.

Do not create parallel structures when equivalent repository mechanisms already exist.

## 19.1 `RESEARCH_STATE.md`

If the repository already uses `RESEARCH_STATE.md`, treat it as compact **current operational state**, not a historical diary.

It should summarize:

- current best hypothesis;
- current best candidate region;
- what is established;
- what is falsified;
- current verifier status;
- immediate next derivation / numerical experiment.

It should remain short enough for a fresh-context agent to read every iteration.

## 19.2 Wiki / durable knowledge

Use the repository wiki or equivalent for durable scientific knowledge:

- derivations;
- conventions;
- Hamiltonian-family notes;
- mechanism hypotheses;
- convergence studies;
- negative results;
- detector-state interpretation;
- literature;
- referee-style audits.

## 19.3 Evidence ledger

Maintain an append-only evidence ledger, using the repository’s existing equivalent if one exists.

Each meaningful run should record at least:

- date / commit / configuration identifier;
- Hamiltonian family;
- parameters;
- \(N\);
- \(T\);
- coupling/scaling convention;
- result status;
- verifier outputs;
- artifact/result-packet location;
- brief interpretation.

---

# 20. Candidate result packets

Every promising candidate—not only the final winner—must have a standardized result packet sufficient for fresh-context audit.

It should contain, as applicable:

1. exact Hamiltonian and parameter region;
2. \(N,T,g_{\alpha,N}\) or \(g_\alpha\);
3. exact/generalized-eigenvalue root data;
4. kernel multiplicities;
5. reconstructed collapsible states;
6. \(\rho_0,\rho_1\);
7. \(E_2,E_\infty,E_{\mathrm{harm}},E_{\mathrm{marg}}\);
8. estimator-resolution checks;
9. finite-\(N\) convergence;
10. long-time / time-average analysis;
11. preferred-basis estimate and stability;
12. robustness tests completed;
13. detector-state diagnostics;
14. mechanism hypothesis / derivation status;
15. control results;
16. reproducibility metadata.

Failed candidates may use lighter packets but must still be represented in the evidence ledger.

---

# 21. Environment policy

This spec is executed inside an existing theoretical/numerical physics repository.

The research agent must **inherit the repository environment before adding infrastructure**.

Allowed methods are adaptive and may include, when scientifically appropriate:

- exact diagonalization;
- dense or sparse generalized-eigenvalue solvers;
- symbolic algebra;
- perturbation theory;
- asymptotic analysis;
- sparse time evolution;
- tensor-network / many-body methods;
- stochastic or adaptive parameter search;
- HPC/cluster execution;
- additional justified numerical methods.

Rules:

- reuse existing implementations where possible;
- do not duplicate functionality unnecessarily;
- do not add major dependencies without a concrete scientific need;
- preserve repository conventions;
- use existing HPC/job infrastructure when available;
- scientific definitions and verifier criteria remain unchanged when numerical methods change.

APP-specific publication packaging is deferred until after journal acceptance. Ordinary scientific reproducibility is required now.

---

# 22. Verifier architecture

Use a **hybrid frozen verifier**.

## 22.1 Executable/objective layer

Deterministic checks should cover all objectively testable requirements, including:

- exact collapse residuals;
- generalized-eigenvalue / root validation;
- kernel multiplicities;
- normalization;
- distribution construction;
- Born metrics;
- estimator robustness;
- finite-\(N\) convergence;
- long-time analysis;
- parameter-region robustness;
- preferred-axis numerical stability;
- reproducibility / result-packet completeness.

## 22.2 Fresh-context scientific-referee layer

A fresh-context referee agent should independently evaluate questions that cannot honestly be reduced to a scalar threshold, including:

- Is the proposed mechanism actually derived rather than asserted?
- Does the mechanism explain the root statistics?
- Do the mechanism-breaking controls causally support the mechanism?
- Is the preferred-basis explanation convincing?
- Are the detector states physically interpretable?
- Is the successful region genuinely non-fine-tuned?
- Does the evidence support the exact strength of the stated claim?
- Are negative evidence and limitations represented fairly?

The referee should receive the frozen spec and the scientific evidence, not rely on the research agent’s private reasoning.

---

# 23. Hard FAIL conditions

The following are hard failures for the principal claim unless the spec is explicitly revised by the user:

1. Born-deviation metrics converge convincingly to a nonzero asymptotic residual while the claim being tested is exact asymptotic Born behavior.
2. Apparent success exists only at isolated or fine-tuned parameter points/manifolds.
3. No unique stable preferred basis emerges.
4. The successful region is destroyed by arbitrarily small generic perturbations.
5. The proposed mechanism fails its mechanism-breaking control.
6. Claimed finite-size convergence is actually numerical-resolution or estimator dependence.
7. The required \(N\to\infty\) then \(T\to\infty\) ordering is not respected.
8. Weak-coupling claims rely on an uncontrolled perturbative expansion.
9. The research agent changes the verifier, success criteria, or active Hamiltonian family without explicit user approval.
10. Evidence is insufficiently reproducible or selectively omits material negative results.

A hard FAIL for one Hamiltonian tier does not terminate the project; it may unlock the next approved tier. A hard FAIL for the final scientific claim prevents `paper_ready = true`.

---

# 24. `paper_ready` gate

`paper_ready` is a **derived verifier state**, not a research-agent opinion.

It may become `true` only when the following mandatory gates are satisfied:

- exact collapse-like formalism established and validated;
- complete exact matrix-pencil characterization established;
- outcome distributions constructed with correct multiplicity and normalization;
- strong and weak Born criteria evaluated separately;
- multiple complementary Born metrics agree;
- controlled finite-\(N\) convergence demonstrated;
- prescribed \(N\to\infty\) before \(T\to\infty\) structure addressed;
- long-time limit or clearly labeled long-time-average fallback established;
- weak-coupling regime controlled;
- successful behavior occupies a finite robust parameter region;
- unique stable preferred basis identified and explained;
- physical mechanism identified;
- analytical/semi-analytical derivation of Born from the mechanism achieved, or the approved analytic-root-statistics + numerical-final-step fallback is convincingly satisfied;
- noninteracting control completed;
- mechanism-breaking control completed;
- detector states physically characterized;
- at least one convincing local many-body realization established;
- post-discovery disorder/imperfection robustness tested;
- scientific reproducibility and evidence bookkeeping complete;
- no unresolved hard FAIL remains;
- executable verifier passes;
- fresh-context scientific referee passes.

Generality across additional Hamiltonian families is a major strengthening objective after the first successful local realization, but is not silently promoted into a new gate without an approved spec revision.

If the evidence supports only a robust **approximate** Born law rather than exact asymptotic Born behavior, `paper_ready` may become true only for a correspondingly weakened, explicitly stated manuscript claim. The verifier must never promote “close” to “exact.”

Until all relevant gates pass:

\[
\boxed{\texttt{paper\_ready = false}.}
\]

Only after

\[
\boxed{\texttt{paper\_ready = true}}
\]

should a separate manuscript-writing specification be activated.

---

# 25. Research-loop principle

The research loop should behave as:

\[
\boxed{
\text{SPEC}
\rightarrow
\text{hypothesis}
\rightarrow
\text{derivation / experiment}
\rightarrow
\text{evidence}
\rightarrow
\text{frozen verifier}
\rightarrow
\text{RESEARCH\_STATE update}
\rightarrow
\text{next hypothesis}
}
\]

The agent is encouraged to be creative about **how to solve the problem**.

It is not allowed to be creative about **what counts as solving the problem**.

