import numpy as np
import pandas as pd

# ===========================
# SCREENED FIFTH FORCE CHECK
# ===========================

# Theory parameters
m_S = 1.973e-4       # eV
alpha_S = 2.053e-31  # dimensionless
hbar_c = 1.97327e-7  # eV·m
M_Pl = 2.435e18 * 1e9  # eV

# Conversion helper
def yukawa_suppression(r_meters):
    """Compute Yukawa factor at distance r (meters)."""
    return np.exp(-m_S * r_meters / hbar_c)

def predicted_force(F_gravity, r_meters):
    """Predicted fifth-force relative to gravity."""
    F_X_over_FG = 2 * alpha_S * M_Pl
    return F_X_over_FG * F_gravity * yukawa_suppression(r_meters)

# ===========================
# Load existing experimental data
# Expected CSV columns: distance_m, measured_force_N, gravity_force_N, experiment_name
# Example row: 0.001,1.2e-11,6.67e-11,"Eot-Wash"
try:
    df = pd.read_csv("existing_force_data.csv")
except FileNotFoundError:
    print("Please provide 'existing_force_data.csv' with experimental data")
    exit()

# Compute predicted fifth-force
df['F_X_N'] = df.apply(lambda row: predicted_force(row['gravity_force_N'], row['distance_m']), axis=1)
df['residual'] = df['measured_force_N'] - df['gravity_force_N']

# Compare residuals to predicted F_X
df['matches_prediction'] = np.isclose(df['residual'], df['F_X_N'], rtol=0.5)  # 50% tolerance

# ===========================
# Summary
# ===========================
total = len(df)
matches = df['matches_prediction'].sum()
print("="*70)
print("SCREENED FIFTH FORCE VS EXISTING DATA")
print("="*70)
print(f"Total data points: {total}")
print(f"Points consistent with prediction: {matches}")
print(f"Percentage: {matches/total*100:.2f}%")
print("="*70)

# Save detailed output
df.to_csv("fifth_force_comparison_results.csv", index=False)
print("Detailed results saved to 'fifth_force_comparison_results.csv'")
