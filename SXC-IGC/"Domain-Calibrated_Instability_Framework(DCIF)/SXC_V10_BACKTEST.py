import numpy as np
import pandas as pd
from SXC_HISTORICAL_INGEST import get_historical_signals

# Load Real Data (VIX and Oil/Supply Chain)
fin_e, geo_e, raw_vix = get_historical_signals()

# Simulation Parameters
T_sys = 0.0
phase = "NOMINAL"
gamma = 0.8
beta = 3.5
dt = 0.05 

print(f"\n{'DAY':<10} | {'TENSION':<8} | {'PHASE':<12} | {'VIX_REAL':<8} | {'STATUS'}")
print("-" * 75)

for i in range(len(fin_e)):
    is_fw = (phase == "FIREWALL")
    # V10 Adaptive Damping
    gamma_eff = 2.2 if is_fw else 1.0
    
    # Inflow combines Finance (VIX) and Geopolitical (Oil Vol)
    total_excitation = (fin_e[i] * 0.7) + (geo_e[i] * 0.3)
    inflow = total_excitation * beta
    outflow = gamma_eff * gamma * T_sys
    
    T_sys = max(0.0, T_sys + (inflow - outflow))
    
    # Hysteresis Logic
    if T_sys >= 1.0: phase = "FIREWALL"
    elif phase == "FIREWALL" and T_sys < 0.4: phase = "NOMINAL"
    
    status = "STABILIZING" if (is_fw and T_sys < 2.5) else "ANALYZING"
    if is_fw and T_sys > 2.5: status = "CRITICAL_LOAD"
    
    print(f"Day {i:<7} | {T_sys:>8.4f} | {phase:<12} | {raw_vix[i]:>8.2f} | {status}")
