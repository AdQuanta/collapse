# Coefficient ledger

Status: **OPEN** for the full goal. Date: 2026-09-13.
Step numbers match the requested ladder; extensions do not fill intervening
unsolved steps. All omitted coefficients are zero unless explicitly retained.

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
| ring | 4, interacting | gx,hx,J1x,hz | conditional-unitary reduction only | OPEN | OPEN | OPEN | OPEN |
| chain | 4, interacting | gx,hx,J1x,hz | conditional-unitary reduction only | OPEN | OPEN | OPEN | OPEN |
| ring and chain | 5 | full NN XYZ | OPEN | OPEN | OPEN | OPEN | OPEN |
| ring and chain | 6 | full NN + NNN XYZ | OPEN | OPEN | OPEN | OPEN | OPEN |
| ring and chain | 7 | additional coupling axes | singular cases proved; regular-domain law OPEN | OPEN | OPEN | OPEN | OPEN, report 02 |
| ring and chain | 8 | remaining fields | OPEN | OPEN | OPEN | OPEN | OPEN |
| ring and chain | 9 | full family | singular domain obstruction; regular-domain characterization OPEN | OPEN | OPEN | OPEN | OPEN |

All gx=0/zero-frequency exceptions and atomic supports are specified in the
reports. The uniform result is a density with respect to dtheta, not sphere
area. Neither a subfamily solution nor a singular-time counterexample meets
the full goal's completion conditions.

Next highest-information question: for the interacting central-X ring,
does the tracial fluctuation limit of the exact relative-unitary echo yield
a folded Gaussian whose variance is the integrated infinite-temperature
detector X autocorrelation? This is **CONJECTURE** until time-ordered
cumulants and uniform finite-time error estimates are controlled. For the
endpoint chain the coupling remains local, so that collective CLT cannot
be transferred without a separate argument. Existing Schur/Volterra and
projective-potential tools remain available for later multichannel work.
