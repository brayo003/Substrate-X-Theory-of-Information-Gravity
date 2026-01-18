import numpy as np
from typing import Tuple

def solve_dcii_coefficients_two_anchor(
    e_stable: float, f_stable: float, t_stable: float,
    e_crisis: float, f_crisis: float, t_crisis: float
) -> Tuple[float, float, float]:
    A = np.array([[e_stable, -f_stable], [e_crisis, -f_crisis]])
    b = np.array([t_stable, t_crisis])
    try:
        x = np.linalg.solve(A, b)
        return 0.0, x[0], x[1]
    except np.linalg.LinAlgError:
        return 0.0, np.nan, np.nan

# Calibration Scenarios for Particle Physics
alpha, beta, gamma = solve_dcii_coefficients_two_anchor(
    e_stable=0.1, f_stable=0.9, t_stable=0.01,
    e_crisis=0.85, f_crisis=0.2, t_crisis=0.72
)

print("--- Particle Physics DCII Calibration ---")
print(f"Alpha (Gradient): {alpha:.4f}")
print(f"Beta (Excitation): {beta:.4f}")
print(f"Gamma (Damping):   {gamma:.4f}")
