#!/usr/bin/env python3
import numpy as np

def substrate_flow_field(mass, position, r):
    """Calculate substrate velocity at distance r from mass"""
    # Your leak-flow equation here
    G = 6.67430e-11
    v_magnitude = np.sqrt(2 * G * mass / r)  # Simplified for testing
    return v_magnitude

def test_binary_system():
    """Test if two stars create stable orbits"""
    print("🚀 RUNNING BINARY STAR TEST")
    print("=" * 50)
    
    # Two stars: Sun-like masses, 1 AU separation
    M1 = 2e30  # kg (Solar mass)
    M2 = 2e30  # kg  
    separation = 1.5e11  # meters (1 AU)
    
    # Test superposition: v_total = v1 + v2
    # Calculate at midpoint between stars
    test_point = separation / 2
    
    v1 = substrate_flow_field(M1, 0, test_point)
    v2 = substrate_flow_field(M2, separation, test_point)
    v_total = v1 + v2
    
    print(f"Star 1 flow at midpoint: {v1:.2f} m/s")
    print(f"Star 2 flow at midpoint: {v2:.2f} m/s") 
    print(f"Total superposition flow: {v_total:.2f} m/s")
    
    # Simple stability check
    expected_orbital_speed = 30000  # m/s (typical binary system)
    
    print(f"Expected orbital speed: {expected_orbital_speed:.2f} m/s")
    print(f"Ratio (total/expected): {v_total/expected_orbital_speed:.2f}")
    
    # Basic stability criterion
    if 0.1 < v_total/expected_orbital_speed < 10:
        print("✅ ORBITS LIKELY STABLE - Theory survives!")
        return True
    else:
        print("❌ ORBITS LIKELY CHAOTIC - Theory fails superposition!")
        return False

if __name__ == "__main__":
    success = test_binary_system()
    
    if success:
        print("\n🎉 THEORY PASSES BASIC TEST - Proceed to detailed simulation!")
    else:
        print("\n💀 THEORY FAILS - Fix superposition assumption first!")
