#!/usr/bin/env python3
"""
URBAN STOCHASTIC CONSISTENCY TESTS
Validate reproducibility and noise sensitivity
"""
import numpy as np
import sys
import os
sys.path.append('../../..')
from core_engine.src.universal_stable_core import UniversalStableCore

def run_with_seed(seed, add_noise=False):
    """Run simulation with specific random seed"""
    np.random.seed(seed)
    
    engine = UniversalStableCore(grid_size=(32, 32))
    engine.set_urban_parameters()
    engine.initialize_domain("urban")
    
    # Add noise if requested
    if add_noise:
        noise = np.random.normal(0, 0.05, (32, 32))
        engine.rho = np.clip(engine.rho + noise, 0, 1)
    
    # Track metrics over time
    metrics = {
        'density_mean': [],
        'density_variance': [],
        'stress': []
    }
    
    for step in range(100):
        if engine.evolve_system_adaptive(1):
            metrics['density_mean'].append(np.mean(engine.rho))
            metrics['density_variance'].append(np.var(engine.rho))
            metrics['stress'].append(engine.stress_history[-1] if engine.stress_history else 0)
        
        if engine.rejected_steps > 10:
            break
    
    return metrics, engine.step_count

def run_stochastic_tests():
    print("🎲 URBAN STOCHASTIC CONSISTENCY TESTS")
    print("Testing reproducibility and noise sensitivity")
    print("=" * 60)
    
    print("\n🔍 TEST 1: Deterministic Reproducibility")
    print("Running same simulation 3 times with same seed...")
    
    # Test 1: Same seed should produce same results
    seeds = [42, 42, 42]  # Same seed repeated
    results_deterministic = []
    
    for i, seed in enumerate(seeds):
        metrics, steps = run_with_seed(seed)
        final_density = metrics['density_mean'][-1] if metrics['density_mean'] else 0
        final_variance = metrics['density_variance'][-1] if metrics['density_variance'] else 0
        
        results_deterministic.append({
            'run': i+1,
            'final_density': final_density,
            'final_variance': final_variance,
            'steps': steps
        })
        
        print(f"  Run {i+1}: Density={final_density:.4f}, Variance={final_variance:.4f}, Steps={steps}")
    
    # Check consistency
    densities = [r['final_density'] for r in results_deterministic]
    density_std = np.std(densities)
    
    if density_std < 0.001:
        print("✅ DETERMINISTIC: All runs produced identical results")
    else:
        print(f"⚠️  NON-DETERMINISTIC: Density std={density_std:.6f}")
    
    print("\n🔍 TEST 2: Noise Sensitivity")
    print("Running with different noise patterns...")
    
    # Test 2: Different seeds with noise
    seeds = [123, 456, 789]  # Different seeds
    results_stochastic = []
    
    for i, seed in enumerate(seeds):
        metrics, steps = run_with_seed(seed, add_noise=True)
        final_density = metrics['density_mean'][-1] if metrics['density_mean'] else 0
        final_variance = metrics['density_variance'][-1] if metrics['density_variance'] else 0
        
        results_stochastic.append({
            'run': i+1,
            'final_density': final_density,
            'final_variance': final_variance,
            'steps': steps
        })
        
        print(f"  Run {i+1}: Density={final_density:.4f}, Variance={final_variance:.4f}, Steps={steps}")
    
    # Check noise sensitivity
    stochastic_densities = [r['final_density'] for r in results_stochastic]
    stochastic_std = np.std(stochastic_densities)
    
    if stochastic_std < 0.01:
        print("✅ ROBUST: System insensitive to noise")
    elif stochastic_std < 0.05:
        print("⚖️  MODERATE: Some noise sensitivity")
    else:
        print("🎲 SENSITIVE: High noise sensitivity")
    
    print("\n🔍 TEST 3: Pattern Consistency")
    print("Comparing pattern formation across runs...")
    
    # Compare pattern metrics
    deterministic_variances = [r['final_variance'] for r in results_deterministic]
    stochastic_variances = [r['final_variance'] for r in results_stochastic]
    
    det_pattern_consistency = np.std(deterministic_variances) < 0.005
    stoch_pattern_consistency = np.std(stochastic_variances) < 0.01
    
    print(f"  Deterministic pattern consistency: {'✅' if det_pattern_consistency else '❌'}")
    print(f"  Stochastic pattern consistency: {'✅' if stoch_pattern_consistency else '❌'}")
    
    # Overall assessment
    print(f"\n📊 STOCHASTIC TEST SUMMARY:")
    print("=" * 50)
    if density_std < 0.001 and stochastic_std < 0.02:
        print("🎯 EXCELLENT: Highly reproducible and robust")
    elif density_std < 0.005 and stochastic_std < 0.05:
        print("✅ GOOD: Generally reproducible")
    else:
        print("⚠️  CAUTION: Significant variability detected")

if __name__ == "__main__":
    run_stochastic_tests()
