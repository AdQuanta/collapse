# Born-like Special-State Point Process

## Definition
A Hamiltonian is considered **Born-like** if the distribution of its projective disentanglement roots on the Bloch sphere approximates the qubit Born rule under projective measurement.

---

## The Reflected-Density Ratio $R(\theta)$

For an outcome-labelled special-state point cloud on the Bloch sphere, the primary polar observable is the **reflected-density ratio**:
$$
R(\theta) = \frac{P(\theta)}{P(\theta) + P(\pi-\theta)}.
$$
The ideal target Born curve is:
$$
R_{\text{Born}}(\theta) = \cos^2(\theta/2) = \frac{1+\cos\theta}{2}.
$$

---

## Fundamental Mathematical Property: $P(\theta)$ vs. $R(\theta)$

> [!IMPORTANT]
> **$P(\theta)$ does NOT require a cosine shape for $R(\theta)$ to equal $\cos^2(\theta/2)$!**
> 
> A common misconception is that obtaining $R(\theta) = \cos^2(\theta/2)$ requires the raw density $P(\theta)$ to be the pure cosine profile $\frac{1+\cos\theta}{\pi}$.
> 
> **Theorem (Exact Inversion Balance):**
> $$
> R(\theta) = \cos^2(\theta/2) \iff P(\theta) = (1+\cos\theta)E(\theta),
> $$
> where $E(\theta)$ is **any reflection-even function**, satisfying $E(\pi-\theta) = E(\theta)$ almost everywhere on $[0, \pi]$.

### Mathematical Proof
If $P(\theta) = (1+\cos\theta)E(\theta)$ with $E(\pi-\theta) = E(\theta)$:
1. The reflected density is:
   $$
   P(\pi-\theta) = [1+\cos(\pi-\theta)]E(\pi-\theta) = (1-\cos\theta)E(\theta).
   $$
2. The denominator is:
   $$
   P(\theta) + P(\pi-\theta) = (1+\cos\theta)E(\theta) + (1-\cos\theta)E(\theta) = 2E(\theta).
   $$
3. Taking the ratio:
   $$
   R(\theta) = \frac{(1+\cos\theta)E(\theta)}{2E(\theta)} = \frac{1+\cos\theta}{2} = \cos^2(\theta/2).
   $$
The even envelope $E(\theta)$ cancels out completely!

### Physical & Numerical Consequences
- **Arbitrary Even Structure:** $E(\theta)$ can have complicated multi-peaked shapes, thermal backgrounds, or band-edge singularities. The raw root density $P(\theta)$ can have violent oscillations, but as long as the antipodal ratio satisfies $P(\theta)/P(\pi-\theta) = \cot^2(\theta/2)$, the response $R(\theta)$ is strictly Born.
- **Diagnostic Protocol:** Because $R(\theta)$ does not uniquely fix $P(\theta)$, production diagnostic reports (see `research_reports/BORN_POSITIVE_MULTICHANNEL.md` and `reports/born_positive_diagnostics_2026-09-12/`) always display three panels together: $P(\theta)$, reflected $P(\pi-\theta)$, and $R(\theta)$ overlaid on $\cos^2(\theta/2)$.
- **Radial Reciprocity:** In terms of the root radius $r = \tan(\theta/2)$, this balance is equivalent to the tilted radial density satisfying $q(1/r) = r^4 q(r)$, or invariance of the tilted measure $r Q(dr)$ under inversion $r \mapsto 1/r$.

---

## Spherical Geometry & Outcome Asymmetry (Draft §4)

Across the entire Bloch sphere $\Omega = (\theta, \phi)$, let $\rho_0(\Omega)$ and $\rho_1(\Omega)$ be the local densities of special states collapsing to outcomes $|0\rangle$ and $|1\rangle$.
Define the **outcome asymmetry**:
$$
a(\Omega) = \frac{\rho_0(\Omega) - \rho_1(\Omega)}{\rho_0(\Omega) + \rho_1(\Omega)}.
$$
- For an ideal projective measurement along unit vector $\hat{n}$:
  $$
  a(\Omega) = \hat{n} \cdot \vec{r}(\Omega),
  $$
  which is a **pure dipolar ($\ell = 1$) spherical harmonic**.
- For a Haar-random unitary baseline, $a(\Omega) = 0$ everywhere (pure $\ell=0$ monopole, see [[haar-baseline]]).
- Higher odd harmonic leakage ($\ell = 3, 5, \dots$) measures departures from the ideal Born dipole.

---

## Density vs. Measure Zero & Covering Radius (Draft §4.1)

For an $n$-qubit detector, the special-state set has finite cardinality $d = 2^n$ and is strictly of Lebesgue measure zero on $S^2$.
- As $d \to \infty$, the points can become **dense** on the sphere.
- The **covering radius** $\delta_n$ is the largest geodesic distance from any point on $S^2$ to the nearest collapsible state.
- For a roughly uniform point process, $\delta_n \sim \sqrt{\log d / d} \sim \sqrt{n} 2^{-n/2}$, shrinking exponentially with detector qubit count.

---

## Stochastic Route: Martingales & Gambler's Ruin (Draft §9, App. D)

How could microscopic dynamics produce Born hitting probabilities?
1. Let $Z_t = \langle \sigma_z \rangle_t$ be a coarse-grained coordinate along a collapse-compatible trajectory with absorbing boundaries at $Z = \pm 1$.
2. If the microscopic dynamics generates a **martingale** (zero drift, $\mathcal{L}z = 0$), the optional stopping theorem gives:
   $$
   \mathbb{E}[Z_\tau] = Z_0 \implies (+1)P(+1) + (-1)P(-1) = z_0.
   $$
3. Together with $P(+1) + P(-1) = 1$, this uniquely yields:
   $$
   P(+1) = \frac{1+z_0}{2} = \cos^2(\theta_0/2), \quad P(-1) = \frac{1-z_0}{2} = \sin^2(\theta_0/2).
   $$
This gambler's ruin mechanism provides a dynamical bridge from zero drift to Born statistics without assuming Gleason's noncontextual event algebra.

---

## Acceptance Criteria (Declared September 11 Gate)

For finite-$N$ benchmarking, the project enforces a declared 64-bin acceptance gate:
1. **Full Coverage:** Complete occupation of all 64 uniform half-open bins across $[0, \pi]$.
2. **Ratio RMSE:** Bin-center $R$ root-mean-square error $\le 0.05$ against $\cos^2(\theta/2)$.
3. **Born Moment Residuals:** Maximal absolute residual $\le 0.05$ across the first eight cosine-moment relations:
   $$
   d_m = |2a_{2m+1} - a_{2m} - a_{2m+2}| \le 0.05, \quad m = 0, \dots, 7,
   $$
   where $a_n = \frac{1}{d}\sum_j \cos(n\theta_j)$.

---

## Key Physical Boundary: Roots vs. Operational Probabilities

> [!WARNING]
> **Root counting is not yet an operational measurement probability.**
> Counting algebraic roots equally is a mathematical diagnostic of the propagator's geometry. A complete physical theory of measurement requires a preparation/selection measure over detector microstates, ready states, and interaction times explaining why nature samples these roots in proportion to their abundance.

See also: [[projective-roots]], [[haar-baseline]], [[theorem-targets]], [[coverage-gates]], [[foundational-draft-aug2026]].
