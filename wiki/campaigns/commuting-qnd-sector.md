# Commuting/QND Detector Sector: Verified Scope and Obstruction

> Sources: User-provided Chat derivation, Unknown; `SPEC.md` v1.0, 2026-09-15
> Raw: [Verbatim supplied derivation](../../raw/campaigns/2026-09-19-commuting-qnd-chat-result.md); [Research specification snapshot](../../raw/project-governance/research-spec-v1.md)
> Updated: 2026-09-19

**Status:** The finite-$N$ reduction and a $Z$-outcome-basis exact-Born obstruction are verified. This does not eliminate the family for every preferred axis, does not give a uniform lower bound on approximate-Born error, and does not advance a paper-readiness gate.

## Model and exact sector reduction

Let the detector magnetization be $M=\sum_i Z_i$ and assume $[H_D,M]=0$. For

$$
H=H_D+h_\perp X_0+h_{0z}Z_0+g_NZ_0\,M,
$$

each detector magnetization sector $m=N-2k$ reduces the qubit dynamics to

$$
u_m(t)=\exp\{-it[h_\perp X_0+(h_{0z}+g_Nm)Z_0]\}.
$$

$H_D$ can generate sector-dependent detector phases, not necessarily one global phase for an arbitrary detector superposition, but those phases do not alter the qubit root coordinates. For a chosen output basis, the preimage $u_m^\dagger|b\rangle$ is an exact collapsible input. The two outcomes are antipodal, and coincident roots receive the summed kernel dimension.

For the physical $Z$ output basis, the outcome-0 polar measure over the full detector Hilbert space is

$$
P_{0,N}^{\theta}(d\theta;t)=2^{-N}\sum_{k=0}^N{N\choose k}\delta_{\Theta_{N-2k}(t)}(d\theta),
$$

where

$$
\Theta_m(t)=2\arcsin\!\left[
\frac{h_\perp}{\sqrt{h_\perp^2+(h_{0z}+g_Nm)^2}}
\left|\sin\!\left(t\sqrt{h_\perp^2+(h_{0z}+g_Nm)^2}\right)\right|
\right].
$$

Set $\Theta_m=0$ at the removable zero-frequency case. A homogeneous solve is needed to retain any south-pole roots at $\lambda=\infty$.

## Collective-scaling trichotomy

For fixed $O(1)$ fields, nonzero $g$, full-Hilbert multiplicity weighting, and $g_N=gN^{-\alpha}$:

- $\alpha>1/2$: typical magnetization fluctuations vanish from the effective detuning, so the measure approaches the uncoupled single-sector orbit;
- $\alpha=1/2$: $m/\sqrt N\Rightarrow\mathcal N(0,1)$, producing a nontrivial Gaussian detuning law;
- $\alpha<1/2$: in the $Z$ output basis, typical longitudinal detuning diverges and the polar measure approaches the north pole.

Thus $N^{-1/2}$ is the only nontrivial pure-power scaling for this particular root-counting ensemble. It is not a general license to replace the specification's conservative $N^{-1}$ operator-norm baseline: any active campaign still needs a fluctuation derivation and a controlled relevant weak-coupling parameter.

## Phase-average kernel and density convention

For fixed detuning $\Delta$ define

$$
\rho=\frac{h_\perp}{\sqrt{h_\perp^2+\Delta^2}}.
$$

Uniform phase averaging gives the density with respect to $d\theta$

$$
p_\rho^{(d\theta)}(\theta)=
\frac{\cos(\theta/2)}{\pi\sqrt{\rho^2-\sin^2(\theta/2)}},
\qquad 0<\theta<2\arcsin\rho.
$$

This is not the SPEC weak density. They are related by

$$
p_b^{(d\theta)}(\theta)=\bar\rho_b(\theta)\sin\theta.
$$

The Born targets in the $d\theta$ convention are therefore

$$
p_{\mathrm{Born},0}^{(d\theta)}=\cos^2(\theta/2)\sin\theta,
\qquad
p_{\mathrm{Born},1}^{(d\theta)}=\sin^2(\theta/2)\sin\theta.
$$

## Critical Gaussian $Z$-basis obstruction

At $g_N=g/\sqrt N$, $g\ne0$, the large-$N$ detuning law is

$$
q(\Delta)=\frac{1}{|g|\sqrt{2\pi}}
\exp\!\left[-\frac{(\Delta-h_{0z})^2}{2g^2}\right].
$$

Its uniform-phase mixture is

$$
p_0^{(d\theta)}(\theta)=
\int_{-h_\perp\cot(\theta/2)}^{h_\perp\cot(\theta/2)}
q(\Delta)
\frac{\cos(\theta/2)\sqrt{h_\perp^2+\Delta^2}}
{\pi\sqrt{h_\perp^2\cos^2(\theta/2)-\Delta^2\sin^2(\theta/2)}},d\Delta.
$$

With

$$
B=\frac{1}{\pi h_\perp}\mathbb E_q\sqrt{h_\perp^2+\Delta^2},
\qquad a=\frac{h_\perp q(0)}2,
$$

the endpoint behavior is

$$
p_0^{(d\theta)}(\theta)=B+O(\theta^2),
\qquad
p_0^{(d\theta)}(\pi-\epsilon)=a\epsilon+O(\epsilon^3).
$$

Hence $\bar\rho_0(\theta)\sim B/\theta$ at the north pole and approaches $a$ at the south pole, whereas the weak Born density is finite at the north pole and vanishes quadratically at the south pole. The reflected marginal ratio also has a linear correction,

$$
R(\theta)=1-\frac aB\theta+O(\theta^2),
$$

instead of $\cos^2(\theta/2)=1-\theta^2/4+O(\theta^4)$. This proves failure of exact weak Born and of the necessary ratio condition for the $Z$ output basis at every fixed finite $h_{0z}/g$.

## Order of limits

The supplied derivation established a phase/Cesàro average. It did not prove instantaneous long-time convergence. In the critical Gaussian sector with $h_\perp>0$, continuous detunings plausibly permit a separate stationary-phase/Riemann–Lebesgue proof that the $N$-first instantaneous measure converges weakly to the same phase mixture, generically with stationary-point decay. That proof remains to be written and frozen before it receives credit. The endpoint-chain reduction has only finitely many discrete orbits and generally only a time average.

Fixed-$T$ roots lying on a one-dimensional curve do not by themselves rule out a two-dimensional weak limit as $T\to\infty$.

## Exact scope of the result

The no-go assumes the $Z$ outcome basis. `SPEC.md` requires the preferred axis to be identified rather than assumed. For a rotated output basis, even the $h_\perp=0$ dynamics can sweep a latitude, so the pole conclusions change. Eliminating the entire commuting/QND family requires either an all-axis obstruction or a proof that $Z$ is the only stable admissible preferred axis.

The endpoint-chain two-sector calculation likewise establishes a $Z$-basis obstruction. A resonant branch has nonzero limiting $d\theta$ density and cap mass $O(\epsilon)$ near the south pole, not a point mass there; the Born cap mass is $O(\epsilon^4)$.

## What remains open

- prove or refute the all-preferred-axis obstruction;
- formalize the instantaneous critical-sector dephasing limit in the prescribed order;
- quantify the mandatory SPEC metrics and determine whether approximate Born error has a uniform positive lower bound;
- justify any $N^{-1/2}$ transverse collective extension by fluctuations and a weak-coupling ratio before activation;
- do not promote the proposed hypercube/first-harmonic mechanism without a derivation.

See also: [[research-specification-v1]], [[hamiltonian-families]], [[born-like-points]], [[projective-roots]].
