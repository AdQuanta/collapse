# Spectral Statistics & Born Geometry

## Overview
A central hypothesis in the early development of the `unitary-collapse` program (Draft §7, App. E) was that the emergence of Born-like root statistics might be directly organized by the energy-level statistics of the detector Hamiltonian—specifically, the crossover between **integrable Poisson statistics** and **chaotic Wigner–Dyson level repulsion**.

---

## The Consecutive-Gap Ratio $\langle \tilde{r} \rangle$

To avoid the ambiguities of spectral unfolding, level statistics are quantified using the symmetrized consecutive-gap ratio (Oganesyan & Huse 2007; Atas et al. 2013):
$$
\tilde{r}_n = \frac{\min(\delta_n, \delta_{n+1})}{\max(\delta_n, \delta_{n+1})}, \quad \delta_n = E_{n+1} - E_n.
$$
Standard theoretical benchmarks:
- **Poisson (Integrable / Localized):** $\langle \tilde{r} \rangle_{\text{Poisson}} = 2\ln 2 - 1 \approx 0.3863$.
- **GOE (Chaotic / Orthogonal):** $\langle \tilde{r} \rangle_{\text{GOE}} \approx 0.5307$.
- **GUE (Unitary / Time-Reversal Broken):** $\langle \tilde{r} \rangle_{\text{GUE}} \approx 0.5996$.

---

## The Historical August 12 Hypothesis (Draft §7)

The foundational draft conjectured that Born-like behavior occupies an **intermediate structural regime**:
1. **Sufficient Complexity & Dephasing:** Enough level mixing and entanglement growth to create effectively irreversible information flow away from the qubit.
2. **Preserved Measurement Axis:** Sufficient conserved or quasi-conserved structure to prevent the pencil from becoming rotationally isotropic (which produces the uniform Haar baseline, see [[haar-baseline]]).
3. **Draft Prediction:** A scan tuning an integrability-breaking parameter (e.g., transverse field $h_x$ in an Ising detector) would show a direct correlation between the gap ratio $\langle \tilde{r} \rangle$ and the Born distance $\Delta_B$.

---

## Subsequent Findings: Detector Level Statistics Are Not Sufficient (Late August 2026)

Rigorous testing of this hypothesis on the Technion Zeus cluster with symmetry-resolved spectra ($N = 17$, `RESEARCH_STATE.md` §10b) decisively refined this picture:

### 1. Detector Level Statistics Alone Do Not Determine Born Similarity
- **Nearest-Neighbor Ring Scan (20 cases):** All resolved sectors exhibited Poisson-like statistics ($\langle \tilde{r} \rangle \approx 0.384$), yet the polar Born score $S_{\text{born}}$ spanned nearly the entire possible range: from **$0.020$ to $0.938$**. The within-family Spearman rank correlation was slightly negative ($\rho = -0.125, p = 0.60$).
- **Second-Neighbor Ring Scan (20 cases):** Stronger Born similarity correlated with GOE-like statistics ($\rho = +0.696, p = 6.5 \times 10^{-4}$), but pooled across both families the correlation was weak ($\rho = +0.212, p = 0.189$).
- **Decisive Central-Field Control:** Holding the detector completely fixed while varying only the central qubit field $h_{z0}$ caused $S_{\text{born}}$ to sweep from $\approx 0.015$ to $\approx 0.932$ on a Poisson detector, and from $\approx 0.055$ to $\approx 0.930$ on a GOE detector. The detector spectra were identical throughout each scan.

### 2. Confounding by the Central-$X$ No-Go (August 27, 2026, §14a)
The early observation that "adding a transverse field $h_x$ destroys Born-like behavior" was found to be confounded by an exact symmetry:
- In central-$X$-only models with $h_{z0} = h_{x0} = 0$, the Hamiltonian commutes with $X_Q$, forcing all roots onto the 1D $y\text{-}z$ great circle ($\text{Re}(\lambda) = 0$).
- Taking the qubit gap $\Delta_Q = h_{z0} \to 0$ does not just close the gap; it reinstates the symmetry that forbids full-sphere support. Adding non-$X$ central couplings ($J_z, J_{zx}$) lifts this constraint and restores full-sphere coverage.

---

## The Sector-Resolved Cardinal Rule

> [!CAUTION]
> **Never mix eigenvalues from independent exact irreducible symmetry sectors before evaluating level spacings.**  
> Superposing independent spectra trivially creates Poissonian statistics (clustering without level repulsion), which can make a strongly chaotic Hamiltonian appear deceptively integrable.

All production spectral analysis (`scripts/analyze_zeus_spectral_relations.py`) resolves:
1. Total longitudinal magnetization $N_\uparrow$.
2. Translation momentum $k$.
3. Spatial reflection parity $\mathcal{P}$ at $k = 0, \pi$.
4. Exact degeneracies (merged before forming ratios).

---

## Synthesis: Where Level Statistics Stand
Detector level statistics are **neither necessary nor sufficient** by themselves to guarantee Born geometry. However:
- Moving a detector family toward Wigner–Dyson statistics *under fixed compatible dynamical conditions and full-sphere coverage* can enhance dipolar sharpness.
- Level statistics remain an essential diagnostic tool to guarantee that a detector is genuinely interacting and not an uncoupled collection of trivial oscillators.

See also: [[symmetry-sectors]], [[haar-baseline]], [[coverage-gates]], [[foundational-draft-aug2026]].
