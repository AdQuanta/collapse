# Figure Card 1: Projective Pencil Roots Define Antipodally Paired Definite-Outcome States

## 1. Figure Card Specification

1. **Claim-like Title**:
   *Projective Matrix-Pencil Roots Define an Antipodally Paired Set of Definite-Outcome Product States on the Bloch Sphere.*

2. **One-Sentence Takeaway**:
   Under unitary evolution of a qubit-detector system, the exact initial product states yielding definite measurement outcomes are the projective roots of a detector-space matrix pencil, whose outcome multisets are forced by unitarity to form exact Bloch antipodes.

3. **Question Answered**:
   How can a globally linear, unitary many-body evolution produce definite, non-superposed measurement outcomes from pure initial states without invoking non-unitary state reduction?

4. **Panel Flow**:
   - **(a) Physical Architecture**: Qubit $|\phi_0\rangle = \alpha|0\rangle + \beta|1\rangle$ coupled to a $d$-dimensional detector $\mathcal{H}_D$ via unitary propagator $U(t) = \exp(-\ii H t)$.
   - **(b) Algebraic Engine**: $2\times 2$ block partition of $U(t) \to$ forward pole pencils $(\alpha C + \beta D)\eta = 0$ (pole $0$) and $(\alpha A + \beta B)\eta = 0$ (pole $1$).
   - **(c) Geometric Projection**: Complex affine pencil roots $z = \beta/\alpha \in \mathbb{CP}^1$ mapped to Bloch sphere coordinates $\theta = 2\arctan|z|$, $\phi = \arg z$.
   - **(d) Antipodal Minor Duality**: Visual mapping of the outcome multisets $\Omega_j^{(0)}$ and $\Omega_j^{(1)}$ on $S^2$, showing $\Omega_j^{(1)} = -\Omega_j^{(0)}$.

5. **Dominant Panel**:
   Panel (d), visually demonstrating that the two outcome multisets are not independent random clouds but exact geometric antipodes.

6. **Instant Comparison**:
   The contrast between an arbitrary set of unconstrained states versus the structured, antipodally locked pairs forced by unitarity via Jacobi's complementary-minor theorem.

7. **Quantitative Anchor**:
   Exactly $d = 2^N$ projective roots counted with algebraic multiplicity in $\mathbb{CP}^1$ for regular pencils of detector dimension $d$.

8. **Alternative Explanation Addressed**:
   Rules out the objection that definite outcomes under unitary dynamics can only be approximate (e.g., asymptotic off-diagonal decay in decoherence). This construction is an exact algebraic identity for perfect disentanglement.

9. **Why Main Text vs. SI**:
   Defines the central mathematical object of the Letter; without establishing the pencil root construction and antipodal duality, the subsequent numerical distributions cannot be physically interpreted.

---

## 2. Publication-Ready Draft Caption

> **FIG. 1. Projective pencil construction and exact antipodal outcome geometry.** (a) System schematic: a readout qubit coupled to a $d$-dimensional many-body detector evolving under global unitary propagator $U(t)$. (b) Partitioning $U(t)$ into $d\times d$ blocks yields the homogeneous forward pole pencils $(\alpha C + \beta D)\eta = 0$ for outcome $0$ and $(\alpha A + \beta B)\eta = 0$ for outcome $1$. (c) Projective roots $z = \beta/\alpha \in \mathbb{CP}^1$ define discrete coordinates on the Bloch sphere $S^2$ via $\theta = 2\arctan |z|$ and $\phi = \arg z$. (d) By Jacobi's complementary-minor theorem, unitarity forces the outcome-$1$ roots to be exact Bloch antipodes of the outcome-$0$ roots ($\Omega_j^{(1)} = -\Omega_j^{(0)}$), guaranteeing an odd antipodal asymmetry $a(-\Omega) = -a(\Omega)$ for any regular detector.
