import numpy as np

print("="*70)
print("FINDING PARAMETERS THAT FIT EXPERIMENTS")
print("="*70)

# Eöt-Wash limit at 0.1 mm: F_max = 3e-13 N (for 1g masses)
F_max_01mm = 3e-13
r_test = 0.0001  # 0.1 mm
G = 6.67430e-11
m = 0.001
F_g = G * m**2 / r_test**2

print(f"At 0.1 mm:")
print(f"  Gravity force: {F_g:.2e} N")
print(f"  Max allowed F_X: {F_max_01mm:.2e} N")
print(f"  Max F_X/F_G: {F_max_01mm/F_g:.2e}")

# Your original: F_X/F_G = 2αM_Pl = 9.04e-4
# But needs to be < F_max/F_g = 4.50e-5
required_reduction = (9.04e-4) / (4.50e-5)
print(f"\nNeed to reduce α_S by factor: {required_reduction:.1f}")

# New α_S
alpha_S_original = 2.053e-31
alpha_S_new = alpha_S_original / required_reduction

print(f"\nOriginal α_S: {alpha_S_original:.3e}")
print(f"New α_S (to fit Eöt-Wash): {alpha_S_new:.3e}")

# What force would this give at 1 mm?
hbar_c = 1.97327e-7
m_S = 1.973e-4
M_Pl = 2.435e18 * 1e9

r_1mm = 0.001
F_g_1mm = G * m**2 / r_1mm**2
yukawa_1mm = np.exp(-m_S * r_1mm / hbar_c)
F_X_1mm_new = 2 * alpha_S_new * M_Pl * F_g_1mm * yukawa_1mm

print(f"\nAt 1 mm with new α_S:")
print(f"  F_X predicted: {F_X_1mm_new:.2e} N")
print(f"  Current sensitivity: ~1e-15 N")
print(f"  Need improvement: {1e-15/F_X_1mm_new:.1f}×")

print("\n" + "="*70)
print("PARAMETER SPACE SUMMARY:")
print("-"*70)
print("To fit Eöt-Wash 2012 data:")
print(f"  m_S must stay ~2e-4 eV for 1 mm range")
print(f"  α_S must be < {alpha_S_new:.3e}")
print(f"  That's {alpha_S_original/alpha_S_new:.1f}× smaller than your value")
print("\nWith these parameters:")
print(f"  Force at 1 mm: {F_X_1mm_new:.2e} N")
print(f"  Need sensitivity: {F_X_1mm_new:.2e} N")
print(f"  Current best: 1e-15 N")
print(f"  Need improvement: {1e-15/F_X_1mm_new:.0f}×")
print("="*70)

# Save allowed parameters
with open('allowed_parameters.txt', 'w') as f:
    f.write("PARAMETERS THAT FIT EXPERIMENTAL DATA\n")
    f.write("="*50 + "\n")
    f.write(f"m_S = {m_S:.3e} eV\n")
    f.write(f"α_S < {alpha_S_new:.3e}\n")
    f.write(f"Force range = {hbar_c/m_S*1000:.3f} mm\n")
    f.write(f"F_X/F_G at contact < {2*alpha_S_new*M_Pl:.3e}\n")
    f.write(f"Force at 1 mm < {F_X_1mm_new:.2e} N\n")
    f.write(f"\nExperimental status:\n")
    f.write(f"Current sensitivity: 1e-15 N\n")
    f.write(f"Required to test: {F_X_1mm_new:.2e} N\n")
    f.write(f"Improvement needed: {1e-15/F_X_1mm_new:.0f}×\n")

print(f"\n📁 Allowed parameters saved to 'allowed_parameters.txt'")
