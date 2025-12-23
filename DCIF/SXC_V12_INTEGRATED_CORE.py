#!/usr/bin/env python3
import numpy as np

class SubstrateXCore:
    def __init__(self):
        self.A = 1e-16 
        self.alpha = 0.016
        self.threshold = 6.0e-17 

    def calculate_viscosity(self, rho_input):
        return self.A * (rho_input ** self.alpha)

    def check_stability(self, current_density, velocity_of_info):
        gamma = self.calculate_viscosity(current_density)
        momentum_tax = gamma * velocity_of_info
        stability_index = (momentum_tax / self.threshold)
        status = "STABLE" if stability_index < 1.0 else "CRITICAL: CASCADE RISK"
        return status, stability_index, gamma

if __name__ == "__main__":
    core = SubstrateXCore()
    print("="*80)
    print("SXC V12 INTEGRATED CORE: OPERATIONAL")
    print("="*80)
    
    # Testing the Saturation Point
    scenarios = [("LOW_FLUX", 1e-15, 1.0), ("CRITICAL_FLUX", 5e-12, 1.5)]
    for name, rho, v in scenarios:
        status, idx, g = core.check_stability(rho, v)
        print(f"{name:15} | Rho: {rho:.1e} | Gamma: {g:.2e} | {status} ({idx:.2f})")
