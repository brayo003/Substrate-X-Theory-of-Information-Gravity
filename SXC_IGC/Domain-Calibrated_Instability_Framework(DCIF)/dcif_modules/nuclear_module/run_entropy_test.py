import pandas as pd
from v12_bridge_controller import SXCOmegaEngine

SIGMA = 1e-3 
engine = SXCOmegaEngine(gamma=0.08) 
data = pd.read_csv('entropy_flux.csv', names=['flux'], header=0)

print(f"{'Step':<10} | {'Int Flux':<12} | {'T_sys (Tension)':<15} | {'State'}")
print("-" * 65)

last_val = None
for i, row in data.iterrows():
    val = float(row['flux'])
    if last_val is None:
        last_val = val
        continue
    
    diff = val - last_val
    t_sys, phase = engine.step(diff * SIGMA)
    last_val = val
    
    # We want to see the rise, the peak, and the recovery
    if i % 10 == 0:
        print(f"{i:<10} | {diff:<12.0f} | {t_sys:<15.4f} | {phase}")
