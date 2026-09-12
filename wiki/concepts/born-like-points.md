# Born-like Special-State Point Process

## Definition
A Hamiltonian is considered "Born-like" if the distribution of its projective disentanglement roots on the Bloch sphere approximates the qubit Born rule.

## The Born Curve
The primary scalar diagnostic is the reflected-density ratio:
$$ R(\theta) = \frac{P(\theta)}{P(\theta)+P(\pi-\theta)} $$
The target Born curve is $ R_{\text{Born}}(\theta) = \cos^2(\theta/2) $.

## Acceptance Criteria
As of 2026-09-11, the "universal-family" task uses a finite-resolution gate:
1. Full reflected polar coverage in 64 uniform bins.
2. Bin-center R RMSE $\le 0.05$ against $\cos^2(\theta/2)$.
3. Maximal absolute Born moment residual $\le 0.05$ over the first eight relations.

## Key Limitations
**Root geometry is not yet an operational probability measure.** Counting algebraic roots equally is a mathematical construction. A physical derivation requires a preparation/selection measure over detector microstates, root multiplicities, and times.

See also: [[projective-roots]], [[spectral-statistics]].
