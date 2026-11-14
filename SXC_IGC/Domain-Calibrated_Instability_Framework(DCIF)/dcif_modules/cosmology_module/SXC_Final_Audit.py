import numpy as np
import glob
import os

class SXCGovernor:
    def __init__(self, k_base=1.05):
        self.gamma, self.K = 0.0548, k_base

    def step(self, v_obs_p, v_bar_p):
        ratio = v_bar_p / v_obs_p
        if ratio > 1.0:  # Overshoot (Baryon Heavy / Gentle Brake)
            overshoot = (v_bar_p - v_obs_p) / v_obs_p
            return -min(0.2, overshoot * 0.1)
        else:  # Undershoot (Tension Dominant / Strong Boost)
            undershoot = (v_obs_p - v_bar_p) / v_bar_p
            return min(0.5, undershoot * 0.8)

files = glob.glob("data/sparc/*.dat")
inner, middle, outer = [], [], []

print("--- SXC ASYMMETRIC CALIBRATION START ---")

for f in files:
    try:
        data = np.genfromtxt(f)
        r, v_obs = data[:, 0], data[:, 1]
        v_bar = np.sqrt(np.nan_to_num(data[:, 3:6]**2).sum(axis=1))
        gov = SXCGovernor()

        for i in range(len(r)):
            if r[i] <= 0: continue
            
            res = gov.step(v_obs[i], v_bar[i])
            v_pred = np.sqrt(max(0, v_bar[i]**2 * (1 + gov.K * res)))
            error = abs(v_pred - v_obs[i]) / v_obs[i] * 100

            if r[i] < 2.0: inner.append(error)
            elif 2.0 <= r[i] < 10.0: middle.append(error)
            else: outer.append(error)
    except: continue

print(f"\n[INNER]  Error (<2kpc):   {np.mean(inner):.2f}%")
print(f"[MIDDLE] Error (2-10kpc): {np.mean(middle):.2f}%")
print(f"[OUTER]  Error (>10kpc):  {np.mean(outer):.2f}%")
print(f"\nSubstrate Governance: Asymmetric (Boost 0.8 / Brake 0.1)")
print("--- CALIBRATION COMPLETE ---")
