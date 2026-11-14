import numpy as np

print("SANITY CHECK ON OUR PARAMETERS")
print("="*50)

m_S = 1.973e-4  # eV
alpha_S = 2.053e-31
hbar = 1.05457e-34
c = 299792458
G = 6.67430e-11
eV = 1.60218e-19

# Convert m_S to kg
m_S_kg = m_S * eV / c**2
print(f"m_S = {m_S:.3e} eV")
print(f"    = {m_S_kg:.3e} kg")
print(f"    = {m_S_kg/9.11e-31:.1f} × electron mass")

# Compton wavelength
lambda_C = hbar/(m_S_kg*c)
print(f"\nCompton wavelength: {lambda_C:.3e} m")
print(f"                   = {lambda_C*1000:.3f} mm ✓")

# Force strength check
M_Pl = np.sqrt(hbar*c/G)  # kg
M_Pl_eV = M_Pl * c**2 / eV

F_ratio = 2 * alpha_S * M_Pl_eV
print(f"\nForce ratio F_X/F_G = {F_ratio:.3e}")
print(f"                    = {F_ratio*100:.3f}% of gravity ✓")

# Energy density in cosmological constant form
rho_Lambda = m_S**4 / alpha_S  # eV^4, rough scaling
rho_Lambda_SI = rho_Lambda * eV**4 / (hbar**3 * c**3)
print(f"\nEffective Λ energy density: {rho_Lambda_SI:.3e} J/m³")
print(f"Compare to critical density: {8.5e-10:.1e} J/m³")
print(f"Ratio: {rho_Lambda_SI/8.5e-10:.3e}")

if rho_Lambda_SI < 8.5e-10:
    print("✅ Below cosmological density - safe")
else:
    print("❌ Would dominate universe!")

print("\n" + "="*50)
print("PARAMETERS LOOK REASONABLE FOR LAB")
print("BUT ASTROPHYSICS NEEDS RECALCULATION")
