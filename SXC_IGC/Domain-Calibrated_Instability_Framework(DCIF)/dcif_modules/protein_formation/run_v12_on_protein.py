import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ================== V12 ENGINE ==================
class SXCOmegaEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = 0.8
        self.gamma = self.gamma_max
        self.beta = 3.5
        self.dt = 0.05
        self.decay_rate = 0.0005 
        
    def excitation_flux(self, signal):
        if signal < 45:
            return 1 - np.exp(-signal / 40.0)
        return 0.675 + ((signal - 45.0) / 20.0)

    def step(self, signal):
        self.gamma *= (1 - self.decay_rate)
        E = self.excitation_flux(signal)
        gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        self.T_sys += (inflow - outflow) * self.dt
        
        if self.T_sys > 1.0:
            self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4:
            self.phase = "NOMINAL"
            
        return self.T_sys, self.phase

# ================== LOAD TRAJECTORY ==================
df = pd.read_csv('ubiquitin_trajectory.csv')
print(f"Loaded trajectory: {len(df)} steps")

# ================== RUN V12 ==================
engine = SXCOmegaEngine()
T_values = []
phase_values = []
K_values = df['signal'] / 100  # K = signal/100

for sig in df['signal']:
    T, phase = engine.step(sig)
    T_values.append(T)
    phase_values.append(phase)

df['T_sys'] = T_values
df['phase'] = phase_values
df['K'] = K_values

# ================== RESULTS ==================
print("\n=== PROTEIN FOLDING STRESS ANALYSIS ===")
print(f"K range: {df['K'].min():.3f} to {df['K'].max():.3f}")
print(f"T_sys range: {df['T_sys'].min():.3f} to {df['T_sys'].max():.3f}")
print(f"FIREWALL moments: {(df['phase'] == 'FIREWALL').sum()}")
print(f"K > 0.5 moments: {(df['K'] > 0.5).sum()} ({(df['K'] > 0.5).sum()/len(df)*100:.1f}%)")

# Find high-stress periods
stress_periods = df[df['K'] > 0.5]
if not stress_periods.empty:
    print(f"\nFirst high-stress period at t={stress_periods.iloc[0]['time']:.3f}")
    print(f"Peak stress: K={stress_periods['K'].max():.3f} at t={stress_periods['K'].idxmax()}")

# ================== PLOT ==================
plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['K'], label='K (stress ratio)', alpha=0.7)
plt.plot(df['time'], df['T_sys'], label='T_sys (system tension)', alpha=0.7)
plt.axhline(y=0.5, color='red', linestyle='--', label='Fracture threshold (K=0.5)')
plt.axhline(y=1.0, color='orange', linestyle='--', label='FIREWALL threshold')
plt.xlabel('Time')
plt.ylabel('Stress metrics')
plt.title('Protein Folding Stress Analysis with V12')
plt.legend()
plt.savefig('protein_v12_analysis.png')
print("\n✅ Plot saved to protein_v12_analysis.png")
