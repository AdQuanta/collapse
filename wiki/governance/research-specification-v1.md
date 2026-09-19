# Research Specification v1.0

> Sources: Repository research specification, Unknown; User instruction, 2026-09-15
> Raw: [Research specification v1.0](../../raw/project-governance/research-spec-v1.md); [Paper readiness reset](../../raw/project-governance/2026-09-15-paper-readiness-reset.md)
> Updated: 2026-09-15

## Authority

`SPEC.md` v1.0 is the controlling research contract. It supersedes prior wiki goals, acceptance gates, active-family declarations, verifier interpretations, and manuscript-readiness judgments wherever they conflict. Historical results remain part of the record, but they do not change what counts as success.

The specification and its verifier are frozen once a run begins. The research process may adapt search and numerical methods inside an approved Hamiltonian family, but changing the success definition, activating a qualitatively new family, or revising the verifier requires explicit user approval and versioned documentation.

## Scientific target

The project tests whether a closed qubit plus many-body detector, evolving unitarily at a fixed externally specified time, has exact product inputs that evolve to definite qubit outcomes and whose initial-qubit distribution approaches Born statistics in a stable, non-fine-tuned weak-coupling region.

For qubit-first block ordering,

$$
U(T)=\begin{pmatrix}U_{00}&U_{01}\\U_{10}&U_{11}\end{pmatrix},
$$

the exact collapsibility conditions are

$$
(U_{10}+\lambda U_{11})|D\rangle=0
$$

for outcome 0 and

$$
(U_{00}+\lambda U_{01})|D\rangle=0
$$

for outcome 1. Finite, infinite, degenerate, and singular-pencil cases must be treated correctly. Each root is weighted by the dimension of its kernel; numerical fidelity alone does not redefine exact collapse.

## Born targets and diagnostics

Each outcome measure is normalized separately and interpreted as $P(\Omega\mid b)$, with equal outcome priors. The strong target is

$$
p_0(\Omega)=\frac{\rho_0(\Omega)}{\rho_0(\Omega)+\rho_1(\Omega)}
=\cos^2\frac{\theta}{2},
$$

while the weak target concerns the azimuthally integrated outcome densities. Passing the weak target does not imply passing the strong one.

No single scalar certifies success. The required diagnostic suite includes global RMS error $E_2$, supported worst-case error $E_\infty$, spherical-harmonic leakage $E_{\mathrm{harm}}$, weak marginal error $E_{\mathrm{marg}}$, and estimator-robustness checks. Earlier fixed-bin thresholds remain useful historical diagnostics only; they are not the specification's success gate.

## Limits and weak coupling

The prescribed order is thermodynamic first and long-time second:

$$
N\to\infty\quad\text{before}\quad T\to\infty.
$$

Actual long-time convergence is preferred. A clearly labeled long-time average is an accepted fallback only if the instantaneous distribution does not converge. Finite-size evidence must show a systematic size sequence, controlled resolution error, stable extrapolation, and convergence across a parameter region rather than at one optimized point.

Weak coupling must be controlled by a relevant dimensionless ratio, with resonant or degenerate sectors treated appropriately. The effect must occupy an open window at nonzero coupling; the decoupled point is not evidence for the target phenomenon.

## Approved search space

The initial approved geometries are:

- a one-dimensional periodic detector ring with collective qubit coupling;
- a one-dimensional endpoint chain with local qubit coupling.

The search proceeds through minimal interaction, field, and coupling tiers. The coupling hierarchy is $ZZ$, then XY type, then XXZ, then XYZ. Cross-axis qubit-detector terms are outside the initial approved space. Next-nearest-neighbor detector terms are also excluded initially and may be proposed only after systematic exploration of simpler nearest-neighbor families.

For collective ring coupling, the conservative operator-norm baseline is $g_{\alpha,N}\propto 1/N$. Another axis-dependent scaling must be justified from detector fluctuations or an identified physical mechanism. Endpoint coupling is generically $O(1)$ in detector size while remaining perturbatively weak.

## What a positive result must explain

A successful regime must occupy a finite open parameter region and possess a unique stable preferred measurement axis, up to swapping its orientation. It must supply a causal mechanism from a many-body property through propagator-block and root statistics to the Born profile.

The required controls are a matched noninteracting detector and a mechanism-breaking intervention. Successful detector null vectors must also receive a physical characterization using relevant energy, entanglement, correlation, participation, localization, symmetry, collective, spectral, or dynamical diagnostics.

Disorder is not part of initial discovery. It becomes a robustness test only after a clean Born-like region has been established. The first priority is one convincing local geometry; generality is a later strengthening program.

## Evidence, verifier, and manuscript gate

The memory model has three roles:

1. `RESEARCH_STATE.md` is the compact current operational handoff.
2. The wiki stores durable derivations, conventions, mechanisms, convergence studies, negative results, literature, and audits.
3. An append-only evidence ledger records every meaningful run with configuration, parameters, sizes, times, scaling, status, verifier outputs, artifacts, and interpretation.

Every promising candidate requires a reproducible result packet. Objective checks belong in an executable frozen verifier; mechanism, basis selection, detector interpretation, robustness, claim strength, and treatment of negative evidence require a fresh-context referee audit.

`paper_ready` is a derived verifier state. It remains false until every applicable gate passes and no hard failure remains. By explicit user instruction, every gate begins `INCOMPLETE` under v1.0 and all existing results require fresh verification; no earlier certification is inherited. Existing manuscript drafts and publication plans are therefore historical or preparatory material, not the active work product under v1.0.

## See Also

- [Research control center](research-control-center.md)
- [Paper readiness ledger](paper-readiness-ledger.md)
- [Exact projective roots](../concepts/projective-roots.md)
- [Born-like point process](../concepts/born-like-points.md)
- [Scientific contract](../methods/scientific-contract.md)
- [Production pipeline](../methods/production-pipeline.md)

