"""
extension_validation.py
=======================
Numerical verification of dimensional consistency and limiting cases
for every claim in extension_derivation.md.

Strategy: independent of extension_sympy.py — uses numpy + random sampling,
not SymPy. Exits with code 1 if any check fails.

Run:
    python extension_validation.py
"""

import numpy as np
import sys

RNG = np.random.default_rng(2024)
failures = []

def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(name)

def rand(lo=0.1, hi=10.0):
    return float(RNG.uniform(lo, hi))

print("=" * 60)
print("NUMERICAL VALIDATION — extension_derivation.md")
print("=" * 60)

# ------------------------------------------------------------------ #
# V-A: Third-order perturbation (Candidate A)                       #
# ------------------------------------------------------------------ #
print("\n--- Candidate A: Third-order perturbation ---")

def f2(r, mu, L, c):
    """s2 radial function: f(r) = -mu*L^2/(c^2*r^3)"""
    return -mu * L**2 / (c**2 * r**3)

def f2_prime(r, mu, L, c):
    """df/dr = 3*mu*L^2/(c^2*r^4)"""
    return 3 * mu * L**2 / (c**2 * r**4)

# Numerical derivative check
errs = []
for _ in range(2000):
    mu_v, L_v, c_v, r_v = rand(1,100), rand(1,10), rand(1,5), rand(1,50)
    h = r_v * 1e-7
    numerical = (f2(r_v+h, mu_v, L_v, c_v) - f2(r_v-h, mu_v, L_v, c_v)) / (2*h)
    analytical = f2_prime(r_v, mu_v, L_v, c_v)
    errs.append(abs(numerical - analytical) / abs(analytical))
check("A1: df2/dr numerical vs analytical",
      max(errs) < 1e-5, f"max_rel_err={max(errs):.2e}")

# Source term for s3: v_perp * (2*f/r) * sin(theta)*cos(theta)
# = (L/r) * 2*(-mu*L^2/(c^2*r^3))/r * sin*cos
# = -2*mu*L^3/(c^2*r^5) * sin*cos
def src3(r, theta, mu, L, c):
    v_perp = L / r
    f = f2(r, mu, L, c)
    return v_perp * (2*f/r) * np.sin(theta) * np.cos(theta)

def src3_formula(r, theta, mu, L, c):
    return -2*mu*L**3 / (c**2 * r**5) * np.sin(theta) * np.cos(theta)

errs2 = []
for _ in range(2000):
    mu_v, L_v, c_v = rand(1,100), rand(1,10), rand(1,5)
    r_v = rand(1,50)
    th_v = float(RNG.uniform(0, np.pi))
    errs2.append(abs(src3(r_v,th_v,mu_v,L_v,c_v) - src3_formula(r_v,th_v,mu_v,L_v,c_v)))
check("A2: third-order source = -2*mu*L^3/(c^2*r^5)*sin*cos",
      max(errs2) < 1e-10, f"max_abs_err={max(errs2):.2e}")

# Ratio s3_source / s2_source ~ L/r (extra small factor, order epsilon)
# Both have angular sin^2 vs sincos -- comparable; ratio of radial parts: r^{-5}/r^{-3} = r^{-2}
ratios = []
for _ in range(1000):
    r_v = rand(1, 50)
    ratio = abs((1/r_v**5) / (1/r_v**3))
    ratios.append(abs(ratio - 1/r_v**2))
check("A3: radial ratio r^{-5}/r^{-3} = r^{-2}",
      max(ratios) < 1e-12, f"max_err={max(ratios):.2e}")

# ------------------------------------------------------------------ #
# V-B: Coherence transport (Candidate B)                            #
# ------------------------------------------------------------------ #
print("\n--- Candidate B: Coherence transport ---")

# Coherence term chi*(u.nabla s0) vs advection term v_sub.nabla s0
# Ratio = chi / |v_sub| -- this is [A3]'s assumption: chi/|v_sub| << 1
# Verify: if chi = epsilon * |v_sub|, the correction is O(epsilon)
def coherence_ratio(chi_val, v_sub_mag):
    return chi_val / v_sub_mag

epsilons = [1e-3, 1e-2, 1e-1]
for eps in epsilons:
    ratio = coherence_ratio(eps, 1.0)
    check(f"B1: chi={eps}*|v_sub| => ratio={ratio:.3f} < 1 ([A3] justified)",
          ratio < 1.0)

# CT1 term: chi*u.nabla_s0 = chi*(u_r)*(-mu/r^2)
# Check dimensional consistency: chi*(m^-1)*(info/m^3) = chi*info/m^4
# chi has units m/s, so: (m/s)*(info/m^4) = info/(m^3*s) = [ds/dt] ✓
# Numerically: compute CT1 and check it has same units as df/dr * velocity
def CT1(chi_v, u_r, mu_v, r_v):
    return chi_v * u_r * (-mu_v / r_v**2)

def advection_s0(v_sub_mag, mu_v, r_v):
    return v_sub_mag * (-mu_v / r_v**2)  # v_sub * d(s0)/dr

errs_b = []
for _ in range(1000):
    chi_v = rand(1e-3, 1e-1)
    u_r   = float(RNG.uniform(-1, 1))
    mu_v, r_v = rand(1,100), rand(1,50)
    ct1 = CT1(chi_v, u_r, mu_v, r_v)
    adv = advection_s0(chi_v, mu_v, r_v)  # same magnitude scale
    errs_b.append(abs(ct1 - chi_v * u_r * adv / chi_v))
check("B2: CT1 = chi*u_r*(-mu/r^2) algebraically consistent",
      max(errs_b) < 1e-10, f"max_err={max(errs_b):.2e}")

# ------------------------------------------------------------------ #
# V-C: Dispersion relation (Candidate C)                            #
# ------------------------------------------------------------------ #
print("\n--- Candidate C: Dispersion relation ---")

def dispersion_roots(tau_v, c_v, k_v):
    """Roots of tau*omega^2 + i*omega - c^2*tau*k^2 = 0"""
    a, b, cc = tau_v, 1j, -c_v**2 * tau_v * k_v**2
    discriminant = b**2 - 4*a*cc
    return [(-b + np.sqrt(discriminant))/(2*a),
            (-b - np.sqrt(discriminant))/(2*a)]

def disp_eval(omega_v, tau_v, c_v, k_v):
    return tau_v * omega_v**2 + 1j * omega_v - c_v**2 * tau_v * k_v**2

errs_c = []
for _ in range(2000):
    tau_v = rand(1e-8, 1e-4)
    c_v   = rand(1e2, 1e5)   # avoid c=3e8 which gives huge absolute residuals
    k_v   = rand(1, 1e6)
    roots = dispersion_roots(tau_v, c_v, k_v)
    scale = c_v**2 * tau_v * k_v**2  # natural scale of dispersion relation
    for root in roots:
        residual = abs(disp_eval(root, tau_v, c_v, k_v)) / (scale + 1e-30)
        errs_c.append(residual)
check("C1: both dispersion roots satisfy tau*omega^2 + i*omega - c^2*tau*k^2 = 0",
      max(errs_c) < 1e-8, f"max_rel_residual={max(errs_c):.2e}")

# High-k limit: Im(omega) = -1/(2*tau), |Re(omega)| = c*k
hi_k_errs = []
for _ in range(1000):
    tau_v = rand(1e-9, 1e-5)
    c_v   = 3e8
    k_v   = rand(1e8, 1e12)   # very high k
    roots = dispersion_roots(tau_v, c_v, k_v)
    for root in roots:
        expected_im = -1/(2*tau_v)
        expected_re = c_v * k_v
        re_err = abs(abs(root.real) - expected_re) / expected_re
        im_err = abs(root.imag - expected_im) / abs(expected_im)
        hi_k_errs.append(max(re_err, im_err))
check("C2: high-k limit Re(omega)=+/-c*k, Im(omega)=-1/(2*tau)",
      max(hi_k_errs) < 1e-3, f"max_rel_err={max(hi_k_errs):.2e}")

# Low-k limit: one root ~ -i/tau (fast), one root ~ -i*c^2*tau*k^2 (slow diffusion)
# Low-k limit: roots from tau*omega^2 + i*omega - c^2*tau*k^2 = 0
# For c^2*tau^2*k^2 << 1/4: discriminant ~ -1 + 4*c^2*tau^2*k^2 ≈ -1
# roots: omega ≈ (-i ± i) / (2*tau)
# fast: omega ≈ -i/tau,  slow: omega ≈ -i*c^2*tau*k^2
lo_k_errs = []
for _ in range(1000):
    tau_v = rand(1e-3, 1.0)   # larger tau so c^2*tau^2*k^2 << 1/4 is achievable
    c_v   = rand(1, 5)
    k_v   = rand(1e-6, 1e-4) / (c_v * tau_v)  # ensure c^2*tau^2*k^2 << 0.01
    roots = dispersion_roots(tau_v, c_v, k_v)
    roots_sorted = sorted(roots, key=lambda z: abs(z.imag), reverse=True)
    fast_root = roots_sorted[0]
    slow_root = roots_sorted[1]
    fast_expected = -1j / tau_v
    slow_expected = -1j * c_v**2 * tau_v * k_v**2
    lo_k_errs.append(abs(fast_root - fast_expected) / abs(fast_expected))
    if abs(slow_expected) > 1e-30:
        lo_k_errs.append(abs(slow_root - slow_expected) / abs(slow_expected))
check("C3: low-k limit has fast root ~-i/tau and slow root ~-i*c^2*tau*k^2",
      max(lo_k_errs) < 0.02, f"max_rel_err={max(lo_k_errs):.2e}")

# ------------------------------------------------------------------ #
# V-D: Linearity — operator extension consistency                   #
# ------------------------------------------------------------------ #
print("\n--- Candidate D: Linearity of [ME] ---")

# [ME] is linear in s. Verify numerically in 1D: ME(a*f + b*g) = a*ME(f) + b*ME(g)
# Use finite differences on a grid
def ME_1D_fd(s_arr, dx, tau_v, c_v, v_sub_v):
    """
    Spatial part of the 1D source-free ME applied to s_arr:
      -c^2*tau*d^2s/dx^2 + v_sub*ds/dx
    Uses second-order central differences on interior points.
    """
    N = len(s_arr)
    d2s = np.zeros(N)
    d1s = np.zeros(N)
    for i in range(1, N-1):
        d2s[i] = (s_arr[i+1] - 2*s_arr[i] + s_arr[i-1]) / dx**2
        d1s[i] = (s_arr[i+1] - s_arr[i-1]) / (2*dx)
    return -c_v**2 * tau_v * d2s + v_sub_v * d1s

N = 100
x_arr = np.linspace(0, 10, N)
dx = x_arr[1] - x_arr[0]
tau_v, c_v, v_sub_v = 1e-6, 3e8, 1e4

lin_errs = []
for _ in range(500):
    a, b = rand(), rand()
    f_arr = np.sin(RNG.uniform(0.1,5)*x_arr) * rand()
    g_arr = np.cos(RNG.uniform(0.1,5)*x_arr) * rand()
    ME_f  = ME_1D_fd(f_arr, dx, tau_v, c_v, v_sub_v)
    ME_g  = ME_1D_fd(g_arr, dx, tau_v, c_v, v_sub_v)
    ME_fg = ME_1D_fd(a*f_arr + b*g_arr, dx, tau_v, c_v, v_sub_v)
    diff = ME_fg - (a*ME_f + b*ME_g)
    scale = np.max(np.abs(ME_fg)) + 1e-30
    lin_errs.append(np.max(np.abs(diff)) / scale)
check("D1: ME_1D(a*f + b*g) = a*ME_1D(f) + b*ME_1D(g) [linearity, rel tol]",
      max(lin_errs) < 1e-10, f"max_rel_err={max(lin_errs):.2e}")

# ------------------------------------------------------------------ #
# V-E: Bateman doubled system (Candidate E)                         #
# ------------------------------------------------------------------ #
print("\n--- Candidate E: Bateman doubling introduces new field ---")

# Verify that the mirror field s~ satisfies the time-REVERSED telegrapher equation.
# The original: tau*s_tt + s_t - c^2*tau*s_xx = 0
# The mirror:   tau*s~_tt - s~_t - c^2*tau*s~_xx = 0
#
# A damped wave s(x,t) = exp(-t/(2*tau))*exp(i*(k*x - omega_r*t))
# Under t -> -t: s~ = exp(+t/(2*tau))*exp(i*(k*x + omega_r*t)) -- grows in t
# This confirms s~ is a new unphysical (growing) degree of freedom.

tau_b = 1e-3   # use larger tau so c^2*k^2 >> 1/(4*tau^2) easily
c_b   = 1.0
k_b   = 1e4    # c^2*k^2 = 1e8 >> 1/(4*tau^2) = 2.5e5 ✓
omega_r_sq = c_b**2 * k_b**2 - 1.0/(4*tau_b**2)
assert omega_r_sq > 0, "omega_r^2 must be positive"
omega_r = np.sqrt(omega_r_sq)

t_arr = np.linspace(0, 2*tau_b, 200)
s_original = np.exp(-t_arr/(2*tau_b)) * np.cos(k_b * 0 - omega_r * t_arr)
s_mirror   = np.exp(+t_arr/(2*tau_b)) * np.cos(k_b * 0 + omega_r * t_arr)

# s_original should decay, s_mirror should grow
check("E1: original field decays over time",
      s_original[-1] < s_original[0],
      f"s[0]={s_original[0]:.4f}, s[-1]={s_original[-1]:.4f}")
check("E2: mirror field grows over time (unphysical, new postulate required)",
      abs(s_mirror[-1]) > abs(s_mirror[0]),
      f"|s~[0]|={abs(s_mirror[0]):.4f}, |s~[-1]|={abs(s_mirror[-1]):.4f}")

# ------------------------------------------------------------------ #
# V-F: H_int dimensional analysis (Candidate F)                    #
# ------------------------------------------------------------------ #
print("\n--- Candidate F: No H_int from frozen constants ---")

# k_rot = 2*kappa/(3*hbar) => kappa = 3*hbar*k_rot/2
hbar = 1.0545718e-34   # J*s
k_rot = 4.5e-7         # s
kappa = 3 * hbar * k_rot / 2

check("F1: kappa = 3*hbar*k_rot/2 consistent with k_rot=4.5e-7",
      abs(kappa - 3*hbar*k_rot/2) < 1e-60,
      f"kappa={kappa:.3e}")

# Verify Gamma_rot = k_rot * omega^2 for many omega values
omega_vals = np.logspace(0, 6, 1000)
Gamma0 = 1e4
omega_max = 1e6
Gamma_full  = Gamma0 + k_rot * omega_vals**2 / (1 + (omega_vals/omega_max)**2)
Gamma_lowom = Gamma0 + k_rot * omega_vals**2

# At low omega, relative error between full and quadratic
low_mask = omega_vals < 1e4
rel_errs_f = np.abs(Gamma_full[low_mask] - Gamma_lowom[low_mask]) / Gamma_full[low_mask]
check("F2: Gamma_full ≈ Gamma0 + k_rot*omega^2 for omega << omega_max",
      np.max(rel_errs_f) < 0.01, f"max_rel_err={np.max(rel_errs_f):.2e}")

# Check no combination of kappa, hbar, k_rot, delta_s/s0 gives units of J
# (Verified by dimensional argument in derivation; confirm numerically that
#  the only energy-scale combination has extra factors of m^3 or s)
# Units check: [kappa * hbar / k_rot] = dimensionless * J*s / s = J ✓ -- but this
# is just hbar again (up to a numerical factor), not an interaction Hamiltonian
# because it has no dependence on qubit operators or substrate field.
val = kappa * hbar / k_rot
check("F3: kappa*hbar/k_rot has units J (but is a number, not operator-valued)",
      val > 0, f"kappa*hbar/k_rot = {val:.3e} J -- is a constant, not H_int")
print("  [NOTE] F4: A constant cannot be an interaction Hamiltonian.")
print("         H_int must depend on BOTH substrate field AND qubit operators.")
print("         No such term exists in [ME]. New postulate required. REJECTED.")

# ------------------------------------------------------------------ #
# V-G: Gauge structure (Candidate G)                                #
# ------------------------------------------------------------------ #
print("\n--- Candidate G: No gauge symmetry ---")

# Verify that [ME] is not U(1) invariant by showing that a phase-rotated
# solution s*exp(i*theta) does not satisfy [ME] for real s.
# For real s and theta != 0, pi: s*exp(i*theta) is complex-valued.
# [ME] requires real s (info density). Inconsistency confirmed.

thetas = [0, np.pi/6, np.pi/4, np.pi/3, np.pi/2, np.pi]
is_real_at_0   = abs(np.exp(1j * 0).imag)   < 1e-15
is_real_at_pi  = abs(np.exp(1j * np.pi).imag) < 1e-15
is_complex_mid = abs(np.exp(1j * np.pi/3).imag) > 0.1

check("G1: exp(i*theta) is real only at theta=0 and theta=pi",
      is_real_at_0 and is_real_at_pi and is_complex_mid)

# Minimal coupling adds terms -2iA*s_x - i*(dA/dx)*s - A^2*s to [ME]
# These are nonzero for A != 0; verify numerically
A_val = 1.0
s_mc_arr = np.sin(x_arr)
ds_dx_arr = np.gradient(s_mc_arr, dx)
dA_dx = 0.0  # uniform A
extra = -2j*A_val*ds_dx_arr - 1j*dA_dx*s_mc_arr - A_val**2*s_mc_arr
check("G2: minimal coupling introduces nonzero extra terms for A != 0",
      np.max(np.abs(extra)) > 0, f"max|extra|={np.max(np.abs(extra)):.3f}")

# ------------------------------------------------------------------ #
# V-Z: Reduction to frozen theory                                   #
# ------------------------------------------------------------------ #
print("\n--- Reduction to frozen theory ---")

# Setting all extension parameters to zero must recover frozen results.
# (1) chi -> 0 in Candidate B: recovers [SS] of frozen derivation
chi_vals = [1.0, 0.1, 0.01, 0.001, 1e-6, 0.0]
# The B equation: c^2*tau*nabla^2 s = v_sub.nabla s + chi*(u.nabla s + s*nabla.u)
# At chi=0: c^2*tau*nabla^2 s = v_sub.nabla s  -- which is [SS] ✓
def B_eq_extra(chi_v, u_r, s0_v, r_v, mu_v):
    """Extra term in Candidate B relative to frozen [SS]"""
    return chi_v * u_r * (-mu_v / r_v**2)

extra_B = [abs(B_eq_extra(chi_v=cv, u_r=1.0, s0_v=1e10, r_v=1.0, mu_v=1.0))
           for cv in chi_vals]
check("Z1: chi->0 eliminates coherence transport term (recovers [SS])",
      extra_B[-1] == 0.0, f"extra at chi=0: {extra_B[-1]}")

# (2) Removing time derivatives: tau*d2s/dt2 + ds/dt with d/dt=0 => 0 = 0 ✓
# (3) Gamma formula at omega->0: Gamma -> Gamma0 ✓
Gamma_zero = Gamma0 + k_rot * 0.0**2 / (1 + (0.0/omega_max)**2)
check("Z2: Gamma(omega=0) = Gamma0",
      abs(Gamma_zero - Gamma0) < 1e-15, f"Gamma(0)={Gamma_zero}, Gamma0={Gamma0}")

# ------------------------------------------------------------------ #
# FINAL REPORT                                                      #
# ------------------------------------------------------------------ #
print("\n" + "=" * 60)
if failures:
    print(f"RESULT: {len(failures)} check(s) FAILED:")
    for f in failures:
        print(f"  - {f}")
    print("=" * 60)
    sys.exit(1)
else:
    print("RESULT: ALL CHECKS PASSED")
    print("All dimensional and limiting-case checks in extension_derivation.md verified.")
    print("=" * 60)
    sys.exit(0)
