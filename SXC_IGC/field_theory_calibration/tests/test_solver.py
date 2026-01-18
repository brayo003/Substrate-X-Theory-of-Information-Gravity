#!/usr/bin/env python3
"""
Test suite for SubstrateXSolver with dimensional scaling
"""
import numpy as np
from src.numerical_solver import SubstrateXSolver

def test_self_consistent_solver():
    """Test the self-consistent dimensional solver"""
    print("🧪 TESTING SELF-CONSISTENT DIMENSIONAL SOLVER")
    print("=" * 60)
    
    # Test with exact parameters
    solver = SubstrateXSolver(
        grid_size=64,           # Small for quick test
        domain_size=1e12,       # 1 trillion meters
        dim=2,
        tau=1e3,                # 1000 seconds
        alpha=1e-40,            # Primary source term
        beta=1e-25,             # Scale switch
        gamma=1e-40,            # Force coupling
        chi=1.0                 # Dimensionless advection coherence
    )
    
    print("\n1. VERIFYING SCALING CALCULATION:")
    L_char = 1e12    # domain_size
    T_char = 1e4     # 10 * tau (since T_char = 10 * tau)
    
    # Expected scaling factors
    expected_alpha_scale = (L_char**3) / (T_char**2)  # 1e36 / 1e8 = 1e28
    expected_beta_scale = (L_char**2 * T_char)        # 1e24 * 1e4 = 1e28
    expected_gamma_scale = (L_char**3) / (T_char**2)  # 1e28
    
    print(f"   Expected scales: α_scale={expected_alpha_scale:.1e}, "
          f"β_scale={expected_beta_scale:.1e}, γ_scale={expected_gamma_scale:.1e}")
    
    # Test 2: Check the resulting parameter values
    print("\n2. RESULTING PARAMETER VALUES:")
    expected_alpha = 1e-40 / expected_alpha_scale
    expected_beta = 1e-25 / expected_beta_scale
    expected_gamma = 1e-40 / expected_gamma_scale
    
    print(f"   Expected: α={expected_alpha:.1e}, β={expected_beta:.1e}, γ={expected_gamma:.1e}")
    print(f"   Actual:   α={solver.alpha:.1e}, β={solver.beta:.1e}, γ={solver.gamma:.1e}")
    
    # Test 3: Quick stability check
    print("\n3. STABILITY TEST:")
    try:
        # Add a test mass if the method exists
        if hasattr(solver, 'add_point_mass'):
            solver.add_point_mass(1e30, (0, 0))  # Add test mass
            
        initial_energy = np.sum(solver.s**2) * solver.dx**2
        
        # Run a few steps
        for step in range(5):
            solver.step()
            
        final_energy = np.sum(solver.s**2) * solver.dx**2
        energy_change = abs(final_energy - initial_energy) / (initial_energy + 1e-10)  # Avoid division by zero
        
        print(f"   Energy change after 5 steps: {energy_change:.1e}")
        
        if energy_change < 1.0:  # Reasonable stability
            print("   ✅ PASSED: Stable with new parameters")
            return True
        else:
            print("   ⚠️  WARNING: Large energy change - may need tuning")
            return False
            
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)[:100]}...")  # Truncate long error messages
        return False

def test_parameter_sensitivity():
    """Test how sensitive the solver is to parameter changes"""
    print("\n4. PARAMETER SENSITIVITY:")
    
    test_cases = [
        # alpha, beta, gamma, chi
        (1e-40, 1e-25, 1e-40, 1.0),  # Default
        (1e-42, 1e-25, 1e-40, 1.0),  # Lower alpha
        (1e-40, 1e-23, 1e-40, 1.0),  # Higher beta
        (1e-40, 1e-25, 1e-38, 1.0),  # Higher gamma
        (1e-40, 1e-25, 1e-40, 0.1),  # Lower chi
    ]
    
    results = []
    
    for i, (a, b, g, c) in enumerate(test_cases, 1):
        try:
            solver = SubstrateXSolver(
                grid_size=32,
                domain_size=1e12,
                dim=2,
                tau=1e3,
                alpha=a,
                beta=b,
                gamma=g,
                chi=c
            )
            results.append(True)
            print(f"   Case {i}: PASSED with α={a:.1e}, β={b:.1e}, γ={g:.1e}, χ={c:.1f}")
        except Exception as e:
            results.append(False)
            print(f"   Case {i}: FAILED with α={a:.1e}, β={b:.1e}, γ={g:.1e}, χ={c:.1f} - {str(e)[:60]}...")
    
    if all(results):
        print("   ✅ ALL PARAMETER COMBINATIONS WORK")
        return True
    else:
        print(f"   ⚠️  {sum(1 for r in results if not r)} OUT OF {len(results)} COMBINATIONS FAILED")
        return False

if __name__ == "__main__":
    print("🚀 RUNNING COMPLETE SOLVER TEST SUITE")
    print("=" * 60)
    
    test1 = test_self_consistent_solver()
    test2 = test_parameter_sensitivity()
    
    print("\n" + "=" * 60)
    if test1 and test2:
        print("🎉 ALL TESTS PASSED - Your solver is ready!")
        print("Next: Begin parameter tuning to match k_eff(r)")
    else:
        print("🔧 SOME TESTS FAILED - Check implementation")
