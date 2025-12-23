import numpy as np
import time

# System Constants
T_sys = 0.0
phase = "NOMINAL"
beta = 3.5
gamma_young = 0.8
gamma_current = gamma_young
decay_rate = 0.005  # Progressive loss of repair capacity
dt = 0.05

print(f"{'DAY':<8} | {'TENSION':<8} | {'DAMPING (γ)':<12} | {'PHASE':<12} | {'STATE'}")
print("-" * 75)

for day in range(1001):
    # 1. Simulate constant environmental excitation (Metabolic Stress)
    # Plus random oxidative spikes (E_noise)
    E_noise = np.random.uniform(0.1, 0.4)
    
    # 2. Aging: Damping Coefficient Decay
    if day < 750:
        gamma_current *= (1 - decay_rate * 0.1) # Natural aging
    
    # 3. INTERVENTION: Project Rejuvenation at Day 750
    if day == 750:
        print("\n[!!!] INTERVENTION: RESTORING SUBSTRATE DAMPING [!!!]\n")
        gamma_current = gamma_young # Resetting to "Young" levels
        
    # 4. Physics Engine
    is_fw = (phase == "FIREWALL")
    gamma_eff = 2.2 if is_fw else 1.0
    
    inflow = E_noise * beta
    outflow = gamma_eff * gamma_current * T_sys
    T_sys += (inflow - outflow) * dt
    
    # 5. Threshold Logic
    if T_sys > 1.0: phase = "FIREWALL"
    elif phase == "FIREWALL" and T_sys < 0.4: phase = "NOMINAL"
    
    # 6. Logging
    if day % 50 == 0 or day == 749 or day == 751:
        status = "HEALTHY" if T_sys < 0.5 else ("SENESCENT" if is_fw else "STRESSED")
        print(f"{day:<8} | {T_sys:>8.4f} | {gamma_current:>12.4f} | {phase:<12} | {status}")
