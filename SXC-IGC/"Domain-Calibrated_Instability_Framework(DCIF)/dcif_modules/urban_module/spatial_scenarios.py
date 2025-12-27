#!/usr/bin/env python3
"""
URBAN SPATIAL SCENARIO TESTS
Test different urban geometries and initial conditions
"""
import numpy as np
import sys
import os
sys.path.append('../../..')
from core_engine.src.universal_stable_core import UniversalStableCore

def create_single_core(grid_size):
    """Single downtown core"""
    rho = np.zeros(grid_size)
    center = (grid_size[0]//3, grid_size[1]//3)
    x, y = np.ogrid[:grid_size[0], :grid_size[1]]
    dist = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    rho = np.exp(-dist**2 / (grid_size[0]//6)**2) * 0.7
    return rho

def create_multi_center(grid_size):
    """Multiple urban centers"""
    rho = np.zeros(grid_size)
    centers = [(grid_size[0]//4, grid_size[1]//4),
               (3*grid_size[0]//4, 3*grid_size[1]//4),
               (grid_size[0]//4, 3*grid_size[1]//4),
               (3*grid_size[0]//4, grid_size[1]//4)]
    
    for center in centers:
        x, y = np.ogrid[:grid_size[0], :grid_size[1]]
        dist = np.sqrt((x - center[0])**2 + (y - center[1])**2)
        rho += np.exp(-dist**2 / (grid_size[0]//8)**2) * 0.4
    
    return np.clip(rho, 0, 1)

def create_linear_corridors(grid_size):
    """Linear development corridors"""
    rho = np.zeros(grid_size)
    # Main horizontal corridor
    rho[grid_size[0]//2, :] = 0.6
    # Main vertical corridor  
    rho[:, grid_size[1]//2] = 0.6
    # Diagonal corridors
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            if abs(i - j) < 3 or abs(i + j - grid_size[0]) < 3:
                rho[i, j] = max(rho[i, j], 0.4)
    return rho

def create_patchy_development(grid_size):
    """Irregular patchy development"""
    rho = np.random.random(grid_size) * 0.3
    # Add some higher density patches
    patches = [(8, 8), (8, 24), (24, 8), (24, 24)]
    for px, py in patches:
        rho[px-2:px+3, py-2:py+3] = 0.7
    return rho

def run_spatial_scenarios():
    print("🏙️ URBAN SPATIAL SCENARIO TESTS")
    print("Testing different urban geometries and initial conditions")
    print("=" * 60)
    
    scenarios = [
        (create_single_core, "Single Downtown Core"),
        (create_multi_center, "Multiple Urban Centers"),
        (create_linear_corridors, "Linear Development Corridors"),
        (create_patchy_development, "Patchy Irregular Development")
    ]
    
    results = []
    
    for scenario_func, scenario_name in scenarios:
        print(f"\n🔍 Testing: {scenario_name}")
        
        engine = UniversalStableCore(grid_size=(32, 32))
        engine.set_urban_parameters()
        
        # Create custom initial conditions
        rho_init = scenario_func((32, 32))
        engine.rho = rho_init
        engine.E = np.ones((32, 32)) * 0.4
        engine.F = np.ones((32, 32)) * 0.3
        
        print(f"  Initial ρ: [{rho_init.min():.3f}, {rho_init.max():.3f}]")
        
        # Run simulation
        pattern_evolution = []
        
        for step in range(150):
            if engine.evolve_system_adaptive(1):
                if step % 30 == 0:
                    density_variance = np.var(engine.rho)
                    pattern_evolution.append(density_variance)
            
            if engine.rejected_steps > 15:
                break
        
        # Analyze pattern evolution
        initial_var = pattern_evolution[0] if pattern_evolution else 0
        final_var = pattern_evolution[-1] if pattern_evolution else 0
        pattern_growth = final_var - initial_var
        
        result = {
            'scenario': scenario_name,
            'initial_variance': initial_var,
            'final_variance': final_var,
            'pattern_growth': pattern_growth,
            'stable_steps': engine.step_count,
            'final_stress': engine.stress_history[-1] if engine.stress_history else 0
        }
        results.append(result)
        
        if pattern_growth > 0.01:
            status = "✅ PATTERN ENHANCEMENT"
        elif pattern_growth > -0.005:
            status = "⚖️  PATTERN MAINTENANCE"  
        else:
            status = "📉 PATTERN DECAY"
            
        print(f"  Result: {status} (Growth: {pattern_growth:+.4f}, Stress: {result['final_stress']:.3f})")
    
    # Summary
    print(f"\n📊 SPATIAL SCENARIO SUMMARY:")
    print("=" * 50)
    for result in results:
        growth_symbol = "📈" if result['pattern_growth'] > 0.01 else "📊" if result['pattern_growth'] > -0.005 else "📉"
        print(f"  {growth_symbol} {result['scenario']}: Growth={result['pattern_growth']:+.4f}")
    
    return results

if __name__ == "__main__":
    run_spatial_scenarios()
