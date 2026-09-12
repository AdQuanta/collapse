# Relative-Unitary Evolution

## The Construction
The launchepad for all "Special State" analysis is the partitioning of the system's evolution operator $U(t) = e^{-iHt}$ into blocks:
$$ U(t) = \begin{pmatrix} A & B \\ C & D \end{pmatrix} $$
where the partition is defined by the central qubit's $Z$ basis.

## The Relative Propagator
The "Relative Propagator" is the operator $W = A^{-1} C$. Its eigenvalues are the projective roots $\lambda$ of the pencil $(C, A)$.
- **Physical Meaning**: A root $\lambda$ defines an initial qubit state $|\phi_0(\lambda)\rangle$ that is perfectly disentangled from the detector at time $t$.
- **Effective Dynamics**: In the $X$-conserving class ($[H, X_q] = 0$), the dynamics reduce to the study of the unitary operator $W = U_+^\dagger U_-$, where $U_\pm$ are the conditional detector evolutions.

## Mapping to the Bloch Sphere
The complex roots $\lambda$ are mapped to polar angles $\theta$ via:
$$ \theta = 2 \arctan |\lambda| $$
The distribution of these $\theta$ values over the ensemble of detector states determines whether the Hamiltonian is "Born-like."

See also: [[projective-roots]], [[born-like-points]].
