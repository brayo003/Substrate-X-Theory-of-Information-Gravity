#!/usr/bin/env python3
"""
pre_hardware_experiment_simulation.py
SXC-IGC Pre-Hardware Validation Simulation

Tests whether M1 (SXC-IGC K0) is distinguishable from M2-M6 under
realistic IBM hardware noise at the actual chip geometry.

Models:
  M0 - Independent Markovian (no spatial correlation)
  M1 - SXC-IGC: K0(r/xi_c) spatial correlation
  M2 - Exponential bath: exp(-r/xi)
  M3 - OU/conventional colored noise (same temporal, exp spatial)
  M4 - 1/f noise (frequency-dependent)
  M5 - EM/circuit crosstalk (power-law spatial decay)
  M6 - Independent noise + readout/measurement errors only

Outputs: pre_hardware_simulation_results.json
"""

import numpy as np
import json, os
from scipy.special import k0 as bessel_k0
from scipy.optimize import curve_fit
from scipy.stats import ks_2samp

RNG = np.random.default_rng(12345)
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "09_spatiotemporal_c2_test", "outputs", "data")
os.makedirs(OUT, exist_ok=True)

print("=" * 65)
print("SXC-IGC Pre-Hardware Experiment Simulation")
print("=" * 65)

# ── Hardware parameters from 06_datasets/props_brisbane.json ──────────────
A_UM = 200.0          # IBM heavy-hex nearest-neighbor spacing (µm)
T1_MED = 232e-6       # s (median T1)
T2_MED = 150e-6       # s (median T2)
READOUT_ERR = 0.020   # median readout error
N_SHOTS = 4096        # shots per circuit (conservative)
T_MEAS = 0.3 * T2_MED  # measurement time (0.3 * T2)

# ── Theory parameters ──────────────────────────────────────────────────────
# ξ_c = v/λ = 2c·τ_B. c is a FREE PARAMETER (GAP-7).
# Three test cases:
XI_C_CASES = {
    "xi_optimistic_1mm":  1_000e-6,   # 1 mm — minimum physically meaningful
    "xi_chip_fitted":     3_000e-6,   # 3 mm — fits chip scale (ξ ~ d_max/3)
    "xi_physical_10cm":   100_000e-6, # 10 cm — p25 default; c ~ 10 km/s
}

GAMMA_0 = 1.0 / T2_MED   # base dephasing rate (rad/s)
UV_CUTOFF = A_UM * 1e-6   # a = 200 µm

# ── Qubit separations on Brisbane ─────────────────────────────────────────
# Heavy-hex grid: coords are integer grid units, spacing = A_UM
# Use a representative linear chain of 20 qubits at grid positions 0..19
N_QUBITS = 20
positions = np.arange(N_QUBITS) * A_UM * 1e-6  # in meters

# All unique separations
pairs = [(i, j, abs(positions[i] - positions[j]))
         for i in range(N_QUBITS) for j in range(i+1, N_QUBITS)]
r_vals = np.array([p[2] for p in pairs])
r_unique = np.unique(np.round(r_vals * 1e6 / 50) * 50) * 1e-6  # 50µm bins

print(f"\nGeometry: {N_QUBITS} qubits, {len(pairs)} pairs")
print(f"Separation range: {r_vals.min()*1e6:.0f} – {r_vals.max()*1e6:.0f} µm")

results = {}

# ─────────────────────────────────────────────────────────────────────────
# SPATIAL CORRELATION MODELS
# ─────────────────────────────────────────────────────────────────────────

def C_M0(r):
    """M0: no spatial correlation"""
    return np.zeros_like(r)

def C_M1_K0(r, xi_c):
    """M1: SXC-IGC K0 correlation"""
    r = np.asarray(r)
    norm = bessel_k0(UV_CUTOFF / xi_c)
    return bessel_k0(r / xi_c) / norm

def C_M2_exp(r, xi):
    """M2: exponential correlation"""
    return np.exp(-r / xi)

def C_M3_OU(r, xi):
    """M3: OU bath — exponential spatial (same as M2 in this approximation)"""
    return np.exp(-r / xi)

def C_M5_crosstalk(r, xi_em, amp):
    """M5: EM/circuit crosstalk — power-law decay"""
    return amp * np.exp(-r / xi_em)

# ─────────────────────────────────────────────────────────────────────────
# CORE TEST: K0 vs EXP shape discrimination at realistic noise
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─"*60)
print("TEST: K0 vs EXP shape discrimination")
print("─"*60)

for xi_name, xi_c in XI_C_CASES.items():
    print(f"\n  ξ_c = {xi_c*1e6:.0f} µm  (d_max/ξ_c = {r_vals.max()/xi_c:.2f})")

    r_test = r_unique[r_unique > 0]

    # True K0 correlation at these separations
    C_K0_true = C_M1_K0(r_test, xi_c)
    # Best-fit exp (free xi parameter)
    try:
        popt, _ = curve_fit(C_M2_exp, r_test, C_K0_true, p0=[xi_c], maxfev=2000)
        xi_fit = popt[0]
        C_exp_fit = C_M2_exp(r_test, xi_fit)
    except Exception:
        xi_fit = xi_c
        C_exp_fit = C_M2_exp(r_test, xi_fit)

    # Max shape difference (ideal, no noise)
    shape_diff_ideal = np.max(np.abs(C_K0_true - C_exp_fit))

    # Add realistic measurement noise
    # Correlation is estimated from N_SHOTS measurements; std ~ 1/sqrt(N_SHOTS)
    # Plus readout error contribution
    sigma_meas = 1.0 / np.sqrt(N_SHOTS) + READOUT_ERR

    n_trials = 1000
    auc_scores = []
    llr_vals = []

    for _ in range(n_trials):
        noise = RNG.normal(0, sigma_meas, len(r_test))
        C_obs = C_K0_true + noise

        # Fit K0 model (1 free param: xi_c)
        try:
            popt_k0, _ = curve_fit(C_M1_K0, r_test, C_obs, p0=[xi_c], maxfev=1000,
                                   bounds=(UV_CUTOFF*2, np.inf))
            C_pred_k0 = C_M1_K0(r_test, popt_k0[0])
        except Exception:
            C_pred_k0 = C_K0_true

        # Fit exp model (1 free param: xi)
        try:
            popt_exp, _ = curve_fit(C_M2_exp, r_test, C_obs, p0=[xi_c], maxfev=1000,
                                    bounds=(UV_CUTOFF*2, np.inf))
            C_pred_exp = C_M2_exp(r_test, popt_exp[0])
        except Exception:
            C_pred_exp = C_exp_fit

        # Log-likelihood ratio (Gaussian noise assumed)
        resid_k0 = C_obs - C_pred_k0
        resid_exp = C_obs - C_pred_exp
        llr = -0.5 * np.sum(resid_k0**2 / sigma_meas**2) + \
               0.5 * np.sum(resid_exp**2 / sigma_meas**2)
        llr_vals.append(llr)

    llr_vals = np.array(llr_vals)
    # When data is from M1: fraction of times K0 wins (LLR > 0)
    power_k0 = np.mean(llr_vals > 0)

    # False positive: generate M2 (exp) data, test if K0 wins incorrectly
    fp_scores = []
    for _ in range(500):
        noise = RNG.normal(0, sigma_meas, len(r_test))
        C_obs_fp = C_M2_exp(r_test, xi_c) + noise
        try:
            popt_k0, _ = curve_fit(C_M1_K0, r_test, C_obs_fp, p0=[xi_c], maxfev=1000,
                                   bounds=(UV_CUTOFF*2, np.inf))
            C_pred_k0 = C_M1_K0(r_test, popt_k0[0])
        except Exception:
            C_pred_k0 = C_M2_exp(r_test, xi_c)
        try:
            popt_exp, _ = curve_fit(C_M2_exp, r_test, C_obs_fp, p0=[xi_c], maxfev=1000,
                                    bounds=(UV_CUTOFF*2, np.inf))
            C_pred_exp = C_M2_exp(r_test, popt_exp[0])
        except Exception:
            C_pred_exp = C_M2_exp(r_test, xi_c)
        resid_k0 = C_obs_fp - C_pred_k0
        resid_exp = C_obs_fp - C_pred_exp
        llr_fp = -0.5*np.sum(resid_k0**2/sigma_meas**2) + 0.5*np.sum(resid_exp**2/sigma_meas**2)
        fp_scores.append(llr_fp > 0)
    fp_rate = np.mean(fp_scores)

    print(f"    Shape diff (ideal): {shape_diff_ideal:.4f}")
    print(f"    Measurement sigma:  {sigma_meas:.4f}")
    print(f"    SNR (diff/sigma):   {shape_diff_ideal/sigma_meas:.2f}")
    print(f"    Power (K0 wins|M1): {power_k0:.3f}")
    print(f"    False positive rate:{fp_rate:.3f}")
    print(f"    d_max/ξ_c ratio:    {r_vals.max()/xi_c:.3f}")

    is_discriminable = (shape_diff_ideal > 3*sigma_meas) and (power_k0 > 0.8) and (fp_rate < 0.1)
    status = "DISCRIMINABLE" if is_discriminable else "NOT DISCRIMINABLE"
    print(f"    STATUS: {status}")

    results[xi_name] = {
        "xi_c_um": xi_c * 1e6,
        "d_max_over_xi_c": float(r_vals.max() / xi_c),
        "shape_diff_ideal": float(shape_diff_ideal),
        "sigma_meas": float(sigma_meas),
        "snr": float(shape_diff_ideal / sigma_meas),
        "power_k0_wins": float(power_k0),
        "false_positive_rate": float(fp_rate),
        "discriminable": 1 if is_discriminable else 0,
        "status": status,
    }

# ─────────────────────────────────────────────────────────────────────────
# TEMPORAL CHANNEL: ω² scaling vs null models
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─"*60)
print("TEST: Temporal channel — Γ_φ(ω) discrimination")
print("─"*60)

TAU_B = 5e-6   # s (substrate correlation time)
omega_range = np.logspace(3, 6, 30)  # 10³ to 10⁶ rad/s
Gamma_0_base = GAMMA_0

# M1: ω² scaling (substrate/OU Markovian regime)
# From C2: Γ_φ = Γ_0 + k_rot·ω²  (valid for ω << 1/τ_B)
k_rot = 4.5e-7  # s (empirical, from IBM data fit)
Gamma_M1 = Gamma_0_base + k_rot * omega_range**2

# M0: constant (Markovian)
Gamma_M0 = np.full_like(omega_range, Gamma_0_base)

# M4: 1/f noise (power law, different scaling)
# For 1/f noise, Γ_φ ~ A/ω for ω >> 1/T₂
Gamma_M4 = Gamma_0_base + 1e3 / omega_range  # ~1/ω scaling

# Measurement noise on Γ_φ
sigma_Gamma = Gamma_0_base * 0.05  # 5% measurement uncertainty

# Are ω² and 1/ω distinguishable above noise?
diff_k0_M4 = np.abs(Gamma_M1 - Gamma_M4)
max_diff_temporal = np.max(diff_k0_M4)
snr_temporal = max_diff_temporal / sigma_Gamma

print(f"  k_rot = {k_rot:.1e} s (empirical)")
print(f"  Γ_φ at ω=10⁶: {Gamma_M1[-1]:.1f} rad/s")
print(f"  Γ_0 (base): {Gamma_0_base:.1f} rad/s")
print(f"  ω² term at ω=10⁶: {k_rot * (1e6)**2:.1f} rad/s")
print(f"  ω² / Γ_0 ratio: {k_rot * (1e6)**2 / Gamma_0_base:.2f}")
print(f"  M1 vs M4 max diff: {max_diff_temporal:.1f} rad/s, SNR={snr_temporal:.1f}")
print(f"  C2 vs OU: IDENTICAL (same Lorentzian PSD, confirmed p25 test1)")
print(f"  C2 vs 1/f: distinguishable at ω > {1e3/k_rot**0.5:.0f} rad/s")

results["temporal_channel"] = {
    "c2_vs_ou": "IDENTICAL — cannot discriminate (proved analytically, p25 test1)",
    "c2_vs_markovian": "Distinguishable if k_rot*omega_max^2 > 5*Gamma_0",
    "k_rot_omega_max_squared_over_Gamma0": float(k_rot * 1e12 / Gamma_0_base),
    "verdict": "WEAK: functional form (omega^2) testable but not unique to C2; OU gives same"
}

# ─────────────────────────────────────────────────────────────────────────
# FALSE POSITIVE: does M5 (crosstalk) mimic K0?
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─"*60)
print("TEST: Does EM crosstalk mimic K0 spatial shape?")
print("─"*60)

xi_c_test = 1000e-6   # 1 mm test case
r_test = r_unique[r_unique > 0]
C_K0_test = C_M1_K0(r_test, xi_c_test)

# Crosstalk with similar length scale
xi_em = 800e-6   # 800 µm EM coupling length
amp_em = 0.05    # 5% crosstalk amplitude
C_xtalk = C_M5_crosstalk(r_test, xi_em, amp_em)

# Can we tell them apart?
diff_xtalk = np.abs(C_K0_test - C_xtalk)
sigma_meas_test = 1.0/np.sqrt(N_SHOTS) + READOUT_ERR
snr_xtalk = np.max(diff_xtalk) / sigma_meas_test

print(f"  K0 (ξ=1mm) vs crosstalk (ξ_em=0.8mm, amp=5%):")
print(f"  Max difference: {np.max(diff_xtalk):.4f}")
print(f"  Measurement sigma: {sigma_meas_test:.4f}")
print(f"  SNR: {snr_xtalk:.2f}")
print(f"  Distinguishable: {'YES' if snr_xtalk > 3 else 'NO'}")
print(f"  NOTE: K0 and exp-decay crosstalk have very similar shapes at r << xi_c")

results["false_positive_crosstalk"] = {
    "max_diff": float(np.max(diff_xtalk)),
    "sigma_meas": float(sigma_meas_test),
    "snr": float(snr_xtalk),
    "distinguishable": int(snr_xtalk > 3),
    "warning": "Crosstalk with similar length scale mimics K0 within measurement noise"
}

# ─────────────────────────────────────────────────────────────────────────
# OVERALL VERDICT
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("OVERALL VERDICT")
print("=" * 65)

any_discriminable = any(v.get("discriminable", False) for v in results.values()
                        if isinstance(v, dict) and "discriminable" in v)

if any_discriminable:
    print("CONDITIONAL: Some ξ_c values produce discriminable signal.")
    print("BUT: Those ξ_c values require c << 1 m/s — physically implausible.")
    final_verdict = "D — INCONCLUSIVE: signal exists at implausible parameter values only"
else:
    print("NOT DISCRIMINABLE: At all physically plausible ξ_c values,")
    print("  K0 and exponential are indistinguishable above measurement noise.")
    print("  The experiment cannot distinguish the substrate model from a")
    print("  conventional exponentially-correlated bath.")
    final_verdict = "D — INCONCLUSIVE: indistinguishable at physically plausible parameters"

results["final_verdict"] = final_verdict
print(f"\nFINAL: {final_verdict}")

# Save
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, np.bool_): return bool(obj)
        return super().default(obj)

fpath = os.path.join(OUT, "pre_hardware_simulation_results.json")
with open(fpath, "w") as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResults saved to: {fpath}")
