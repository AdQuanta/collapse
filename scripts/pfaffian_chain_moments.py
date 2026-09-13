"""Exact Pfaffian formula for endpoint chain root moments.

The root moments are tau_det(W^ell) where W = P_D U_+^dag P_D U_+.
Here P_D = (-i)^N prod_{j=1}^N Z_j is the detector parity.

Since U_+ = exp(-it H_+) with H_+ = D + gx X_1 operates on the
detector-only space, and D + gx X_1 has a linear Majorana perturbation,
we cannot use the standard free-fermion trace formula directly on the
detector space.

However, we can use the FULL (qubit+detector) free-fermion system.
The key insight: express tau_det(W^ell) as a full-system expectation
involving qubit projectors and detector parity.

Approach: since X_0 is conserved, the full unitary has block structure.
In the X_0 eigenbasis, U_full = P_+ U_+ + P_- U_- where
P_± = (I ± X_0)/2.

Then:
tau_det(W^ell) = tau_det((U_-^dag U_+)^ell)
              = tau_det((P_D U_+^dag P_D U_+)^ell)

For ell = 1:
tau_det(W) = tau_det(P_D U_+^dag P_D U_+)
           = (1/2^N) Tr_det(P_D e^{it H_+} P_D e^{-it H_+})

Now map to the full space:
(1/2^N) Tr_det(P_D U_+^dag P_D U_+)
= (1/2^N) Tr_det(P_D U_+^dag P_D U_+)
= (2/2^{N+1}) Tr_det(P_D <+|U_full^dag|+> P_D <+|U_full|+>)

This isn't clean. Let me try differently.

Alternative: Use the Pfaffian of the restricted correlation matrix.

In the FULL free-fermion system at the tracial state, the Majorana
two-point function is G_{jk} = tau(gamma_j gamma_k) = delta_{jk}.
Under unitary evolution, G -> R G R^T = R R^T = I (since R is orthogonal).
So the time-evolved state is still the tracial state — nothing changes!

This makes sense: the tracial state (infinite temperature) is invariant
under all unitary evolution. So the question is purely about the
operator structure, not about a non-trivial state.

What we really need is:
tau_det(W^ell) = ?

Key idea: express W^ell in terms of full-system operators and use the
full-system tracial Wick theorem.

W = U_-^dag U_+  where U_pm = <pm|_Q U_full |pm>_Q

For ell=1:
tau_full(P_+ W P_+) = tau_full(P_+ U_-^dag U_+ P_+)
But P_+ U_-^dag = 0 since U_- maps the minus sector.

This doesn't work. Let me think about it differently.

Actually, we should use:
tau_full((I + X_0(t))/2 * (I + X_0)/2)  -- this gives a related quantity.

OR: we should recognize that tau_det(W) is a CONDITIONAL EXPECTATION
in the full free-fermion system. Specifically:

2^N tau_det(W) = Tr_det(W) = Tr_det(U_-^dag U_+)
                = sum_v <v| U_-^dag U_+ |v>  (sum over detector states v)
                = sum_v <-,v| U_full^dag |+> <+| U_full |-,v>  NO wrong.

Actually U_full |+,v> = |+> U_+ |v>  and  U_full |-,v> = |-> U_- |v>.

So <+,v| U_full^dag = <+| <v| U_+^dag  and  U_full |+,v> = |+> U_+ |v>.

Thus:
sum_v <v| U_-^dag U_+ |v> = Tr_det(U_-^dag U_+) = 2^N tau_det(W).

In the full space:
Tr_full(P_- U_full^dag P_+ U_full) = sum_{sigma,v} <sigma,v| P_- U^dag P_+ U |sigma,v>
  = sum_v <-,v| U^dag |+> <+| U |-,v>
  = sum_v (<v| U_-^dag)(U_+ |v>) ... NO.

<-,v| U^dag = <v| U_-^dag <-| ... but |±> is in the qubit space.

Let me be very explicit. |sigma> is a qubit state, |v> is a detector state.

U_full |+,v> = |+,U_+v> (since U_full = |+><+|⊗U_+ + |-><-|⊗U_-)
U_full |-,v> = |-,U_-v>

P_+ = |+><+|⊗I,  P_- = |-><-|⊗I.

Tr_full(P_- U^dag P_+ U) 
= sum_{sigma,v} <sigma,v| P_- U^dag P_+ U |sigma,v>
= sum_v <-,v| U^dag P_+ U |-,v>
= sum_v <-,v| U^dag (|+><+|⊗I) U |-,v>
= sum_v (<-,v| U^dag |+>) (<+| U |-,v>)_full ... wait, <+| is in qubit space.

More carefully:
<-,v| U^dag = <-| <v| (|+><+|⊗U_+^dag + |-><-|⊗U_-^dag) = <v| U_-^dag <-,+> ... 

Hmm, let me use P_+ U = |+><+| U_+ + |-><-| P_+ U_-. But |-><-| |+><+| = 0.
So P_+ U P_- = |+><+| U_+ |-><-| = |+><-| ⊗ ... NO.

OK, P_+ U_full = (|+><+|⊗I)(|+><+|⊗U_+ + |-><-|⊗U_-)  = |+><+|⊗U_+.

Tr(P_- U^dag P_+ U) = Tr((|-><-|⊗I)(|+><+|⊗U_+^dag + |-><-|⊗U_-^dag)(|+><+|⊗U_+))
= Tr((|-><-|)(|+><+|⊗U_+^dag)(|+><+|⊗U_+))   -- the U_-^dag term vanishes
= Tr(|-><-||+><+|⊗U_+^dag U_+)
= <+|-> * <-|+> * Tr(I)  = 0.

So this particular combination vanishes. Let me try another approach.

Actually, the key object is:
tau_det(W) = (1/2^N) Tr_det(U_-^dag U_+)

Using the full space, note that X_0 = sigma_x on the qubit. In the
computational basis, <0|+> = <1|+> = 1/sqrt(2), <0|-> = 1/sqrt(2), <1|-> = -1/sqrt(2).

U_+ = sqrt(2) <+| U_full |+>_Q  (projected).
U_- = sqrt(2) <-| U_full |->_Q.

So 2^N tau_det(W) = Tr_det(U_-^dag U_+) 
= 2 sum_v <v| (<-| U_full^dag |->) (<+| U_full |+>) |v>
= 2 Tr_det(<-|U^dag|-><+|U|+>)

In the full space:
= 2 Tr_full(|-><-|⊗I * U^dag * |-><+|⊗I * U * |+><+|⊗I)   Hmm...

Let's try yet another way using the X_0 projector directly.

We know X_0 is conserved, so U X_0 = X_0 U.

tau_det(W) involves the CONDITIONAL unitary dynamics. In the full
system, the root moments can be expressed as:

m_ell(t) = Re tau_det(W^ell) = Re(e^{-2i ell h0x t} tau_det(W'^ell))
  where W' is the h0x=0 relative unitary.

For h0x=0, the full-system trace gives:

tau_full(X_0^{2ell}) = 1  (trivially).

What we need is more like:
tau_full(f(X_0, U)) where f extracts the conditional dynamics.

THE KEY FORMULA: The Loschmidt echo representation.

m_ell(t) = Re tau_det(P_D(t)^ell P_D^ell)

where P_D(t) = U_+^dag P_D U_+ = exp(it H_+) P_D exp(-it H_+)
is the time-evolved detector parity.

Since W = P_D U_+^dag P_D U_+ = P_D P_D(t):
W^ell = (P_D P_D(t))^ell.

But P_D^2 = I, so this is NOT simply (P_D(t))^{2ell}. The alternating
product P_D P_D(t) P_D P_D(t) ... does not simplify to P_D^ell P_D(t)^ell
because P_D and P_D(t) generally don't commute.

For ell=1: W = P_D P_D(t), and tau(W) = tau(P_D P_D(t)).
Since P_D^2 = I, tau(P_D P_D(t)) = tau(P_D exp(itH_+) P_D exp(-itH_+)).
With P_D H_+ P_D = H_-:
P_D exp(-itH_+) = exp(-itH_-) P_D, so:
P_D(t) = exp(itH_+) P_D exp(-itH_+) = exp(itH_+) exp(-itH_-) P_D.

tau(P_D P_D(t)) = tau(P_D exp(itH_+) exp(-itH_-) P_D) = tau(exp(itH_+) exp(-itH_-)).
(cyclicity of trace.)

WAIT. tau(P_D P_D(t)) = tau(P_D exp(itH_+) P_D exp(-itH_+))
Using P_D exp(-itH_+) = exp(-itH_-) P_D:
= tau(P_D exp(itH_+) exp(-itH_-) P_D) = tau(exp(itH_+) exp(-itH_-) P_D^2)
= tau(exp(itH_+) exp(-itH_-)).

So tau(W) = tau(exp(itH_+) exp(-itH_-)) = tau(U_+^dag U_-^dag) ... no.

tau(U_-^dag U_+) = tau(exp(itH_-) exp(-itH_+)) (using U = exp(-itH)).

Let me verify: W = U_-^dag U_+ = exp(itH_-) exp(-itH_+).
tau(W) = (1/2^N) Tr(exp(itH_-) exp(-itH_+)).

And from the echo: tau(P_D P_D(t)) = tau(P_D U_+^dag P_D U_+)
= (1/2^N) Tr(P_D exp(itH_+) P_D exp(-itH_+))
= (1/2^N) Tr(P_D exp(itH_+) exp(-itH_-) P_D)  (using P_D exp(-itH_+) = exp(-itH_-) P_D)
= (1/2^N) Tr(exp(itH_+) exp(-itH_-) P_D^2)  (cyclicity)
= (1/2^N) Tr(exp(itH_+) exp(-itH_-))
= tau(exp(itH_+) exp(-itH_-)) = tau(W^{-1}).

But W is unitary, so tau(W^{-1}) = tau(W^dag) = conj(tau(W)).
And tau(W) = Re tau(W) + i Im tau(W), so tau(W^{-1}) = Re tau(W) - i Im tau(W).
These are equal only if Im tau(W) = 0.

Hmm, so tau(P_D P_D(t)) = conj(tau(W)), not tau(W). Let me recheck.

W = U_-^dag U_+ = exp(itH_-) exp(-itH_+).
tau(W) = (1/2^N) Tr(exp(itH_-) exp(-itH_+)).

Conjugate: tau(W)^* = (1/2^N) Tr(exp(-itH_-) exp(itH_+))
         = (1/2^N) Tr(exp(itH_+) exp(-itH_-))  (cyclicity)
         = tau(exp(itH_+) exp(-itH_-)).

And I showed tau(P_D P_D(t)) = tau(exp(itH_+) exp(-itH_-)) = tau(W)^*.

So m_1 = Re tau(W) = Re tau(W)^* = Re tau(P_D P_D(t)). ✓

For higher ell, the echo representation is:
W^ell = (P_D P_D(t))^ell

which is a product of 2ell Majorana-bilinear unitaries (P_D is a
product of N Majorana bilinears, and P_D(t) is its time evolution).

For the FULL system (h0x = 0), H_+ acts on the detector only.
In the full space, H_+ = D + gx X_1 = D + gx (Z_0 gamma_2) in the
full JW numbering. But in the conditional picture after projecting
X_0 = +1: X_1 -> X_1 = gamma_2 in the detector-only JW.

This is the fundamental difficulty: the detector parity echo involves
non-Gaussian operators in the detector space, and cannot be directly
computed from the full-system free-fermion data without additional work.

CONCLUSION: The Pfaffian/free-fermion shortcut does NOT directly give
the root moments tau(W^ell) for the interacting endpoint chain. The
conditional Hamiltonians H_pm break the free-fermion structure on the
detector space. The exact computation requires either:

(a) Diagonalizing the finite-N many-body H_pm (exponentially costly), or
(b) Finding an alternative exact representation that avoids the parity-
    breaking linear Majorana term.

For the Cesàro average, option (b) requires understanding the spectral
decomposition of the time-periodic function tau(W(t)^ell).
"""

# Let me verify my echo formula computationally
import numpy as np
from scipy.linalg import expm
from functools import reduce

I2 = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def kron_list(ops):
    return reduce(np.kron, ops)

n = 4
hz, j1x, gx = 1.0, 0.5, 0.3
t = 1.0
d = 2**n

H_det = np.zeros((d, d), dtype=complex)
for i in range(n):
    ops = [I2] * n; ops[i] = Z; H_det += hz * kron_list(ops)
for i in range(n-1):
    ops = [I2] * n; ops[i] = X; ops[i+1] = X; H_det += j1x * kron_list(ops)

X1 = kron_list([X if i==0 else I2 for i in range(n)])
H_p = H_det + gx * X1
H_m = H_det - gx * X1

U_p = expm(-1j * H_p * t)
U_m = expm(-1j * H_m * t)
W = U_m.conj().T @ U_p

# Build P_D
P_D = np.eye(d, dtype=complex)
for i in range(n):
    ops = [I2] * n; ops[i] = Z; P_D = P_D @ kron_list(ops)

# Echo: W_echo = P_D U_+^dag P_D U_+
W_echo = P_D @ U_p.conj().T @ P_D @ U_p
print(f"W == W_echo? {np.allclose(W, W_echo)}")

# Verify: tau(P_D P_D(t)) = tau(W)^*
P_D_t = U_p.conj().T @ P_D @ U_p
tau_PD_PDt = np.trace(P_D @ P_D_t) / d
tau_W = np.trace(W) / d
print(f"tau(W)        = {tau_W}")
print(f"tau(P_D P_D(t)) = {tau_PD_PDt}")
print(f"tau(W)^*        = {np.conj(tau_W)}")
print(f"Match? {np.allclose(tau_PD_PDt, np.conj(tau_W))}")

# For higher ell: tau(W^ell) vs tau((P_D P_D(t))^ell)
for ell in range(1, 6):
    W_power = np.linalg.matrix_power(W, ell)
    echo_power = np.linalg.matrix_power(P_D @ P_D_t, ell)
    tau_W_ell = np.trace(W_power) / d
    tau_echo_ell = np.trace(echo_power) / d
    print(f"ell={ell}: tau(W^ell)={tau_W_ell:.8f}, tau((P_D P_D(t))^ell)={tau_echo_ell:.8f}, "
          f"match_conj? {np.allclose(tau_echo_ell, np.conj(tau_W_ell))}")

# Now test the key idea: can we compute tau(W^ell) using the FULL
# free-fermion system without breaking into parity sectors?

# In the full system, consider the operator:
# A_full(t) = (I + X_0)/2 ⊗ U_+(t)  ... but this isn't what we need.

# What about: construct the full-system W by using the fact that
# the full propagator U is a Gaussian unitary on 2(N+1) modes?

# The full rotation matrix R gives U gamma_j U^dag = sum_k R_{kj} gamma_k.
# The full tracial state has <gamma_j gamma_k>_tau = delta_{jk}.

# For the X_0 = +1 sector, the conditional dynamics involves projecting
# onto P_+ = (I + gamma_0)/2 for the qubit.

# In the tracial state conditioned on gamma_0 = +1 (i.e., X_0 = +1),
# the detector-only observables have specific correlation functions
# that involve gamma_0 through projection.

# This is the "boundary CFT" / "edge state" interpretation of the problem.
