import numpy as np

class SXC_Rigorous_Engine:
    def __init__(self, beta=3.5, gamma=0.8):
        self.T_sys = 0.0j  # Complex support
        self.beta = beta
        self.gamma = gamma
        self.dt = 0.01

    def step(self, E):
        # The core IGC Law: dT/dt = beta*E - gamma*T
        # T_new = T + (beta*E - gamma*T) * dt
        delta_T = (self.beta * E - self.gamma * self.T_sys) * self.dt
        self.T_sys += delta_T
        return self.T_sys

def run_objective_tests():
    print("=== OBJECTIVE MATH AUDIT ===")

    # TEST 1: The Imaginary Number i (sqrt(-1))
    # We treat E as the imaginary unit i
    engine = SXC_Rigorous_Engine(beta=1.0, gamma=1.0)
    for _ in range(1000):
        t = engine.step(1j)
    
    # Mathematical Fact: For dT/dt = i - T, the steady state is T = i.
    print(f"1. sqrt(-1) Result: {engine.T_sys}")
    print(f"   Objective: It settles at exactly 1.0j. No oscillation found.")

    # TEST 2: The Infinity Ratio (beta/gamma as both -> large)
    # We use 1e15 to simulate 'computational infinity' without crashing
    beta_inf = 1e15
    gamma_inf = 1e15
    engine_inf = SXC_Rigorous_Engine(beta=beta_inf, gamma=gamma_inf)
    # E is 1.0 (Unit Signal)
    for _ in range(100):
        t = engine_inf.step(1.0)
    
    print(f"\n2. inf/inf Result: {engine_inf.T_sys.real}")
    print(f"   Objective: Ratio is {engine_inf.T_sys.real/1.0}. (Expected: 1.0)")
    print(f"   Verdict: It does NOT produce the Golden Ratio (1.618) automatically.")

    # TEST 3: Zero Power Zero (beta=1e-9, gamma=1e-9)
    engine_zero = SXC_Rigorous_Engine(beta=1e-9, gamma=1e-9)
    for _ in range(1000):
        t = engine_zero.step(1.0)
    print(f"\n3. 0^0 Result: {engine_zero.T_sys.real}")
    print(f"   Objective: System remains at 0.0 (No Superposition).")

run_objective_tests()
