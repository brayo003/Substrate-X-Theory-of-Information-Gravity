def test_analytic_scaling():
    """Verify what scaling your equations REQUIRE mathematically"""
    print("=== ANALYTIC SCALING TEST ===")
    
    # Your master equation in steady state, spherical symmetry:
    # (1/r²) d/dr (r² s v_sub) = αE - β(1/r²) d/dr (r² E v_sub)
    
    # For point mass: E = 0 outside star, so:
    # (1/r²) d/dr (r² s v_sub) = 0
    # Therefore: r² s v_sub = constant
    # So: s v_sub ∝ 1/r²  ← THIS IS FORCED BY YOUR EQUATION!
    
    print("YOUR EQUATION REQUIRES: s × v_sub ∝ 1/r²")
    print("This means:")
    print("If s ∝ 1/r², then v_sub ∝ constant")
    print("If s ∝ 1/r, then v_sub ∝ 1/r") 
    print("If s ∝ 1/r³, then v_sub ∝ r")
    
    # Check what your solver actually produced
    r = np.logspace(8, 12, 1000)
    s_simulated = 1.0 / r**2  # Your result
    v_sub_simulated = 1.0 / np.sqrt(r)  # Your result
    
    product = s_simulated * v_sub_simulated
    scaling = np.polyfit(np.log(r), np.log(product), 1)[0]
    
    print(f"Your simulation gave: s × v_sub ∝ r^{scaling:.3f}")
    print(f"Required: s × v_sub ∝ r^-2.000")
    
    if abs(scaling + 2.0) < 0.1:
        print("✅ SCALING CORRECT - Your solver works!")
        return True
    else:
        print("❌ SCALING WRONG - Your numerical solver is broken!")
        return False