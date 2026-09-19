# User-supplied commuting/QND derivation

> Source: User-provided Chat result
> Original: `/Users/matanhaller/.codex/attachments/01f8bfb2-5e48-4069-9516-dde8521f087f/Pasted text.txt`
> Collected: 2026-09-19
> Published: Unknown

The material below is preserved verbatim as source evidence. It is not accepted as correct merely by inclusion; see the audited synthesis in `wiki/campaigns/commuting-qnd-sector.md`.

---

## Case 1 — commuting/QND detector sector

I would start by eliminating the entire class in which the detector is diagonal in the same \(Z\) basis through which it talks to the qubit. This turns out to give a fairly strong no-go result and, importantly, identifies the unique nontrivial collective \(N\)-scaling.

Take, for the ring,

\[
H=
h_{0x}X_0+h_{0y}Y_0+h_{0z}Z_0
+H_D(\{Z_i\})
+g_N Z_0 M,
\qquad
M=\sum_{i=1}^N Z_i ,
\]

where, for the present no-NNN hierarchy,

\[
H_D=
h_z\sum_i Z_i
+
J_z\sum_i Z_iZ_{i+1}.
\]

The result actually extends to arbitrary \(H_D(\{Z_i\})\).

I will use the existing project convention

\[
P_N(d\theta;t)=2^{-N}\sum_{j=1}^{2^N}\delta_{\theta_j(t)}(d\theta)
\]

for one outcome pencil, counting roots with multiplicity.

---

### 1. Exact finite-\(N\) reduction

For a detector computational-basis configuration
\(\mathbf s=(s_1,\ldots,s_N)\), \(s_i=\pm1\),

\[
M_{\mathbf s}=\sum_i s_i\equiv m.
\]

Because \(H_D\) commutes with both \(M\) and all qubit operators,

\[
U(t)|\mathbf s\rangle
=
e^{-iE_{\mathbf s}t}
u_m(t)|\mathbf s\rangle ,
\]

where the entire root geometry is governed by the \(2\times2\) unitary

\[
u_m(t)
=
e^{-it\left(
h_{0x}X+h_{0y}Y+
\Delta_m Z
\right)},
\qquad
\Delta_m=h_{0z}+g_Nm.
\]

Thus **\(h_z\), \(J_z\), and indeed every diagonal detector interaction disappear completely from the collapse-angle distribution**. They only generate an overall detector phase.

Define

\[
h_\perp=\sqrt{h_{0x}^2+h_{0y}^2},
\qquad
\Omega_m=\sqrt{h_\perp^2+\Delta_m^2}.
\]

For the outcome-\(0\) collapse pencil, the initial qubit state is simply the inverse image

\[
|\psi_{0,m}\rangle=u_m^\dagger(t)|0\rangle.
\]

Writing its Bloch polar angle as \(\Theta_m(t)\),

\[
\boxed{
\sin^2\frac{\Theta_m(t)}2
=
\frac{h_\perp^2}{\Omega_m^2}
\sin^2(\Omega_m t)
}
\]

or

\[
\boxed{
\Theta_m(t)
=
2\arcsin\left[
\frac{h_\perp}{\Omega_m}
|\sin(\Omega_m t)|
\right].
}
\]

Therefore

\[
\boxed{
P_N(d\theta;t)
=
2^{-N}
\sum_{k=0}^{N}
{N\choose k}
\delta_{\Theta_{N-2k}(t)}(d\theta).
}
\]

This is exact.

The outcome-\(1\) preimage is orthogonal to the outcome-\(0\) preimage for every \(m\), so its Bloch vector is antipodal:

\[
\Omega_{1,m}=-\Omega_{0,m}.
\]

Hence, already at finite \(N\),

\[
\boxed{\rho_1(\Omega)=\rho_0(-\Omega).}
\]

That part of the desired structure comes automatically. The nontrivial problem is obtaining the correct *relative density*.

---

# 2. Immediate obstruction: \(h_\perp=0\)

If

\[
h_{0x}=h_{0y}=0,
\]

then

\[
\Theta_m(t)=0
\]

for every \(m,N,t,g_N,h_z,J_z\).

Thus

\[
P_N=P_\infty=\delta_0,
\]

while the complementary outcome is at the south pole.

This is simply QND phase accumulation. The detector can acquire arbitrarily complicated configuration-dependent phases, but the qubit never leaves the measurement axis.

So:

\[
\boxed{
\text{single commuting coupling axis + qubit field parallel to it}
\Longrightarrow
\text{no nontrivial Born abundance}.
}
\]

Adding \(ZZ\) interactions cannot repair this.

---

# 3. Collective ring: the \(N\)-scaling is essentially fixed

Now let \(h_\perp\neq0\) and write

\[
g_N=g\,N^{-\alpha}.
\]

Under the root-counting measure,

\[
\frac{M}{\sqrt N}
\Rightarrow X,
\qquad X\sim\mathcal N(0,1).
\]

Consequently

\[
g_N M
=
gN^{1/2-\alpha}X_N.
\]

There are three sharply different regimes.

### \( \alpha>1/2 \): interaction disappears

Then

\[
g_NM\to0
\]

in probability, and therefore

\[
\boxed{
P_\infty(d\theta;t)
=
\delta_{\Theta_0(t)}(d\theta)
}
\]

with

\[
\Theta_0(t)
=
2\arcsin
\left[
\frac{h_\perp}
{\sqrt{h_\perp^2+h_{0z}^2}}
\left|
\sin\!\left(
t\sqrt{h_\perp^2+h_{0z}^2}
\right)
\right|
\right].
\]

In particular, the conventional \(g_N\sim1/N\) Kac scaling gives a **trivial thermodynamic collapse distribution**.

This is an important negative result.

---

### \( \alpha=1/2 \): unique nontrivial typical-state limit

Now

\[
g_NM\Rightarrow gX.
\]

Hence

\[
\boxed{
P_\infty(d\theta;t)
=
\operatorname{Law}
\left[
\Theta(h_{0z}+gX,t)
\right]
}
\]

with

\[
\Theta(\Delta,t)
=
2\arcsin
\left[
\frac{h_\perp}
{\sqrt{h_\perp^2+\Delta^2}}
\left|
\sin(t\sqrt{h_\perp^2+\Delta^2})
\right|
\right].
\]

So

\[
\boxed{g_N\propto N^{-1/2}}
\]

is the **only power-law scaling producing an \(O(1)\) distribution of effective longitudinal fields under the collapsible-root counting measure.**

That is already one answer to the axis-scaling question in the project.

---

### \( \alpha<1/2 \): interaction becomes too strong and again trivializes

For a typical root,

\[
|g_NM|\to\infty.
\]

Then

\[
\frac{h_\perp}
{\sqrt{h_\perp^2+(h_{0z}+g_NM)^2}}
\to0,
\]

so

\[
\Theta_m(t)\to0.
\]

Therefore

\[
\boxed{
P_\infty(d\theta;t)=\delta_0(d\theta).
}
\]

This is slightly counterintuitive: making the collective longitudinal coupling stronger does **not** produce richer collapse directions. It locks the effective rotation axes increasingly close to \(Z\).

Thus the scaling classification is

\[
\boxed{
\begin{array}{ccl}
\alpha>1/2 &:& \text{coupling self-averages away},\\[2mm]
\alpha=1/2 &:& \text{nontrivial Gaussian effective-field ensemble},\\[2mm]
\alpha<1/2 &:& \text{longitudinal locking } \Rightarrow\delta_0.
\end{array}}
\]

---

# 4. Exact long-time distribution

For a fixed effective detuning \(\Delta\), define

\[
\rho(\Delta)
=
\frac{h_\perp}
{\sqrt{h_\perp^2+\Delta^2}}.
\]

Long-time averaging makes \(|\sin\Omega t|\) sample its standard phase distribution. The resulting polar density is

\[
\boxed{
p_\rho(\theta)
=
\frac{\cos(\theta/2)}
{\pi\sqrt{\rho^2-\sin^2(\theta/2)}}
}
\]

on

\[
0<\theta<2\arcsin\rho,
\]

and zero elsewhere. For \(\rho=0\), this becomes \(\delta_0\).

Thus

\[
\boxed{
\overline P_N(d\theta)
=
2^{-N}
\sum_k{N\choose k}
p_{\rho(\Delta_{N-2k})}(\theta)d\theta .
}
\]

For the critical scaling,

\[
\boxed{
\overline p_\infty(\theta)
=
\int_{-\infty}^{\infty}
\frac{dx}{\sqrt{2\pi}}e^{-x^2/2}
p_{\rho(h_{0z}+gx)}(\theta).
}
\]

For this commuting class, the two orders of limits generically commute weakly:

\[
\lim_{N\to\infty}\overline P_N
=
\overline P_\infty,
\]

because the time average acts independently on each effective two-level frequency and the subsequent integrands are bounded against continuous test functions. Exceptional zero-frequency cases reduce to the already trivial limits.

---

# 5. A stronger Born obstruction

The \(N^{-1/2}\) case is the only one worth examining further, so the question is whether its continuous weak distribution might secretly yield Born.

Let

\[
\Delta=h_{0z}+gX
\]

with Gaussian density

\[
q(\Delta)=
\frac1{|g|\sqrt{2\pi}}
\exp\left[-\frac{(\Delta-h_{0z})^2}{2g^2}\right].
\]

The time-averaged density can be written exactly as

\[
\overline p_\infty(\theta)
=
\int_{-h_\perp\cot(\theta/2)}
^{h_\perp\cot(\theta/2)}
q(\Delta)
\frac{
\cos(\theta/2)\sqrt{h_\perp^2+\Delta^2}
}{
\pi
\sqrt{
h_\perp^2\cos^2(\theta/2)
-\Delta^2\sin^2(\theta/2)
}
}
\,d\Delta.
\]

This lets us inspect the poles.

Put

\[
\epsilon=\pi-\theta.
\]

Near the south pole,

\[
\cot\frac{\theta}{2}
\simeq\frac{\epsilon}{2},
\]

so only detunings

\[
|\Delta|\lesssim \frac{h_\perp\epsilon}{2}
\]

contribute. Expanding,

\[
\boxed{
\overline p_\infty(\pi-\epsilon)
=
\frac{h_\perp q(0)}{2}\,\epsilon
+O(\epsilon^3).
}
\]

Meanwhile

\[
\overline p_\infty(0)
=
\frac{1}{\pi h_\perp}
\mathbb E\sqrt{h_\perp^2+\Delta^2}
\equiv B>0.
\]

Therefore the normalized outcome ratio

\[
\overline R(\theta)
=
\frac{\overline p_\infty(\theta)}
{\overline p_\infty(\theta)+
\overline p_\infty(\pi-\theta)}
\]

obeys

\[
\boxed{
\overline R(\theta)
=
1-
\frac{h_\perp q(0)}
{2B}\theta
+O(\theta^2)
\qquad (\theta\to0).
}
\]

But Born requires

\[
\cos^2\frac\theta2
=
1-\frac{\theta^2}{4}
+O(\theta^4).
\]

So the QND critical model has a **linear polar correction**, whereas Born has a quadratic one:

\[
\boxed{
\overline R(\theta)-R_{\rm Born}(\theta)
=
-C\theta+O(\theta^2),
\qquad
C>0.
}
\]

For every finite \(h_{0z}/g\),

\[
q(0)>0,
\]

so \(C\neq0\).

This gives a clean result:

\[
\boxed{
\textbf{The critical collective QND ring cannot produce the exact
time-averaged Born profile.}
}
\]

One could make \(C\) exponentially small by taking \(|h_{0z}|\gg g\), but that is not a mechanism for Born behavior; it simply makes resonant configurations exponentially rare. I would not regard this direction as high priority for numerical optimization.

---

# 6. Strong Born rule is even more strongly obstructed

At any fixed \(t\), the critical ring distribution depends on a single continuous random variable \(X\):

\[
X\mapsto \Omega_0(X,t).
\]

Its support on the Bloch sphere is therefore generically a **one-dimensional curve**, not a two-dimensional surface density.

Thus the strong quantity

\[
\rho_0(\theta,\phi)
\]

is singular with respect to Bloch-sphere area measure.

So this QND family cannot produce a regular strong-Born density at fixed \(T\).

The \(\phi\)-averaged version is the only potentially meaningful Born comparison here, and even its time-averaged form has the pole obstruction just derived.

---

# 7. Endpoint-chain version is worse

Now take

\[
H=
\mathbf h_0\cdot\boldsymbol\sigma_0+
H_D(\{Z_i\})
+
g_z Z_0Z_1.
\]

Again \(H_D\) may contain \(h_z\) and nearest-neighbor \(J_z\).

Only \(s_1=\pm1\) enters the qubit evolution:

\[
\Delta_\pm=h_{0z}\pm g_z.
\]

Exactly half of all detector roots belong to each sector, so for **every \(N\)**,

\[
\boxed{
P_N(d\theta;t)
=
\frac12\delta_{\Theta_+(t)}
+
\frac12\delta_{\Theta_-(t)}.
}
\]

Hence

\[
P_\infty=P_N.
\]

The time-averaged distribution is

\[
\boxed{
\overline p(\theta)
=
\frac12p_{\rho_+}(\theta)
+
\frac12p_{\rho_-}(\theta),
}
\]

where

\[
\rho_\pm
=
\frac{h_\perp}
{\sqrt{h_\perp^2+(h_{0z}\pm g_z)^2}}.
\]

This gives another exact obstruction to Born.

If

\[
\rho_{\max}<1,
\]

then the distribution has compact support

\[
\theta\le
2\arcsin\rho_{\max}<\pi.
\]

Consequently there is a finite interval near the north pole on which

\[
\overline p(\pi-\theta)=0
\]

and hence

\[
\overline R(\theta)=1,
\]

whereas

\[
\cos^2(\theta/2)<1
\]

for every \(\theta>0\).

If instead \(\rho_{\max}=1\), one of the effective detunings vanishes. That branch has

\[
p_1(\theta)=\frac1\pi
\]

over the entire interval. It therefore leaves finite weight at the south pole and cannot reproduce the Born endpoint behavior. The doubly resonant case simply gives

\[
R=\frac12.
\]

So

\[
\boxed{
\textbf{pure endpoint QND coupling cannot give the exact weak Born profile either.}
}
\]

Its strong distribution is still more clearly excluded: finite \(N\) gives two points, while infinite-time averaging gives only two one-dimensional Bloch orbits.

---

## Conceptual ledger update

| family | case | nonzero coefficients | hierarchy | perturbative parameter | analytic status | \(P_N\) | \(P_\infty\) | \(\bar P_N\) | \(\bar P_\infty\) | \(R\) quantities | Born deviation | physical interpretation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ring | QND-0 | \(h_{0z},h_z,J_{1z},g_z(N)\) | any | any | **exact / excluded** | \(\delta_0\) | \(\delta_0\) | \(\delta_0\) | \(\delta_0\) | trivial poles | maximal | pure phase measurement; no qubit rotation |
| ring | QND-weak | \(h_{0\perp},h_{0z},h_z,J_{1z},gN^{-\alpha}\), \(\alpha>1/2\) | \(g_NM\to0\) | \(gN^{1/2-\alpha}\) | **exact / excluded** | binomial atoms | one atom | mixture \(p_\rho\) | one \(p_\rho\) | explicit piecewise | not Born | detector self-averages away |
| ring | QND-critical | same, \(\alpha=1/2\) | \(g_NM=O(1)\) | \(g/h_{\rm scale}\) | **exact reduction; Born no-go for \(\bar R\)** | binomial atoms | Gaussian pushforward | binomial mixture | Gaussian mixture | exact integral | \(R=1-C\theta+\cdots\), vs Born \(1-\theta^2/4+\cdots\) | static Gaussian longitudinal field |
| ring | QND-strong | same, \(\alpha<1/2\) | \(|g_NM|\to\infty\) | \(h_\perp/(g_N\sqrt N)\) | **exact / excluded** | binomial atoms | \(\delta_0\) | mixture | \(\delta_0\) | trivial | maximal | longitudinal locking |
| chain | endpoint-QND-0 | \(h_{0z},h_z,J_{1z},g_z\) | any | \(g_z/h\) | **exact / excluded** | \(\delta_0\) | same | same | same | trivial | maximal | phase-only endpoint coupling |
| chain | endpoint-QND-\(\perp\) | \(h_{0\perp},h_{0z},h_z,J_{1z},g_z\) | perturbative or otherwise | \(g_z/h\) | **exact / excluded as exact Born mechanism** | two atoms | same | two \(p_\rho\)'s | same | closed mixture | compact-support/resonant obstruction | detector acts as binary static field |

The important point is that **adding longitudinal Ising interactions does not move any of these rows toward Born**. The detector may be many-body interacting energetically, but as far as collapse-root geometry is concerned it is still just a classical static field.

---

## What is now established

This removes a surprisingly large portion of parameter space. Purely commuting \(Z_0\)-\(Z\) coupling cannot be the physical mechanism behind a robust Born profile. The only nontrivial collective scaling under the project's root-count measure is \(g_z\sim N^{-1/2}\), but even there the resulting profile has the wrong pole asymptotics, and the fixed-time strong distribution remains singular.

There is also a referee-relevant scaling issue. \(1/N\) Kac scaling keeps the collective coupling uniformly bounded in operator norm but becomes thermodynamically invisible to typical collapsible roots. \(1/\sqrt N\) keeps **typical fluctuations** finite but does not keep the interaction norm uniformly bounded on the rare fully polarized detector states. Any eventual collective positive result will need to state clearly which perturbativity criterion is physically intended.

## Next highest-information calculation

The next step should **not** be another diagonal variant. The highest-information move is to introduce the minimal ingredient that invalidates this no-go: a genuinely noncommuting detector transition.

I recommend analyzing

\[
\boxed{
H=
h_{0z}Z_0
+h_z\sum_iZ_i
+J_z\sum_iZ_iZ_{i+1}
+
\frac{g_x}{\sqrt N}X_0\sum_iX_i
}
\]

on the ring, first at \(J_z=0\) as the analytically soluble control and then at \(J_z\neq0\), with

\[
g_x\ll |h_{0z}|,|h_z|,|J_z|.
\]

Unlike the QND family, the perturbation now changes both qubit and detector configurations. The first-order collapse pencil becomes a weighted hypercube-flip operator rather than a static-field pushforward. The decisive analytic question is whether its spectral/root measure acquires the required **odd first harmonic** rather than only an even or antipodally trivial response.

That calculation has substantially higher information gain than numerically exploring the QND critical Gaussian integral: if the transverse perturbative family is also symmetry-forbidden at leading order, we can eliminate another major Hamiltonian sector before spending any Codex budget.
