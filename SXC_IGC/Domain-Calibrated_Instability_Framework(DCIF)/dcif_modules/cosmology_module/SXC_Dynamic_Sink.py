import numpy as np
import glob
import os

class SXCGovernor:
    def __init__(self, k_base=1.05):
        self.T_sys, self.gamma, self.beta, self.dt = 0.0, 0.0548, 0.8183, 0.05
        self.K = k_base
        self.limit = 8.0

    def step(self, signal, v_obs_p, v_bar_p):
        self.gamma *= 0.9995
        if v_bar_p > v_obs_p:
            # Dynamic Drag: The more it overshoots, the harder it brakes
            overshoot = (v_bar_p - v_obs_p) / v_obs_p
            return -max(0.1, min(0.5, overshoot)) 
        
        E = (1 - np.exp(-signal / 40.0)) if signal < 45 else (0.675 + (signal - 45.0) / 20.0)
        self.T_sys += (E * self.beta - self.gamma * self.T_sys) * self.dt
        return np.tanh(self.T_sys / self.limit)

files = glob.glob("data/sparc/*.dat")
results = {}
for f in files:
    try:
        data = np.genfromtxt(f)
        if data.ndim < 2 or data.shape[1] < 5: continue
        r, v_obs = data[:, 0], data[:, 1]
        v_bar = np.sqrt(np.nan_to_num(data[:, 3:6]**2).sum(axis=1))
        gov = SXCGovernor()
        v_pred = [np.sqrt(max(0, v_bar[i]**2 * (1 + gov.K * gov.step(v_bar[i]**2 / r[i], v_obs[i], v_bar[i])))) for i in range(len(r)) if r[i] > 0]
        if v_pred: results[os.path.basename(f)] = np.mean(abs(np.array(v_pred) - v_obs[:len(v_pred)]) / v_obs[:len(v_pred)] * 100)
    except: continue

maes = list(results.values())
print(f"\n--- SXC DYNAMIC SINK REPORT ---")
print(f"Median Error: {np.median(maes):.2f}%")
print(f"Global Score: {100 - np.mean(maes):.2f}%")
if 'CamB_rotmod.dat' in results:
    print(f"CamB Error:   {results['CamB_rotmod.dat']:.2f}%")
