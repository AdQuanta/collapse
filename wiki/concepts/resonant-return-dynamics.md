# Resonant return dynamics

**PROVED, SCOPED (2026-09-12).** With central qubit first, write

\[
H=\begin{pmatrix}H_+&Q^\dagger\\Q&H_-\end{pmatrix},\qquad
H_\pm=H_D\pm(h_{0z}I+g_zL_z),\qquad
Q=(h_{0x}+ih_{0y})I+g_xL_x+ig_yL_y.
\]

For rings, Lx,y=sum X,Y/sqrt(N), Lz=sum Z/N. For endpoint chains,
Lx,y,z are the Pauli operators at site 1. At nonreal z the exact projected
resolvent is

\[
G_{00}=[z-H_+-Q^\dagger(z-H_-)^{-1}Q]^{-1},\qquad
G_{10}=(z-H_-)^{-1}QG_{00}.
\]

This retains repeated qubit flips and conditional longitudinal shifts.
Reconstruct time-domain A(t), C(t) before computing the projective roots;
roots of a resolvent pencil are not roots of the physical time pencil.
The equivalent Volterra kernel is Q† exp(-i H- t) Q.

For a charge-conserving detector, the first transverse response admits an
exact similarity whose radial scale is sqrt(|gx²-gy²|), away from gx=±gy.
It helps organize multichannel candidates, but does not make full dynamics
equivalent. The nonunitary similarity becomes ill-conditioned with N.
The exact return operator supplies the next terms that must be retained.

The dimensional estimate g²/E_D is not a uniform operator-norm bound.
At z=E+i delta, ||Sigma|| <= ||Q||²/|delta|, and the ring norm can grow
with N. A spectral-measure estimate is needed before assigning a typical
return scale. If gz is order epsilon while h0 is order epsilon², conditional
detector energies still contain the order-epsilon longitudinal term.

**REPRODUCED_NUMERIC:** Forty-eight reduced QZ snapshots verify finite-size
identities and finite return effects. Seven archived high-N snapshots with
gx,gy both nonzero supply positive polar leads. Their P/reflected-P and
R/Born panels expose both improving ratio errors and remaining moment
residuals. These do not prove an open stable Born phase.

Sources: [derivation and validation](../../research_reports/BORN_RESONANT_RETURN.md),
[positive multichannel audit](../../research_reports/BORN_POSITIVE_MULTICHANNEL.md).
See [[weak-coupling-search]] and [[projective-roots]].
