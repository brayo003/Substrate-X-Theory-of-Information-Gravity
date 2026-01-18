import numpy as np

print("="*80)
print("BUILDING A DARK MATTER-EXPLAINING FIFTH FORCE")
print("="*80)

# The REAL dark matter problem:
# 1. Galactic rotation curves flat
# 2. Missing mass in galaxy clusters  
# 3. Gravitational lensing
# 4. CMB anisotropies

print("\nDARK MATTER FACTS:")
print("-"*80)
print("1. Dark matter density today: ρ_DM ≈ 2.4e-27 kg/m³")
print("2. Dark matter halos: ~100 kpc size")
print("3. Characteristic velocity: v ~ 200 km/s")
print("4. No strong self-interaction: σ/m < 1 cm²/g")

print("\n" + "="*80)
print("HOW A FIFTH FORCE COULD EXPLAIN IT:")
print("="*80)
print("""
Instead of WIMPs (particles), maybe:
1. Normal matter feels an EXTRA force
2. This force is SCREENED on small scales (solar system)
3. But UNSCREENED on galactic scales
4. Makes galaxies rotate as if they have extra mass

This is called "MOdified Newtonian Dynamics" (MOND)
But MOND has problems with clusters and CMB.
A SCREENED fifth force could fix MOND's problems.
""")

# Let's calculate required parameters
print("\n" + "="*80)
print("CALCULATING REQUIRED PARAMETERS:")
print("="*80)

# MOND acceleration scale: a₀ ≈ 1.2e-10 m/s²
a0 = 1.2e-10

# For galaxy with mass M at distance R, need:
# Extra force F_X such that: v²/R = √(GM/R² * a₀)

# At characteristic scale: R ~ 10 kpc, v ~ 200 km/s
kpc = 3.086e19  # meters
R_gal = 10 * kpc
v_gal = 2e5  # m/s

# Observed acceleration
a_obs = v_gal**2 / R_gal

print(f"Galactic scale (10 kpc, 200 km/s):")
print(f"  Radius: {R_gal/kpc:.0f} kpc = {R_gal:.2e} m")
print(f"  Velocity: {v_gal/1000:.0f} km/s")
print(f"  Observed acceleration: {a_obs:.2e} m/s²")
print(f"  MOND scale a₀: {a0:.2e} m/s²")
print(f"  Ratio a_obs/a₀: {a_obs/a0:.2f}")

# Required force enhancement
F_enhancement = a_obs / np.sqrt(G * 1e11 * 1.9885e30 / R_gal**2 * a0)
# Actually simpler: in MOND, effective G' = G/μ(x) where x = a/a₀

print(f"\nRequired force enhancement at 10 kpc: ~{a_obs/a0:.1f}×")

# For a Yukawa force: F = F_N * (1 + α * e^{-r/λ})
# Need: α * e^{-R_gal/λ} ≈ a_obs/a₀ at R_gal

# Try λ ~ 10 kpc (force works at galactic scales)
lambda_dm = 10 * kpc  # 10 kpc range

hbar = 1.0545718e-34
c = 299792458
eV = 1.6021766e-19

m_dm = hbar * c / (lambda_dm * eV)  # eV
alpha_dm = a_obs/a0 / np.exp(-R_gal/lambda_dm)

print(f"\nFor Yukawa force with λ = {lambda_dm/kpc:.0f} kpc:")
print(f"  Required mediator mass: m = ħc/λ = {m_dm:.2e} eV")
print(f"  Required coupling: α = {alpha_dm:.2e}")

# Check screening in solar system
R_solar = 1.496e11  # 1 AU
screening_solar = alpha_dm * np.exp(-R_solar/lambda_dm)
print(f"\nIn solar system (1 AU):")
print(f"  Force enhancement: {screening_solar:.2e}")
print(f"  Completely screened ✓")

print("\n" + "="*80)
print("THIS THEORY WOULD:")
print("-"*80)
print("1. EXPLAIN galactic rotation without dark matter")
print("2. BE SCREENED in solar system (pass tests)")
print("3. PREDICT different cluster dynamics than ΛCDM")
print("4. BE TESTABLE with galaxy surveys and CMB")

print("\n" + "="*80)
print("CHALLENGES:")
print("-"*80)
print("1. Must fit CMB power spectrum (hard for MOND-like)")
print("2. Must explain Bullet Cluster (apparent DM separation)")
print("3. Must not affect BBN or stellar evolution too much")

# Save dark matter theory
with open('dark_matter_fifth_force.txt', 'w') as f:
    f.write("DARK MATTER-EXPLAINING FIFTH FORCE THEORY\n")
    f.write("="*60 + "\n\n")
    f.write("Concept: Screened force that mimics dark matter on galactic scales\n\n")
    f.write("Required parameters:\n")
    f.write(f"  Mediator mass: m = {m_dm:.2e} eV\n")
    f.write(f"  Coupling: α = {alpha_dm:.2e}\n")
    f.write(f"  Force range: λ = {lambda_dm/kpc:.0f} kpc\n\n")
    f.write("Predictions:\n")
    f.write("1. No dark matter particles needed\n")
    f.write("2. Force screened at <1 kpc scales (solar system safe)\n")
    f.write("3. Specific galaxy rotation curve shapes\n")
    f.write("4. Testable with JWST and galaxy surveys\n\n")
    f.write("Challenges:\n")
    f.write("1. CMB fits (needs additional fields)\n")
    f.write("2. Cluster collisions (Bullet Cluster)\n")
    f.write("3. Fine-tuning of screening scale\n")

print(f"\n📁 Dark matter theory saved to 'dark_matter_fifth_force.txt'")
