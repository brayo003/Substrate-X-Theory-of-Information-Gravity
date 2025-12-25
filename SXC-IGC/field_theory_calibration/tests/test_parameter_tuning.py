#!/usr/bin/env python3
"""Tune parameters to match target k_eff values"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def tune_parameters():
    """Find parameters that give desired k_eff values"""
    print("🎯 PARAMETER TUNING FOR TARGET k_eff")
    print("=" * 60)
    
    # Target: solar system k_eff ≈ 2e-4, galactic k_eff ≈ 0.3
    # We found F field gives k_eff ≈ 1.7e-4 with gamma=1.0
    # So we need to scale gamma to get exactly 2e-4
    
    mass_solar = 2e30
    target_k_eff_solar = 2e-4
    
    # Test different gamma values
    gamma_values = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    
    print("Tuning gamma parameter:")
    for gamma in gamma_values:
        solver = SubstrateXSolver(
            grid_size=16,
            domain_size=2e11,
            alpha=1.0,
            beta=1.0, 
            gamma=gamma,
            chi=1.0,
            tau=1e3
        )
        
        solver.add_point_mass(mass_solar, (0,0))
        
        max_F = np.max(np.abs(solver.F))
        k_eff = max_F / (solver.gamma * mass_solar)
        
        print(f"  gamma={gamma:.1f} → k_eff={k_eff:.6f} (target: {target_k_eff_solar:.1e})")
        
        if abs(k_eff - target_k_eff_solar) / target_k_eff_solar < 0.1:  # Within 10%
            print(f"  🎉 Found good gamma: {gamma:.1f}")
            optimal_gamma = gamma
            break
    
    print(f"\n💡 RECOMMENDATION:")
    print(f"   Use gamma ≈ {optimal_gamma if 'optimal_gamma' in locals() else gamma_values[-1]:.1f}")
    print(f"   Calculate k_eff from F field: k_eff = max(F) / (gamma * mass)")

if __name__ == "__main__":
    tune_parameters()
