#!/usr/bin/env python3
"""
Test suite for static PDE solver and k_eff calibration
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import laplace
from src.numerical_solver import SubstrateXSolver

def solve_static_pde(solver, mass, position, max_iterations=10000, tolerance=1e-10):
    """
    Solve the static (time-independent) PDE to find equilibrium s field
    and compute k_eff = |∇(s)| / |∇Φ_Newton|
    """
    print(f"🔍 SOLVING STATIC PDE FOR MASS {mass/solver.M_sun:.2f} M_sun")
    print("=" * 60)
    
    # Add the mass to create source terms
    solver.add_point_mass(mass, position)
    
    # Store original dynamic parameters
    original_s = solver.s.copy()
    
    try:
        # Initialize for static solution
        s_static = np.zeros_like(solver.s)
        residual_history = []
        
        print("Iterating to static solution...")
        
        for iteration in range(max_iterations):
            s_old = s_static.copy()
            
            # Compute all RHS terms
            laplacian_s = solver.compute_laplacian(s_static)
            
            # Advection term: ∇·(s v_sub)
            if solver.dim == 2:
                s_v_sub = s_static[:,:,np.newaxis] * solver.v_sub
            else:
                s_v_sub = s_static[:,:,:,np.newaxis] * solver.v_sub
            advection_term = solver.compute_divergence(s_v_sub)
            
            # Coherence term: ∇·(χ s u)  
            if solver.dim == 2:
                chi_s_u = solver.chi * s_static[:,:,np.newaxis] * solver.u
            else:
                chi_s_u = solver.chi * s_static[:,:,:,np.newaxis] * solver.u
            coherence_term = solver.compute_divergence(chi_s_u)
            
            # Source terms
            energy_term = solver.alpha * solver.E
            
            # β∇·(E v_sub)
            if solver.dim == 2:
                E_v_sub = solver.E[:,:,np.newaxis] * solver.v_sub
            else:
                E_v_sub = solver.E[:,:,:,np.newaxis] * solver.v_sub
            energy_advection_term = solver.beta * solver.compute_divergence(E_v_sub)
            
            # γ∇·F
            force_term = solver.gamma * solver.compute_divergence(solver.F)
            
            # Irreversible processes
            sigma_irr = 1e-15 * s_static**2  # Nonlinear dissipation
            
            # Assemble RHS for static equation
            rhs = (- (1.0/solver.tau) * (advection_term + coherence_term) +
                   energy_term + energy_advection_term + force_term - sigma_irr)
            
            # Solve for s using Jacobi iteration: ∇²s = rhs/c²
            rhs_normalized = rhs / solver.c**2
            
            # Jacobi update (simplified - you may need more sophisticated elliptic solver)
            if solver.dim == 2:
                s_new = np.zeros_like(s_static)
                s_new[1:-1, 1:-1] = (
                    rhs_normalized[1:-1, 1:-1] * solver.dx**2 +
                    s_static[1:-1, :-2] + s_static[1:-1, 2:] +
                    s_static[:-2, 1:-1] + s_static[2:, 1:-1]
                ) / 4
            else:
                s_new = np.zeros_like(s_static)
                s_new[1:-1, 1:-1, 1:-1] = (
                    rhs_normalized[1:-1, 1:-1, 1:-1] * solver.dx**2 +
                    s_static[1:-1, 1:-1, :-2] + s_static[1:-1, 1:-1, 2:] +
                    s_static[1:-1, :-2, 1:-1] + s_static[1:-1, 2:, 1:-1] +
                    s_static[:-2, 1:-1, 1:-1] + s_static[2:, 1:-1, 1:-1]
                ) / 6
            
            # Apply boundary conditions
            s_new[0,:] = 0; s_new[-1,:] = 0; s_new[:,0] = 0; s_new[:,-1] = 0
            
            # Check convergence
            residual = np.max(np.abs(s_new - s_old))
            residual_history.append(residual)
            
            s_static = s_new
            
            if iteration % 1000 == 0:
                print(f"   Iteration {iteration}: residual = {residual:.2e}")
            
            if residual < tolerance:
                print(f"✅ CONVERGED after {iteration} iterations")
                break
        
        else:
            print(f"⚠️  MAX ITERATIONS REACHED: residual = {residual:.2e}")
        
        # Compute k_eff from the static solution
        k_eff_value = compute_k_eff(solver, s_static, mass, position)
        
        print(f"🎯 RESULT: k_eff = {k_eff_value:.6f}")
        return k_eff_value, s_static, residual_history
        
    except Exception as e:
        print(f"❌ ERROR in static solver: {e}")
        return None, None, None

def compute_k_eff(solver, s_static, mass, position):
    """
    Compute k_eff = |∇(s)| / |∇Φ_Newton| at characteristic radius
    """
    # Compute gradient of substrate field
    grad_s = solver.compute_gradient(s_static)
    grad_s_magnitude = np.sqrt(np.sum(grad_s**2, axis=-1))
    
    # Compute Newtonian gravitational acceleration
    if solver.dim == 2:
        x0, y0 = position
        r = np.sqrt((solver.X - x0)**2 + (solver.Y - y0)**2) + solver.r_min
        g_newton_magnitude = solver.G * mass / r**2
    else:
        x0, y0, z0 = position
        r = np.sqrt((solver.X - x0)**2 + (solver.Y - y0)**2 + (solver.Z - z0)**2) + solver.r_min
        g_newton_magnitude = solver.G * mass / r**2
    
    # Compute k_eff as the ratio (averaged over meaningful region)
    # Avoid division by zero and focus on region where both fields are significant
    mask = (g_newton_magnitude > 1e-10 * np.max(g_newton_magnitude))
    
    if np.any(mask):
        k_eff_map = np.zeros_like(grad_s_magnitude)
        k_eff_map[mask] = grad_s_magnitude[mask] / g_newton_magnitude[mask]
        
        # Return median value to avoid edge effects
        k_eff_value = np.median(k_eff_map[k_eff_map > 0])
        return k_eff_value
    else:
        return 0.0

def test_k_eff_calibration():
    """
    Test the static solver across different scales to calibrate parameters
    """
    print("🎯 K_EFF CALIBRATION TEST")
    print("=" * 60)
    
    # Test solar system scale
    print("\n1. SOLAR SYSTEM SCALE (1 AU equivalent):")
    solver_solar = SubstrateXSolver(
        grid_size=128,
        domain_size=2e11,  # ~1 AU scale
        alpha=1e-68,
        beta=1e-53, 
        gamma=1e-68,
        chi=1.0
    )
    
    k_eff_solar, s_solar, residuals_solar = solve_static_pde(
        solver_solar, 
        mass=2e30,  # Solar mass
        position=(0, 0)
    )
    
    print(f"   Target: k_eff ≈ 2e-4, Actual: {k_eff_solar:.2e}")
    
    # Test galactic scale  
    print("\n2. GALACTIC SCALE (10 kpc equivalent):")
    solver_galactic = SubstrateXSolver(
        grid_size=128,
        domain_size=3e20,  # ~10 kpc scale
        alpha=1e-68,
        beta=1e-53,
        gamma=1e-68, 
        chi=1.0
    )
    
    k_eff_galactic, s_galactic, residuals_galactic = solve_static_pde(
        solver_galactic,
        mass=1e41,  # Galactic mass scale (~50 billion solar masses)
        position=(0, 0)
    )
    
    print(f"   Target: k_eff ≈ 0.3, Actual: {k_eff_galactic:.3f}")
    
    # Analysis
    print("\n3. CALIBRATION ANALYSIS:")
    ratio_achieved = k_eff_galactic / k_eff_solar if k_eff_solar > 0 else 0
    ratio_target = 0.3 / 2e-4  # 1500
    
    print(f"   k_eff ratio (galactic/solar): {ratio_achieved:.1f}")
    print(f"   Target ratio: {ratio_target:.1f}")
    print(f"   Match quality: {100 * (1 - abs(ratio_achieved - ratio_target)/ratio_target):.1f}%")
    
    return k_eff_solar, k_eff_galactic

if __name__ == "__main__":
    k_solar, k_galactic = test_k_eff_calibration()
    
    print("\n" + "=" * 60)
    if abs(k_solar - 2e-4)/2e-4 < 0.5 and abs(k_galactic - 0.3)/0.3 < 0.5:
        print("🎉 EXCELLENT MATCH! Parameters reproduce k_eff(r) discovery!")
    else:
        print("🔧 NEEDS TUNING: Adjust parameters to match k_eff targets")
