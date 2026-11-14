import pandas as pd
import sys
from v12_bridge_controller import SXCOmegaEngine

# Initialize the Ruler - Gamma 0.1 (Brittle) for high sensitivity
engine = SXCOmegaEngine(gamma=0.1) 
data = pd.read_csv('real_nuclear_flux.csv')

# We use the 'births' column as a proxy for high-variance Flux
# Births column is index 4
flux_data = data.iloc[:, 4] 

print(f"{'Step':<10} | {'Input Flux':<12} | {'T_sys (Tension)':<15} | {'Regime'}")
print("-" * 65)

for i, val in enumerate(flux_data[:25]):
    # Scaling factor of 0.01 to keep T_sys in observable range
    scaled_val = val * 0.01 
    t_sys, phase = engine.step(scaled_val)
    print(f"{i:<10} | {val:<12.1f} | {t_sys:<15.4f} | {phase}")

