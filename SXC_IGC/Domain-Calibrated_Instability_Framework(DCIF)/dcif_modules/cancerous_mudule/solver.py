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
        return 0.0, x[0], x[1] # alpha, beta, gamma
    except np.linalg.LinAlgError:
        return 0.0, np.nan, np.nan
