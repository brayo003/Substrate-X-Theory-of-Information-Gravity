#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class ProperStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, eta_scale=0.0, **kwargs):
        super().__init__(**kwargs)
        self.eta_scale = eta_scale
        print(f"🔧 PROPER STIFFNESS: α={self.alpha:.1e}, η={eta_scale}")
    
    def compute_field_evolution(self):
        rho, E, F = self.rho, self.E, self.F
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.eta_scale != 0:
            # The issue: we need to understand what terms are in dF_dt
            # Let's examine what we're modifying
            print(f"DEBUG: dF_dt before mod - min: {np.min(dF_dt):.6f}, max: {np.max(dF_dt):.6f}, RMS: {np.sqrt(np.mean(dF_dt**2)):.6f}")
            
            # Apply variable stiffness - but we need to be careful about the sign
            # If the original equation is: dF_dt = ... - αF + ...
            # Then we want: dF_dt = ... - α_eff F + ...
            alpha_eff = self.alpha * (1.0 + self.eta_scale * rho**2)
            
            # Remove original αF term, add α_eff F term
            # Since we don't know the sign, let's try both directions
            stiffness_change = (alpha_eff - self.alpha) * F
            
            # Try subtracting (if original is +αF) or adding (if original is -αF)
            dF_dt_test1 = dF_dt - stiffness_change  # If original is +αF
            dF_dt_test2 = dF_dt + stiffness_change  # If original is -αF
            
            # Choose the one that makes physical sense (should reduce field in high density)
            # High density → high stiffness → faster decay → more negative dF_dt
            center_idx = self.grid_size // 2
            center_rho = rho[center_idx, center_idx]
            center_F = F[center_idx, center_idx]
            
            if center_rho > 0.5:  # At high density center
                effect1 = dF_dt_test1[center_idx, center_idx] 
                effect2 = dF_dt_test2[center_idx, center_idx]
                
                # We want stronger negative effect at center (faster decay)
                if abs(effect1) > abs(effect2) and effect1 * center_F < 0:
                    dF_dt = dF_dt_test1
                    print(f"DEBUG: Using subtraction (effect: {effect1:.6f})")
                else:
                    dF_dt = dF_dt_test2  
                    print(f"DEBUG: Using addition (effect: {effect2:.6f})")
            
            print(f"DEBUG: dF_dt after mod - min: {np.min(dF_dt):.6f}, max: {np.max(dF_dt):.6f}, RMS: {np.sqrt(np.mean(dF_dt**2)):.6f}")
        
        return dE_dt, dF_dt

def test_proper_stiffness():
    print("🔧 TESTING PROPER STIFFNESS FIX")
    print("=" * 50)
    
    # Test with significant η to see clear effects
    eta_values = [0.0, 1000.0]
    
    for eta in eta_values:
        print(f"\n🧪 Testing η = {eta}")
        solver = ProperStiffnessSolver(alpha=1e-5, delta1=25.0, eta_scale=eta)
        solver.initialize_system('gaussian')
        
        # Run just a few steps to see immediate effects
        for step in range(5):
            solver.evolve_system(1)  # Single step at a time
            F_center = solver.F[32, 32]  # Center value
            F_rms = np.sqrt(np.mean(solver.F**2))
            print(f"Step {step}: F_center={F_center:.6f}, F_RMS={F_rms:.6f}")

test_proper_stiffness()
