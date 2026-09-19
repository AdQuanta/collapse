# Approved Hamiltonian Families and Unlocking Order

> Sources: `SPEC.md` v1.0, 2026-09-15
> Raw: [Research specification snapshot](../../raw/project-governance/research-spec-v1.md)
> Updated: 2026-09-19

This page is an operational map of the approved search space. Older star, pixel, random-graph, all-to-all, cross-axis, and next-nearest-neighbor models are historical ideas, not active families.

## Initial ring family

For qubit $0$ and a periodic detector of $N$ spins,

$$
H_q=h_{0z}Z_0,
$$

$$
H_D=h_z\sum_{i=1}^N Z_i+J\sum_{i=1}^N Z_iZ_{i+1},
\qquad Z_{N+1}=Z_1,
$$

$$
H_{qD}=g_{z,N}Z_0\sum_{i=1}^N Z_i.
$$

After systematic failure at this tier, approved axis-aligned collective terms may be unlocked:

$$
H_{qD}=\sum_{\alpha=x,y,z}g_{\alpha,N}\sigma_0^\alpha\sum_i\sigma_i^\alpha.
$$

## Initial endpoint-chain family

For an open detector chain,

$$
H_q=h_{0z}Z_0,
$$

$$
H_D=h_z\sum_{i=1}^N Z_i+J\sum_{i=1}^{N-1}Z_iZ_{i+1},
$$

$$
H_{qD}=g_z Z_0Z_1.
$$

After systematic failure, the approved axis-aligned endpoint coupling is

$$
H_{qD}=g_xX_0X_1+g_yY_0Y_1+g_zZ_0Z_1.
$$

## Complexity hierarchy

Change one structural ingredient at a time:

1. detector interactions: Ising $\rightarrow$ symmetric XX/XY $\rightarrow$ XXZ $\rightarrow$ XYZ;
2. one-body fields: longitudinal only $\rightarrow$ one transverse direction $\rightarrow$ fully general fields if needed;
3. qubit-detector coupling: ZZ $\rightarrow$ XX+YY/XY $\rightarrow$ XXZ $\rightarrow$ XYZ.

Cross-axis terms such as $X_0Z_i$, NNN detector interactions, random graphs, and all-to-all models require explicit user approval. A simpler tier can be abandoned after systematic numerical failure across parameters, multiple relevant $N$ and $T$, refinement where warranted, and pathology checks; an analytic no-go is not mandatory.

## Coupling scaling

For collective ring operators $S_\alpha=\sum_i\sigma_i^\alpha$, the conservative baseline is

$$
g_{\alpha,N}\propto N^{-1},
$$

because $\|S_\alpha\|\sim N$. A fluctuation-based scaling $g_{\alpha,N}\propto N^{-\kappa_\alpha/2}$ is allowed only after deriving $\operatorname{Var}(S_\alpha)\sim N^{\kappa_\alpha}$ and showing the relevant weak-coupling ratio remains controlled. In particular, $1/\sqrt N$ is not an automatic default.

The endpoint coupling is local and can remain $O(1)$ in $N$, but it must still be perturbatively small relative to the appropriate gap, bandwidth, or resonant-sector scale.

## Current status

The commuting longitudinal/QND starting tier has a partially verified Z-outcome-basis obstruction; see [[commuting-qnd-sector]]. It does not yet eliminate the family for every candidate preferred axis. No positive historical candidate, finite-bin certificate, or old parameter lead has v1.0 credit. The next tier may be unlocked only after the frozen search record establishes systematic failure at the simpler tier.

See also: [[research-specification-v1]], [[commuting-qnd-sector]], [[production-pipeline]], [[symmetry-sectors]].
