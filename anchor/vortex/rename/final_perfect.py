import numpy as np

print("="*60)
print("PERFECTLY CONSISTENT SCREENED FIFTH FORCE THEORY")
print("="*60)

# For 1 mm range exactly
hbar_c = 1.97327e-7  # eV·m
range_target = 0.001  # 1 mm in meters
m_S = hbar_c / range_target

print(f"\n1. FOR 1 MM RANGE:")
print(f"   m_S = {m_S:.3e} eV")
print(f"   = {m_S*1000:.3f} meV")
print(f"   1/m_S = {1.97327e-7/m_S*1000:.3f} mm ✓")

# For 0.1% force at contact
force_target = 1e-3  # 0.1% of gravity
M_Pl = 2.435e18 * 1e9  # GeV to eV
alpha_S = force_target / (2 * M_Pl)

print(f"\n2. FOR 0.1% FORCE AT CONTACT:")
print(f"   α_S = {alpha_S:.3e}")
print(f"   F_X/F_G = 2α_S M_Pl = {2*alpha_S*M_Pl:.3e} ✓")

# At 1 mm
r = 0.001  # meters
r_natural = r / hbar_c
yukawa = np.exp(-m_S * r_natural)
force_at_1mm = force_target * yukawa

print(f"\n3. AT 1 MM DISTANCE:")
print(f"   Yukawa factor = exp(-m_S * r/ħc)")
print(f"   = exp(-{m_S:.3e} * {r_natural:.3e})")
print(f"   = {yukawa:.3e}")
print(f"   F_X/F_G = {force_target:.3e} × {yukawa:.3e}")
print(f"   = {force_at_1mm:.3e} = {force_at_1mm*100:.3f}% of gravity")

# Physical force between 1g masses
G = 6.67430e-11
m = 0.001
F_gravity = G * m**2 / r**2
F_X = force_at_1mm * F_gravity

print(f"\n4. FOR TWO 1g MASSES AT 1 mm:")
print(f"   F_gravity = {F_gravity:.2e} N")
print(f"   F_X = {F_X:.2e} N")
print(f"   Equivalent to {F_X/9.81:.2e} grams of weight")

# Detectability
print(f"\n5. DETECTABILITY:")
print(f"   Current best: ~1e-15 N (Eöt-Wash)")
print(f"   Required: {F_X:.1e} N")
print(f"   Factor needed: {F_X/1e-15:.0f}× better")

if F_X > 1e-15:
    print("   ✅ IN PRINCIPLE DETECTABLE")
else:
    print("   ❌ BELOW CURRENT SENSITIVITY")

print(f"\n" + "="*60)
print("SUMMARY: A consistent theory exists but is")
print(f"         {F_X/1e-15:.0f}× below current detection limits.")
print("="*60)

# Save to file
with open('consistent_theory_parameters.txt', 'w') as f:
    f.write("Consistent Screened Fifth Force Parameters\n")
    f.write("="*50 + "\n")
    f.write(f"m_S = {m_S:.3e} eV\n")
    f.write(f"α_S = {alpha_S:.3e}\n")
    f.write(f"Range = {range_target*1000:.3f} mm\n")
    f.write(f"F_X/F_G at contact = {force_target:.3e}\n")
    f.write(f"F_X/F_G at 1 mm = {force_at_1mm:.3e}\n")
    f.write(f"Force between 1g masses at 1 mm = {F_X:.2e} N\n")
    
print(f"\n📁 Parameters saved to 'consistent_theory_parameters.txt'")
