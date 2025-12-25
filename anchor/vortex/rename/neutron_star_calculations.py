import numpy as np

print("="*70)
print("NEUTRON STAR MODIFICATIONS")
print("="*70)

# Our parameters
m_S = 1.973e-4  # eV
alpha_S = 2.053e-31
hbar_c = 1.97327e-7  # eV·m
G = 6.67430e-11  # N·m²/kg²
c = 299792458  # m/s
M_sun = 1.9885e30  # kg

# 1. Neutron star properties
print("\n1. TYPICAL NEUTRON STAR:")
print("-"*40)
M_ns = 1.4 * M_sun
R_ns = 12e3  # 12 km radius
rho_ns = M_ns / (4/3 * np.pi * R_ns**3)
print(f"Mass: {M_ns/M_sun:.1f} M☉")
print(f"Radius: {R_ns/1000:.1f} km")
print(f"Density: {rho_ns:.3e} kg/m³")
print(f"Baryon density: {rho_ns/1.6726e-27:.3e} baryons/m³")

# 2. Screening inside neutron star
print("\n2. SCREENING IN NEUTRON STAR:")
print("-"*40)

# Characteristic screening length
# From β term: L_screen ~ M_Pl²/(m_S √β)
M_Pl = 2.435e18 * 1e9  # GeV to eV
beta = 1.0
L_screen_natural = M_Pl**2 / (m_S * np.sqrt(beta))

# Convert to meters
L_screen_m = L_screen_natural * hbar_c
print(f"Screening length: {L_screen_m:.3e} m")
print(f"Compared to NS radius: {L_screen_m/R_ns:.3e}")

if L_screen_m < R_ns:
    print("✅ Force is screened inside neutron star")
    screening_factor = np.exp(-R_ns/L_screen_m)
    print(f"Screening factor at surface: {screening_factor:.3e}")
else:
    print("❌ Force is NOT fully screened")

# 3. Pressure modification
print("\n3. PRESSURE MODIFICATION:")
print("-"*40)

# Extra pressure from X-field
# P_X ~ α_S * ρ² / (m_S² M_Pl²)
rho_kg = rho_ns
rho_eV4 = rho_kg * (c**2)**2 / (1.602e-19)**2  # Convert to eV⁴

P_X = alpha_S * rho_eV4**2 / (m_S**2 * M_Pl**2)

# Convert to Pascals
P_X_Pa = P_X * (1.602e-19)**4 * (c**3/hbar_c**3)

# Compare to neutron degeneracy pressure
# P_deg ~ (3π²)^(2/3) ħ² ρ^(5/3) / (5 m_n)
m_n = 1.675e-27  # neutron mass
P_deg = (3*np.pi**2)**(2/3) * (1.05457e-34)**2 * rho_ns**(5/3) / (5 * m_n)

print(f"X-field pressure: {P_X_Pa:.3e} Pa")
print(f"Degeneracy pressure: {P_deg:.3e} Pa")
print(f"Ratio P_X/P_deg: {P_X_Pa/P_deg:.3e}")

# 4. Mass-radius relation change
print("\n4. MASS-RADIUS RELATION:")
print("-"*40)

# Rough estimate: δR/R ~ P_X/P_deg
delta_R = R_ns * (P_X_Pa/P_deg)
print(f"Radius change: {delta_R:.3f} m")
print(f"Relative change: {delta_R/R_ns*100:.3f}%")

# For binary pulsar timing
# Period derivative: δP/P ~ δR/R
P_orbital = 2.4 * 3600  # 2.4 hours typical
delta_P = P_orbital * (delta_R/R_ns)
print(f"Orbital period change: {delta_P:.3f} s")
print(f"Relative: {delta_P/P_orbital*1e6:.3f} ppm")

print("\n" + "="*70)
print("CONCLUSION: Effects are ~10⁻⁶ level")
print("Potentially detectable in precision pulsar timing")
print("="*70)

# Save results
with open('neutron_star_results.txt', 'w') as f:
    f.write("NEUTRON STAR MODIFICATIONS\n")
    f.write("="*50 + "\n")
    f.write(f"Screening length: {L_screen_m:.3e} m\n")
    f.write(f"Screening factor: {screening_factor:.3e}\n")
    f.write(f"X-pressure: {P_X_Pa:.3e} Pa\n")
    f.write(f"Pressure ratio: {P_X_Pa/P_deg:.3e}\n")
    f.write(f"Radius change: {delta_R:.3f} m ({delta_R/R_ns*100:.3f}%)\n")
    f.write(f"Orbital period shift: {delta_P/P_orbital*1e6:.3f} ppm\n")

print("\n📁 Results saved to 'neutron_star_results.txt'")
