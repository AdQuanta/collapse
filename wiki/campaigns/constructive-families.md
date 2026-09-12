# Constructive Born-like Families

## Objective
Find a specific, analytically certified class of Hamiltonians that satisfy the declared "Born-like" finite-resolution gate.

## The Acceptance Gate ($C_B$)
The current study uses a binary "pass/fail" gate based on a 64-bin histogram of roots:
1. **Full Coverage**: Every bin must have at least one root.
2. **Ratio RMSE**: Root-count ratio RMSE $\le 0.05$ against $\cos^2(\theta/2)$.
3. **Moment Residuals**: Maximal absolute Born moment residual $\le 0.05$ over the first eight relations $d_m = 2a_{2m+1} - a_{2m} - a_{2m+2}$.

## The Constructive Commuting Class
A sufficient family is constructed using the "Commuting X/XX" class:
$$ H = K - h_{x0}X_q - h_{z0}Z_q - X_q \sum g_i X_i $$
where $K$ is any detector-only Hamiltonian that commutes with all $X_i$.

### Why it works
The condition $[K, V] = 0$ allows for an exact reduction of the many-body problem to a set of $2^N$ independent two-dimensional conditional qubit blocks. The projective roots are determined by the "folded" coupling spectrum $\sum s_i g_i$. By carefully choosing the $g_i$ values (using a specific set of thirteen divisors), one can "design" a root distribution that passes the $C_B$ gate.

## Key Results
- **Existence**: A nonempty native Hamiltonian family satisfies $C_B$ analytically.
- **Broadness**: This family allows arbitrary detector size $N \ge 13$, arbitrary commuting detector dynamics $K$, and an open neighborhood of coupling/field perturbations.
- **Non-Necessity**: This family proves that neither detector chaos nor specific graph topologies are necessary for Born-like polar response.

## Implementation
The microscopic formula for this class allows testing for $C_B$ without a full many-body eigensolve:
$$ \theta_s = |\text{wrap}(\sum_i s_i \phi_i)| $$
where $\phi_i = 2 t g_i$.

See also: [[born-like-points]], [[spectral-statistics]].
