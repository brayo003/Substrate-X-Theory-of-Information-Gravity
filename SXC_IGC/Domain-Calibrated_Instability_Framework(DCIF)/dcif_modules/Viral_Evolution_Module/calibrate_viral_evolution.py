import numpy as np

def solve_dcii_coefficients_two_anchor(e_s, f_s, t_s, e_c, f_c, t_c):
    A = np.array([[e_s, -f_s], [e_c, -f_c]])
    b = np.array([t_s, t_c])
    try:
        x = np.linalg.solve(A, b)
        return 0.0, x[0], x[1]
    except np.linalg.LinAlgError:
        return 0.0, np.nan, np.nan

# Anchor 1: Endemic Stability (Low E, High F, T=0.05)
# Anchor 2: Antigenic Shift/Pandemic (High E, Low F, T=0.80)
alpha, beta, gamma = solve_dcii_coefficients_two_anchor(
    e_s=0.15, f_s=0.85, t_s=0.05,
    e_c=0.90, f_c=0.10, t_c=0.80
)

print("--- Viral Evolution DCII Calibration ---")
print(f"Alpha (Gradient): {alpha:.4f}")
print(f"Beta (Excitation): {beta:.4f}")
print(f"Gamma (Damping):   {gamma:.4f}")
