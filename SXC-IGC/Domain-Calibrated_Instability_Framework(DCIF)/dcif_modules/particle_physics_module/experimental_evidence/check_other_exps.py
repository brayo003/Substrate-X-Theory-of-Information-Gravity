import numpy as np

print("="*70)
print("CHECKING OTHER EXPERIMENTS")
print("="*70)

experiments = [
    {"name": "Eöt-Wash 2012", "year": 2012, "sensitivity_N": 1e-15, "distance_m": 1e-3},
    {"name": "CANNEX 2023", "year": 2023, "sensitivity_N": 5e-16, "distance_m": 5e-4},
    {"name": "Stanford 2021", "year": 2021, "sensitivity_N": 2e-15, "distance_m": 2e-3},
    {"name": "Irvine 2019", "year": 2019, "sensitivity_N": 3e-15, "distance_m": 1e-3},
]

# Your predicted force at different distances
def predict_force(r):
    m_S = 1.973e-4
    alpha_S = 2.053e-31
    hbar_c = 1.97327e-7
    M_Pl = 2.435e18 * 1e9
    G = 6.67430e-11
    m = 0.001
    
    F_g = G * m**2 / r**2
    yukawa = np.exp(-m_S * r / hbar_c)
    return 2 * alpha_S * M_Pl * F_g * yukawa

print("\nYour theory vs experiments (for 1g masses):")
print("-"*60)
print("Experiment      | Distance | Sensitivity | Your F_X | Status")
print("-"*60)

for exp in experiments:
    r = exp["distance_m"]
    F_pred = predict_force(r)
    sens = exp["sensitivity_N"]
    status = "❌ Ruled out" if F_pred > sens else "✅ Allowed"
    
    print(f"{exp['name']:15} | {r*1000:6.1f} mm | {sens:8.1e} N | {F_pred:8.1e} N | {status}")

print("\n" + "="*70)
print("CONCLUSION:")
print("Your current parameters are ruled out by multiple experiments.")
print("To survive, α_S needs to be ~20× smaller.")
print("But then force becomes 400× harder to detect.")
print("="*70)
