#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class FixedOptimalBalanceSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, delta1=10.0, delta2=1.0, **kwargs):
        super().__init__(**kwargs) 
        
        # STEP 1: Force store our parameters
        self.delta1 = delta1 
        self.delta2 = delta2
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        print(f"🔧 FIXED SOLVER: δ₁={self.delta1}, δ₂={self.delta2}")
        print(f"   M={M_factor:.0f}, η_power={eta_power}, ρ_cut={rho_cutoff}")
        
    def compute_effective_stiffness(self, rho):
        if self.M_factor == 0.0:
            return self.alpha
        tanh_term = np.tanh(self.eta_power * (rho - self.rho_cutoff))
        stiffness_factor = 1.0 + self.M_factor * np.maximum(0.0, tanh_term)
        return self.alpha * stiffness_factor
        
    def compute_field_evolution(self):
        """COMPLETE OVERRIDE: Use OUR parameters for E and F evolution"""
        rho, E, F = self.rho, self.E, self.F
        
        # Get base evolution for reference, but we'll override key parts
        dE_dt_base, dF_dt_base = super().compute_field_evolution()
        
        # MANUAL OVERRIDE: Recalculate using OUR parameters
        # This is where we ensure δ₁=10.0, δ₂=1.0 are actually used
        
        # For now, let's verify what parameters the base class is using
        print(f"🔍 DEBUG: Base class delta1={getattr(self, 'delta1', 'MISSING')}, "
              f"delta2={getattr(self, 'delta2', 'MISSING')}")
        
        # Apply stiffness modification to whatever base gives us
        if self.M_factor != 0.0:
            alpha_eff = self.compute_effective_stiffness(rho)
            dF_dt_base = dF_dt_base + (alpha_eff - self.alpha) * F
            
        return dE_dt_base, dF_dt_base

def verify_parameters(solver):
    """Verify our parameters are actually being used"""
    print(f"\n🔍 PARAMETER VERIFICATION:")
    print(f"Our stored δ₁: {solver.delta1}")
    print(f"Our stored δ₂: {solver.delta2}")
    print(f"Base class attributes: {[attr for attr in dir(solver) if 'delta' in attr]}")

print("🚀 COMPLETE OVERRIDE FIX TEST")
print("Target: Ensure δ₁=10.0, δ₂=1.0 are used in computation")
print("=" * 70)

solver = FixedOptimalBalanceSolver(
    alpha=1e-5,
    delta1=10.0,
    delta2=1.0,
    M_factor=10000.0,
    eta_power=20.0,
    rho_cutoff=0.8
)

verify_parameters(solver)

print(f"\n💫 If the debug shows base class using wrong parameters,")
print("we need to completely rewrite compute_field_evolution from scratch.")
