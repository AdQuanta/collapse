# Hamiltonian Families

The `unitary-collapse` project investigates a broad spectrum of Hamiltonian families to determine which structural properties of $H$ move the special-state point process away from Haar isotropy and toward a measurement-like Born dipole.

---

## Foundational Archetypes (Draft §6)

In the foundational draft (`main.pdf`), detector Hamiltonians are classified into three primary structural archetypes based on their spatial locality and interaction topology:

```
Noninteracting Disordered      Interacting Pixels             Tube / Chain Geometry
Q coupled to independent       Strong intra-pixel coupling;   Q couples to edge site 1;
disordered detector spins      weak/no inter-pixel coupling   information propagates inward
[Schulman / Star Model]        [Domain Locality]              [Strict Spatial Locality]
<-------------------------- More Structure & Locality -------------------------->
```

### Family I: Noninteracting Disordered Detector (§6.1)
- **Hamiltonian:**
  $$
  H_D = \sum_{i=1}^n h_i^z \sigma_i^z, \quad H_{QD} = \sum_{i=1}^n g_i \sigma_Q^x \sigma_i^x.
  $$
- **Mechanism:** The measured qubit couples to independent detector spins without mutual detector interactions. Disorder in $h_i^z$ and/or $g_i$ is essential.
- **Literature Precursor:** Conceptually closest to Schulman’s special-state theory (1997, 2012), where heavy-tailed Cauchy/Lorentzian noise was shown to generate Born-like outcome probabilities.
- **Status:** Shows Born-like behavior in specific parameter windows, but lacks internal detector thermalization.

### Family II: Interacting "Pixel" Detectors (§6.2)
- **Hamiltonian:**
  $$
  H = H_Q + H_{D_0} + H_{D_1} + H_{QD_0} + H_{QD_1}, \quad [H_{D_0}, H_{D_1}] = 0.
  $$
- **Mechanism:** The detector is divided into distinct macroscopic sub-domains ("pixels"). Strong interactions within each domain allow internal dephasing, while weak or zero inter-pixel coupling associates distinct spatial record sectors with measurement outcomes $|0\rangle$ and $|1\rangle$.

### Family III: Local "Tube" or Chain Detector (§6.3)
- **Hamiltonian:**
  $$
  H = H_Q + H_{Q,1} + \sum_{\ell=1}^L H_\ell + \sum_{\ell=1}^{L-1} H_{\ell,\ell+1}.
  $$
- **Mechanism:** The qubit couples only to the boundary site/layer ($\ell = 1$), and information propagates sequentially into deeper layers.
- **Physical Role of Locality:** Information deposited in the detector moves away ballistically or diffusively, suppressing coherent backflow onto the qubit and enforcing an effective arrow of time without requiring all-to-all connectivity.

---

## Detailed Model Families in the Codebase

### 1. Single-Pixel Model (`SinglePixelHamiltonian`)
The primary numerical workhorse implemented in `core/hamiltonians/numpy_hamiltonians.py` and `quspin_hamiltonians.py`.
- **Intra-pixel:** Nearest-neighbor $Z_i Z_j$, second-neighbor $Z_i Z_k$, and XY exchange $(X_i X_j + Y_i Y_j)/2$.
- **Central Coupling:** $X_0 X_i$, $Z_0 Z_i$, $Z_0 X_i$, $Y_0 Y_i$, scaled as $1/\sqrt{N_{\text{pixel}}}$ or unscaled.
- **Topologies:** 1D chain, periodic ring, all-to-all, and random graphs (Erdős–Rényi, Watts–Strogatz, Barabási–Albert, Random Regular).

### 2. Mixed-Field Ising Model & The Transverse-Field Clue
- **Hamiltonian:**
  $$
  H_D = \sum_{\langle i,j \rangle} J_{ij} \sigma_i^z \sigma_j^z + \sum_i h_i^z \sigma_i^z + h_x \sum_i \sigma_i^x, \quad H_{QD} = \sum_i g_i \sigma_Q^x \sigma_i^x.
  $$
- **The Transverse-Field Observation (Draft §6.4):** In early simulations, adding a transverse field $h_x$ drove the long-time distribution toward the uniform Haar baseline.
- **Crucial Update (August 27, 2026):** As proved in `RESEARCH_STATE.md` §14a, setting $h_{z0} = h_{x0} = 0$ in central-$X$-only models enforces an exact symmetry $[H, X_Q] = 0$ that restricts all roots to a 1D great circle on the Bloch sphere. The apparent breakdown was partly an artifact of this great-circle constraint. Breaking $X$-conservation (e.g. adding $J_z$ or transverse central fields) is required for full-sphere support.

### 3. Constructive Commuting Class (`core/born_asymptotic.py`)
- **Hamiltonian:** $H = K - h_{x0}X_q - h_{z0}Z_q - X_q \sum g_i X_i$, where $[K, \sum g_i X_i] = 0$.
- **Certificate:** Analytically certified discrete family ($N \ge 13$) passing the 64-bin acceptance gate via rational combinatorial divisors ([[constructive-families]]).
- **Limitation:** In the continuous thermodynamic limit, Theorems B and C prove that this class cannot yield continuous Born support ([[asymptotic-obstructions]]).

### 4. Weak-Coupling Interacting Rings & Chains (`core/ring_chain_family.py`)
- **Interactions:** Weak qubit-detector coupling with $g_x/\sqrt{N}, g_y/\sqrt{N}, g_z/N$ on periodic rings, or unscaled on chain endpoints.
- **Leads:** Audited positive ring sequences ($N=14\text{--}17$) with $S_{\text{born}} > 0.93$ and ratio RMSE $< 0.02$ at $t = 10^6$ ([[weak-coupling-search]], [[resonant-return-dynamics]]).

See also: [[big-picture]], [[spectral-statistics]], [[coverage-gates]], [[foundational-draft-aug2026]].
