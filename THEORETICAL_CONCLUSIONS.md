# Theoretical conclusions

### What is proved

**PROVED ANALYTICALLY:** regular degree-`d` projective pencils have `d` roots
counted with algebraic multiplicity; unitary complementary-minor duality pairs
the two forward label multisets by exact Bloch antipodes; strict
`[H,Z_Q]=0` pointer-QND evolution gives only the two poles; and appending a
dynamically uncoupled tensor-factor spectator repeats every root without
changing normalized root geometry.

### What the existing numerics establish

**VERIFIED NUMERICALLY:** the hashed matched-ring N=16 roots reproduce the
stored polar score and legacy full-sphere result. The modern analysis is fully
covered, axis aligned, and dipole dominated, with `L>=3` approximately
0.011--0.013 across three grids, but `eta` approximately 1.14 rather than one.
Its stricter direct density-ratio residual remains `0.526--0.602` across those
grids, so the finite cloud is not Born-exact at the density level.
The finite-size harmonic trend is nonmonotonic and not converged. Strict QND is
exactly pole-only for detector N=2--6. Uncoupled spectator dimensions through
8 leave normalized geometry invariant to roundoff.

A common reanalysis of 1,366 completed Erdos-Renyi, Watts-Strogatz,
Barabasi-Albert, and random-regular network realizations shows that occasional
high polar Born scores do not imply a resolved Born-compatible sphere. At a
common `16 x 8` equal-area resolution, every network realization has incomplete
coverage (median `0.25` in all four families), so unregularized harmonic and
dipole claims must be withheld.

**PROVED ANALYTICALLY and VERIFIED NUMERICALLY:** the common `hz0=hx0=0`,
central-X-only network Hamiltonians conserve `X_Q`. Their production roots are
therefore confined to the `y-z` great circle, independently of detector graph
connectivity. Across all 1,366 saved clouds, `max |r_x| < 1.27e-7`. Detector
graph randomization alone cannot repair this full-sphere obstruction.

The same theorem is verified across 672 completed nearest- and
second-neighbour `hz0=0` Sobol rings; second-neighbour connectivity does not
restore two-dimensional support. In contrast, nonzero `hz0` breaks the
obstruction: 52 of 400 narrow matched-band `N=14` configurations fully cover
the common sphere. Yet their median `L>=3=0.366` and median `eta=1.253` show
that symmetry breaking, matching, and coverage are not sufficient for Born
geometry. All 52 remain extremely well aligned with `+z`.

One homogeneous-QZ-audited `N=8` Haar realization is fully covered but has
`L>=3=0.896`, `eta=0.0267`, and `epsilon_B=0.657`, providing a finite-sample
null with no stable target dipole. Additional seeds are in the Zeus manifest.

### Which Hamiltonian ingredients appear necessary

**INFERRED:** departure from strict conservation of the central pointer is
necessary for nontrivial sphere coverage in the tested matrix-pencil model.
A preferred axis is necessary for a stable nonzero target dipole. No stronger
cross-family necessity claim is yet justified.

### Which ingredients appear sufficient

**NOT SUPPORTED:** no presently isolated ingredient is sufficient. The matched
ring combination is a successful finite-size example, not a sufficiency
theorem or a demonstrated universality class.
The 400-point matched-band comparison explicitly falsifies the sufficiency of
field matching plus nonzero transverse coupling and angular coverage.

### Counterexamples / no-go classes

**PROVED ANALYTICALLY and VERIFIED NUMERICALLY:** strict pointer-QND
Hamiltonians are pole-degenerate even when the detector is interacting and
internally noncommuting. **NOT SUPPORTED:** resonance, exact degeneracy, heavy
tails, interaction, or generic scrambling alone guarantees Born geometry.
Central-X-conserving (`hz0=hx0=0`, X-only coupling) models form a second exact
no-go for two-dimensional full-sphere support: roots remain on one great
circle, even across four random graph families.

### Role of transverse mixing

**INFERRED:** some central transverse/noncommuting action is required to escape
the QND poles. **HPC CALCULATION REQUIRED:** whether there is an intermediate
optimal strength and whether strong mixing eventually increases higher odd
harmonics.

### Role of field matching

**SUPPORTED NUMERICALLY:** exact matching occurs in the strongest stored clean
ring sequence. **NOT SUPPORTED:** matching alone is sufficient; resonance
controls broaden support without necessarily producing Born geometry.
Within 52 resolved `N=14` Sobol cases, smaller absolute
`delta=(hz0-hz)/Jx` improves the legacy polar score but has no FDR-resolved
association with higher-odd leakage. **HPC CALCULATION REQUIRED:** homogeneous
QZ detuning scans across size and time.

### Role of scrambling

**NOT SUPPORTED:** available evidence does not establish a monotonic relation
between spectral chaos/scrambling and dipole purity. Symmetry-resolved common
pipeline comparisons are still required.

### Relation to Gleason's theorem

Gleason-type trace-rule conclusions apply only after positivity,
normalization, orthogonal additivity, and appropriate noncontextuality are
supplied. Hamiltonian root geometry does not derive those assumptions. A pure
dipole is a necessary geometric signature of the qubit trace-rule sector, not
proof that algebraic roots carry physical probabilities.

### Composition/context-consistency results

**PROVED ANALYTICALLY and VERIFIED NUMERICALLY:** normalized algebraic root
geometry is invariant under adding an uncoupled tensor-factor spectator; raw
multiplicity scales by spectator dimension. Detector-basis permutations are
also exactly invariant. Conversely, nonuniform direct-sum duplication of one
dynamically identical detector microsector changes normalized equal-root
weights. Thus unweighted root counting fails a general refinement-
noncontextuality test. Ready-sector, coarse-graining, and interacting-context
invariance remain open.

### Strongest Hamiltonian classification currently justified

The best supported motif is a preferred readout axis plus weak controlled
central transverse mixing and structured many-body detector dynamics. This
combination can produce a strongly aligned, approximately dipolar finite-size
root field. It is distinguished from merely QND dynamics by nontrivial sphere
coverage and from generic unitary/Haar behavior by a stable selected axis.
Whether field matching and limited scrambling are causal parts of the motif is
**CONJECTURAL**.
Current Sobol evidence narrows the motif: breaking both pointer-QND and
central-X conservation is necessary for two-dimensional support in the tested
classes, but once support exists, suppression of higher odd multipoles is a
separate and currently unexplained property.

### Highest-value next theorem

Prove or falsify a controlled statement connecting the conditional detector
unitaries and transverse-coupling scaling to suppression of odd multipoles,
for example sufficient spectral/mixing conditions implying
`sum_{l>=3} P_l / P_odd -> 0` while the dipole tends to the selected axis.
The theorem must leave the separate physical root-selection measure explicit.

Current evidence therefore distinguishes the best finite Born-like examples
by full-sphere support, a stable preferred axis, controlled transverse mixing,
and unusually small higher-odd content—not by unitarity, interaction,
decoherence, QND structure, or scrambling alone. These features are not yet a
sufficient microscopic criterion, and equal-root weighting is not generally
refinement-noncontextual. The decisive classification remains **HPC
CALCULATION REQUIRED**.
