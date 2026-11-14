import numpy as np

def run_stability_check():
    print("--- [VALIDATION] Verifying Fixed Point Attraction ---")
    r, a, b = 0.15, 1.0, 1.0
    # Analytic stable fixed point
    x_stable = (a + np.sqrt(a**2 + 4*b*r)) / (2*b)
    
    x = 0.5 # Start away from equilibrium
    dt = 0.05
    for i in range(1000):
        dx = (r*x + a*x**2 - b*x**3) * dt
        x += dx
    
    error = abs(x - x_stable)
    print(f"Target x_stable: {x_stable:.6f}")
    print(f"Engine x_final:  {x:.6f}")
    print(f"L-Infinity Error: {error:.2e}")

if __name__ == "__main__":
    run_stability_check()
