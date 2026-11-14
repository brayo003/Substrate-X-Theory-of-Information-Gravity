#!/usr/bin/env python3
"""
REAL CALIBRATION: Tune parameters to get substrate response
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def find_working_parameters():
    """Find parameters that actually make the substrate field respond"""
    print("🎯 FINDING WORKING PARAMETERS")
    print("=" * 60)
    
    # Test progressively stronger parameters
    param_sets = [
        {'alpha': 1e-10, 'beta': 1e-10, 'gamma': 1e-10, 'name': 'VERY WEAK'},
        {'alpha': 1e-5, 'beta': 1e-5, 'gamma': 1e-5, 'name': 'WEAK'},
        {'alpha': 1e0, 'beta': 1e0, 'gamma': 1e0, 'name': 'MODERATE'},
        {'alpha': 1e5, 'beta': 1e5, 'gamma': 1e5, 'name': 'STRONG'},
        {'alpha': 1e10, 'beta': 1e10, 'gamma': 1e10, 'name': 'VERY STRONG'},
    ]
    
    mass = 2e30
    
    for params in param_sets:
        print(f"\n🔬 Testing {params['name']}: α,β,γ = {params['alpha']:.0e}")
        
        solver = SubstrateXSolver(
            grid_size=16,
            domain_size=2e11,
            alpha=params['alpha'],
            beta=params['beta'],
            gamma=params['gamma'],
            chi=1.0,
            tau=1e3
        )
        
        solver.add_point_mass(mass, (0,0))
        
        # Measure initial state
        s_initial = np.max(np.abs(solver.s))
        F_initial = np.max(np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2))
        
        # Evolve
        for i in range(50):
            solver.step()
        
        # Measure final state
        s_final = np.max(np.abs(solver.s))
        F_final = np.max(np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2))
        
        s_change = s_final - s_initial
        F_change = (F_final - F_initial) / F_initial * 100
        
        print(f"  s field: {s_initial:.2e} → {s_final:.2e} (change: {s_change:.2e})")
        print(f"  F field change: {F_change:.2f}%")
        
        # If we see meaningful substrate response
        if s_change > 1e-10:
            print(f"  🎉 SUBSTRATE ACTIVATED!")
            print(f"  Use these parameters: α,β,γ ≈ {params['alpha']:.0e}")
            return params
    
    print(f"\n❌ No parameter set activated the substrate field sufficiently")
    print(f"   Try even stronger parameters: α,β,γ > 1e10")

def calibrate_k_eff():
    """Once we have working parameters, calibrate k_eff"""
    print(f"\n🎯 CALIBRATING k_eff WITH WORKING PARAMETERS")
    print("=" * 60)
    
    # Use parameters that showed some effect
    working_params = {'alpha': 1e10, 'beta': 1e10, 'gamma': 1e10}
    
    test_scales = [
        {'mass': 2e30, 'domain': 2e11, 'target_k_eff': 2e-4, 'name': 'SOLAR'},
        {'mass': 1e41, 'domain': 3e20, 'target_k_eff': 0.3, 'name': 'GALACTIC'}
    ]
    
    for scale in test_scales:
        print(f"\n�� {scale['name']} SCALE:")
        
        solver = SubstrateXSolver(
            grid_size=32,
            domain_size=scale['domain'],
            **working_params
        )
        
        solver.add_point_mass(scale['mass'], (0,0))
        
        # Measure baseline Newtonian
        char_distance = scale['domain'] / 10
        distances = np.sqrt(solver.X**2 + solver.Y**2)
        char_idx = np.unravel_index(np.argmin(np.abs(distances - char_distance)), distances.shape)
        
        F_baseline = np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)[char_idx]
        g_newton = solver.G * scale['mass'] / (distances[char_idx] + solver.r_min)**2
        
        print(f"  Newtonian baseline: {g_newton:.6e} m/s²")
        print(f"  Initial F: {F_baseline:.6e} m/s²")
        
        # Evolve to let substrate modify gravity
        print("  Evolving substrate field...")
        for i in range(100):
            solver.step()
        
        F_final = np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)[char_idx]
        k_eff = (F_final - g_newton) / g_newton
        
        print(f"  Final F: {F_final:.6e} m/s²")
        print(f"  k_eff measured: {k_eff:.6f}")
        print(f"  k_eff target: {scale['target_k_eff']:.6f}")
        
        if abs(k_eff - scale['target_k_eff']) < 0.1 * scale['target_k_eff']:
            print(f"  ✅ GOOD MATCH!")
        else:
            print(f"  ⚠️  Needs parameter tuning")

if __name__ == "__main__":
    find_working_parameters()
    calibrate_k_eff()
    
    print(f"\n💡 CALIBRATION STRATEGY:")
    print("1. Find parameters that activate substrate field (s field changes)")
    print("2. Tune those parameters to get k_eff ≈ 2e-4 at solar scales") 
    print("3. Use SAME parameters at galactic scales - k_eff should naturally be ~0.3")
    print("4. If not, your theory needs scale-dependent parameters")
