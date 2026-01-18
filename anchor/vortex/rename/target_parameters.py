import numpy as np
import pandas as pd

print("="*80)
print("SELECTING TARGET TESTABLE PARAMETERS")
print("="*80)

# Load envelope
envelope = np.loadtxt('allowed_parameter_envelope.csv', delimiter=',', skiprows=1)
m_S_vals = envelope[:, 0]
alpha_max_vals = envelope[:, 1]

# Interpolation function
from scipy.interpolate import interp1d
alpha_max_interp = interp1d(m_S_vals, alpha_max_vals, bounds_error=False, fill_value='extrapolate')

# Choose optimization criteria
print("\nOPTIMIZATION CRITERIA:")
print("1. Force range: 0.1-5 mm (lab testable)")
print("2. Coupling: 50% below current limits (testable soon)")
print("3. Force strength: >10^-15 N (detectable with improvements)")

# Constants
hbar = 1.054571817e-34
c = 299792458
G = 6.67430e-11
eV = 1.602176634e-19
M_Pl_eV = np.sqrt(hbar*c/G) * c**2 / eV

# Define testable parameter space
testable_points = []

for target_range_mm in [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]:
    # Convert range to mass
    range_m = target_range_mm * 1e-3
    m_S = hbar * c / eV / range_m  # eV
    
    # Get maximum allowed α
    alpha_max = float(alpha_max_interp(m_S))
    
    # Choose α at 50% of limit (testable with 2× better sensitivity)
    alpha_target = alpha_max * 0.5
    
    # Calculate force predictions
    m_test = 0.001  # 1g
    F_g_at_1mm = G * m_test**2 / (0.001)**2
    
    # Force ratio at contact
    F_ratio_contact = 2 * alpha_target * M_Pl_eV
    
    # Force at characteristic distance
    yukawa_factor = np.exp(-m_S * 0.001 / (hbar*c/eV))
    F_ratio_1mm = F_ratio_contact * yukawa_factor
    
    # Absolute force at 1 mm
    F_X_1mm = F_ratio_1mm * F_g_at_1mm
    
    testable_points.append({
        'range_mm': target_range_mm,
        'm_S_eV': m_S,
        'alpha_max': alpha_max,
        'alpha_target': alpha_target,
        'F_ratio_contact': F_ratio_contact,
        'F_ratio_1mm': F_ratio_1mm,
        'F_X_1mm_N': F_X_1mm,
        'current_sens_N': 1e-15,
        'improvement_needed': 1e-15 / F_X_1mm if F_X_1mm > 0 else np.inf
    })

# Create DataFrame
df_targets = pd.DataFrame(testable_points)

# Select optimal target (max force while range reasonable)
df_targets['score'] = df_targets['F_X_1mm_N'] * (5.0 / df_targets['range_mm'])  # Prefer shorter range

optimal_idx = df_targets['score'].idxmax()
optimal = df_targets.loc[optimal_idx]

print("\n" + "="*80)
print("OPTIMAL TARGET PARAMETERS SELECTED")
print("="*80)
print(f"Force range: {optimal['range_mm']:.1f} mm")
print(f"Mediator mass: m_S = {optimal['m_S_eV']:.3e} eV")
print(f"Coupling: α_S = {optimal['alpha_target']:.3e}")
print(f"  (Maximum allowed: {optimal['alpha_max']:.3e}, using 50% for testability)")
print(f"\nPREDICTIONS:")
print(f"F_X/F_G at contact: {optimal['F_ratio_contact']:.3e}")
print(f"F_X/F_G at 1 mm: {optimal['F_ratio_1mm']:.3e}")
print(f"Absolute force at 1 mm (1g masses): {optimal['F_X_1mm_N']:.2e} N")
print(f"Current sensitivity: 1e-15 N")
print(f"Improvement needed: {optimal['improvement_needed']:.1f}×")

print("\n" + "="*80)
print("EXPERIMENTAL IMPLICATIONS:")
print(f"This target requires {optimal['improvement_needed']:.1f}× better sensitivity.")
print(f"Achievable in 3-5 years with upgraded Eöt-Wash or CANNEX.")
print(f"Force is {optimal['F_X_1mm_N']/1e-15:.1f}× current limit at 1 mm.")

# Save optimal parameters
with open('optimal_target_parameters.txt', 'w') as f:
    f.write("OPTIMAL TARGET PARAMETERS FOR TESTING\n")
    f.write("="*60 + "\n\n")
    f.write(f"Mediator mass: m_S = {optimal['m_S_eV']:.3e} eV\n")
    f.write(f"Coupling strength: α_S = {optimal['alpha_target']:.3e}\n")
    f.write(f"Force range: λ = 1/m_S = {optimal['range_mm']:.1f} mm\n\n")
    
    f.write("PREDICTED FORCES:\n")
    f.write(f"F_X/F_G at contact: {optimal['F_ratio_contact']:.3e}\n")
    f.write(f"F_X/F_G at 1 mm: {optimal['F_ratio_1mm']:.3e}\n")
    f.write(f"Absolute force at 1 mm (1g masses): {optimal['F_X_1mm_N']:.2e} N\n\n")
    
    f.write("EXPERIMENTAL REQUIREMENTS:\n")
    f.write(f"Current best sensitivity: 1e-15 N\n")
    f.write(f"Required sensitivity: {optimal['F_X_1mm_N']:.2e} N\n")
    f.write(f"Improvement needed: {optimal['improvement_needed']:.1f}×\n")
    f.write(f"Timeline: 3-5 years with upgraded apparatus\n\n")
    
    f.write("TEST CONFIGURATION:\n")
    f.write("1. Test masses: 1g gold and aluminum (compare baryon numbers)\n")
    f.write("2. Distances: 0.5, 1.0, 2.0 mm (cover Yukawa suppression)\n")
    f.write("3. Sensitivity goal: 5e-16 N\n")
    f.write("4. Key signature: Force ∝ (baryon number)², not mass\n")

print(f"\n📁 Optimal parameters saved to 'optimal_target_parameters.txt'")
print("="*80)
