#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class WorkingStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, eta_scale=0.0, **kwargs):
        super().__init__(**kwargs)
        self.eta_scale = eta_scale
    
    def compute_field_evolution(self):
        # Get current fields
        rho, E, F = self.rho, self.E, self.F
        
        # Call parent method to get base evolution
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.eta_scale != 0:
            # Compute density-dependent stiffness
            alpha_eff = self.alpha * (1.0 + self.eta_scale * rho**2)
            
            # Replace constant stiffness with variable stiffness in F evolution
            original_stiffness = self.alpha * F
            variable_stiffness = alpha_eff * F
            dF_dt = dF_dt - original_stiffness + variable_stiffness
        
        return dE_dt, dF_dt

def test_working_stiffness():
    print("🔧 WORKING VARIABLE STIFFNESS TEST")
    print("=" * 50)
    
    # Test key eta values
    eta_values = [0.0, 100.0, 500.0, 1000.0, 5000.0]
    
    for eta in eta_values:
        print(f"\nTesting η = {eta}")
        solver = WorkingStiffnessSolver(alpha=1e-5, delta1=25.0, eta_scale=eta)
        solver.initialize_system('gaussian')
        
        try:
            solver.evolve_system(30)
            analysis = solver.compute_diagnostics()
            
            g = analysis['keff_galactic']
            s = analysis['keff_solar']
            ratio = g/s if s > 0 else 0
            
            print(f"  Galactic: {g:.6f}")
            print(f"  Solar:    {s:.6f}") 
            print(f"  Ratio:    {ratio:.1f}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

test_working_stiffness()
