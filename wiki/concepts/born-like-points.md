# Born Criteria for Collapsible-State Measures

> Sources: `SPEC.md` v1.0, 2026-09-15
> Raw: [Research specification snapshot](../../raw/project-governance/research-spec-v1.md)
> Updated: 2026-09-19

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

Define the azimuthally integrated surface density

$$
\bar\rho_b(\theta)=\int_0^{2\pi}\rho_b(\theta,\phi)\,d\phi,
\qquad
\int_0^\pi\bar\rho_b(\theta)\sin\theta\,d\theta=1.
$$

The weak target is

$$
\bar\rho_0(\theta)=\cos^2\frac\theta2,
\qquad
\bar\rho_1(\theta)=\sin^2\frac\theta2.
$$

If a calculation instead reports the probability density $p_b(\theta)$ with respect to $d\theta$, then

$$
p_b(\theta)=\bar\rho_b(\theta)\sin\theta.
$$

Therefore the Born targets in that convention are $p_0(\theta)=\cos^2(\theta/2)\sin\theta$ and $p_1(\theta)=\sin^2(\theta/2)\sin\theta$. Confusing these two density conventions changes endpoint powers and can create false agreements or false no-go arguments.

## Mandatory diagnostics

Every candidate must report all of the following, with estimator dependence checked:

1. $E_2$, the global spherical RMS error of $p_0$ from $\cos^2(\theta/2)$;
2. $E_\infty$, the worst supported error, evaluated only where the estimator is resolved;
3. $E_{\mathrm{harm}}$, leakage outside the $Y_{00}$ and $Y_{10}$ sectors in the preferred basis;
4. $E_{\mathrm{marg}}$, the weighted polar-marginal error for both $\bar\rho_0$ and $\bar\rho_1$.

Coverage, multiplicities, numerical residuals, binning/KDE/harmonic-reconstruction sensitivity, and both outcome sample sizes accompany these scores. No legacy scalar score or 64-bin gate substitutes for this suite.

## Required limits

The physical order is

$$
N\to\infty\quad\text{before}\quad T\to\infty.
$$

Instantaneous convergence after the large-$N$ limit is preferred. A Cesàro time average is an accepted fallback only if instantaneous convergence fails, and the two claims must never be conflated. Convergence must be demonstrated over a finite open weak-coupling parameter region, not at one fitted point.

## Reflected ratios are secondary

For a single polar density $P(\theta)$, the identity

$$
\frac{P(\theta)}{P(\theta)+P(\pi-\theta)}=\cos^2\frac\theta2
$$

is equivalent, where the denominator is nonzero, to $P(\theta)=(1+\cos\theta)E(\theta)$ with reflection-even $E$. This inversion-balance identity is valid but is not the SPEC strong or weak criterion: it neither constructs the two independently normalized outcome measures nor tests full-sphere support. It may be reported only as a derived diagnostic.

## Interpretation boundary

Root counting describes propagator geometry. It is not yet an operational probability law or an ontology. A successful paper claim also needs a physical preparation/selection interpretation and a mechanism linking many-body structure to the two root measures.

## Status

All historical Born-like labels are uncredited under v1.0 until the dual roots, multiplicity weights, both measures, mandatory metrics, preferred basis, ordered limits, robustness region, and controls are rerun through the frozen verifier. `paper_ready = false`.

See also: [[projective-roots]], [[coverage-gates]], [[haar-baseline]], [[research-specification-v1]].
