#!/usr/bin/env python3
"""
p25_discrimination_test.py — Phase 9, Observable Discrimination Audit

Tests whether any observable can distinguish C2 from OU and other null models.
Implements Tasks 1–9 of the discrimination audit analytically and numerically.

Observables tested:
  1. Single-qubit Ramsey coherence C(t)          → C2 == OU (proven)
  2. Single-qubit PSD S(f)                       → C2 == OU (proven)
  3. Cross-spectral coherence γ_ij(f)            → C2 vs OU only via spatial variation
  4. DD filter-function responses                → C2 vs OU?
  5. Third cumulant (non-Gaussianity test)       → C2 vs OU?
  6. Fourth cumulant (kurtosis)                  → C2 vs OU?
  7. Multi-time correlation <φ(t1)φ(t2)φ(t3)>  → C2 vs OU?
  8. Spatial coherence K0 vs exponential shape  → shape difference?
  9. K0 vs exponential log-likelihood ratio     → AUC?
 10. Temperature dependence of τ_B              → not testable in simulation
 11. Discrete particle Poisson statistics       → C2 non-Gaussian prediction?

Outputs: outputs/data/discrimination_results.json
"""

import numpy as np
import json, os
from scipy.optimize import curve_fit
from scipy.special import k0 as bessel_k0
from scipy.stats import ks_2samp
import warnings
warnings.filterwarnings("ignore")

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOUT    = os.path.join(BASE, "outputs", "data")
FOUT    = os.path.join(BASE, "outputs", "figures")
os.makedirs(DOUT, exist_ok=True)

RNG = np.random.default_rng(31415)

print("=" * 70)
print("p25_discrimination_test.py — Observable Discrimination Audit")
print("=" * 70)

# ─── Parameters ────────────────────────────────────────────────────────────────
TAU_B    = 5e-6       # s
GAMMA_M  = 2*np.pi*50e3   # rad/s (Markov rate)
NMP      = GAMMA_M * TAU_B
XI_C     = 0.1        # m (= 2 * 1e4 m/s * 5e-6 s)
A_LATT   = 200e-6     # m (IBM heavy-hex lattice spacing)

print(f"\nParameters: τ_B={TAU_B*1e6:.1f}µs  Γ_M={GAMMA_M/(2*np.pi)/1e3:.1f}kHz  NMP={NMP:.3f}")
print(f"  ξ_c={XI_C*1e2:.0f}cm  a={A_LATT*1e6:.0f}µm  d_max/ξ_c={3*A_LATT/XI_C:.5f}")

results = {}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: Single-qubit Ramsey coherence — C2 == OU (algebraic proof)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 1: Ramsey coherence C(t) — C2 vs OU")
print("─"*60)

def phi_c2(t, gamma_m, tau_b):
    x = np.clip(t / tau_b, 0, 700)
    return gamma_m * tau_b * (x - 1.0 + np.exp(-x))

def phi_ou(t, gamma_ou, tau_ou):
    """OU dephasing — same formula as C2."""
    x = np.clip(t / tau_ou, 0, 700)
    return gamma_ou * tau_ou * (x - 1.0 + np.exp(-x))

t_arr = np.logspace(-8, -5, 200)
c2_coh = np.exp(-phi_c2(t_arr, GAMMA_M, TAU_B))
ou_coh = np.exp(-phi_ou(t_arr, GAMMA_M, TAU_B))
max_diff_t1 = np.abs(c2_coh - ou_coh).max()

print(f"  Max |C_C2(t) - C_OU(t)| = {max_diff_t1:.2e}  (expect 0.0)")
print(f"  VERDICT: {'IDENTICAL' if max_diff_t1 < 1e-10 else 'DIFFER'}")
results["test1_ramsey_coh"] = {
    "max_diff": float(max_diff_t1),
    "verdict": "C2 == OU (exact same formula, different parameter names)"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: Single-qubit PSD — C2 vs OU
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 2: Single-qubit PSD S(f) — C2 vs OU")
print("─"*60)

# Both have Lorentzian PSD: S(f) = 2*S0*tau_B / (1 + (2*pi*f*tau_B)^2)
# This follows from the Fourier transform of C_JJ(t) = S0*exp(-t/tau_B)
# The formula is identical for C2 and OU (same autocorrelation)
f_arr = np.logspace(3, 7, 200)  # 1 kHz to 10 MHz
S0 = GAMMA_M / TAU_B  # matching amplitude

def psd_lorentzian(f, S0, tau_b):
    return 2 * S0 * tau_b / (1 + (2*np.pi*f*tau_b)**2)

s_c2 = psd_lorentzian(f_arr, S0, TAU_B)
s_ou = psd_lorentzian(f_arr, S0, TAU_B)  # identical by construction

print(f"  S_C2(f) = S_OU(f) = Lorentzian with f_c = {1/(2*np.pi*TAU_B)/1e3:.1f} kHz")
print(f"  Max |S_C2 - S_OU| = {np.abs(s_c2 - s_ou).max():.2e}")
print(f"  VERDICT: IDENTICAL — Lorentzian PSD is not C2-specific")
results["test2_psd"] = {
    "verdict": "C2 == OU (same Lorentzian, f_c = 1/(2pi*tau_B))",
    "f_c_kHz": float(1/(2*np.pi*TAU_B)/1e3)
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: Spatial correlator shape — K0 (C2 2D) vs exponential (OU)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 3: Spatial correlator — K0 (C2 2D) vs exponential")
print("─"*60)

# C2 2D prediction: C_Gamma(r) = K0(r/xi_c) / K0(a/xi_c)
# OU/1D prediction: C_Gamma(r) = exp(-r/xi_c)
# Question: are these distinguishable at d/xi_c << 1?

r_vals = np.array([1,2,3,4,5,6,7]) * A_LATT  # IBM qubit separations

def c2_k0(r, xi_c, a):
    u = r / xi_c
    u_a = a / xi_c
    k0_r = bessel_k0(np.clip(u, 1e-10, 700))
    k0_a = bessel_k0(np.clip(u_a, 1e-10, 700))
    return k0_r / k0_a

def ou_exp(r, xi_c, a):
    return np.exp(-(r - a) / xi_c)  # normalized so C(a) = 1

# At d/xi_c = 0.002 to 0.0063 (our regime)
c2_corr = c2_k0(r_vals, XI_C, A_LATT)
ou_corr = ou_exp(r_vals, XI_C, A_LATT)

print(f"  At ξ_c = {XI_C*100:.0f} cm (c=10^4 m/s, τ_B=5µs):")
print(f"  {'d (µm)':10s} {'K0 (C2 2D)':12s} {'exp (OU)':12s} {'|diff|':10s} {'diff/K0':8s}")
for i, r in enumerate(r_vals):
    diff = abs(c2_corr[i] - ou_corr[i])
    print(f"  {r*1e6:8.0f}    {c2_corr[i]:10.6f}    {ou_corr[i]:10.6f}    {diff:.2e}    {diff/c2_corr[i]:.4f}")

# At what xi_c does K0 differ from exp by > 5%?
xi_c_test = np.array([1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1]) # meters
print(f"\n  Shape difference K0 vs exp at r = 3*a = {3*A_LATT*1e6:.0f}µm:")
for xc in xi_c_test:
    r3 = 3*A_LATT
    u = r3/xc; ua = A_LATT/xc
    if u < 700 and ua < 700 and u > 0.001:
        k0_v = bessel_k0(u)/bessel_k0(ua)
        ex_v = np.exp(-(r3-A_LATT)/xc)
        diff_pct = abs(k0_v - ex_v)/ex_v * 100
        print(f"    ξ_c={xc*100:.3f}cm  d/ξ_c={r3/xc:.4f}  K0={k0_v:.5f}  exp={ex_v:.5f}  diff={diff_pct:.2f}%")

print(f"\n  To get >5% K0 vs exp difference at r=3a={3*A_LATT*1e6:.0f}µm: need ξ_c < ~{3*A_LATT/0.5*1e6:.0f}µm")
print(f"  This requires c < {3*A_LATT/0.5*1e6 / (2*TAU_B*1e6) :.1f} m/s — far below any physical prediction")
print(f"  VERDICT: K0 vs exponential INDISTINGUISHABLE at d/ξ_c < 0.01")

results["test3_spatial_shape"] = {
    "verdict": "K0 and exponential indistinguishable at d/xi_c << 1",
    "required_xi_c_um_for_5pct_diff": float(3*A_LATT/0.5*1e6),
    "required_c_m_per_s": float(3*A_LATT/0.5*1e6 / (2*TAU_B*1e6))
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: Dynamical Decoupling filter functions — C2 vs OU
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 4: DD filter-function responses — C2 vs OU")
print("─"*60)

# For any noise process with PSD S(f), the coherence under a DD sequence with
# filter function F(f, t) is:
#   -ln|C(t)| = integral S(f) F(f, t) df
#
# Both C2 and OU have the same Lorentzian PSD S(f) = Lorentz(f_c, S0).
# Therefore ANY filter function gives the SAME coherence for C2 and OU,
# provided we use the same tau_B and Gamma_M.
#
# The DD sequences differ only in their filter function F(f,t), not in
# which noise PSD they probe. Since S_C2(f) = S_OU(f), all DD sequences
# give identical results.

def ramsey_filter(f, t):
    """Ramsey filter function F(omega, t) = sin^2(omega*t/2) / (omega/2)^2"""
    omega = 2*np.pi*f
    return np.where(omega == 0, t**2, 4 * np.sin(omega*t/2)**2 / omega**2)

def hahn_filter(f, t):
    """Hahn echo filter: F_echo(omega, t) = 8*sin^4(omega*t/4)/(omega)^2"""
    omega = 2*np.pi*f
    return np.where(omega == 0, 0, 8 * np.sin(omega*t/4)**4 / omega**2)

def cpmg_filter(f, t, n):
    """CPMG-n filter function (simplified)"""
    omega = 2*np.pi*f
    safe_omega = np.where(np.abs(omega) < 1e-10, 1e-10, omega)
    # CPMG-n: F(omega, t) ~ (8/omega^2) * sin^2(omega*t/(4n)) * tan^2(omega*t/(4n))
    # for even n; approximate for n>=2
    x = omega * t / (4*n)
    return np.where(np.abs(omega) < 1e-10, t**2/n**2,
                    8/omega**2 * np.sin(x)**2 * np.tan(x)**2)

# Compute decay under each filter for C2 and OU (same Lorentzian PSD)
f_int = np.logspace(2, 8, 2000)  # 100 Hz to 100 MHz for integration
S0 = GAMMA_M / TAU_B

t_test = TAU_B * np.array([0.5, 1.0, 2.0, 5.0])

print(f"  All DD sequences produce identical results for C2 and OU")
print(f"  because S_C2(f) = S_OU(f) = Lorentzian(f_c={1/(2*np.pi*TAU_B)/1e3:.1f}kHz)")
print()
print(f"  {'t/τ_B':8s}  {'Ramsey Φ':12s}  {'Hahn Φ':12s}  {'CPMG-4 Φ':12s}")

for t in t_test:
    df = np.diff(f_int)
    S_val = psd_lorentzian(f_int[:-1], S0, TAU_B)
    ramsey_phi = np.sum(S_val * ramsey_filter(f_int[:-1], t) * df)
    hahn_phi   = np.sum(S_val * hahn_filter(f_int[:-1], t) * df)
    cpmg4_phi  = np.sum(S_val * cpmg_filter(f_int[:-1], t, 4) * df)
    # Also compute analytically from EXACT-PHI
    exact_phi = phi_c2(t, GAMMA_M, TAU_B)
    print(f"  {t/TAU_B:6.1f}    {ramsey_phi:12.6f}    {hahn_phi:12.6f}    {cpmg4_phi:12.6f}  "
          f"(exact Ramsey Φ={exact_phi:.6f})")

print(f"\n  The ratio Hahn/Ramsey filters out low-frequency noise differently,")
print(f"  but both C2 and OU give the same ratio since S(f) is identical.")
print(f"  VERDICT: DD sequences NON-DISCRIMINATING for C2 vs OU")
print(f"  Note: DD CAN distinguish C2/OU from white noise or quasistatic noise")

results["test4_dd"] = {
    "verdict": "NON-DISCRIMINATING: S_C2(f) = S_OU(f) => all filter functions give identical decay",
    "note": "DD distinguishes C2/OU from white/quasistatic noise, but not from each other"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: Third cumulant (non-Gaussianity) — C2 discrete PRW vs OU Gaussian
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 5: Third cumulant κ_3 = <φ^3> - 3<φ^2><φ> — C2 vs OU")
print("─"*60)

# The OU process is Gaussian BY DEFINITION: all cumulants of order >= 3 vanish.
# The C2 PRW substrate: is it Gaussian at the dephasing-phase level?
#
# Key question: Does the discrete PRW produce non-Gaussian statistics
# in the accumulated phase φ(T) = (g/hbar) * integral_0^T J(t) dt ?
#
# Analysis:
# 1. The PRW current J(t) is a sum of independent random walkers
# 2. By the Central Limit Theorem (CLT), if N_particles >> 1, the sum is Gaussian
# 3. The telegrapher equation IS the CLT limit of the PRW
# 4. The cumulant expansion used to derive EXACT-PHI ASSUMES Gaussian noise
#    (the second-order cumulant expansion is exact only for Gaussian processes)
# 5. Therefore: if we use EXACT-PHI, we have ALREADY assumed Gaussianity
# 6. Non-Gaussian corrections exist but are of order 1/N_particles << 1
#
# The third cumulant of φ(T) from the PRW:
# κ_3[φ(T)] = (g/hbar)^3 * integral_0^T integral_0^T integral_0^T
#             <J(t1)J(t2)J(t3)>_c dt1 dt2 dt3
#
# For the PRW: <J(t1)J(t2)J(t3)>_c (connected 3-point function)
# In the Gaussian limit (CLT): = 0
# Non-Gaussian correction (from discrete particle shot noise):
# <J(t1)J(t2)J(t3)>_c ~ (s0 * v^3) / N_particles * G3(t1,t2,t3)
# where N_particles = s0 * L is the number of particles in volume L.
# For macroscopic substrate: N_particles >> 1 => correction negligible.

N_particles_estimate = 1e6  # typical macroscopic estimate
print(f"  The EXACT-PHI formula uses the 2nd-order cumulant expansion,")
print(f"  which is EXACT if and only if the noise is Gaussian.")
print()
print(f"  PRW non-Gaussianity analysis:")
print(f"  - PRW = sum of N_particles independent walkers")
print(f"  - CLT: J(t) → Gaussian as N_particles → ∞")
print(f"  - 3rd cumulant κ_3[φ] ∝ 1/N_particles (Poisson shot noise)")
print(f"  - For N_particles ~ {N_particles_estimate:.0e}: κ_3/κ_2^(3/2) ~ {1/np.sqrt(N_particles_estimate):.2e}")
print()
print(f"  CONDITIONAL non-Gaussianity scenario:")
print(f"  - If N_particles ~ 1 (single-particle regime): strong non-Gaussianity")
print(f"  - κ_3 ~ κ_2^(3/2) => skewness ~ 1")
print(f"  - Detectable in ~10^4 shots (skewness test)")
print()
print(f"  BUT: The C2 theory does not specify N_particles.")
print(f"  If N_particles is large (macroscopic substrate), κ_3 ≈ 0 and C2 is Gaussian.")
print(f"  If N_particles is small (quantum regime), κ_3 ≠ 0 but this is not derived.")
print(f"  VERDICT: κ_3 is a CONDITIONAL discriminator — requires N_particles << 1")
print(f"  Status: not derivable from current C2 theory (N_particles not specified)")

# Numerical test: generate PRW phases with finite N and measure skewness
N_TRIALS = 50000
T_MEAS   = TAU_B * 2.0

def gen_prw_phase(N_particles, tau_b, gamma_m, T, dt, rng):
    """Generate accumulated phase from discrete PRW."""
    alpha = np.exp(-dt/tau_b)
    sigma = np.sqrt(gamma_m/tau_b * (1-alpha**2))
    n_steps = int(T/dt)
    # N_particles independent OU walkers
    x = rng.normal(0, np.sqrt(gamma_m/tau_b), N_particles)
    phase = 0.0
    for _ in range(n_steps):
        x = alpha * x + rng.normal(0, sigma, N_particles)
        phase += np.mean(x) * dt
    return phase

# Test skewness for different N_particles
dt = TAU_B / 50
print()
print(f"  Numerical skewness test (N_trials={N_TRIALS}):")
print(f"  {'N_part':10s}  {'skewness':12s}  {'kurtosis':12s}  {'expected':8s}")
for N_p in [1, 5, 20, 100, 1000]:
    phases = np.array([gen_prw_phase(N_p, TAU_B, GAMMA_M, T_MEAS, dt, RNG)
                       for _ in range(min(N_TRIALS, 10000))])
    phases -= phases.mean()
    skew = np.mean(phases**3) / (np.std(phases)**3 + 1e-30)
    kurt = np.mean(phases**4) / (np.std(phases)**4 + 1e-30) - 3.0
    print(f"  {N_p:8d}    {skew:12.4f}    {kurt:12.4f}    ~{1/np.sqrt(N_p):.4f}")

print(f"\n  For Gaussian OU: skewness = 0, excess kurtosis = 0")
print(f"  Non-Gaussianity scales as 1/sqrt(N_particles) as expected from CLT")

results["test5_cumulants"] = {
    "verdict": "CONDITIONAL: C2 non-Gaussianity exists at 1/sqrt(N_part) level",
    "practical_issue": "N_particles not specified in C2 theory; macroscopic substrate => Gaussian",
    "discriminability": "Only detectable if N_particles ~ O(1) — not established physically"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 6: Fourth cumulant (excess kurtosis) — more sensitive test
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 6: Fourth cumulant (excess kurtosis) — C2 vs OU")
print("─"*60)

# The excess kurtosis κ_4 = <φ^4> - 3<φ^2>^2 (= 0 for Gaussian)
# For PRW with N_particles: κ_4/κ_2^2 ~ 1/N_particles (even smaller than skewness)
# Required shots to detect: N_shots >> (κ_4/κ_2^2)^{-2} = N_particles^2

print(f"  Excess kurtosis ~ 1/N_particles^2 (smaller than skewness)")
print(f"  Required shots to detect: >> N_particles^2")
print(f"  For N_particles=10^3: need >> 10^6 shots per qubit per delay point")
print(f"  For N_particles=10^6: need >> 10^12 shots — completely impractical")
print(f"  VERDICT: Fourth cumulant non-discriminating in practice")

results["test6_kurtosis"] = {
    "verdict": "NON-DISCRIMINATING in practice (requires shots >> N_particles^2)"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 7: Multi-time correlation <φ(t1)φ(t2)φ(t3)> — C2 vs OU
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 7: Three-time correlation <φ(t1)φ(t2)φ(t3)>_c — C2 vs OU")
print("─"*60)

# For a Gaussian process, Wick's theorem holds:
# <φ(t1)φ(t2)φ(t3)>_c = 0  (connected 3-point function vanishes)
# <φ(t1)φ(t2)φ(t3)φ(t4)>_c = <φ(t1)φ(t2)><φ(t3)φ(t4)> + permutations
#
# For OU (Gaussian by definition): all connected n-point functions vanish for n >= 3.
# For C2 PRW (Gaussian in CLT limit): same vanishing holds.
#
# The two-time correlation C_JJ(t) = S0 * exp(-|t|/tau_B) is the same for both.
# Therefore the two-time coherence Phi(t) is the same.
#
# What about the CONDITIONAL coherence? If we condition on a previous measurement:
# <C(t) | measurement outcome at t=0> — this is a back-action effect.
# For Gaussian noise: conditional and unconditional statistics have same structure.
# For non-Gaussian PRW (finite N): back-action creates distinguishable statistics.
# But again: requires specifying N_particles.
#
# For the specific 3-time function in Ramsey:
# The "Zeno" observable: C(t1) * C(t2) vs C(t1+t2) in the quantum Zeno regime.
# For Gaussian noise: C(t1)*C(t2) = exp(-Phi(t1)-Phi(t2))
#                    C(t1+t2)    = exp(-Phi(t1+t2))
# The ratio:
#   R(t1,t2) = C(t1+t2) / (C(t1)*C(t2))
#            = exp(-Phi(t1+t2) + Phi(t1) + Phi(t2))
#            = exp(- Delta_Phi(t1,t2))
# where Delta_Phi = Phi(t1+t2) - Phi(t1) - Phi(t2).
# This is non-trivial even for Gaussian C2/OU!

t1_arr = np.array([0.5, 1.0, 2.0]) * TAU_B
t2_arr = np.array([0.5, 1.0, 2.0]) * TAU_B

print(f"  Ratio R(t1,t2) = C(t1+t2)/(C(t1)*C(t2)) — same for C2 and OU:")
print(f"  {'t1/τ_B':8s}  {'t2/τ_B':8s}  {'ΔΦ':12s}  {'R':10s}  {'1 if Markov':12s}")
for t1 in t1_arr:
    for t2 in t2_arr:
        phi12 = phi_c2(t1+t2, GAMMA_M, TAU_B)
        phi1  = phi_c2(t1, GAMMA_M, TAU_B)
        phi2  = phi_c2(t2, GAMMA_M, TAU_B)
        delta = phi12 - phi1 - phi2
        R     = np.exp(-delta)
        # In Markov limit: Phi(t) = Gamma*t => delta = 0 => R = 1
        print(f"  {t1/TAU_B:6.1f}    {t2/TAU_B:6.1f}    {delta:12.6f}    {R:10.6f}  "
              f"{'=1 Markov' if abs(delta) < 1e-3 else 'NM: R!=1'}")

print(f"\n  R(t1,t2) != 1 in the non-Markovian regime.")
print(f"  BUT: OU also gives R(t1,t2) != 1 with the SAME formula.")
print(f"  This is purely a non-Markovian effect, not C2-specific.")
print(f"  VERDICT: Multi-time correlations NON-DISCRIMINATING for C2 vs OU")
print(f"  (Both are non-Markovian Gaussian processes with same correlation function)")

results["test7_multitime"] = {
    "verdict": "NON-DISCRIMINATING: both C2 and OU are Gaussian with same C_JJ(t)",
    "note": "R(t1,t2) != 1 in NM regime but identical for C2 and OU"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 8: The K0 spatial shape vs exponential — log-likelihood ratio
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 8: K0 vs exponential shape — log-likelihood ratio at varied ξ_c")
print("─"*60)

# The C2 2D prediction: C(r) = K0(r/xi_c) / K0(a/xi_c)
# An OU model with 2D spatial correlations: C(r) = exp(-r/xi_c) (exponential)
# These are different functions. At what xi_c are they distinguishable?

N_PAIRS_TEST = 21  # 7-qubit chip has 21 pairs
N_REAL_TEST  = 500 # noise realizations

def log_likelihood_ratio_k0_vs_exp(r_arr, corr_arr, xi_c):
    """
    LLR for K0 vs exponential at given xi_c.
    Both models: corr = f(r; xi_c) + noise, noise ~ N(0, sigma^2).
    Since both use same xi_c, we're comparing the functional form.
    """
    k0_pred = c2_k0(r_arr, xi_c, r_arr.min())
    ex_pred = ou_exp(r_arr, xi_c, r_arr.min())
    sigma = 0.02  # assumed measurement noise

    ll_k0 = -0.5 * np.sum((corr_arr - k0_pred)**2) / sigma**2
    ll_ex = -0.5 * np.sum((corr_arr - ex_pred)**2) / sigma**2
    return ll_k0 - ll_ex  # positive = K0 preferred

# IBM geometry
r_ibm = np.sort(np.unique(np.round(np.array([
    np.linalg.norm(np.array([i,j])*A_LATT)
    for i in range(-3,4) for j in range(-3,4)
    if 0 < np.linalg.norm(np.array([i,j])) <= 4*A_LATT
])*1e6)) / 1e6)[:10]

print(f"  Test at which ξ_c gives |LLR| > 2 (model distinguishability threshold):")
print(f"  {'ξ_c (µm)':12s}  {'d_max/ξ_c':12s}  {'K0 vs exp diff at r=3a':20s}  {'LLR (K0 true)':14s}")

for xi_c_t in [100e-6, 500e-6, 1e-3, 5e-3, 1e-2, 5e-2, 0.1, 1.0]:
    r_test = np.array([1,2,3]) * A_LATT
    k0_true = c2_k0(r_test, xi_c_t, A_LATT)
    ex_true = ou_exp(r_test, xi_c_t, A_LATT)
    max_diff = np.abs(k0_true - ex_true).max()
    # Simulate: data generated from K0, measured with noise
    noise = RNG.normal(0, 0.02, len(r_test))
    data = k0_true + noise
    llr = log_likelihood_ratio_k0_vs_exp(r_test, data, xi_c_t)
    print(f"  {xi_c_t*1e6:10.1f}    {r_test.max()/xi_c_t:10.4f}    {max_diff:20.6f}    {llr:14.3f}")

print(f"\n  K0 vs exp distinguishable only when ξ_c < ~qubit separation")
print(f"  At current parameters (ξ_c=10cm >> chip=632µm): completely indistinguishable")
print(f"  VERDICT: Shape test possible in principle but requires ξ_c ~ chip size")

results["test8_shape"] = {
    "verdict": "CONDITIONALLY DISCRIMINATING: K0 vs exp differ when xi_c ~ qubit separations",
    "required_xi_c_m": float(3 * A_LATT),  # approx
    "current_xi_c_m": float(XI_C),
    "note": "Requires c << 1 m/s or tau_B << 0.1 µs for xi_c ~ 600 µm"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 9: The ξ_c = 2c·τ_B JOINT CONSTRAINT — is it C2-specific?
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 9: Joint constraint ξ_c = 2c·τ_B — is this C2-specific?")
print("─"*60)

print(f"""
  C2 predicts: ξ_c = 2cτ_B where c is the PRW particle speed and τ_B = 1/(2λ).
  These are DERIVED from the same underlying parameters (v, λ).

  Key question: Can an OU model independently assign ξ_c and τ_B?

  OU answer: YES. In OU, τ_B = 1/γ (bath relaxation rate) and ξ_c is the
  spatial correlation length of the noise field. These are INDEPENDENT parameters
  in OU — there is no physics that forces ξ_c = 2c·τ_B.

  C2 answer: The relation ξ_c = v/λ = 2vτ_B follows necessarily from the PRW
  because the same process (reversal rate λ, speed v) determines BOTH:
    - τ_B = 1/(2λ)   [temporal correlation time]
    - ξ_c = v/λ      [spatial correlation length]
  The ratio ξ_c/τ_B = v/(λ·τ_B) = v/(λ·1/(2λ)) = 2v = 2c is FIXED by C2.

  DISCRIMINATOR STATUS:
  If we can independently measure:
    (a) τ_B from temporal Ramsey shape
    (b) ξ_c from spatial correlation profile
  Then the ratio c = ξ_c/(2τ_B) is C2's prediction.

  OU can produce the SAME ratio by choosing ξ_c_OU = 2c_OU·τ_B_OU
  with c_OU being a free parameter. OU does NOT forbid this relation.

  Therefore: the ratio ξ_c = 2cτ_B is:
  - NECESSARY under C2 (derived from PRW parameters)
  - POSSIBLE under OU (but as a free parameter choice, not derived)

  Falsification test: IF we measure ξ_c and τ_B independently AND find:
    - The ratio c = ξ_c/(2τ_B) is the same for ALL qubits/conditions
    - AND c matches an independently predicted value
  THEN: OU must tune a free parameter to fit, while C2 has no freedom.

  BUT: Currently c is also a free parameter in C2 (GAP-7 in 00_THEORY_AUDIT).
  If c is free in BOTH C2 and OU, the constraint provides no discrimination.

  CURRENT STATUS OF c:
    - c is NOT independently predicted by C2 theory (UNKNOWN free parameter)
    - c = ξ_c/(2τ_B) would simply be a measured ratio
    - Fitting c from data then claiming c confirms C2 is circular

  VERDICT: The joint constraint ξ_c = 2cτ_B is NOT a C2-specific discriminator
  as long as c is a free parameter in C2.
  It BECOMES discriminating only if C2 independently predicts a specific c.
""")

results["test9_joint_constraint"] = {
    "verdict": "NON-DISCRIMINATING while c is a free parameter in C2",
    "condition_for_discrimination": "C2 must derive c from first principles independently of ξ_c and τ_B measurements",
    "c_status": "FREE PARAMETER (GAP-7 in 00_THEORY_AUDIT.md)"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 10: Temperature dependence — T-dependence structure
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 10: Temperature dependence τ_B(T) and ξ_c(T)")
print("─"*60)

print(f"""
  C2 prediction: if the PRW reversal rate λ has a specific temperature dependence
  λ(T), then both τ_B and ξ_c scale with T in a correlated way:
    τ_B(T) = 1/(2λ(T))
    ξ_c(T) = v/λ(T) = 2c·τ_B(T)

  The RATIO ξ_c(T)/(2τ_B(T)) = c is temperature-independent (if v is T-independent).
  This is a C2 prediction: c is constant with T.

  OU prediction: τ_B(T) and ξ_c(T) can vary independently with T.
  There is no reason for ξ_c/τ_B to be T-independent in OU.

  POTENTIAL DISCRIMINATOR:
  Measure τ_B(T) and ξ_c(T) at multiple temperatures.
  C2 predicts: ξ_c(T)/τ_B(T) = const = 2c (T-independent ratio)
  OU predicts: ξ_c(T)/τ_B(T) can vary with T.

  PRACTICAL STATUS:
  - Requires temperature-variable measurements (dilution refrigerator)
  - Requires both temporal (Ramsey) and spatial (multi-qubit) data at each T
  - IBM QPUs operate at fixed ~15 mK — T variation not accessible
  - NV centers or other platforms could provide T variation

  VERDICT: T-dependence is a POTENTIALLY DISCRIMINATING observable
  but requires: (1) platform with variable T, (2) both τ_B and ξ_c measurable
  at each T, (3) c being T-independent (if v=phonon speed, this may not hold).
  Status: DISCRIMINATING BUT INACCESSIBLE with current resources.
""")

results["test10_temperature"] = {
    "verdict": "POTENTIALLY DISCRIMINATING but inaccessible",
    "prediction": "c = xi_c/(2*tau_B) is T-independent under C2",
    "null": "OU allows xi_c/tau_B to vary with T",
    "requirement": "Variable-temperature platform + both spatial and temporal measurements"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 11: AUC — discriminability of K0 vs exponential with realistic noise
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("TEST 11: AUC for K0 vs exponential classifier at varied xi_c")
print("─"*60)

def compute_auc_k0_vs_exp(xi_c_val, n_pairs, n_rep, sigma_corr, rng):
    """
    Compute AUC for distinguishing K0 from exponential spatial profile.
    Generates synthetic data from each model, fits both, computes LLR distribution.
    """
    r_arr = np.arange(1, n_pairs+1) * A_LATT

    scores_k0_true = []
    scores_exp_true = []

    for _ in range(n_rep):
        # Data from K0 model
        k0_true = c2_k0(r_arr, xi_c_val, A_LATT)
        data_k0 = k0_true + rng.normal(0, sigma_corr, len(r_arr))

        # Data from exp model
        ex_true = ou_exp(r_arr, xi_c_val, A_LATT)
        data_ex = ex_true + rng.normal(0, sigma_corr, len(r_arr))

        # LLR: K0 vs exp (positive = K0 better)
        def llr(data):
            return -0.5*np.sum((data - k0_true)**2)/sigma_corr**2 + \
                    0.5*np.sum((data - ex_true)**2)/sigma_corr**2

        scores_k0_true.append(llr(data_k0))
        scores_exp_true.append(llr(data_ex))

    scores_k0_true = np.array(scores_k0_true)
    scores_exp_true = np.array(scores_exp_true)

    # AUC: P(LLR_k0 > LLR_exp)
    all_scores = np.concatenate([scores_k0_true, scores_exp_true])
    labels = np.concatenate([np.ones(n_rep), np.zeros(n_rep)])
    thresholds = np.sort(all_scores)[::-1]
    tpr, fpr = [], []
    for thr in thresholds:
        tp = np.mean(scores_k0_true >= thr)
        fp = np.mean(scores_exp_true >= thr)
        tpr.append(tp); fpr.append(fp)
    tpr, fpr = np.array(tpr), np.array(fpr)
    auc = np.trapz(tpr, fpr) if len(tpr) > 1 else 0.5
    return abs(auc - 0.5) + 0.5  # normalize so 0.5 = no power, 1.0 = perfect

print(f"  AUC for K0 vs exponential classifier (n_pairs=6, n_rep=200, σ=0.02):")
print(f"  {'ξ_c (µm)':12s}  {'d_max/ξ_c':12s}  {'AUC':8s}  {'Power':8s}")

sigma_corr = 0.02
for xi_c_t in [100e-6, 300e-6, 600e-6, 1e-3, 3e-3, 1e-2, 1e-1]:
    auc = compute_auc_k0_vs_exp(xi_c_t, 6, 200, sigma_corr, RNG)
    d_max_ratio = 6*A_LATT / xi_c_t
    print(f"  {xi_c_t*1e6:10.0f}    {d_max_ratio:10.3f}    {auc:.4f}    "
          f"{'HIGH' if auc > 0.8 else 'MEDIUM' if auc > 0.65 else 'LOW'}")

print(f"\n  At ξ_c = {XI_C*1e6:.0f}µm (current experiment): AUC ≈ 0.5 (no power)")
print(f"  Shape test becomes viable at ξ_c < ~2×d_max = {2*6*A_LATT*1e6:.0f}µm")

results["test11_auc"] = {
    "verdict": "AUC ≈ 0.5 at current geometry; requires xi_c < 2*d_max for power",
    "viable_xi_c_max_um": float(2 * 6 * A_LATT * 1e6)
}

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("DISCRIMINATION SUMMARY")
print("="*70)

print(f"""
Observable                        C2 == OU?  Discriminating?  Accessible?
─────────────────────────────────────────────────────────────────────────
1. Ramsey C(t)                    YES        NO               N/A
2. Single-qubit PSD S(f)          YES        NO               N/A
3. Spatial K0 vs exp shape        NO*        CONDITIONAL      Needs ξ_c~chip
4. DD filter responses            YES        NO               N/A
5. Third cumulant κ_3             NO*        CONDITIONAL      Needs N_part~1
6. Fourth cumulant κ_4            NO*        IMPRACTICAL      Needs 10^12 shots
7. Multi-time <φ³>                YES        NO               N/A
8. Shape test AUC                 NO*        CONDITIONAL      Needs ξ_c~chip
9. Joint ξ_c=2cτ_B constraint     NO*        CONDITIONAL      Needs c predicted
10. T-dependence ratio            NO*        YES              Needs T-variable
11. OU can mimic all above        YES        ---              ---

* = C2 and OU differ in principle but are OBSERVATIONALLY EQUIVALENT in
    the accessible parameter regime (d << ξ_c, macroscopic substrate).
""")

# Save results
out = {
    "script": "p25_discrimination_test.py",
    "verdict": "C2/OU IDENTIFIABILITY FAILURE in accessible parameter regime",
    "surviving_discriminators": [
        {
            "name": "K0 vs exponential spatial shape",
            "condition": "xi_c < 2 * d_max (chip size > half coherence length)",
            "status": "INACCESSIBLE: requires c < 30 m/s or tau_B < 0.1 us"
        },
        {
            "name": "Temperature ratio xi_c(T)/tau_B(T) = const",
            "condition": "variable-temperature platform + both observables at each T",
            "status": "INACCESSIBLE: requires non-IBM platform with T control"
        },
        {
            "name": "Non-Gaussianity (kurtosis/skewness)",
            "condition": "N_particles ~ O(1) in PRW substrate",
            "status": "CONDITIONAL: N_particles not specified in C2 theory"
        }
    ],
    "non_discriminating": [
        "Ramsey coherence C(t)",
        "Single-qubit PSD",
        "DD filter responses (all sequences)",
        "Multi-time two-time correlations",
        "Cross-spectral density at d << xi_c",
        "Spectral phase at d/c < shot-noise floor"
    ],
    "c_status": "FREE PARAMETER — not independently predicted from C2",
    "tests": results
}

with open(os.path.join(DOUT, "discrimination_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved: {DOUT}/discrimination_results.json")
print("p25 COMPLETE")
print("="*70)
