# Candidate: interacting central-X ring echo and exact autocorrelation law

2026-09-13. Frozen before v3 validation. Initial status **CONJECTURE** for the
thermodynamic echo theorem; exact algebra below is proposed for independent
verification. This extends the interacting transverse step while retaining
earlier coefficients. Endpoint chains receive local moment checks only;
no collective CLT is assumed for endpoint coupling.

## Hypothesis, alternative and predicted signatures

For H_N=D_N+X_Q(a+g M_N/sqrt(N)), M_N=sum X_i, with arbitrary fixed finite
uniform detector fields and NN/NNN XYZ interactions, the thermodynamic
production polar measure at every fixed t is

    Law(F(a t + g sigma(t) G)), F(u)=arccos(cos(2u)), G~N(0,1),
    sigma(t)^2 = integral |integral_0^t exp(i omega s) ds|^2 nu(d omega).

Here nu is the infinite-temperature, zero-momentum detector X dynamical
spectral measure, normalized to one. The strongest alternative is a surviving
non-Gaussian time-ordering contribution. The exact relative unitary avoids
the nonnormal-root obstruction, but its required convergence must be proved.

Minimal discriminating intervention: turn on J1x in the transverse-field
model D=h sum Z+J sum XX. The recurrence predicts

    mu_0=1, mu_2=4h^2, mu_4=16h^4+32h^2 J^2          (ring/infinite),
    mu_4=16h^4+16h^2 J^2                             (endpoint N>=2).

Thus sigma(t)^2=t^2-h^2 t^4/3+(2h^4+4h^2 J^2)t^6/45+O(t^8)
for the ring; ignoring detector interactions predicts the wrong t^6 term.
The leading commutator of the ring fluctuations obeys

    ||[M/sqrt(N), i[D,M/sqrt(N)]]||_(2,tau)^2=16h^2/N.

The finite-N first echo moment has the independent Taylor prediction

    tau(W(t))=1-2g^2 t^2
        +[2g^4-4g^4/(3N)+(2/3)g^2h^2]t^4+O(t^6),
    W=exp(it[D-gM/sqrt(N)]) exp(-it[D+gM/sqrt(N)]).

These are cheap exact checks, not proof of the full limiting law.

## Candidate recurrence

Represent a Pauli word by finitely many nonidentity site factors. Starting
with X_0, apply L(O)=[D,O], keeping only Hamiltonian terms whose support
overlaps the word. Use XY=iZ, YZ=iX, ZX=iY and reversed-product minus signs.
No spatial truncation is used on the infinite chain: each finite commutator
order reaches only finitely many sites. For the collective observable,

    mu_2k = sum_j [coefficient of X_j in L^(2k)(X_0)].

For an endpoint observable keep only the X_0 coefficient on the half/open
chain. Periodic reduction modulo N supplies finite-ring certificates.
Candidate implementation: `core/analytic_liouvillian.py`; independent v3
uses full exact Pauli matrices and the identity
mu_2k=||L^k(M)||_(2,tau)^2/N instead of this coefficient recurrence.

For full XYZ the second moment predicts

    mu_2=4(hy^2+hz^2)+8(J1y-J1z)^2+8(J2y-J2z)^2.

This isolates which coefficients first change the collective detector motion.
Zeroing the transverse field and Jdy-Jdz terms returns the conserved-M case.

## Proof tasks before promotion

1. Bound fluctuation commutators in normalized Hilbert-Schmidt norm uniformly
   on every compact time interval by C_T/sqrt(N), using tracial locality.
2. Control time ordering of the exact echo by that bound, not an unbounded
   operator-norm first-Magnus approximation.
3. Prove the scalar CLT for the time-integrated quasi-local observable, then
   pass its characteristic functions to unitary spectral moments.
4. Give an exact constructive representation of nu (local moments and a
   determinate moment problem), rather than a formal many-body spectral sum.
5. Establish the Cesàro average after the thermodynamic limit, including
   atoms and low-frequency spectral weight; compute the measure-defined R.

The locality input is bounded finite-range dynamics and conditional-expectation
localization, as in Nachtergaele, Sims and Young, Theorem 3.1, Theorem 3.5 and
Section 4 of [Quasi-Locality Bounds I](https://arxiv.org/abs/1810.02428).
The proposed echo/CLT/root and time-average deductions are this report's
research claims, not claims attributed to that source.
