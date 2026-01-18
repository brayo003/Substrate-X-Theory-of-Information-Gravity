#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class CalibratedStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=0.0, eta_power=10.0, rho_cutoff=0.5, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        # Calculate maximum possible alpha_eff for diagnostics
        if M_factor > 0:
            self.alpha_eff_max = self.alpha * (1.0 + M_factor)
        else:
            self.alpha_eff_max = self.alpha
        
        print(f"🔧 TANH STIFFNESS: M={M_factor:.0f}, alpha_eff_max={self.alpha_eff_max:.2e}, ρ_cut={rho_cutoff}, power={eta_power}")
    
    def compute_effective_stiffness(self, rho):
        """Hyperbolic Tangent Limiter: α_eff(ρ) = α × (1 + M × tanh(η_power × (ρ - ρ_cutoff)))"""
        if self.M_factor == 0.0:
            return self.alpha * 1.0
            
        # Tanh ramps from ~ -1 to +1. We need it to ramp from 0 to 1 for the stiffness factor (1 + M*tanh) to work.
        # A simple approximation for a step function where tanh(x) is 0 for x < 0 and tanh(x) is 1 for x > large positive x:
        # We enforce the step by using rho - rho_cutoff.
        
        tanh_term = np.tanh(self.eta_power * (rho - self.rho_cutoff))
        
        # We shift and scale the tanh to approximate a ramp from 0 to 1 over the activation range.
        # This function starts near 0 for rho << rho_cutoff and saturates near 1 for rho >> rho_cutoff.
        # The factor is 0.5 * (1 + tanh(x)), where tanh(x) is from -1 to 1. 
        # Here we just use the raw tanh, which acts as a switch:
        # For rho < rho_cutoff, tanh is negative, making the stiffness factor < 1.0 (slight reduction).
        # For rho > rho_cutoff, tanh is positive, pushing the stiffness factor towards 1.0 + M.
        
        # Let's use the simplest, most direct form that uses M as the maximum factor:
        stiffness_factor = 1.0 + self.M_factor * np.maximum(0.0, tanh_term)
        
        return self.alpha * stiffness_factor
        
    def compute_field_evolution(self):
        rho, E, F = self.rho, self.E, self.F
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.M_factor != 0.0:
            alpha_eff = self.compute_effective_stiffness(rho)
            
            # The change in dF/dt due to variable stiffness:
            # dF/dt = ... - α*F + α_eff*F
            # This is equivalent to: dF/dt = ... + (α_eff - α)*F
            dF_dt = dF_dt + (alpha_eff - self.alpha) * F
            
        return dE_dt, dF_dt

# --- Test Execution Block ---
if __name__ == '__main__':
    from complete_field_theory_solver_fixed import run_calibrated_tests
    
    # Target scale ratio: Galactic/Solar ~ 100x
    print("🚀 TANH STIFFNESS CALIBRATION TEST")
    print("Target: Solar ~0.001, Galactic ~0.100")
    print("============================================================\n")
    
    # Test Matrix
    M_factors = [0, 500.0, 2000.0, 5000.0]
    
    for M in M_factors:
        solver = CalibratedStiffnessSolver(
            M_factor=M, 
            eta_power=10.0, 
            rho_cutoff=0.5, 
            steps=100
        )
        run_calibrated_tests(solver)
        print("-" * 60)
        
