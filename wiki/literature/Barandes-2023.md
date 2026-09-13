---
name: barandes-2023
description: The Stochastic-Quantum Correspondence — quantum mechanics as an indivisible stochastic process.
metadata:
  type: reference
---

# Barandes 2023 — The Stochastic-Quantum Correspondence

**Reference**: J. A. Barandes, arXiv: [2302.10778](https://arxiv.org/abs/2302.10778) [quant-ph] (2023).

**Related**:
- J. A. Barandes and D. Kagan, *Foundations of Physics* **50**, 998–1018 (2020). arXiv: [1405.6755](https://arxiv.org/abs/1405.6755). (Minimal Modal Interpretation — precursor.)

## Core Thesis
Quantum mechanics is mathematically equivalent to a **real-valued, non-negative stochastic process** on a physical configuration space—specifically, an **indivisible** stochastic process. Complex probability amplitudes emerge as linearizing potentials for the intrinsically non-Markovian (indivisible) stochastic composition, not as ontological primitives.

## Key Concepts
- **Unistochastic matrices:** $\Gamma_{ji} = |U_{ji}|^2$ form doubly stochastic transition matrices with non-negative entries.
- **Indivisibility:** Quantum dynamics violates the Chapman–Kolmogorov equation at unmeasured intermediate times: $\Gamma(t_2, t_0) = \Gamma(t_2, t_1)\Gamma(t_1, t_0) + \mathcal{I}(t_2, t_1, t_0)$, where $\mathcal{I}$ is the interference tensor.
- **Division events:** Times at which measurement/decoherence restores $\mathcal{I} \to 0$ and Chapman–Kolmogorov holds. "Collapse" is a division event followed by Bayesian conditioning.
- **Complex amplitudes as gauge potentials:** $U_{ji} = \sqrt{\Gamma_{ji}} \, e^{i\phi_{ji}}$ linearizes the nonlinear indivisible composition into a group representation.

## Distinction from Nelson's Stochastic Mechanics (1966)
Unlike Nelson's Brownian diffusion approach, the SQC:
- Is explicitly **indivisible** (not Markovian).
- Is immune to Wallstrom's objection (phase quantization is algebraic, not postulated).
- Matches multi-time correlations exactly (Nelson's fail).
- Requires no physical "stochastic medium."

## Relevance to `unitary-collapse`
The SQC provides a natural language for the `unitary-collapse` mechanism:
1. **Projective roots as autonomous division events:** States for which many-body dynamics suppresses $\mathcal{I}$ without external measurement.
2. **Born rule from divisibility structure:** If only projective-root states produce autonomous divisions, their geometric distribution gives Born's rule physical content through the stochastic process structure.
3. **Repository implementation:** Divisibility monitoring ($D_{00}(t', t)$) was implemented in `archive/sqc.ipynb`, directly measuring $\mathcal{I}$ amplitude.
