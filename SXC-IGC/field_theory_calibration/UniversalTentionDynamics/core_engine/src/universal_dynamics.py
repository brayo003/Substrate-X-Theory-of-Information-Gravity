#!/usr/bin/env python3
"""
UNIVERSAL DYNAMICS ENGINE - Core Implementation
Multi-scale field theory for complex systems modeling
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.fft import fft2, ifft2, fftfreq

class UniversalDynamicsEngine:
    """
    Core engine implementing the multi-scale field theory
    with surgical stiffness and robust numerical methods
    """
    
    def __init__(self, grid_size=128, L=1.0, dt=0.001, **params):
        self.grid_size = grid_size
        self.L = L
        self.dx = L / grid_size
        self.dt = dt
        
        # Default parameters with safety bounds
        self.alpha = params.get('alpha', 1e-5)
        self.beta = params.get('beta', 0.5)
        self.gamma = params.get('gamma', 0.2)
        self.delta1 = params.get('delta1', 0.5)
        self.delta2 = params.get('delta2', 0.3)
        self.kappa = params.get('kappa', 0.4)
        self.tau_rho = params.get('tau_rho', 0.1)
        self.tau_E = params.get('tau_E', 0.1)
        self.tau_F = params.get('tau_F', 0.1)
        
        # Surgical stiffness parameters
        self.M_factor = params.get('M_factor', 10000.0)
        self.eta_power = params.get('eta_power', 20.0)
        self.rho_cutoff = params.get('rho_cutoff', 0.8)
        self.cubic_damping = params.get('cubic_damping', 0.1)
        
        # Fields
        self.rho = np.zeros((grid_size, grid_size))
        self.E = np.zeros((grid_size, grid_size))
        self.F = np.zeros((grid_size, grid_size))
        
        self._setup_spectral_operators()
        
    def _setup_spectral_operators(self):
        """Setup spectral differentiation for IMEX integration"""
        n = self.grid_size
        kx = 2 * np.pi * fftfreq(n, self.dx)
        ky = 2 * np.pi * fftfreq(n, self.dx)
        kx_grid, ky_grid = np.meshgrid(kx, ky, indexing='ij')
        
        self.k_squared = kx_grid**2 + ky_grid**2
        self.implicit_factor_F = 1.0 / (1.0 + self.dt * self.k_squared)
        self.implicit_factor_E = 1.0 / (1.0 + self.dt * self.k_squared)
    
    def compute_effective_stiffness(self, rho):
        """Surgical stiffness with safety clamping"""
        tanh_term = np.tanh(self.eta_power * (rho - self.rho_cutoff))
        stiffness_factor = 1.0 + self.M_factor * np.maximum(0.0, tanh_term)
        stiffness_factor = np.minimum(stiffness_factor, 1e6)  # Safety bound
        return self.alpha * stiffness_factor
    
    def apply_periodic_laplacian_spectral(self, field):
        """Spectral Laplacian with PBCs"""
        field_hat = fft2(field)
        laplacian_hat = -self.k_squared * field_hat
        return np.real(ifft2(laplacian_hat))
    
    def compute_nonlinear_terms(self, rho, E, F):
        """Compute explicit nonlinear terms for IMEX"""
        laplacian_rho = self.apply_periodic_laplacian_spectral(rho)
        laplacian_E = self.apply_periodic_laplacian_spectral(E)
        laplacian_F = self.apply_periodic_laplacian_spectral(F)
        
        alpha_eff = self.compute_effective_stiffness(rho)
        
        # ρ evolution
        drho_dt_explicit = (self.gamma + alpha_eff * F**2) * laplacian_rho - rho / self.tau_rho
        
        # E evolution
        dE_dt_explicit = self.beta * F - E / self.tau_E
        
        # F evolution with cubic damping
        stiffness_modification = (alpha_eff - self.alpha) * F
        cubic_stabilization = -self.cubic_damping * F**3
        
        dF_dt_explicit = (self.delta1 * rho + self.delta2 * E - 
                         self.kappa * F - F / self.tau_F +
                         stiffness_modification + cubic_stabilization)
        
        return drho_dt_explicit, dE_dt_explicit, dF_dt_explicit, laplacian_E, laplacian_F
    
    def evolve_imex(self):
        """IMEX integration step"""
        rho, E, F = self.rho, self.E, self.F
        
        # Explicit terms
        drho_explicit, dE_explicit, dF_explicit, lap_E, lap_F = self.compute_nonlinear_terms(rho, E, F)
        
        # Update ρ (mostly explicit)
        self.rho += self.dt * drho_explicit
        
        # IMEX for E and F
        E_hat = fft2(E + self.dt * dE_explicit)
        self.E = np.real(ifft2(E_hat * self.implicit_factor_E))
        
        F_hat = fft2(F + self.dt * dF_explicit)
        self.F = np.real(ifft2(F_hat * self.implicit_factor_F))
        
        # Numerical safety
        self._apply_numerical_safety()
    
    def _apply_numerical_safety(self):
        """Prevent numerical blow-ups"""
        self.rho = np.clip(self.rho, -1e3, 1e3)
        self.E = np.clip(self.E, -1e3, 1e3)
        self.F = np.clip(self.F, -1e3, 1e3)
        
        if (np.any(np.isnan(self.rho)) or np.any(np.isnan(self.E)) or 
            np.any(np.isnan(self.F))):
            self.initialize_gaussian(amplitude=0.5)
    
    def initialize_gaussian(self, amplitude=1.0, sigma=0.1):
        """Initialize with periodic Gaussian"""
        x = np.linspace(-self.L/2, self.L/2, self.grid_size, endpoint=False)
        y = np.linspace(-self.L/2, self.L/2, self.grid_size, endpoint=False)
        X, Y = np.meshgrid(x, y, indexing='ij')
        
        r2 = X**2 + Y**2
        self.rho = amplitude * np.exp(-r2 / (2 * sigma**2))
        
        k = 2 * np.pi / self.L
        self.E = 0.01 * np.sin(k * X) * np.cos(k * Y)
        self.F = 0.01 * np.cos(k * X) * np.sin(k * Y)
    
    def evolve(self, steps=1):
        """Evolve system for given number of steps"""
        for _ in range(steps):
            self.evolve_imex()
    
    def get_field_statistics(self):
        """Get field statistics for monitoring"""
        return {
            'rho_max': np.max(self.rho),
            'rho_rms': np.sqrt(np.mean(self.rho**2)),
            'E_rms': np.sqrt(np.mean(self.E**2)),
            'F_rms': np.sqrt(np.mean(self.F**2)),
            'stiffness_active': np.max(self.rho) > self.rho_cutoff
        }

# Factory function for easy creation
def create_engine(domain='general', **kwargs):
    """Factory function to create domain-optimized engines"""
    domain_params = {
        'finance': {'dt': 0.001, 'cubic_damping': 0.5, 'M_factor': 50000},
        'urban': {'dt': 0.01, 'cubic_damping': 0.2, 'M_factor': 10000},
        'healthcare': {'dt': 0.005, 'cubic_damping': 0.1, 'M_factor': 20000},
        'general': {'dt': 0.001, 'cubic_damping': 0.1, 'M_factor': 10000}
    }
    
    params = domain_params.get(domain, domain_params['general'])
    params.update(kwargs)
    
    return UniversalDynamicsEngine(**params)

if __name__ == "__main__":
    # Test the core engine
    engine = create_engine('finance')
    engine.initialize_gaussian()
    print("🧪 Testing Universal Dynamics Engine...")
    engine.evolve(100)
    stats = engine.get_field_statistics()
    print(f"📊 Field stats: {stats}")
