"""Verify dimerized Hamiltonian symmetry exploitation."""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Suppress QuSpin stdout noise
os.environ["QSPIN_DEBUG"] = "0"
import contextlib, io

import time
import numpy as np

# Import with suppressed QuSpin chatter
with contextlib.redirect_stdout(io.StringIO()):
    from collapse.hamiltonians.quspin_hamiltonians import DimerizedPixelHamiltonianQuSpin


def test_eigenvalue_consistency(N_pixel, Jx, hx, hz):
    """Compare symmetry-exploiting diagonalize vs full (no symmetry)."""
    label = f"N_pixel={N_pixel}, Jx={Jx}, hx={hx}, hz={hz}"

    with contextlib.redirect_stdout(io.StringIO()):
        ham_sym = DimerizedPixelHamiltonianQuSpin(
            N_pixel=N_pixel, J=1.0, Jx=Jx, Jz=0.0,
            hx=hx, hz=hz, seed=42, use_symmetry=True,
        )
        ham_nosym = DimerizedPixelHamiltonianQuSpin(
            N_pixel=N_pixel, J=1.0, Jx=Jx, Jz=0.0,
            hx=hx, hz=hz, seed=42, use_symmetry=False,
        )

        info = ham_sym._symmetry_info()
        sym_flags = (
            f"mag={info['can_use_mag']}, "
            f"shift={info['can_use_dimer_shift']} (n_d={info['n_d']}), "
            f"swap={info['can_use_swap']}"
        )

        E_sym, V_sym = ham_sym.diagonalize()
        E_nosym, V_nosym = ham_nosym.diagonalize()
        match_diag = np.allclose(np.sort(E_sym), np.sort(E_nosym))

        sectors_sym = ham_sym.diagonalize_sectors()
        sectors_nosym = ham_nosym.diagonalize_sectors()
        E_s = np.sort(np.concatenate([s["E"] for s in sectors_sym]))
        E_ns = np.sort(np.concatenate([s["E"] for s in sectors_nosym]))
        match_sec = np.allclose(E_s, E_ns)
        n_sec = len(sectors_sym)
        n_sec_nosym = len(sectors_nosym)

    status = "OK" if (match_diag and match_sec) else "FAIL"
    print(
        f"  [{status}] {label}  |  {sym_flags}\n"
        f"         diag match={match_diag}, "
        f"sectors: {n_sec_nosym} -> {n_sec}, match={match_sec}"
    )
    return match_diag and match_sec


def benchmark(N_pixel, Jx):
    """Time diagonalize_sectors with and without symmetry."""
    N = N_pixel + 1
    kw = dict(N_pixel=N_pixel, J=1.0, Jx=Jx, Jz=0.0, hx=0.0, hz=0.1, seed=42)

    with contextlib.redirect_stdout(io.StringIO()):
        ham_sym = DimerizedPixelHamiltonianQuSpin(**kw, use_symmetry=True)
        ham_nosym = DimerizedPixelHamiltonianQuSpin(**kw, use_symmetry=False)
        info = ham_sym._symmetry_info()

        t0 = time.perf_counter()
        sectors_nosym = ham_nosym.diagonalize_sectors()
        dt_nosym = time.perf_counter() - t0

        t0 = time.perf_counter()
        sectors_sym = ham_sym.diagonalize_sectors()
        dt_sym = time.perf_counter() - t0

    speedup = dt_nosym / dt_sym if dt_sym > 0 else float("inf")
    print(
        f"  N={N:2d} (N_pixel={N_pixel:2d})  D={2**N:6d}  |  "
        f"no-sym: {dt_nosym:7.3f}s ({len(sectors_nosym):3d} sec)  |  "
        f"sym: {dt_sym:7.3f}s ({len(sectors_sym):3d} sec)  |  "
        f"speedup: {speedup:5.1f}x"
    )


print("=" * 70)
print("1. EIGENVALUE CONSISTENCY CHECKS")
print("=" * 70)
all_ok = True

# Case: Jx != 0 (no mag, but swap + shift available)
all_ok &= test_eigenvalue_consistency(4, Jx=0.01, hx=0.0, hz=0.1)
all_ok &= test_eigenvalue_consistency(6, Jx=0.01, hx=0.0, hz=0.1)
all_ok &= test_eigenvalue_consistency(8, Jx=0.01, hx=0.0, hz=0.1)

# Case: Jx = 0 (mag + swap + shift)
all_ok &= test_eigenvalue_consistency(4, Jx=0.0, hx=0.0, hz=0.1)
all_ok &= test_eigenvalue_consistency(6, Jx=0.0, hx=0.0, hz=0.1)
all_ok &= test_eigenvalue_consistency(8, Jx=0.0, hx=0.0, hz=0.1)

# Case: hx != 0 (no mag, swap + shift)
all_ok &= test_eigenvalue_consistency(4, Jx=0.0, hx=0.5, hz=0.1)
all_ok &= test_eigenvalue_consistency(6, Jx=0.0, hx=0.5, hz=0.1)

# Case: N_pixel=2 (n_d=1, no shift, but swap)
all_ok &= test_eigenvalue_consistency(2, Jx=0.01, hx=0.0, hz=0.1)
all_ok &= test_eigenvalue_consistency(2, Jx=0.0, hx=0.0, hz=0.1)

print()
print("OVERALL:", "ALL PASSED" if all_ok else "SOME FAILED")

print()
print("=" * 70)
print("2. BENCHMARK: Jx=0.01/sqrt(N_pixel)  (typical Born script)")
print("   [No magnetisation; dimer shift + swap only]")
print("=" * 70)
for np_ in [4, 6, 8, 10, 12]:
    Jx = 0.01 / np.sqrt(np_)
    benchmark(np_, Jx=Jx)

print()
print("=" * 70)
print("3. BENCHMARK: Jx=0  (all three symmetries)")
print("   [Magnetisation + dimer shift + swap]")
print("=" * 70)
for np_ in [4, 6, 8, 10, 12]:
    benchmark(np_, Jx=0.0)
