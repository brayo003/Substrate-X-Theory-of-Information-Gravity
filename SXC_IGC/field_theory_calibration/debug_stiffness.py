#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class DebugStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, eta_scale=0.0, **kwargs):
        super().__init__(**kwargs)
        self.eta_scale = eta_scale
        self.modification_count = 0
    
    def compute_field_evolution(self):
        rho, E, F = self.rho, self.E, self.F
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.eta_scale != 0:
            self.modification_count += 1
            # Test if modification is actually applied
            alpha_eff = self.alpha * (1.0 + self.eta_scale * rho**2)
            modification = (alpha_eff - self.alpha) * F
            print(f"DEBUG: Modification magnitude: {np.max(np.abs(modification)):.6f}")
            dF_dt = dF_dt + modification
        
        return dE_dt, dF_dt

def test_debug():
    print("🐛 DEBUGGING STIFFNESS MODIFICATION")
    print("=" * 50)
    
    solver = DebugStiffnessSolver(alpha=1e-5, delta1=25.0, eta_scale=1000.0)
    solver.initialize_system('gaussian')
    
    print("Before evolution - testing one step:")
    dE_dt, dF_dt = solver.compute_field_evolution()
    print(f"dF_dt range: [{np.min(dF_dt):.6f}, {np.max(dF_dt):.6f}]")
    
    print(f"\nModification was called {solver.modification_count} times")

test_debug()
