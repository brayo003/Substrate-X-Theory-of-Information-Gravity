#!/usr/bin/env python3
"""
GATE 2 NUMERICAL APPROACH - COUPLED FIXED POINT WITH ETA_W3=0
Test sensitivity of η_W3 assumption by solving coupled system
"""

import sympy as sp
import numpy as np

def numerical_coupled_fixed_point():
    """
    Solve coupled fixed-point system with η_W3=0 and test sensitivity
    """
    
    print("=" * 70)
    print("GATE 2 NUMERICAL APPROACH - COUPLED FIXED POINT")
    print("=" * 70)
    
    # Step 1: Define beta functions (simplified)
    print("\nStep 1: Define beta functions")
    print("-" * 70)
    
    print("Using Falls-Litim fixed point as initial condition:")
    print("  g* = 0.707")
    print("  λ* = 0.193")
    print("  w̃₂* = -0.0046")
    print()
    
    print("Beta function structure:")
    print("  β_g = (2 + η_g) g + ...")
    print("  β_λ = (-2 + η_λ) λ + ...")
    print("  β_w2 = η_w2 w̃₂ + ...")
    print("  β_w3 = (2 + η_w3) w̃₃' + A_W3")
    print()
    print("Assumption: η_w3 = 0 (to be tested)")
    print()
    
    # Step 2: A_W3 from earlier calculation
    print("\nStep 2: A_W3 from earlier calculation")
    print("-" * 70)
    
    g_star = 0.707
    lambda_star = 0.193
    w2_tilde_star = -0.0046
    
    A0 = w2_tilde_star + (1 - 2*lambda_star) / (16 * sp.pi * g_star)
    A0_num = float(A0.evalf())
    
    alpha2 = 8
    n_eff = 4
    
    aw3_litim = -n_eff * (alpha2 * w2_tilde_star)**3 / (4 * A0**4) / (4 * sp.pi)**2
    aw3_litim_num = float(aw3_litim.evalf())
    
    print(f"A₀ = {A0_num:.6f}")
    print(f"A_W3 (Litim) = {aw3_litim_num:.6f}")
    print()
    
    # Step 3: Fixed point with η_w3 = 0
    print("\nStep 3: Fixed point with η_w3 = 0")
    print("-" * 70)
    
    print("β_w3 = 2 w̃₃' + A_W3 = 0")
    print("w̃₃'* = -A_W3 / 2")
    print()
    
    w3_prime_star = -aw3_litim_num / 2
    print(f"w̃₃'* = {w3_prime_star:.6f}")
    print()
    
    # Step 4: Test sensitivity to η_w3
    print("\nStep 4: Test sensitivity to η_w3")
    print("-" * 70)
    
    print("Test different η_w3 values:")
    for eta_w3 in [-2, -1, -0.5, 0, 0.5, 1, 2]:
        if eta_w3 == -2:
            print(f"η_w3 = {eta_w3}: DENOMINATOR ZERO - SINGULAR")
        else:
            w3_prime = -aw3_litim_num / (2 + eta_w3)
            print(f"η_w3 = {eta_w3}: w̃₃'* = {w3_prime:.6f}")
    print()
    
    # Step 5: Check backreaction on other couplings
    print("\nStep 5: Check backreaction on other couplings")
    print("-" * 70)
    
    print("Currently: using pre-W3 fixed point values")
    print("This assumes w̃₃ does not affect g*, λ*, w̃₂*")
    print()
    print("This is NOT self-consistent but provides a first estimate")
    print()
    
    # Step 6: Sign analysis
    print("\nStep 6: Sign analysis")
    print("-" * 70)
    
    print("A_W3 > 0 (positive)")
    print("w̃₃'* = -A_W3/2 < 0 (negative)")
    print()
    print("For η_w3 > -2:")
    print("  - Denominator positive")
    print("  - w̃₃'* negative")
    print("  - Sign is robust")
    print()
    print("For η_w3 < -2:")
    print("  - Denominator negative")
    print("  - w̃₃'* positive")
    print("  - Sign would flip")
    print()
    print("For η_w3 = -2:")
    print("  - Singularity (unphysical)")
    print()
    
    # Step 7: Conclusion
    print("\n" + "=" * 70)
    print("NUMERICAL APPROACH CONCLUSION")
    print("=" * 70)
    print()
    print("With η_w3 = 0:")
    print(f"  w̃₃'* = {w3_prime_star:.6f} (negative)")
    print()
    print("Sensitivity analysis:")
    print("  - For η_w3 ∈ [-1, +1]: w̃₃'* ∈ [-12.22, -4.07]")
    print("  - Sign remains negative for η_w3 > -2")
    print("  - Sign would flip only for η_w3 < -2 (unlikely)")
    print()
    print("Scientific assessment:")
    print("  - The η_w3 = 0 assumption leads to:")
    print("    * w̃₃* ≠ 0 (negative)")
    print("    * Sign is robust for reasonable η_w3")
    print("  - Magnitude uncertain by factor ~3")
    print()
    print("  - This supports the qualitative conclusion:")
    print("    * w̃₃* is nonzero and negative")
    print("  - But quantitative value is uncertain")
    print()
    print("  - For precise quantitative result, η_w3 still required")
    print()
    print("=" * 70)
    
    return {
        'w3_prime_star_eta0': w3_prime_star,
        'aw3_litim': aw3_litim_num,
        'sensitivity_range': [-12.22, -4.07],
        'sign_robust': True,
        'sign_flip_threshold': -2
    }

if __name__ == "__main__":
    result = numerical_coupled_fixed_point()
    print(f"\nw̃₃'* (η=0): {result['w3_prime_star_eta0']:.6f}")
    print(f"Sign robust: {result['sign_robust']}")
