---
name: altshuler-et-al-1997
description: Foundational mapping of quasiparticle decay in interacting systems to Anderson localization on a high-dimensional Fock-space graph.
metadata:
  type: reference
---

# Altshuler et al. 1997 — Quasiparticle Lifetime and Localization in Fock Space

**Reference**: B. L. Altshuler, Y. Gefen, A. Kamenev, and L. S. Levitov, "Quasiparticle Lifetime in a Finite System: A Nonperturbative Approach", *Physical Review Letters* **78**(14), 2803–2806 (1997). DOI: [10.1103/PhysRevLett.78.2803](https://doi.org/10.1103/PhysRevLett.78.2803). arXiv: [cond-mat/9609132](https://arxiv.org/abs/cond-mat/9609132).

## Core Thesis
Demonstrated that the decay and thermalization of a single quasiparticle in a closed, interacting quantum dot can be mapped directly onto single-particle Anderson localization on a high-dimensional **Fock-space graph** (Cayley tree). Altshuler et al. showed that perturbation theory (Fermi's Golden Rule) fails at low excitation energies, where the scarcity of resonant multi-particle decay channels induces a quantum localization transition in Fock space, stabilizing quasiparticles with infinite lifetimes.

## Key Mathematical Formalism
- **Many-Body Fock Space as a Tree Graph:**
  - *Root Node:* Initial state with 1 quasiparticle excitation of energy $\epsilon$.
  - *Generation 1:* 2-quasiparticle / 1-quasihole (2p-1h) states connected via two-body Coulomb matrix elements $M$.
  - *Generation $m$:* $(m+1)\text{p}-m\text{h}$ states.
  - The effective branching ratio (connectivity) scales with energy:
    $$K(\epsilon) \approx \frac{\epsilon^2}{2 \Delta^2},$$
    where $\Delta$ is the single-particle level spacing.
- **Fock-Space Localization Transition:**
  Using the Abou-Chacra–Thouless–Anderson criterion for localization on a Bethe lattice with connectivity $K$, the hopping matrix element $M$ competes with the energy mismatch between generations.
  - Localization occurs when the tunneling rate is smaller than the typical level separation:
    $$K(\epsilon) \frac{M^2}{\Delta^2} \lesssim 1 \implies \epsilon < \epsilon_{\text{th}} \approx \Delta \sqrt{\frac{g}{\ln g}},$$
    where $g = E_F / \Delta \gg 1$ is the dimensionless conductance.
  - Below $\epsilon_{\text{th}}$, the quasiparticle cannot decay: the state is localized in Fock space, preserving non-ergodicity.

## Relevance to `unitary-collapse`
Altshuler et al.'s Fock-space graph framework provides the physical picture for why a many-body detector does not immediately thermalize upon coupling to a qubit. If the detector operates near a Fock-space localization boundary, excitations remain structured and coherent rather than dissipating into ergodic thermal noise, providing conditions where the dual outcome pencils $(U_{10}, -U_{11})$ and $(U_{00}, -U_{01})$ may support stable, unentangled projective roots. Under SPEC v1.0, this mechanism hypothesis requires fresh verification against matched controls.
