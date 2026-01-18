#!/usr/bin/env python3
"""
QUICK MAGNITUDE FIX - Testing source boost without parameter conflicts
"""

import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class SimpleBoostSolver(CompleteFieldTheorySolver):
    """Simple solver with source boosting"""
    
    def __init__(self, 
                 grid_size=64, domain_size=1.0,
                 alpha=0.01, beta=0.8, gamma=0.3,
                 delta1=0.5, delta2=0.3, kappa=0.5,
                 tau_rho=0.2, tau_E=0.15, tau_F=0.25,
                 source_boost=1.0):
        
        super().__init__(grid_size, domain_size, alpha, beta, gamma,
                        delta1, delta2, kappa, tau_rho, tau_E, tau_F)
        self.source_boost = source_boost
        print(f"🔧 SOURCE BOOST: {source_boost}x")
    
    def evolve_step(self):
        """Boosted evolution"""
        new_rho, new_E, new_F = super().evolve_step()
        
        # Apply source boost to F field
        lap_F = self.laplacian(self.F)
        
        # BOOSTED F field evolution
        dF_dt_boosted = (
            self.delta2 * self.E * self.source_boost -  # BOOSTED source
            lap_F -
            self.alpha * self.F -
            self.gamma * self.laplacian(lap_F) -
            self.F / self.tau_F
        )
        
        new_F_boosted = self.F + self.dt * dF_dt_boosted
        new_F_boosted = np.clip(new_F_boosted, -20.0, 20.0)
        
        return new_rho, new_E, new_F_boosted

def quick_magnitude_test():
    print("🚀 QUICK MAGNITUDE BOOST TEST")
    print("=" * 50)
    
    # Test simple source boosts
    boosts = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
    
    for boost in boosts:
        print(f"\n🔬 Testing {boost:.1f}x source boost...")
        
        try:
            solver = SimpleBoostSolver(
                source_boost=boost,
                delta1=0.5, delta2=0.3
            )
            
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
                    # Compute forces
                    grad_F_x, grad_F_y = np.gradient(final['F'], solver.dx, solver.dx)
                    grad_F = np.sqrt(grad_F_x**2 + grad_F_y**2)
                    keff_solar = np.mean(grad_F[solar_mask]) * 1e-2
                    keff_galactic = np.mean(grad_F[galactic_mask]) * 1e-2
                    
                    print(f"✅ STABLE - F_RMS: {final_diag['F_rms']:.3f}")
                    print(f"   keff_solar: {keff_solar:.2e} ({keff_solar/1e-3*100:.1f}% of target)")
                    print(f"   keff_galactic: {keff_galactic:.3f} ({keff_galactic/0.1*100:.1f}% of target)")
                else:
                    print(f"✅ STABLE - Analysis failed")
            else:
                print(f"❌ No results")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

# Also test the original scale separation to see current baseline
def test_current_baseline():
    print(f"\n📊 TESTING CURRENT BASELINE (no boost)")
    print("=" * 50)
    
    from complete_field_theory_solver_fixed import CompleteFieldTheorySolver
    
    solver = CompleteFieldTheorySolver(
        delta1=0.5, delta2=0.3  # Original parameters
    )
    
    results, diagnostics = solver.evolve_system(steps=80, pattern='gaussian')
    
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
            
            print(f"📈 BASELINE PERFORMANCE:")
            print(f"   F_RMS: {final_diag['F_rms']:.4f}")
            print(f"   keff_solar: {keff_solar:.2e} (need {1e-3/keff_solar:.1f}x boost)")
            print(f"   keff_galactic: {keff_galactic:.4f} (need {0.1/keff_galactic:.1f}x boost)")
            
            return keff_solar, keff_galactic
    
    return None, None

if __name__ == "__main__":
    # First check current baseline
    solar_base, galactic_base = test_current_baseline()
    
    if solar_base is not None:
        print(f"\n🎯 REQUIRED BOOST FACTORS:")
        print(f"   Solar scale: {1e-3/solar_base:.1f}x needed")
        print(f"   Galactic scale: {0.1/galactic_base:.1f}x needed")
    
    # Test magnitude boosts
    quick_magnitude_test()
