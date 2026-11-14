#!/usr/bin/env python3
"""
Corrected Weyl Tensor Calculation for S²×S²
Uses simpler approach to compute W₃
"""

import sympy as sp

def s2xs2_corrected_weyl():
    """
    Compute W₃ for S²×S² using the correct approach
    """

    print("=" * 70)
    print("CORRECTED WEYL TENSOR CALCULATION FOR S²×S²")
    print("=" * 70)

    # Define coordinates
    theta1, phi1, theta2, phi2 = sp.symbols('theta1 phi1 theta2 phi2', real=True)

    # Define radii (use r1 = r2 = 1 for simplicity)
    r1, r2 = sp.symbols('r1 r2', positive=True)

    print("\nStep 1: Define metric matrix")
    print("-" * 70)

    # Metric components for S²(r₁) × S²(r₂)
    g = sp.Matrix([
        [r1**2, 0, 0, 0],
        [0, r1**2 * sp.sin(theta1)**2, 0, 0],
        [0, 0, r2**2, 0],
        [0, 0, 0, r2**2 * sp.sin(theta2)**2]
    ])

    print("Metric tensor:")
    print(g)

    # Inverse metric
    print("\nStep 2: Compute inverse metric")
    print("-" * 70)

    g_inv = sp.Matrix([
        [1/r1**2, 0, 0, 0],
        [0, 1/(r1**2 * sp.sin(theta1)**2), 0, 0],
        [0, 0, 1/r2**2, 0],
        [0, 0, 0, 1/(r2**2 * sp.sin(theta2)**2)]
    ])

    print("Inverse metric:")
    print(g_inv)

    # Compute Christoffel symbols
    print("\nStep 3: Compute Christoffel symbols")
    print("-" * 70)

    coords = [theta1, phi1, theta2, phi2]

    Gamma = []
    for k in range(4):
        Gamma_row = []
        for i in range(4):
            Gamma_col = []
            for j in range(4):
                gamma = 0
                for l in range(4):
                    term = g_inv[k,l] * (
                        sp.diff(g[j,l], coords[i]) +
                        sp.diff(g[i,l], coords[j]) -
                        sp.diff(g[i,j], coords[l])
                    )
                    gamma += term
                Gamma_col.append(sp.simplify(gamma/2))
            Gamma_row.append(Gamma_col)
        Gamma.append(sp.Matrix(Gamma_row))

    print("Christoffel symbols computed")

    # Compute Riemann tensor (upper index first)
    print("\nStep 4: Compute Riemann tensor")
    print("-" * 70)

    Riemann = []
    for k in range(4):
        Riemann_k = []
        for l in range(4):
            Riemann_kl = []
            for i in range(4):
                Riemann_kli = []
                for j in range(4):
                    riemann = (
                        sp.diff(Gamma[k][l,j], coords[i]) -
                        sp.diff(Gamma[k][l,i], coords[j])
                    )
                    for m in range(4):
                        riemann += (
                            Gamma[k][m,j] * Gamma[m][l,i] -
                            Gamma[k][m,i] * Gamma[m][l,j]
                        )
                    Riemann_kli.append(sp.simplify(riemann))
                Riemann_kl.append(Riemann_kli)
            Riemann_k.append(Riemann_kl)
        Riemann.append(Riemann_k)

    print("Riemann tensor computed")

    # Compute Ricci tensor
    print("\nStep 5: Compute Ricci tensor")
    print("-" * 70)

    Ricci = sp.zeros(4, 4)
    for i in range(4):
        for j in range(4):
            ricci_ij = 0
            for k in range(4):
                ricci_ij += Riemann[k][i][k][j]
            Ricci[i,j] = sp.simplify(ricci_ij)

    print("Ricci tensor:")
    print(Ricci)

    # Scalar curvature
    print("\nStep 6: Compute scalar curvature")
    print("-" * 70)

    R_scalar = 0
    for i in range(4):
        for j in range(4):
            R_scalar += g_inv[i,j] * Ricci[i,j]

    R_scalar = sp.simplify(R_scalar)
    print(f"R = {R_scalar}")

    # Evaluate for r1 = r2 = 1
    R_equal = R_scalar.subs({r1: 1, r2: 1})
    print(f"R (r1=r2=1) = {R_equal}")

    # Compute Weyl tensor using the standard formula
    print("\nStep 7: Compute Weyl tensor")
    print("-" * 70)

    # Lower Riemann: R_ijkl = g_km R^m_ijl
    Riemann_low = []
    for i in range(4):
        Riemann_i = []
        for j in range(4):
            Riemann_ij = []
            for k in range(4):
                Riemann_ijk = []
                for l in range(4):
                    rijkl = 0
                    for m in range(4):
                        rijkl += g[k,m] * Riemann[m][i][j][l]
                    Riemann_ijk.append(sp.simplify(rijkl))
                Riemann_ij.append(Riemann_ijk)
            Riemann_i.append(Riemann_ij)
        Riemann_low.append(Riemann_i)

    # Weyl tensor: C_ijkl = R_ijkl - (1/2)(g_ik R_jl - g_il R_jk - g_jk R_il + g_jl R_ik) + (1/6) R (g_ik g_jl - g_il g_jk)
    Weyl = []
    for i in range(4):
        Weyl_i = []
        for j in range(4):
            Weyl_ij = []
            for k in range(4):
                Weyl_ijk = []
                for l in range(4):
                    cijkl = Riemann_low[i][j][k][l]

                    cijkl -= (sp.Rational(1,2) * (
                        g[i,k] * Ricci[j,l] -
                        g[i,l] * Ricci[j,k] -
                        g[j,k] * Ricci[i,l] +
                        g[j,l] * Ricci[i,k]
                    ))

                    cijkl += (sp.Rational(1,6) * R_scalar * (
                        g[i,k] * g[j,l] -
                        g[i,l] * g[j,k]
                    ))

                    Weyl_ijk.append(sp.simplify(cijkl))
                Weyl_ij.append(Weyl_ijk)
            Weyl_i.append(Weyl_ij)
        Weyl.append(Weyl_i)

    print("Weyl tensor computed")

    # Check if Weyl is non-zero
    print("\nStep 8: Check if Weyl tensor is non-zero")
    print("-" * 70)

    non_zero_count = 0
    for i in range(4):
        for j in range(4):
            for k in range(4):
                for l in range(4):
                    if Weyl[i][j][k][l] != 0:
                        non_zero_count += 1

    print(f"Number of non-zero Weyl components: {non_zero_count}")

    if non_zero_count > 0:
        print("✓ TEST 2 PASSED: Weyl tensor is non-zero on S²×S²")
    else:
        print("✗ TEST 2 FAILED: Weyl tensor is zero")

    # Compute W₃ using the contraction: W₃ = C_{μνρσ} C^{νμ}_{αβ} C^{ρσ αβ}
    print("\nStep 9: Compute W₃")
    print("-" * 70)

    # First, compute C^{νμ}_{αβ} = g^{νρ} g^{μσ} C_{ρσαβ}
    C_upper_lower = []
    for nu in range(4):
        C_nu = []
        for mu in range(4):
            C_nu_mu = []
            for alpha in range(4):
                C_nu_mu_alpha = []
                for beta in range(4):
                    cnu_mu_alpha_beta = 0
                    for rho in range(4):
                        for sigma in range(4):
                            cnu_mu_alpha_beta += (
                                g_inv[nu,rho] * g_inv[mu,sigma] *
                                Weyl[rho][sigma][alpha][beta]
                            )
                    C_nu_mu_alpha.append(sp.simplify(cnu_mu_alpha_beta))
                C_nu_mu.append(C_nu_mu_alpha)
            C_nu.append(C_nu_mu)
        C_upper_lower.append(C_nu)

    # Second, compute C^{ρσ αβ} = g^{ρμ} g^{σν} g^{αγ} g^{βδ} C_{μνγδ}
    C_full_upper = []
    for rho in range(4):
        C_rho = []
        for sigma in range(4):
            C_rho_sigma = []
            for alpha in range(4):
                C_rho_sigma_alpha = []
                for beta in range(4):
                    crho_sigma_alpha_beta = 0
                    for mu in range(4):
                        for nu in range(4):
                            for gamma in range(4):
                                for delta in range(4):
                                    crho_sigma_alpha_beta += (
                                        g_inv[rho,mu] * g_inv[sigma,nu] *
                                        g_inv[alpha,gamma] * g_inv[beta,delta] *
                                        Weyl[mu][nu][gamma][delta]
                                    )
                    C_rho_sigma_alpha.append(sp.simplify(crho_sigma_alpha_beta))
                C_rho_sigma.append(C_rho_sigma_alpha)
            C_rho.append(C_rho_sigma)
        C_full_upper.append(C_rho)

    # Compute W₃
    W3 = 0
    for mu in range(4):
        for nu in range(4):
            for rho in range(4):
                for sigma in range(4):
                    for alpha in range(4):
                        for beta in range(4):
                            W3 += (
                                Weyl[mu][nu][rho][sigma] *
                                C_upper_lower[nu][mu][alpha][beta] *
                                C_full_upper[rho][sigma][alpha][beta]
                            )

    W3 = sp.simplify(W3)

    print(f"W₃ (general) = {W3}")

    # Evaluate for r1 = r2 = 1
    W3_equal = W3.subs({r1: 1, r2: 1})
    print(f"W₃ (r1=r2=1) = {W3_equal}")

    # Try to simplify further
    W3_simplified = sp.simplify(W3_equal)
    print(f"W₃ (simplified) = {W3_simplified}")

    # If it's coordinate-dependent, evaluate at a specific point
    # For S²×S², the result should be constant, so any point should give the same value
    W3_evaluated = W3_equal.subs({theta1: sp.pi/2, phi1: 0, theta2: sp.pi/2, phi2: 0})
    W3_evaluated = sp.simplify(W3_evaluated)
    print(f"W₃ (evaluated at θ₁=π/2, θ₂=π/2) = {W3_evaluated}")

    # Numerical value
    try:
        W3_num = float(W3_evaluated)
        print(f"W₃ (numerical) = {W3_num}")

        # Expected value
        expected = 128/27
        print(f"Expected W₃ = {expected}")

        # Check
        if abs(W3_num - expected) < 1e-6:
            print("✓ TEST 3 PASSED: W₃ = 128/27 confirmed")
        else:
            print(f"✗ TEST 3 FAILED: W₃ = {W3_num}, expected {expected}")
    except:
        print("Could not convert to float")
        print(f"Symbolic result: {W3_evaluated}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Non-zero Weyl components: {non_zero_count}")
    print(f"R (r1=r2=1): {R_equal}")
    print(f"W₃ (evaluated): {W3_evaluated}")
    print()

    return {
        'W3_computed': W3_evaluated,
        'R_scalar': R_equal,
        'non_zero_weyl': non_zero_count,
        'status': 'weyl_computed'
    }

if __name__ == "__main__":
    result = s2xs2_corrected_weyl()
    print(f"\nStatus: {result['status']}")
