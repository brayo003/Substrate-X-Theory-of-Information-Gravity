import numpy as np
from typing import Tuple

def solve_dcii_coefficients_two_anchor(e_s, f_s, t_s, e_c, f_c, t_c):
    A = np.array([[e_s, -f_s], [e_c, -f_c]])
    b = np.array([t_s, t_c])
    try:
        x = np.linalg.solve(A, b)
        return 0.0, x[0], x[1]
    except np.linalg.LinAlgError:
        return 0.0, np.nan, np.nan

# Anchor 1: Steady-State Urban Flow (Low E, High F, T=0.06)
# Anchor 2: Systemic Gridlock/Failure (High E, Low F, T=0.90)
alpha, beta, gamma = solve_dcii_coefficients_two_anchor(
    e_s=0.25, f_s=0.85, t_s=0.06,
    e_c=0.92, f_c=0.12, t_c=0.90
)

print("--- Urban DCII Calibration ---")
print(f"Alpha (Gradient): {alpha:.4f}")
print(f"Beta (Excitation): {beta:.4f}")
print(f"Gamma (Damping):   {gamma:.4f}")
