import numpy as np

print("="*70)
print("FIXED NEUTRON STAR CALCULATIONS")
print("="*70)

# Our parameters - BUT THESE ARE PROBABLY WRONG FOR ASTROPHYSICS
m_S = 1.973e-4  # eV
alpha_S = 2.053e-31
hbar = 1.05457e-34
c = 299792458
G = 6.67430e-11
M_sun = 1.9885e30
eV = 1.60218e-19

print("\nPROBLEM IDENTIFIED:")
print("-"*40)
print("Our parameters give:")
print(f"m_S = {m_S:.3e} eV = {m_S*eV:.3e} J")
print(f"Mass equivalent: {m_S*eV/c**2:.3e} kg")
print("This is LIGHTER than an electron!")
print("Such a light field would have HUGE effects.")

print("\nREALITY CHECK:")
print("-"*40)
# For neutron stars, any new force must be:
# 1. Either very weak (α_S << our value)
# 2. Or very heavy (m_S >> our value)
# 3. Or screened much more effectively

# Correct approach: pressure from a massive vector field
# P_X ~ α_S * ρ² * ħ³/(m_S⁴ c⁵)

rho_ns = 3.8e17  # kg/m³
rho_SI = rho_ns  # kg/m³

# Convert to natural units: ρ in J/m³
rho_J = rho_SI * c**2  # J/m³

# Characteristic energy density
# For a force with range λ = ħ/(m_S c)
lambda_S = hbar/(m_S*eV/c * c)  # m
print(f"Force range: {lambda_S:.3e} m")

# Screening happens when potential V ~ m_S² X²
# In dense matter: X ~ α_S ρ/(m_S² M_Pl)
M_Pl = np.sqrt(hbar*c/G)

# Screening condition in neutron star
X_ns = alpha_S * rho_J / (m_S**2 * eV**2 * M_Pl)
V_ns = 0.5 * m_S**2 * eV**2 * X_ns**2

print(f"\nIn neutron star core:")
print(f"Field amplitude X: {X_ns:.3e} (dimensionless)")
print(f"Potential energy: {V_ns:.3e} J/m³")
print(f"Compared to ρc²: {V_ns/rho_J:.3e}")

if V_ns/rho_J < 1e-6:
    print("✅ Force weakly coupled in NS")
    effect = V_ns/rho_J
    print(f"Expected effects: ~{effect*100:.3e}%")
else:
    print("❌ Force strongly coupled - would alter NS dramatically")

# Realistic estimate for allowed parameters
print("\nREALISTIC PARAMETER BOUNDS FROM NS:")
print("-"*40)
# Observations constrain NS structure to ~1%
# So any new force must contribute <1% to pressure

# Solve for maximum α_S given m_S
alpha_max = 1e-2 * m_S**2 * M_Pl**2 / rho_J  # Rough scaling
print(f"For m_S = {m_S:.3e} eV:")
print(f"Maximum allowed α_S < {alpha_max:.3e}")
print(f"Our α_S = {alpha_S:.3e}")
print(f"Ratio: {alpha_S/alpha_max:.3e}")

if alpha_S < alpha_max:
    print("✅ Parameters allowed by NS observations")
else:
    print("❌ Parameters ruled out by NS observations")

print("\n" + "="*70)
print("CONCLUSION: Need to check parameter consistency")
print("Our α_S might be too large for given m_S")
print("="*70)
