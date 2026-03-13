import numpy as np

class SXCPhysicalEngine:
    def __init__(self, temp_k=773):
        # Physical Constants for 316 Stainless Steel
        k_b = 8.617e-5  # Boltzmann constant in eV/K
        E_v = 1.1       # Vacancy migration energy (eV)
        v_0 = 1e13      # Jump frequency (Hz)
        
        # Calculate Jump Frequency (The physical 'forgetting' rate)
        # Gamma is the probability of a defect annealing per time step
        self.gamma = v_0 * np.exp(-E_v / (k_b * temp_k)) * 1e-6 # Normalized to ms
        self.t_sys = 0.0

    def step(self, flux):
        self.t_sys = flux + (self.t_sys * (1 - self.gamma))
        return self.t_sys, self.gamma

# Scenario: High-Flux Pulsed Neutron Source (like a Spallation source)
# Each pulse is 0.05 DPA (Displacements Per Atom)
engine = SXCPhysicalEngine(temp_k=773)

print(f"{'Step':<10} | {'Gamma (Anneal)':<15} | {'T_sys (Debt)':<15} | {'State'}")
print("-" * 60)

for i in range(101):
    # Pulse every 20 steps
    flux = 0.05 if i % 20 == 0 else 0.0
    t_sys, gamma = engine.step(flux)
    
    if i % 10 == 0:
        state = "CRITICAL" if t_sys > 0.1 else "NOMINAL"
        print(f"{i:<10} | {gamma:<15.4e} | {t_sys:<15.4f} | {state}")

