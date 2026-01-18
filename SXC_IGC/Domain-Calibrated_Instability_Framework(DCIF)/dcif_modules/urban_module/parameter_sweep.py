#!/usr/bin/env python3
"""
URBAN PARAMETER SWEEP TESTS
Find stable parameter ranges for urban pattern formation
"""
import numpy as np
import sys
import os
sys.path.append('../../..')
from core_engine.src.universal_stable_core import UniversalStableCore

def run_parameter_sweep():
    print("🎯 URBAN PARAMETER SWEEP TESTS")
    print("Finding stable parameter ranges for pattern formation")
    print("=" * 60)
    
    # Test different parameter regimes
    test_cases = [
        # (D_rho, D_E, D_F, delta1, delta2, description)
        (0.01, 0.05, 0.8, 2.5, 1.2, "Turing Pattern Regime"),
        (0.02, 0.1, 0.5, 1.8, 0.8, "Fast Development"),
        (0.03, 0.08, 0.6, 2.2, 1.5, "Balanced Growth"),
        (0.015, 0.06, 1.0, 3.0, 2.0, "High Constraint"),
        (0.04, 0.12, 0.4, 1.5, 1.0, "Low Regulation")
    ]
    
    results = []
    
    for D_rho, D_E, D_F, delta1, delta2, desc in test_cases:
        print(f"\n🔬 Testing: {desc}")
        print(f"  D_rho={D_rho}, D_E={D_E}, D_F={D_F}, δ₁={delta1}, δ₂={delta2}")
        
        engine = UniversalStableCore(grid_size=(32, 32))
        engine.set_urban_parameters()
        
        # Override with test parameters
        engine.D_rho, engine.D_E, engine.D_F = D_rho, D_E, D_F
        engine.delta1, engine.delta2 = delta1, delta2
        
        # Initialize urban pattern
        engine.initialize_domain("urban")
        
        # Run simulation
        stable_steps = 0
        pattern_formed = False
        
        for step in range(200):
            if engine.evolve_system_adaptive(1):
                stable_steps += 1
                
                # Check for pattern formation
                if step > 50:
                    density_variance = np.var(engine.rho)
                    if density_variance > 0.02:  # Pattern threshold
                        pattern_formed = True
                        break
            
            if engine.rejected_steps > 20:
                break
        
        # Record results
        result = {
            'parameters': (D_rho, D_E, D_F, delta1, delta2),
            'description': desc,
            'stable_steps': stable_steps,
            'pattern_formed': pattern_formed,
            'final_stress': engine.stress_history[-1] if engine.stress_history else 0,
            'final_variance': np.var(engine.rho)
        }
        results.append(result)
        
        status = "✅ STABLE + PATTERNS" if pattern_formed else "⚠️  STABLE" if stable_steps > 150 else "❌ UNSTABLE"
        print(f"  Result: {status} (Steps: {stable_steps}, Stress: {result['final_stress']:.3f})")
    
    # Summary
    print(f"\n📊 PARAMETER SWEEP SUMMARY:")
    print("=" * 50)
    successful = [r for r in results if r['pattern_formed']]
    stable = [r for r in results if r['stable_steps'] > 150]
    
    print(f"✅ Successful patterns: {len(successful)}/{len(results)}")
    print(f"⚠️  Stable but no patterns: {len(stable) - len(successful)}")
    print(f"❌ Unstable: {len(results) - len(stable)}")
    
    # Recommend best parameters
    if successful:
        best = max(successful, key=lambda x: x['final_variance'])
        print(f"\n🎯 RECOMMENDED PARAMETERS: {best['description']}")
        print(f"   D_rho={best['parameters'][0]}, D_E={best['parameters'][1]}, D_F={best['parameters'][2]}")
        print(f"   δ₁={best['parameters'][3]}, δ₂={best['parameters'][4]}")
    
    return results

if __name__ == "__main__":
    run_parameter_sweep()
