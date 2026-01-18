#!/usr/bin/env python3
"""
Test the comprehensive temporal system across all domains and grid sizes
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_temporal import create_temporal_engine, UniversalTemporalSystem
import numpy as np

print("🕰️ COMPREHENSIVE TEMPORAL SYSTEM TEST")
print("Testing stability across domains and grid sizes")
print("=" * 60)

# Test grid sizes that previously exploded
grid_sizes = [20, 32, 64, 128]
domains = ['finance', 'urban', 'healthcare', 'cosmic']

results = {}

for domain in domains:
    print(f"\n🌍 DOMAIN: {domain}")
    print("-" * 40)
    
    domain_results = {}
    for grid_size in grid_sizes:
        print(f"  Testing grid {grid_size}x{grid_size}...")
        
        try:
            # Create temporal engine
            engine = create_temporal_engine(domain=domain, grid_size=grid_size)
            engine.initialize_gaussian(amplitude=0.5)
            
            # Evolve substantial steps
            engine.evolve(100, verbose=False)
            
            # Get final statistics
            stats = engine.get_temporal_statistics()
            
            # Determine stability
            stable = (stats['stability_warnings'] == 0 and 
                     stats['rho_max'] < 100 and 
                     not np.any(np.isnan(engine.rho)))
            
            domain_results[grid_size] = {
                'stable': stable,
                'physical_time': stats['physical_time'],
                'rho_max': stats['rho_max'],
                'warnings': stats['stability_warnings'],
                'dt': stats['current_dt'],
                'cfl': stats['cfl_number']
            }
            
            status = "✅ STABLE" if stable else "❌ UNSTABLE"
            print(f"    {status} | t={stats['physical_time']:.3f}{stats['time_units']} | ρ_max={stats['rho_max']:.3f} | CFL={stats['cfl_number']:.3f}")
            
        except Exception as e:
            domain_results[grid_size] = {
                'stable': False,
                'error': str(e)
            }
            print(f"    💥 CRASH: {str(e)}")
    
    results[domain] = domain_results

print(f"\n{'='*60}")
print("📊 TEMPORAL SYSTEM TEST RESULTS")
print("=" * 60)

for domain, domain_results in results.items():
    print(f"\n{domain.upper():>12}: ", end="")
    for grid_size in grid_sizes:
        result = domain_results.get(grid_size, {})
        if result.get('stable', False):
            print(f" {grid_size}✅", end="")
        elif 'error' in result:
            print(f" {grid_size}💥", end="")
        else:
            print(f" {grid_size}❌", end="")
    print()

print(f"\n💡 TEMPORAL SYSTEM ANALYSIS:")
print("✅ Green: Stable evolution with proper time scaling")
print("❌ Red: Unstable but non-crashing (needs tuning)")  
print("💥 Red: Complete crash (critical instability)")

# Test time scaling consistency
print(f"\n{'='*60}")
print("⏱️  TIME SCALING VERIFICATION")
print("=" * 60)

for domain in domains:
    config = UniversalTemporalSystem.get_domain_time_config(domain)
    dt_32 = UniversalTemporalSystem.compute_adaptive_dt(domain, 32)
    dt_64 = UniversalTemporalSystem.compute_adaptive_dt(domain, 64)
    dt_128 = UniversalTemporalSystem.compute_adaptive_dt(domain, 128)
    
    print(f"{domain:>12}: dt_32={dt_32:.2e}, dt_64={dt_64:.2e}, dt_128={dt_128:.2e}")
    print(f"{'':>12}  Scaling 32→64: {dt_64/dt_32:.3f}x (theoretical: 0.25x)")
    print(f"{'':>12}  Scaling 32→128: {dt_128/dt_32:.3f}x (theoretical: 0.0625x)")
