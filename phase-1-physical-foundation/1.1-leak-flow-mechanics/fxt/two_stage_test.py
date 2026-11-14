#!/usr/bin/env python3
"""
two_stage_test.py
Corrected Two-Stage Statistical Test with Full Null Family Competition.

KEY FIX for M7/M9 failure:
  Prior fitter: K0 vs exp-only null → K0 always wins on heavy-tailed data
  Corrected fitter: K0 vs BEST-FITTING null from full family
    LLR = ll(K0) - max(ll(M2), ll(M7), ll(M9), ll(M10), ll(M11))
  This forces K0 to be BETTER than any conventional model, not just exponential.

Two-stage procedure:
  Stage 1: Phase-1 screening (scale estimation, data-dependent)
  Stage 2: K0 vs best-null LLR test
    Threshold calibrated by parametric bootstrap under the NULL distribution
    conditioned on passing Stage 1 — not selected from desired power.

Output: two_stage_results.json
"""

import numpy as np
import json, os
from scipy.special import k0 as bessel_k0
from scipy.optimize import curve_fit
import sxc_igc_core as core

RNG_DEV = np.random.default_rng(271828)   # development/calibration seed
RNG_VAL = np.random.default_rng(141421)   # held-out validation seed
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "09_spatiotemporal_c2_test", "outputs", "data")
os.makedirs(OUT, exist_ok=True)

positions, pairs, R_ARR = core.make_geometry(12)
N_PAIRS = len(pairs)
T_ARR   = np.linspace(0.15*core.T2_MEDIAN, 0.55*core.T2_MEDIAN, 10)
N_SHOTS = 8192   # use higher shot count to improve power
results = {}

print("="*65)
print("TWO-STAGE STATISTICS AUDIT")
print("="*65)

# ─────────────────────────────────────────────────────────────────────────────
# CORRECTED TEST STATISTIC: K0 vs best-fitting null from full family
# ─────────────────────────────────────────────────────────────────────────────

def fit_k0_model(r_v, c_v, e_v, xi_hint):
    """K0 + exp-crosstalk model. Returns (ll, amp_k0, xi_k0)."""
    def full(r, ak, xk, at, xt):
        xk = max(float(xk), core.A_M * 2)
        return ak*bessel_k0(r/xk)/bessel_k0(core.A_M/xk) + at*np.exp(-r/xt)
    try:
        p, _ = curve_fit(full, r_v, c_v, sigma=e_v, absolute_sigma=True,
                          p0=[0.05, xi_hint, 0.015, 300e-6],
                          bounds=([0, core.A_M*2, 0, core.A_M],
                                  [1.0, 0.02, 0.5, 0.005]), maxfev=3000)
        ll = float(-0.5*np.sum(((c_v - full(r_v, *p))/e_v)**2))
        return ll, float(p[0]), float(p[1])
    except Exception:
        return -1e9, 0.0, np.nan


def fit_best_null(r_v, c_v, e_v):
    """
    Fit all conventional null models and return the BEST log-likelihood.
    Null family: M2 (exp), M7 (power-law, 3 exponents), M9 (two-bath),
                 M10 (stretched-exp), M11 (Matern), M5 (xtalk-only).
    Returns: best_ll, best_model_name
    """
    best_ll = -1e9
    best_name = "none"

    # M2: exp
    try:
        p, _ = curve_fit(lambda r, a, x: a*np.exp(-r/x), r_v, c_v,
                          p0=[0.1, 600e-6], sigma=e_v, absolute_sigma=True,
                          bounds=([0, core.A_M*2], [1, 0.05]), maxfev=1500)
        ll = float(-0.5*np.sum(((c_v - p[0]*np.exp(-r_v/p[1]))/e_v)**2))
        if ll > best_ll: best_ll = ll; best_name = "M2"
    except Exception: pass

    # M7: power-law at three exponents
    for alpha0 in [0.5, 0.8, 1.2]:
        try:
            def m7(r, a, al): return a * (np.maximum(r, core.A_M)/core.A_M)**(-al)
            p, _ = curve_fit(m7, r_v, c_v, p0=[0.08, alpha0], sigma=e_v,
                              absolute_sigma=True,
                              bounds=([0, 0.1], [1, 3.0]), maxfev=1500)
            ll = float(-0.5*np.sum(((c_v - m7(r_v, *p))/e_v)**2))
            if ll > best_ll: best_ll = ll; best_name = f"M7_a{alpha0}"
        except Exception: pass

    # M9: two-bath
    try:
        def m9(r, a1, x1, a2, x2): return a1*np.exp(-r/x1) + a2*np.exp(-r/x2)
        p, _ = curve_fit(m9, r_v, c_v, p0=[0.08, 250e-6, 0.05, 1500e-6],
                          sigma=e_v, absolute_sigma=True,
                          bounds=([0, core.A_M*2, 0, core.A_M*2],
                                  [0.5, 0.005, 0.5, 0.05]), maxfev=2000)
        ll = float(-0.5*np.sum(((c_v - m9(r_v, *p))/e_v)**2))
        if ll > best_ll: best_ll = ll; best_name = "M9"
    except Exception: pass

    # M10: stretched-exp
    try:
        def m10(r, a, x, b): return a*np.exp(-(r/x)**b)
        p, _ = curve_fit(m10, r_v, c_v, p0=[0.10, 600e-6, 0.7], sigma=e_v,
                          absolute_sigma=True,
                          bounds=([0, core.A_M*2, 0.1], [1, 0.05, 2.0]),
                          maxfev=2000)
        ll = float(-0.5*np.sum(((c_v - m10(r_v, *p))/e_v)**2))
        if ll > best_ll: best_ll = ll; best_name = "M10"
    except Exception: pass

    # M11: Matern
    try:
        def m11(r, a, x): return a*(1+np.sqrt(3)*r/x)*np.exp(-np.sqrt(3)*r/x)
        p, _ = curve_fit(m11, r_v, c_v, p0=[0.10, 600e-6], sigma=e_v,
                          absolute_sigma=True,
                          bounds=([0, core.A_M*2], [1, 0.05]), maxfev=1500)
        ll = float(-0.5*np.sum(((c_v - m11(r_v, *p))/e_v)**2))
        if ll > best_ll: best_ll = ll; best_name = "M11"
    except Exception: pass

    return best_ll, best_name


def corrected_llr(C_gamma, C_gamma_err, xi_hint):
    """
    LLR = ll(K0) - ll(best conventional null).
    Positive = K0 preferred over all tested conventional models.
    """
    valid = (~np.isnan(C_gamma)) & np.isfinite(C_gamma) & (C_gamma_err > 1e-9)
    r_v = R_ARR[valid]; c_v = C_gamma[valid]; e_v = C_gamma_err[valid]
    if len(r_v) < 6:
        return 0.0, 0.0, "insufficient"

    ll_k0, amp_k0, xi_k0 = fit_k0_model(r_v, c_v, e_v, xi_hint)
    ll_null, null_name   = fit_best_null(r_v, c_v, e_v)
    llr = ll_k0 - ll_null
    return float(llr), float(amp_k0), null_name


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1: Phase-1 screening
# ─────────────────────────────────────────────────────────────────────────────

def phase1_xi_est(C_gamma, C_gamma_err):
    """Estimate correlation length scale. Returns xi_est in metres."""
    valid = (~np.isnan(C_gamma)) & np.isfinite(C_gamma) & (C_gamma_err > 1e-9) & (C_gamma > 0)
    r_v = R_ARR[valid]; c_v = C_gamma[valid]; e_v = C_gamma_err[valid]
    if len(r_v) < 4:
        return 1.0  # default to large (fail screen)
    try:
        p, _ = curve_fit(lambda r, a, x: a*np.exp(-r/x), r_v, c_v,
                          p0=[0.1, 1e-3], sigma=e_v, absolute_sigma=True,
                          bounds=([0, core.A_M*2], [1.0, 0.05]), maxfev=1000)
        return float(p[1])
    except Exception:
        return 1.0


SCREEN_THRESH = 2.0e-3   # metres

# ─────────────────────────────────────────────────────────────────────────────
# CALIBRATION STEP: derive LLR threshold from null distribution under Stage-1
# Using RNG_DEV (development set) — NOT the validation set.
# ─────────────────────────────────────────────────────────────────────────────

print("\n── Calibration: null LLR distribution under Stage-1 conditioning ──")
print("   (using development RNG — separate from validation)")

N_CAL = 600
# Use the worst conventional null for calibration: M7_pow0.5
C_worst_null = np.clip(
    core.C_M7_powerlaw(R_ARR, 0.08, core.A_M, 0.5) + core.C_M5_crosstalk(R_ARR),
    0, 0.98)

null_llrs_cond = []  # null LLRs that passed Stage 1

for _ in range(N_CAL):
    data, _ = core.generate_dataset(R_ARR, pairs, T_ARR, N_SHOTS, RNG_DEV, C_worst_null)
    Cg, Ce  = core.extract_C_gamma(data)
    xi_est  = phase1_xi_est(Cg, Ce)
    if xi_est > SCREEN_THRESH:
        continue
    llr, ak, _ = corrected_llr(Cg, Ce, xi_est)
    null_llrs_cond.append(float(llr))

n_pass_cal = len(null_llrs_cond)
print(f"  Calibration: {n_pass_cal}/{N_CAL} worst-null trials passed Stage-1")

if n_pass_cal < 20:
    print("  WARNING: too few null trials passed screening for reliable calibration")
    LLR_THRESHOLD = 3.0
    print(f"  Using fallback threshold: {LLR_THRESHOLD}")
else:
    null_arr = np.array(null_llrs_cond)
    # Threshold = 90th percentile of null LLR distribution under Stage-1
    # This gives FP <= 10% conditional on passing Stage 1
    LLR_THRESHOLD = float(np.percentile(null_arr, 90))
    print(f"  Null LLR under S: mean={null_arr.mean():.3f} std={null_arr.std():.3f}")
    print(f"  90th percentile (FP=0.10 threshold): {LLR_THRESHOLD:.3f}")

results["calibration"] = {
    "n_cal_trials": N_CAL,
    "null_model_used": "M7_pow0.5 (worst case)",
    "n_passed_screen": n_pass_cal,
    "screen_thresh_mm": SCREEN_THRESH * 1e3,
    "llr_threshold_fp10": float(LLR_THRESHOLD),
    "note": "Threshold derived from null distribution, not from desired power"
}

print(f"\n  FIXED THRESHOLD: {LLR_THRESHOLD:.3f}")
print("  This threshold is now FROZEN for the validation step.")

# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION STEP: FP rates on all null models + power on K0
# Using RNG_VAL (validation set — never seen by calibration step)
# ─────────────────────────────────────────────────────────────────────────────

print("\n── Validation: FP rates on full null family (held-out RNG_VAL) ──")
N_VAL = 300

NULL_CONFIGS = {
    "M0":          np.clip(core.C_M0(R_ARR) + core.C_M5_crosstalk(R_ARR), 0, 0.98),
    "M2_exp":      np.clip(core.C_M2_exp(R_ARR, 600e-6, 0.10) + core.C_M5_crosstalk(R_ARR), 0, 0.98),
    "M5_xtalk":    np.clip(core.C_M5_crosstalk(R_ARR), 0, 0.98),
    "M7_pow0.5":   np.clip(core.C_M7_powerlaw(R_ARR, 0.08, core.A_M, 0.5) + core.C_M5_crosstalk(R_ARR), 0, 0.98),
    "M7_pow1.0":   np.clip(core.C_M7_powerlaw(R_ARR, 0.08, core.A_M, 1.0) + core.C_M5_crosstalk(R_ARR), 0, 0.98),
    "M8_gauss":    np.clip(core.C_M8_gaussian(R_ARR, 0.10, 600e-6) + core.C_M5_crosstalk(R_ARR), 0, 0.98),
    "M9_twobath":  np.clip(core.C_M9_twobath(R_ARR, 0.08, 250e-6, 0.05, 1500e-6) + core.C_M5_crosstalk(R_ARR), 0, 0.98),
    "M10_stretch": np.clip(core.C_M10_stretched_exp(R_ARR, 0.10, 600e-6, 0.7) + core.C_M5_crosstalk(R_ARR), 0, 0.98),
    "M11_matern":  np.clip(core.C_M11_matern(R_ARR, 0.10, 600e-6) + core.C_M5_crosstalk(R_ARR), 0, 0.98),
}

val_fp = {}
worst_fp = 0.0; worst_model = ""

for mname, C_null in NULL_CONFIGS.items():
    fp_count = 0; llrs = []
    for _ in range(N_VAL):
        data, _ = core.generate_dataset(R_ARR, pairs, T_ARR, N_SHOTS, RNG_VAL, C_null)
        Cg, Ce  = core.extract_C_gamma(data)
        xi_est  = phase1_xi_est(Cg, Ce)
        if xi_est > SCREEN_THRESH:
            continue
        llr, ak, _ = corrected_llr(Cg, Ce, xi_est)
        detected = (llr > LLR_THRESHOLD) and (ak > 0.01)
        fp_count += int(detected); llrs.append(float(llr))

    n_tested = len(llrs)
    fp_rate  = fp_count / N_VAL  # denominator = all trials, not just screened
    cp95     = core.clopper_pearson_upper(fp_count, N_VAL)
    status   = "FAIL" if fp_rate > 0.10 else "pass"
    if fp_rate > worst_fp: worst_fp = fp_rate; worst_model = mname

    val_fp[mname] = {
        "fp_count": fp_count, "n_all_trials": N_VAL,
        "n_screened_in": n_tested,
        "fp_rate": float(fp_rate), "cp95_upper": float(cp95),
        "llr_mean": float(np.mean(llrs)) if llrs else 0.0,
        "status": status,
    }
    print(f"  {mname:15s}: FP={fp_count}/{N_VAL} ({fp_rate:.3f}) "
          f"CP95<{cp95:.3f}  screened_in={n_tested}  [{status}]")

print(f"\n  Worst-case FP: {worst_fp:.3f} ({worst_model})")
gate_null = "FAIL" if worst_fp > 0.10 else "PASS"
print(f"  Global null gate: {gate_null}")

# ─────────────────────────────────────────────────────────────────────────────
# POWER ANALYSIS: K0 at several (xi_c, sub_frac) points
# ─────────────────────────────────────────────────────────────────────────────

print("\n── Power analysis: K0 detection (held-out RNG_VAL) ──")

POWER_CONFIGS = [
    (0.5e-3, 0.15), (0.5e-3, 0.20), (0.5e-3, 0.30),
    (1.0e-3, 0.15), (1.0e-3, 0.20), (1.0e-3, 0.30),
    (2.0e-3, 0.15), (2.0e-3, 0.20),
]

power_results = {}
for xi_c, sf in POWER_CONFIGS:
    C_K0 = np.clip(
        core.C_M1_K0(R_ARR, xi_c, sf) + core.C_M5_crosstalk(R_ARR),
        0, 0.98)
    tp = 0; llrs_k0 = []
    for _ in range(N_VAL):
        data, _ = core.generate_dataset(R_ARR, pairs, T_ARR, N_SHOTS, RNG_VAL, C_K0)
        Cg, Ce  = core.extract_C_gamma(data)
        xi_est  = phase1_xi_est(Cg, Ce)
        if xi_est > SCREEN_THRESH:
            continue
        llr, ak, _ = corrected_llr(Cg, Ce, xi_est)
        detected = (llr > LLR_THRESHOLD) and (ak > 0.01)
        tp += int(detected); llrs_k0.append(float(llr))

    n_screened = len(llrs_k0)
    power = tp / N_VAL
    k = f"xi{xi_c*1e3:.1f}mm_sf{sf:.2f}"
    power_results[k] = {
        "xi_c_mm": xi_c*1e3, "sub_frac": sf,
        "n_all": N_VAL, "n_screened_in": n_screened,
        "tp_count": tp, "power": float(power),
        "llr_mean": float(np.mean(llrs_k0)) if llrs_k0 else 0.0,
    }
    flag = "✓" if power >= 0.80 else "✗"
    print(f"  {flag} xi_c={xi_c*1e3:.1f}mm sf={sf:.2f}: "
          f"power={power:.3f} screened_in={n_screened}/{N_VAL}")

gate_power = any(v["power"] >= 0.80 for v in power_results.values())
print(f"\n  Any design passes power gate (>=0.80): {gate_power}")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL VERDICT
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "="*65)
print("SUMMARY")
print("="*65)
all_pass = (gate_null == "PASS") and gate_power
print(f"  Null gate:  {gate_null}")
print(f"  Power gate: {'PASS' if gate_power else 'FAIL'}")
print(f"  Overall:    {'PASS' if all_pass else 'FAIL'}")

if all_pass:
    best = max(power_results.values(), key=lambda x: x["power"])
    verdict = (f"PROCEED_CANDIDATE: xi_c={best['xi_c_mm']:.1f}mm "
               f"sf={best['sub_frac']:.2f} power={best['power']:.3f} "
               f"worst_FP={worst_fp:.3f} threshold={LLR_THRESHOLD:.3f}")
else:
    fail_reasons = []
    if gate_null == "FAIL":
        fail_reasons.append(f"null gate failed: worst FP={worst_fp:.3f} on {worst_model}")
    if not gate_power:
        best_p = max(v["power"] for v in power_results.values())
        fail_reasons.append(f"power gate failed: best power={best_p:.3f} < 0.80")
    verdict = "STOP: " + "; ".join(fail_reasons)

print(f"\n  VERDICT: {verdict}")

# Save
class NpEnc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, np.ndarray): return o.tolist()
        if isinstance(o, np.bool_): return bool(o)
        return super().default(o)

output = {
    "calibration": results.get("calibration", {}),
    "llr_threshold": float(LLR_THRESHOLD),
    "n_shots": N_SHOTS,
    "validation_fp": val_fp,
    "worst_case_fp": {"model": worst_model, "fp_rate": float(worst_fp)},
    "power_results": power_results,
    "null_gate": gate_null,
    "power_gate": "PASS" if gate_power else "FAIL",
    "overall_gate": "PASS" if all_pass else "FAIL",
    "verdict": verdict,
}
fpath = os.path.join(OUT, "two_stage_results.json")
with open(fpath, "w") as f:
    json.dump(output, f, indent=2, cls=NpEnc)
print(f"\nSaved: {fpath}")
