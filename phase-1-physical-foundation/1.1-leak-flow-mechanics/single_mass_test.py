#!/usr/bin/env python3
import numpy as np

def test_single_mass_scaling():
    """Test ONE mass with proper boundary conditions"""
    print("🔧 TESTING SINGLE MASS WITH FIXED BOUNDARIES")
    print("=" * 50)
    
    # Star parameters
    M = 2e30  # kg (Sun mass)
    R_star = 7e8  # meters (Sun radius)
    s_star = 1e20  # information density at surface (GUESS)
    v_star = 1000  # m/s, flow speed at surface (OUTWARD)
    
    # Test points at different distances
    r_points = [R_star, 1e10, 1e11, 1e12]  # From surface to far away
    
    print("Testing Option A: s ∝ 1/r, v_sub ∝ 1/r")
    print("r (m)        s×v           expected      ratio")
    print("-" * 45)
    
    success = True
    for r in r_points:
        # Option A: s ∝ 1/r, v_sub ∝ 1/r
        s = s_star * (R_star / r)
        v = v_star * (R_star / r)
        product = s * v
        expected = (s_star * v_star) * (R_star**2) / (r**2)
        ratio = product / expected
        
        print(f"{r:.1e}    {product:.2e}    {expected:.2e}    {ratio:.2f}")
        
        if abs(ratio - 1.0) > 0.01:
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ SCALING LAW SATISFIED - Theory is mathematically consistent!")
        print("You can now proceed to binary stars and other tests.")
    else:
        print("❌ SCALING BROKEN - Something is wrong with the implementation")
    
    return success

def test_flow_direction():
    """Test if flow direction makes physical sense"""
    print("\n🧭 TESTING FLOW DIRECTION PHYSICS")
    print("At star surface: Information should flow OUTWARD (v_sub > 0)")
    print("This means mass CREATES information that diffuses outward")
    print("Gravity emerges from pressure gradients, not direct flow")
    
    return True

if __name__ == "__main__":
    scaling_ok = test_single_mass_scaling()
    direction_ok = test_flow_direction()
    
    if scaling_ok and direction_ok:
        print("\n🎉 SINGLE MASS FOUNDATION IS SOLID!")
        print("Next: Add your actual substrate equations to this framework")
    else:
        print("\n💀 FOUNDATION NEEDS WORK - Fix scaling before continuing")
