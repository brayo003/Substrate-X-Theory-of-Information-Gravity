import pandas as pd
import numpy as np

# ================== V12 URBAN ENGINE ==================
class SXCOmegaEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.beta = 4.2  # Higher sensitivity for social substrates
        self.dt = 0.1
        self.decay_rate = 0.02 # Civic resilience (how fast the street "heals")
        
    def excitation_flux(self, signal):
        return 1 - np.exp(-signal / 25.0)

    def step(self, signal):
        inflow = self.excitation_flux(signal) * self.beta
        outflow = self.decay_rate * self.T_sys
        self.T_sys += (inflow - outflow) * self.dt
        
        if self.T_sys > 1.0:
            self.phase = "FIREWALL" # The street is "Captured"
        elif self.T_sys < 0.3:
            self.phase = "NOMINAL"
        return self.T_sys, self.phase

# ================== SIMULATED SUBSTRATE DATA ==================
# Creating a 3-day high-intensity window
np.random.seed(42)
dates = pd.date_range("2024-01-01", periods=72, freq="H")
# Signal = complaints per hour (spiking in the evenings)
signals = [np.random.randint(0, 10) + (15 if (d.hour > 18 or d.hour < 4) else 0) for d in dates]

df = pd.DataFrame({"timestamp": dates, "complaints": signals})
engine = SXCOmegaEngine()

# Apply V12
results = [engine.step(s) for s in df['complaints']]
df['T_sys'], df['phase'] = zip(*results)

print("\n=== URBAN SUBSTRATE: DRUG-INDUCED INSTABILITY ===")
print(f"Substrate Fracture (FIREWALL) count: {sum(df['phase'] == 'FIREWALL')} hours")
print("-" * 50)
print(df[['timestamp', 'complaints', 'T_sys', 'phase']].tail(10))

if any(df['phase'] == 'FIREWALL'):
    print("\n[!] ALERT: SUBSTRATE FRACTURE DETECTED.")
    print("The street has reached 'Captured' status. Tension is self-sustaining.")
