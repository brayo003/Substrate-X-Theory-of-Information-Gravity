import pandas as pd
from v12_bridge_controller import SXCOmegaEngine

# High Sensitivity recalibration
SIGMA = 5e-3 
engine = SXCOmegaEngine(gamma=0.08) 
data = pd.read_csv('entropy_flux.csv', names=['flux'], header=0)

print(f"{'Step':<10} | {'Int Flux':<12} | {'T_sys':<12} | {'State'}")
print("-" * 55)

last_val = None
for i, row in data.iterrows():
    try:
        val = float(row['flux'])
    except:
        continue
    if last_val is None:
        last_val = val
        continue
    
    diff = val - last_val
    t_sys, phase = engine.step(diff * SIGMA)
    last_val = val
    
    # We prioritize logging the transition points
    if t_sys > 1.0 or i % 10 == 0:
        state_label = f"*** {phase} ***" if phase != "NOMINAL" else phase
        print(f"{i:<10} | {diff:<12.0f} | {t_sys:<12.4f} | {state_label}")
