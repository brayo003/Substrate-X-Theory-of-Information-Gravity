"""
Field-Level Transport Observable Stress Test

This script determines whether the validated modal telegraph discriminant
can be elevated into a mathematically defensible field-level transport observable
for arbitrary evolving fields.
"""

import numpy as np
import json
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class FieldState:
    """Field state for standalone implementation."""
    field_values: np.ndarray
    field_velocity: np.ndarray
    coordinates: np.ndarray
    dx: float
    dy: float
    dz: float
    dt: float
    physical_time: float
    grid_shape: tuple


def initialize_field_state_1d(x_range=(0.0, 25.0), nx=100, initial_value=1.0, dt=0.01):
    """Initialize 1D field state."""
    x = np.linspace(x_range[0], x_range[1], nx)
    dx = (x_range[1] - x_range[0]) / (nx - 1) if nx > 1 else 1.0
    
    coordinates = np.column_stack([x, np.zeros_like(x)])
    
    field_values = np.full(nx, initial_value)
    field_velocity = np.zeros(nx)
    
    return FieldState(
        field_values=field_values,
        field_velocity=field_velocity,
        coordinates=coordinates,
        dx=dx,
        dy=1.0,
        dz=1.0,
        dt=dt,
        physical_time=0.0,
        grid_shape=(nx, 1, 1),
    )


def initialize_field_state_2d(x_range=(0.0, 25.0), y_range=(0.0, 25.0), nx=50, ny=50, initial_value=1.0, dt=0.01):
    """Initialize 2D field state."""
    x = np.linspace(x_range[0], x_range[1], nx)
    y = np.linspace(y_range[0], y_range[1], ny)
    dx = (x_range[1] - x_range[0]) / (nx - 1) if nx > 1 else 1.0
    dy = (y_range[1] - y_range[0]) / (ny - 1) if ny > 1 else 1.0
    
    X, Y = np.meshgrid(x, y, indexing='ij')
    coordinates = np.column_stack([X.ravel(), Y.ravel(), np.zeros(nx * ny)])
    
    field_values = np.full(nx * ny, initial_value)
    field_velocity = np.zeros(nx * ny)
    
    return FieldState(
        field_values=field_values,
        field_velocity=field_velocity,
        coordinates=coordinates,
        dx=dx,
        dy=dy,
        dz=1.0,
        dt=dt,
        physical_time=0.0,
        grid_shape=(nx, ny, 1),
    )


def evolve_field_telegraph_1d(state, c, tau):
    """Evolve field using telegraph equation (1D implementation)."""
    s = state.field_values
    v = state.field_velocity
    dx = state.dx
    dt = state.dt
    
    laplacian = np.zeros_like(s)
    if len(s) > 2:
        laplacian[1:-1] = (s[2:] - 2*s[1:-1] + s[:-2]) / (dx**2)
    
    acceleration = (c**2) * laplacian - v / tau
    v_new = v + dt * acceleration
    s_new = s + dt * v_new
    
    return FieldState(
        s_new, v_new, state.coordinates,
        dx, state.dy, state.dz, dt,
        state.physical_time + dt, state.grid_shape
    )


def evolve_field_telegraph_2d(state, c, tau):
    """Evolve field using telegraph equation (2D implementation)."""
    s = state.field_values.reshape(state.grid_shape)
    v = state.field_velocity.reshape(state.grid_shape)
    dx, dy = state.dx, state.dy
    dt = state.dt
    
    laplacian = np.zeros_like(s)
    if s.shape[0] > 2:
        laplacian[1:-1, :, 0] = (s[2:, :, 0] - 2*s[1:-1, :, 0] + s[:-2, :, 0]) / (dx**2)
    if s.shape[1] > 2:
        laplacian[:, 1:-1, 0] = (s[:, 2:, 0] - 2*s[:, 1:-1, 0] + s[:, :-2, 0]) / (dy**2)
    
    acceleration = (c**2) * laplacian - v / tau
    v_new = v + dt * acceleration
    s_new = s + dt * v_new
    
    return FieldState(
        s_new.ravel(), v_new.ravel(), state.coordinates,
        dx, dy, state.dz, dt,
        state.physical_time + dt, state.grid_shape
    )


class FieldLevelTransportStressTest:
    """Comprehensive stress test for field-level transport observables."""
    
    def __init__(self):
        self.results = {
            'test_date': '2026-08-09',
            'telegraph_equation': 'τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s',
            'modal_discriminant': 'D(k) = 4c²τ²k² - 1',
            'phases': {},
            'conclusion': None,
        }
    
    def compute_modal_discriminant(self, c, tau, k):
        """Compute exact modal discriminant."""
        return 4 * c**2 * tau**2 * k**2 - 1
    
    def compute_modal_regime(self, c, tau, k):
        """Compute modal regime from discriminant."""
        D = self.compute_modal_discriminant(c, tau, k)
        if D > 0:
            return "coherent"
        elif D < 0:
            return "overdamped"
        else:
            return "critical"
    
    def compute_spectrum_1d(self, field):
        """Compute 1D spatial spectrum."""
        s = field.field_values
        L = field.coordinates[-1, 0] - field.coordinates[0, 0]
        
        s_k = np.fft.fft(s)
        power_spectrum = np.abs(s_k)**2
        k_values = 2 * np.pi * np.fft.fftfreq(len(s), d=field.dx)
        
        return {
            'power_spectrum': power_spectrum,
            'k_values': k_values,
            'L': L,
        }
    
    def compute_spectrum_2d(self, field):
        """Compute 2D spatial spectrum."""
        s = field.field_values.reshape(field.grid_shape)
        Lx = field.coordinates[-1, 0] - field.coordinates[0, 0]
        Ly = field.coordinates[np.prod(field.grid_shape)//2, 1] - field.coordinates[0, 1]
        
        s_k = np.fft.fft2(s)
        power_spectrum = np.abs(s_k)**2
        
        kx_values = 2 * np.pi * np.fft.fftfreq(field.grid_shape[0], d=field.dx)
        ky_values = 2 * np.pi * np.fft.fftfreq(field.grid_shape[1], d=field.dy)
        
        return {
            'power_spectrum': power_spectrum,
            'kx_values': kx_values,
            'ky_values': ky_values,
            'Lx': Lx,
            'Ly': Ly,
        }
    
    def compute_dominant_mode_1d(self, field):
        """Compute dominant mode wavenumber in 1D."""
        spectrum = self.compute_spectrum_1d(field)
        power_spectrum = spectrum['power_spectrum']
        k_values = spectrum['k_values']
        
        # Exclude DC component
        power_spectrum_copy = power_spectrum.copy()
        power_spectrum_copy[0] = 0
        
        k_idx = np.argmax(power_spectrum_copy)
        k_dominant = abs(k_values[k_idx])
        
        return k_dominant
    
    def compute_dominant_mode_2d(self, field):
        """Compute dominant mode wavevector magnitude in 2D."""
        spectrum = self.compute_spectrum_2d(field)
        power_spectrum = spectrum['power_spectrum']
        kx_values = spectrum['kx_values']
        ky_values = spectrum['ky_values']
        
        # Exclude DC component
        power_spectrum_copy = power_spectrum.copy()
        power_spectrum_copy[0, 0] = 0
        
        k_idx = np.unravel_index(np.argmax(power_spectrum_copy), power_spectrum.shape)
        kx_dominant = kx_values[k_idx[0]]
        ky_dominant = ky_values[k_idx[1]]
        k_dominant = np.sqrt(kx_dominant**2 + ky_dominant**2)
        
        return k_dominant
    
    def compute_spectral_transport_metrics_1d(self, field, c, tau):
        """Compute comprehensive spectral transport metrics for 1D field."""
        spectrum = self.compute_spectrum_1d(field)
        power_spectrum = spectrum['power_spectrum']
        k_values = spectrum['k_values']
        
        # Compute discriminant for each k
        discriminants = 4 * c**2 * tau**2 * k_values**2 - 1
        
        # Classification
        coherent_mask = discriminants > 0
        overdamped_mask = discriminants < 0
        critical_mask = discriminants == 0
        
        # Power fractions
        total_power = np.sum(power_spectrum)
        if total_power > 0:
            f_prop = np.sum(power_spectrum[coherent_mask]) / total_power
            f_over = np.sum(power_spectrum[overdamped_mask]) / total_power
            f_crit = np.sum(power_spectrum[critical_mask]) / total_power
        else:
            f_prop = f_over = f_crit = 0.0
        
        # Weighted discriminant
        if total_power > 0:
            D_weighted = np.sum(power_spectrum * discriminants) / total_power
        else:
            D_weighted = -1.0
        
        # Dominant mode
        k_dominant = self.compute_dominant_mode_1d(field)
        D_dominant = 4 * c**2 * tau**2 * k_dominant**2 - 1
        
        # Spectral entropy
        if total_power > 0:
            power_normalized = power_spectrum / total_power
            power_normalized = power_normalized[power_normalized > 0]
            spectral_entropy = -np.sum(power_normalized * np.log(power_normalized))
        else:
            spectral_entropy = 0.0
        
        return {
            'k_dominant': k_dominant,
            'D_dominant': D_dominant,
            'f_prop': f_prop,
            'f_over': f_over,
            'f_crit': f_crit,
            'D_weighted': D_weighted,
            'spectral_entropy': spectral_entropy,
        }
    
    def initialize_multimode_field_1d(self, modes, c, tau, nx, dt):
        """Initialize 1D field with multiple Fourier modes."""
        L = 5 * max([2 * np.pi / k for k, A, omega in modes])
        x_range = (0.0, L)
        
        state = initialize_field_state_1d(x_range=x_range, nx=nx, initial_value=1.0, dt=dt)
        
        x_coords = state.coordinates[:, 0]
        s_values = np.ones_like(x_coords)
        v_values = np.zeros_like(x_coords)
        
        for k, A, omega in modes:
            s_values += A * np.cos(k * x_coords)
            v_values += A * (-1.0/(2*tau) * np.cos(k * x_coords) + omega * np.sin(k * x_coords))
        
        state.field_values = s_values
        state.field_velocity = v_values
        
        return state, L
    
    def run_phase_1_modal_baseline(self):
        """PHASE 1: Reproduce modal baseline."""
        print("="*80)
        print("PHASE 1: MODAL BASELINE")
        print("="*80)
        
        c, tau = 1.0, 1.0
        k_values = [0.25, 0.40, 0.50, 0.60, 0.75, 1.00, 1.2566]
        k_c = 1.0 / (2 * c * tau)
        
        results = []
        
        for k in k_values:
            true_regime = self.compute_modal_regime(c, tau, k)
            D = self.compute_modal_discriminant(c, tau, k)
            
            results.append({
                'k': k,
                'true_regime': true_regime,
                'D': D,
            })
        
        print(f"Critical wavenumber k_c = {k_c:.4f} rad/m")
        for r in results:
            print(f"k={r['k']:.4f}: {r['true_regime']}, D={r['D']:.4f}")
        
        self.results['phases']['phase_1'] = results
        return results
    
    def run_phase_2_amplitude_invariance(self):
        """PHASE 2: Amplitude invariance."""
        print("\n" + "="*80)
        print("PHASE 2: AMPLITUDE INVARIANCE")
        print("="*80)
        
        c, tau, s0 = 1.0, 1.0, 1.0
        k_values = [0.25, 0.40, 0.50, 0.60, 0.75, 1.00, 1.2566]
        amplitudes = [0.01, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80]
        
        results = []
        
        for k in k_values:
            true_regime = self.compute_modal_regime(c, tau, k)
            
            for A in amplitudes:
                wavelength = 2 * np.pi / k
                nx = int(5 * wavelength * 20) + 1
                
                state, L = self.initialize_multimode_field_1d([(k, A, 0)], c, tau, nx, 0.01)
                
                # Evolve briefly
                for _ in range(10):
                    state = evolve_field_telegraph_1d(state, c, tau)
                
                # Compute spectral metrics
                metrics = self.compute_spectral_transport_metrics_1d(state, c, tau)
                
                results.append({
                    'k': k,
                    'A': A,
                    'true_regime': true_regime,
                    'k_dominant': metrics['k_dominant'],
                    'D_dominant': metrics['D_dominant'],
                    'f_prop': metrics['f_prop'],
                    'f_over': metrics['f_over'],
                })
        
        # Analyze amplitude dependence
        amplitude_independent = True
        for k in k_values:
            k_results = [r for r in results if r['k'] == k]
            if len(k_results) > 1:
                first_regime = "coherent" if k_results[0]['D_dominant'] > 0 else "overdamped"
                for r in k_results:
                    current_regime = "coherent" if r['D_dominant'] > 0 else "overdamped"
                    if current_regime != first_regime:
                        amplitude_independent = False
                        break
        
        print(f"Amplitude independence: {amplitude_independent}")
        
        self.results['phases']['phase_2'] = {
            'results': results,
            'amplitude_independent': amplitude_independent,
        }
        
        return results
    
    def run_phase_3_two_mode_mixtures(self):
        """PHASE 3: Two-mode mixtures."""
        print("\n" + "="*80)
        print("PHASE 3: TWO-MODE MIXTURES")
        print("="*80)
        
        c, tau = 1.0, 1.0
        k1, k2 = 0.25, 0.75  # One overdamped, one coherent
        
        results = []
        
        # Test different amplitude ratios
        amplitude_ratios = [
            (0.8, 0.2),  # Dominant overdamped
            (0.5, 0.5),  # Equal
            (0.2, 0.8),  # Dominant coherent
        ]
        
        for A1, A2 in amplitude_ratios:
            omega1 = 0.0  # Overdamped
            omega2 = np.sqrt(c**2 * k2**2 - 1.0/(4*tau**2))  # Coherent
            
            modes = [(k1, A1, omega1), (k2, A2, omega2)]
            
            wavelength_min = min([2 * np.pi / k for k, A, omega in modes])
            nx = int(5 * (2 * np.pi / wavelength_min) * 20) + 1
            
            state, L = self.initialize_multimode_field_1d(modes, c, tau, nx, 0.01)
            
            # Evolve briefly
            for _ in range(10):
                state = evolve_field_telegraph_1d(state, c, tau)
            
            # Compute spectral metrics
            metrics = self.compute_spectral_transport_metrics_1d(state, c, tau)
            
            # True modal classification
            true_regime1 = self.compute_modal_regime(c, tau, k1)
            true_regime2 = self.compute_modal_regime(c, tau, k2)
            
            results.append({
                'A1': A1,
                'A2': A2,
                'true_regime1': true_regime1,
                'true_regime2': true_regime2,
                'k_dominant': metrics['k_dominant'],
                'D_dominant': metrics['D_dominant'],
                'f_prop': metrics['f_prop'],
                'f_over': metrics['f_over'],
            })
        
        for r in results:
            print(f"A1={r['A1']:.2f}, A2={r['A2']:.2f}: k_dom={r['k_dominant']:.4f}, f_prop={r['f_prop']:.3f}")
        
        self.results['phases']['phase_3'] = results
        return results
    
    def run_phase_4_multimode_spectra(self):
        """PHASE 4: Multimode spectra."""
        print("\n" + "="*80)
        print("PHASE 4: MULTIMODE SPECTRA")
        print("="*80)
        
        c, tau = 1.0, 1.0
        
        # Create 5-mode mixture spanning both regimes
        k_values = [0.25, 0.40, 0.50, 0.75, 1.00]
        amplitudes = [0.2, 0.3, 0.4, 0.5, 0.6]
        
        modes = []
        for k, A in zip(k_values, amplitudes):
            if c**2 * k**2 > 1.0/(4*tau**2):
                omega = np.sqrt(c**2 * k**2 - 1.0/(4*tau**2))
            else:
                omega = 0.0
            modes.append((k, A, omega))
        
        wavelength_min = min([2 * np.pi / k for k, A, omega in modes])
        nx = int(5 * (2 * np.pi / wavelength_min) * 20) + 1
        
        state, L = self.initialize_multimode_field_1d(modes, c, tau, nx, 0.01)
        
        # Evolve briefly
        for _ in range(10):
            state = evolve_field_telegraph_1d(state, c, tau)
        
        # Compute spectral metrics
        metrics = self.compute_spectral_transport_metrics_1d(state, c, tau)
        
        # True modal classifications
        true_regimes = [self.compute_modal_regime(c, tau, k) for k in k_values]
        
        print(f"Dominant k: {metrics['k_dominant']:.4f}")
        print(f"Dominant D: {metrics['D_dominant']:.4f}")
        print(f"Propagating power fraction: {metrics['f_prop']:.3f}")
        print(f"Overdamped power fraction: {metrics['f_over']:.3f}")
        print(f"Weighted D: {metrics['D_weighted']:.4f}")
        print(f"Spectral entropy: {metrics['spectral_entropy']:.3f}")
        print(f"True modal regimes: {true_regimes}")
        
        result = {
            'modes': modes,
            'true_regimes': true_regimes,
            'metrics': metrics,
        }
        
        self.results['phases']['phase_4'] = result
        return result
    
    def run_phase_5_2d_generalization(self):
        """PHASE 5: 2D generalization."""
        print("\n" + "="*80)
        print("PHASE 5: 2D GENERALIZATION")
        print("="*80)
        
        c, tau = 1.0, 1.0
        
        # Test single 2D mode with clear propagating regime
        kx, ky = 0.3, 0.0  # Coherent regime
        k_mag = np.sqrt(kx**2 + ky**2)
        
        nx, ny = 60, 40
        state = initialize_field_state_2d(
            x_range=(0.0, 20.0), y_range=(0.0, 10.0),
            nx=nx, ny=ny, initial_value=1.0, dt=0.01
        )
        
        # Initialize with 2D plane wave
        X = state.coordinates[:, 0].reshape(nx, ny)
        Y = state.coordinates[:, 1].reshape(nx, ny)
        A = 0.5
        
        # Calculate correct omega for this c, tau
        if c**2 * k_mag**2 > 1.0/(4*tau**2):
            omega = np.sqrt(c**2 * k_mag**2 - 1.0/(4*tau**2))
        else:
            omega = 0.0
        
        s_values = 1.0 + A * np.cos(kx * X + ky * Y)
        state.field_values = s_values.ravel()
        
        # Initialize velocity
        v_values = A * (-1.0/(2*tau) * np.cos(kx * X + ky * Y) + omega * np.sin(kx * X + ky * Y))
        state.field_velocity = v_values.ravel()
        
        # Evolve briefly
        for _ in range(10):
            state = evolve_field_telegraph_2d(state, c, tau)
        
        # Compute dominant mode
        k_dominant = self.compute_dominant_mode_2d(state)
        D_dominant = 4 * c**2 * tau**2 * k_dominant**2 - 1
        
        true_regime = self.compute_modal_regime(c, tau, k_mag)
        dominant_regime = "coherent" if D_dominant > 0 else "overdamped"
        
        print(f"True |k|: {k_mag:.4f}, True regime: {true_regime}")
        print(f"Measured |k|: {k_dominant:.4f}, Measured regime: {dominant_regime}")
        
        result = {
            'k_mag': k_mag,
            'true_regime': true_regime,
            'k_dominant': k_dominant,
            'D_dominant': D_dominant,
            'dominant_regime': dominant_regime,
            'agreement': (true_regime == dominant_regime),
        }
        
        self.results['phases']['phase_5'] = result
        return result
    
    def run_phase_6_noise_robustness(self):
        """PHASE 6: Noise robustness."""
        print("\n" + "="*80)
        print("PHASE 6: NOISE ROBUSTNESS")
        print("="*80)
        
        c, tau = 1.0, 1.0
        k, A = 0.75, 0.5
        
        snr_values = [40, 20, 10, 5]  # dB
        
        results = []
        
        for snr_db in snr_values:
            wavelength = 2 * np.pi / k
            nx = int(5 * wavelength * 20) + 1
            
            # Calculate correct omega for this c, tau
            if c**2 * k**2 > 1.0/(4*tau**2):
                omega = np.sqrt(c**2 * k**2 - 1.0/(4*tau**2))
            else:
                omega = 0.0
            
            state, L = self.initialize_multimode_field_1d([(k, A, omega)], c, tau, nx, 0.01)
            
            # Add noise
            signal_power = np.var(state.field_values)
            noise_power = signal_power / (10**(snr_db/10))
            noise = np.random.normal(0, np.sqrt(noise_power), len(state.field_values))
            state.field_values += noise
            
            # Evolve briefly
            for _ in range(10):
                state = evolve_field_telegraph_1d(state, c, tau)
            
            # Compute spectral metrics
            metrics = self.compute_spectral_transport_metrics_1d(state, c, tau)
            
            results.append({
                'snr_db': snr_db,
                'k_dominant': metrics['k_dominant'],
                'D_dominant': metrics['D_dominant'],
                'spectral_entropy': metrics['spectral_entropy'],
            })
        
        for r in results:
            print(f"SNR={r['snr_db']}dB: k_dom={r['k_dominant']:.4f}, D_dom={r['D_dominant']:.4f}")
        
        self.results['phases']['phase_6'] = results
        return results
    
    def run_phase_7_resolution_convergence(self):
        """PHASE 7: Resolution convergence."""
        print("\n" + "="*80)
        print("PHASE 7: RESOLUTION CONVERGENCE")
        print("="*80)
        
        c, tau, k, A = 1.0, 1.0, 0.75, 0.5
        resolution_factors = [10, 20, 40, 80]
        
        results = []
        
        for res_factor in resolution_factors:
            wavelength = 2 * np.pi / k
            nx = int(5 * wavelength * res_factor) + 1
            
            # Calculate correct omega for this c, tau
            if c**2 * k**2 > 1.0/(4*tau**2):
                omega = np.sqrt(c**2 * k**2 - 1.0/(4*tau**2))
            else:
                omega = 0.0
            
            state, L = self.initialize_multimode_field_1d([(k, A, omega)], c, tau, nx, 0.01)
            
            # Evolve briefly
            for _ in range(10):
                state = evolve_field_telegraph_1d(state, c, tau)
            
            # Compute spectral metrics
            metrics = self.compute_spectral_transport_metrics_1d(state, c, tau)
            
            results.append({
                'resolution_factor': res_factor,
                'k_dominant': metrics['k_dominant'],
                'D_dominant': metrics['D_dominant'],
            })
        
        # Analyze convergence
        k_dominants = [r['k_dominant'] for r in results]
        k_std = np.std(k_dominants)
        
        print(f"k_dominant std: {k_std:.6f}")
        
        self.results['phases']['phase_7'] = {
            'results': results,
            'k_std': k_std,
        }
        
        return results
    
    def run_phase_8_parameter_sweep(self):
        """PHASE 8: c and τ parameter sweep."""
        print("\n" + "="*80)
        print("PHASE 8: PARAMETER SWEEP")
        print("="*80)
        
        c_values = [0.5, 1.0, 2.0]
        tau_values = [0.5, 1.0, 2.0]
        
        results = []
        
        for c in c_values:
            for tau in tau_values:
                k_c = 1.0 / (2 * c * tau)
                
                # Test a mode that should be propagating for this (c, τ)
                k_test = 2.0 * k_c  # Twice the critical wavenumber
                true_regime = self.compute_modal_regime(c, tau, k_test)
                
                # Calculate correct omega for this c, tau
                if c**2 * k_test**2 > 1.0/(4*tau**2):
                    omega = np.sqrt(c**2 * k_test**2 - 1.0/(4*tau**2))
                else:
                    omega = 0.0
                
                wavelength = 2 * np.pi / k_test
                nx = int(5 * wavelength * 20) + 1
                
                state, L = self.initialize_multimode_field_1d([(k_test, 0.5, omega)], c, tau, nx, 0.01)
                
                # Evolve briefly
                for _ in range(10):
                    state = evolve_field_telegraph_1d(state, c, tau)
                
                # Compute spectral metrics
                metrics = self.compute_spectral_transport_metrics_1d(state, c, tau)
                
                results.append({
                    'c': c,
                    'tau': tau,
                    'k_c': k_c,
                    'k_test': k_test,
                    'true_regime': true_regime,
                    'k_dominant': metrics['k_dominant'],
                    'D_dominant': metrics['D_dominant'],
                })
        
        for r in results:
            print(f"c={r['c']}, τ={r['tau']}: k_c={r['k_c']:.4f}, k_test={r['k_test']:.4f}, k_dom={r['k_dominant']:.4f}")
        
        self.results['phases']['phase_8'] = results
        return results
    
    def compute_scientific_decision(self):
        """Compute final scientific decision."""
        print("\n" + "="*80)
        print("SCIENTIFIC DECISION ANALYSIS")
        print("="*80)
        
        # Analyze each phase
        phase_2 = self.results['phases']['phase_2']
        phase_3 = self.results['phases']['phase_3']
        phase_4 = self.results['phases']['phase_4']
        phase_5 = self.results['phases']['phase_5']
        phase_6 = self.results['phases']['phase_6']
        phase_7 = self.results['phases']['phase_7']
        phase_8 = self.results['phases']['phase_8']
        
        # Decision criteria
        criteria = {
            'amplitude_independence': phase_2['amplitude_independent'],
            'two_mode_stability': True,  # Will analyze
            'multimode_meaningful': True,  # Will analyze
            '2d_validity': phase_5['agreement'],
            'noise_robustness': True,  # Will analyze
            'resolution_convergence': phase_7['k_std'] < 0.01,
            'parameter_validity': True,  # Will analyze
        }
        
        # Analyze two-mode stability
        two_mode_dominant_correct = 0
        for r in phase_3:
            # Check if dominant mode correctly reflects the regime
            if r['A1'] > r['A2']:  # Overdamped dominant
                if r['D_dominant'] < 0:
                    two_mode_dominant_correct += 1
            else:  # Coherent dominant
                if r['D_dominant'] > 0:
                    two_mode_dominant_correct += 1
        
        criteria['two_mode_stability'] = two_mode_dominant_correct / len(phase_3) > 0.5
        
        # Analyze multimode meaningfulness
        metrics = phase_4['metrics']
        # Check if spectral metrics provide meaningful information
        criteria['multimode_meaningful'] = (0 < metrics['f_prop'] < 1 and 0 < metrics['f_over'] < 1)
        
        # Analyze noise robustness
        high_snr_k = phase_6[0]['k_dominant']
        low_snr_k = phase_6[-1]['k_dominant']
        criteria['noise_robustness'] = abs(high_snr_k - low_snr_k) / high_snr_k < 0.1
        
        # Analyze parameter validity
        parameter_correct = sum(1 for r in phase_8 if abs(r['k_dominant'] - r['k_test']) / r['k_test'] < 0.1)
        criteria['parameter_validity'] = parameter_correct / len(phase_8) > 0.8
        
        print("Criteria:")
        for criterion, value in criteria.items():
            print(f"  {criterion}: {value}")
        
        # Decision
        passed_criteria = sum(1 for v in criteria.values() if v)
        total_criteria = len(criteria)
        
        if passed_criteria >= total_criteria - 1:
            if criteria['multimode_meaningful']:
                conclusion = "CASE_B: STRUCTURED SPECTRAL OBSERVABLE REQUIRED"
            else:
                conclusion = "CASE_A: SINGLE SCALAR JUSTIFIED"
        elif passed_criteria >= total_criteria - 2:
            conclusion = "CASE_B: STRUCTURED SPECTRAL OBSERVABLE REQUIRED"
        else:
            conclusion = "CASE_C: SPECTRAL REPRESENTATION FAILS"
        
        print(f"\nPassed: {passed_criteria}/{total_criteria}")
        print(f"FINAL CONCLUSION: {conclusion}")
        
        self.results['conclusion'] = conclusion
        self.results['criteria'] = criteria
        
        return conclusion
    
    def save_results(self):
        """Save stress test results."""
        
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            else:
                return obj
        
        results_serializable = convert_numpy_types(self.results)
        
        # Save JSON
        json_path = '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/q_capability_experiment/FIELD_LEVEL_TRANSPORT_STRESS_TEST_RESULTS.json'
        with open(json_path, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        print(f"\nJSON results saved to: {json_path}")
        
        # Save markdown report
        md_path = '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/q_capability_experiment/FIELD_LEVEL_TRANSPORT_STRESS_TEST_RESULTS.md'
        
        with open(md_path, 'w') as f:
            f.write("# Field-Level Transport Stress Test Results\n\n")
            f.write(f"**Test Date:** {results_serializable['test_date']}\n\n")
            f.write(f"**Telegraph Equation:** {results_serializable['telegraph_equation']}\n\n")
            f.write(f"**Modal Discriminant:** {results_serializable['modal_discriminant']}\n\n")
            f.write(f"**Conclusion:** {results_serializable['conclusion']}\n\n")
            f.write("---\n\n")
            
            f.write("## Phase Results\n\n")
            
            f.write("### Phase 1: Modal Baseline\n\n")
            for r in results_serializable['phases']['phase_1']:
                f.write(f"- k={r['k']:.4f}: {r['true_regime']}, D={r['D']:.4f}\n")
            
            f.write("\n### Phase 2: Amplitude Invariance\n\n")
            f.write(f"Amplitude independent: {results_serializable['phases']['phase_2']['amplitude_independent']}\n")
            
            f.write("\n### Phase 3: Two-Mode Mixtures\n\n")
            for r in results_serializable['phases']['phase_3']:
                f.write(f"- A1={r['A1']:.2f}, A2={r['A2']:.2f}: k_dom={r['k_dominant']:.4f}, f_prop={r['f_prop']:.3f}\n")
            
            f.write("\n### Phase 4: Multimode Spectra\n\n")
            metrics = results_serializable['phases']['phase_4']['metrics']
            f.write(f"- Dominant k: {metrics['k_dominant']:.4f}\n")
            f.write(f"- Propagating power fraction: {metrics['f_prop']:.3f}\n")
            f.write(f"- Overdamped power fraction: {metrics['f_over']:.3f}\n")
            f.write(f"- Weighted D: {metrics['D_weighted']:.4f}\n")
            f.write(f"- Spectral entropy: {metrics['spectral_entropy']:.3f}\n")
            
            f.write("\n### Phase 5: 2D Generalization\n\n")
            f.write(f"Agreement: {results_serializable['phases']['phase_5']['agreement']}\n")
            
            f.write("\n### Phase 6: Noise Robustness\n\n")
            for r in results_serializable['phases']['phase_6']:
                f.write(f"- SNR={r['snr_db']}dB: k_dom={r['k_dominant']:.4f}\n")
            
            f.write("\n### Phase 7: Resolution Convergence\n\n")
            f.write(f"k_dominant std: {results_serializable['phases']['phase_7']['k_std']:.6f}\n")
            
            f.write("\n### Phase 8: Parameter Sweep\n\n")
            for r in results_serializable['phases']['phase_8']:
                f.write(f"- c={r['c']}, τ={r['tau']}: k_dom={r['k_dominant']:.4f}\n")
            
            f.write("\n## Decision Criteria\n\n")
            for criterion, value in results_serializable['criteria'].items():
                f.write(f"- {criterion}: {value}\n")
            
            f.write("\n---\n\n")
            f.write("## Final Decision\n\n")
            f.write(f"**{results_serializable['conclusion']}**\n\n")
        
        print(f"Markdown report saved to: {md_path}")
        
        return results_serializable


def main():
    """Run field-level transport stress test."""
    print("="*80)
    print("FIELD-LEVEL TRANSPORT OBSERVABLE STRESS TEST")
    print("Validating spectral observables for field-level transport classification")
    print("="*80)
    
    test = FieldLevelTransportStressTest()
    
    # Run all phases
    test.run_phase_1_modal_baseline()
    test.run_phase_2_amplitude_invariance()
    test.run_phase_3_two_mode_mixtures()
    test.run_phase_4_multimode_spectra()
    test.run_phase_5_2d_generalization()
    test.run_phase_6_noise_robustness()
    test.run_phase_7_resolution_convergence()
    test.run_phase_8_parameter_sweep()
    
    # Compute decision
    print("\nComputing scientific decision...")
    conclusion = test.compute_scientific_decision()
    
    # Save results
    print("\nSaving results...")
    results = test.save_results()
    
    print("\n" + "="*80)
    print("STRESS TEST COMPLETE")
    print("="*80)
    print(f"Final conclusion: {conclusion}")
    
    return test.results


if __name__ == "__main__":
    results = main()
