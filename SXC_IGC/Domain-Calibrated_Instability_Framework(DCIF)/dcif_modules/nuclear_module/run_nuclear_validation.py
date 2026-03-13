import pandas as pd
import sys
from v12_bridge_controller import SXCOmegaEngine

# SIGMA bridges the Gap between 10^14 and our 1.0 Tension scale
SIGMA = 1e-14 

engine_steady = SXCOmegaEngine(gamma=0.05) 
engine_pulsed = SXCOmegaEngine(gamma=0.05)

data = pd.read_csv('true_nuclear_data.csv')

print(f"{'Time':<10} | {'Steady T':<12} | {'Pulsed T':<12} | {'Gap (Memory)'}")
print("-" * 65)

for i, row in data.iloc[::100].iterrows():
    t_steady, _ = engine_steady.step(row['flux_steady'] * SIGMA)
    t_pulsed, _ = engine_pulsed.step(row['flux_pulsed'] * SIGMA)
    gap = t_pulsed - t_steady
    print(f"{row['time']:<10.1f} | {t_steady:<12.4f} | {t_pulsed:<12.4f} | {gap:.4f}")
