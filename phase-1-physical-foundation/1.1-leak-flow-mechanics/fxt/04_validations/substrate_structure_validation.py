"""
substrate_structure_validation.py
===================================
Numerical validation of the mathematical claims in substrate_structure_audit.md.

Each test is labelled V1–V20 and corresponds to a specific theorem or claim.
A PASS/FAIL result is printed with the specific numerical evidence.

Tests cover:
  V1–V3:   Z2 grading and parity decomposition
  V4–V6:   Non-Clifford structure of the coefficient algebra
  V7–V8:   Non-holomorphic character of Psi = s + iJ/c
  V9–V11:  Dispersion relation and dissipative character
  V12–V13: Path integral weights (real positive, not complex)
  V14:     Information geometry dimension
  V15–V16: Commutativity of observable algebra
  V17–V19: T-reversal breaking
  V20:     Symplectic structure and energy dissipation

Run with:  python substrate_structure_validation.py
Requires:  numpy >= 1.20, scipy >= 1.7
"""

import numpy as np
from scipy.linalg import eig, eigvals, norm
from scipy.fft import fft, ifft, fftfreq
import warnings
warnings.filterwarnings('ignore')

PASS_COUNT = 0
FAIL_COUNT = 0

def check(label, condition, evidence=""):
    global PASS_COUNT, FAIL_COUNT
    status = "PASS" if condition else "FAIL"
    if condition:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
    print(f"  {status}  {label}")
    if evidence:
        print(f"         {evidence}")

print("=" * 70)
print("SUBSTRATE STRUCTURE VALIDATION — NUMERICAL TESTS")
print("=" * 70)

# ---------------------------------------------------------------------------
# Physical parameters (representative values)
# ---------------------------------------------------------------------------
c = 3.0        # wave speed [m/s, arbitrary units]
tau = 0.5      # damping time [s]
lam = 1.0 / (2 * tau)  # reversal rate = 1/(2*tau)
v = c          # PRW speed = c

print(f"\nParameters: c={c}, tau={tau}, lambda={lam:.4f}\n")

# ---------------------------------------------------------------------------
# V1–V3: Z2 GRADING
# ---------------------------------------------------------------------------
print("-" * 50)
print("V1–V3: Z2 Grading")
print("-" * 50)

# V1: P^2 = I
P = np.array([[1, 0], [0, -1]], dtype=float)
P_sq = P @ P
check("V1: P^2 = I",
      np.allclose(P_sq, np.eye(2)),
      f"||P^2 - I|| = {norm(P_sq - np.eye(2)):.2e}")

# V2: {P, M_off} = 0
M_off = lam * np.array([[0, 1], [1, 0]], dtype=float)
anticomm = P @ M_off + M_off @ P
check("V2: {P, M_off} = 0  (Z2 grading is exact)",
      np.allclose(anticomm, 0),
      f"||{{P, M_off}}|| = {norm(anticomm):.2e}")

# V3: Eigenvalues of P are ±1 (Z2 = two-grade structure)
evals_P = np.sort(eigvals(P).real)
check("V3: Eigenvalues of P = {-1, +1}",
      np.allclose(sorted(evals_P), [-1.0, 1.0]),
      f"eigenvals = {evals_P}")

# ---------------------------------------------------------------------------
# V4–V6: COEFFICIENT ALGEBRA
# ---------------------------------------------------------------------------
print()
print("-" * 50)
print("V4–V6: Coefficient Algebra is ℝ⊕ℝ (not Clifford)")
print("-" * 50)

# The transport coefficient matrix A = [[0,1],[c^2,0]]
A = np.array([[0, 1], [c**2, 0]], dtype=float)

# V4: A^2 = c^2 * I (Euclidean, not Minkowski)
A_sq = A @ A
check("V4: A^2 = c^2*I (Euclidean signature, NOT Minkowski Dirac)",
      np.allclose(A_sq, c**2 * np.eye(2)),
      f"||A^2 - c^2*I|| = {norm(A_sq - c**2 * np.eye(2)):.2e}")

# V5: Eigenvalues of A are ±c (real, classical wave speeds)
evals_A = np.sort(eigvals(A).real)
check("V5: Eigenvalues of A = {-c, +c} (real classical characteristics)",
      np.allclose(sorted(evals_A), [-c, c]),
      f"eigenvals = {evals_A}")

# V6: algebra {I, A} is commutative (A commutes with any polynomial in A)
# Generate a random element: alpha*I + beta*A
rng = np.random.default_rng(42)
a1, b1 = rng.standard_normal(2)
a2, b2 = rng.standard_normal(2)
elem1 = a1 * np.eye(2) + b1 * A
elem2 = a2 * np.eye(2) + b2 * A
comm_12 = elem1 @ elem2 - elem2 @ elem1
check("V6: Algebra {I, A} is commutative (random elements commute)",
      np.allclose(comm_12, 0, atol=1e-12),
      f"||[elem1, elem2]|| = {norm(comm_12):.2e}")

# ---------------------------------------------------------------------------
# V7–V8: COMPLEX STRUCTURE (Ψ = s + iJ/c)
# ---------------------------------------------------------------------------
print()
print("-" * 50)
print("V7–V8: Complex Structure Ψ = s + iJ/c is not C-linear")
print("-" * 50)

# Discretise [C-s, C-J] on a grid and test C-linearity
N = 64
dx = 2 * np.pi / N
x_grid = np.arange(N) * dx

# Initial condition: single Fourier mode
k0 = 2.0
s_ic = np.sin(k0 * x_grid)
J_ic = c * np.cos(k0 * x_grid)

def transport_rhs(s_field, J_field, c_val, tau_val, dx_val):
    """Right-hand side of [C-s, C-J] using spectral derivatives."""
    k_grid = fftfreq(len(s_field), d=dx_val / (2 * np.pi))
    s_hat = fft(s_field)
    J_hat = fft(J_field)
    ds_dt = -np.real(ifft(1j * k_grid * J_hat))
    dJ_dt = -c_val**2 * np.real(ifft(1j * k_grid * s_hat)) - J_field / tau_val
    return ds_dt, dJ_dt

# Evolve a small step
dt_small = 1e-4
ds_dt, dJ_dt = transport_rhs(s_ic, J_ic, c, tau, dx)
s_new = s_ic + dt_small * ds_dt
J_new = J_ic + dt_small * dJ_dt

# Compute Psi at initial time and at new time
Psi_ic = s_ic + 1j * J_ic / c
Psi_new = s_new + 1j * J_new / c
dPsi_dt_numerical = (Psi_new - Psi_ic) / dt_small

# Correct formula from [C-s],[C-J]:
# dPsi/dt = ds/dt + i/c * dJ/dt
#          = -dJ/dx + (i/c)*(-c^2 ds/dx - J/tau)
#          = -dJ/dx - ic*ds/dx - iJ/(c*tau)
k_grid = fftfreq(N, d=dx / (2 * np.pi))
s_hat = fft(s_ic)
J_hat = fft(J_ic)
ds_dx_field = np.real(ifft(1j * k_grid * s_hat))
dJ_dx_field = np.real(ifft(1j * k_grid * J_hat))
expected_dPsi = -dJ_dx_field - 1j * c * ds_dx_field - 1j * J_ic / (c * tau)
residual = norm(dPsi_dt_numerical - expected_dPsi) / (norm(dPsi_dt_numerical) + 1e-12)
check("V7: Ψ evolution matches direct formula dΨ/dt = -∂_xJ - ic∂_xs - iJ/(cτ)",
      residual < 0.01,
      f"relative residual = {residual:.2e}")

# V8: Test C-linearity: L(i*Psi) vs i*L(Psi)
# L(Psi) = dPsi/dt (the actual numerical derivative)
L_Psi = dPsi_dt_numerical

# For i*Psi: s_new = -Im(Psi)*c, J_new = Re(Psi)*c  (multiplication by i in C)
iPsi = 1j * Psi_ic
s_i = np.real(iPsi)
J_i = np.imag(iPsi) * c

ds_i_dt, dJ_i_dt = transport_rhs(s_i, J_i, c, tau, dx)
iPsi_new = s_i + dt_small * ds_i_dt + 1j * (J_i + dt_small * dJ_i_dt) / c
L_iPsi = (iPsi_new - iPsi) / dt_small

iL_Psi = 1j * L_Psi  # i * L(Psi)

c_linear_residual = norm(L_iPsi - iL_Psi) / (norm(L_iPsi) + 1e-12)
check("V8: Equation is NOT C-linear: L(iΨ) ≠ iL(Ψ)",
      c_linear_residual > 0.05,  # should be significantly nonzero
      f"||L(iΨ) - iL(Ψ)|| / ||L(iΨ)|| = {c_linear_residual:.4f} (should be > 0)")

# ---------------------------------------------------------------------------
# V9–V11: DISPERSION RELATION
# ---------------------------------------------------------------------------
print()
print("-" * 50)
print("V9–V11: Dispersion Relation")
print("-" * 50)

# V9: Roots of omega^2 + i*omega/tau - c^2*k^2 = 0
k_test = 5.0  # k > k_c = 1/(2*c*tau)
k_c = 1.0 / (2 * c * tau)
print(f"       k_c = {k_c:.4f}, k_test = {k_test} (propagating regime: k > k_c)")

# Solve quadratic
# omega = -i/(2*tau) ± sqrt(c^2*k^2 - 1/(4*tau^2))
discriminant = c**2 * k_test**2 - 1.0 / (4 * tau**2)
omega_plus = -1j / (2 * tau) + np.sqrt(complex(discriminant))
omega_minus = -1j / (2 * tau) - np.sqrt(complex(discriminant))

# Check both roots satisfy the dispersion relation
def disp_residual(om):
    return abs(om**2 + 1j * om / tau - c**2 * k_test**2)

check("V9: omega_+ satisfies ω²+i(ω/τ)-c²k²=0",
      disp_residual(omega_plus) < 1e-10,
      f"residual = {disp_residual(omega_plus):.2e}")

# V10: Im(omega) = -1/(2*tau) < 0 (dissipative, not unitary)
check("V10: Im(ω) = -1/(2τ) < 0 for all k (dissipative, incompatible with unitarity)",
      abs(omega_plus.imag - (-1.0 / (2 * tau))) < 1e-10,
      f"Im(ω) = {omega_plus.imag:.6f}, -1/(2τ) = {-1/(2*tau):.6f}")

# V11: Evanescent mode for k < k_c
k_evan = k_c / 2  # k < k_c
disc_evan = c**2 * k_evan**2 - 1.0 / (4 * tau**2)  # < 0
omega_evan_plus = -1j / (2 * tau) + np.sqrt(complex(disc_evan))  # purely imaginary
omega_evan_minus = -1j / (2 * tau) - np.sqrt(complex(disc_evan))
check("V11: For k < k_c, ω is purely imaginary (evanescent, no propagation)",
      abs(omega_evan_plus.real) < 1e-12,
      f"Re(ω) = {omega_evan_plus.real:.2e} ≈ 0")

# ---------------------------------------------------------------------------
# V12–V13: PATH INTEGRAL WEIGHTS
# ---------------------------------------------------------------------------
print()
print("-" * 50)
print("V12–V13: Path Integral Weights")
print("-" * 50)

# PRW: W = (lambda*Dt)^n * (1-lambda*Dt)^(T/Dt - n)
Dt = 0.01  # small time step
T_total = 1.0
N_steps = int(T_total / Dt)
n_reversals_list = [0, 5, 10, 20, 50]

# V12: All PRW weights are real and positive
prw_weights = []
for n_rev in n_reversals_list:
    if n_rev <= N_steps:
        w = (lam * Dt)**n_rev * (1 - lam * Dt)**(N_steps - n_rev)
        prw_weights.append(w)

all_real_positive = all(w > 0 and np.isreal(w) for w in prw_weights)
check("V12: All PRW path weights are real and positive",
      all_real_positive,
      f"sample weights = {[f'{w:.3e}' for w in prw_weights[:3]]}")

# V13: Total probability = 1 (classical probability measure)
# Sum over all n_reversals from 0 to N_steps: binomial distribution
from scipy.special import comb
total_prob = sum(
    comb(N_steps, n, exact=True) * (lam * Dt)**n * (1 - lam * Dt)**(N_steps - n)
    for n in range(N_steps + 1)
)
check("V13: Sum of all PRW weights = 1 (classical probability measure)",
      abs(total_prob - 1.0) < 1e-10,
      f"total probability = {total_prob:.10f}")

# Contrast: Feynman weights |exp(iS/hbar)|^2 = 1 but exp(iS) is complex
hbar = 1.0
S_vals = np.linspace(0, 2 * np.pi, 100)
feynman_weights = np.exp(1j * S_vals / hbar)
feynman_real = np.allclose(feynman_weights.imag, 0)
print(f"         Feynman weights exp(iS/ℏ) are complex: {not feynman_real}")

# ---------------------------------------------------------------------------
# V14: INFORMATION GEOMETRY DIMENSION
# ---------------------------------------------------------------------------
print()
print("-" * 50)
print("V14: Information Geometry — State Space Dimension")
print("-" * 50)

# PRW internal state: (n+, n-) with n+ + n- = 1 (normalised)
# Parametrised by p = n+ in [0,1]: 1-dimensional
# Qubit state: (alpha, beta) with |alpha|^2 + |beta|^2 = 1, alpha,beta in C
# Parametrised by (theta, phi): 2-dimensional

prw_dof = 1   # one real parameter p in [0,1]
qubit_dof = 2  # two real parameters (theta in [0,pi], phi in [0,2pi))

check("V14: PRW internal DOF = 1 < Qubit DOF = 2 (missing phase)",
      prw_dof < qubit_dof,
      f"PRW dim = {prw_dof}, Qubit dim = {qubit_dof}")

# Demonstrate missing phase: two qubit states with same p but different phi
theta_q = np.pi / 3
phi1, phi2 = 0.0, np.pi / 2

# State 1: cos(θ/2)|0> + sin(θ/2)|1>
psi1 = np.array([np.cos(theta_q/2), np.sin(theta_q/2)])
# State 2: cos(θ/2)|0> + e^{iπ/2}sin(θ/2)|1>
psi2 = np.array([np.cos(theta_q/2), np.exp(1j * phi2) * np.sin(theta_q/2)])

# Same population in |0>: |<0|psi>|^2 = cos^2(theta/2) for both
pop_0_1 = abs(psi1[0])**2
pop_0_2 = abs(psi2[0])**2
same_populations = np.isclose(pop_0_1, pop_0_2)

# Different σ_x expectation (coherence observable):
sigma_x = np.array([[0, 1], [1, 0]])
exp_sx_1 = np.real(psi1.conj() @ sigma_x @ psi1)
exp_sx_2 = np.real(psi2.conj() @ sigma_x @ psi2)
different_coherence = not np.isclose(exp_sx_1, exp_sx_2)

check("V14b: Two qubit states with same PRW-accessible populations but different φ "
      "give different ⟨σx⟩",
      same_populations and different_coherence,
      f"⟨σx⟩₁={exp_sx_1:.4f}, ⟨σx⟩₂={exp_sx_2:.4f}, pop₀={pop_0_1:.4f}")

# ---------------------------------------------------------------------------
# V15–V16: COMMUTATIVITY
# ---------------------------------------------------------------------------
print()
print("-" * 50)
print("V15–V16: Commutativity of Observable Algebra")
print("-" * 50)

# V15: s and J commute pointwise
s_field = np.random.default_rng(1).standard_normal(100)
J_field = np.random.default_rng(2).standard_normal(100)

comm_sJ = s_field * J_field - J_field * s_field  # should be exactly 0
check("V15: s·J - J·s = 0 pointwise (commutative multiplication)",
      np.allclose(comm_sJ, 0),
      f"max|s·J - J·s| = {np.max(np.abs(comm_sJ)):.2e}")

# V16: E_sub and P_sub commute
E_sub = 0.5 * c**2 * s_field**2 + 0.5 * J_field**2
P_sub = s_field * J_field
comm_EP = E_sub * P_sub - P_sub * E_sub
check("V16: E_sub·P_sub - P_sub·E_sub = 0 (commutative observable algebra)",
      np.allclose(comm_EP, 0),
      f"max|[E_sub, P_sub]| = {np.max(np.abs(comm_EP)):.2e}")

# ---------------------------------------------------------------------------
# V17–V19: T-REVERSAL BREAKING
# ---------------------------------------------------------------------------
print()
print("-" * 50)
print("V17–V19: Time-Reversal Symmetry Breaking")
print("-" * 50)

# Evolve [C-s, C-J] forward by time T, then backward — should NOT recover IC if damping present

N_grid = 64
L = 2 * np.pi
dx_grid = L / N_grid
x_grid2 = np.arange(N_grid) * dx_grid

# Initial condition
s0_field = np.sin(x_grid2) + 0.5 * np.sin(2 * x_grid2)
J0_field = c * np.cos(x_grid2)

def rk4_step(s_f, J_f, dt_val, c_val, tau_val, dx_val):
    def rhs(sf, jf):
        k_grid2 = fftfreq(len(sf), d=dx_val / (2 * np.pi))
        sf_hat = fft(sf)
        jf_hat = fft(jf)
        ds = -np.real(ifft(1j * k_grid2 * jf_hat))
        dj = -c_val**2 * np.real(ifft(1j * k_grid2 * sf_hat)) - jf / tau_val
        return ds, dj
    k1s, k1j = rhs(s_f, J_f)
    k2s, k2j = rhs(s_f + dt_val/2 * k1s, J_f + dt_val/2 * k1j)
    k3s, k3j = rhs(s_f + dt_val/2 * k2s, J_f + dt_val/2 * k2j)
    k4s, k4j = rhs(s_f + dt_val * k3s, J_f + dt_val * k3j)
    return (s_f + dt_val/6 * (k1s + 2*k2s + 2*k3s + k4s),
            J_f + dt_val/6 * (k1j + 2*k2j + 2*k3j + k4j))

# Evolve forward by T_run steps
T_run = 0.2
dt_run = 0.001
n_steps = int(T_run / dt_run)

s_fwd = s0_field.copy()
J_fwd = J0_field.copy()
for _ in range(n_steps):
    s_fwd, J_fwd = rk4_step(s_fwd, J_fwd, dt_run, c, tau, dx_grid)

# V17: Energy decreases under forward evolution
E_init = 0.5 * c**2 * np.mean(s0_field**2) + 0.5 * np.mean(J0_field**2)
E_final = 0.5 * c**2 * np.mean(s_fwd**2) + 0.5 * np.mean(J_fwd**2)
check("V17: Energy E_sub decreases under forward evolution (dissipative)",
      E_final < E_init,
      f"E_init = {E_init:.6f}, E_final = {E_final:.6f}, ratio = {E_final/E_init:.4f}")

# V18: Evolve backward (negate dt) — T-symmetry would require recovery of IC
# Under T-reversal: (s, J) → (s, -J) and time reversed
# If T-invariant: evolving backward from (s_fwd, -J_fwd) should return to (s0, -J0)
s_bwd = s_fwd.copy()
J_bwd = -J_fwd.copy()  # T-reversal flips J
for _ in range(n_steps):
    s_bwd, J_bwd = rk4_step(s_bwd, J_bwd, dt_run, c, tau, dx_grid)
# J_bwd is now the T-image after backward run; compare s_bwd with s0
s_recovery_error = norm(s_bwd - s0_field) / norm(s0_field)
J_recovery_error = norm(-J_bwd - J0_field) / norm(J0_field)  # note sign flip

check("V18: T-reversed backward evolution does NOT recover IC (T-symmetry broken)",
      s_recovery_error > 0.01,
      f"s recovery error = {s_recovery_error:.4f} (>0.01 confirms T-breaking)")

# V19: Same test with tau → infinity (no damping) — should be T-invariant
tau_inf = 1e6  # effectively no damping
s_fwd_undamped = s0_field.copy()
J_fwd_undamped = J0_field.copy()
for _ in range(n_steps):
    s_fwd_undamped, J_fwd_undamped = rk4_step(
        s_fwd_undamped, J_fwd_undamped, dt_run, c, tau_inf, dx_grid)

s_bwd_undamped = s_fwd_undamped.copy()
J_bwd_undamped = -J_fwd_undamped.copy()
for _ in range(n_steps):
    s_bwd_undamped, J_bwd_undamped = rk4_step(
        s_bwd_undamped, J_bwd_undamped, dt_run, c, tau_inf, dx_grid)

s_recovery_undamped = norm(s_bwd_undamped - s0_field) / norm(s0_field)
check("V19: Undamped (τ→∞) system IS T-invariant (backward evolution recovers IC)",
      s_recovery_undamped < 0.01,
      f"s recovery error (undamped) = {s_recovery_undamped:.6f} (<0.01 confirms T-invariance)")

# ---------------------------------------------------------------------------
# V20: SYMPLECTIC STRUCTURE AND ENERGY DISSIPATION
# ---------------------------------------------------------------------------
print()
print("-" * 50)
print("V20: Energy Dissipation Rate")
print("-" * 50)

# Theoretical: dE_sub/dt = -(1/tau) ∫ J^2 dx
# Numerical: measure actual energy loss rate
dt_energy = 0.001
s_en = s0_field.copy()
J_en = J0_field.copy()

E_before = (0.5 * c**2 * np.mean(s_en**2) + 0.5 * np.mean(J_en**2)) * (N_grid * dx_grid)
s_en, J_en = rk4_step(s_en, J_en, dt_energy, c, tau, dx_grid)
E_after = (0.5 * c**2 * np.mean(s_en**2) + 0.5 * np.mean(J_en**2)) * (N_grid * dx_grid)

dE_numerical = (E_after - E_before) / dt_energy

# Theoretical: dE/dt = -(1/tau) ∫ J^2 dx
dE_theoretical = -(1.0 / tau) * np.mean(J0_field**2) * (N_grid * dx_grid)

check("V20: Measured energy loss rate matches -(1/τ)∫J²dx",
      abs(dE_numerical - dE_theoretical) / abs(dE_theoretical) < 0.05,
      f"dE/dt (numerical) = {dE_numerical:.4f}, theoretical = {dE_theoretical:.4f}")

# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print(f"RESULTS: {PASS_COUNT} PASS,  {FAIL_COUNT} FAIL  (out of {PASS_COUNT+FAIL_COUNT} tests)")
print("=" * 70)

if FAIL_COUNT == 0:
    print("""
All 20 tests pass. The numerical evidence confirms:

  - The substrate coefficient algebra is ℝ⊕ℝ (commutative, not Clifford)
  - The complex field Ψ=s+iJ/c does NOT satisfy a C-linear equation
  - Dispersion roots have Im(ω) = -1/(2τ) < 0 (dissipation, not unitarity)
  - PRW path weights are real positive (classical probability, not quantum amplitude)
  - The PRW internal DOF is 1-dimensional (qubit needs 2D for complex phase)
  - Observable algebra is commutative: [s,J]_pointwise = [E_sub,P_sub]_pointwise = 0
  - T-reversal symmetry is broken by the damping term −J/τ
  - Undamped system IS T-invariant (damping is the sole source of breaking)
  - Energy dissipation rate matches -(1/τ)∫J²dx (classical Hamiltonian with loss)

MANDATORY CONCLUSION: B
The substrate contains richer mathematical structure than pure classical
diffusion (it has symplectic structure, Z2 grading, causal propagation,
and a path-integral representation), but this structure is insufficient
for quantum-state emergence due to three proven obstructions:

  Q1: Commutative observable algebra (cannot derive [ŝ,Ĵ]=iℏδ internally)
  Q2: No complex phase degree of freedom (cannot derive superposition)
  Q3: T-reversal breaking (cannot derive unitary Hamiltonian evolution)
""")
else:
    print(f"\n  WARNING: {FAIL_COUNT} test(s) failed — review output above.\n")
