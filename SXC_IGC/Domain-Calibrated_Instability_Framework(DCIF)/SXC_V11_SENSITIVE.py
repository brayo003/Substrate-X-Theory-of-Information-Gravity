import numpy as np
import pandas as pd
from SXC_HISTORICAL_INGEST import get_historical_signals

# Load 2020 Data
fin_e_raw, geo_e, raw_vix = get_historical_signals()

# BI-MODAL EXCITATION CALIBRATION
# Re-mapping E to be ultra-sensitive above VIX 50
def bi_modal_excitation(vix_array):
    e_out = []
    for v in vix_array:
        if v < 45:
            # Standard Logarithmic Absorption
            e = 1 - np.exp(-v / 40.0)
        else:
            # Linear Acceleration (Structural Threat)
            e = 0.675 + ((v - 45.0) / 20.0) 
        e_out.append(e)
    return np.array(e_out)

fin_e = bi_modal_excitation(raw_vix)

# Simulation Loop
T_sys = 0.0
phase = "NOMINAL"
gamma, beta, dt = 0.8, 3.5, 0.05

print(f"\n{'DAY':<8} | {'TENSION':<8} | {'PHASE':<12} | {'VIX_REAL':<8} | {'E_SENSITIVE'}")
print("-" * 75)

for i in range(len(fin_e)):
    is_fw = (phase == "FIREWALL")
    gamma_eff = 2.2 if is_fw else 1.0
    
    inflow = ((fin_e[i] * 0.7) + (geo_e[i] * 0.3)) * beta
    outflow = gamma_eff * gamma * T_sys
    T_sys += (inflow - outflow) * dt

    if T_sys > 1.0:
        phase = "FIREWALL"
    elif phase == "FIREWALL" and T_sys < 0.4:
        phase = "NOMINAL"

    print(f"Day {i:<8} | {T_sys:>8.4f} | {phase:<12} | {raw_vix[i]:>8.2f} | {fin_e[i]:>8.4f}")
