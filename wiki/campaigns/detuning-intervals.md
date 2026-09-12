# Detuning and Commuting Vector Fields

## Objective
Investigate whether an open interval of central-Z detuning ($b$) can produce exact Born balance for detectors with commuting vector fields.

## Theorem H: No Detuning Interval
For native-sign conditional dynamics where the detector operators $K_N, V_N, W_N$ all commute, and where the joint spectral law has a finite transverse second moment: **there is no nonempty open interval $I$ of detuning $b$ on which all limiting laws satisfy exact continuous Born reflection balance.**

### The Proof Mechanism
The proof relies on the "south-pole mass" $S_b(\epsilon) = \Pr(X > 1-\epsilon)$:
1. **Resonance Case**: If the active field law assigns positive mass to $-w$ in $I$, then for small $\epsilon$, there is a region where the root radius $k_b$ is large and the phase is near the pole. This forces $S_b(\epsilon) \ge C\epsilon$, which contradicts the Born requirement $S_b(\epsilon) = o(\epsilon)$.
2. **Gap Case**: If there is a detuning gap $|w+b| \ge \delta > 0$, then $S_b(\epsilon) = o(\epsilon^{3/2})$. However, Born balance requires $S_b(\epsilon) \ge \frac{2m}{3\pi}\epsilon^{3/2}$ for some $m>0$.

## Corollary H1: Native XX/ZX Families
The collective family $V_N = h + gS_N$ and $W_N = cS_N$ (where $S_N = N^{-1/2}\sum X_i$) is **excluded pointwise**. For any real $h, b, c$, the long-time root limit is not a continuous full-support exact-Born law.

## Key Insight
This result improves previous obstructions by showing that even with detuning, the "phase-mixed" mechanism cannot produce Born statistics unless the coupling spectrum has an **infinite second moment** (e.g., the heavy-tail counterexample). Native Rademacher spectra are too "tight" to allow this.

See also: [[asymptotic-obstructions]], [[born-like-points]].
