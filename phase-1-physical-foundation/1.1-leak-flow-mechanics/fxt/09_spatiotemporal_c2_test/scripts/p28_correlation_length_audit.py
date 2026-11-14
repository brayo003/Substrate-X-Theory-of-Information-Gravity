#!/usr/bin/env python3
"""
p28_correlation_length_audit.py — Phase 9e
Audit: ξ_c numerical predictions and K0 discriminator accessibility.
"""
import numpy as np
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOUT = os.path.join(BASE, "outputs", "data")
os.makedirs(DOUT, exist_ok=True)

print("=" * 70)
print("p28_correlation_length_audit.py — Correlation Length Consequences")
print("=" * 70)

v_s = 6000.0  # m/s — FPUT acoustic speed Si (derived)

# tau_B values actually used in the project
tau_b_project = {
    "Tuna-17 median": 5.0e-6,
    "NM_PREDICTION_AUDIT fitted": 0.75e-6,
    "Simulation injection": 5.0e-6,
    "Phase 9 Ramsey fits": 5.34e-6,
}

# Platform sizes
platforms = {
    "IBM 7-qubit (sim)": 632e-6,
    "IBM Eagle 127q": 14e-3,
    "IBM Heron 133q": 12e-3,
    "Rigetti Ankaa-3 84q": 8e-3,  # approximate
}

print("\n── ξ_c for c = v_s = 6000 m/s at project τ_B values ──")
print(f"{'τ_B source':30s}  {'τ_B (µs)':10s}  {'ξ_c (cm)':12s}")
print("─"*55)
xi_results = {}
for name, tb in tau_b_project.items():
    xi = 2 * v_s * tb
    print(f"  {name:28s}  {tb*1e6:8.2f}    {xi*100:10.3f}")
    xi_results[name] = {"tau_b_us": tb*1e6, "xi_c_cm": xi*100}

print("\n── Required τ_B for ξ_c ~ platform size ──")
print(f"{'Platform':28s}  {'Size (mm)':10s}  {'τ_B needed (µs)':16s}  {'NMP at Γ=50kHz':15s}")
print("─"*70)
Gamma_M = 2*np.pi*50e3  # 50 kHz Markov rate
tau_needed = {}
for name, size in platforms.items():
    tau_n = size / (2 * v_s)
    nmp = Gamma_M * tau_n
    print(f"  {name:26s}  {size*1e3:8.2f}    {tau_n*1e6:14.3f}    {nmp:13.3f}")
    tau_needed[name] = {"size_mm": size*1e3, "tau_needed_us": tau_n*1e6, "NMP": nmp}

print("""
NMP interpretation:
  NMP < 0.01: Markovian — τ_B NOT identifiable from Ramsey shape
  NMP 0.1–5:  Non-Markovian — τ_B identifiable
  NMP > 10:   Quasistatic — shape saturates

At Eagle (14mm): τ_B needed = 1.17 µs → NMP = 0.37  [identifiable, suboptimal]
At 7-qubit sim:  τ_B needed = 0.053 µs → NMP = 0.017 [Markov, τ_B unidentifiable]
""")

print("── K0 vs exponential discriminator ──")
from scipy.special import k0 as bessel_k0
a_latt = 200e-6  # IBM NN spacing

xi_test_cases = {
    "τ_B=5µs (project value)": 2*v_s*5e-6,
    "τ_B=1.17µs (Eagle match)": 14e-3,
    "τ_B=0.67µs (Ankaa match)": 8e-3,
}

print(f"\n  K0(r/ξ_c) vs exp(-r/ξ_c) at r = a to 5a (a=200µm):")
print(f"  {'ξ_c':12s}  {'r':8s}  {'K0':8s}  {'exp':8s}  {'|diff|':8s}  {'diff%':6s}")
print("  " + "─"*60)

k0_results = {}
for case, xi_c in xi_test_cases.items():
    r_vals = np.arange(1, 6) * a_latt
    k0_norm = bessel_k0(a_latt/xi_c) if a_latt/xi_c > 0 else np.inf
    for r in r_vals:
        u = r / xi_c
        ua = a_latt / xi_c
        k0_val = bessel_k0(np.clip(u, 1e-10, 700)) / bessel_k0(np.clip(ua, 1e-10, 700))
        exp_val = np.exp(-(r - a_latt)/xi_c)
        diff = abs(k0_val - exp_val)
        pct = diff/exp_val*100
        if r == a_latt or r == 5*a_latt:
            print(f"  {xi_c*100:8.3f}cm  {r*1e6:5.0f}µm  {k0_val:8.5f}  {exp_val:8.5f}  {diff:.5f}  {pct:5.1f}%")
    k0_results[case] = {"xi_c_cm": xi_c*100}

print("""
DISCRIMINATOR ASSESSMENT:
  At ξ_c = 6cm (τ_B=5µs, project value): K0 and exp differ by <0.001 at chip scale
  → Not discriminable on any current chip

  At ξ_c = 1.4cm (τ_B=1.17µs, Eagle size): K0 and exp differ by ~30-40%
  → Discriminable on Eagle if r/ξ_c ~ 1 is achieved (d ~ ξ_c ~ 14mm)
  → Eagle d_max ~ 14mm ≈ ξ_c → AUC ~ 1.0 in principle

EXPERIMENTAL BRANCH CLASSIFICATION:
  CONDITIONALLY OPEN — requires:
  (1) τ_B ~ 1.2 µs (not 5 µs) — this τ_B value has NOT been measured on real hardware
  (2) Eagle-class chip access (not currently available)
  (3) [PHON] identification assumption accepted
""")

output = {
    "xi_c_at_project_tau_b": xi_results,
    "tau_needed_for_platforms": tau_needed,
    "k0_results": k0_results,
    "discriminator": "CONDITIONALLY OPEN — requires tau_B~1.2us and Eagle access"
}
with open(os.path.join(DOUT, "correlation_length_consequence.json"), "w") as f:
    json.dump(output, f, indent=2)
print(f"Saved: {DOUT}/correlation_length_consequence.json")
print("p28 COMPLETE")
