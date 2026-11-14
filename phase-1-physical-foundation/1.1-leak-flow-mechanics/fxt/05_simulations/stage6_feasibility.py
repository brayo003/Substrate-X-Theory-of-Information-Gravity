import numpy as np

omega_max = 1e6
omega_test = 1e6     # test rotation rate
Gamma0 = 5e5          # NV T2*
rel_uncertainty = 0.02 # 2% uncertainty in Γ measurement

# Minimum detectable extra decoherence: Delta_Gamma_min = rel_uncertainty * Gamma0
Delta_Gamma_min = rel_uncertainty * Gamma0

# From substrate: Delta_Gamma = k_rot * omega^2 / (1 + (omega/omega_max)^2)
# Solve for k_rot_min:
k_rot_min = Delta_Gamma_min * (1 + (omega_test/omega_max)**2) / omega_test**2

print("Experimental feasibility")
print(f"Base Γ0 = {Gamma0:.2e} s⁻¹")
print(f"Measurement uncertainty = {rel_uncertainty*100:.0f}%  → ΔΓ_min = {Delta_Gamma_min:.2e} s⁻¹")
print(f"At test rotation ω = {omega_test:.2e} rad/s")
print(f"Minimum detectable k_rot = {k_rot_min:.2e} s")
print(f"Your predicted k_rot = 4.5e-7 s")
if 4.5e-7 > k_rot_min:
    print("→ Predicted effect IS detectable with current precision.")
else:
    print("→ Predicted effect is BELOW current detection threshold.")
