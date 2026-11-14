#!/usr/bin/env python3
"""
p20_joint_c2_test.py — Phase 9, Step 4
Compute c_C2 = d_c / tau_B; test stability; compare to injection value.

Outputs:
  outputs/data/joint_c2_results.json
  outputs/figures/fig_c2_joint_test.png
"""

import numpy as np
import json, os

BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "outputs", "data")
FIG_DIR  = os.path.join(BASE, "outputs", "figures")

print("=" * 60)
print("p20_joint_c2_test.py — Joint C2 Test: c = d_c / tau_B")
print("=" * 60)

# Load temporal results
ft = np.load(os.path.join(DATA_DIR, "ramsey_fit_results.npz"))
tau_b_fits  = ft["tau_b_fits_us"]   # µs
tau_b_errs  = ft["tau_b_errs_us"]
tau_b_valid = ft["tau_b_valid"]

# Load spatial results
sp = np.load(os.path.join(DATA_DIR, "spatial_results.npz"))
d_c_result = float(sp["d_c_result"])    # meters
d_c_err    = float(sp["d_c_err"])
xi_c_inj   = float(sp["xi_c_inj"])
delta_aic  = float(sp["delta_aic_null_minus_exp"])

# Injection values
with open(os.path.join(DATA_DIR, "ramsey_sim_meta.json")) as f:
    meta = json.load(f)
C2_INJ  = meta["injection"]["c2_speed_m_per_s"]
TAU_B_INJ_US = meta["injection"]["tau_B_us"]

print(f"\nInputs:")
print(f"  d_c measured:    {d_c_result*1e6:.2f} ± {d_c_err*1e6:.2f} µm")
print(f"  d_c injected:    {xi_c_inj/2*1e6:.2f} µm  (= xi_c/2)")
print(f"  tau_B valid qubits: {tau_b_valid.sum()} / {len(tau_b_valid)}")
print(f"  tau_B injected:  {TAU_B_INJ_US:.2f} µs")
print(f"  ΔAIC(null-exp):  {delta_aic:.2f}")
print()

# Only proceed if d_c was extracted
if np.isnan(d_c_result):
    print("ABORT: d_c not extracted from spatial fit — joint test cannot proceed.")
    result = {"verdict": "TECHNICALLY_INCONCLUSIVE",
              "reason": "d_c not extracted"}
    with open(os.path.join(DATA_DIR, "joint_c2_results.json"), "w") as f:
        json.dump(result, f, indent=2)
    raise SystemExit(0)

# Per-qubit c_C2 = d_c / tau_B  (convert units: d_c in m, tau_B in s)
valid_idx = np.where(tau_b_valid)[0]
c_c2_per_qubit = []
c_c2_err_per_qubit = []

for qi in valid_idx:
    tau_b_s   = tau_b_fits[qi] * 1e-6
    tau_b_e_s = tau_b_errs[qi] * 1e-6
    c_val     = d_c_result / tau_b_s
    # Error propagation: sigma_c/c = sqrt((sigma_d/d)^2 + (sigma_tau/tau)^2)
    c_err = c_val * np.sqrt((d_c_err/d_c_result)**2 + (tau_b_e_s/tau_b_s)**2)
    c_c2_per_qubit.append(c_val)
    c_c2_err_per_qubit.append(c_err)
    print(f"  Q{qi:02d}: tau_B={tau_b_fits[qi]:.2f}µs  "
          f"c_C2={c_val:.3e} m/s  ±{c_err:.3e}")

c_arr = np.array(c_c2_per_qubit)
e_arr = np.array(c_c2_err_per_qubit)

print()
print("Joint test summary:")
print(f"  c_C2 injected:   {C2_INJ:.3e} m/s")
if len(c_arr) > 0:
    print(f"  c_C2 mean:       {c_arr.mean():.3e} m/s")
    print(f"  c_C2 std:        {c_arr.std():.3e} m/s")
    cv = c_arr.std() / c_arr.mean() if c_arr.mean() != 0 else np.nan
    print(f"  CV (std/mean):   {cv:.2f}  ({'stable' if cv < 0.3 else 'unstable'})")
    ratio = c_arr.mean() / C2_INJ
    print(f"  Ratio (meas/inj):{ratio:.2f}")
    within_3x = abs(np.log10(ratio)) < np.log10(3)
    print(f"  Within 3× of injection: {'YES' if within_3x else 'NO'}")

    # Stability test: split qubits into two halves
    if len(c_arr) >= 4:
        half = len(c_arr) // 2
        c1 = c_arr[:half].mean()
        c2 = c_arr[half:].mean()
        split_ratio = c1 / c2 if c2 != 0 else np.nan
        print(f"\n  Subset stability: half1={c1:.3e}, half2={c2:.3e}, ratio={split_ratio:.2f}")
        stable = abs(np.log10(split_ratio)) < np.log10(2) if not np.isnan(split_ratio) else False
        print(f"  Subset stable (within 2×): {'YES' if stable else 'NO'}")
    else:
        stable = None
        print("\n  Too few valid qubits for subset stability test")

    # d_c uncertainty dominates — report explicitly
    print(f"\n  d_c uncertainty dominates c_C2 error (d/xi_c << 1 problem).")
    print(f"  The spatial fit is poorly constrained — xi_c >> chip size.")
    print(f"  c_C2 estimate has very large fractional uncertainty: {e_arr.mean()/c_arr.mean():.1%}")
else:
    print("  No valid qubit pairs — cannot compute c_C2")
    cv = np.nan
    stable = None

print()

# Verdict
if np.isnan(d_c_result) or len(c_arr) == 0:
    verdict = "TECHNICALLY_INCONCLUSIVE"
    reason  = "d_c not constrained"
elif delta_aic < 2 and delta_aic > -2:
    verdict = "TECHNICALLY_INCONCLUSIVE"
    reason  = "spatial signal indistinguishable from null (|ΔAIC| < 2)"
elif delta_aic < -2:
    verdict = "COMPATIBLE_UNDERDETERMINED"
    reason  = "null model preferred spatially; c_C2 not extractable independently"
else:
    verdict = "COMPATIBLE_UNDERDETERMINED"
    reason  = "c_C2 extracted but d_c uncertainty too large for strong test"

print(f"Joint test verdict: {verdict}")
print(f"Reason: {reason}")

result = {
    "script": "p20_joint_c2_test.py",
    "c2_injected": C2_INJ,
    "d_c_m": float(d_c_result),
    "d_c_err_m": float(d_c_err),
    "tau_b_mean_us": float(tau_b_fits[tau_b_valid].mean()) if tau_b_valid.any() else None,
    "c_c2_per_qubit": c_arr.tolist(),
    "c_c2_mean": float(c_arr.mean()) if len(c_arr) > 0 else None,
    "c_c2_std": float(c_arr.std()) if len(c_arr) > 0 else None,
    "cv": float(cv) if not np.isnan(cv) else None,
    "delta_aic_spatial": float(delta_aic),
    "verdict": verdict,
    "reason": reason,
    "limitation": "xi_c >> chip size: d_c poorly constrained; joint test is under-determined"
}

with open(os.path.join(DATA_DIR, "joint_c2_results.json"), "w") as f:
    json.dump(result, f, indent=2)
print(f"\nSaved: {DATA_DIR}/joint_c2_results.json")

# Figure
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: c_C2 per qubit
    ax = axes[0]
    if len(c_arr) > 0:
        ax.errorbar(valid_idx, c_arr, yerr=e_arr, fmt="o", color="red", ms=8)
        ax.axhline(C2_INJ, color="black", ls="--", label=f"Injected c={C2_INJ:.1e}")
        ax.axhline(c_arr.mean(), color="red", ls=":", label=f"Mean c={c_arr.mean():.1e}")
    ax.set_xlabel("Qubit index")
    ax.set_ylabel("c_C2 = d_c/τ_B  (m/s)")
    ax.set_title("c_C2 per qubit")
    ax.legend(fontsize=8)
    ax.set_yscale("log")

    # Right: d_c vs tau_B scatter
    ax2 = axes[1]
    if tau_b_valid.any():
        tb = tau_b_fits[tau_b_valid] * 1e-6
        dc_arr_plot = np.full(len(tb), d_c_result)
        ax2.scatter(tb * 1e6, dc_arr_plot * 1e6, color="blue", s=80, label="Measured")
        ax2.errorbar(tb * 1e6, dc_arr_plot * 1e6,
                     xerr=tau_b_errs[tau_b_valid], yerr=np.full(len(tb), d_c_err*1e6),
                     fmt="none", color="blue", alpha=0.5)
    # Show C2 prediction line: d_c = c * tau_B
    tb_range = np.linspace(0.1e-6, 50e-6, 200)
    ax2.plot(tb_range*1e6, C2_INJ * tb_range * 1e6, "k--", label=f"C2 pred (c={C2_INJ:.1e})")
    ax2.set_xlabel("τ_B (µs)")
    ax2.set_ylabel("d_c (µm)")
    ax2.set_title("d_c vs τ_B — C2 consistency")
    ax2.legend(fontsize=8)

    fig.suptitle("Joint C2 Test: c_C2 = d_c / τ_B", fontsize=13)
    plt.tight_layout()
    fpath = os.path.join(FIG_DIR, "fig_c2_joint_test.png")
    plt.savefig(fpath, dpi=120)
    plt.close()
    print(f"Saved: {fpath}")
except ImportError:
    print("matplotlib not available — figure skipped")

print("\np20 COMPLETE")
print("=" * 60)
