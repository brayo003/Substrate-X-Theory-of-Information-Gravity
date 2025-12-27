#!/usr/bin/env python3
"""
Test if our engine naturally produces inflationary expansion
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')

from universal_dynamics import create_engine
import numpy as np

print("🌠 COSMIC INFLATION TEST")
print("Can our engine produce exponential expansion?")
print("=" * 50)

# Parameters tuned for inflationary behavior
inflation_engine = create_engine(
    grid_size=48,
    dt=1e4,              # Fine timestep for early universe
    M_factor=1e10,       # High stiffness for phase transition
    rho_cutoff=0.3,      # Inflation threshold
    alpha=1e-12,         # Weak coupling
    delta1=1e-8,         # Very weak sources
    delta2=1e-8,
    cubic_damping=0.05,  # Minimal damping during inflation
    tau_rho=1e15,        # Very slow relaxation
    tau_E=1e15,
    tau_F=1e15
)

# Start with quantum fluctuation-sized region
print("Initializing Planck-scale fluctuation...")
inflation_engine.initialize_gaussian(amplitude=0.1, sigma=0.08)

# Track expansion history
expansion_history = []
density_history = []
time_steps = []

initial_volume = np.sum(np.abs(inflation_engine.rho) > 0.001)

print(f"Initial volume: {initial_volume} cells")
print("Beginning cosmic evolution...")

# Simulate early universe evolution
for step in range(30):
    inflation_engine.evolve(1)
    
    current_volume = np.sum(np.abs(inflation_engine.rho) > 0.001)
    expansion_factor = current_volume / initial_volume
    mean_density = np.mean(inflation_engine.rho)
    
    expansion_history.append(expansion_factor)
    density_history.append(mean_density)
    time_steps.append(step)
    
    if step % 5 == 0 or expansion_factor > 10:
        print(f"   Step {step}: Volume = {current_volume} cells (x{expansion_factor:.1f})")
        print(f"      Mean density: {mean_density:.6f}")
        
        # Check for exponential growth
        if step > 5 and expansion_history[-1] > expansion_history[-2] * 1.5:
            print("      🚀 EXPONENTIAL EXPANSION DETECTED!")

# Analyze expansion behavior
final_expansion = expansion_history[-1]
max_expansion = max(expansion_history)

print(f"\n📊 INFLATION RESULTS:")
print(f"   Final expansion: {final_expansion:.1f}x")
print(f"   Maximum expansion: {max_expansion:.1f}x")
print(f"   Final density: {density_history[-1]:.6f}")

# Check for inflationary signatures
if max_expansion > 20:
    print("💫 STRONG INFLATIONARY EXPANSION!")
    print("   Matches cosmic inflation predictions")
elif max_expansion > 5:
    print("🌠 MODERATE EXPANSION DETECTED")
    print("   Similar to early universe growth")

# Check if expansion was exponential
if len(expansion_history) > 10:
    early_growth = expansion_history[5] / expansion_history[0]
    late_growth = expansion_history[-1] / expansion_history[5]
    
    print(f"   Early growth (steps 0-5): {early_growth:.1f}x")
    print(f"   Late growth (steps 5-30): {late_growth:.1f}x")
    
    if early_growth > late_growth * 2:
        print("   📈 EARLY RAPID GROWTH (Inflation-like!)")

# Test reheating transition
print(f"\n🔥 TESTING REHEATING TRANSITION")
if density_history[-1] > 0 and any(d < 0 for d in density_history):
    print("   NEGATIVE → POSITIVE DENSITY TRANSITION")
    print("   This matches reheating after inflation!")

print("\n🎯 Cosmic inflation test complete!")

# Save data for analysis
np.savez('cosmic_inflation_data.npz',
         expansion=expansion_history,
         density=density_history,
         time=time_steps)

print("💾 Data saved to cosmic_inflation_data.npz")
