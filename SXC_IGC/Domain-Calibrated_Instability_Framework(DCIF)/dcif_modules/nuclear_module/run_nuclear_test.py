import pandas as pd
from v12_bridge_controller import SXCOmegaEngine

engine_a = SXCOmegaEngine(gamma=0.5) # Steady
engine_b = SXCOmegaEngine(gamma=0.5) # Pulsed
data = pd.read_csv('nuclear_memory_test.csv')

print(f"{'Time':<10} | {'T_Steady':<12} | {'T_Pulsed':<12} | {'Memory Gap'}")
print("-" * 65)

last_gap = 0
for i, row in data.iloc[::50].iterrows():
    ta, _ = engine_a.step(row['flux_steady'] * 10) 
    tb, _ = engine_b.step(row['flux_pulsed'] * 10)
    last_gap = abs(ta - tb)
    print(f"{row['time']:<10.1f} | {ta:<12.4f} | {tb:<12.4f} | {last_gap:.4f}")

print("-" * 65)
print(f"FINAL RESULT: {'MEMORY DETECTED' if last_gap > 0.1 else 'NO MEMORY'}")
