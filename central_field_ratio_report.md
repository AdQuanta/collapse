# Central-Field Ising Bath Ratio Derivation

This note gives a self-contained derivation of the angle distribution and
ratio

```math
B(\theta,t)=\frac{P(\theta,t)}{P(\theta,t)+P(\pi-\theta,t)}
```

for the central-spin Ising bath in the two cases `hz0 = 0` and
`hz0 = hz`.  The coupling is scaled as

```math
g=\frac{J_x}{\sqrt N}.
```

The main conclusion is:

- For \(h_{z0}=0\), the angle is a folded unitary phase.  At fixed time
  the large-\(N\), \(J_x/\sqrt N\) limit gives a wrapped Gaussian phase
  law.  Long-time histograms are time-mixtures of such folded wrapped
  Gaussians, and are not Born-like in the tested regime.
- For \(h_{z0}=h_z\), matched-field resonances produce tangent poles and
  a heavy \(x^{-2}\) eigenvalue-radius tail.  The Born-like ratio comes
  from an additional reciprocal closed-loop envelope.

The second statement is deliberately phrased as "Born-like" rather than
"exact Born".  Exact Born behavior for the ratio requires a precise
reciprocity condition on the eigenvalue-radius density.  The Hamiltonian
derivation explains why this condition is natural in the matched-field
case, and simulations support it approximately, but it is stronger than
the mere existence of the resonant heavy tail.

## Model and Spectral Object

Consider

```math
H
=H_B+h_{z0}Z_0+gX_0V,
\qquad
g=\frac{J_x}{\sqrt N},
```

where

```math
H_B
=J\sum_{i=1}^N Z_iZ_{i+1}
+h_z\sum_{i=1}^N Z_i,
\qquad
V=\sum_{i=1}^N X_i.
```

Periodic bath boundary conditions are assumed:

```math
Z_{N+1}=Z_1.
```

Write the unitary in central-spin \(Z_0\)-blocks:

```math
U(t)=e^{-iHt}
=
\begin{pmatrix}
U_{00}(t)&U_{01}(t)\\
U_{10}(t)&U_{11}(t)
\end{pmatrix}.
```

The relevant nonunitary bath operator is

```math
M(t)=U_{00}^{-1}(t)U_{10}(t),
```

or equivalently the generalized eigenvalue problem

```math
U_{10}(t)v=\lambda(t)U_{00}(t)v.
```

Define

```math
x=|\lambda|=\tan\frac{\theta}{2},
\qquad
0\le \theta\le \pi.
```

Let \(q(x,t)\) be the density of \(x\).  Since

```math
\frac{dx}{d\theta}
=\frac{1+x^2}{2},
```

the angle density is

```math
P(\theta,t)
=q(x,t)\frac{1+x^2}{2}.
```

The transformation \(\theta\mapsto \pi-\theta\) sends

```math
x\mapsto \frac1x.
```

Therefore

```math
P(\pi-\theta,t)
=q(1/x,t)\frac{1+x^2}{2x^2}.
```

Hence the ratio is exactly

```math
\boxed{
B(\theta,t)
=
\frac{q(x,t)}
{q(x,t)+x^{-2}q(1/x,t)}
}.
```

The Born ratio is

```math
B_{\rm Born}(\theta)
=\cos^2\frac{\theta}{2}
=\frac{1}{1+x^2}.
```

Equating this to the exact ratio gives the sharp criterion

```math
\boxed{
q(1/x,t)=x^4q(x,t).
}
```

Thus any analytic derivation of a Born-like ratio must explain an
approximate reciprocal relation of this form.  A heavy tail alone is not
enough.

## General Dyson Expansion

In the central \(Z_0\)-basis,

```math
H=
\begin{pmatrix}
D_+&gV\\
gV&D_-
\end{pmatrix},
\qquad
D_\pm=H_B\pm h_{z0}.
```

Let

```math
H_d=
\begin{pmatrix}
D_+&0\\
0&D_-
\end{pmatrix},
\qquad
H_x=
\begin{pmatrix}
0&gV\\
gV&0
\end{pmatrix}.
```

The off-diagonal block of \(e^{-i(H_d+H_x)t}\) has only odd powers of
\(g\).  To first order,

```math
U_{10}(t)
=
-ig\int_0^t
e^{-iD_-(t-\tau)}
V
e^{-iD_+\tau}\,d\tau
+O(g^3).
```

The diagonal block is

```math
U_{00}(t)=e^{-iD_+t}+O(g^2),
\qquad
U_{00}^{-1}(t)=e^{iD_+t}+O(g^2).
```

Multiplying gives

```math
M(t)
=
-ig\int_0^t
e^{iD_+t}
e^{-iD_-(t-\tau)}
V
e^{-iD_+\tau}\,d\tau
+O(g^3).
```

Because \(D_\pm=H_B\pm h_{z0}I\),

```math
\boxed{
M(t)
=
-ig\int_0^t
e^{2ih_{z0}(t-\tau)}
e^{iH_B\tau}
V
e^{-iH_B\tau}\,d\tau
+O(g^3).
}
```

Now use the bath \(Z\)-basis

```math
|s\rangle=|s_1,\ldots,s_N\rangle,
\qquad
s_i=\pm1.
```

Then

```math
H_B|s\rangle=E_s^{(B)}|s\rangle,
```

where

```math
E_s^{(B)}
=J\sum_i s_is_{i+1}
+h_z\sum_i s_i.
```

Let \(s^{(k)}\) denote the configuration obtained from \(s\) by flipping
\(s_k\).  Since \(V=\sum_iX_i\), the first-order matrix element is
nonzero only between \(s\) and \(s^{(k)}\):

```math
\boxed{
\langle s^{(k)}|M(t)|s\rangle
=
g e^{2ih_{z0}t}
\frac{e^{-i\delta_{sk}t}-1}{\delta_{sk}}
+O(g^3),
}
```

with

```math
\delta_{sk}
=
2h_{z0}+E_s^{(B)}-E_{s^{(k)}}^{(B)}.
```

Only the field term at \(k\) and the two adjacent Ising bonds change when
\(s_k\) flips.  Thus

```math
E_s^{(B)}-E_{s^{(k)}}^{(B)}
=
2s_k\bigl[h_z+J(s_{k-1}+s_{k+1})\bigr],
```

so

```math
\boxed{
\delta_{sk}
=
2h_{z0}
+2s_k\bigl[h_z+J(s_{k-1}+s_{k+1})\bigr].
}
```

This denominator is the local object that distinguishes the two cases.

## Case I: No Central Field, \(h_{z0}=0\)

When \(h_{z0}=0\),

```math
H=H_B\otimes I_0+gX_0\otimes V.
```

This has an exact simplification in the central \(X_0\)-basis.  There,
the central spin labels two bath Hamiltonians:

```math
H_\pm=H_B\pm gV,
\qquad
U_\pm(t)=e^{-it(H_B\pm gV)}.
```

Returning to the central \(Z_0\)-basis gives

```math
U_{00}=\frac{U_++U_-}{2},
\qquad
U_{10}=\frac{U_+-U_-}{2}.
```

Define the unitary relative evolution

```math
A(t)=U_-^{-1}(t)U_+(t).
```

Then

```math
\begin{aligned}
M(t)
&=U_{00}^{-1}U_{10} \\
&=(U_++U_-)^{-1}(U_+-U_-) \\
&=(A+I)^{-1}(A-I).
\end{aligned}
```

This identity is exact.  Because \(A(t)\) is unitary, write its
eigenvalues as

```math
A(t)\psi_j=e^{i\alpha_j(t)}\psi_j.
```

Then

```math
\lambda_j(t)
=
\frac{e^{i\alpha_j(t)}-1}{e^{i\alpha_j(t)}+1}
=
i\tan\frac{\alpha_j(t)}{2}.
```

Therefore

```math
\theta_j(t)
=
2\arctan|\lambda_j(t)|
=
2\arctan\left|\tan\frac{\alpha_j(t)}{2}\right|.
```

Thus the no-central-field angle distribution is exactly a folded
eigenphase distribution of the unitary \(A(t)\).  It is not a direct
resonant-radius distribution.

### Large-\(N\) Phase Cumulants

Differentiate \(A(t)=U_-^{-1}(t)U_+(t)\):

```math
\dot A(t)=-2ig\,V_-(t)A(t),
```

where

```math
V_-(t)=U_-^{-1}(t)VU_-(t).
```

Hence

```math
A(t)
=
\mathcal T
\exp\left[
-2ig\int_0^tV_-(\tau)\,d\tau
\right].
```

At leading order in \(g\), replace \(V_-(t)\) by the bath-Heisenberg
operator

```math
V_B(t)=e^{iH_Bt}Ve^{-iH_Bt}.
```

The cumulants of the phase are built from connected normalized traces
over the finite bath Hilbert space,

```math
\frac{1}{2^N}\operatorname{Tr}_B(\cdots).
```

This trace is only a Hilbert-space counting average.  No physical
temperature or thermodynamic ensemble is being introduced.

Because \(V_B(t)=\sum_i X_i(t)\) is a sum of \(N\) translated local
terms, the connected normalized trace of \(m\) such sums scales as
\(O(N)\), away from special degeneracies.  Thus

```math
\kappa_m(t)=O(Ng^m)
=O\left(J_x^mN^{1-m/2}\right).
```

With \(g=J_x/\sqrt N\),

```math
\kappa_2=O(1),
\qquad
\kappa_{m\ge3}\to0.
```

So the fixed-time large-\(N\) phase law is Gaussian on the circle.

The variance is

```math
\sigma_0^2(t)
=
4J_x^2
\int_0^t\int_0^t
C(\tau-\tau')\,d\tau\,d\tau',
```

where

```math
C(u)=
\frac{1}{N2^N}
\operatorname{Tr}_B\bigl[V_B(u)V\bigr].
```

For the Ising bath, a single spin flip has local frequency

```math
\Omega=2s_k\bigl[h_z+J(s_{k-1}+s_{k+1})\bigr].
```

Counting the possible values of \(s_{k-1}+s_{k+1}\) gives

```math
C(u)
=
\frac12\cos(2h_zu)
+\frac14\cos((2h_z+4J)u)
+\frac14\cos((2h_z-4J)u).
```

Therefore

```math
\boxed{
\sigma_0^2(t)
=
8J_x^2
\sum_a w_a
\frac{1-\cos(\Omega_at)}{\Omega_a^2},
}
```

with

```math
(\Omega_a,w_a)
=
(2h_z,1/2),
\quad
(2h_z+4J,1/4),
\quad
(2h_z-4J,1/4).
```

The fixed-time phase density is the wrapped Gaussian

```math
W_{\sigma_0}(\alpha,t)
=
\frac{1}{2\pi}
\sum_{n\in\mathbb Z}
e^{-n^2\sigma_0^2(t)/2}e^{in\alpha}.
```

Equivalently,

```math
W_{\sigma_0}(\alpha,t)
=
\frac{1}{\sqrt{2\pi\sigma_0^2(t)}}
\sum_{\ell\in\mathbb Z}
\exp\left[
-\frac{(\alpha+2\pi\ell)^2}{2\sigma_0^2(t)}
\right].
```

Folding gives

```math
\boxed{
P_0(\theta,t)
=
W_{\sigma_0}(\theta,t)+W_{\sigma_0}(-\theta,t).
}
```

For the symmetric zero-drift situation this is

```math
P_0(\theta,t)=2W_{\sigma_0}(\theta,t).
```

### Long-Time Histogram

The simulations discussed in this project sample many unitary times and
pool the eigenvalues.  That object is not a single fixed-time wrapped
Gaussian.  It is the time mixture

```math
\boxed{
\overline P_0(\theta)
=
\left\langle
W_{\sigma_0(t)}(\theta)
+W_{\sigma_0(t)}(-\theta)
\right\rangle_t.
}
```

The corresponding ratio is

```math
\boxed{
\overline B_0(\theta)
=
\frac{\overline P_0(\theta)}
{\overline P_0(\theta)+\overline P_0(\pi-\theta)}.
}
```

This ratio is generally not Born-like.  In the numerically tested regime
\(J_x\ll h_z\ll J\), \(\overline P_0\) is concentrated near small
\(\theta\), and \(\overline B_0(\theta)\) is closer to a sharp
phase-support ratio than to \(\cos^2(\theta/2)\).

## Case II: Matched Central Field, \(h_{z0}=h_z\)

For \(h_{z0}=h_z\), the denominator becomes

```math
\delta_{sk}
=
2h_z
+2s_k\bigl[h_z+J(s_{k-1}+s_{k+1})\bigr].
```

Set

```math
r=s_{k-1}+s_{k+1}\in\{-2,0,2\}.
```

Then

```math
\delta=2h_z+2s_k(h_z+Jr).
```

The local channels are:

```math
s_k=-1,\ r=0:
\quad
\delta=0,
```

```math
s_k=+1,\ r=0:
\quad
\delta=4h_z,
```

```math
s_k=-1,\ r=\pm2:
\quad
\delta=\mp4J,
```

```math
s_k=+1,\ r=+2:
\quad
\delta=4h_z+4J,
```

```math
s_k=+1,\ r=-2:
\quad
\delta=4h_z-4J.
```

Thus the matched-field case has exact resonances:

```math
\boxed{
s_k=-1,
\qquad
s_{k-1}+s_{k+1}=0.
}
```

For these channels,

```math
\delta_{sk}=0,
```

and

```math
\frac{e^{-i\delta t}-1}{\delta}\to -it.
```

So first-order perturbation gives the secular term

```math
\langle s^{(k)}|M(t)|s\rangle
=
-igt\,e^{2ih_zt}
+O(g^3).
```

Finite-order perturbation is insufficient at long times because it
generates powers of \(gt\).  The resonant subspace must be resummed.

### Resonant Effective Blocks and Tangent Poles

A resonant pair satisfies

```math
E_s^{(B)}+h_z
=
E_{s^{(k)}}^{(B)}-h_z.
```

Inside such a degenerate subspace, the leading effective Hamiltonian has
the form

```math
H_{\rm eff}
=
E I
+\Omega\sigma_x
+\text{off-resonant corrections}.
```

For an isolated symmetric resonant pair,

```math
\Omega=g.
```

With loop dressing,

```math
\Omega=g c+O(g^2/\Delta),
```

where \(\Delta\) denotes the nonresonant denominators
\(4h_z,4J,4J\pm4h_z\).

The resonant block evolves as

```math
U_{00}^{\rm res}(t)=e^{-iEt}\cos(\Omega t),
\qquad
U_{10}^{\rm res}(t)=-ie^{-iEt}\sin(\Omega t).
```

Therefore

```math
\lambda_{\rm res}(t)
=
-i\tan(\Omega t)
```

in the isolated case, or more generally

```math
\lambda_{\rm res}(t)
\sim
-ib\tan(\Omega t)
```

with an effective scale \(b\).

Long-time unitary sampling makes \(\Omega t\) equidistributed modulo
\(\pi\) for nonzero \(\Omega\).  Hence

```math
x=b|\tan(\Omega t)|
```

has density

```math
\boxed{
q_b(x)
=
\frac{2b}{\pi(b^2+x^2)}.
}
```

Thus

```math
\boxed{
q_b(x)\sim \frac{2b}{\pi x^2},
\qquad
x\to\infty.
}
```

This is the analytic source of the heavy tail observed in the
matched-field simulations.

### Why Heavy Tail Alone Does Not Give Born

For the scaled Cauchy law above,

```math
q_b(1/x)
=
\frac{2b}{\pi(b^2+x^{-2})}.
```

Substituting into the exact ratio identity gives

```math
B_b(\theta)
=
\frac{1+b^2x^2}
{(1+b^2)(1+x^2)}.
```

For \(b=1\),

```math
B_b(\theta)=\frac12.
```

So the tangent-pole heavy tail is not, by itself, the Born rule.  It
explains the large-\(x\) endpoint behavior and the strong difference
from the \(h_{z0}=0\) case, but the Born-like ratio needs an additional
reciprocal closed-loop structure.

### Closed-Loop Origin of the Reciprocal Envelope

Let \(B(t)\) be the first-order bath matrix from the Dyson expansion.
The purely resonant first-order part flips

```math
s_k=-1\to +1.
```

Thus it raises bath magnetization by \(2\).  As a directed bath graph,
the purely resonant piece is nilpotent: repeated application must stop
after finitely many steps.  Consequently, the first-order resonant graph
has only zero eigenvalues.

Nonzero eigenvalues of the full \(M(t)\) therefore come from closed
paths, not from open one-step resonant edges.  Formally,

```math
\operatorname{Tr}B^\ell
=
\sum_{s_0,\ldots,s_{\ell-1},\ s_\ell=s_0}
\prod_{j=0}^{\ell-1}B_{s_{j+1},s_j}.
```

Also,

```math
\log\det(zI-B)
=
D\log z
-
\sum_{\ell=1}^\infty
\frac{1}{\ell z^\ell}
\operatorname{Tr}B^\ell.
```

Thus the eigenvalue density is controlled by closed loops.

The matched-field condition distinguishes one resonant loop coordinate
from three complementary local loop coordinates:

```math
Y=(Y_0,Y_1,Y_2,Y_3),
```

where \(Y_0\) is the resonant coordinate and \(Y_\perp=(Y_1,Y_2,Y_3)\)
is the complementary block.

The projective radius is

```math
x
=
\frac{|Y_0|}{\sqrt{Y_1^2+Y_2^2+Y_3^2}}.
```

Write

```math
\rho=\sqrt{Y_1^2+Y_2^2+Y_3^2},
\qquad
|Y_0|=x\rho.
```

The four-coordinate volume element gives the universal projective
Jacobian

```math
\boxed{
q_{\rm core}(x)
=
\mathcal N
\frac{W(\log x)}{(1+x^2)^2}.
}
```

Here \(W\) is the closed-loop envelope: it contains finite-size
structure, loop weights, and deviations from perfect isotropy.  This is
not assumed to be constant.

The map

```math
x\mapsto \frac1x
```

exchanges the resonant coordinate and the complementary radius.  In log
variables

```math
u=\log x,
```

this is

```math
u\mapsto -u.
```

If the matched-field closed-loop envelope is reciprocal,

```math
\boxed{
W(u)=W(-u),
}
```

then

```math
q_{\rm core}(1/x)
=
\mathcal N
\frac{W(-u)}{(1+x^{-2})^2}
=
x^4q_{\rm core}(x).
```

Therefore the core contribution gives

```math
\boxed{
B_{\rm core}(\theta)
=
\frac{1}{1+x^2}
=
\cos^2\frac{\theta}{2}.
}
```

This is the analytic mechanism for the Born-like ratio.

### Heavy-Tail Correction to the Born-Like Core

The full matched-field density has both the reciprocal closed-loop core
and tangent-pole contributions:

```math
q_h(x)
=
q_{\rm core}(x)
+q_{\rm pole}(x)
+q_{\rm nr}(x),
```

where \(q_{\rm nr}\) denotes bounded nonresonant background.

A useful minimal model is

```math
q_h(x)
=
A\frac{W(u)}{(1+x^2)^2}
+
C\frac{1}{1+x^2},
\qquad
u=\log x,
```

with \(W(u)\approx W(-u)\).  Let

```math
\eta(u)=\frac{C}{AW(u)}.
```

Using the exact ratio identity,

```math
B_h(\theta)
=
\frac{q_h(x)}
{q_h(x)+x^{-2}q_h(1/x)}.
```

If \(W(u)=W(-u)\), this becomes

```math
\boxed{
B_h(\theta)
=
\frac{\cos^2(\theta/2)+\eta(u)}
{1+2\eta(u)}.
}
```

For \(\eta\ll1\),

```math
B_h(\theta)
=
\cos^2\frac{\theta}{2}
+
\eta(u)\left[
1-2\cos^2\frac{\theta}{2}
\right]
+O(\eta^2).
```

Thus the Born ratio is recovered where the reciprocal closed-loop core
dominates.  The heavy-tail pole term produces systematic deviations,
especially near the endpoint \(\theta=\pi\), and explains why the raw
distribution need not equal the strict projective law
\(2\pi^{-1}\cos^2(\theta/2)\).

## Comparison of the Two Cases

The two cases differ in the origin of their ratio.

For \(h_{z0}=0\),

```math
H=H_B\otimes I_0+gX_0V
```

is exactly diagonalizable in the central \(X_0\)-basis.  The object
\(M\) is a Cayley transform of a unitary relative evolution:

```math
M=(A+I)^{-1}(A-I).
```

The angle is a folded eigenphase.  In the large-\(N\) scaled-coupling
limit, fixed-time phases are wrapped Gaussian, and long-time pooled
histograms are mixtures of folded wrapped Gaussians.  There is no
matched resonant denominator, no tangent pole mechanism, and no reason
for the reciprocal condition

```math
q(1/x)=x^4q(x)
```

to hold.

For \(h_{z0}=h_z\), the central \(X_0\)-basis simplification is gone.
Instead, the direct \(Z_0\)-basis denominator contains exact resonances:

```math
\delta_{sk}=0
\quad
\text{for}
\quad
s_k=-1,\quad s_{k-1}+s_{k+1}=0.
```

These resonances require all-orders resummation.  Resummation gives
tangent poles and a heavy \(x^{-2}\) tail.  The same matched-field
closed-loop structure naturally organizes the non-pole core into

```math
q_{\rm core}(x)
=
\mathcal N
\frac{W(\log x)}{(1+x^2)^2}.
```

When the closed-loop envelope is approximately reciprocal,

```math
W(u)\approx W(-u),
```

the ratio becomes approximately Born:

```math
B_h(\theta)\approx \cos^2\frac{\theta}{2}.
```

## Simulation Consistency

Exact-diagonalization checks with the scaled coupling confirm the
qualitative distinction.  For example, with

```math
J=1,
\qquad
h_z=0.1,
\qquad
J_x=0.05,
```

and long unitary-time sampling:

- For \(h_{z0}=0\), the distribution is narrow in \(x\), the largest
  sampled \(x\) remains \(O(1)\), and the ratio is not Born-like.
- For \(h_{z0}=h_z\), the sampled \(x\) values extend to very large
  values, and Hill-type tail estimates give a density exponent close to
  \(2\), consistent with \(q(x)\sim x^{-2}\).
- The matched-field ratio is much closer to \(\cos^2(\theta/2)\) than
  the no-central-field ratio, but this agreement should be interpreted
  as evidence for approximate reciprocal closed-loop symmetry, not as a
  strict finite-\(N\) theorem.

## Final Status

The exact finite-\(N\) Hamiltonian derivation proves:

1. \(M=U_{00}^{-1}U_{10}\) is the relevant spectral object.
2. The universal ratio identity is

   ```math
   B(\theta)
   =
   \frac{q(x)}
   {q(x)+x^{-2}q(1/x)}.
   ```

3. Exact Born ratio is equivalent to

   ```math
   q(1/x)=x^4q(x).
   ```

4. For \(h_{z0}=0\), \(M\) is the Cayley transform of a unitary relative
   evolution, so \(\theta\) is a folded eigenphase.
5. For \(h_{z0}=h_z\), exact matched-field resonances appear in the
   local denominator.
6. Resumming those resonances produces tangent poles and a heavy
   \(x^{-2}\) tail.

The Born-like ratio in the matched-field case follows analytically from
the additional closed-loop envelope condition

```math
W(u)\approx W(-u),
\qquad
u=\log x.
```

This is the current sharp formulation: the Hamiltonian rigorously
produces the resonant closed-loop structure, and the observed Born-like
ratio is explained by approximate reciprocal symmetry of the closed-loop
envelope.
