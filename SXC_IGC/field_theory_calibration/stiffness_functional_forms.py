#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class AdvancedStiffnessSolver(CompleteFieldTheorySolver):
    """Test different functional forms for variable stiffness"""
    
    def __init__(self, stiffness_type='quadratic', eta_param=0.0, **kwargs):
        super().__init__(**kwargs)
        self.stiffness_type = stiffness_type
        self.eta_param = eta_param
        print(f"🔧 {stiffness_type.upper()} STIFFNESS: α={self.alpha:.1e}, η={eta_param}")
    
    def compute_effective_stiffness(self, rho):
        """Different functional forms for α_eff(ρ)"""
        if self.stiffness_type == 'quadratic':
            return self.alpha * (1.0 + self.eta_param * rho**2)
        
        elif self.stiffness_type == 'exponential':
            return self.alpha * np.exp(self.eta_param * rho)
        
        elif self.stiffness_type == 'rational':
            return self.alpha * (1.0 + self.eta_param * rho) / (1.0 + 0.1 * self.eta_param * rho)
        
        elif self.stiffness_type == 'step':
            # Step function: high stiffness only in high density regions
            high_density_mask = rho > 0.1
            return self.alpha * (1.0 + self.eta_param * high_density_mask)
        
        else:
            return self.alpha
    
    def compute_field_evolution(self, rho, E, F):
        dF_dt = super().compute_field_evolution(rho, E, F)
        
        if self.eta_param != 0:
            alpha_eff = self.compute_effective_stiffness(rho)
            stiffness_term = alpha_eff * F
            original_stiffness = self.alpha * F
            dF_dt = dF_dt - original_stiffness + stiffness_term
        
        return dF_dt

def test_functional_forms():
    print("🧪 TESTING DIFFERENT STIFFNESS FUNCTIONAL FORMS")
    print("=" * 60)
    
    forms = ['quadratic', 'exponential', 'rational', 'step']
    optimal_eta = 100.0  # Start with reasonable value
    
    for form in forms:
        print(f"\n🔬 Testing {form} stiffness:")
        print("-" * 30)
        
        solver = AdvancedStiffnessSolver(
            alpha=1e-5, 
            delta1=25.0, 
            stiffness_type=form, 
            eta_param=optimal_eta
        )
        solver.initialize_system('gaussian')
        solver.evolve_system(30)  # REMOVED: verbose parameter
        print("   Evolution completed")
        
        analysis = solver.compute_diagnostics()
        g = analysis['keff_galactic']
        s = analysis['keff_solar']
        
        print(f"   Galactic: {g:.6f}")
        print(f"   Solar:    {s:.6f}")
        print(f"   Ratio:    {g/s:.1f}")
        print(f"   Galactic Progress: {g/0.0046:.1f}x of 22x needed")
        print(f"   Solar Progress: {s/0.00455:.1f}x of 0.22x needed")

test_functional_forms()
