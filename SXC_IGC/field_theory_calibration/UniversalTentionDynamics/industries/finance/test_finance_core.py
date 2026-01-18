#!/usr/bin/env python3
"""
CORRECTED SMOKE TEST: Market Dynamics
Finance domain validation for SXC-IGC engine
"""
import sys
import os
sys.path.insert(0, '../..')
from core_engine.src.universal_dynamics_monitored import create_monitored_engine
import numpy as np
import random

SEED = 123
random.seed(SEED)
np.random.seed(SEED)

print("💹 CORRECTED FINANCE DOMAIN SMOKE TEST")
print("Testing volatility, reaction-diffusion of assets, and constraints")
print("="*60)

def test_finance_market_smoke():
    engine = create_monitored_engine(
        'finance',
        grid_size=32,
        # Finance scaling: faster reaction, moderate diffusion
        M_factor=10000,
        tau_rho=0.0005,
        tau_E=0.0002,
        tau_F=0.001,
        delta1=2.0,
        delta2=1.0,
        kappa=1.2,
        cubic_damping=0.2,
        breaking_threshold=0.7,
        dt=0.00005
    )

    print("✅ Finance-scale SXC-IGC Engine Created")
    
    # Initialize market
    engine.initialize_gaussian(amplitude=1.0)
    
    # Initialize E field for market opportunities
    engine.E = np.random.uniform(0, 0.5, (32,32))
    
    # Run simulation
    market_data = []
    for step in range(100):
        engine.evolve(1, verbose=False)
        avg_density = np.mean(engine.rho)
        avg_development = np.mean(engine.E)
        stress = np.mean(engine.stress_history)
        market_data.append({'density': avg_density, 'development': avg_development, 'stress': stress})
        if step % 20 == 0:
            print(f"Step {step}: Density={avg_density:.3f}, Stress={stress:.3f}")
    
    final_density = market_data[-1]['density']
    density_change = final_density - market_data[0]['density']
    max_stress = max(d['stress'] for d in market_data)
    
    print(f"\n📊 FINANCE MARKET RESULTS:")
    print(f"Final Density: {final_density:.3f}")
    print(f"Density Change: {density_change:+.3f}")
    print(f"Max Stress: {max_stress:.3f}")
    
    dynamics_emerged = abs(density_change) > 0.01
    stable = max_stress < 0.5
    
    return dynamics_emerged and stable

if __name__ == "__main__":
    success = test_finance_market_smoke()
    print(f"\n🎯 SMOKE TEST: {'PASSED' if success else 'FAILED'}")
    print("="*60)
