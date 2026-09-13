# Coefficient ledger [SUPERSEDED]

> [!IMPORTANT]
> **This original coefficient ledger has been superseded and replaced by the authoritative atomic master ledgers in the wiki:**
> - **Ring geometry:** [`wiki/campaigns/analytic_distribution_ring_master_ledger.md`](../../wiki/campaigns/analytic_distribution_ring_master_ledger.md)
> - **Endpoint chain geometry:** [`wiki/campaigns/analytic_distribution_chain_master_ledger.md`](../../wiki/campaigns/analytic_distribution_chain_master_ledger.md)
>
> All active case classification, status tracking, and analytical program records are now maintained separately per geometry in the wiki master ledgers above.

Status: **SUPERSEDED** (active progress tracked in wiki master ledgers). Date: 2026-09-13.
Historical summary of initial 9-step ladder below:

| Family | Step | Coefficients ON | P_N | N→∞ | Time average | R(theta) | Status |
|---|---|---|---|---|---|---|---|
| ring | 1 | gx | binomial folded atoms | folded Gaussian | uniform if gx!=0 | 1/2 | PROVED, report 01 |
| chain | 1 | gx | one folded atom | unchanged | uniform if gx!=0 | 1/2 | PROVED, report 01 |
| ring | 2 | gx,hx | same as step 1 | same | same | same | PROVED, report 01 |
| chain | 2 | gx,hx | same as step 1 | same | same | same | PROVED, report 01 |
| ring | 3 | gx,hx,J1x | same as step 1 | same | same | same | PROVED, report 01 |
| chain | 3 | gx,hx,J1x | same as step 1 | same | same | same | PROVED, report 01 |
| ring | commuting extension of 6 | gx,hx,J1x,J2x | same as step 1 | same | same | same | PROVED, report 01 |
| chain | commuting extension of 6 | gx,hx,J1x,J2x | same as step 1 | same | same | same | PROVED, report 01 |
| ring | commuting central-field extension | previous + h0x | shifted binomial | shifted folded Gaussian | uniform unless gx=h0x=0 | 1/2 or atomic | PROVED, report 01 |
| chain | commuting central-field extension | previous + h0x | two atoms | unchanged | uniform/zero-frequency atom mixture | explicit measure ratio | PROVED, report 01 |
| ring | 4, J1x=J2x=hx=0 slice | gx,hz | SU2 binomial atoms | periodically refocused Gaussian | explicit positive mixture/Bessel moments | explicit density ratio | PROVED, report 03 |
| chain | 4, J1x=J2x=hx=0 slice | gx,hz | one SU2 atom | unchanged | explicit arcsine polar cap | explicit density ratio | PROVED, report 03 |
| ring | 4, interacting | gx,hx,J1x,hz | exact Pauli/Newton recurrence | proved folded Gaussian via local autocorrelation | proved spectral atom formula; uniform if hx!=0 | exact measure formula; 1/2 if hx!=0 | PROVED representation, report 05 |
| chain | 4, interacting | gx,hx,J1x,hz | exact conditional-unitary recurrence | proved norm limit | OPEN | OPEN | partial PROVED, report 07 |
| ring | 5 | gx,h0x,detector fields,full NN XYZ | exact Pauli/Newton recurrence | proved folded Gaussian via local autocorrelation | proved spectral atom formula; uniform if hx!=0 | exact measure formula | PROVED representation, report 05 |
| chain | 5 | gx,h0x,detector fields,full NN XYZ | exact conditional-unitary recurrence | proved norm limit | uniform for a.e. h0x; exceptional fields OPEN | 1/2 for a.e. h0x | PROVED a.e.-field result, reports 07,10 |
| ring | 6 | previous + detector NNN XYZ | exact Pauli/Newton recurrence | proved folded Gaussian via local autocorrelation | proved spectral atom formula; uniform if hx!=0 | exact measure formula | PROVED representation, report 05 |
| chain | 6 | previous + detector NNN XYZ | exact conditional-unitary recurrence | proved norm limit | uniform for a.e. h0x; exceptional fields OPEN | 1/2 for a.e. h0x | PROVED a.e.-field result, reports 07,10 |
| ring and chain | 7 | additional coupling axes | singular cases proved; regular-domain law OPEN | OPEN | OPEN | OPEN | OPEN, report 02 |
| ring and chain | 8 | remaining fields | OPEN | OPEN | OPEN | OPEN | OPEN |
| ring and chain | 9 | full family | singular domain obstruction; regular-domain characterization OPEN | OPEN | OPEN | OPEN | OPEN |

All gx=0/zero-frequency exceptions and atomic supports are specified in the
reports. The uniform result is a density with respect to dtheta, not sphere
area. Neither a subfamily solution nor a singular-time counterexample meets
the full goal's completion conditions.

Next highest-information question: establish the interacting endpoint-chain
Cesàro measure at the remaining exceptional prescribed central fields,
retaining hx and general detector XYZ/NNN terms, or cross the next central-
axis obstruction. Report 10 now proves the full uniform ordered probability
law and R=1/2 for a.e. h0x by scalar modulation and Plancherel; this does
not identify the null exceptional set or cover h0x=0 automatically.
Report 09 proves the first-moment mean at every h0x via
a local self-adjoint Liouvillian. The higher-moment replica functional
has norm 2^(N(ell-1)); an N-uniform bound on its actual spectral variation
would suffice but is OPEN. Second-moment variations 2.14→6.27 at N=2–5
do not justify that bound. Seek weaker near-zero cancellation/locality
control of every moment at exceptional fields; neither the first-moment
nor a.e.-field result fills the arbitrary-parameter completion requirements.
The restricted hx=0 boundary-Majorana work is parked following the user's
focus correction: no dependency from that benchmark to the full result has
been established. The v4 candidate check failed at the bound pole equation;
its append-only record is retained and the candidate is not promoted.
Additional central coupling axes still require a separate nonnormal-root
argument. No new benchmark should be expanded without identifying the
specific full-goal obstruction it resolves.
The ring echo conjecture is now PROVED in its central-X scope in report 05;
its spectral recurrence determines the generic law, with an explicitly
uniform average whenever the detector hx and gx are nonzero.
