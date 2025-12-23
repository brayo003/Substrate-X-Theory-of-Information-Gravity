import numpy as np
from typing import Tuple

def solve_dcii_coefficients_two_anchor(
    e_stable: float, f_stable: float, t_stable: float,
    e_crisis: float, f_crisis: float, t_crisis: float
) -> Tuple[float, float, float]:
    """
    Fixed parameter naming to match DCII Documentation.
    T = beta*E - gamma*F
    """
    A = np.array([[e_stable, -f_stable], [e_crisis, -f_crisis]])
    b = np.array([t_stable, t_crisis])
    try:
        x = np.linalg.solve(A, b)
        return 0.0, x[0], x[1]
    except np.linalg.LinAlgError:
        return 0.0, np.nan, np.nan

# Calibration: Dark Matter
# Stable: Galactic Core | Crisis: Bullet Cluster Separation
alpha, beta, gamma = solve_dcii_coefficients_two_anchor(
    e_stable=0.3, f_stable=0.01, t_stable=0.05,
    e_crisis=0.95, f_crisis=0.001, t_crisis=0.85
)

print("--- Dark Matter DCII Calibration ---")
print(f"Alpha (Gradient): {alpha:.4f}")
print(f"Beta (Excitation): {beta:.4f}")
print(f"Gamma (Damping):   {gamma:.4f}")
