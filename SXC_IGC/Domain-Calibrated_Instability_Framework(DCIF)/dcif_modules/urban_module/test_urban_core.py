#!/usr/bin/env python3
"""
CORRECTED SMOKE TEST: City Growth Patterns
Proper urban scaling for SXC-IGC engine
"""
import sys
import os
sys.path.insert(0, '../..')
from core_engine.src.universal_dynamics_monitored import create_monitored_engine
import numpy as np
import random

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

print("🏙️ CORRECTED CITY GROWTH SMOKE TEST")
print("Proper urban scaling: slower decay, stronger coupling")
print("=" * 60)

def test_city_growth_smoke():
    # URBAN-SCALE PARAMETERS
    engine = create_monitored_engine(
        'general', 
        grid_size=32,
        # URBAN SCALING: Slower decay, stronger excitation
        M_factor=20000,      # Moderate constraints
        tau_rho=0.001,       # SLOWER decay for urban patterns
        tau_E=0.0005,        # Fast development response
        tau_F=0.002,         # Moderate constraint dynamics
        delta1=3.0,          # STRONG development drive
        delta2=2.0,          # Strong infrastructure coupling
        kappa=1.5,           # Moderate regulatory friction
        cubic_damping=0.1,   # Less damping for growth
        breaking_threshold=0.8,
        dt=0.0001
    )
    
    print("✅ Urban-Scale SXC-IGC Engine Created")
    print(f"   τ_ρ: {engine.tau_rho} (SLOW decay) | δ1: {engine.delta1} (STRONG drive)")
    
    # CORRECT initialization
    engine.initialize_gaussian(amplitude=1.0)  # Downtown core
    
    # Add development potential (E field) - URBAN SCALE
    engine.E = np.zeros((32, 32))
    engine.E[16, :] = 0.8    # East-west development corridor
    engine.E[:, 16] = 0.8    # North-south development corridor
    engine.E[8, 8] = 0.6     # Subcenter development
    
    print("✅ Urban pattern initialized")
    print("   - Downtown core + development corridors")
    
    # Run urban growth simulation
    growth_data = []
    
    for step in range(100):
        engine.evolve(1, verbose=False)
        
        density_mean = np.mean(engine.rho)
        development = np.mean(engine.E)
        stress = np.mean(engine.stress_history)
        
        growth_data.append({
            'density': density_mean,
            'development': development, 
            'stress': stress
        })
        
        if step % 20 == 0:
            print(f"   Step {step}: Density={density_mean:.3f}, Stress={stress:.3f}")
    
    # Results analysis
    final_density = growth_data[-1]['density']
    density_change = final_density - growth_data[0]['density']
    max_stress = max(d['stress'] for d in growth_data)
    
    print(f"\n📊 URBAN GROWTH RESULTS:")
    print(f"   Final Density: {final_density:.3f}")
    print(f"   Density Change: {density_change:+.3f}")
    print(f"   Max Stress: {max_stress:.3f}")
    
    # Success: Some density dynamics emerged
    dynamics_emerged = abs(density_change) > 0.01
    stable = max_stress < 0.5
    
    return dynamics_emerged and stable

if __name__ == "__main__":
    success = test_city_growth_smoke()
    print(f"\n🎯 SMOKE TEST: {'PASSED' if success else 'FAILED'}")
    print("=" * 60)
