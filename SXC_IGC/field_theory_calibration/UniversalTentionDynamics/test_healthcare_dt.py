#!/usr/bin/env python3
"""
Test healthcare with different dt values to find stability threshold
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust_corrected import create_robust_engine
import numpy as np

print("🏥 HEALTHCARE DT STABILITY TEST")
print("Finding the stable dt threshold for healthcare")
print("=" * 50)

dt_values = [0.001, 0.002, 0.003, 0.004, 0.005, 0.006]
results = {}

for dt in dt_values:
    print(f"\n🧪 Testing healthcare with dt={dt}:")
    try:
        engine = create_robust_engine('healthcare', grid_size=32, dt=dt)
        engine.initialize_gaussian(amplitude=1.0)
        
        # Evolve and monitor
        stable = True
        for step in range(20):
            engine.evolve_robust_imex()
            rho_max = np.max(engine.rho)
            
            if rho_max > 1000:
                print(f"  💥 Exploded at step {step} (ρ_max={rho_max:.1f})")
                stable = False
                break
            elif step % 5 == 0:
                print(f"  Step {step}: ρ_max={rho_max:.3f}")
        
        if stable:
            final_rho = np.max(engine.rho)
            print(f"  ✅ STABLE - Final ρ_max={final_rho:.3f}")
        
        results[dt] = stable
        
    except Exception as e:
        print(f"  💀 CRASHED: {e}")
        results[dt] = False

print(f"\n{'='*50}")
print("📊 HEALTHCARE DT STABILITY RESULTS:")
print("=" * 50)
for dt, stable in results.items():
    status = "✅ STABLE" if stable else "💥 UNSTABLE"
    print(f"dt={dt:.3f}: {status}")

# Find stability threshold
stable_dts = [dt for dt, stable in results.items() if stable]
if stable_dts:
    max_stable_dt = max(stable_dts)
    print(f"\n💡 STABILITY THRESHOLD: dt < {max_stable_dt:.3f}")
else:
    print(f"\n❌ NO STABLE dt FOUND")
