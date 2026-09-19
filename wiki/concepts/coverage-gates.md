# Coverage Gates & Polar Acceptance

## The Concept of Coverage
In the `collapse` project, "coverage" refers to whether the set of projective roots provides enough support on the Bloch sphere to define a continuous-like distribution.

## The Finite-Bin Gate
Because finite $N$ produces a discrete measure, earlier studies used a **bin-based coverage diagnostic**:
- The polar interval $[0, \pi]$ is divided into $B$ uniform bins (typically $B=64$ or $B=100$).
- **Full Coverage**: A result "has coverage" if every bin contains at least one root.
- **Failure**: If any bin is empty, the global RMSE and maximum error are reported as `null` (undefined), as the distribution is not "full-sphere."

## Historical Polar Acceptance Gate (Sept 11 Study)
For the constructive family study, the following strict gate was adopted. It is not a current `SPEC.md` v1.0 paper-readiness criterion:
1. **Full 64-bin coverage**.
2. **Bin-center R RMSE $\le 0.05$** against $\cos^2(\theta/2)$.
3. **Max Born moment residual $\le 0.05$** over the first eight relations.

## Why this is Necessary
Without coverage gates, a "Born-like" score could be artificially high if roots are clustered in a few favorable bins, even if huge gaps exist elsewhere. Coverage ensures that the Born-like behavior is a global property of the root distribution.

## Current SPEC v1.0 Replacement

No fixed number of occupied polar bins is a paper-readiness gate. At finite (N), support is handled inside the density estimator: (E_\infty) is evaluated only where support is adequate, while binning, KDE, harmonic reconstruction, or any alternative estimator must be varied to expose estimator dependence. Empty regions cannot be hidden, but neither may an arbitrary bin edge redefine success.

Coverage is now assessed together with the complete sphere-level evidence:

- separately normalized multiplicity-weighted measures \(\rho_0\) and \(\rho_1\);
- strong-Born errors \(E_2\), supported \(E_\infty\), and \(E_{\mathrm{harm}}\), including unwanted \(m\ne0\) structure;
- the separately reported weak marginal error \(E_{\mathrm{marg}}\);
- stability under estimator resolution and reasonable estimator choices;
- a systematic sequence of increasing \(N\), followed by instantaneous long-time convergence at large \(N\), or a clearly labeled long-time-average fallback;
- a unique preferred axis, stable up to reversal, rather than a favorable preselected polar cut.

The historical 64-bin and moment thresholds may be reproduced as diagnostics, but they cannot certify convergence, an open parameter region, or `paper_ready`.

See also: [[born-like-points]], [[production-pipeline]].
