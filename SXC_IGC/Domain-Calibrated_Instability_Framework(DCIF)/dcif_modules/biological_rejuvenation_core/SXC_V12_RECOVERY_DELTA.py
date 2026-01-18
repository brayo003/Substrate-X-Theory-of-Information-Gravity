import numpy as np
from SXC_V12_CORE import SXCOmegaEngine

# Start at the Saturation Point
engine = SXCOmegaEngine()
engine.T_sys = 1.7103
engine.phase = "FIREWALL"

print("CRISIS RECOVERY PROTOCOL")
print("-" * 45)
print(f"INITIAL STATE: Signal=120, Tension={engine.T_sys}, Phase={engine.phase}")

# Step 1: Lower Signal to 'Normal' (25.0)
target_signal = 25.0
for _ in range(100): engine.step(target_signal)
print(f"POST-NORMALIZATION: Signal={target_signal}, Tension={engine.T_sys:.4f}, Phase={engine.phase}")

# Step 2: Apply the 'Deep Clean' Flush to break the Hysteresis
print("\n[!!!] APPLYING DEEP CLEAN INTERVENTION [!!!]")
engine.apply_intervention("DEEP")
engine.step(target_signal)

print(f"POST-INTERVENTION: Tension={engine.T_sys:.4f}, Phase={engine.phase}")
