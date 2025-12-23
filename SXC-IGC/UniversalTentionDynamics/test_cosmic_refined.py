#!/usr/bin/env python3
"""
Refined cosmic physics test with better parameters
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')

from universal_dynamics import create_engine
import numpy as np

print("🌌 REFINED COSMIC PHYSICS TEST")
print("=" * 50)

# Better cosmic parameters - adjusted for numerical stability
cosmic_engine = create_engine(
    grid_size=128,       # Higher resolution
    dt=1e8,             # Smaller timestep for stability
    M_factor=1e8,       # Reduced stiffness
    rho_cutoff=0.1,     # More reasonable threshold
    alpha=1e-10,        # Adjusted coupling
    delta1=1e-6,        # Weaker source terms
    delta2=1e-6,
    cubic_damping=0.5,  # Stronger stabilization
    tau_rho=1e10,       # Slower relaxation
    tau_E=1e10,
    tau_F=1e10
)

print("🌠 Refined cosmic engine created")
print(f"   Grid: {cosmic_engine.grid_size}²")
print(f"   Damping: {cosmic_engine.cubic_damping}")

# Initialize with smoother cosmic seed
cosmic_engine.initialize_gaussian(amplitude=0.5, sigma=0.4)

print("Initial field ranges:")
print(f"   ρ: [{np.min(cosmic_engine.rho):.3f}, {np.max(cosmic_engine.rho):.3f}]")
print(f"   E: [{np.min(cosmic_engine.E):.3f}, {np.max(cosmic_engine.E):.3f}]")
print(f"   F: [{np.min(cosmic_engine.F):.3f}, {np.max(cosmic_engine.F):.3f}]")

print("\n🌀 Evolving cosmic system (slowly)...")
# Evolve in smaller steps with monitoring
for step in range(20):
    cosmic_engine.evolve(1)
    
    # Monitor field stability
    if step % 5 == 0:
        rho_range = np.max(cosmic_engine.rho) - np.min(cosmic_engine.rho)
        print(f"   Step {step}: ρ range = {rho_range:.3f}")

print("\n📊 FINAL COSMIC STRUCTURE ANALYSIS:")

# Calculate radial density profile
center = cosmic_engine.grid_size // 2
radial_profile = []
radii = []

for r in range(1, center):
    mask = np.zeros((cosmic_engine.grid_size, cosmic_engine.grid_size))
    y, x = np.ogrid[:cosmic_engine.grid_size, :cosmic_engine.grid_size]
    distance = np.sqrt((x - center)**2 + (y - center)**2)
    mask[(distance >= r-1) & (distance < r)] = 1
    
    if np.sum(mask) > 0:
        radial_density = np.mean(cosmic_engine.rho[mask == 1])
        radial_profile.append(radial_density)
        radii.append(r)

print(f"Radial bins analyzed: {len(radial_profile)}")

if len(radial_profile) > 5:
    center_density = radial_profile[0]
    edge_density = radial_profile[-1]
    
    print(f"Center density: {center_density:.6f}")
    print(f"Edge density: {edge_density:.6f}")
    
    if edge_density > 0:
        density_ratio = center_density / edge_density
        print(f"Center/Edge ratio: {density_ratio:.1f}x")
        
        if density_ratio > 2:
            print("💫 STRONG HALO-LIKE STRUCTURE!")
        elif density_ratio > 1.1:
            print("🌠 WEAK HALO SIGNATURE DETECTED")
        else:
            print("🌫️  UNIFORM DISTRIBUTION")
    
    # Check for realistic dark matter profile (should decrease with radius)
    if radial_profile[0] > radial_profile[1] > radial_profile[2]:
        print("📉 DENSITY DECREASES WITH RADIUS (Realistic!)")
    else:
        print("📈 Unusual density profile")

# Field statistics
stats = cosmic_engine.get_field_statistics()
print(f"\nField Statistics:")
print(f"   ρ max: {stats['rho_max']:.6f}")
print(f"   ρ RMS: {stats['rho_rms']:.6f}")
print(f"   Stiffness active: {stats['stiffness_active']}")

print("\n🎯 Cosmic simulation completed successfully!")
