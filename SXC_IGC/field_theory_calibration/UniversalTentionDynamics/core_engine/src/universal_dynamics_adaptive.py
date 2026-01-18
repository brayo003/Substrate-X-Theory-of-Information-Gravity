#!/usr/bin/env python3
"""
UNIVERSAL DYNAMICS ENGINE - ADAPTIVE SANE VERSION
Ecosystem-based stiffness that adapts, breaks, and recovers
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.fft import fft2, ifft2, fftfreq

class AdaptiveUniversalEngine:
    """
    Sane universal engine with ecosystem-style adaptive constraints
    """
    
    def __init__(self, grid_size=64, L=1.0, dt=0.001, **params):
        self.grid_size = grid_size
        self.L = L
        self.dx = L / grid_size
        self.dt = dt
        
        # Physical parameters
        self.alpha = max(params.get('alpha', 1e-5), 0)
        self.beta = params.get('beta', 0.5)
        self.gamma = max(params.get('gamma', 0.2), 0)
        
        self.delta1 = params.get('delta1', 0.5)
        self.delta2 = params.get('delta2', 0.3)
        self.kappa = max(params.get('kappa', 0.4), 0)
        
        self.tau_rho = max(params.get('tau_rho', 0.1), 1e-10)
        self.tau_E = max(params.get('tau_E', 0.1), 1e-10)
        self.tau_F = max(params.get('tau_F', 0.1), 1e-10)
        
        # SANE ADAPTIVE STIFFNESS PARAMETERS
        self.M_factor = min(max(params.get('M_factor', 5000.0), 0), 1e5)  # Base stiffness
        
        # Adaptive parameters - Ecosystem style
        self.velocity_sensitivity = params.get('velocity_sensitivity', 10.0)  # How much speed increases resistance
        self.state_sensitivity = params.get('state_sensitivity', 5.0)        # How much overextension increases resistance
        self.breaking_threshold = params.get('breaking_threshold', 2.0)      # Stress level where constraints break
        self.broken_resistance = params.get('broken_resistance', 0.1)        # Residual resistance after breaking
        self.recovery_rate = params.get('recovery_rate', 0.01)               # How quickly broken constraints heal
        
        self.rho_cutoff = min(max(params.get('rho_cutoff', 0.8), 0), 1)
        self.cubic_damping = max(params.get('cubic_damping', 0.1), 0)
        
        # Fields
        self.rho = np.zeros((grid_size, grid_size))
        self.E = np.zeros((grid_size, grid_size))    
        self.F = np.zeros((grid_size, grid_size))
        
        # Adaptive state tracking - SANE MEMORY SYSTEM
        self.previous_rho = np.zeros((grid_size, grid_size))
        self.broken_regions = np.zeros((grid_size, grid_size), dtype=bool)  # Where constraints are broken
        self.stress_history = np.zeros((grid_size, grid_size))  # Accumulated stress memory
        
        # Stability monitoring
        self.step_count = 0
        self.stability_warnings = 0
        
        self._setup_spectral_operators()
        
        print("🌿 ADAPTIVE UNIVERSAL ENGINE")
        print("Features: Ecosystem stiffness + Adaptive constraints + Breakable limits")
        print(f"Grid: {grid_size}x{grid_size} | dt={dt}")
        print(f"Base M_factor: {self.M_factor} | Breaking threshold: {self.breaking_threshold}")
        print("=" * 50)
    
    def _setup_spectral_operators(self):
        """Setup spectral differentiation"""
        n = self.grid_size
        kx = 2 * np.pi * fftfreq(n, self.dx)
        ky = 2 * np.pi * fftfreq(n, self.dx)
        kx_grid, ky_grid = np.meshgrid(kx, ky, indexing='ij')
        
        self.k_squared = kx_grid**2 + ky_grid**2
        
        # IMEX factors
        max_diffusion = 1.0
        stability_bound = 1.0 + self.dt * max_diffusion * np.max(self.k_squared)
        
        self.implicit_factor_E = 1.0 / stability_bound
        self.implicit_factor_F = 1.0 / stability_bound
    
    def compute_adaptive_stiffness(self, rho):
        """
        SANE ADAPTIVE STIFFNESS - Ecosystem style
        Resistance grows with velocity and state, can break under stress
        """
        # Calculate velocity (how fast system is changing)
        if self.step_count > 0:
            rho_velocity = np.abs(rho - self.previous_rho) / self.dt
        else:
            rho_velocity = np.zeros_like(rho)
        
        # Calculate overextension (how far beyond normal)
        overextension = np.maximum(0, rho - self.rho_cutoff)
        
        # Calculate stress level (combination of velocity and overextension)
        stress_level = (self.velocity_sensitivity * rho_velocity + 
                       self.state_sensitivity * overextension)
        
        # Update broken regions based on stress
        new_breaks = stress_level > self.breaking_threshold
        self.broken_regions = np.logical_or(self.broken_regions, new_breaks)
        
        # Update stress history (ecosystem memory)
        self.stress_history = 0.95 * self.stress_history + 0.05 * stress_level
        
        # SANE ADAPTIVE RESISTANCE CALCULATION
        base_stiffness = 1.0 + self.M_factor * np.tanh(20.0 * overextension)
        
        # Velocity-dependent resistance (faster movement → more resistance)
        velocity_resistance = 1.0 + self.velocity_sensitivity * rho_velocity
        
        # State-dependent resistance (more overextension → more resistance)  
        state_resistance = 1.0 + self.state_sensitivity * overextension
        
        # Combine adaptive factors
        adaptive_factor = velocity_resistance * state_resistance
        
        # Apply breaking: broken regions have much lower resistance
        broken_resistance = np.where(self.broken_regions, self.broken_resistance, 1.0)
        
        # Recovery mechanism: broken regions heal when stress is low
        recovery_conditions = (self.broken_regions & 
                             (self.stress_history < self.breaking_threshold * 0.5))
        self.broken_regions[recovery_conditions] = False
        
        # Final adaptive stiffness
        stiffness_factor = base_stiffness * adaptive_factor * broken_resistance
        
        # Reasonable upper bound
        max_stiffness = 1e4
        stiffness_factor = np.minimum(stiffness_factor, max_stiffness)
        
        return self.alpha * stiffness_factor
    
    def apply_periodic_laplacian_spectral(self, field):
        """Spectral Laplacian"""
        field_hat = fft2(field)
        laplacian_hat = -self.k_squared * field_hat
        return np.real(ifft2(laplacian_hat))
    
    def compute_nonlinear_terms_adaptive(self, rho, E, F):
        """
        Compute nonlinear terms with adaptive stiffness
        """
        laplacian_rho = self.apply_periodic_laplacian_spectral(rho)
        laplacian_E = self.apply_periodic_laplacian_spectral(E)
        laplacian_F = self.apply_periodic_laplacian_spectral(F)
        
        # Use adaptive stiffness instead of rigid stiffness
        alpha_eff = self.compute_adaptive_stiffness(rho)
        
        # ρ evolution with adaptive diffusion
        diffusion_coeff = self.gamma + alpha_eff * F**2
        diffusion_coeff = np.maximum(diffusion_coeff, 0)
        reaction_term = -rho / self.tau_rho
        drho_dt_explicit = diffusion_coeff * laplacian_rho + reaction_term
        
        # E evolution
        dE_dt_explicit = self.beta * F - E / self.tau_E
        
        # F evolution with adaptive source terms
        stiffness_modification = (alpha_eff - self.alpha) * F
        cubic_stabilization = -self.cubic_damping * F**3
        
        source_terms = self.delta1 * rho + self.delta2 * E
        source_terms = np.clip(source_terms, -100, 100)
        
        dF_dt_explicit = (source_terms + laplacian_F - 
                         self.kappa * F - F / self.tau_F +
                         stiffness_modification + cubic_stabilization)
        
        return drho_dt_explicit, dE_dt_explicit, dF_dt_explicit, laplacian_E, laplacian_F
    
    def evolve_adaptive_imex(self):
        """
        Adaptive IMEX integration with ecosystem memory
        """
        # Store previous state for velocity calculation
        self.previous_rho = self.rho.copy()
        
        rho, E, F = self.rho, self.E, self.F
        
        # Get adaptive nonlinear terms
        drho_explicit, dE_explicit, dF_explicit, lap_E, lap_F = self.compute_nonlinear_terms_adaptive(rho, E, F)
        
        # Update ρ with positivity
        rho_new = rho + self.dt * drho_explicit
        rho_new = np.maximum(rho_new, 0.0)
        self.rho = rho_new
        
        # IMEX for E
        E_explicit_part = E + self.dt * dE_explicit
        E_hat = fft2(E_explicit_part)
        E_new_hat = E_hat * self.implicit_factor_E
        self.E = np.real(ifft2(E_new_hat))
        
        # IMEX for F
        F_explicit_part = F + self.dt * dF_explicit
        F_hat = fft2(F_explicit_part)
        F_new_hat = F_hat * self.implicit_factor_F
        self.F = np.real(ifft2(F_new_hat))
        
        # Apply bounds
        self._enforce_adaptive_bounds()
        self.step_count += 1
    
    def _enforce_adaptive_bounds(self):
        """Enforce bounds with adaptive limits"""
        self.rho = np.maximum(self.rho, 0.0)
        
        # Adaptive bounds based on system state
        current_max = np.max(self.rho)
        adaptive_bound = 100.0 * (1.0 + 0.1 * current_max)  # Looser bounds when growing
        
        self.E = np.clip(self.E, -adaptive_bound, adaptive_bound)
        self.F = np.clip(self.F, -adaptive_bound, adaptive_bound)
        
        if (np.any(np.isnan(self.rho)) or np.any(np.isnan(self.E)) or 
            np.any(np.isnan(self.F))):
            self.stability_warnings += 1
            if self.stability_warnings < 3:
                print(f"⚠️  Stability warning at step {self.step_count}")
    
    def initialize_gaussian(self, amplitude=1.0, sigma=0.1):
        """Initialize fields"""
        center = self.grid_size // 2
        x = np.linspace(-self.L/2, self.L/2, self.grid_size, endpoint=False)
        y = np.linspace(-self.L/2, self.L/2, self.grid_size, endpoint=False)
        X, Y = np.meshgrid(x, y, indexing='ij')
        
        r2 = X**2 + Y**2
        self.rho = amplitude * np.exp(-r2 / (2 * sigma**2))
        
        k = 2 * np.pi / self.L
        self.E = 0.01 * np.sin(k * X) * np.cos(k * Y)
        self.F = 0.01 * np.cos(k * X) * np.sin(k * Y)
        
        # Initialize adaptive state
        self.previous_rho = self.rho.copy()
        
        print(f"Initialized: ρ_max={np.max(self.rho):.3f}")
        print(f"Adaptive engine ready - constraints will adapt to system behavior")
    
    def evolve(self, steps=1, verbose=False):
        """Evolve system with adaptive stiffness"""
        for step in range(steps):
            self.evolve_adaptive_imex()
            
            if verbose and steps > 1 and (step % 20 == 0 or step == steps-1):
                rho_max = np.max(self.rho)
                broken_fraction = np.mean(self.broken_regions)
                stress_avg = np.mean(self.stress_history)
                print(f"   Step {step}: ρ_max={rho_max:.3f}, broken={broken_fraction:.3f}, stress={stress_avg:.3f}")
    
    def get_adaptive_statistics(self):
        """Get comprehensive adaptive statistics"""
        return {
            'rho_max': np.max(self.rho),
            'rho_min': np.min(self.rho),
            'rho_rms': np.sqrt(np.mean(self.rho**2)),
            'broken_fraction': np.mean(self.broken_regions),
            'avg_stress': np.mean(self.stress_history),
            'stability_warnings': self.stability_warnings,
            'adaptive_constraints_active': np.max(self.rho) > self.rho_cutoff
        }

# Factory function for adaptive engines
def create_adaptive_engine(domain='general', **kwargs):
    """Create domain-optimized adaptive engines"""
    domain_params = {
        'finance': {
            'M_factor': 3000,
            'velocity_sensitivity': 15.0,  # High velocity sensitivity (fast moves → more resistance)
            'state_sensitivity': 8.0,      # Moderate state sensitivity  
            'breaking_threshold': 1.5,     # Low breaking threshold (markets break easily)
            'broken_resistance': 0.05,     # Very low broken resistance (complete breakdown)
            'cubic_damping': 0.3,
            'dt': 0.001
        },
        'urban': {
            'M_factor': 8000,
            'velocity_sensitivity': 8.0,   # Moderate velocity sensitivity
            'state_sensitivity': 12.0,     # High state sensitivity (infrastructure limits)
            'breaking_threshold': 3.0,     # High breaking threshold (urban systems resilient)
            'broken_resistance': 0.3,      # Moderate broken resistance (partial functionality)
            'cubic_damping': 0.4,
            'dt': 0.001
        },
        'healthcare': {
            'M_factor': 6000,
            'velocity_sensitivity': 12.0,  # High velocity sensitivity (rapid spread → response)
            'state_sensitivity': 10.0,     # High state sensitivity (capacity limits)
            'breaking_threshold': 2.0,     # Medium breaking threshold
            'broken_resistance': 0.2,      # Some residual function when broken
            'cubic_damping': 0.2,
            'dt': 0.001
        },
        'general': {
            'M_factor': 5000,
            'velocity_sensitivity': 10.0,
            'state_sensitivity': 5.0,
            'breaking_threshold': 2.0,
            'broken_resistance': 0.1,
            'cubic_damping': 0.25,
            'dt': 0.001
        }
    }
    
    params = domain_params.get(domain, domain_params['general'])
    params.update(kwargs)
    
    return AdaptiveUniversalEngine(**params)

if __name__ == "__main__":
    print("🌿 TESTING ADAPTIVE SANE UNIVERSAL ENGINE")
    print("Ecosystem-style constraints that adapt, break, and recover")
    print("=" * 60)
    
    # Test all domains
    domains = ['finance', 'urban', 'healthcare']
    
    for domain in domains:
        print(f"\n🔬 Testing {domain} domain:")
        engine = create_adaptive_engine(domain, grid_size=32)
        engine.initialize_gaussian(amplitude=1.0)
        engine.evolve(50, verbose=True)
        
        stats = engine.get_adaptive_statistics()
        print(f"  Final ρ_max: {stats['rho_max']:.3f}")
        print(f"  Broken regions: {stats['broken_fraction']:.3f}")
        print(f"  Average stress: {stats['avg_stress']:.3f}")
        print(f"  Stability warnings: {stats['stability_warnings']}")
        
        if stats['stability_warnings'] == 0 and stats['rho_max'] < 100:
            print("  ✅ SANE AND STABLE")
        else:
            print("  ❌ NEEDS TUNING")
    
    print(f"\n{'='*60}")
    print("🎯 ADAPTIVE SANE MODEL READY!")
    print("Constraints now behave like real ecosystems")
    print("Resistance adapts to velocity and state")
    print("Systems can break and recover realistically")
    print("=" * 60)
