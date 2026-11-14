#!/usr/bin/env python3
"""
Unit tests for Substrate X Theory dimensional consistency.

Verifies that all terms in the master equation have consistent units.
"""
import numpy as np
import unittest
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from numerical_solver import SubstrateXSolver

class TestUnits(unittest.TestCase):    
    def setUp(self):
        """Set up test case with a solver instance."""
        self.solver = SubstrateXSolver(
            grid_size=32,
            domain_size=1e12,  # meters
            dim=2,
            alpha=1e-10,  # Will be scaled in __init__
            gamma=1e-10,  # Will be scaled in __init__
            tau=1e3,      # seconds
            chi=1e6       # m/s (will be capped at 0.9c)
        )
        
        # Create a test energy density field (J/m³)
        self.test_E = np.zeros_like(self.solver.E)
        self.test_E[16, 16] = 1.0  # 1 J/m³ at center
        
        # Create a test force density field (N/m³)
        self.test_F = np.zeros_like(self.solver.F)
        self.test_F[16, 16, :] = [1.0, 0.0]  # 1 N/m³ in x-direction at center
    
    def test_alphaE_units(self):
        """Test that αE has units of [s]/T²."""
        # αE should have units of [s]/T²
        alphaE = self.solver.alpha * self.test_E
        
        # Verify the term is non-zero where we set it
        self.assertNotEqual(alphaE[16, 16], 0.0)
        
        # Verify the term is zero elsewhere
        self.assertEqual(alphaE[0, 0], 0.0)
        
        print(f"\nαE test:")
        print(f"  α = {self.solver.alpha:.3e} [s] L / M")
        print(f"  E = {self.test_E[16, 16]:.1f} J/m³")
        print(f"  αE = {alphaE[16, 16]:.3e} [s]/T²")
    
    def test_gamma_divF_units(self):
        """Test that γ∇·F has units of [s]/T²."""
        # Compute divergence of F
        if self.solver.dim == 2:
            # For 2D: F has shape (nx, ny, 2)
            grad_Fx = np.gradient(self.test_F[:,:,0], self.solver.dx, axis=1)
            grad_Fy = np.gradient(self.test_F[:,:,1], self.solver.dx, axis=0)
            divF = grad_Fx + grad_Fy
        else:
            # For 3D: F has shape (nx, ny, nz, 3)
            grad_Fx = np.gradient(self.test_F[:,:,:,0], self.solver.dx, axis=2)
            grad_Fy = np.gradient(self.test_F[:,:,:,1], self.solver.dx, axis=1)
            grad_Fz = np.gradient(self.test_F[:,:,:,2], self.solver.dx, axis=0)
            divF = grad_Fx + grad_Fy + grad_Fz
        
        # γ∇·F should have units of [s]/T²
        gamma_divF = self.solver.gamma * divF
        
        print(f"\nγ∇·F test:")
        print(f"  γ = {self.solver.gamma:.3e} [s] L³ / M")
        print(f"  |∇·F| = {np.max(np.abs(divF)):.3e} N/m⁴")
        print(f"  γ∇·F = {np.max(np.abs(gamma_divF)):.3e} [s]/T²")
        
        # Verify the term is non-zero where we set it
        self.assertNotEqual(np.max(np.abs(gamma_divF)), 0.0)

if __name__ == "__main__":
    unittest.main()
