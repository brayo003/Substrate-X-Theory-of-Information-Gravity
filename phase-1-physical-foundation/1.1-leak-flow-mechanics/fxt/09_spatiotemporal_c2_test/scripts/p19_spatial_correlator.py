#!/usr/bin/env python3
"""
p19_spatial_correlator.py — Phase 9, Step 3
Compute inter-qubit phase-noise correlations; fit K0/exponential/null; extract d_c.

Outputs:
  outputs/data/spatial_results.npz
  outputs/data/spatial_results.json
  outputs/figures/fig_spatial_corr_matrix.png
  outputs/figures/fig_spatial_corr_vs_dist.png
"""

import numpy as np
import json, os
from scipy.optimize import curve_fit
from scipy.special import k0 as bessel_k0
import warnings
warnings.filterwarnings("ignore")

BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "outputs", "data")
FIG_DIR  = os.path.join(BASE, "outputs", "figures")

# ─── Load data ────────────────────────────────────────────────────────────────
d = np.load(os.path.join(DATA_DIR, "ramsey_sim.npz"))
phase_noise = d["phase_noise_arr"]   # (N_real, N_Q, N_delays)
dist_matrix = d["dist_matrix"]       # (N_Q, N_Q) in meters
t_delays    = d["t_delays"]
N_Q         = int(d["n_qubits"])
XI_C_INJ    = float(d["xi_c_inj"])
TAU_B_INJ   = float(d["tau_b_inj"])
C2_INJ      = float(d["c2_speed_inj"])
F_CM        = float(d["f_common_mode"])
N_REAL      = phase_noise.shape[0]

print("=" * 60)
print("p19_spatial_correlator.py — Spatial Correlation Analysis")
print("=" * 60)
print(f"Loaded {N_Q} qubits, {N_REAL} noise realizations, {len(t_delays)} delays")
print(f"  xi_c injected: {XI_C_INJ*1e6:.1f} µm")
print(f"  c_C2 injected: {C2_INJ:.2e} m/s")
print()

# ─── Compute phase-noise cross-correlation matrix ─────────────────────────────
# Integrate over delay axis: cumulative phase = integral of noise power
# Use the phase noise at the longest delay (most accumulated phase) for max SNR
# Also compute full delay-averaged correlation

# For each realization, take the last delay point (most SNR)
# phase_noise shape: (N_real, N_Q, N_delays)
phase_final = phase_noise[:, :, -1]   # (N_real, N_Q)

# Normalize each realization to zero mean
phase_final -= phase_final.mean(axis=0, keepdims=True)

# Correlation matrix from outer products
corr_matrix = np.zeros((N_Q, N_Q))
for ri in range(N_REAL):
    p = phase_final[ri]
    norms = np.sqrt(np.outer(p**2 + 1e-30, p**2 + 1e-30))
    corr_matrix += np.outer(p, p) / (N_REAL * norms.mean() + 1e-30)

# Proper Pearson correlation
cov_raw = np.cov(phase_final.T)   # (N_Q, N_Q)
std_vec = np.sqrt(np.diag(cov_raw))
corr_pearson = cov_raw / np.outer(std_vec, std_vec)

print("Phase-noise Pearson correlation matrix:")
for i in range(N_Q):
    row = "  ".join(f"{corr_pearson[i, j]:+.4f}" for j in range(N_Q))
    print(f"  Q{i:02d}: {row}")
print()

# ─── Extract off-diagonal pairs: corr vs. distance ───────────────────────────
pairs = []
for i in range(N_Q):
    for j in range(i+1, N_Q):
        d_ij = dist_matrix[i, j]
        r_ij = corr_pearson[i, j]
        pairs.append({"i": i, "j": j, "d_m": d_ij, "d_um": d_ij*1e6, "corr": r_ij})

pairs.sort(key=lambda x: x["d_m"])
print(f"Off-diagonal pairs: {len(pairs)}")
for p in pairs:
    print(f"  Q{p['i']:02d}-Q{p['j']:02d}: d={p['d_um']:.0f}µm  corr={p['corr']:+.4f}")
print()

d_arr   = np.array([p["d_m"] for p in pairs])
r_arr   = np.array([p["corr"] for p in pairs])
d_um    = d_arr * 1e6

# ─── Model fits ──────────────────────────────────────────────────────────────
# Note: at d/xi_c << 1, all correlations are near r_max.
# We fit: corr(d) = A * f(d; xi_c) + offset
# where offset captures common-mode

def model_exp_spatial(d, A, xi_c):
    return A * np.exp(-d / xi_c)

def model_k0_spatial(d, A, xi_c):
    # K0 modified Bessel function; regularized for small argument
    x = np.clip(d / xi_c, 1e-6, 500)
    return A * bessel_k0(x)

def model_null(d, A):
    return np.full_like(d, A)

fit_results = {}

# Common-mode estimate: mean correlation at nearest-neighbor pairs
nn_corrs = [p["corr"] for p in pairs if p["d_um"] < 300]
cm_estimate = np.mean(nn_corrs) if nn_corrs else float(np.mean(r_arr))
print(f"Common-mode estimate (from NN pairs): {cm_estimate:.4f}")
print(f"Common-mode fraction (injected):      {F_CM:.2f}")
print()

# Subtract common-mode before fitting spatial decay
r_detrended = r_arr - cm_estimate

# Exponential fit
try:
    p0 = [r_arr.max() - cm_estimate, XI_C_INJ]
    popt, pcov = curve_fit(model_exp_spatial, d_arr, r_detrended,
                           p0=p0, bounds=([0, 1e-6], [2.0, 1.0]),
                           maxfev=5000)
    perr = np.sqrt(np.diag(pcov))
    A_fit, xi_c_fit = popt
    d_c_fit = xi_c_fit / 2.0   # d_c = xi_c / 2 (from C2: xi_c = 2*c*tau_B => d_c = c*tau_B)
    resid = r_detrended - model_exp_spatial(d_arr, *popt)
    sse_exp = np.sum(resid**2)
    fit_results["exponential"] = {
        "A": float(A_fit), "xi_c_m": float(xi_c_fit),
        "xi_c_um": float(xi_c_fit*1e6),
        "d_c_m": float(d_c_fit), "d_c_um": float(d_c_fit*1e6),
        "xi_c_err_m": float(perr[1]),
        "d_c_err_m": float(perr[1]/2),
        "SSE": float(sse_exp), "n_params": 2,
        "AIC": len(d_arr)*np.log(sse_exp/len(d_arr)) + 2*2,
        "success": True
    }
    print(f"Exponential fit: xi_c = {xi_c_fit*1e6:.1f} ± {perr[1]*1e6:.1f} µm")
    print(f"  -> d_c = {d_c_fit*1e6:.1f} ± {perr[1]/2*1e6:.1f} µm")
except Exception as e:
    fit_results["exponential"] = {"success": False, "error": str(e)}
    print(f"Exponential fit FAILED: {e}")

# Null fit (no spatial dependence)
try:
    popt_null, _ = curve_fit(model_null, d_arr, r_detrended, p0=[0.0])
    resid_null = r_detrended - model_null(d_arr, *popt_null)
    sse_null = np.sum(resid_null**2)
    fit_results["null"] = {
        "A": float(popt_null[0]),
        "SSE": float(sse_null), "n_params": 1,
        "AIC": len(d_arr)*np.log(sse_null/len(d_arr)) + 2*1,
        "success": True
    }
    print(f"Null fit: A = {popt_null[0]:.4f}")
except Exception as e:
    fit_results["null"] = {"success": False, "error": str(e)}

print()

# ─── AIC comparison and spatial signal test ───────────────────────────────────
print("Model comparison (spatial):")
for mname, mr in fit_results.items():
    if mr["success"]:
        print(f"  {mname:12s}: AIC={mr['AIC']:8.2f}  SSE={mr['SSE']:.6f}")

aic_exp  = fit_results["exponential"].get("AIC", np.inf)
aic_null = fit_results["null"].get("AIC", np.inf)
delta_aic = aic_null - aic_exp  # positive = null worse = exponential preferred
print(f"\n  ΔAIC(null - exp) = {delta_aic:.2f}")
if delta_aic > 2:
    print("  -> Exponential preferred over null: spatial signal detected")
elif delta_aic < -2:
    print("  -> Null preferred: NO spatial signal detected (flat correlation)")
else:
    print("  -> Models indistinguishable (|ΔAIC| < 2): weak/no spatial signal")
print()

# ─── Key result: d_c extraction ──────────────────────────────────────────────
d_c_result = None
d_c_err    = None
if fit_results["exponential"]["success"]:
    d_c_result = fit_results["exponential"]["d_c_m"]
    d_c_err    = fit_results["exponential"]["d_c_err_m"]
    print(f"d_c extracted: {d_c_result*1e6:.2f} ± {d_c_err*1e6:.2f} µm")
    print(f"d_c injected (xi_c/2): {XI_C_INJ/2*1e6:.2f} µm")
    print(f"  NOTE: d_c uncertainty will be very large because d/xi_c << 1")
    print(f"  The spatial correlation is nearly flat across the chip.")
    print(f"  d_c is NOT well-constrained from this geometry.")
else:
    print("d_c: NOT EXTRACTED (fit failed)")
print()

# ─── Save results ─────────────────────────────────────────────────────────────
out_npz = os.path.join(DATA_DIR, "spatial_results.npz")
np.savez(out_npz,
    corr_pearson=corr_pearson,
    d_arr=d_arr,
    r_arr=r_arr,
    cm_estimate=np.array(cm_estimate),
    d_c_result=np.array(d_c_result if d_c_result is not None else np.nan),
    d_c_err=np.array(d_c_err if d_c_err is not None else np.nan),
    xi_c_inj=np.array(XI_C_INJ),
    delta_aic_null_minus_exp=np.array(delta_aic),
)
print(f"Saved: {out_npz}")

out_json = os.path.join(DATA_DIR, "spatial_results.json")
with open(out_json, "w") as f:
    json.dump({
        "script": "p19_spatial_correlator.py",
        "n_qubits": N_Q, "n_realizations": N_REAL,
        "cm_estimate": float(cm_estimate),
        "d_c_m": float(d_c_result) if d_c_result is not None else None,
        "d_c_um": float(d_c_result*1e6) if d_c_result is not None else None,
        "d_c_err_m": float(d_c_err) if d_c_err is not None else None,
        "xi_c_inj_um": float(XI_C_INJ*1e6),
        "delta_aic_null_minus_exp": float(delta_aic),
        "pairs": pairs,
        "model_fits": {k: {kk: vv for kk, vv in v.items() if kk != "error"}
                       for k, v in fit_results.items()},
        "limitation": "d/xi_c << 1 for all pairs: spatial decay unresolvable on 7-qubit chip"
    }, f, indent=2)
print(f"Saved: {out_json}")

# ─── Figures ─────────────────────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Correlation matrix heatmap
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr_pearson, vmin=-1, vmax=1, cmap="RdBu_r")
    plt.colorbar(im, ax=ax, label="Pearson correlation")
    ax.set_xticks(range(N_Q))
    ax.set_yticks(range(N_Q))
    ax.set_xticklabels([f"Q{q:02d}" for q in range(N_Q)], rotation=45)
    ax.set_yticklabels([f"Q{q:02d}" for q in range(N_Q)])
    ax.set_title("Phase-Noise Correlation Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig_spatial_corr_matrix.png"), dpi=120)
    plt.close()

    # Correlation vs. distance
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(d_um, r_arr, color="black", s=60, zorder=5, label="Measured pairs")
    ax.scatter(d_um, r_detrended, color="blue", s=40, marker="^",
               label="CM-subtracted")
    if fit_results["exponential"]["success"]:
        d_plot = np.linspace(d_arr.min(), d_arr.max(), 200)
        r_plot = model_exp_spatial(d_plot, fit_results["exponential"]["A"],
                                   fit_results["exponential"]["xi_c_m"])
        ax.plot(d_plot*1e6, r_plot, "r-", lw=2, label=f"Exp fit (ξ_c={fit_results['exponential']['xi_c_um']:.0f}µm)")
    ax.axhline(0, color="gray", ls=":")
    ax.set_xlabel("Qubit separation (µm)")
    ax.set_ylabel("Phase-noise correlation")
    ax.set_title("Spatial Correlation vs. Distance")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig_spatial_corr_vs_dist.png"), dpi=120)
    plt.close()
    print("Figures saved.")

except ImportError:
    print("matplotlib not available — figures skipped")

print()
print("p19 COMPLETE")
print("=" * 60)
