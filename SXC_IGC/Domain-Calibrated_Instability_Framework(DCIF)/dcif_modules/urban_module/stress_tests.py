#!/usr/bin/env python3
"""
URBAN STRESS & EDGE CASE TESTS
Test stability under extreme conditions
"""
import numpy as np
import sys
import os
sys.path.append('../../..')
from core_engine.src.universal_stable_core import UniversalStableCore

def run_stress_tests():
    print("🚨 URBAN STRESS & EDGE CASE TESTS")
    print("Testing stability under extreme conditions")
    print("=" * 60)
    
    stress_cases = [
        # (delta1, delta2, D_F, E_init, F_init, description)
        (5.0, 0.5, 0.1, 0.8, 0.1, "Over-Excitation Boom"),
        (1.0, 0.1, 0.1, 0.3, 0.1, "Under-Inhibition"),
        (3.0, 1.5, 0.01, 0.5, 0.5, "Diffusion Failure"),
        (4.0, 0.8, 2.0, 0.9, 0.2, "High Volatility"),
        (0.5, 2.0, 0.8, 0.2, 0.8, "Over-Regulation")
    ]
    
    results = []
    
    for delta1, delta2, D_F, E_init, F_init, desc in stress_cases:
        print(f"\n💥 Testing: {desc}")
        print(f"  δ₁={delta1}, δ₂={delta2}, D_F={D_F}, E_init={E_init}, F_init={F_init}")
        
        engine = UniversalStableCore(grid_size=(32, 32))
        engine.set_urban_parameters()
        
        # Apply stress parameters
        engine.delta1, engine.delta2 = delta1, delta2
        engine.D_F = D_F
        
        # Stressful initial conditions
        engine.initialize_domain("urban")
        engine.E = np.ones((32, 32)) * E_init
        engine.F = np.ones((32, 32)) * F_init
        
        emergency_brakes_activated = 0
        max_stress = 0
        
        for step in range(100):
            steps_done = engine.evolve_system_adaptive(1)
            
            if engine.stress_history:
                current_stress = engine.stress_history[-1]
                max_stress = max(max_stress, current_stress)
                
                if current_stress > 0.8:
                    emergency_brakes_activated += 1
            
            if not steps_done or engine.rejected_steps > 25:
                break
        
        result = {
            'scenario': desc,
            'max_stress': max_stress,
            'emergency_brakes': emergency_brakes_activated,
            'successful_steps': engine.step_count,
            'rejected_steps': engine.rejected_steps,
            'final_dt': engine.dt
        }
        results.append(result)
        
        if result['successful_steps'] > 80:
            status = "✅ SYSTEM STABLE"
        elif result['successful_steps'] > 50:
            status = "⚠️  PARTIAL STABILITY"
        else:
            status = "❌ SYSTEM FAILURE"
            
        print(f"  Result: {status}")
        print(f"    Max Stress: {max_stress:.3f}, Emergency Brakes: {emergency_brakes_activated}")
        print(f"    Successful Steps: {result['successful_steps']}/100, Final dt: {engine.dt:.6f}")
    
    # Summary
    print(f"\n📊 STRESS TEST SUMMARY:")
    print("=" * 50)
    stable_cases = [r for r in results if r['successful_steps'] > 80]
    partial_cases = [r for r in results if 50 <= r['successful_steps'] <= 80]
    failed_cases = [r for r in results if r['successful_steps'] < 50]
    
    print(f"✅ Stable: {len(stable_cases)}/{len(results)}")
    print(f"⚠️  Partial: {len(partial_cases)}/{len(results)}")  
    print(f"❌ Failed: {len(failed_cases)}/{len(results)}")
    
    # Show most dangerous scenarios
    if failed_cases:
        print(f"\n🚨 MOST DANGEROUS SCENARIOS:")
        for case in failed_cases[:2]:
            print(f"   💥 {case['scenario']} (Steps: {case['successful_steps']})")
    
    return results

if __name__ == "__main__":
    run_stress_tests()
