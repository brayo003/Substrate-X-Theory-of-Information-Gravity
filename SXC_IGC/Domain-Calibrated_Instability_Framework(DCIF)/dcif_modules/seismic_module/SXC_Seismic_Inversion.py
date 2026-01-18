import pandas as pd
import numpy as np

class SXCSeismicGovernor:
    def __init__(self):
        self.T_sys = 0.0
        self.limit = 1.0

    def step(self, mag, depth):
        # The CamB Logic: Drag if Mag is low, Tension if Mag is high
        E = mag / 10.0
        # If the energy is too shallow, apply high viscosity (substrate absorption)
        if depth < 20: 
            viscosity = -0.2 * (20 - depth) / 20
            return viscosity
        
        self.T_sys = np.tanh(E / self.limit)
        return self.T_sys

df = pd.read_csv("global_seismic_substrate.csv")
gov = SXCSeismicGovernor()

print(f"\n--- SXC UNIVERSAL SEISMIC INVERSION ---")
print(f"{'MAG':<5} | {'DEPTH':<7} | {'SXC TENSION'}")
print("-" * 35)

for _, row in df.iterrows():
    tension = gov.step(row['mag'], row['depth'])
    # IDENTIFY CRISIS ONLY:
    if tension > 0.5 or tension < -0.15:
        print(f"{row['mag']:<5.1f} | {row['depth']:<7.1f} | {tension:.4f} [!] SNAPPING")
