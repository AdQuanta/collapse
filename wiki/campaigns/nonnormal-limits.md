# Non-Normal Thermodynamic Root Limits

## Objective
Explore whether noncommuting thermodynamic root laws can be derived using singular-value measures or Gaussian operator-moment limits.

## The Scalar Potential $J(x)$
Theorem F establishes a scalar potential equivalent to the polar root measure:
$$ J_{C,A}(x) = \frac{1}{2\pi d} \int_0^{2\pi} \left[ \log|\det(C-e^{x+i\phi}A)| - \log|\det(C-e^{i\phi}A)| \right] d\phi $$
Key properties:
- $J$ uniquely determines the normalized polar root measure, including zero and infinite roots.
- Weak convergence of root measures $\mu_n \Rightarrow \mu$ is equivalent to the uniform convergence of $J_n \to J_\mu$ on compact intervals.
- This provides a convergence criterion for all regular native noncommuting pencils.

## The Gaussian Substitution Failure (Theorem G)
A critical counterexample was constructed using the "Exchange" channel:
$H_N = -\frac{g}{\sqrt{N}}(X_q \sum X_i + Y_q \sum Y_i)$.
- **The Limit**: All bounded continuous singular-value statistics of the propagator blocks converge to those of independent Gaussians.
- **The Native Reality**: At every regular time, the native projective root law is exactly $\delta_0$ for every $N$.
- **The Disagreement**: The Gaussian limiting blocks have a non-trivial continuous polar law.

**Conclusion:** Operator-moment convergence and weak singular-value convergence are **insufficient** to justify substituting a classical Gaussian field into the non-normal root problem.

## Required Control
To correctly derive root limits from singular values, one needs control over the **logarithmic tails** of the singular-value measure (specifically, uniform integrability of $\log s$). The native exchange example proves that this control can fail even when all bounded trace observables converge.

See also: [[asymptotic-obstructions]], [[projective-roots]].
