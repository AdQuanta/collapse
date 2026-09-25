 # Equivalence of the Fixed-Input and Outcome Pencils

> Sources: User instruction, 2026-09-21; Repository execution, 2026-09-21
> Raw: [Fixed-input/outcome equivalence](../../raw/campaigns/2026-09-21-fixed-input-outcome-equivalence.md); [Outcome antipodality verification](../../raw/campaigns/2026-09-21-outcome-antipodality-verification.md)
> Updated: 2026-09-21

The production Born pipeline solves a different pencil from the one `SPEC.md` §3 writes down. It solves the block-*column* pencil $U_{10}v=zU_{00}v$, in which the qubit starts in $|0\rangle$ and the question is whether the output factorizes; the specification defines collapsibility through the block-*row* pencils, in which the input qubit ray varies and the output is required to be a definite outcome. The two are nevertheless the same characterization. They are exchanged by time reversal, and whenever the model is time-reversal invariant they differ only by complex conjugation, which leaves every polar quantity fixed. This page proves both statements and marks the one corner of the approved families where the second fails.

## Statement

Write $U$ qubit-first with blocks $U_{ba}$. The **fixed-input** roots are the projective solutions of $U_{10}v=zU_{00}v$; the **outcome-$b$** roots are the [[projective-roots]] solutions of $(U_{10}+\lambda U_{11})|D\rangle=0$ and $(U_{00}+\lambda U_{01})|D\rangle=0$.

> **Theorem (time-reversal duality).** For every unitary $U$ on $\mathbb C^2\otimes\mathcal H_D$, the fixed-input characterization of $U$ is the outcome-0 characterization of $U^{\dagger}$ — the same projective roots with the same kernel dimensions.

> **Corollary (equality under time-reversal symmetry).** If $U^{T}=U$, equivalently if $H$ is real in the computational basis, then the fixed-input roots of $U$ are the complex conjugates of its outcome-0 roots, with equal kernel dimensions. Radii are identical; azimuths are mirrored.

## Proof of the duality

Let $z$ be a fixed-input root with kernel vector $v$. Then

$$U\big(|0\rangle\otimes v\big)=|0\rangle\otimes U_{00}v+|1\rangle\otimes U_{10}v=\big(|0\rangle+z|1\rangle\big)\otimes U_{00}v,$$

so writing $|D'\rangle=U_{00}v$ and applying $U^{\dagger}$,

$$U^{\dagger}\big(|\psi_q(z)\rangle\otimes|D'\rangle\big)\ \propto\ |0\rangle\otimes v,$$

which is exactly the definition of a state exactly collapsible to outcome 0 for the unitary $U^{\dagger}$, at the projective point $z$. Conversely, if $U^{\dagger}(|\psi_q(\lambda)\rangle\otimes|D\rangle)=|0\rangle\otimes|D''\rangle$ then $U(|0\rangle\otimes|D''\rangle)=|\psi_q(\lambda)\rangle\otimes|D\rangle$, which forces $U_{10}|D''\rangle=\lambda U_{00}|D''\rangle$ and $|D\rangle\propto U_{00}|D''\rangle$.

The correspondence $v\mapsto U_{00}v$ is linear and injective on the fixed-input kernel: if $U_{00}v=0$ while $U_{10}v=zU_{00}v$, then $U(|0\rangle\otimes v)=0$, which is impossible for $v\neq0$ under a unitary. The converse supplies surjectivity. The kernel dimensions therefore agree ray by ray, and the argument is homogeneous, so it covers $\lambda=\infty$ without a special case. $\blacksquare$

Physically the duality says the two pencils ask the same question with the arrow of time reversed. The fixed-input pencil asks which initial detector states disentangle from a qubit prepared in $|0\rangle$; the outcome pencil asks which initial qubit rays are driven to a definite outcome. Running the propagator backwards turns one into the other.

## Proof of the corollary

$U=e^{-iHT}$ satisfies $U^{T}=U$ if and only if $H^{T}=H$; a Hermitian $H$ has $H^{T}=\overline H$, so this holds if and only if $H$ is real. In that case $U_{01}^{T}=U_{10}$, and because $\det M=\det M^{T}$ and $\dim\ker M=\dim\ker M^{T}$, the outcome-1 pencil may be transposed without changing its roots or weights:

$$\big(U_{00}+\lambda U_{01}\big)^{T}=U_{00}+\lambda U_{10}=-\lambda\left(U_{10}-\Big(-\tfrac1\lambda\Big)U_{00}\right).$$

The outcome-1 roots are therefore the fixed-input roots under $z=-1/\lambda_1$. Composing with the antipodal pairing of [[outcome-antipodality]], $\lambda_1=-1/\overline{\lambda_0}$,

$$z=-\frac{1}{\lambda_1}=-\frac{1}{-1/\overline{\lambda_0}}=\overline{\lambda_0}. \qquad\blacksquare$$

## Why this settles the scoring question

Conjugation preserves modulus, so $|z|=|\lambda_0|$ and the two polar root laws are the same law. Together with [[outcome-antipodality]], which supplies $\rho_1^{(\theta)}(\theta)=\rho_0^{(\theta)}(\pi-\theta)$, this closes the chain that [[born-like-points]] requires before a single reflected histogram may be read as the specification's weak ratio. The scoring `born_ratio_from_theta(theta, pi - theta)` applied to fixed-input radii computes the weak Born criterion itself. Every $S_{\mathrm{Born}}$ in the repository is the specification quantity rather than an approximation to it, for every Hamiltonian in the approved families carrying no single-site $Y$ term.

An earlier session in this repository recorded the opposite conclusion — that the pipeline used a surrogate observable — on the strength of a Haar-unitary counterexample, where the two root sets genuinely differ because a Haar unitary is not symmetric. That claim is withdrawn; the counterexample is outside the approved families.

## Where the corollary fails

$U^{T}=U$ fails exactly when a single-site $Y$ operator is present. Every other term in the approved families of [[hamiltonian-families]] — $Z_iZ_j$, $X_iX_j$, $Y_iY_j$, $Z_0Z_i$, $X_0X_i$, $Y_0Y_i$, $X_i$, $Z_i$ — is real in the computational basis, so the $h_y$ and $h_{0y}$ self-fields added on 2026-09-20 are the sole exception.

This matters in practice because the `screen_00` region of [[chain-born-regions]] carries $h_{0y}=-1.69$ as its only imaginary term. There the duality still holds but the corollary does not, and the two measures genuinely differ: a 2.706e-02 gap in sorted radii at $N=5$, $t=211$, and an $S_{\mathrm{Born}}$ gap of 0.0224, 0.0097 and 0.0030 at $N=6,8,10$ on the frozen six-time window. The gap shrinks with size, consistent with one qubit-local breaking term among $N+1$ sites, but that is a measurement and not an asymptotic result.

## What the theorem does not give

- **The azimuths are mirrored, not preserved.** A full-sphere measure built from the fixed-input pencil is the true one reflected through the $xz$ plane, so the transverse components of an estimated preferred basis come out sign-flipped unless the roots are conjugated first. The strong criterion of [[born-like-points]] is sensitive to this; the weak criterion is not.
- **It pairs roots and kernel dimensions, not detector states.** The collapsible detector state at a fixed-input root is $v$, while the paired outcome-0 state is $U_{00}v$; these are different vectors.
- **It makes neither Born criterion true** and grants no paper-readiness gate. It removes a conditional from the interpretation of existing scores without supplying evidence about their values.

## Numerical certification

`tests/test_fixed_input_outcome_equivalence.py` certifies both statements in the form used here: 14 passed. On Haar unitaries of matrix dimension 8 (seeds 7, 11, 23) the duality is exact: the fixed-input roots of $U$ and the outcome-0 roots of $U^{\dagger}$ agree to `0.000e+00`, while the fixed-input and outcome-0 roots of the same $U$ differ by 3.043, 2.789 and 1.799.

A 36-cell sweep of both approved families — `connectivity` in {ring, chain}, `central_coupling` in {all, first}, $N\in\{3,4,5\}$, $t\in\{1,37,211\}$ — certifies the corollary. With the $Y$ self-fields off the worst $\max|U-U^{T}|$ is 1.665e-16, the worst $|z-\overline{\lambda_0}|$ is 8.265e-14 and the worst sorted-radii gap is 5.662e-14. With $h_y=0.7$ and $h_{0y}=-1.69$ the same sweep gives 1.026, 2.670 and 1.541e-01. On a Haar unitary the conjugation map gives 1.442, so the agreement is produced by the symmetry rather than by the map being vacuous.

At $N=5$, $t=211$ on the `screen_00` parameters with $h_{0y}$ set to zero, `characterize_pencil_roots` returns `regular` with 32 distinct roots and total kernel weight 32 on both pencils, and $|z-(-1/\lambda_1)|$ is 7.130e-10, confirming the intermediate step of the proof separately from its conclusion.

## Status

**PROVED.** The duality is unconditional; the corollary holds exactly for time-reversal-invariant members of the approved families and fails only on the $Y$ self-fields. No gate is promoted and `paper_ready` remains `false`.

See also: [[outcome-antipodality]], [[projective-roots]], [[born-like-points]], [[homogeneous-qz]], [[relative-evolution]], [[chain-born-regions]].
