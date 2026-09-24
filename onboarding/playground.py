"""Disentangling spectrum of a qubit + detector unitary -- self-contained playground.

Requires only numpy, scipy, matplotlib.  No repository code.  Run `python playground.py --help`.

THE OBJECT.  U acts on qubit (x) detector, dimension 2*d.  Write U in the qubit basis as four d x d blocks
    U = [[U00, U01], [U10, U11]]        (U_ba: qubit a in, qubit b out)
A product input (|0> + lam|1>) (x) |D> collapses EXACTLY to qubit |0> iff (U10 + lam U11)|D> = 0,
and to |1> iff (U00 + lam U01)|D> = 0.  Each is a d x d matrix pencil with d roots lam_j (a "disentangling
spectrum").  lam -> Bloch vector of the input qubit ray -> two point clouds on the sphere (outcome 0 and 1).
THEOREM (prove it): the two clouds are exact antipodes for every unitary U.
The outcome ratio R(theta) = rho0/(rho0+rho1) at polar angle theta from the outcome-0 pole is "Born" iff
R = cos^2(theta/2).

MODELS.  (1) ring: H = -|h0| n.sigma_0 - hz sum Z_i - J sum Z_i Z_{i+1} - (g/sqrt N) X_0 sum X_i, n = (sin th, 0, cos th).
         Matched field hz = |h0| makes a qubit flip resonant with a domain-wall pixel flip.
         (2) ladder: H_Q = -h0 Z, detector = M random bands at energies 2 h0 m of width w, coupling g X (x) GUE.
         (3) haar: U Haar-random.   (4) qnd: [U, Z_0] = 0.
The "dephased" unitary replaces exp(-iE_k t) by one random phase per distinct level: it is what a single very
long time samples, with far less noise (check this yourself with --time).
"""
from __future__ import annotations
import argparse, sys
import numpy as np
from scipy.linalg import eigh, eig
from scipy.stats import unitary_group

# ----------------------------------------------------------------------------- operators
def paulis(n):
    """Return lists X[i], Z[i] of 2^n x 2^n Pauli matrices on site i (site 0 = qubit)."""
    sx = np.array([[0, 1], [1, 0]], float); sz = np.array([[1, 0], [0, -1]], float); I2 = np.eye(2)
    def op(P, i):
        m = np.array([[1.0]])
        for j in range(n): m = np.kron(m, P if j == i else I2)
        return m
    return [op(sx, i) for i in range(n)], [op(sz, i) for i in range(n)]

def ring_hamiltonian(N, J=1.0, hz=1.0, h0=1.0, theta_deg=0.0, g=0.1):
    X, Z = paulis(N + 1); th = np.radians(theta_deg)
    H = -h0 * (np.cos(th) * Z[0] + np.sin(th) * X[0]) - hz * sum(Z[1:])
    H -= J * sum(Z[i] @ Z[i % N + 1] for i in range(1, N + 1))
    H -= (g / np.sqrt(N)) * sum(X[0] @ X[i] for i in range(1, N + 1))
    return H

def ladder_hamiltonian(d, M=8, w=0.0, g=0.3, h0=1.0, rng=None):
    rng = rng or np.random.default_rng(0); per = d // M
    E_D = np.concatenate([2 * h0 * m + w * (rng.uniform(size=per) - 0.5) for m in range(M)])
    B = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d)); B = (B + B.conj().T) / np.sqrt(16 * d)
    return np.kron(-h0 * np.diag([1, -1]), np.eye(d)) + np.kron(np.eye(2), np.diag(E_D)) + g * np.kron([[0, 1], [1, 0]], B)

# ----------------------------------------------------------------------------- unitaries
def dephased_unitary(H, rng, tol=1e-8):
    E, V = eigh(H)
    lvl = np.concatenate([[0], np.cumsum(np.diff(E) > tol)])          # one phase per distinct level
    ph = rng.uniform(0, 2 * np.pi, lvl.max() + 1)[lvl]
    return (V * np.exp(1j * ph)) @ V.conj().T

def time_unitary(H, t):
    E, V = eigh(H); return (V * np.exp(-1j * E * t)) @ V.conj().T

def rotate_qubit(U, theta_deg, d):
    """Change the qubit basis to the eigenbasis of n.sigma, n = (sin th, 0, cos th)."""
    th = np.radians(theta_deg); c, s = np.cos(th / 2), np.sin(th / 2)
    R = np.kron(np.array([[c, -s], [s, c]]), np.eye(d)); return R.T @ U @ R

# ----------------------------------------------------------------------------- the spectrum
def bloch(lam):
    lam = np.asarray(lam); fin = np.isfinite(lam); l = np.where(fin, lam, 0)
    n = 1 + np.abs(l) ** 2
    return np.stack([np.where(fin, 2 * l.real / n, 0), np.where(fin, 2 * l.imag / n, 0), np.where(fin, (1 - np.abs(l) ** 2) / n, -1)], 1)

def disentangling_spectrum(U, d):
    """Outcome-0 and outcome-1 clouds (Bloch vectors of the collapsible input qubit rays)."""
    U00, U01, U10, U11 = U[:d, :d], U[:d, d:], U[d:, :d], U[d:, d:]
    lam0 = eig(U10, -U11, right=False)          # (U10 + lam U11) D = 0
    lam1 = eig(U00, -U01, right=False)          # (U00 + lam U01) D = 0
    r0, r1 = bloch(lam0), bloch(lam1)
    antipodal_error = np.max(np.abs(np.sort(r1[:, 2]) - np.sort(-r0[:, 2])))
    return r0, r1, antipodal_error

def outcome_ratio(r0, r1, n_bins=24):
    """Fit the axis (dipole of cloud0 - cloud1), bin polar angles about it, return R, Born, MAE, steepness k."""
    dip = r0.mean(0) - r1.mean(0); n = dip / max(np.linalg.norm(dip), 1e-12)
    th0, th1 = np.arccos(np.clip(r0 @ n, -1, 1)), np.arccos(np.clip(r1 @ n, -1, 1))
    edges = np.linspace(0, np.pi, n_bins + 1); mid = (edges[1:] + edges[:-1]) / 2
    h0, _ = np.histogram(th0, edges); h1, _ = np.histogram(th1, edges); tot = h0 + h1
    R = np.full(n_bins, np.nan); ok = tot > 0; R[ok] = h0[ok] / tot[ok]; born = np.cos(mid / 2) ** 2
    ks = np.linspace(0.5, 4, 351)
    model = lambda k: np.cos(mid / 2) ** (2 * k) / (np.cos(mid / 2) ** (2 * k) + np.sin(mid / 2) ** (2 * k))
    k = ks[np.argmin([np.nanmean((R - model(k)) ** 2) for k in ks])]
    return dict(mid=mid, R=R, born=born, mae=float(np.nanmean(np.abs(R - born))), k=float(k), axis=n,
                coverage=int(ok.sum()), pole_fraction=float(np.mean(np.abs(r0 @ n) > 0.95)))

# ----------------------------------------------------------------------------- experiments
def cloud(kind, N=8, K=8, seed=0, **kw):
    """Pooled dephased clouds for one model.  kind in {ring, ladder, haar, qnd}."""
    rng = np.random.default_rng(seed); d = 2 ** N; R0 = []; R1 = []
    if kind == "ring":   H = ring_hamiltonian(N, **kw)
    elif kind == "qnd":  H = ring_hamiltonian(N, **{**kw, "theta_deg": 90.0})   # h0 || coupling axis: [H, X0] = 0
    elif kind == "ladder": H = ladder_hamiltonian(d, rng=rng, **kw)
    th = kw.get("theta_deg", 0.0) if kind == "ring" else (90.0 if kind == "qnd" else 0.0)
    for _ in range(K):
        U = unitary_group.rvs(2 * d, random_state=rng) if kind == "haar" else dephased_unitary(H, rng)
        if kind in ("ring", "qnd"): U = rotate_qubit(U, th, d)   # read out in the self-field eigenbasis
        r0, r1, err = disentangling_spectrum(U, d); R0.append(r0); R1.append(r1)
    return np.vstack(R0), np.vstack(R1)

def summarize(name, r0, r1):
    s = outcome_ratio(r0, r1)
    print(f"{name:34s} roots {len(r0):5d}  MAE vs Born {s['mae']:.3f}  steepness k {s['k']:.2f} (Born=1)  "
          f"pole frac {s['pole_fraction']:.2f}  coverage {s['coverage']}/24  axis {np.round(s['axis'], 2)}")
    return s

def figure(panels, path):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    C0, C1, BORN = "#0072B2", "#D55E00", "#6E6E6E"                    # Okabe-Ito blue / vermillion (CVD-safe), gray
    fig, ax = plt.subplots(2, len(panels), figsize=(3.4 * len(panels), 6.2))
    for j, (title, r0, r1) in enumerate(panels):
        s = outcome_ratio(r0, r1); n = s["axis"]
        # 2-D view: component along the fitted axis vs one transverse component
        e1 = np.cross(n, [0, 1, 0]); e1 = e1 / max(np.linalg.norm(e1), 1e-9) if np.linalg.norm(e1) > 1e-6 else np.array([1., 0, 0])
        for r, c, lab in ((r0, C0, "outcome 0"), (r1, C1, "outcome 1")):
            ax[0, j].scatter(r @ e1, r @ n, s=4, c=c, alpha=0.35, lw=0, label=lab)
        ax[0, j].add_patch(plt.Circle((0, 0), 1, fill=False, color=BORN, lw=0.8)); ax[0, j].set_aspect("equal")
        ax[0, j].set_xlim(-1.1, 1.1); ax[0, j].set_ylim(-1.1, 1.1); ax[0, j].set_title(title, fontsize=11)
        ax[0, j].set_xticks([]); ax[0, j].set_yticks([]); [sp.set_visible(False) for sp in ax[0, j].spines.values()]
        ax[1, j].plot(s["mid"], s["born"], "--", color=BORN, lw=1.5, label="Born  cos²(θ/2)")
        ax[1, j].plot(s["mid"], s["R"], "o-", color=C0, lw=1.5, ms=4, label="R(θ) measured")
        ax[1, j].set_ylim(-0.03, 1.03); ax[1, j].set_xticks([0, np.pi / 2, np.pi]); ax[1, j].set_xticklabels(["0", "π/2", "π"])
        ax[1, j].set_xlabel("θ from outcome-0 pole (fitted axis)"); ax[1, j].grid(alpha=0.25)
        ax[1, j].text(0.03, 0.06, f"MAE {s['mae']:.3f}\nk = {s['k']:.2f}", transform=ax[1, j].transAxes, fontsize=9)
        for sp in ("top", "right"): ax[1, j].spines[sp].set_visible(False)
    ax[0, 0].legend(loc="lower left", fontsize=8, frameon=False, markerscale=3); ax[1, 0].set_ylabel("outcome ratio R(θ)")
    ax[1, 0].legend(loc="upper right", fontsize=8, frameon=False)
    fig.suptitle("Disentangling spectrum of a qubit + detector unitary: where the collapsible inputs sit, and how they split", fontsize=11)
    fig.tight_layout(); fig.savefig(path, dpi=160); print("wrote", path)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("experiment", choices=["anchors", "rotate", "detune", "gscan", "ladder", "time"])
    p.add_argument("--N", type=int, default=8); p.add_argument("--K", type=int, default=8); p.add_argument("--seed", type=int, default=0)
    p.add_argument("--fig", default=None, help="write a figure to this path (anchors, rotate)")
    a = p.parse_args(); N, K, seed = a.N, a.K, a.seed
    if a.experiment == "anchors":
        P = [("QND:  h0 ∥ coupling  ([U, X0] = 0)", *cloud("qnd", N, K, seed)),
             ("Haar-random unitary", *cloud("haar", N, K, seed)),
             ("matched ring  (hz = |h0|, g = 0.1)", *cloud("ring", N, K, seed, g=0.1)),
             ("same ring, self-field rotated 45°", *cloud("ring", N, K, seed, g=0.1, theta_deg=45.0))]
        for t, r0, r1 in P: summarize(t, r0, r1)
        if a.fig: figure(P, a.fig)
    elif a.experiment == "rotate":
        for th in (0, 20, 45, 70, 85, 89, 90):
            r0, r1 = cloud("ring", N, K, seed, theta_deg=th); s = summarize(f"theta = {th:>4} deg", r0, r1)
            print(f"      fitted axis is {np.degrees(np.arccos(np.clip(abs(s['axis'][2]), 0, 1))):.1f} deg from the self-field direction")
    elif a.experiment == "detune":
        for h0 in (0.5, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 2.0, 3.0):
            summarize(f"|h0| = {h0:<4}  (hz = 1, gap 2|h0|)", *cloud("ring", N, K, seed, h0=h0))
    elif a.experiment == "gscan":
        for g in (0.03, 0.1, 0.3, 0.5, 0.7, 1.0, 2.0):
            summarize(f"g = {g:<4}", *cloud("ring", N, K, seed, g=g))
    elif a.experiment == "ladder":
        for M, w, g in ((8, 0.0, 0.1), (8, 0.0, 0.6), (8, 0.0, 2.0), (8, 1.0, 0.1), (2, 0.0, 0.6), (16, 0.0, 0.6)):
            summarize(f"ladder M={M:<2} width w={w:<3} g={g:<3}", *cloud("ladder", N, K, seed, M=M, w=w, g=g))
    elif a.experiment == "time":
        H = ring_hamiltonian(N); d = 2 ** N; rng = np.random.default_rng(seed)
        for t in (3, 30, 300, 3e3, 3e4, 1e6):
            r0, r1, _ = disentangling_spectrum(time_unitary(H, t), d); summarize(f"single time t = {t:<8g}", r0, r1)
        r0, r1 = cloud("ring", N, 1, seed); summarize("one dephased draw", r0, r1)
