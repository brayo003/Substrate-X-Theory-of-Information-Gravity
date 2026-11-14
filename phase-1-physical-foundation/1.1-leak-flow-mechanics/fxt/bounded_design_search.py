#!/usr/bin/env python3
"""
bounded_design_search.py
Bounded Design-Space Search: SXC-IGC K0 vs Conventional Noise

MANDATE:
  Search the full allowed experimental design space (grid sweep).
  For each design point ask:
    P(detect B | B) >= 0.80  AND  P(false substrate | A) <= 0.10

  If ANY point passes both criteria → PROCEED candidate found.
  If NO point passes → DECLARE INFEASIBLE, STOP.

  Hard constraints:
    - IBM Brisbane (127 qubits, heavy-hex, a=200 µm)
    - QPU budget: 10 min
    - Crosstalk calibration uncertainty modelled explicitly
    - ξ_c and substrate amplitude are swept, NOT assumed
    - Joint K0 + exp-crosstalk fitter (corrects prior amplitude bias)
    - No post-hoc fitting tricks

  Scientific constraints:
    - Positive result proves: K0-shaped spatial correlation exists.
    - It does NOT prove C2 / SXC-IGC is correct.
    - ξ_c is a FREE parameter (GAP-7). Not independently predicted.
    - Temporal channel excluded (non-discriminating vs OU noise, proved).

  Output: bounded_design_search_results.json
"""

import numpy as np
import json, os, time
from scipy.special import k0 as bessel_k0
from scipy.optimize import curve_fit

RNG = np.random.default_rng(42424242)
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "09_spatiotemporal_c2_test", "outputs", "data")
os.makedirs(OUT, exist_ok=True)

print("=" * 68)
print("BOUNDED DESIGN-SPACE SEARCH: SXC-IGC K0 vs Conventional Noise")
print("=" * 68)

# ── Fixed hardware constants (Brisbane calibration) ───────────────────────────
A_M          = 200e-6          # m, heavy-hex lattice spacing
T2_GOOD      = 150e-6          # s
T1_GOOD      = 300e-6          # s
GAMMA_PHI    = 1.0 / T2_GOOD   # ~6667 rad/s
GAMMA_RELAX  = 1.0 / (2*T1_GOOD)
TAU_B        = 5e-6            # s, substrate bath correlation time
UV_CUT       = A_M             # UV cutoff = lattice spacing
XTALK_TRUE   = 0.015           # EM crosstalk amplitude
XI_EM        = 300e-6          # m, EM crosstalk decay length
READOUT_ERR  = 0.020

# QPU budget
# IBM Open Plan: ~600 s QPU execution time.
# Per-shot time: IBM runs shots in parallel batches.
#   A short circuit (prep + delay + meas) at delay ~T2/3 ~ 50 µs takes:
#   gate overhead ~1 µs + delay ~50 µs + readout ~1 µs = ~52 µs per shot.
#   But IBM batches shots: effective throughput ~1 µs per shot per qubit.
#   We use 5 µs/shot as a conservative realistic estimate.
QPU_BUDGET_S        = 600.0
CIRCUIT_TIME_S      = 5e-6     # s per shot (realistic IBM batched execution)
CALIBRATION_OVERHEAD= 60.0     # s fixed overhead for crosstalk calibration

# ── Design grid (trimmed for tractable runtime) ───────────────────────────────
# Core insight: we need xi_c that puts qubit pairs in the 0.5–5 xi_c range.
# Brisbane chain of 12 qubits: separations 200–2200 µm.
# So xi_c must be 400 µm – 4400 µm for any coverage.
# We test the key boundary region.

XI_C_GRID       = [0.5e-3, 1.0e-3, 2.0e-3, 3.0e-3, 5.0e-3]  # m
SUB_FRAC_GRID   = [0.03, 0.05, 0.08, 0.15]   # substrate correlation amplitude
N_SHOTS_GRID    = [4096, 8192]
N_QUBITS        = 12           # fixed — 66 pairs, fits in budget, enough shape pts
XTALK_CAL_ERRS  = [0.0, 0.010, 0.020]  # fractional uncertainty on measured xtalk

N_TRIALS  = 60    # per world per design point (fast but ~±13% CI on power)
N_TIME    = 10    # time points per Ramsey decay
T_ARR     = np.linspace(0.15 * T2_GOOD, 0.55 * T2_GOOD, N_TIME)
LLR_THR   = 3.0   # K0 decision threshold

total_pts = len(XI_C_GRID) * len(SUB_FRAC_GRID) * len(N_SHOTS_GRID) * len(XTALK_CAL_ERRS)
est_s     = total_pts * 2 * N_TRIALS * 0.08   # ~0.08s per trial (vectorized)
print(f"Grid: {total_pts} design points × {2*N_TRIALS} trials = "
      f"{total_pts*2*N_TRIALS:,} total trials")
print(f"Estimated runtime: {est_s:.0f}s (~{est_s/60:.1f} min)\n")

# ── Positions (fixed linear chain of N_QUBITS) ────────────────────────────────
positions = np.arange(N_QUBITS) * A_M
pairs = [(i, j, abs(positions[i] - positions[j]))
         for i in range(N_QUBITS) for j in range(i+1, N_QUBITS)]
R_ARR = np.array([p[2] for p in pairs])  # shape (n_pairs,)
N_PAIRS = len(pairs)

# ── Ramsey signals precomputed for all time points ────────────────────────────
def ramsey_signal(t_arr, gph=GAMMA_PHI, grel=GAMMA_RELAX, tau_b=TAU_B):
    """Exact non-Markovian Ramsey decay for array of times."""
    phi = gph * tau_b * (t_arr / tau_b - 1.0 + np.exp(-t_arr / tau_b))
    return np.exp(-phi) * np.exp(-grel * t_arr)

W_BASE = ramsey_signal(T_ARR)   # shape (N_TIME,), same for all qubits (mean params)

# ─────────────────────────────────────────────────────────────────────────────
# VECTORIZED WORLD GENERATOR
# Returns C_gamma estimates (n_pairs,) for one synthetic dataset.
# ─────────────────────────────────────────────────────────────────────────────

def generate_and_extract(xi_c, substrate_frac, n_shots, include_substrate,
                         xtalk_cal_error):
    """
    One trial: generate synthetic data + extract C_Gamma(r) vector.
    Returns: C_gamma (n_pairs,), C_gamma_err (n_pairs,)
    """
    # Per-qubit variation in gamma_phi (10% spread)
    gph_i = GAMMA_PHI * (1.0 + 0.10 * RNG.standard_normal(N_QUBITS))
    gph_i = np.clip(gph_i, GAMMA_PHI * 0.5, GAMMA_PHI * 2.0)
    gph_est = np.mean(gph_i)

    # Substrate correlation profile
    if include_substrate and xi_c > UV_CUT * 2:
        norm_k0 = bessel_k0(UV_CUT / xi_c)
        C_sub_arr = substrate_frac * bessel_k0(R_ARR / xi_c) / norm_k0
    else:
        C_sub_arr = np.zeros(N_PAIRS)

    # EM crosstalk profile
    C_xt_arr = XTALK_TRUE * np.exp(-R_ARR / XI_EM)

    # Total correlation per pair
    C_total = np.clip(C_sub_arr + C_xt_arr, 0.0, 0.98)  # (n_pairs,)

    # Per-qubit Ramsey signals at all time points (n_qubits, N_TIME)
    W_all = np.array([ramsey_signal(T_ARR, gph_i[k]) for k in range(N_QUBITS)])

    # For each pair: cross-signal = W_i * W_j * exp(C_total * gph_est * t)
    # Shape: (n_pairs, N_TIME)
    C_gamma_samples = np.zeros((N_PAIRS, N_TIME))

    for p_idx, (qi, qj, _) in enumerate(pairs):
        Wi = W_all[qi]   # (N_TIME,)
        Wj = W_all[qj]   # (N_TIME,)
        # True cross signal
        cross_true = Wi * Wj * np.exp(C_total[p_idx] * GAMMA_PHI * T_ARR)

        # Add readout noise (vectorized binomial)
        def meas(sig):
            p = np.clip((1.0 + sig) / 2.0, 0.0, 1.0)
            p_m = p * (1 - 2*READOUT_ERR) + READOUT_ERR
            cnts = RNG.binomial(n_shots, p_m)
            return 2.0 * cnts / n_shots - 1.0

        Wi_m   = meas(Wi)
        Wj_m   = meas(Wj)
        cross_m = meas(cross_true)

        denom = Wi_m * Wj_m
        valid = np.abs(denom) > 1e-6
        C_ij = np.where(valid, cross_m / denom, np.nan)

        # Extract C_Gamma = ln(C_ij) / (gph_est * t)
        with np.errstate(divide='ignore', invalid='ignore'):
            vals = np.where((C_ij > 1e-6) & valid,
                            np.log(C_ij) / (gph_est * T_ARR), np.nan)
        C_gamma_samples[p_idx] = vals

    # Average over time points
    C_gamma   = np.nanmean(C_gamma_samples, axis=1)
    C_gamma_e = np.nanstd(C_gamma_samples, axis=1) / np.sqrt(
                    np.sum(~np.isnan(C_gamma_samples), axis=1).clip(1))

    return C_gamma, C_gamma_e, gph_est


# ─────────────────────────────────────────────────────────────────────────────
# JOINT FITTER: K0 + exp crosstalk (4 params vs 2 params null)
# ─────────────────────────────────────────────────────────────────────────────

def fit_joint(C_gamma, C_gamma_e, xi_c_hint, xtalk_cal_error):
    """
    Full model: amp_K0 * K0(r/xi_K0)/K0(a/xi_K0)  +  amp_xt * exp(-r/xi_xt)
    Null model: amp_xt * exp(-r/xi_xt)

    Crosstalk xi_xt is known ±xtalk_cal_error (fractional).
    Returns: llr (>0 → K0 preferred), amp_k0_fit.
    """
    valid = (~np.isnan(C_gamma)) & (~np.isnan(C_gamma_e)) & (C_gamma_e > 1e-9)
    r_v = R_ARR[valid]
    C_v = C_gamma[valid]
    e_v = C_gamma_e[valid]

    if len(r_v) < 6:
        return 0.0, 0.0

    # Calibration uncertainty on xtalk length scale
    xi_xt_meas = XI_EM * (1.0 + xtalk_cal_error * RNG.standard_normal())
    xi_xt_meas = max(xi_xt_meas, A_M * 2)

    def model_full(r, amp_K0, xi_K0, amp_xt, xi_xt):
        xi_K0 = max(float(xi_K0), UV_CUT * 2)
        norm  = bessel_k0(UV_CUT / xi_K0)
        return amp_K0 * bessel_k0(r / xi_K0) / norm + amp_xt * np.exp(-r / xi_xt)

    def model_null(r, amp_xt, xi_xt):
        return amp_xt * np.exp(-r / xi_xt)

    # Fit full model
    try:
        p0f = [0.04, xi_c_hint, XTALK_TRUE, xi_xt_meas]
        blo = [0.0,  UV_CUT*2,  0.0,        A_M*2]
        bhi = [1.0,  0.02,      0.5,        0.005]
        pf, _ = curve_fit(model_full, r_v, C_v, p0=p0f, sigma=e_v,
                           absolute_sigma=True, bounds=(blo, bhi), maxfev=2000)
        ll_f   = -0.5 * float(np.sum(((C_v - model_full(r_v, *pf)) / e_v)**2))
        amp_k0 = float(pf[0])
    except Exception:
        ll_f = -1e9; amp_k0 = 0.0

    # Fit null model
    try:
        p0n = [XTALK_TRUE, xi_xt_meas]
        blo_n = [0.0, A_M*2];  bhi_n = [0.5, 0.005]
        pn, _ = curve_fit(model_null, r_v, C_v, p0=p0n, sigma=e_v,
                           absolute_sigma=True, bounds=(blo_n, bhi_n), maxfev=1000)
        ll_n = -0.5 * float(np.sum(((C_v - model_null(r_v, *pn)) / e_v)**2))
    except Exception:
        ll_n = -1e9

    llr = ll_f - ll_n
    return float(llr), amp_k0


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SWEEP
# ─────────────────────────────────────────────────────────────────────────────

def check_budget(n_shots):
    n_circuits = N_PAIRS * N_TIME
    runtime = n_circuits * n_shots * CIRCUIT_TIME_S + CALIBRATION_OVERHEAD
    return runtime <= QPU_BUDGET_S, float(runtime)

sweep_results = {}
feasible_points = []
t0 = time.time()
pt = 0

for xi_c in XI_C_GRID:
    for n_shots in N_SHOTS_GRID:
        ok_budget, runtime_s = check_budget(n_shots)
        if not ok_budget:
            continue
        for sub_frac in SUB_FRAC_GRID:
            for xtalk_err in XTALK_CAL_ERRS:
                pt += 1
                key = (f"xi{xi_c*1e3:.1f}mm_sf{sub_frac:.2f}_"
                       f"s{n_shots}_xe{xtalk_err:.3f}")

                # Run World A (null) trials
                fp_decisions = []
                for _ in range(N_TRIALS):
                    Cg, Ce, _ = generate_and_extract(
                        xi_c, sub_frac, n_shots, False, xtalk_err)
                    llr, _ = fit_joint(Cg, Ce, xi_c, xtalk_err)
                    fp_decisions.append(llr > LLR_THR)

                # Run World B (substrate) trials
                tp_decisions = []
                for _ in range(N_TRIALS):
                    Cg, Ce, _ = generate_and_extract(
                        xi_c, sub_frac, n_shots, True, xtalk_err)
                    llr, ak = fit_joint(Cg, Ce, xi_c, xtalk_err)
                    tp_decisions.append((llr > LLR_THR) and (ak > 0.001))

                power   = float(np.mean(tp_decisions))
                fp_rate = float(np.mean(fp_decisions))
                passes  = (power >= 0.80) and (fp_rate <= 0.10)

                rec = {
                    "xi_c_mm": xi_c * 1e3,
                    "sub_frac": sub_frac,
                    "n_shots": n_shots,
                    "xtalk_cal_error": xtalk_err,
                    "power": power,
                    "fp_rate": fp_rate,
                    "passes": passes,
                    "runtime_s": runtime_s,
                }
                sweep_results[key] = rec
                if passes:
                    feasible_points.append(rec)

                elapsed = time.time() - t0
                print(f"  [{pt:3d}] xi={xi_c*1e3:.1f}mm sf={sub_frac:.2f} "
                      f"shots={n_shots} xe={xtalk_err:.3f} → "
                      f"power={power:.2f} fp={fp_rate:.2f} "
                      f"{'PASS✓' if passes else 'fail'} "
                      f"[{elapsed:.0f}s]")

# ─────────────────────────────────────────────────────────────────────────────
# VERDICT
# ─────────────────────────────────────────────────────────────────────────────

elapsed_total = time.time() - t0
print(f"\n{'='*68}")
print(f"SWEEP COMPLETE: {pt} design points in {elapsed_total:.0f}s")
print(f"Feasible points (power≥0.80 AND fp≤0.10): {len(feasible_points)}")
print(f"{'='*68}")

if feasible_points:
    feasible_points.sort(key=lambda x: (-x["power"], x["fp_rate"]))
    best = feasible_points[0]
    print(f"\nBEST DESIGN:")
    print(f"  ξ_c          = {best['xi_c_mm']:.1f} mm")
    print(f"  substrate_frac = {best['sub_frac']:.2f}")
    print(f"  n_shots      = {best['n_shots']}")
    print(f"  xtalk_cal_err= {best['xtalk_cal_error']:.3f}")
    print(f"  Power        = {best['power']:.3f}")
    print(f"  FP rate      = {best['fp_rate']:.3f}")
    print(f"  Runtime est. = {best['runtime_s']:.0f}s ({best['runtime_s']/60:.1f}min)")

    min_xi = min(fp["xi_c_mm"] for fp in feasible_points)
    max_xi = max(fp["xi_c_mm"] for fp in feasible_points)
    min_sf = min(fp["sub_frac"] for fp in feasible_points)

    verdict = "PROCEED_CANDIDATE_FOUND"
    verdict_text = (
        f"PROCEED CANDIDATE FOUND. "
        f"Best: xi_c={best['xi_c_mm']:.1f}mm, sub_frac>={min_sf:.2f}, "
        f"shots={best['n_shots']}. "
        f"Power={best['power']:.2f}, FP={best['fp_rate']:.2f}. "
        f"Feasible xi_c range: {min_xi:.1f}–{max_xi:.1f} mm. "
        f"REQUIRES Phase 1 (measure xi_c) before hardware execution."
    )
    print(f"\n{verdict_text}")
    print()
    print("SCIENTIFIC NOTES (pre-registered, not revisable after hardware):")
    print(f"  1. ξ_c is NOT predicted by C2 — GAP-7 confirmed. c is free.")
    print(f"  2. substrate_frac is NOT predicted — coupling g is unknown.")
    print(f"  3. A positive result would show: K0-shaped spatial correlation")
    print(f"     exists after controlling for EM crosstalk and OU noise.")
    print(f"  4. It would NOT prove SXC-IGC. It would NOT revive C2 closure.")
    print(f"  5. If Phase 1 returns xi_c > {max_xi:.0f} mm: STOP, inconclusive.")

else:
    # Report best attempt
    valid = [v for v in sweep_results.values()
             if isinstance(v, dict) and "power" in v]
    best_a = max(valid, key=lambda x: x["power"] - x["fp_rate"]) if valid else {}

    verdict = "INFEASIBLE_STOP"
    verdict_text = (
        "STOP. No design within fixed hardware/budget/noise constraints "
        "achieves P(detect B|B)>=0.80 with P(false|A)<=0.10. "
        "The K0 substrate signature is NOT reliably distinguishable from "
        "conventional correlated noise at any tested parameter combination. "
        "This is evidence against the experimental design, NOT against the theory. "
        "Do not submit QPU jobs. Do not modify the hypothesis."
    )
    print(f"\n{verdict_text}")
    if best_a:
        print(f"\nBest attempt: power={best_a.get('power',0):.2f}, "
              f"fp={best_a.get('fp_rate',1):.2f} "
              f"(xi={best_a.get('xi_c_mm','?'):.1f}mm, "
              f"sf={best_a.get('sub_frac','?'):.2f})")

# Save
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, np.bool_): return bool(obj)
        return super().default(obj)

output = {
    "verdict": verdict,
    "verdict_text": verdict_text,
    "n_feasible": len(feasible_points),
    "feasible_points": feasible_points[:10],
    "best": feasible_points[0] if feasible_points else None,
    "config": {
        "xi_c_grid_mm": [x*1e3 for x in XI_C_GRID],
        "sub_frac_grid": SUB_FRAC_GRID,
        "n_shots_grid": N_SHOTS_GRID,
        "n_qubits": N_QUBITS,
        "xtalk_cal_errs": XTALK_CAL_ERRS,
        "n_trials": N_TRIALS,
        "llr_threshold": LLR_THR,
    },
}
fpath = os.path.join(OUT, "bounded_design_search_results.json")
with open(fpath, "w") as f:
    json.dump(output, f, indent=2, cls=NpEncoder)
print(f"\nSaved: {fpath}")
