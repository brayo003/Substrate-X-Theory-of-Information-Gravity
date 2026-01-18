#!/usr/bin/env python3
"""
Test cosmic-scale physics with Universal Dynamics Engine
"""
import sys
import os

# Add core engine to path
sys.path.insert(0, 'core_engine/src')

from universal_dynamics import create_engine
import numpy as np

print("🌌 COSMIC PHYSICS TEST")
print("Testing if our engine can simulate dark matter halos")
print("=" * 50)

# Create cosmic-scale engine
cosmic_engine = create_engine(
    grid_size=64,        # Model a galaxy
    dt=1e16,            # Cosmic timescale (millions of years)
    M_factor=1e12,      # Galactic stiffness  
    rho_cutoff=1e-6,    # Cosmic density threshold
    alpha=1e-20,        # Fundamental coupling
    delta1=1e-10,       # Weak cosmic coupling
    delta2=1e-10,       # Weak cosmic coupling
    cubic_damping=0.01  # Minimal cosmic damping
)

print("🌠 Cosmic engine created with parameters:")
print(f"   M_factor: {cosmic_engine.M_factor:.1e}")
print(f"   rho_cutoff: {cosmic_engine.rho_cutoff:.1e}")
print(f"   dt: {cosmic_engine.dt:.1e}")

# Initialize with cosmic-scale Gaussian (dark matter halo seed)
cosmic_engine.initialize_gaussian(amplitude=1e-4, sigma=0.3)

print("\n🌀 Evolving cosmic system...")
# Evolve for cosmic timescales
cosmic_engine.evolve(50)

# Analyze results
stats = cosmic_engine.get_field_statistics()
print("\n📊 Cosmic Simulation Results:")
for key, value in stats.items():
    if isinstance(value, float):
        print(f"   {key}: {value:.3e}")
    else:
        print(f"   {key}: {value}")

# Check for halo-like structures
rho_flat = cosmic_engine.rho.flatten()
density_profile = np.histogram(rho_flat, bins=20)

print(f"\n🌍 Density Distribution:")
print(f"   Min density: {np.min(cosmic_engine.rho):.3e}")
print(f"   Max density: {np.max(cosmic_engine.rho):.3e}") 
print(f"   Mean density: {np.mean(cosmic_engine.rho):.3e}")

# Look for dark matter halo signature
central_density = cosmic_engine.rho[32, 32]  # Center
edge_density = cosmic_engine.rho[0, 0]       # Edge

if central_density > edge_density * 10:
    print("💫 HALO-LIKE STRUCTURE DETECTED!")
    print(f"   Center/Edge density ratio: {central_density/edge_density:.1f}x")
else:
    print("🌫️  No strong halo structure detected")

print("\n🎯 Next: Compare with actual dark matter halo profiles!")
