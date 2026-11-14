import numpy as np
import matplotlib.pyplot as plt

omega_max = 1e6
Gamma0 = 5e5
rel_uncertainty = 0.02   # 2%

omega_range = np.logspace(3, 9, 100)   # 1e3 to 1e9 rad/s

# Minimum detectable extra decoherence: ΔΓ_min = rel_uncertainty * Gamma0
Delta_Gamma_min = rel_uncertainty * Gamma0

# Solve for k_min: k_min = ΔΓ_min * (1 + (ω/ω_max)^2) / ω^2
k_min = Delta_Gamma_min * (1 + (omega_range/omega_max)**2) / omega_range**2

plt.figure(figsize=(8,5))
plt.loglog(omega_range, k_min, 'b-', label='Detection threshold $k_{min}$')
plt.axhline(4.5e-7, color='red', linestyle='--', label='Predicted $k_{rot}=4.5\\times10^{-7}$ s')
plt.fill_between(omega_range, k_min, 1e-3, alpha=0.1, color='green', label='Detectable region')
plt.xlabel('Rotation frequency $\\omega$ (rad/s)')
plt.ylabel('Minimum detectable $k_{rot}$ (s)')
plt.title('Substrate X detectability map (2% measurement uncertainty)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('stage6_detectability_map.png', dpi=150)

# Print some representative values
print("Detectability map (2% uncertainty):")
print("ω (rad/s)    | k_min (s)   | Prediction detectable?")
for w in [1e3, 1e4, 1e5, 1e6, 1e7, 1e8]:
    kmin = Delta_Gamma_min * (1 + (w/omega_max)**2) / w**2
    detectable = 4.5e-7 > kmin
    print(f"{w:.1e}      {kmin:.2e}       {'YES' if detectable else 'no'}")
