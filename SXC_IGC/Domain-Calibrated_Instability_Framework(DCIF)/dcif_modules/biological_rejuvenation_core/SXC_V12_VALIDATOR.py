import numpy as np
from SXC_V12_CORE import SXCOmegaEngine
from SXC_HISTORICAL_2008 import get_2008_signals

# 1. Initialize Engine
engine = SXCOmegaEngine()

# 2. Ingest 2008 Data
_, _, raw_vix = get_2008_signals()

print(f"{'DAY':<5} | {'VIX':<8} | {'TENSION':<8} | {'PHASE':<12}")
print("-" * 45)

# 3. Process Stream
for i, v in enumerate(raw_vix):
    # Apply Maintenance Pulse (Aging/Systemic Fatigue Mitigation)
    if i > 0 and i % 30 == 0: 
        engine.apply_intervention("DEEP")
    
    t, p = engine.step(v)
    
    # Log transitions and checkpoints
    if i % 5 == 0 or p == "FIREWALL":
        print(f"{i:<5} | {v:<8.2f} | {t:>8.4f} | {p:<12}")
