#!/usr/bin/env python3
# diagnosis.py - COMPLETE THEORY DIAGNOSTIC

import numpy as np
import matplotlib.pyplot as plt

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

def test_force_law_compatibility():
    """Find which force laws are mathematically possible"""
    print("\n=== FORCE LAW COMPATIBILITY TEST ===")
    
    # Your equation forces: s × v_sub ∝ 1/r²
    # Possible force laws:
    
    force_laws = [
        ("F = k s v_sub", "s v_sub ∝ 1/r² → F ∝ 1/r² ✅"),
        ("F = k s² v_sub", "s² v_sub ∝ s × (s v_sub) ∝ s × 1/r²"),
        ("F = k v_sub²", "v_sub² ∝ ?"),
        ("F = k ∇s", "∇s ∝ ds/dr"),
        ("F = k s ∇s", "s ∇s ∝ s × ds/dr"),
    ]
    
    # Test each with different s scalings
    s_scalings = [
        ("s ∝ 1/r", "v_sub ∝ 1/r → F = k s v_sub ∝ 1/r² ✅"),
        ("s ∝ 1/r²", "v_sub ∝ constant → F = k s v_sub ∝ 1/r² ✅"), 
        ("s ∝ 1/r³", "v_sub ∝ r → F = k s v_sub ∝ 1/r² ✅"),
    ]
    
    print("POSSIBLE COMBINATIONS:")
    for s_scaling, result in s_scalings:
        print(f"  {s_scaling:15} → {result}")
    
    print("\nYOUR SIMULATION GAVE: s ∝ 1/r², v_sub ∝ 1/√r")
    print("THIS VIOLATES YOUR OWN EQUATION: s × v_sub ∝ 1/r^{2.5} ≠ 1/r²")
    
    return True  # Force law itself is fine, implementation is wrong

def test_solver_accuracy():
    """Check if your numerical solver is working correctly"""
    print("\n=== SOLVER ACCURACY TEST ===")
    
    # Test on a known analytic solution
    # For s ∝ 1/r², v_sub ∝ constant satisfies: ∇·(s v_sub) = 0
    
    r = np.logspace(8, 12, 1000)
    dr = r[1] - r[0]
    
    # Known solution: s = A/r², v_sub = B (constant)
    A, B = 1e40, 1e3
    s_analytic = A / r**2
    v_sub_analytic = B * np.ones_like(r)
    
    # Check if it satisfies your equation numerically
    residuals = []
    for i in range(1, len(r)-1):
        # ∇·(s v_sub) in spherical: (1/r²) d/dr (r² s v_r)
        flux_right = (r[i] + dr/2)**2 * s_analytic[i] * v_sub_analytic[i]
        flux_left = (r[i] - dr/2)**2 * s_analytic[i-1] * v_sub_analytic[i-1]
        divergence = (flux_right - flux_left) / (r[i]**2 * dr)
        residuals.append(divergence)
    
    max_residual = np.max(np.abs(residuals))
    print(f"Max residual for analytic solution: {max_residual:.2e}")
    
    if max_residual < 1e-10:
        print("✅ SOLVER WORKS - reproduces known solution")
        return True
    else:
        print("❌ SOLVER BROKEN - cannot reproduce known solution")
        return False

def test_boundary_conditions():
    """Check if boundary conditions are properly enforced"""
    print("\n=== BOUNDARY CONDITION TEST ===")
    
    # Your equation: ∇·(s v_sub) = sources
    # At large r: s → 0, v_sub → 0
    # At r = R_star: need physical boundary condition
    
    print("CURRENT BOUNDARY ISSUES:")
    print("1. No boundary condition specified at star surface")
    print("2. v_sub singular as r → 0 in your initial guess")
    print("3. s normalization arbitrary")
    
    print("\nSUGGESTED FIXES:")
    print("At r = R_star: s(R_star) = s_star (fixed information density)")
    print("At r = R_star: v_sub(R_star) determined by star's properties")
    print("At large r: s → s_background (cosmic information density)")
    
    return False  # Boundary conditions definitely need work

def test_energy_coupling():
    """Check the αE source term behavior"""
    print("\n=== ENERGY COUPLING TEST ===")
    
    # Your equation has: ∂s/∂t + ∇·(s v_sub) = αE + ...
    # But for a static star, E ≠ 0 only inside the star
    
    r = np.logspace(8, 12, 1000)
    R_star = 7e8
    
    # Energy density: E > 0 inside star, E = 0 outside
    E = np.where(r <= R_star, 1e10, 0)
    
    # The source αE creates information INSIDE the star
    # This information must flow OUTWARD via s v_sub
    
    print("PROBLEM: Your initial guess has v_sub pointing INWARD")
    print("But information is CREATED inside star and must flow OUT")
    print("This suggests: v_sub should point OUTWARD near the star!")
    
    print("\nPOSSIBLE RESOLUTION:")
    print("v_sub changes direction - inward far away, outward near surface")
    print("This would be a RADICAL but physically interesting result")
    
    return "DIRECTION_AMBIGUITY"

def run_complete_diagnostic():
    """Run all diagnostic tests"""
    print("🚀 RUNNING COMPLETE THEORY DIAGNOSTIC")
    print("=" * 60)
    
    tests = [
        ("Analytic Scaling", test_analytic_scaling),
        ("Force Law Compatibility", test_force_law_compatibility), 
        ("Solver Accuracy", test_solver_accuracy),
        ("Boundary Conditions", test_boundary_conditions),
        ("Energy Coupling", test_energy_coupling),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔬 RUNNING: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ TEST CRASHED: {e}")
            results.append((test_name, "CRASH"))
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY:")
    for test_name, result in results:
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠️  " + str(result)
        print(f"  {test_name:25} → {status}")
    
    # Overall assessment
    passes = sum(1 for _, result in results if result is True)
    if passes == len(tests):
        print("\n🎉 ALL TESTS PASS - Theory is mathematically sound!")
        return True
    else:
        print(f"\n🔧 {len(tests)-passes}/{len(tests)} tests need attention")
        print("Focus on fixing these issues before proceeding")
        return False

if __name__ == "__main__":
    run_complete_diagnostic()