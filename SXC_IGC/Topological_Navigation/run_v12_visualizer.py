import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Ensure the current directory is in the path
sys.path.append(os.getcwd())

from SXC_IGC.Topological_Navigation.gamma_radar_v12 import get_topological_tension

# 1. Create Substrate Health range (3.0 is Healthy, 0.0 is the Crash Pole)
health_range = np.linspace(3.0, -0.2, 500)
tension_values = [get_topological_tension(h) for h in health_range]

# 2. Plotting
plt.figure(figsize=(12, 7))
plt.plot(health_range, tension_values, label='Substrate Tension |Γ(z)|', color='red', lw=2)
plt.axvline(0, color='black', linestyle='--', label='Crash Pole (Singularity at 0)')
plt.axhline(5.0, color='blue', linestyle=':', label='V12 Governor Reset Threshold')

plt.title("SXC-V12-G: Topological Radar (1909 Mapping)")
plt.xlabel("Substrate Health (Stability -> Failure)")
plt.ylabel("Tension Magnitude")
plt.yscale('log')
plt.grid(True, which="both", ls="-", alpha=0.3)
plt.legend()

# 3. Finalize
plt.savefig('v12_gamma_radar.png')
print("-" * 50)
print("SUCCESS: v12_gamma_radar.png generated in current directory.")
print("LOGIC: As Health slides toward 0, Tension hits the Blue Line.")
print("This is where the V12 triggers the Hysteresis Reset.")
print("-" * 50)
