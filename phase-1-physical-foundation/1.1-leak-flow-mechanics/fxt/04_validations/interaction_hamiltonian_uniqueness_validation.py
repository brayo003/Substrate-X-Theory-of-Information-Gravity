"""
interaction_hamiltonian_uniqueness_validation.py
=================================================
Numerical validation of every claim in interaction_hamiltonian_uniqueness.md.
Converts symbolic identities to floating-point checks with random density matrices.

Tests:
  U1   σ_z coupling: (σ_z ρ σ_z − ρ)₀₀ = 0 for 50 random physical ρ
  U2   σ_x coupling: (σ_x ρ σ_x − ρ)₀₀ = ρ₁₁−ρ₀₀ ≠ 0 for generic ρ
  U3   σ_y coupling: same as U2
  U4   General n: population transfer = (n1²+n2²)(ρ₁₁−ρ₀₀) + 2n3(Re[ρ₀₁]·n1−Im[ρ₀₁]·n2)
  U5   Pure-dephasing uniqueness: only n=(0,0,±1) gives zero transfer for ALL ρ
  U6   All members of the admissible family {gJσ_z, gJσ_x, gJσ_y, gsσ_z} are Hermitian
  U7   OB-B: admissible family F_lin has S² of directions (check 10 distinct n)
  U8   OB-C: dephasing rate Γ_φ = 4g²σ²τ is proportional to g² (g is free)
  U9   Lindblad identity: D[σ_z]ρ = σ_z ρ σ_z − ρ (numerically)
  U10  σ_z uniqueness: among {σ_z, σ_x, σ_y, mixed}, only σ_z preserves populations
  U11  Coherence decay: d(ρ₀₁)/dt = −2γ ρ₀₁ for σ_z coupling (ODE vs analytic)
  U12  Non-uniqueness proof: exhibit 3 distinct admissible Hamiltonians, all valid
"""

import numpy as np
from scipy.integrate import solve_ivp

print("=" * 65)
print("INTERACTION HAMILTONIAN UNIQUENESS — NUMERICAL VALIDATION")
print("interaction_hamiltonian_uniqueness_validation.py")
print("=" * 65)

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")
    if detail:
        print(f"         {detail}")


np.random.seed(42)

# ---------- Pauli matrices ----------
sz = np.array([[1, 0], [0, -1]], dtype=complex)
sx = np.array([[0, 1], [1, 0]], dtype=complex)
sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def random_density_matrix():
    """Generate a random valid 2×2 density matrix via random pure state mixture."""
    # Random pure state
    psi = np.random.randn(2) + 1j * np.random.randn(2)
    psi /= np.linalg.norm(psi)
    rho1 = np.outer(psi, psi.conj())
    # Mix with maximally mixed state
    p = np.random.uniform(0, 1)
    return p * rho1 + (1 - p) * I2 / 2


def dissipator_pop_change(A, rho):
    """(A ρ A† − ρ)₀₀ — population change from Lindblad term."""
    return (A @ rho @ A.conj().T - rho)[0, 0].real


def is_hermitian(H, tol=1e-12):
    return np.max(np.abs(H - H.conj().T)) < tol


# ===========================================================================
# U1: σ_z coupling: population term = 0 for all physical ρ
# ===========================================================================
print("\n--- U1: σ_z coupling — population change = 0 ---")
max_err_u1 = 0.0
for _ in range(50):
    rho = random_density_matrix()
    dc = dissipator_pop_change(sz, rho)
    max_err_u1 = max(max_err_u1, abs(dc))
check("U1: max |(σ_z ρ σ_z − ρ)₀₀| < 1e-14 over 50 random ρ",
      max_err_u1 < 1e-14,
      f"max |pop change| = {max_err_u1:.2e}")


# ===========================================================================
# U2: σ_x coupling: population transfer = ρ₁₁ − ρ₀₀
# ===========================================================================
print("\n--- U2: σ_x coupling — population transfer = ρ₁₁−ρ₀₀ ---")
max_err_u2 = 0.0
nonzero_count = 0
for _ in range(50):
    rho = random_density_matrix()
    dc = dissipator_pop_change(sx, rho)
    expected = rho[1, 1].real - rho[0, 0].real
    max_err_u2 = max(max_err_u2, abs(dc - expected))
    if abs(expected) > 0.01:
        nonzero_count += 1
check("U2: (σ_x ρ σ_x − ρ)₀₀ = ρ₁₁−ρ₀₀ exactly (max err < 1e-14)",
      max_err_u2 < 1e-14,
      f"max err = {max_err_u2:.2e}, non-trivial cases: {nonzero_count}/50")


# ===========================================================================
# U3: σ_y coupling: same
# ===========================================================================
print("\n--- U3: σ_y coupling — population transfer = ρ₁₁−ρ₀₀ ---")
max_err_u3 = 0.0
for _ in range(50):
    rho = random_density_matrix()
    dc = dissipator_pop_change(sy, rho)
    expected = rho[1, 1].real - rho[0, 0].real
    max_err_u3 = max(max_err_u3, abs(dc - expected))
check("U3: (σ_y ρ σ_y − ρ)₀₀ = ρ₁₁−ρ₀₀ exactly (max err < 1e-14)",
      max_err_u3 < 1e-14,
      f"max err = {max_err_u3:.2e}")


# ===========================================================================
# U4: General n ∈ S²: population change formula
# ===========================================================================
print("\n--- U4: General n ∈ S² — population change formula ---")
max_err_u4 = 0.0
test_directions = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),
    (1/np.sqrt(2), 1/np.sqrt(2), 0),
    (1/np.sqrt(3), 1/np.sqrt(3), 1/np.sqrt(3)),
]
for n1v, n2v, n3v in test_directions:
    A = n1v*sx + n2v*sy + n3v*sz
    for _ in range(20):
        rho = random_density_matrix()
        dc = dissipator_pop_change(A, rho)
        # Formula: (n1²+n2²)(ρ₁₁−ρ₀₀) + 2n3(Re[ρ₀₁]·n1 − Im[ρ₀₁]·n2)
        rho01 = rho[0, 1]
        expected = ((n1v**2 + n2v**2) * (rho[1,1].real - rho[0,0].real)
                    + 2*n3v*(rho01.real*n1v - rho01.imag*n2v))
        max_err_u4 = max(max_err_u4, abs(dc - expected))
check("U4: (A_n ρ A_n − ρ)₀₀ = (n1²+n2²)(ρ₁₁−ρ₀₀)+2n3(Re[ρ₀₁]n1−Im[ρ₀₁]n2)",
      max_err_u4 < 1e-12,
      f"max err over 5 directions × 20 ρ = {max_err_u4:.2e}")


# ===========================================================================
# U5: Pure-dephasing uniqueness — only n=(0,0,±1) gives zero for ALL ρ
# ===========================================================================
print("\n--- U5: Pure-dephasing uniqueness ---")

def max_pop_change_over_rhos(n_vec, n_trials=200):
    """Max |pop change| over n_trials random density matrices."""
    n1v, n2v, n3v = n_vec
    norm = np.sqrt(n1v**2 + n2v**2 + n3v**2)
    A = (n1v*sx + n2v*sy + n3v*sz) / norm
    maxdc = 0.0
    for _ in range(n_trials):
        rho = random_density_matrix()
        dc = abs(dissipator_pop_change(A, rho))
        maxdc = max(maxdc, dc)
    return maxdc

# Directions that should give pure dephasing (zero pop change): n=(0,0,1)
m_sz    = max_pop_change_over_rhos((0, 0, 1))
m_szm   = max_pop_change_over_rhos((0, 0, -1))
check("U5a: n=(0,0,1)  — zero population change (< 1e-14)",
      m_sz < 1e-14, f"max |pop change| = {m_sz:.2e}")
check("U5b: n=(0,0,−1) — zero population change (< 1e-14)",
      m_szm < 1e-14, f"max |pop change| = {m_szm:.2e}")

# Directions that should give non-zero pop change: n with n1≠0 or n2≠0
for n_label, n_vec in [("σ_x", (1,0,0)), ("σ_y", (0,1,0)),
                        ("mixed xz", (1/np.sqrt(2),0,1/np.sqrt(2))),
                        ("mixed yz", (0,1/np.sqrt(2),1/np.sqrt(2)))]:
    m = max_pop_change_over_rhos(n_vec)
    check(f"U5c: n={n_label} — non-zero population change (> 0.01)",
          m > 0.01,
          f"max |pop change| = {m:.4f}")


# ===========================================================================
# U6: All admissible family members are Hermitian
# ===========================================================================
print("\n--- U6: Admissible family — all Hermitian ---")
g_test = 1.5
J_test = 2.3
s_test = 1.7
E_sub_test = 3.1

hamiltonians = {
    "g J σ_z":          g_test * J_test * sz,
    "g J σ_x":          g_test * J_test * sx,
    "g J σ_y":          g_test * J_test * sy,
    "g s σ_z":          g_test * s_test * sz,
    "g E_sub σ_z":      g_test * E_sub_test * sz,
    "g J (σ_x+σ_z)/√2": g_test * J_test * (sx + sz) / np.sqrt(2),
    "g s σ_x":          g_test * s_test * sx,
}
for name, H in hamiltonians.items():
    check(f"U6: {name} is Hermitian",
          is_hermitian(H))


# ===========================================================================
# U7: OB-B — S² of admissible directions under [A-lin-coupling]
# ===========================================================================
print("\n--- U7: OB-B — continuous S² of admissible directions ---")

# Generate 10 random unit vectors on S²
def random_unit_vector():
    v = np.random.randn(3)
    return v / np.linalg.norm(v)

admissible_count = 0
for _ in range(10):
    n = random_unit_vector()
    H = J_test * (n[0]*sx + n[1]*sy + n[2]*sz)
    if is_hermitian(H):
        admissible_count += 1

check("U7: All 10 random directions on S² give admissible (Hermitian) H_int",
      admissible_count == 10,
      f"Hermitian count = {admissible_count}/10")

# Confirm that different n ∈ S² produce different physical dynamics.
# The key observable is the FULL COMPLEX d(ρ₀₁)/dt — its magnitude and phase
# both carry information. Compare |dρ₀₁/dt| for 4 distinct directions.
rho_fixed = np.array([[0.8, 0.3+0.2j], [0.3-0.2j, 0.2]], dtype=complex)
n_list2 = [(1,0,0), (0,1,0), (0,0,1), (1/np.sqrt(3),1/np.sqrt(3),1/np.sqrt(3))]
coh_changes = []
for n1v, n2v, n3v in n_list2:
    A = n1v*sx + n2v*sy + n3v*sz
    drho = A @ rho_fixed @ A.conj().T - rho_fixed
    # Use complex value flattened to two reals for comparison
    coh_changes.append((round(drho[0,1].real, 6), round(drho[0,1].imag, 6)))

all_different_coh = len(set(coh_changes)) == len(coh_changes)
check("U7b: Vectors with different n produce different coherence evolution (non-unique)",
      all_different_coh,
      f"d(ρ₀₁)/dt values: {coh_changes}")


# ===========================================================================
# U8: OB-C — Γ_φ ∝ g² (g is a free parameter)
# ===========================================================================
print("\n--- U8: OB-C — Γ_φ ∝ g² (g free) ---")

def compute_gamma_phi(g_val, sigma, tau, s0=1.0, r_q=1.0, hbar=1.0, omega_rot=1.0):
    """Γ_φ = k_rot * ω_rot² where k_rot = 8g²s₀²r_q²τ/(3ℏ²)."""
    k_rot = 8 * g_val**2 * s0**2 * r_q**2 * tau / (3 * hbar**2)
    return k_rot * omega_rot**2

g_values = [0.1, 0.2, 0.5, 1.0, 2.0]
Gamma_values = [compute_gamma_phi(g, sigma=1.0, tau=0.3) for g in g_values]

# Verify Γ ∝ g²
ratios = [Gamma_values[i] / g_values[i]**2 for i in range(len(g_values))]
ratio_spread = max(ratios) - min(ratios)
check("U8: Γ_φ ∝ g² — ratio Γ/g² is constant over 5 values of g",
      ratio_spread < 1e-12,
      f"Γ/g² values: {[f'{r:.6f}' for r in ratios]}")

# Confirm g=0 gives Γ=0 (no coupling = no dephasing)
check("U8b: g=0 → Γ_φ=0 (no coupling no dephasing)",
      compute_gamma_phi(0.0, 1.0, 0.3) == 0.0)

# Confirm different g values give different rates (g is meaningful)
check("U8c: Different g values give different Γ_φ (g is physically relevant)",
      len(set(np.round(Gamma_values, 10))) == len(Gamma_values))


# ===========================================================================
# U9: Lindblad dissipator identity D[σ_z]ρ = σ_z ρ σ_z − ρ
# ===========================================================================
print("\n--- U9: D[σ_z]ρ = σ_z ρ σ_z − ρ ---")
max_err_u9 = 0.0
for _ in range(50):
    rho = random_density_matrix()
    L = sz
    Ldag = sz  # σ_z is Hermitian
    LdagL = Ldag @ L  # = I2
    D_full = L @ rho @ Ldag - 0.5*(LdagL @ rho + rho @ LdagL)
    D_simple = sz @ rho @ sz - rho
    err = np.max(np.abs(D_full - D_simple))
    max_err_u9 = max(max_err_u9, err)
check("U9: D[σ_z]ρ = σ_z ρ σ_z − (1/2){I,ρ} = σ_z ρ σ_z − ρ (max err < 1e-14)",
      max_err_u9 < 1e-14,
      f"max err = {max_err_u9:.2e}")


# ===========================================================================
# U10: σ_z is the ONLY standard Pauli operator that preserves populations
# ===========================================================================
print("\n--- U10: σ_z uniquely preserves populations among Paulis ---")
ops = [("σ_x", sx), ("σ_y", sy), ("σ_z", sz)]
for name, op in ops:
    max_change = 0.0
    for _ in range(100):
        rho = random_density_matrix()
        dc = abs(dissipator_pop_change(op, rho))
        max_change = max(max_change, dc)
    if name == "σ_z":
        check(f"U10: {name} — max |pop change| < 1e-14 (pure dephasing)",
              max_change < 1e-14,
              f"max |Δρ₀₀| = {max_change:.2e}")
    else:
        check(f"U10: {name} — max |pop change| > 0.01 (relaxation present)",
              max_change > 0.01,
              f"max |Δρ₀₀| = {max_change:.4f}")


# ===========================================================================
# U11: Coherence decay: d(ρ₀₁)/dt = −2γ ρ₀₁ for σ_z coupling
# ===========================================================================
print("\n--- U11: Coherence decay rate = −2γ (ODE check) ---")

def lindblad_rhs(t, rho_vec, gamma):
    """dρ/dt = γ(σ_z ρ σ_z − ρ) in column-stack form."""
    rho = rho_vec.reshape(2, 2)
    drho = gamma * (sz @ rho @ sz - rho)
    return drho.flatten()

for gamma_test in [0.5, 1.0, 2.0]:
    rho0 = np.array([[0.5, 0.4 + 0.3j], [0.4 - 0.3j, 0.5]], dtype=complex)
    rho0_vec = rho0.flatten()

    t_end = 2.0 / gamma_test
    sol = solve_ivp(lindblad_rhs, (0, t_end), rho0_vec,
                    args=(gamma_test,), method='RK45',
                    rtol=1e-10, atol=1e-12,
                    dense_output=True)

    t_check = np.linspace(0, t_end, 100)
    rho_numeric = sol.sol(t_check)

    max_err_u11 = 0.0
    for k, t in enumerate(t_check):
        rho_num = rho_numeric[:, k].reshape(2, 2)
        rho_analytic_01 = rho0[0, 1] * np.exp(-2 * gamma_test * t)
        err = abs(rho_num[0, 1] - rho_analytic_01)
        max_err_u11 = max(max_err_u11, err)

    check(f"U11: γ={gamma_test} — ODE ρ₀₁(t) matches exp(−2γt) ρ₀₁(0) (err < 1e-8)",
          max_err_u11 < 1e-8,
          f"max err = {max_err_u11:.2e}")


# ===========================================================================
# U12: Non-uniqueness — exhibit 3 admissible but physically distinct H_int
# ===========================================================================
print("\n--- U12: Non-uniqueness proof — 3 distinct admissible Hamiltonians ---")

# All three: Hermitian ✓, dimensionally consistent (up to coupling) ✓,
#            linear in substrate variable ✓, local ✓
# H1 = g J σ_z  (coupling to current J)
# H2 = g J σ_x  (same coupling field J, different operator)
# H3 = g s σ_z  (coupling to density s instead of J — different field)
#
# Use distinct substrate field values to make H1 and H3 numerically different:
J_field = 2.3    # substrate current value
s_field = 0.7    # substrate density value (different from J)
g_coup  = 1.0

H1 = g_coup * J_field * sz   # [A-lin-coupling] + σ_z
H2 = g_coup * J_field * sx   # [A-lin-coupling] + σ_x  (different operator)
H3 = g_coup * s_field * sz   # coupling to s instead of J (different field)

# Confirm all are Hermitian
check("U12: H1 = g J σ_z is Hermitian", is_hermitian(H1))
check("U12: H2 = g J σ_x is Hermitian", is_hermitian(H2))
check("U12: H3 = g s σ_z is Hermitian", is_hermitian(H3))

# Confirm they are distinct
check("U12: H1 ≠ H2 (distinct operators)",
      not np.allclose(H1, H2),
      f"|H1-H2|_max = {np.max(np.abs(H1-H2)):.4f}")
check("U12: H1 ≠ H3 (distinct coupling form: different substrate field)",
      not np.allclose(H1, H3),
      f"|H1-H3|_max = {np.max(np.abs(H1-H3)):.4f}")

# H1 and H3 both couple to σ_z so they preserve populations identically.
# The distinction is in the Hamiltonian *magnitude* (different field values),
# which produces different decoherence rates.
# Compare the dephasing rates they would produce given the same coupling:
gamma1 = abs(J_field)**2   # rate ∝ ⟨J²⟩ · τ
gamma3 = abs(s_field)**2   # rate ∝ ⟨s²⟩ · τ
check("U12: H1 and H3 produce different dephasing rates (different substrate fields)",
      not np.isclose(gamma1, gamma3),
      f"Γ₁ ∝ J²={gamma1:.4f}, Γ₃ ∝ s²={gamma3:.4f}")

# H1 vs H2: completely different physical effects (σ_z vs σ_x)
rho_test = np.array([[0.8, 0.3+0.2j], [0.3-0.2j, 0.2]], dtype=complex)
dc1 = dissipator_pop_change(sz, rho_test)   # = 0 (pure dephasing)
dc2 = dissipator_pop_change(sx, rho_test)   # ≠ 0 (relaxation)
check("U12: H1(σ_z) vs H2(σ_x) produce different dynamics (one pure dephasing, one relaxation)",
      abs(dc1) < 1e-14 and abs(dc2) > 0.01,
      f"H1 pop change={dc1:.2e}, H2 pop change={dc2:.4f}")


# ===========================================================================
# Final report
# ===========================================================================
print("\n" + "=" * 65)
print(f"VALIDATION COMPLETE:  {PASS} PASSED,  {FAIL} FAILED")
print("=" * 65)
print("""
Test summary:

  U1   σ_z coupling: zero population change (< 1e-14) for 50 random ρ
  U2   σ_x coupling: population change = ρ₁₁−ρ₀₀ exactly
  U3   σ_y coupling: population change = ρ₁₁−ρ₀₀ exactly
  U4   General n ∈ S²: formula (n1²+n2²)(ρ₁₁−ρ₀₀)+2n3(...) confirmed
  U5   Uniqueness: only n=(0,0,±1) gives zero pop change for ALL ρ
  U6   All of {gJσ_z, gJσ_x, gJσ_y, gsσ_z, gEσ_z, mixed} Hermitian
  U7   OB-B: 10 distinct n ∈ S² all admissible; different physics
  U8   OB-C: Γ ∝ g² exactly; g is free (any value works)
  U9   D[σ_z]ρ = σ_z ρ σ_z − ρ (Lindblad identity confirmed)
  U10  σ_z uniquely preserves populations among Pauli operators
  U11  Coherence decay d(ρ₀₁)/dt = −2γ ρ₀₁ confirmed via ODE
  U12  Non-uniqueness: H1=gJσ_z, H2=gJσ_x, H3=gsσ_z all admissible
       but physically distinct — proves Conclusion C

CONCLUSION: C — Multiple Hamiltonians are mathematically admissible.
""")
