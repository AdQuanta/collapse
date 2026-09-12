# The Relative Propagator

The relative propagator is the central mathematical object used to identify "special states"—initial qubit states that result in perfect disentanglement from the detector at a specific time $t$.

## Mathematical Construction
Given the system's evolution operator $U(t) = e^{-iHt}$, we partition it into blocks according to the central qubit's $Z$-basis:
$$ U(t) = \begin{pmatrix} A & B \\ C & D \end{pmatrix} $$
where $A, B, C, D$ are operators acting on the detector's Hilbert space.

The **relative propagator** $W$ is defined as:
$$ W = A^{-1} C $$
The eigenvalues $\lambda$ of $W$ are precisely the projective roots of the pencil $(C, A)$.

## Physical Interpretation
A root $\lambda$ corresponds to an initial qubit state:
$$ |\phi_0(\lambda)\rangle = \frac{|0\rangle + \lambda|1\rangle}{\sqrt{1 + |\lambda|^2}} $$
which, at time $t$, evolves into a state that is a product state between the qubit and the detector. This represents a moment of "collapse" or "disentanglement" for that specific input state.

## Relation to the Bloch Sphere
The complex root $\lambda$ is mapped to the Bloch sphere's polar angle $\theta$ via:
$$ \theta = 2 \arctan |\lambda| $$
The ensemble of all such $\lambda$ for a given Hamiltonian and time $t$ forms a point process on the Bloch sphere. The project's primary goal is to determine whether this distribution approximates the Born rule's $\cos^2(\theta/2)$ density.

## Special Cases
- **X-Conserving Class**: If $[H, X_q] = 0$, the dynamics simplify. $W$ becomes the relative unitary $U_+^\dagger U_-$, where $U_\pm$ are the conditional detector evolutions.
- **Pointer-QND**: In the strict QND limit $[H, Z_q] = 0$, $C=0$, meaning $W=0$. The only roots are at $\lambda=0$, corresponding to the north pole of the Bloch sphere.

See also: [[projective-roots]], [[born-like-points]], [[relative-evolution]].
