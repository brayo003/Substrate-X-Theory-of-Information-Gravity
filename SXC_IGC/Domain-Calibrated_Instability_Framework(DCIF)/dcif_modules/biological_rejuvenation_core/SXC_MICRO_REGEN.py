import numpy as np

T_sys = 0.0
phase = "NOMINAL"
beta = 3.5
gamma_young = 0.8
gamma_current = gamma_young
decay_rate = 0.005
dt = 0.05

print(f"{'DAY':<8} | {'TENSION':<8} | {'γ (DAMPING)':<12} | {'PHASE':<12} | {'STATE'}")
print("-" * 75)

for day in range(1001):
    E_noise = np.random.uniform(0.1, 0.4)
    
    # Natural Aging
    gamma_current *= (1 - decay_rate * 0.1)
    
    # MICRO-INTERVENTION: 5% Recovery every 100 days
    if day > 0 and day % 100 == 0:
        gamma_current = min(gamma_young, gamma_current * 1.05)
        # Indicator of maintenance
        # print(f"[FIX] Day {day}: γ boosted to {gamma_current:.4f}")

    # Physics Engine
    is_fw = (phase == "FIREWALL")
    gamma_eff = 2.2 if is_fw else 1.0
    inflow = E_noise * beta
    outflow = gamma_eff * gamma_current * T_sys
    T_sys += (inflow - outflow) * dt
    
    if T_sys > 1.0: phase = "FIREWALL"
    elif phase == "FIREWALL" and T_sys < 0.4: phase = "NOMINAL"
    
    if day % 100 == 0 or day == 999:
        status = "HEALTHY" if T_sys < 0.5 else ("SENESCENT" if is_fw else "STRESSED")
        print(f"{day:<8} | {T_sys:>8.4f} | {gamma_current:>12.4f} | {phase:<12} | {status}")
