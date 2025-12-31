#!/usr/bin/env python3
"""
CORRECTED SMOKE TEST: Resource Allocation
Proper urban scaling for supply/demand balance
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

print("⚡ CORRECTED RESOURCE ALLOCATION SMOKE TEST")
print("Proper urban scaling: balanced supply/demand dynamics")
print("=" * 60)

def test_resource_smoke():
    # RESOURCE-SCALE PARAMETERS
    engine = create_monitored_engine(
        'general',
        grid_size=32,
        # RESOURCE SCALING: Balanced supply/demand
        M_factor=18000,      # Distribution capacity
        tau_rho=0.0008,      # SLOWER demand dynamics
        tau_E=0.0006,        # Fast supply response
        tau_F=0.001,         # Distribution dynamics
        delta1=2.0,          # Moderate base demand
        delta2=3.0,          # STRONG supply coupling
        kappa=1.0,           # Distribution efficiency
        cubic_damping=0.08,  # Moderate saturation
        breaking_threshold=0.6,
        dt=0.0001
    )
    
    print("✅ Resource-Scale SXC-IGC Engine Created")
    print(f"   τ_ρ: {engine.tau_rho} (SLOW) | δ2: {engine.delta2} (STRONG supply)")
    
    # Initialize with balanced supply/demand
    engine.initialize_gaussian(amplitude=0.3)  # Base demand
    
    # Supply centers (E field) - URBAN SCALE
    engine.E = np.zeros((32, 32))
    engine.E[8, 8] = 0.9    # NW supply hub
    engine.E[8, 24] = 0.9   # NE supply hub  
    engine.E[24, 8] = 0.9   # SW supply hub
    engine.E[24, 24] = 0.9  # SE supply hub
    
    # Demand patterns (ρ field) - URBAN SCALE
    engine.rho[12:20, 12:20] = 0.7  # Central residential (high demand)
    engine.rho[4:8, 4:8] = 0.5      # Suburban area (medium demand)
    
    # Distribution network (F field)
    engine.F = np.ones((32, 32)) * 0.6  # Default distribution resistance
    engine.F[16, :] = 0.3               # Main distribution corridor
    
    print("✅ Resource network initialized")
    print("   - 4 Supply hubs (high E)")
    print("   - Demand zones (moderate ρ)")
    print("   - Distribution network (F field)")
    
    # Run resource simulation
    resource_data = []
    
    for step in range(100):
        engine.evolve(1, verbose=False)
        
        demand = np.mean(engine.rho)
        supply = np.mean(engine.E)
        balance = supply / (demand + 1e-8)
        stress = np.mean(engine.stress_history)
        
        resource_data.append({
            'demand': demand,
            'supply': supply, 
            'balance': balance,
            'stress': stress
        })
        
        if step % 20 == 0:
            status = "BALANCED" if 0.8 < balance < 1.2 else "STRESSED"
            print(f"   Step {step}: Supply/Demand={balance:.2f} [{status}]")
    
    # Results analysis
    balances = [d['balance'] for d in resource_data]
    avg_balance = np.mean(balances)
    balanced_steps = sum(1 for b in balances if 0.7 < b < 1.3)
    
    print(f"\n📊 RESOURCE ALLOCATION RESULTS:")
    print(f"   Avg Supply/Demand: {avg_balance:.2f}")
    print(f"   Balanced Steps: {balanced_steps}/100")
    print(f"   Stability: {max(d['stress'] for d in resource_data):.3f}")
    
    # Success: Reasonable balance achieved
    reasonable_balance = 0.5 < avg_balance < 2.0
    some_balance_achieved = balanced_steps > 30
    stable = max(d['stress'] for d in resource_data) < 0.5
    
    return reasonable_balance and some_balance_achieved and stable

if __name__ == "__main__":
    success = test_resource_smoke()
    print(f"\n🎯 SMOKE TEST: {'PASSED' if success else 'FAILED'}")
    print("=" * 60)
