#!/usr/bin/env python3
"""
Test calibration of the Substrate X solver with physical parameters
"""
import numpy as np
from src.numerical_solver import SubstrateXSolver

def calculate_k_eff(solver, mass_kg, position):
    """Calculate k_eff from the current solution"""
    # Calculate gradient of the substrate field
    grad_s = solver.compute_gradient(solver.s)
    grad_s_mag = np.sqrt(np.sum(grad_s**2, axis=-1))
    
    # Calculate Newtonian acceleration
    if solver.dim == 2:
        x0, y0 = position
        r = np.sqrt((solver.X - x0)**2 + (solver.Y - y0)**2) + solver.r_min
        g_newton = solver.G * mass_kg / r**2
    else:
        x0, y0, z0 = position
        r = np.sqrt((solver.X - x0)**2 + (solver.Y - y0)**2 + (solver.Z - z0)**2) + solver.r_min
        g_newton = solver.G * mass_kg / r**2
    
    # Calculate k_eff in regions where the field is significant
    mask = (grad_s_mag > 1e-6 * np.max(grad_s_mag)) & (g_newton > 0)
    if np.any(mask):
        k_eff = np.median(grad_s_mag[mask] / g_newton[mask])
    else:
        k_eff = 0.0
    
    return k_eff

def solve_with_min_iterations(solver, mass_kg, position, min_iter=100, max_iter=5000):
    """Run the solver with a minimum number of iterations"""
    # Add the mass to the simulation
    solver.add_point_mass(mass_kg, position)
    
    print(f"Mass: {mass_kg/solver.M_sun:.1f} M_sun at position {position}")
    print("Iterating...")
    
    for i in range(max_iter):
        # Store previous state for convergence check
        s_prev = solver.s.copy()
        
        # Take a step
        solver.step()
        
        # Calculate residual
        residual = np.max(np.abs(solver.s - s_prev))
        
        if i % 100 == 0:
            print(f"  Iter {i}: max_s = {np.max(solver.s):.2e}, residual = {residual:.2e}")
        
        # Check for convergence after minimum iterations
        if i > min_iter and residual < 1e-10:
            print(f"✅ Converged after {i} iterations")
            break
    else:
        print(f"⚠️  Max iterations reached. Final residual: {residual:.2e}")
    
    return calculate_k_eff(solver, mass_kg, position)

def test_proper_calibration():
    """Test calibration with physical parameters"""
    print("🎯 PROPER CALIBRATION WITH PHYSICAL PARAMETERS")
    print("=" * 60)
    
    # Physical parameters (adjust these based on your needs)
    physical_params = {
        'alpha': 1e-8,    # Coupling strength
        'beta': 1e-5,     # Nonlinearity
        'gamma': 1e-8,    # Information density
        'chi': 1.0,       # Advection coherence
        'tau': 1e3        # Relaxation time
    }
    
    # Solar system test
    print("\n1. SOLAR SYSTEM SCALE (1 AU):")
    solver = SubstrateXSolver(
        grid_size=64,
        domain_size=2e11,  # ~1 AU
        **physical_params
    )
    
    # Position at the center of the domain
    position = (0, 0)
    
    # Run the simulation
    k_eff = solve_with_min_iterations(solver, 2e30, position, min_iter=200)
    print(f"  k_eff = {k_eff:.3e}")
    
    return k_eff

if __name__ == "__main__":
    test_proper_calibration()
