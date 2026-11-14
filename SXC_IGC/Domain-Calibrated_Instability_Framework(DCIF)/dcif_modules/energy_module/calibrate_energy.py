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

# Anchor 1: Nominal Grid (Low E, High F, T=0.03)
# Anchor 2: Near-Collapse / Brownout (High E, Low F, T=0.92)
alpha, beta, gamma = solve_dcii_coefficients_two_anchor(
    e_s=0.20, f_s=0.90, t_s=0.03,
    e_c=0.95, f_c=0.10, t_c=0.92
)

print("--- Energy DCII Calibration ---")
print(f"Alpha (Gradient): {alpha:.4f}")
print(f"Beta (Excitation): {beta:.4f}")
print(f"Gamma (Damping):   {gamma:.4f}")
