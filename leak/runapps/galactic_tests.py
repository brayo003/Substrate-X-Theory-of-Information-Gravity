#!/usr/bin/env python3
import numpy as np

def galactic_rotation_curve():
    """Test if substrate explains galactic rotation without dark matter"""
    print("🌌 TESTING GALACTIC ROTATION CURVES")
    print("=" * 50)
    
    # Problem: Stars orbit too fast at galactic edges
    # Dark matter solution: Invisible mass halo
    # Substrate solution: Modified force law at large scales
    
    print("OBSERVED: Rotation curves flat at large radii")
    print("NEWTONIAN: v ∝ 1/√r (decreasing)")
    print("DARK MATTER: v ≈ constant (flat)")
    
    print("\nSUBSTRATE X HYPOTHESES:")
    print("1. Information density s(r) has different large-scale profile")
    print("2. Substrate flow v_sub(r) modifies effective gravity")  
    print("3. Scale-dependent coupling constants")
    print("4. Dimensional transition effects (Phase 2)")
    
    return "flat_rotation_curve"

def dark_matter_replacement_test():
    """Calculate if substrate effects can replace dark matter"""
    print("\n🕵️ CAN SUBSTRATE REPLACE DARK MATTER?")
    print("=" * 50)
    
    # Milky Way: ~1.5e11 M_sun visible, ~8e11 M_sun dark matter
    visible_mass = 1.5e11  # Solar masses
    dark_mass = 8e11      # Solar masses
    
    print(f"Visible mass: {visible_mass:.1e} M_sun")
    print(f"Dark matter needed: {dark_mass:.1e} M_sun")
    print(f"Ratio: {dark_mass/visible_mass:.1f}x more dark than visible")
    
    print("\nSUBSTRATE REQUIREMENT:")
    print(f"Must provide ~5x gravitational enhancement at large scales")
    print("Test: Calculate s(r) × v_sub(r) at r = 50 kpc")
    
    return dark_mass/visible_mass
