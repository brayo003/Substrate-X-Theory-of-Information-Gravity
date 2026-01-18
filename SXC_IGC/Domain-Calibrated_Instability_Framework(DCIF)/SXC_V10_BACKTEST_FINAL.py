import numpy as np
import pandas as pd
from SXC_HISTORICAL_INGEST import get_historical_signals

# Load Real Data
fin_e, geo_e, raw_vix = get_historical_signals()

# Stability Constants
T_sys = 0.0
phase = "NOMINAL"
gamma = 0.8
beta = 3.5
dt = 0.05 

print(f"\n{'DAY':<8} | {'TENSION':<8} | {'PHASE':<12} | {'VIX_REAL':<8} | {'STATUS'}")
print("-" * 75)

for i in range(len(fin_e)):
    is_fw = (phase == "FIREWALL")
    gamma_eff = 2.2 if is_fw else 1.0

    # Multi-domain Inflow
    total_excitation = (fin_e[i] * 0.7) + (geo_e[i] * 0.3)
    inflow = total_excitation * beta
    outflow = gamma_eff * gamma * T_sys

    # Correct Integration
    T_sys += (inflow - outflow) * dt

    # Threshold Logic
    if T_sys > 1.0:
        phase = "FIREWALL"
        status = "STABILIZING" if T_sys > 1.5 else "ANALYZING"
    else:
        if phase == "FIREWALL" and T_sys < 0.4: # Hysteresis
            phase = "NOMINAL"
        status = "STABILIZING"

    print(f"Day {i:<8} | {T_sys:>8.4f} | {phase:<12} | {raw_vix[i]:>8.2f} | {status}")
