import numpy as np
import glob
import os
import matplotlib.pyplot as plt

class V12Governor:
    def __init__(self, k=1.05, limit=5.0):
        self.T_sys = 0.0
        self.gamma = 0.0548
        self.beta = 0.8183
        self.dt = 0.05
        self.decay = 0.0005
        self.K = k
        self.limit = limit

    def step(self, signal):
        self.gamma *= (1 - self.decay)
        E = (1 - np.exp(-signal / 40.0)) if signal < 45 else (0.675 + (signal - 45.0) / 20.0)
        self.T_sys += (E * self.beta - self.gamma * self.T_sys) * self.dt
        return np.tanh(self.T_sys / self.limit)

def process_sparc_file(filepath):
    try:
        data = np.genfromtxt(filepath)
        if data.ndim < 2 or data.shape[1] < 5: return None
    except: return None
    
    r, v_obs = data[:, 0], data[:, 1]
    v_bar = np.sqrt(np.nan_to_num(data[:, 3])**2 + np.nan_to_num(data[:, 4])**2 + np.nan_to_num(data[:, 5])**2)
    
    gov = V12Governor()
    errors = [abs(np.sqrt(v_bar[i]**2 * (1 + gov.K * gov.step(v_bar[i]**2 / r[i]))) - v_obs[i]) / v_obs[i] * 100 
              for i in range(len(r)) if r[i] > 0 and v_obs[i] > 0]
    return np.mean(errors) if errors else None

# Execution
files = glob.glob("data/sparc/*.dat")
results = {os.path.basename(f).replace(".dat", ""): process_sparc_file(f) for f in files}
valid_results = {k: v for k, v in results.items() if v is not None}
sorted_galaxies = sorted(valid_results.items(), key=lambda x: x[1])

print("\n--- TOP 10 GALAXIES (BEST FIT: 10th Percentile) ---")
for name, error in sorted_galaxies[:10]:
    print(f"{name:<15}: {error:.2f}% error")

print("\n--- BOTTOM 10 GALAXIES (WORST FIT: 90th Percentile) ---")
for name, error in sorted_galaxies[-10:]:
    print(f"{name:<15}: {error:.2f}% error")

# Stats Summary
all_maes = list(valid_results.values())
print(f"\nGlobal Score: {100 - np.mean(all_maes):.2f}%")
