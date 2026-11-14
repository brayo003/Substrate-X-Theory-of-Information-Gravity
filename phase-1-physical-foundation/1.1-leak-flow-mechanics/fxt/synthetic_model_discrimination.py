#!/usr/bin/env python3
"""
synthetic_model_discrimination.py
SXC-IGC Full Synthetic Experiment — Blind World A vs World B Recovery

τ_B is the substrate bath correlation time = 1/(2λ) where λ is the PRW
direction-reversal rate. It appears in:
  - C_JJ(t) = S₀·exp(−t/τ_B)  [substrate autocorrelation, DERIVED]
  - S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²)  [Lorentzian PSD, DERIVED]
  - ξ_c = 2c·τ_B  [coherence length, DERIVED — but c is FREE]
  - Φ(t) = Γ_M·τ_B·[t/τ_B − 1 + exp(−t/τ_B)]  [exact dephasing, DERIVED]
  - NMP = τ_B·Γ_φ  [non-Markovianity parameter]

τ_B IS MEASURABLE from the Ramsey trace curvature (NM regime).
It is NOT the same as T₂ or T₁.
ξ_c = 2c·τ_B requires c separately, which is NOT derived from C2 (GAP-7).

World A: All ordinary physics, no substrate K₀ component.
World B: World A + genuine K₀ substrate spatial correlation.

The analysis must distinguish them blindly.

Outputs: synthetic_discrimination_results.json
"""

import numpy as np
import json, os
from scipy.special import k0 as bessel_k0
from scipy.optimize import curve_fit, minimize
from scipy.stats import chi2

RNG = np.random.default_rng(99999)
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "09_spatiotemporal_c2_test", "outputs", "data")
os.makedirs(OUT, exist_ok=True)

print("=" * 65)
print("SXC-IGC Synthetic Blind Discrimination: World A vs World B")
print("=" * 65)

# ── Hardware parameters (Brisbane calibration) ────────────────────────────
N_QUBITS     = 16        # usable qubits (T1/T2 ratio > 2 filter)
A_UM         = 200.0     # µm, heavy-hex lattice spacing
T1_GOOD      = 300e-6    # s  — select qubits with T1 > 300 µs
T2_GOOD      = 150e-6    # s  — T2 for good qubits
T1_RATIO_REQ = 2.0       # require T1 > 2*T2

GAMMA_PHI    = 1.0/T2_GOOD          # base dephasing rate (rad/s)
GAMMA_RELAX  = 1.0/(2*T1_GOOD)     # T1 relaxation contribution
READOUT_ERR  = 0.020                # symmetric readout error
CROSSTALK    = 0.015                # EM crosstalk amplitude (nearest-neighbor)
XI_EM        = 300e-6               # m, EM crosstalk length scale

N_SHOTS      = 4096      # shots per measurement
N_TIME_PTS   = 12        # time points per Ramsey decay
T_MAX        = 0.6 * T2_GOOD

# Substrate parameters
TAU_B        = 5e-6      # s  (measurable from NM regime)
# Two test cases for ξ_c (the key unknown)
XI_C_TESTABLE = 1.0e-3   # 1 mm — would be testable (c = 100 m/s)
XI_C_LARGE    = 50.0e-3  # 50 mm — physically motivated but not testable

# Substrate signal amplitude (fraction of total dephasing from substrate)
SUBSTRATE_FRAC = 0.08    # 8% of dephasing is correlated substrate contribution

UV_CUT = A_UM * 1e-6    # 200 µm cutoff

# ── Qubit layout: linear chain ────────────────────────────────────────────
positions = np.arange(N_QUBITS) * A_UM * 1e-6  # metres
pairs = [(i, j, abs(positions[i] - positions[j]))
         for i in range(N_QUBITS) for j in range(i+1, N_QUBITS)]
r_arr = np.array([p[2] for p in pairs])
t_arr = np.linspace(T_MAX / N_TIME_PTS, T_MAX, N_TIME_PTS)

print(f"\nSetup: {N_QUBITS} qubits, {len(pairs)} pairs, {N_TIME_PTS} time points")
print(f"T2 = {T2_GOOD*1e6:.0f} µs, Γ_φ = {GAMMA_PHI:.0f} rad/s")
print(f"τ_B = {TAU_B*1e6:.1f} µs, NMP = {TAU_B*GAMMA_PHI:.3f}")
print(f"Readout error: {READOUT_ERR*100:.1f}%, EM crosstalk: {CROSSTALK*100:.1f}%")


# ─────────────────────────────────────────────────────────────────────────
# HELPER: exact dephasing including T1, non-Markovian tau_B, readout errors
# ─────────────────────────────────────────────────────────────────────────

def ramsey_signal(t, gamma_phi, gamma_relax, tau_B_val):
    """Exact Ramsey decay with T1 and non-Markovian correction."""
    # Exact non-Markovian dephasing (Kubo 1963, DERIVED)
    phi = gamma_phi * tau_B_val * (t/tau_B_val - 1 + np.exp(-t/tau_B_val))
    # T1 relaxation envelope
    relax = np.exp(-gamma_relax * t)
    return np.exp(-phi) * relax


def add_readout_noise(signal, n_shots, readout_err):
    """Add finite-shot noise and readout misclassification."""
    # Pauli expectation value in [-1, 1]; map to prob in [0,1]
    p = (1 + signal) / 2
    # Readout error: p_meas = (1-e)*p + e*(1-p) = p*(1-2e) + e
    p_meas = p * (1 - 2*readout_err) + readout_err
    p_meas = np.clip(p_meas, 0, 1)
    # Shot noise
    counts = RNG.binomial(n_shots, p_meas)
    p_est = counts / n_shots
    # Convert back to expectation value
    return 2*p_est - 1


def readout_crosstalk_matrix(n_qubits, crosstalk_amp, xi_em, positions):
    """Build readout crosstalk covariance matrix."""
    C = np.zeros((n_qubits, n_qubits))
    for i in range(n_qubits):
        for j in range(n_qubits):
            r = abs(positions[i] - positions[j])
            C[i,j] = crosstalk_amp * np.exp(-r / xi_em)
    np.fill_diagonal(C, 1.0)
    return C


# ─────────────────────────────────────────────────────────────────────────
# WORLD GENERATOR
# ─────────────────────────────────────────────────────────────────────────

def generate_world(xi_c, include_substrate, n_trials=200):
    """
    Generate synthetic C_ij(t) data for all qubit pairs.

    Returns: dict with keys 'C_ij_obs' (n_pairs, n_time), 'r_arr', 't_arr'
    """
    C_xt_mat = readout_crosstalk_matrix(N_QUBITS, CROSSTALK, XI_EM, positions)

    # Per-qubit single-qubit Ramsey signals (with qubit-to-qubit variation)
    gamma_phi_i = GAMMA_PHI * (1 + 0.1*RNG.standard_normal(N_QUBITS))
    gamma_phi_i = np.clip(gamma_phi_i, GAMMA_PHI*0.5, GAMMA_PHI*1.5)

    # Substrate spatial correlation (K0 shape)
    if include_substrate:
        norm_k0 = bessel_k0(UV_CUT / xi_c)
        def C_substrate(r):
            return SUBSTRATE_FRAC * bessel_k0(r / xi_c) / norm_k0
    else:
        def C_substrate(r):
            return np.zeros_like(r)

    # EM crosstalk correlation
    def C_xtalk(r):
        return CROSSTALK * np.exp(-r / XI_EM)

    # Generate data for each qubit pair
    C_ij_obs = np.zeros((len(pairs), N_TIME_PTS))

    for p_idx, (i, j, r_ij) in enumerate(pairs):
        for t_idx, t in enumerate(t_arr):
            # Single-qubit signals
            W_i = ramsey_signal(t, gamma_phi_i[i], GAMMA_RELAX, TAU_B)
            W_j = ramsey_signal(t, gamma_phi_i[j], GAMMA_RELAX, TAU_B)

            # Cross-correlation from substrate + crosstalk
            C_total = C_substrate(r_ij) + C_xtalk(r_ij)
            C_total = min(C_total, 0.99)  # physical bound

            # Cross term: ⟨σx,i·σx,j⟩ = W_i·W_j·(1 + correction) for correlated noise
            # For Gaussian correlated dephasing: ⟨WiWj⟩ = Wi·Wj·exp(C_total·Gamma_phi·t)
            # (derived in observable_mapping_audit.md)
            cross_signal = W_i * W_j * np.exp(C_total * GAMMA_PHI * t)

            # Add readout noise (single qubit)
            W_i_meas = add_readout_noise(np.array([W_i]), N_SHOTS, READOUT_ERR)[0]
            W_j_meas = add_readout_noise(np.array([W_j]), N_SHOTS, READOUT_ERR)[0]

            # Add simultaneous readout noise to cross term
            cross_meas = add_readout_noise(np.array([cross_signal]), N_SHOTS, READOUT_ERR)[0]

            # Readout crosstalk adds a spurious correlation term
            xtalk_spurious = C_xt_mat[i, j] * READOUT_ERR * RNG.standard_normal()

            denom = W_i_meas * W_j_meas
            if abs(denom) < 1e-6:
                C_ij_obs[p_idx, t_idx] = np.nan
            else:
                C_ij_obs[p_idx, t_idx] = (cross_meas + xtalk_spurious) / denom

    return {"C_ij_obs": C_ij_obs, "r_arr": r_arr, "t_arr": t_arr,
            "gamma_phi_true": float(np.mean(gamma_phi_i)),
            "xi_c": xi_c, "substrate": include_substrate}


# ─────────────────────────────────────────────────────────────────────────
# ANALYSIS PIPELINE (blind — does not know true world)
# ─────────────────────────────────────────────────────────────────────────

def extract_spatial_correlation(data, gamma_phi_est):
    """
    Extract C_Gamma(r) from C_ij(t) data.
    Uses: C_Gamma(r) = 1 + mean_t[ln(C_ij(t)) / (Gamma_phi * t)]
    """
    C_ij = data["C_ij_obs"]
    t_pts = data["t_arr"]
    r_pts = data["r_arr"]

    n_pairs = len(r_pts)
    C_gamma_est = np.zeros(n_pairs)
    C_gamma_err = np.zeros(n_pairs)

    for p_idx in range(n_pairs):
        samples = []
        for t_idx, t in enumerate(t_pts):
            v = C_ij[p_idx, t_idx]
            if np.isnan(v) or v <= 0 or v > 10:
                continue
            # C_Gamma(r) = ln(C_ij(t)) / (Gamma_phi * t)
            # Derivation: C_ij(t) = exp(C_Gamma*Gamma_phi*t)
            # so C_Gamma = ln(C_ij)/(Gamma_phi*t)
            val = np.log(v) / (gamma_phi_est * t)
            samples.append(val)
        if samples:
            C_gamma_est[p_idx] = np.mean(samples)
            C_gamma_err[p_idx] = np.std(samples) / np.sqrt(len(samples)) if len(samples) > 1 else 0.05
        else:
            C_gamma_est[p_idx] = np.nan
            C_gamma_err[p_idx] = np.nan

    return r_pts, C_gamma_est, C_gamma_err


def fit_spatial_models(r_pts, C_gamma_est, C_gamma_err, xi_c_hint):
    """Fit K0 and exponential models. Return log-likelihood ratio and AIC diff."""
    valid = ~np.isnan(C_gamma_est) & ~np.isnan(C_gamma_err) & (C_gamma_err > 0)
    r_v = r_pts[valid]
    C_v = C_gamma_est[valid]
    e_v = C_gamma_err[valid]

    if len(r_v) < 4:
        return {"status": "insufficient_data", "llr": 0.0, "delta_aic": 0.0}

    # Model 1: K0
    def model_k0(r, xi, amp):
        norm = bessel_k0(UV_CUT / xi) if xi > UV_CUT*2 else 1.0
        return amp * bessel_k0(r / xi) / norm

    # Model 2: Exponential
    def model_exp(r, xi, amp):
        return amp * np.exp(-r / xi)

    # Fit K0
    try:
        p0_k0 = [xi_c_hint, float(np.max(C_v))]
        popt_k0, pcov_k0 = curve_fit(model_k0, r_v, C_v, p0=p0_k0, sigma=e_v,
                                      absolute_sigma=True, maxfev=2000,
                                      bounds=([UV_CUT*2, 0], [np.inf, 2]))
        resid_k0 = (C_v - model_k0(r_v, *popt_k0)) / e_v
        chi2_k0 = np.sum(resid_k0**2)
        ll_k0 = -0.5 * chi2_k0
        k_k0 = 2  # free params
    except Exception:
        chi2_k0 = 1e10; ll_k0 = -1e10; k_k0 = 2; popt_k0 = [xi_c_hint, 0]

    # Fit Exp
    try:
        p0_exp = [xi_c_hint, float(np.max(C_v))]
        popt_exp, _ = curve_fit(model_exp, r_v, C_v, p0=p0_exp, sigma=e_v,
                                 absolute_sigma=True, maxfev=2000,
                                 bounds=([UV_CUT*2, 0], [np.inf, 2]))
        resid_exp = (C_v - model_exp(r_v, *popt_exp)) / e_v
        chi2_exp = np.sum(resid_exp**2)
        ll_exp = -0.5 * chi2_exp
        k_exp = 2
    except Exception:
        chi2_exp = 1e10; ll_exp = -1e10; k_exp = 2; popt_exp = [xi_c_hint, 0]

    n_data = len(r_v)
    llr = ll_k0 - ll_exp  # positive: K0 preferred
    delta_aic = (2*k_exp - 2*ll_exp) - (2*k_k0 - 2*ll_k0)  # positive: K0 preferred

    # K0 amplitude from fit
    amp_k0_fit = float(popt_k0[1]) if len(popt_k0) > 1 else 0.0
    xi_k0_fit = float(popt_k0[0])

    return {
        "status": "ok",
        "llr": float(llr),          # >0: K0 preferred
        "delta_aic": float(delta_aic),  # >0: K0 preferred
        "chi2_k0": float(chi2_k0),
        "chi2_exp": float(chi2_exp),
        "xi_k0_fit": xi_k0_fit,
        "amp_k0_fit": amp_k0_fit,
        "n_data": int(n_data),
    }


# ─────────────────────────────────────────────────────────────────────────
# MAIN SIMULATION: World A vs World B, both ξ_c cases
# ─────────────────────────────────────────────────────────────────────────

N_TRIALS = 300   # Monte Carlo trials per world
results = {}

for xi_label, xi_c_val in [("xi_1mm", XI_C_TESTABLE), ("xi_50mm", XI_C_LARGE)]:
    print(f"\n{'='*60}")
    print(f"ξ_c = {xi_c_val*1e3:.0f} mm")
    print(f"{'='*60}")

    for world_label, include_sub in [("world_A_null", False), ("world_B_substrate", True)]:
        print(f"\n  {world_label} (substrate={'YES' if include_sub else 'NO'}):")

        llr_vals = []
        delta_aic_vals = []
        amp_recovered = []
        correct_decisions = 0

        for trial in range(N_TRIALS):
            # Generate synthetic data
            data = generate_world(xi_c_val, include_sub)

            # Analysis: extract C_Gamma(r)
            r_pts, C_gamma_est, C_gamma_err = extract_spatial_correlation(
                data, data["gamma_phi_true"])

            # Fit models
            fit = fit_spatial_models(r_pts, C_gamma_est, C_gamma_err, xi_c_val)

            if fit["status"] != "ok":
                continue

            llr_vals.append(fit["llr"])
            delta_aic_vals.append(fit["delta_aic"])
            amp_recovered.append(fit.get("amp_k0_fit", 0))

            # Decision: K0 preferred if LLR > threshold
            # Threshold: LLR > 2 (roughly p < 0.05 for 1 DoF chi2)
            if include_sub:
                correct_decisions += int(fit["llr"] > 2.0)
            else:
                correct_decisions += int(fit["llr"] <= 2.0)

        n_valid = len(llr_vals)
        if n_valid == 0:
            print("    No valid trials")
            continue

        llr_arr = np.array(llr_vals)
        power_or_specificity = correct_decisions / N_TRIALS

        if include_sub:
            # World B: power = fraction correctly identified as substrate
            fp_rate = np.mean(llr_arr <= 2.0)  # false negatives
            print(f"    Trials: {n_valid}/{N_TRIALS}")
            print(f"    LLR: mean={np.mean(llr_arr):.2f}, std={np.std(llr_arr):.2f}")
            print(f"    Power (K0 correctly identified): {power_or_specificity:.3f}")
            print(f"    Median amp recovered: {np.median(amp_recovered):.4f} (injected: {SUBSTRATE_FRAC:.4f})")
            label = "DETECTABLE" if power_or_specificity > 0.8 else "NOT DETECTABLE"
        else:
            # World A: specificity = fraction correctly identified as NO substrate
            fp_rate = np.mean(llr_arr > 2.0)
            print(f"    Trials: {n_valid}/{N_TRIALS}")
            print(f"    LLR: mean={np.mean(llr_arr):.2f}, std={np.std(llr_arr):.2f}")
            print(f"    Specificity (null correctly identified): {power_or_specificity:.3f}")
            print(f"    False positive rate: {fp_rate:.3f}")
            label = "NULL IDENTIFIED" if power_or_specificity > 0.9 else "TOO MANY FALSE POSITIVES"

        print(f"    STATUS: {label}")

        results[f"{xi_label}_{world_label}"] = {
            "xi_c_mm": xi_c_val * 1e3,
            "substrate": include_sub,
            "n_trials": N_TRIALS,
            "n_valid": n_valid,
            "llr_mean": float(np.mean(llr_arr)),
            "llr_std": float(np.std(llr_arr)),
            "fraction_correct": float(power_or_specificity),
            "false_positive_rate": float(fp_rate),
            "status": label,
        }


# ─────────────────────────────────────────────────────────────────────────
# τ_B IDENTIFICATION TEST
# ─────────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print("τ_B IDENTIFICATION TEST")
print(f"{'='*60}")
print(f"τ_B = {TAU_B*1e6:.1f} µs (NMP = τ_B·Γ_φ = {TAU_B*GAMMA_PHI:.3f})")
print()

# Can τ_B be extracted from a single-qubit Ramsey trace?
# Yes, via the non-Markovian shape: W(t) = exp(-Gamma_M*tau_B*(t/tau_B-1+exp(-t/tau_B)))
# At short times W ~ exp(-Gamma_M*t²/(2*tau_B)) (Gaussian); at long times W ~ exp(-Gamma_M*t)
# The crossover at t ~ tau_B is the signature.

t_ramsey = np.linspace(1e-6, 4*T2_GOOD, 100)
W_true = ramsey_signal(t_ramsey, GAMMA_PHI, GAMMA_RELAX, TAU_B)
W_markov = np.exp(-GAMMA_PHI * t_ramsey)  # pure exponential (no tau_B)

max_diff_nm = np.max(np.abs(W_true - W_markov))
sigma_ramsey = 1.0/np.sqrt(N_SHOTS)
snr_tau_B = max_diff_nm / sigma_ramsey

print(f"NM vs Markovian max difference: {max_diff_nm:.4f}")
print(f"Shot noise (1/sqrt(N_shots)): {sigma_ramsey:.4f}")
print(f"SNR for τ_B detection: {snr_tau_B:.1f}")

if TAU_B * GAMMA_PHI > 0.1 and snr_tau_B > 3:
    print("STATUS: τ_B IS MEASURABLE from Ramsey trace curvature")
    tau_b_measurable = True
else:
    print("STATUS: τ_B NOT measurable (NMP too small or SNR too low)")
    tau_b_measurable = False

# What does measuring τ_B give us?
# ξ_c = 2c·τ_B, but c is still free.
# Measuring τ_B gives ONE parameter; ξ_c still needs c.
# Only if c is independently constrained does ξ_c follow.

print(f"\nτ_B role summary:")
print(f"  τ_B = 1/(2λ) — substrate bath correlation time [DERIVED from PRW]")
print(f"  τ_B is MEASURABLE from Ramsey trace shape (NMP condition)")
print(f"  ξ_c = 2c·τ_B — still requires c (FREE PARAMETER, GAP-7)")
print(f"  Measuring τ_B alone does NOT determine ξ_c")
print(f"  The spatial test still requires independently measuring ξ_c first")

results["tau_B_identification"] = {
    "tau_B_us": TAU_B * 1e6,
    "NMP": float(TAU_B * GAMMA_PHI),
    "snr_tau_B_detection": float(snr_tau_B),
    "measurable": tau_b_measurable,
    "c_still_free": True,
    "xi_c_still_undetermined": True,
    "note": "tau_B measurable from Ramsey curvature; xi_c requires c (not predicted)"
}


# ─────────────────────────────────────────────────────────────────────────
# FINAL VERDICT
# ─────────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print("FINAL VERDICT")
print(f"{'='*60}")

# Check if World A null correctly maintained and World B detected
# for the testable ξ_c case
r_1mm_A = results.get("xi_1mm_world_A_null", {})
r_1mm_B = results.get("xi_1mm_world_B_substrate", {})
r_50mm_A = results.get("xi_50mm_world_A_null", {})
r_50mm_B = results.get("xi_50mm_world_B_substrate", {})

print("\nξ_c = 1 mm (testable if c ~ 100 m/s):")
print(f"  World A specificity: {r_1mm_A.get('fraction_correct', 0):.3f}")
print(f"  World B power:       {r_1mm_B.get('fraction_correct', 0):.3f}")
print(f"  World A FP rate:     {r_1mm_A.get('false_positive_rate', 0):.3f}")

print("\nξ_c = 50 mm (physically motivated, OU-like c ~ 5 km/s):")
print(f"  World A specificity: {r_50mm_A.get('fraction_correct', 0):.3f}")
print(f"  World B power:       {r_50mm_B.get('fraction_correct', 0):.3f}")
print(f"  World A FP rate:     {r_50mm_A.get('false_positive_rate', 0):.3f}")

# Decision
a_ok = r_1mm_A.get('fraction_correct', 0) > 0.90
b_ok = r_1mm_B.get('fraction_correct', 0) > 0.80
fp_ok = r_1mm_A.get('false_positive_rate', 0) < 0.10

if a_ok and b_ok and fp_ok:
    verdict = "READY FOR PHASE 1 (measure xi_c first, then shape test)"
    print(f"\nVERDICT: {verdict}")
    print("The analysis pipeline can correctly distinguish World A from World B")
    print("IF ξ_c = 1 mm. This requires Phase 1 to confirm ξ_c ≤ 3 mm.")
else:
    verdict = "NOT READY: World A/B discrimination insufficient at testable parameters"
    print(f"\nVERDICT: {verdict}")

results["final_verdict"] = verdict
results["experiment_ready"] = bool(a_ok and b_ok and fp_ok)

fpath = os.path.join(OUT, "synthetic_discrimination_results.json")
with open(fpath, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved: {fpath}")
