# Collapse and Chaos

Python simulation toolkit for studying qubit–detector Hamiltonians,
projective disentanglement roots, Born-like angular statistics, and
symmetry-resolved spectral chaos.

This repository supports an ongoing theoretical and numerical research
project. A PRL-style manuscript package, including its sources, generated
figures, provenance records, and compiled PDFs, is maintained in
[`manuscript/`](manuscript/).

The codebase includes small-system NumPy reference implementations,
symmetry-aware QuSpin calculations, parameter-space studies, diagnostic
figures, and reproducible PBS workflows for the Technion Zeus cluster.

---

## Overview

The main model consists of a central qubit coupled to a detector of $N_D$
qubits. The project investigates how the detector Hamiltonian, interaction
network, spectral structure, and central-qubit coupling affect the projective
roots extracted from the time-evolution operator.

The principal numerical observable is the angular distribution of these
roots. In particular, the reflected-density ratio

```math
R(\theta)=\frac{P(\theta)}{P(\theta)+P(\pi-\theta)}
```

is compared with the qubit Born curve

```math
R_{\mathrm{Born}}(\theta)=\cos^2(\theta/2).
```

The repository also studies whether Born-like behavior correlates with
detector level statistics, near-degenerate couplings, resonance conditions,
system size, evolution time, and graph connectivity.

---

## Key Features

- **Qubit–detector Hamiltonians**: central-spin, single-pixel, two-pixel,
  dimerized, and mixed-field model families, with NumPy and QuSpin
  implementations where applicable.

- **Detector interaction graphs**: chain, periodic ring, all-to-all,
  Erdős–Rényi, Watts–Strogatz, Barabási–Albert, and random-regular
  connectivity. Periodic rings can include independent second-nearest-neighbor
  couplings.

- **Projective-root solvers**: homogeneous generalized-eigenvalue methods for
  finite, infinite, and indeterminate roots, with residual and regularity
  diagnostics.

- **Born-like diagnostics**: $P(\theta)$, $R(\theta)$, $S_{\mathrm{Born}}$,
  RMSE, occupied-bin coverage, azimuthal uniformity, wrapped-Gaussian and
  wrapped-Cauchy fits, radius-tail statistics, and full-sphere diagnostics.

- **Symmetry-resolved spectral analysis**: level-spacing distributions and
  adjacent-gap ratios computed within irreducible sectors rather than from
  mixed spectra.

- **Parameter-space studies**: deterministic grids, Sobol sampling, ranked
  follow-up studies, central-field sweeps, network-realization studies, and
  finite-size scaling campaigns.

- **Zeus workflows**: bounded PBS arrays, configuration manifests,
  per-configuration checkpoints, restart support, and independently verifiable
  completion markers.

- **Reproducible random graphs**: campaigns record graph families, generator
  parameters, seeds, and realized edge lists where supported by the workflow.

---

## Physics Background

### Qubit–Detector Hamiltonian

A representative single-pixel Hamiltonian is

```math
\begin{aligned}
H={}&H_Q+H_D+H_{QD},\\[2mm]
H_Q={}&-h_{x0}X_0-h_{z0}Z_0,\\
H_D={}&-h_z\sum_i Z_i
       -J\sum_{(i,j)\in E}Z_iZ_j
       -J_{\pm}\sum_{(i,j)\in E}
       \left(\sigma_i^+\sigma_j^-+\sigma_i^-\sigma_j^+\right)\\
    &-J_2\sum_{(i,j)\in E_2}Z_iZ_j
       -J_{\pm2}\sum_{(i,j)\in E_2}
       \left(\sigma_i^+\sigma_j^-+\sigma_i^-\sigma_j^+\right),\\
H_{QD}={}&-\sum_i\left(
       J_xX_0X_i+J_yY_0Y_i+J_zZ_0Z_i+J_{zx}Z_0X_i
       \right).
\end{aligned}
```

Here, site $0$ is the central qubit, $E$ is the detector interaction graph,
and $E_2$ is the second-nearest-neighbor edge set used by the corresponding
periodic-ring model. The implementation supports additional anisotropic and
exchange channels; consult the Hamiltonian class docstrings for the complete
parameterization and operator conventions.

Many collective-coupling campaigns use

```math
J_{x,\mathrm{eff}}=\frac{J_{x,\mathrm{source}}}{\sqrt{N_D}},
```

and analogously for $J_y$. This scaling is a campaign-level convention: the
Hamiltonian constructor receives the effective coupling. Results must record
both the source and effective values whenever this convention is used.

### Projective Disentanglement Roots

With the central qubit first in the tensor-product basis, time evolution is
partitioned as

```math
U(t)=e^{-iHt}=\begin{pmatrix}A&B\\C&D\end{pmatrix}.
```

For the production fixed-input-pole convention, projective roots are obtained
from the generalized linear pencil

```math
Cv=\lambda Av.
```

A finite root $\lambda$ defines the normalized qubit state

```math
|\phi_0(\lambda)\rangle=
\frac{|0\rangle+\lambda|1\rangle}{\sqrt{1+|\lambda|^2}},
\qquad
\theta=2\arctan|\lambda|,
\qquad
\phi=\arg\lambda.
```

[`core/relative_evolution_pencil.py`](core/relative_evolution_pencil.py)
implements the homogeneous generalized-eigenvalue calculation. It retains
finite, infinite, and indeterminate projective pairs and reports numerical
regularity checks. Direct $A^{-1}C$-style calculations remain available for
comparison but are unreliable when $A$ is singular or poorly conditioned.

### Born-Like Similarity

The main scalar similarity score is

```math
S_{\mathrm{Born}}
=1-2\int_0^\pi
\left|R(\theta)-\cos^2(\theta/2)\right|\sin\theta\,d\theta.
```

`S_Born` is a finite-sample screening diagnostic. A high value means that the
measured angular ratio is close to the Born curve under the stated binning and
weighting conventions. It is not, by itself, a probability assignment, a
convergence proof, or a derivation of the Born rule.

### Spectral Statistics and Symmetries

Level-spacing statistics are meaningful only after all applicable exact
symmetries have been resolved. Depending on the Hamiltonian, the analysis can
separate sectors by:

- detector magnetization or magnetization parity;
- translation momentum on clean periodic rings;
- reflection parity where it is compatible with momentum;
- exact graph automorphisms, including twin-vertex symmetries;
- spatial symmetries of dimerized and two-pixel models.

Generic random graphs are not assigned circular symmetry. The spectral tools
provide unfolded spacing distributions and adjacent-gap ratios with Poisson
and Wigner–Dyson reference statistics.

---

## Repository Structure

```text
collapse/
├── core/                     # Reusable physics and numerical library
│   ├── hamiltonians/         # NumPy and QuSpin Hamiltonian families
│   │   ├── base.py
│   │   ├── numpy_hamiltonians.py
│   │   └── quspin_hamiltonians.py
│   ├── analysis.py           # Relative-evolution analysis
│   ├── relative_evolution_pencil.py
│   ├── born.py               # Polar Born-like diagnostics
│   ├── gleason_diagnostics.py
│   ├── level_spacing.py      # Spectral statistics
│   ├── graph_symmetry.py     # Exact graph automorphisms
│   ├── graph_spectral_sectors.py
│   ├── detector_graphs.py    # Seeded detector-network construction
│   ├── sobol_coupling_scan.py
│   └── visualization.py
├── scripts/                  # Study runners, analyses, and figure builders
├── configs/                  # Versioned research and Zeus configurations
├── hpc/                      # PBS jobs, submission wrappers, and runbooks
├── tests/                    # Unit, regression, invariant, and smoke tests
├── manuscript/               # PRL Letter, supplement, figures, and audits
├── reports/                  # Local research reports; excluded from Git
├── figures/                  # Local generated figures; excluded from Git
├── work/                     # Zeus results and intermediate data; excluded
├── archive/                  # Legacy code; not imported by active modules
├── AGENTS.md                 # Scientific and engineering contribution rules
└── README.md
```

Reusable physics belongs in `core/`; executable orchestration belongs in
`scripts/`; scientifically meaningful parameter sets belong in `configs/`.
Active code must not import from generated-data or legacy directories.
Additional generated locations such as `output/`, `presentations/`, `proofs/`,
and `tmp/` are reserved in `.gitignore` and may not exist in a fresh checkout.

---

## Installation

### Prerequisites

- Python **3.11**, matching the Zeus environment
- A virtual environment is strongly recommended
- A working compiler/runtime compatible with QuSpin if running the optional
  symmetry-aware calculations

The current repository does not contain packaging metadata or a dependency
lock/requirements file. Run commands from the repository root so the local
`core` package is on Python's import path. The commands below install the
core libraries used by the package and test suite; reproduce archival results
only with the environment recorded in the corresponding result metadata.

### Setup

```bash
# Clone the research group's repository, then enter it
git clone <repository-url>
cd collapse

# Create and activate a Python 3.11 virtual environment (macOS / Linux)
python3.11 -m venv .venv
source .venv/bin/activate

# Install the core numerical and test dependencies
python -m pip install --upgrade pip
python -m pip install numpy scipy matplotlib pytest

# Optional: symmetry-aware Hamiltonians
python -m pip install quspin

# Verify the installation
python -m pytest -q
```

### Core Dependencies

| Package | Purpose |
| --- | --- |
| **NumPy** | Dense arrays and small-system reference calculations |
| **SciPy** | Linear algebra, statistics, fitting, and sparse numerics |
| **Matplotlib** | Diagnostic and publication-quality figures |
| **pytest** | Unit, regression, and integration tests |
| **QuSpin** | Optional symmetry-aware many-body Hamiltonians |

Some report and PDF-building scripts additionally import Pillow, pypdf, or
ReportLab. Install those only when using the corresponding workflow.

---

## Quick Start

The following small-system calculation constructs one central qubit and three
detector qubits, checks Hermiticity, and diagonalizes the Hamiltonian:

```python
import numpy as np

from core import SinglePixelHamiltonianNumpy

model = SinglePixelHamiltonianNumpy(
    N_pixel=3,
    J=1.0,
    Jpm=0.2,
    Jx=0.05,
    hz=0.1,
    hz0=0.0,
    connectivity="ring",
    central_coupling="all",
)

hamiltonian = model.generate()
energies = np.linalg.eigvalsh(hamiltonian)

assert hamiltonian.shape == (16, 16)
assert np.allclose(hamiltonian, hamiltonian.conj().T)
print(energies)
```

Production-scale scripts are not suitable as local smoke tests.

---

## Key Scripts and Workflows

### Local demonstrations

- [`scripts/born_sampling_demo.py`](scripts/born_sampling_demo.py) — basic
  sampling and Born-diagnostic workflow.
- [`scripts/level_spacing_demo.py`](scripts/level_spacing_demo.py) — compact
  level-spacing analysis example.
- [`scripts/single_pixel_ring_grid.py`](scripts/single_pixel_ring_grid.py) —
  parameter-grid study for the periodic single-pixel detector.

### Analysis and figure generation

- [`scripts/plot_born_candidate_diagnostics.py`](scripts/plot_born_candidate_diagnostics.py)
  — diagnostic $P(\theta)$ and $R(\theta)$ figures.
- [`scripts/analyze_network_sobol_born_relations.py`](scripts/analyze_network_sobol_born_relations.py)
  — relations between graph-family parameters, spectral characteristics, and
  Born-like similarity.
- [`scripts/build_ranked_ring_momentum_spacing_figures.py`](scripts/build_ranked_ring_momentum_spacing_figures.py)
  — momentum-resolved ring level-spacing figures.
- [`scripts/build_network_sobol_graph_ranked_2x3.py`](scripts/build_network_sobol_graph_ranked_2x3.py)
  — ranked random-network diagnostics with graph visualization.

### Zeus campaigns

Zeus studies normally combine three files:

1. a JSON parameter set in `configs/`;
2. a Python campaign runner in `scripts/`;
3. a PBS array and submission wrapper in `hpc/`.

Submit from the repository root on Zeus and use a unique `RUN_ROOT` for every
scientifically distinct campaign:

```bash
RUN_ROOT="$PWD/work/my_campaign_$(date +%Y%m%d_%H%M%S)" \
  bash hpc/submit_<campaign>.sh
```

Rerunning the same wrapper with the same `RUN_ROOT` resumes configurations
whose checkpoints are valid. See [`hpc/README.md`](hpc/README.md) and the
campaign-specific runbooks before submission. Do not submit or alter
production jobs from a local development machine.

---

## Configuration and Reproducibility

Scientifically relevant parameters are stored in versioned JSON files under
[`configs/`](configs). These include, as applicable:

- Hamiltonian coefficients and connectivity parameters;
- detector size and evolution times;
- source and effective collective couplings;
- Sobol dimension, bounds, and sample count;
- random seeds and graph-generation parameters;
- solver choices, tolerances, and symmetry conventions;
- output and checkpoint policies.

A completed configuration normally contains:

| File | Contents |
| --- | --- |
| `COMPLETE.json` | Completion state and output checksums |
| `metadata.json` | Effective parameters, seeds, graph, timings, versions, and code provenance |
| `validation.json` | Normalization, dimension, Hermiticity, and solver checks |
| `metrics.json` | Scalar diagnostics |
| `results.npz` | Numerical arrays |

Treat `COMPLETE.json` as the commit marker. A partially populated directory is
not sufficient evidence that a calculation finished successfully. For random
networks, retain the realized edge list as well as the generator seed and
parameters.

---

## Testing

Run a focused test while developing:

```bash
python -m pytest -q tests/test_<feature>.py
```

Run the complete suite before sharing a substantial branch when feasible:

```bash
python -m pytest -q
```

Scientific changes should include suitable independent checks, such as:

- NumPy–QuSpin agreement at small system size;
- Hermiticity, unitarity, normalization, or dimension identities;
- reconstruction of the Hilbert-space dimension from symmetry sectors;
- generalized-eigenvalue residuals and regularity checks;
- deterministic-seed regression tests;
- size, timestep, cutoff, or tolerance sensitivity studies.

A visually plausible figure is not sufficient validation.

---

## Notation

| Symbol | Meaning |
| --- | --- |
| $N_D$ | Number of detector qubits |
| $H_Q$ | Central-qubit Hamiltonian |
| $H_D$ | Detector Hamiltonian |
| $H_{QD}$ | Qubit–detector interaction Hamiltonian |
| $J$, $J_{\pm}$ | Detector ZZ and exchange couplings on $E$ |
| $J_2$, $J_{\pm2}$ | Second-nearest-neighbor ring couplings |
| $J_x$, $J_y$, $J_z$, $J_{zx}$ | Central-qubit–detector couplings |
| $h_z$ | Detector longitudinal field |
| $h_{x0}$, $h_{z0}$ | Central-qubit fields |
| $t$ | Evolution time |
| $\lambda$ | Generalized projective root |
| $\theta$, $\phi$ | Polar and azimuthal root coordinates |
| $P(\theta)$ | Root polar-angle density |
| $R(\theta)$ | Reflected-density ratio |
| $S_{\mathrm{Born}}$ | Finite-sample similarity score relative to the Born curve |

---

## Further Documentation

- [`manuscript/README.md`](manuscript/README.md) — contents of the manuscript
  package and its evidence trail.
- [`manuscript/BUILD.md`](manuscript/BUILD.md) — manuscript build and verification
  instructions.
- [`hpc/README.md`](hpc/README.md) — Zeus campaign layout and operating notes.
- [`AGENTS.md`](AGENTS.md) — scientific and engineering standards for
  contributions.

---

## Research Status and Citation

This is active research software. A manuscript draft exists under
`manuscript/`, but there is not yet a preferred publication citation. Until a
formal software release or paper exists, collaborators citing results from
this repository should record the repository URL, Git commit hash,
configuration file, and result provenance, and coordinate attribution with
the project maintainers.

Claims in exploratory scripts or generated reports should not be interpreted
as peer-reviewed conclusions.

## Data and License

Bulk results, downloaded Zeus data, generated reports, and most figures are
excluded from Git. Transfer required datasets separately and preserve their
original directory structure or pass explicit paths to analysis scripts.

No license file is currently included. Until the research group selects and
adds a license, treat this repository as internal group research code and do
not redistribute it outside the authorized collaboration.

## Contact

For questions, reproducibility issues, or proposed changes, open an issue in
the research group's repository or contact the project maintainers through the
group's usual collaboration channel.
