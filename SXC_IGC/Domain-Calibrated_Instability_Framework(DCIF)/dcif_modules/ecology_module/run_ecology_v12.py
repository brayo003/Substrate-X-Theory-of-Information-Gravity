import pandas as pd
import numpy as np

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
            
        return self.T_sys, self.phase

# ================== LOAD DATA ==================
df = pd.read_csv('data/ecosystem_analog.csv')
print(f'Loaded {len(df)} records from ecosystem_analog.csv')
print(f'Columns: {df.columns.tolist()}')

# Use energy as signal
signal = df['energy'].values
signal_norm = (signal - signal.min()) / (signal.max() - signal.min()) * 100

# Run V12
engine = SXCOmegaEngine()
T_values = []
phases = []

for s in signal_norm:
    T, p = engine.step(s)
    T_values.append(T)
    phases.append(p)

df['T_sys'] = T_values
df['phase'] = phases
df['K'] = df['energy'] / df['energy'].max()

# Results
print('\n=== ECOLOGY MODULE RESULTS ===')
print(f'K range: {df["K"].min():.3f} to {df["K"].max():.3f}')
print(f'K > 0.5: {(df["K"] > 0.5).sum()} ({(df["K"] > 0.5).mean()*100:.1f}%)')
print(f'T_sys range: {df["T_sys"].min():.2f} to {df["T_sys"].max():.2f}')
print(f'FIREWALL moments: {(df["phase"] == "FIREWALL").sum()} ({(df["phase"] == "FIREWALL").mean()*100:.1f}%)')

# Save
df.to_csv('data/ecology_v12_results.csv', index=False)
print('\n✅ Saved to data/ecology_v12_results.csv')
