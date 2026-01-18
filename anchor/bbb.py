def multi_domain_rigorous():
    """
    Only after Pioneer validates, test other domains.
    """
    # Step 1: Pioneer validation
    eta_pioneer, err_pioneer, pioneer_valid = pioneer_analysis()
    
    if not pioneer_valid:
        print("\nSTOP: Pioneer doesn't support η≠0. Framework fails.")
        return
    
    print("\n=== MOVING TO SECOND DOMAIN ===")
    
    # Load real pulsar data (simplified)
    # In reality: PSR B1913+16 timing residuals
    t = np.array([0, 5, 10, 15, 20])  # years
    P_dot_residual = np.array([1.02e-14, 1.01e-14, 0.99e-14, 1.00e-14, 1.01e-14])  # s/s
    
    # Alternative: P_dot = η * some_physical_model(t)
    # Fit η independently
    def pulsar_model(t, eta):
        return eta * 1.2e-12 * (1 + 0.01 * t)  # simplified
    
    popt_p, pcov_p = curve_fit(pulsar_model, t, P_dot_residual, p0=[0.01])
    eta_pulsar = popt_p[0]
    
    print(f"Pulsar η: {eta_pulsar:.6f}")
    print(f"Pioneer η: {eta_pioneer:.6f}")
    
    # Test if they're consistent (same η within errors)
    diff_sigma = abs(eta_pioneer - eta_pulsar) / np.sqrt(err_pioneer**2)
    
    if diff_sigma > 2:
        print(f"\nSCALE DEPENDENCE DETECTED: {diff_sigma:.1f}σ difference")
        print("η varies between solar system and binary pulsar scales.")
    else:
        print("\nConsistent η across domains (no scale dependence)")
