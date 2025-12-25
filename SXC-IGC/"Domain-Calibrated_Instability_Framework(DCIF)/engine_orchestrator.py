import os
import json
import numpy as np

class SXC_IGC_Engine:
    def __init__(self, module_path):
        with open(os.path.join(module_path, 'coefficients.json'), 'r') as f:
            data = json.load(f)
            # Support both flat and nested 'coefficients' keys
            coeffs = data.get('coefficients', data)
            self.alpha = coeffs['alpha']
            self.beta = coeffs['beta']
            self.gamma = coeffs['gamma']
        
        # Engine Parameters
        self.r = 0.153267  # Linear growth rate
        self.a = 1.0       # Quadratic feedback
        self.b = 1.0       # Cubic saturation
        self.dt = 0.05     # Time step
        self.sigma = 0.02  # Stochastic forcing

    def run_simulation(self, E, F, rho_grad=0, steps=1000):
        # 1. Calculate Initial Tension (DCII)
        x = (self.alpha * rho_grad) + (self.beta * E) - (self.gamma * F)
        history = [x]

        # 2. Iterative Drift (SXC-IGC)
        for _ in range(steps):
            drift = (self.r * x) + (self.a * x**2) - (self.b * x**3)
            noise = np.random.normal(0, self.sigma)
            x = x + self.dt * drift + noise
            history.append(x)
        
        return history

# Example Usage: Load Quantum and test stability
# engine = SXC_IGC_Engine('./quantum_module')
# results = engine.run_simulation(E=0.5, F=0.5)
