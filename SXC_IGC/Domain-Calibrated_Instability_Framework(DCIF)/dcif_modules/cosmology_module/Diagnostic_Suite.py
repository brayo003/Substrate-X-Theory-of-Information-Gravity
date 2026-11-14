import numpy as np
import matplotlib.pyplot as plt
import os

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

def run_diagnostics(galaxy_file):
    filepath = f'data/sparc/{galaxy_file}'
    data = np.genfromtxt(filepath)
    r = data[:, 0]
    v_obs = data[:, 1]
    v_bar = np.sqrt(np.nan_to_num(data[:, 3])**2 + np.nan_to_num(data[:, 4])**2 + np.nan_to_num(data[:, 5])**2)
    
    gov = V12Governor()
    v_sxc_list = []
    tensions = []
    
    for i in range(len(r)):
        signal = v_bar[i]**2 / max(r[i], 0.1)
        tension = gov.step(signal)
        tensions.append(tension)
        v_sxc = np.sqrt(v_bar[i]**2 * (1 + gov.K * tension))
        v_sxc_list.append(v_sxc)
        
    v_sxc_arr = np.array(v_sxc_list)
    errors = abs(v_sxc_arr - v_obs) / v_obs * 100
    return r, v_obs, v_bar, v_sxc_arr, tensions, errors

# Plotting Execution
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
targets = [('UGC05414_rotmod.dat', 'Elite'), ('CamB_rotmod.dat', 'Anomaly')]

for i, (f, label) in enumerate(targets):
    r, v_obs, v_bar, v_sxc, tensions, errors = run_diagnostics(f)
    
    # 1. Rotation Curve Comparison
    axes[0, i].plot(r, v_obs, 'ko', label='Observed')
    axes[0, i].plot(r, v_sxc, 'r-', label='V12 SXC Prediction')
    axes[0, i].plot(r, v_bar, 'b--', label='Baryonic (Newton)')
    axes[0, i].set_title(f"{label}: {f.split('_')[0]} Rotation Curve")
    axes[0, i].legend()

    # 2. Tension vs Error Gradient
    ax2 = axes[1, i].twinx()
    axes[1, i].bar(r, errors, color='gray', alpha=0.3, label='Error %')
    ax2.plot(r, tensions, 'g-', label='Governor Tension (Saturation)')
    axes[1, i].set_ylabel('Error %')
    ax2.set_ylabel('Substrate Tension (tanh)')
    axes[1, i].set_title(f"{label}: Information Gravity Internal State")

plt.tight_layout()
plt.savefig('SXC_Global_Diagnostic.png')
print("Diagnostics complete. Open 'SXC_Global_Diagnostic.png' to see the internal failure points.")
