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