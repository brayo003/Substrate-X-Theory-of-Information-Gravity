import numpy as np
import json

def solve_v12(e_s, f_s, t_s, e_c, f_c, t_c):
    # Matrix A: [[E_stable, -F_stable], [E_crisis, -F_crisis]]
    # Vector b: [T_stable, T_crisis]
    A = np.array([[e_s, -f_s], [e_c, -f_c]])
    b = np.array([t_s, t_c])
    return np.linalg.solve(A, b)

# Verified Historical Data Points
# Stable (2019): E=1.39, F=790k, T=0.85
# Crisis (2021): E=1.26, F=811k, T=4.30
beta, gamma = solve_v12(1.39, 790000, 0.85, 1.26, 811000, 4.30)

ratio = beta / gamma

print("--- SXC-V12 EMPIRICAL AUDIT (HISTORICAL GROUND TRUTH) ---")
print(f"BETA (Sensitivity): {beta:.8f}")
print(f"GAMMA (Damping):     {gamma:.8f}")
print(f"RATIO (β/γ):         {ratio:.2f}")

if ratio > 20:   state = "BRITTLE [SNAP]"
elif ratio > 4:  state = "STIFF [FRACTURE]"
else:            state = "ELASTIC [FLOW]"

print(f"SUBSTRATE STATE:     {state}")
print("-" * 50)

# Write to coefficients.json
with open('coefficients.json', 'w') as f:
    json.dump({
        "module": "logistics_empirical",
        "coefficients": {"beta": float(beta), "gamma": float(gamma)},
        "ratio": float(ratio),
        "state": state
    }, f, indent=4)
print("AUDIT COMPLETE: coefficients.json updated.")
