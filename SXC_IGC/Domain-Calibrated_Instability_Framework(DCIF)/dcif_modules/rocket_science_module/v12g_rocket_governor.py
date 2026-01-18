import math
from scipy.special import gamma

def calculate_rocket_tension(pressure, temp_celsius):
    # Normalize 'Health' based on thermal limits (Max 3000C)
    health = max(0.001, 1.0 - (temp_celsius / 3000.0))
    
    # Apply V12-G Logic: The 1909 Gamma Radar
    # As health approaches 0 (the pole), tension spikes
    tension = abs(gamma(health))
    
    return round(health, 4), round(tension, 4)

# Simulated Rocket Test
engine_pressures = [50, 150, 2500, 2990] # Temp in Celsius
for p in engine_pressures:
    h, t = calculate_rocket_tension(100, p)
    status = "STABLE" if t < 5.0 else "V12-G RESET TRIGGERED (ABORT)"
    print(f"Temp: {p}C | Health: {h} | Tension: {t} | Status: {status}")
