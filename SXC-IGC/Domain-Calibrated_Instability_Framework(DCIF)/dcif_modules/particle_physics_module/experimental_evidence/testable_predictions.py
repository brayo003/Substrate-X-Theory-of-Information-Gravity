import numpy as np
import pandas as pd

# Theory parameters
m_S = 1.973e-4       # eV
alpha_S = 2.053e-31  # dimensionless
hbar_c = 1.97327e-7  # eV·m
M_Pl = 2.435e18 * 1e9  # eV

# Lab distances (m)
distances = np.array([0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01])  # 0.1 mm to 1 cm

# Experimental sensitivities (N)
sensitivity = 1e-15  # Approx Eöt-Wash limit

def yukawa_factor(r):
    return np.exp(-m_S * r / hbar_c)

def predicted_force(F_g, r):
    """Predicted fifth-force relative to gravity"""
    F_X_over_FG = 2 * alpha_S * M_Pl
    return F_X_over_FG * F_g * yukawa_factor(r)

# Assume 1g test masses
m1 = m2 = 0.001  # kg
G = 6.67430e-11
F_gravity = G * m1 * m2 / distances**2

results = []
for r, F_g in zip(distances, F_gravity):
    F_X = predicted_force(F_g, r)
    detectable = F_X > sensitivity
    results.append((r, F_g, F_X, detectable))

df = pd.DataFrame(results, columns=['distance_m', 'F_gravity_N', 'F_X_N', 'detectable'])
df.to_csv('lab_test_predictions.csv', index=False)

print("Predictions for lab-scale fifth force saved to 'lab_test_predictions.csv'")
print(df)
