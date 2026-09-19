# Weak Born Criterion Correction

> Source: User instruction in the active Codex conversation
> Collected: 2026-09-19
> Published: 2026-09-19

### Weak Born criterion

For outcome \(b\in\{0,1\}\), let \(\rho_b(\theta,\phi)=P(\Omega\mid b)\) be normalized on the Bloch sphere,

\[
\int_{S^2}\rho_b(\Omega)\,d\Omega=1.
\]

Define the polar marginal probability density

\[
\rho_b^{(\theta)}(\theta)
=
\sin\theta\int_0^{2\pi}\rho_b(\theta,\phi)\,d\phi,
\qquad
\int_0^\pi \rho_b^{(\theta)}(\theta)\,d\theta=1.
\]

With equal outcome priors, define

\[
p_0^{\mathrm{weak}}(\theta)
=
\frac{\rho_0^{(\theta)}(\theta)}
{\rho_0^{(\theta)}(\theta)+\rho_1^{(\theta)}(\theta)},
\qquad
p_1^{\mathrm{weak}}(\theta)=1-p_0^{\mathrm{weak}}(\theta).
\]

The **weak Born criterion** in the preferred basis is

\[
p_0^{\mathrm{weak}}(\theta)=\cos^2\frac{\theta}{2},
\qquad
p_1^{\mathrm{weak}}(\theta)=\sin^2\frac{\theta}{2},
\]

for all \(\theta\) where the denominator is nonzero.

Unlike the strong Born criterion, this condition is imposed only after marginalizing over the azimuth \(\phi\). Therefore azimuthal deviations or anisotropies may be hidden by the marginalization.
