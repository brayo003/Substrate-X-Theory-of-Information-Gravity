import numpy as np

omega_max = 1e6
Gamma0 = 5e5           # typical NV T2* rate
omega_exp = 1e6        # a typical achievable rotation rate? (arbitrary)
noise_floor = 0.02     # 2% relative uncertainty in Γ

k_vals = np.logspace(-12, -4, 20)

print("Sensitivity analysis for k_rot")
print("k_rot (s)    | extra Γ (s⁻¹) | fraction of Γ0 | detectable? (>2%)")
for k in k_vals:
    extra = k * omega_exp**2 / (1 + (omega_exp/omega_max)**2)
    frac = extra / Gamma0
    detect = frac > noise_floor
    print(f"{k:.1e}        {extra:.2e}        {frac:.4f}         {'YES' if detect else 'no'}")
