#!/usr/bin/env python3
"""
MINIMAL WORKING TEST - Testing the core physics without parameter conflicts
"""

import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class MinimalIntegratedSolver(CompleteFieldTheorySolver):
    """Minimal solver with reduced α and basic modifications"""
    
    def __init__(self, 
                 grid_size=64, domain_size=1.0,
                 alpha=1e-5,  # CRITICAL: Reduced for long-range
                 beta=0.8, gamma=0.3,
                 delta1=0.5, delta2=0.3, kappa=0.5,
                 tau_rho=0.2, tau_E=0.15, tau_F=0.25):
        
        super().__init__(grid_size, domain_size, alpha, beta, gamma,
                        delta1, delta2, kappa, tau_rho, tau_E, tau_F)
        
        print(f"🔧 MINIMAL SOLVER: α={alpha:.1e} (reduced)")
    
    def evolve_step(self):
        """Simple evolution with reduced α"""
        new_rho, new_E, new_F = super().evolve_step()
        
        # Just test if reduced α works
        return new_rho, new_E, new_F

def test_minimal_solver():
    print("🚀 TESTING MINIMAL SOLVER WITH REDUCED α")
    print("=" * 50)
    
    # Test just the core: reduced α
    test_cases = [
        {'alpha': 1e-5, 'delta1': 0.5, 'delta2': 0.3},
        {'alpha': 1e-5, 'delta1': 5.0, 'delta2': 3.0},  # 10x sources
        {'alpha': 1e-5, 'delta1': 25.0, 'delta2': 15.0},  # 50x sources
        {'alpha': 1e-6, 'delta1': 25.0, 'delta2': 15.0},  # Even smaller α
    ]
    
    base_params = {
        'grid_size': 64, 'domain_size': 1.0,
        'beta': 0.8, 'gamma': 0.3, 'kappa': 0.5,
        'tau_rho': 0.2, 'tau_E': 0.15, 'tau_F': 0.25
    }
    
    for i, case in enumerate(test_cases):
        print(f"\n🔬 Test {i+1}: α={case['alpha']:.1e}, δ₁={case['delta1']:.1f}")
        
        try:
            solver = MinimalIntegratedSolver(**{**base_params, **case})
            results, diagnostics = solver.evolve_system(steps=60, pattern='gaussian')
            
            if results:
                final = results[-1]
                final_diag = diagnostics[-1]
                
                # Quick analysis
                center_x, center_y = final['F'].shape[1] // 2, final['F'].shape[0] // 2
                y, x = np.ogrid[-center_y:final['F'].shape[0]-center_y, 
                               -center_x:final['F'].shape[1]-center_x]
                r = np.sqrt(x*x + y*y) * solver.dx
                
                solar_mask = (r >= 0.04) & (r <= 0.06)
                galactic_mask = (r >= 0.28) & (r <= 0.32)
                
                if np.any(solar_mask) and np.any(galactic_mask):
                    grad_F_x, grad_F_y = np.gradient(final['F'], solver.dx, solver.dx)
                    grad_F = np.sqrt(grad_F_x**2 + grad_F_y**2)
                    keff_solar = np.mean(grad_F[solar_mask]) * 1e-2
                    keff_galactic = np.mean(grad_F[galactic_mask]) * 1e-2
                    
                    F_solar = np.mean(np.abs(final['F'][solar_mask]))
                    F_galactic = np.mean(np.abs(final['F'][galactic_mask]))
                    propagation_ratio = F_galactic / F_solar if F_solar > 0 else 0
                    
                    print(f"✅ STABLE - F_RMS: {final_diag['F_rms']:.4f}")
                    print(f"   keff_solar: {keff_solar:.2e} ({keff_solar/1e-3*100:.1f}% of target)")
                    print(f"   keff_galactic: {keff_galactic:.4f} ({keff_galactic/0.1*100:.1f}% of target)")
                    print(f"   Propagation: {propagation_ratio:.3f}")
                    
                    # Check if we're making progress
                    if keff_galactic > 0.001:  # 1% of galactic target
                        print(f"🎉 PROGRESS! Galactic scale appearing!")
                    
                else:
                    print(f"✅ STABLE - Analysis failed")
            else:
                print(f"❌ No results")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

# Also test current performance for comparison
def test_current_performance():
    print(f"\n📊 CURRENT PERFORMANCE (α=0.01) for comparison")
    print("=" * 50)
    
    from complete_field_theory_solver_fixed import CompleteFieldTheorySolver
    
    solver = CompleteFieldTheorySolver(alpha=0.01, delta1=25.0, delta2=15.0)
    results, diagnostics = solver.evolve_system(steps=60, pattern='gaussian')
    
    if results:
        final = results[-1]
        final_diag = diagnostics[-1]
        
        center_x, center_y = final['F'].shape[1] // 2, final['F'].shape[0] // 2
        y, x = np.ogrid[-center_y:final['F'].shape[0]-center_y, 
                       -center_x:final['F'].shape[1]-center_x]
        r = np.sqrt(x*x + y*y) * solver.dx
        
        solar_mask = (r >= 0.04) & (r <= 0.06)
        galactic_mask = (r >= 0.28) & (r <= 0.32)
        
        if np.any(solar_mask) and np.any(galactic_mask):
            grad_F_x, grad_F_y = np.gradient(final['F'], solver.dx, solver.dx)
            grad_F = np.sqrt(grad_F_x**2 + grad_F_y**2)
            keff_solar = np.mean(grad_F[solar_mask]) * 1e-2
            keff_galactic = np.mean(grad_F[galactic_mask]) * 1e-2
            
            print(f"📈 WITH α=0.01:")
            print(f"   keff_solar: {keff_solar:.2e}")
            print(f"   keff_galactic: {keff_galactic:.4f}")
            print(f"   F_RMS: {final_diag['F_rms']:.4f}")

if __name__ == "__main__":
    # Test current performance for baseline
    test_current_performance()
    
    # Test reduced α
    test_minimal_solver()
    
    print(f"\n🎯 THEORETICAL TEST:")
    print(f"Testing if reduced α (1e-5) enables galactic-scale propagation")
    print(f"compared to current α=0.01 which kills long-range effects")
