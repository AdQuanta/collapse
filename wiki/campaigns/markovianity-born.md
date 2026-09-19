# Markovianity versus Born-like root statistics

> Sources: Repository execution, 2026-09-20; User conjecture, 2026-09-20
> Raw: [Memory versus Born comparison](../../raw/campaigns/2026-09-20-markovianity-born-comparison.md)
> Updated: 2026-09-20

**Status:** Exploratory mechanism study. **No paper-readiness gate is claimed or advanced**, no verifier is frozen, and `paper_ready` remains `false`. The result is a negative/reorienting one and is recorded so the same ground is not re-explored.

## Question

Is one-way information flow from qubit into detector — Markovianity — necessary or sufficient for the projective-root measure to approach $R(\theta)=\cos^2(\theta/2)$?

As posed the question is not testable. At finite $N$ a finite bath always recurs, so no model in the approved family is strictly Markovian; and Born-likeness is asymptotic ($N\to\infty$ then $T\to\infty$) while Markovianity is a property of the whole trajectory $\{\Lambda_t\}$ and of the initial detector state, which the root measure never sees. The study therefore measures information backflow on a fixed stated window and studies its $N$-scaling.

## Method

The qubit Choi matrix is the Gram matrix of the four propagator-block images of the detector state, since $\sum_\mu (K_\mu)_{ij}\overline{(K_\mu)_{kl}} = \langle U_{kl}D_0 | U_{ij}D_0\rangle$. Verified against an explicit partial trace to $1.11\times10^{-16}$. Memory diagnostics therefore ride on the blocks the root pipeline already extracts; no $2^{N+1}$ density matrix and no partial trace are built. See [[homogeneous-qz]] for the root side.

288 configurations over the two SPEC-approved geometries plus two mechanism-separating controls, at matched effective coupling $\epsilon=0.10$, $N=4\ldots9$. Full parameter disclosure in [the report](../../research_reports/MARKOVIANITY_BORN_2026-09-20.md).

## Findings

**The geometry labelling in the conjecture is backwards.** The collectively coupled ring, expected to be the non-Markovian model, has $N_{\rm BLP}$ decaying monotonically with $N$ in every row, reaching $1.1\times10^{-3}$ at $N=9$: it is asymptotically Markovian under both the conservative $g_N\propto 1/N$ and the fluctuation $g_N\propto N^{-1/2}$ scalings. The only family whose memory saturates is the **gapped endpoint chain**, flat at $\approx 0.23$ from $N=6$. At criticality the same chain is the most Markovian object in the grid ($3\times10^{-4}$). **Detector phase, not geometry, decides.**

**Sufficiency is refuted.** The five least-Markovian configurations carry $S_{\rm Born}$ between $-0.32$ and $-0.63$, below the uninformative baseline.

**Necessity is not supported, and the sign runs against it.** Controlling for size by correlating within each $N$, Spearman $\rho(N_{\rm BLP}, S_{\rm Born})$ becomes negative and strengthens: $-0.587$ ($p=0.0026$) at $N=9$ over all cells, $-0.845$ ($p=0.00055$) restricted to the two SPEC production cells. Less memory goes with more Born-like.

**But nothing here is Born-like**, and the apparent finite-size improvement is an **estimator artifact**. Root count grows as $2^N$, so noise on $R$ falls from $0.408$ at $N=4$ to $0.072$ at $N=9$. Thinning the $N=9$ root set back to the $N=4$ budget returns $S_{\rm Born}$ to its $N=4$ value in every cell. This is `SPEC.md` hard-FAIL condition 6 and is recorded as a negative result. The within-$N$ correlations are unaffected, since at fixed $N$ every cell has identical root count and noise.

## Scope and cautions

The finding is an association across a parameter grid, not a causal mechanism; no mechanism-breaking control was run. $S_{\rm Born}$ is a diagnostic, not a SPEC metric — $E_2$, $E_\infty$, $E_{\rm harm}$, $E_{\rm marg}$ were not computed. $N\le 9$ because a matched comparison must be dense on both sides: the endpoint chain has no symmetry-sector path. $N_{\rm BLP}$ is an unnormalized window accumulation and a lower bound on the BLP supremum, comparable only at fixed window and sampling.

The $h_{x0}=0$ arm is a memory reference only: $[H,Z_0]=0$ collapses every root onto the pole, which is the commuting/QND tier already covered by [[commuting-qnd-sector]].

## What would sharpen it

The gapped endpoint chain is the only family whose memory saturates. If the negative association holds it should be the worst Born performer at large $N$, and its memory can be suppressed continuously by tuning $h_x/J$ toward criticality without changing anything else — which makes it the natural mechanism-breaking control.

See also: [[commuting-qnd-sector]], [[born-like-points]], [[projective-roots]], [[hamiltonian-families]].
