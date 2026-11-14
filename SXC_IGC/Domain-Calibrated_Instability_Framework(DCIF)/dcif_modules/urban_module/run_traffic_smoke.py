#!/usr/bin/env python3
"""
CORRECTED SMOKE TEST: Traffic Flow Optimization  
Proper urban scaling for congestion dynamics
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

print("🚗 CORRECTED TRAFFIC FLOW SMOKE TEST")
print("Proper urban scaling: sustained congestion patterns")
print("=" * 60)

def test_traffic_smoke():
    # TRAFFIC-SCALE PARAMETERS
    engine = create_monitored_engine(
        'general',
        grid_size=32,
        # TRAFFIC SCALING: Sustained congestion, road dynamics
        M_factor=15000,      # Road capacity
        tau_rho=0.0005,      # SLOWER congestion decay
        tau_E=0.001,         # Traffic generation
        tau_F=0.0008,        # Road resistance dynamics  
        delta1=4.0,          # STRONG traffic generation
        delta2=2.5,          # Strong route coupling
        kappa=2.0,           # Congestion resistance
        cubic_damping=0.05,  # Minimal dissipation
        breaking_threshold=0.7,
        dt=0.0001
    )
    
    print("✅ Traffic-Scale SXC-IGC Engine Created")
    print(f"   τ_ρ: {engine.tau_rho} (SLOW decay) | δ1: {engine.delta1} (STRONG traffic)")
    
    # Initialize with road network
    engine.initialize_gaussian(amplitude=0.5)  # Base traffic
    
    # Create road network in F field (resistance)
    engine.F = np.ones((32, 32)) * 0.8  # Default high resistance
    engine.F[8, :] = 0.1                # Highway - low resistance
    engine.F[:, 8] = 0.1                # Highway - low resistance
    engine.F[24, :] = 0.1               # Second highway
    engine.F[:, 24] = 0.1               # Second highway
    
    # Add traffic demand in E field (excitation)
    engine.E = np.zeros((32, 32))
    engine.E[0, 0] = 1.0    # Morning commute from NW
    engine.E[31, 31] = 1.0  # Evening commute from SE
    
    print("✅ Traffic network initialized")
    print("   - Highway grid (low resistance F)")
    print("   - Commute sources (high excitation E)")
    
    # Run traffic simulation
    traffic_data = []
    congestion_events = 0
    
    for step in range(100):
        engine.evolve(1, verbose=False)
        
        congestion = np.mean(engine.rho)
        road_resistance = np.mean(engine.F)
        stress = np.mean(engine.stress_history)
        
        traffic_data.append({
            'congestion': congestion,
            'resistance': road_resistance,
            'stress': stress
        })
        
        if congestion > 0.1:  # Meaningful congestion threshold
            congestion_events += 1
            
        if step % 20 == 0:
            status = "CONGESTED" if congestion > 0.1 else "FLOWING"
            print(f"   Step {step}: Congestion={congestion:.3f} [{status}]")
    
    # Results analysis
    avg_congestion = np.mean([d['congestion'] for d in traffic_data])
    max_congestion = max(d['congestion'] for d in traffic_data)
    congestion_ratio = congestion_events / len(traffic_data)
    
    print(f"\n📊 TRAFFIC FLOW RESULTS:")
    print(f"   Avg Congestion: {avg_congestion:.3f}")
    print(f"   Max Congestion: {max_congestion:.3f}")
    print(f"   Congestion Events: {congestion_events}/100")
    
    # Success: Some congestion patterns emerged
    patterns_emerged = congestion_ratio > 0.2 and max_congestion > 0.15
    stable = max(d['stress'] for d in traffic_data) < 0.5
    
    return patterns_emerged and stable

if __name__ == "__main__":
    success = test_traffic_smoke()
    print(f"\n🎯 SMOKE TEST: {'PASSED' if success else 'FAILED'}")
    print("=" * 60)
