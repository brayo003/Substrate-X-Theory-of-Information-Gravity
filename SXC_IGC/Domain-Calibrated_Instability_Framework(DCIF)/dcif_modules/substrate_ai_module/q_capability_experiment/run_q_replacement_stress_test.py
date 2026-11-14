"""
Q Replacement Stress Test

This script stress-tests candidate Q replacements against the validated
telegraph equation to determine whether they can serve as transport
regime classifiers.
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


def evolve_field_telegraph_1d(state, c, tau):
    """Evolve field using telegraph equation (1D implementation)."""
    s = state.field_values
    v = state.field_velocity
    dx = state.dx
    dt = state.dt
    
    # 1D Laplacian
    laplacian = np.zeros_like(s)
    if len(s) > 2:
        laplacian[1:-1] = (s[2:] - 2*s[1:-1] + s[:-2]) / (dx**2)
    
    # Telegraph equation
    acceleration = (c**2) * laplacian - v / tau
    v_new = v + dt * acceleration
    s_new = s + dt * v_new
    
    return FieldState(
        s_new, v_new, state.coordinates,
        dx, state.dy, state.dz, dt,
        state.physical_time + dt, state.grid_shape
    )


class QReplacementStressTest:
    """Stress test for Q replacement candidates."""
    
    def __init__(self):
        self.results = {
            'test_date': '2026-08-09',
            'telegraph_equation': 'τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s',
            'candidates': {},
            'test_suites': {},
            'conclusion': None,
        }
    
    def compute_true_transport_regime(self, c, tau, k):
        """Compute true telegraph transport regime."""
        k_c = 1.0 / (2 * c * tau)
        
        if k > k_c:
            return "coherent"
        elif k < k_c:
            return "overdamped"
        else:
            return "critical"
    
    def compute_spectral_discriminant(self, field, c, tau):
        """Candidate A: Spectral transport discriminant."""
        s = field.field_values
        L = field.coordinates[-1, 0] - field.coordinates[0, 0]
        
        # Compute spatial FFT
        s_k = np.fft.fft(s)
        power_spectrum = np.abs(s_k)**2
        
        # Get wavenumbers
        k_values = 2 * np.pi * np.fft.fftfreq(len(s), d=field.dx)
        
        # Find dominant wavenumber (exclude DC component)
        power_spectrum[0] = 0  # Ignore DC
        k_idx = np.argmax(power_spectrum)
        k_dominant = abs(k_values[k_idx])
        
        # Compute discriminant
        Q = 4 * c**2 * tau**2 * k_dominant**2 - 1
        
        # Classification
        if Q > 0:
            regime = "coherent"
        elif Q < 0:
            regime = "overdamped"
        else:
            regime = "critical"
        
        return {
            'Q': Q,
            'k_dominant': k_dominant,
            'regime': regime,
        }
    
    def compute_weighted_discriminant(self, field, c, tau):
        """Candidate B: Weighted spectral discriminant."""
        s = field.field_values
        
        # Compute spatial FFT
        s_k = np.fft.fft(s)
        power_spectrum = np.abs(s_k)**2
        
        # Get wavenumbers
        k_values = 2 * np.pi * np.fft.fftfreq(len(s), d=field.dx)
        
        # Compute discriminant for each k
        discriminants = 4 * c**2 * tau**2 * k_values**2 - 1
        
        # Weighted average
        total_power = np.sum(power_spectrum)
        if total_power > 0:
            Q = np.sum(power_spectrum * discriminants) / total_power
        else:
            Q = -1.0
        
        # Classification
        if Q > 0:
            regime = "coherent"
        elif Q < 0:
            regime = "overdamped"
        else:
            regime = "critical"
        
        return {
            'Q': Q,
            'regime': regime,
        }
    
    def compute_local_phase_discriminant(self, field, c, tau):
        """Candidate C: Local phase gradient discriminant."""
        s = field.field_values
        
        # Simple local gradient estimate (Hilbert transform not available in pure numpy)
        # Use gradient of field as phase proxy for single-mode fields
        ds_dx = np.gradient(s, field.dx)
        
        # Estimate local wavenumber from gradient magnitude
        # For s = s0 + A cos(kx), |∇s| ≈ Ak at peaks
        # This is an approximation
        s_mag = np.abs(s)
        s_mag[s_mag < 1e-10] = 1e-10  # Avoid division by zero
        
        k_local = np.abs(ds_dx) / s_mag
        
        # Compute local discriminant
        Q_local = 4 * c**2 * tau**2 * k_local**2 - 1
        
        # Use mean for classification
        Q_mean = np.mean(Q_local)
        
        if Q_mean > 0:
            regime = "coherent"
        elif Q_mean < 0:
            regime = "overdamped"
        else:
            regime = "critical"
        
        return {
            'Q': Q_mean,
            'Q_local': Q_local.tolist(),
            'regime': regime,
        }
    
    def initialize_fourier_mode(self, k, A, s0, c, tau, nx, dt):
        """Initialize field with controlled Fourier mode."""
        wavelength = 2 * np.pi / k
        L = 5 * wavelength
        x_range = (0.0, L)
        
        state = initialize_field_state_1d(
            x_range=x_range,
            nx=nx,
            initial_value=s0,
            dt=dt,
        )
        
        # Initialize with Fourier mode
        x_coords = state.coordinates[:, 0]
        s_values = s0 + A * np.cos(k * x_coords)
        state.field_values = s_values
        
        # Initialize velocity consistently
        propagating = c**2 * k**2 > 1.0 / (4 * tau**2)
        if propagating:
            omega = np.sqrt(c**2 * k**2 - 1.0 / (4 * tau**2))
            v_values = A * (-1.0/(2*tau) * np.cos(k * x_coords) + omega * np.sin(k * x_coords))
        else:
            v_values = np.zeros_like(x_coords)
        
        state.field_velocity = v_values
        
        return state, L
    
    def measure_transport(self, field, k, L, duration=5.0):
        """Measure actual transport regime from temporal evolution."""
        times = []
        amplitudes = []
        
        current_field = field
        current_time = 0.0
        dt = field.dt
        
        num_steps = int(duration / dt)
        output_interval = max(1, num_steps // 50)
        
        for step in range(num_steps):
            if step % output_interval == 0:
                # Measure Fourier component at k
                x_coords = current_field.coordinates[:, 0]
                s_values = current_field.field_values
                
                C = np.sum(s_values * np.cos(k * x_coords)) * (L / len(x_coords))
                S = np.sum(s_values * np.sin(k * x_coords)) * (L / len(x_coords))
                amplitude = np.sqrt(C**2 + S**2)
                
                times.append(current_time)
                amplitudes.append(amplitude)
            
            current_field = evolve_field_telegraph_1d(current_field, 1.0, 1.0)
            current_time += dt
        
        # Fit oscillation frequency
        times = np.array(times)
        amplitudes = np.array(amplitudes)
        
        # Check for oscillations
        fft_amp = np.fft.fft(amplitudes)
        freqs = np.fft.fftfreq(len(amplitudes), d=times[1] - times[0])
        
        # Find dominant frequency (excluding DC)
        fft_amp[0] = 0
        dominant_freq_idx = np.argmax(np.abs(fft_amp))
        omega_measured = abs(freqs[dominant_freq_idx])
        
        if omega_measured > 0.1:
            measured_regime = "coherent"
        else:
            measured_regime = "overdamped"
        
        return measured_regime
    
    def run_single_test(self, c, tau, k, A, s0, resolution_factor=20, duration=5.0, dt=0.01):
        """Run single test case."""
        
        true_regime = self.compute_true_transport_regime(c, tau, k)
        
        wavelength = 2 * np.pi / k
        nx = int(5 * wavelength * resolution_factor) + 1
        
        state, L = self.initialize_fourier_mode(k, A, s0, c, tau, nx, dt)
        
        # Evolve briefly to get dynamic field
        for _ in range(10):
            state = evolve_field_telegraph_1d(state, c, tau)
        
        # Compute candidates
        spectral = self.compute_spectral_discriminant(state, c, tau)
        weighted = self.compute_weighted_discriminant(state, c, tau)
        local = self.compute_local_phase_discriminant(state, c, tau)
        
        # Measure actual transport
        measured_regime = self.measure_transport(state, k, L, duration)
        
        result = {
            'c': c,
            'tau': tau,
            'k': k,
            'A': A,
            's0': s0,
            'true_regime': true_regime,
            'measured_regime': measured_regime,
            'spectral_Q': spectral['Q'],
            'spectral_regime': spectral['regime'],
            'weighted_Q': weighted['Q'],
            'weighted_regime': weighted['regime'],
            'local_Q': local['Q'],
            'local_regime': local['regime'],
        }
        
        # Agreement checks
        result['spectral_agreement'] = (spectral['regime'] == true_regime)
        result['weighted_agreement'] = (weighted['regime'] == true_regime)
        result['local_agreement'] = (local['regime'] == true_regime)
        
        return result
    
    def run_amplitude_sweep(self):
        """Test amplitude independence."""
        print("="*80)
        print("AMPLITUDE SWEEP TEST")
        print("="*80)
        
        c, tau, s0 = 1.0, 1.0, 1.0
        k_values = [0.25, 0.40, 0.50, 0.60, 0.75, 1.00, 1.2566]
        amplitudes = [0.05, 0.10, 0.20, 0.40, 0.60, 0.80]
        
        results = []
        
        for k in k_values:
            for A in amplitudes:
                result = self.run_single_test(c, tau, k, A, s0)
                results.append(result)
        
        # Analyze
        spectral_correct = sum(1 for r in results if r['spectral_agreement'])
        weighted_correct = sum(1 for r in results if r['weighted_agreement'])
        local_correct = sum(1 for r in results if r['local_agreement'])
        total = len(results)
        
        print(f"Spectral: {spectral_correct}/{total} ({spectral_correct/total:.1%})")
        print(f"Weighted: {weighted_correct}/{total} ({weighted_correct/total:.1%})")
        print(f"Local: {local_correct}/{total} ({local_correct/total:.1%})")
        
        self.results['test_suites']['amplitude_sweep'] = {
            'results': results,
            'spectral_accuracy': spectral_correct / total,
            'weighted_accuracy': weighted_correct / total,
            'local_accuracy': local_correct / total,
        }
        
        return results
    
    def run_parameter_sweep(self):
        """Test c/τ independence."""
        print("\n" + "="*80)
        print("PARAMETER SWEEP TEST")
        print("="*80)
        
        c_values = [0.5, 1.0, 2.0]
        tau_values = [0.5, 1.0, 2.0]
        k = 0.75  # Above typical critical
        A, s0 = 0.5, 1.0
        
        results = []
        
        for c in c_values:
            for tau in tau_values:
                result = self.run_single_test(c, tau, k, A, s0)
                results.append(result)
        
        # Analyze
        spectral_correct = sum(1 for r in results if r['spectral_agreement'])
        weighted_correct = sum(1 for r in results if r['weighted_agreement'])
        local_correct = sum(1 for r in results if r['local_agreement'])
        total = len(results)
        
        print(f"Spectral: {spectral_correct}/{total} ({spectral_correct/total:.1%})")
        print(f"Weighted: {weighted_correct}/{total} ({weighted_correct/total:.1%})")
        print(f"Local: {local_correct}/{total} ({local_correct/total:.1%})")
        
        self.results['test_suites']['parameter_sweep'] = {
            'results': results,
            'spectral_accuracy': spectral_correct / total,
            'weighted_accuracy': weighted_correct / total,
            'local_accuracy': local_correct / total,
        }
        
        return results
    
    def run_resolution_sweep(self):
        """Test resolution convergence."""
        print("\n" + "="*80)
        print("RESOLUTION SWEEP TEST")
        print("="*80)
        
        c, tau, k, A, s0 = 1.0, 1.0, 0.75, 0.5, 1.0
        resolution_factors = [10, 20, 40, 80]
        
        results = []
        
        for res_factor in resolution_factors:
            result = self.run_single_test(c, tau, k, A, s0, resolution_factor=res_factor)
            results.append(result)
        
        # Analyze convergence
        spectral_Q = [r['spectral_Q'] for r in results]
        weighted_Q = [r['weighted_Q'] for r in results]
        local_Q = [r['local_Q'] for r in results]
        
        spectral_std = np.std(spectral_Q)
        weighted_std = np.std(weighted_Q)
        local_std = np.std(local_Q)
        
        print(f"Spectral Q std: {spectral_std:.6f}")
        print(f"Weighted Q std: {weighted_std:.6f}")
        print(f"Local Q std: {local_std:.6f}")
        
        self.results['test_suites']['resolution_sweep'] = {
            'results': results,
            'spectral_std': spectral_std,
            'weighted_std': weighted_std,
            'local_std': local_std,
        }
        
        return results
    
    def compute_conclusion(self):
        """Compute final conclusion."""
        print("\n" + "="*80)
        print("CONCLUSION ANALYSIS")
        print("="*80)
        
        amplitude = self.results['test_suites']['amplitude_sweep']
        parameter = self.results['test_suites']['parameter_sweep']
        resolution = self.results['test_suites']['resolution_sweep']
        
        # Evaluate each candidate
        spectral_scores = {
            'amplitude_accuracy': amplitude['spectral_accuracy'],
            'parameter_accuracy': parameter['spectral_accuracy'],
            'resolution_stability': 1.0 / (1.0 + resolution['spectral_std']),
        }
        
        weighted_scores = {
            'amplitude_accuracy': amplitude['weighted_accuracy'],
            'parameter_accuracy': parameter['weighted_accuracy'],
            'resolution_stability': 1.0 / (1.0 + resolution['weighted_std']),
        }
        
        local_scores = {
            'amplitude_accuracy': amplitude['local_accuracy'],
            'parameter_accuracy': parameter['local_accuracy'],
            'resolution_stability': 1.0 / (1.0 + resolution['local_std']),
        }
        
        # Overall scores
        spectral_overall = np.mean(list(spectral_scores.values()))
        weighted_overall = np.mean(list(weighted_scores.values()))
        local_overall = np.mean(list(local_scores.values()))
        
        print(f"Spectral overall: {spectral_overall:.3f}")
        print(f"Weighted overall: {weighted_overall:.3f}")
        print(f"Local overall: {local_overall:.3f}")
        
        # Decision
        if spectral_overall > 0.9:
            conclusion = "SPECTRAL DISCRIMINANT VALIDATED"
        elif weighted_overall > 0.9:
            conclusion = "WEIGHTED SPECTRAL DISCRIMINANT VALIDATED"
        elif local_overall > 0.8:
            conclusion = "LOCAL APPROXIMATION ACCEPTABLE"
        else:
            conclusion = "NO VALID REPLACEMENT FOUND"
        
        print(f"\nFINAL CONCLUSION: {conclusion}")
        
        self.results['conclusion'] = conclusion
        self.results['candidates'] = {
            'spectral': spectral_scores,
            'weighted': weighted_scores,
            'local': local_scores,
        }
        
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
        json_path = '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/q_capability_experiment/Q_REPLACEMENT_STRESS_TEST_RESULTS.json'
        with open(json_path, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        print(f"\nJSON results saved to: {json_path}")
        
        # Save markdown report
        md_path = '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/q_capability_experiment/Q_REPLACEMENT_STRESS_TEST_RESULTS.md'
        
        with open(md_path, 'w') as f:
            f.write("# Q Replacement Stress Test Results\n\n")
            f.write(f"**Test Date:** {results_serializable['test_date']}\n\n")
            f.write(f"**Telegraph Equation:** {results_serializable['telegraph_equation']}\n\n")
            f.write(f"**Conclusion:** {results_serializable['conclusion']}\n\n")
            f.write("---\n\n")
            
            f.write("## Test Suites\n\n")
            
            f.write("### Amplitude Sweep\n\n")
            amp = results_serializable['test_suites']['amplitude_sweep']
            f.write(f"- Spectral accuracy: {amp['spectral_accuracy']:.1%}\n")
            f.write(f"- Weighted accuracy: {amp['weighted_accuracy']:.1%}\n")
            f.write(f"- Local accuracy: {amp['local_accuracy']:.1%}\n\n")
            
            f.write("### Parameter Sweep\n\n")
            param = results_serializable['test_suites']['parameter_sweep']
            f.write(f"- Spectral accuracy: {param['spectral_accuracy']:.1%}\n")
            f.write(f"- Weighted accuracy: {param['weighted_accuracy']:.1%}\n")
            f.write(f"- Local accuracy: {param['local_accuracy']:.1%}\n\n")
            
            f.write("### Resolution Sweep\n\n")
            res = results_serializable['test_suites']['resolution_sweep']
            f.write(f"- Spectral Q std: {res['spectral_std']:.6f}\n")
            f.write(f"- Weighted Q std: {res['weighted_std']:.6f}\n")
            f.write(f"- Local Q std: {res['local_std']:.6f}\n\n")
            
            f.write("## Candidate Performance\n\n")
            candidates = results_serializable['candidates']
            f.write("### Spectral Discriminant\n\n")
            for metric, value in candidates['spectral'].items():
                f.write(f"- {metric}: {value:.3f}\n")
            
            f.write("\n### Weighted Discriminant\n\n")
            for metric, value in candidates['weighted'].items():
                f.write(f"- {metric}: {value:.3f}\n")
            
            f.write("\n### Local Approximation\n\n")
            for metric, value in candidates['local'].items():
                f.write(f"- {metric}: {value:.3f}\n")
            
            f.write("\n---\n\n")
            f.write("## Final Decision\n\n")
            f.write(f"**{results_serializable['conclusion']}**\n\n")
        
        print(f"Markdown report saved to: {md_path}")
        
        return results_serializable


def main():
    """Run Q replacement stress test."""
    print("="*80)
    print("Q REPLACEMENT STRESS TEST")
    print("Validating replacement candidates against telegraph equation")
    print("="*80)
    
    test = QReplacementStressTest()
    
    # Run test suites
    print("\nRunning amplitude sweep...")
    test.run_amplitude_sweep()
    
    print("\nRunning parameter sweep...")
    test.run_parameter_sweep()
    
    print("\nRunning resolution sweep...")
    test.run_resolution_sweep()
    
    # Compute conclusion
    print("\nComputing conclusion...")
    conclusion = test.compute_conclusion()
    
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
