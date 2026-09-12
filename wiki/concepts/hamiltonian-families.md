# Hamiltonian Families

The `unitary-collapse` project employs a diverse set of Hamiltonian families to explore the conditions under which Born-like root statistics emerge. These families range from highly structured, analytically tractable models to disordered, random-graph detectors.

## 1. Single-Pixel Model
The most general "workhorse" of the project. It consists of a central qubit coupled to a "pixel" of $N_{\text{pixel}}$ qubits.
- **Intra-pixel Interactions**: Supports ZZ and Exchange (XY) couplings.
- **Central Coupling**: Supports XX, ZZ, and ZX channels.
- **Topologies**:
    - **Deterministic**: Chain, Ring, and All-to-all.
    - **Random Graphs**: Erdős–Rényi, Watts–Strogatz, Barabási–Albert, and Random Regular (Expander) graphs.
- ** Implementation**: `SinglePixelHamiltonian` (NumPy/QuSpin).

## 2. Dimerized Pixel Model
A variant of the single-pixel model where intra-pixel ZZ interactions are restricted to non-overlapping dimers:
\[ H_{\text{intra}} = -J \sum_{i=1}^{N_{\text{pixel}}/2} \sigma^z_{2i-1} \sigma^z_{2i} \]
This model is used to study the effect of breaking the translation symmetry of the ring.

## 3. Two-Pixel Model
A symmetric construction where the central qubit is sandwiched between two identical pixels.
- **Opposite Coupling**: The central qubit couples with opposite signs to the two pixels.
- **Purpose**: Used to explore the effect of balanced "push-pull" dynamics on the root distribution.

## 4. Central-Spin (Star) Model
A simpler geometry where the central qubit is coupled to $N^*$ satellite qubits with no interactions between the satellites themselves.
- **Interactions**: Purely XX and ZZ central couplings.
- **Implementation**: `CentralSpinHamiltonian` (NumPy/QuSpin).

## 5. Mixed-Field Ising Model
A standard 1D chain with periodic boundary conditions, featuring ZZ interactions and both transverse ($X$) and longitudinal ($Z$) fields.
- **Purpose**: Used as a baseline for studying the effects of disorder and field-driven transitions.

## 6. Constructive Commuting Class
A specifically designed class where the detector Hamiltonian $K$ commutes with the coupling operator $V = \sum g_i X_i$.
- **Mechanism**: Allows for a reduction to independent 2D blocks.
- **Result**: By tuning $g_i$, a "designer" Born-like distribution can be analytically certified.
- See: [[constructive-families]].

## 7. Weak-Coupling Interacting Families
Perturbatively coupled XYZ rings and endpoint-chains.
- **Focus**: Studies the stability of Born-like behavior under weak coupling and the role of resonances.
- See: [[weak-coupling-search]].

See also: [[production-pipeline]], [[symmetry-resolution]].
