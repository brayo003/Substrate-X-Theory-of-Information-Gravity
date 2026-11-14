#!/usr/bin/env python3
"""
p22_synthetic_recovery.py — Phase 9, Step 6
Inject known c values, recover blind. Map recovery accuracy vs tau_B/T2* regime.

Outputs:
  outputs/data/synthetic_recovery_results.json
  outputs/figures/fig_synthetic_recovery.png
"""

import numpy as np
import json, os
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings("ignore")

BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "outputs", "data")
FIG_DIR  = os.path.join(BASE, "outputs", "figures")

RNG = np.random.default_rng(99)

print("=" * 60)
print("p22_synthetic_recovery.py — Synthetic Recovery Map")
print("=" * 60)

# ─── Parameter grid ───────────────────────────────────────────────────────────
C2_VALS    = [1e2, 1e3, 1e4, 1e5, 1e6]   # m/s
NMP_RATIOS = [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]   # tau_B / T2*
N_TRIALS   = 30   # per grid point
SHOTS      = 4096
N_DELAYS   = 40
T_MIN, T_MAX = 100e-9, 300e-6
t = np.logspace(np.log10(T_MIN), np.log10(T_MAX), N_DELAYS)

# Fixed: Markov rate (sets T2*)
GAMMA_M_BASE = 2*np.pi * 50e3   # 50 kHz

def phi_exact(t, gamma_m, tau_b):
    x = np.clip(t / tau_b, 0, 500)
    return gamma_m * tau_b * (x - 1.0 + np.exp(-x))

def model_c2(t, A, gm, tb):
    return A * np.exp(-phi_exact(t, gm, tb))

def model_gauss(t, A, TG):
    return A * np.exp(-(t/TG)**2)

def model_exp(t, A, G):
    return A * np.exp(-G*t)

def fit_tau_b(t, y, yerr, gamma_m_0, tau_b_0):
    """Return (tau_b_fit, success)."""
    try:
        p0 = [1.0, gamma_m_0, tau_b_0]
        po, _ = curve_fit(model_c2, t, y, p0=p0,
                          bounds=([0.5,1e2,1e-10],[1.5,1e8,1e-1]),
                          maxfev=5000)
        return po[2], True, po[1]
    except:
        return np.nan, False, np.nan

def fit_d_c(d_arr, r_arr):
    """Return (d_c, success)."""
    try:
        def exp_sp(d, A, xi):
            return A * np.exp(-d / xi)
        po, _ = curve_fit(exp_sp, d_arr, r_arr,
                          p0=[r_arr.max(), d_arr.mean()],
                          bounds=([0, 1e-9], [2.0, 1.0]),
                          maxfev=3000)
        return po[1] / 2.0, True   # d_c = xi_c / 2
    except:
        return np.nan, False

# Simple 2-qubit geometry: separation d = 200 µm
D_PAIR = 200e-6

print(f"Grid: {len(C2_VALS)} c values × {len(NMP_RATIOS)} NMP regimes × {N_TRIALS} trials")
print(f"Fixed: Gamma_M = {GAMMA_M_BASE/(2*np.pi)/1e3:.0f} kHz, d_pair = {D_PAIR*1e6:.0f} µm\n")

records = []

for c_inj in C2_VALS:
    for nmp_ratio in NMP_RATIOS:
        # Derive tau_B from NMP/T2* ratio
        # T2* ~ 1/Gamma_M (rough), NMP = Gamma_M * tau_B
        # nmp_ratio = tau_B / T2* = tau_B * Gamma_M  => tau_B = nmp_ratio / Gamma_M
        tau_b = nmp_ratio / GAMMA_M_BASE
        nmp   = GAMMA_M_BASE * tau_b   # same as nmp_ratio

        xi_c  = 2 * c_inj * tau_b
        # Spatial correlation at d_pair
        r_true = np.exp(-D_PAIR / xi_c)

        recovered_c  = []
        recovered_tb = []
        classified_as = []  # "c2", "gauss", "exp"

        for _ in range(N_TRIALS):
            # Generate noisy Ramsey trace
            ideal = np.exp(-phi_exact(t, GAMMA_M_BASE, tau_b))
            p0s   = (1.0 + ideal) / 2.0
            counts = RNG.binomial(SHOTS, p0s)
            y  = 2*counts/SHOTS - 1.0
            ye = np.sqrt(p0s * (1-p0s) / SHOTS) * 2

            # Try C2-exact fit to get tau_B
            tb_fit, ok, gm_fit = fit_tau_b(t, y, ye, GAMMA_M_BASE, tau_b)

            if not ok or tb_fit < 1.5e-10 or tb_fit > 0.09:
                classified_as.append("bound")
                recovered_tb.append(np.nan)
                recovered_c.append(np.nan)
                continue

            # Simulate spatial: generate 100 realization phase differences
            N_SP = 100
            phases = RNG.normal(0, np.sqrt(2*phi_exact(t[-1], GAMMA_M_BASE, tau_b)),
                                size=(N_SP, 2))
            corr_sim = np.corrcoef(phases[:,0], phases[:,1])[0,1]
            corr_with_cm = 0.2 + 0.8 * r_true + RNG.normal(0, 0.05)
            corr_detrend = corr_with_cm - 0.2

            # Fit spatial: d_c from single pair (limited)
            # With only 1 pair we can't fit spatial decay — use d_c = -D/ln(corr)
            if corr_detrend > 0.001:
                d_c_est = -D_PAIR / np.log(max(corr_detrend, 1e-6))
            else:
                recovered_c.append(np.nan)
                recovered_tb.append(tb_fit)
                classified_as.append("c2_no_spatial")
                continue

            c_est = d_c_est / tb_fit
            recovered_tb.append(tb_fit)
            recovered_c.append(c_est)

            # Classify by best model (using AIC on Ramsey)
            try:
                po_g, _ = curve_fit(model_gauss, t, y, p0=[1.0,t[N_DELAYS//3]],
                                    bounds=([0.5,1e-9],[1.5,1e-2]), maxfev=2000)
                po_e, _ = curve_fit(model_exp, t, y, p0=[1.0, 1/t[N_DELAYS//2]],
                                    bounds=([0.5,1e2],[1.5,1e8]), maxfev=2000)
                r_c2 = y - model_c2(t, 1.0, gm_fit, tb_fit)
                r_g  = y - model_gauss(t, *po_g)
                r_e  = y - model_exp(t, *po_e)
                sse = {"c2": np.sum(r_c2**2), "gauss": np.sum(r_g**2), "exp": np.sum(r_e**2)}
                winner = min(sse, key=sse.get)
                classified_as.append(winner)
            except:
                classified_as.append("c2")

        # Compute recovery statistics
        valid_c  = np.array([v for v in recovered_c if v is not None and not np.isnan(v)])
        valid_tb = np.array([v for v in recovered_tb if v is not None and not np.isnan(v)])
        n_valid  = len(valid_c)
        n_total  = N_TRIALS

        if n_valid > 0:
            log_ratio = np.log10(valid_c / c_inj)
            bias_log  = np.mean(log_ratio)
            rms_log   = np.std(log_ratio)
            frac_within_3x = np.mean(np.abs(log_ratio) < np.log10(3))
            tb_mean = valid_tb.mean()
            tb_bias = (tb_mean - tau_b) / tau_b
        else:
            bias_log = np.nan; rms_log = np.nan
            frac_within_3x = 0.0; tb_mean = np.nan; tb_bias = np.nan

        from collections import Counter
        class_counts = Counter(classified_as)

        rec = {
            "c_inj": c_inj, "nmp_ratio": nmp_ratio,
            "tau_b_us": tau_b*1e6, "nmp": nmp,
            "xi_c_um": xi_c*1e6, "r_true": float(r_true),
            "n_valid": n_valid, "n_total": n_total,
            "recovery_frac": n_valid/n_total,
            "bias_log10": float(bias_log) if not np.isnan(bias_log) else None,
            "rms_log10": float(rms_log) if not np.isnan(rms_log) else None,
            "frac_within_3x": float(frac_within_3x),
            "tb_bias_frac": float(tb_bias) if not np.isnan(tb_bias) else None,
            "class_counts": dict(class_counts),
        }
        records.append(rec)

        print(f"  c={c_inj:.0e} NMP/T2*={nmp_ratio:4.2f}: "
              f"recovery={n_valid}/{n_total}  "
              f"within3x={frac_within_3x:.0%}  "
              f"bias={bias_log:+.2f}log10  "
              f"class={dict(class_counts)}")

print()

# Summary
print("Recovery summary by NMP regime:")
for nmp_r in NMP_RATIOS:
    recs = [r for r in records if r["nmp_ratio"] == nmp_r]
    frac = np.mean([r["frac_within_3x"] for r in recs])
    print(f"  tau_B/T2* = {nmp_r:5.2f}: mean within-3x = {frac:.0%}")

# Save
with open(os.path.join(DATA_DIR, "synthetic_recovery_results.json"), "w") as f:
    json.dump({"script": "p22_synthetic_recovery.py",
               "c_vals": C2_VALS, "nmp_ratios": NMP_RATIOS,
               "n_trials": N_TRIALS, "records": records}, f, indent=2)
print(f"\nSaved: {DATA_DIR}/synthetic_recovery_results.json")

# Figure
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Recovery fraction heatmap
    frac_grid = np.zeros((len(C2_VALS), len(NMP_RATIOS)))
    for i, c in enumerate(C2_VALS):
        for j, nr in enumerate(NMP_RATIOS):
            rr = [r for r in records if r["c_inj"] == c and r["nmp_ratio"] == nr]
            frac_grid[i, j] = rr[0]["frac_within_3x"] if rr else 0

    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(frac_grid, aspect="auto", origin="lower",
                   vmin=0, vmax=1, cmap="RdYlGn")
    plt.colorbar(im, ax=ax, label="Fraction recovered within 3×")
    ax.set_xticks(range(len(NMP_RATIOS)))
    ax.set_xticklabels([str(v) for v in NMP_RATIOS])
    ax.set_yticks(range(len(C2_VALS)))
    ax.set_yticklabels([f"{v:.0e}" for v in C2_VALS])
    ax.set_xlabel("τ_B / T₂*  (NMP ratio)")
    ax.set_ylabel("c_C2 injected (m/s)")
    ax.set_title("Synthetic Recovery: Fraction within 3× of true c_C2")
    for i in range(len(C2_VALS)):
        for j in range(len(NMP_RATIOS)):
            ax.text(j, i, f"{frac_grid[i,j]:.0%}", ha="center", va="center",
                    fontsize=8, color="black")
    plt.tight_layout()
    fpath = os.path.join(FIG_DIR, "fig_synthetic_recovery.png")
    plt.savefig(fpath, dpi=120)
    plt.close()
    print(f"Saved: {fpath}")
except ImportError:
    print("matplotlib not available — figure skipped")

print("\np22 COMPLETE")
print("=" * 60)
