import numpy as np

# From the theory paper
alpha_S = 5e-21
G = 6.67430e-11  # N·m²/kg²
M_Pl = 2.176434e-8  # kg (Planck mass)

# Force ratio at contact
F_ratio = alpha_S / (4 * np.pi * G * M_Pl**2)

# Yukawa range
m_S = 2e-10  # eV
hbar_c = 1.97327e-7  # eV·m
range_m = 1/(m_S / hbar_c)  # in meters

print("Physics Check:")
print("==============")
print(f"Coupling α_S = {alpha_S:.1e}")
print(f"Mass m_S = {m_S:.1e} eV")
print(f"Yukawa range = {range_m*1000:.2f} mm")
print(f"Contact force ratio F_X/F_G = {F_ratio:.3e}")
print()
print("Interpretation:")
if F_ratio > 1e-3:
    print("✅ Predicted force is >0.1% of gravity - detectable")
elif F_ratio > 1e-6:
    print("⚠️  Very weak but might be detectable with precision instruments")
else:
    print("❌ Too weak for current technology")
