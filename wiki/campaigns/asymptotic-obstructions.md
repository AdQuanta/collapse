# Asymptotic Born Obstructions

## Objective
Determine if Born-like root statistics can be established as a robust long-time thermodynamic limit ($N \to \infty, t \to \infty$) for the native qubit-detector model.

## Key Theorems & Obstructions
The research has established several fundamental obstructions to an exact Born limit:

### 1. The Recurrence Obstruction (Theorem A)
In any finite-dimensional Hermitian system, there are arbitrarily late times at which all roots return to the north pole ($\theta \approx 0$). Consequently, a joint root-measure limit with continuous full angular support cannot be independent of late-time subsequences.

### 2. Commuting Conditional Dynamics (Theorem B)
For Hamiltonians of the form $H_N = I \otimes K_N - X_q \otimes (V_N + h_N I)$ where $[K_N, V_N] = 0$, the long-time limit is necessarily $P_* = L\delta_0 + (1-L)d\theta/\pi$. This is only Born if $L=1$ (all roots at the pole), meaning **no member of this class has a continuous, fully supported exact Born long-time limit.**

### 3. Central-X Field Obstruction (Theorem C)
For the $X$-conserving class, the set of central fields $h$ that allow a Born limit has Lebesgue measure zero. A robust "Born phase" cannot exist as an open interval of fields in this class.

### 4. Folded Gaussian Baseline (Theorem D)
The standard collective coupling $V_N = \frac{g}{\sqrt{N}} \sum X_i$ converges to a folded wrapped Gaussian. Its reflected response converges to $1/2$, not Born. This confirms that "more random" (in the sense of CLT) is not "more Born."

### 5. Detuned Commuting Obstruction (Theorem E)
For detuned commuting models ($b \neq 0$), a Born limit requires the coupling spectrum to have an infinite third absolute moment. Native linear-X Rademacher spectra have sub-Gaussian tails and are thus excluded.

## Status
**Partial analytical resolution.** While large classes of commuting and $X$-conserving models are excluded, the full-model problem (non-commuting detectors, $YY/ZZ/ZX$ interactions) remains **OPEN**.

See also: [[born-like-points]], [[spectral-statistics]].
