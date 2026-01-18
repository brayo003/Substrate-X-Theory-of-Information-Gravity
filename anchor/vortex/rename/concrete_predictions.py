import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

print("="*80)
print("CONCRETE EXPERIMENTAL PREDICTIONS")
print("="*80)

# Load optimal parameters
optimal = {
    'm_S': 1.000e-3,  # Will be filled from previous step
    'alpha_S': 1.234e-33,  # Will be filled
    'range_mm': 0.2  # Will be filled
}

# Actually, let's use the envelope to pick good values
envelope = np.loadtxt('allowed_parameter_envelope.csv', delimiter=',', skiprows=1)

# Choose: m_S for ~1 mm range gives good testability
hbar = 1.054571817e-34
c = 299792458
eV = 1.602176634e-19

target_range_mm = 1.0
m_S_target = hbar * c / eV / (target_range_mm * 1e-3)

# Find max alpha for this m_S
from scipy.interpolate import interp1d
alpha_max_interp = interp1d(envelope[:, 0], envelope[:, 1], bounds_error=False, fill_value='extrapolate')
alpha_max = float(alpha_max_interp(m_S_target))
alpha_target = alpha_max * 0.5  # 50% below limit

optimal['m_S'] = m_S_target
optimal['alpha_S'] = alpha_target
optimal['range_mm'] = target_range_mm

print(f"Using parameters:")
print(f"  m_S = {optimal['m_S']:.3e} eV")
print(f"  α_S = {optimal['alpha_S']:.3e}")
print(f"  Range = {optimal['range_mm']:.1f} mm")

# Constants
G = 6.67430e-11
M_Pl_eV = np.sqrt(hbar*c/G) * c**2 / eV
hbar_c = hbar * c / eV  # eV·m

# Generate predictions
distances_mm = np.array([0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0])
distances_m = distances_mm * 1e-3

test_masses_kg = np.array([0.001, 0.005, 0.010, 0.050, 0.100])  # 1g to 100g

predictions = []

for m1 in test_masses_kg:
    for m2 in test_masses_kg:
        for r_mm, r_m in zip(distances_mm, distances_m):
            # Gravitational force
            F_g = G * m1 * m2 / r_m**2
            
            # Yukawa suppression
            yukawa = np.exp(-optimal['m_S'] * r_m / hbar_c)
            
            # Fifth force
            F_ratio = 2 * optimal['alpha_S'] * M_Pl_eV * yukawa
            F_X = F_ratio * F_g
            
            # Signal-to-noise (assuming 1e-15 N sensitivity)
            SN_ratio = F_X / 1e-15 if F_X > 0 else 0
            
            predictions.append({
                'mass1_g': m1 * 1000,
                'mass2_g': m2 * 1000,
                'distance_mm': r_mm,
                'F_gravity_N': F_g,
                'F_X_N': F_X,
                'F_X_over_FG': F_ratio,
                'yukawa_factor': yukawa,
                'SN_ratio': SN_ratio,
                'detectable': SN_ratio > 3  # 3σ detection
            })

# Create DataFrame
df_pred = pd.DataFrame(predictions)

# Save detailed predictions
df_pred.to_csv('detailed_predictions.csv', index=False)

# Create summary table for experimentalists
summary = df_pred[(df_pred['mass1_g'] == 1) & (df_pred['mass2_g'] == 1)].copy()
summary = summary[['distance_mm', 'F_gravity_N', 'F_X_N', 'F_X_over_FG', 'detectable']]
summary.columns = ['Distance (mm)', 'Gravity Force (N)', 'Predicted F_X (N)', 'F_X/F_G', 'Detectable (3σ)']

print(f"\n📁 Detailed predictions saved to 'detailed_predictions.csv'")
print(f"📊 {len(predictions):,} prediction points generated")

# Display key predictions
print("\n" + "="*80)
print("KEY PREDICTIONS FOR EXPERIMENTALISTS (1g masses)")
print("="*80)
print(summary.to_string(index=False))

# Generate experimental protocol
print("\n" + "="*80)
print("EXPERIMENTAL PROTOCOL")
print("="*80)

protocol = """
EXPERIMENT DESIGN FOR DETECTION:

1. APPARATUS REQUIREMENTS:
   - Torsion balance or micro-cantilever
   - Vacuum chamber (<10^-7 mbar)
   - Temperature control (±0.1 K)
   - Laser interferometer (1 nm positioning)
   - Test masses: Gold (Au) and Aluminum (Al)

2. MEASUREMENT SEQUENCE:
   Phase 1: Distance scan (0.5-2.0 mm)
     - Measure force between gold masses
     - Compare to Newtonian prediction
     - Look for Yukawa suppression pattern
   
   Phase 2: Material dependence
     - Compare Au-Au vs Al-Al
     - Expected ratio: (197/27)^2 ≈ 53.2
     - Signature of baryon coupling
   
   Phase 3: Control experiments
     - Same mass, different materials (Cu vs Al)
     - Temperature dependence (10-300 K)
     - Magnetic shielding

3. SENSITIVITY GOALS:
   - Distance: 0.1 mm to 10 mm
   - Force: 5e-16 N (5× better than current)
   - Integration time: 1 week per data point
   - Systematic errors: <10^-16 N

4. EXPECTED SIGNALS:
   - Non-1/r² dependence in 0.5-2.0 mm range
   - Material-dependent force strength
   - No effect from EM shielding (not EM force)

5. FALSIFICATION CRITERIA:
   If no deviation >3σ seen at:
     - 1.0 mm with 5e-16 N sensitivity
     - Material independence
   Then theory is ruled out at these parameters.
"""

print(protocol)

# Plot predictions
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Force vs distance for different masses
ax1 = axes[0, 0]
for mass in [1, 5, 10]:  # grams
    df_mass = df_pred[(df_pred['mass1_g'] == mass) & (df_pred['mass2_g'] == mass)]
    ax1.plot(df_mass['distance_mm'], df_mass['F_X_N'], 'o-', label=f'{mass}g masses')

ax1.axhline(y=1e-15, color='red', linestyle='--', label='Current sensitivity')
ax1.axhline(y=5e-16, color='orange', linestyle='--', label='Target sensitivity')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel('Distance (mm)', fontsize=12)
ax1.set_ylabel('Predicted F_X (N)', fontsize=12)
ax1.set_title('Force vs Distance for Different Masses', fontsize=14)
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot 2: F_X/F_G ratio
ax2 = axes[0, 1]
df_1g = df_pred[(df_pred['mass1_g'] == 1) & (df_pred['mass2_g'] == 1)]
ax2.plot(df_1g['distance_mm'], df_1g['F_X_over_FG'], 'b-', linewidth=2)
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel('Distance (mm)', fontsize=12)
ax2.set_ylabel('F_X / F_G', fontsize=12)
ax2.set_title('Fifth Force Relative to Gravity', fontsize=14)
ax2.grid(True, alpha=0.3)

# Plot 3: Material dependence
ax3 = axes[1, 0]
materials = {
    'Hydrogen (H)': 1,
    'Helium (He)': 4,
    'Carbon (C)': 12,
    'Aluminum (Al)': 27,
    'Gold (Au)': 197
}

material_names = list(materials.keys())
baryon_numbers = list(materials.values())
force_ratios = [(n/1)**2 for n in baryon_numbers]  # Relative to hydrogen

ax3.bar(material_names, force_ratios, color='skyblue')
ax3.set_yscale('log')
ax3.set_ylabel('Force relative to Hydrogen', fontsize=12)
ax3.set_title('Material Dependence (∝ baryon number²)', fontsize=14)
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3, axis='y')

# Plot 4: Detection prospects
ax4 = axes[1, 1]
detectable = df_pred[df_pred['detectable']]
not_detectable = df_pred[~df_pred['detectable']]

ax4.scatter(detectable['distance_mm'], detectable['mass1_g'], 
            c='green', s=50, alpha=0.6, label='Detectable (3σ)')
ax4.scatter(not_detectable['distance_mm'], not_detectable['mass1_g'],
            c='red', s=30, alpha=0.3, label='Not detectable')

ax4.set_xscale('log')
ax4.set_yscale('log')
ax4.set_xlabel('Distance (mm)', fontsize=12)
ax4.set_ylabel('Test mass (g)', fontsize=12)
ax4.set_title('Detection Prospects with Current Sensitivity', fontsize=14)
ax4.grid(True, alpha=0.3)
ax4.legend()

plt.tight_layout()
plt.savefig('experimental_predictions.png', dpi=150, bbox_inches='tight')

print(f"\n📊 Prediction plots saved to 'experimental_predictions.png'")

# Save experimental guidance
with open('experimental_guidance.md', 'w') as f:
    f.write("# Experimental Guidance for Fifth Force Search\n\n")
    f.write("## Target Parameters\n")
    f.write(f"- Mediator mass: m_S = {optimal['m_S']:.3e} eV\n")
    f.write(f"- Coupling: α_S = {optimal['alpha_S']:.3e}\n")
    f.write(f"- Force range: {optimal['range_mm']:.1f} mm\n\n")
    
    f.write("## Required Apparatus\n")
    f.write("1. Force sensitivity: 5e-16 N (5× better than current)\n")
    f.write("2. Distance control: 0.1-10 mm range, ±1 μm precision\n")
    f.write("3. Test masses: Various materials for baryon dependence test\n")
    f.write("4. Environment: Ultra-high vacuum, temperature stability\n\n")
    
    f.write("## Key Signatures\n")
    f.write("1. Yukawa suppression: Force drops faster than 1/r²\n")
    f.write("2. Material dependence: Force ∝ (baryon number)²\n")
    f.write("3. Distance scaling: Characteristic 1/m_S length scale\n\n")
    
    f.write("## Falsification Criteria\n")
    f.write("Theory ruled out if:\n")
    f.write("1. No deviation >3σ at 1 mm with 5e-16 N sensitivity\n")
    f.write("2. Force shows no material dependence\n")
    f.write("3. Force follows pure 1/r² at all distances\n")

print(f"\n📄 Experimental guidance saved to 'experimental_guidance.md'")
print("="*80)
