"""
Information-Gravity Coupling Module
Handles the coupling between Substrate X density and gravitational potential.
"""

import numpy as np
from scipy import ndimage

class InformationGravityCoupling:
    def __init__(self, grid_size=32, domain_size=1e21, coupling_strength=1.0, G=6.67430e-11):
        self.grid_size = grid_size
        self.domain_size = domain_size
        self.coupling_strength = coupling_strength
        self.G = G  # Gravitational constant
        
        # Grid spacing
        self.dx = domain_size / grid_size
        self.dy = domain_size / grid_size
        
        # Create coordinate arrays
        x = np.linspace(-domain_size/2, domain_size/2, grid_size)
        y = np.linspace(-domain_size/2, domain_size/2, grid_size)
        self.X, self.Y = np.meshgrid(x, y)
        
    def compute_gravitational_potential(self, density):
        """Compute gravitational potential from density distribution"""
        # Simple implementation using convolution with 1/r kernel
        epsilon = 1e-10 * self.domain_size  # Regularization
        
        # Create Green's function (1/r potential)
        r = np.sqrt(self.X**2 + self.Y**2 + epsilon**2)
        green_function = -self.G / r
        
        # Convolve density with Green's function
        potential = ndimage.convolve(density, green_function, mode='constant', cval=0.0)
        potential *= self.dx * self.dy  # Account for grid spacing
        
        return potential * self.coupling_strength
    
    def compute_gravitational_response(self, density, current_potential, dt, tau=1.0):
        """Compute gravitational response to density changes"""
        # Compute new potential from density
        new_potential = self.compute_gravitational_potential(density)
        
        # Relaxation toward new potential (simplified)
        if tau > 0:
            # Exponential relaxation
            alpha = dt / (tau + dt)
            potential_next = (1 - alpha) * current_potential + alpha * new_potential
        else:
            potential_next = new_potential
        
        return {
            'phi_next': potential_next,
            'phi_new': new_potential,
            'relaxation_factor': alpha if tau > 0 else 1.0
        }
    
    def compute_coupling_force(self, density, potential):
        """Compute the force coupling density and potential"""
        # Gradient of potential gives force field
        grad_phi_x, grad_phi_y = np.gradient(potential, self.dx, self.dy)
        
        # Force density (simplified coupling)
        force_density = -density * np.sqrt(grad_phi_x**2 + grad_phi_y**2)
        
        return {
            'force_x': grad_phi_x,
            'force_y': grad_phi_y, 
            'force_magnitude': np.sqrt(grad_phi_x**2 + grad_phi_y**2),
            'force_density': force_density
        }
