#!/usr/bin/env python3
"""Test calibration using time evolution to steady state"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def test_time_evolution_calibration():
    """Use time evolution to reach steady state"""
    print("🎯 CALIBRATION VIA TIME EVOLUTION")
    print("=" * 60)
    
    # Use VERY strong parameters to ensure we see an effect
    strong_params = {
        'alpha': 1.0,      # Much stronger - we need to see ANY signal
        'beta': 1.0,       # Strong nonlinearity
        'gamma': 1.0,      # Strong coupling
        'chi': 1.0,
        'tau': 1e3
    }
    
    print(f"Using STRONG parameters: α={strong_params['alpha']:.1e}, β={strong_params['beta']:.1e}, γ={strong_params['gamma']:.1e}")
    
    solver = SubstrateXSolver(
        grid_size=32,
        domain_size=2e11,
        **strong_params
    )
    
    print(f"\nScaled parameters:")
    print(f"  α: {solver.alpha:.2e}")
    print(f"  β: {solver.beta:.2e}") 
    print(f"  γ: {solver.gamma:.2e}")
    
    # Add mass
    mass_kg = 2e30
    solver.add_point_mass(mass_kg, (0, 0))
    
    print(f"\nInitial state after mass addition:")
    print(f"  E: [{np.min(solver.E):.2e}, {np.max(solver.E):.2e}]")
    print(f"  F: [{np.min(solver.F):.2e}, {np.max(solver.F):.2e}]")
    print(f"  s: [{np.min(solver.s):.2e}, {np.max(solver.s):.2e}]")
    
    # Evolve in time
    print(f"\nEvolving 500 time steps...")
    for step in range(500):
        solver.step()
        
        if step % 50 == 0:
            max_s = np.max(np.abs(solver.s))
            max_E = np.max(np.abs(solver.E)) 
            print(f"  Step {step}: max_s = {max_s:.2e}, max_E = {max_E:.2e}")
    
    # Calculate k_eff
    max_s = np.max(np.abs(solver.s))
    k_eff = max_s / (solver.gamma * mass_kg) if max_s > 0 else 0.0
    
    print(f"\n🎯 RESULT AFTER TIME EVOLUTION:")
    print(f"  Max s: {max_s:.2e}")
    print(f"  k_eff: {k_eff:.2e}")
    
    return k_eff

if __name__ == "__main__":
    test_time_evolution_calibration()
