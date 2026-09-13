---
name: cramer-1986
description: Foundational formulation of the Transactional Interpretation of Quantum Mechanics based on Wheeler-Feynman absorber theory.
metadata:
  type: reference
---

# Cramer 1986 — The Transactional Interpretation of Quantum Mechanics

**Reference**: John G. Cramer, "The transactional interpretation of quantum mechanics", *Reviews of Modern Physics* **58**(3), 647–687 (1986). DOI: [10.1103/RevModPhys.58.647](https://doi.org/10.1103/RevModPhys.58.647).

*Monograph*: J. G. Cramer, *The Quantum Handshake: Entanglement, Nonlocality and Transactions*, Springer International Publishing (2016). DOI: [10.1007/978-3-319-24642-0](https://doi.org/10.1007/978-3-319-24642-0).

## Core Thesis
Relativistic quantum wave equations are time-symmetric, admitting both retarded (forward in time) and advanced (backward in time) solutions. Drawing on Wheeler–Feynman absorber theory, Cramer models quantum events as standing-wave exchanges—**transactions** or "quantum handshakes"—between an emitter sending a retarded **offer wave (OW)** forward in time and absorbers sending advanced **confirmation waves (CW)** backward in time.

## Key Mathematical Formalism
- **The Quantum Handshake & Born's Rule:**
  1. An emitter $E$ sends an offer wave $|\psi(t)\rangle = \sum_j c_j |j\rangle$ forward in time ($t > t_E$).
  2. Each prospective absorber $A_j$ responds with an advanced confirmation wave $\langle \phi_j(t)| \propto c_j^* \langle j|$ propagating backward in time ($t < t_{A_j}$).
  3. The echo arriving back at the emitter has intensity:
     $$\mathcal{P}_j = \text{OW}_j(x_E, t_E) \times \text{CW}_j(x_E, t_E) = c_j \cdot c_j^* = |c_j|^2.$$
     **Born's rule is derived physically** as the constructive standing-wave intensity of the completed two-way handshake circuit.
- **Resolution of EPR Nonlocality:** In Bell experiments, the causal link between detectors does not cross spacelike intervals; it travels along a continuous light-like zig-zag through the past light cones of the detectors back to the emitter:
  $$\text{Detector A } (t_A) \xrightarrow{\text{advanced wave}} \text{Source } (t_S) \xrightarrow{\text{retarded wave}} \text{Detector B } (t_B).$$

## Relevance to `unitary-collapse`
Cramer's transactional interpretation invokes future boundary conditions to select which transaction actualizes. This provides a physical mechanism analogous to Schulman's two-time boundary conditions. In `unitary-collapse`, by contrast, retrocausality is unnecessary: the selection of definite outcomes is performed forward in time by the algebraic structure of the detector's matrix pencil $(A_N, C_N)$.
