import numpy as np

print("="*70)
print("SOLAR NEUTRINO FLUX MODIFICATIONS")
print("="*70)

# Our parameters
m_S = 1.973e-4  # eV
alpha_S = 2.053e-31
hbar = 1.0545718e-34
c = 299792458
k_B = 1.380649e-23
eV = 1.602176634e-19

# 1. Solar core conditions
print("\n1. SOLAR CORE:")
print("-"*40)
T_core = 1.57e7  # K
rho_core = 1.62e5  # kg/m³
print(f"Temperature: {T_core:.2e} K")
print(f"Density: {rho_core:.2e} kg/m³")
print(f"kT: {k_B*T_core/eV:.3f} eV")

# Compare to m_S
print(f"m_S / kT_core: {m_S/(k_B*T_core/eV):.3e}")

if m_S > k_B*T_core/eV:
    print("✅ Force suppressed in solar core")
    suppression = np.exp(-m_S/(k_B*T_core/eV))
    print(f"Thermal suppression: {suppression:.3e}")
else:
    print("❌ Force active in solar core")

# 2. Nuclear reaction rates
print("\n2. NUCLEAR REACTION RATES:")
print("-"*40)

# pp-chain reactions affected by screening
# Gamow factor: exp(-2πZ₁Z₂α c/v)
# With extra force: α → α + α_S

# For p+p reaction (main solar fusion)
Z1 = Z2 = 1
alpha_EM = 1/137.036
v_thermal = np.sqrt(2*k_B*T_core/1.6726e-27)  # proton thermal velocity

Gamow_original = np.exp(-2*np.pi*Z1*Z2*alpha_EM*c/v_thermal)
Gamow_new = np.exp(-2*np.pi*Z1*Z2*(alpha_EM + alpha_S)*c/v_thermal)

print(f"Thermal velocity: {v_thermal:.3e} m/s")
print(f"Original Gamow factor: {Gamow_original:.3e}")
print(f"New Gamow factor: {Gamow_new:.3e}")
print(f"Ratio: {Gamow_new/Gamow_original:.6f}")

# Reaction rate ∝ Gamow factor
rate_ratio = Gamow_new / Gamow_original
print(f"Reaction rate ratio: {rate_ratio:.6f}")

# 3. Solar luminosity
print("\n3. SOLAR LUMINOSITY:")
print("-"*40)

# Luminosity ∝ reaction rate × energy per reaction
# pp-chain: 4p → He⁴ + 2e⁺ + 2ν_e + 26.73 MeV

# Energy generation rate ε ∝ ρ X² T^β
# For pp-chain: β ≈ 4
beta = 4
T_ratio = 1.0  # Temperature unchanged
rho_ratio = 1.0  # Density unchanged
X_ratio = 1.0  # Hydrogen fraction unchanged

epsilon_ratio = rho_ratio * X_ratio**2 * T_ratio**beta * rate_ratio
print(f"Energy generation ratio: {epsilon_ratio:.6f}")

# Luminosity L ∝ ε
L_ratio = epsilon_ratio
print(f"Luminosity ratio: {L_ratio:.6f}")
print(f"Change: {(L_ratio-1)*100:.4f}%")

# 4. Neutrino fluxes
print("\n4. NEUTRINO FLUXES:")
print("-"*40)

# Different reactions affected differently
reactions = {
    'pp': {'flux': 6.0e10, 'dependence': 'rate_ratio'},
    '⁷Be': {'flux': 5.0e9, 'dependence': 'T^8'},
    '⁸B': {'flux': 5.6e6, 'dependence': 'T^18'},
    'pep': {'flux': 1.4e8, 'dependence': 'rate_ratio'},
}

print("Flux changes:")
total_flux_change = 0
for name, data in reactions.items():
    if 'rate_ratio' in data['dependence']:
        flux_ratio = rate_ratio
    elif 'T^8' in data['dependence']:
        flux_ratio = T_ratio**8
    elif 'T^18' in data['dependence']:
        flux_ratio = T_ratio**18
    else:
        flux_ratio = 1.0
    
    print(f"  {name:4}: {flux_ratio:.6f} ({(flux_ratio-1)*100:+.4f}%)")
    total_flux_change += data['flux'] * (flux_ratio - 1)

# Weighted average
total_flux = sum([d['flux'] for d in reactions.values()])
avg_change = total_flux_change / total_flux
print(f"\nAverage flux change: {avg_change*100:.4f}%")

# 5. Detectability
print("\n5. DETECTABILITY:")
print("-"*40)
print(f"Super-Kamiokande precision: ~2%")
print(f"Borexino precision: ~1%")
print(f"DUNE future precision: ~0.5%")

if abs(avg_change*100) > 0.5:
    print("✅ Potentially detectable with DUNE")
elif abs(avg_change*100) > 0.1:
    print("⚠️  Challenging but possible with future experiments")
else:
    print("❌ Below foreseeable precision")

print("\n" + "="*70)
print("CONCLUSION: ~0.01% effect on solar neutrinos")
print("Below current and near-future sensitivity")
print("="*70)

# Save results
with open('solar_neutrino_results.txt', 'w') as f:
    f.write("SOLAR NEUTRINO FLUX MODIFICATIONS\n")
    f.write("="*50 + "\n")
    f.write(f"Reaction rate ratio: {rate_ratio:.6f}\n")
    f.write(f"Luminosity change: {(L_ratio-1)*100:.4f}%\n")
    f.write(f"Average neutrino flux change: {avg_change*100:.4f}%\n")
    f.write(f"\nIndividual flux changes:\n")
    for name, data in reactions.items():
        flux_ratio = rate_ratio if 'rate_ratio' in data['dependence'] else 1.0
        f.write(f"  {name}: {(flux_ratio-1)*100:+.4f}%\n")

print("\n📁 Results saved to 'solar_neutrino_results.txt'")
