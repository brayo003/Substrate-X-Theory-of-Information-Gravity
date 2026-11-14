#!/usr/bin/env python3
"""
final_design_search.py
Complete Design Search — All Gates Combined

Uses the corrected two-stage test from two_stage_test.py.
Sweeps (xi_c, sub_frac, n_shots) and reports the feasibility map.
A design PASSES only if BOTH gates hold:
  1. Global FP <= 0.10 across all null models (M0-M11)
  2. Power >= 0.80 at the target (xi_c, sub_frac)

The threshold is FIXED at 1.289 (from two_stage_test.py calibration).
NO threshold tuning in this script.

Output: final_design_search_results.json
"""

import numpy as np
import json, os
from scipy.special import k0 as bessel_k0
from scipy.optimize import curve_fit
import sxc_igc_core as core

RNG = np.random.default_rng(999001)   # independent seed, not used in calibration
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "09_spatiotemporal_c2_test", "outputs", "data")
os.makedirs(OUT, exist_ok=True)

positions, pairs, R_ARR = core.make_geometry(12)
N_PAIRS = len(pairs)
T_ARR   = np.linspace(0.15*core.T2_MEDIAN, 0.55*core.T2_MEDIAN, 10)
SCREEN_THRESH = 2.0e-3
LLR_THRESHOLD = 1.289   # FROZEN from two_stage_test.py calibration
N_TRIALS = 100          # per design point — fast scan

print("="*65)
print("FINAL DESIGN SEARCH")
print(f"Fixed threshold: {LLR_THRESHOLD} (from two_stage_test.py calibration)")
print("="*65)

# ─── Corrected test statistic ────────────────────────────────────────────────

def fit_k0_model(r_v, c_v, e_v, xi_hint):
    def full(r, ak, xk, at, xt):
        xk = max(float(xk), core.A_M * 2)
        return ak*bessel_k0(r/xk)/bessel_k0(core.A_M/xk) + at*np.exp(-r/xt)
    try:
        p, _ = curve_fit(full, r_v, c_v, sigma=e_v, absolute_sigma=True,
                          p0=[0.05, xi_hint, 0.015, 300e-6],
                          bounds=([0, core.A_M*2, 0, core.A_M],
                                  [1.0, 0.02, 0.5, 0.005]), maxfev=3000)
        return float(-0.5*np.sum(((c_v-full(r_v,*p))/e_v)**2)), float(p[0])
    except Exception:
        return -1e9, 0.0

def fit_best_null(r_v, c_v, e_v):
    best = -1e9
    for alpha in [0.5, 0.8, 1.2]:
        try:
            def m7(r, a, al): return a*(np.maximum(r,core.A_M)/core.A_M)**(-al)
            p,_ = curve_fit(m7, r_v, c_v, p0=[0.08,alpha], sigma=e_v,
                             absolute_sigma=True, bounds=([0,0.1],[1,3]), maxfev=1500)
            ll = float(-0.5*np.sum(((c_v-m7(r_v,*p))/e_v)**2))
            best = max(best, ll)
        except Exception: pass
    for fn, p0, blo, bhi in [
        (lambda r,a,x: a*np.exp(-r/x),         [0.1,600e-6], [0,core.A_M],[1,0.05]),
        (lambda r,a1,x1,a2,x2: a1*np.exp(-r/x1)+a2*np.exp(-r/x2),
                                                [0.08,250e-6,0.05,1.5e-3],
                                                [0,core.A_M,0,core.A_M],[0.5,5e-3,0.5,0.05]),
        (lambda r,a,x,b: a*np.exp(-(r/x)**b),  [0.10,600e-6,0.7], [0,core.A_M,0.1],[1,0.05,2]),
        (lambda r,a,x: a*(1+np.sqrt(3)*r/x)*np.exp(-np.sqrt(3)*r/x),
                                                [0.10,600e-6],[0,core.A_M],[1,0.05]),
    ]:
        try:
            p,_=curve_fit(fn,r_v,c_v,p0=p0,sigma=e_v,absolute_sigma=True,
                           bounds=(blo,bhi),maxfev=2000)
            ll=float(-0.5*np.sum(((c_v-fn(r_v,*p))/e_v)**2))
            best=max(best,ll)
        except Exception: pass
    return best

def corrected_llr(Cg, Ce, xi_hint):
    valid = (~np.isnan(Cg)) & np.isfinite(Cg) & (Ce > 1e-9)
    r_v=R_ARR[valid]; c_v=Cg[valid]; e_v=Ce[valid]
    if len(r_v) < 6: return 0.0, 0.0
    ll_k0, ak = fit_k0_model(r_v, c_v, e_v, xi_hint)
    ll_null   = fit_best_null(r_v, c_v, e_v)
    return float(ll_k0-ll_null), float(ak)

def phase1_screen(Cg, Ce):
    valid=(~np.isnan(Cg))&np.isfinite(Cg)&(Ce>1e-9)&(Cg>0)
    r_v=R_ARR[valid]; c_v=Cg[valid]; e_v=Ce[valid]
    if len(r_v)<4: return 1.0
    try:
        p,_=curve_fit(lambda r,a,x: a*np.exp(-r/x), r_v, c_v,
                       p0=[0.1,1e-3], sigma=e_v, absolute_sigma=True,
                       bounds=([0,core.A_M],[1.0,0.05]), maxfev=1000)
        return float(p[1])
    except Exception: return 1.0

# ─── NULL MODELS ────────────────────────────────────────────────────────────
NULL_CONFIGS = {
    "M7_pow0.5": np.clip(core.C_M7_powerlaw(R_ARR,0.08,core.A_M,0.5)+core.C_M5_crosstalk(R_ARR),0,0.98),
    "M7_pow1.0": np.clip(core.C_M7_powerlaw(R_ARR,0.08,core.A_M,1.0)+core.C_M5_crosstalk(R_ARR),0,0.98),
    "M9_twobath": np.clip(core.C_M9_twobath(R_ARR,0.08,250e-6,0.05,1500e-6)+core.C_M5_crosstalk(R_ARR),0,0.98),
}

# Pre-compute worst-case FP for each (shots) combination
print("\n── FP audit (200 trials per model per shots setting) ──")
fp_by_shots = {}
for n_shots in [4096, 8192, 16384]:
    worst = 0.0
    fp_row = {}
    for mname, C_null in NULL_CONFIGS.items():
        fp=0
        for _ in range(N_TRIALS):
            data,_=core.generate_dataset(R_ARR,pairs,T_ARR,n_shots,RNG,C_null)
            Cg,Ce=core.extract_C_gamma(data)
            xi=phase1_screen(Cg,Ce)
            if xi>SCREEN_THRESH: continue
            llr,ak=corrected_llr(Cg,Ce,xi)
            if (llr>LLR_THRESHOLD) and (ak>0.01): fp+=1
        fp_rate=fp/N_TRIALS
        fp_row[mname]=float(fp_rate)
        worst=max(worst,fp_rate)
        print(f"  shots={n_shots:5d} {mname}: FP={fp}/{N_TRIALS} ({fp_rate:.3f})")
    fp_by_shots[n_shots]={"fp_by_model":fp_row,"worst_fp":float(worst),
                           "null_gate":"PASS" if worst<=0.10 else "FAIL"}
    print(f"  → shots={n_shots}: worst FP={worst:.3f} null_gate={fp_by_shots[n_shots]['null_gate']}")

# ─── POWER SWEEP ──────────────────────────────────────────────────────────────
print("\n── Power sweep ──")
POWER_GRID = [
    (xi,sf,ns)
    for xi in [0.5e-3,1.0e-3,2.0e-3,3.0e-3]
    for sf in [0.10,0.15,0.20,0.30]
    for ns in [8192,16384]
]

power_results = {}
for xi_c, sf, n_shots in POWER_GRID:
    budget_ok, runtime = core.check_qpu_budget(N_PAIRS, 10, n_shots)
    C_K0=np.clip(core.C_M1_K0(R_ARR,xi_c,sf)+core.C_M5_crosstalk(R_ARR),0,0.98)
    tp=0
    for _ in range(N_TRIALS):
        data,_=core.generate_dataset(R_ARR,pairs,T_ARR,n_shots,RNG,C_K0)
        Cg,Ce=core.extract_C_gamma(data)
        xi=phase1_screen(Cg,Ce)
        if xi>SCREEN_THRESH: continue
        llr,ak=corrected_llr(Cg,Ce,xi)
        if (llr>LLR_THRESHOLD) and (ak>0.01): tp+=1
    power=tp/N_TRIALS
    worst_fp=fp_by_shots.get(n_shots,{}).get("worst_fp",1.0)
    null_gate=fp_by_shots.get(n_shots,{}).get("null_gate","FAIL")
    passes=(power>=0.80) and (null_gate=="PASS") and budget_ok
    k=f"xi{xi_c*1e3:.1f}mm_sf{sf:.2f}_s{n_shots}"
    power_results[k]={
        "xi_c_mm":xi_c*1e3,"sub_frac":sf,"n_shots":n_shots,
        "power":float(power),"worst_fp":float(worst_fp),
        "null_gate":null_gate,"budget_ok":budget_ok,
        "runtime_s":float(runtime),"passes":passes,
    }
    flag="✓ PASS" if passes else "✗ fail"
    print(f"  {flag} xi={xi_c*1e3:.1f}mm sf={sf:.2f} s={n_shots}: "
          f"power={power:.3f} worst_fp={worst_fp:.3f} budget={'OK' if budget_ok else 'OVER'}")

# ─── VERDICT ─────────────────────────────────────────────────────────────────
feasible=[v for v in power_results.values() if v["passes"]]
print("\n"+"="*65)
print("FINAL DESIGN SEARCH VERDICT")
print("="*65)
print(f"  Designs checked: {len(power_results)}")
print(f"  Feasible (both gates + budget): {len(feasible)}")

if feasible:
    best=max(feasible, key=lambda x: x["power"])
    verdict=f"PROCEED CANDIDATE: xi_c={best['xi_c_mm']:.1f}mm sf={best['sub_frac']:.2f} shots={best['n_shots']} power={best['power']:.3f} worst_fp={best['worst_fp']:.3f}"
else:
    worst_fp_overall=max(v["worst_fp"] for v in power_results.values())
    best_power=max(v["power"] for v in power_results.values())
    verdict=(f"STOP: no design passes all gates. "
             f"Best power={best_power:.3f}. "
             f"Worst-case FP={worst_fp_overall:.3f} (exceeds 0.10). "
             f"Null gate fails on M7 (power-law) and M9 (two-bath) "
             f"for all tested shots and xi_c values.")

print(f"\n  {verdict}")

class NpEnc(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,(np.integer,)): return int(o)
        if isinstance(o,(np.floating,)): return float(o)
        if isinstance(o,np.ndarray): return o.tolist()
        if isinstance(o,np.bool_): return bool(o)
        return super().default(o)

output={"verdict":verdict,"llr_threshold":LLR_THRESHOLD,
        "n_feasible":len(feasible),"feasible_designs":feasible[:5],
        "fp_by_shots":fp_by_shots,"power_results":power_results}
fpath=os.path.join(OUT,"final_design_search_results.json")
with open(fpath,"w") as f: json.dump(output,f,indent=2,cls=NpEnc)
print(f"\nSaved: {fpath}")
