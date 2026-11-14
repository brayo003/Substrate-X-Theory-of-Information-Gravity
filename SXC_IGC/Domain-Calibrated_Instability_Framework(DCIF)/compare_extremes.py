import numpy as np
import json
import os

def run_engine(module_name, E, F, rho_grad, steps=500):
    # Dynamic path resolution: looks in dcif_modules/ relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "dcif_modules", module_name, "coefficients.json")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Critical Module Missing: {path}")

    with open(path, 'r') as f:
        data = json.load(f)
    
    c = data.get('coefficients', data)
    alpha, beta, gamma = c['alpha'], c['beta'], c['gamma']
    
    # Engine constants (SXC-IGC Core)
    r, a, b, dt = 0.153267, 1.0, 1.0, 0.05
    sigma = 0.15 if "quantum" in module_name else 0.02
    
    x = (alpha * rho_grad) + (beta * E) - (gamma * F)
    history = [x]
    
    for _ in range(steps):
        drift = (r * x) + (a * x**2) - (b * x**3)
        noise = np.random.normal(0, sigma)
        x = x + (dt * drift) + noise
        if abs(x) > 10: x = np.sign(x) * 10 # Saturation Cap
        history.append(x)
    return history

# Run Simulations
try:
    bh_data = run_engine("black_hole_module", E=0.2, F=0.0, rho_grad=0.8)
    q_data = run_engine("quantum_module", E=0.4, F=0.6, rho_grad=0.0)

    print(f"--- SXC-IGC EXTREME DOMAIN LOG ---")
    print(f"BLACK HOLE: Final State x={bh_data[-1]:.4f} | Status: COLLAPSE")
    print(f"QUANTUM   : Mean Tension x={np.mean(q_data):.4f} | Status: STOCHASTIC")
except Exception as e:
    print(f"ERROR: {e}")
