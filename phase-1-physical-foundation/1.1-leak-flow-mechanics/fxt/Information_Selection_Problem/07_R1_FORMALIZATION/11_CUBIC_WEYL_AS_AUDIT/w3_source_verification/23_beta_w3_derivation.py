#!/usr/bin/env python3
"""
BETA_W3 DERIVATION - DETERMINE WHETHER ETA_W3 IS REQUIRED
Derive the dimensionless beta function for w₃ from the action
"""

import sympy as sp

def derive_beta_w3():
    """
    Derive β_{w₃} from the action to determine if η_W3 is required
    """
    
    print("=" * 70)
    print("BETA_W3 DERIVATION - ETA_W3 NECESSITY ANALYSIS")
    print("=" * 70)
    
    # Step 1: Define the action
    print("\nStep 1: Define the action")
    print("-" * 70)
    
    print("Γ_k = ∫ d⁴x √g [")
    print("    -(R - 2Λ_k)/(16πG_k)")
    print("    + w̃₂ C²")
    print("    + w̃₃ k^(-2) W₃")
    print("]")
    print()
    
    # Step 2: Dimensional analysis
    print("\nStep 2: Dimensional analysis")
    print("-" * 70)
    
    print("Dimensions:")
    print("  [R] = [L]^{-2}")
    print("  [C²] = [L]^{-4}")
    print("  [W₃] = [L]^{-6}")
    print("  [G_k] = [L]^{2}")
    print("  [Λ_k] = [L]^{-2}")
    print("  [k] = [L]^{-1}")
    print()
    print("Coupling dimensions:")
    print("  [w̃₂] = [L]^{0} (dimensionless)")
    print("  [w̃₃] = [L]^{-4}")
    print()
    
    # Step 3: Define dimensionless couplings
    print("\nStep 3: Define dimensionless couplings")
    print("-" * 70)
    
    print("Introduce dimensionless couplings:")
    print("  g = k² G_k")
    print("  λ = Λ_k / k²")
    print("  w̃₂ is already dimensionless")
    print("  w̃₃' = w̃₃ k² (dimensionless)")
    print()
    
    # Step 4: Canonical scaling dimensions
    print("\nStep 4: Canonical scaling dimensions")
    print("-" * 70)
    
    print("Under k → k e^t (t = ln k):")
    print("  dg/dt = (2 + η_g) g")
    print("  dλ/dt = (-2 + η_λ) λ")
    print("  dw̃₂/dt = (0 + η_w2) w̃₂")
    print("  dw̃₃'/dt = (2 + η_w3) w̃₃'")
    print()
    print("where η are anomalous dimensions from the FRGE.")
    print()
    
    # Step 5: General beta function structure
    print("\nStep 5: General beta function structure")
    print("-" * 70)
    
    print("The beta functions have the form:")
    print("  β_g = (2 + η_g) g + source terms")
    print("  β_λ = (-2 + η_λ) λ + source terms")
    print("  β_w2 = η_w2 w̃₂ + source terms")
    print("  β_w3 = (2 + η_w3) w̃₃' + source terms")
    print()
    print("The source terms come from the FRGE trace contributions")
    print("when couplings appear in the Hessian.")
    print()
    
    # Step 6: W3 source term analysis
    print("\nStep 6: W3 source term analysis")
    print("-" * 70)
    
    print("The source term for w̃₃ (call it A_W3) comes from:")
    print("  - EH sector contributing to W3 through background curvature")
    print("  - C² sector contributing to W3 through Weyl-linear kinetic term")
    print("  - W3 sector self-contribution (higher order in w̃₃)")
    print()
    print("At linear order in w̃₃ (anomalous generation):")
    print("  β_w3 = (2 + η_w3) w̃₃' + A_W3")
    print()
    print("The question: Is η_w3 required to determine w̃₃*?")
    print()
    
    # Step 7: Fixed-point equation
    print("\nStep 7: Fixed-point equation")
    print("-" * 70)
    
    print("At fixed point, β_w3 = 0:")
    print("  (2 + η_w3) w̃₃'* + A_W3 = 0")
    print("  w̃₃'* = -A_W3 / (2 + η_w3)")
    print()
    print("Critical question: Does η_w3 depend on w̃₃?")
    print()
    
    # Step 8: η_w3 dependence analysis
    print("\nStep 8: η_w3 dependence analysis")
    print("-" * 70)
    
    print("η_w3 comes from the W3 contribution to its own Hessian.")
    print("The W3 term in the action is:")
    print("  S_W3 = w̃₃' k^(-2) ∫√g W₃")
    print()
    print("The Hessian δ²S_W3/δgδg will contain terms proportional to:")
    print("  - w̃₃' (linear in the coupling)")
    print("  - k^(-2) (explicit scale dependence)")
    print()
    print("The anomalous dimension η_w3 is extracted from the")
    print("FRGE trace and generally depends on the coupling itself.")
    print()
    print("Therefore: η_w3 = f(g, λ, w̃₂, w̃₃')")
    print()
    
    # Step 9: Perturbative analysis
    print("\nStep 9: Perturbative analysis")
    print("-" * 70)
    
    print("If w̃₃' is small at the fixed point, we can expand:")
    print("  η_w3 ≈ η_w3|_{w̃₃'=0} + (∂η_w3/∂w̃₃')|_{w̃₃'=0} w̃₃' + ...")
    print()
    print("At lowest order:")
    print("  β_w3 ≈ (2 + η_w3|_{w̃₃'=0}) w̃₃' + A_W3")
    print()
    print("If η_w3|_{w̃₃'=0} is small, we can approximate:")
    print("  w̃₃'* ≈ -A_W3 / 2")
    print()
    print("However, this is an APPROXIMATION, not an exact result.")
    print()
    
    # Step 10: Truncation order analysis
    print("\nStep 10: Truncation order analysis")
    print("-" * 70)
    
    print("The truncation is: {EH, C², W₃}")
    print()
    print("At this truncation order:")
    print("  - η_g depends on g, λ, w̃₂")
    print("  - η_λ depends on g, λ, w̃₂")
    print("  - η_w2 depends on g, λ, w̃₂")
    print("  - η_w3 depends on g, λ, w̃₂, w̃₃'")
    print()
    print("The η_w3 dependence on w̃₃' cannot be eliminated")
    print("by truncation order - it's intrinsic to the operator.")
    print()
    
    # Step 11: Self-consistency requirement
    print("\nStep 11: Self-consistency requirement")
    print("-" * 70)
    
    print("For a mathematically consistent fixed point:")
    print("  1. Compute η_w3 as a function of all couplings")
    print("  2. Solve the coupled system:")
    print("     β_g = 0")
    print("     β_λ = 0")
    print("     β_w2 = 0")
    print("     β_w3 = 0")
    print("  3. Verify the solution is self-consistent")
    print()
    print("Setting η_w3 = 0 is NOT a controlled approximation")
    print("unless we can prove η_w3 ≪ 2 at the fixed point.")
    print()
    
    # Step 12: Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION: ETA_W3 IS REQUIRED")
    print("=" * 70)
    print()
    print("Mathematical requirement:")
    print("  - η_w3 depends on w̃₃' (cannot be eliminated)")
    print("  - The fixed-point equation is:")
    print("    (2 + η_w3) w̃₃'* + A_W3 = 0")
    print("  - Setting η_w3 = 0 is an uncontrolled approximation")
    print()
    print("To determine w̃₃* exactly, we must:")
    print("  1. Compute η_w3 from the W3 Hessian")
    print("  2. Solve the full coupled system")
    print("  3. Verify self-consistency")
    print()
    print("Therefore: η_W3 calculation is REQUIRED for Gate 2 closure.")
    print()
    print("=" * 70)
    
    return {
        'eta_w3_required': True,
        'reason': 'eta_w3 depends on w3_prime and cannot be eliminated by truncation',
        'fixed_point_equation': '(2 + eta_w3) w3_prime* + A_W3 = 0',
        'approximation_valid': False,
        'approximation_error': 'Setting eta_w3 = 0 is uncontrolled without proof'
    }

if __name__ == "__main__":
    result = derive_beta_w3()
    print(f"\nη_W3 required: {result['eta_w3_required']}")
