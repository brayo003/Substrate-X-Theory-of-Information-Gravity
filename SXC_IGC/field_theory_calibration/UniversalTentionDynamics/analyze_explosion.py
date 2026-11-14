#!/usr/bin/env python3
"""
Analyze why explosions happen at grid_size > 32
"""
import numpy as np

def analyze_stability_conditions():
    print("🔍 STABILITY ANALYSIS: Why grids > 32 explode")
    print("=" * 50)
    
    # CFL condition for diffusion: dt < dx² / (2*D)
    # Where dx = 1/(N-1) for grid size N
    
    grid_sizes = [20, 32, 40, 64]
    base_dt = 0.01  # Assuming this is your time step
    D_effective = 1.0  # Effective diffusion coefficient
    
    print("\n📐 NUMERICAL STABILITY ANALYSIS:")
    print("Grid Size | dx       | Max Stable dt | Your dt | Stable?")
    print("-" * 55)
    
    for N in grid_sizes:
        dx = 1.0 / (N - 1)
        max_stable_dt = (dx ** 2) / (2 * D_effective)
        is_stable = base_dt < max_stable_dt
        
        stability = "✅ STABLE" if is_stable else "💥 EXPLODES"
        print(f"{N:>9} | {dx:.6f} | {max_stable_dt:.6f}    | {base_dt:.3f}   | {stability}")
    
    print(f"\n💡 INSIGHT: For grid_size=64, you need dt < {max_stable_dt:.6f}")
    print("   But you're using dt = 0.010000")
    print("   That's {:.1f}x larger than stable limit!".format(base_dt/max_stable_dt))

if __name__ == "__main__":
    analyze_stability_conditions()
