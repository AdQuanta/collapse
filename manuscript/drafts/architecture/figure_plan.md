# Four-Figure Manuscript Architecture (PRL / NatPhys Format)

This figure plan establishes the four empirical and theoretical pillars of the Letter. In accordance with the **Scientific Writing Skill**, the figures form an autonomous, figure-first narrative: an expert skimming only the visual plates and captions recovers the complete, rigorous scientific argument.

---

## The Four Pillars

```
+---------------------------------------------------------------------------------+
| Fig. 1 CONCEPT: The Projective Pencil & Exact Antipodal Duality                 |
| System schematic | Block partition | Roots on S^2 | Exact minor antipodality    |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
| Fig. 2 PROOF: Full-Sphere Born Dipole in an Interacting Spin Ring                |
| Equal-area 2D map | Dipole fit (98.2% ell=1 power) | Haar null contrast         |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
| Fig. 3 ROBUSTNESS: Finite-Size Scaling & Harmonic Suppression                   |
| S_B monotonic rise (0.192 -> 0.807) | Unit coverage | Azimuthal gate (|c2|<=0.25) |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
| Fig. 4 BOUNDARIES: Analytic Certification & Rigorous No-Gos                     |
| Commuting-X constructive family | Detuning interval no-go | Non-normal breakdown |
+---------------------------------------------------------------------------------+
```

---

## Detailed Figure Specifications

### Figure 1: The Projective Pencil Framework & Antipodal Duality (Concept)
- **Scientific Role**: Concept & Platform.
- **Dominant Scientific Idea**: Definite-outcome product inputs under unitary evolution are projective matrix-pencil roots whose outcome multisets are exact Bloch antipodes.
- **Panels**:
  - **(a) Physical System**: Qubit coupled to a many-body detector $\mathcal{H}_D$ ($d=2^N$) via Hamiltonian $H$.
  - **(b) Pencil Engine**: Block partitioning $U(t) = \begin{pmatrix} A & B \\ C & D \end{pmatrix} \to$ forward pole pencils $(\alpha C + \beta D)\eta = 0$ and $(\alpha A + \beta B)\eta = 0$.
  - **(c) Bloch Projection**: Complex pencil roots $z = \beta/\alpha \to$ polar angles $\theta = 2\arctan |z|$, azimuthal phases $\phi = \arg z$.
  - **(d) Antipodal Minor Duality**: Visual demonstration that outcome-$0$ roots $\Omega_j^{(0)}$ and outcome-$1$ roots $\Omega_j^{(1)}$ satisfy $\Omega_j^{(1)} = -\Omega_j^{(0)}$.
- **Dominant Visual**: Panel (d) showing the exact antipodal pairing on the Bloch sphere.
- **Instant Comparison**: Generic independent root clouds vs. the exact antipodal pairing forced by unitarity.
- **Quantitative Anchor**: Exactly $d = 2^N$ projective roots counted with algebraic multiplicity.

---

### Figure 2: Emergence of Full-Sphere Born Dipoles in Many-Body Rings (Proof)
- **Scientific Role**: Decisive Observation & Primary Proof.
- **Dominant Scientific Idea**: Clean interacting spin rings generate a full-sphere dipolar root asymmetry matching the Born rule, distinct from the uniform Haar null.
- **Panels**:
  - **(a) Full-Sphere Asymmetry Map**: Equal-area projection ($36\times18$ bins) of asymmetry $a(\phi, \mu)$ at $N=16, t=10^4\,\hbar/J$.
  - **(b) Polar Profile vs. Born Dipole**: Polar slice $R(\theta)$ compared against the ideal Born curve $\cos^2(\theta/2)$.
  - **(c) Control Contrast**: Side-by-side comparison of the matched spin ring against the flat Haar-scrambling null ($S_{\mathrm{B}} = 0$) and a strict-QND localized pole distribution.
- **Dominant Visual**: Panel (a) the high-resolution 2D full-sphere dipole map.
- **Instant Comparison**: The pronounced dipolar gradient of the interacting ring vs. the featureless flat intensity of the Haar ensemble.
- **Quantitative Anchor**: Count-weighted Born residual of $0.089$; correlation with $\mu = \cos\theta$ of $0.971$; dipole mode carries $98.2\%$ of resolved odd multipole power.

---

### Figure 3: Finite-Size Scaling & Systematic Harmonic Suppression (Robustness)
- **Scientific Role**: Mechanism, Scaling & Controls.
- **Dominant Scientific Idea**: The Born dipolar profile converges monotonically with system size while maintaining unit full-sphere coverage and suppressing azimuthal warping.
- **Panels**:
  - **(a) Polar Score Scaling**: Median and range of $S_{\mathrm{B}}$ across four time decades ($t=10^3\text{--}10^6\,\hbar/J$) as a function of $N=11\text{--}16$, contrasted with the Haar baseline.
  - **(b) Full-Sphere Coverage**: Fraction of occupied equal-area bins demonstrating unit coverage ($1.0$) across all $N \ge 11$.
  - **(c) Azimuthal Harmonic Gate**: Second-harmonic distortion $|c_2|$ across sizes, showing compliance with the gate $|c_2| \le 0.25$.
- **Dominant Visual**: Panel (a) the monotonic upward scaling curve of median $S_{\mathrm{B}}$.
- **Instant Comparison**: Monotonic rise of structured ring scores ($0.192 \to 0.807$) contrasted against the flat horizontal Haar intensity baseline ($S_{\mathrm{B}} = 0$).
- **Quantitative Anchor**: Monotonic increase of median $S_{\mathrm{B}}$: $N=11$ ($0.192$), $N=12$ ($0.341$), $N=13$ ($0.495$), $N=14$ ($0.638$), $N=15$ ($0.742$), $N=16$ ($0.807$).

---

### Figure 4: Theoretical Certification & Non-Normal Boundaries (Boundaries)
- **Scientific Role**: Theoretical Boundaries, Certification & No-Gos.
- **Dominant Scientific Idea**: Born geometry is analytically certifiable in constructive commuting-X families but is bounded by rigorous no-gos in simple commuting fields and non-normal limits.
- **Panels**:
  - **(a) Constructive Family Certification**: Folded energy spectrum $\sum_i s_i g_i$ analytically satisfying the finite-resolution gate $C_{\mathrm{B}}$.
  - **(b) Detuning Interval No-Go**: Theorem H demonstration showing the unavoidable breakdown of Born balance across open detuning intervals in commuting vector fields.
  - **(c) Non-Normal Counterexample**: Native exchange channel root law ($\delta_0$) contrasted with the incorrect Gaussian-substitution prediction, revealing the breakdown of singular-value shortcuts.
- **Dominant Visual**: Panel (a) the exact analytical recovery of the Born profile in the constructive family.
- **Instant Comparison**: Analytical success of the structured constructive class vs. the rigorous failure of naive commuting and Gaussian approximations.
- **Quantitative Anchor**: Proof of Theorem H across detuning intervals; divergence of logarithmic singular-value tails.
