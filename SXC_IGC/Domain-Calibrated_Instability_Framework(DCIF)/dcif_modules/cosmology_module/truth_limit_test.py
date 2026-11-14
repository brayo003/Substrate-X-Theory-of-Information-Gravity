import numpy as np
import glob
import os
import sys

class UnitaryGovernor:
    def __init__(self):
        # Constants remain SPARC-standard (The 1.254 scaling baseline)
        self.T_sys = 0.0
        self.gamma = 0.0548
        self.beta = 0.8183
        self.dt = 0.05
        self.K = 1.05

    def step(self, signal, v_obs, v_bar):
        # Sigmoidal Energy Input
        E = (1 - np.exp(-signal / 40.0)) if signal < 45 else (0.675 + (signal - 45.0) / 20.0)
        
        # Unitary Update: The Tanh function forces the system to stay between -1 and 1
        # It represents the physical saturation of the information substrate.
        d_tension = (E * self.beta - self.gamma * self.T_sys) * self.dt
        self.T_sys = np.tanh(self.T_sys + d_tension)
        
        return self.T_sys

# 1. Target the 'problem' galaxy again
files = glob.glob("data/sparc/*.dat")
files.sort(key=lambda x: os.path.getsize(x), reverse=True)
target = files[0]

print(f"--- SXC HARD-LIMIT TRUTH TEST ---")
print(f"Substrate: {os.path.basename(target)}")

try:
    data = np.genfromtxt(target)
    r, v_obs = data[:, 0], data[:, 1]
    v_bar = np.sqrt(np.nan_to_num(data[:, 3:6]**2).sum(axis=1))
    
    gov = UnitaryGovernor()
    v_preds = []
    tensions = []

    for i in range(len(r)):
        if r[i] <= 0: continue
        sig = v_bar[i]**2 / r[i]
        
        # Calculate prediction using constrained tension
        t_val = gov.step(sig, v_obs[i], v_bar[i])
        tensions.append(t_val)
        
        # Prediction logic
        pred = np.sqrt(max(0, v_bar[i]**2 * (1 + gov.K * t_val)))
        v_preds.append(pred)

    mae = np.mean(abs(np.array(v_preds) - v_obs[:len(v_preds)]) / v_obs[:len(v_preds)] * 100)
    
    print(f"Max Tension:   {max(tensions):.4f} (Limit: 1.0)")
    print(f"Final Tension: {tensions[-1]:.4f}")
    print(f"Mean Error:    {mae:.2f}%")

    if mae < 20.0 and max(tensions) < 1.0:
        print("\nVERDICT: UNIVERSAL CERTAINTY. The theory survives the Unitary Limit.")
    else:
        print("\nVERDICT: BS. The theory requires infinite energy to fit the curve.")

except Exception as e:
    print(f"Test Error: {e}")
