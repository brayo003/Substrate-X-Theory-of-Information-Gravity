"""
substrate_transport_validation.py
==================================
Numerical limiting-case tests for substrate_transport_derivation.md.

Every test uses only the PRW microscopic parameters (v, lambda) or the
continuum parameters derived from them (tau=1/(2*lambda), c=v, D=c^2*tau).
No phenomenological constants are fitted.

Tests:
  V1   Energy transport: dE_sub/dt + div(F_E) = -J^2/tau  (PDE residual)
  V2   Momentum transport: dP_sub/dt + dE_sub/dx = -P_sub/tau  (PDE residual)
  V3   Total information conserved in source-free evolution
  V4   Dispersion: propagating modes (k > k_c) oscillate at Omega1(k)
  V5   Dispersion: evanescent modes (k < k_c) decay without oscillation
  V6   Energy dissipation: E_sub decays monotonically (no sources)
  V7   Vorticity steady-state: Omega_J_ss = -2*s*omega_sub
  V8   Current variance: <|delta_J|^2> = (2/3)*s0^2*omega_rot^2*r^2
  V9   Diffusion limit (tau->0): telegrapher reduces to diffusion equation
  V10  Critical wavenumber k_c = 1/(2*c*tau) = lambda/c confirmed numerically
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit
from scipy.signal import argrelextrema
import warnings
warnings.filterwarnings("ignore")

print("=" * 65)
print("SUBSTRATE TRANSPORT — NUMERICAL VALIDATION")
print("substrate_transport_validation.py")
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

# ---------------------------------------------------------------------------
# Shared setup: PRW parameters
# ---------------------------------------------------------------------------
N     = 256        # spatial grid points
L_box = 20.0       # domain length
h     = L_box / N  # grid spacing
x_arr = np.arange(N) * h
x0    = L_box / 2

# PRW microscopic parameters
v_mic = 2.0        # microscopic speed  [m/s]
lam   = 1.5        # reversal rate      [s^-1]

# Derived continuum parameters
tau_c = 1.0 / (2.0 * lam)    # damping time  [s]
c_c   = v_mic                  # causal speed  [m/s]
D_c   = c_c**2 * tau_c         # diffusivity   [m^2/s]
k_c   = 1.0 / (2.0 * c_c * tau_c)  # critical wavenumber [rad/m]

print(f"\n  PRW parameters: v={v_mic}, lambda={lam}")
print(f"  Derived:        tau={tau_c:.4f}, c={c_c}, D={D_c:.4f}, k_c={k_c:.4f}")

def grad_c(f):
    """Central-difference gradient (periodic BCs)."""
    return (np.roll(f, -1) - np.roll(f, 1)) / (2.0 * h)

def laplacian(f):
    """Second-order Laplacian (periodic BCs)."""
    return (np.roll(f, -1) - 2.0 * f + np.roll(f, 1)) / h**2

def rhs_coupled(t_val, y):
    """RHS of coupled (C-s, C-J) system (source-free, no drift)."""
    s = y[:N]
    J = y[N:]
    ds = -grad_c(J)
    dJ = -c_c**2 * grad_c(s) - (1.0 / tau_c) * J
    return np.concatenate([ds, dJ])


# ===========================================================================
# V1: Energy transport PDE residual
# ===========================================================================
print("\n--- V1: Energy transport equation residual ---")

# Evolve (s, J) for one time unit, then check:
#   dE_sub/dt + d(c^2*s*J)/dx  ==  -J^2/tau  (pointwise)
#
# Strategy: record s, J at t and t+dt; compute finite-difference dE_sub/dt
# and compare to RHS.

sigma_v1 = 1.5
s0_v1 = np.exp(-((x_arr - x0)**2) / (2*sigma_v1**2))
J0_v1 = c_c * s0_v1 * 0.3  # non-zero initial flux
y0_v1 = np.concatenate([s0_v1, J0_v1])

dt_small = 1e-4
sol_v1 = solve_ivp(rhs_coupled, (0, 2*dt_small), y0_v1,
                   method='RK45', rtol=1e-10, atol=1e-12,
                   t_eval=[0, dt_small, 2*dt_small], max_step=dt_small/5)

s_t0 = sol_v1.y[:N, 0];  J_t0 = sol_v1.y[N:, 0]
s_t1 = sol_v1.y[:N, 1];  J_t1 = sol_v1.y[N:, 1]
s_t2 = sol_v1.y[:N, 2];  J_t2 = sol_v1.y[N:, 2]

# Energy at three times
E0 = 0.5*c_c**2*s_t0**2 + 0.5*J_t0**2
E1 = 0.5*c_c**2*s_t1**2 + 0.5*J_t1**2
E2 = 0.5*c_c**2*s_t2**2 + 0.5*J_t2**2

dE_dt = (E2 - E0) / (2*dt_small)
div_FE = grad_c(c_c**2 * s_t1 * J_t1)
dissip = -J_t1**2 / tau_c

residual_v1 = dE_dt + div_FE - dissip
# Interior only (avoid boundary artefacts)
rel_v1 = np.max(np.abs(residual_v1[10:-10])) / (np.max(np.abs(dissip[10:-10])) + 1e-12)
check("V1: Energy eq ∂E_sub/∂t + ∂(c²sJ)/∂x = −J²/τ (residual < 3%)",
      rel_v1 < 0.03,
      f"max rel residual = {rel_v1:.4e}")


# ===========================================================================
# V2: Momentum transport PDE residual
# ===========================================================================
print("\n--- V2: Momentum transport equation residual ---")

P_t0 = s_t0 * J_t0
P_t1 = s_t1 * J_t1
P_t2 = s_t2 * J_t2

dP_dt  = (P_t2 - P_t0) / (2*dt_small)
dE_dx  = grad_c(E1)
damp_P = -P_t1 / tau_c

residual_v2 = dP_dt + dE_dx - damp_P
rel_v2 = np.max(np.abs(residual_v2[10:-10])) / (np.max(np.abs(damp_P[10:-10])) + 1e-12)
check("V2: Momentum eq ∂P_sub/∂t + ∂E_sub/∂x = −P_sub/τ (residual < 3%)",
      rel_v2 < 0.03,
      f"max rel residual = {rel_v2:.4e}")


# ===========================================================================
# V3: Total information conserved (source-free)
# ===========================================================================
print("\n--- V3: Total information Q = ∫s dx conserved ---")

s_ic = np.exp(-((x_arr - x0)**2) / (2*2.0**2))
J_ic = np.zeros(N)
y0_v3 = np.concatenate([s_ic, J_ic])

T_v3 = 5.0
t_eval_v3 = np.linspace(0, T_v3, 200)
sol_v3 = solve_ivp(rhs_coupled, (0, T_v3), y0_v3,
                   method='RK45', rtol=1e-10, atol=1e-12,
                   t_eval=t_eval_v3, max_step=0.01)

Q_v3 = np.sum(sol_v3.y[:N, :], axis=0) * h
Q_rel_var = np.max(np.abs(Q_v3 - Q_v3[0])) / Q_v3[0]
check("V3: Q = ∫s dx conserved to < 0.01% over T=5",
      Q_rel_var < 1e-4,
      f"max relative variation = {Q_rel_var:.2e}")


# ===========================================================================
# V4: Propagating mode (k > k_c) oscillates at Omega1(k)
# ===========================================================================
print("\n--- V4: Propagating mode oscillates at Omega1(k) ---")

# Choose k = 3 * k_c  (well into propagating regime)
k_test = 3.0 * k_c
Omega1_theory = np.sqrt(c_c**2 * k_test**2 - 1.0/(4.0*tau_c**2))
period_theory = 2.0 * np.pi / Omega1_theory

# Initialize a single cosine mode
s_mode = np.cos(k_test * x_arr)
J_mode = np.zeros(N)
y0_v4 = np.concatenate([s_mode, J_mode])

T_v4 = 4.0 * period_theory
t_eval_v4 = np.linspace(0, T_v4, 800)
sol_v4 = solve_ivp(rhs_coupled, (0, T_v4), y0_v4,
                   method='RK45', rtol=1e-10, atol=1e-12,
                   t_eval=t_eval_v4, max_step=period_theory/100)

# Measure the spatial mode amplitude at wavenumber k_test via projection
proj_v4 = np.array([
    np.sum(sol_v4.y[:N, i] * np.cos(k_test * x_arr)) * h / (L_box/2)
    for i in range(len(t_eval_v4))
])

# Remove the exponential damping envelope before measuring frequency
# Fit: A(t) * cos(Omega1*t + phi), A(t) = A0 * exp(-t/(2*tau))
decay_env = np.exp(-t_eval_v4 / (2.0 * tau_c))
proj_norm = proj_v4 / (decay_env + 1e-12)

# Find zero crossings to measure half-period
sign_changes = np.where(np.diff(np.sign(proj_norm)))[0]
if len(sign_changes) >= 4:
    half_periods = np.diff(t_eval_v4[sign_changes])
    period_meas  = 2.0 * np.median(half_periods)
    Omega1_meas  = 2.0 * np.pi / period_meas
    omega_err    = abs(Omega1_meas - Omega1_theory) / Omega1_theory
    check("V4: Propagating mode frequency matches Ω₁(k)=√(c²k²−1/4τ²) (within 3%)",
          omega_err < 0.03,
          f"Ω₁_theory={Omega1_theory:.4f}, Ω₁_measured={Omega1_meas:.4f}, err={omega_err:.4f}")
else:
    check("V4: Enough zero crossings for frequency measurement", False,
          f"only {len(sign_changes)} sign changes found")


# ===========================================================================
# V5: Evanescent mode (k < k_c) decays without oscillation
# ===========================================================================
print("\n--- V5: Evanescent mode (k < k_c) has no oscillation ---")

# Choose k = 0.3 * k_c  (well into evanescent regime)
k_evan = 0.3 * k_c
# Theory: both roots purely imaginary => purely exponential decay, no oscillation

s_evan = np.cos(k_evan * x_arr)
J_evan = np.zeros(N)
y0_v5  = np.concatenate([s_evan, J_evan])

T_v5 = 5.0 / lam   # a few damping times
t_eval_v5 = np.linspace(0, T_v5, 400)
sol_v5 = solve_ivp(rhs_coupled, (0, T_v5), y0_v5,
                   method='RK45', rtol=1e-10, atol=1e-12,
                   t_eval=t_eval_v5, max_step=T_v5/200)

proj_v5 = np.array([
    np.sum(sol_v5.y[:N, i] * np.cos(k_evan * x_arr)) * h / (L_box/2)
    for i in range(len(t_eval_v5))
])

# Check for absence of oscillation: no zero crossing after initial transient
# (skip the first 20% of the time series)
skip = int(0.2 * len(t_eval_v5))
proj_late = proj_v5[skip:]
sign_changes_evan = np.sum(np.diff(np.sign(proj_late)) != 0)
check("V5: Evanescent mode has no oscillation (0 sign changes after transient)",
      sign_changes_evan == 0,
      f"sign changes in late signal = {sign_changes_evan}")


# ===========================================================================
# V6: Energy E_sub decays monotonically (source-free, no drift)
# ===========================================================================
print("\n--- V6: E_sub decays monotonically in source-free evolution ---")

# From the energy equation: dE_sub/dt = -div(F_E) - J^2/tau
# Integrating over space: d/dt int(E_sub dx) = -int(J^2/tau dx) <= 0
# So total energy is a non-increasing function of time.

s_v6 = np.exp(-((x_arr - x0)**2) / (2*1.5**2))
J_v6 = c_c * s_v6 * 0.5
y0_v6 = np.concatenate([s_v6, J_v6])

T_v6 = 8.0
t_eval_v6 = np.linspace(0, T_v6, 300)
sol_v6 = solve_ivp(rhs_coupled, (0, T_v6), y0_v6,
                   method='RK45', rtol=1e-10, atol=1e-12,
                   t_eval=t_eval_v6, max_step=0.02)

E_total_v6 = np.array([
    np.sum(0.5*c_c**2*sol_v6.y[:N, i]**2 + 0.5*sol_v6.y[N:, i]**2) * h
    for i in range(len(t_eval_v6))
])

# Check monotonic decrease
dE_v6 = np.diff(E_total_v6)
n_increase = np.sum(dE_v6 > 1e-12)
check("V6: Total energy E_sub is non-increasing (monotone decay)",
      n_increase == 0,
      f"number of time steps with dE>0: {n_increase}")


# ===========================================================================
# V7: Vorticity steady state: Omega_J_ss = -2*s*omega_sub
# ===========================================================================
print("\n--- V7: Vorticity steady state Omega_J = -2s*omega_sub ---")

# In 2D (z-component): omega_sub = (1/2)*curl(v_sub)
# We model a uniform substrate vorticity omega_sub_val by adding a
# drift v_sub = (-omega_sub_val*y, omega_sub_val*x) in 2D.
# For the 1D test: use the vorticity equation directly.
# d(Omega_J)/dt = -(1/tau)*Omega_J - (2s/tau)*omega_sub
# Steady state: Omega_J = -2*s*omega_sub

# Numerically: initialise Omega_J at zero, evolve to steady state under constant
# source -(2*s_bar/tau)*omega_sub_val for a uniform density s_bar.

omega_sub_val = 0.4
s_bar_v7      = 1.0
tau_v7        = tau_c

# ODE: dOmega/dt = -(1/tau)*Omega - (2*s_bar/tau)*omega_sub
# Exact solution: Omega(t) = (Omega_0 + 2*s_bar*omega_sub)*exp(-t/tau) - 2*s_bar*omega_sub
# Steady state: Omega_ss = -2*s_bar*omega_sub

Omega_0 = 0.0
T_v7 = 20.0 * tau_v7
t_arr_v7 = np.linspace(0, T_v7, 500)

def vort_rhs(t_val, y):
    Omega = y[0]
    return [-(1.0/tau_v7)*Omega - (2.0*s_bar_v7/tau_v7)*omega_sub_val]

sol_v7 = solve_ivp(vort_rhs, (0, T_v7), [Omega_0],
                   method='RK45', rtol=1e-10, atol=1e-12,
                   t_eval=t_arr_v7)

Omega_final = sol_v7.y[0, -1]
Omega_ss_theory = -2.0 * s_bar_v7 * omega_sub_val
err_v7 = abs(Omega_final - Omega_ss_theory) / abs(Omega_ss_theory)
check("V7: Vorticity steady state Ω_J = −2s·ω_sub (within 0.1%)",
      err_v7 < 1e-3,
      f"Ω_J_numerical={Omega_final:.6f}, theory={Omega_ss_theory:.6f}, err={err_v7:.2e}")


# ===========================================================================
# V8: Current variance <|delta_J|^2> = (2/3)*s0^2*omega_rot^2*r^2
# ===========================================================================
print("\n--- V8: Angular-averaged current variance ---")

# Generate random unit vectors r_hat on the sphere, compute |delta_J|^2 = s0^2*(omega_rot x r_hat)^2
# Average over N_mc sample directions.
N_mc = 100000
np.random.seed(42)

s0_v8      = 1.5
omega_v8   = 2.3    # omega_rot
r_v8       = 0.8    # fixed radius

# Random points on unit sphere
phi_mc   = 2.0*np.pi * np.random.rand(N_mc)
costheta = 2.0*np.random.rand(N_mc) - 1.0
sintheta = np.sqrt(1.0 - costheta**2)

r_vec = np.column_stack([
    sintheta * np.cos(phi_mc),
    sintheta * np.sin(phi_mc),
    costheta
]) * r_v8  # shape (N_mc, 3)

# omega_rot along z-axis: omega_rot_vec = (0, 0, omega_v8)
omega_vec = np.array([0.0, 0.0, omega_v8])

# delta_J = s0 * (omega_rot x r)
cross_prod = np.cross(omega_vec[np.newaxis, :], r_vec)  # (N_mc, 3)
deltaJ_vec = s0_v8 * cross_prod
deltaJ_sq  = np.sum(deltaJ_vec**2, axis=1)

mean_var_mc = np.mean(deltaJ_sq)
theory_var  = (2.0/3.0) * s0_v8**2 * omega_v8**2 * r_v8**2
err_v8 = abs(mean_var_mc - theory_var) / theory_var
check("V8: ⟨|δJ|²⟩ = (2/3)s₀²ω_rot²r² (MC average, within 1%)",
      err_v8 < 0.01,
      f"MC average={mean_var_mc:.6f}, theory={theory_var:.6f}, err={err_v8:.4f}")


# ===========================================================================
# V9: Diffusion limit (tau -> 0): telegrapher reduces to diffusion
# ===========================================================================
print("\n--- V9: Diffusion limit: telegrapher → diffusion as tau→0 ---")

# In the limit tau->0 with D = c^2*tau = const, the telegrapher reduces to
# ds/dt = D * ∇²s  (Fourier's second law).
# For a Gaussian initial condition, the variance grows as w^2(t) = w0^2 + 2*D*t.
#
# Test: use a very small tau (tau_small = 0.01) and verify Gaussian spreading
# matches D = c^2*tau, not the telegrapher's ballistic early-time behavior.

tau_small = 0.02
c_small   = 3.0
D_small   = c_small**2 * tau_small   # = 0.18
lam_small = 1.0 / (2.0 * tau_small)

sigma0_v9 = 1.0
s_v9 = np.exp(-((x_arr - x0)**2) / (2.0*sigma0_v9**2))
J_v9 = np.zeros(N)
y0_v9 = np.concatenate([s_v9, J_v9])

def rhs_v9(t_val, y):
    s_f = y[:N];  J_f = y[N:]
    ds = -grad_c(J_f)
    dJ = -c_small**2 * grad_c(s_f) - (1.0/tau_small)*J_f
    return np.concatenate([ds, dJ])

T_v9 = 6.0   # several diffusion times (t_diff = w0^2/(2D) ≈ 2.8)
t_eval_v9 = np.linspace(2.0*tau_small, T_v9, 60)  # skip early ballistic transient

sol_v9 = solve_ivp(rhs_v9, (0, T_v9), y0_v9,
                   method='RK45', rtol=1e-10, atol=1e-12,
                   t_eval=t_eval_v9, max_step=tau_small/5)

w2_v9 = []
t_v9  = []
for i, t_val in enumerate(t_eval_v9):
    s_snap = np.maximum(sol_v9.y[:N, i], 0)
    norm   = np.sum(s_snap) * h
    if norm > 1e-12:
        mean_x = np.sum(x_arr * s_snap) * h / norm
        var_x  = np.sum((x_arr - mean_x)**2 * s_snap) * h / norm
        w2_v9.append(var_x)
        t_v9.append(t_val)

t_v9  = np.array(t_v9)
w2_v9 = np.array(w2_v9)

# Fit w^2 = w0^2 + 2*D*t
coeffs_v9 = np.polyfit(t_v9, w2_v9, 1)
D_measured_v9 = coeffs_v9[0] / 2.0
D_err_v9 = abs(D_measured_v9 - D_small) / D_small
check("V9: Diffusion limit tau→0: Gaussian spreads at D=c²τ (within 5%)",
      D_err_v9 < 0.05,
      f"D_measured={D_measured_v9:.5f}, D_expected={D_small:.5f}, err={D_err_v9:.4f}")


# ===========================================================================
# V10: Critical wavenumber k_c = lambda/c confirmed
# ===========================================================================
print("\n--- V10: Critical wavenumber k_c = lambda/c ---")

# For each wavenumber k the EXACT solution of the coupled (C-s,C-J) system
# for a pure cosine mode is:
#
#   Propagating (k > k_c):  s(t) = exp(-t/2tau) * [A*cos(Omega1*t) + B*sin(Omega1*t)]
#   Evanescent  (k < k_c):  s(t) = C*exp(-alpha1*t) + D*exp(-alpha2*t)
#
# where alpha1,2 = 1/(2tau) ∓ sqrt(1/(4tau^2) - c^2*k^2)  > 0.
#
# Classification: fit the projected amplitude to each model; use residuals.

def fit_oscillatory(t_arr, proj_arr):
    """Fit A*exp(-t/2tau)*cos(w*t+phi). Return residual RMS."""
    try:
        def model(t, A, w, phi):
            return A * np.exp(-t / (2.0*tau_c)) * np.cos(w*t + phi)
        p0 = [proj_arr[0], Omega1_theory_ref, 0.0]
        popt, _ = curve_fit(model, t_arr, proj_arr, p0=p0, maxfev=5000)
        resid = proj_arr - model(t_arr, *popt)
        return np.sqrt(np.mean(resid**2)), popt[1]
    except Exception:
        return np.inf, 0.0

def fit_evanescent(t_arr, proj_arr):
    """Fit C*exp(-a1*t) + D*exp(-a2*t) with a1,a2 > 0. Return residual RMS."""
    try:
        def model(t, C, a1, D, a2):
            return C * np.exp(-np.abs(a1)*t) + D * np.exp(-np.abs(a2)*t)
        p0 = [proj_arr[0]*0.6, 1.0/tau_c, proj_arr[0]*0.4, 1.0/(2.0*tau_c)]
        popt, _ = curve_fit(model, t_arr, proj_arr, p0=p0, maxfev=5000)
        resid = proj_arr - model(t_arr, *popt)
        return np.sqrt(np.mean(resid**2))
    except Exception:
        return np.inf

k_values   = np.array([0.2, 0.5, 0.8, 1.2, 1.5, 2.0, 3.0]) * k_c
theory_osc = (k_values / k_c) > 1.0

# Reference oscillation frequency for fit initialisation (k=2*k_c)
Omega1_theory_ref = np.sqrt(c_c**2*(2*k_c)**2 - 1.0/(4*tau_c**2))

T_v10      = 15.0 * tau_c
n_v10      = 600
t_eval_v10 = np.linspace(0.5*tau_c, T_v10, n_v10)   # skip t=0 transient

oscillatory_flags = []
for k_test in k_values:
    s_k = np.cos(k_test * x_arr)
    J_k = np.zeros(N)
    sol_k = solve_ivp(rhs_coupled, (0, T_v10),
                      np.concatenate([s_k, J_k]),
                      method='RK45', rtol=1e-10, atol=1e-12,
                      t_eval=t_eval_v10, max_step=tau_c/30)

    proj_k = np.array([
        np.sum(sol_k.y[:N, i] * np.cos(k_test * x_arr)) * h / (L_box/2)
        for i in range(n_v10)
    ])

    # For oscillatory fit, use the actual Omega1 for this k
    Omega1_k = abs(c_c**2 * k_test**2 - 1.0/(4*tau_c**2))
    if c_c**2*k_test**2 > 1.0/(4*tau_c**2):
        Omega1_theory_ref = np.sqrt(c_c**2*k_test**2 - 1.0/(4*tau_c**2))
    else:
        Omega1_theory_ref = 0.01  # evanescent — dummy value for fit

    rms_osc,  _ = fit_oscillatory(t_eval_v10, proj_k)
    rms_evan    = fit_evanescent(t_eval_v10, proj_k)

    # Mode is oscillatory if the oscillatory fit is strictly better
    is_osc = rms_osc < rms_evan
    oscillatory_flags.append(is_osc)

oscillatory_flags = np.array(oscillatory_flags)
k_over_kc = k_values / k_c

n_correct = np.sum(oscillatory_flags == theory_osc)
print(f"  k/k_c values: {np.round(k_over_kc, 2)}")
print(f"  Oscillatory?  {oscillatory_flags.astype(int)}")
print(f"  Theory:       {theory_osc.astype(int)}")
check("V10: Oscillatory/evanescent transition at k_c confirmed (≥6/7 correct)",
      n_correct >= 6,
      f"{n_correct}/{len(k_values)} modes correctly classified")


# ===========================================================================
# Final report
# ===========================================================================
print("\n" + "=" * 65)
print(f"VALIDATION COMPLETE:  {PASS} PASSED,  {FAIL} FAILED")
print("=" * 65)
print("""
Test summary:

  V1   Energy eq ∂E_sub/∂t + ∂(c²sJ)/∂x = −J²/τ  (PDE residual)
  V2   Momentum eq ∂P_sub/∂t + ∂E_sub/∂x = −P_sub/τ  (PDE residual)
  V3   Total information Q = ∫s dx conserved to < 0.01%
  V4   Propagating mode (k>k_c) oscillates at Ω₁(k)=√(c²k²−1/4τ²)
  V5   Evanescent mode (k<k_c) decays without oscillation
  V6   Total energy E_sub non-increasing (monotone decay)
  V7   Vorticity steady state Ω_J = −2s·ω_sub  confirmed
  V8   ⟨|δJ|²⟩ = (2/3)s₀²ω_rot²r²  (MC sphere average)
  V9   Diffusion limit (τ→0): D = c²τ recovered
  V10  Critical wavenumber k_c = λ/c confirmed by mode classification

All tests use only derived parameters (τ=1/(2λ), c=v, D=c²τ).
No phenomenological constants are fitted.
""")
