#!/usr/bin/env python3
"""
UNIVERSAL DYNAMICS ENGINE - MONITORED VERSION
Lightweight monitoring: warnings, emergency brakes, hysteresis
No auto-tuning - manual parameter control only
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.fft import fft2, ifft2, fftfreq

class MonitoredUniversalEngine:
    """
    Monitored engine with lightweight diagnostics and safety systems
    """
    
    def __init__(self, grid_size=64, L=1.0, dt=0.0001, **params):
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
        
        # Adaptive parameters - FIXED SCALING FROM BEFORE
        self.M_factor = min(max(params.get('M_factor', 50000.0), 0), 5e5)
        self.velocity_sensitivity = params.get('velocity_sensitivity', 2.0)
        self.state_sensitivity = params.get('state_sensitivity', 2.0)
        self.breaking_threshold = params.get('breaking_threshold', 1.0)
        self.broken_resistance = params.get('broken_resistance', 0.5)
        self.recovery_rate = params.get('recovery_rate', 0.01)
        
        self.rho_cutoff = min(max(params.get('rho_cutoff', 0.8), 0), 1)
        self.cubic_damping = max(params.get('cubic_damping', 0.8), 0)
        
        # Fields
        self.rho = np.zeros((grid_size, grid_size))
        self.E = np.zeros((grid_size, grid_size))    
        self.F = np.zeros((grid_size, grid_size))
        
        # Adaptive state tracking
        self.previous_rho = np.zeros((grid_size, grid_size))
        self.smoothed_velocity = np.zeros((grid_size, grid_size))
        self.broken_regions = np.zeros((grid_size, grid_size), dtype=bool)
        self.stress_history = np.zeros((grid_size, grid_size))
        
        # MONITORING SYSTEM - LIGHTWEIGHT
        self.step_count = 0
        self.stability_warnings = 0
        self.emergency_brakes_applied = 0
        
        # YOUR STATIC HEURISTICS
        self.rho_max_warning_threshold = 1e3    # YOUR: rho_max > 1e3: early warning
        self.rho_max_brake_threshold = 1e5      # YOUR: rho_max > 1e5: emergency brake
        self.broken_frac_brake_threshold = 0.5  # YOUR: broken_frac > 0.5 for >100 steps
        self.p_fail_warning_threshold = 0.2     # YOUR: p_fail mean > 0.2 in quiet periods
        
        # Hysteresis and state tracking
        self.consecutive_high_broken_steps = 0
        self.brake_active = False
        self.brake_delay_counter = 0
        self.quiet_period_steps = 0
        
        self._setup_spectral_operators()
        
        print("🔍 MONITORED UNIVERSAL ENGINE")
        print(f"Grid: {grid_size}x{grid_size} | dt={dt}")
        print("MONITORING: Warnings at 1e3, Brakes at 1e5, Hysteresis active")
        print("NO AUTO-TUNING - Manual parameter control only")
        print("=" * 50)
    
    def _setup_spectral_operators(self):
        """Setup spectral differentiation"""
        n = self.grid_size
        kx = 2 * np.pi * fftfreq(n, self.dx)
        ky = 2 * np.pi * fftfreq(n, self.dx)
        kx_grid, ky_grid = np.meshgrid(kx, ky, indexing='ij')
        
        self.k_squared = kx_grid**2 + ky_grid**2
        
        max_diffusion = 1.0
        stability_bound = 1.0 + self.dt * max_diffusion * np.max(self.k_squared)
        
        self.implicit_factor_E = 1.0 / stability_bound
        self.implicit_factor_F = 1.0 / stability_bound
    
    def _check_monitoring_thresholds(self):
        """
        YOUR STATIC HEURISTICS - Lightweight monitoring only
        """
        current_rho_max = np.max(self.rho)
        current_broken_frac = np.mean(self.broken_regions)
        current_p_fail = np.mean(self.stress_history > self.breaking_threshold)
        
        # YOUR: rho_max > 1e3: early warning
        if current_rho_max > self.rho_max_warning_threshold and not self.brake_active:
            print(f"⚠️  EARLY WARNING: rho_max = {current_rho_max:.1f} > {self.rho_max_warning_threshold}")
        
        # YOUR: rho_max > 1e5: emergency brake
        if current_rho_max > self.rho_max_brake_threshold and not self.brake_active:
            print(f"🚨 EMERGENCY BRAKE: rho_max = {current_rho_max:.1f} > {self.rho_max_brake_threshold}")
            self._apply_emergency_brake()
            return True  # Stop evolution
        
        # YOUR: broken_frac > 0.5 for >100 steps
        if current_broken_frac > self.broken_frac_brake_threshold:
            self.consecutive_high_broken_steps += 1
            if self.consecutive_high_broken_steps > 100 and not self.brake_active:
                print(f"🚨 CONSTRAINT FAILURE: broken_frac = {current_broken_frac:.3f} > {self.broken_frac_brake_threshold} for 100+ steps")
                self._apply_emergency_brake()
                return True
        else:
            self.consecutive_high_broken_steps = 0
        
        # YOUR: p_fail mean > 0.2 in quiet periods (only logs warning)
        if current_p_fail > self.p_fail_warning_threshold:
            self.quiet_period_steps += 1
            if self.quiet_period_steps > 50:  # Consider it a quiet period after 50 steps
                print(f"⚠️  HIGH FAILURE PROBABILITY: p_fail = {current_p_fail:.3f} > {self.p_fail_warning_threshold} in quiet period")
        else:
            self.quiet_period_steps = 0
        
        return False  # Continue evolution
    
    def _apply_emergency_brake(self):
        """Emergency brake with hysteresis - YOUR: delayed re-enable"""
        self.brake_active = True
        self.brake_delay_counter = 200  # YOUR: delay before re-enable
        self.emergency_brakes_applied += 1
        
        # Apply emergency measures
        emergency_reduction = 0.1
        self.rho *= emergency_reduction
        self.E *= emergency_reduction  
        self.F *= emergency_reduction
        
        # Reset broken regions and stress
        self.broken_regions = np.zeros_like(self.broken_regions, dtype=bool)
        self.stress_history = np.zeros_like(self.stress_history)
        
        print(f"🛑 EMERGENCY BRAKE ACTIVE - System stabilized, delay: {self.brake_delay_counter} steps")
    
    def _update_brake_status(self):
        """Update brake status with hysteresis"""
        if self.brake_active:
            self.brake_delay_counter -= 1
            if self.brake_delay_counter <= 0:
                self.brake_active = False
                print("✅ BRAKE RELEASED - System resuming normal operation")
    
    def compute_adaptive_stiffness(self, rho):
        """Fixed adaptive stiffness from previous working version"""
        if self.step_count > 0:
            raw_velocity = np.abs(rho - self.previous_rho) / self.dt
        else:
            raw_velocity = np.zeros_like(rho)
        
        self.smoothed_velocity = (0.9 * self.smoothed_velocity + 0.1 * raw_velocity)
        rho_velocity = self.smoothed_velocity
        
        overextension = np.maximum(0, rho - self.rho_cutoff)
        
        raw_stress = (self.velocity_sensitivity * rho_velocity + 
                     self.state_sensitivity * overextension)
        stress_level = np.minimum(raw_stress, 1.0)
        
        # Only update if not in brake mode
        if not self.brake_active:
            new_breaks = stress_level > self.breaking_threshold
            self.broken_regions = np.logical_or(self.broken_regions, new_breaks)
            
            self.stress_history = 0.95 * self.stress_history + 0.05 * stress_level
            
            # Recovery with hysteresis - YOUR: require stress < threshold * 0.8
            recovery_conditions = (self.broken_regions & 
                                 (self.stress_history < self.breaking_threshold * 0.8))
            self.broken_regions[recovery_conditions] = False
        
        base_stiffness = 1.0 + self.M_factor * np.tanh(20.0 * overextension)
        velocity_resistance = 1.0 + self.velocity_sensitivity * rho_velocity
        state_resistance = 1.0 + self.state_sensitivity * overextension
        adaptive_factor = velocity_resistance * state_resistance
        
        broken_resistance = np.where(self.broken_regions, self.broken_resistance, 1.0)
        
        stiffness_factor = base_stiffness * adaptive_factor * broken_resistance
        max_stiffness = 1e5
        stiffness_factor = np.minimum(stiffness_factor, max_stiffness)
        
        return self.alpha * stiffness_factor
    
    def apply_periodic_laplacian_spectral(self, field):
        """Spectral Laplacian"""
        field_hat = fft2(field)
        laplacian_hat = -self.k_squared * field_hat
        return np.real(ifft2(laplacian_hat))
    
    def compute_nonlinear_terms(self, rho, E, F):
        """Compute nonlinear terms with safety limits"""
        laplacian_rho = self.apply_periodic_laplacian_spectral(rho)
        laplacian_E = self.apply_periodic_laplacian_spectral(E)
        laplacian_F = self.apply_periodic_laplacian_spectral(F)
        
        alpha_eff = self.compute_adaptive_stiffness(rho)
        
        diffusion_coeff = self.gamma + alpha_eff * F**2
        diffusion_coeff = np.maximum(diffusion_coeff, 0)
        reaction_term = -rho / (self.tau_rho * 0.5)
        
        drho_dt_explicit = diffusion_coeff * laplacian_rho + reaction_term
        max_update = 10.0
        drho_dt_explicit = np.clip(drho_dt_explicit, -max_update, max_update)
        
        dE_dt_explicit = self.beta * F - E / self.tau_E
        dE_dt_explicit = np.clip(dE_dt_explicit, -max_update, max_update)
        
        stiffness_modification = (alpha_eff - self.alpha) * F
        cubic_stabilization = -self.cubic_damping * F**3
        
        source_terms = self.delta1 * rho + self.delta2 * E
        source_terms = np.clip(source_terms, -50, 50)
        
        dF_dt_explicit = (source_terms + laplacian_F - 
                         self.kappa * F - F / self.tau_F +
                         stiffness_modification + cubic_stabilization)
        dF_dt_explicit = np.clip(dF_dt_explicit, -max_update, max_update)
        
        return drho_dt_explicit, dE_dt_explicit, dF_dt_explicit, laplacian_E, laplacian_F
    
    def evolve_monitored_imex(self):
        """Monitored IMEX integration with safety systems"""
        # Skip evolution if brake is active
        if self.brake_active:
            self._update_brake_status()
            self.step_count += 1
            return
        
        self.previous_rho = self.rho.copy()
        
        rho, E, F = self.rho, self.E, self.F
        
        drho_explicit, dE_explicit, dF_explicit, lap_E, lap_F = self.compute_nonlinear_terms(rho, E, F)
        
        # Apply updates
        rho_new = rho + self.dt * drho_explicit
        rho_new = np.maximum(rho_new, 0.0)
        
        # YOUR: Check monitoring thresholds BEFORE applying updates
        temp_rho = self.rho.copy()
        self.rho = rho_new  # Temporarily set to check thresholds
        should_brake = self._check_monitoring_thresholds()
        self.rho = temp_rho  # Restore
        
        if should_brake:
            return  # Brake applied, skip this evolution step
        
        # Apply updates if no brake
        self.rho = rho_new
        
        E_explicit_part = E + self.dt * dE_explicit
        E_hat = fft2(E_explicit_part)
        E_new_hat = E_hat * self.implicit_factor_E
        self.E = np.real(ifft2(E_new_hat))
        
        F_explicit_part = F + self.dt * dF_explicit
        F_hat = fft2(F_explicit_part)
        F_new_hat = F_hat * self.implicit_factor_F
        self.F = np.real(ifft2(F_new_hat))
        
        # Final safety check
        self._enforce_safety_bounds()
        self.step_count += 1
    
    def _enforce_safety_bounds(self):
        """Final safety bounds"""
        self.rho = np.maximum(self.rho, 0.0)
        
        # Hard limits
        current_max = np.max(self.rho)
        if current_max > 1e6:  # Nuclear option
            self.rho = self.rho * (1000 / current_max)
            self.E = self.E * 0.01
            self.F = self.F * 0.01
            print("💥 HARD LIMIT ENFORCED - System reset")
        
        self.E = np.clip(self.E, -100, 100)
        self.F = np.clip(self.F, -100, 100)
        
        # Check for numerical errors
        if (np.any(np.isnan(self.rho)) or np.any(np.isnan(self.E)) or 
            np.any(np.isnan(self.F))):
            self.stability_warnings += 1
            print(f"❌ NUMERICAL INSTABILITY at step {self.step_count}")
            self._apply_emergency_brake()
    
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
        
        self.previous_rho = self.rho.copy()
        self.smoothed_velocity = np.zeros_like(self.rho)
        
        print(f"Initialized: ρ_max={np.max(self.rho):.3f}")
        print("Monitoring system active - Manual tuning required")
    
    def evolve(self, steps=1, verbose=False):
        """Evolve system with monitoring"""
        for step in range(steps):
            self.evolve_monitored_imex()
            
            if verbose and steps > 1 and (step % 20 == 0 or step == steps-1):
                rho_max = np.max(self.rho)
                broken_frac = np.mean(self.broken_regions)
                stress_avg = np.mean(self.stress_history)
                brake_status = "BRAKE" if self.brake_active else "RUN"
                print(f"   Step {step} [{brake_status}]: ρ_max={rho_max:.3f}, broken={broken_frac:.3f}")
    
    def get_monitoring_statistics(self):
        """Get comprehensive monitoring statistics"""
        return {
            'rho_max': np.max(self.rho),
            'rho_min': np.min(self.rho),
            'broken_fraction': np.mean(self.broken_regions),
            'avg_stress': np.mean(self.stress_history),
            'stability_warnings': self.stability_warnings,
            'emergency_brakes_applied': self.emergency_brakes_applied,
            'brake_active': self.brake_active,
            'brake_delay_remaining': self.brake_delay_counter,
            'step_count': self.step_count
        }

# Factory function with monitoring
def create_monitored_engine(domain='general', **kwargs):
    """Create domain-optimized monitored engines"""
    domain_params = {
        'finance': {
            'M_factor': 30000,
            'velocity_sensitivity': 2.0,
            'state_sensitivity': 2.0,
            'breaking_threshold': 0.8,
            'broken_resistance': 0.5,
            'cubic_damping': 0.8,
            'dt': 0.0001
        },
        'urban': {
            'M_factor': 80000,
            'velocity_sensitivity': 1.5,
            'state_sensitivity': 2.5,
            'breaking_threshold': 1.2,
            'broken_resistance': 0.6,
            'cubic_damping': 1.0,
            'dt': 0.0001
        },
        'healthcare': {
            'M_factor': 60000,
            'velocity_sensitivity': 2.5,
            'state_sensitivity': 2.0,
            'breaking_threshold': 1.0,
            'broken_resistance': 0.5,
            'cubic_damping': 0.6,
            'dt': 0.0001
        },
        'general': {
            'M_factor': 50000,
            'velocity_sensitivity': 2.0,
            'state_sensitivity': 2.0,
            'breaking_threshold': 1.0,
            'broken_resistance': 0.5,
            'cubic_damping': 0.8,
            'dt': 0.0001
        }
    }
    
    params = domain_params.get(domain, domain_params['general'])
    params.update(kwargs)
    
    return MonitoredUniversalEngine(**params)

if __name__ == "__main__":
    print("🔍 TESTING MONITORED UNIVERSAL ENGINE")
    print("Lightweight monitoring: Warnings at 1e3, Brakes at 1e5, Hysteresis")
    print("NO AUTO-TUNING - Manual parameter control only")
    print("=" * 60)
    
    # Test all domains
    domains = ['finance', 'urban', 'healthcare']
    
    for domain in domains:
        print(f"\n🔬 Testing {domain} domain:")
        engine = create_monitored_engine(domain, grid_size=32)
        engine.initialize_gaussian(amplitude=1.0)
        engine.evolve(100, verbose=True)
        
        stats = engine.get_monitoring_statistics()
        print(f"  Final ρ_max: {stats['rho_max']:.3f}")
        print(f"  Broken regions: {stats['broken_fraction']:.3f}")
        print(f"  Emergency brakes: {stats['emergency_brakes_applied']}")
        print(f"  Stability warnings: {stats['stability_warnings']}")
        
        if stats['emergency_brakes_applied'] == 0 and stats['rho_max'] < 100:
            print("  ✅ STABLE WITH MONITORING")
        elif stats['emergency_brakes_applied'] > 0:
            print("  🛑 BRAKES ACTIVATED - Parameters need tuning")
        else:
            print("  ⚠️  MONITORING ACTIVE - System within bounds")
    
    print(f"\n{'='*60}")
    print("🎯 LIGHTWEIGHT MONITORING ACTIVE!")
    print("Warnings at 1e3, Brakes at 1e5, Hysteresis for recovery")
    print("Manual tuning required - No auto-parameter adjustment")
    print("=" * 60)
