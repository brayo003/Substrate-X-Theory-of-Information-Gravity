import numpy as np
from typing import Tuple

def solve_dcii_coefficients_two_anchor(
    e_stable: float, f_stable: float, t_stable: float,
    e_crisis: float, f_crisis: float, t_crisis: float
) -> Tuple[float, float, float]:
    """
    Generalized Solver for DCII coefficients beta (β) and gamma (γ) using 
    two defined anchor points.
    
    T = β*E - γ*F. Assumes alpha is 0.0.
    
    A = [[E_stable, -F_stable], [E_crisis, -F_crisis]]
    b = [T_stable, T_crisis]
    x = [beta, gamma]
    
    Returns: (alpha, beta, gamma)
    """
    
    # --- 1. Construct the System Matrix (A) and Target Vector (b) ---
    A = np.array([
        [e_stable, -f_stable],
        [e_crisis, -f_crisis]
    ])
    b = np.array([t_stable, t_crisis])
    
    # --- 2. Solve the System ---
    try:
        x = np.linalg.solve(A, b)
        
        beta = x[0]
        gamma = x[1]
        alpha = 0.0
        
        return alpha, beta, gamma
        
    except np.linalg.LinAlgError:
        # Matrix is singular (e.g., input scenarios are not linearly independent)
        return 0.0, np.nan, np.nan

if __name__ == "__main__":
    # --- Logistics Calibration Test ---
    # Stable: 5,000 containers (E), 4,500 throughput (F), 0.1 Tension
    # Crisis: 50,000 containers (E), 200 throughput (F), 0.95 Tension
    a, b, g = solve_dcii_coefficients_two_anchor(5e3, 4.5e3, 0.1, 5e4, 2e2, 0.95)
    
    print(f"Logistics Beta (Sensitivity): {b:.8f}")
    print(f"Logistics Gamma (Damping): {g:.8f}")
    
    # Check for Brittle signature (Beta > 1.0)
    state = "BRITTLE" if b > 1.0 else "RESILIENT"
    print(f"Substrate State: {state}")
