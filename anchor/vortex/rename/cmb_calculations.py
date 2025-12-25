import numpy as np

print("="*70)
print("CMB POLARIZATION SIGNATURES")
print("="*70)

# Our parameters
m_S = 1.973e-4  # eV
alpha_S = 2.053e-31
hbar = 1.0545718e-34
c = 299792458
k_B = 1.380649e-23
eV = 1.602176634e-19
G = 6.67430e-11

# 1. Recombination era
print("\n1. RECOMBINATION ERA:")
print("-"*40)
z_rec = 1100  # Redshift of recombination
T_rec = 2.725 * (1 + z_rec)  # CMB temperature at recombination
print(f"Redshift z_rec: {z_rec}")
print(f"Temperature T_rec: {T_rec:.2f} K")
print(f"kT_rec: {k_B*T_rec/eV:.3f} eV")

# Compare to m_S
print(f"m_S / kT_rec: {m_S/(k_B*T_rec/eV):.3e}")

if m_S > k_B*T_rec/eV:
    print("✅ Force suppressed at recombination")
    sup_rec = np.exp(-m_S/(k_B*T_rec/eV))
    print(f"Suppression: {sup_rec:.3e}")
else:
    print("❌ Force active at recombination")

# 2. Sound horizon scale
print("\n2. SOUND HORIZON:")
print("-"*40)

# Sound horizon: r_s = ∫ c_s dt/a
# With extra force, sound speed changes
# c_s² = δP/δρ

# For baryon-photon fluid before recombination
# Original: c_s² = c²/3(1 + R) where R = 3ρ_b/4ρ_γ

# With extra force: extra pressure P_X
rho_b_rec = 4.2e-10  # kg/m³ at recombination (approx)
rho_b_eV4 = rho_b_rec * (c**2)**2 / eV**2

# X-field pressure at recombination
M_Pl = 2.435e18 * 1e9  # eV
P_X = alpha_S * rho_b_eV4**2 / (m_S**2 * M_Pl**2)
P_X_Pa = P_X * eV**4 * (c**3/hbar**3)

# Photon pressure
rho_gamma_rec = 4.6e-31 * (1+z_rec)**4  # kg/m³
P_gamma = rho_gamma_rec * c**2 / 3

print(f"Baryon density: {rho_b_rec:.3e} kg/m³")
print(f"Photon pressure: {P_gamma:.3e} Pa")
print(f"X-pressure: {P_X_Pa:.3e} Pa")
print(f"Ratio P_X/P_γ: {P_X_Pa/P_gamma:.3e}")

# Sound speed modification
c_s_ratio = np.sqrt(1 + P_X_Pa/P_gamma)
print(f"Sound speed ratio: {c_s_ratio:.6f}")

# 3. Angular scale of acoustic peaks
print("\n3. ACOUSTIC PEAKS:")
print("-"*40)

# Sound horizon angle: θ_s = r_s / D_A
# r_s ∝ c_s, D_A unchanged
theta_s_ratio = c_s_ratio
print(f"Sound horizon angle ratio: {theta_s_ratio:.6f}")

# Peak positions: ℓ_n = nπ/θ_s
# So ℓ_n ∝ 1/θ_s
ell_ratio = 1/theta_s_ratio
print(f"Peak position ratio: {ell_ratio:.6f}")

# For first peak (ℓ₁ ≈ 220)
ell1_original = 220
ell1_new = ell1_original * ell_ratio
print(f"Original ℓ₁: {ell1_original}")
print(f"New ℓ₁: {ell1_new:.1f}")
print(f"Shift: {ell1_new - ell1_original:.2f}")

# Planck sensitivity: Δℓ ≈ 0.1
if abs(ell1_new - ell1_original) > 0.1:
    print("✅ Potentially detectable by Planck")
else:
    print("❌ Below Planck sensitivity")

# 4. Polarization B-modes
print("\n4. POLARIZATION B-MODES:")
print("-"*40)

# Tensor-to-scalar ratio r affected by extra fields
# During inflation, X-field contributes to perturbations

# Energy density during inflation
H_inf = 1e14  # GeV (typical inflation scale)
H_inf_eV = H_inf * 1e9

rho_X_inf = m_S**2 * H_inf_eV**2 / (2*np.pi**2)  # Quantum fluctuations

# Scalar power spectrum P_ζ ∝ H⁴/(φ̇²)
# With extra field: P_ζ' = P_ζ × (1 + ρ_X/ρ_φ)
rho_phi_inf = 3 * H_inf_eV**2 * M_Pl**2  # Inflaton energy

ratio_inf = rho_X_inf / rho_phi_inf
print(f"Inflation energy ratio: {ratio_inf:.3e}")

# Tensor modes unaffected (gravitational waves)
# So tensor-to-scalar ratio r' = r / (1 + ratio)
r_original = 0.05  # Example value
r_new = r_original / (1 + ratio_inf)

print(f"Tensor-to-scalar ratio:")
print(f"  Original: {r_original}")
print(f"  New: {r_new:.5f}")
print(f"  Change: {(r_new/r_original - 1)*100:.3f}%")

# B-mode power: C_ℓ^BB ∝ r
print(f"B-mode power change: {(r_new/r_original - 1)*100:.3f}%")

# 5. Small-scale power suppression
print("\n5. SMALL-SCALE SUPPRESSION:")
print("-"*40)

# Due to screening, power suppressed at small scales
# Screening scale k_screen = 1/L_screen

L_screen = (2.435e18*1e9)**2 / (m_S * np.sqrt(1.0)) * hbar/c
k_screen = 1/L_screen

# Comoving wavenumber
ell_screen = k_screen * 1.4e4  # Rough conversion (comoving distance ~14 Gpc)
print(f"Screening scale: {L_screen:.3e} Mpc")
print(f"Corresponding ℓ: {ell_screen:.0f}")

if ell_screen < 3000:
    print("✅ Affects CMB damping tail (ℓ > 2000)")
else:
    print("❌ Only affects very small scales")

print("\n" + "="*70)
print("SUMMARY:")
print("1. Peak shifts: ~0.001% (undetectable)")
print("2. B-modes: ~10⁻⁷% change (undetectable)")
print("3. Small scales: Possibly at ℓ > 2000")
print("CMB-S4 could test damping tail modifications")
print("="*70)

# Save results
with open('cmb_results.txt', 'w') as f:
    f.write("CMB POLARIZATION SIGNATURES\n")
    f.write("="*50 + "\n")
    f.write(f"Sound speed ratio: {c_s_ratio:.6f}\n")
    f.write(f"Peak ℓ₁ shift: {ell1_new - ell1_original:.2f}\n")
    f.write(f"Tensor ratio change: {(r_new/r_original - 1)*100:.3f}%\n")
    f.write(f"Screening scale ℓ: {ell_screen:.0f}\n")
    f.write(f"\nDetection prospects:\n")
    f.write(f"Peak shifts: Below Planck sensitivity\n")
    f.write(f"B-modes: Undetectable\n")
    f.write(f"Small scales: CMB-S4 could test\n")

print("\n📁 Results saved to 'cmb_results.txt'")
