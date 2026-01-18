"""
Fixed version of Substrate X solver with corrected mass addition
"""
import numpy as np
from .numerical_solver import SubstrateXSolver

class SubstrateXSolverFixed(SubstrateXSolver):
    """
    Fixed version with correct mass addition physics
    """
    
    def add_point_mass(self, mass, position, radius=None):
        """
        CORRECTED: Add gravitational source with proper potential
        
        Parameters:
        -----------
        mass : float
            Mass in kg
        position : tuple
            (x, y) or (x, y, z) position in meters
        radius : float, optional
            Characteristic radius for regularization
        """
        if radius is None:
            radius = 2 * self.G * mass / (self.c**2)  # Schwarzschild radius
        
        if self.dim == 2:
            x0, y0 = position
            r = np.sqrt((self.X - x0)**2 + (self.Y - y0)**2)
            r_reg = r + self.r_min  # Regularized distance
            
            # CORRECTED: E field is gravitational potential
            # E = -G·M / r  (units: m²/s²)
            self.E += -self.G * mass / r_reg
            
            # F field is gravitational acceleration  
            # F = -∇(G·M/r) = G·M·r̂/r² (units: m/s²)
            F_mag = self.G * mass / (r_reg**2)
            F_x = -F_mag * (self.X - x0) / (r_reg + 1e-10)
            F_y = -F_mag * (self.Y - y0) / (r_reg + 1e-10)
            self.F[:,:,0] += F_x
            self.F[:,:,1] += F_y
            
            # Substrate velocity (unchanged)
            v_esc = np.sqrt(2 * self.G * mass / r_reg)
            v_sub_mag = np.minimum(v_esc, 0.9 * self.c)
            v_sub_x = -v_sub_mag * (self.X - x0) / (r_reg + 1e-10)
            v_sub_y = -v_sub_mag * (self.Y - y0) / (r_reg + 1e-10)
            self.v_sub[:,:,0] += v_sub_x
            self.v_sub[:,:,1] += v_sub_y
            
            print(f"Added mass {mass/self.M_sun:.3f} M_sun at ({x0/1e9:.2f}, {y0/1e9:.2f}) billion m")
