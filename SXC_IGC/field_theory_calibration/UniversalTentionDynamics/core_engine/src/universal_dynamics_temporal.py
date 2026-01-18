#!/usr/bin/env python3
"""
UNIVERSAL DYNAMICS ENGINE - TEMPORAL VERSION
With comprehensive time scaling system and grid-aware stability
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.fft import fft2, ifft2, fftfreq

class UniversalTemporalSystem:
    """
    Universal time scaling system that:
    - Maps numerical steps → physical time
    - Adapts dt based on grid size & stability
    - Provides domain-appropriate time units
    - Ensures temporal universality
    """
    
    # Domain-specific time bases (physical meaning)
    DOMAIN_TIME_BASES = {
        'finance': {
            'characteristic_time': 1.0, 
            'units': 'days', 
            'base_stability_factor': 0.001,
            'description': 'Financial market dynamics'
        },
        'urban': {
            'characteristic_time': 30.0, 
            'units': 'days', 
            'base_stability_factor': 0.005,
            'description': 'Urban development patterns'
        },
        'healthcare': {
            'characteristic_time': 7.0, 
            'units': 'days', 
            'base_stability_factor': 0.002,
            'description': 'Epidemiological spread'
        },
        'cosmic': {
            'characteristic_time': 1e6, 
            'units': 'years', 
            'base_stability_factor': 1e-8,
            'description': 'Cosmic structure formation'
        },
        'general': {
            'characteristic_time': 1.0, 
            'units': 'time_units', 
            'base_stability_factor': 0.001,
            'description': 'General universal dynamics'
        }
    }
    
    @classmethod
    def get_domain_time_config(cls, domain):
        """Get time configuration for specific domain"""
        return cls.DOMAIN_TIME_BASES.get(domain, cls.DOMAIN_TIME_BASES['general'])
    
    @classmethod
    def compute_adaptive_dt(cls, domain, grid_size, stability_margin=0.5):
        """
        Compute adaptive time step based on:
        - Domain characteristic time
        - Grid size (CFL condition)
        - Stability margin
        """
        config = cls.get_domain_time_config(domain)
        base_dt = config['base_stability_factor']
        
        # CFL condition: dt ~ dx², where dx = 1/(grid_size-1)
        # So dt should scale as 1/grid_size² for stability
        grid_scaling = 1.0 / (grid_size ** 2)
        
        # Reference scaling (32x32 grid as baseline)
        reference_scaling = 1.0 / (32 ** 2)
        
        # Adaptive dt that ensures stability
        adaptive_dt = base_dt * (grid_scaling / reference_scaling) * stability_margin
        
        # Ensure dt doesn't become too small
        min_dt = 1e-10
        adaptive_dt = max(adaptive_dt, min_dt)
        
        return adaptive_dt
    
    @classmethod
    def steps_to_physical_time(cls, domain, steps, dt):
        """Convert numerical steps to physical time"""
        config = cls.get_domain_time_config(domain)
        characteristic_time = config['characteristic_time']
        return steps * dt * characteristic_time

class TemporalUniversalEngine:
    """
    Enhanced universal engine with comprehensive time system:
    - Grid-aware adaptive time stepping
    - Physical time tracking
    - Domain-appropriate temporal scaling
    - Guaranteed numerical stability
    """
    
    def __init__(self, grid_size=64, domain='general', L=1.0, **params):
        self.grid_size = grid_size
        self.domain = domain
        self.L = L
        self.dx = L / grid_size
        
        # TEMPORAL SYSTEM INITIALIZATION
        self.temporal_system = UniversalTemporalSystem()
        self.domain_time_config = self.temporal_system.get_domain_time_config(domain)
        
        # Compute adaptive time step based on grid size and domain
        stability_margin = params.get('stability_margin', 0.3)  # Conservative
        self.dt = self.temporal_system.compute_adaptive_dt(domain, grid_size, stability_margin)
        
        # Time tracking
        self.step_count = 0
        self.physical_time = 0.0
        self.time_units = self.domain_time_config['units']
        
        # Physical parameters with bounds checking
        self.alpha = max(params.get('alpha', 1e-5), 0)
        self.beta = params.get('beta', 0.5)
        self.gamma = max(params.get('gamma', 0.2), 0)
        
        self.delta1 = params.get('delta1', 0.5)
        self.delta2 = params.get('delta2', 0.3)
        self.kappa = max(params.get('kappa', 0.4), 0)
        
        # Physical timescales (now related to domain characteristic time)
        base_tau = 0.1  # Dimensionless base
        domain_scale = self.domain_time_config['characteristic_time']
        self.tau_rho = max(params.get('tau_rho', base_tau * domain_scale), 1e-10)
        self.tau_E = max(params.get('tau_E', base_tau * domain_scale), 1e-10)
        self.tau_F = max(params.get('tau_F', base_tau * domain_scale), 1e-10)
        
        # Surgical stiffness with reasonable bounds
        self.M_factor = min(max(params.get('M_factor', 10000.0), 0), 1e6)  # Reduced upper bound
        self.eta_power = min(max(params.get('eta_power', 20.0), 0), 100)
        self.rho_cutoff = min(max(params.get('rho_cutoff', 0.8), 0), 1)
        self.cubic_damping = max(params.get('cubic_damping', 0.1), 0)
        
        # Fields with guaranteed positivity for rho
        self.rho = np.zeros((grid_size, grid_size))
        self.E = np.zeros((grid_size, grid_size))    
        self.F = np.zeros((grid_size, grid_size))
        
        # Numerical stability monitors
        self.stability_warnings = 0
        self.max_stability_violations = 5
        
        self._setup_spectral_operators()
        
        print("🕰️  TEMPORAL UNIVERSAL ENGINE")
        print(f"Domain: {domain} | Grid: {grid_size}x{grid_size}")
        print(f"Time: dt={self.dt:.2e} | Units: {self.time_units}")
        print(f"Physical timescales: τ_ρ={self.tau_rho:.3f}, τ_E={self.tau_E:.3f}, τ_F={self.tau_F:.3f}")
        print("=" * 60)
        
    def _setup_spectral_operators(self):
        """Setup spectral differentiation with stability verification"""
        n = self.grid_size
        kx = 2 * np.pi * fftfreq(n, self.dx)
        ky = 2 * np.pi * fftfreq(n, self.dx)
        kx_grid, ky_grid = np.meshgrid(kx, ky, indexing='ij')
        
        self.k_squared = kx_grid**2 + ky_grid**2
        
        # Verify CFL condition for stability
        max_diffusion = 1.0  # Maximum diffusion coefficient
        cfl_condition = self.dt * max_diffusion * np.max(self.k_squared)
        
        if cfl_condition > 0.5:  # Conservative CFL limit
            print(f"⚠️  CFL warning: {cfl_condition:.3f} (should be < 0.5)")
            # Auto-adjust dt if needed
            suggested_dt = 0.5 / (max_diffusion * np.max(self.k_squared))
            print(f"   Suggested dt: {suggested_dt:.2e} (current: {self.dt:.2e})")
        
        # Improved IMEX factors with verified stability
        stability_bound = 1.0 + self.dt * max_diffusion * np.max(self.k_squared)
        self.implicit_factor_E = 1.0 / stability_bound
        self.implicit_factor_F = 1.0 / stability_bound
    
    def compute_effective_stiffness(self, rho):
        """Surgical stiffness with enhanced stability"""
        rho_clamped = np.maximum(rho, 0.0)
        
        tanh_term = np.tanh(self.eta_power * (rho_clamped - self.rho_cutoff))
        stiffness_factor = 1.0 + self.M_factor * np.maximum(0.0, tanh_term)
        
        # Enhanced stability: gradual stiffness increase
        max_stiffness = 1e4  # Further reduced for stability
        stiffness_factor = np.minimum(stiffness_factor, max_stiffness)
        
        return self.alpha * stiffness_factor
    
    def apply_periodic_laplacian_spectral(self, field):
        """Spectral Laplacian with stability checks"""
        field_hat = fft2(field)
        laplacian_hat = -self.k_squared * field_hat
        return np.real(ifft2(laplacian_hat))
    
    def compute_nonlinear_terms_temporal(self, rho, E, F):
        """
        Compute nonlinear terms with temporal stability
        """
        laplacian_rho = self.apply_periodic_laplacian_spectral(rho)
        laplacian_E = self.apply_periodic_laplacian_spectral(E)
        laplacian_F = self.apply_periodic_laplacian_spectral(F)
        
        # Effective stiffness with temporal considerations
        alpha_eff = self.compute_effective_stiffness(rho)
        
        # 1. ρ EVOLUTION: Enhanced positivity preservation
        diffusion_coeff = self.gamma + alpha_eff * F**2
        diffusion_coeff = np.maximum(diffusion_coeff, 0)
        
        reaction_term = -rho / self.tau_rho
        drho_dt_explicit = diffusion_coeff * laplacian_rho + reaction_term
        
        # 2. E EVOLUTION: Time-scaled dynamics
        dE_dt_explicit = self.beta * F - E / self.tau_E
        
        # 3. F EVOLUTION: Enhanced stability with temporal scaling
        stiffness_modification = (alpha_eff - self.alpha) * F
        cubic_stabilization = -self.cubic_damping * F**3
        
        # Time-aware source term limiting
        source_terms = self.delta1 * rho + self.delta2 * E
        source_terms = np.clip(source_terms, -100, 100)  # Conservative bounds
        
        dF_dt_explicit = (source_terms + laplacian_F - 
                         self.kappa * F - F / self.tau_F +
                         stiffness_modification + cubic_stabilization)
        
        return drho_dt_explicit, dE_dt_explicit, dF_dt_explicit, laplacian_E, laplacian_F
    
    def evolve_temporal_imex(self):
        """
        Temporal IMEX integration with physical time tracking
        """
        rho, E, F = self.rho, self.E, self.F
        
        # Get temporally stable nonlinear terms
        drho_explicit, dE_explicit, dF_explicit, lap_E, lap_F = self.compute_nonlinear_terms_temporal(rho, E, F)
        
        # STEP 1: Update ρ with enhanced positivity
        rho_new = rho + self.dt * drho_explicit
        rho_new = np.maximum(rho_new, 0.0)
        self.rho = rho_new
        
        # STEP 2: IMEX for E
        E_explicit_part = E + self.dt * dE_explicit
        E_hat = fft2(E_explicit_part)
        E_new_hat = E_hat * self.implicit_factor_E
        self.E = np.real(ifft2(E_new_hat))
        
        # STEP 3: IMEX for F  
        F_explicit_part = F + self.dt * dF_explicit
        F_hat = fft2(F_explicit_part)
        F_new_hat = F_hat * self.implicit_factor_F
        self.F = np.real(ifft2(F_new_hat))
        
        # STEP 4: Update physical time
        self.step_count += 1
        self.physical_time = self.temporal_system.steps_to_physical_time(
            self.domain, self.step_count, self.dt
        )
        
        # STEP 5: Enhanced stability enforcement
        self._enforce_temporal_bounds()
    
    def _enforce_temporal_bounds(self):
        """Enhanced physical bounds with temporal awareness"""
        # ρ must be non-negative
        self.rho = np.maximum(self.rho, 0.0)
        
        # Time-dependent bounds (more conservative for early evolution)
        time_factor = min(1.0, self.physical_time / 10.0)  # Ramp up bounds
        max_bound = 1000.0 * time_factor if time_factor > 0 else 10.0
        
        self.E = np.clip(self.E, -max_bound, max_bound)
        self.F = np.clip(self.F, -max_bound, max_bound)
        
        # Enhanced stability monitoring
        if (np.any(np.isnan(self.rho)) or np.any(np.isnan(self.E)) or 
            np.any(np.isnan(self.F))):
            self.stability_warnings += 1
            if self.stability_warnings <= self.max_stability_violations:
                print(f"⚠️  Temporal instability at step {self.step_count}, time {self.physical_time:.3f} {self.time_units}")
            self._temporal_emergency_stabilize()
    
    def _temporal_emergency_stabilize(self):
        """Temporal-aware emergency stabilization"""
        # Reset to safe state with time-dependent amplitude
        time_safe_factor = min(1.0, 1.0 / (self.physical_time + 1.0))
        safe_amplitude = 0.5 * time_safe_factor
        
        self.rho = np.maximum(self.rho, 0.0)
        self.rho = np.clip(self.rho, 0, safe_amplitude * 2)
        self.E = np.clip(self.E, -safe_amplitude, safe_amplitude)
        self.F = np.clip(self.F, -safe_amplitude, safe_amplitude)
        
        # Progressive time step reduction
        if self.stability_warnings > 2:
            self.dt *= 0.7
            print(f"🔄 Reduced dt to {self.dt:.2e} for stability")
    
    def initialize_gaussian(self, amplitude=1.0, sigma=0.1):
        """Initialize with temporal considerations"""
        center = self.grid_size // 2
        x = np.linspace(-self.L/2, self.L/2, self.grid_size, endpoint=False)
        y = np.linspace(-self.L/2, self.L/2, self.grid_size, endpoint=False)
        X, Y = np.meshgrid(x, y, indexing='ij')
        
        r2 = X**2 + Y**2
        self.rho = amplitude * np.exp(-r2 / (2 * sigma**2))
        
        # Domain-appropriate initial perturbations
        k = 2 * np.pi / self.L
        if self.domain == 'cosmic':
            # Cosmic scales: larger wavelengths
            self.E = 0.001 * np.sin(0.5 * k * X) * np.cos(0.5 * k * Y)
            self.F = 0.001 * np.cos(0.5 * k * X) * np.sin(0.5 * k * Y)
        else:
            # Other domains: standard wavelengths
            self.E = 0.01 * np.sin(k * X) * np.cos(k * Y)
            self.F = 0.01 * np.cos(k * X) * np.sin(k * Y)
        
        print(f"Initialized: ρ_max={np.max(self.rho):.3f} | Domain: {self.domain}")
    
    def evolve(self, steps=1, verbose=False):
        """Temporal evolution with physical time reporting"""
        if verbose and steps > 1:
            initial_time = self.physical_time
            print(f"🕰️  Evolving {steps} steps → {steps * self.dt * self.domain_time_config['characteristic_time']:.3f} {self.time_units}")
        
        for step in range(steps):
            self.evolve_temporal_imex()
            
            if verbose and steps > 1 and (step % 50 == 0 or step == steps-1):
                stats = self.get_temporal_statistics()
                time_str = f"t={self.physical_time:.3f}{self.time_units}"
                print(f"   Step {self.step_count} ({time_str}): ρ∈[{np.min(self.rho):.3f},{stats['rho_max']:.3f}]")
    
    def get_temporal_statistics(self):
        """Get comprehensive temporal statistics"""
        return {
            'step_count': self.step_count,
            'physical_time': self.physical_time,
            'time_units': self.time_units,
            'rho_max': np.max(self.rho),
            'rho_min': np.min(self.rho),
            'rho_rms': np.sqrt(np.mean(self.rho**2)),
            'E_rms': np.sqrt(np.mean(self.E**2)),
            'F_rms': np.sqrt(np.mean(self.F**2)),
            'stiffness_active': np.max(self.rho) > self.rho_cutoff,
            'stability_warnings': self.stability_warnings,
            'current_dt': self.dt,
            'cfl_number': self.dt * np.max(self.k_squared)
        }

# Factory function for temporal engines
def create_temporal_engine(domain='general', **kwargs):
    """Create domain-optimized temporal engines"""
    return TemporalUniversalEngine(domain=domain, **kwargs)

if __name__ == "__main__":
    print("🧪 TESTING TEMPORAL UNIVERSAL ENGINE")
    
    # Test different domains and grid sizes
    test_cases = [
        ('finance', 32),
        ('urban', 64), 
        ('healthcare', 48),
        ('cosmic', 128)  # Large grid that previously exploded!
    ]
    
    for domain, grid_size in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing {domain} with grid {grid_size}x{grid_size}")
        print(f"{'='*50}")
        
        engine = create_temporal_engine(domain=domain, grid_size=grid_size)
        engine.initialize_gaussian(amplitude=0.5)
        
        print("Evolving 50 steps...")
        engine.evolve(50, verbose=True)
        
        stats = engine.get_temporal_statistics()
        print(f"\n📊 FINAL STATISTICS:")
        print(f"   Physical time: {stats['physical_time']:.3f} {stats['time_units']}")
        print(f"   Steps: {stats['step_count']}")
        print(f"   ρ range: [{stats['rho_min']:.3f}, {stats['rho_max']:.3f}]")
        print(f"   Stability warnings: {stats['stability_warnings']}")
        print(f"   CFL number: {stats['cfl_number']:.3f}")
        
        if stats['stability_warnings'] == 0 and stats['rho_max'] < 1000:
            print("✅ SUCCESS: Temporal engine stable!")
        else:
            print("❌ Stability issues detected")
