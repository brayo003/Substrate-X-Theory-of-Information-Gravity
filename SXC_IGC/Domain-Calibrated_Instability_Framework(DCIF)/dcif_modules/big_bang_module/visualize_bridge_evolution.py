import numpy as np
import matplotlib.pyplot as plt

# CONSTANTS
C = 299792458.0
PI = np.pi

# LOGARITHMIC RANGE: From Planck Length to Hubble Horizon
scales = np.logspace(-35, 26, 500) 

# THE BRIDGE EQUATION
a0_values = (C**2) / (4 * PI * scales)

plt.figure(figsize=(10, 6))
plt.loglog(scales, a0_values, color='cyan', linewidth=2, label='Substrate-X Bridge ($a_0$)')

# MARKING THE KEY REGIMES
plt.axvline(x=1.616e-35, color='red', linestyle='--', alpha=0.5, label='Planck Scale (Firewall)')
plt.axvline(x=1.37e26, color='yellow', linestyle='--', alpha=0.5, label='Hubble Horizon (Current)')
plt.scatter([3.086e19], [5.2e-11], color='magenta', zorder=5, label='Galactic Calibration (NGC 5055)')

plt.title("The Evolution of the Information Bridge")
plt.xlabel("Universal Scale $R_H$ (meters)")
plt.ylabel("Bridge Acceleration $a_0$ ($m/s^2$)")
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.legend()

# Annotations
plt.text(1e-34, 1e45, "PRIMORDIAL\nINFLATION", color='red', fontweight='bold')
plt.text(1e10, 1e-5, "GALACTIC\nSTABILITY", color='magenta', fontweight='bold')

plt.tight_layout()
plt.savefig('bridge_evolution_plot.png')
print("✅ Visualization Saved: bridge_evolution_plot.png")
