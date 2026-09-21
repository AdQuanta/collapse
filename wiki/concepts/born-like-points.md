# Born Criteria for Collapsible-State Measures

> Sources: `SPEC.md` v1.0, 2026-09-15; User correction, 2026-09-19; Repository execution, 2026-09-21
> Raw: [Research specification snapshot](../../raw/project-governance/research-spec-v1.md); [Weak Born criterion correction](../../raw/project-governance/2026-09-19-weak-born-criterion-correction.md); [Outcome antipodality verification](../../raw/campaigns/2026-09-21-outcome-antipodality-verification.md)
> Updated: 2026-09-21

The specification defines two separately normalized outcome measures. A single reflected histogram or a visually close finite-size curve is not the target.

## Conditional outcome measures

For outcome $b\in\{0,1\}$, let $\rho_b(\Omega)=P(\Omega\mid b)$ and normalize

$$
\int_{S^2}\rho_b(\Omega)\,d\Omega=1.
$$

With equal outcome priors, define

$$
p_0(\Omega)=\frac{\rho_0(\Omega)}{\rho_0(\Omega)+\rho_1(\Omega)}.
$$

The strong Born criterion in the preferred basis is

$$
p_0(\Omega)=\cos^2\frac\theta2,
\qquad
p_1(\Omega)=\sin^2\frac\theta2.
$$

This is a full-sphere statement. Azimuthal structure and unsupported regions cannot be hidden by polar binning.

## Weak polar criterion

Define the probability density of the polar angle with respect to $d\theta$,

$$
\rho_b^{(\theta)}(\theta)
=\sin\theta\int_0^{2\pi}\rho_b(\theta,\phi)\,d\phi,
\qquad
\int_0^\pi\rho_b^{(\theta)}(\theta)\,d\theta=1.
$$

With equal outcome priors, first form the ratio after marginalizing over azimuth,

$$
p_0^{\mathrm{weak}}(\theta)
=\frac{\rho_0^{(\theta)}(\theta)}
{\rho_0^{(\theta)}(\theta)+\rho_1^{(\theta)}(\theta)},
\qquad
p_1^{\mathrm{weak}}(\theta)=1-p_0^{\mathrm{weak}}(\theta).
$$

The weak Born criterion is

$$
p_0^{\mathrm{weak}}(\theta)=\cos^2\frac\theta2,
\qquad
p_1^{\mathrm{weak}}(\theta)=\sin^2\frac\theta2,
$$

where the denominator is nonzero. For $0<\theta<\pi$, the common Jacobian $\sin\theta$ cancels from this ratio, so it can equivalently be evaluated from the azimuthally integrated surface densities. The criterion does not prescribe either outcome marginal separately: the two marginals may share a nontrivial polar envelope. It is weaker than the full-sphere criterion because marginalization can hide azimuthal deviations or anisotropies.

## Mandatory diagnostics

Every candidate must report all of the following, with estimator dependence checked:

1. $E_2$, the global spherical RMS error of $p_0$ from $\cos^2(\theta/2)$;
2. $E_\infty$, the worst supported error, evaluated only where the estimator is resolved;
3. $E_{\mathrm{harm}}$, leakage outside the $Y_{00}$ and $Y_{10}$ sectors in the preferred basis;
4. $E_{\mathrm{marg}}$, the normalized, $\sin\theta$-weighted error of the weak marginal ratios on their supported polar domain.

Coverage, multiplicities, numerical residuals, binning/KDE/harmonic-reconstruction sensitivity, and both outcome sample sizes accompany these scores. No legacy scalar score or 64-bin gate substitutes for this suite.

## Required limits

The physical order is

$$
N\to\infty\quad\text{before}\quad T\to\infty.
$$

Instantaneous convergence after the large-$N$ limit is preferred. A Cesàro time average is an accepted fallback only if instantaneous convergence fails, and the two claims must never be conflated. Convergence must be demonstrated over a finite open weak-coupling parameter region, not at one fitted point.

## Reflected ratios are secondary

For a single polar density $P(\theta)$, the reflected ratio

$$
\frac{P(\theta)}{P(\theta)+P(\pi-\theta)}=\cos^2\frac\theta2
$$

is equivalent, where the denominator is nonzero, to $P(\theta)=(1+\cos\theta)E(\theta)$ with reflection-even $E$. It equals the SPEC weak ratio only when the two independently normalized outcome marginals obey $\rho_1^{(\theta)}(\theta)=\rho_0^{(\theta)}(\pi-\theta)$. Unitarity forces exactly that, because the two outcome measures are antipodal ([[outcome-antipodality]]), so a single reflected polar histogram does construct the weak ratio. The search scripts histogram the *fixed-input* pencil rather than an outcome pencil, which supplies the same polar law whenever the model is time-reversal invariant ([[fixed-input-outcome-equivalence]]). It still constructs nothing about the strong full-sphere criterion, which needs the joint $(\theta,\phi)$ density and its antipodal image.

## Interpretation boundary

Root counting describes propagator geometry. It is not yet an operational probability law or an ontology. A successful paper claim also needs a physical preparation/selection interpretation and a mechanism linking many-body structure to the two root measures.

## Status

All historical Born-like labels are uncredited under v1.0 until the dual roots, multiplicity weights, both measures, mandatory metrics, preferred basis, ordered limits, robustness region, and controls are rerun through the frozen verifier. `paper_ready = false`.

See also: [[projective-roots]], [[outcome-antipodality]], [[fixed-input-outcome-equivalence]], [[coverage-gates]], [[haar-baseline]], [[research-specification-v1]].
