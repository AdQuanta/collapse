# Figure Plan (4-Figure PRL/NatPhys Format)

This compressed sequence is designed for a high-impact letter. Each figure serves as a decisive pillar of the argument: *Unitary dynamics produce a sparse yet dense set of collapsible states that follow a Born-like distribution.*

## Figure Sequence

### Fig 1: The Collapsible State Framework (Concept)
- **Takeaway**: Projective roots of the relative propagator $W=A^{-1}C$ define a discrete set of "collapsible states" on the Bloch sphere.
- **Panels**:
    - (a) System schematic: Qubit $\otimes$ Detector.
    - (b) The mapping: $U(t)$ blocks $\to$ Projective pencil $\to$ Roots $\lambda$.
    - (c) Geometric projection: $\lambda \to$ points on the Bloch sphere.
- **Narrative**: Establishes the fundamental object of the paper.

### Fig 2: Emergence of Born Statistics (Proof)
- **Takeaway**: In complex interacting detectors, the collapsible states follow the Born rule $\cos^2(\theta/2)$.
- **Panels**:
    - (a) The Born Profile: Root distribution histogram vs. Born curve for $N=17$ interacting rings.
    - (b) Scaling: Ratio RMSE and Moment Residuals as a function of $N$, showing convergence.
    - (c) Control Contrast: Comparison with Haar-random (isotropic) and QND (poles).
- **Narrative**: Provides the primary numerical evidence.

### Fig 3: The Sparsity-Density Paradox (Mechanism)
- **Takeaway**: The set of collapsible states is sparse relative to the Hilbert space but becomes dense on the Bloch sphere as $N \to \infty$.
- **Panels**:
    - (a) Visual progression: Root points on the sphere for $N=5, 10, 15$.
    - (b) Coverage Scaling: Fraction of sphere covered vs. $N$.
    - (c) Measure Convergence: Empirical $R(\theta)$ approaching the Born limit as the "graininess" vanishes.
- **Narrative**: Explains how a discrete algebraic set yields a continuous probability measure.

### Fig 4: Theoretical Certification and Limits (Anchor)
- **Takeaway**: Born geometry is analytically certifiable for specific classes but is obstructed by rigorous no-gos in others.
- **Panels**:
    - (a) **Existence**: The "Constructive Family" root distribution vs. the Born curve.
    - (b) **Obstruction I**: The detuning-interval no-go (RMSE vs. detuning $b$).
    - (c) **Obstruction II**: The non-normal limit (Native Exchange vs. Gaussian substitution).
- **Narrative**: Completes the scientific loop: we can design it, and we know exactly where it fails.
