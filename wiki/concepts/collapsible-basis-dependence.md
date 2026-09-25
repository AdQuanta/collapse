# Basis Dependence of Collapsible States

> Sources: `SPEC.md` v1.0, 2026-09-15; Repository derivation and audit, 2026-09-21; Preferred-basis campaign, 2026-09-21
> Raw: [Output-basis dependence derivation and audit](../../raw/campaigns/2026-09-21-collapsible-output-basis-dependence.md)
> Updated: 2026-09-21

A collapsible state is defined relative to a choice of qubit *output* basis, and the choice is not cosmetic: changing it changes both the collapsible input rays and the collapsible detector states. This page derives the transformation law, shows that the input basis is by contrast inert, counts the resulting correspondence, records what survives the change, and derives the self-consistency condition the `SPEC.md` §12 preferred axis must satisfy. It closes with an audit showing that the production estimator solves a lab-frame pencil while fitting a free axis, so that condition is not currently imposed.

## Conventions

Qubit-first blocks $U=\begin{pmatrix}A&B\\C&D\end{pmatrix}$ with $A=U_{00}$, $B=U_{01}$, $C=U_{10}$, $D=U_{11}$, each of size $d=\dim\mathcal H_D$, as `core/projective_roots.py::split_qubit_first_blocks` returns them. An input ray $[\alpha:\beta]$ carries the qubit ket $\beta|0\rangle+\alpha|1\rangle$ with $z=\alpha/\beta$. Define the **branch operators**

$$
N_0(\alpha,\beta)=\beta A+\alpha B,
\qquad
N_1(\alpha,\beta)=\beta C+\alpha D,
$$

so that $U|\Psi_{\rm in}\rangle=|0\rangle\otimes N_0|D\rangle+|1\rangle\otimes N_1|D\rangle$. The input is collapsible to outcome $b$ exactly when the other branch is killed, $N_{1-b}|D\rangle=0$. For outcome $0$ this is $(C+zD)\eta=0$, which is what `forward_pole_root_spectrum` solves; $N_{1-b}$ is the forbidden branch $\widehat M_b$ of [[outcome-antipodality]].

## The output-basis transformation law

Let the output basis be $|b_{\mathbf n}\rangle=V|b\rangle$ for $V\in SU(2)$. Collapsibility to $b$ in that basis is $(\langle b'_{\mathbf n}|\otimes I)U|\Psi_{\rm in}\rangle=0$ for the other branch $b'$, and since $\langle b'_{\mathbf n}|=\langle b'|V^\dagger$,

$$
(\langle b'_{\mathbf n}|\otimes I)\,U=(\langle b'|\otimes I)\,(V^{\dagger}\otimes I)U .
$$

**Changing the qubit output basis is exactly replacing $U$ by $U^{(\mathbf n)}=(V^{\dagger}\otimes I)U$** — physically, appending a qubit-only gate at readout, with the detector untouched.

Writing $V^{\dagger}=(w_{bc})$, the branch operators transform as a two-component spinor with operator-valued entries,

$$
\boxed{\;N_b^{(\mathbf n)}(\alpha,\beta)=w_{b0}\,N_0(\alpha,\beta)+w_{b1}\,N_1(\alpha,\beta)\;}
$$

so the new outcome-$0$ pencil is

$$
N_1^{(\mathbf n)}=\beta\,(w_{10}A+w_{11}C)+\alpha\,(w_{10}B+w_{11}D).
$$

This is a pencil on a *different* pair of matrices — independent linear combinations of all four blocks. Two consequences follow immediately. There is no Bloch rotation $R$ with $z_j^{(\mathbf n)}=R\cdot z_j$, so the root set is not a rigid rotation of the old one; and $\ker N_1^{(\mathbf n)}$ is the kernel of a different operator, so the collapsible **detector** states change as well. The collapsible set is output-basis dependent in both of its factors.

## The input basis is inert

`SPEC.md` §2 defines collapsibility as $U(T)|\Psi_{\rm in}\rangle=|b\rangle\otimes|D_b'\rangle$. The condition names no input basis: $|\psi\rangle$ is simply a vector in $\mathbb C^2$. A change of input basis, $U\mapsto U(W\otimes I)$, relabels the coordinates $z$ of the same rays and rotates the Bloch root cloud rigidly, leaving the collapsible set invariant.

The asymmetry is structural. The input side is a continuum, $\mathbb{CP}^1$, which needs coordinates but no choice; the output side is a discrete two-outcome alternative, which needs a choice, and the choice changes the set. The `SPEC.md` §12 preferred axis is therefore an **output**-side object. This is why it must be identified rather than assumed, and it is the general form of the scope limitation [[commuting-qnd-sector]] already records for its own no-go.

## The collapsible correspondence has bidegree $(d,d)$

Fix an input ray and ask which output axes make it collapsible. The condition is

$$
\det\!\big(w_{10}N_0(\alpha,\beta)+w_{11}N_1(\alpha,\beta)\big)=0,
$$

a homogeneous binary form of degree $d$ in $(w_{10}:w_{11})$, hence generically $d$ roots in $\mathbb{CP}^1$ — that is, **$d$ output directions**. Dually, a fixed output axis admits $d$ input rays. The collapsible locus is a curve of bidegree $(d,d)$ in $\mathbb{CP}^1_{\rm in}\times\mathbb{CP}^1_{\rm out}$, and choosing an output basis is slicing it one way rather than the other.

Two degenerate checks confirm the count. At $d=1$ (no detector, $U\in U(2)$) the branch operators are scalars and $w_{10}N_0+w_{11}N_1=0$ has the single solution $(N_1:-N_0)$, the unique axis through $U|\psi\rangle$ — correct, since a single-qubit state is a basis state in exactly one basis. At $U=I$ one has $N_0=\beta I$, $N_1=\alpha I$, so the outcome-$0$ pencil $\alpha I$ has the root $z=0$ with kernel dimension $d$ (every $|D\rangle$ works), and for a fixed ray $\det(w_{10}\beta+w_{11}\alpha)^d=0$ gives the axis containing $|\psi\rangle$ with multiplicity $d$.

The interpretation matters for how the project's target is read: **the existence of collapsible states is generic and carries no physics on its own.** Every input ray is collapsible for $d$ suitable output axes. The content of `SPEC.md` §12 is that one single axis should serve a whole cloud of input rays *with Born statistics*.

## What survives a change of output basis

**Antipodality is basis-covariant.** The theorem of [[outcome-antipodality]] is proved for every unitary with no family restriction, and $U^{(\mathbf n)}=(V^\dagger\otimes I)U$ is unitary whenever $U$ is. So outcome $0_{\mathbf n}$ and $1_{\mathbf n}$ remain antipodally paired with equal kernel dimensions in every output basis, and $\rho_1=\mathcal A_*\rho_0$ holds throughout.

**$B_1$ is invariant under input rotation.** With $S=\sum_j k_j\mathbf u_j\mathbf u_j^{\mathsf T}$ and $\mathbf m=\sum_j k_j\mathbf u_j$, an input rotation $R$ sends $S\mapsto RSR^{\mathsf T}$ and $\mathbf m\mapsto R\mathbf m$, so

$$
\hat{\mathbf n}_{\rm raw}\;\mapsto\;(RSR^{\mathsf T})^{-1}R\mathbf m=RS^{-1}R^{\mathsf T}R\mathbf m=R\,\hat{\mathbf n}_{\rm raw},
$$

using $R^{-\mathsf T}=R$ and $R^{-1}=R^{\mathsf T}$. The fitted axis rotates with the cloud and $B_1=\|\hat{\mathbf n}_{\rm raw}\|$ is unchanged. This is the expected covariance and is a useful check on the estimator.

**$B_1$ is not invariant under output-basis change**, because the cloud is then a different point set. $B_1$ is a function of the output basis, $B_1=B_1(\mathbf n)$, and the same is true of every diagnostic built from the cloud.

## The preferred basis is a fixed point

Born's rule measures the angle from the outcome direction itself,

$$
P(0_{\mathbf n}\mid\psi)=|\langle 0_{\mathbf n}|\psi\rangle|^{2}=\cos^{2}\!\frac{\theta_{\mathbf n}}{2},
$$

with $\theta_{\mathbf n}$ the Bloch angle between $\psi$ and $\mathbf n$. The `SPEC.md` §5.1 target $p_0(\Omega)=\cos^2(\theta/2)$ is therefore a Born statement only when $\theta$ is measured from the same axis that *defines* outcome $0$. Writing $\Phi(\mathbf n)=\hat{\mathbf n}_{\rm fit}\big(\mathcal C_0(\mathbf n)\big)$ for the axis fitted from the outcome-$0$ cloud of the pencil built in output basis $\mathbf n$, the preferred basis must satisfy

$$
\boxed{\;\Phi(\mathbf n_\ast)=\mathbf n_\ast\;}
$$

Read against `SPEC.md` §12, uniqueness up to $\mathbf n_\ast\leftrightarrow-\mathbf n_\ast$ is uniqueness of this fixed point up to outcome relabelling, and the stability requirement is that the fixed point be attracting. The condition also supplies an algorithm — fixed-point iteration $\mathbf n_{k+1}=\Phi(\mathbf n_k)$, costing one pencil solve plus one $3\times3$ solve per step — in place of a search over $S^2$.

## What the implementation currently does

Audited on 2026-09-21. `core/projective_roots.py::forward_pole_root_spectrum(unitary, outcome, **solver_options)` takes no basis argument and uses $(D,-C)$ for outcome $0$ and $(B,-A)$ for outcome $1$: the lab-frame $\hat z$ output basis, hardcoded. The campaign path does not rotate the propagator before calling it: `scripts/eval_preferred_basis.py` passes the propagator as returned by `unitary_at_time`, and `core/outcome_measures.py::preferred_axis_from_cloud` then fits $\hat{\mathbf n}$ freely, with the §6 quartet evaluated at that fitted axis.

The rotation itself is already implemented in the repository, and implemented in exactly the form derived above. `scripts/h0_basis_outcome_clouds.py::rotate_qubit0_output_basis` builds $(R^\dagger\otimes I)U$ by combining the blocks as `rotated[:half] = r00*top + r01*bottom`, `rotated[half:] = r10*top + r11*bottom` — an independent confirmation of the spinor law. Its own docstring records that it is "not part of the frozen goal_preferred_basis.md campaign machinery, which is left untouched", and that it serves two ad hoc $\mathbf h_0$-rotation figure scripts. The capability exists; the measurement path does not use it.

So the **scoring** axis rotates while the **pencil's** output basis does not. In the language above, $\Phi$ is evaluated once, at $\mathbf n=\hat z$, and its output is not fed back, so the fixed-point condition is not imposed. The diagnostic that would expose the gap, $\hat{\mathbf n}\cdot\hat z$, is not reported; [[preferred-basis-campaign]] reports $\hat{\mathbf n}\cdot\hat{\mathbf h}_0$ instead. The estimator cannot detect the mismatch unaided: a cloud that happens to be Born about some axis other than the pencil's output axis returns $B_1=1$ at that other axis, which is not Born's rule for the measurement being described.

This is the general form of a scope limitation already recorded, for one family, in [[commuting-qnd-sector]]: "The no-go assumes the Z outcome basis. SPEC.md requires the preferred axis to be identified rather than assumed."

## An alternative reading of WP5, and why it survives only as a confound

[[preferred-basis-campaign]] WP5 rotates $\mathbf h_0$ at fixed $|\mathbf h_0|=2.9527$ and reports $B_1$ at $N=8$ of $0.0417$, $0.4485$, $1.0108$, $1.3018$ and $1.4530$ for $\mathbf h_0\parallel x$, $\parallel y$, $\parallel z$, the `screen_00` direction and "generic 3". `RESEARCH_STATE.md` reads the pattern as pointing at the detector's own distinguished axis, while noting that three points cannot establish it.

The misalignment $\hat{\mathbf n}\cdot\hat z$ is recoverable from published numbers for two of those rows. For $\mathbf h_0\parallel z$, $\hat{\mathbf n}\cdot\hat{\mathbf h}_0=1.0000$ and $\hat{\mathbf h}_0=\hat z$, so the fitted axis coincides with the pencil's output axis, and $B_1=1.0108$. For `screen_00`, whose self-field is $h_{0x}=-1.35$, $h_{0y}=-1.69$, $h_{0z}=+2.01$, one has $\hat{\mathbf h}_0\cdot\hat z=2.01/2.9527=0.6807$, about $47^\circ$ from $\hat z$; with $\hat{\mathbf n}\cdot\hat{\mathbf h}_0=0.9997$ the fitted axis sits about $47^\circ$ from the output axis, and $B_1=1.3018$. For $\mathbf h_0\parallel x$ and $\parallel y$ only $\hat{\mathbf n}\cdot\hat{\mathbf h}_0$ is published ($-0.063$, $0.001$), which confines $\hat{\mathbf n}$ to a plane without fixing $\hat{\mathbf n}\cdot\hat z$.

Those two rows invite the reading that $B_1$ tracks misalignment between the fitted axis and the hardcoded output axis, which would make the $x$ and $y$ nulls a basis artifact rather than a mechanism.

> **Status: Disputed**, and largely resolved *against* the misalignment reading.
> The campaign's own centre series settles it. At `screen_00` the misalignment is fixed at about $47^\circ$ — the self-field does not move and $\hat{\mathbf n}\cdot\hat{\mathbf h}_0$ stays at $0.9997$ — yet $B_1$ runs $1.3018\to1.1496\to0.8795$ at $N=8,10,12$, crossing *through* $1$. $B_1$ is therefore not a function of misalignment, and the misalignment reading cannot account for the WP5 pattern on its own. It survives only as a **confound** on fixed-$N$ comparisons between cells whose fitted axes sit at different angles to $\hat z$ — which is what WP5 is. The detector-axis reading of `RESEARCH_STATE.md` is not refuted here.

The fixed-point condition does not rest on this reading. It is definitional: whatever sets the value of $B_1$, a cloud scored about an axis other than the one defining the outcome is not being scored against Born's rule. That holds at every $N$ and for every cell, including the $N=12$ centre point where $B_1$ passes below $1$.

The confound is cheap to remove: rebuild the pencil with $U\mapsto(V^\dagger\otimes I)U$ for $V$ carrying $\hat z$ to the fitted axis, then re-fit. Doing so at the $\mathbf h_0\parallel x$ cell tests the artifact question directly; doing so at the centre makes the $N=8,10,12$ series a like-for-like comparison of Born scores rather than of clouds scored off-axis.

## Status

The transformation law, the inertness of the input basis, the bidegree-$(d,d)$ count, the invariance table and the fixed-point condition are **derivations**, unconditional in dimension, Hamiltonian family, regularity, degeneracy and defectiveness. They are not yet covered by a test or a frozen verifier, and the one helper that implements the output-basis rotation, `scripts/h0_basis_outcome_clouds.py::rotate_qubit0_output_basis`, sits outside the campaign path by its own documentation. The implementation audit is a reading of code as of 2026-09-21. The WP5 misalignment reading is explicitly disputed above and demoted to a confound.

**No gate is promoted and `paper_ready` remains `false`.** Two consequences for the campaign follow: $\hat{\mathbf n}\cdot\hat z$ should be reported alongside $\hat{\mathbf n}\cdot\hat{\mathbf h}_0$, since it is the alignment the Born reading actually requires; and closing the fixed-point loop is a prerequisite for reading any $B_1$ — above, below, or at $1$ — as a Born score. The second is cheaper than it sounds, since the rotation helper already exists and need only be wired into the evaluation path and iterated.

See also: [[projective-roots]], [[outcome-antipodality]], [[born-like-points]], [[fixed-input-outcome-equivalence]], [[preferred-basis-campaign]], [[commuting-qnd-sector]], [[research-specification-v1]].
