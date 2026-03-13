import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ================== V12 ENGINE ==================
class SXCOmegaEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = 'NOMINAL'
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
        gamma_eff = 2.2 if self.phase == 'FIREWALL' else 1.0
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        self.T_sys += (inflow - outflow) * self.dt
        
        if self.T_sys > 1.0:
            self.phase = 'FIREWALL'
        elif self.phase == 'FIREWALL' and self.T_sys < 0.4:
            self.phase = 'NOMINAL'
            
        return self.T_sys

# Load data
df = pd.read_csv('kenya_maize_yield.csv')
df = df.sort_values('Year').reset_index(drop=True)

values = df['Yield'].values
years = df['Year'].values

# Normalize
vmin, vmax = values.min(), values.max()
signal = (values - vmin) / (vmax - vmin) * 100

# Run V12
engine = SXCOmegaEngine()
T = []
for s in signal:
    T.append(engine.step(s))

df['T_sys'] = T
df['K'] = values / vmax
df['dT'] = df['T_sys'].diff()
df['accel'] = df['dT'].diff()

# Known drought years in Kenya
droughts = [1984, 1999, 2000, 2008, 2009, 2016, 2017, 2022]

# Check acceleration before droughts
print("\n=== ACCELERATION BEFORE DROUGHTS ===")
for d in droughts:
    # Get 5 years before drought
    mask = (df['Year'] >= d-5) & (df['Year'] <= d)
    window = df[mask].copy()
    if len(window) > 3:
        accel_before = window['accel'].iloc[:-1].mean()
        print(f"{d}: avg accel {accel_before:.4f} (over {len(window)-1} years)")

# Plot
plt.figure(figsize=(12,8))

plt.subplot(3,1,1)
plt.plot(df['Year'], df['Yield'], 'b-')
for d in droughts:
    plt.axvline(d, color='r', linestyle='--', alpha=0.5)
plt.ylabel('Maize Yield (kg/ha)')
plt.title('Kenya Maize Yield with Drought Years')

plt.subplot(3,1,2)
plt.plot(df['Year'], df['K'], 'g-')
plt.axhline(0.5, color='r', linestyle='--', label='K=0.5')
plt.ylabel('K (stress)')
plt.legend()

plt.subplot(3,1,3)
plt.plot(df['Year'][2:], df['accel'][2:], 'purple')
plt.axhline(0, color='k', linestyle='-', alpha=0.3)
plt.xlabel('Year')
plt.ylabel('Acceleration')
plt.title('Stress Acceleration')

plt.tight_layout()
plt.savefig('kenya_maize_analysis.png')
print("\nPlot saved to kenya_maize_analysis.png")
