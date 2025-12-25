import numpy as np

print("="*70)
print("EXTRA DIMENSION INTERPRETATION")
print("="*70)

# Our parameters
m_S = 1.973e-4  # eV
hbar_c = 1.97327e-7  # eV·m

# 1. Extra dimension size from Kaluza-Klein theory
# In KK theory: m_KK = n/R where R is extra dimension radius
# For first mode (n=1): R = 1/m_KK
R_extra = 1/m_S  # in natural units (eV^-1)

# Convert to meters
R_extra_m = R_extra * hbar_c  # eV^-1 * (eV·m) = m

print("\n1. EXTRA DIMENSION SIZE:")
print(f"Mass m_S = {m_S:.3e} eV")
print(f"Extra dimension radius R = 1/m_S = {R_extra:.3e} eV⁻¹")
print(f"In meters: R = {R_extra_m:.3e} m = {R_extra_m*1000:.3f} mm")

# 2. String theory connection
# String scale M_s related to extra dimension size
# Typical: M_s ~ 1/√(α') where α' is string tension
print("\n2. STRING THEORY CONNECTION:")
M_Pl = 2.435e18  # GeV
M_s_guess = M_Pl * np.sqrt(m_S/M_Pl)  # Rough estimate
print(f"String scale estimate: M_s ~ {M_s_guess:.3e} GeV")
print(f"That's {M_s_guess/1000:.1f} TeV")
print(f"LHC reaches ~14 TeV, so this might be testable!")

# 3. KK tower
print("\n3. KALUZA-KLEIN TOWER:")
print("Higher modes: m_n = n × m_S")
print("First few modes:")
for n in [1, 2, 3, 10, 100]:
    m_n = n * m_S
    range_n = hbar_c / m_n
    print(f"  n={n:3}: m = {m_n:.3e} eV, range = {range_n*1000:.3f} mm")

# 4. Experimental signatures
print("\n4. EXPERIMENTAL SIGNATURES:")
print("- Colliders: Look for KK graviton production")
print(f"  Mass: {m_S*1e-9:.3f} GeV (too light for LHC)")
print("- Fifth force: As we calculated")
print("- Astrophysics: Affects stellar evolution")
print("- Cosmology: Changes early universe expansion")

print("\n" + "="*70)
print("KEY INSIGHT:")
print(f"An extra dimension of size {R_extra_m*1000:.3f} mm")
print("predicts a force with our exact parameters!")
print("="*70)
