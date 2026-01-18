import numpy as np

print("="*70)
print("SCREENED FIFTH FORCE AS DARK MATTER ALTERNATIVE")
print("="*70)

# Our consistent parameters
m_S = 1.973e-4  # eV
alpha_S = 2.053e-31
hbar_c = 1.97327e-7  # eV·m
M_Pl = 2.435e18 * 1e9  # GeV to eV

# 1. Galactic scale effects
print("\n1. GALACTIC SCALES:")
print("-"*40)

# Milky Way: ~100,000 light years across
ly_to_m = 9.461e15
galaxy_size = 1e5 * ly_to_m  # meters

# Yukawa suppression at galactic scales
r_galaxy = galaxy_size / 2  # half-radius
r_natural = r_galaxy / hbar_c
yukawa_galaxy = np.exp(-m_S * r_natural)

print(f"Galaxy radius: {galaxy_size/ly_to_m:.0f} ly = {galaxy_size:.2e} m")
print(f"Yukawa factor at galaxy edge: {yukawa_galaxy:.3e}")
print(f"That's essentially ZERO at galactic scales.")

# 2. But what if dark matter ISN'T particles?
print("\n2. ALTERNATIVE: Modified Gravity (MOND-like):")
print("-"*40)

# MOND acceleration scale: a₀ ≈ 1.2e-10 m/s²
a0 = 1.2e-10

# Our force strength at 1 kpc (kiloparsec)
kpc_to_m = 3.086e19
r_kpc = 1 * kpc_to_m
yukawa_kpc = np.exp(-m_S * (r_kpc / hbar_c))

# Force from our theory at 1 kpc
F_ratio = 2 * alpha_S * M_Pl * yukawa_kpc
print(f"At 1 kpc (~3260 ly):")
print(f"  Yukawa factor: {yukawa_kpc:.3e}")
print(f"  F_X/F_G: {F_ratio:.3e}")
print(f"  Acceleration ratio: {F_ratio:.3e}")

# Too small! Our force dies too fast for galaxy rotation curves

# 3. What if m_S is MUCH smaller for dark matter?
print("\n3. REQUIRED FOR DARK MATTER REPLACEMENT:")
print("-"*40)

# Need force to work at ~10 kpc scale
r_dm = 10 * kpc_to_m

# Solve for m_S that gives 50% suppression at 10 kpc
# yukawa = exp(-m_S * r/ħc) = 0.5
m_S_dm = -np.log(0.5) * hbar_c / r_dm
print(f"For 50% suppression at 10 kpc:")
print(f"  Required m_S = {m_S_dm:.3e} eV")
print(f"  Range = {hbar_c/m_S_dm/ly_to_m:.1f} light years")
print(f"  That's {m_S_dm/m_S:.1e}× smaller than our 1 mm force")

# Corresponding α_S for same force strength
alpha_S_dm = alpha_S * (m_S_dm/m_S)**2  # Rough scaling
print(f"  Required α_S ≈ {alpha_S_dm:.3e}")

print("\n" + "="*70)
print("CONCLUSION:")
print("Our 1 mm force CANNOT explain dark matter directly.")
print("But a similar mechanism with m_S ~ 10⁻²⁶ eV could.")
print("="*70)
