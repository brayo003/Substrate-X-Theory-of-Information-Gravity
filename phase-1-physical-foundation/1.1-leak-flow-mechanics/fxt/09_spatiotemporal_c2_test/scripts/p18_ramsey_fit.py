#!/usr/bin/env python3
"""
p18_ramsey_fit.py — Phase 9, Step 2
Fit 4 models to each qubit's Ramsey trace; extract tau_B with uncertainty.

Models:
  1. Exponential:    exp(-Gamma*t)
  2. Gaussian:       exp(-(t/T_G)^2)
  3. Stretched-exp:  exp(-(t/T_S)^beta)
  4. C2-exact:       exp(-Phi(t; Gamma_M, tau_B))  [EXACT-PHI]

Outputs:
  outputs/data/ramsey_fit_results.npz
  outputs/data/ramsey_fit_results.json
  outputs/figures/fig_ramsey_traces.png
  outputs/figures/fig_tau_b_distribution.png
"""

import numpy as np
import json, os
from scipy.optimize import curve_fit, minimize
from scipy.special import gammaln
import warnings
warnings.filterwarnings("ignore")

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE, "outputs", "data")
FIG_DIR   = os.path.join(BASE, "outputs", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ─── Load simulation data ─────────────────────────────────────────────────────
d = np.load(os.path.join(DATA_DIR, "ramsey_sim.npz"))
t            = d["t_delays"]
traces       = d["ramsey_traces"]      # (n_qubits, n_delays)
trace_std    = d["ramsey_std"]
N_Q          = int(d["n_qubits"])
TAU_B_INJ    = float(d["tau_b_inj"])
GAMMA_M_INJ  = float(d["gamma_m_inj"])
gamma_m_pq   = d["gamma_m_per_qubit"]
tau_b_pq     = d["tau_b_per_qubit"]

print("=" * 60)
print("p18_ramsey_fit.py — Ramsey Model Fitting")
print("=" * 60)
print(f"Loaded {N_Q} qubits, {len(t)} delay points")
print()

# ─── Model definitions ───────────────────────────────────────────────────────
def phi_exact(t, gamma_m, tau_b):
    x = np.clip(t / tau_b, 0, 500)
    return gamma_m * tau_b * (x - 1.0 + np.exp(-x))

def model_exp(t, A, Gamma):
    return A * np.exp(-Gamma * t)

def model_gauss(t, A, T_G):
    return A * np.exp(-(t / T_G)**2)

def model_strexp(t, A, T_S, beta):
    return A * np.exp(-(t / T_S)**beta)

def model_c2exact(t, A, gamma_m, tau_b):
    return A * np.exp(-phi_exact(t, gamma_m, tau_b))

# ─── AIC/BIC helpers ─────────────────────────────────────────────────────────
def aic(residuals, k, sigma):
    n = len(residuals)
    sse = np.sum((residuals / sigma)**2)
    log_like = -0.5 * sse
    return 2*k - 2*log_like

def bic(residuals, k, sigma):
    n = len(residuals)
    sse = np.sum((residuals / sigma)**2)
    log_like = -0.5 * sse
    return k * np.log(n) - 2*log_like

# ─── Fit each qubit ──────────────────────────────────────────────────────────
results = []

for qi in range(N_Q):
    y    = traces[qi]
    yerr = trace_std[qi]
    res  = {"qubit": qi}

    # --- Model 1: Exponential ---
    try:
        p0 = [1.0, 1.0 / (t[len(t)//2])]
        popt, pcov = curve_fit(model_exp, t, y, p0=p0, sigma=yerr,
                               bounds=([0.5, 1e2], [1.5, 1e8]), maxfev=5000)
        resid = y - model_exp(t, *popt)
        res["exp"] = {"A": popt[0], "Gamma": popt[1],
                      "AIC": aic(resid, 2, yerr), "BIC": bic(resid, 2, yerr),
                      "T2star_us": 1e6/popt[1], "success": True}
    except Exception as e:
        res["exp"] = {"success": False, "error": str(e)}

    # --- Model 2: Gaussian ---
    try:
        p0 = [1.0, t[len(t)//3]]
        popt, pcov = curve_fit(model_gauss, t, y, p0=p0, sigma=yerr,
                               bounds=([0.5, 1e-8], [1.5, 1e-2]), maxfev=5000)
        resid = y - model_gauss(t, *popt)
        res["gauss"] = {"A": popt[0], "T_G_us": popt[1]*1e6,
                        "AIC": aic(resid, 2, yerr), "BIC": bic(resid, 2, yerr),
                        "success": True}
    except Exception as e:
        res["gauss"] = {"success": False, "error": str(e)}

    # --- Model 3: Stretched exponential ---
    try:
        p0 = [1.0, t[len(t)//3], 1.5]
        popt, pcov = curve_fit(model_strexp, t, y, p0=p0, sigma=yerr,
                               bounds=([0.5, 1e-8, 0.3], [1.5, 1e-2, 3.0]), maxfev=5000)
        resid = y - model_strexp(t, *popt)
        res["strexp"] = {"A": popt[0], "T_S_us": popt[1]*1e6, "beta": popt[2],
                         "AIC": aic(resid, 3, yerr), "BIC": bic(resid, 3, yerr),
                         "success": True}
    except Exception as e:
        res["strexp"] = {"success": False, "error": str(e)}

    # --- Model 4: C2 exact [EXACT-PHI] ---
    try:
        p0 = [1.0, gamma_m_pq[qi], tau_b_pq[qi]]
        popt, pcov = curve_fit(model_c2exact, t, y, p0=p0, sigma=yerr,
                               bounds=([0.5, 1e3, 1e-8], [1.5, 1e7, 1e-2]),
                               maxfev=10000)
        resid = y - model_c2exact(t, *popt)
        # tau_B uncertainty from covariance matrix
        perr = np.sqrt(np.diag(pcov)) if pcov is not None else [0, 0, 0]
        tau_b_fit = popt[2]
        tau_b_err = perr[2]
        # Check if tau_B hit bounds (parameter-bound fit)
        at_lower = tau_b_fit < 1.5e-8
        at_upper = tau_b_fit > 0.9e-2
        res["c2exact"] = {
            "A": popt[0], "gamma_m_kHz": popt[1]/(2*np.pi)/1e3,
            "tau_b_us": tau_b_fit*1e6,
            "tau_b_err_us": tau_b_err*1e6,
            "tau_b_at_bound": bool(at_lower or at_upper),
            "AIC": aic(resid, 3, yerr), "BIC": bic(resid, 3, yerr),
            "success": True
        }
    except Exception as e:
        res["c2exact"] = {"success": False, "error": str(e)}

    results.append(res)

    # Print summary
    print(f"Q{qi:02d}  inject: Γ={gamma_m_pq[qi]/(2*np.pi)/1e3:.1f}kHz  τ_B={tau_b_pq[qi]*1e6:.2f}µs")
    for mname in ["exp", "gauss", "strexp", "c2exact"]:
        r = res[mname]
        if r["success"]:
            bic_val = r["BIC"]
            extra = ""
            if mname == "c2exact":
                extra = f"  τ_B={r['tau_b_us']:.2f}±{r['tau_b_err_us']:.2f}µs"
                if r["tau_b_at_bound"]:
                    extra += " [AT BOUND]"
            print(f"    {mname:10s}: BIC={bic_val:8.1f}{extra}")
        else:
            print(f"    {mname:10s}: FAILED")
    print()

# ─── Model comparison summary ─────────────────────────────────────────────────
print("Model comparison — BIC winner per qubit:")
winners = []
for res in results:
    bic_vals = {}
    for m in ["exp", "gauss", "strexp", "c2exact"]:
        if res[m]["success"]:
            bic_vals[m] = res[m]["BIC"]
    if bic_vals:
        winner = min(bic_vals, key=bic_vals.get)
        winners.append(winner)
        best_bic = bic_vals[winner]
        delta_c2 = bic_vals.get("c2exact", np.nan) - best_bic
        print(f"  Q{res['qubit']:02d}: winner={winner:10s}  "
              f"ΔBIC(c2exact-best)={delta_c2:+.1f}")
    else:
        winners.append("none")

from collections import Counter
cnt = Counter(winners)
print(f"\nWinner counts: {dict(cnt)}")
n_c2_wins = cnt.get("c2exact", 0)
print(f"C2-exact wins: {n_c2_wins}/{N_Q} qubits")
print()

# ─── tau_B estimates from C2 fits ────────────────────────────────────────────
tau_b_fits = []
tau_b_errs = []
tau_b_bounded = []
for res in results:
    r = res["c2exact"]
    if r["success"]:
        tau_b_fits.append(r["tau_b_us"])
        tau_b_errs.append(r["tau_b_err_us"])
        tau_b_bounded.append(r["tau_b_at_bound"])
    else:
        tau_b_fits.append(np.nan)
        tau_b_errs.append(np.nan)
        tau_b_bounded.append(True)

tau_b_fits = np.array(tau_b_fits)
tau_b_errs = np.array(tau_b_errs)
bounded_mask = np.array(tau_b_bounded)

valid = ~bounded_mask & ~np.isnan(tau_b_fits)
print("tau_B extraction summary:")
print(f"  Injection value:        {TAU_B_INJ*1e6:.2f} µs")
print(f"  Qubits with valid fit:  {valid.sum()}/{N_Q}")
print(f"  Qubits at bound:        {bounded_mask.sum()}/{N_Q}")
if valid.any():
    tb_valid = tau_b_fits[valid]
    print(f"  tau_B range (valid):    {tb_valid.min():.2f} – {tb_valid.max():.2f} µs")
    print(f"  tau_B mean ± std:       {tb_valid.mean():.2f} ± {tb_valid.std():.2f} µs")
    cv = tb_valid.std() / tb_valid.mean()
    print(f"  CV (std/mean):          {cv:.2f}  ({'< 0.5 OK' if cv < 0.5 else '> 0.5 HIGH'})")
print()

# ─── Save results ─────────────────────────────────────────────────────────────
out_npz = os.path.join(DATA_DIR, "ramsey_fit_results.npz")
np.savez(out_npz,
    tau_b_fits_us=tau_b_fits,
    tau_b_errs_us=tau_b_errs,
    tau_b_bounded=bounded_mask,
    tau_b_valid=valid,
    tau_b_inj_us=np.array(TAU_B_INJ * 1e6),
    winners=np.array(winners),
)
print(f"Saved: {out_npz}")

out_json = os.path.join(DATA_DIR, "ramsey_fit_results.json")
with open(out_json, "w") as f:
    json.dump({
        "script": "p18_ramsey_fit.py",
        "n_qubits": N_Q,
        "tau_b_inj_us": TAU_B_INJ * 1e6,
        "qubit_results": results,
        "model_winners": winners,
        "winner_counts": dict(cnt),
        "c2exact_wins": n_c2_wins,
        "tau_b_fits_us": tau_b_fits.tolist(),
        "tau_b_errs_us": tau_b_errs.tolist(),
        "tau_b_bounded": bounded_mask.tolist(),
        "tau_b_valid_count": int(valid.sum()),
    }, f, indent=2)
print(f"Saved: {out_json}")

# ─── Figures ─────────────────────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    t_us = t * 1e6

    for qi in range(N_Q):
        ax = axes[qi]
        ax.errorbar(t_us, traces[qi], yerr=trace_std[qi],
                    fmt="k.", ms=3, alpha=0.5, label="Data")
        # Plot fits
        colors = {"exp": "blue", "gauss": "green", "strexp": "orange", "c2exact": "red"}
        for mname, col in colors.items():
            res = results[qi][mname]
            if not res["success"]:
                continue
            if mname == "exp":
                yfit = model_exp(t, res["A"], res["Gamma"])
            elif mname == "gauss":
                yfit = model_gauss(t, res["A"], res["T_G_us"]/1e6)
            elif mname == "strexp":
                yfit = model_strexp(t, res["A"], res["T_S_us"]/1e6, res["beta"])
            elif mname == "c2exact":
                yfit = model_c2exact(t, res["A"],
                                     res["gamma_m_kHz"]*2*np.pi*1e3,
                                     res["tau_b_us"]/1e6)
            lw = 2 if mname == "c2exact" else 1
            ax.plot(t_us, yfit, color=col, lw=lw, label=mname)
        ax.set_xscale("log")
        ax.axvline(TAU_B_INJ*1e6, color="gray", ls=":", lw=1, label=f"τ_B={TAU_B_INJ*1e6:.1f}µs")
        ax.set_title(f"Q{qi:02d}")
        ax.set_xlabel("Delay (µs)")
        ax.set_ylabel("Signal")
        if qi == 0:
            ax.legend(fontsize=7, loc="upper right")

    # Hide unused subplot
    if N_Q < len(axes):
        for ax in axes[N_Q:]:
            ax.set_visible(False)

    fig.suptitle("Ramsey Traces + Model Fits (Phase 9 Simulation)", fontsize=13)
    plt.tight_layout()
    fpath = os.path.join(FIG_DIR, "fig_ramsey_traces.png")
    plt.savefig(fpath, dpi=120)
    plt.close()
    print(f"Saved: {fpath}")

    # tau_B distribution plot
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    qubits = np.arange(N_Q)
    ax2.errorbar(qubits[valid], tau_b_fits[valid], yerr=tau_b_errs[valid],
                 fmt="o", color="red", ms=8, label="C2-exact fit (valid)")
    if bounded_mask.any():
        ax2.scatter(qubits[bounded_mask & ~np.isnan(tau_b_fits)],
                    tau_b_fits[bounded_mask & ~np.isnan(tau_b_fits)],
                    marker="x", color="gray", s=80, label="At bound")
    ax2.axhline(TAU_B_INJ*1e6, color="black", ls="--", label=f"τ_B injected = {TAU_B_INJ*1e6:.1f}µs")
    ax2.set_xlabel("Qubit index")
    ax2.set_ylabel("τ_B (µs)")
    ax2.set_title("τ_B Extracted per Qubit (C2-exact fit)")
    ax2.legend()
    ax2.set_xticks(qubits)
    ax2.set_xticklabels([f"Q{q:02d}" for q in qubits])
    plt.tight_layout()
    fpath2 = os.path.join(FIG_DIR, "fig_tau_b_distribution.png")
    plt.savefig(fpath2, dpi=120)
    plt.close()
    print(f"Saved: {fpath2}")

except ImportError:
    print("matplotlib not available — figures skipped")

print()
print("p18 COMPLETE")
print("=" * 60)
