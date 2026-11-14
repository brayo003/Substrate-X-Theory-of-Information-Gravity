import numpy as np
from scipy.optimize import fsolve

# Fixed Substrate Constants
a = 0.05      # Birth/Growth acceleration
beta = 0.1    # Sensitivity
kappa = 5.0   # Resource pool
z_target = 7.15 # Our derived critical height

def find_stability_gamma(gamma_guess):
    # We want to find a gamma where the "Push" equals the "Pull"
    # At equilibrium T*, the quadratic growth must be manageable
    # f = aT^2 - gamma*T + beta*kappa/z
    
    # Let's test for a small, sustainable population T = 1.0
    T_stable = 1.0
    balance = a*(T_stable**2) - gamma_guess*T_stable + (beta*kappa/z_target)
    return balance

gamma_stable = fsolve(find_stability_gamma, 0.1)[0]

print(f"=== STABILITY AUDIT ===")
print(f"To prevent Shatter at z = {z_target}:")
print(f"Required Damping (gamma) must be >= {gamma_stable:.4f}")
print(f"Current System Gamma was: 0.1000")
print(f"Stability Gap: {gamma_stable - 0.1:.4f}")

if gamma_stable > 0.1:
    print("\nRESULT: The system is structurally destined to fail unless damping increases.")
else:
    print("\nRESULT: The system is inherently stable.")
