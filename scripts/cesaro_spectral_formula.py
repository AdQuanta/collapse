"""Spectral analysis of the time-dependent root moments.

For the paramagnetic endpoint chain (hz > J1x, h0x=0):
m_ell(t) = tau(W(t)^ell) is a real-valued quasi-periodic function of t.

Its Cesàro average equals the zero-frequency Fourier component.
If m_ell(t) has a finite number of incommensurate frequencies, the
Cesàro average is the DC component. If it has a continuous spectrum,
the Cesàro average is the spectral weight at zero.

Since H_+ = D + gx X_1 is a finite-dimensional Hamiltonian with discrete
spectrum {E_j}, U_+ = sum_j |j><j| exp(-i E_j t), and:
tau(W) = (1/2^N) sum_{j,k} |<j|P_D|k>|^2 exp(i(E_k^(-) - E_j^(+))t)
       = (1/2^N) sum_{j,k} c_{jk} exp(i omega_{jk} t)

where omega_{jk} = E_k - E_j are frequency differences of H_+.
(Since P_D H_+ P_D = H_-, the eigenvalues of H_- are related to those
of H_+ by the parity conjugation.)

The Cesàro average picks out j,k pairs where E_k^(-) = E_j^(+),
i.e., where an eigenvalue of H_- equals an eigenvalue of H_+.

Since P_D H_+ P_D = H_-, if |j> is an eigenstate of H_+ with energy E,
then P_D|j> is an eigenstate of H_- with the SAME energy E.
So H_+ and H_- have the SAME spectrum! The energy levels are shared.

If the spectrum of H_+ is non-degenerate, then for each eigenvalue E_j:
H_+ |j> = E_j |j>, H_- (P_D|j>) = E_j (P_D|j>).

The Cesàro average of tau(W) is then:
b_1 = sum_j (1/2^N) |<j|P_D|j>|^2

(only the diagonal j=k terms survive, since generically omega_{jk} = E_k - E_j != 0
for j != k.)

WAIT: the H_- eigenvalues ARE the H_+ eigenvalues (same spectrum),
but the eigenstates are P_D rotated. So the frequency differences
omega_{jk} = E_k^{H_-} - E_j^{H_+} = E_{sigma(k)} - E_j where
sigma is the permutation induced by P_D.

If the spectrum is non-degenerate, the zero-frequency terms are those
where sigma(k) = j, i.e., k = sigma^{-1}(j). So:

b_1 = sum_j (1/2^N) |<j|P_D|sigma^{-1}(j)>|^2

Actually, let me be more careful. Let {|j+>} be eigenstates of H_+
with energies E_j, and {|k->} = {P_D|k+>} be eigenstates of H_-.

W = sum_{j,k} |j+><j+| P_D |k+><k+| P_D U_+^dag
  = U_-^dag U_+
  = sum_{j,k} exp(i E_j t) |j-><j-| * exp(-i E_k t) |k+><k+|
  = sum_{j,k} exp(i(E_j - E_k)t) |j-><j-||k+><k+|

Hmm, W acts on the detector space. Let me use its eigendecomposition.

W = U_-^dag U_+ = sum_j exp(i E_j t) |j-> <j-| * sum_k exp(-i E_k t) |k+><k+|
  = sum_{j,k} exp(i(E_j - E_k)t) <j-|k+> |j-> ⊗ <k+|   (partial trace sense)

Actually: W = U_-^dag U_+ where both act on the detector space.
tau(W) = (1/2^N) sum_v <v|W|v>
       = (1/2^N) sum_v <v| (sum_j e^{iE_jt}|j-><j-|) (sum_k e^{-iE_kt}|k+><k+|) |v>
       = (1/2^N) sum_{j,k} e^{i(E_j-E_k)t} |<j-|k+>|^2   [wait, not right]

Actually: tau(W) = (1/2^N) Tr(W) = (1/2^N) sum_v <v|U_-^dag U_+|v>.

H_+ |k+> = E_k |k+>, so U_+ = sum_k e^{-iE_kt} |k+><k+|.
H_- |j-> = E_j |j->, so U_-^dag = sum_j e^{iE_jt} |j-><j-|.
(note: H_+ and H_- have the same eigenvalues since they're unitarily related)

W = sum_{j,k} e^{i(E_j-E_k)t} |j-><j-|k+><k+|.

tau(W) = (1/2^N) sum_{j,k} e^{i(E_j-E_k)t} <k+|j-><j-|k+>
       = (1/2^N) sum_{j,k} e^{i(E_j-E_k)t} |<j-|k+>|^2.

The Cesàro average (generic non-degenerate spectrum) picks out E_j = E_k:
b_1 = (1/2^N) sum_{j: E_j = E_k for some k} |<j-|j+>|^2

Since |j-> = P_D|j+>, the overlap is <j-|k+> = <j+|P_D|k+>.
For E_j = E_k and non-degenerate: only j = k contributes (since H_+ and H_-
share the same spectrum, the matching is one-to-one).

b_1 = (1/2^N) sum_j |<j+|P_D|j+>|^2

This is the average of the squared "parity expectation" over eigenstates.

For higher ell:
tau(W^ell) = (1/2^N) sum_{j1,...,j_ell, k1,...,k_ell} 
  prod exp(i(E_{j_m} - E_{k_m})t) * prod <j_m-|k_m+> <k_m+|j_{m+1}->

The Cesàro average at non-degenerate spectrum requires all frequency
differences to sum to zero: sum (E_{j_m} - E_{k_m}) = 0.

For the paramagnetic case, H_+ has a non-degenerate spectrum for generic
parameters. The simplest resonance condition is k_m = j_m for all m:
b_ell = (1/2^N) sum_j <j+|P_D|j+>^ell   (if all overlaps are real)

Wait, for real Hamiltonians, the eigenstates can be chosen real, and
P_D is real, so <j+|P_D|j+> is real. Thus <j+|P_D|j+>^ell is well-defined.

Let me verify: b_ell = (1/2^N) sum_j p_j^ell where p_j = <j+|P_D|j+>.
"""
import numpy as np
from scipy.linalg import expm
from functools import reduce

I2 = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def kron_list(ops):
    return reduce(np.kron, ops)


def verify_cesaro_formula(n, hz, j1x, gx, T=500, n_samples=2000, max_ell=8):
    """Verify: b_ell = (1/2^N) sum_j p_j^ell where p_j = <j+|P_D|j+>."""
    d = 2**n
    
    # Build H_+
    H_det = np.zeros((d, d), dtype=complex)
    for i in range(n):
        ops = [I2] * n; ops[i] = Z; H_det += hz * kron_list(ops)
    for i in range(n-1):
        ops = [I2] * n; ops[i] = X; ops[i+1] = X; H_det += j1x * kron_list(ops)
    
    X1 = kron_list([X if i==0 else I2 for i in range(n)])
    H_p = H_det + gx * X1
    H_m = H_det - gx * X1
    
    # Build P_D
    P_D = np.eye(d, dtype=complex)
    for i in range(n):
        ops = [I2] * n; ops[i] = Z; P_D = P_D @ kron_list(ops)
    
    # Eigendecompose H_+
    evals, evecs = np.linalg.eigh(H_p.real)
    
    # Compute p_j = <j+|P_D|j+>
    parity_expectations = np.array([
        np.real(evecs[:, j].conj() @ P_D @ evecs[:, j])
        for j in range(d)
    ])
    
    # Predicted Cesàro moments
    b_predicted = np.array([
        np.mean(parity_expectations**ell) for ell in range(max_ell)
    ])
    
    # Numerical Cesàro average
    dt = T / n_samples
    b_numerical = np.zeros(max_ell)
    for k in range(n_samples):
        t = (k + 0.5) * dt
        U_p = expm(-1j * H_p * t)
        U_m = expm(-1j * H_m * t)
        W = U_m.conj().T @ U_p
        W_power = np.eye(d, dtype=complex)
        for ell in range(max_ell):
            b_numerical[ell] += np.real(np.trace(W_power) / d) * dt
            W_power = W_power @ W
    b_numerical /= T
    
    return b_predicted, b_numerical, parity_expectations, evals


if __name__ == '__main__':
    print("=== Verify: b_ell = <p_j^ell> over H_+ eigenstates ===\n")
    
    for n, hz, j1x, gx in [(4, 1.0, 0.5, 0.3), (5, 1.0, 0.5, 0.3),
                             (4, 0.5, 1.0, 0.3), (5, 1.0, 1.0, 0.3)]:
        b_pred, b_num, pj, evals = verify_cesaro_formula(n, hz, j1x, gx, T=300, n_samples=1500)
        
        print(f"  N={n}, hz={hz}, J1x={j1x}, gx={gx}:")
        print(f"    Spectrum non-degenerate? min gap = {np.min(np.diff(np.sort(evals))):.6e}")
        
        for ell in range(1, 6):
            err = abs(b_pred[ell] - b_num[ell])
            print(f"    ell={ell}: predicted={b_pred[ell]:.8f}, numerical={b_num[ell]:.8f}, err={err:.2e}")
        
        # Distribution of parity expectations
        print(f"    Parity expectations p_j: min={pj.min():.4f}, max={pj.max():.4f}, "
              f"mean={pj.mean():.4f}, std={np.std(pj):.4f}")
        print()
    
    print("=== Check for degeneracies and off-diagonal contributions ===\n")
    
    # In the degenerate case, off-diagonal overlaps <j+|P_D|k+> with E_j = E_k
    # also contribute. Let me check.
    n, hz, j1x, gx = 4, 0.5, 1.0, 0.3
    d = 2**n
    
    H_det = np.zeros((d, d), dtype=complex)
    for i in range(n):
        ops = [I2] * n; ops[i] = Z; H_det += hz * kron_list(ops)
    for i in range(n-1):
        ops = [I2] * n; ops[i] = X; ops[i+1] = X; H_det += j1x * kron_list(ops)
    
    X1 = kron_list([X if i==0 else I2 for i in range(n)])
    H_p = H_det + gx * X1
    
    P_D = np.eye(d, dtype=complex)
    for i in range(n):
        ops = [I2] * n; ops[i] = Z; P_D = P_D @ kron_list(ops)
    
    evals, evecs = np.linalg.eigh(H_p.real)
    
    # Check for near-degenerate eigenvalues
    gaps = np.diff(np.sort(evals))
    print(f"  N={n} topological: smallest gaps = {np.sort(gaps)[:5]}")
    
    # The full Cesàro formula including degeneracies:
    # b_ell = (1/2^N) sum_{j,k: E_j=E_k} <j+|P_D|k+>^ell is wrong for ell>1.
    # 
    # The correct formula for ell=1 is:
    # b_1 = (1/2^N) sum_{j,k: E_j=E_k} |<j-|k+>|^2
    # where |j-> = P_D|j+>.
    #
    # But <j-|k+> = <j+|P_D|k+>, so:
    # b_1 = (1/2^N) sum_{j,k: E_j=E_k} |<j+|P_D|k+>|^2
    
    # For non-degenerate spectrum: only j=k, giving sum |<j+|P_D|j+>|^2.
    # For the topological case with near-degenerate pairs, we need the
    # full degenerate subspace treatment.
    
    # The CORRECT general formula for higher ell:
    # tau(W^ell) = (1/2^N) sum_{j1,k1,...,j_ell,k_ell}
    #   exp(i t sum_m (E_{j_m} - E_{k_m}))
    #   * prod_m <j_m+|P_D|k_m+> * <k_m+|j_{m+1}+>
    #
    # Wait, the structure is:
    # W = sum_{j,k} e^{i(E_j-E_k)t} |P_D j+><k+|   [with <P_D j+| = <j+|P_D^dag = <j+|P_D]
    #
    # Hmm, let me redo. W = U_-^dag U_+ where U_- = P_D U_+ P_D.
    # W = P_D U_+^dag P_D U_+ = P_D (sum_j e^{iE_jt}|j+><j+|) P_D (sum_k e^{-iE_kt}|k+><k+|)
    # = sum_{j,k} e^{i(E_j-E_k)t} P_D|j+><j+|P_D|k+><k+|
    # = sum_{j,k} e^{i(E_j-E_k)t} |j-><j+|P_D|k+><k+|
    #
    # But |j-> = P_D|j+> and <j+|P_D = <j-|, so:
    # W = sum_{j,k} e^{i(E_j-E_k)t} <j-|k+> |j-> <k+|
    #   = sum_{j,k} e^{i(E_j-E_k)t} M_{jk} |j-> <k+|
    # where M_{jk} = <j-|k+> = <j+|P_D|k+>.
    #
    # W^ell = sum_{j_1,k_1,...,j_ell,k_ell} prod_m [e^{i(E_{j_m}-E_{k_m})t} M_{j_m,k_m}]
    #         * |j_1-><k_1+|j_2-><k_2+| ... |j_ell-><k_ell+|
    #
    # The chain constraint is k_m = j_{m+1} (in the + basis), i.e.,
    # <k_m+|j_{m+1}-> = delta_{k_m,j_{m+1}} ... NO, the bases are different.
    # <k_m+|j_{m+1}-> = <k_m+|P_D|j_{m+1}+> = M_{j_{m+1},k_m}^*.
    # Hmm, this is getting complicated. Let me just verify numerically.
    
    # The simplest Cesàro prediction for non-degenerate spectrum:
    # b_ell = (1/2^N) sum_j (M_{jj})^ell = (1/2^N) sum_j p_j^ell
    # where p_j = <j+|P_D|j+>.
    
    # For the trace chain:
    # tau(W^ell) = (1/2^N) Tr(W^ell)
    # W = sum_{j,k} M_{jk} e^{i(E_j-E_k)t} |j-><k+|
    # 
    # Tr(W) = sum_j <j+|W|j+> + sum_j <j-|W|j-> ... no, just sum over any basis.
    # Using |k+> basis:
    # Tr(W) = sum_k <k+|W|k+> = sum_k sum_{j,j'} M_{jj'} e^{i(E_j-E_{j'})t} <k+|j-><j'+|k+>
    #       = sum_k sum_j M_{jk} e^{i(E_j-E_k)t} <k+|j->
    #       = sum_{j,k} M_{jk} M_{jk}^* e^{i(E_j-E_k)t}  [since <k+|j-> = M_{jk}^*]
    #
    # Wait: <k+|j-> = <k+|P_D|j+> = M_{j,k}. So:
    # Tr(W) = sum_{j,k} M_{jk} M_{jk} e^{i(E_j-E_k)t}
    #       = sum_{j,k} (M_{jk})^2 e^{i(E_j-E_k)t}
    #
    # But M_{jk} = <j+|P_D|k+> is real (real basis), and M is symmetric
    # (P_D is Hermitian and real: P_D^T = P_D).
    
    # So Tr(W) = sum_{j,k} M_{jk}^2 cos((E_j-E_k)t) (imaginary part cancels by symmetry).
    # Cesàro average: b_1 = (1/2^N) sum_j M_{jj}^2 = (1/2^N) sum_j p_j^2.
    
    # For W^2:
    # W^2 = sum_{j1,k1,j2,k2} M_{j1,k1} M_{j2,k2} e^{i((E_{j1}-E_{k1})+(E_{j2}-E_{k2}))t}
    #        |j1-><k1+|j2-><k2+|
    # <k1+|j2-> = M_{j2,k1}, so:
    # W^2 = sum_{j1,k1,j2,k2} M_{j1,k1} M_{j2,k1} M_{j2,k2} 
    #        e^{i((E_{j1}-E_{k1})+(E_{j2}-E_{k2}))t} |j1-><k2+|
    
    # Hmm wait: <k1+|j2-> = <k1+|P_D j2+> = M_{j2,k1}. And:
    # W^2 = sum_{j1,j2,k1,k2} M_{j1,k1} M_{j2,k1} M_{j2,k2} ... no, it's
    # sum M_{j1,k1} * <k1+|j2-> * M_{j2,k2} = sum M_{j1,k1} M_{j2,k1} M_{j2,k2}
    # ... with middle contraction giving M matrix multiplication.
    
    # Actually, define the operator in the |j+> basis:
    # <j+|W|k+> = sum_{j',k'} M_{j',k'} e^{i(E_{j'}-E_{k'})t} <j+|j'-><k'+|k+>
    # = sum_{j'} M_{j',k} e^{i(E_{j'}-E_k)t} <j+|j'->
    # = sum_{j'} M_{j',k} M_{j',j} e^{i(E_{j'}-E_k)t}
    
    # So in the |+> basis, the matrix elements of W are:
    # W_{jk} = sum_{j'} M_{j'j} M_{j'k} e^{i(E_{j'}-E_k)t}
    # = [M^T diag(e^{iE_{j'}t}) M]_{jk} * e^{-iE_k t}
    
    # Or more neatly: let D(t) = diag(e^{iE_jt}). Then:
    # W = M^T D(t) M D(-t)   in the |+> basis.
    
    # Trace: Tr(W) = Tr(M^T D(t) M D(-t)) = sum_{j,k} M_{kj} e^{iE_kt} M_{jk}... 
    # Hmm, this is just sum_{j,k} M_{jk}^2 e^{i(E_j-E_k)t}. Same as before ✓.
    
    # For W^ell in the |+> basis:
    # W^ell = (M^T D M D^{-1})^ell
    
    # Since M and D don't commute, this doesn't simplify further.
    # But the Cesàro average picks out the diagonal of D:
    # At non-degenerate spectrum, Cesàro of W = M^T * diag(M_{jj}) * M * ???
    # 
    # Actually, Cesàro of D(t)_{jk} D(-t)_{kl} = delta_{jk} delta_{kl} = delta_{jl} delta_{jk}.
    # So Cesàro of <j|W|k> = sum_{j'} M_{j'j} M_{j'k} * [Cesàro of e^{i(E_{j'}-E_k)t}]
    # = M_{kj} M_{kk} = M_{jk} p_k   (using M symmetric, and p_k = M_{kk}).
    
    # So <j|W_avg|k> = M_{jk} p_k  in the |+> basis.
    # W_avg = M * diag(p_k).
    
    # Tr(W_avg) = sum_j M_{jj} p_j = sum_j p_j^2 ✓
    
    # Tr(W_avg^ell) = Tr((M*diag(p))^ell)
    # = sum_{j1,...,j_ell} M_{j1,j2} p_{j2} M_{j2,j3} p_{j3} ... M_{j_ell,j1} p_{j1}
    
    # So b_ell = (1/2^N) Tr((M * diag(p))^ell).
    
    # THIS IS THE EXACT CESÀRO FORMULA for non-degenerate spectrum.
    
    # Verify this:
    M = evecs.T.real @ P_D.real @ evecs.real  # M_{jk} = <j+|P_D|k+>
    pj = np.diag(M)
    
    W_avg = M @ np.diag(pj)
    
    b_pred_new = np.array([np.real(np.trace(np.linalg.matrix_power(W_avg, ell)) / d)
                           for ell in range(8)])
    
    _, b_num, _, _ = verify_cesaro_formula(n, hz, j1x, gx, T=500, n_samples=2000)
    
    print(f"\n  Exact Cesàro formula: b_ell = (1/2^N) Tr((M diag(p))^ell)")
    print(f"  N={n}, hz={hz}, J1x={j1x}, gx={gx}:")
    for ell in range(1, 6):
        err = abs(b_pred_new[ell] - b_num[ell])
        print(f"    ell={ell}: formula={b_pred_new[ell]:.8f}, cesaro={b_num[ell]:.8f}, err={err:.2e}")
    
    # Also verify for paramagnetic case
    print()
    n, hz, j1x, gx = 5, 1.0, 0.5, 0.3
    d = 2**n
    
    H_det = np.zeros((d, d), dtype=complex)
    for i in range(n):
        ops = [I2] * n; ops[i] = Z; H_det += hz * kron_list(ops)
    for i in range(n-1):
        ops = [I2] * n; ops[i] = X; ops[i+1] = X; H_det += j1x * kron_list(ops)
    
    X1 = kron_list([X if i==0 else I2 for i in range(n)])
    H_p = H_det + gx * X1
    P_D = np.eye(d, dtype=complex)
    for i in range(n):
        ops = [I2] * n; ops[i] = Z; P_D = P_D @ kron_list(ops)
    
    evals_p, evecs_p = np.linalg.eigh(H_p.real)
    M = evecs_p.T.real @ P_D.real @ evecs_p.real
    pj = np.diag(M)
    W_avg = M @ np.diag(pj)
    
    b_pred_new = np.array([np.real(np.trace(np.linalg.matrix_power(W_avg, ell)) / d)
                           for ell in range(8)])
    
    _, b_num, _, _ = verify_cesaro_formula(n, hz, j1x, gx, T=500, n_samples=2000)
    
    print(f"  Paramagnetic: N={n}, hz={hz}, J1x={j1x}, gx={gx}:")
    print(f"  Spectrum gap: {np.min(np.diff(np.sort(evals_p))):.6e}")
    for ell in range(1, 8):
        err = abs(b_pred_new[ell] - b_num[ell])
        print(f"    ell={ell}: formula={b_pred_new[ell]:.8f}, cesaro={b_num[ell]:.8f}, err={err:.2e}")
    
    # Distribution of parity expectations
    print(f"\n    p_j stats: mean={pj.mean():.6f}, std={np.std(pj):.6f}")
    print(f"    p_j values: {np.sort(pj)[:5]}...{np.sort(pj)[-5:]}")
