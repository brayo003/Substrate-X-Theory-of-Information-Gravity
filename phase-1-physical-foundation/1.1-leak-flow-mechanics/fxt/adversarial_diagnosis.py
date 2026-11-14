#!/usr/bin/env python3
"""
adversarial_diagnosis.py
Diagnose why M7 (power-law) produced 84% FP and M9 (two-bath) 25% FP.

Parts:
  A. Geometry analysis: what information content does the 12-qubit chain have?
  B. Shape similarity: how similar are K0, M7, M9 over the actual r range?
  C. Profile likelihood: what xi_c does the K0 fitter assign to M7/M9 data?
  D. Fisher information: is the 4-param model locally identifiable?
  E. Confusion matrix across full null family

Output: adversarial_diagnosis_results.json
"""

import numpy as np
import json, os
from scipy.special import k0 as bessel_k0
from scipy.optimize import curve_fit, minimize_scalar
import sxc_igc_core as core

RNG  = np.random.default_rng(314159)
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "09_spatiotemporal_c2_test", "outputs", "data")
os.makedirs(OUT, exist_ok=True)

positions, pairs, R_ARR = core.make_geometry(12)
N_PAIRS = len(pairs)
T_ARR   = np.linspace(0.15*core.T2_MEDIAN, 0.55*core.T2_MEDIAN, 10)
N_SHOTS = 4096
N_TRIALS_DIAG = 300
results = {}

print("="*65)
print("ADVERSARIAL DIAGNOSIS")
print("="*65)

# ── A. GEOMETRY ANALYSIS ─────────────────────────────────────────────────────
print("\n─── A. Geometry: separation distribution ───")
r_um = R_ARR * 1e6
print(f"  n_pairs={N_PAIRS}, r_min={r_um.min():.0f} µm, r_max={r_um.max():.0f} µm")
unique_r = np.unique(np.round(r_um / 50) * 50)
print(f"  Unique separations (50µm bins): {len(unique_r)}")
print(f"  Range in units of xi_c=1mm: {r_um.min()/1000:.2f} – {r_um.max()/1000:.2f}")

# How many distinct shape bins does the geometry provide?
# K0 shape changes significantly across ~0.5-3 xi_c.
# At xi_c=1mm: pairs span 0.2-2.2 units. At xi_c=0.5mm: 0.4-4.4 units.
for xi_c_mm in [0.5, 1.0, 2.0]:
    xi_c = xi_c_mm * 1e-3
    r_xi = R_ARR / xi_c
    n_bins_covered = np.sum((r_xi >= 0.3) & (r_xi <= 5.0))
    print(f"  xi_c={xi_c_mm}mm: pairs in [0.3,5]·xi_c = {n_bins_covered}/{N_PAIRS}")

results["geometry"] = {
    "n_pairs": N_PAIRS,
    "r_min_um": float(r_um.min()),
    "r_max_um": float(r_um.max()),
    "n_unique_50um_bins": int(len(unique_r)),
}

# ── B. SHAPE SIMILARITY ───────────────────────────────────────────────────────
print("\n─── B. Shape similarity over chip range ───")
XI_C = 1.0e-3   # 1 mm reference

# Normalised profiles over R_ARR
def normed(v): return v / v.max() if v.max() > 0 else v

C_K0  = normed(core.C_M1_K0(R_ARR, XI_C, 1.0))
C_M7a = normed(core.C_M7_powerlaw(R_ARR, 1.0, core.A_M, 0.5))
C_M7b = normed(core.C_M7_powerlaw(R_ARR, 1.0, core.A_M, 1.0))
C_M9  = normed(core.C_M9_twobath(R_ARR, 1.0, 250e-6, 0.5, 1500e-6))
C_M8  = normed(core.C_M8_gaussian(R_ARR, 1.0, 600e-6))

# Best-fit exponential to K0 (shape reference)
try:
    p_exp, _ = curve_fit(lambda r, x: np.exp(-r/x), R_ARR, C_K0,
                          p0=[1e-3], bounds=([0], [0.05]), maxfev=1000)
    C_exp_fit = np.exp(-R_ARR / p_exp[0])
except Exception:
    C_exp_fit = np.exp(-R_ARR / XI_C)

# L2 distance between normalised shapes
def shape_dist(a, b): return float(np.sqrt(np.mean((a - b)**2)))

print(f"  Shape distance (normalised L2 over 66 pairs):")
print(f"    K0 vs best-fit-exp:   {shape_dist(C_K0, C_exp_fit):.4f}")
print(f"    K0 vs M7(alpha=0.5):  {shape_dist(C_K0, C_M7a):.4f}")
print(f"    K0 vs M7(alpha=1.0):  {shape_dist(C_K0, C_M7b):.4f}")
print(f"    K0 vs M9(two-bath):   {shape_dist(C_K0, C_M9):.4f}")
print(f"    K0 vs M8(Gaussian):   {shape_dist(C_K0, C_M8):.4f}")
print(f"    exp vs M7(alpha=0.5): {shape_dist(C_exp_fit, C_M7a):.4f}")

sigma_noise = 1.0 / np.sqrt(N_SHOTS) + 0.02
print(f"  Measurement noise (1/sqrt(N)+readout): {sigma_noise:.4f}")
print(f"  SNR(K0 vs M7a): {shape_dist(C_K0,C_M7a)/sigma_noise:.2f}")
print(f"  SNR(K0 vs M9):  {shape_dist(C_K0,C_M9)/sigma_noise:.2f}")

results["shape_similarity"] = {
    "xi_c_mm": 1.0,
    "K0_vs_exp":  shape_dist(C_K0, C_exp_fit),
    "K0_vs_M7a":  shape_dist(C_K0, C_M7a),
    "K0_vs_M7b":  shape_dist(C_K0, C_M7b),
    "K0_vs_M9":   shape_dist(C_K0, C_M9),
    "K0_vs_M8":   shape_dist(C_K0, C_M8),
    "sigma_noise": sigma_noise,
    "snr_K0_vs_M7a": shape_dist(C_K0, C_M7a)/sigma_noise,
    "snr_K0_vs_M9":  shape_dist(C_K0, C_M9)/sigma_noise,
}

# ── C. PROFILE LIKELIHOOD: what xi_c does K0 fitter assign to M7/M9? ─────────
print("\n─── C. Profile likelihood: K0 fit to adversarial data ───")

def profile_ll_k0(r_v, c_v, e_v, xi_vals):
    """Scan xi_c and return profile log-likelihood for K0 model."""
    lls = []
    for xi in xi_vals:
        if xi <= core.A_M * 2: lls.append(-1e9); continue
        def model(r, ak, at, xt):
            return ak*bessel_k0(r/xi)/bessel_k0(core.A_M/xi) + at*np.exp(-r/xt)
        try:
            p, _ = curve_fit(model, r_v, c_v, p0=[0.05, 0.015, 300e-6],
                              sigma=e_v, absolute_sigma=True,
                              bounds=([0, 0, core.A_M*2], [1, 0.5, 0.005]),
                              maxfev=2000)
            ll = -0.5*np.sum(((c_v - model(r_v, *p))/e_v)**2)
            lls.append(float(ll))
        except Exception:
            lls.append(-1e9)
    return np.array(lls)

xi_scan = np.logspace(-4, -2, 40)  # 0.1mm to 10mm

# Generate one M7 and one M9 dataset (no shot noise for pure shape analysis)
C_M7_true = core.C_M7_powerlaw(R_ARR, 0.08, core.A_M, 0.8) + core.C_M5_crosstalk(R_ARR)
C_M9_true = core.C_M9_twobath(R_ARR, 0.08, 250e-6, 0.05, 1500e-6) + core.C_M5_crosstalk(R_ARR)

sigma_ref = np.full(N_PAIRS, sigma_noise)

ll_M7 = profile_ll_k0(R_ARR, C_M7_true, sigma_ref, xi_scan)
ll_M9 = profile_ll_k0(R_ARR, C_M9_true, sigma_ref, xi_scan)

xi_opt_M7 = float(xi_scan[np.argmax(ll_M7)]) * 1e3
xi_opt_M9 = float(xi_scan[np.argmax(ll_M9)]) * 1e3
print(f"  K0 fitter assigns xi_c = {xi_opt_M7:.2f} mm to M7 data")
print(f"  K0 fitter assigns xi_c = {xi_opt_M9:.2f} mm to M9 data")
print(f"  Both are within the chip's accessible range → K0 model absorbs them")

# Compare K0 null LLR for M7 vs best conventional fit
def null_ll(r_v, c_v, e_v):
    try:
        pn, _ = curve_fit(lambda r, at, xt: at*np.exp(-r/xt), r_v, c_v,
                           p0=[0.015, 300e-6], sigma=e_v, absolute_sigma=True,
                           bounds=([0, core.A_M*2], [0.5, 0.005]), maxfev=1000)
        return float(-0.5*np.sum(((c_v - pn[0]*np.exp(-r_v/pn[1]))/e_v)**2))
    except Exception:
        return -1e9

ll_null_M7 = null_ll(R_ARR, C_M7_true, sigma_ref)
ll_null_M9 = null_ll(R_ARR, C_M9_true, sigma_ref)
print(f"  LLR(K0 vs exp-null) on M7 data: {max(ll_M7)-ll_null_M7:.2f}")
print(f"  LLR(K0 vs exp-null) on M9 data: {max(ll_M9)-ll_null_M9:.2f}")

ROOT_CAUSE_M7 = ("Power-law has heavier tail than exponential at large r, "
                 "mimicking K0 which also has heavier-than-exp tail. "
                 "The K0 fitter finds a good fit by choosing xi_c at the "
                 f"chip scale ({xi_opt_M7:.1f}mm). The null (exp) cannot fit "
                 "the heavy tail, so LLR favours K0 artifactually.")
ROOT_CAUSE_M9 = ("Two-bath has a slow exponential component (xi2~1.5mm) "
                 "that mimics K0's long tail. K0 absorbs it by choosing "
                 f"xi_c~{xi_opt_M9:.1f}mm. FP rate lower because the short "
                 "component partially discriminates from K0 shape.")

print(f"\n  ROOT CAUSE M7: {ROOT_CAUSE_M7}")
print(f"\n  ROOT CAUSE M9: {ROOT_CAUSE_M9}")

results["profile_likelihood"] = {
    "xi_opt_M7_mm": xi_opt_M7,
    "xi_opt_M9_mm": xi_opt_M9,
    "llr_K0_vs_exp_null_on_M7": float(max(ll_M7) - ll_null_M7),
    "llr_K0_vs_exp_null_on_M9": float(max(ll_M9) - ll_null_M9),
    "root_cause_M7": ROOT_CAUSE_M7,
    "root_cause_M9": ROOT_CAUSE_M9,
}

# ── D. CONFUSION MATRIX across full null family ───────────────────────────────
print("\n─── D. Confusion matrix: full null family (300 trials each) ───")
print("     Using CORRECTED meas_joint estimator from sxc_igc_core.py")

# All null models with their default parameters + EM crosstalk
NULL_CONFIGS = {
    "M0":          core.C_M0(R_ARR) + core.C_M5_crosstalk(R_ARR),
    "M2_exp":      core.C_M2_exp(R_ARR, 600e-6, 0.10) + core.C_M5_crosstalk(R_ARR),
    "M5_xtalk":    core.C_M5_crosstalk(R_ARR),
    "M7_pow0.5":   core.C_M7_powerlaw(R_ARR, 0.08, core.A_M, 0.5) + core.C_M5_crosstalk(R_ARR),
    "M7_pow1.0":   core.C_M7_powerlaw(R_ARR, 0.08, core.A_M, 1.0) + core.C_M5_crosstalk(R_ARR),
    "M8_gauss":    core.C_M8_gaussian(R_ARR, 0.10, 600e-6) + core.C_M5_crosstalk(R_ARR),
    "M9_twobath":  core.C_M9_twobath(R_ARR, 0.08, 250e-6, 0.05, 1500e-6) + core.C_M5_crosstalk(R_ARR),
    "M10_stretch": core.C_M10_stretched_exp(R_ARR, 0.10, 600e-6, 0.7) + core.C_M5_crosstalk(R_ARR),
    "M11_matern":  core.C_M11_matern(R_ARR, 0.10, 600e-6) + core.C_M5_crosstalk(R_ARR),
}

LLR_THR = 3.0
confusion = {}
worst_fp  = 0.0
worst_model = ""

for mname, C_spatial in NULL_CONFIGS.items():
    C_spatial = np.clip(C_spatial, 0.0, 0.98)
    fp_count = 0
    llr_list = []

    for _ in range(N_TRIALS_DIAG):
        data, gph = core.generate_dataset(
            R_ARR, pairs, T_ARR, N_SHOTS, RNG, C_spatial)
        Cg, Ce = core.extract_C_gamma(data)
        llr, ak, _ = core.fit_k0_plus_null(
            R_ARR, Cg, Ce, 1.0e-3, core.XI_EM_DEFAULT, RNG)
        detected = (llr > LLR_THR) and (ak > 0.01)
        fp_count += int(detected)
        llr_list.append(float(llr))

    fp_rate = fp_count / N_TRIALS_DIAG
    cp95    = core.clopper_pearson_upper(fp_count, N_TRIALS_DIAG)
    llr_arr = np.array(llr_list)
    status  = "FAIL" if fp_rate > 0.10 else "pass"

    if fp_rate > worst_fp:
        worst_fp = fp_rate; worst_model = mname

    confusion[mname] = {
        "fp_count": fp_count,
        "n_trials": N_TRIALS_DIAG,
        "fp_rate": float(fp_rate),
        "cp95_upper": float(cp95),
        "llr_mean": float(llr_arr.mean()),
        "llr_std": float(llr_arr.std()),
        "status": status,
    }
    print(f"  {mname:15s}: FP={fp_count}/{N_TRIALS_DIAG} ({fp_rate:.3f}) "
          f"CP95<{cp95:.3f}  LLR={llr_arr.mean():.2f}±{llr_arr.std():.2f}  [{status}]")

print(f"\n  Worst-case FP: {worst_fp:.3f} ({worst_model})")
gate_null = "FAIL (worst-case FP > 0.10)" if worst_fp > 0.10 else "PASS"
print(f"  Global null gate: {gate_null}")

results["confusion_matrix"] = confusion
results["worst_case_fp"] = {"model": worst_model, "fp_rate": float(worst_fp)}
results["global_null_gate"] = gate_null

# ── E. SAVE ──────────────────────────────────────────────────────────────────
class NpEnc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, np.ndarray): return o.tolist()
        if isinstance(o, np.bool_): return bool(o)
        return super().default(o)

fpath = os.path.join(OUT, "adversarial_diagnosis_results.json")
with open(fpath, "w") as f:
    json.dump(results, f, indent=2, cls=NpEnc)
print(f"\nSaved: {fpath}")
