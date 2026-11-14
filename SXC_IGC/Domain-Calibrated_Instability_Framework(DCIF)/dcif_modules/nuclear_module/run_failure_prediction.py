import numpy as np

class SXCFailureEngine:
    def __init__(self, temp_k=473): # 200 degrees Celsius
        k_b = 8.617e-5
        E_v = 1.1       # Vacancy migration energy
        v_0 = 1e13
        # At 200C, gamma becomes infinitesimally small
        self.gamma = v_0 * np.exp(-E_v / (k_b * temp_k)) * 1e-6 
        self.t_sys = 0.0
        self.rho_0 = 1e10 # Base dislocation density

    def step(self, flux):
        self.t_sys = flux + (self.t_sys * (1 - self.gamma))
        # Mapping T_sys to Dislocation Density (Exponential buildup)
        current_rho = self.rho_0 * np.exp(self.t_sys * 12) 
        return self.t_sys, current_rho

engine = SXCFailureEngine(temp_k=473)
print(f"{'Step':<6} | {'T_sys':<10} | {'Rho (m^-2)':<15} | {'Status'}")
print("-" * 55)

for i in range(201):
    flux = 0.05 if i % 10 == 0 else 0.0
    t_sys, rho = engine.step(flux)
    
    if i % 20 == 0:
        state = "!!! SHATTER !!!" if rho > 1e15 else "STABLE"
        print(f"{i:<6} | {t_sys:<10.4f} | {rho:<15.2e} | {state}")
