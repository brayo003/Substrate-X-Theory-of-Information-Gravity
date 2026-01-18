#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class ExponentialStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, eta_base=0.0, eta_power=10.0, rho_cutoff=0.5, **kwargs):
        super().__init__(**kwargs)
        self.eta_base = eta_base
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        print(f"🔧 EXPONENTIAL STIFFNESS: α={self.alpha:.1e}, η_base={eta_base}, η_power={eta_power}, ρ_cut={rho_cutoff}")
    
    def compute_effective_stiffness(self, rho):
        """Exponential step function: α_eff(ρ) = α × (1 + η_base × exp(η_power × (ρ - ρ_cutoff)))"""
        # Creates sharp stiffness increase above cutoff
        stiffness_factor = 1.0 + self.eta_base * np.exp(self.eta_power * (rho - self.rho_cutoff))
        return self.alpha * stiffness_factor
    
    def compute_field_evolution(self):
        rho, E, F = self.rho, self.E, self.F
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.eta_base != 0:
            # Apply exponential stiffness
            alpha_eff = self.compute_effective_stiffness(rho)
            
            # Remove original αF, add α_eff F (using addition based on debug results)
            stiffness_change = (alpha_eff - self.alpha) * F
            dF_dt = dF_dt + stiffness_change  # Using addition based on debug
            
            # Debug info
            center_idx = self.grid_size // 2
            center_stiffness = alpha_eff[center_idx, center_idx] / self.alpha
            edge_stiffness = alpha_eff[0, 0] / self.alpha
            print(f"DEBUG: Stiffness contrast - center: {center_stiffness:.0f}x, edge: {edge_stiffness:.1f}x")
        
        return dE_dt, dF_dt

def test_exponential_stiffness():
    print("🚀 EXPONENTIAL STIFFNESS TEST")
    print("Target: Create sharp stiffness contrast between center and edges")
    print("=" * 60)
    
    # Test parameters for surgical stiffness
    test_cases = [
        {"eta_base": 1e4, "eta_power": 10, "rho_cutoff": 0.5, "label": "Strong Surgical"},
        {"eta_base": 1e5, "eta_power": 15, "rho_cutoff": 0.3, "label": "Very Strong"},
        {"eta_base": 1e3, "eta_power": 8, "rho_cutoff": 0.7, "label": "Moderate"},
    ]
    
    for case in test_cases:
        print(f"\n🔬 Testing: {case['label']}")
        print(f"  η_base={case['eta_base']:.0e}, η_power={case['eta_power']}, ρ_cut={case['rho_cutoff']}")
        print("-" * 50)
        
        solver = ExponentialStiffnessSolver(
            alpha=1e-5, 
            delta1=25.0,
            eta_base=case['eta_base'],
            eta_power=case['eta_power'], 
            rho_cutoff=case['rho_cutoff']
        )
        solver.initialize_system('gaussian')
        
        # Run evolution with monitoring
        for step in range(10):
            solver.evolve_system(1)
            
            # Monitor field behavior
            F_center = solver.F[32, 32]
            F_edge = solver.F[0, 0] 
            F_rms = np.sqrt(np.mean(solver.F**2))
            
            print(f"Step {step}: Center={F_center:.6f}, Edge={F_edge:.6f}, RMS={F_rms:.6f}")
            
            # Check if we're getting the desired effect
            if step > 2:
                center_edge_ratio = abs(F_center / F_edge) if F_edge != 0 else 0
                print(f"  Center/Edge ratio: {center_edge_ratio:.3f}")

def analyze_stiffness_contrast():
    """Just analyze the stiffness function itself"""
    print("\n📊 STIFFNESS FUNCTION ANALYSIS")
    print("=" * 50)
    
    rho_values = np.linspace(0, 1, 11)
    
    test_params = [
        (1e4, 10, 0.5),
        (1e5, 15, 0.3), 
        (1e3, 8, 0.7)
    ]
    
    for eta_base, eta_power, rho_cut in test_params:
        print(f"\nη_base={eta_base:.0e}, η_power={eta_power}, ρ_cut={rho_cut}:")
        for rho in rho_values:
            stiffness = 1.0 + eta_base * np.exp(eta_power * (rho - rho_cut))
            print(f"  ρ={rho:.1f} → stiffness_factor={stiffness:.0f}")

# Run tests
test_exponential_stiffness()
analyze_stiffness_contrast()
