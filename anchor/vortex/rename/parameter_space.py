import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

print("="*80)
print("EXPERIMENTAL PARAMETER SPACE ANALYSIS")
print("="*80)

# Constants
hbar = 1.054571817e-34      # J·s
c = 299792458               # m/s
G = 6.67430e-11             # m³/kg/s²
eV = 1.602176634e-19        # J
M_Pl = np.sqrt(hbar*c/G)    # kg
M_Pl_eV = M_Pl * c**2 / eV  # eV

# Experimental constraints (F_max in N at distance r for 1g masses)
experiments = [
    # Distance (m), Force limit (N), Experiment, Year
    (5.0e-5, 1.0e-12, "Eöt-Wash", 2012),
    (1.0e-4, 3.0e-13, "Eöt-Wash", 2012),
    (2.0e-4, 1.0e-13, "Eöt-Wash", 2012),
    (5.0e-4, 3.0e-14, "Eöt-Wash", 2012),
    (1.0e-3, 1.0e-14, "Eöt-Wash", 2012),
    (2.0e-3, 5.0e-15, "Eöt-Wash", 2012),
    (5.0e-3, 2.0e-15, "Eöt-Wash", 2012),
    (1.0e-2, 1.0e-15, "Eöt-Wash", 2012),
    (5.0e-4, 5.0e-16, "CANNEX", 2023),
    (1.0e-3, 2.0e-16, "CANNEX Projected", 2025),
    (2.0e-3, 1.0e-16, "CANNEX Projected", 2025),
]

# Convert to DataFrame
df_exp = pd.DataFrame(experiments, columns=['r_m', 'F_max_N', 'Experiment', 'Year'])

# Mass configuration (1g test masses)
m_test = 0.001  # kg

def calculate_constraints():
    """Calculate maximum allowed α_S for given m_S at each distance"""
    
    # Mass grid (eV)
    m_S_grid = np.logspace(-6, 1, 200)  # 1 μeV to 10 eV
    results = []
    
    for idx, row in df_exp.iterrows():
        r = row['r_m']
        F_max = row['F_max_N']
        
        # Gravitational force at this distance
        F_g = G * m_test**2 / r**2
        
        # Maximum allowed F_X/F_G ratio
        max_ratio = F_max / F_g
        
        # For each m_S, calculate maximum α_S that satisfies F_X/F_G ≤ max_ratio
        # F_X/F_G = 2α_S M_Pl_eV * exp(-m_S * r / (ħc/eV))
        hbar_c = hbar * c / eV  # eV·m
        
        for m_S in m_S_grid:
            yukawa = np.exp(-m_S * r / hbar_c)
            if yukawa > 1e-30:  # Avoid numerical issues
                alpha_max = max_ratio / (2 * M_Pl_eV * yukawa)
                results.append({
                    'r_m': r,
                    'r_mm': r*1000,
                    'm_S_eV': m_S,
                    'alpha_max': alpha_max,
                    'F_max_N': F_max,
                    'Experiment': row['Experiment'],
                    'Year': row['Year']
                })
    
    return pd.DataFrame(results)

# Calculate all constraints
print("\nCalculating experimental constraints...")
df_constraints = calculate_constraints()

# Find the envelope of constraints (most stringent at each m_S)
def find_envelope(df):
    """Find the upper envelope of allowed α_S for each m_S"""
    m_S_unique = np.unique(df['m_S_eV'])
    envelope = []
    
    for m_S in m_S_unique:
        df_m = df[df['m_S_eV'] == m_S]
        alpha_min = df_m['alpha_max'].min()
        envelope.append((m_S, alpha_min))
    
    return np.array(envelope)

envelope = find_envelope(df_constraints)

# Save envelope
np.savetxt('allowed_parameter_envelope.csv', envelope, 
           delimiter=',', header='m_S_eV,alpha_max', comments='')

print(f"\n✅ Calculated {len(df_constraints):,} constraint points")
print(f"✅ Envelope has {len(envelope)} points")
print(f"📁 Saved envelope to 'allowed_parameter_envelope.csv'")

# Plot constraints
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: All experimental limits
ax1 = axes[0, 0]
for exp in df_exp['Experiment'].unique():
    df_exp_sub = df_constraints[df_constraints['Experiment'] == exp]
    for r in df_exp_sub['r_mm'].unique():
        df_r = df_exp_sub[df_exp_sub['r_mm'] == r]
        ax1.plot(df_r['m_S_eV'], df_r['alpha_max'], 
                alpha=0.3, label=f'{exp} ({r:.1f} mm)' if r==0.1 else '')

ax1.plot(envelope[:, 0], envelope[:, 1], 'k-', linewidth=3, label='Allowed Envelope')
ax1.fill_between(envelope[:, 0], 0, envelope[:, 1], alpha=0.2, color='green', label='Allowed Region')

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel('Mediator mass m_S (eV)', fontsize=12)
ax1.set_ylabel('Maximum coupling α_S', fontsize=12)
ax1.set_title('Experimental Constraints on Parameter Space', fontsize=14)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right', fontsize=8)

# Plot 2: Force range vs m_S
ax2 = axes[0, 1]
range_mm = hbar * c / eV / (envelope[:, 0] * eV) * 1000  # mm
ax2.plot(envelope[:, 0], range_mm, 'b-', linewidth=2)
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel('m_S (eV)', fontsize=12)
ax2.set_ylabel('Force range 1/m_S (mm)', fontsize=12)
ax2.set_title('Force Range vs Mass', fontsize=14)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='1 mm')
ax2.axhline(y=0.1, color='orange', linestyle='--', alpha=0.5, label='0.1 mm')
ax2.legend()

# Plot 3: Your original parameters
ax3 = axes[1, 0]
your_m_S = 1.973e-4
your_alpha = 2.053e-31

# Find allowed alpha at your m_S
envelope_interp = interp1d(envelope[:, 0], envelope[:, 1], bounds_error=False, fill_value='extrapolate')
allowed_alpha = envelope_interp(your_m_S)

ax3.plot(envelope[:, 0], envelope[:, 1], 'k-', label='Allowed Envelope')
ax3.fill_between(envelope[:, 0], 0, envelope[:, 1], alpha=0.2, color='green', label='Allowed')
ax3.plot(your_m_S, your_alpha, 'ro', markersize=10, label='Your Parameters')
ax3.plot(your_m_S, allowed_alpha, 'go', markersize=10, label=f'Max allowed: {allowed_alpha:.2e}')

ax3.set_xscale('log')
ax3.set_yscale('log')
ax3.set_xlabel('m_S (eV)', fontsize=12)
ax3.set_ylabel('α_S', fontsize=12)
ax3.set_title('Your Parameters vs Constraints', fontsize=14)
ax3.grid(True, alpha=0.3)
ax3.legend()

# Plot 4: Target testable region
ax4 = axes[1, 1]
# Choose target: m_S for 1 mm range, α_S just below limit
target_m_S = 1e-3  # 1 meV gives ~0.2 mm range
target_alpha = envelope_interp(target_m_S) * 0.5  # 50% below limit

ax4.plot(envelope[:, 0], envelope[:, 1], 'k-', label='Limit')
ax4.plot(target_m_S, target_alpha, 's', markersize=12, color='purple', 
         label=f'Target: m_S={target_m_S:.2e} eV\nα={target_alpha:.2e}')

# Highlight testable region
testable_m_S = np.logspace(-4, -2, 100)  # 0.1 meV to 10 meV
testable_alpha = envelope_interp(testable_m_S) * 0.5
ax4.fill_between(testable_m_S, 0, testable_alpha, alpha=0.3, color='purple', label='Testable Region')

ax4.set_xscale('log')
ax4.set_yscale('log')
ax4.set_xlabel('m_S (eV)', fontsize=12)
ax4.set_ylabel('α_S', fontsize=12)
ax4.set_title('Target Testable Parameter Space', fontsize=14)
ax4.grid(True, alpha=0.3)
ax4.legend(loc='upper right')

plt.tight_layout()
plt.savefig('parameter_space_analysis.png', dpi=150, bbox_inches='tight')

print(f"\n📊 Plots saved to 'parameter_space_analysis.png'")

# Display summary
print("\n" + "="*80)
print("PARAMETER SPACE SUMMARY")
print("="*80)
print(f"For your m_S = {your_m_S:.3e} eV:")
print(f"  Your α_S = {your_alpha:.3e}")
print(f"  Maximum allowed α_S = {allowed_alpha:.3e}")
print(f"  Ratio (your/max) = {your_alpha/allowed_alpha:.2f}")
if your_alpha > allowed_alpha:
    print("  ❌ YOUR PARAMETERS ARE RULED OUT")
else:
    print("  ✅ Your parameters are allowed")

print(f"\nRecommended target for testability:")
print(f"  m_S = {target_m_S:.3e} eV (range ~{hbar*c/eV/target_m_S*1000:.1f} mm)")
print(f"  α_S = {target_alpha:.3e} (50% below current limit)")
print(f"  F_X/F_G at contact = {2*target_alpha*M_Pl_eV:.3e}")

print("\n" + "="*80)
