import numpy as np
from SXC_V12_CORE import SXCOmegaEngine

engine = SXCOmegaEngine()
engine.T_sys = 0.9664 # Post-normalization tension
engine.phase = "FIREWALL"
target_signal = 25.0

print(f"STARTING TENSION: {engine.T_sys}")

# INTERVENTION 1
engine.apply_intervention("DEEP")
engine.step(target_signal)
print(f"POST-CLEAN 1: Tension={engine.T_sys:.4f}, Phase={engine.phase}")

# INTERVENTION 2 (The Double-Tap)
engine.apply_intervention("DEEP")
engine.step(target_signal)
print(f"POST-CLEAN 2: Tension={engine.T_sys:.4f}, Phase={engine.phase}")
