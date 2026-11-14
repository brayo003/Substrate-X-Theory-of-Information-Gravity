#!/usr/bin/env python3
"""
UNIVERSAL NEURAL DYNAMICS - EXCITABLE VERSION
Tuned for neural computation while maintaining universal equations
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.fft import fft2, ifft2, fftfreq

class ExcitableNeuralEngine:
    """
    Universal neural engine tuned for excitability
    Same equations, different parameter regime
    """
    
    def __init__(self, grid_size=64, L=1.0, dt=0.0001, **params):
        self.grid_size = grid_size
        self.L = L
        self.dx = L / grid_size
        self.dt = dt
        
        # NEURAL-TUNED PARAMETERS - SAME EQUATIONS
        self.alpha = max(params.get('alpha', 1e-4), 0)      # Higher sensitivity
        self.beta = params.get('beta', 0.8)                 # Stronger coupling
        self.gamma = max(params.get('gamma', 0.1), 0)       # Less diffusion
        
        # EXCITATION-DOMINANT REGIME
        self.delta1 = params.get('delta1', 1.2)             # Strong excitation
        self.delta2 = params.get('delta2', 0.9)             # Strong coupling
        self.kappa = max(params.get('kappa', 0.3), 0)       # Weaker inhibition
        
        # FASTER DYNAMICS FOR NEURAL RESPONSE
        self.tau_rho = max(params.get('tau_rho', 0.05), 1e-10)  # Faster membrane
        self.tau_E = max(params.get('tau_E', 0.08), 1e-10)      # Faster excitation
        self.tau_F = max(params.get('tau_F', 0.1), 1e-10)       # Slower inhibition
        
        # LOWER THRESHOLDS FOR EXCITABILITY
        self.M_factor = min(max(params.get('M_factor', 10000.0), 0), 1e5)
        self.velocity_sensitivity = params.get('velocity_sensitivity', 5.0)
        self.state_sensitivity = params.get('state_sensitivity', 3.0)
        self.breaking_threshold = params.get('breaking_threshold', 0.3)  # Lower threshold
        self.broken_resistance = params.get('broken_resistance', 0.2)    # Less refractory damping
        self.recovery_rate = params.get('recovery_rate', 0.05)           # Faster recovery
        
        self.rho_cutoff = min(max(params.get('rho_cutoff', 0.4), 0), 1)  # Lower spike threshold
        self.cubic_damping = max(params.get('cubic_damping', 0.1), 0)    # Less damping
        
        # NEURAL AUGMENTATIONS
        self.refractory = np.zeros((grid_size, grid_size), dtype=int)
        self.refractory_period = params.get('refractory_period', 4)
        self.spike_amplitude = params.get('spike_amplitude', 3.0)        # Stronger spikes
        self.resting_potential = params.get('resting_potential', 0.05)   # Higher baseline
        
        # Fields
        self.rho = np.zeros((grid_size, grid_size))
        self.E = np.zeros((grid_size, grid_size))    
        self.F = np.zeros((grid_size, grid_size))
        
        # Adaptive state
        self.previous_rho = np.zeros((grid_size, grid_size))
        self.smoothed_velocity = np.zeros((grid_size, grid_size))
        self.broken_regions = np.zeros((grid_size, grid_size), dtype=bool)
        self.stress_history = np.zeros((grid_size, grid_size))
        
        # Monitoring
        self.step_count = 0
        self.stability_warnings = 0
        self.total_spikes = 0
        self.spike_events = np.zeros((grid_size, grid_size), dtype=bool)
        
        self._setup_spectral_operators()
        
        print("⚡ EXCITABLE NEURAL ENGINE")
        print("Same universal equations - Neural-tuned parameters")
        print(f"Grid: {grid_size}x{grid_size} | dt={dt}")
        print(f"Lower thresholds | Faster dynamics | Stronger excitation")
        print("=" * 50)
    
    def _setup_spectral_operators(self):
        """Same spectral operators"""
        n = self.grid_size
        kx = 2 * np.pi * fftfreq(n, self.dx)
        ky = 2 * np.pi * fftfreq(n, self.dx)
        kx_grid, ky_grid = np.meshgrid(kx, ky, indexing='ij')
        
        self.k_squared = kx_grid**2 + ky_grid**2
        
        max_diffusion = 1.0
        stability_bound = 1.0 + self.dt * max_diffusion * np.max(self.k_squared)
        
        self.implicit_factor_E = 1.0 / stability_bound
        self.implicit_factor_F = 1.0 / stability_bound
    
    def compute_adaptive_stiffness(self, rho):
        """Same function, lower thresholds"""
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
        
        if not np.any(self.refractory > 0):
            new_breaks = stress_level > self.breaking_threshold
            self.broken_regions = np.logical_or(self.broken_regions, new_breaks)
            
            self.stress_history = 0.9 * self.stress_history + 0.1 * stress_level  # Faster learning
            
            recovery_conditions = (self.broken_regions & 
                                 (self.stress_history < self.breaking_threshold * 0.6))
            self.broken_regions[recovery_conditions] = False
        
        base_stiffness = 1.0 + self.M_factor * np.tanh(25.0 * overextension)  # Sharper transition
        velocity_resistance = 1.0 + self.velocity_sensitivity * rho_velocity
        state_resistance = 1.0 + self.state_sensitivity * overextension
        adaptive_factor = velocity_resistance * state_resistance
        
        broken_resistance = np.where(self.broken_regions, self.broken_resistance, 1.0)
        
        stiffness_factor = base_stiffness * adaptive_factor * broken_resistance
        max_stiffness = 1e5
        stiffness_factor = np.minimum(stiffness_factor, max_stiffness)
        
        return self.alpha * stiffness_factor
    
    def apply_periodic_laplacian_spectral(self, field):
        """Same spectral Laplacian"""
        field_hat = fft2(field)
        laplacian_hat = -self.k_squared * field_hat
        return np.real(ifft2(laplacian_hat))
    
    def compute_neural_dynamics(self, rho, E, F):
        """Same equations, neural-tuned parameters"""
        laplacian_rho = self.apply_periodic_laplacian_spectral(rho)
        laplacian_E = self.apply_periodic_laplacian_spectral(E)
        laplacian_F = self.apply_periodic_laplacian_spectral(F)
        
        alpha_eff = self.compute_adaptive_stiffness(rho)
        
        diffusion_coeff = self.gamma + alpha_eff * F**2
        diffusion_coeff = np.maximum(diffusion_coeff, 0)
        
        leak_current = rho / self.tau_rho
        synaptic_input = self.delta1 * rho + self.delta2 * E
        
        drho_dt_explicit = diffusion_coeff * laplacian_rho + synaptic_input - leak_current
        max_update = 25.0  # Higher for more dynamics
        drho_dt_explicit = np.clip(drho_dt_explicit, -max_update, max_update)
        
        dE_dt_explicit = self.beta * F - E / self.tau_E
        dE_dt_explicit = np.clip(dE_dt_explicit, -max_update, max_update)
        
        stiffness_modification = (alpha_eff - self.alpha) * F
        cubic_stabilization = -self.cubic_damping * F**3
        
        source_terms = self.delta1 * rho + self.delta2 * E
        source_terms = np.clip(source_terms, -100, 100)  # Looser bounds
        
        dF_dt_explicit = (source_terms + laplacian_F - 
                         self.kappa * F - F / self.tau_F +
                         stiffness_modification + cubic_stabilization)
        dF_dt_explicit = np.clip(dF_dt_explicit, -max_update, max_update)
        
        return drho_dt_explicit, dE_dt_explicit, dF_dt_explicit, laplacian_E, laplacian_F
    
    def check_spike_thresholds(self):
        """Same spike logic"""
        self.spike_events = np.zeros((self.grid_size, self.grid_size), dtype=bool)
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.refractory[i, j] > 0:
                    self.rho[i, j] = self.resting_potential
                    self.refractory[i, j] -= 1
                elif self.rho[i, j] > self.rho_cutoff:
                    self.spike_events[i, j] = True
                    self.rho[i, j] = self.spike_amplitude
                    self.refractory[i, j] = self.refractory_period
                    self.total_spikes += 1
    
    def evolve_universal_neural(self):
        """Same evolution, faster dynamics"""
        self.previous_rho = self.rho.copy()
        
        rho, E, F = self.rho, self.E, self.F
        
        drho_explicit, dE_explicit, dF_explicit, lap_E, lap_F = self.compute_neural_dynamics(rho, E, F)
        
        rho_new = rho + self.dt * drho_explicit
        rho_new = np.maximum(rho_new, 0.0)
        self.rho = rho_new
        
        E_explicit_part = E + self.dt * dE_explicit
        E_hat = fft2(E_explicit_part)
        E_new_hat = E_hat * self.implicit_factor_E
        self.E = np.real(ifft2(E_new_hat))
        
        F_explicit_part = F + self.dt * dF_explicit
        F_hat = fft2(F_explicit_part)
        F_new_hat = F_hat * self.implicit_factor_F
        self.F = np.real(ifft2(F_new_hat))
        
        self.check_spike_thresholds()
        self._enforce_neural_bounds()
        self.step_count += 1
    
    def _enforce_neural_bounds(self):
        """Looser bounds for neural activity"""
        self.rho = np.maximum(self.rho, 0.0)
        
        current_max = np.max(self.rho)
        if current_max > 5000:  # Higher limit for spikes
            self.rho = self.rho * (1000 / current_max)
        
        self.E = np.clip(self.E, -100, 100)
        self.F = np.clip(self.F, -100, 100)
    
    def stimulate_neurons(self, center, radius, strength=2.0):  # Stronger default
        """Stronger stimulation"""
        stimulus = np.zeros((self.grid_size, self.grid_size))
        
        cx, cy = center
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                distance = np.sqrt((i-cx)**2 + (j-cy)**2)
                if distance <= radius:
                    stimulus[i, j] = strength * (1 - distance/radius)
        
        self.E += stimulus
    
    def get_neural_statistics(self):
        """Same statistics"""
        active_neurons = np.sum(self.spike_events)
        avg_potential = np.mean(self.rho)
        max_potential = np.max(self.rho)
        refractory_neurons = np.sum(self.refractory > 0)
        
        return {
            'step': self.step_count,
            'active_neurons': active_neurons,
            'total_spikes': self.total_spikes,
            'avg_potential': avg_potential,
            'max_potential': max_potential,
            'spike_rate': self.total_spikes / max(1, self.step_count),
            'refractory_neurons': refractory_neurons,
            'avg_stress': np.mean(self.stress_history),
            'plastic_synapses': np.mean(self.broken_regions)
        }

# Test the excitable neural engine
if __name__ == "__main__":
    print("⚡ TESTING EXCITABLE NEURAL ENGINE")
    print("Same universal equations - Neural parameter regime")
    print("=" * 60)
    
    # Test 1: Neural response with stronger stimulation
    print("\n🔬 TEST 1: Neural Response")
    engine1 = ExcitableNeuralEngine(grid_size=32)
    engine1.stimulate_neurons((8, 8), radius=4, strength=3.0)
    
    for step in range(80):
        engine1.evolve_universal_neural()
        
        stats = engine1.get_neural_statistics()
        if step % 15 == 0 or stats['active_neurons'] > 0:
            print(f"  Step {step:3d}: Spikes: {stats['active_neurons']:2d}, "
                  f"Total: {stats['total_spikes']:3d}, "
                  f"Max V: {stats['max_potential']:5.2f}")
    
    # Test 2: Signal propagation
    print("\n🔬 TEST 2: Signal Propagation")
    engine2 = ExcitableNeuralEngine(grid_size=32)
    
    # Strong left-side stimulation
    for i in range(32):
        for j in range(8):
            engine2.E[i, j] = 2.5
    
    propagation = []
    for step in range(100):
        engine2.evolve_universal_neural()
        
        layers = [
            np.sum(engine2.spike_events[:, :8]),
            np.sum(engine2.spike_events[:, 8:16]),
            np.sum(engine2.spike_events[:, 16:24]), 
            np.sum(engine2.spike_events[:, 24:])
        ]
        propagation.append(layers)
        
        if step % 20 == 0:
            print(f"  Step {step:3d}: Layer spikes: {layers}")
    
    # Test 3: Neural plasticity
    print("\n🔬 TEST 3: Neural Plasticity")
    engine3 = ExcitableNeuralEngine(grid_size=24)
    
    initial_plasticity = np.mean(engine3.broken_regions)
    
    for step in range(150):
        if step % 30 < 15:
            engine3.stimulate_neurons((6, 6), radius=3, strength=2.5)
        
        engine3.evolve_universal_neural()
        
        if step % 30 == 0:
            current_plasticity = np.mean(engine3.broken_regions)
            print(f"  Step {step:3d}: Plastic synapses: {current_plasticity:.3f}")
    
    final_plasticity = np.mean(engine3.broken_regions)
    
    print(f"\n📊 EXCITABLE NEURAL RESULTS:")
    print(f"  Test 1 - Total spikes: {engine1.total_spikes}")
    print(f"  Test 2 - Signal reached end: {any(propagation[-1][3] > 0 for p in propagation[-10:])}")
    print(f"  Test 3 - Plasticity change: {final_plasticity - initial_plasticity:+.3f}")
    
    success = (engine1.total_spikes > 0 and 
               any(propagation[-1][3] > 0 for p in propagation[-10:]) and
               abs(final_plasticity - initial_plasticity) > 0.01)
    
    print(f"\n🎯 EXCITABLE REGIME: {'SUCCESS' if success else 'NEEDS MORE TUNING'}")
    print("Same universal equations - Different parameter regime")
    print("=" * 60)
